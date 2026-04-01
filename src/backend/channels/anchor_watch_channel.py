# -*- coding: utf-8 -*-
"""
L2: Anchor Watch Channel - 锚泊监控

监测锚位、摆动半径和走锚状态，提供走锚告警。
基于锚泊位置和当前 GPS 位置计算漂移距离，
当漂移距离超过摆动半径时触发告警。

摆动半径估算:
- swing_radius ≈ sqrt(chain_length² - depth²) 锚链悬垂线近似
"""

from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Any, Dict, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算两个经纬度点之间的距离 (米)。"""
    R = 6_371_000  # 地球平均半径 (m)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class AnchorWatchChannel(MarineChannel):
    """锚泊监控 Channel — 检测走锚与摆动范围。"""

    name = "anchor_watch"
    description = "锚泊监控与走锚告警"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._anchored: bool = False
        self._anchor_position: Optional[Dict[str, float]] = None
        self._depth: float = 0.0
        self._chain_length: float = 0.0
        self._swing_radius: float = 0.0
        self._current_position: Optional[Dict[str, float]] = None
        self._drift_distance: float = 0.0
        self._alarm_status: str = "normal"
        self._anchor_time: Optional[str] = None

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Anchor watch ready")
        return True

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "anchored": self._anchored,
            "anchor_position": self._anchor_position,
            "swing_radius": self._swing_radius,
            "drift_distance": self._drift_distance,
            "alarm_status": self._alarm_status,
            "depth": self._depth,
            "chain_length": self._chain_length,
            "anchor_time": self._anchor_time,
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

        if event_type == "anchor_drop":
            return self._handle_anchor_drop(event)
        elif event_type == "position_update":
            return self._handle_position_update(event)
        elif event_type == "anchor_weigh":
            return self._handle_anchor_weigh(event)

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    # ---- event handlers ----

    def _handle_anchor_drop(self, event: dict) -> dict:
        lat = event.get("position_lat")
        lon = event.get("position_lon")
        if any(v is None for v in [lat, lon]):
            return {"status": "error", "reason": "position_lat and position_lon are required"}

        depth = event.get("depth", 0.0)
        chain_length = event.get("chain_length", 0.0)

        self._anchored = True
        self._anchor_position = {"lat": lat, "lon": lon}
        self._depth = depth
        self._chain_length = chain_length
        self._swing_radius = self._calculate_swing_radius(depth, chain_length)
        self._drift_distance = 0.0
        self._alarm_status = "normal"
        self._anchor_time = datetime.now().isoformat()
        self._current_position = {"lat": lat, "lon": lon}

        return {
            "status": "processed",
            "anchored": True,
            "swing_radius": self._swing_radius,
        }

    def _handle_position_update(self, event: dict) -> dict:
        lat = event.get("lat")
        lon = event.get("lon")
        if any(v is None for v in [lat, lon]):
            return {"status": "error", "reason": "lat and lon are required"}

        self._current_position = {"lat": lat, "lon": lon}

        if self._anchored and self._anchor_position is not None:
            self._drift_distance = _haversine_m(
                self._anchor_position["lat"],
                self._anchor_position["lon"],
                lat,
                lon,
            )
            dragging = self.check_dragging()
            return {
                "status": "processed",
                "drift_distance": self._drift_distance,
                "dragging": dragging["dragging"],
                "alarm_status": self._alarm_status,
            }

        return {"status": "processed", "drift_distance": 0.0, "dragging": False}

    def _handle_anchor_weigh(self, event: dict) -> dict:
        self._anchored = False
        self._anchor_position = None
        self._drift_distance = 0.0
        self._alarm_status = "normal"
        self._swing_radius = 0.0
        self._depth = 0.0
        self._chain_length = 0.0
        self._anchor_time = None
        return {"status": "processed", "anchored": False}

    # ---- dragging check ----

    def check_dragging(self) -> Dict[str, Any]:
        """检查是否走锚。

        当前位置与锚位距离 > swing_radius 时告警。

        Returns:
            走锚状态字典。
        """
        if not self._anchored or self._anchor_position is None:
            return {"dragging": False, "details": "Not anchored"}

        if self._current_position is None:
            return {"dragging": False, "details": "No position data"}

        dragging = self._drift_distance > self._swing_radius
        if dragging:
            self._alarm_status = "dragging"
        else:
            self._alarm_status = "normal"

        return {
            "dragging": dragging,
            "drift_distance": self._drift_distance,
            "swing_radius": self._swing_radius,
            "alarm_status": self._alarm_status,
            "details": f"Drift {self._drift_distance:.1f}m vs radius {self._swing_radius:.1f}m",
        }

    # ---- helpers ----

    @staticmethod
    def _calculate_swing_radius(depth: float, chain_length: float) -> float:
        """估算摆动半径 (m)。

        swing_radius ≈ sqrt(chain_length² - depth²)
        """
        if chain_length <= depth:
            return chain_length  # 锚链不够长，以锚链长度为半径
        return math.sqrt(chain_length ** 2 - depth ** 2)
