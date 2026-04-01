# -*- coding: utf-8 -*-
"""
L2: Autopilot Monitor — 自动舵监控

监控自动舵系统状态，包括航向保持、轨迹控制、风向舵等模式。
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)

VALID_MODES = ("standby", "heading_hold", "track_control", "wind_steering")


class AutopilotMonitorChannel(MarineChannel):
    """自动舵监控 Channel — 监控自动舵系统状态和航向跟踪。"""

    name = "autopilot_monitor"
    description = "自动舵监控与航向跟踪"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._mode: str = "standby"
        self._set_heading_deg: float = 0.0
        self._actual_heading_deg: float = 0.0
        self._cross_track_error_m: float = 0.0
        self._rudder_limit_deg: float = 15.0
        self._gain_settings: dict = {
            "proportional": 1.0,
            "derivative": 0.5,
            "counter_rudder": 0.3,
        }

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Autopilot monitor ready")
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

    def set_mode(self, mode: str) -> dict:
        """设置自动舵模式。"""
        if mode not in VALID_MODES:
            return {"status": "error", "reason": f"invalid mode: {mode}"}
        old_mode = self._mode
        self._mode = mode
        logger.info("Autopilot mode changed: %s -> %s", old_mode, mode)
        return {"status": "ok", "old_mode": old_mode, "new_mode": mode}

    def set_heading(self, heading_deg: float) -> dict:
        """设置目标航向。"""
        self._set_heading_deg = heading_deg % 360.0
        return {
            "status": "ok",
            "set_heading_deg": self._set_heading_deg,
        }

    def update_navigation(
        self,
        actual_heading: float,
        cross_track_error: float = 0.0,
    ) -> dict:
        """更新实际航行状态。"""
        self._actual_heading_deg = actual_heading % 360.0
        self._cross_track_error_m = cross_track_error
        return {
            "status": "ok",
            "actual_heading_deg": self._actual_heading_deg,
            "cross_track_error_m": self._cross_track_error_m,
        }

    def _heading_error(self) -> float:
        """计算航向误差，含 360 wrap 处理。"""
        diff = self._set_heading_deg - self._actual_heading_deg
        # normalise to [-180, 180]
        diff = (diff + 180) % 360 - 180
        return diff

    def get_autopilot_status(self) -> dict:
        """返回自动舵完整状态。"""
        heading_error = self._heading_error()
        on_course = abs(heading_error) < 5.0
        return {
            "mode": self._mode,
            "set_heading": self._set_heading_deg,
            "actual_heading": self._actual_heading_deg,
            "heading_error": round(heading_error, 2),
            "cross_track_error_m": round(self._cross_track_error_m, 2),
            "rudder_limit": self._rudder_limit_deg,
            "on_course": on_course,
            "gain_settings": dict(self._gain_settings),
        }

    def get_status(self) -> Dict[str, Any]:
        heading_error = self._heading_error()
        on_course = abs(heading_error) < 5.0
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "mode": self._mode,
            "heading_error": round(heading_error, 2),
            "on_course": on_course,
            "cross_track_error_m": round(self._cross_track_error_m, 2),
        }

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "autopilot_update":
            actual_heading = event.get("actual_heading", self._actual_heading_deg)
            xte = event.get("cross_track_error", self._cross_track_error_m)
            result = self.update_navigation(actual_heading, xte)
            return {**result, "event_status": "updated"}

        if event_type == "set_heading":
            heading = event.get("heading_deg", 0.0)
            return self.set_heading(heading)

        if event_type == "set_mode":
            mode = event.get("mode", "standby")
            return self.set_mode(mode)

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}
