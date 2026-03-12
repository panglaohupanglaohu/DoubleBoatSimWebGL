# -*- coding: utf-8 -*-
"""
Integration Tests - Marine Channels (Simplified)

简化版集成测试：验证 Channel 基本功能和接口

测试场景:
1. Navigation Data Channel 基本功能
2. Cargo Monitor Channel 基本功能  
3. Weather Routing Channel 基本功能
4. Engine Monitor Channel 基本功能
5. Power Management Channel 基本功能

Author: CaptainCatamaran 🐱⛵
Date: 2026-03-12
Phase: 3 - System Integration
"""

import pytest
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'marine_engineer_agent'))

from skills.channels.navigation_data import NavigationDataChannel
from skills.channels.cargo_monitor import CargoMonitorChannel, CargoType
from skills.channels.weather_routing import WeatherRoutingChannel, RoutingStrategy
from skills.channels.engine_monitor import EngineMonitorChannel
from skills.channels.power_management import PowerManagementChannel


class TestNavigationDataIntegration:
    """导航数据 Channel 集成测试"""
    
    def test_navigation_channel_initialization(self):
        """测试导航 Channel 初始化"""
        nav = NavigationDataChannel()
        assert nav is not None
        assert nav.name == "navigation_data"
    
    def test_position_update(self):
        """测试位置更新"""
        nav = NavigationDataChannel()
        nav.update_position(latitude=35.6762, longitude=139.6503, source="GPS")
        
        report = nav.get_nav_status()
        assert report is not None
        assert "position" in report or "gps" in str(report).lower()
    
    def test_depth_update(self):
        """测试水深更新"""
        nav = NavigationDataChannel()
        nav.update_depth(depth_m=150.0, temperature_c=18.5)
        
        report = nav.get_nav_status()
        assert report is not None
    
    def test_speed_update(self):
        """测试速度更新"""
        nav = NavigationDataChannel()
        nav.update_speed(speed_knots=12.5, distance_nm=1250.0)
        
        report = nav.get_nav_status()
        assert report is not None
    
    def test_navigation_report(self):
        """测试导航报告生成"""
        nav = NavigationDataChannel()
        
        # 更新多个参数
        nav.update_position(latitude=35.6762, longitude=139.6503)
        nav.update_depth(depth_m=150.0)
        nav.update_speed(speed_knots=12.5)
        
        report = nav.get_nav_status()
        assert report is not None
        assert isinstance(report, dict)


class TestCargoMonitorIntegration:
    """货物监控 Channel 集成测试"""
    
    def test_cargo_channel_initialization(self):
        """测试货物 Channel 初始化"""
        cargo = CargoMonitorChannel()
        assert cargo is not None
        assert cargo.name == "cargo_monitor"
    
    def test_reefer_container_registration(self):
        """测试冷藏箱注册"""
        cargo = CargoMonitorChannel()
        cargo.register_reefer_container(
            container_id="MSKU123456",
            setpoint_c=-18.0,
            current_temp_c=-17.5,
            humidity_percent=55.0,
            status="running"
        )
        
        report = cargo.get_status_report()
        assert report["reefer_containers"]["count"] >= 1
    
    def test_cargo_tank_registration(self):
        """测试液货舱注册"""
        cargo = CargoMonitorChannel()
        cargo.register_cargo_tank(
            tank_id="TANK-1",
            tank_name="No.1 Cargo Tank",
            cargo_type=CargoType.LIQUID_BULK,
            capacity_m3=10000,
            current_level_percent=85.0,
            temperature_c=25.0,
            pressure_bar=0.2
        )
        
        report = cargo.get_status_report()
        assert report["cargo_tanks"]["count"] >= 1
    
    def test_temperature_update(self):
        """测试温度更新"""
        cargo = CargoMonitorChannel()
        cargo.register_reefer_container(
            container_id="MSKU123456",
            setpoint_c=-18.0,
            current_temp_c=-17.5,
            humidity_percent=55.0,
            status="running"
        )
        
        cargo.update_reefer_temperature("MSKU123456", -16.0)
        
        report = cargo.get_status_report()
        assert report["reefer_containers"]["count"] >= 1
    
    def test_alarm_generation(self):
        """测试报警生成"""
        cargo = CargoMonitorChannel()
        cargo.register_reefer_container(
            container_id="MSKU123456",
            setpoint_c=-18.0,
            current_temp_c=-10.0,  # 严重偏差
            humidity_percent=55.0,
            status="alarm"
        )
        
        alarms = cargo.get_active_alarms()
        assert len(alarms) > 0
    
    def test_ventilation_registration(self):
        """测试通风系统注册"""
        cargo = CargoMonitorChannel()
        cargo.register_ventilation(
            cargo_hold_id="HOLD-1",
            fan_running=True,
            ventilation_rate_m3h=5000,
            inlet_temp_c=20.0,
            outlet_temp_c=25.0,
            inlet_humidity_percent=60.0,
            outlet_humidity_percent=75.0,
            dew_point_c=18.0
        )
        
        report = cargo.get_status_report()
        assert report is not None


