# -*- coding: utf-8 -*-
"""
Safety System Monitor Channel — 安全系统综合监控

监控所有安全系统（救生设备、消防系统、水密门等）的状态与合规性。
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)

VALID_CATEGORIES = ("life_saving", "fire_fighting", "watertight", "evacuation", "personal_protection")
VALID_SYSTEM_STATUSES = ("ready", "not_ready", "inspection_due", "fault")
VALID_DOOR_STATUSES = ("closed", "open", "fault")


class SafetySystemMonitorChannel(MarineChannel):
    """安全系统综合监控 Channel — SOLAS 安全设备与水密完整性监控。"""

    name = "safety_system_monitor"
    description = "安全系统综合监控（救生/消防/水密门/疏散/个人防护）"
    version = "1.0.0"
    priority = ChannelPriority.P0

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._systems: Dict[str, Dict[str, Any]] = {}
        self._watertight_doors: Dict[str, Dict[str, Any]] = {}

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Safety system monitor ready")
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

    def update_system(
        self,
        system_id: str,
        category: str,
        status: str,
        last_inspection: Optional[str] = None,
        next_inspection: Optional[str] = None,
    ) -> dict:
        """Update or register a safety system."""
        if category not in VALID_CATEGORIES:
            return {"status": "error", "reason": f"Invalid category: {category}"}
        if status not in VALID_SYSTEM_STATUSES:
            return {"status": "error", "reason": f"Invalid status: {status}"}

        self._systems[system_id] = {
            "system_id": system_id,
            "category": category,
            "status": status,
            "last_inspection": last_inspection,
            "next_inspection": next_inspection,
            "updated_at": datetime.now().isoformat(),
        }
        return {"status": "updated", "system_id": system_id}

    def update_watertight_door(self, door_id: str, location: str, door_status: str) -> dict:
        """Update watertight door status."""
        if door_status not in VALID_DOOR_STATUSES:
            return {"status": "error", "reason": f"Invalid door status: {door_status}"}

        alarm_active = door_status in ("open", "fault")
        self._watertight_doors[door_id] = {
            "door_id": door_id,
            "location": location,
            "status": door_status,
            "alarm_active": alarm_active,
            "updated_at": datetime.now().isoformat(),
        }
        return {"status": "updated", "door_id": door_id}

    def get_safety_status(self) -> dict:
        """Return comprehensive safety system status."""
        systems = dict(self._systems)
        total_ready = sum(1 for s in systems.values() if s["status"] == "ready")
        total_not_ready = sum(1 for s in systems.values() if s["status"] == "not_ready")
        total_fault = sum(1 for s in systems.values() if s["status"] == "fault")

        watertight_integrity = (
            len(self._watertight_doors) > 0
            and all(d["status"] == "closed" for d in self._watertight_doors.values())
        ) if self._watertight_doors else True

        solas_ready = total_not_ready == 0 and total_fault == 0 and watertight_integrity

        inspections_due = [
            s["system_id"]
            for s in systems.values()
            if s["status"] == "inspection_due"
        ]

        return {
            "systems": systems,
            "total_ready": total_ready,
            "total_not_ready": total_not_ready,
            "total_fault": total_fault,
            "watertight_integrity": watertight_integrity,
            "solas_ready": solas_ready,
            "inspections_due": inspections_due,
        }

    def get_status(self) -> Dict[str, Any]:
        safety = self.get_safety_status()
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "solas_ready": safety["solas_ready"],
            "watertight_integrity": safety["watertight_integrity"],
            "total_fault": safety["total_fault"],
            "systems_count": len(self._systems),
        }

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "safety_system_update":
            system_id = event.get("system_id")
            category = event.get("category")
            status = event.get("status")
            if any(v is None for v in [system_id, category, status]):
                return {"status": "error", "reason": "system_id, category and status are required"}
            return self.update_system(
                system_id,
                category,
                status,
                last_inspection=event.get("last_inspection"),
                next_inspection=event.get("next_inspection"),
            )

        if event_type == "watertight_door_update":
            door_id = event.get("door_id")
            location = event.get("location")
            door_status = event.get("door_status")
            if any(v is None for v in [door_id, location, door_status]):
                return {"status": "error", "reason": "door_id, location and door_status are required"}
            return self.update_watertight_door(door_id, location, door_status)

        return {"status": "ignored", "reason": f"Unknown event type: {event_type}"}
