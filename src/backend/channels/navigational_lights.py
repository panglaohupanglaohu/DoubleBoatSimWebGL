# -*- coding: utf-8 -*-
"""
L2: Navigational Lights — COLREG Part C 航行灯监控

监控所有规定灯光状态，检查 COLREG 合规。
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)

# 各种船舶状态所需的灯光配置
_REQUIRED_LIGHTS: Dict[str, List[str]] = {
    "underway": ["masthead", "sidelight_port", "sidelight_stbd", "stern"],
    "at_anchor": ["anchor"],
    "moored": ["anchor"],
    "nuc": ["all_round_red", "all_round_red"],
    "restricted_maneuverability": ["all_round_red", "all_round_white", "all_round_red"],
    "towing": ["masthead", "masthead", "sidelight_port", "sidelight_stbd", "stern", "towing"],
    "fishing": ["all_round_red", "all_round_white"],
}

_VALID_STATUSES = ("underway", "at_anchor", "moored", "nuc",
                   "restricted_maneuverability", "towing", "fishing")


class NavigationalLightsChannel(MarineChannel):
    """航行灯监控 Channel — COLREG Part C 合规检查。"""

    name = "navigational_lights"
    description = "COLREG Part C 航行灯合规监控"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._lights: Dict[str, Dict[str, Any]] = {}
        self._vessel_status: str = "underway"

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Navigational lights monitor ready")
        return True

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

    def update_light(self, light_id: str, light_type: str,
                     status: str = "on", brightness: float = 100.0) -> dict:
        """更新灯光状态。"""
        self._lights[light_id] = {
            "light_id": light_id,
            "type": light_type,
            "status": status,
            "brightness_percent": brightness,
        }
        return {"status": "updated", "light_id": light_id, "light_type": light_type}

    def set_vessel_status(self, status: str) -> dict:
        """设置船舶状态。"""
        if status not in _VALID_STATUSES:
            return {"status": "error",
                    "reason": f"Invalid vessel status: {status}. Valid: {_VALID_STATUSES}"}
        self._vessel_status = status
        return {"status": "vessel_status_set", "vessel_status": status}

    def get_light_configuration(self) -> dict:
        """根据 vessel_status 返回灯光配置合规情况。"""
        required_types = _REQUIRED_LIGHTS.get(self._vessel_status, [])

        # 统计实际亮灯类型（status == "on"）
        actual_lights = [
            lid for lid, info in self._lights.items()
            if info["status"] == "on"
        ]
        actual_types = [
            self._lights[lid]["type"] for lid in actual_lights
        ]

        # 检查缺少的灯
        remaining_required = list(required_types)
        for t in actual_types:
            if t in remaining_required:
                remaining_required.remove(t)

        missing_lights = remaining_required
        compliant = len(missing_lights) == 0

        return {
            "vessel_status": self._vessel_status,
            "required_lights": required_types,
            "actual_lights": actual_lights,
            "missing_lights": missing_lights,
            "compliant": compliant,
        }

    def check_colreg_compliance(self) -> dict:
        """全面 COLREG 合规检查。"""
        config = self.get_light_configuration()

        faulty_lights = [
            lid for lid, info in self._lights.items()
            if info["status"] == "fault"
        ]

        violations = list(config["missing_lights"])
        compliant = config["compliant"] and len(faulty_lights) == 0

        return {
            "compliant": compliant,
            "vessel_status": self._vessel_status,
            "violations": violations,
            "faulty_lights": faulty_lights,
        }

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "light_status_update":
            light_id = event.get("light_id")
            light_type = event.get("light_type")
            if any(v is None for v in [light_id, light_type]):
                return {"status": "error", "reason": "light_id and light_type required"}
            return self.update_light(
                light_id=light_id,
                light_type=light_type,
                status=event.get("status", "on"),
                brightness=event.get("brightness", 100.0),
            )

        if event_type == "vessel_status_change":
            new_status = event.get("vessel_status")
            if new_status is None:
                return {"status": "error", "reason": "vessel_status required"}
            return self.set_vessel_status(new_status)

        return {"status": "ignored", "reason": f"Unknown event type: {event_type}"}

    def get_status(self) -> Dict[str, Any]:
        compliance = self.check_colreg_compliance()
        faulty_count = len(compliance["faulty_lights"])
        missing_count = len(compliance["violations"])
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "vessel_status": self._vessel_status,
            "light_count": len(self._lights),
            "compliant": compliance["compliant"],
            "faulty_count": faulty_count,
            "missing_count": missing_count,
        }
