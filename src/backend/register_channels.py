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
from channels.ship_shore_link import ShipShoreLinkChannel
from channels.autonomy_manager import AutonomyManagerChannel
from channels.predictive_health import PredictiveHealthChannel
from channels.route_optimizer import RouteOptimizerChannel
from channels.voyage_planner import VoyagePlannerChannel
from channels.cyber_security import CyberSecurityChannel
from channels.deterministic_network import DeterministicNetworkChannel
from channels.nats_event_bus import NATSEventBusChannel
from channels.colregs_brain import COLREGsAutonomousBrainChannel
from channels.wpc_attitude_control import WPCAttitudeControlChannel
from channels.openbridge_hmi import OpenBridgeHMIChannel
from channels.build_team_manager import BuildTeamManagerChannel
from channels.execution_team_manager import ExecutionTeamManagerChannel
from channels.system_evolution import SystemEvolutionChannel
from channels.weather_routing_channel import WeatherRoutingChannel
from channels.crew_fatigue_monitor import CrewFatigueMonitorChannel
from channels.ballast_water_monitor import BallastWaterMonitorChannel
from channels.emission_monitor import EmissionMonitorChannel
from channels.anchor_watch_channel import AnchorWatchChannel
from channels.cargo_monitor import CargoMonitorChannel
from channels.fire_detection_channel import FireDetectionChannel
from channels.vdr_recorder import VDRRecorderChannel
from channels.dynamic_positioning import DynamicPositioningChannel
from channels.ais_processor import AISProcessorChannel
from channels.hull_stress_monitor import HullStressMonitorChannel
from channels.power_management import PowerManagementChannel
from channels.bilge_water_monitor import BilgeWaterMonitorChannel
from channels.communication_manager import CommunicationManagerChannel
from channels.gyro_compass_monitor import GyroCompassMonitorChannel
from channels.speed_log_monitor import SpeedLogMonitorChannel
from channels.rudder_control_monitor import RudderControlMonitorChannel
from channels.tank_level_monitor import TankLevelMonitorChannel
from channels.alarm_management import AlarmManagementChannel
from channels.autopilot_monitor import AutopilotMonitorChannel
from channels.echo_sounder_monitor import EchoSounderMonitorChannel
from channels.propulsion_monitor import PropulsionMonitorChannel
from channels.mooring_monitor import MooringMonitorChannel
from channels.man_overboard import ManOverboardChannel
from channels.safety_system_monitor import SafetySystemMonitorChannel
from channels.lrit_reporter import LRITReporterChannel
from channels.navigational_lights import NavigationalLightsChannel
from channels.voyage_data_analyzer import VoyageDataAnalyzerChannel
from channels.maintenance_planner import MaintenancePlannerChannel
from channels.bridge_chat import BridgeChatChannel
from channels.cargo_orbit_telemetry import CargoOrbitTelemetryChannel
from datetime import datetime
from channels.agent_set_protocol import create_coordination_bus
from channels.agent_set_coordinator import AgentSetCoordinator
from channels.shore_supervision_set import ShoreSupervisionSet
from channels.shipboard_execution_set import ShipboardExecutionSet


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


