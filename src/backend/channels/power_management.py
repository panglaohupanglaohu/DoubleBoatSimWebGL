# -*- coding: utf-8 -*-
"""
Power Management Channel - 电力管理系统

双体船电力系统管理（发电机、负载、电池），
提供电力平衡监控和燃油效率分析。
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class PowerManagementChannel(MarineChannel):
    """电力管理 Channel — 发电机、负载和电池管理。"""

    name = "power_management"
    description = "双体船电力系统管理"
    version = "1.0.0"
    priority = ChannelPriority.P0

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._generators: Dict[str, Dict[str, Any]] = {}
        self._loads: Dict[str, Dict[str, Any]] = {}
        self._battery: Dict[str, Any] = {
            "capacity_kwh": 500.0,
            "soc_percent": 80.0,
            "charging": False,
        }

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Power management ready")
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

    def update_generator(
        self,
        gen_id: str,
        rated_kw: float = 500.0,
        current_kw: float = 0.0,
        fuel_rate_lph: float = 0.0,
        status: str = "running",
        rpm: int = 1800,
    ) -> Dict[str, Any]:
        gen_data = {
            "gen_id": gen_id,
            "rated_kw": rated_kw,
            "current_kw": current_kw,
            "fuel_rate_lph": fuel_rate_lph,
            "status": status,
            "rpm": rpm,
        }
        self._generators[gen_id] = gen_data
        return gen_data

    def update_load(
        self,
        load_id: str,
        category: str = "hotel",
        current_kw: float = 0.0,
        priority: int = 3,
    ) -> Dict[str, Any]:
        load_data = {
            "load_id": load_id,
            "category": category,
            "current_kw": current_kw,
            "priority": priority,
        }
        self._loads[load_id] = load_data
        return load_data

    def get_power_balance(self) -> Dict[str, Any]:
        total_generation_kw = sum(
            g["current_kw"]
            for g in self._generators.values()
            if g["status"] == "running"
        )
        total_load_kw = sum(l["current_kw"] for l in self._loads.values())
        reserve_kw = total_generation_kw - total_load_kw

        if total_generation_kw > 0:
            reserve_percent = reserve_kw / total_generation_kw * 100.0
        else:
            reserve_percent = 0.0

        load_shedding_needed = reserve_percent < 15.0

        return {
            "total_generation_kw": total_generation_kw,
            "total_load_kw": total_load_kw,
            "reserve_kw": reserve_kw,
            "reserve_percent": reserve_percent,
            "load_shedding_needed": load_shedding_needed,
        }

    def get_fuel_efficiency(self) -> Dict[str, Any]:
        running_gens = [
            g for g in self._generators.values()
            if g["status"] == "running"
        ]
        total_fuel_rate_lph = sum(g["fuel_rate_lph"] for g in running_gens)
        total_generation_kw = sum(g["current_kw"] for g in running_gens)

        # specific fuel consumption in g/kWh (fuel density 0.84 kg/L)
        if total_generation_kw > 0:
            sfc = (total_fuel_rate_lph * 0.84 * 1000.0) / total_generation_kw
        else:
            sfc = 0.0

        if sfc <= 0.0:
            efficiency_rating = "good"
        elif sfc < 200.0:
            efficiency_rating = "good"
        elif sfc < 250.0:
            efficiency_rating = "acceptable"
        else:
            efficiency_rating = "poor"

        return {
            "total_fuel_rate_lph": total_fuel_rate_lph,
            "specific_fuel_consumption": sfc,
            "efficiency_rating": efficiency_rating,
        }

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "generator_update":
            gen_id = event.get("gen_id")
            if gen_id is None:
                return {"status": "error", "reason": "gen_id is required"}
            result = self.update_generator(
                gen_id=gen_id,
                rated_kw=event.get("rated_kw", 500.0),
                current_kw=event.get("current_kw", 0.0),
                fuel_rate_lph=event.get("fuel_rate_lph", 0.0),
                status=event.get("status", "running"),
                rpm=event.get("rpm", 1800),
            )
            return {"status": "recorded", "generator": result}

        elif event_type == "load_update":
            load_id = event.get("load_id")
            if load_id is None:
                return {"status": "error", "reason": "load_id is required"}
            result = self.update_load(
                load_id=load_id,
                category=event.get("category", "hotel"),
                current_kw=event.get("current_kw", 0.0),
                priority=event.get("priority", 3),
            )
            return {"status": "recorded", "load": result}

        elif event_type == "battery_update":
            self._battery.update({
                k: event[k]
                for k in ("capacity_kwh", "soc_percent", "charging")
                if k in event
            })
            return {"status": "recorded", "battery": self._battery.copy()}

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    def get_status(self) -> Dict[str, Any]:
        balance = self.get_power_balance()
        generators_running = sum(
            1 for g in self._generators.values() if g["status"] == "running"
        )
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "generators_running": generators_running,
            "total_generation_kw": balance["total_generation_kw"],
            "total_load_kw": balance["total_load_kw"],
            "reserve_percent": balance["reserve_percent"],
            "battery_soc": self._battery["soc_percent"],
            "load_shedding_needed": balance["load_shedding_needed"],
        }
