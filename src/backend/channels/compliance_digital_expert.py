# -*- coding: utf-8 -*-
"""
Compliance Digital Expert Channel - 船舶合规数字专家

聚合导航、机舱、能效状态，输出统一的风险、合规、建议和证据结构。
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelPriority, ChannelStatus, get_default_registry

logger = logging.getLogger(f"{__name__}.compliance_digital_expert")


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

    def build_cognitive_snapshot(self) -> Dict[str, Any]:
        nav = self._get_channel_status("intelligent_navigation")
        engine = self._get_channel_status("intelligent_engine")
        efficiency = self._get_channel_status("energy_efficiency")

        risk_level = "low"
        evidence: List[str] = []
        actions: List[str] = []
        compliance_status = "compliant"

        logger.debug("🧠 Building cognitive snapshot...")

        nav_report = {}
        nav_channel = self._registry().get("intelligent_navigation")
        if nav_channel and hasattr(nav_channel, "generate_navigation_report"):
            nav_report = nav_channel.generate_navigation_report()
            overall = nav_report.get("overall_status")
            if overall in {"danger", "warning"}:
                risk_level = "high" if overall == "danger" else "medium"
                evidence.append(f"navigation:{overall}")
                actions.append("依据 COLREGs 规则复核避碰动作与瞭望状态")

        engine_alerts = engine.get("alerts", []) if engine.get("available") else []
        if engine_alerts:
            risk_level = "high" if any(a.get("level") == "critical" for a in engine_alerts) else max(risk_level, "medium")
            evidence.extend([f"engine:{a.get('message','alert')}" for a in engine_alerts[:3]])
            actions.append("执行机舱点检并确认故障诊断结果")
            compliance_status = "attention_required"

        if efficiency.get("health") not in {None, "ok"}:
            evidence.append(f"efficiency:{efficiency.get('health_message', 'deviation detected')}")
            actions.append("检查 CII / EEXI / SEEMP 偏差并生成能效纠偏动作")
            compliance_status = "attention_required"

        rules = [
            self.knowledge_rules["COLREGs"]["rule_7"],
            self.knowledge_rules["COLREGs"]["rule_8"],
        ]
        if engine_alerts:
            rules.append(self.knowledge_rules["ENGINE"]["lubrication"])
        if efficiency.get("available"):
            rules.append(self.knowledge_rules["EFFICIENCY"]["cii"])

        return {
            "timestamp": datetime.now().isoformat(),
            "risk_level": risk_level,
            "compliance_status": compliance_status,
            "evidence": evidence,
            "recommended_actions": actions or ["当前系统无高优先级异常，维持监控。"],
            "maintenance_report": self.generate_maintenance_report(),
            "rules": rules,
            "navigation": nav_report or nav,
            "engine": engine,
            "efficiency": efficiency,
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


__all__ = ["ComplianceDigitalExpertChannel"]
