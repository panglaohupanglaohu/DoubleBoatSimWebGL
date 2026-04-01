# -*- coding: utf-8 -*-
"""
深度整合测试 — 编排器 + 导航 + 告警联动

覆盖:
- 编排器 bilge/comms/rudder/tank/alarm 整合 (20+ tests)
- Navigation 增强: add_ais_target 去重, remove_stale_targets, get_closest_targets (15+ tests)
- 告警联动: channel_alarm 事件处理 (10+ tests)
"""

import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from backend.channels.decision_orchestrator import DecisionOrchestratorChannel
from backend.channels.intelligent_navigation import (
    AISTarget,
    IntelligentNavigationChannel,
)
from backend.channels.alarm_management import AlarmManagementChannel
from backend.channels.bilge_water_monitor import BilgeWaterMonitorChannel
from backend.channels.communication_manager import CommunicationManagerChannel
from backend.channels.rudder_control_monitor import RudderControlMonitorChannel
from backend.channels.tank_level_monitor import TankLevelMonitorChannel
from backend.channels.marine_base import get_default_registry, register_channel


# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════

@pytest.fixture()
def orchestrator():
    ch = DecisionOrchestratorChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def nav_channel():
    ch = IntelligentNavigationChannel()
    ch.initialize()
    ch.update_own_ship(latitude=31.0, longitude=121.0, course=90.0, speed=12.0)
    return ch


@pytest.fixture()
def alarm_channel():
    ch = AlarmManagementChannel()
    ch.initialize()
    return ch


def _make_ais(mmsi, lat=31.01, lon=121.01, course=270.0, speed=10.0,
              vessel_type="Cargo", ts=None):
    return AISTarget(
        mmsi=mmsi, latitude=lat, longitude=lon,
        course=course, speed=speed, heading=course,
        vessel_type=vessel_type,
        timestamp=ts or datetime.now(),
    )


def _register_bilge(*, marpol_compliant=True):
    ch = BilgeWaterMonitorChannel()
    ch.initialize()
    if not marpol_compliant:
        ch.update_compartment("ER1", level_percent=90.0, oil_content_ppm=20.0)
        ch._oily_water_separator["operational"] = False
    register_channel(ch)
    return ch


def _register_comms(*, gmdss_compliant=True, distress_active=False):
    ch = CommunicationManagerChannel()
    ch.initialize()
    if gmdss_compliant:
        ch.add_system("VHF1", "vhf")
        ch.add_system("MF1", "mf")
        ch.add_system("SAT1", "inmarsat")
    if distress_active:
        ch.activate_distress({"lat": 31.0, "lon": 121.0})
    register_channel(ch)
    return ch


def _register_rudder(*, solas_compliant=True):
    ch = RudderControlMonitorChannel()
    ch.initialize()
    if solas_compliant:
        ch.update_rudder("R1", angle_deg=0.0, ordered_angle_deg=0.0,
                         response_time_s=5.0)
    else:
        ch.update_rudder("R1", angle_deg=0.0, ordered_angle_deg=0.0,
                         response_time_s=35.0)  # exceeds 28s limit
    register_channel(ch)
    return ch


def _register_tank(*, fuel_low=False):
    ch = TankLevelMonitorChannel()
    ch.initialize()
    if fuel_low:
        ch.update_tank("FO1", "fuel_oil", capacity_m3=100.0, current_m3=10.0)
    else:
        ch.update_tank("FO1", "fuel_oil", capacity_m3=100.0, current_m3=80.0)
    register_channel(ch)
    return ch


def _register_alarm(*, emergency=False):
    ch = AlarmManagementChannel()
    ch.initialize()
    if emergency:
        ch.raise_alarm("EMG-001", "engine", "emergency", "Engine room fire detected")
    register_channel(ch)
    return ch


# ═══════════════════════════════════════════════════════════════
# 1. 编排器深度整合测试 (20+ tests)
# ═══════════════════════════════════════════════════════════════

class TestOrchBilge:
    """Bilge water MARPOL 整合测试。"""

    def test_orch_bilge_marpol_violation(self, orchestrator):
        """bilge 不合规 → marpol_violation_bilge action."""
        _register_bilge(marpol_compliant=False)
        plan = orchestrator._build_action_plan(snapshot={})
        actions = [a for a in plan if a["recommended_action"] == "marpol_violation_bilge"]
        assert len(actions) == 1
        assert actions[0]["domain"] == "compliance"
        assert actions[0]["priority"] == "critical"

    def test_orch_bilge_compliant_no_action(self, orchestrator):
        """bilge 合规 → 无 marpol action."""
        _register_bilge(marpol_compliant=True)
        plan = orchestrator._build_action_plan(snapshot={})
        actions = [a for a in plan if a["recommended_action"] == "marpol_violation_bilge"]
        assert len(actions) == 0


