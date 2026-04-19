# -*- coding: utf-8 -*-
"""
Man Overboard (MOB) Channel — 落水告警与搜救管理

检测人员落水事件，记录位置，管理搜救模式。
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)

VALID_SEARCH_PATTERNS = (
    "none",
    "williamson_turn",
    "anderson_turn",
    "scharnow_turn",
    "expanding_square",
    "sector_search",
    "parallel_sweep",
    "creeping_line",
)

# Water temperature → survival time mapping (hours, approximate)
# Ref: IMO MSC/Circ.1046, SOLAS Ch III — conservative (no immersion suit)
_SURVIVAL_TABLE = [
    (2, 0.75),
    (5, 1.0),     # corrected: IMO 建议 ≤ 1.0h
    (10, 3.0),
    (15, 6.0),
    (20, 12.0),
    (25, 24.0),
]


def _estimate_survival_hours(water_temp_c: float) -> float:
    """Estimate survival time in hours based on water temperature."""
    if water_temp_c <= _SURVIVAL_TABLE[0][0]:
        return _SURVIVAL_TABLE[0][1]
    for i in range(1, len(_SURVIVAL_TABLE)):
        t_low, h_low = _SURVIVAL_TABLE[i - 1]
        t_high, h_high = _SURVIVAL_TABLE[i]
        if water_temp_c <= t_high:
            ratio = (water_temp_c - t_low) / (t_high - t_low)
            return h_low + ratio * (h_high - h_low)
    return _SURVIVAL_TABLE[-1][1]


class ManOverboardChannel(MarineChannel):
    """MOB 落水告警 Channel — 人员落水检测与搜救响应管理。"""

    name = "man_overboard"
    description = "人员落水(MOB)检测与搜救管理"
    version = "1.0.0"
    priority = ChannelPriority.P0

    def __init__(self, config=None, bus=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._mob_active: bool = False
        self._mob_position: Optional[Dict[str, Any]] = None
        self._mob_markers: List[Dict[str, Any]] = []
        self._search_pattern: str = "none"
        self._mob_activated_at: Optional[float] = None
        self._water_temp_c: float = 15.0
        self._bus = bus

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Man overboard channel ready")
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

    def activate_mob(self, lat: float, lon: float) -> dict:
        """Activate MOB alert with position."""
        now = time.time()
        self._mob_active = True
        self._mob_activated_at = now
        self._mob_position = {
            "lat": lat,
            "lon": lon,
            "timestamp": datetime.fromtimestamp(now).isoformat(),
        }
        self._search_pattern = "williamson_turn"
        self._set_health(ChannelStatus.WARN, "MOB ACTIVE")
        logger.warning(f"🚨 MOB activated at ({lat}, {lon})")
        result = {
            "status": "mob_activated",
            "position": self._mob_position,
            "search_pattern": self._search_pattern,
        }
        if self._bus is not None:
            try:
                from .marine_message_bus import MarineMessage, MessageType, MessagePriority
                msg = MarineMessage(
                    message_type=MessageType.URGENCY_PAN_PAN,
                    priority=MessagePriority.URGENCY,
                    sender_channel=self.name,
                    subject="mob.activated",
                    content={"lat": lat, "lon": lon,
                             "timestamp": self._mob_position["timestamp"]},
                )
                self._bus.publish_sync(msg)
            except Exception as e:
                logger.warning(f"MOB processing error: {e}")
        return result

    def deactivate_mob(self) -> dict:
        """Cancel MOB alert."""
        self._mob_active = False
        self._mob_position = None
        self._mob_activated_at = None
        self._search_pattern = "none"
        self._mob_markers.clear()
        self._set_health(ChannelStatus.OK, "MOB cancelled")
        logger.info("✅ MOB deactivated")
        return {"status": "mob_deactivated"}

    def add_mob_marker(self, lat: float, lon: float) -> dict:
        """Add a MOB marker point for search area tracking."""
        marker = {
            "position": {"lat": lat, "lon": lon},
            "time": datetime.now().isoformat(),
        }
        self._mob_markers.append(marker)
        return {"status": "marker_added", "marker": marker, "total_markers": len(self._mob_markers)}

    def set_search_pattern(self, pattern: str) -> dict:
        """Set search/rescue pattern."""
        if pattern not in VALID_SEARCH_PATTERNS:
            return {"status": "error", "reason": f"Invalid pattern: {pattern}. Valid: {VALID_SEARCH_PATTERNS}"}
        self._search_pattern = pattern
        return {"status": "pattern_set", "search_pattern": pattern}

    def _elapsed_minutes(self) -> float:
        """Minutes since MOB activation."""
        if self._mob_activated_at is None:
            return 0.0
        return round((time.time() - self._mob_activated_at) / 60.0, 1)

    def estimate_drift(self, wind_speed_kn=10.0, wind_dir_deg=0.0,
                       current_speed_kn=0.5, current_dir_deg=0.0,
                       elapsed_min=0.0, initial_position_error_nm=0.3):
        """IAMSAR Vol III 漂移估算 + Total Probable Error 搜索半径。"""
        import math
        if elapsed_min <= 0:
            elapsed_min = self._elapsed_minutes()
        if elapsed_min <= 0:
            return {"drift_nm": 0.0, "search_radius_nm": 0.5,
                    "datum_error": 0.0, "total_error": 0.0}
        hours = elapsed_min / 60.0
        # Wind leeway: IAMSAR 3-4% for PIW with PFD
        leeway = wind_speed_kn * 0.035
        lw_dir = (wind_dir_deg + 180.0) % 360.0
        lw_x = leeway * math.sin(math.radians(lw_dir))
        lw_y = leeway * math.cos(math.radians(lw_dir))
        cu_x = current_speed_kn * math.sin(math.radians(current_dir_deg))
        cu_y = current_speed_kn * math.cos(math.radians(current_dir_deg))
        dx = (lw_x + cu_x) * hours
        dy = (lw_y + cu_y) * hours
        drift_nm = math.sqrt(dx**2 + dy**2)
        # IAMSAR Total Probable Error (TPE)
        # E = sqrt(X^2 + Y^2 + De^2)
        # X = initial position error, Y = drift position error, De = datum error
        datum_error = drift_nm * 0.15  # 15% drift uncertainty
        drift_position_error = hours * 0.1
        total_error = math.sqrt(
            initial_position_error_nm ** 2
            + drift_position_error ** 2
            + datum_error ** 2
        )
        # Search radius = drift + safety factor * TPE (IAMSAR fs=1.1~1.6)
        search_r = drift_nm + 1.3 * total_error + 0.5
        return {
            "drift_nm": round(drift_nm, 3),
            "search_radius_nm": round(search_r, 2),
            "elapsed_min": round(elapsed_min, 1),
            "datum_error": round(datum_error, 3),
            "total_error": round(total_error, 3),
        }

    def get_mob_status(self) -> dict:
        """Return comprehensive MOB status."""
        elapsed = self._elapsed_minutes()
        survival_hours = _estimate_survival_hours(self._water_temp_c)
        return {
            "mob_active": self._mob_active,
            "mob_position": self._mob_position,
            "elapsed_minutes": elapsed,
            "search_pattern": self._search_pattern,
            "markers_count": len(self._mob_markers),
            "survival_estimate": {
                "water_temp_c": self._water_temp_c,
                "estimated_hours": round(survival_hours, 1),
            },
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "mob_active": self._mob_active,
            "mob_position": self._mob_position,
            "elapsed_minutes": self._elapsed_minutes(),
            "search_pattern": self._search_pattern,
        }

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "mob_alert":
            lat = event.get("lat")
            lon = event.get("lon")
            if any(v is None for v in [lat, lon]):
                return {"status": "error", "reason": "lat and lon are required"}
            return self.activate_mob(lat, lon)

        if event_type == "mob_cancel":
            return self.deactivate_mob()

        return {"status": "ignored", "reason": f"Unknown event type: {event_type}"}