class TestWeatherRoutingIntegration:
    """气象导航 Channel 集成测试"""
    
    def test_weather_channel_initialization(self):
        """测试气象 Channel 初始化"""
        weather = WeatherRoutingChannel()
        assert weather is not None
        assert weather.name == "weather_routing"
    
    def test_route_creation(self):
        """测试航线创建"""
        weather = WeatherRoutingChannel()
        
        tokyo = {"latitude": 35.6762, "longitude": 139.6503}
        la = {"latitude": 34.0522, "longitude": -118.2437}
        
        route = weather.create_route(
            departure=(tokyo["latitude"], tokyo["longitude"]),
            arrival=(la["latitude"], la["longitude"]),
            departure_time=datetime.now(),
            strategy=RoutingStrategy.BALANCED
        )
        
        assert route is not None
        assert route.total_distance_nm > 0
    
    def test_weather_forecast_loading(self):
        """测试气象预报加载"""
        weather = WeatherRoutingChannel()
        
        # 加载仿真气象数据
        weather.load_weather_forecast(
            start_time=datetime.now(),
            duration_hours=48,
            interval_hours=3
        )
        
        report = weather.get_status_report()
        assert report["weather"]["forecasts_loaded"] > 0
    
    def test_routing_recommendations(self):
        """测试航线建议"""
        weather = WeatherRoutingChannel()
        
        tokyo = {"latitude": 35.6762, "longitude": 139.6503}
        la = {"latitude": 34.0522, "longitude": -118.2437}
        
        weather.create_route(
            departure=(tokyo["latitude"], tokyo["longitude"]),
            arrival=(la["latitude"], la["longitude"]),
            departure_time=datetime.now(),
            strategy=RoutingStrategy.MOST_EFFICIENT
        )
        
        recommendations = weather.get_routing_recommendations()
        assert isinstance(recommendations, list)


class TestEngineMonitorIntegration:
    """主机监控 Channel 集成测试"""
    
    def test_engine_channel_initialization(self):
        """测试主机 Channel 初始化"""
        engine = EngineMonitorChannel()
        assert engine is not None
        assert engine.name == "engine_monitor"
    
    def test_rpm_update(self):
        """测试转速更新"""
        engine = EngineMonitorChannel()
        engine.update_rpm(rpm=120, load_percent=75.0)
        
        status = engine.get_status()
        assert status["running"] is True
        assert status["rpm"] == 120
    
    def test_temperature_update(self):
        """测试温度更新"""
        engine = EngineMonitorChannel()
        engine.update_temperature("cooling_water", 85.0)
        
        status = engine.get_status()
        assert status is not None
    
    def test_pressure_update(self):
        """测试压力更新"""
        engine = EngineMonitorChannel()
        engine.update_pressure("lube_oil", 4.5)
        
        status = engine.get_status()
        assert status is not None
    
    def test_fuel_consumption_update(self):
        """测试燃油消耗更新"""
        engine = EngineMonitorChannel()
        engine.update_fuel_consumption(180.0)
        
        efficiency = engine.get_fuel_efficiency_report()
        assert efficiency is not None


class TestPowerManagementIntegration:
    """电力管理 Channel 集成测试"""
    
    def test_power_channel_initialization(self):
        """测试电力 Channel 初始化"""
        power = PowerManagementChannel()
        assert power is not None
        assert power.name == "power_management"
    
    def test_generator_addition(self):
        """测试发电机添加"""
        power = PowerManagementChannel()
        power.add_generator(
            gen_id="GEN-1",
            rated_power_kw=1000,
            current_voltage=440,
            current_frequency=60.0
        )
        
        status = power.get_status()
        assert len(status["generators"]) >= 1
    
    def test_generator_load_update(self):
        """测试发电机负载更新"""
        power = PowerManagementChannel()
        power.add_generator("GEN-1", rated_power_kw=1000, current_voltage=440, current_frequency=60.0)
        power.update_generator_load("GEN-1", load_kw=750)
        
        status = power.get_status()
        assert status["total_load_kw"] == 750
    
    def test_bus_bar_update(self):
        """测试汇流排更新"""
        power = PowerManagementChannel()
        power.update_bus_bar(voltage=440, frequency=60.0)
        
        status = power.get_status()
        assert status is not None
    
    def test_load_sharing_optimization(self):
        """测试负载分配优化"""
        power = PowerManagementChannel()
        power.add_generator("GEN-1", rated_power_kw=1000, current_voltage=440, current_frequency=60.0)
        power.add_generator("GEN-2", rated_power_kw=1000, current_voltage=440, current_frequency=60.0)
        
        optimization = power.optimize_load_sharing(total_load_kw=1500)
        assert optimization is not None
        assert "distribution" in optimization


class TestMultiChannelIntegration:
    """多 Channel 联合测试"""
    
    def test_channel_compatibility(self):
        """测试所有 Channel 可共存"""
        nav = NavigationDataChannel()
        cargo = CargoMonitorChannel()
        weather = WeatherRoutingChannel()
        engine = EngineMonitorChannel()
        power = PowerManagementChannel()
        
        assert nav is not None
        assert cargo is not None
        assert weather is not None
        assert engine is not None
        assert power is not None
    
    def test_channel_registry(self):
        """测试 Channel 注册"""
        from agent_reach.channels import get_channel
        
        # 测试获取 Marine Channel
        nav_channel = get_channel("navigation_data")
        assert nav_channel is not None
        
        cargo_channel = get_channel("cargo_monitor")
        assert cargo_channel is not None
        
        weather_channel = get_channel("weather_routing")
        assert weather_channel is not None
        
        engine_channel = get_channel("engine_monitor")
        assert engine_channel is not None
        
        power_channel = get_channel("power_management")
        assert power_channel is not None
    
    def test_channel_check_method(self):
        """测试 Channel 健康检查"""
        channels = [
            NavigationDataChannel(),
            CargoMonitorChannel(),
            WeatherRoutingChannel(),
            EngineMonitorChannel(),
            PowerManagementChannel()
        ]
        
        for channel in channels:
            status, message = channel.check()
            assert status in ["ok", "warn", "off", "error"]
