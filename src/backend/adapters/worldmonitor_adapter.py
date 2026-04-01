# -*- coding: utf-8 -*-
"""
WorldMonitor Adapter - 网关层适配器

优先委托给 WorldMonitorRealAdapter (真实 API)，失败时回退到内置 mock 数据。
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# 尝试导入真实适配器
try:
    from adapters.worldmonitor_adapter_real import WorldMonitorRealAdapter
except ImportError:
    WorldMonitorRealAdapter = None  # type: ignore[misc,assignment]


class WorldMonitorAdapter:
    """WorldMonitor 数据适配器（网关版：真实 API + mock fallback）"""

    def __init__(
        self,
        base_url: str = "https://api.worldmonitor.app/api/v1",
        config: Optional[Dict[str, Any]] = None,
    ):
        self.base_url = base_url
        self.created_at = datetime.now().isoformat()

        # 尝试初始化真实适配器
        self._real: Optional[Any] = None
        if WorldMonitorRealAdapter is not None:
            try:
                real_config = dict(config or {})
                real_config.setdefault("base_url", base_url)
                self._real = WorldMonitorRealAdapter(real_config)
                logger.info("WorldMonitor gateway: real adapter loaded")
            except Exception as e:
                logger.warning(f"WorldMonitor gateway: real adapter init failed ({e}), using mock")
                self._real = None

        self.mode = "real" if self._real is not None else "mock"

    # ------------------------------------------------------------------
    # 状态查询
    # ------------------------------------------------------------------

    @property
    def is_real(self) -> bool:
        """真实适配器是否可用且已连接。"""
        if self._real is None:
            return False
        return getattr(self._real, "_initialized", False) and self._real.api_key != "placeholder"

    # ------------------------------------------------------------------
    # Mock 数据构建 (保留原始占位逻辑)
    # ------------------------------------------------------------------

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

    def _mock_ais_response(self, lat_range, lng_range) -> Dict[str, Any]:
        return {
            "mode": "mock",
            "source": "worldmonitor",
            "kind": "ais",
            "base_url": self.base_url,
            "connected": False,
            "message": "WorldMonitor 尚未完成真实 API 接入，当前返回方案层占位结构。",
            "requested": {"lat_range": lat_range, "lng_range": lng_range},
            "targets": self._build_mock_targets(lat_range, lng_range),
            "timestamp": datetime.now().isoformat(),
        }

    def _mock_weather_response(self, lat: float, lng: float) -> Dict[str, Any]:
        return {
            "mode": "mock",
            "source": "worldmonitor",
            "kind": "marine_weather",
            "connected": False,
            "message": "WorldMonitor 海洋气象尚未真实接入。",
            "position": {"lat": lat, "lng": lng},
            "weather": {
                "wind": {"speed": 18.5, "direction": 132.0, "gust": 25.4},
                "wave": {"height": 2.4, "period": 8.2, "direction": 141.0},
                "current": {"speed": 1.6, "direction": 88.0},
                "visibility_nm": 7.5,
                "advisory": "Cross-sea state acceptable for supervised autonomy; monitor fuel drift.",
            },
            "timestamp": datetime.now().isoformat(),
        }

    # ------------------------------------------------------------------
    # 公开 async 方法 — 先尝试 real，失败 fallback mock
    # ------------------------------------------------------------------

    async def get_ais_targets(
        self, lat_range: Optional[tuple] = None, lng_range: Optional[tuple] = None
    ) -> Dict[str, Any]:
        if self._real is not None:
            try:
                bbox = None
                if lat_range and lng_range:
                    bbox = {
                        "min_lat": lat_range[0], "max_lat": lat_range[1],
                        "min_lng": lng_range[0], "max_lng": lng_range[1],
                    }
                targets = await self._real.get_ais_targets(bbox=bbox)
                return {
                    "mode": "real",
                    "source": "worldmonitor",
                    "kind": "ais",
                    "base_url": self.base_url,
                    "connected": True,
                    "message": "Data from WorldMonitor real adapter.",
                    "requested": {"lat_range": lat_range, "lng_range": lng_range},
                    "targets": [t.to_dict() if hasattr(t, "to_dict") else t for t in targets],
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                logger.warning(f"WorldMonitor AIS real call failed, using mock: {e}")

        return self._mock_ais_response(lat_range, lng_range)

    async def get_marine_weather(self, lat: float, lng: float) -> Dict[str, Any]:
        if self._real is not None:
            try:
                weather = await self._real.get_marine_weather(lat, lng)
                if weather is not None:
                    wd = weather.to_dict() if hasattr(weather, "to_dict") else weather
                    return {
                        "mode": "real",
                        "source": "worldmonitor",
                        "kind": "marine_weather",
                        "connected": True,
                        "message": "Data from WorldMonitor real adapter.",
                        "position": wd.get("position", {"lat": lat, "lng": lng}),
                        "weather": {
                            "wind": wd.get("wind", {}),
                            "wave": wd.get("wave", {}),
                            "current": wd.get("current", {}),
                            "visibility_nm": wd.get("visibility", 0),
                        },
                        "timestamp": datetime.now().isoformat(),
                    }
            except Exception as e:
                logger.warning(f"WorldMonitor Weather real call failed, using mock: {e}")

        return self._mock_weather_response(lat, lng)

    async def get_ports(self) -> Dict[str, Any]:
        if self._real is not None:
            try:
                ports = await self._real.get_ports()
                return {
                    "mode": "real",
                    "source": "worldmonitor",
                    "kind": "ports",
                    "connected": True,
                    "ports": ports,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                logger.warning(f"WorldMonitor Ports real call failed, using mock: {e}")

        return {
            "mode": "mock",
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
        if self._real is not None:
            try:
                routes = await self._real.get_shipping_routes()
                return {
                    "mode": "real",
                    "source": "worldmonitor",
                    "kind": "shipping_routes",
                    "connected": True,
                    "routes": routes,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                logger.warning(f"WorldMonitor Routes real call failed, using mock: {e}")

        return {
            "mode": "mock",
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
