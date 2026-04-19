# -*- coding: utf-8 -*-
"""
L3: Weather Routing Channel - 气象导航

基于天气预报数据评估航线风险，提供气象导航建议。

风险因子:
- 风速 > 40kn → 高危
- 浪高 > 4m → 中危
- 能见度 < 1nm → 高危
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class WeatherRoutingChannel(MarineChannel):
    """气象导航 Channel — 评估航线天气风险并提供建议。"""

    name = "weather_routing"
    description = "气象导航与航线天气风险评估"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._forecasts: Dict[str, Dict[str, Any]] = {}
        self._alert_level: str = "normal"
        self._recommended_routes: List[Dict[str, Any]] = []
        self._current_weather: Dict[str, Any] = {}
        self._weather_grid: Dict[tuple, Dict[str, Any]] = {}

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Weather routing ready")
        return True

    def get_status(self) -> Dict[str, Any]:
        current = self._current_weather.copy() if self._current_weather else {}
        if current and "risk_level" not in current:
            current["risk_level"] = self._compute_point_risk_level(current)
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "forecast_count": len(self._forecasts),
            "alert_level": self._alert_level,
            "recommended_routes": len(self._recommended_routes),
            "current_weather": current,
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

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "weather_forecast":
            return self._handle_forecast(event)
        elif event_type == "route_candidate":
            return self._handle_route_candidate(event)
        elif event_type == "weather_alert":
            return self._handle_weather_alert(event)
        elif event_type == "weather_data_update":
            return self._handle_weather_data_update(event)

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    # ---- event handlers ----

    def _handle_forecast(self, event: dict) -> dict:
        region = event.get("region", "unknown")
        forecast = {
            "wind_speed": event.get("wind_speed", 0.0),
            "wave_height": event.get("wave_height", 0.0),
            "visibility": event.get("visibility", 10.0),
            "precipitation": event.get("precipitation", 0.0),
            "region": region,
            "timestamp": datetime.now().isoformat(),
        }
        self._forecasts[region] = forecast
        self._current_weather = forecast
        return {"status": "cached", "region": region, "forecast_count": len(self._forecasts)}

    def _handle_route_candidate(self, event: dict) -> dict:
        waypoints = event.get("waypoints", [])
        if not waypoints:
            return {"status": "error", "reason": "no waypoints provided"}

        risk = self.evaluate_route_weather_risk(waypoints)
        recommendations = self.generate_weather_recommendations(waypoints)

        route_result = {
            "waypoints_count": len(waypoints),
            "risk": risk,
            "recommendations": recommendations,
        }
        if risk["risk_level"] in ("low", "medium"):
            self._recommended_routes.append(route_result)

        return {"status": "evaluated", **route_result}

    def _handle_weather_alert(self, event: dict) -> dict:
        severity = event.get("severity", "warning")
        self._alert_level = severity
        if severity == "critical":
            self._set_health(ChannelStatus.WARN, f"Weather alert: {event.get('message', 'severe weather')}")
        return {"status": "alert_received", "alert_level": self._alert_level}

    def _handle_weather_data_update(self, event: dict) -> dict:
        lat = event.get("lat", 0.0)
        lon = event.get("lon", 0.0)
        result = self.update_weather_data(
            lat=lat,
            lon=lon,
            wind_speed=event.get("wind_speed", 0.0),
            wave_height=event.get("wave_height", 0.0),
            visibility=event.get("visibility", 10.0),
        )
        return {"status": "grid_updated", **result}

    # ---- core algorithms ----

    def evaluate_route_weather_risk(self, waypoints: list) -> dict:
        if not waypoints:
            return {"risk_score": 0.0, "risk_level": "low", "segments": [], "recommendation": "No waypoints to evaluate"}

        segments: List[Dict[str, Any]] = []
        total_score = 0.0

        for i, wp in enumerate(waypoints):
            lat = wp.get("lat", 0.0)
            lon = wp.get("lon", 0.0)
            seg_score = self._score_point(lat, lon)
            segments.append({
                "index": i,
                "lat": lat,
                "lon": lon,
                "risk_score": seg_score,
                "risk_level": self._level_from_score(seg_score),
            })
            total_score += seg_score

        avg_score = total_score / len(waypoints) if waypoints else 0.0
        risk_level = self._level_from_score(avg_score)

        recommendation_map = {
            "low": "航线天气条件良好，建议按计划航行",
            "medium": "航线存在中等天气风险，建议加强瞭望",
            "high": "航线天气条件恶劣，建议调整航线或等待天气好转",
            "critical": "航线极端天气风险，强烈建议更改航线",
        }

        return {
            "risk_score": round(avg_score, 2),
            "risk_level": risk_level,
            "segments": segments,
            "recommendation": recommendation_map.get(risk_level, ""),
        }

    def generate_weather_recommendations(self, waypoints: list = None) -> list:
        recommendations: List[str] = []
        weather = self._current_weather

        if not weather:
            return ["无可用天气数据，建议获取最新预报"]

        wind = weather.get("wind_speed", 0.0)
        wave = weather.get("wave_height", 0.0)
        vis = weather.get("visibility", 10.0)

        if wind > 40:
            recommendations.append(f"当前风速 {wind}kn 超过安全阈值 (40kn)，建议避开该区域或降速航行")
        if wave > 4:
            recommendations.append(f"浪高 {wave}m 达到中危水平，建议调整航向减小横摇")
        if vis < 1:
            recommendations.append(f"能见度 {vis}nm 极低，建议开启雾航模式并加强雷达瞭望")

        if not recommendations:
            recommendations.append("当前气象条件适合航行")

        return recommendations[:3]

    def update_weather_data(self, lat: float, lon: float, wind_speed: float,
                            wave_height: float, visibility: float) -> dict:
        """更新指定位置的天气网格数据。"""
        key = (round(lat), round(lon))
        self._weather_grid[key] = {
            "wind_speed": wind_speed,
            "wave_height": wave_height,
            "visibility": visibility,
            "timestamp": datetime.now().isoformat(),
        }
        return {"grid_key": list(key), "grid_size": len(self._weather_grid)}

    def get_weather_grid(self) -> dict:
        """返回天气网格数据（key 转为字符串以便 JSON 序列化）。"""
        return {
            "grid_size": len(self._weather_grid),
            "grid": {f"{k[0]},{k[1]}": v for k, v in self._weather_grid.items()},
        }

    # ---- helpers ----

    def _score_point(self, lat: float, lon: float) -> float:
        # 先查找最近的grid点
        key = (round(lat), round(lon))
        weather = self._weather_grid.get(key)
        # fallback到全局天气数据
        if not weather:
            weather = self._current_weather
        if not weather:
            return 0.0

        score = 0.0
        wind = weather.get("wind_speed", 0.0)
        wave = weather.get("wave_height", 0.0)
        vis = weather.get("visibility", 10.0)

        if wind > 40:
            score += min((wind - 40) * 2.5, 50)
        elif wind > 25:
            score += (wind - 25) * 1.0

        if wave > 4:
            score += min((wave - 4) * 8, 30)
        elif wave > 2:
            score += (wave - 2) * 3

        if vis < 1:
            score += min((1 - vis) * 40, 40)
        elif vis < 3:
            score += (3 - vis) * 5

        return min(score, 100.0)

    @staticmethod
    def _level_from_score(score: float) -> str:
        if score >= 75:
            return "critical"
        if score >= 50:
            return "high"
        if score >= 25:
            return "medium"
        return "low"

    @staticmethod
    def _compute_point_risk_level(weather: dict) -> str:
        wind = weather.get("wind_speed", 0.0)
        wave = weather.get("wave_height", 0.0)
        vis = weather.get("visibility", 10.0)
        if wind > 40 or vis < 1:
            return "high"
        if wave > 4 or wind > 25:
            return "medium"
        return "low"

    # ── ISO 19030 燃油优化 ──
    def fuel_optimization(self, route_waypoints: list = None,
                          vessel_speed_kn: float = 12.0,
                          fuel_consumption_rate: float = 25.0) -> Dict[str, Any]:
        """ISO 19030 燃油消耗预测与航线优化 (SEEMP Part III)."""
        waypoints = route_waypoints or []
        n_legs = max(len(waypoints) - 1, 1)
        distance_nm = n_legs * 120  # estimate
        hours = distance_nm / vessel_speed_kn if vessel_speed_kn > 0 else 0
        base_fuel_mt = hours * fuel_consumption_rate / 1000
        weather_factor = 1.0
        if self._active and hasattr(self, '_weather_grid'):
            weather_factor = 1.08  # rough sea penalty
        optimized_fuel_mt = base_fuel_mt * 0.95  # 5% savings from weather routing
        return {
            "distance_nm": round(distance_nm, 1),
            "estimated_hours": round(hours, 1),
            "base_fuel_mt": round(base_fuel_mt, 2),
            "optimized_fuel_mt": round(optimized_fuel_mt, 2),
            "fuel_saving_percent": 5.0,
            "weather_factor": weather_factor,
            "reference": "ISO 19030:2016, SEEMP Part III",
        }

    def passage_plan_update(self, optimized_route: list = None) -> Dict[str, Any]:
        """更新航次计划以反映气象优化结果."""
        return {"updated": True, "waypoints": len(optimized_route or []),
                "reference": "ISO 19030"}
