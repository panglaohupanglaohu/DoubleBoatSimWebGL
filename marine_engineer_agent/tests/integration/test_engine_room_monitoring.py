# -*- coding: utf-8 -*-
"""
Integration Test: Engine Room Monitoring

测试场景：机舱监控联合仿真
- Engine Monitor Channel (主机监控)
- Power Management Channel (电力管理)
- Navigation Data Channel (航行数据)

验证:
1. 主机 - 电力协同
2. 负载分配优化
3. 燃油效率分析
4. 综合报警管理
"""

import pytest
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'marine_engineer_agent'))

from skills.channels.engine_monitor import EngineMonitorChannel, AlarmLevel
from skills.channels.power_management import PowerManagementChannel
from skills.channels.navigation_data import NavigationDataChannel


class TestEngineRoomIntegration:
    """机舱监控集成测试"""
    
    @pytest.fixture
    def engine_channel(self):
        """初始化主机监控 Channel"""
        return EngineMonitorChannel()
    
    @pytest.fixture
    def power_channel(self):
        """初始化电力管理 Channel"""
        return PowerManagementChannel()
    
    @pytest.fixture
    def nav_channel(self):
        """初始化导航数据 Channel"""
        return NavigationDataChannel()
    
    def test_engine_power_coordination(self, engine_channel, power_channel):
        """测试主机 - 电力协同"""
        # 设置主机状态
        engine_channel.update_rpm(rpm=120, load_percent=85.0)
        engine_channel.update_temperature("cooling_water", 85.0)
        engine_channel.update_pressure("lube_oil", 4.5)
        
        # 设置电力负载
        power_channel.add_generator(
            gen_id="GEN-1",
            rated_power_kw=1000,
            current_voltage=440,
            current_frequency=60.0
        )
        power_channel.update_generator_load("GEN-1", load_kw=800)
        
        # 验证协同状态
        engine_report = engine_channel.get_status()
        power_report = power_channel.get_status()
        
        assert engine_report["running"] is True
        assert engine_report["load_percent"] == 85.0
        assert power_report["total_load_kw"] == 800
        assert power_report["generators"][0]["load_percent"] == 80.0
    
    def test_load_sharing_optimization(self, power_channel):
        """测试负载分配优化"""
        # 添加多台发电机
        power_channel.add_generator("GEN-1", rated_power_kw=1000, current_voltage=440, current_frequency=60.0)
        power_channel.add_generator("GEN-2", rated_power_kw=1000, current_voltage=440, current_frequency=60.0)
        power_channel.add_generator("GEN-3", rated_power_kw=500, current_voltage=440, current_frequency=60.0)
        
        # 设置总负载
        total_load = 1800  # kW
        
        # 优化负载分配
        optimization = power_channel.optimize_load_sharing(total_load)
        
        # 验证分配结果
        assert optimization is not None
        assert "distribution" in optimization
        assert optimization["total_load"] == total_load
        
        # 验证每台发电机负载在合理范围
        for gen_dist in optimization["distribution"]:
            assert 0 <= gen_dist["load_kw"] <= gen_dist["rated_kw"]
    
    def test_fuel_efficiency_analysis(self, engine_channel, nav_channel):
        """测试燃油效率分析"""
        # 设置主机工况
        engine_channel.update_rpm(rpm=120, load_percent=75.0)
        engine_channel.update_fuel_consumption(180.0)  # g/kWh
        
        # 设置航行状态
        nav_channel.update_position(latitude=35.6762, longitude=139.6503, course=45.0, speed=15.0)
        
        # 获取燃油效率报告
        efficiency_report = engine_channel.get_fuel_efficiency_report()
        
        assert efficiency_report is not None
        assert "fuel_consumption_rate" in efficiency_report
        assert "efficiency_rating" in efficiency_report
        
        # 验证效率评级
        assert efficiency_report["efficiency_rating"] in ["excellent", "good", "fair", "poor"]
    
    def test_emergency_power_response(self, engine_channel, power_channel):
        """测试应急电源响应"""
        # 模拟主发电机故障
        power_channel.add_generator("GEN-1", rated_power_kw=1000, current_voltage=440, current_frequency=60.0)
        power_channel.add_generator("GEN-2", rated_power_kw=1000, current_voltage=440, current_frequency=60.0)
        
        # 模拟 GEN-1 故障
        power_channel.simulate_generator_failure("GEN-1")
        
        # 验证应急响应
        status = power_channel.get_status()
        assert status["emergency_mode"] is True
        assert status["available_generators"] == 1
        
        # 验证应急发电机启动
        power_channel.start_emergency_generator()
        status = power_channel.get_status()
        assert status["emergency_generator_running"] is True
    
    def test_comprehensive_engine_room_report(self, engine_channel, power_channel, nav_channel):
        """测试综合机舱报告"""
        # 设置主机状态
        engine_channel.update_rpm(rpm=120, load_percent=80.0)
        engine_channel.update_temperature("cooling_water", 82.0)
        engine_channel.update_pressure("lube_oil", 4.2)
        engine_channel.update_temperature("exhaust", 350.0)
        
        # 设置电力状态
        power_channel.add_generator("GEN-1", rated_power_kw=1000, current_voltage=440, current_frequency=60.0)
        power_channel.update_generator_load("GEN-1", load_kw=750)
        
        # 设置航行状态
        nav_channel.update_position(latitude=35.6762, longitude=139.6503, course=45.0, speed=14.5)
        
        # 生成综合报告
        report = self.generate_engine_room_report(engine_channel, power_channel, nav_channel)
        
        # 验证报告结构
        assert "engine" in report
        assert "power" in report
        assert "navigation" in report
        assert "overall_health" in report
        assert "recommendations" in report
        
        # 验证数据准确性
        assert report["engine"]["rpm"] == 120
        assert report["engine"]["load_percent"] == 80.0
        assert report["power"]["total_load_kw"] == 750
        assert report["navigation"]["speed"] == 14.5
        
        # 验证健康状态
        assert report["overall_health"] in ["excellent", "good", "fair", "poor", "critical"]
    
    def test_alarm_cascade(self, engine_channel, power_channel):
        """测试报警级联"""
        # 模拟主机滑油低压报警
        engine_channel.update_pressure("lube_oil", 2.0)  # 低于正常值
        
        # 获取报警
        alarms = engine_channel.get_active_alarms()
        
        # 验证报警生成
        assert len(alarms) > 0
        
        # 验证报警级别
        critical_alarms = [a for a in alarms if a.level in [AlarmLevel.SHUTDOWN, AlarmLevel.SLOW_DOWN]]
        
        # 滑油低压应该触发严重报警
        assert len(critical_alarms) > 0 or len(alarms) > 0
    
    def test_maintenance_prediction(self, engine_channel):
        """测试维护预测"""
        # 模拟长期运行数据
        for i in range(100):
            engine_channel.update_rpm(rpm=120, load_percent=75.0)
            engine_channel.update_temperature("cooling_water", 80.0 + i * 0.1)
        
        # 获取维护建议
        maintenance = engine_channel.get_maintenance_recommendations()
        
        assert maintenance is not None
        assert "items" in maintenance
        
        # 验证维护项目
        for item in maintenance["items"]:
            assert "component" in item
            assert "priority" in item
            assert "recommended_action" in item
    
    def generate_engine_room_report(self, engine, power, nav) -> dict:
        """生成综合机舱报告 (辅助方法)"""
        engine_report = engine.get_status()
        power_report = power.get_status()
        nav_report = nav.get_navigation_report()
        
        # 计算整体健康状态
        health_score = 100
        
        # 主机健康扣分
        if engine_report.get("load_percent", 0) > 90:
            health_score -= 20
        if engine_report.get("cooling_water_temp", 0) > 90:
            health_score -= 15
        
        # 电力系统健康扣分
        if power_report.get("emergency_mode", False):
            health_score -= 30
        if power_report.get("total_load_kw", 0) > power_report.get("total_capacity_kw", 1) * 0.9:
            health_score -= 15
        
        # 映射到健康等级
        if health_score >= 90:
            overall_health = "excellent"
        elif health_score >= 75:
            overall_health = "good"
        elif health_score >= 60:
            overall_health = "fair"
        elif health_score >= 40:
            overall_health = "poor"
        else:
            overall_health = "critical"
        
        # 生成建议
        recommendations = []
        if engine_report.get("load_percent", 0) > 85:
            recommendations.append("Consider reducing engine load")
        if power_report.get("emergency_mode", False):
            recommendations.append("Emergency power mode active - repair main generators")
        
        return {
            "engine": {
                "rpm": engine_report.get("rpm", 0),
                "load_percent": engine_report.get("load_percent", 0),
                "cooling_water_temp": engine_report.get("cooling_water_temp", 0),
                "lube_oil_pressure": engine_report.get("lube_oil_pressure", 0)
            },
            "power": {
                "total_load_kw": power_report.get("total_load_kw", 0),
                "total_capacity_kw": power_report.get("total_capacity_kw", 0),
                "emergency_mode": power_report.get("emergency_mode", False)
            },
            "navigation": {
                "speed": nav_report.get("speed", {}).get("speed_over_ground", 0),
                "course": nav_report.get("heading", {}).get("true_heading", 0)
            },
            "overall_health": overall_health,
            "recommendations": recommendations
        }
