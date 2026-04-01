# -*- coding: utf-8 -*-
"""
L2: Tank Level Monitor — 液舱监控

监控船舶液舱（燃油、淡水、压载水、污水等）的液位和状态。
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any, Dict, List

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)

_FUEL_TYPES = {"fuel_oil", "diesel_oil", "lub_oil"}
_WATER_TYPES = {"fresh_water"}
_HIGH_LEVEL_TYPES = {"ballast", "sewage"}


class TankLevelMonitorChannel(MarineChannel):
    """液舱监控 Channel — 监控船舶液舱液位和状态。"""

    name = "tank_level_monitor"
    description = "船舶液舱液位监控与燃油续航估算"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._tanks: Dict[str, Dict[str, Any]] = {}

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Tank level monitor ready")
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

    def update_tank(self, tank_id: str, tank_type: str,
                    capacity_m3: float, current_m3: float,
                    temperature_c: float = 25.0) -> dict:
        """更新液舱数据。"""
        if capacity_m3 <= 0:
            capacity_m3 = 1.0  # 防止除零
        current_m3 = max(0.0, min(current_m3, capacity_m3))
        level_percent = (current_m3 / capacity_m3) * 100.0

        self._tanks[tank_id] = {
            "tank_id": tank_id,
            "type": tank_type,
            "capacity_m3": capacity_m3,
            "current_m3": current_m3,
            "level_percent": round(level_percent, 1),
            "temperature_c": temperature_c,
            "last_update": time.time(),
        }

        self._update_health()
        return {
            "tank_id": tank_id,
            "level_percent": round(level_percent, 1),
            "tank_count": len(self._tanks),
        }

    def get_tank_summary(self) -> dict:
        """获取液舱综合摘要。"""
        tanks = dict(self._tanks)
        total_fuel = sum(
            t["current_m3"] for t in tanks.values()
            if t["type"] in _FUEL_TYPES
        )
        total_fresh_water = sum(
            t["current_m3"] for t in tanks.values()
            if t["type"] in _WATER_TYPES
        )

        low_level_alarms = [
            t["tank_id"] for t in tanks.values()
            if t["level_percent"] < 20.0
            and t["type"] not in _HIGH_LEVEL_TYPES
        ]
        high_level_alarms = [
            t["tank_id"] for t in tanks.values()
            if t["level_percent"] > 90.0
            and t["type"] in _HIGH_LEVEL_TYPES
        ]

        return {
            "tanks": tanks,
            "total_fuel_m3": round(total_fuel, 2),
            "total_fresh_water_m3": round(total_fresh_water, 2),
            "low_level_alarms": low_level_alarms,
            "high_level_alarms": high_level_alarms,
        }

    def estimate_fuel_endurance(self, consumption_m3_per_hour: float = 0.5) -> dict:
        """估算燃油续航。"""
        total_fuel = sum(
            t["current_m3"] for t in self._tanks.values()
            if t["type"] in _FUEL_TYPES
        )
        if consumption_m3_per_hour <= 0:
            consumption_m3_per_hour = 0.5

        hours = total_fuel / consumption_m3_per_hour
        nm_at_12kts = hours * 12.0

        return {
            "total_fuel_m3": round(total_fuel, 2),
            "hours_remaining": round(hours, 1),
            "nautical_miles_at_12kts": round(nm_at_12kts, 1),
        }

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")
        if event_type == "tank_reading":
            result = self.update_tank(
                tank_id=event.get("tank_id", ""),
                tank_type=event.get("tank_type", "fuel_oil"),
                capacity_m3=event.get("capacity_m3", 100.0),
                current_m3=event.get("current_m3", 50.0),
                temperature_c=event.get("temperature_c", 25.0),
            )
            return {"status": "updated", **result}
        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    def get_status(self) -> Dict[str, Any]:
        summary = self.get_tank_summary()
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "tank_count": len(self._tanks),
            "total_fuel_m3": summary["total_fuel_m3"],
            "total_fresh_water_m3": summary["total_fresh_water_m3"],
            "low_level_count": len(summary["low_level_alarms"]),
            "high_level_count": len(summary["high_level_alarms"]),
        }

    def _update_health(self):
        """根据液舱状态更新Channel健康。"""
        summary = self.get_tank_summary()
        if summary["low_level_alarms"]:
            self._set_health(ChannelStatus.WARN, f"Low level: {summary['low_level_alarms']}")
        elif summary["high_level_alarms"]:
            self._set_health(ChannelStatus.WARN, f"High level: {summary['high_level_alarms']}")
        else:
            self._set_health(ChannelStatus.OK, "All tanks normal")
