# -*- coding: utf-8 -*-
"""
L2: Fire Detection Channel - 火灾探测

监测各区域温度、烟雾浓度和 CO 浓度传感器读数，
评估火灾风险并管理告警状态。

火灾风险阈值:
- 温度 > 80°C → 火灾风险
- 烟雾浓度 > 0.5 → 火灾风险
- CO > 50 ppm → 火灾风险
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class FireDetectionChannel(MarineChannel):
    """火灾探测 Channel — 传感器监测、风险评估与告警管理。"""

    name = "fire_detection"
    description = "火灾探测与告警管理"
    version = "1.0.0"
    priority = ChannelPriority.P0

    # 阈值常量
    TEMP_THRESHOLD: float = 80.0     # SOLAS II-2 fixed temp
    SMOKE_THRESHOLD: float = 0.5    # Photoelectric smoke
    CO_THRESHOLD: float = 50.0      # CO detector (OSHA PEL)
    SOLAS_ALARM_DEADLINE_S = 60.0   # SOLAS II-2/7.4 alarm deadline

    def __init__(self, config=None, bus=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        # 各区域最新传感器读数: zone_id -> {temperature, smoke_level, co_ppm, updated_at}
        self._zones: Dict[str, Dict[str, Any]] = {}
        # 活跃告警: alarm_id -> {zone_id, alarm_type, triggered_at, acknowledged}
        self._active_alarms: Dict[str, Dict[str, Any]] = {}
        # 历史告警
        self._alarm_history: List[Dict[str, Any]] = []
        self._alarm_counter: int = 0
        self._bus = bus

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Fire detection ready")
        return True

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "zones": {zid: self._zone_summary(zdata) for zid, zdata in self._zones.items()},
            "active_alarms": list(self._active_alarms.values()),
            "alarm_history_count": len(self._alarm_history),
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

        if event_type == "sensor_reading":
            return self._handle_sensor_reading(event)
        elif event_type == "alarm_trigger":
            return self._handle_alarm_trigger(event)
        elif event_type == "alarm_acknowledge":
            return self._handle_alarm_acknowledge(event)

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    # ---- event handlers ----

    def _handle_sensor_reading(self, event: dict) -> dict:
        zone_id = event.get("zone_id")
        if zone_id is None:
            return {"status": "error", "reason": "zone_id is required"}

        reading = {
            "zone_id": zone_id,
            "temperature": event.get("temperature", 0.0),
            "smoke_level": event.get("smoke_level", 0.0),
            "co_ppm": event.get("co_ppm", 0.0),
            "updated_at": datetime.now().isoformat(),
        }
        self._zones[zone_id] = reading

        # 自动评估火灾风险
        risk = self.evaluate_fire_risk(zone_id)
        if risk["fire_risk"]:
            alarm = self._create_alarm(zone_id, "auto_fire_risk", risk["reasons"])
            return {"status": "risk_detected", "zone_id": zone_id, "risk": risk, "alarm": alarm}

        return {"status": "recorded", "zone_id": zone_id, "risk": risk}

    def _handle_alarm_trigger(self, event: dict) -> dict:
        zone_id = event.get("zone_id")
        alarm_type = event.get("alarm_type", "manual")
        if zone_id is None:
            return {"status": "error", "reason": "zone_id is required"}

        alarm = self._create_alarm(zone_id, alarm_type)
        return {"status": "alarm_triggered", "alarm": alarm}

    def _handle_alarm_acknowledge(self, event: dict) -> dict:
        alarm_id = event.get("alarm_id")
        if alarm_id is None:
            return {"status": "error", "reason": "alarm_id is required"}

        if alarm_id not in self._active_alarms:
            return {"status": "error", "reason": f"alarm {alarm_id} not found or already resolved"}

        alarm = self._active_alarms.pop(alarm_id)
        alarm["acknowledged"] = True
        alarm["acknowledged_at"] = datetime.now().isoformat()
        self._alarm_history.append(alarm)

        # 如果没有更多活跃告警，恢复正常状态
        if not self._active_alarms:
            self._set_health(ChannelStatus.OK, "All alarms acknowledged")

        return {"status": "acknowledged", "alarm_id": alarm_id}

    # ---- core algorithms ----

    def evaluate_fire_risk(self, zone_id: str) -> Dict[str, Any]:
        """评估指定区域的火灾风险。

        温度 > 80°C 或 烟雾 > 0.5 或 CO > 50ppm → 火灾风险
        """
        zone = self._zones.get(zone_id)
        if zone is None:
            return {"fire_risk": False, "zone_id": zone_id, "reasons": [], "message": "zone not found"}

        reasons: List[str] = []
        temp = zone.get("temperature", 0.0)
        smoke = zone.get("smoke_level", 0.0)
        co = zone.get("co_ppm", 0.0)

        if temp > self.TEMP_THRESHOLD:
            reasons.append(f"温度 {temp}°C 超过阈值 {self.TEMP_THRESHOLD}°C")
        if smoke > self.SMOKE_THRESHOLD:
            reasons.append(f"烟雾浓度 {smoke} 超过阈值 {self.SMOKE_THRESHOLD}")
        if co > self.CO_THRESHOLD:
            reasons.append(f"CO 浓度 {co}ppm 超过阈值 {self.CO_THRESHOLD}ppm")

        fire_risk = len(reasons) > 0
        return {
            "fire_risk": fire_risk,
            "zone_id": zone_id,
            "reasons": reasons,
            "message": "火灾风险" if fire_risk else "正常",
        }

    # ---- helpers ----

    def _create_alarm(self, zone_id: str, alarm_type: str, reasons: list = None) -> Dict[str, Any]:
        self._alarm_counter += 1
        alarm_id = f"FIRE-{self._alarm_counter:04d}"
        alarm = {
            "alarm_id": alarm_id,
            "zone_id": zone_id,
            "alarm_type": alarm_type,
            "reasons": reasons or [],
            "triggered_at": datetime.now().isoformat(),
            "acknowledged": False,
        }
        self._active_alarms[alarm_id] = alarm
        self._set_health(ChannelStatus.WARN, f"Fire alarm active in zone {zone_id}")
        logger.warning(f"🔥 Fire alarm {alarm_id} triggered in zone {zone_id}: {alarm_type}")
        if self._bus is not None:
            try:
                from .marine_message_bus import MarineMessage, MessageType, MessagePriority
                msg = MarineMessage(
                    message_type=MessageType.SAFETY_ALERT,
                    priority=MessagePriority.DISTRESS,
                    sender_channel=self.name,
                    subject="fire.alarm",
                    content={"alarm_id": alarm_id, "zone_id": zone_id,
                             "alarm_type": alarm_type},
                )
                self._bus.publish_sync(msg)
            except Exception as e:
                logger.warning(f"Fire detection error: {e}")
        return alarm

    def _zone_summary(self, zone: Dict[str, Any]) -> Dict[str, Any]:
        zone_id = zone.get("zone_id", "")
        risk = self.evaluate_fire_risk(zone_id)
        return {
            **zone,
            "fire_risk": risk["fire_risk"],
        }
