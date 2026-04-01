# -*- coding: utf-8 -*-
"""
Communication Manager Channel - 通信管理系统

船舶通信系统管理 (VHF/MF/HF/Inmarsat/VSAT),
GMDSS 合规检查和遇险通信控制。
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)

# GMDSS 所需的系统类型组合
_SATELLITE_TYPES = {"inmarsat", "vsat"}


class CommunicationManagerChannel(MarineChannel):
    """通信管理 Channel — VHF/MF/HF/Inmarsat/VSAT 管理和 GMDSS 合规。"""

    name = "communication_manager"
    description = "船舶通信系统管理与 GMDSS 合规"
    version = "1.0.0"
    priority = ChannelPriority.P0

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._systems: Dict[str, Dict[str, Any]] = {}
        self._distress_active: bool = False
        self._dsc_controller_id: str = ""

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Communication manager ready")
        return True

    def get_status(self) -> Dict[str, Any]:
        comms = self.get_comms_status()
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "systems_count": len(self._systems),
            "operational_count": comms["operational_count"],
            "gmdss_compliant": comms["gmdss_compliant"],
            "distress_active": self._distress_active,
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

    # ---- public helpers ----

    def add_system(
        self,
        name: str,
        sys_type: str,
        frequency_mhz: float = 156.8,
    ) -> Dict[str, Any]:
        """添加或更新通信系统。"""
        entry = {
            "system_name": name,
            "type": sys_type,
            "status": "operational",
            "signal_strength": 100,
            "frequency_mhz": frequency_mhz,
            "last_check": datetime.now().isoformat(),
        }
        self._systems[name] = entry
        return entry

    def update_system_status(
        self,
        name: str,
        status: str,
        signal_strength: int = 100,
    ) -> Dict[str, Any]:
        """更新通信系统状态。"""
        if name not in self._systems:
            return {"error": f"system '{name}' not found"}
        self._systems[name]["status"] = status
        self._systems[name]["signal_strength"] = signal_strength
        self._systems[name]["last_check"] = datetime.now().isoformat()
        return dict(self._systems[name])

    def get_comms_status(self) -> Dict[str, Any]:
        """获取完整通信状态。"""
        systems = list(self._systems.values())
        operational = [s for s in systems if s["status"] == "operational"]
        degraded = [s for s in systems if s["status"] == "degraded"]
        failed = [s for s in systems if s["status"] == "failed"]

        # GMDSS 合规: 至少 VHF + (MF 或 HF) + 卫星
        types_operational = {s["type"] for s in operational}
        has_vhf = "vhf" in types_operational
        has_mf_or_hf = bool(types_operational & {"mf", "hf"})
        has_satellite = bool(types_operational & _SATELLITE_TYPES)
        gmdss_compliant = has_vhf and has_mf_or_hf and has_satellite

        return {
            "systems": systems,
            "operational_count": len(operational),
            "degraded_count": len(degraded),
            "failed_count": len(failed),
            "gmdss_compliant": gmdss_compliant,
        }

    def activate_distress(self, position: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """激活遇险模式。"""
        self._distress_active = True
        logger.warning("🆘 DISTRESS activated! position=%s", position)
        return {
            "distress_active": True,
            "position": position,
            "dsc_controller_id": self._dsc_controller_id,
            "timestamp": datetime.now().isoformat(),
        }

    # ---- event processing ----

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "comms_status_update":
            return self._handle_comms_status_update(event)
        elif event_type == "distress_alert":
            return self._handle_distress_alert(event)

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    def _handle_comms_status_update(self, event: dict) -> dict:
        name = event.get("system_name")
        if name is None:
            return {"status": "error", "reason": "system_name is required"}
        status = event.get("status", "operational")
        signal = event.get("signal_strength", 100)
        if name not in self._systems:
            sys_type = event.get("sys_type", event.get("type", "vhf"))
            freq = event.get("frequency_mhz", 156.8)
            self.add_system(name, sys_type, freq)
        result = self.update_system_status(name, status, signal)
        return {"status": "updated", "system": result}

    def _handle_distress_alert(self, event: dict) -> dict:
        position = event.get("position")
        result = self.activate_distress(position)
        return {"status": "distress_activated", "result": result}
