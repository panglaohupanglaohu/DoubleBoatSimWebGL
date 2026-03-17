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

    def initialize(self) -> bool:
        self._initialized = True
        self._set_health(ChannelStatus.OK, "全场景决策编排器已就绪")
        logger.info("✅ Decision Orchestrator initialized")
        return True

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        logger.info("🛑 Decision Orchestrator shutdown")
        return True

    def build_decision_package(self) -> Dict[str, Any]:
        registry = get_default_registry()
        compliance = registry.get("compliance_digital_expert")
        perception = registry.get("distributed_perception_hub")
        logger.debug("📦 Building decision package...")
        snapshot = compliance.query_compliance_status("overall") if compliance and hasattr(compliance, "query_compliance_status") else {}
        latest_events = perception.get_latest_events(10) if perception and hasattr(perception, "get_latest_events") else []
        package = {
            "generated_at": datetime.now().isoformat(),
            "risk_level": snapshot.get("risk_level", "unknown"),
            "compliance_status": snapshot.get("compliance_status", "unknown"),
            "summary": "已整合导航、机舱、能效的最小决策包。",
            "recommended_actions": snapshot.get("recommended_actions", []),
            "maintenance_report": snapshot.get("maintenance_report", {}),
            "supporting_evidence": snapshot.get("evidence", []),
            "latest_events": latest_events,
            "feedback_records": self.feedback_records[-10:],
        }
        return package

    def record_feedback(self, action: str, outcome: str, confirmed_by: str = "system") -> Dict[str, Any]:
        record = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "outcome": outcome,
            "confirmed_by": confirmed_by,
        }
        self.feedback_records.append(record)
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
            "feedback_records_count": len(self.feedback_records),
        }

    async def build_decision_package_async(self) -> Dict[str, Any]:
        """异步构建决策包."""
        return await asyncio.get_event_loop().run_in_executor(None, self.build_decision_package)

    async def record_feedback_async(self, action: str, outcome: str, confirmed_by: str = "system") -> Dict[str, Any]:
        """异步记录反馈."""
        return await asyncio.get_event_loop().run_in_executor(None, self.record_feedback, action, outcome, confirmed_by)


__all__ = ["DecisionOrchestratorChannel"]
