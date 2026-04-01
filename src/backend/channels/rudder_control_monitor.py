# -*- coding: utf-8 -*-
"""
L2: Rudder Control Monitor — 舵机监控

监控舵机系统状态、舵角跟踪和SOLAS合规检查。
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any, Dict

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class RudderControlMonitorChannel(MarineChannel):
    """舵机监控 Channel — 舵机系统状态监控和舵角跟踪。"""

    name = "rudder_control_monitor"
    description = "舵机系统状态监控和舵角跟踪"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._rudders: Dict[str, Dict[str, Any]] = {}
        self._max_rudder_angle: float = 35.0
        self._response_time_limit_s: float = 28.0  # SOLAS: 28s for 35° to 35°

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Rudder control monitor ready")
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

    def update_rudder(self, rudder_id: str, angle_deg: float,
                      ordered_angle_deg: float = 0.0,
                      pressure_bar: float = 150.0,
                      response_time_s: float = 5.0) -> dict:
        """更新舵机状态。"""
        angle_deg = max(-self._max_rudder_angle,
                        min(self._max_rudder_angle, angle_deg))

        if response_time_s > self._response_time_limit_s:
            status = "fault"
        elif abs(angle_deg - ordered_angle_deg) > 2.0:
            status = "warning"
        elif pressure_bar < 80.0 or pressure_bar > 250.0:
            status = "warning"
        else:
            status = "ok"

        self._rudders[rudder_id] = {
            "rudder_id": rudder_id,
            "angle_deg": angle_deg,
            "ordered_angle_deg": ordered_angle_deg,
            "hydraulic_pressure_bar": pressure_bar,
            "status": status,
            "response_time_s": response_time_s,
            "last_update": time.time(),
        }

        self._update_health()
        return {
            "rudder_id": rudder_id,
            "angle_deg": angle_deg,
            "rudder_status": status,
            "rudder_count": len(self._rudders),
        }

    def get_steering_status(self) -> dict:
        """获取综合舵机状态。"""
        rudders = dict(self._rudders)
        any_fault = any(r["status"] == "fault" for r in rudders.values())
        angle_mismatch = any(
            abs(r["angle_deg"] - r["ordered_angle_deg"]) > 2.0
            for r in rudders.values()
        )
        response_times = [r["response_time_s"] for r in rudders.values()]
        avg_response = (sum(response_times) / len(response_times)) if response_times else 0.0
        solas_compliant = (
            not any_fault
            and all(r["response_time_s"] <= self._response_time_limit_s
                    for r in rudders.values())
        )

        return {
            "rudders": rudders,
            "any_fault": any_fault,
            "angle_mismatch": angle_mismatch,
            "solas_compliant": solas_compliant,
            "average_response_time_s": round(avg_response, 2),
        }

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")
        if event_type == "rudder_reading":
            result = self.update_rudder(
                rudder_id=event.get("rudder_id", ""),
                angle_deg=event.get("angle_deg", 0.0),
                ordered_angle_deg=event.get("ordered_angle_deg", 0.0),
                pressure_bar=event.get("pressure_bar", 150.0),
                response_time_s=event.get("response_time_s", 5.0),
            )
            return {"status": "updated", **result}
        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    def get_status(self) -> Dict[str, Any]:
        steering = self.get_steering_status()
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "rudder_count": len(self._rudders),
            "any_fault": steering["any_fault"],
            "solas_compliant": steering["solas_compliant"],
        }

    def _update_health(self):
        """根据舵机状态更新Channel健康。"""
        if any(r["status"] == "fault" for r in self._rudders.values()):
            self._set_health(ChannelStatus.ERROR, "Rudder fault detected")
        elif any(r["status"] == "warning" for r in self._rudders.values()):
            self._set_health(ChannelStatus.WARN, "Rudder warning")
        else:
            self._set_health(ChannelStatus.OK, "All rudders normal")