def register_ship_shore_link():
    """注册船岸通信链路管理 Channel."""
    channel = ShipShoreLinkChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
        status = channel.get_status()
        print(f"   状态：{status['health']}")
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_autonomy_manager():
    """注册自主等级管理 Channel."""
    channel = AutonomyManagerChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
        status = channel.get_status()
        print(f"   状态：{status['health']}")
        print(f"   MASS等级：{status.get('mass_level', 'N/A')}")
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_predictive_health():
    """注册预测性健康管理 Channel."""
    channel = PredictiveHealthChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
        status = channel.get_status()
        print(f"   状态：{status['health']}")
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_route_optimizer():
    """注册航线优化 Channel."""
    channel = RouteOptimizerChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
        status = channel.get_status()
        print(f"   状态：{status['health']}")
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_voyage_planner():
    """注册航次计划管理 Channel."""
    channel = VoyagePlannerChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
        status = channel.get_status()
        print(f"   状态：{status['health']}")
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_cyber_security():
    """注册网络安全管理 Channel."""
    channel = CyberSecurityChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
        status = channel.get_status()
        print(f"   威胁等级：{status.get('threat_level', 'N/A')}")
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_deterministic_network():
    """注册 L0 确定性网络 Channel."""
    channel = DeterministicNetworkChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_nats_event_bus():
    """注册 L1 NATS 事件总线 Channel."""
    channel = NATSEventBusChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_colregs_brain():
    """注册 L3 COLREGs 自主大脑 Channel."""
    channel = COLREGsAutonomousBrainChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_wpc_attitude_control():
    """注册 L4 穿浪双体船姿态控制 Channel."""
    channel = WPCAttitudeControlChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_openbridge_hmi():
    """注册 L5 OpenBridge HMI Channel."""
    channel = OpenBridgeHMIChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_build_team_manager():
    """注册构建智能体团队管理器 Channel."""
    channel = BuildTeamManagerChannel(config={"llm_backend": "copilot"})
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_execution_team_manager():
    """注册执行智能体团队管理器 Channel."""
    channel = ExecutionTeamManagerChannel(config={"llm_backend": "deepseek"})
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_system_evolution():
    """注册系统自我演进引擎 Channel."""
    channel = SystemEvolutionChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_weather_routing():
    """注册 L3 气象导航 Channel."""
    channel = WeatherRoutingChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_crew_fatigue_monitor():
    """注册 L5 船员疲劳监测 Channel."""
    channel = CrewFatigueMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_ballast_water_monitor():
    """注册 L2 压载水管理监测 Channel."""
    channel = BallastWaterMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_emission_monitor():
    """注册 L2 排放监测 Channel."""
    channel = EmissionMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_anchor_watch():
    """注册 L2 锚泊监控 Channel."""
    channel = AnchorWatchChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_cargo_monitor():
    """注册 L2 货物监控 Channel."""
    channel = CargoMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_fire_detection():
    """注册 L2 火灾探测 Channel."""
    channel = FireDetectionChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_vdr_recorder():
    """注册 L2 VDR 航行数据记录仪 Channel."""
    channel = VDRRecorderChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_dynamic_positioning():
    """注册 L2 动态定位 Channel."""
    channel = DynamicPositioningChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_ais_processor():
    """注册 L2 AIS 处理器 Channel."""
    channel = AISProcessorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_hull_stress_monitor():
    """注册 L2 船体应力监测 Channel."""
    channel = HullStressMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_power_management():
    """注册 L2 电力管理 Channel."""
    channel = PowerManagementChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_bilge_water_monitor():
    """注册 L2 舱底水监测 Channel."""
    channel = BilgeWaterMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_communication_manager():
    """注册 L2 通信管理 Channel."""
    channel = CommunicationManagerChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_gyro_compass_monitor():
    """注册 L2 电罗经监控 Channel."""
    channel = GyroCompassMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_speed_log_monitor():
    """注册 L2 计程仪监控 Channel."""
    channel = SpeedLogMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_rudder_control_monitor():
    """注册 L2 舵机监控 Channel."""
    channel = RudderControlMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_tank_level_monitor():
    """注册 L2 液舱监控 Channel."""
    channel = TankLevelMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_alarm_management():
    """注册 L2 集中告警管理 Channel."""
    channel = AlarmManagementChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_autopilot_monitor():
    """注册 L2 自动舵监控 Channel."""
    channel = AutopilotMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_echo_sounder_monitor():
    """注册 L2 测深仪监控 Channel."""
    channel = EchoSounderMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_propulsion_monitor():
    """注册 L2 推进系统监控 Channel."""
    channel = PropulsionMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_mooring_monitor():
    """注册 L2 系泊监控 Channel."""
    channel = MooringMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_man_overboard():
    """注册 MOB 落水告警 Channel."""
    channel = ManOverboardChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_safety_system_monitor():
    """注册安全系统综合监控 Channel."""
    channel = SafetySystemMonitorChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_lrit_reporter():
    """注册 LRIT 远程追踪报告 Channel."""
    channel = LRITReporterChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_navigational_lights():
    """注册航行灯监控 Channel."""
    channel = NavigationalLightsChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_voyage_data_analyzer():
    """注册航次数据分析 Channel."""
    channel = VoyageDataAnalyzerChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_maintenance_planner():
    """注册维修计划管理 Channel."""
    channel = MaintenancePlannerChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel






def register_bridge_chat():
    """Register Bridge Chat Channel."""
    from channels.marine_base import get_default_registry
    registry = get_default_registry()
    channel_registry = {}
    for ch_name in registry.list_channels():
        ch = registry.get(ch_name)
        if ch:
            channel_registry[ch_name] = ch
    channel = BridgeChatChannel(channel_registry=channel_registry)
    result = register_channel(channel)
    if result:
        print(f"✅ Channel: {channel.name}")
        channel.initialize()
    else:
        print(f"❌ Failed: {channel.name}")
    return channel


