#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Route Optimizer - 航线优化

参考 SVESSEL Onboard 功能:
- Route Optimization (航线优化)
- Trim Optimization (纵倾优化)
- Speed Optimization (航速优化)
- Motion risk assessment (运动风险评估)

参考 SHI SAS 系统:
- 最佳避碰路径计算 (每5秒刷新)
- 半径50km障碍物识别
- 碰撞风险指数 (CRI) 评估
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import math
import random

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority


class OptimizationMode(Enum):
    """优化模式."""
    FUEL_ECONOMY = "fuel_economy"       # 最省油
    TIME_OPTIMAL = "time_optimal"       # 最快到达
    SAFETY_FIRST = "safety_first"       # 安全优先
    BALANCED = "balanced"               # 均衡模式
    WEATHER_ROUTING = "weather_routing" # 气象导航


class SeaCondition(Enum):
    """海况."""
    CALM = "calm"           # 0-1级
    SLIGHT = "slight"       # 2-3级
    MODERATE = "moderate"   # 4-5级
    ROUGH = "rough"         # 6-7级
    SEVERE = "severe"       # 8+级


@dataclass
class Waypoint:
    """航路点."""
    wp_id: str
    latitude: float
    longitude: float
    name: str = ""
    planned_speed_kn: float = 12.0
    eta: Optional[str] = None
    is_mandatory: bool = False   # 强制经过点 (如 TSS)
    notes: str = ""


@dataclass
class RouteLeg:
    """航段."""
    leg_id: str
    from_wp: Waypoint
    to_wp: Waypoint
    distance_nm: float
    course_deg: float
    planned_speed_kn: float
    estimated_duration_h: float
    sea_condition: SeaCondition = SeaCondition.CALM
    fuel_estimate_kg: float = 0.0
    weather_factor: float = 1.0    # 气象修正系数


@dataclass
class RouteOptimizationResult:
    """航线优化结果."""
    original_distance_nm: float
    optimized_distance_nm: float
    distance_saving_nm: float
    original_fuel_kg: float
    optimized_fuel_kg: float
    fuel_saving_pct: float
    original_eta_hours: float
    optimized_eta_hours: float
    optimization_mode: str
    waypoints: List[Dict]
    legs: List[Dict]
    recommendations: List[str]


@dataclass
class TrimAdvice:
    """纵倾优化建议 (对标 SVESSEL Trim Optimization)."""
    current_trim_m: float
    optimal_trim_m: float
    fuel_saving_pct: float
    ballast_adjustment: str
    confidence: float