class TestOrchComms:
    """Communication GMDSS / distress 整合测试。"""

    def test_orch_comms_gmdss_noncompliant(self, orchestrator):
        """GMDSS 不合规 → gmdss_non_compliant action."""
        _register_comms(gmdss_compliant=False)
        plan = orchestrator._build_action_plan(snapshot={})
        actions = [a for a in plan if a["recommended_action"] == "gmdss_non_compliant"]
        assert len(actions) == 1
        assert actions[0]["domain"] == "communication"
        assert actions[0]["priority"] == "high"

    def test_orch_comms_distress(self, orchestrator):
        """遇险激活 → distress_active action."""
        _register_comms(gmdss_compliant=True, distress_active=True)
        plan = orchestrator._build_action_plan(snapshot={})
        actions = [a for a in plan if a["recommended_action"] == "distress_active"]
        assert len(actions) == 1
        assert actions[0]["priority"] == "critical"

    def test_orch_comms_normal_no_action(self, orchestrator):
        """通信正常 → 无 comms action."""
        _register_comms(gmdss_compliant=True, distress_active=False)
        plan = orchestrator._build_action_plan(snapshot={})
        comms_actions = [a for a in plan if a["domain"] == "communication"]
        assert len(comms_actions) == 0


class TestOrchRudder:
    """Rudder control SOLAS 整合测试。"""

    def test_orch_rudder_fault(self, orchestrator):
        """舵机不合规 → steering_fault action."""
        _register_rudder(solas_compliant=False)
        plan = orchestrator._build_action_plan(snapshot={})
        actions = [a for a in plan if a["recommended_action"] == "steering_fault"]
        assert len(actions) == 1
        assert actions[0]["domain"] == "steering"
        assert actions[0]["priority"] == "critical"

    def test_orch_rudder_ok_no_action(self, orchestrator):
        """舵机正常 → 无 steering action."""
        _register_rudder(solas_compliant=True)
        plan = orchestrator._build_action_plan(snapshot={})
        actions = [a for a in plan if a["domain"] == "steering"]
        assert len(actions) == 0


class TestOrchTank:
    """Tank fuel level 整合测试。"""

    def test_orch_tank_low_fuel(self, orchestrator):
        """燃油低 → low_fuel_warning action."""
        _register_tank(fuel_low=True)
        plan = orchestrator._build_action_plan(snapshot={})
        actions = [a for a in plan if a["recommended_action"] == "low_fuel_warning"]
        assert len(actions) == 1
        assert actions[0]["domain"] == "fuel"
        assert actions[0]["priority"] == "high"

    def test_orch_tank_normal_no_action(self, orchestrator):
        """燃油正常 → 无 fuel action."""
        _register_tank(fuel_low=False)
        plan = orchestrator._build_action_plan(snapshot={})
        actions = [a for a in plan if a["domain"] == "fuel"]
        assert len(actions) == 0


class TestOrchAlarm:
    """Alarm emergency 整合测试。"""

    def test_orch_alarm_emergency(self, orchestrator):
        """有紧急告警 → emergency_alarm_active action."""
        _register_alarm(emergency=True)
        plan = orchestrator._build_action_plan(snapshot={})
        actions = [a for a in plan if a["recommended_action"] == "emergency_alarm_active"]
        assert len(actions) == 1
        assert actions[0]["domain"] == "alarm"
        assert actions[0]["priority"] == "critical"

    def test_orch_alarm_no_emergency(self, orchestrator):
        """无紧急告警 → 无 alarm action."""
        _register_alarm(emergency=False)
        plan = orchestrator._build_action_plan(snapshot={})
        actions = [a for a in plan if a["domain"] == "alarm"]
        assert len(actions) == 0


