# -*- coding: utf-8 -*-
"""
Integration Test: Voyage Monitoring

测试场景：航行监控联合仿真
- Navigation Data Channel (导航数据)
- Vessel AIS Channel (AIS 目标追踪)
- Weather Routing Channel (气象导航)

验证:
1. 多源数据融合
2. 碰撞预警 (CPA/TCPA)
3. 气象航线优化
4. 综合安全评估
"""

import pytest
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'marine_engineer_agent'))

from skills.channels.navigation_data import NavigationDataChannel
from skills.channels.vessel_ais import VesselAISChannel, VesselPosition
from skills.channels.weather_routing import WeatherRoutingChannel, RoutingStrategy


class TestVoyageMonitoringIntegration:
    """航行监控集成测试"""
    
    @pytest.fixture
    def nav_channel(self):
        """初始化导航数据 Channel"""
        return NavigationDataChannel()
    
    @pytest.fixture
    def ais_channel(self):
        """初始化 AIS Channel"""
        return VesselAISChannel()
    
    @pytest.fixture
    def weather_channel(self):
        """初始化气象导航 Channel"""
        return WeatherRoutingChannel()
    
    def test_position_and_ais_integration(self, nav_channel, ais_channel):
        """测试位置数据与 AIS 目标融合"""
        # 设置本船位置
        nav_channel.update_position(
            latitude=35.6762,
            longitude=139.6503,
            course=45.0,
            speed=12.5
        )
        
        # 添加 AIS 目标船
        target = VesselPosition(
            mmsi=123456789,
            latitude=35.7000,
            longitude=139.7000,
            course=225.0,
            speed=10.0,
            heading=220,
            status=0
        )
        ais_channel.add_target(target)
        
        # 获取本船位置
        nav_report = nav_channel.get_navigation_report()
        assert nav_report["position"]["latitude"] == 35.6762
        assert nav_report["position"]["longitude"] == 139.6503
        
        # 获取 AIS 目标
        ais_report = ais_channel.get_targets()
        assert len(ais_report) >= 1
        assert ais_report[0]["mmsi"] == "123456789"
    
    def test_cpa_tcpa_calculation(self, nav_channel, ais_channel):
        """测试 CPA/TCPA 碰撞预警计算"""
        # 设置本船状态
        nav_channel.update_position(
            latitude=35.6762,
            longitude=139.6503,
            course=0.0,  # 向北
            speed=15.0
        )
        
        # 添加横向穿越的目标船
        target = VesselPosition(
            mmsi=987654321,
            latitude=35.7000,
            longitude=139.6503,
            course=90.0,  # 向东
            speed=12.0,
            heading=90,
            status=0
        )
        ais_channel.add_target(target)
        
        # 计算 CPA/TCPA
        cpa, tcpa = ais_channel.calculate_cpa_tcpa(
            target,
            own_lat=35.6762,
            own_lon=139.6503,
            own_course=0.0,
            own_speed=15.0
        )
        
        # CPA/TCPA 应该为有限值
        assert cpa is not None
        assert tcpa is not None
        
        # 验证碰撞风险
        collision_risk = ais_channel.assess_collision_risk(cpa, tcpa)
        assert collision_risk in ["safe", "caution", "warning", "danger"]
    
    def test_weather_routing_integration(self, nav_channel, weather_channel):
        """测试气象航线优化"""
        # 设置航线
        start_point = {"latitude": 35.6762, "longitude": 139.6503}  # 东京
        end_point = {"latitude": 34.0522, "longitude": -118.2437}  # 洛杉矶
        
        # 设置气象条件
        weather_channel.update_conditions(
            wind_speed=25.0,  # 节
            wind_direction=270.0,  # 西风
            wave_height=3.5,  # 米
            wave_period=8.0,
            current_speed=2.0,
            current_direction=90.0
        )
        
        # 计算优化航线
        route = weather_channel.calculate_optimal_route(
            start_point,
            end_point,
            strategy=RoutingStrategy.MOST_EFFICIENT
        )
        
        assert route is not None
        assert "waypoints" in route
        assert len(route["waypoints"]) > 0
        assert "estimated_time" in route
        assert "fuel_consumption" in route
    
    def test_comprehensive_voyage_report(self, nav_channel, ais_channel, weather_channel):
        """测试综合航行报告生成"""
        # 设置本船状态
        nav_channel.update_position(
            latitude=35.6762,
            longitude=139.6503,
            course=45.0,
            speed=12.5
        )
        
        # 添加多个 AIS 目标
        targets = [
            VesselPosition(mmsi=100000000+i, latitude=35.68+i*0.01, longitude=139.66+i*0.01,
                          course=45.0+i*10, speed=10.0+i, heading=45, status=0)
            for i in range(3)
        ]
        for target in targets:
            ais_channel.add_target(target)
        
        # 设置气象条件
        weather_channel.update_conditions(
            wind_speed=15.0,
            wind_direction=90.0,
            wave_height=2.0,
            wave_period=7.0
        )
        
        # 生成综合报告
        voyage_report = self.generate_voyage_report(nav_channel, ais_channel, weather_channel)
        
        # 验证报告结构
        assert "navigation" in voyage_report
        assert "ais_targets" in voyage_report
        assert "weather" in voyage_report
        assert "safety_level" in voyage_report
        assert "recommendations" in voyage_report
        
        # 验证数据准确性
        assert voyage_report["navigation"]["speed"] == 12.5
        assert len(voyage_report["ais_targets"]) == 3
        assert voyage_report["weather"]["wind_speed"] == 15.0
        
        # 验证安全等级
        assert voyage_report["safety_level"] in ["safe", "caution", "warning", "danger"]
    
    def test_severe_weather_response(self, nav_channel, weather_channel):
        """测试恶劣天气响应"""
        # 设置正常气象条件
        weather_channel.update_conditions(
            wind_speed=10.0,
            wave_height=1.5
        )
        
        # 验证正常状态
        weather_report = weather_channel.get_weather_report()
        assert weather_report["severity"] in ["calm", "moderate"]
        
        # 模拟恶劣天气
        weather_channel.update_conditions(
            wind_speed=55.0,  # 台风级
            wave_height=8.0,
            wave_period=12.0
        )
        
        # 验证恶劣天气检测
        weather_report = weather_channel.get_weather_report()
        assert weather_report["severity"] in ["severe", "extreme"]
        
        # 获取避台建议
        recommendations = weather_channel.get_routing_recommendations()
        assert len(recommendations) > 0
        assert any("avoid" in rec.lower() or "heave" in rec.lower() 
                  for rec in recommendations)
    
    def test_navigation_sensor_fusion(self, nav_channel):
        """测试导航传感器数据融合"""
        # 模拟多传感器输入
        nav_channel.update_gps(
            latitude=35.6762,
            longitude=139.6503,
            quality=4,  # RTK 固定解
            satellites=12
        )
        
        nav_channel.update_compass(
            true_heading=45.0,
            magnetic_heading=40.0,
            variation=5.0
        )
        
        nav_channel.update_depth(
            depth_meters=150.0,
            temperature=18.5
        )
        
        nav_channel.update_log(
            speed_through_water=12.5,
            distance_nm=1250.0
        )
        
        # 获取融合报告
        report = nav_channel.get_navigation_report()
        
        # 验证传感器数据
        assert "gps" in report["sensors"]
        assert "compass" in report["sensors"]
        assert "depth" in report["sensors"]
        assert "log" in report["sensors"]
        
        # 验证数据质量
        gps_data = report["sensors"]["gps"]
        assert gps_data["quality"] == "RTK_FIX"
        assert gps_data["satellites"] == 12
    
    def generate_voyage_report(self, nav, ais, weather) -> Dict[str, Any]:
        """生成综合航行报告 (辅助方法)"""
        nav_report = nav.get_navigation_report()
        ais_targets = ais.get_targets()
        weather_report = weather.get_weather_report()
        
        # 计算综合安全等级
        safety_level = "safe"
        if weather_report.get("severity") in ["severe", "extreme"]:
            safety_level = "warning"
        if len(ais_targets) > 0:
            # 简化：实际应计算 CPA/TCPA
            safety_level = "caution" if safety_level == "safe" else safety_level
        
        # 生成建议
        recommendations = []
        if weather_report.get("severity") in ["rough", "severe", "extreme"]:
            recommendations.append("Consider route adjustment due to weather")
        if len(ais_targets) > 5:
            recommendations.append("High traffic area - maintain vigilant lookout")
        
        return {
            "navigation": {
                "position": nav_report["position"],
                "course": nav_report["heading"]["true_heading"],
                "speed": nav_report["speed"]["speed_over_ground"]
            },
            "ais_targets": [
                {"mmsi": t.mmsi, "bearing": t.bearing if hasattr(t, 'bearing') else 0}
                for t in ais_targets
            ],
            "weather": {
                "wind_speed": weather_report.get("wind_speed", 0),
                "wave_height": weather_report.get("wave_height", 0),
                "severity": weather_report.get("severity", "unknown")
            },
            "safety_level": safety_level,
            "recommendations": recommendations
        }
