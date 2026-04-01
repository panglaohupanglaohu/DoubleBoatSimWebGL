# -*- coding: utf-8 -*-
"""
L2: Gyro Compass Monitor — 电罗经监控

监控航向传感器（电罗经、磁罗经、GPS罗经）的一致性和可靠性。
"""

from __future__ import annotations

import math
import logging
import time
from datetime import datetime
from typing import Any, Dict, List

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class GyroCompassMonitorChannel(MarineChannel):
    """电罗经监控 Channel — 监控航向传感器一致性。"""

    name = "gyro_compass_monitor"
    description = "电罗经监控与航向一致性检测"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._compasses: Dict[str, Dict[str, Any]] = {}
        self._heading_deviation_limit_deg: float = 3.0

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Gyro compass monitor ready")
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

    def get_status(self) -> Dict[str, Any]:
        consensus = self.get_heading_consensus()
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "compass_count": len(self._compasses),
            "consensus_heading": consensus.get("consensus_heading"),
            "agreement": consensus.get("agreement"),
            "max_deviation": consensus.get("max_deviation"),
        }

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "compass_reading":
            compass_id = event.get("compass_id", "")
            compass_type = event.get("compass_type", "gyro")
            heading_deg = event.get("heading_deg", 0.0)
            rate_of_turn = event.get("rate_of_turn_deg_s", 0.0)
            result = self.update_compass(compass_id, compass_type, heading_deg, rate_of_turn)
            return {"status": "updated", **result}

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    def update_compass(self, compass_id: str, compass_type: str,
                       heading_deg: float, rate_of_turn: float = 0.0) -> dict:
        """更新罗经数据。"""
        heading_deg = heading_deg % 360.0
        status = "ok"
        self._compasses[compass_id] = {
            "compass_id": compass_id,
            "type": compass_type,
            "heading_deg": heading_deg,
            "rate_of_turn_deg_s": rate_of_turn,
            "status": status,
            "last_update": time.time(),
        }
        # 重新检查一致性，将偏差超限的标记为 warning
        self._check_consistency()
        return {
            "compass_id": compass_id,
            "heading_deg": heading_deg,
            "compass_count": len(self._compasses),
        }

    def _check_consistency(self):
        """检查所有罗经一致性，标记偏差超限的为 warning。"""
        ok_compasses = [c for c in self._compasses.values() if c["status"] in ("ok", "warning")]
        if len(ok_compasses) < 2:
            return

        consensus = self._compute_vector_average([c["heading_deg"] for c in ok_compasses])
        for c in ok_compasses:
            dev = self._angular_diff(c["heading_deg"], consensus)
            if dev > self._heading_deviation_limit_deg:
                c["status"] = "warning"
            else:
                c["status"] = "ok"

    def get_heading_consensus(self) -> dict:
        """计算所有 ok 状态罗经的航向共识。"""
        ok_compasses = [c for c in self._compasses.values() if c["status"] == "ok"]
        if not ok_compasses:
            return {
                "consensus_heading": None,
                "max_deviation": 0.0,
                "agreement": True,
                "compasses_used": 0,
                "unreliable_compasses": [],
            }

        headings = [c["heading_deg"] for c in ok_compasses]
        consensus = self._compute_vector_average(headings)

        deviations = [self._angular_diff(h, consensus) for h in headings]
        max_dev = max(deviations) if deviations else 0.0

        unreliable = []
        for c in self._compasses.values():
            if c["status"] != "ok":
                continue
            dev = self._angular_diff(c["heading_deg"], consensus)
            if dev > self._heading_deviation_limit_deg:
                unreliable.append(c["compass_id"])

        # Also include compasses already marked warning/fault
        for c in self._compasses.values():
            if c["status"] in ("warning", "fault") and c["compass_id"] not in unreliable:
                unreliable.append(c["compass_id"])

        agreement = max_dev < self._heading_deviation_limit_deg

        return {
            "consensus_heading": round(consensus, 2),
            "max_deviation": round(max_dev, 2),
            "agreement": agreement,
            "compasses_used": len(ok_compasses),
            "unreliable_compasses": unreliable,
        }

    @staticmethod
    def _compute_vector_average(headings: List[float]) -> float:
        """向量平均法计算航向平均值（正确处理 360→0 循环）。"""
        sin_sum = sum(math.sin(math.radians(h)) for h in headings)
        cos_sum = sum(math.cos(math.radians(h)) for h in headings)
        avg = math.degrees(math.atan2(sin_sum, cos_sum))
        return avg % 360.0

    @staticmethod
    def _angular_diff(a: float, b: float) -> float:
        """计算两个角度之间的最小差值 (0-180)。"""
        diff = abs(a - b) % 360.0
        return min(diff, 360.0 - diff)
