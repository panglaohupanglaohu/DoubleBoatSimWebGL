# -*- coding: utf-8 -*-
"""
L2: Alarm Management — 集中告警管理

集中管理全船告警的触发、确认、静音和清除。
"""

from __future__ import annotations

import logging
import time
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)

# IMO A.1021(26) alarm priority levels
_PRIORITY_ORDER = {"emergency": 0, "alarm": 1, "warning": 2, "caution": 3}
_MAX_HISTORY = 100
_ESCALATION_TIMEOUT_S = 30.0  # IMO A.1021(26) unack escalation


class AlarmManagementChannel(MarineChannel):
    """集中告警管理 Channel — 统一管理全船告警优先级、确认和静音。"""

    name = "alarm_management"
    description = "全船告警集中管理"
    version = "1.0.0"
    priority = ChannelPriority.P0

    def __init__(self, config=None, bus=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._alarms: Dict[str, Dict[str, Any]] = {}
        self._alarm_history: deque = deque(maxlen=_MAX_HISTORY)
        self._bus = bus

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Alarm management ready")
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

    def raise_alarm(self, alarm_id: str, source_channel: str,
                    priority: str, description: str) -> dict:
        """触发告警。"""
        if priority not in _PRIORITY_ORDER:
            priority = "caution"

        now = time.time()
        self._alarms[alarm_id] = {
            "alarm_id": alarm_id,
            "source_channel": source_channel,
            "priority": priority,
            "description": description,
            "active": True,
            "acknowledged": False,
            "silenced": False,
            "timestamp": now,
            "acknowledge_time": None,
        }

        self._update_health()
        result = {
            "alarm_id": alarm_id,
            "priority": priority,
            "raised": True,
            "total_active": len(self._alarms),
        }
        if self._bus is not None:
            try:
                from .marine_message_bus import MarineMessage, MessageType, MessagePriority
                msg = MarineMessage(
                    message_type=MessageType.SAFETY_ALERT,
                    priority=MessagePriority.URGENCY,
                    sender_channel=self.name,
                    subject="alarm.raised",
                    content={"alarm_id": alarm_id, "priority": priority,
                             "source_channel": source_channel,
                             "description": description},
                )
                self._bus.publish_sync(msg)
            except Exception as e:
                logger.warning(f"Alarm processing error: {e}")
        return result

    def acknowledge_alarm(self, alarm_id: str) -> dict:
        """确认告警。"""
        alarm = self._alarms.get(alarm_id)
        if alarm is None:
            return {"alarm_id": alarm_id, "acknowledged": False, "reason": "not found"}
        alarm["acknowledged"] = True
        alarm["acknowledge_time"] = time.time()
        return {"alarm_id": alarm_id, "acknowledged": True}

    def silence_alarm(self, alarm_id: str) -> dict:
        """静音告警。"""
        alarm = self._alarms.get(alarm_id)
        if alarm is None:
            return {"alarm_id": alarm_id, "silenced": False, "reason": "not found"}
        alarm["silenced"] = True
        return {"alarm_id": alarm_id, "silenced": True}

    def clear_alarm(self, alarm_id: str) -> dict:
        """清除告警（移入历史）。"""
        alarm = self._alarms.pop(alarm_id, None)
        if alarm is None:
            return {"alarm_id": alarm_id, "cleared": False, "reason": "not found"}
        alarm["active"] = False
        alarm["cleared_time"] = time.time()
        self._alarm_history.append(alarm)
        self._update_health()
        return {"alarm_id": alarm_id, "cleared": True}

    def get_active_alarms(self) -> list:
        """返回所有活跃告警（按优先级排序）。"""
        return sorted(
            self._alarms.values(),
            key=lambda a: _PRIORITY_ORDER.get(a["priority"], 99),
        )

    def get_alarm_summary(self) -> dict:
        """获取告警摘要。"""
        alarms = list(self._alarms.values())
        emergency_count = sum(1 for a in alarms if a["priority"] == "emergency")
        alarm_count = sum(1 for a in alarms if a["priority"] == "alarm")
        warning_count = sum(1 for a in alarms if a["priority"] == "warning")
        caution_count = sum(1 for a in alarms if a["priority"] == "caution")
        unacknowledged = [a for a in alarms if not a["acknowledged"]]

        oldest_unack: Optional[dict] = None
        if unacknowledged:
            oldest_unack = min(unacknowledged, key=lambda a: a["timestamp"])

        return {
            "total_active": len(alarms),
            "emergency_count": emergency_count,
            "alarm_count": alarm_count,
            "warning_count": warning_count,
            "caution_count": caution_count,
            "unacknowledged_count": len(unacknowledged),
            "oldest_unacknowledged": oldest_unack,
        }

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")
        if event_type == "raise_alarm":
            result = self.raise_alarm(
                alarm_id=event.get("alarm_id", ""),
                source_channel=event.get("source_channel", ""),
                priority=event.get("priority", "caution"),
                description=event.get("description", ""),
            )
            return {"status": "raised", **result}
        elif event_type == "channel_alarm":
            result = self.raise_alarm(
                alarm_id=event.get("alarm_id", ""),
                source_channel=event.get("source_channel", ""),
                priority=event.get("priority", "caution"),
                description=event.get("description", ""),
            )
            return {"status": "raised", **result}
        elif event_type == "acknowledge_alarm":
            result = self.acknowledge_alarm(alarm_id=event.get("alarm_id", ""))
            return {"status": "acknowledged", **result}
        elif event_type == "clear_alarm":
            result = self.clear_alarm(alarm_id=event.get("alarm_id", ""))
            return {"status": "cleared", **result}
        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    def get_status(self) -> Dict[str, Any]:
        summary = self.get_alarm_summary()
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "total_active": summary["total_active"],
            "emergency_count": summary["emergency_count"],
            "unacknowledged_count": summary["unacknowledged_count"],
        }

    def get_unacknowledged_escalations(self):
        now = time.time()
        result = []
        for a in self._alarms.values():
            if not a["acknowledged"] and (now - a["timestamp"]) > _ESCALATION_TIMEOUT_S:
                result.append({"alarm_id": a["alarm_id"], "priority": a["priority"],
                    "elapsed_s": round(now - a["timestamp"], 1)})
        return sorted(result, key=lambda x: _PRIORITY_ORDER.get(x["priority"], 99))

    def _update_health(self):
        """根据告警状态更新Channel健康。"""
        summary = self.get_alarm_summary()
        if summary["emergency_count"] > 0:
            self._set_health(ChannelStatus.ERROR, f"{summary['emergency_count']} emergency alarm(s)")
        elif summary["alarm_count"] > 0:
            self._set_health(ChannelStatus.WARN, f"{summary['alarm_count']} active alarm(s)")
        else:
            self._set_health(ChannelStatus.OK, "No critical alarms")
