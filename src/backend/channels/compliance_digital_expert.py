# -*- coding: utf-8 -*-
"""
Compliance Digital Expert Channel - 船舶合规数字专家

聚合导航、机舱、能效状态，输出统一的风险、合规、建议和证据结构。
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelPriority, ChannelStatus, get_default_registry

logger = logging.getLogger(f"{__name__}.compliance_digital_expert")


RISK_ORDER = {"low": 0, "medium": 1, "high": 2}
POSITIVE_OUTCOMES = {"success", "positive_outcome", "confirmed", "effective", "resolved"}


class ComplianceDigitalExpertChannel(MarineChannel):
    name = "compliance_digital_expert"
    description = "船舶合规数字专家 (COLREGs/机舱/能效统一认知层)"
    version = "0.1.0"
    priority = ChannelPriority.P0
    dependencies: List[str] = ["intelligent_navigation", "intelligent_engine", "energy_efficiency"]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.config = config or {}
        self._config = self.config
        self.knowledge_rules = {
            "COLREGs": {
                "rule_5": "保持正规瞭望。",
                "rule_7": "使用一切适当手段判断碰撞危险。",
                "rule_8": "避碰行动应及早、明显并有效。",
            },
            "ENGINE": {
                "cooling": "冷却异常需优先排查海水回路、换热器和循环泵。",
                "lubrication": "润滑异常需优先检查滑油液位、滤器和油泵。",
            },
            "EFFICIENCY": {
                "cii": "持续跟踪 CII 与燃油消耗，避免评级下滑。",
                "seemp": "建议把能效偏差纳入 SEEMP 闭环管理。",
            },
        }

    def initialize(self) -> bool:
        self._initialized = True
        self._set_health(ChannelStatus.OK, "船舶合规数字专家已就绪")
        logger.info("✅ Compliance Digital Expert initialized")
        return True

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        logger.info("🛑 Compliance Digital Expert shutdown")
        return True

    def _registry(self):
        return get_default_registry()

    def _get_channel_status(self, name: str) -> Dict[str, Any]:
        channel = self._registry().get(name)
        if not channel:
            return {"available": False, "name": name}
        try:
            status = channel.get_status()
            status["available"] = True
            return status
        except Exception as exc:
            return {"available": False, "name": name, "error": str(exc)}

    def _max_risk(self, current: str, candidate: str) -> str:
        return candidate if RISK_ORDER.get(candidate, -1) > RISK_ORDER.get(current, -1) else current

    def _build_learning_state(
        self,
        evidence: List[str],
        colregs_assessment: List[Dict[str, Any]],
        engine_findings: List[Dict[str, Any]],
        energy_recommendations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        orchestrator = self._registry().get("decision_orchestrator")
        feedback_records = getattr(orchestrator, "feedback_records", []) if orchestrator else []
        recent_feedback = feedback_records[-10:]
        positive_feedback = sum(1 for item in recent_feedback if item.get("outcome") in POSITIVE_OUTCOMES)
        total_feedback = len(recent_feedback)
        positive_ratio = round(positive_feedback / total_feedback, 2) if total_feedback else 0.0

        rule_confidence = {
            "COLREGs": round(min(0.99, 0.58 + 0.05 * len(colregs_assessment) + 0.12 * positive_ratio), 2),
            "ENGINE": round(min(0.99, 0.56 + 0.04 * len(engine_findings) + 0.10 * positive_ratio), 2),
            "EFFICIENCY": round(min(0.99, 0.54 + 0.03 * len(energy_recommendations) + 0.08 * positive_ratio), 2),
        }

        return {
            "learning_mode": "feedback_adaptive" if total_feedback else "cold_start",
            "feedback_events": len(feedback_records),
            "recent_feedback_window": total_feedback,
            "positive_feedback_ratio": positive_ratio,
            "retained_evidence": len(evidence),
            "rule_confidence": rule_confidence,
            "last_feedback": recent_feedback[-1] if recent_feedback else None,
        }

    def build_cognitive_snapshot(self) -> Dict[str, Any]:
        nav = self._get_channel_status("intelligent_navigation")
        engine = self._get_channel_status("intelligent_engine")
        efficiency = self._get_channel_status("energy_efficiency")
        perception = self._get_channel_status("distributed_perception_hub")

        risk_level = "low"
        evidence: List[str] = []
        actions: List[str] = []
        compliance_status = "compliant"

        logger.debug("🧠 Building cognitive snapshot...")

        nav_report = {}
        colregs_assessment: List[Dict[str, Any]] = []
        nav_channel = self._registry().get("intelligent_navigation")
        if nav_channel and hasattr(nav_channel, "generate_navigation_report"):
            nav_report = nav_channel.generate_navigation_report()
            overall = nav_report.get("overall_status")
            if overall in {"danger", "warning"}:
                risk_level = self._max_risk(risk_level, "high" if overall == "danger" else "medium")
                evidence.append(f"navigation:{overall}")
                actions.append("依据 COLREGs 规则复核避碰动作与瞭望状态")
            colregs_assessment = nav_report.get("colregs_assessments", [])
            if colregs_assessment:
                evidence.extend(
                    [f"colregs:{item['encounter_type']}:{item['rule']}" for item in colregs_assessment[:3]]
                )
                actions.extend([item["recommended_action"] for item in colregs_assessment[:2]])

        engine_alerts = engine.get("alerts", []) if engine.get("available") else []
        engine_findings: List[Dict[str, Any]] = []
        engine_channel = self._registry().get("intelligent_engine")
        if engine_channel and hasattr(engine_channel, "diagnose_faults"):
            engine_findings = engine_channel.diagnose_faults()
        if engine_alerts:
            risk_level = self._max_risk(
                risk_level,
                "high" if any(a.get("level") == "critical" for a in engine_alerts) else "medium",
            )
            evidence.extend([f"engine:{a.get('message','alert')}" for a in engine_alerts[:3]])
            actions.append("执行机舱点检并确认故障诊断结果")
            compliance_status = "attention_required"
        if engine_findings:
            evidence.extend([f"engine_fault:{item['fault_type']}" for item in engine_findings[:3]])
            actions.extend([item["recommended_action"] for item in engine_findings[:2]])

        if efficiency.get("health") not in {None, "ok"}:
            evidence.append(f"efficiency:{efficiency.get('health_message', 'deviation detected')}")
            actions.append("检查 CII / EEXI / SEEMP 偏差并生成能效纠偏动作")
            compliance_status = "attention_required"

        energy_channel = self._registry().get("energy_efficiency")
        energy_recommendations: List[Dict[str, Any]] = []
        if energy_channel and hasattr(energy_channel, "get_recommendations"):
            try:
                energy_recommendations = [
                    {
                        "title": rec.title,
                        "priority": rec.priority,
                        "expected_improvement": rec.expected_improvement,
                    }
                    for rec in energy_channel.get_recommendations()[:3]
                ]
            except Exception as exc:
                logger.debug(f"Energy recommendation build skipped: {exc}")
        if energy_recommendations:
            evidence.extend([f"energy:{rec['title']}" for rec in energy_recommendations[:2]])
            actions.extend([rec["title"] for rec in energy_recommendations[:2]])

        recent_events = []
        perception_channel = self._registry().get("distributed_perception_hub")
        if perception_channel and hasattr(perception_channel, "get_latest_events"):
            recent_events = perception_channel.get_latest_events(5)
        if recent_events:
            evidence.append(f"perception:recent_events:{len(recent_events)}")

        learning_state = self._build_learning_state(
            evidence,
            colregs_assessment,
            engine_findings,
            energy_recommendations,
        )

        rules = [
            self.knowledge_rules["COLREGs"]["rule_7"],
            self.knowledge_rules["COLREGs"]["rule_8"],
        ]
        if engine_alerts:
            rules.append(self.knowledge_rules["ENGINE"]["lubrication"])
        if efficiency.get("available"):
            rules.append(self.knowledge_rules["EFFICIENCY"]["cii"])

        dedup_actions = []
        for item in actions or ["当前系统无高优先级异常，维持监控。"]:
            if item not in dedup_actions:
                dedup_actions.append(item)

        return {
            "timestamp": datetime.now().isoformat(),
            "risk_level": risk_level,
            "compliance_status": compliance_status,
            "evidence": evidence,
            "recommended_actions": dedup_actions or ["当前系统无高优先级异常，维持监控。"],
            "maintenance_report": self.generate_maintenance_report(),
            "rules": rules,
            "expert_cognition": {
                "perception": {
                    "recent_events_count": len(recent_events),
                    "fusion_health": perception.get("health", "unknown"),
                },
                "memory": {
                    "feedback_ready": True,
                    "retained_evidence": len(evidence),
                },
                "thinking": {
                    "colregs_cases": len(colregs_assessment),
                    "engine_findings": len(engine_findings),
                    "energy_actions": len(energy_recommendations),
                },
                "learning": {
                    "closed_loop_feedback": learning_state["feedback_events"] > 0,
                    "feedback_events": learning_state["feedback_events"],
                    "positive_feedback_ratio": learning_state["positive_feedback_ratio"],
                    "next_focus": "risk_mitigation" if risk_level != "low" else "efficiency_optimization",
                },
            },
            "learning_state": learning_state,
            "engineering_parameters": {
                "navigation": nav.get("risk_thresholds", {}),
                "engine": {
                    "health_score": engine.get("engine_health_score"),
                    "trend": engine.get("trend"),
                },
                "energy": {
                    "vessel": efficiency.get("vessel"),
                    "recommendations": energy_recommendations,
                },
            },
            "navigation": nav_report or nav,
            "engine": engine,
            "efficiency": efficiency,
            "perception": {
                "status": perception,
                "recent_events": recent_events,
            },
        }

    def generate_maintenance_report(self) -> Dict[str, Any]:
        engine_channel = self._registry().get("intelligent_engine")
        advice = []
        if engine_channel and hasattr(engine_channel, "get_maintenance_advice"):
            advice = engine_channel.get_maintenance_advice()
        return {
            "title": "AI Native 运维摘要",
            "generated_at": datetime.now().isoformat(),
            "summary": "基于导航、机舱、能效的统一认知摘要。",
            "actions": advice[:5] if advice else ["暂无新增维护动作。"],
        }

    def query_compliance_status(self, query: str = "") -> Dict[str, Any]:
        snapshot = self.build_cognitive_snapshot()
        if "机舱" in query or "engine" in query.lower():
            snapshot["focus"] = "engine"
        elif "导航" in query or "避碰" in query:
            snapshot["focus"] = "navigation"
        elif "能效" in query or "cii" in query.lower():
            snapshot["focus"] = "efficiency"
        else:
            snapshot["focus"] = "overall"
        return snapshot

    def explain_navigation_decision(self) -> Dict[str, Any]:
        snapshot = self.build_cognitive_snapshot()
        return {
            "focus": "navigation",
            "risk_level": snapshot["risk_level"],
            "evidence": snapshot["evidence"],
            "rules": [self.knowledge_rules["COLREGs"]["rule_7"], self.knowledge_rules["COLREGs"]["rule_8"]],
        }

    def explain_engine_alert(self) -> Dict[str, Any]:
        snapshot = self.build_cognitive_snapshot()
        return {
            "focus": "engine",
            "maintenance_report": snapshot["maintenance_report"],
            "recommended_actions": snapshot["recommended_actions"],
        }

    def get_status(self) -> Dict[str, Any]:
        cognitive = self.build_cognitive_snapshot()
        return {
            "name": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "health_message": self._health.message,
            "risk_level": cognitive["risk_level"],
            "compliance_status": cognitive["compliance_status"],
            "evidence_count": len(cognitive["evidence"]),
            "recommended_actions_count": len(cognitive["recommended_actions"]),
        }

    async def build_cognitive_snapshot_async(self) -> Dict[str, Any]:
        """异步构建认知快照."""
        return await asyncio.get_event_loop().run_in_executor(None, self.build_cognitive_snapshot)

    async def query_compliance_status_async(self, query: str = "") -> Dict[str, Any]:
        """异步查询合规状态."""
        return await asyncio.get_event_loop().run_in_executor(None, self.query_compliance_status, query)


__all__ = ["ComplianceDigitalExpertChannel"]
