# -*- coding: utf-8 -*-
"""
Bilge Water Monitor Channel - 舱底水监测

MARPOL Annex I 合规 — 舱底水排放监测。
监测各舱室舱底水液位和含油量,
跟踪油水分离器 (OWS) 状态, 确保排放合规。
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class BilgeWaterMonitorChannel(MarineChannel):
    """舱底水监测 Channel — MARPOL Annex I 排放合规监测。"""

    name = "bilge_water_monitor"
    description = "舱底水监测与 MARPOL Annex I 合规"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._compartments: Dict[str, Dict[str, Any]] = {}
        self._oily_water_separator: Dict[str, Any] = {
            "operational": True,
            "oil_content_output_ppm": 0.0,
        }
        self._discharge_limit_ppm: float = 15.0

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Bilge water monitor ready")
        return True

    def get_status(self) -> Dict[str, Any]:
        bilge = self.get_bilge_status()
        compliance = self.check_marpol_compliance()
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "compartment_count": len(self._compartments),
            "any_alarm": bilge["any_alarm"],
            "discharge_permitted": bilge["discharge_permitted"],
            "marpol_compliant": compliance["compliant"],
        }

    def shutdown(self) -> bool:
        self._active = False
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True

    async def start(self):
        self._active = True
        self._set_health(ChannelStatus.OK, "Running")

    async def stop(self):
        self._active = False

    # ---- public helpers ----

    def update_compartment(
        self,
        comp_id: str,
        level_percent: float,
        oil_content_ppm: float = 0.0,
    ) -> Dict[str, Any]:
        """更新舱室舱底水状态。"""
        alarm = level_percent > 80.0 or oil_content_ppm > self._discharge_limit_ppm
        entry = {
            "comp_id": comp_id,
            "level_percent": level_percent,
            "oil_content_ppm": oil_content_ppm,
            "alarm_active": alarm,
            "pump_running": level_percent > 60.0,
            "last_update": datetime.now().isoformat(),
        }
        self._compartments[comp_id] = entry
        return entry

    def get_bilge_status(self) -> Dict[str, Any]:
        """获取完整舱底水状态。"""
        compartments = list(self._compartments.values())

        any_alarm = any(
            c["level_percent"] > 80.0 or c["oil_content_ppm"] > self._discharge_limit_ppm
            for c in compartments
        ) if compartments else False

        ows_operational = self._oily_water_separator["operational"]
        ows_output_ppm = self._oily_water_separator["oil_content_output_ppm"]
        discharge_permitted = ows_operational and ows_output_ppm <= self._discharge_limit_ppm

        return {
            "compartments": compartments,
            "any_alarm": any_alarm,
            "ows_status": dict(self._oily_water_separator),
            "discharge_permitted": discharge_permitted,
        }

    def check_marpol_compliance(self) -> Dict[str, Any]:
        """检查 MARPOL Annex I 合规性。"""
        violations: List[str] = []
        max_oil_ppm = 0.0

        for comp in self._compartments.values():
            oil_ppm = comp["oil_content_ppm"]
            if oil_ppm > max_oil_ppm:
                max_oil_ppm = oil_ppm
            if oil_ppm > self._discharge_limit_ppm:
                violations.append(
                    f"Compartment {comp['comp_id']}: oil content {oil_ppm} ppm > {self._discharge_limit_ppm} ppm"
                )

        if not self._oily_water_separator["operational"]:
            violations.append("OWS not operational")

        ows_output = self._oily_water_separator["oil_content_output_ppm"]
        if ows_output > self._discharge_limit_ppm:
            violations.append(
                f"OWS output {ows_output} ppm > {self._discharge_limit_ppm} ppm"
            )

        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "oil_content_max_ppm": max_oil_ppm,
        }

    # ---- event processing ----

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "bilge_reading":
            return self._handle_bilge_reading(event)
        elif event_type == "ows_update":
            return self._handle_ows_update(event)

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    def _handle_bilge_reading(self, event: dict) -> dict:
        comp_id = event.get("comp_id")
        if comp_id is None:
            return {"status": "error", "reason": "comp_id is required"}
        level = event.get("level_percent", 0.0)
        oil = event.get("oil_content_ppm", 0.0)
        result = self.update_compartment(comp_id, level, oil)
        return {"status": "updated", "compartment": result}

    def _handle_ows_update(self, event: dict) -> dict:
        if "operational" in event:
            self._oily_water_separator["operational"] = bool(event["operational"])
        if "oil_content_output_ppm" in event:
            self._oily_water_separator["oil_content_output_ppm"] = float(
                event["oil_content_output_ppm"]
            )
        return {"status": "updated", "ows": dict(self._oily_water_separator)}
