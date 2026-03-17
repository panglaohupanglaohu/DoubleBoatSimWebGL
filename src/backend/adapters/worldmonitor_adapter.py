# -*- coding: utf-8 -*-
"""
WorldMonitor Adapter - 方案层适配器

当前阶段只提供接口骨架与占位响应，4 小时后再进行真实接入。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional


class WorldMonitorAdapter:
    """WorldMonitor 数据适配器（方案层占位版）"""

    def __init__(self, base_url: str = "https://api.worldmonitor.app/api/v1"):
        self.base_url = base_url
        self.mode = "placeholder"
        self.created_at = datetime.now().isoformat()

    async def get_ais_targets(self, lat_range: Optional[tuple] = None, lng_range: Optional[tuple] = None) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "source": "worldmonitor",
            "kind": "ais",
            "base_url": self.base_url,
            "connected": False,
            "message": "WorldMonitor 尚未完成真实 API 接入，当前返回方案层占位结构。",
            "requested": {
                "lat_range": lat_range,
                "lng_range": lng_range,
            },
            "targets": [],
            "timestamp": datetime.now().isoformat(),
        }

    async def get_marine_weather(self, lat: float, lng: float) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "source": "worldmonitor",
            "kind": "marine_weather",
            "connected": False,
            "message": "WorldMonitor 海洋气象尚未真实接入。",
            "position": {
                "lat": lat,
                "lng": lng,
            },
            "weather": None,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_ports(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "source": "worldmonitor",
            "kind": "ports",
            "connected": False,
            "ports": [],
            "timestamp": datetime.now().isoformat(),
        }

    async def get_shipping_routes(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "source": "worldmonitor",
            "kind": "shipping_routes",
            "connected": False,
            "routes": [],
            "timestamp": datetime.now().isoformat(),
        }
