# -*- coding: utf-8 -*-
"""
Channel 注册脚本 - 注册所有可用的 Marine Channels
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from channels.marine_base import get_default_registry, register_channel
from channels.energy_efficiency_manager import (
    EnergyEfficiencyChannel,
    VesselInfo,
    VesselType,
    FuelType,
)
from channels.intelligent_navigation import (
    IntelligentNavigationChannel,
    AISTarget,
)
from channels.intelligent_engine import IntelligentEngineChannel
from channels.compliance_digital_expert import ComplianceDigitalExpertChannel
from channels.distributed_perception_hub import DistributedPerceptionHubChannel
from channels.decision_orchestrator import DecisionOrchestratorChannel
from channels.rcs_control import RCSControlChannel
from channels.structural_health_monitor import StructuralHealthMonitorChannel
from datetime import datetime


def register_energy_efficiency_channel():
    """注册能效管理 Channel."""
    vessel = VesselInfo(
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
    
    channel = EnergyEfficiencyChannel(config={"vessel": vessel})
    result = register_channel(channel)
    
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
        status = channel.get_status()
        print(f"   状态：{status['health']}")
        print(f"   船舶：{status.get('vessel', {}).get('name', 'N/A')}")
    else:
        print(f"❌ 注册失败：{channel.name}")
    
    return channel


def register_intelligent_navigation():
    """注册智能导航 Channel."""
    channel = IntelligentNavigationChannel(config={
        "dcpa_limit": 0.5,
        "tcpa_limit": 30.0
    })
    
    result = register_channel(channel)
    
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
        status = channel.get_status()
        print(f"   状态：{status['health']}")
        print(f"   描述：{status.get('health_message', 'N/A')}")
        
        # 添加一些测试 AIS 目标
        test_targets = [
            AISTarget(mmsi=413000001, latitude=31.25, longitude=122.5, course=180, speed=12, heading=180),
            AISTarget(mmsi=413000002, latitude=31.3, longitude=122.6, course=270, speed=8, heading=270),
            AISTarget(mmsi=413000003, latitude=31.2, longitude=122.4, course=90, speed=15, heading=90),
        ]
        
        # 更新本船位置
        channel.update_own_ship(
            latitude=31.2304,
            longitude=121.4737,
            course=45,
            speed=10
        )
        
        for target in test_targets:
            channel.add_ais_target(target)
        
        # 计算碰撞风险
        risks = channel.get_collision_risks()
        print(f"   AIS 目标：{len(test_targets)} 个")
        print(f"   碰撞风险：{len(risks)} 个")
    else:
        print(f"❌ 注册失败：{channel.name}")
    
    return channel


def register_intelligent_engine():
    """注册智能机舱 Channel."""
    channel = IntelligentEngineChannel(config={"max_snapshots": 120})
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
        status = channel.get_status()
        print(f"   状态：{status['health']}")
        print(f"   健康度：{status.get('engine_health_score', 'N/A')}")
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_compliance_digital_expert():
    """注册船舶合规数字专家 Channel."""
    channel = ComplianceDigitalExpertChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_distributed_perception_hub():
    """注册分布式感知网络 Channel."""
    channel = DistributedPerceptionHubChannel(config={"max_events": 500})
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_decision_orchestrator():
    """注册全场景决策编排 Channel."""
    channel = DecisionOrchestratorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_rcs_control():
    """注册 RCS 姿态控制 Channel."""
    channel = RCSControlChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_structural_health_monitor():
    """注册 SHM Channel."""
    channel = StructuralHealthMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def list_registered_channels():
    """列出所有已注册的 Channel."""
    registry = get_default_registry()
    channels = registry.list_channels()
    
    print(f"\n📋 已注册 Channel 列表 ({len(channels)} 个):")
    for name in channels:
        channel = registry.get(name)
        if channel:
            status = channel.get_status()
            print(f"  - {name}: {status.get('health', 'unknown')}")


if __name__ == "__main__":
    print("🔧 开始注册 Marine Channels...")
    register_energy_efficiency_channel()
    register_intelligent_navigation()
    register_intelligent_engine()
    register_compliance_digital_expert()
    register_distributed_perception_hub()
    register_decision_orchestrator()
    register_rcs_control()
    register_structural_health_monitor()
    list_registered_channels()
    print("\n✅ Channel 注册完成")
