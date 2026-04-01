# -*- coding: utf-8 -*-
"""
L2: Propulsion Monitor — 推进系统监控

双体船推进系统（主机、喷水推进器、CPP等）监控。
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class PropulsionMonitorChannel(MarineChannel):
    """推进系统监控 Channel — 主机与推进器状态监控。"""

    name = "propulsion_monitor"
    description = "推进系统监控（主机/喷水推进/CPP）"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._engines: Dict[str, Dict[str, Any]] = {}
        self._propulsors: Dict[str, Dict[str, Any]] = {}

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Propulsion monitor ready")
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

    def update_engine(
        self,
        engine_id: str,
        engine_type: str = "diesel",
        rated_kw: float = 2000.0,
        current_kw: float = 0.0,
        rpm: int = 0,
        exhaust_temp_c: float = 350.0,
        lub_oil_pressure_bar: float = 4.5,
        coolant_temp_c: float = 80.0,
        running_hours: float = 0.0,
    ) -> dict:
        """更新主机状态。"""
        status = "running" if rpm > 0 else "standby"
        if exhaust_temp_c >= 450 or lub_oil_pressure_bar < 3.0 or coolant_temp_c >= 95:
            status = "alarm"

        self._engines[engine_id] = {
            "engine_id": engine_id,
            "type": engine_type,
            "rated_kw": rated_kw,
            "current_kw": current_kw,
            "rpm": rpm,
            "exhaust_temp_c": exhaust_temp_c,
            "lub_oil_pressure_bar": lub_oil_pressure_bar,
            "coolant_temp_c": coolant_temp_c,
            "status": status,
            "running_hours": running_hours,
        }

        return {
            "engine_id": engine_id,
            "status": status,
            "engine_count": len(self._engines),
        }

    def update_propulsor(
        self,
        propulsor_id: str,
        prop_type: str = "waterjet",
        rpm: int = 0,
        pitch_percent: float = 100.0,
        thrust_kn: float = 0.0,
    ) -> dict:
        """更新推进器状态。"""
        status = "running" if rpm > 0 else "standby"

        self._propulsors[propulsor_id] = {
            "propulsor_id": propulsor_id,
            "type": prop_type,
            "rpm": rpm,
            "pitch_percent": pitch_percent,
            "thrust_kn": thrust_kn,
            "status": status,
        }

        return {
            "propulsor_id": propulsor_id,
            "status": status,
            "propulsor_count": len(self._propulsors),
        }

    def get_propulsion_status(self) -> dict:
        """返回推进系统完整状态。"""
        running_engines = [
            e for e in self._engines.values() if e["status"] == "running"
        ]
        total_power_kw = sum(e["current_kw"] for e in running_engines)
        total_rated_kw = sum(e["rated_kw"] for e in running_engines)
        total_thrust_kn = sum(p["thrust_kn"] for p in self._propulsors.values())
        any_alarm = any(
            e["status"] == "alarm" for e in self._engines.values()
        ) or any(
            p["status"] == "alarm" for p in self._propulsors.values()
        )
        efficiency = (
            (total_power_kw / total_rated_kw * 100.0) if total_rated_kw > 0 else 0.0
        )

        return {
            "engines": dict(self._engines),
            "propulsors": dict(self._propulsors),
            "total_power_kw": round(total_power_kw, 2),
            "total_thrust_kn": round(total_thrust_kn, 2),
            "any_alarm": any_alarm,
            "efficiency_percent": round(efficiency, 2),
        }

    def get_engine_health(self, engine_id: str) -> dict:
        """单台主机健康评估。"""
        engine = self._engines.get(engine_id)
        if engine is None:
            return {"error": f"Engine {engine_id} not found"}

        exhaust_ok = engine["exhaust_temp_c"] < 450.0
        lub_ok = engine["lub_oil_pressure_bar"] > 3.0
        coolant_ok = engine["coolant_temp_c"] < 95.0

        score = 0
        total = 3
        if exhaust_ok:
            score += 1
        if lub_ok:
            score += 1
        if coolant_ok:
            score += 1
        health_score = round(score / total * 100.0, 1)

        return {
            "engine_id": engine_id,
            "exhaust_temp_normal": exhaust_ok,
            "lub_oil_normal": lub_ok,
            "coolant_normal": coolant_ok,
            "health_score": health_score,
        }

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "engine_update":
            engine_id = event.get("engine_id")
            if engine_id is None:
                return {"status": "error", "reason": "engine_id is required"}
            result = self.update_engine(
                engine_id,
                engine_type=event.get("engine_type", "diesel"),
                rated_kw=event.get("rated_kw", 2000.0),
                current_kw=event.get("current_kw", 0.0),
                rpm=event.get("rpm", 0),
                exhaust_temp_c=event.get("exhaust_temp_c", 350.0),
                lub_oil_pressure_bar=event.get("lub_oil_pressure_bar", 4.5),
                coolant_temp_c=event.get("coolant_temp_c", 80.0),
                running_hours=event.get("running_hours", 0.0),
            )
            return {**result, "event_status": "updated"}

        if event_type == "propulsor_update":
            propulsor_id = event.get("propulsor_id")
            if propulsor_id is None:
                return {"status": "error", "reason": "propulsor_id is required"}
            result = self.update_propulsor(
                propulsor_id,
                prop_type=event.get("prop_type", "waterjet"),
                rpm=event.get("rpm", 0),
                pitch_percent=event.get("pitch_percent", 100.0),
                thrust_kn=event.get("thrust_kn", 0.0),
            )
            return {**result, "event_status": "updated"}

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    def get_status(self) -> Dict[str, Any]:
        running_engines = [
            e for e in self._engines.values() if e["status"] == "running"
        ]
        total_power_kw = sum(e["current_kw"] for e in running_engines)
        total_rated_kw = sum(e["rated_kw"] for e in running_engines)
        total_thrust_kn = sum(p["thrust_kn"] for p in self._propulsors.values())
        any_alarm = any(
            e["status"] == "alarm" for e in self._engines.values()
        ) or any(
            p["status"] == "alarm" for p in self._propulsors.values()
        )
        efficiency = (
            (total_power_kw / total_rated_kw * 100.0) if total_rated_kw > 0 else 0.0
        )

        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "engines_running": len(running_engines),
            "total_power_kw": round(total_power_kw, 2),
            "total_thrust_kn": round(total_thrust_kn, 2),
            "any_alarm": any_alarm,
            "efficiency_percent": round(efficiency, 2),
        }
