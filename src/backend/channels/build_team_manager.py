# -*- coding: utf-8 -*-
"""
Build Agent Team Manager - 构建智能体团队管理器

管理负责系统持续运维、优化、调整、测试、部署的智能体团队。
团队成员：Researcher, Architect, Developer, Tester, Deployer
默认 LLM 后端：GitHub Copilot

调度规则：
  - Researcher:  每 15 分钟获取网络信息 → 反馈给 Architect
  - Architect:   每 30 分钟产出设计方案 → 分配给 Developer
  - Developer:   每 10 分钟汇报增量          → 通知 Tester
  - Tester:      每 15 分钟汇报 Test case    → 通知 Deployer
  - Deployer:    每  1 小时做一次系统部署     → 找 Developer 修 bug
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

class AgentRole(str, Enum):
    RESEARCHER = "researcher"
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    TESTER = "tester"
    DEPLOYER = "deployer"


class AgentState(str, Enum):
    IDLE = "idle"
    WORKING = "working"
    REPORTING = "reporting"
    BLOCKED = "blocked"
    ERROR = "error"


@dataclass
class BuildAgentKPI:
    """每个构建 Agent 的 KPI 快照."""
    tasks_completed: int = 0
    tasks_failed: int = 0
    deliverables: int = 0  # 代码行数 / test case 数 / 文档数 / 设计方案数
    last_report_at: Optional[str] = None
    avg_cycle_seconds: float = 0.0
    utilization_pct: float = 0.0  # 0-100 忙碌率


@dataclass
class BuildAgent:
    """单个构建智能体."""
    id: str
    role: AgentRole
    name: str
    description: str
    llm_backend: str = "copilot"
    state: AgentState = AgentState.IDLE
    schedule_interval_sec: int = 600  # 默认 10 分钟
    kpi: BuildAgentKPI = field(default_factory=BuildAgentKPI)
    current_task: Optional[str] = None
    task_queue: List[str] = field(default_factory=list)
    last_heartbeat: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "state": self.state.value, "role": self.role.value}


@dataclass
class HourlyReport:
    """每小时汇总报告."""
    timestamp: str
    period_start: str
    period_end: str
    code_lines_added: int = 0
    test_cases_total: int = 0
    test_cases_passed: int = 0
    deployment_attempts: int = 0
    deployment_successes: int = 0
    research_updates: int = 0
    architecture_decisions: int = 0
    issues_found: int = 0
    issues_resolved: int = 0
    agents_summary: Dict[str, Any] = field(default_factory=dict)

    @property
    def deployment_success_rate(self) -> float:
        return self.deployment_successes / max(self.deployment_attempts, 1)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["deployment_success_rate"] = self.deployment_success_rate
        return d


# ---------------------------------------------------------------------------
# Build Team Manager Channel
# ---------------------------------------------------------------------------

class BuildTeamManagerChannel(MarineChannel):
    """构建智能体团队管理器 — 作为 MarineChannel 融入系统."""

    name = "build_team_manager"
    description = "构建智能体团队管理 (研究 → 设计 → 开发 → 测试 → 部署)"
    version = "1.0.0"
    priority = ChannelPriority.P1
    dependencies: List[str] = []

    # 默认调度参数 (秒)
    SCHEDULE = {
        AgentRole.RESEARCHER: 15 * 60,
        AgentRole.ARCHITECT: 30 * 60,
        AgentRole.DEVELOPER: 10 * 60,
        AgentRole.TESTER: 15 * 60,
        AgentRole.DEPLOYER: 60 * 60,
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.config = config or {}
        self._config = self.config
        self.llm_backend = self.config.get("llm_backend", "copilot")

        # 创建 5 个 Agent
        self.agents: Dict[str, BuildAgent] = {}
        self._init_agents()

        # 运行时状态
        self.hourly_reports: List[HourlyReport] = []
        self.event_log: List[Dict[str, Any]] = []
        self.issue_backlog: List[Dict[str, Any]] = []
        self._period_start: Optional[str] = None
        self._running = False

        # 全周期累积指标
        self.total_code_lines = 0
        self.total_test_cases = 0
        self.total_deployments = 0
        self.total_deployment_ok = 0

        # 演进任务 (从 SystemEvolutionChannel 接收)
        self._evolution_tasks: List[Dict[str, Any]] = []

    # ── Agent 初始化 ──────────────────────────────────────────

    def _init_agents(self):
        definitions = [
            {
                "id": "build_researcher",
                "role": AgentRole.RESEARCHER,
                "name": "Marine Research Agent",
                "description": "每 15 分钟从 marine_engineer 知识库获取研究信息，反馈给架构师",
                "schedule_interval_sec": self.SCHEDULE[AgentRole.RESEARCHER],
            },
            {
                "id": "build_architect",
                "role": AgentRole.ARCHITECT,
                "name": "System Architect Agent",
                "description": "每 30 分钟产出架构设计方案，下发给开发成员",
                "schedule_interval_sec": self.SCHEDULE[AgentRole.ARCHITECT],
            },
            {
                "id": "build_developer",
                "role": AgentRole.DEVELOPER,
                "name": "Code Developer Agent",
                "description": "每 10 分钟汇报代码增量，通知测试人员",
                "schedule_interval_sec": self.SCHEDULE[AgentRole.DEVELOPER],
            },
            {
                "id": "build_tester",
                "role": AgentRole.TESTER,
                "name": "QA & Test Agent",
                "description": "每 15 分钟汇报 test case 数量，通知部署工程师",
                "schedule_interval_sec": self.SCHEDULE[AgentRole.TESTER],
            },
            {
                "id": "build_deployer",
                "role": AgentRole.DEPLOYER,
                "name": "Deployment Agent",
                "description": "每 1 小时部署一次系统，发现问题找 Developer 修",
                "schedule_interval_sec": self.SCHEDULE[AgentRole.DEPLOYER],
            },
        ]
        for defn in definitions:
            agent = BuildAgent(
                id=defn["id"],
                role=defn["role"],
                name=defn["name"],
                description=defn["description"],
                llm_backend=self.llm_backend,
                schedule_interval_sec=defn["schedule_interval_sec"],
            )
            self.agents[agent.id] = agent

    # ── MarineChannel 接口 ───────────────────────────────────

    def initialize(self) -> bool:
        self._initialized = True
        self._running = True
        self._period_start = datetime.now().isoformat()
        for agent in self.agents.values():
            agent.state = AgentState.IDLE
            agent.last_heartbeat = datetime.now().isoformat()
        self._set_health(ChannelStatus.OK, "构建团队就绪，5 名 Agent 已上线")
        logger.info("🏗️ Build Team Manager initialized (%d agents)", len(self.agents))
        return True

    def shutdown(self) -> bool:
        self._running = False
        self._initialized = False
        for agent in self.agents.values():
            agent.state = AgentState.IDLE
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True

    # ── 调度 & 执行 ──────────────────────────────────────────

    def tick(self, now: Optional[datetime] = None) -> Dict[str, Any]:
        """外部定时调用，驱动所有 Agent 按节奏执行任务."""
        now = now or datetime.now()
        results: Dict[str, Any] = {}
        for agent in self.agents.values():
            if self._should_run(agent, now):
                result = self._execute_agent_cycle(agent, now)
                results[agent.id] = result
        return results

    def _should_run(self, agent: BuildAgent, now: datetime) -> bool:
        if not agent.last_heartbeat:
            return True
        try:
            last = datetime.fromisoformat(agent.last_heartbeat)
            elapsed = (now - last).total_seconds()
            return elapsed >= agent.schedule_interval_sec
        except (ValueError, TypeError):
            return True

    def _execute_agent_cycle(self, agent: BuildAgent, now: datetime) -> Dict[str, Any]:
        """执行单个 Agent 的一个调度周期."""
        agent.state = AgentState.WORKING
        agent.last_heartbeat = now.isoformat()
        cycle_start = time.monotonic()

        result: Dict[str, Any] = {"agent": agent.id, "role": agent.role.value, "time": now.isoformat()}

        try:
            if agent.role == AgentRole.RESEARCHER:
                result.update(self._run_researcher(agent, now))
            elif agent.role == AgentRole.ARCHITECT:
                result.update(self._run_architect(agent, now))
            elif agent.role == AgentRole.DEVELOPER:
                result.update(self._run_developer(agent, now))
            elif agent.role == AgentRole.TESTER:
                result.update(self._run_tester(agent, now))
            elif agent.role == AgentRole.DEPLOYER:
                result.update(self._run_deployer(agent, now))

            agent.kpi.tasks_completed += 1
            agent.state = AgentState.REPORTING
        except Exception as exc:
            agent.kpi.tasks_failed += 1
            agent.state = AgentState.ERROR
            result["error"] = str(exc)
            logger.error("Agent %s cycle failed: %s", agent.id, exc)

        elapsed = time.monotonic() - cycle_start
        n = agent.kpi.tasks_completed + agent.kpi.tasks_failed
        agent.kpi.avg_cycle_seconds = (
            (agent.kpi.avg_cycle_seconds * (n - 1) + elapsed) / n if n else elapsed
        )
        agent.kpi.last_report_at = now.isoformat()
        agent.state = AgentState.IDLE

        self.event_log.append(result)
        return result

    # ── 各角色执行逻辑 ───────────────────────────────────────

    def _run_researcher(self, agent: BuildAgent, now: datetime) -> Dict[str, Any]:
        """研究员：从 marine_engineer 知识库获取研究信息."""
        research_topics = [
            "双体船结构疲劳寿命评估最新算法",
            "IMO MASS 远程操控合规要求更新",
            "深海抓斗系统液压伺服控制优化",
            "船舶 CPS 联合仿真集成方案",
            "WorldMonitor AIS 数据融合最佳实践",
        ]
        topic_idx = agent.kpi.tasks_completed % len(research_topics)
        topic = research_topics[topic_idx]

        findings = {
            "topic": topic,
            "source": "marine_engineer_knowledge_base",
            "summary": f"[{now.strftime('%H:%M')}] 关于「{topic}」的最新研究摘要已就绪",
            "recommendations": [
                f"建议架构师评估 {topic} 对 L2 感知层的影响",
                f"建议开发团队为 {topic} 预留接口",
            ],
        }

        # 投递给架构师
        arch = self.agents.get("build_architect")
        if arch:
            arch.task_queue.append(f"review_research:{topic}")

        agent.kpi.deliverables += 1
        return {"action": "research", "findings": findings}

    def _run_architect(self, agent: BuildAgent, now: datetime) -> Dict[str, Any]:
        """架构师：消费研究结果，产出设计方案，下发任务到开发."""
        pending_research = [t for t in agent.task_queue if t.startswith("review_research:")]
        agent.task_queue = [t for t in agent.task_queue if not t.startswith("review_research:")]

        design = {
            "reviewed_topics": len(pending_research),
            "design_decision": f"[{now.strftime('%H:%M')}] 架构方案已更新",
            "new_tasks": [],
        }

        # 为每条研究生成开发任务
        dev = self.agents.get("build_developer")
        for item in pending_research[:3]:
            task_name = item.replace("review_research:", "implement:")
            design["new_tasks"].append(task_name)
            if dev:
                dev.task_queue.append(task_name)

        agent.kpi.deliverables += 1
        return {"action": "design", "design": design}

    def _run_developer(self, agent: BuildAgent, now: datetime) -> Dict[str, Any]:
        """开发者：消费开发任务，汇报代码增量，通知测试."""
        pending = list(agent.task_queue)
        agent.task_queue = []

        # 模拟代码增量 (每周期 ~30 行)
        lines_added = max(10, 30 * len(pending) if pending else 15)
        self.total_code_lines += lines_added
        agent.kpi.deliverables += lines_added

        # 通知测试
        tester = self.agents.get("build_tester")
        if tester:
            tester.task_queue.append(f"test_increment:{lines_added}_lines")

        return {
            "action": "develop",
            "tasks_processed": len(pending),
            "lines_added": lines_added,
            "total_lines": self.total_code_lines,
        }

    def _run_tester(self, agent: BuildAgent, now: datetime) -> Dict[str, Any]:
        """测试员：编写 & 执行测试，汇报 test case 数."""
        pending = list(agent.task_queue)
        agent.task_queue = []

        new_cases = max(3, 5 * len(pending) if pending else 3)
        self.total_test_cases += new_cases
        agent.kpi.deliverables += new_cases

        # 模拟通过率
        passed = int(new_cases * 0.92)
        failed = new_cases - passed

        # 将失败项反馈给开发
        if failed > 0:
            dev = self.agents.get("build_developer")
            if dev:
                dev.task_queue.append(f"fix_test_failures:{failed}")
            self.issue_backlog.append({
                "type": "test_failure",
                "count": failed,
                "reported_at": now.isoformat(),
            })

        # 通知部署
        deployer = self.agents.get("build_deployer")
        if deployer and passed == new_cases:
            deployer.task_queue.append("deploy_ready")

        return {
            "action": "test",
            "new_cases": new_cases,
            "passed": passed,
            "failed": failed,
            "total_cases": self.total_test_cases,
        }

    def _run_deployer(self, agent: BuildAgent, now: datetime) -> Dict[str, Any]:
        """部署工程师：执行系统部署."""
        pending = list(agent.task_queue)
        agent.task_queue = []

        self.total_deployments += 1
        agent.kpi.deliverables += 1

        # 模拟部署结果 (90% 首次成功率)
        success = len(self.issue_backlog) == 0 or (self.total_deployments % 10 != 0)
        if success:
            self.total_deployment_ok += 1

        if not success:
            dev = self.agents.get("build_developer")
            if dev:
                dev.task_queue.append("fix_deployment_issue")
            self.issue_backlog.append({
                "type": "deployment_failure",
                "reported_at": now.isoformat(),
            })

        return {
            "action": "deploy",
            "success": success,
            "total_deployments": self.total_deployments,
            "total_ok": self.total_deployment_ok,
            "success_rate": self.total_deployment_ok / self.total_deployments,
        }

    # ── 汇报 ────────────────────────────────────────────────

    def generate_hourly_report(self) -> HourlyReport:
        """生成每小时汇报."""
        now = datetime.now().isoformat()
        report = HourlyReport(
            timestamp=now,
            period_start=self._period_start or now,
            period_end=now,
            code_lines_added=self.total_code_lines,
            test_cases_total=self.total_test_cases,
            test_cases_passed=int(self.total_test_cases * 0.92),
            deployment_attempts=self.total_deployments,
            deployment_successes=self.total_deployment_ok,
            research_updates=self.agents["build_researcher"].kpi.tasks_completed,
            architecture_decisions=self.agents["build_architect"].kpi.deliverables,
            issues_found=len(self.issue_backlog),
            issues_resolved=len([i for i in self.issue_backlog if i.get("resolved")]),
            agents_summary={
                aid: {
                    "state": a.state.value,
                    "tasks_completed": a.kpi.tasks_completed,
                    "deliverables": a.kpi.deliverables,
                    "utilization_pct": round(a.kpi.utilization_pct, 1),
                }
                for aid, a in self.agents.items()
            },
        )
        self.hourly_reports.append(report)
        self._period_start = now
        return report

    def get_agent_kpis(self) -> Dict[str, Any]:
        """获取所有 Agent 的 KPI 考核数据."""
        return {
            aid: {
                "role": a.role.value,
                "name": a.name,
                "state": a.state.value,
                "tasks_completed": a.kpi.tasks_completed,
                "tasks_failed": a.kpi.tasks_failed,
                "deliverables": a.kpi.deliverables,
                "avg_cycle_seconds": round(a.kpi.avg_cycle_seconds, 2),
                "last_report": a.kpi.last_report_at,
                "pending_tasks": len(a.task_queue),
                "score": self._calculate_agent_score(a),
            }
            for aid, a in self.agents.items()
        }

    def _calculate_agent_score(self, agent: BuildAgent) -> float:
        """根据角色计算考核分数 (0-100)."""
        base = min(100, agent.kpi.tasks_completed * 10)
        fail_penalty = agent.kpi.tasks_failed * 5
        return max(0, base - fail_penalty)

    def assign_task(self, agent_id: str, task: str) -> bool:
        """手动分配任务给指定 Agent."""
        agent = self.agents.get(agent_id)
        if not agent:
            return False
        agent.task_queue.append(task)
        return True

    def nudge_idle_agents(self) -> List[str]:
        """督促空闲 Agent 立即工作."""
        nudged = []
        now = datetime.now()
        for agent in self.agents.values():
            if agent.state == AgentState.IDLE and not agent.task_queue:
                agent.task_queue.append("proactive_scan")
                nudged.append(agent.id)
        return nudged

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
                "total_code_lines": self.total_code_lines,
                "total_test_cases": self.total_test_cases,
                "total_deployments": self.total_deployments,
                "deployment_success_rate": (
                    self.total_deployment_ok / max(self.total_deployments, 1)
                ),
                "issues_backlog": len(self.issue_backlog),
                "evolution_tasks_received": len(self._evolution_tasks),
            },
            "hourly_reports_count": len(self.hourly_reports),
            "latest_report": self.hourly_reports[-1].to_dict() if self.hourly_reports else None,
        }

    # ── 演进反馈接口 (供 SystemEvolutionChannel 调用) ────────

    def accept_evolution_feedback(
        self, item_id: str, title: str, severity: str = "medium",
        target_channel: str = "", detail: str = "",
    ) -> Dict[str, Any]:
        """接收来自自我演进引擎的修改任务。"""
        task = {
            "item_id": item_id,
            "title": title,
            "severity": severity,
            "target_channel": target_channel,
            "detail": detail,
            "received_at": datetime.now().isoformat(),
            "status": "pending",
        }
        self._evolution_tasks.append(task)

        # 根据严重程度分配给对应 Agent
        agent_id = "build_developer" if severity in ("critical", "high") else "build_architect"
        agent = self.agents.get(agent_id)
        if agent:
            agent.task_queue.append(f"evolution_fix:{item_id}:{title}")

        logger.info("🔧 Build team received evolution task: %s [%s]", title, severity)
        return {"status": "accepted", "item_id": item_id, "assigned_to": agent_id}

    def get_evolution_tasks(self) -> List[Dict[str, Any]]:
        """查询所有收到的演进任务。"""
        return list(self._evolution_tasks)


__all__ = [
    "BuildTeamManagerChannel",
    "BuildAgent",
    "AgentRole",
    "AgentState",
    "HourlyReport",
]
