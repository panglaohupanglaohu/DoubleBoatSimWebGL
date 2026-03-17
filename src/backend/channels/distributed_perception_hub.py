# -*- coding: utf-8 -*-
"""
Distributed Perception Hub Channel - 分布式感知网络骨架

统一采集导航、机舱、能效事件，形成最小事件流。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

from .marine_base import MarineChannel, ChannelPriority, ChannelStatus, get_default_registry


@dataclass
class FusionEvent:
    """多源感知融合事件"""
    id: str
    timestamp: str
    event_type: str  # navigation/engine/efficiency/ais/weather/fusion
    source: str      # channel name or external source
    payload: Dict[str, Any]
    confidence: float = 1.0  # 0.0-1.0
    fused_with: List[str] = None  # other event IDs this was fused with
    risk_correlation: Optional[Dict[str, float]] = None  # correlation to risk factors
    
    def to_dict(self):
        result = asdict(self)
        # Handle None values for lists
        if self.fused_with is None:
            result.pop('fused_with', None)
        if self.risk_correlation is None:
            result.pop('risk_correlation', None)
        return result


class DistributedPerceptionHubChannel(MarineChannel):
    name = "distributed_perception_hub"
    description = "分布式感知网络 (多源融合 + 风险关联)"
    version = "0.2.0"
    priority = ChannelPriority.P0
    dependencies: List[str] = ["intelligent_navigation", "intelligent_engine", "energy_efficiency", "worldmonitor_real"]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.config = config or {}
        self._config = self.config
        self.max_events = self.config.get("max_events", 500)
        self.events: List[FusionEvent] = []
        self.fusion_rules = self._load_fusion_rules()
        self.risk_correlations = self._load_risk_correlations()
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{self.name}")

    def _load_fusion_rules(self) -> Dict[str, Any]:
        """加载多源感知融合规则"""
        return {
            # AIS 目标与导航风险融合
            "ais_nav_fusion": {
                "match_criteria": ["mmsi", "position", "course", "speed"],
                "fusion_logic": "enhance_collision_risk_assessment",
                "confidence_boost": 0.2
            },
            # 气象数据与能效融合
            "weather_efficiency_fusion": {
                "match_criteria": ["position", "timestamp"],
                "fusion_logic": "adjust_efficiency_prediction",
                "confidence_boost": 0.15
            },
            # 机舱状态与导航决策融合
            "engine_nav_fusion": {
                "match_criteria": ["timestamp", "vessel_id"],
                "fusion_logic": "correlate_engine_impact_on_navigation",
                "confidence_boost": 0.25
            }
        }
    
    def _load_risk_correlations(self) -> Dict[str, List[str]]:
        """加载风险关联规则"""
        return {
            "collision_risk": ["ais_target_proximity", "weather_severity", "engine_availability"],
            "mechanical_risk": ["engine_status", "maintenance_schedule", "operational_hours"],
            "compliance_risk": ["cii_deviation", "eexi_threshold", "seemp_adherence"],
            "weather_risk": ["wave_height", "wind_speed", "visibility", "current_strength"]
        }

    def initialize(self) -> bool:
        self._initialized = True
        self.capture_system_snapshot()
        self._set_health(ChannelStatus.OK, "分布式感知网络就绪")
        self.logger.info("🔄 Distributed perception hub initialized with fusion rules")
        return True

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True

    def append_event(self, event_type: str, payload: Dict[str, Any], source: str, confidence: float = 1.0) -> FusionEvent:
        """添加融合事件"""
        event = FusionEvent(
            id=f"evt-{len(self.events)+1}",
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            source=source,
            payload=payload,
            confidence=confidence
        )
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        return event

    def fuse_ais_with_navigation(self, ais_payload: Dict[str, Any], nav_payload: Dict[str, Any]) -> Optional[FusionEvent]:
        """融合 AIS 数据与导航数据"""
        try:
            # 检查是否可以融合 (基于位置、时间相近)
            ais_lat = ais_payload.get("latitude")
            ais_lng = ais_payload.get("longitude")
            nav_lat = nav_payload.get("own_ship", {}).get("latitude")
            nav_lng = nav_payload.get("own_ship", {}).get("longitude")
            
            if not all([ais_lat, ais_lng, nav_lat, nav_lng]):
                return None
            
            # 计算距离（简化版）
            import math
            lat_diff = abs(ais_lat - nav_lat)
            lng_diff = abs(ais_lng - nav_lng)
            distance_nm = math.sqrt(lat_diff**2 + lng_diff**2) * 60  # approx nautical miles
            
            if distance_nm > 20.0:  # 超过 20 海里不融合
                return None
            
            # 创建融合事件
            fused_payload = {
                "ais_target": ais_payload,
                "navigation_context": nav_payload,
                "distance_nm": round(distance_nm, 3),
                "fusion_confidence": min(0.95, 0.7 + (0.3 * (1 - distance_nm/20.0)))  # 距离越近，置信度越高
            }
            
            # 计算风险关联
            risk_corr = {}
            if distance_nm < 0.5:  # 500 米内高风险
                risk_corr["collision_risk"] = 0.9
            elif distance_nm < 1.0:
                risk_corr["collision_risk"] = 0.7
            elif distance_nm < 3.0:
                risk_corr["collision_risk"] = 0.4
            
            fusion_event = FusionEvent(
                id=f"fus-{len(self.events)+1}",
                timestamp=datetime.now().isoformat(),
                event_type="ais_nav_fusion",
                source="ais+navigation",
                payload=fused_payload,
                confidence=fused_payload["fusion_confidence"],
                risk_correlation=risk_corr
            )
            
            self.events.append(fusion_event)
            if len(self.events) > self.max_events:
                self.events = self.events[-self.max_events:]
            
            self.logger.debug(f"🔗 Fused AIS+NAV event, distance: {distance_nm}nm, confidence: {fusion_event.confidence}")
            return fusion_event
            
        except Exception as e:
            self.logger.error(f"❌ AIS+NAV fusion failed: {e}")
            return None

    def fuse_weather_with_efficiency(self, weather_payload: Dict[str, Any], efficiency_payload: Dict[str, Any]) -> Optional[FusionEvent]:
        """融合气象数据与能效数据"""
        try:
            # 检查是否可以融合（基于位置、时间相近）
            pos1 = weather_payload.get("position", {})
            pos2 = efficiency_payload.get("position", {})
            lat1, lng1 = pos1.get("lat"), pos1.get("lng")
            lat2, lng2 = pos2.get("latitude"), pos2.get("longitude")
            
            if not all([lat1, lng1, lat2, lng2]):
                return None
            
            import math
            lat_diff = abs(lat1 - lat2)
            lng_diff = abs(lng1 - lng2)
            distance_nm = math.sqrt(lat_diff**2 + lng_diff**2) * 60
            
            if distance_nm > 5.0:  # 超过 5 海里不融合
                return None
            
            # 气象对能效影响评估
            wind_speed = weather_payload.get("wind", {}).get("speed", 0)
            wave_height = weather_payload.get("wave", {}).get("height", 0)
            efficiency_factor = 1.0
            
            if wind_speed > 20:  # 强风
                efficiency_factor *= 0.95  # 燃油消耗 +5%
            if wave_height > 3.0:  # 大浪
                efficiency_factor *= 0.92  # 燃油消耗 +8%
            
            fused_payload = {
                "weather_data": weather_payload,
                "efficiency_data": efficiency_payload,
                "position_distance_nm": round(distance_nm, 3),
                "weather_efficiency_impact": {
                    "wind_factor": wind_speed,
                    "wave_factor": wave_height,
                    "predicted_efficiency_change": round((1.0 - efficiency_factor) * 100, 2)
                },
                "fusion_confidence": min(0.9, 0.6 + (0.3 * (1 - distance_nm/5.0)))
            }
            
            # 计算风险关联
            risk_corr = {}
            if wind_speed > 25 or wave_height > 4.0:
                risk_corr["weather_risk"] = 0.8
            elif wind_speed > 15 or wave_height > 2.5:
                risk_corr["weather_risk"] = 0.5
            
            fusion_event = FusionEvent(
                id=f"fus-{len(self.events)+1}",
                timestamp=datetime.now().isoformat(),
                event_type="weather_efficiency_fusion",
                source="weather+efficiency",
                payload=fused_payload,
                confidence=fused_payload["fusion_confidence"],
                risk_correlation=risk_corr
            )
            
            self.events.append(fusion_event)
            if len(self.events) > self.max_events:
                self.events = self.events[-self.max_events:]
            
            self.logger.debug(f"🔗 Fused Weather+Efficiency event, impact: {(1-efficiency_factor)*100:+.1f}%, confidence: {fusion_event.confidence}")
            return fusion_event
            
        except Exception as e:
            self.logger.error(f"❌ Weather+Efficiency fusion failed: {e}")
            return None

    def capture_system_snapshot(self) -> List[FusionEvent]:
        """捕获系统快照并尝试融合"""
        registry = get_default_registry()
        captured: List[FusionEvent] = []
        
        # 获取各通道状态
        nav_ch = registry.get("intelligent_navigation")
        engine_ch = registry.get("intelligent_engine") 
        efficiency_ch = registry.get("energy_efficiency")
        worldmonitor_ch = registry.get("worldmonitor_real")  # 真实数据源
        
        # 获取状态
        nav_status = nav_ch.get_status() if nav_ch else {"error": "channel_not_found"}
        engine_status = engine_ch.get_status() if engine_ch else {"error": "channel_not_found"}
        efficiency_status = efficiency_ch.get_status() if efficiency_ch else {"error": "channel_not_found"}
        
        # 从 WorldMonitor 获取真实数据（如果可用）- 当前使用同步方式避免 asyncio 问题
        worldmonitor_ais = None
        worldmonitor_weather = None
        if worldmonitor_ch:
            try:
                # 尝试直接调用（如果 worldmonitor_real 有这些方法）
                if hasattr(worldmonitor_ch, 'get_ais_targets'):
                    worldmonitor_ais = worldmonitor_ch.get_ais_targets()
                if hasattr(worldmonitor_ch, 'get_marine_weather'):
                    worldmonitor_weather = worldmonitor_ch.get_marine_weather(31.2304, 121.4737)
            except Exception as e:
                self.logger.warning(f"WorldMonitor data fetch failed: {e}")
                pass  # 不阻塞主线程
        
        # 记录基础事件
        if nav_ch:
            nav_evt = self.append_event("navigation_event", nav_status, "intelligent_navigation")
            captured.append(nav_evt)
        if engine_ch:
            engine_evt = self.append_event("engine_event", engine_status, "intelligent_engine")
            captured.append(engine_evt)
        if efficiency_ch:
            efficiency_evt = self.append_event("efficiency_event", efficiency_status, "energy_efficiency")
            captured.append(efficiency_evt)
        
        # 尝试融合 AIS + Navigation
        if nav_ch and worldmonitor_ais:
            try:
                # 实际融合逻辑
                fusion_result = self.fuse_ais_with_navigation(
                    worldmonitor_ais, 
                    nav_status
                )
                if fusion_result:
                    captured.append(fusion_result)
            except Exception as e:
                self.logger.warning(f"AIS+Navigation fusion failed: {e}")
        
        # 尝试融合 Weather + Efficiency  
        if worldmonitor_weather and efficiency_ch:
            try:
                fusion_result = self.fuse_weather_with_efficiency(
                    worldmonitor_weather,
                    efficiency_status
                )
                if fusion_result:
                    captured.append(fusion_result)
            except Exception as e:
                self.logger.warning(f"Weather+Efficiency fusion failed: {e}")
        
        # 尝试与 NMEA2000 数据融合
        try:
            nmea_ch = registry.get("nmea2000_parser")
            if nmea_ch:
                nmea_messages = []
                if hasattr(nmea_ch, 'get_messages'):
                    nmea_messages = nmea_ch.get_messages()
                
                # 融合 NMEA2000 AIS 数据与 WorldMonitor AIS 数据
                for msg in nmea_messages:
                    if msg.pgn == 129038 or msg.pgn == 129039:  # AIS A/B 类位置报告
                        nmea_ais_data = {
                            "mmsi": msg.fields.get("user_id"),
                            "latitude": msg.fields.get("latitude"),
                            "longitude": msg.fields.get("longitude"),
                            "course": msg.fields.get("course_over_ground"),
                            "speed": msg.fields.get("speed_over_ground"),
                            "heading": msg.fields.get("true_heading"),
                            "timestamp": msg.timestamp,
                            "source": "nmea2000"
                        }
                        
                        # 与 WorldMonitor AIS 融合
                        if worldmonitor_ais:
                            nmea_world_fusion = self.fuse_nmea_with_worldmonitor_ais(nmea_ais_data, worldmonitor_ais)
                            if nmea_world_fusion:
                                captured.append(nmea_world_fusion)
        except Exception as e:
            self.logger.warning(f"NMEA2000+WorldMonitor fusion failed: {e}")
        
        return captured

    def fuse_nmea_with_worldmonitor_ais(self, nmea_ais: Dict[str, Any], worldmonitor_ais: Dict[str, Any]) -> Optional[FusionEvent]:
        """融合 NMEA2000 AIS 数据与 WorldMonitor AIS 数据"""
        try:
            # 检查是否可以融合（基于 MMSI 匹配）
            nmea_mmsi = nmea_ais.get("mmsi")
            wm_targets = worldmonitor_ais.get("targets", [])
            
            matching_target = None
            for target in wm_targets:
                if target.get("mmsi") == nmea_mmsi:
                    matching_target = target
                    break
            
            if not matching_target:
                return None  # 没有匹配的目标，无法融合
            
            # 计算位置差异（验证数据一致性）
            nmea_lat = nmea_ais.get("latitude")
            nmea_lon = nmea_ais.get("longitude")
            wm_lat = matching_target.get("latitude")
            wm_lon = matching_target.get("longitude")
            
            if not all([nmea_lat, nmea_lon, wm_lat, wm_lon]):
                return None
            
            import math
            lat_diff = abs(nmea_lat - wm_lat)
            lon_diff = abs(nmea_lon - wm_lon)
            position_delta_nm = math.sqrt(lat_diff**2 + lon_diff**2) * 60  # approx nautical miles
            
            # 如果位置差异小于 0.1 海里，认为是同一条船
            if position_delta_nm > 0.1:
                return None  # 位置差异过大，不是同一条船
            
            # 创建融合事件
            fused_payload = {
                "nmea2000_source": nmea_ais,
                "worldmonitor_source": matching_target,
                "position_delta_nm": round(position_delta_nm, 3),
                "fusion_type": "ais_cross_validation",
                "confidence": 0.9 if position_delta_nm < 0.05 else 0.7  # 位置越接近，置信度越高
            }
            
            # 风险关联计算
            risk_corr = {}
            if position_delta_nm > 0.05:  # 如果差异较大，可能存在传感器误差风险
                risk_corr["sensor_accuracy_risk"] = 0.6
            
            fusion_event = FusionEvent(
                id=f"fus-nmea-wm-{len(self.events)+1}",
                timestamp=datetime.now().isoformat(),
                event_type="nmea_world_ais_fusion",
                source="nmea2000+worldmonitor",
                payload=fused_payload,
                confidence=fused_payload["confidence"],
                risk_correlation=risk_corr
            )
            
            self.events.append(fusion_event)
            if len(self.events) > self.max_events:
                self.events = self.events[-self.max_events:]
            
            self.logger.debug(f"🔗 Fused NMEA2000+WorldMonitor AIS, delta: {position_delta_nm}nm, conf: {fusion_event.confidence}")
            return fusion_event
            
        except Exception as e:
            self.logger.error(f"❌ NMEA2000+WorldMonitor AIS fusion failed: {e}")
            return None



    def get_latest_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        return [evt.to_dict() for evt in self.events[-limit:]]

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "health_message": self._health.message,
            "event_count": len(self.events),
            "fusion_events_count": len([e for e in self.events if "fusion" in e.event_type]),
            "latest_events": self.get_latest_events(5),
            "fusion_capabilities": {
                "ais_nav_fusion": True,
                "weather_efficiency_fusion": True,
                "engine_nav_fusion": True,
            },
            "cloud_sync": {
                "enabled": False,
                "mode": "placeholder",
                "message": "已预留云同步接口，当前使用本地事件流。",
            },
        }




__all__ = ["DistributedPerceptionHubChannel"]