class TestOrchCombined:
    """编排器多 Channel 联合测试。"""

    def test_orch_all_channels_triggered(self, orchestrator):
        """所有 Channel 同时告警 → 所有 action 都出现。"""
        _register_bilge(marpol_compliant=False)
        _register_comms(gmdss_compliant=False, distress_active=True)
        _register_rudder(solas_compliant=False)
        _register_tank(fuel_low=True)
        _register_alarm(emergency=True)

        plan = orchestrator._build_action_plan(
            snapshot={},
            weather_risk={"risk_score": 85, "recommendation": "Typhoon approach"},
            crew_fatigue={"fatigue_scores": {"OOW": 20}},
        )
        action_types = {a["recommended_action"] for a in plan}
        assert "marpol_violation_bilge" in action_types
        assert "gmdss_non_compliant" in action_types
        assert "distress_active" in action_types
        assert "steering_fault" in action_types
        assert "low_fuel_warning" in action_types
        assert "emergency_alarm_active" in action_types
        assert "review_route" in action_types
        assert "recommend_watch_change" in action_types

    def test_orch_all_channels_normal(self, orchestrator):
        """所有 Channel 正常 → 无额外 action (只有 baseline monitor)."""
        _register_bilge(marpol_compliant=True)
        _register_comms(gmdss_compliant=True, distress_active=False)
        _register_rudder(solas_compliant=True)
        _register_tank(fuel_low=False)
        _register_alarm(emergency=False)

        plan = orchestrator._build_action_plan(snapshot={})
        # Only the baseline "ops-monitor" action
        assert len(plan) == 1
        assert plan[0]["id"] == "ops-monitor"

    def test_orch_channel_missing_graceful(self, orchestrator):
        """Channel 不存在时优雅降级 — 不崩溃。"""
        # Don't register any channels — registry is empty (reset by conftest)
        plan = orchestrator._build_action_plan(snapshot={})
        assert isinstance(plan, list)
        # Should at least have the baseline monitor action
        assert len(plan) >= 1

    def test_orch_multiple_domain_actions(self, orchestrator):
        """weather + hull + bilge + comms 联合触发。"""
        _register_bilge(marpol_compliant=False)
        _register_comms(gmdss_compliant=False)

        plan = orchestrator._build_action_plan(
            snapshot={},
            weather_risk={"risk_score": 90, "recommendation": "Severe storm"},
        )
        domains = {a["domain"] for a in plan}
        assert "compliance" in domains    # bilge marpol
        assert "communication" in domains  # gmdss
        assert "navigation" in domains     # weather review_route

    def test_orch_action_plan_sorted_by_priority(self, orchestrator):
        """Action plan 应按优先级排序 (critical → high → medium → low)."""
        _register_bilge(marpol_compliant=False)   # critical
        _register_comms(gmdss_compliant=False)     # high
        _register_tank(fuel_low=True)              # high

        plan = orchestrator._build_action_plan(snapshot={})
        priorities = [a["priority"] for a in plan]
        rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        ranks = [rank.get(p, 9) for p in priorities]
        assert ranks == sorted(ranks), f"Plan not sorted by priority: {priorities}"

    def test_orch_bilge_and_alarm_concurrent(self, orchestrator):
        """bilge violation + emergency alarm 同时触发。"""
        _register_bilge(marpol_compliant=False)
        _register_alarm(emergency=True)

        plan = orchestrator._build_action_plan(snapshot={})
        action_types = {a["recommended_action"] for a in plan}
        assert "marpol_violation_bilge" in action_types
        assert "emergency_alarm_active" in action_types

    def test_orch_distress_and_rudder_concurrent(self, orchestrator):
        """distress + rudder fault 同时触发。"""
        _register_comms(gmdss_compliant=True, distress_active=True)
        _register_rudder(solas_compliant=False)

        plan = orchestrator._build_action_plan(snapshot={})
        action_types = {a["recommended_action"] for a in plan}
        assert "distress_active" in action_types
        assert "steering_fault" in action_types

    def test_orch_comms_gmdss_and_distress_both(self, orchestrator):
        """GMDSS 不合规且遇险同时激活 → 两个 action。"""
        _register_comms(gmdss_compliant=False, distress_active=True)
        plan = orchestrator._build_action_plan(snapshot={})
        comms_actions = [a for a in plan if a["domain"] == "communication"]
        assert len(comms_actions) == 2
        action_types = {a["recommended_action"] for a in comms_actions}
        assert "gmdss_non_compliant" in action_types
        assert "distress_active" in action_types

    def test_orch_action_ids_unique(self, orchestrator):
        """所有 action id 唯一。"""
        _register_bilge(marpol_compliant=False)
        _register_comms(gmdss_compliant=False, distress_active=True)
        _register_rudder(solas_compliant=False)
        _register_tank(fuel_low=True)
        _register_alarm(emergency=True)

        plan = orchestrator._build_action_plan(snapshot={})
        ids = [a["id"] for a in plan]
        assert len(ids) == len(set(ids)), f"Duplicate action ids: {ids}"


