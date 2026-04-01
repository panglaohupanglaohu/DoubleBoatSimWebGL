# -*- coding: utf-8 -*-
"""PoseidonX Agent Team Framework -- Concurrent Task Execution Engine.

Provides DAG-aware concurrent task dispatch with configurable parallelism.
Tasks with unmet dependencies wait; independent tasks run in parallel up to
max_concurrency workers.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class TaskStatus(Enum):
    """Task lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels (lower value = higher priority)."""

    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class AgentTask:
    """A unit of work dispatched to an agent."""

    task_id: str = ""
    agent_id: str = ""
    team_id: str = ""
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 2
    created_at: str = ""
    started_at: str = ""
    completed_at: str = ""
    result: Any = None
    error: str = ""
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.task_id:
            self.task_id = str(uuid.uuid4())[:12]
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "team_id": self.team_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }


StatusCallback = Callable[[AgentTask, TaskStatus, TaskStatus], None]


class TaskEngine:
    """Concurrent task execution engine with dependency resolution.

    Parameters
    ----------
    max_concurrency : int
        Maximum number of tasks executing in parallel (default 4).
    """

    def __init__(self, max_concurrency: int = 4) -> None:
        self._max_concurrency = max_concurrency
        self._tasks: Dict[str, AgentTask] = {}
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._workers: List[asyncio.Task] = []
        self._running = False
        self._callbacks: List[StatusCallback] = []
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._semaphore = asyncio.Semaphore(self._max_concurrency)
        for i in range(self._max_concurrency):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)

    async def stop(self) -> None:
        self._running = False
        for _ in self._workers:
            await self._queue.put("")
        for w in self._workers:
            w.cancel()
        self._workers.clear()

    def on_status_change(self, callback: StatusCallback) -> None:
        self._callbacks.append(callback)

    async def submit_task(self, task: AgentTask) -> AgentTask:
        async with self._lock:
            self._tasks[task.task_id] = task
        await self._enqueue_if_ready(task.task_id)
        return task

    async def submit_batch(self, tasks: List[AgentTask]) -> List[AgentTask]:
        async with self._lock:
            for t in tasks:
                self._tasks[t.task_id] = t
        for t in tasks:
            await self._enqueue_if_ready(t.task_id)
        return tasks

    def get_task(self, task_id: str) -> Optional[AgentTask]:
        return self._tasks.get(task_id)

    def get_team_tasks(self, team_id: str) -> List[AgentTask]:
        return [t for t in self._tasks.values() if t.team_id == team_id]

    def get_agent_tasks(self, agent_id: str) -> List[AgentTask]:
        return [t for t in self._tasks.values() if t.agent_id == agent_id]

    async def cancel_task(self, task_id: str) -> Optional[AgentTask]:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        if task.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
            old = task.status
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now(timezone.utc).isoformat()
            self._fire_callbacks(task, old, TaskStatus.CANCELLED)
        return task

    def stats(self) -> Dict[str, Any]:
        from collections import Counter
        counts = Counter(t.status.value for t in self._tasks.values())
        return {
            "total": len(self._tasks),
            "by_status": dict(counts),
            "max_concurrency": self._max_concurrency,
            "running": self._running,
        }

    async def _enqueue_if_ready(self, task_id: str) -> None:
        task = self._tasks.get(task_id)
        if task is None or task.status != TaskStatus.PENDING:
            return
        if self._dependencies_met(task):
            await self._queue.put(task_id)

    def _dependencies_met(self, task: AgentTask) -> bool:
        for dep_id in task.dependencies:
            dep = self._tasks.get(dep_id)
            if dep is None or dep.status != TaskStatus.COMPLETED:
                return False
        return True

    async def _worker(self, name: str) -> None:
        while self._running:
            try:
                task_id = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            if not task_id:
                continue
            task = self._tasks.get(task_id)
            if task is None or task.status != TaskStatus.PENDING:
                continue
            if not self._dependencies_met(task):
                old = task.status
                task.status = TaskStatus.FAILED
                task.error = "Dependency not met"
                task.completed_at = datetime.now(timezone.utc).isoformat()
                self._fire_callbacks(task, old, TaskStatus.FAILED)
                self._cascade_dependents()
                continue
            assert self._semaphore is not None
            async with self._semaphore:
                await self._execute(task)

    async def _execute(self, task: AgentTask) -> None:
        old_status = task.status
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc).isoformat()
        self._fire_callbacks(task, old_status, TaskStatus.RUNNING)
        try:
            await asyncio.sleep(0)
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc).isoformat()
            if task.result is None:
                task.result = {"message": f"Task '{task.title}' completed"}
            self._fire_callbacks(task, TaskStatus.RUNNING, TaskStatus.COMPLETED)
        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.error = str(exc)
            task.completed_at = datetime.now(timezone.utc).isoformat()
            self._fire_callbacks(task, TaskStatus.RUNNING, TaskStatus.FAILED)
        self._cascade_dependents()

    def _cascade_dependents(self) -> None:
        for t in self._tasks.values():
            if t.status == TaskStatus.PENDING and self._dependencies_met(t):
                asyncio.ensure_future(self._queue.put(t.task_id))

    def _fire_callbacks(
        self, task: AgentTask, old: TaskStatus, new: TaskStatus
    ) -> None:
        for cb in self._callbacks:
            try:
                cb(task, old, new)
            except Exception:
                pass


_engine: Optional[TaskEngine] = None


def get_task_engine(max_concurrency: int = 4) -> TaskEngine:
    global _engine
    if _engine is None:
        _engine = TaskEngine(max_concurrency=max_concurrency)
    return _engine
