# -*- coding: utf-8 -*-
"""
Integration Test: Cargo Monitoring

测试场景：货物监控联合仿真
- Cargo Monitor Channel (货物监控)
- Weather Routing Channel (气象导航)

验证:
1. 冷藏箱温度监控
2. 液货舱液位/压力监控
3. 通风控制优化
4. 货物安全评估
"""

import pytest
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'marine_engineer_agent'))

from skills.channels.cargo_monitor import CargoMonitorChannel, CargoType, AlarmLevel
from skills.channels.weather_routing import WeatherRoutingChannel


class TestCargoMonitoringIntegration:
    """货物监控集成测试"""
    
    @pytest.fixture
    def cargo_channel(self):
        """初始化货物监控 Channel"""
        return CargoMonitorChannel()
    
    @pytest.fixture
    def weather_channel(self):
        """初始化气象导航 Channel"""
        return WeatherRoutingChannel()
    
    def test_reefer_container_monitoring(self, cargo_channel):
        """测试冷藏集装箱监控"""
        # 注册多个冷藏箱
        containers = [
            {"id": "MSKU123456", "setpoint": -18.0, "temp": -17.5, "humidity": 55.0},
            {"id": "TGHU789012", "setpoint": 2.0, "temp": 3.5, "humidity": 85.0},
            {"id": "HLXU345678", "setpoint": -25.0, "temp": -24.0, "humidity": 50.0},
        ]
        
        for container in containers:
            cargo_channel.register_reefer_container(
                container_id=container["id"],
                setpoint_c=container["setpoint"],
                current_temp_c=container["temp"],
                humidity_percent=container["humidity"],
                status="running"
            )
        
        # 更新温度
        cargo_channel.update_reefer_temperature("MSKU123456", -15.0)  # 温度上升
        
        # 获取状态报告
        report = cargo_channel.get_status_report()
        
        # 验证报告
        assert report["reefer_containers"]["count"] == 3
        assert report["reefer_containers"]["alarms"] >= 0
        
        # 验证温度偏差检测
        alarms = cargo_channel.get_active_alarms()
        temp_alarms = [a for a in alarms if "temperature" in a.message.lower()]
        assert len(temp_alarms) > 0  # 温度偏差应触发报警
    
    def test_cargo_tank_monitoring(self, cargo_channel):
        """测试液货舱监控"""
        # 注册液货舱
        cargo_channel.register_cargo_tank(
            tank_id="TANK-1",
            tank_name="No.1 Cargo Oil Tank",
            cargo_type=CargoType.LIQUID_BULK,
            capacity_m3=10000,
            current_level_percent=85.0,
            temperature_c=25.0,
            pressure_bar=0.2
        )
        
        cargo_channel.register_cargo_tank(
            tank_id="TANK-2",
            tank_name="No.2 Cargo Oil Tank",
            cargo_type=CargoType.LIQUID_BULK,
            capacity_m3=10000,
            current_level_percent=50.0,
            temperature_c=28.0,
            pressure_bar=0.15
        )
        
        # 更新液位
        cargo_channel.update_tank_level("TANK-1", level_m=9.0, level_percent=90.0)
        
        # 更新压力
        cargo_channel.update_tank_pressure("TANK-1", pressure_bar=0.6)  # 高压
        
        # 获取状态
        report = cargo_channel.get_status_report()
        
        # 验证报告
        assert report["cargo_tanks"]["count"] == 2
        assert report["cargo_tanks"]["total_volume_m3"] > 0
        
        # 验证高压报警
        alarms = cargo_channel.get_active_alarms()
        pressure_alarms = [a for a in alarms if "pressure" in a.message.lower()]
        assert len(pressure_alarms) > 0
    
    def test_ventilation_control(self, cargo_channel, weather_channel):
        """测试通风控制优化"""
        # 注册通风状态
        cargo_channel.register_ventilation(
            cargo_hold_id="HOLD-1",
            fan_running=True,
            ventilation_rate_m3h=5000,
            inlet_temp_c=20.0,
            outlet_temp_c=25.0,
            inlet_humidity_percent=60.0,
            outlet_humidity_percent=75.0,
            dew_point_c=18.0
        )
        
        # 设置外界气象条件
        weather_channel.update_conditions(
            temp=22.0,
            humidity=80.0,
            wind_speed=10.0
        )
        
        # 获取通风建议
        recommendation = cargo_channel.get_ventilation_recommendation("HOLD-1")
        
        # 验证建议
        assert recommendation is not None
        assert "recommendation" in recommendation
        assert "condensation_risk" in recommendation
        
        # 验证建议类型
        assert recommendation["recommendation"] in ["start", "stop", "maintain"]
    
    def test_cargo_safety_assessment(self, cargo_channel):
        """测试货物安全评估"""
        # 注册冷藏箱
        cargo_channel.register_reefer_container(
            container_id="MSKU123456",
            setpoint_c=-18.0,
            current_temp_c=-12.0,  # 温度严重偏差
            humidity_percent=90.0,  # 高湿度
            status="alarm"
        )
        
        # 注册液货舱
        cargo_channel.register_cargo_tank(
            tank_id="TANK-1",
            tank_name="No.1 Cargo Tank",
            cargo_type=CargoType.LIQUID_BULK,
            capacity_m3=10000,
            current_level_percent=96.0,  # 高液位
            temperature_c=30.0,
            pressure_bar=0.8  # 高压
        )
        
        # 获取安全评估
        safety_report = cargo_channel.get_safety_assessment()
        
        # 验证评估结果
        assert safety_report is not None
        assert "overall_status" in safety_report
        assert "critical_issues" in safety_report
        assert "recommendations" in safety_report
        
        # 验证安全等级
        assert safety_report["overall_status"] in ["safe", "caution", "warning", "critical"]
        
        # 应该检测到多个问题
        assert len(safety_report["critical_issues"]) > 0
    
    def test_temperature_trend_analysis(self, cargo_channel):
        """测试温度趋势分析"""
        # 注册冷藏箱
        cargo_channel.register_reefer_container(
            container_id="MSKU123456",
            setpoint_c=-18.0,
            current_temp_c=-18.0,
            humidity_percent=55.0,
            status="running"
        )
        
        # 模拟温度变化序列
        temperatures = [-18.0, -17.8, -17.5, -17.2, -17.0, -16.5, -16.0]
        for temp in temperatures:
            cargo_channel.update_reefer_temperature("MSKU123456", temp)
        
        # 获取趋势分析
        trend = cargo_channel.get_temperature_trend("MSKU123456")
        
        # 验证趋势
        assert trend is not None
        assert "trend" in trend
        assert "rate_of_change" in trend
        
        # 温度应该呈上升趋势
        assert trend["trend"] in ["rising", "stable", "falling"]
    
    def test_multi_cargo_type_support(self, cargo_channel):
        """测试多货物类型支持"""
        # 注册不同类型货物
        cargo_channel.register_reefer_container(
            container_id="REEFER-1",
            setpoint_c=-18.0,
            current_temp_c=-17.5,
            humidity_percent=55.0,
            status="running"
        )
        
        cargo_channel.register_cargo_tank(
            tank_id="TANK-LNG",
            tank_name="LNG Tank",
            cargo_type=CargoType.GAS_CARGO,
            capacity_m3=50000,
            current_level_percent=70.0,
            temperature_c=-162.0,  # LNG 低温
            pressure_bar=0.1
        )
        
        cargo_channel.register_cargo_tank(
            tank_id="TANK-CHEM",
            tank_name="Chemical Tank",
            cargo_type=CargoType.LIQUID_BULK,
            capacity_m3=5000,
            current_level_percent=60.0,
            temperature_c=35.0,
            pressure_bar=0.2
        )
        
        # 获取综合报告
        report = cargo_channel.get_status_report()
        
        # 验证多货物类型
        assert report["reefer_containers"]["count"] == 1
        assert report["cargo_tanks"]["count"] == 2
        
        # 验证特殊货物监控
        lng_tank = cargo_channel.get_tank_status("TANK-LNG")
        assert lng_tank["temperature_c"] == -162.0  # 超低温
    
    def test_alarm_management_workflow(self, cargo_channel):
        """测试报警管理工作流程"""
        # 注册冷藏箱并触发报警
        cargo_channel.register_reefer_container(
            container_id="MSKU123456",
            setpoint_c=-18.0,
            current_temp_c=-10.0,  # 严重温度偏差
            humidity_percent=95.0,  # 高湿度
            status="alarm"
        )
        
        # 获取初始报警
        initial_alarms = cargo_channel.get_active_alarms()
        assert len(initial_alarms) > 0
        
        # 确认报警
        for alarm in initial_alarms:
            cargo_channel.acknowledge_alarm(alarm.alarm_id)
        
        # 验证报警已确认
        acknowledged_alarms = cargo_channel.get_acknowledged_alarms()
        assert len(acknowledged_alarms) == len(initial_alarms)
        
        # 清除报警
        for alarm in initial_alarms:
            cargo_channel.clear_alarm(alarm.alarm_id)
        
        # 验证报警已清除
        final_alarms = cargo_channel.get_active_alarms()
        assert len(final_alarms) == 0
    
    def test_comprehensive_cargo_report(self, cargo_channel, weather_channel):
        """测试综合货物报告"""
        # 设置完整货物配置
        # 冷藏箱
        for i in range(5):
            cargo_channel.register_reefer_container(
                container_id=f"REEFER-{i:03d}",
                setpoint_c=-18.0 if i % 2 == 0 else 2.0,
                current_temp_c=-17.5 if i % 2 == 0 else 3.0,
                humidity_percent=55.0 if i % 2 == 0 else 85.0,
                status="running"
            )
        
        # 液货舱
        for i in range(3):
            cargo_channel.register_cargo_tank(
                tank_id=f"TANK-{i:03d}",
                tank_name=f"Tank {i}",
                cargo_type=CargoType.LIQUID_BULK if i < 2 else CargoType.GAS_CARGO,
                capacity_m3=10000,
                current_level_percent=70.0 + i * 5,
                temperature_c=25.0 + i,
                pressure_bar=0.2 + i * 0.1
            )
        
        # 通风系统
        for i in range(2):
            cargo_channel.register_ventilation(
                cargo_hold_id=f"HOLD-{i:03d}",
                fan_running=True,
                ventilation_rate_m3h=5000,
                inlet_temp_c=20.0 + i,
                outlet_temp_c=25.0 + i,
                inlet_humidity_percent=60.0 + i * 5,
                outlet_humidity_percent=70.0 + i * 5,
                dew_point_c=18.0 + i
            )
        
        # 设置气象条件
        weather_channel.update_conditions(
            temp=25.0,
            humidity=75.0,
            wind_speed=12.0
        )
        
        # 生成综合报告
        report = self.generate_cargo_report(cargo_channel, weather_channel)
        
        # 验证报告结构
        assert "summary" in report
        assert "reefer_containers" in report
        assert "cargo_tanks" in report
        assert "ventilation" in report
        assert "weather_impact" in report
        assert "safety_status" in report
        assert "recommendations" in report
        
        # 验证数据准确性
        assert report["summary"]["total_reefers"] == 5
        assert report["summary"]["total_tanks"] == 3
        assert report["summary"]["active_alarms"] >= 0
    
    def generate_cargo_report(self, cargo, weather) -> dict:
        """生成综合货物报告 (辅助方法)"""
        cargo_report = cargo.get_status_report()
        weather_report = weather.get_weather_report()
        
        # 计算安全状态
        safety_status = "safe"
        if cargo_report["alarms"]["active"] > 0:
            safety_status = "caution"
        if cargo_report["alarms"]["critical"] > 0:
            safety_status = "warning"
        
        # 气象影响评估
        weather_impact = "minimal"
        if weather_report.get("severity") in ["rough", "severe"]:
            weather_impact = "moderate"
        if weather_report.get("severity") in ["extreme"]:
            weather_impact = "significant"
        
        # 生成建议
        recommendations = []
        if cargo_report["reefer_containers"]["alarms"] > 0:
            recommendations.append("Check reefer containers with temperature alarms")
        if cargo_report["cargo_tanks"]["high_level_count"] > 0:
            recommendations.append("Monitor high-level cargo tanks")
        if weather_impact != "minimal":
            recommendations.append("Consider weather impact on cargo operations")
        
        return {
            "summary": {
                "total_reefers": cargo_report["reefer_containers"]["count"],
                "total_tanks": cargo_report["cargo_tanks"]["count"],
                "active_alarms": cargo_report["alarms"]["active"],
                "critical_alarms": cargo_report["alarms"]["critical"]
            },
            "reefer_containers": cargo_report["reefer_containers"],
            "cargo_tanks": cargo_report["cargo_tanks"],
            "ventilation": cargo_report.get("ventilation", {}),
            "weather_impact": weather_impact,
            "safety_status": safety_status,
            "recommendations": recommendations
        }
