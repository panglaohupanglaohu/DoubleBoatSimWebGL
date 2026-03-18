# -*- coding: utf-8 -*-
"""
Structural Health Monitor Channel - 结构健康监测第一版
"""

from __future__ import annotations

from typing import Any, Dict, List

from .marine_base import MarineChannel, ChannelPriority, ChannelStatus, get_default_registry


class StructuralHealthMonitorChannel(MarineChannel):
    name = "structural_health_monitor"
    description = "结构健康监测 (应变 / 疲劳 / 寿命余度第一版)"
    version = "0.1.0"
    priority = ChannelPriority.P1
    dependencies: List[str] = ["rcs_control", "intelligent_engine", "distributed_perception_hub"]

    def initialize(self) -> bool:
        self._initialized = True
        self._set_health(ChannelStatus.OK, "SHM ready")
        return True

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True

    def compute_health_state(self) -> Dict[str, Any]:
        registry = get_default_registry()
        rcs = registry.get("rcs_control")
        engine = registry.get("intelligent_engine")
        perception = registry.get("distributed_perception_hub")

        rcs_state = rcs.get_status() if rcs else {}
        engine_state = engine.get_status() if engine else {}
        fusion_count = 0
        if perception and hasattr(perception, "get_fusion_state"):
            fusion_count = len(perception.get_fusion_state().get("active_tracks", []))

        roll_cmd = float(rcs_state.get("roll_rate_cmd", 0.5) or 0.5)
        engine_health = float(engine_state.get("engine_health_score", 90) or 90)
        load_factor = max(0.1, (100 - engine_health) / 100)
        traffic_factor = min(1.0, fusion_count / 8)

        fatigue_damage_index = round(min(0.95, 0.12 + 0.22 * load_factor + 0.18 * traffic_factor), 3)
        life_remaining_pct = round(max(35.0, 100 - fatigue_damage_index * 55), 2)

        strain_hotspots = [
            {"zone": "bridge_joint", "microstrain": round(110 + roll_cmd * 18 + traffic_factor * 22, 1)},
            {"zone": "port_bow", "microstrain": round(95 + roll_cmd * 14, 1)},
            {"zone": "starboard_bow", "microstrain": round(97 + roll_cmd * 15, 1)},
        ]

        return {
            "longitudinal_bending_moment_kNm": round(1850 + roll_cmd * 160 + traffic_factor * 120, 2),
            "torsion_kNm": round(640 + roll_cmd * 90 + traffic_factor * 70, 2),
            "fatigue_damage_index": fatigue_damage_index,
            "life_remaining_pct": life_remaining_pct,
            "fbg_status": "online",
            "strain_hotspots": strain_hotspots,
        }

    def get_status(self) -> Dict[str, Any]:
        health_state = self.compute_health_state()
        return {
            "name": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "health_message": self._health.message,
            **health_state,
        }


__all__ = ["StructuralHealthMonitorChannel"]