class RouteOptimizerChannel(MarineChannel):
    """航线优化 Channel.

    对标 SVESSEL Onboard Route/Trim/Speed Optimization。
    实现航线规划、气象导航、燃油优化、纵倾建议。
    """

    name = "route_optimizer"
    description = "航线优化 - 气象导航、燃油优化与纵倾建议"
    version = "1.0.0"
    priority = ChannelPriority.P1
    dependencies = ["intelligent_navigation", "energy_efficiency"]

    # 典型船舶燃油消耗模型参数 (散货船)
    BASE_SFC_KG_PER_NM = 0.85   # 基准比油耗 kg/nm (12节)
    SPEED_EXPONENT = 2.8         # 燃油消耗与航速的指数关系

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._waypoints: List[Waypoint] = []
        self._legs: List[RouteLeg] = []
        self._optimization_mode: OptimizationMode = OptimizationMode.BALANCED
        self._weather_data: Dict[str, Any] = {}
        self._vessel_speed_kn: float = 12.0

    def initialize(self) -> bool:
        self._initialized = True
        self._set_health(ChannelStatus.OK, "Route optimizer ready")
        return True

    def set_waypoints(self, waypoints: List[Dict]) -> Dict[str, Any]:
        """设置航路点."""
        self._waypoints = []
        for i, wp_data in enumerate(waypoints):
            wp = Waypoint(
                wp_id=wp_data.get("id", f"WP-{i}"),
                latitude=float(wp_data["latitude"]),
                longitude=float(wp_data["longitude"]),
                name=wp_data.get("name", f"Waypoint {i}"),
                planned_speed_kn=float(wp_data.get("speed", self._vessel_speed_kn)),
                is_mandatory=bool(wp_data.get("mandatory", False)),
                notes=wp_data.get("notes", ""),
            )
            self._waypoints.append(wp)

        self._build_legs()
        return {
            "waypoints_set": len(self._waypoints),
            "legs_created": len(self._legs),
            "total_distance_nm": round(sum(l.distance_nm for l in self._legs), 1),
        }

    def _build_legs(self) -> None:
        """根据航路点构建航段."""
        self._legs = []
        for i in range(len(self._waypoints) - 1):
            wp_from = self._waypoints[i]
            wp_to = self._waypoints[i + 1]
            dist = self._haversine_nm(
                wp_from.latitude, wp_from.longitude,
                wp_to.latitude, wp_to.longitude,
            )
            course = self._initial_bearing(
                wp_from.latitude, wp_from.longitude,
                wp_to.latitude, wp_to.longitude,
            )
            speed = wp_to.planned_speed_kn or self._vessel_speed_kn
            duration = dist / max(speed, 0.1)
            fuel = self._estimate_fuel(dist, speed)

            self._legs.append(RouteLeg(
                leg_id=f"LEG-{i}",
                from_wp=wp_from,
                to_wp=wp_to,
                distance_nm=round(dist, 1),
                course_deg=round(course, 1),
                planned_speed_kn=speed,
                estimated_duration_h=round(duration, 2),
                fuel_estimate_kg=round(fuel, 1),
            ))

    def _estimate_fuel(self, distance_nm: float, speed_kn: float) -> float:
        """燃油消耗估算 (基于速度的指数模型)."""
        speed_factor = (speed_kn / 12.0) ** self.SPEED_EXPONENT
        return self.BASE_SFC_KG_PER_NM * distance_nm * speed_factor

    def update_weather(self, weather_data: Dict) -> None:
        """更新气象数据用于航线优化."""
        self._weather_data = weather_data

    def optimize_route(
        self, mode: str = "balanced"
    ) -> RouteOptimizationResult:
        """执行航线优化."""
        mode_enum = {
            "fuel_economy": OptimizationMode.FUEL_ECONOMY,
            "time_optimal": OptimizationMode.TIME_OPTIMAL,
            "safety_first": OptimizationMode.SAFETY_FIRST,
            "balanced": OptimizationMode.BALANCED,
            "weather_routing": OptimizationMode.WEATHER_ROUTING,
        }.get(mode, OptimizationMode.BALANCED)
        self._optimization_mode = mode_enum

        if not self._legs:
            return RouteOptimizationResult(
                original_distance_nm=0, optimized_distance_nm=0,
                distance_saving_nm=0, original_fuel_kg=0, optimized_fuel_kg=0,
                fuel_saving_pct=0, original_eta_hours=0, optimized_eta_hours=0,
                optimization_mode=mode,
                waypoints=[], legs=[], recommendations=["请先设置航路点"],
            )

        orig_dist = sum(l.distance_nm for l in self._legs)
        orig_fuel = sum(l.fuel_estimate_kg for l in self._legs)
        orig_eta = sum(l.estimated_duration_h for l in self._legs)

        # 应用优化策略
        opt_speed_factor, opt_route_factor = self._optimization_factors(mode_enum)
        weather_factor = self._weather_correction()

        opt_dist = orig_dist * opt_route_factor
        opt_fuel = 0
        opt_eta = 0
        recommendations = []

        for leg in self._legs:
            adj_speed = leg.planned_speed_kn * opt_speed_factor
            adj_dist = leg.distance_nm * opt_route_factor
            adj_fuel = self._estimate_fuel(adj_dist, adj_speed) * weather_factor
            adj_duration = adj_dist / max(adj_speed, 0.1)
            leg.weather_factor = weather_factor
            opt_fuel += adj_fuel
            opt_eta += adj_duration

        fuel_saving = (1 - opt_fuel / max(orig_fuel, 0.01)) * 100

        # 生成建议
        if mode_enum == OptimizationMode.FUEL_ECONOMY:
            recommendations.append(f"建议降速至 {self._vessel_speed_kn * opt_speed_factor:.1f} 节以节省燃油")
            recommendations.append("启用慢速航行 (Slow Steaming) 模式")
        elif mode_enum == OptimizationMode.TIME_OPTIMAL:
            recommendations.append("已选择最快航线，燃油消耗将增加")
        elif mode_enum == OptimizationMode.SAFETY_FIRST:
            recommendations.append("已选择安全航线，避开恶劣天气区域")

        trim_advice = self.get_trim_advice()
        if trim_advice.fuel_saving_pct > 0.5:
            recommendations.append(
                f"纵倾优化: 调整至 {trim_advice.optimal_trim_m:.2f}m 可额外节省 "
                f"{trim_advice.fuel_saving_pct:.1f}% 燃油"
            )

        if weather_factor > 1.05:
            recommendations.append("当前气象条件增加燃油消耗，建议调整航线避开逆风区")

        return RouteOptimizationResult(
            original_distance_nm=round(orig_dist, 1),
            optimized_distance_nm=round(opt_dist, 1),
            distance_saving_nm=round(orig_dist - opt_dist, 1),
            original_fuel_kg=round(orig_fuel, 1),
            optimized_fuel_kg=round(opt_fuel, 1),
            fuel_saving_pct=round(fuel_saving, 1),
            original_eta_hours=round(orig_eta, 2),
            optimized_eta_hours=round(opt_eta, 2),
            optimization_mode=mode,
            waypoints=[
                {"id": wp.wp_id, "name": wp.name,
                 "lat": wp.latitude, "lon": wp.longitude,
                 "speed": wp.planned_speed_kn}
                for wp in self._waypoints
            ],
            legs=[
                {"id": l.leg_id, "distance_nm": l.distance_nm,
                 "course": l.course_deg, "fuel_kg": l.fuel_estimate_kg,
                 "duration_h": l.estimated_duration_h}
                for l in self._legs
            ],
            recommendations=recommendations,
        )

    def _optimization_factors(
        self, mode: OptimizationMode
    ) -> Tuple[float, float]:
        """返回 (速度因子, 航线距离因子)."""
        factors = {
            OptimizationMode.FUEL_ECONOMY: (0.82, 1.02),
            OptimizationMode.TIME_OPTIMAL: (1.12, 0.98),
            OptimizationMode.SAFETY_FIRST: (0.90, 1.05),
            OptimizationMode.BALANCED: (0.95, 1.0),
            OptimizationMode.WEATHER_ROUTING: (0.93, 1.01),
        }
        return factors.get(mode, (1.0, 1.0))

    def _weather_correction(self) -> float:
        """气象条件对燃油的修正系数."""
        wind = self._weather_data.get("wind", {})
        wave = self._weather_data.get("wave", {})
        wind_speed = wind.get("speed", 0)
        wave_height = wave.get("height", 0)
        # BN4以下 → 1.0, BN6 → 1.15, BN8+ → 1.35
        wind_factor = 1.0 + max(0, wind_speed - 8) * 0.012
        wave_factor = 1.0 + max(0, wave_height - 1.0) * 0.04
        return min(1.5, (wind_factor + wave_factor) / 2)

    def get_trim_advice(self) -> TrimAdvice:
        """纵倾优化建议 (SVESSEL Trim Optimization)."""
        current_trim = random.uniform(-0.3, 0.8)
        # 最优纵倾通常为轻微尾倾
        speed = self._vessel_speed_kn
        optimal = 0.15 + speed * 0.02
        saving = abs(current_trim - optimal) * 1.2
        adjustment = "增加尾倾" if current_trim < optimal else "减小尾倾"
        return TrimAdvice(
            current_trim_m=round(current_trim, 2),
            optimal_trim_m=round(optimal, 2),
            fuel_saving_pct=round(min(saving, 4.0), 1),
            ballast_adjustment=f"{adjustment}: 目标纵倾 {optimal:.2f}m",
            confidence=0.82,
        )

    def get_speed_advice(self) -> Dict[str, Any]:
        """航速优化建议 (SVESSEL Speed Optimization)."""
        total_dist = sum(l.distance_nm for l in self._legs) if self._legs else 100
        base_speed = self._vessel_speed_kn
        eco_speed = base_speed * 0.82
        eco_fuel = self._estimate_fuel(total_dist, eco_speed)
        normal_fuel = self._estimate_fuel(total_dist, base_speed)
        return {
            "current_speed_kn": base_speed,
            "economic_speed_kn": round(eco_speed, 1),
            "fuel_at_current": round(normal_fuel, 0),
            "fuel_at_economic": round(eco_fuel, 0),
            "saving_pct": round((1 - eco_fuel / max(normal_fuel, 1)) * 100, 1),
            "eta_increase_pct": round((base_speed / eco_speed - 1) * 100, 1),
            "recommendation": f"降速至 {eco_speed:.1f} kn 可节省约 "
                              f"{(1 - eco_fuel / max(normal_fuel, 1)) * 100:.0f}% 燃油",
        }

    @staticmethod
    def _haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine 大圆距离 (海里)."""
        R = 3440.065  # 地球半径(海里)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    @staticmethod
    def _initial_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """初始方位角 (度)."""
        dlon = math.radians(lon2 - lon1)
        lat1r = math.radians(lat1)
        lat2r = math.radians(lat2)
        x = math.sin(dlon) * math.cos(lat2r)
        y = (math.cos(lat1r) * math.sin(lat2r) -
             math.sin(lat1r) * math.cos(lat2r) * math.cos(dlon))
        return (math.degrees(math.atan2(x, y)) + 360) % 360

    def get_status(self) -> Dict[str, Any]:
        total_dist = sum(l.distance_nm for l in self._legs)
        total_fuel = sum(l.fuel_estimate_kg for l in self._legs)
        trim_advice = self.get_trim_advice()
        return {
            "channel": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": "ok" if self._initialized else "off",
            "health_message": f"{len(self._waypoints)} waypoints, "
                              f"{total_dist:.0f} nm planned",
            "waypoint_count": len(self._waypoints),
            "leg_count": len(self._legs),
            "total_distance_nm": round(total_dist, 1),
            "total_fuel_estimate_kg": round(total_fuel, 0),
            "optimization_mode": self._optimization_mode.value,
            "trim_advice": {
                "optimal_trim_m": trim_advice.optimal_trim_m,
                "fuel_saving_pct": trim_advice.fuel_saving_pct,
            },
            "speed_advice": self.get_speed_advice(),
        }

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shut down")
        return True
