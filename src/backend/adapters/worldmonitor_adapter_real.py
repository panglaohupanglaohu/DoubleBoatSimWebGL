# -*- coding: utf-8 -*-
"""
WorldMonitor 真实数据源适配器

当前阶段：占位实现，等待真实 API 配置
目标：接入 WorldMonitor 的真实 AIS / Weather / Ports / Routes 数据源
"""

import asyncio
import aiohttp
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging
import random

logger = logging.getLogger(__name__)


@dataclass
class WM_AIS_Target:
    """WorldMonitor AIS 目标数据结构"""
    mmsi: str
    latitude: float
    longitude: float
    course: float
    speed: float
    heading: float
    vessel_type: str
    timestamp: str
    # AI Native 扩展字段
    risk_level: str = "low"  # low/medium/high
    risk_factors: List[str] = None
    predicted_trajectory: List[Dict] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class WM_Marine_Weather:
    """WorldMonitor 海洋气象数据结构"""
    position: Dict[str, float]  # {"lat": float, "lng": float}
    wind: Dict[str, float]      # {"speed": knots, "direction": deg, "gust": knots}
    wave: Dict[str, float]      # {"height": meters, "period": sec, "direction": deg}
    current: Dict[str, float]   # {"speed": knots, "direction": deg}
    visibility: float           # nautical miles
    timestamp: str

    def to_dict(self):
        return asdict(self)


