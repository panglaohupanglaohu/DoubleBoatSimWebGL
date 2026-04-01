# -*- coding: utf-8 -*-
"""
Hull Stress Monitor Channel - 船体应力监测

监测双体船连接桥和船体结构的应力状态，
提供结构健康度评估和疲劳评估。
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class HullStressMonitorChannel(MarineChannel):
    """船体应力监测 Channel — 监测双体船连接桥和船体结构应力。"""

    name = "hull_stress_monitor"
    description = "船体应力监测与结构健康评估"
    version = "1.0.0"
    priority = ChannelPriority.P0

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._sensors: Dict[str, Dict[str, Any]] = {}
        self._stress_limits: Dict[str, float] = {
            "yield_stress_mpa": 250.0,
            "fatigue_limit_mpa": 160.0,
            "alarm_threshold": 0.8,
        }

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Hull stress monitor ready")
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

    def update_sensor(
        self,
        sensor_id: str,
        location: str,
        stress_mpa: float,
        strain: float = 0.0,
        temperature_c: float = 20.0,
    ) -> Dict[str, Any]:
        reading = {
            "sensor_id": sensor_id,
            "location": location,
            "stress_mpa": stress_mpa,
            "strain": strain,
            "temperature_c": temperature_c,
            "timestamp": datetime.now().isoformat(),
        }
        self._sensors[sensor_id] = reading
        return reading

    def get_structural_health(self) -> Dict[str, Any]:
        yield_stress = self._stress_limits["yield_stress_mpa"]
        alarm_threshold = self._stress_limits["alarm_threshold"]

        if not self._sensors:
            return {
                "max_stress": 0.0,
                "stress_ratio": 0.0,
                "health_score": 100.0,
                "hotspots": [],
                "alarm_active": False,
            }

        max_stress = max(s["stress_mpa"] for s in self._sensors.values())
        stress_ratio = max_stress / yield_stress
        health_score = max(0.0, 100.0 - stress_ratio * 100.0)

        hotspots = [
            s["sensor_id"]
            for s in self._sensors.values()
            if s["stress_mpa"] / yield_stress > 0.6
        ]

        alarm_active = any(
            s["stress_mpa"] > alarm_threshold * yield_stress
            for s in self._sensors.values()
        )

        return {
            "max_stress": max_stress,
            "stress_ratio": stress_ratio,
            "health_score": health_score,
            "hotspots": hotspots,
            "alarm_active": alarm_active,
        }

    def get_fatigue_assessment(self) -> Dict[str, Any]:
        fatigue_limit = self._stress_limits["fatigue_limit_mpa"]

        if not self._sensors:
            return {
                "sensors_above_fatigue": 0,
                "max_fatigue_ratio": 0.0,
                "recommendation": "normal",
            }

        sensors_above = [
            s for s in self._sensors.values()
            if s["stress_mpa"] > fatigue_limit
        ]
        max_fatigue_ratio = max(
            (s["stress_mpa"] / fatigue_limit for s in self._sensors.values()),
            default=0.0,
        )

        if max_fatigue_ratio > 1.5:
            recommendation = "seek_shelter"
        elif max_fatigue_ratio > 1.2:
            recommendation = "reduce_speed"
        elif max_fatigue_ratio > 1.0:
            recommendation = "monitor"
        else:
            recommendation = "normal"

        return {
            "sensors_above_fatigue": len(sensors_above),
            "max_fatigue_ratio": max_fatigue_ratio,
            "recommendation": recommendation,
        }

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")
        if event_type == "stress_reading":
            sensor_id = event.get("sensor_id")
            if sensor_id is None:
                return {"status": "error", "reason": "sensor_id is required"}
            result = self.update_sensor(
                sensor_id=sensor_id,
                location=event.get("location", "unknown"),
                stress_mpa=event.get("stress_mpa", 0.0),
                strain=event.get("strain", 0.0),
                temperature_c=event.get("temperature_c", 20.0),
            )
            return {"status": "recorded", "sensor": result}
        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    def get_status(self) -> Dict[str, Any]:
        health = self.get_structural_health()
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "sensor_count": len(self._sensors),
            "max_stress_mpa": health["max_stress"],
            "stress_ratio": health["stress_ratio"],
            "health_score": health["health_score"],
            "alarm_active": health["alarm_active"],
        }