# ═══════════════════════════════════════════════════════════════
# 2. Navigation 增强测试 (15+ tests)
# ═══════════════════════════════════════════════════════════════

class TestNavAISAddTarget:
    """AIS target add / dedup 测试。"""

    def test_nav_ais_add_new_target(self, nav_channel):
        """添加新目标。"""
        t = _make_ais(mmsi=123456789)
        nav_channel.add_ais_target(t)
        assert len(nav_channel.ais_targets) == 1
        assert nav_channel.ais_targets[0].mmsi == 123456789

    def test_nav_ais_update_by_mmsi(self, nav_channel):
        """MMSI 去重更新 — 同 MMSI 覆盖旧记录。"""
        t1 = _make_ais(mmsi=111000001, lat=31.0, lon=121.0, speed=5.0)
        t2 = _make_ais(mmsi=111000001, lat=31.5, lon=121.5, speed=15.0)
        nav_channel.add_ais_target(t1)
        nav_channel.add_ais_target(t2)
        assert len(nav_channel.ais_targets) == 1
        assert nav_channel.ais_targets[0].speed == 15.0
        assert nav_channel.ais_targets[0].latitude == 31.5

    def test_nav_ais_no_duplicate_mmsi(self, nav_channel):
        """同 MMSI 不重复。"""
        for _ in range(5):
            nav_channel.add_ais_target(_make_ais(mmsi=222000001))
        assert len(nav_channel.ais_targets) == 1

    def test_nav_ais_multiple_different_mmsi(self, nav_channel):
        """多个不同 MMSI 全部保留。"""
        for i in range(10):
            nav_channel.add_ais_target(_make_ais(mmsi=300000000 + i))
        assert len(nav_channel.ais_targets) == 10

    def test_nav_ais_update_preserves_order(self, nav_channel):
        """更新已有 MMSI 后总数不变，顺序中更新到原位置。"""
        nav_channel.add_ais_target(_make_ais(mmsi=400000001))
        nav_channel.add_ais_target(_make_ais(mmsi=400000002))
        nav_channel.add_ais_target(_make_ais(mmsi=400000003))
        # Update the second one
        nav_channel.add_ais_target(_make_ais(mmsi=400000002, speed=20.0))
        assert len(nav_channel.ais_targets) == 3
        assert nav_channel.ais_targets[1].mmsi == 400000002
        assert nav_channel.ais_targets[1].speed == 20.0


class TestNavRemoveStale:
    """Stale target removal 测试。"""

    def test_nav_remove_stale_default_timeout(self, nav_channel):
        """默认 300 秒超时清理。"""
        old_ts = datetime.now() - timedelta(seconds=400)
        nav_channel.add_ais_target(_make_ais(mmsi=500000001, ts=old_ts))
        nav_channel.add_ais_target(_make_ais(mmsi=500000002))  # fresh
        removed = nav_channel.remove_stale_targets()
        assert removed == 1
        assert len(nav_channel.ais_targets) == 1
        assert nav_channel.ais_targets[0].mmsi == 500000002

    def test_nav_remove_stale_custom_timeout(self, nav_channel):
        """自定义超时。"""
        old_ts = datetime.now() - timedelta(seconds=60)
        nav_channel.add_ais_target(_make_ais(mmsi=600000001, ts=old_ts))
        removed = nav_channel.remove_stale_targets(timeout_s=30)
        assert removed == 1
        assert len(nav_channel.ais_targets) == 0

    def test_nav_remove_stale_keeps_fresh(self, nav_channel):
        """未过期不清理。"""
        nav_channel.add_ais_target(_make_ais(mmsi=700000001))
        nav_channel.add_ais_target(_make_ais(mmsi=700000002))
        removed = nav_channel.remove_stale_targets()
        assert removed == 0
        assert len(nav_channel.ais_targets) == 2

    def test_nav_remove_stale_empty(self, nav_channel):
        """无目标时不报错。"""
        removed = nav_channel.remove_stale_targets()
        assert removed == 0

    def test_nav_remove_stale_all_expired(self, nav_channel):
        """全部过期全部清理。"""
        old_ts = datetime.now() - timedelta(seconds=500)
        for i in range(5):
            nav_channel.add_ais_target(_make_ais(mmsi=800000000 + i, ts=old_ts))
        removed = nav_channel.remove_stale_targets()
        assert removed == 5
        assert len(nav_channel.ais_targets) == 0

    def test_nav_remove_stale_boundary(self, nav_channel):
        """恰好在超时边界内的目标应保留 (<=)。"""
        # Use 299s so we're comfortably within the 300s window
        almost_ts = datetime.now() - timedelta(seconds=299)
        nav_channel.add_ais_target(_make_ais(mmsi=810000001, ts=almost_ts))
        removed = nav_channel.remove_stale_targets(timeout_s=300)
        assert removed == 0


