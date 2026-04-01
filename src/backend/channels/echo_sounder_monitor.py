# -*- coding: utf-8 -*-
"""
L2: Echo Sounder Monitor — 测深仪监控

监控水深并提供搁浅预警，跟踪深度趋势。
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any, Dict, List

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)

_MAX_HISTORY = 100


class EchoSounderMonitorChannel(MarineChannel):
    """测深仪监控 Channel — 水深监控和搁浅预警。"""

    name = "echo_sounder_monitor"
    description = "测深仪监控与搁浅预警"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._current_depth_m: float = 0.0
        self._draught_m: float = 5.0
        self._safety_contour_m: float = 10.0
        self._shallow_alarm_m: float = 8.0
        self._depth_history: List[Dict[str, Any]] = []

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Echo sounder monitor ready")
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

    def update_depth(self, depth_m: float, transducer_offset_m: float = 0.0) -> dict:
        """更新深度读数。depth = raw_depth + offset"""
        corrected = depth_m + transducer_offset_m
        self._current_depth_m = corrected

        self._depth_history.append({
            "depth_m": corrected,
            "timestamp": time.time(),
        })
        if len(self._depth_history) > _MAX_HISTORY:
            self._depth_history = self._depth_history[-_MAX_HISTORY:]

        shallow = corrected < self._shallow_alarm_m
        if shallow:
            self._set_health(ChannelStatus.WARN, f"Shallow water: {corrected:.1f}m")
        else:
            self._set_health(ChannelStatus.OK, "Depth normal")

        return {
            "status": "ok",
            "current_depth_m": round(corrected, 2),
            "shallow_alarm": shallow,
        }

    def _calculate_trend(self) -> str:
        """基于最近 10 个读数的线性回归简化趋势。"""
        recent = self._depth_history[-10:]
        if len(recent) < 3:
            return "steady"

        depths = [r["depth_m"] for r in recent]
        n = len(depths)
        x_mean = (n - 1) / 2.0
        y_mean = sum(depths) / n
        numerator = sum((i - x_mean) * (d - y_mean) for i, d in enumerate(depths))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "steady"

        slope = numerator / denominator

        if slope < -0.1:
            return "shoaling"
        elif slope > 0.1:
            return "deepening"
        return "steady"

    def get_depth_status(self) -> dict:
        """返回完整深度状态。"""
        underkeel = self._current_depth_m - self._draught_m
        trend = self._calculate_trend()
        shallow = self._current_depth_m < self._shallow_alarm_m
        grounding = underkeel < 2.0

        return {
            "current_depth_m": round(self._current_depth_m, 2),
            "underkeel_clearance_m": round(underkeel, 2),
            "depth_trend": trend,
            "shallow_alarm": shallow,
            "grounding_risk": grounding,
            "draught_m": self._draught_m,
            "safety_contour_m": self._safety_contour_m,
            "readings_count": len(self._depth_history),
        }

    def get_status(self) -> Dict[str, Any]:
        underkeel = self._current_depth_m - self._draught_m
        shallow = self._current_depth_m < self._shallow_alarm_m
        grounding = underkeel < 2.0
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "current_depth_m": round(self._current_depth_m, 2),
            "underkeel_clearance_m": round(underkeel, 2),
            "shallow_alarm": shallow,
            "grounding_risk": grounding,
        }

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "depth_reading":
            depth_m = event.get("depth_m", 0.0)
            offset = event.get("transducer_offset_m", 0.0)
            result = self.update_depth(depth_m, offset)
            return {**result, "event_status": "updated"}

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}
