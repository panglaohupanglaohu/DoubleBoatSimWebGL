# -*- coding: utf-8 -*-
"""
测试 EnergyEfficiencyChannel - IMO 能效管理 Channel.

验证 Channel 集成到 DoubleBoatClawSystem 的功能完整性。
"""

import sys
import os
# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from datetime import datetime
from backend.channels.energy_efficiency_manager import (
    EnergyEfficiencyChannel,
    VesselInfo,
    VesselType,
    FuelType,
    VoyageData,
)
from backend.channels.marine_base import ChannelStatus, ChannelPriority


class TestEnergyEfficiencyChannel:
    """EnergyEfficiencyChannel 测试用例."""
    
    @pytest.fixture
    def sample_vessel(self) -> VesselInfo:
        """创建测试船舶配置."""
        return VesselInfo(
            imo_number=9876543,
            vessel_name="Ocean Pioneer",
            vessel_type=VesselType.BULK_CARRIER,
            dwt=82000,
            gross_tonnage=43500,
            length=229,
            beam=32,
            draft=14.5,
            main_engine_power=14280,
            fuel_type=FuelType.HFO,
            built_year=2015
        )
    
    @pytest.fixture
    def channel(self, sample_vessel) -> EnergyEfficiencyChannel:
        """创建能效 Channel 实例."""
        return EnergyEfficiencyChannel(config={"vessel": sample_vessel})
    
    def test_channel_initialization(self, channel):
        """测试 Channel 初始化."""
        assert channel.name == "energy_efficiency"
        assert channel.description == "船舶能效管理 (EEXI/CII/SEEMP)"
        assert channel.version == "1.0.0"
        assert channel.priority == ChannelPriority.P0
        assert channel._initialized is False
    
    def test_channel_initialize(self, channel):
        """测试 Channel 初始化方法."""
        result = channel.initialize()
        assert result is True
        assert channel._initialized is True
        assert channel._health.status == ChannelStatus.OK
    
    def test_channel_get_status(self, channel):
        """测试获取 Channel 状态."""
        channel.initialize()
        status = channel.get_status()
        
        assert status["name"] == "energy_efficiency"
        assert status["version"] == "1.0.0"
        assert status["initialized"] is True
        assert status["health"] == "ok"
        assert "vessel" in status
        assert status["vessel"]["name"] == "Ocean Pioneer"
        assert status["vessel"]["imo"] == 9876543
    
    def test_channel_shutdown(self, channel):
        """测试 Channel 关闭."""
        channel.initialize()
        result = channel.shutdown()
        
        assert result is True
        assert channel._initialized is False
        assert channel._health.status == ChannelStatus.OFF
    
    def test_channel_check(self, channel):
        """测试 Channel 检查方法."""
        # 未初始化
        status, message = channel.check()
        assert status == "off"
        
        # 初始化后
        channel.initialize()
        status, message = channel.check()
        assert status == "ok"
    
    def test_eexi_calculation(self, channel):
        """测试 EEXI 计算."""
        channel.initialize()
        
        result = channel.calculate_eexi(
            installed_power=10000,
            sfc=170
        )
        
        assert result.attained_eexi > 0
        assert result.reference_line > 0
        assert hasattr(result, 'compliance_status')
    
    def test_cii_calculation(self, channel):
        """测试 CII 计算."""
        channel.initialize()
        
        result = channel.calculate_cii(
            total_fuel=15000000,  # kg
            total_distance=45000,  # nm
            year=2026
        )
        
        assert result.attained_cii > 0
        assert result.required_cii > 0
        assert hasattr(result, 'rating')
    
    def test_voyage_data_class(self):
        """测试 VoyageData 数据类."""
        voyage = VoyageData(
            voyage_id="V001",
            departure_port="Shanghai",
            arrival_port="Los Angeles",
            departure_time=datetime(2026, 1, 1, 0, 0),
            arrival_time=datetime(2026, 1, 15, 12, 0),
            distance_nm=5500,
            fuel_consumed=850000,
            fuel_type=FuelType.HFO,
            cargo_weight=75000
        )
        
        assert voyage.voyage_id == "V001"
        assert voyage.distance_nm == 5500
        assert voyage.fuel_consumed == 850000
    
    def test_recommendations(self, channel):
        """测试能效建议生成."""
        channel.initialize()
        
        recommendations = channel.get_recommendations()
        assert isinstance(recommendations, list)
    
    def test_compliance_report(self, channel):
        """测试合规报告生成."""
        channel.initialize()
        
        # 创建测试航次数据
        voyage = VoyageData(
            voyage_id="V001",
            departure_port="Shanghai",
            arrival_port="Los Angeles",
            departure_time=datetime(2026, 1, 1, 0, 0),
            arrival_time=datetime(2026, 1, 15, 12, 0),
            distance_nm=5500,
            fuel_consumed=850000,
            fuel_type=FuelType.HFO,
            cargo_weight=75000
        )
        
        report = channel.generate_compliance_report(year=2026, voyages=[voyage])
        assert report is not None
    
    def test_channel_health(self, channel):
        """测试 Channel 健康状态追踪."""
        channel.initialize()
        
        health = channel.get_health()
        assert health.status == ChannelStatus.OK
        assert "Ocean Pioneer" in health.message


class TestEnergyEfficiencyChannelRegistry:
    """测试 Channel 注册表集成."""
    
    @pytest.fixture
    def sample_vessel(self) -> VesselInfo:
        """创建测试船舶配置."""
        return VesselInfo(
            imo_number=9876543,
            vessel_name="Ocean Pioneer",
            vessel_type=VesselType.BULK_CARRIER,
            dwt=82000,
            gross_tonnage=43500,
            length=229,
            beam=32,
            draft=14.5,
            main_engine_power=14280,
            fuel_type=FuelType.HFO,
            built_year=2015
        )
    
    def test_channel_registration(self, sample_vessel):
        """测试 Channel 注册到默认注册表."""
        from backend.channels.marine_base import (
            get_default_registry,
            register_channel,
            get_channel,
        )
        
        channel = EnergyEfficiencyChannel(config={"vessel": sample_vessel})
        result = register_channel(channel)
        
        assert result is True
        
        # 从注册表获取
        retrieved = get_channel("energy_efficiency")
        assert retrieved is not None
        assert retrieved.name == "energy_efficiency"
    
    def test_registry_list_channels(self, sample_vessel):
        """测试注册表列出所有 Channel."""
        from backend.channels.marine_base import get_default_registry
        
        registry = get_default_registry()
        channels = registry.list_channels()
        
        assert "energy_efficiency" in channels


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
