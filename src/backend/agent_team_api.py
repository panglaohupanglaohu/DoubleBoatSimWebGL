# -*- coding: utf-8 -*-
"""
Agent Team API Routes - 双团队管理 REST API

提供构建团队 & 执行团队的状态查询、KPI 考核、
任务分配、报告查询等端点。挂载至 FastAPI 的 router。
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

router = APIRouter(prefix="/api/v1/agent-teams", tags=["Agent Teams"])


# ---------------------------------------------------------------------------
# 全局引用（在 main.py startup 时注入）
# ---------------------------------------------------------------------------
_build_team = None
_execution_team = None
_scheduler = None


def set_teams(build_team, execution_team, scheduler):
    """在应用启动时由 main.py 调用，注入团队实例."""
    global _build_team, _execution_team, _scheduler
    _build_team = build_team
    _execution_team = execution_team
    _scheduler = scheduler


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class TaskAssignment(BaseModel):
    agent_id: str
    task: str

class FeedbackSubmission(BaseModel):
    category: str = "optimization"
    severity: str = "medium"
    title: str
    detail: str


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

@router.get("/scheduler/status")
async def scheduler_status():
    if not _scheduler:
        raise HTTPException(503, "Scheduler not initialized")
    return _scheduler.get_status()


@router.post("/scheduler/report")
async def scheduler_generate_report():
    if not _scheduler:
        raise HTTPException(503, "Scheduler not initialized")
    return _scheduler.generate_report_now()


@router.post("/scheduler/tick")
async def scheduler_tick_once():
    """手动触发一次调度 tick (调试用)."""
    if not _scheduler:
        raise HTTPException(503, "Scheduler not initialized")
    return _scheduler.tick_once()


# ---------------------------------------------------------------------------
# Build Team
# ---------------------------------------------------------------------------

@router.get("/build/status")
async def build_team_status():
    if not _build_team:
        raise HTTPException(503, "Build team not initialized")
    return _build_team.get_status()


@router.get("/build/kpis")
async def build_team_kpis():
    if not _build_team:
        raise HTTPException(503, "Build team not initialized")
    return _build_team.get_agent_kpis()


@router.get("/build/agents/{agent_id}")
async def build_agent_detail(agent_id: str):
    if not _build_team:
        raise HTTPException(503, "Build team not initialized")
    agent = _build_team.agents.get(agent_id)
    if not agent:
        raise HTTPException(404, f"Agent '{agent_id}' not found")
    return agent.to_dict()


@router.post("/build/assign")
async def build_assign_task(body: TaskAssignment):
    if not _build_team:
        raise HTTPException(503, "Build team not initialized")
    ok = _build_team.assign_task(body.agent_id, body.task)
    if not ok:
        raise HTTPException(404, f"Agent '{body.agent_id}' not found")
    return {"status": "assigned", "agent_id": body.agent_id, "task": body.task}


@router.get("/build/reports")
async def build_reports(limit: int = 10):
    if not _build_team:
        raise HTTPException(503, "Build team not initialized")
    reports = _build_team.hourly_reports[-limit:]
    return [r.to_dict() for r in reports]


@router.get("/build/issues")
async def build_issues():
    if not _build_team:
        raise HTTPException(503, "Build team not initialized")
    return _build_team.issue_backlog


# ---------------------------------------------------------------------------
# Execution Team
# ---------------------------------------------------------------------------

@router.get("/execution/status")
async def execution_team_status():
    if not _execution_team:
        raise HTTPException(503, "Execution team not initialized")
    return _execution_team.get_status()


@router.get("/execution/agents/{agent_id}")
async def execution_agent_detail(agent_id: str):
    if not _execution_team:
        raise HTTPException(503, "Execution team not initialized")
    agent = _execution_team.agents.get(agent_id)
    if not agent:
        raise HTTPException(404, f"Agent '{agent_id}' not found")
    return agent.to_dict()


@router.get("/execution/reports")
async def execution_reports(limit: int = 10):
    if not _execution_team:
        raise HTTPException(503, "Execution team not initialized")
    reports = _execution_team.execution_reports[-limit:]
    return [r.to_dict() for r in reports]


@router.get("/execution/feedback")
async def execution_feedback():
    if not _execution_team:
        raise HTTPException(503, "Execution team not initialized")
    return [item.to_dict() for item in _execution_team.feedback_queue]


@router.post("/execution/feedback")
async def submit_feedback(body: FeedbackSubmission):
    if not _execution_team:
        raise HTTPException(503, "Execution team not initialized")
    item = _execution_team.submit_feedback(
        category=body.category,
        severity=body.severity,
        title=body.title,
        detail=body.detail,
    )
    return item.to_dict()


# ---------------------------------------------------------------------------
# Combined
# ---------------------------------------------------------------------------

@router.get("/overview")
async def teams_overview():
    """一站式获取双团队全局概览."""
    result: Dict[str, Any] = {}
    if _build_team:
        bs = _build_team.get_status()
        result["build_team"] = {
            "health": bs["health"],
            "agent_count": bs["agent_count"],
            "metrics": bs["metrics"],
        }
    if _execution_team:
        es = _execution_team.get_status()
        result["execution_team"] = {
            "health": es["health"],
            "agent_count": es["agent_count"],
            "metrics": es["metrics"],
        }
    if _scheduler:
        result["scheduler"] = _scheduler.get_status()
    return result


__all__ = ["router", "set_teams"]