class TestNavClosestTargets:
    """get_closest_targets 测试。"""

    def test_nav_closest_targets(self, nav_channel):
        """获取最近目标。"""
        # Add targets at different distances
        nav_channel.add_ais_target(_make_ais(mmsi=900000001, lat=31.001, lon=121.001))
        nav_channel.add_ais_target(_make_ais(mmsi=900000002, lat=31.01, lon=121.01))
        nav_channel.add_ais_target(_make_ais(mmsi=900000003, lat=31.1, lon=121.1))
        result = nav_channel.get_closest_targets(n=2)
        assert len(result) == 2
        # Should be sorted by CPA
        assert result[0]["cpa"] <= result[1]["cpa"]

    def test_nav_closest_targets_less_than_n(self, nav_channel):
        """目标数少于 n。"""
        nav_channel.add_ais_target(_make_ais(mmsi=910000001))
        result = nav_channel.get_closest_targets(n=5)
        assert len(result) == 1

    def test_nav_closest_targets_empty(self, nav_channel):
        """无目标。"""
        result = nav_channel.get_closest_targets()
        assert result == []

    def test_nav_closest_targets_has_expected_keys(self, nav_channel):
        """返回结果包含预期字段。"""
        nav_channel.add_ais_target(_make_ais(mmsi=920000001))
        result = nav_channel.get_closest_targets(n=1)
        assert len(result) == 1
        entry = result[0]
        for key in ("mmsi", "cpa", "tcpa", "range", "bearing", "risk_level", "vessel_type"):
            assert key in entry, f"Missing key: {key}"

    def test_nav_closest_targets_default_n(self, nav_channel):
        """默认 n=5。"""
        for i in range(10):
            nav_channel.add_ais_target(
                _make_ais(mmsi=930000000 + i, lat=31.0 + i * 0.001, lon=121.0 + i * 0.001)
            )
        result = nav_channel.get_closest_targets()
        assert len(result) == 5


# ═══════════════════════════════════════════════════════════════
# 3. 告警联动测试 (10+ tests)
# ═══════════════════════════════════════════════════════════════

