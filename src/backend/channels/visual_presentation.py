# -*- coding: utf-8 -*-
"""Visual Presentation Channel — camera views & scene presentation for digital twin."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

from .marine_base import MarineChannel, ChannelPriority, ChannelStatus

logger = logging.getLogger(__name__)


_DEFAULT_VIEWS: Dict[str, Dict[str, Any]] = {
    "bridge": {"label": "Bridge View", "camera": [8.5, 6.5, 14.5], "target": [0, 2.8, 2.2]},
    "top": {"label": "Top View", "camera": [0, 60, 0.1], "target": [0, 0, 0]},
    "bow": {"label": "Bow View", "camera": [0, 6, -25], "target": [0, 2, 0]},
    "stern": {"label": "Stern View", "camera": [0, 6, 25], "target": [0, 2, 0]},
    "port": {"label": "Port View", "camera": [-25, 8, 0], "target": [0, 2, 0]},
    "starboard": {"label": "Starboard View", "camera": [25, 8, 0], "target": [0, 2, 0]},
    "overview": {"label": "Overview", "camera": [40, 30, 40], "target": [0, 0, 0]},
    "free": {"label": "Free Camera", "camera": None, "target": None},
}


_COMMAND_MAP: Dict[str, str] = {
    # English
    "top view": "top",
    "bow view": "bow",
    "stern view": "stern",
    "port view": "port",
    "starboard view": "starboard",
    "overview": "overview",
    "bridge": "bridge",
    "free": "free",
    # Chinese
    "顶视图": "top",
    "俯视图": "top",
    "鸟瞰": "top",
    "船首视角": "bow",
    "船尾视角": "stern",
    "左舷视角": "port",
    "右舷视角": "starboard",
    "全景": "overview",
    "总览": "overview",
    "自由视角": "free",
    "bridge视角": "bridge",
    "舰桥视角": "bridge",
}


class VisualPresentationChannel(MarineChannel):
    """Visual presentation & camera control agent for digital twin."""

    name = "visual_presentation"
    description = "Visual presentation & camera control agent for digital twin"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_view: str = "bridge"
        self._view_history: List[Dict[str, Any]] = []
        self._available_views: Dict[str, Dict[str, Any]] = {
            k: dict(v) for k, v in _DEFAULT_VIEWS.items()
        }
        self._auto_view_rules: List[Dict[str, Any]] = []

    # ---- MarineChannel interface ----

    def initialize(self) -> bool:
        self._initialized = True
        self._set_health(ChannelStatus.OK, "Visual presentation ready")
        return True

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "health": self._health.status.value,
            "health_message": self._health.message,
            "current_view": self._current_view,
            "available_views": list(self._available_views.keys()),
            "history_count": len(self._view_history),
            "auto_rules_count": len(self._auto_view_rules),
        }

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True

    # ---- View management ----

    def set_view(self, view_name: str, source: str = "manual") -> Dict[str, Any]:
        """Switch camera to *view_name*. Returns the view details dict."""
        if view_name not in self._available_views:
            return {"ok": False, "error": f"Unknown view: {view_name}"}

        prev = self._current_view
        self._current_view = view_name
        view_info = self._available_views[view_name]

        record = {
            "from": prev,
            "to": view_name,
            "source": source,
            "timestamp": datetime.now().isoformat(),
        }
        self._view_history.append(record)
        if len(self._view_history) > 50:
            self._view_history = self._view_history[-50:]

        logger.debug("View changed: %s -> %s (source=%s)", prev, view_name, source)
        return {"ok": True, "view": view_name, **view_info}

    def get_available_views(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._available_views)

    def get_view_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return list(self._view_history[-limit:])

    def suggest_view(self, context: Dict[str, Any]) -> str:
        """Suggest a view based on context (risk_level, scene_type, etc.)."""
        risk = context.get("risk_level", "normal")
        scene = context.get("scene_type", "")

        if risk in ("critical", "emergency"):
            return "bridge"
        if risk == "high":
            return "overview"
        if scene == "docking":
            return "top"
        if scene == "open_sea":
            return "bow"
        if scene == "engine_room":
            return "stern"

        # Check auto-rules
        for rule in self._auto_view_rules:
            match_key = rule.get("match_key")
            match_val = rule.get("match_value")
            if match_key and context.get(match_key) == match_val:
                return rule.get("view", "bridge")

        return self._current_view

    def process_command(self, command_text: str) -> Dict[str, Any]:
        """Parse natural language command and map to a view change."""
        text = command_text.strip().lower()
        for keyword, view_name in _COMMAND_MAP.items():
            if keyword in text:
                result = self.set_view(view_name, source="bridge_command")
                return {
                    "matched_keyword": keyword,
                    "view": view_name,
                    "result": result,
                }
        return {"matched_keyword": None, "view": None, "error": "No view command recognized"}