class WorldMonitorRealAdapter:
    """WorldMonitor 真实 API 适配器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.api_key = self.config.get("api_key") or "placeholder"
        self.base_url = self.config.get("base_url") or "https://api.worldmonitor.app/api/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        self._initialized = False
        
        # 真实数据缓存
        self._ais_cache = {}
        self._weather_cache = {}
        self._ports_cache = {}
        self._routes_cache = {}
        self._cache_ttl = self.config.get("cache_ttl", 30)  # 30秒缓存
    
    async def initialize(self):
        """初始化 HTTP 会话"""
        if not self.api_key or self.api_key == "placeholder":
            logger.warning("⚠️ WorldMonitor API key is not configured - using mock mode")
            self._initialized = True
            return False
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.session = aiohttp.ClientSession(
            base_url=self.base_url,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=10)
        )
        self._initialized = True
        logger.info("🌍 WorldMonitor adapter initialized")
        return True
    
    async def close(self):
        """关闭 HTTP 会话"""
        if self.session:
            await self.session.close()
    
    def _is_cache_valid(self, cache_entry):
        """检查缓存是否有效"""
        if not cache_entry:
            return False
        return (datetime.now() - cache_entry["timestamp"]).total_seconds() < self._cache_ttl
    
    async def get_ais_targets(self, bbox: Optional[Dict] = None) -> List[WM_AIS_Target]:
        """
        获取 WorldMonitor AIS 目标数据
        
        Args:
            bbox: 可选地理边界框 {"min_lat": float, "max_lat": float, "min_lng": float, "max_lng": float}
        
        Returns:
            AIS 目标列表
        """
        if not self._initialized:
            await self.initialize()
        
        cache_key = f"ais_{bbox}"
        cached = self._ais_cache.get(cache_key)
        if cached and self._is_cache_valid(cached):
            logger.debug(f"📦 WorldMonitor AIS: using cache for {cache_key}")
            return cached["data"]
        
        # 如果没有配置真实 API key，返回模拟数据
        if self.api_key == "placeholder":
            logger.warning("🔍 WorldMonitor: using mock AIS data (no API key)")
            return self._mock_ais_targets(bbox)
        
        try:
            params = {}
            if bbox:
                params.update({
                    "min_lat": bbox["min_lat"],
                    "max_lat": bbox["max_lat"], 
                    "min_lng": bbox["min_lng"],
                    "max_lng": bbox["max_lng"]
                })
            
            async with self.session.get("/ais", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    targets = [WM_AIS_Target(**item) for item in data.get("targets", [])]
                    
                    # 缓存结果
                    self._ais_cache[cache_key] = {
                        "data": targets,
                        "timestamp": datetime.now()
                    }
                    
                    logger.info(f"📡 Fetched {len(targets)} AIS targets from WorldMonitor")
                    return targets
                else:
                    logger.error(f"❌ WorldMonitor AIS API error: {response.status}")
                    # API 失败时也返回模拟数据，避免前端崩溃
                    return self._mock_ais_targets(bbox)
        
        except Exception as e:
            logger.error(f"💥 WorldMonitor AIS fetch failed: {e}")
            return self._mock_ais_targets(bbox)
    
    async def get_marine_weather(self, lat: float, lng: float) -> Optional[WM_Marine_Weather]:
        """获取 WorldMonitor 海洋气象数据"""
        if not self._initialized:
            await self.initialize()
        
        cache_key = f"weather_{lat}_{lng}"
        cached = self._weather_cache.get(cache_key)
        if cached and self._is_cache_valid(cached):
            logger.debug(f"📦 WorldMonitor Weather: using cache for {cache_key}")
            return cached["data"]
        
        if self.api_key == "placeholder":
            logger.warning("🔍 WorldMonitor: using mock weather data (no API key)")
            return self._mock_weather(lat, lng)
        
        try:
            params = {"lat": lat, "lng": lng}
            async with self.session.get("/marine-weather", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    weather = WM_Marine_Weather(**data.get("weather", {}))
                    
                    self._weather_cache[cache_key] = {
                        "data": weather,
                        "timestamp": datetime.now()
                    }
                    
                    logger.info(f"🌤️ Fetched marine weather for ({lat}, {lng}) from WorldMonitor")
                    return weather
                else:
                    logger.error(f"❌ WorldMonitor Weather API error: {response.status}")
                    return self._mock_weather(lat, lng)
        
        except Exception as e:
            logger.error(f"💥 WorldMonitor Weather fetch failed: {e}")
            return self._mock_weather(lat, lng)
    
    async def get_ports(self, region: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取港口数据"""
        if not self._initialized:
            await self.initialize()
        
        cache_key = f"ports_{region}"
        cached = self._ports_cache.get(cache_key)
        if cached and self._is_cache_valid(cached):
            return cached["data"]
        
        if self.api_key == "placeholder":
            logger.warning("🔍 WorldMonitor: using mock ports data (no API key)")
            return self._mock_ports(region)
        
        try:
            params = {"region": region} if region else {}
            async with self.session.get("/ports", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    ports = data.get("ports", [])
                    
                    self._ports_cache[cache_key] = {
                        "data": ports,
                        "timestamp": datetime.now()
                    }
                    
                    logger.info(f"⚓ Fetched {len(ports)} ports from WorldMonitor")
                    return ports
                else:
                    return self._mock_ports(region)
        
        except Exception as e:
            logger.error(f"💥 WorldMonitor Ports fetch failed: {e}")
            return self._mock_ports(region)
    
    async def get_shipping_routes(self, origin_port: Optional[str] = None, dest_port: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取航运路线数据"""
        if not self._initialized:
            await self.initialize()
        
        cache_key = f"routes_{origin_port}_{dest_port}"
        cached = self._routes_cache.get(cache_key)
        if cached and self._is_cache_valid(cached):
            return cached["data"]
        
        if self.api_key == "placeholder":
            logger.warning("🔍 WorldMonitor: using mock routes data (no API key)")
            return self._mock_routes(origin_port, dest_port)
        
        try:
            params = {}
            if origin_port: params["origin"] = origin_port
            if dest_port: params["destination"] = dest_port
            
            async with self.session.get("/shipping-routes", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    routes = data.get("routes", [])
                    
                    self._routes_cache[cache_key] = {
                        "data": routes,
                        "timestamp": datetime.now()
                    }
                    
                    logger.info(f"🚢 Fetched {len(routes)} shipping routes from WorldMonitor")
                    return routes
                else:
                    return self._mock_routes(origin_port, dest_port)
        
        except Exception as e:
            logger.error(f"💥 WorldMonitor Routes fetch failed: {e}")
            return self._mock_routes(origin_port, dest_port)
    
    # Mock 数据生成器（用于占位模式）
    def _mock_ais_targets(self, bbox: Optional[Dict] = None) -> List[WM_AIS_Target]:
        """模拟 AIS 目标数据"""
        import random
        from datetime import datetime, timedelta
        
        # 模拟 3-8 个目标
        count = random.randint(3, 8)
        targets = []
        
        base_lat = bbox["min_lat"] if bbox else 31.2304
        base_lng = bbox["min_lng"] if bbox else 121.4737
        
        for i in range(count):
            lat = base_lat + random.uniform(-0.1, 0.1)
            lng = base_lng + random.uniform(-0.1, 0.1)
            targets.append(WM_AIS_Target(
                mmsi=f"413{i:06d}",
                latitude=lat,
                longitude=lng,
                course=random.uniform(0, 360),
                speed=random.uniform(5, 25),
                heading=random.uniform(0, 360),
                vessel_type=random.choice(["Container Ship", "Bulk Carrier", "Tanker", "General Cargo"]),
                timestamp=(datetime.now() - timedelta(seconds=random.randint(0, 60))).isoformat(),
                risk_level=random.choice(["low", "medium"]),
                risk_factors=["good_visibility", "moderate_traffic"] if random.random() > 0.7 else ["poor_visibility", "heavy_traffic"],
                predicted_trajectory=[{"lat": lat + random.uniform(-0.01, 0.01), "lng": lng + random.uniform(-0.01, 0.01), "time": 300}]  # 5分钟后位置
            ))
        
        return targets
    
    def _mock_weather(self, lat: float, lng: float) -> WM_Marine_Weather:
        """模拟海洋气象数据"""
        import random
        from datetime import datetime
        
        return WM_Marine_Weather(
            position={"lat": lat, "lng": lng},
            wind={
                "speed": random.uniform(10, 25),      # 节
                "direction": random.uniform(0, 360),  # 度
                "gust": random.uniform(20, 35)        # 阵风
            },
            wave={
                "height": random.uniform(1.0, 3.5),   # 米
                "period": random.uniform(5, 12),      # 秒
                "direction": random.uniform(0, 360)   # 度
            },
            current={
                "speed": random.uniform(1, 3),        # 节
                "direction": random.uniform(0, 360)   # 度
            },
            visibility=random.uniform(5, 20),         # 海里
            timestamp=datetime.now().isoformat()
        )
    
    def _mock_ports(self, region: Optional[str] = None) -> List[Dict[str, Any]]:
        """模拟港口数据"""
        import random
        
        base_ports = [
            {"name": "Shanghai Port", "code": "CNSHA", "country": "CN", "coordinates": {"lat": 31.2304, "lng": 121.4737}, "status": "operational"},
            {"name": "Singapore Port", "code": "SGSIN", "country": "SG", "coordinates": {"lat": 1.2667, "lng": 103.8}, "status": "operational"},
            {"name": "Rotterdam Port", "code": "NLRTM", "country": "NL", "coordinates": {"lat": 51.88, "lng": 4.29}, "status": "operational"},
            {"name": "Los Angeles Port", "code": "USLAX", "country": "US", "coordinates": {"lat": 33.71, "lng": -118.27}, "status": "operational"},
            {"name": "Hamburg Port", "code": "DEHAM", "country": "DE", "coordinates": {"lat": 53.53, "lng": 9.98}, "status": "operational"},
        ]
        
        # 如果指定了区域，筛选对应港口
        if region:
            region_lower = region.lower()
            filtered = [p for p in base_ports if region_lower in p["name"].lower() or region_lower in p["country"].lower()]
            return random.sample(filtered, min(len(filtered), random.randint(2, 4)))
        
        return random.sample(base_ports, random.randint(3, 5))
    
    def _mock_routes(self, origin_port: Optional[str] = None, dest_port: Optional[str] = None) -> List[Dict[str, Any]]:
        """模拟航运路线数据"""
        import random
        
        base_routes = [
            {
                "id": "route_001",
                "name": "Shanghai to Singapore",
                "origin": {"name": "Shanghai Port", "code": "CNSHA"},
                "destination": {"name": "Singapore Port", "code": "SGSIN"},
                "distance": 2600,  # nautical miles
                "estimated_transit_time": 120,  # hours
                "traffic_density": "high",
                "weather_conditions": "moderate",
                "recommended_departure_window": "2026-03-16T08:00:00Z"
            },
            {
                "id": "route_002", 
                "name": "Singapore to Rotterdam",
                "origin": {"name": "Singapore Port", "code": "SGSIN"},
                "destination": {"name": "Rotterdam Port", "code": "NLRTM"},
                "distance": 6800,
                "estimated_transit_time": 312,
                "traffic_density": "moderate", 
                "weather_conditions": "variable",
                "recommended_departure_window": "2026-03-17T14:00:00Z"
            },
            {
                "id": "route_003",
                "name": "Rotterdam to Los Angeles",
                "origin": {"name": "Rotterdam Port", "code": "NLRTM"}, 
                "destination": {"name": "Los Angeles Port", "code": "USLAX"},
                "distance": 5200,
                "estimated_transit_time": 260,
                "traffic_density": "high",
                "weather_conditions": "moderate",
                "recommended_departure_window": "2026-03-18T06:00:00Z"
            }
        ]
        
        # 如果指定了起点终点，匹配路线
        if origin_port and dest_port:
            matched = []
            for route in base_routes:
                if (origin_port.upper() in route["origin"]["code"] or origin_port.lower() in route["origin"]["name"].lower()) and \
                   (dest_port.upper() in route["destination"]["code"] or dest_port.lower() in route["destination"]["name"].lower()):
                    matched.append(route)
            return matched
        
        return random.sample(base_routes, random.randint(2, 3))


# 便利函数
async def get_worldmonitor_adapter(config: Optional[Dict[str, Any]] = None) -> WorldMonitorRealAdapter:
    """获取 WorldMonitor 适配器实例"""
    adapter = WorldMonitorRealAdapter(config)
    await adapter.initialize()
    return adapter


__all__ = [
    "WorldMonitorRealAdapter",
    "WM_AIS_Target", 
    "WM_Marine_Weather",
    "get_worldmonitor_adapter"
]
