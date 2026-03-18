# -*- coding: utf-8 -*-
"""
Maritime Scene Model - 海事情景语义层

为导航、感知和数字孪生提供统一的场景上下文。
"""

from __future__ import annotations

from typing import Any, Dict, List


class MaritimeSceneModel:
    """根据本船状态和周边目标生成海事情景语义。"""

    def evaluate(self, own_ship: Dict[str, Any], targets: List[Any]) -> Dict[str, Any]:
        scene_type = "open_sea"
        constraints = ["Maintain standard COLREGs watch and CPA/TCPA margins."]
        overlay_hints = ["baseline_tracks"]
        priority_rules = ["Rule 5", "Rule 7", "Rule 8"]

        own_latitude = float(own_ship.get("latitude", 0.0) or 0.0)
        own_speed = float(own_ship.get("speed", 0.0) or 0.0)
        target_types = [str(getattr(target, "vessel_type", "") or "") for target in targets]
        target_count = len(targets)

        if own_latitude >= 58 or any("ice" in vessel_type.lower() for vessel_type in target_types):
            scene_type = "ice_navigation"
            constraints = [
                "Preserve enlarged passing distance around ice targets.",
                "Reduce speed before close-quarters manoeuvre in ice-infested waters.",
            ]
            overlay_hints = ["iceberg_hazard", "escort_lane", "safe_corridor"]
            priority_rules = ["Rule 5", "Rule 6", "Rule 7", "Rule 19"]
        elif any(vessel_type in {"Tug", "Dredger", "Offshore Support Vessel"} for vessel_type in target_types):
            scene_type = "offshore_operation"
            constraints = [
                "Assume restricted manoeuvrability for nearby service vessels.",
                "Avoid cutting across work areas and towed equipment sectors.",
            ]
            overlay_hints = ["work_zone", "support_vessel", "restricted_sector"]
            priority_rules = ["Rule 18", "Rule 8"]
        elif target_count >= 5 and own_speed < 8:
            scene_type = "port_approach"
            constraints = [
                "Expect dense mixed traffic during port entry or departure.",
                "Prefer speed moderation and explicit route confirmation with pilotage constraints.",
            ]
            overlay_hints = ["port_lane", "pilot_transfer", "berth_queue"]
            priority_rules = ["Rule 6", "Rule 8", "Rule 9"]
        elif target_count >= 4:
            scene_type = "narrow_channel"
            constraints = [
                "Prioritise lane discipline and starboard-side channel keeping.",
                "Avoid unnecessary crossing in constrained waterway geometry.",
            ]
            overlay_hints = ["channel_axis", "bank_clearance", "meeting_zone"]
            priority_rules = ["Rule 9", "Rule 14", "Rule 15"]

        return {
            "scene_type": scene_type,
            "target_density": target_count,
            "constraints": constraints,
            "priority_rules": priority_rules,
            "overlay_hints": overlay_hints,
        }


__all__ = ["MaritimeSceneModel"]