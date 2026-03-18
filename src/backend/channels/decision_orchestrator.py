# -*- coding: utf-8 -*-
"""
Decision Orchestrator Channel - 全场景决策与运维生成骨架
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelPriority, ChannelStatus, get_default_registry

logger = logging.getLogger(f"{__name__}.decision_orchestrator")


PRIORITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


class DecisionOrchestratorChannel(MarineChannel):
    name = "decision_orchestrator"
    description = "全场景决策与运维编排 (风险摘要 + 运维动作 + 反馈闭环)"
    version = "0.1.0"
    priority = ChannelPriority.P0
    dependencies: List[str] = [
        "compliance_digital_expert",
        "distributed_perception_hub",
        "intelligent_navigation",
        "intelligent_engine",
        "energy_efficiency",
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.config = config or {}
        self._config = self.config
        self.feedback_records: List[Dict[str, Any]] = []
        self.latest_package: Dict[str, Any] = {}
        self.last_coordination_at: Optional[str] = None
        self.coordination_runs = 0
        self.event_sink = self.config.get("event_sink")

    def set_event_sink(self, event_sink: Any) -> None:
        """设置协调层事件持久化目标。"""
        self.event_sink = event_sink

    def initialize(self) -> bool:
        self._initialized = True
        self._set_health(ChannelStatus.OK, "全场景决策编排器已就绪")
        logger.info("✅ Decision Orchestrator initialized")
        return True

    def _build_action_plan(
        self,
        snapshot: Dict[str, Any],
        nav_report: Dict[str, Any],
        engine_status: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        action_plan: List[Dict[str, Any]] = []
        generated_at = datetime.now().isoformat()

        for item in nav_report.get("colregs_assessments", [])[:3]:
            action_plan.append(
                {
                    "id": f"nav-{item['target_mmsi']}",
                    "domain": "navigation",
                    "priority": "critical" if item["risk_level"] == "danger" else "high",
                    "title": f"{item['encounter_type']} risk with target {item['target_mmsi']}",
                    "rationale": item["summary"],
                    "rule": item["rule"],
                    "recommended_action": item["recommended_action"],
                    "execute_before": generated_at,
                }
            )

        for alert in engine_status.get("alerts", [])[:2]:
            action_plan.append(
                {
                    "id": f"eng-{abs(hash(alert.get('message', 'engine'))) % 100000}",
                    "domain": "engine",
                    "priority": "critical" if alert.get("level") == "critical" else "high",
                    "title": alert.get("message", "Engine alert"),
                    "rationale": "Engine subsystem health requires operator confirmation.",
                    "rule": "Machinery Safety",
                    "recommended_action": "Dispatch engine room verification and reduce propulsion stress if required.",
                    "execute_before": generated_at,
                }
            )

        energy_rec = snapshot.get("engineering_parameters", {}).get("energy", {}).get("recommendations", [])
        for rec in energy_rec[:2]:
            action_plan.append(
                {
                    "id": f"ene-{abs(hash(rec['title'])) % 100000}",
                    "domain": "energy",
                    "priority": rec.get("priority", "medium"),
                    "title": rec["title"],
                    "rationale": "Improve compliance and voyage efficiency margins.",
                    "rule": "CII/EEXI/SEEMP",
                    "recommended_action": rec["title"],
                    "expected_improvement": rec.get("expected_improvement"),
                    "execute_before": generated_at,
                }
            )

        if not action_plan:
            action_plan.append(
                {
                    "id": "ops-monitor",
                    "domain": "operations",
                    "priority": "low",
                    "title": "Maintain supervised monitoring",
                    "rationale": "No high-priority anomaly has been detected in the current cycle.",
                    "rule": "Baseline supervision",
                    "recommended_action": "Continue watchkeeping and preserve current control setpoints.",
                    "execute_before": generated_at,
                }
            )

        action_plan.sort(key=lambda item: PRIORITY_RANK.get(item["priority"], 9))
        return action_plan

    def _build_task_graph(
        self,
        action_plan: List[Dict[str, Any]],
        autonomy_mode: str,
        snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        generated_at = datetime.now().isoformat()
        nodes: List[Dict[str, Any]] = [
            {
                "id": "mission",
                "type": "mission",
                "label": "CPS mission brief",
                "status": snapshot.get("compliance_status", "unknown"),
                "priority": snapshot.get("risk_level", "unknown"),
            }
        ]
        edges: List[Dict[str, str]] = []
        execution_order: List[str] = []

        seen_domains = set()
        for item in action_plan:
            domain_id = f"domain:{item['domain']}"
            if domain_id not in seen_domains:
                nodes.append(
                    {
                        "id": domain_id,
                        "type": "domain",
                        "label": item["domain"],
                        "status": "ready",
                        "priority": item["priority"],
                    }
                )
                edges.append({"from": "mission", "to": domain_id, "relation": "dispatches"})
                seen_domains.add(domain_id)

            task_id = f"task:{item['id']}"
            nodes.append(
                {
                    "id": task_id,
                    "type": "task",
                    "label": item["title"],
                    "status": "ready",
                    "priority": item["priority"],
                    "execute_before": item.get("execute_before", generated_at),
                }
            )
            edges.append({"from": domain_id, "to": task_id, "relation": "contains"})
            execution_order.append(task_id)

        return {
            "generated_at": generated_at,
            "autonomy_mode": autonomy_mode,
            "nodes": nodes,
            "edges": edges,
            "execution_order": execution_order,
            "feedback_channel": "decision_feedback_event",
        }

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        logger.info("🛑 Decision Orchestrator shutdown")
        return True

    def build_decision_package(self) -> Dict[str, Any]:
        registry = get_default_registry()
        compliance = registry.get("compliance_digital_expert")
        perception = registry.get("distributed_perception_hub")
        navigation = registry.get("intelligent_navigation")
        engine = registry.get("intelligent_engine")
        logger.debug("📦 Building decision package...")
        snapshot = compliance.query_compliance_status("overall") if compliance and hasattr(compliance, "query_compliance_status") else {}
        latest_events = perception.get_latest_events(10) if perception and hasattr(perception, "get_latest_events") else []
        nav_report = navigation.generate_navigation_report() if navigation and hasattr(navigation, "generate_navigation_report") else {}
        engine_status = engine.get_status() if engine else {}
        action_plan = self._build_action_plan(snapshot, nav_report, engine_status)
        autonomy_mode = "supervised_autonomy" if snapshot.get("risk_level") in {"medium", "high"} else "advisory"
        task_graph = self._build_task_graph(action_plan, autonomy_mode, snapshot)
        package = {
            "generated_at": datetime.now().isoformat(),
            "risk_level": snapshot.get("risk_level", "unknown"),
            "compliance_status": snapshot.get("compliance_status", "unknown"),
            "summary": f"航行风险 {snapshot.get('risk_level', 'unknown')}，当前需要执行 {len(action_plan)} 个跨域动作。",
            "autonomy_mode": autonomy_mode,
            "recommended_actions": snapshot.get("recommended_actions", []),
            "action_plan": action_plan,
            "task_graph": task_graph,
            "mission_brief": {
                "operational_picture": {
                    "overall_status": nav_report.get("overall_status", "unknown"),
                    "active_risks": len(nav_report.get("collision_risks", [])),
                    "engine_alerts": len(engine_status.get("alerts", [])),
                    "recent_events": len(latest_events),
                },
                "control_objectives": [
                    "Preserve safe CPA/TCPA margins under COLREGs constraints.",
                    "Protect propulsion and cooling subsystem availability.",
                    "Maintain efficiency and compliance within voyage limits.",
                ],
                "execution_style": autonomy_mode,
                "watchstanding_note": snapshot.get("recommended_actions", ["Maintain normal watch."])[0],
            },
            "maintenance_report": snapshot.get("maintenance_report", {}),
            "supporting_evidence": snapshot.get("evidence", []),
            "latest_events": latest_events,
            "feedback_records": self.feedback_records[-10:],
            "component_status": {
                "navigation": nav_report.get("risk_index", {}),
                "engine": {
                    "health": engine_status.get("health"),
                    "health_score": engine_status.get("engine_health_score"),
                },
            },
            "kpi_targets": {
                "minimum_dcpa_nm": getattr(navigation, "dcpa_limit", None),
                "maximum_tcpa_min": getattr(navigation, "tcpa_limit", None),
                "engine_health_score_floor": 85,
                "decision_latency_target_ms": 200,
            },
        }
        self.latest_package = package
        return package

    def coordinate_agents(self, event_sink: Optional[Any] = None) -> Dict[str, Any]:
        """执行一次跨智能体协调循环。"""
        registry = get_default_registry()
        perception = registry.get("distributed_perception_hub")

        captured_events: List[Dict[str, Any]] = []
        if perception and hasattr(perception, "capture_system_snapshot"):
            try:
                snapshot_events = perception.capture_system_snapshot()
                captured_events = [event.to_dict() for event in snapshot_events]
                perception_sink = getattr(perception, "event_sink", None)
                if event_sink and captured_events and perception_sink is not event_sink:
                    event_sink.save_batch(captured_events)
            except Exception as exc:
                logger.warning(f"Perception snapshot during coordination failed: {exc}")

        package = self.build_decision_package()
        decision_event = {
            "timestamp": package["generated_at"],
            "event_type": "decision_package_event",
            "source": self.name,
            "payload": package,
            "confidence": 1.0,
        }
        if event_sink:
            event_sink.save_event(decision_event)

        self.coordination_runs += 1
        self.last_coordination_at = package["generated_at"]

        return {
            "timestamp": self.last_coordination_at,
            "captured_events": len(captured_events),
            "decision_risk_level": package.get("risk_level", "unknown"),
            "recommended_actions_count": len(package.get("recommended_actions", [])),
            "coordination_runs": self.coordination_runs,
        }

    def record_feedback(self, action: str, outcome: str, confirmed_by: str = "system") -> Dict[str, Any]:
        record = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "outcome": outcome,
            "confirmed_by": confirmed_by,
        }
        self.feedback_records.append(record)
        if self.event_sink:
            try:
                self.event_sink.save_event(
                    {
                        "timestamp": record["timestamp"],
                        "event_type": "decision_feedback_event",
                        "source": self.name,
                        "payload": {
                            **record,
                            "coordination_runs": self.coordination_runs,
                            "decision_generated_at": self.latest_package.get("generated_at"),
                        },
                        "confidence": 1.0,
                    }
                )
            except Exception as exc:
                logger.warning(f"Failed to persist decision feedback: {exc}")
        return record

    def get_status(self) -> Dict[str, Any]:
        package = self.build_decision_package()
        return {
            "name": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "health_message": self._health.message,
            "risk_level": package["risk_level"],
            "compliance_status": package["compliance_status"],
            "recommended_actions_count": len(package["recommended_actions"]),
            "action_plan_count": len(package.get("action_plan", [])),
            "task_graph_nodes": len(package.get("task_graph", {}).get("nodes", [])),
            "feedback_records_count": len(self.feedback_records),
            "coordination_runs": self.coordination_runs,
            "last_coordination_at": self.last_coordination_at,
            "autonomy_mode": package.get("autonomy_mode"),
        }

    async def build_decision_package_async(self) -> Dict[str, Any]:
        """异步构建决策包."""
        return await asyncio.get_event_loop().run_in_executor(None, self.build_decision_package)

    async def record_feedback_async(self, action: str, outcome: str, confirmed_by: str = "system") -> Dict[str, Any]:
        """异步记录反馈."""
        return await asyncio.get_event_loop().run_in_executor(None, self.record_feedback, action, outcome, confirmed_by)


__all__ = ["DecisionOrchestratorChannel"]
