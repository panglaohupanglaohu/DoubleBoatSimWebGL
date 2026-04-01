# -*- coding: utf-8 -*-
"""
L2: Ballast Water Monitor - 压载水管理监测

监测压载水舱状态、BWM 处理事件和置换记录，
检查 IMO BWM Convention (D-1/D-2 标准) 合规性。

D-2 标准:
- 可存活生物 ≥50μm: < 10 个/m³
- 可存活生物 10~50μm: < 10 个/mL
- 弧菌: < 1 cfu/100mL
- 大肠杆菌: < 250 cfu/100mL
- 肠球菌: < 100 cfu/100mL
"""

from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class BallastWaterMonitorChannel(MarineChannel):
    """压载水管理监测 Channel — 跟踪压载水舱状态与合规性。"""

    name = "ballast_water"
    description = "压载水管理监测与 BWM Convention 合规检查"
    version = "1.0.0"
    priority = ChannelPriority.P1

    # D-2 标准阈值
    D2_VIABLE_ORGANISMS_50UM = 10  # 个/m³ (≥50μm)
    D2_VIABLE_ORGANISMS_10UM = 10  # 个/mL (10~50μm)

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._tanks: Dict[str, Dict[str, Any]] = {}
        self._treatment_events: List[Dict[str, Any]] = []
        self._exchange_records: List[Dict[str, Any]] = []
        self._total_capacity_m3: float = 0.0

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Ballast water monitor ready")
        return True

    def get_status(self) -> Dict[str, Any]:
        tanks_list = list(self._tanks.values())
        treatment_status = self._get_treatment_status()
        compliance = self.check_bwm_compliance()
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "tanks": tanks_list,
            "treatment_status": treatment_status,
            "compliance_status": compliance,
            "total_capacity": self._total_capacity_m3,
            "exchange_records_count": len(self._exchange_records),
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

        if event_type == "tank_status":
            return self._handle_tank_status(event)
        elif event_type == "treatment_event":
            return self._handle_treatment_event(event)
        elif event_type == "exchange_record":
            return self._handle_exchange_record(event)

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    # ---- event handlers ----

    def _handle_tank_status(self, event: dict) -> dict:
        tank_id = event.get("tank_id")
        if tank_id is None:
            return {"status": "error", "reason": "tank_id is required"}

        tank_data = {
            "tank_id": tank_id,
            "level_percent": event.get("level_percent", 0.0),
            "salinity": event.get("salinity", 0.0),
            "temperature": event.get("temperature", 0.0),
            "treated": event.get("treated", False),
            "updated_at": datetime.now().isoformat(),
        }
        self._tanks[tank_id] = tank_data
        self._recalc_capacity()
        return {"status": "processed", "tank_id": tank_id}

    def _handle_treatment_event(self, event: dict) -> dict:
        tank_id = event.get("tank_id")
        if tank_id is None:
            return {"status": "error", "reason": "tank_id is required"}

        record = {
            "tank_id": tank_id,
            "method": event.get("method", "UV"),
            "start_time": event.get("start_time", datetime.now().isoformat()),
            "status": event.get("status", "in_progress"),
            "recorded_at": datetime.now().isoformat(),
        }
        self._treatment_events.append(record)

        # 如果处理完成，标记舱室为已处理
        if record["status"] == "completed" and tank_id in self._tanks:
            self._tanks[tank_id]["treated"] = True

        return {"status": "processed", "tank_id": tank_id, "treatment_status": record["status"]}

    def _handle_exchange_record(self, event: dict) -> dict:
        tank_id = event.get("tank_id")
        if tank_id is None:
            return {"status": "error", "reason": "tank_id is required"}

        lat = event.get("position_lat")
        lon = event.get("position_lon")
        if any(v is None for v in [lat, lon]):
            return {"status": "error", "reason": "position_lat and position_lon are required"}

        record = {
            "tank_id": tank_id,
            "position_lat": lat,
            "position_lon": lon,
            "volume_m3": event.get("volume_m3", 0.0),
            "recorded_at": datetime.now().isoformat(),
        }
        self._exchange_records.append(record)
        return {"status": "processed", "tank_id": tank_id, "volume_m3": record["volume_m3"]}

    # ---- compliance ----

    def check_bwm_compliance(self) -> Dict[str, Any]:
        """检查是否符合 IMO BWM Convention (D-1/D-2 标准)。

        D-2 标准: 处理后可存活生物 < 10/m³ (≥50μm 尺寸)。
        简化判断: 所有非空舱必须标记为已处理。

        Returns:
            合规状态字典。
        """
        if not self._tanks:
            return {"compliant": True, "standard": "D-2", "details": "No tanks registered"}

        untreated = []
        for tank_id, tank in self._tanks.items():
            if tank.get("level_percent", 0) > 0 and not tank.get("treated", False):
                untreated.append(tank_id)

        compliant = len(untreated) == 0
        return {
            "compliant": compliant,
            "standard": "D-2",
            "untreated_tanks": untreated,
            "total_tanks": len(self._tanks),
            "treated_tanks": len(self._tanks) - len(untreated),
            "d2_threshold_organisms_per_m3": self.D2_VIABLE_ORGANISMS_50UM,
            "details": "All tanks treated" if compliant else f"{len(untreated)} tank(s) not treated",
        }

    # ---- helpers ----

    def _get_treatment_status(self) -> Dict[str, Any]:
        in_progress = [e for e in self._treatment_events if e["status"] == "in_progress"]
        completed = [e for e in self._treatment_events if e["status"] == "completed"]
        return {
            "total_events": len(self._treatment_events),
            "in_progress": len(in_progress),
            "completed": len(completed),
        }

    def _recalc_capacity(self) -> None:
        self._total_capacity_m3 = sum(
            t.get("level_percent", 0) for t in self._tanks.values()
        )
