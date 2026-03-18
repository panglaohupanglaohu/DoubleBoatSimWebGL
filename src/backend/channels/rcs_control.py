# -*- coding: utf-8 -*-
"""
RCS Control Channel - 双体船主动姿态控制第一版
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelPriority, ChannelStatus, get_default_registry


RISK_WEIGHT = {"safe": 0.2, "caution": 0.45, "warning": 0.7, "danger": 1.0}


class RCSControlChannel(MarineChannel):
    name = "rcs_control"
    description = "双体船主动姿态控制 (T-Foil / Trim Tabs 第一版)"
    version = "0.1.0"
    priority = ChannelPriority.P1
    dependencies: List[str] = ["intelligent_navigation", "distributed_perception_hub"]

    def initialize(self) -> bool:
        self._initialized = True
        self._set_health(ChannelStatus.OK, "RCS control ready")
        return True

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True

    def compute_control_state(self) -> Dict[str, Any]:
        registry = get_default_registry()
        navigation = registry.get("intelligent_navigation")
        perception = registry.get("distributed_perception_hub")

        nav_report = navigation.generate_navigation_report() if navigation and hasattr(navigation, "generate_navigation_report") else {}
        fusion_tracks = []
        if perception and hasattr(perception, "get_fusion_state"):
            fusion_tracks = perception.get_fusion_state().get("active_tracks", [])

        risk = nav_report.get("overall_status", "safe")
        risk_weight = RISK_WEIGHT.get(risk, 0.2)
        traffic_factor = min(1.0, len(fusion_tracks) / 6)

        foil_angle_deg = round(1.5 + 5.5 * risk_weight + 1.5 * traffic_factor, 2)
        trim_tab_angle_deg = round(1.0 + 4.0 * risk_weight + 1.2 * traffic_factor, 2)
        roll_rate_cmd = round(0.4 + 2.2 * risk_weight + 0.6 * traffic_factor, 2)
        heave_damping_gain = round(0.8 + 1.7 * risk_weight + 0.4 * traffic_factor, 2)
        comfort_target_msdv = round(max(0.15, 0.55 - 0.2 * risk_weight), 2)

        return {
            "control_mode": "stabilize_and_comfort",
            "foil_angle_deg": foil_angle_deg,
            "trim_tab_angle_deg": trim_tab_angle_deg,
            "roll_rate_cmd": roll_rate_cmd,
            "heave_damping_gain": heave_damping_gain,
            "comfort_target_msdv": comfort_target_msdv,
            "stability_margin": round(max(0.1, 1.0 - risk_weight * 0.45), 2),
            "traffic_factor": round(traffic_factor, 2),
            "risk_basis": risk,
        }

    def get_status(self) -> Dict[str, Any]:
        control_state = self.compute_control_state()
        return {
            "name": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "health_message": self._health.message,
            **control_state,
        }


__all__ = ["RCSControlChannel"]