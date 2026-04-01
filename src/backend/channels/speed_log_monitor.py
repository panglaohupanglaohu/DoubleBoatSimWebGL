# -*- coding: utf-8 -*-
"""
L2: Speed Log Monitor — 计程仪监控

监控船速传感器（对水速度、对地速度）并累计航行距离。
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class SpeedLogMonitorChannel(MarineChannel):
    """计程仪监控 Channel — 监控船速传感器并累计航行距离。"""

    name = "speed_log_monitor"
    description = "计程仪监控与船速一致性检测"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._sensors: Dict[str, Dict[str, Any]] = {}
        self._speed_deviation_limit_knots: float = 1.0
        self._distance_run_nm: float = 0.0
        self._last_distance_update: Optional[float] = None

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Speed log monitor ready")
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
        consensus = self.get_speed_consensus()
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "sensor_count": len(self._sensors),
            "average_speed_knots": consensus.get("average_speed_knots"),
            "agreement": consensus.get("agreement"),
            "distance_run_nm": round(self._distance_run_nm, 3),
        }

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "speed_reading":
            sensor_id = event.get("sensor_id", "")
            sensor_type = event.get("sensor_type", "stw")
            speed_knots = event.get("speed_knots", 0.0)
            result = self.update_sensor(sensor_id, sensor_type, speed_knots)
            return {"status": "updated", **result}

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    def update_sensor(self, sensor_id: str, sensor_type: str,
                      speed_knots: float) -> dict:
        """更新速度传感器数据。"""
        status = "ok"
        self._sensors[sensor_id] = {
            "sensor_id": sensor_id,
            "type": sensor_type,
            "speed_knots": speed_knots,
            "status": status,
            "last_update": time.time(),
        }
        self._check_consistency()
        return {
            "sensor_id": sensor_id,
            "speed_knots": speed_knots,
            "sensor_count": len(self._sensors),
        }

    def _check_consistency(self):
        """检查所有传感器一致性，标记偏差超限的为 warning。"""
        ok_sensors = [s for s in self._sensors.values() if s["status"] in ("ok", "warning")]
        if len(ok_sensors) < 2:
            return

        avg_speed = sum(s["speed_knots"] for s in ok_sensors) / len(ok_sensors)
        for s in ok_sensors:
            dev = abs(s["speed_knots"] - avg_speed)
            if dev > self._speed_deviation_limit_knots:
                s["status"] = "warning"
            else:
                s["status"] = "ok"

    def get_speed_consensus(self) -> dict:
        """计算所有 ok 状态传感器的速度共识。"""
        ok_sensors = [s for s in self._sensors.values() if s["status"] == "ok"]
        if not ok_sensors:
            return {
                "average_speed_knots": None,
                "max_deviation": 0.0,
                "agreement": True,
                "sensors_used": 0,
            }

        speeds = [s["speed_knots"] for s in ok_sensors]
        avg_speed = sum(speeds) / len(speeds)
        deviations = [abs(sp - avg_speed) for sp in speeds]
        max_dev = max(deviations) if deviations else 0.0

        agreement = max_dev < self._speed_deviation_limit_knots

        return {
            "average_speed_knots": round(avg_speed, 2),
            "max_deviation": round(max_dev, 2),
            "agreement": agreement,
            "sensors_used": len(ok_sensors),
        }

    def update_distance(self) -> dict:
        """基于平均速度和时间间隔更新累计航行距离。"""
        now = time.time()
        consensus = self.get_speed_consensus()
        avg_speed = consensus.get("average_speed_knots")

        if avg_speed is None or self._last_distance_update is None:
            self._last_distance_update = now
            return {
                "distance_run_nm": round(self._distance_run_nm, 3),
                "elapsed_h": 0.0,
                "delta_nm": 0.0,
            }

        elapsed_h = (now - self._last_distance_update) / 3600.0
        delta_nm = avg_speed * elapsed_h
        self._distance_run_nm += delta_nm
        self._last_distance_update = now

        return {
            "distance_run_nm": round(self._distance_run_nm, 3),
            "elapsed_h": round(elapsed_h, 6),
            "delta_nm": round(delta_nm, 6),
        }
