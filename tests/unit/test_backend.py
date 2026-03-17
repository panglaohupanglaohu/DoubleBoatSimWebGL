#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DoubleBoatClawSystem 单元测试 - 后端模块
"""

import pytest
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from backend.main import (
    SensorData,
    AISTarget,
    EngineStatus,
    Alarm,
    SimulationEngine,
)


class TestSensorData:
    """传感器数据模型测试"""

    def test_create_sensor_data(self):
        """测试创建传感器数据"""
        sensor = SensorData(
            sensor_id="GPS-001",
            sensor_type="GPS",
            value=31.2304,
            unit="deg",
            timestamp="2026-03-13T18:00:00",
            quality="good"
        )
        assert sensor.sensor_id == "GPS-001"
        assert sensor.sensor_type == "GPS"
        assert sensor.value == 31.2304
        assert sensor.unit == "deg"
        assert sensor.quality == "good"

    def test_sensor_data_default_quality(self):
        """测试默认质量参数"""
        sensor = SensorData(
            sensor_id="TEST-001",
            sensor_type="TEST",
            value=100.0,
            unit="units",
            timestamp="2026-03-13T18:00:00"
        )
        assert sensor.quality == "good"


class TestAISTarget:
    """AIS 目标模型测试"""

    def test_create_ais_target(self):
        """测试创建 AIS 目标"""
        target = AISTarget(
            mmsi="123456789",
            latitude=31.2304,
            longitude=121.4737,
            course=135.0,
            speed=12.3,
            heading=135.0,
            vessel_type="Cargo"
        )
        assert target.mmsi == "123456789"
        assert target.latitude == 31.2304
        assert target.course == 135.0
        assert target.speed == 12.3

    def test_ais_target_with_cpa_tcpa(self):
        """测试带 CPA/TCPA 的 AIS 目标"""
        target = AISTarget(
            mmsi="987654321",
            latitude=31.25,
            longitude=121.50,
            course=225.0,
            speed=10.0,
            heading=225.0,
            vessel_type="Tanker",
            cpa=0.5,
            tcpa=300.0
        )
        assert target.cpa == 0.5
        assert target.tcpa == 300.0


class TestEngineStatus:
    """主机状态模型测试"""

    def test_create_engine_status(self):
        """测试创建主机状态"""
        status = EngineStatus(
            engine_id="ENG-001",
            rpm=120.0,
            load=75.0,
            cooling_water_temp=82.0,
            lube_oil_pressure=4.5,
            fuel_consumption=180.0,
            status="running"
        )
        assert status.engine_id == "ENG-001"
        assert status.rpm == 120.0
        assert status.load == 75.0
        assert status.status == "running"

    def test_engine_status_empty_alarms(self):
        """测试空报警列表"""
        status = EngineStatus(
            engine_id="ENG-001",
            rpm=120.0,
            load=75.0,
            cooling_water_temp=82.0,
            lube_oil_pressure=4.5,
            fuel_consumption=180.0,
            status="running"
        )
        assert status.alarms == []


class TestAlarm:
    """报警模型测试"""

    def test_create_alarm(self):
        """测试创建报警"""
        alarm = Alarm(
            alarm_id="ALM-001",
            level="WARNING",
            source="ENGINE",
            message="Cooling water temperature high",
            timestamp="2026-03-13T18:00:00"
        )
        assert alarm.alarm_id == "ALM-001"
        assert alarm.level == "WARNING"
        assert alarm.source == "ENGINE"
        assert alarm.acknowledged == False

    def test_alarm_acknowledged(self):
        """测试报警确认"""
        alarm = Alarm(
            alarm_id="ALM-002",
            level="CRITICAL",
            source="ENGINE",
            message="Lube oil pressure low",
            timestamp="2026-03-13T18:00:00",
            acknowledged=True
        )
        assert alarm.acknowledged == True


class TestSimulationEngine:
    """仿真引擎测试"""

    def test_create_simulation_engine(self):
        """测试创建仿真引擎"""
        engine = SimulationEngine()
        assert engine.running == False
        assert engine.ship_position["lat"] == 31.2304
        assert engine.ship_position["lon"] == 121.4737
        assert len(engine.ais_targets) == 5

    def test_engine_start_stop(self):
        """测试引擎启动停止"""
        engine = SimulationEngine()
        engine.start()
        assert engine.running == True
        
        engine.stop()
        assert engine.running == False

    def test_engine_initial_state(self):
        """测试引擎初始状态"""
        engine = SimulationEngine()
        assert engine.engine["rpm"] == 120.0
        assert engine.engine["load"] == 75.0
        assert engine.engine["cooling_water_temp"] == 82.0


class TestDataValidation:
    """数据验证测试"""

    def test_sensor_data_value_range(self):
        """测试传感器数据值范围"""
        # GPS 纬度应在 -90 到 90 之间
        sensor = SensorData(
            sensor_id="GPS-001",
            sensor_type="GPS",
            value=31.2304,
            unit="deg",
            timestamp="2026-03-13T18:00:00"
        )
        assert -90 <= sensor.value <= 90

    def test_engine_rpm_range(self):
        """测试主机 RPM 范围"""
        status = EngineStatus(
            engine_id="ENG-001",
            rpm=120.0,
            load=75.0,
            cooling_water_temp=82.0,
            lube_oil_pressure=4.5,
            fuel_consumption=180.0,
            status="running"
        )
        assert status.rpm >= 0
        assert status.rpm <= 200  # 假设最大 RPM 为 200

    def test_engine_temperature_range(self):
        """测试主机温度范围"""
        status = EngineStatus(
            engine_id="ENG-001",
            rpm=120.0,
            load=75.0,
            cooling_water_temp=82.0,
            lube_oil_pressure=4.5,
            fuel_consumption=180.0,
            status="running"
        )
        # 正常工作温度应在 70-95°C 之间
        assert 70 <= status.cooling_water_temp <= 95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
