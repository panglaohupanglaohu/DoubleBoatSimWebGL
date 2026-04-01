# -*- coding: utf-8 -*-
"""
L2: Maintenance Planner Channel - 维修计划管理 (PMS)

设备维修计划和状态跟踪，工单管理。
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)

VALID_CATEGORIES = {"engine", "navigation", "safety", "hull", "electrical"}
VALID_STATUSES = {"ok", "maintenance_due", "overdue", "out_of_service"}
VALID_WO_STATUSES = {"open", "in_progress", "completed", "cancelled"}


class MaintenancePlannerChannel(MarineChannel):
    """维修计划管理 Channel — PMS 设备跟踪与工单管理。"""

    name = "maintenance_planner"
    description = "设备维修计划与工单管理"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._equipment: Dict[str, Dict[str, Any]] = {}
        self._work_orders: List[Dict[str, Any]] = []

    # ---- lifecycle ----

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Maintenance planner ready")
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

    def register_equipment(self, equip_id: str, name: str, category: str,
                           maintenance_interval_hours: float = 500) -> dict:
        equip = {
            "equip_id": equip_id,
            "name": name,
            "category": category,
            "running_hours": 0.0,
            "last_maintenance_hours": 0.0,
            "maintenance_interval_hours": maintenance_interval_hours,
            "status": "ok",
        }
        self._equipment[equip_id] = equip
        return {"status": "registered", "equipment": equip}

    def update_running_hours(self, equip_id: str, hours: float) -> dict:
        equip = self._equipment.get(equip_id)
        if equip is None:
            return {"status": "error", "reason": f"equipment {equip_id} not found"}
        equip["running_hours"] = hours
        self._check_maintenance_status(equip)
        return {"status": "updated", "equipment": equip}

    def record_maintenance(self, equip_id: str) -> dict:
        equip = self._equipment.get(equip_id)
        if equip is None:
            return {"status": "error", "reason": f"equipment {equip_id} not found"}
        equip["last_maintenance_hours"] = equip["running_hours"]
        equip["status"] = "ok"
        return {"status": "maintenance_recorded", "equipment": equip}

    def create_work_order(self, equip_id: str, description: str, priority: int = 3) -> dict:
        wo = {
            "work_order_id": str(uuid.uuid4())[:8],
            "equip_id": equip_id,
            "description": description,
            "priority": max(1, min(5, priority)),
            "status": "open",
            "created_at": datetime.now().isoformat(),
        }
        self._work_orders.append(wo)
        return {"status": "work_order_created", "work_order": wo}

    def get_maintenance_summary(self) -> dict:
        due_count = sum(1 for e in self._equipment.values() if e["status"] == "maintenance_due")
        overdue_count = sum(1 for e in self._equipment.values() if e["status"] == "overdue")
        open_wo = sum(1 for wo in self._work_orders if wo["status"] in ("open", "in_progress"))

        # 找最近下一个需要维修的设备
        next_maint: Optional[Dict[str, Any]] = None
        min_remaining = float("inf")
        for equip in self._equipment.values():
            interval = equip["maintenance_interval_hours"]
            since_last = equip["running_hours"] - equip["last_maintenance_hours"]
            remaining = interval - since_last
            if remaining < min_remaining:
                min_remaining = remaining
                next_maint = {
                    "equip_id": equip["equip_id"],
                    "name": equip["name"],
                    "remaining_hours": remaining,
                }

        return {
            "total_equipment": len(self._equipment),
            "due_count": due_count,
            "overdue_count": overdue_count,
            "open_work_orders": open_wo,
            "next_maintenance": next_maint,
        }

    # ---- event processing ----

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "equipment_update":
            equip_id = event.get("equip_id")
            hours = event.get("running_hours")
            if equip_id is None or hours is None:
                return {"status": "error", "reason": "equip_id and running_hours required"}
            return self.update_running_hours(equip_id, hours)
        elif event_type == "maintenance_complete":
            equip_id = event.get("equip_id")
            if equip_id is None:
                return {"status": "error", "reason": "equip_id required"}
            return self.record_maintenance(equip_id)
        elif event_type == "work_order":
            equip_id = event.get("equip_id", "")
            desc = event.get("description", "")
            prio = event.get("priority", 3)
            return self.create_work_order(equip_id, desc, prio)

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    def get_status(self) -> Dict[str, Any]:
        summary = self.get_maintenance_summary()
        return {
            "name": self.name,
            "total_equipment": summary["total_equipment"],
            "due_count": summary["due_count"],
            "overdue_count": summary["overdue_count"],
            "open_work_orders": summary["open_work_orders"],
            "initialized": self._initialized,
            "health": self._health.status.value,
        }

    # ---- internal ----

    @staticmethod
    def _check_maintenance_status(equip: dict) -> None:
        interval = equip["maintenance_interval_hours"]
        since_last = equip["running_hours"] - equip["last_maintenance_hours"]
        if since_last >= interval * 1.1:
            equip["status"] = "overdue"
        elif since_last >= interval:
            equip["status"] = "maintenance_due"
        else:
            equip["status"] = "ok"
