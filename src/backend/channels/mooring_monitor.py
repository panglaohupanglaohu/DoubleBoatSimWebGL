# -*- coding: utf-8 -*-
"""
L2: Mooring Monitor — 锚泊/系泊监控

系泊操作监控（系缆载荷、绞缆机状态）。
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)

VALID_MOORING_MODES = ("free", "alongside", "buoy", "anchor")
VALID_LINE_POSITIONS = (
    "bow_port", "bow_stbd", "stern_port", "stern_stbd",
    "spring_fwd", "spring_aft",
)


class MooringMonitorChannel(MarineChannel):
    """系泊监控 Channel — 系缆载荷与绞缆机状态监控。"""

    name = "mooring_monitor"
    description = "锚泊/系泊监控（系缆载荷/绞缆机）"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._lines: Dict[str, Dict[str, Any]] = {}
        self._winches: Dict[str, Dict[str, Any]] = {}
        self._mooring_mode: str = "free"

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Mooring monitor ready")
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

    def update_line(
        self,
        line_id: str,
        position: str,
        tension_kn: float,
        breaking_load_kn: float = 500.0,
    ) -> dict:
        """更新系缆状态，自动判断status。"""
        if tension_kn >= breaking_load_kn:
            status = "parted"
        elif tension_kn > 0.7 * breaking_load_kn:
            status = "strained"
        elif tension_kn < 5.0:
            status = "slack"
        else:
            status = "secured"

        self._lines[line_id] = {
            "line_id": line_id,
            "position": position,
            "tension_kn": tension_kn,
            "breaking_load_kn": breaking_load_kn,
            "status": status,
        }

        if status == "parted":
            self._set_health(ChannelStatus.ERROR, f"Line {line_id} parted!")
        elif status == "strained":
            self._set_health(ChannelStatus.WARN, f"Line {line_id} strained")

        return {
            "line_id": line_id,
            "status": status,
            "tension_kn": tension_kn,
            "load_ratio": round(tension_kn / breaking_load_kn, 3) if breaking_load_kn > 0 else 0.0,
        }

    def update_winch(
        self,
        winch_id: str,
        line_id: str,
        brake_set: bool = True,
        motor_running: bool = False,
        auto_tension: bool = False,
    ) -> dict:
        """更新绞缆机状态。"""
        self._winches[winch_id] = {
            "winch_id": winch_id,
            "line_id": line_id,
            "brake_set": brake_set,
            "motor_running": motor_running,
            "auto_tension": auto_tension,
        }
        return {
            "winch_id": winch_id,
            "line_id": line_id,
            "brake_set": brake_set,
        }

    def set_mooring_mode(self, mode: str) -> dict:
        """设置系泊模式。"""
        if mode not in VALID_MOORING_MODES:
            return {"status": "error", "reason": f"invalid mode: {mode}"}
        old_mode = self._mooring_mode
        self._mooring_mode = mode
        logger.info("Mooring mode changed: %s -> %s", old_mode, mode)
        return {"status": "ok", "old_mode": old_mode, "new_mode": mode}

    def get_mooring_status(self) -> dict:
        """返回系泊完整状态。"""
        lines = dict(self._lines)
        winches = dict(self._winches)

        all_secured = (
            len(lines) > 0 and all(l["status"] == "secured" for l in lines.values())
        )
        any_strained = any(l["status"] == "strained" for l in lines.values())
        any_parted = any(l["status"] == "parted" for l in lines.values())

        load_ratios = [
            l["tension_kn"] / l["breaking_load_kn"]
            for l in lines.values()
            if l["breaking_load_kn"] > 0
        ]
        max_load_ratio = round(max(load_ratios), 3) if load_ratios else 0.0

        return {
            "mode": self._mooring_mode,
            "lines": lines,
            "winches": winches,
            "all_secured": all_secured,
            "any_strained": any_strained,
            "any_parted": any_parted,
            "max_load_ratio": max_load_ratio,
        }

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "line_reading":
            line_id = event.get("line_id")
            if line_id is None:
                return {"status": "error", "reason": "line_id is required"}
            result = self.update_line(
                line_id,
                position=event.get("position", "bow_port"),
                tension_kn=event.get("tension_kn", 0.0),
                breaking_load_kn=event.get("breaking_load_kn", 500.0),
            )
            return {**result, "event_status": "updated"}

        if event_type == "winch_update":
            winch_id = event.get("winch_id")
            if winch_id is None:
                return {"status": "error", "reason": "winch_id is required"}
            result = self.update_winch(
                winch_id,
                line_id=event.get("line_id", ""),
                brake_set=event.get("brake_set", True),
                motor_running=event.get("motor_running", False),
                auto_tension=event.get("auto_tension", False),
            )
            return {**result, "event_status": "updated"}

        if event_type == "mooring_mode":
            mode = event.get("mode", "free")
            return self.set_mooring_mode(mode)

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    def get_status(self) -> Dict[str, Any]:
        lines = self._lines
        load_ratios = [
            l["tension_kn"] / l["breaking_load_kn"]
            for l in lines.values()
            if l["breaking_load_kn"] > 0
        ]
        max_load_ratio = round(max(load_ratios), 3) if load_ratios else 0.0
        all_secured = (
            len(lines) > 0 and all(l["status"] == "secured" for l in lines.values())
        )
        any_parted = any(l["status"] == "parted" for l in lines.values())

        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "mooring_mode": self._mooring_mode,
            "line_count": len(lines),
            "all_secured": all_secured,
            "any_parted": any_parted,
            "max_load_ratio": max_load_ratio,
        }