def register_visual_presentation():
    """Register the Visual Presentation channel."""
    from channels.visual_presentation import VisualPresentationChannel
    channel = VisualPresentationChannel()
    channel.initialize()
    register_channel(channel)
    print(f"✅ 已注册 Channel: {channel.name}")


def register_agent_sets():
    """Create and register the dual agent-set topology.

    Must be called AFTER all individual channels are registered.
    Returns the AgentSetCoordinator instance.
    """
    registry = get_default_registry()

    bus = create_coordination_bus(max_size=4096)

    shore = ShoreSupervisionSet(coordination_bus=bus)
    for ch_name in shore.member_channel_names:
        ch = registry.get(ch_name)
        if ch:
            shore.add_channel(ch)

    orchestrator = registry.get("decision_orchestrator")
    ship = ShipboardExecutionSet(
        coordination_bus=bus,
        decision_orchestrator=orchestrator,
    )
    for ch_name in ship.member_channel_names:
        ch = registry.get(ch_name)
        if ch:
            ship.add_channel(ch)


    # Add visual_presentation to ship set
    vp = registry.get("visual_presentation")
    if vp:
        ship.add_channel(vp)

    coordinator = AgentSetCoordinator(
        shore_set=shore,
        ship_set=ship,
        bus=bus,
    )

    register_channel(shore)
    shore.initialize()
    print(f"  Registered: {shore.name} ({len(shore.list_members())} members)")

    register_channel(ship)
    ship.initialize()
    print(f"  Registered: {ship.name} ({len(ship.list_members())} members)")

    register_channel(coordinator)
    coordinator.initialize()
    print(f"  Registered: {coordinator.name}")

    return coordinator


def register_marine_datacenter_energy():
    """注册船载数据中心 AI 能耗管理 Channel."""
    from channels.marine_datacenter_energy import MarineDataCenterEnergyChannel
    channel = MarineDataCenterEnergyChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
        status = channel.get_status()
        print(f"   状态：{status['health']}, PUE: {status['current_pue']} → 目标 {status['target_pue']}")
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_cargo_orbit_telemetry():
    """注册货船轨道遥测上报 Channel."""
    channel = CargoOrbitTelemetryChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
        status = channel.get_status()
        print(f"   状态：{status['health']}")
    else:
        print(f"❌ 注册失败：{channel.name}")
    return channel


def register_aiot_mesh():
    """注册 AIoT Mesh (BIOS + LoRA + MC-RFID + 带外通信) 关联学习 Channel."""
    from channels.aiot_mesh_channel import AIoTMeshChannel
    channel = AIoTMeshChannel()
    result = register_channel(channel)
    if result:
        print(f"✅ 已注册 Channel: {channel.name}")
        channel.initialize()
        status = channel.get_status()
        c = status.get("counts", {})
        print(f"   状态：{status['health']}  BIOS={c.get('bios',0)} "
              f"LoRA={c.get('lora',0)} RFID={c.get('rfid',0)} OOB={c.get('oob_queue',0)}")
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
    register_ship_shore_link()
    register_autonomy_manager()
    register_predictive_health()
    register_route_optimizer()
    register_voyage_planner()
    register_cyber_security()
    register_deterministic_network()
    register_nats_event_bus()
    register_colregs_brain()
    register_wpc_attitude_control()
    register_openbridge_hmi()
    register_build_team_manager()
    register_execution_team_manager()
    register_weather_routing()
    register_crew_fatigue_monitor()
    register_ballast_water_monitor()
    register_emission_monitor()
    register_anchor_watch()
    register_cargo_monitor()
    register_fire_detection()
    register_vdr_recorder()
    register_dynamic_positioning()
    register_ais_processor()
    register_hull_stress_monitor()
    register_power_management()
    register_bilge_water_monitor()
    register_communication_manager()
    register_rudder_control_monitor()
    register_tank_level_monitor()
    register_alarm_management()
    register_autopilot_monitor()
    register_echo_sounder_monitor()
    register_propulsion_monitor()
    register_mooring_monitor()
    register_man_overboard()
    register_safety_system_monitor()
    register_lrit_reporter()
    register_navigational_lights()
    register_voyage_data_analyzer()
    register_maintenance_planner()
    register_bridge_chat()
    register_visual_presentation()
    register_agent_sets()
    register_system_evolution()
    register_marine_datacenter_energy()
    register_cargo_orbit_telemetry()
    register_aiot_mesh()
    list_registered_channels()
    print("\n✅ Channel 注册完成")
