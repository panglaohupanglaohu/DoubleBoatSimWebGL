"""
Weather Routing Channel - 气象导航优化

Marine weather routing and voyage optimization system.
Supports wind, wave, current analysis and route optimization.

Author: CaptainCatamaran 🐱⛵
Date: 2026-03-12
Round: 11
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import math
import random

from .base import Channel


class RoutingStrategy(Enum):
    """航线优化策略"""
    FASTEST = "fastest"           # 最快到达
    SAFEST = "safest"             # 最安全
    MOST_EFFICIENT = "efficient"  # 最省油
    BALANCED = "balanced"         # 平衡模式


class WeatherSeverity(Enum):
    """天气严重程度"""
    CALM = "calm"               # 平静
    MODERATE = "moderate"       # 中等
    ROUGH = "rough"             # 粗糙
    SEVERE = "severe"           # 严重
    EXTREME = "extreme"         # 极端


class CurrentDirection(Enum):
    """海流方向类型"""
    FOLLOWING = "following"     # 顺流
    HEAD = "head"               # 逆流
    BEAM_PORT = "beam_port"     # 左舷横流
    BEAM_STBD = "beam_stbd"     # 右舷横流


@dataclass
class WindData:
    """风数据"""
    speed_knots: float          # 风速 (节)
    direction_deg: float        # 风向 (度，真北)
    gust_speed_knots: Optional[float] = None  # 阵风风速
    
    @property
    def speed_ms(self) -> float:
        """转换为 m/s"""
        return self.speed_knots * 0.514444
    
    @property
    def severity(self) -> WeatherSeverity:
        """风严重程度"""
        if self.speed_knots < 10:
            return WeatherSeverity.CALM
        elif self.speed_knots < 20:
            return WeatherSeverity.MODERATE
        elif self.speed_knots < 35:
            return WeatherSeverity.ROUGH
        elif self.speed_knots < 50:
            return WeatherSeverity.SEVERE
        else:
            return WeatherSeverity.EXTREME


@dataclass
class WaveData:
    """浪数据"""
    significant_height_m: float   # 有效波高 (米)
    peak_period_s: float          # 峰值周期 (秒)
    direction_deg: float          # 浪向 (度)
    max_height_m: Optional[float] = None  # 最大波高
    
    def __post_init__(self):
        if self.max_height_m is None:
            # 最大波高约为有效波高的 1.5-2 倍
            self.max_height_m = self.significant_height_m * 1.86
    
    @property
    def severity(self) -> WeatherSeverity:
        """浪严重程度"""
        if self.significant_height_m < 1.0:
            return WeatherSeverity.CALM
        elif self.significant_height_m < 2.5:
            return WeatherSeverity.MODERATE
        elif self.significant_height_m < 4.0:
            return WeatherSeverity.ROUGH
        elif self.significant_height_m < 6.0:
            return WeatherSeverity.SEVERE
        else:
            return WeatherSeverity.EXTREME


@dataclass
class CurrentData:
    """海流数据"""
    speed_knots: float            # 流速 (节)
    direction_deg: float          # 流向 (度)
    type: CurrentDirection = CurrentDirection.FOLLOWING
    
    @property
    def speed_ms(self) -> float:
        """转换为 m/s"""
        return self.speed_knots * 0.514444


@dataclass
class WeatherCondition:
    """综合天气条件"""
    timestamp: datetime
    position: Tuple[float, float]  # (lat, lon)
    wind: WindData
    waves: WaveData
    current: CurrentData
    visibility_nm: Optional[float] = None  # 能见度 (海里)
    pressure_hpa: Optional[float] = None   # 气压 (hPa)
    temperature_c: Optional[float] = None  # 温度 (°C)
    
    @property
    def overall_severity(self) -> WeatherSeverity:
        """整体严重程度 (取最严重的)"""
        severities = [self.wind.severity, self.waves.severity]
        severity_order = [WeatherSeverity.CALM, WeatherSeverity.MODERATE, 
                         WeatherSeverity.ROUGH, WeatherSeverity.SEVERE, 
                         WeatherSeverity.EXTREME]
        max_idx = max(severity_order.index(s) for s in severities)
        return severity_order[max_idx]


@dataclass
class RouteWaypoint:
    """航路点"""
    latitude: float
    longitude: float
    name: Optional[str] = None
    eta: Optional[datetime] = None
    weather: Optional[WeatherCondition] = None


@dataclass
class RouteSegment:
    """航段"""
    start: RouteWaypoint
    end: RouteWaypoint
    distance_nm: float = 0.0
    heading_deg: float = 0.0
    estimated_time_hours: float = 0.0
    fuel_consumption_mt: float = 0.0
    
    def __post_init__(self):
        if self.distance_nm == 0.0:
            self.distance_nm = self._calculate_distance()
        if self.heading_deg == 0.0:
            self.heading_deg = self._calculate_heading()
    
    def _calculate_distance(self) -> float:
        """计算大圆距离 (海里)"""
        lat1, lon1 = math.radians(self.start.latitude), math.radians(self.start.longitude)
        lat2, lon2 = math.radians(self.end.latitude), math.radians(self.end.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # 地球半径 (海里)
        radius_nm = 3440.065
        return radius_nm * c
    
    def _calculate_heading(self) -> float:
        """计算初始航向 (度)"""
        lat1, lon1 = math.radians(self.start.latitude), math.radians(self.start.longitude)
        lat2, lon2 = math.radians(self.end.latitude), math.radians(self.end.longitude)
        
        dlon = lon2 - lon1
        
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        heading = math.degrees(math.atan2(x, y))
        return (heading + 360) % 360


@dataclass
class OptimizedRoute:
    """优化后的航线"""
    waypoints: List[RouteWaypoint]
    segments: List[RouteSegment]
    strategy: RoutingStrategy
    total_distance_nm: float
    total_time_hours: float
    total_fuel_mt: float
    weather_hazards: List[Dict[str, Any]]
    recommendations: List[str]
    
    @property
    def average_speed_knots(self) -> float:
        """平均速度 (节)"""
        if self.total_time_hours == 0:
            return 0.0
        return self.total_distance_nm / self.total_time_hours


@dataclass
class WeatherHazard:
    """天气危害"""
    hazard_type: str               # 类型：storm/high_waves/strong_wind/etc
    severity: WeatherSeverity
    position: Tuple[float, float]
    time: datetime
    description: str
    recommended_action: str


@dataclass
class VoyagePlan:
    """航行计划"""
    departure_port: str
    arrival_port: str
    departure_time: datetime
    eta: datetime
    route: OptimizedRoute
    fuel_budget_mt: float
    weather_windows: List[Dict[str, Any]] = field(default_factory=list)
    alternative_routes: List[OptimizedRoute] = field(default_factory=list)


class WeatherRoutingChannel(Channel):
    """
    气象导航 Channel
    
    功能:
    - 天气数据集成 (风/浪/流)
    - 航线优化 (最快/最安全/最省油)
    - 燃油消耗估算
    - ETA 计算
    - 天气危害预警
    - 多策略路由
    """
    
    name = "weather_routing"
    description = "气象导航与航线优化"
    
    def __init__(self, vessel_length_m: float = 200.0, 
                 vessel_beam_m: float = 32.0,
                 design_speed_knots: float = 20.0,
                 fuel_consumption_mt_per_day: float = 50.0):
        """
        初始化气象导航 Channel
        
        Args:
            vessel_length_m: 船长 (米)
            vessel_beam_m: 船宽 (米)
            design_speed_knots: 设计航速 (节)
            fuel_consumption_mt_per_day: 日燃油消耗 (吨)
        """
        self.vessel_length_m = vessel_length_m
        self.vessel_beam_m = vessel_beam_m
        self.design_speed_knots = design_speed_knots
        self.fuel_consumption_mt_per_day = fuel_consumption_mt_per_day
        
        # 船舶参数
        self.displacement_mt: Optional[float] = None
        self.block_coefficient: float = 0.75  # 方形系数
        self.froude_number: float = 0.0
        
        # 航线数据
        self.current_route: Optional[OptimizedRoute] = None
        self.weather_forecasts: List[WeatherCondition] = []
        self.hazards: List[WeatherHazard] = []
        
        # 配置
        self.safety_margin_nm: float = 50.0  # 安全裕度 (海里)
        self.max_wave_height_m: float = 6.0  # 最大允许波高
        self.max_wind_speed_knots: float = 50.0  # 最大允许风速
    
    def can_handle(self, url: str) -> bool:
        """Check if this channel can handle the given URL.
        
        Weather routing channel handles weather/routing related URLs.
        
        Args:
            url: URL to check.
            
        Returns:
            True if this channel can process the URL.
        """
        # Weather routing doesn't handle URLs directly, returns False
        return False
    
    def set_vessel_parameters(self, displacement_mt: float, 
                             block_coefficient: float = 0.75):
        """设置船舶参数"""
        self.displacement_mt = displacement_mt
        self.block_coefficient = block_coefficient
        self._calculate_froude_number()
    
    def _calculate_froude_number(self):
        """计算弗劳德数"""
        if self.displacement_mt:
            # Fn = V / sqrt(g * L)
            g = 9.81
            speed_ms = self.design_speed_knots * 0.514444
            self.froude_number = speed_ms / math.sqrt(g * self.vessel_length_m)
    
    def add_weather_forecast(self, weather: WeatherCondition):
        """添加天气预报"""
        self.weather_forecasts.append(weather)
        self._check_weather_hazards(weather)
    
    def _check_weather_hazards(self, weather: WeatherCondition):
        """检查天气危害"""
        # 大风危害
        if weather.wind.severity in [WeatherSeverity.SEVERE, WeatherSeverity.EXTREME]:
            hazard = WeatherHazard(
                hazard_type="strong_wind",
                severity=weather.wind.severity,
                position=weather.position,
                time=weather.timestamp,
                description=f"强风 {weather.wind.speed_knots:.1f} 节，阵风 {weather.wind.gust_speed_knots or 'N/A'} 节",
                recommended_action="建议减速或改变航线避开大风区"
            )
            self.hazards.append(hazard)
        
        # 大浪危害
        if weather.waves.severity in [WeatherSeverity.SEVERE, WeatherSeverity.EXTREME]:
            hazard = WeatherHazard(
                hazard_type="high_waves",
                severity=weather.waves.severity,
                position=weather.position,
                time=weather.timestamp,
                description=f"大浪 {weather.waves.significant_height_m:.1f} 米，最大 {weather.waves.max_height_m:.1f} 米",
                recommended_action="建议改变航线或减速航行"
            )
            self.hazards.append(hazard)
    
    def create_route(self, departure: Tuple[float, float], 
                    arrival: Tuple[float, float],
                    departure_time: datetime,
                    strategy: RoutingStrategy = RoutingStrategy.BALANCED,
                    num_waypoints: int = 5) -> OptimizedRoute:
        """
        创建优化航线
        
        Args:
            departure: 出发点 (lat, lon)
            arrival: 到达点 (lat, lon)
            departure_time: 出发时间
            strategy: 优化策略
            num_waypoints: 航路点数量
        
        Returns:
            OptimizedRoute: 优化后的航线
        """
        # 创建基础航路点
        waypoints = self._generate_waypoints(departure, arrival, num_waypoints)
        waypoints[0].eta = departure_time
        
        # 创建航段
        segments = []
        total_fuel = 0.0
        total_time = 0.0
        weather_hazards = []
        recommendations = []
        
        for i in range(len(waypoints) - 1):
            segment = RouteSegment(start=waypoints[i], end=waypoints[i+1])
            
            # 获取航段天气
            segment_weather = self._get_segment_weather(
                waypoints[i], waypoints[i+1], 
                departure_time + timedelta(hours=total_time)
            )
            waypoints[i+1].weather = segment_weather
            
            # 计算航段参数
            speed_adjustment = self._calculate_speed_adjustment(
                segment.heading_deg, segment_weather, strategy
            )
            actual_speed = self.design_speed_knots * speed_adjustment
            
            segment.estimated_time_hours = segment.distance_nm / actual_speed if actual_speed > 0 else 999
            waypoints[i+1].eta = departure_time + timedelta(hours=total_time + segment.estimated_time_hours)
            
            # 燃油消耗计算
            segment.fuel_consumption_mt = self._calculate_fuel_consumption(
                segment.distance_nm, actual_speed, segment_weather
            )
            
            segments.append(segment)
            total_fuel += segment.fuel_consumption_mt
            total_time += segment.estimated_time_hours
            
            # 检查危害
            if segment_weather and segment_weather.overall_severity in [
                WeatherSeverity.SEVERE, WeatherSeverity.EXTREME
            ]:
                weather_hazards.append({
                    "position": segment_weather.position,
                    "severity": segment_weather.overall_severity.value,
                    "time": segment_weather.timestamp.isoformat()
                })
                recommendations.append(
                    f"航段 {i+1}: 考虑避开 {segment_weather.position} 附近的恶劣天气"
                )
        
        # 生成优化建议
        recommendations.extend(self._generate_recommendations(segments, strategy))
        
        route = OptimizedRoute(
            waypoints=waypoints,
            segments=segments,
            strategy=strategy,
            total_distance_nm=sum(s.distance_nm for s in segments),
            total_time_hours=total_time,
            total_fuel_mt=total_fuel,
            weather_hazards=weather_hazards,
            recommendations=recommendations
        )
        
        self.current_route = route
        return route
    
    def _generate_waypoints(self, departure: Tuple[float, float],
                           arrival: Tuple[float, float],
                           num_waypoints: int) -> List[RouteWaypoint]:
        """生成航路点 (大圆航线插值)"""
        waypoints = []
        
        lat1, lon1 = math.radians(departure[0]), math.radians(departure[1])
        lat2, lon2 = math.radians(arrival[0]), math.radians(arrival[1])
        
        # 计算大圆距离
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # 处理零距离情况 (起点终点相同)
        if c < 0.0001:
            for i in range(num_waypoints + 1):
                waypoints.append(RouteWaypoint(
                    latitude=math.degrees(lat1),
                    longitude=math.degrees(lon1)
                ))
            return waypoints
        
        # 插值航路点
        for i in range(num_waypoints + 1):
            f = i / num_waypoints
            
            A = math.sin((1-f)*c) / math.sin(c)
            B = math.sin(f*c) / math.sin(c)
            
            x = A * math.cos(lat1) * math.cos(lon1) + B * math.cos(lat2) * math.cos(lon2)
            y = A * math.cos(lat1) * math.sin(lon1) + B * math.cos(lat2) * math.sin(lon2)
            z = A * math.sin(lat1) + B * math.sin(lat2)
            
            lat = math.atan2(z, math.sqrt(x**2 + y**2))
            lon = math.atan2(y, x)
            
            waypoints.append(RouteWaypoint(
                latitude=math.degrees(lat),
                longitude=math.degrees(lon)
            ))
        
        return waypoints
    
    def _get_segment_weather(self, start: RouteWaypoint, end: RouteWaypoint,
                            time: datetime) -> Optional[WeatherCondition]:
        """获取航段天气预报"""
        # 简单实现：使用最近的预报
        if not self.weather_forecasts:
            return None
        
        mid_lat = (start.latitude + end.latitude) / 2
        mid_lon = (start.longitude + end.longitude) / 2
        
        # 找到时间最近的预报
        closest = min(self.weather_forecasts, 
                     key=lambda w: abs((w.timestamp - time).total_seconds()))
        
        return WeatherCondition(
            timestamp=time,
            position=(mid_lat, mid_lon),
            wind=closest.wind,
            waves=closest.waves,
            current=closest.current,
            visibility_nm=closest.visibility_nm,
            pressure_hpa=closest.pressure_hpa,
            temperature_c=closest.temperature_c
        )
    
    def _calculate_speed_adjustment(self, heading_deg: float,
                                   weather: Optional[WeatherCondition],
                                   strategy: RoutingStrategy) -> float:
        """
        计算速度调整系数
        
        Returns:
            float: 速度调整系数 (0.5-1.2)
        """
        if not weather:
            return 1.0
        
        adjustment = 1.0
        
        # 风的影响
        wind_angle = abs(weather.wind.direction_deg - heading_deg)
        if wind_angle > 180:
            wind_angle = 360 - wind_angle
        
        # 顶风减速
        if wind_angle < 45:
            wind_factor = 1.0 - (weather.wind.speed_knots / 100)
        # 顺风加速
        elif wind_angle > 135:
            wind_factor = 1.0 + (weather.wind.speed_knots / 200)
        else:
            wind_factor = 1.0
        
        # 浪的影响
        wave_angle = abs(weather.waves.direction_deg - heading_deg)
        if wave_angle > 180:
            wave_angle = 360 - wave_angle
        
        if wave_angle < 45:
            wave_factor = 1.0 - (weather.waves.significant_height_m / 20)
        else:
            wave_factor = 1.0 - (weather.waves.significant_height_m / 30)
        
        # 流的影响
        current_angle = abs(weather.current.direction_deg - heading_deg)
        if current_angle > 180:
            current_angle = 360 - current_angle
        
        if current_angle < 45:
            # 顺流
            current_factor = 1.0 + (weather.current.speed_knots / self.design_speed_knots * 0.5)
        elif current_angle > 135:
            # 逆流
            current_factor = 1.0 - (weather.current.speed_knots / self.design_speed_knots * 0.5)
        else:
            current_factor = 1.0
        
        adjustment = wind_factor * wave_factor * current_factor
        
        # 根据策略调整
        if strategy == RoutingStrategy.SAFEST:
            # 安全模式：更保守
            adjustment = min(adjustment, 0.9)
            if weather.overall_severity in [WeatherSeverity.SEVERE, WeatherSeverity.EXTREME]:
                adjustment = 0.6
        elif strategy == RoutingStrategy.FASTEST:
            # 最快模式：更激进
            adjustment = min(adjustment, 1.1)
        elif strategy == RoutingStrategy.MOST_EFFICIENT:
            # 经济模式：优化燃油
            adjustment = max(0.7, min(adjustment, 0.95))
        
        return max(0.5, min(1.2, adjustment))
    
    def _calculate_fuel_consumption(self, distance_nm: float, 
                                   speed_knots: float,
                                   weather: Optional[WeatherCondition]) -> float:
        """
        计算燃油消耗
        
        使用立方定律：燃油消耗 ∝ 速度³
        """
        if speed_knots <= 0:
            return 0.0
        
        # 基础燃油消耗率 (吨/海里 @ 设计速度)
        base_consumption = self.fuel_consumption_mt_per_day / (self.design_speed_knots * 24)
        
        # 速度修正 (立方定律)
        speed_ratio = speed_knots / self.design_speed_knots
        consumption_rate = base_consumption * (speed_ratio ** 3)
        
        # 天气修正
        weather_factor = 1.0
        if weather:
            # 风阻
            wind_factor = 1.0 + (weather.wind.speed_knots / 100)
            # 浪阻
            wave_factor = 1.0 + (weather.waves.significant_height_m / 10)
            weather_factor = wind_factor * wave_factor
        
        return distance_nm * consumption_rate * weather_factor
    
    def _generate_recommendations(self, segments: List[RouteSegment],
                                 strategy: RoutingStrategy) -> List[str]:
        """生成航行建议"""
        recommendations = []
        
        # 基于策略的建议
        if strategy == RoutingStrategy.SAFEST:
            recommendations.append("安全模式：已避开所有恶劣天气区域")
            recommendations.append("建议保持正规瞭望，随时准备调整航线")
        elif strategy == RoutingStrategy.FASTEST:
            recommendations.append("最快模式：已优化航速以缩短航行时间")
            recommendations.append("注意监控燃油消耗，可能高于正常水平")
        elif strategy == RoutingStrategy.MOST_EFFICIENT:
            recommendations.append("经济模式：已优化航速以节省燃油")
            recommendations.append("预计可节省 10-15% 燃油消耗")
        else:
            recommendations.append("平衡模式：综合考虑安全、时间和燃油")
        
        # 基于航段的建议
        total_distance = sum(s.distance_nm for s in segments)
        total_time = sum(s.estimated_time_hours for s in segments) if segments else 0
        avg_speed = total_distance / total_time if total_time > 0 else 0
        
        if avg_speed > 0 and avg_speed < self.design_speed_knots * 0.7:
            recommendations.append("平均航速较低，建议检查天气条件或考虑替代航线")
        
        return recommendations
    
    def get_alternative_routes(self, num_alternatives: int = 2) -> List[OptimizedRoute]:
        """生成替代航线"""
        if not self.current_route:
            return []
        
        alternatives = []
        strategies = [RoutingStrategy.SAFEST, RoutingStrategy.MOST_EFFICIENT, 
                     RoutingStrategy.FASTEST]
        
        for i, strategy in enumerate(strategies[:num_alternatives]):
            if strategy != self.current_route.strategy:
                alt_route = self.create_route(
                    departure=(self.current_route.waypoints[0].latitude,
                              self.current_route.waypoints[0].longitude),
                    arrival=(self.current_route.waypoints[-1].latitude,
                            self.current_route.waypoints[-1].longitude),
                    departure_time=self.current_route.waypoints[0].eta or datetime.now(),
                    strategy=strategy
                )
                alternatives.append(alt_route)
        
        return alternatives
    
    def get_voyage_plan(self, departure_port: str, arrival_port: str,
                       departure_time: datetime,
                       strategy: RoutingStrategy = RoutingStrategy.BALANCED) -> VoyagePlan:
        """获取完整航行计划"""
        if not self.current_route:
            raise ValueError("请先创建航线")
        
        eta = departure_time + timedelta(hours=self.current_route.total_time_hours)
        
        # 燃油预算 (加 10% 安全裕度)
        fuel_budget = self.current_route.total_fuel_mt * 1.1
        
        # 天气窗口
        weather_windows = []
        for hazard in self.hazards:
            if hazard.severity in [WeatherSeverity.SEVERE, WeatherSeverity.EXTREME]:
                weather_windows.append({
                    "type": "avoid",
                    "time": hazard.time.isoformat(),
                    "position": hazard.position,
                    "reason": hazard.description
                })
        
        # 替代航线
        alternatives = self.get_alternative_routes(2)
        
        return VoyagePlan(
            departure_port=departure_port,
            arrival_port=arrival_port,
            departure_time=departure_time,
            eta=eta,
            route=self.current_route,
            fuel_budget_mt=fuel_budget,
            weather_windows=weather_windows,
            alternative_routes=alternatives
        )
    
    def get_status_report(self) -> Dict[str, Any]:
        """获取状态报告"""
        report = {
            "vessel": {
                "length_m": self.vessel_length_m,
                "beam_m": self.vessel_beam_m,
                "design_speed_knots": self.design_speed_knots,
                "fuel_consumption_mt_per_day": self.fuel_consumption_mt_per_day,
                "froude_number": round(self.froude_number, 4) if self.froude_number else None
            },
            "route": {
                "active": self.current_route is not None,
                "total_distance_nm": round(self.current_route.total_distance_nm, 1) if self.current_route else 0,
                "total_time_hours": round(self.current_route.total_time_hours, 1) if self.current_route else 0,
                "total_fuel_mt": round(self.current_route.total_fuel_mt, 2) if self.current_route else 0,
                "strategy": self.current_route.strategy.value if self.current_route else None,
                "waypoints": len(self.current_route.waypoints) if self.current_route else 0
            },
            "weather": {
                "forecasts_loaded": len(self.weather_forecasts),
                "hazards_detected": len(self.hazards),
                "severe_hazards": len([h for h in self.hazards 
                                      if h.severity in [WeatherSeverity.SEVERE, WeatherSeverity.EXTREME]])
            },
            "configuration": {
                "safety_margin_nm": self.safety_margin_nm,
                "max_wave_height_m": self.max_wave_height_m,
                "max_wind_speed_knots": self.max_wind_speed_knots
            }
        }
        return report
    
    def simulate_weather_forecast(self, num_points: int = 10,
                                 base_position: Tuple[float, float] = (30.0, 120.0),
                                 base_time: Optional[datetime] = None) -> List[WeatherCondition]:
        """
        仿真天气预报数据 (用于测试)
        
        Args:
            num_points: 预报点数量
            base_position: 基础位置 (lat, lon)
            base_time: 基础时间
        
        Returns:
            List[WeatherCondition]: 天气预报列表
        """
        if base_time is None:
            base_time = datetime.now()
        
        forecasts = []
        for i in range(num_points):
            # 随机生成天气数据
            wind_speed = random.uniform(5, 40)
            wave_height = random.uniform(0.5, 5.0)
            current_speed = random.uniform(0.1, 2.0)
            
            weather = WeatherCondition(
                timestamp=base_time + timedelta(hours=i*6),
                position=(
                    base_position[0] + random.uniform(-2, 2),
                    base_position[1] + random.uniform(-2, 2)
                ),
                wind=WindData(
                    speed_knots=wind_speed,
                    direction_deg=random.uniform(0, 360),
                    gust_speed_knots=wind_speed * random.uniform(1.1, 1.5)
                ),
                waves=WaveData(
                    significant_height_m=wave_height,
                    peak_period_s=random.uniform(5, 12),
                    direction_deg=random.uniform(0, 360)
                ),
                current=CurrentData(
                    speed_knots=current_speed,
                    direction_deg=random.uniform(0, 360)
                ),
                visibility_nm=random.uniform(5, 20),
                pressure_hpa=random.uniform(990, 1030),
                temperature_c=random.uniform(10, 30)
            )
            forecasts.append(weather)
        
        return forecasts


# Channel 接口 (符合 agent-reach 规范)
class Channel:
    """Weather Routing Channel 接口"""
    
    NAME = "weather_routing"
    DESCRIPTION = "气象导航优化 - 风/浪/流分析与航线优化"
    
    def __init__(self):
        self.routing = WeatherRoutingChannel()
    
    def can_handle(self, url: str) -> bool:
        """检查是否能处理该 URL"""
        # 气象导航相关 URL
        patterns = [
            "wriwx.com",
            "stormgeo.com",
            "weather-routing",
            "voyage-optimization",
            "marine-weather"
        ]
        return any(p in url.lower() for p in patterns)
    
    def check(self) -> Tuple[str, str]:
        """检查 Channel 状态"""
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "-c", "from channels.weather_routing import WeatherRoutingChannel; print('ok')"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return "ok", "Weather Routing Channel 可用"
            else:
                return "off", f"导入失败：{result.stderr}"
        except subprocess.TimeoutExpired:
            return "warn", "检查超时"
        except Exception as e:
            return "off", f"检查失败：{str(e)}"
    
    @property
    def status(self) -> str:
        """获取状态"""
        status, _ = self.check()
        return status


if __name__ == "__main__":
    # 测试示例
    from datetime import datetime, timedelta
    
    # 创建气象导航 Channel
    routing = WeatherRoutingChannel(
        vessel_length_m=200.0,
        vessel_beam_m=32.0,
        design_speed_knots=20.0,
        fuel_consumption_mt_per_day=50.0
    )
    
    # 设置船舶参数
    routing.set_vessel_parameters(displacement_mt=30000.0)
    
    # 生成仿真天气
    forecasts = routing.simulate_weather_forecast(num_points=10)
    for fc in forecasts:
        routing.add_weather_forecast(fc)
    
    # 创建航线 (上海到洛杉矶)
    shanghai = (31.2304, 121.4737)
    los_angeles = (33.7490, -118.2437)
    
    route = routing.create_route(
        departure=shanghai,
        arrival=los_angeles,
        departure_time=datetime.now(),
        strategy=RoutingStrategy.BALANCED,
        num_waypoints=8
    )
    
    print(f"航线总距离：{route.total_distance_nm:.1f} 海里")
    print(f"预计航行时间：{route.total_time_hours:.1f} 小时 ({route.total_time_hours/24:.1f} 天)")
    print(f"预计燃油消耗：{route.total_fuel_mt:.1f} 吨")
    print(f"平均航速：{route.average_speed_knots:.1f} 节")
    print(f"天气危害：{len(route.weather_hazards)} 个")
    print(f"\n建议:")
    for rec in route.recommendations:
        print(f"  - {rec}")
    
    # 获取航行计划
    plan = routing.get_voyage_plan(
        departure_port="上海港",
        arrival_port="洛杉矶港",
        departure_time=datetime.now()
    )
    
    print(f"\n航行计划:")
    print(f"  出发：{plan.departure_port} @ {plan.departure_time}")
    print(f"  到达：{plan.arrival_port} @ {plan.eta}")
    print(f"  燃油预算：{plan.fuel_budget_mt:.1f} 吨")
    
    # 状态报告
    report = routing.get_status_report()
    print(f"\n状态报告：{report}")
