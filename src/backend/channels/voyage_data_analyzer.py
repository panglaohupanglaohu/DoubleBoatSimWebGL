# -*- coding: utf-8 -*-
"""
L2: Voyage Data Analyzer Channel - 航次数据分析

实时分析航次数据，生成 KPI 指标：距离、燃油、航速、延误等。
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class VoyageDataAnalyzerChannel(MarineChannel):
    """航次数据分析 Channel — 实时 KPI 计算与航次生命周期管理。"""

    name = "voyage_data_analyzer"
    description = "航次数据分析与 KPI 监控"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._voyage: Optional[Dict[str, Any]] = None
        self._kpi_data: Dict[str, Any] = self._default_kpi()

    @staticmethod
    def _default_kpi() -> Dict[str, Any]:
        return {
            "distance_nm": 0.0,
            "fuel_consumed_mt": 0.0,
            "avg_speed_knots": 0.0,
            "max_speed_knots": 0.0,
            "weather_delays_hours": 0.0,
            "route_deviation_nm": 0.0,
        }

    # ---- lifecycle ----

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Voyage data analyzer ready")
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

    # ---- core methods ----

    def start_voyage(self, voyage_id: str, departure: str, arrival: str, eta: Optional[str] = None) -> dict:
        self._voyage = {
            "voyage_id": voyage_id,
            "departure_port": departure,
            "arrival_port": arrival,
            "start_time": datetime.now().isoformat(),
            "eta": eta,
        }
        self._kpi_data = self._default_kpi()
        return {"status": "voyage_started", "voyage": self._voyage}

    def end_voyage(self) -> dict:
        if self._voyage is None:
            return {"status": "error", "reason": "no active voyage"}
        report = {
            "status": "voyage_ended",
            "voyage": self._voyage,
            "kpi": dict(self._kpi_data),
            "fuel_efficiency": self._calc_fuel_efficiency(),
        }
        self._voyage = None
        self._kpi_data = self._default_kpi()
        return report

    def update_kpi(self, distance_nm: Optional[float] = None,
                   fuel_mt: Optional[float] = None,
                   speed_knots: Optional[float] = None) -> dict:
        if distance_nm is not None:
            self._kpi_data["distance_nm"] += distance_nm
        if fuel_mt is not None:
            self._kpi_data["fuel_consumed_mt"] += fuel_mt
        if speed_knots is not None:
            # 更新平均速度 (增量加权)
            old_avg = self._kpi_data["avg_speed_knots"]
            dist = self._kpi_data["distance_nm"]
            if dist > 0 and distance_nm and distance_nm > 0:
                weight = distance_nm / dist
                self._kpi_data["avg_speed_knots"] = old_avg * (1 - weight) + speed_knots * weight
            else:
                self._kpi_data["avg_speed_knots"] = speed_knots
            if speed_knots > self._kpi_data["max_speed_knots"]:
                self._kpi_data["max_speed_knots"] = speed_knots
        return {"status": "kpi_updated", "kpi": dict(self._kpi_data)}

    def get_voyage_kpi(self) -> dict:
        fuel_eff = self._calc_fuel_efficiency()
        avg_speed = self._kpi_data["avg_speed_knots"]

        # 估算到达时间
        estimated_arrival: Optional[str] = None
        if self._voyage and self._voyage.get("eta"):
            estimated_arrival = self._voyage["eta"]

        # 航次进度
        total_distance = (self._voyage or {}).get("total_distance")
        progress: Optional[float] = None
        if total_distance and total_distance > 0:
            progress = self._kpi_data["distance_nm"] / total_distance * 100

        return {
            "voyage_info": self._voyage,
            "kpi": dict(self._kpi_data),
            "fuel_efficiency": fuel_eff,
            "estimated_arrival": estimated_arrival,
            "voyage_progress_percent": progress,
        }

    # ---- event processing ----

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "voyage_start":
            return self.start_voyage(
                voyage_id=event.get("voyage_id", "unknown"),
                departure=event.get("departure_port", ""),
                arrival=event.get("arrival_port", ""),
                eta=event.get("eta"),
            )
        elif event_type == "voyage_end":
            return self.end_voyage()
        elif event_type == "kpi_update":
            return self.update_kpi(
                distance_nm=event.get("distance_nm"),
                fuel_mt=event.get("fuel_mt"),
                speed_knots=event.get("speed_knots"),
            )

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    def get_status(self) -> Dict[str, Any]:
        fuel_eff = self._calc_fuel_efficiency()
        return {
            "name": self.name,
            "active_voyage": self._voyage is not None,
            "voyage_id": self._voyage["voyage_id"] if self._voyage else None,
            "distance_nm": self._kpi_data["distance_nm"],
            "fuel_efficiency": fuel_eff,
            "initialized": self._initialized,
            "health": self._health.status.value,
        }

    # ---- internal ----

    def _calc_fuel_efficiency(self) -> Optional[float]:
        dist = self._kpi_data["distance_nm"]
        if dist == 0:
            return None
        return self._kpi_data["fuel_consumed_mt"] / dist
