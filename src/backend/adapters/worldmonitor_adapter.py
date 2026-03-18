# -*- coding: utf-8 -*-
"""
WorldMonitor Adapter - 方案层适配器

当前阶段只提供接口骨架与占位响应，4 小时后再进行真实接入。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional


class WorldMonitorAdapter:
    """WorldMonitor 数据适配器（方案层占位版）"""

    def __init__(self, base_url: str = "https://api.worldmonitor.app/api/v1"):
        self.base_url = base_url
        self.mode = "placeholder"
        self.created_at = datetime.now().isoformat()

    def _build_mock_targets(self, lat_range: Optional[tuple], lng_range: Optional[tuple]) -> List[Dict[str, Any]]:
        min_lat, max_lat = lat_range or (31.18, 31.32)
        min_lng, max_lng = lng_range or (121.40, 121.56)
        return [
            {
                "mmsi": "413000101",
                "latitude": round((min_lat + max_lat) / 2 + 0.018, 5),
                "longitude": round((min_lng + max_lng) / 2 + 0.011, 5),
                "course": 226.0,
                "speed": 12.4,
                "heading": 224.0,
                "vessel_type": "Container Ship",
                "risk_level": "medium",
                "risk_factors": ["crossing_traffic", "reduced_margin"],
            },
            {
                "mmsi": "413000202",
                "latitude": round((min_lat + max_lat) / 2 - 0.022, 5),
                "longitude": round((min_lng + max_lng) / 2 + 0.019, 5),
                "course": 176.0,
                "speed": 9.3,
                "heading": 177.0,
                "vessel_type": "Bulk Carrier",
                "risk_level": "low",
                "risk_factors": ["parallel_course"],
            },
            {
                "mmsi": "413000303",
                "latitude": round((min_lat + max_lat) / 2 + 0.006, 5),
                "longitude": round((min_lng + max_lng) / 2 - 0.027, 5),
                "course": 44.0,
                "speed": 15.1,
                "heading": 42.0,
                "vessel_type": "Tanker",
                "risk_level": "medium",
                "risk_factors": ["closing_speed", "dense_lane"],
            },
        ]

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
            "targets": self._build_mock_targets(lat_range, lng_range),
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
            "weather": {
                "wind": {"speed": 18.5, "direction": 132.0, "gust": 25.4},
                "wave": {"height": 2.4, "period": 8.2, "direction": 141.0},
                "current": {"speed": 1.6, "direction": 88.0},
                "visibility_nm": 7.5,
                "advisory": "Cross-sea state acceptable for supervised autonomy; monitor fuel drift.",
            },
            "timestamp": datetime.now().isoformat(),
        }

    async def get_ports(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "source": "worldmonitor",
            "kind": "ports",
            "connected": False,
            "ports": [
                {"name": "Shanghai", "country": "CN", "status": "open", "eta_congestion_hours": 6},
                {"name": "Ningbo-Zhoushan", "country": "CN", "status": "open", "eta_congestion_hours": 4},
                {"name": "Singapore", "country": "SG", "status": "open", "eta_congestion_hours": 8},
            ],
            "timestamp": datetime.now().isoformat(),
        }

    async def get_shipping_routes(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "source": "worldmonitor",
            "kind": "shipping_routes",
            "connected": False,
            "routes": [
                {
                    "route_id": "east-china-sea-mainline",
                    "origin": "Shanghai",
                    "destination": "Singapore",
                    "distance_nm": 2290,
                    "recommended_speed_kn": 11.8,
                    "weather_penalty_pct": 3.4,
                }
            ],
            "timestamp": datetime.now().isoformat(),
        }