class TestAlarmChannelAlarm:
    """channel_alarm 事件处理测试。"""

    def test_alarm_channel_alarm_event(self, alarm_channel):
        """channel_alarm 事件正确触发 raise_alarm。"""
        event = {
            "type": "channel_alarm",
            "alarm_id": "ENG-OVERTEMP-001",
            "source_channel": "intelligent_engine",
            "priority": "alarm",
            "description": "Engine cylinder temperature exceeds limit",
        }
        result = asyncio.run(alarm_channel.process_event(event))
        assert result["status"] == "raised"
        assert result["alarm_id"] == "ENG-OVERTEMP-001"
        active = alarm_channel.get_active_alarms()
        assert len(active) == 1
        assert active[0]["source_channel"] == "intelligent_engine"

    def test_alarm_channel_alarm_missing_fields(self, alarm_channel):
        """缺少字段时仍能处理 — 使用默认值。"""
        event = {"type": "channel_alarm"}
        result = asyncio.run(alarm_channel.process_event(event))
        assert result["status"] == "raised"
        # Should have used defaults for missing fields
        active = alarm_channel.get_active_alarms()
        assert len(active) == 1
        assert active[0]["priority"] == "caution"  # default

    def test_alarm_channel_alarm_priority(self, alarm_channel):
        """优先级正确设定。"""
        for prio in ("emergency", "alarm", "warning", "caution"):
            event = {
                "type": "channel_alarm",
                "alarm_id": f"TEST-{prio}",
                "source_channel": "test",
                "priority": prio,
                "description": f"Test {prio}",
            }
            asyncio.run(alarm_channel.process_event(event))
        alarms = alarm_channel.get_active_alarms()
        priorities = [a["priority"] for a in alarms]
        assert priorities == ["emergency", "alarm", "warning", "caution"]

    def test_alarm_multiple_channel_alarms(self, alarm_channel):
        """多个 channel 告警。"""
        sources = [
            ("NAV-001", "intelligent_navigation", "warning"),
            ("ENG-001", "intelligent_engine", "alarm"),
            ("HULL-001", "hull_stress_monitor", "emergency"),
        ]
        for alarm_id, src, prio in sources:
            event = {
                "type": "channel_alarm",
                "alarm_id": alarm_id,
                "source_channel": src,
                "priority": prio,
                "description": f"Alert from {src}",
            }
            asyncio.run(alarm_channel.process_event(event))
        assert len(alarm_channel.get_active_alarms()) == 3
        summary = alarm_channel.get_alarm_summary()
        assert summary["emergency_count"] == 1
        assert summary["alarm_count"] == 1
        assert summary["warning_count"] == 1

    def test_alarm_channel_alarm_dedup(self, alarm_channel):
        """同一 alarm_id 覆盖而非重复。"""
        event = {
            "type": "channel_alarm",
            "alarm_id": "DEDUP-001",
            "source_channel": "nav",
            "priority": "warning",
            "description": "First",
        }
        asyncio.run(alarm_channel.process_event(event))
        # Raise again with different description
        event["description"] = "Second"
        asyncio.run(alarm_channel.process_event(event))
        active = alarm_channel.get_active_alarms()
        assert len(active) == 1
        assert active[0]["description"] == "Second"

    def test_alarm_acknowledge_via_event(self, alarm_channel):
        """通过事件确认告警。"""
        # First raise
        asyncio.run(alarm_channel.process_event({
            "type": "channel_alarm",
            "alarm_id": "ACK-001",
            "source_channel": "engine",
            "priority": "alarm",
            "description": "Test alarm",
        }))
        # Then acknowledge
        result = asyncio.run(alarm_channel.process_event({
            "type": "acknowledge_alarm",
            "alarm_id": "ACK-001",
        }))
        assert result["status"] == "acknowledged"
        assert result["acknowledged"] is True
        active = alarm_channel.get_active_alarms()
        assert active[0]["acknowledged"] is True

    def test_alarm_clear_via_event(self, alarm_channel):
        """通过事件清除告警。"""
        asyncio.run(alarm_channel.process_event({
            "type": "channel_alarm",
            "alarm_id": "CLR-001",
            "source_channel": "nav",
            "priority": "warning",
            "description": "Temporary",
        }))
        result = asyncio.run(alarm_channel.process_event({
            "type": "clear_alarm",
            "alarm_id": "CLR-001",
        }))
        assert result["status"] == "cleared"
        assert result["cleared"] is True
        assert len(alarm_channel.get_active_alarms()) == 0

    def test_alarm_acknowledge_nonexistent(self, alarm_channel):
        """确认不存在的告警。"""
        result = asyncio.run(alarm_channel.process_event({
            "type": "acknowledge_alarm",
            "alarm_id": "NOPE-001",
        }))
        assert result["acknowledged"] is False

    def test_alarm_clear_nonexistent(self, alarm_channel):
        """清除不存在的告警。"""
        result = asyncio.run(alarm_channel.process_event({
            "type": "clear_alarm",
            "alarm_id": "NOPE-002",
        }))
        assert result["cleared"] is False

    def test_alarm_unknown_event_type(self, alarm_channel):
        """未知事件类型 → ignored。"""
        result = asyncio.run(alarm_channel.process_event({"type": "bogus_event"}))
        assert result["status"] == "ignored"

    def test_alarm_emergency_updates_health(self, alarm_channel):
        """emergency 告警应将 Channel 健康设为 ERROR。"""
        asyncio.run(alarm_channel.process_event({
            "type": "channel_alarm",
            "alarm_id": "EMG-HEALTH",
            "source_channel": "engine",
            "priority": "emergency",
            "description": "Fire in engine room",
        }))
        status = alarm_channel.get_status()
        assert status["health"] == "error"
        assert status["emergency_count"] == 1

    def test_alarm_silence_alarm(self, alarm_channel):
        """静音告警。"""
        alarm_channel.raise_alarm("SIL-001", "nav", "warning", "Test")
        result = alarm_channel.silence_alarm("SIL-001")
        assert result["silenced"] is True
        active = alarm_channel.get_active_alarms()
        assert active[0]["silenced"] is True
