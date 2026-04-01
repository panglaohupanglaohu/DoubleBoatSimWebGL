# -*- coding: utf-8 -*-
"""
L2: Emission Monitor - 船舶排放监测

监测 NOx、SOx、CO2 和颗粒物排放，跟踪燃料切换事件
和排放控制区 (ECA) 合规状态。

合规标准:
- ECA 区域内 SOx: 硫含量 ≤ 0.10%
- 全球 SOx: 硫含量 ≤ 0.50% (IMO 2020)
- NOx Tier III (ECA): 按发动机转速分级
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)

# 燃料硫含量映射 (%)
FUEL_SULFUR_CONTENT = {
    "HFO": 3.50,
    "LSFO": 0.50,
    "VLSFO": 0.50,
    "MGO": 0.10,
    "MDO": 0.50,
    "LNG": 0.00,
    "METHANOL": 0.00,
}


class EmissionMonitorChannel(MarineChannel):
    """船舶排放监测 Channel — 跟踪排放数据与 ECA 合规。"""

    name = "emission_monitor"
    description = "船舶排放监测与 ECA 合规检查"
    version = "1.0.0"
    priority = ChannelPriority.P1

    # SOx 合规限值 (硫含量 %)
    SOX_LIMIT_ECA = 0.10
    SOX_LIMIT_GLOBAL = 0.50

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._current_emissions: Dict[str, float] = {
            "nox_ppm": 0.0,
            "sox_ppm": 0.0,
            "co2_percent": 0.0,
            "particulate_mg_m3": 0.0,
        }
        self._fuel_type: str = "VLSFO"
        self._in_eca: bool = False
        self._eca_region: Optional[str] = None
        self._eca_entry_time: Optional[str] = None
        self._applicable_limit: float = self.SOX_LIMIT_GLOBAL
        self._fuel_switch_log: List[Dict[str, Any]] = []
        self._reading_history: List[Dict[str, Any]] = []

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Emission monitor ready")
        return True

    def get_status(self) -> Dict[str, Any]:
        compliance = self.check_eca_compliance()
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "current_emissions": dict(self._current_emissions),
            "eca_status": {
                "in_eca": self._in_eca,
                "region": self._eca_region,
                "entry_time": self._eca_entry_time,
                "applicable_limit": self._applicable_limit,
            },
            "compliance_status": compliance,
            "fuel_type": self._fuel_type,
            "fuel_switches": len(self._fuel_switch_log),
            "readings_count": len(self._reading_history),
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

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "exhaust_reading":
            return self._handle_exhaust_reading(event)
        elif event_type == "fuel_switch":
            return self._handle_fuel_switch(event)
        elif event_type == "eca_entry":
            return self._handle_eca_entry(event)

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    # ---- event handlers ----

    def _handle_exhaust_reading(self, event: dict) -> dict:
        self._current_emissions = {
            "nox_ppm": event.get("nox_ppm", 0.0),
            "sox_ppm": event.get("sox_ppm", 0.0),
            "co2_percent": event.get("co2_percent", 0.0),
            "particulate_mg_m3": event.get("particulate_mg_m3", 0.0),
        }
        reading = {**self._current_emissions, "timestamp": datetime.now().isoformat()}
        self._reading_history.append(reading)
        return {"status": "processed", "emissions": dict(self._current_emissions)}

    def _handle_fuel_switch(self, event: dict) -> dict:
        from_fuel = event.get("from_fuel", self._fuel_type)
        to_fuel = event.get("to_fuel")
        if to_fuel is None:
            return {"status": "error", "reason": "to_fuel is required"}

        record = {
            "from_fuel": from_fuel,
            "to_fuel": to_fuel,
            "timestamp": event.get("timestamp", datetime.now().isoformat()),
        }
        self._fuel_switch_log.append(record)
        self._fuel_type = to_fuel
        return {"status": "processed", "fuel_type": to_fuel}

    def _handle_eca_entry(self, event: dict) -> dict:
        region = event.get("region")
        if region is None:
            return {"status": "error", "reason": "region is required"}

        self._in_eca = True
        self._eca_region = region
        self._eca_entry_time = event.get("entry_time", datetime.now().isoformat())
        self._applicable_limit = event.get("applicable_limit", self.SOX_LIMIT_ECA)
        return {
            "status": "processed",
            "region": region,
            "applicable_limit": self._applicable_limit,
        }

    # ---- compliance ----

    def check_eca_compliance(self) -> Dict[str, Any]:
        """检查 SOx ECA 合规性。

        ECA 区域: 硫含量 ≤ 0.10%
        全球: 硫含量 ≤ 0.50%

        Returns:
            合规状态字典。
        """
        limit = self.SOX_LIMIT_ECA if self._in_eca else self.SOX_LIMIT_GLOBAL
        sulfur_content = FUEL_SULFUR_CONTENT.get(self._fuel_type, 0.50)
        compliant = sulfur_content <= limit

        return {
            "compliant": compliant,
            "fuel_type": self._fuel_type,
            "sulfur_content_percent": sulfur_content,
            "limit_percent": limit,
            "in_eca": self._in_eca,
            "eca_region": self._eca_region,
            "details": "Compliant" if compliant else f"Sulfur {sulfur_content}% exceeds limit {limit}%",
        }
