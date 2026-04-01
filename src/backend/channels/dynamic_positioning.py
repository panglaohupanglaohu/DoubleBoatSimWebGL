# -*- coding: utf-8 -*-
"""
L2: Dynamic Positioning Channel - 动态定位系统

双体船海上作业时的自动站位保持。
基于 Haversine 距离计算偏移，简化 PID 推力分配。
"""

from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算两个经纬度点之间的距离 (米)。"""
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class DynamicPositioningChannel(MarineChannel):
    """动态定位 Channel — 海上作业自动站位保持。"""

    name = "dynamic_positioning"
    description = "动态定位系统 (DP)"
    version = "1.0.0"
    priority = ChannelPriority.P0

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._station: Optional[Dict[str, float]] = None
        self._current_position: Dict[str, float] = {"lat": 0.0, "lon": 0.0, "heading": 0.0}
        self._dp_mode: str = "standby"
        self._thrusters: List[Dict[str, Any]] = [
            {"id": "bow_tunnel", "type": "tunnel", "thrust_pct": 0.0, "azimuth_deg": 0.0},
            {"id": "stern_tunnel", "type": "tunnel", "thrust_pct": 0.0, "azimuth_deg": 180.0},
            {"id": "port_azimuth", "type": "azimuth", "thrust_pct": 0.0, "azimuth_deg": 0.0},
            {"id": "stbd_azimuth", "type": "azimuth", "thrust_pct": 0.0, "azimuth_deg": 0.0},
        ]
        self._excursion_limit_m: float = 25.0
        self._wind_speed: float = 0.0
        self._current_speed: float = 0.0

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "DP system ready")
        return True

    def get_status(self) -> Dict[str, Any]:
        excursion = self._compute_excursion_m()
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "dp_mode": self._dp_mode,
            "station": self._station,
            "current_position": self._current_position,
            "excursion_m": excursion,
            "excursion_limit_m": self._excursion_limit_m,
            "thrusters": self._thrusters,
        }

    def shutdown(self) -> bool:
        self._active = False
        self._dp_mode = "standby"
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True

    async def start(self):
        self._active = True
        self._set_health(ChannelStatus.OK, "Running")

    async def stop(self):
        self._active = False
        self._dp_mode = "standby"

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "position_update":
            return self._handle_position_update(event)
        elif event_type == "set_station":
            return self._handle_set_station(event)
        elif event_type == "wind_update":
            return self._handle_wind_update(event)

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    # ---- public helpers ----

    def set_station(self, lat: float, lon: float, heading: float = 0.0) -> dict:
        """设定目标站位。"""
        self._station = {"lat": lat, "lon": lon, "heading": heading}
        self._dp_mode = "station_keeping"
        return {
            "status": "station_set",
            "station": self._station,
            "dp_mode": self._dp_mode,
        }

    def compute_position_error(self) -> dict:
        """计算当前位置与目标站位的偏差。"""
        if self._station is None:
            return {"error": "no station set", "distance_m": 0.0, "heading_error_deg": 0.0}

        distance = _haversine_m(
            self._current_position["lat"],
            self._current_position["lon"],
            self._station["lat"],
            self._station["lon"],
        )
        heading_error = self._station["heading"] - self._current_position["heading"]
        # 归一化到 [-180, 180]
        heading_error = (heading_error + 180) % 360 - 180

        return {
            "distance_m": round(distance, 2),
            "heading_error_deg": round(heading_error, 2),
            "within_limit": distance <= self._excursion_limit_m,
        }

    def compute_thruster_allocation(self) -> dict:
        """基于位置偏差计算推力分配（简化 PID 模型）。"""
        error = self.compute_position_error()
        distance = error["distance_m"]
        heading_err = error["heading_error_deg"]

        if self._station is None:
            return {"allocated": False, "reason": "no station set", "thrusters": self._thrusters}

        # 简化 PID: 推力比例 = 偏差 / 限值, 上限 100%
        thrust_ratio = min(distance / self._excursion_limit_m, 1.0) if self._excursion_limit_m > 0 else 0.0
        heading_ratio = min(abs(heading_err) / 180.0, 1.0)

        # 方位角: 从当前位置指向目标站位
        if distance > 0.1 and self._station is not None:
            bearing = self._calculate_bearing(
                self._current_position["lat"],
                self._current_position["lon"],
                self._station["lat"],
                self._station["lon"],
            )
        else:
            bearing = 0.0

        for thruster in self._thrusters:
            if thruster["type"] == "tunnel":
                thruster["thrust_pct"] = round(heading_ratio * 100, 1)
            else:
                thruster["thrust_pct"] = round(thrust_ratio * 100, 1)
                thruster["azimuth_deg"] = round(bearing, 1)

        return {
            "allocated": True,
            "thrust_ratio": round(thrust_ratio, 3),
            "bearing_deg": round(bearing, 1),
            "thrusters": self._thrusters,
        }

    def get_capability_plot(self, wind_speed: float = 0.0, current_speed: float = 0.0) -> dict:
        """计算 DP 能力（最大可抗风速/流速）。"""
        # 简化模型: 4 个推进器，每个最大推力 100kN
        max_thrust_kn = 400.0
        # 风力 ≈ 0.5 * rho * Cd * A * V^2  (简化系数)
        wind_force_kn = 0.05 * wind_speed ** 2
        current_force_kn = 0.1 * current_speed ** 2
        total_env_force = wind_force_kn + current_force_kn
        utilisation = total_env_force / max_thrust_kn if max_thrust_kn > 0 else 0.0

        # 最大可抗风速 (current=0时)
        max_wind = math.sqrt(max_thrust_kn / 0.05) if 0.05 > 0 else 0.0
        # 最大可抗流速 (wind=0时)
        max_current = math.sqrt(max_thrust_kn / 0.1) if 0.1 > 0 else 0.0

        return {
            "max_thrust_kn": max_thrust_kn,
            "wind_force_kn": round(wind_force_kn, 2),
            "current_force_kn": round(current_force_kn, 2),
            "total_env_force_kn": round(total_env_force, 2),
            "utilisation_pct": round(utilisation * 100, 1),
            "capable": utilisation < 1.0,
            "max_wind_speed": round(max_wind, 1),
            "max_current_speed": round(max_current, 1),
        }

    # ---- event handlers ----

    def _handle_position_update(self, event: dict) -> dict:
        lat = event.get("lat")
        lon = event.get("lon")
        if any(v is None for v in [lat, lon]):
            return {"status": "error", "reason": "lat and lon are required"}

        heading = event.get("heading", self._current_position["heading"])
        self._current_position = {"lat": lat, "lon": lon, "heading": heading}

        excursion = self._compute_excursion_m()
        alarm = excursion > self._excursion_limit_m if self._station else False

        if alarm:
            self._set_health(ChannelStatus.WARN, f"Excursion {excursion:.1f}m > limit {self._excursion_limit_m}m")

        return {
            "status": "processed",
            "excursion_m": round(excursion, 2),
            "alarm": alarm,
            "dp_mode": self._dp_mode,
        }

    def _handle_set_station(self, event: dict) -> dict:
        lat = event.get("lat")
        lon = event.get("lon")
        if any(v is None for v in [lat, lon]):
            return {"status": "error", "reason": "lat and lon are required"}
        heading = event.get("heading", 0.0)
        return self.set_station(lat, lon, heading)

    def _handle_wind_update(self, event: dict) -> dict:
        self._wind_speed = event.get("wind_speed", 0.0)
        return {"status": "processed", "wind_speed": self._wind_speed}

    # ---- internal ----

    def _compute_excursion_m(self) -> float:
        if self._station is None:
            return 0.0
        return _haversine_m(
            self._current_position["lat"],
            self._current_position["lon"],
            self._station["lat"],
            self._station["lon"],
        )

    @staticmethod
    def _calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """计算从点1到点2的方位角 (度)。"""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dlam = math.radians(lon2 - lon1)
        x = math.sin(dlam) * math.cos(phi2)
        y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
        bearing = math.degrees(math.atan2(x, y))
        return (bearing + 360) % 360
