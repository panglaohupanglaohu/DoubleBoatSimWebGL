# -*- coding: utf-8 -*-
"""
L2: LRIT Reporter — Long Range Identification and Tracking

按 IMO MSC.202(81) 实现 LRIT 合规报告。
标准 6 小时报告间隔，自动生成并维护报告历史。
"""

from __future__ import annotations

import logging
import time
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)

_MAX_REPORT_HISTORY = 50


class LRITReporterChannel(MarineChannel):
    """LRIT 远程追踪报告 Channel — IMO MSC.202(81) 合规。"""

    name = "lrit_reporter"
    description = "LRIT 远程识别与追踪报告"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._reporting_interval_hours: float = 6.0
        self._last_report_time: Optional[float] = None
        self._ship_info: dict = {
            "imo_number": None,
            "mmsi": None,
            "flag_state": "",
            "ship_name": "",
        }
        self._report_history: deque = deque(maxlen=_MAX_REPORT_HISTORY)
        self._data_center: str = ""

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "LRIT reporter ready")
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

    def set_ship_info(self, imo_number: int, mmsi: int,
                      flag_state: str, ship_name: str) -> dict:
        """设置船舶识别信息。"""
        self._ship_info = {
            "imo_number": imo_number,
            "mmsi": mmsi,
            "flag_state": flag_state,
            "ship_name": ship_name,
        }
        return {"status": "ship_info_set", "ship_info": self._ship_info}

    def generate_report(self, lat: float, lon: float) -> dict:
        """生成 LRIT 位置报告。"""
        now = time.time()
        report = {
            "ship_info": dict(self._ship_info),
            "position": {"lat": lat, "lon": lon},
            "timestamp": datetime.fromtimestamp(now).isoformat(),
            "epoch": now,
            "data_center": self._data_center,
        }
        self._last_report_time = now
        self._report_history.append(report)
        logger.info(f"📡 LRIT report generated at ({lat}, {lon})")
        return report

    def check_reporting_due(self) -> dict:
        """检查是否到报告时间。"""
        now = time.time()
        if self._last_report_time is None:
            return {
                "reporting_due": True,
                "reason": "no_previous_report",
                "elapsed_hours": None,
            }
        elapsed_seconds = now - self._last_report_time
        elapsed_hours = elapsed_seconds / 3600.0
        due = elapsed_hours >= self._reporting_interval_hours
        return {
            "reporting_due": due,
            "elapsed_hours": round(elapsed_hours, 2),
            "interval_hours": self._reporting_interval_hours,
        }

    def get_report_history(self) -> list:
        """返回最近报告记录。"""
        return list(self._report_history)

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "lrit_position_update":
            lat = event.get("lat")
            lon = event.get("lon")
            if any(v is None for v in [lat, lon]):
                return {"status": "error", "reason": "lat and lon are required"}
            due = self.check_reporting_due()
            if due["reporting_due"]:
                report = self.generate_report(lat, lon)
                return {"status": "report_generated", "report": report}
            return {"status": "not_due", "check": due}

        return {"status": "ignored", "reason": f"Unknown event type: {event_type}"}

    def get_status(self) -> Dict[str, Any]:
        due = self.check_reporting_due()
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "reporting_interval_hours": self._reporting_interval_hours,
            "last_report_time": self._last_report_time,
            "reports_sent": len(self._report_history),
            "reporting_due": due["reporting_due"],
        }
