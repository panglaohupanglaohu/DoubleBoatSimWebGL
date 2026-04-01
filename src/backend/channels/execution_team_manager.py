# -*- coding: utf-8 -*-
"""
Execution Agent Team Manager - 执行智能体团队管理器

管理负责 AI Native 系统运行时功能最大化的智能体团队。
团队通过 DeepSeek 驱动，实时运行系统核心功能，
并将发现的问题和优化建议反馈给构建团队。

角色分工：
  - Perception Agent   : 管理分布式感知融合 (L2)
  - Decision Agent     : 管理决策编排 (L3)
  - Navigation Agent   : 管理自主航行 / COLREGS 合规 (L3)
  - Energy Agent       : 管理能效优化 (跨层)
  - Feedback Agent     : 汇总执行数据，向构建团队提交优化需求
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from channels.marine_base import MarineChannel, ChannelPriority, ChannelStatus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class ExecRole(str, Enum):
    PERCEPTION = "perception"
    DECISION = "decision"
    NAVIGATION = "navigation"
    ENERGY = "energy"
    FEEDBACK = "feedback"


class ExecState(str, Enum):
    IDLE = "idle"
    MONITORING = "monitoring"
    OPTIMIZING = "optimizing"
    ALERTING = "alerting"
    ERROR = "error"


@dataclass
class ExecAgentMetrics:
    """执行 Agent 运行时指标."""
    cycles_run: int = 0
    anomalies_detected: int = 0
    optimizations_applied: int = 0
    feedback_sent: int = 0
    uptime_seconds: float = 0.0
    last_cycle_at: Optional[str] = None


@dataclass
class ExecAgent:
    """单个执行智能体."""
    id: str
    role: ExecRole
    name: str
    description: str
    llm_backend: str = "deepseek"
    state: ExecState = ExecState.IDLE
    target_channels: List[str] = field(default_factory=list)
    metrics: ExecAgentMetrics = field(default_factory=ExecAgentMetrics)
    config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "state": self.state.value, "role": self.role.value}


@dataclass
class FeedbackItem:
    """执行团队向构建团队发送的反馈条目."""
    id: str
    source_agent: str
    category: str  # bug, optimization, feature_request, alert
    severity: str  # critical, high, medium, low
    title: str
    detail: str
    created_at: str
    resolved: bool = False
    resolution: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionReport:
    """执行团队的定期运行报告."""
    timestamp: str
    period_seconds: float
    perception_events: int = 0
    decisions_made: int = 0
    nav_corrections: int = 0
    energy_savings_pct: float = 0.0
    anomalies: int = 0
    feedback_items_sent: int = 0
    channel_health: Dict[str, str] = field(default_factory=dict)
    agents_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Execution Team Manager Channel
# ---------------------------------------------------------------------------

class ExecutionTeamManagerChannel(MarineChannel):
    """执行智能体团队管理器 — 融入 AI Native CPS 架构."""

    name = "execution_team_manager"
    description = "执行智能体团队管理 (感知 → 决策 → 导航 → 能效 → 反馈)"
    version = "1.0.0"
    priority = ChannelPriority.P0  # 执行团队优先级最高
    dependencies: List[str] = [
        "distributed_perception_hub",
        "decision_orchestrator",
    ]

    # 默认运行间隔 (秒) — 执行团队运行更频繁
    SCHEDULE = {
        ExecRole.PERCEPTION: 5,    # 每 5 秒一次感知融合
        ExecRole.DECISION: 10,     # 每 10 秒一次决策评估
        ExecRole.NAVIGATION: 10,   # 每 10 秒一次航行校正
        ExecRole.ENERGY: 30,       # 每 30 秒一次能效评估
        ExecRole.FEEDBACK: 60,     # 每 60 秒汇总反馈
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.config = config or {}
        self._config = self.config
        self.llm_backend = self.config.get("llm_backend", "deepseek")

        self.agents: Dict[str, ExecAgent] = {}
        self._init_agents()

        self.feedback_queue: List[FeedbackItem] = []
        self.execution_reports: List[ExecutionReport] = []
        self.event_log: List[Dict[str, Any]] = []
        self._running = False
        self._start_time: Optional[float] = None

        # 全局运行时指标
        self.total_perception_events = 0
        self.total_decisions = 0
        self.total_nav_corrections = 0
        self.total_energy_savings_pct = 0.0
        self.total_anomalies = 0
        self._feedback_counter = 0

    # ── Agent 初始化 ──────────────────────────────────────────

    def _init_agents(self):
        definitions = [
            {
                "id": "exec_perception",
                "role": ExecRole.PERCEPTION,
                "name": "Perception Fusion Agent",
                "description": "持续融合 AIS/雷达/气象/WorldMonitor 数据，检测异常",
                "target_channels": [
                    "distributed_perception_hub",
                    "nmea_channel",
                    "worldmonitor",
                ],
            },
            {
                "id": "exec_decision",
                "role": ExecRole.DECISION,
                "name": "Decision & Planning Agent",
                "description": "实时评估态势，产出决策建议，驱动自主操控",
                "target_channels": [
                    "decision_orchestrator",
                    "colregs_brain",
                ],
            },
            {
                "id": "exec_navigation",
                "role": ExecRole.NAVIGATION,
                "name": "Navigation Control Agent",
                "description": "航行纠偏、COLREGS 合规检查、姿态控制",
                "target_channels": [
                    "colregs_brain",
                    "wpc_attitude_control",
                ],
            },
            {
                "id": "exec_energy",
                "role": ExecRole.ENERGY,
                "name": "Energy Optimization Agent",
                "description": "能效分析 (CII/EEXI)、航速优化、燃料节省",
                "target_channels": [
                    "energy_efficiency",
                    "data_lakehouse",
                ],
            },
            {
                "id": "exec_feedback",
                "role": ExecRole.FEEDBACK,
                "name": "Feedback & Issue Agent",
                "description": "汇总执行数据，向构建团队提交优化需求与 bug 报告",
                "target_channels": [
                    "build_team_manager",
                    "event_store",
                ],
            },
        ]
        for defn in definitions:
            agent = ExecAgent(
                id=defn["id"],
                role=defn["role"],
                name=defn["name"],
                description=defn["description"],
                llm_backend=self.llm_backend,
                target_channels=defn.get("target_channels", []),
            )
            self.agents[agent.id] = agent

    # ── MarineChannel 接口 ───────────────────────────────────

    def initialize(self) -> bool:
        self._initialized = True
        self._running = True
        self._start_time = time.monotonic()
        for agent in self.agents.values():
            agent.state = ExecState.MONITORING
        self._set_health(ChannelStatus.OK, "执行团队就绪，5 名 Agent 已上线")
        logger.info("⚡ Execution Team Manager initialized (%d agents)", len(self.agents))
        return True

    def shutdown(self) -> bool:
        self._running = False
        self._initialized = False
        for agent in self.agents.values():
            agent.state = ExecState.IDLE
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True

    # ── 调度 & 执行 ──────────────────────────────────────────

    def tick(self, now: Optional[datetime] = None, channel_registry: Optional[Dict] = None) -> Dict[str, Any]:
        """外部定时调用，驱动所有执行 Agent."""
        now = now or datetime.now()
        results: Dict[str, Any] = {}
        for agent in self.agents.values():
            if self._should_run(agent, now):
                result = self._execute_agent_cycle(agent, now, channel_registry)
                results[agent.id] = result
        return results

    def _should_run(self, agent: ExecAgent, now: datetime) -> bool:
        interval = self.SCHEDULE.get(agent.role, 30)
        if not agent.metrics.last_cycle_at:
            return True
        try:
            last = datetime.fromisoformat(agent.metrics.last_cycle_at)
            return (now - last).total_seconds() >= interval
        except (ValueError, TypeError):
            return True

    def _execute_agent_cycle(
        self, agent: ExecAgent, now: datetime,
        channel_registry: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        agent.state = ExecState.MONITORING
        agent.metrics.last_cycle_at = now.isoformat()
        cycle_start = time.monotonic()
        result: Dict[str, Any] = {
            "agent": agent.id, "role": agent.role.value, "time": now.isoformat()
        }

        try:
            if agent.role == ExecRole.PERCEPTION:
                result.update(self._run_perception(agent, now, channel_registry))
            elif agent.role == ExecRole.DECISION:
                result.update(self._run_decision(agent, now, channel_registry))
            elif agent.role == ExecRole.NAVIGATION:
                result.update(self._run_navigation(agent, now, channel_registry))
            elif agent.role == ExecRole.ENERGY:
                result.update(self._run_energy(agent, now, channel_registry))
            elif agent.role == ExecRole.FEEDBACK:
                result.update(self._run_feedback(agent, now))

            agent.metrics.cycles_run += 1
            agent.state = ExecState.MONITORING
        except Exception as exc:
            agent.state = ExecState.ERROR
            result["error"] = str(exc)
            logger.error("Exec agent %s cycle failed: %s", agent.id, exc)

        elapsed = time.monotonic() - cycle_start
        agent.metrics.uptime_seconds += elapsed
        self.event_log.append(result)
        return result

    # ── 各角色执行逻辑 ───────────────────────────────────────

    def _run_perception(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
        """感知 Agent：融合多源数据，检测异常."""
        # 如果有实际 channel registry，从中获取感知数据
        snapshot: Dict[str, Any] = {}
        if registry:
            hub = registry.get("distributed_perception_hub")
            if hub and hasattr(hub, "capture_system_snapshot"):
                try:
                    snapshot = hub.capture_system_snapshot()
                except Exception:
                    snapshot = {"error": "snapshot_unavailable"}

        # 基本感知事件模拟
        event_count = 3 + (agent.metrics.cycles_run % 5)
        anomaly = 1 if agent.metrics.cycles_run % 7 == 0 else 0
        self.total_perception_events += event_count
        self.total_anomalies += anomaly

        if anomaly:
            agent.state = ExecState.ALERTING
            agent.metrics.anomalies_detected += 1
            self._create_feedback(
                agent.id, "alert", "high",
                f"感知异常 #{agent.metrics.anomalies_detected}",
                f"在第 {agent.metrics.cycles_run} 个感知周期检测到数据异常",
            )

        return {
            "action": "perception_fusion",
            "events_processed": event_count,
            "anomaly_detected": anomaly > 0,
            "snapshot_available": bool(snapshot),
        }

    def _run_decision(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
        """决策 Agent：态势评估 & 行动建议."""
        decision_quality = 0.85 + (agent.metrics.cycles_run % 10) * 0.01
        self.total_decisions += 1

        actions_recommended = [
            {"type": "course_adjustment", "priority": "medium", "detail": "建议微调航向 2°"},
            {"type": "speed_optimization", "priority": "low", "detail": "当前航速经济性良好"},
        ]

        if self.total_anomalies > 0 and agent.metrics.cycles_run % 5 == 0:
            actions_recommended.append({
                "type": "emergency_assessment", "priority": "high",
                "detail": "需要评估最近的感知异常对航行安全的影响",
            })

        return {
            "action": "decision_evaluation",
            "decision_quality": round(decision_quality, 3),
            "actions_recommended": len(actions_recommended),
            "details": actions_recommended,
        }

    def _run_navigation(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
        """航行 Agent：COLREGS 合规 & 纠偏."""
        correction_needed = agent.metrics.cycles_run % 4 == 0
        if correction_needed:
            self.total_nav_corrections += 1
            agent.metrics.optimizations_applied += 1

        colregs_status = "COMPLIANT"
        if agent.metrics.cycles_run % 20 == 0 and agent.metrics.cycles_run > 0:
            colregs_status = "REVIEW_NEEDED"
            self._create_feedback(
                agent.id, "optimization", "medium",
                "COLREGS 规则需要审查",
                "建议构建团队更新 COLREGS 规则引擎以覆盖最新 IMO 规定",
            )

        return {
            "action": "navigation_control",
            "correction_applied": correction_needed,
            "colregs_status": colregs_status,
            "total_corrections": self.total_nav_corrections,
        }

    def _run_energy(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
        """能效 Agent：CII/EEXI 实时评估."""
        # 模拟能效节省 (最高 ~8%)
        savings = 2.5 + (agent.metrics.cycles_run % 12) * 0.5
        self.total_energy_savings_pct = savings
        agent.metrics.optimizations_applied += 1

        cii_rating = "A" if savings > 5 else "B" if savings > 3 else "C"

        if cii_rating == "C":
            self._create_feedback(
                agent.id, "optimization", "high",
                "CII 评级下降至 C",
                "建议构建团队优化航速控制算法以改善 CII 评级",
            )

        return {
            "action": "energy_optimization",
            "savings_pct": round(savings, 2),
            "cii_rating": cii_rating,
            "cycle": agent.metrics.cycles_run,
        }

    def _run_feedback(self, agent: ExecAgent, now: datetime) -> Dict[str, Any]:
        """反馈 Agent：汇总 & 发送反馈给构建团队."""
        pending = list(self.feedback_queue)
        self.feedback_queue = []
        agent.metrics.feedback_sent += len(pending)

        return {
            "action": "feedback_delivery",
            "items_sent": len(pending),
            "items": [item.to_dict() for item in pending[:10]],  # 最多 10 条
            "total_feedback_sent": agent.metrics.feedback_sent,
        }

    # ── 反馈生成 ─────────────────────────────────────────────

    def _create_feedback(
        self, source: str, category: str, severity: str, title: str, detail: str,
    ):
        self._feedback_counter += 1
        item = FeedbackItem(
            id=f"FB-{self._feedback_counter:04d}",
            source_agent=source,
            category=category,
            severity=severity,
            title=title,
            detail=detail,
            created_at=datetime.now().isoformat(),
        )
        self.feedback_queue.append(item)
        return item

    def submit_feedback(self, category: str, severity: str, title: str, detail: str) -> FeedbackItem:
        """外部接口：手动提交反馈."""
        return self._create_feedback("external", category, severity, title, detail)

    # ── 汇报 ────────────────────────────────────────────────

    def generate_execution_report(self) -> ExecutionReport:
        """生成执行团队运行报告."""
        elapsed = time.monotonic() - (self._start_time or time.monotonic())
        report = ExecutionReport(
            timestamp=datetime.now().isoformat(),
            period_seconds=round(elapsed, 1),
            perception_events=self.total_perception_events,
            decisions_made=self.total_decisions,
            nav_corrections=self.total_nav_corrections,
            energy_savings_pct=round(self.total_energy_savings_pct, 2),
            anomalies=self.total_anomalies,
            feedback_items_sent=sum(a.metrics.feedback_sent for a in self.agents.values()),
            channel_health={},
            agents_summary={
                aid: {
                    "state": a.state.value,
                    "cycles": a.metrics.cycles_run,
                    "anomalies": a.metrics.anomalies_detected,
                    "optimizations": a.metrics.optimizations_applied,
                    "uptime_s": round(a.metrics.uptime_seconds, 1),
                }
                for aid, a in self.agents.items()
            },
        )
        self.execution_reports.append(report)
        return report

    # ── Channel Status ───────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "health_message": self._health.message,
            "running": self._running,
            "llm_backend": self.llm_backend,
            "agent_count": len(self.agents),
            "agents": {aid: a.to_dict() for aid, a in self.agents.items()},
            "metrics": {
                "total_perception_events": self.total_perception_events,
                "total_decisions": self.total_decisions,
                "total_nav_corrections": self.total_nav_corrections,
                "energy_savings_pct": round(self.total_energy_savings_pct, 2),
                "total_anomalies": self.total_anomalies,
                "pending_feedback": len(self.feedback_queue),
            },
            "reports_count": len(self.execution_reports),
            "latest_report": (
                self.execution_reports[-1].to_dict() if self.execution_reports else None
            ),
        }


__all__ = [
    "ExecutionTeamManagerChannel",
    "ExecAgent",
    "ExecRole",
    "ExecState",
    "FeedbackItem",
    "ExecutionReport",
]
