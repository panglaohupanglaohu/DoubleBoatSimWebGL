# -*- coding: utf-8 -*-
"""
Hull Stress Monitor + Power Management + Orchestrator Integration 测试

覆盖:
- HullStressMonitorChannel: 传感器更新、结构健康度、疲劳评估、process_event、get_status
- PowerManagementChannel: 发电机/负载管理、电力平衡、燃油效率、process_event、get_status
- DecisionOrchestratorChannel: hull/power → action_plan 集成、优雅降级
"""

import asyncio
import pytest

from backend.channels.hull_stress_monitor import HullStressMonitorChannel
from backend.channels.power_management import PowerManagementChannel
from backend.channels.decision_orchestrator import DecisionOrchestratorChannel
from backend.channels.marine_base import get_default_registry


# ══════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════

@pytest.fixture()
def hull():
    ch = HullStressMonitorChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def power():
    ch = PowerManagementChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def orchestrator():
    ch = DecisionOrchestratorChannel()
    ch.initialize()
    return ch


# ══════════════════════════════════════════════════════════════
# 1. Hull Stress Monitor 测试 (20+ tests)
# ══════════════════════════════════════════════════════════════

class TestHullInit:
    def test_hull_init(self, hull):
        assert hull._initialized is True
        assert hull._active is True
        assert hull._sensors == {}
        assert hull.name == "hull_stress_monitor"

    def test_hull_init_no_sensors(self, hull):
        assert len(hull._sensors) == 0


class TestHullUpdateSensor:
    def test_hull_update_sensor(self, hull):
        result = hull.update_sensor("S1", "bow_port", 120.0, strain=0.001, temperature_c=25.0)
        assert result["sensor_id"] == "S1"
        assert result["location"] == "bow_port"
        assert result["stress_mpa"] == 120.0
        assert result["strain"] == 0.001
        assert result["temperature_c"] == 25.0
        assert "timestamp" in result
        assert "S1" in hull._sensors

    def test_hull_update_multiple_sensors(self, hull):
        hull.update_sensor("S1", "bow_port", 100.0)
        hull.update_sensor("S2", "bow_starboard", 110.0)
        hull.update_sensor("S3", "cross_deck", 130.0)
        assert len(hull._sensors) == 3

    def test_hull_sensor_locations(self, hull):
        hull.update_sensor("S1", "bow_port", 80.0)
        hull.update_sensor("S2", "stern_stbd", 90.0)
        assert hull._sensors["S1"]["location"] == "bow_port"
        assert hull._sensors["S2"]["location"] == "stern_stbd"


class TestHullStructuralHealth:
    def test_hull_structural_health_no_sensors(self, hull):
        health = hull.get_structural_health()
        assert health["max_stress"] == 0.0
        assert health["stress_ratio"] == 0.0
        assert health["health_score"] == 100.0
        assert health["hotspots"] == []
        assert health["alarm_active"] is False

    def test_hull_structural_health_normal(self, hull):
        # stress < 0.6 * yield(250) = 150 → no hotspots
        hull.update_sensor("S1", "bow", 100.0)
        health = hull.get_structural_health()
        assert health["stress_ratio"] == pytest.approx(100.0 / 250.0)
        assert health["hotspots"] == []
        assert health["alarm_active"] is False

    def test_hull_structural_health_elevated(self, hull):
        # stress > 0.6 * 250 = 150 → hotspot, but < 0.8*250=200 → no alarm
        hull.update_sensor("S1", "cross_deck", 170.0)
        health = hull.get_structural_health()
        assert "S1" in health["hotspots"]
        assert health["alarm_active"] is False

    def test_hull_structural_health_alarm(self, hull):
        # stress > 0.8 * 250 = 200 → alarm active
        hull.update_sensor("S1", "cross_deck", 210.0)
        health = hull.get_structural_health()
        assert health["alarm_active"] is True
        assert "S1" in health["hotspots"]

    def test_hull_structural_health_critical(self, hull):
        # stress near yield (250)
        hull.update_sensor("S1", "bow", 245.0)
        health = hull.get_structural_health()
        assert health["stress_ratio"] == pytest.approx(245.0 / 250.0)
        assert health["health_score"] == pytest.approx(max(0, 100 - 245.0 / 250.0 * 100))
        assert health["alarm_active"] is True

    def test_hull_health_score_calculation(self, hull):
        hull.update_sensor("S1", "bow", 125.0)
        health = hull.get_structural_health()
        expected_score = max(0.0, 100.0 - (125.0 / 250.0) * 100.0)
        assert health["health_score"] == pytest.approx(expected_score)

    def test_hull_hotspots_identification(self, hull):
        hull.update_sensor("S1", "bow", 100.0)   # ratio 0.4 → not hotspot
        hull.update_sensor("S2", "mid", 160.0)    # ratio 0.64 → hotspot
        hull.update_sensor("S3", "stern", 200.0)  # ratio 0.8 → hotspot
        health = hull.get_structural_health()
        assert "S1" not in health["hotspots"]
        assert "S2" in health["hotspots"]
        assert "S3" in health["hotspots"]


class TestHullFatigue:
    def test_hull_fatigue_normal(self, hull):
        # stress 100 < fatigue_limit 160 → normal
        hull.update_sensor("S1", "bow", 100.0)
        fatigue = hull.get_fatigue_assessment()
        assert fatigue["sensors_above_fatigue"] == 0
        assert fatigue["recommendation"] == "normal"

    def test_hull_fatigue_above_limit(self, hull):
        # stress 180 > fatigue_limit 160 → above
        hull.update_sensor("S1", "bow", 180.0)
        fatigue = hull.get_fatigue_assessment()
        assert fatigue["sensors_above_fatigue"] == 1

    def test_hull_fatigue_no_sensors(self, hull):
        fatigue = hull.get_fatigue_assessment()
        assert fatigue["sensors_above_fatigue"] == 0
        assert fatigue["max_fatigue_ratio"] == 0.0
        assert fatigue["recommendation"] == "normal"

    def test_hull_fatigue_recommendation_monitor(self, hull):
        # fatigue_ratio > 1.0 but <= 1.2 → monitor
        # stress = 170 → ratio = 170/160 = 1.0625
        hull.update_sensor("S1", "bow", 170.0)
        fatigue = hull.get_fatigue_assessment()
        assert fatigue["recommendation"] == "monitor"

    def test_hull_fatigue_recommendation_reduce_speed(self, hull):
        # fatigue_ratio > 1.2 but <= 1.5 → reduce_speed
        # stress = 200 → ratio = 200/160 = 1.25
        hull.update_sensor("S1", "bow", 200.0)
        fatigue = hull.get_fatigue_assessment()
        assert fatigue["recommendation"] == "reduce_speed"

    def test_hull_fatigue_recommendation_seek_shelter(self, hull):
        # fatigue_ratio > 1.5 → seek_shelter
        # stress = 250 → ratio = 250/160 = 1.5625
        hull.update_sensor("S1", "bow", 250.0)
        fatigue = hull.get_fatigue_assessment()
        assert fatigue["recommendation"] == "seek_shelter"


class TestHullProcessEvent:
    def test_hull_process_event(self, hull):
        event = {
            "type": "stress_reading",
            "sensor_id": "S1",
            "location": "bow",
            "stress_mpa": 150.0,
            "strain": 0.002,
            "temperature_c": 30.0,
        }
        result = asyncio.run(hull.process_event(event))
        assert result["status"] == "recorded"
        assert result["sensor"]["sensor_id"] == "S1"
        assert "S1" in hull._sensors

    def test_hull_process_event_missing_sensor_id(self, hull):
        event = {"type": "stress_reading"}
        result = asyncio.run(hull.process_event(event))
        assert result["status"] == "error"

    def test_hull_process_event_unknown_type(self, hull):
        event = {"type": "unknown"}
        result = asyncio.run(hull.process_event(event))
        assert result["status"] == "ignored"


class TestHullGetStatus:
    def test_hull_get_status(self, hull):
        hull.update_sensor("S1", "bow", 120.0)
        status = hull.get_status()
        assert status["name"] == "hull_stress_monitor"
        assert status["active"] is True
        assert status["initialized"] is True
        assert status["sensor_count"] == 1
        assert "max_stress_mpa" in status
        assert "stress_ratio" in status
        assert "health_score" in status
        assert "alarm_active" in status
        assert "health" in status


# ══════════════════════════════════════════════════════════════
# 2. Power Management 测试 (20+ tests)
# ══════════════════════════════════════════════════════════════

class TestPowerInit:
    def test_power_init(self, power):
        assert power._initialized is True
        assert power._active is True
        assert power._generators == {}
        assert power._loads == {}
        assert power.name == "power_management"

    def test_power_init_battery_defaults(self, power):
        assert power._battery["capacity_kwh"] == 500.0
        assert power._battery["soc_percent"] == 80.0
        assert power._battery["charging"] is False


class TestPowerUpdateGenerator:
    def test_power_update_generator(self, power):
        gen = power.update_generator("G1", rated_kw=1000.0, current_kw=800.0,
                                     fuel_rate_lph=180.0, status="running", rpm=1800)
        assert gen["gen_id"] == "G1"
        assert gen["rated_kw"] == 1000.0
        assert gen["current_kw"] == 800.0
        assert gen["fuel_rate_lph"] == 180.0
        assert gen["status"] == "running"
        assert "G1" in power._generators


class TestPowerUpdateLoad:
    def test_power_update_load(self, power):
        load = power.update_load("L1", category="propulsion", current_kw=300.0, priority=1)
        assert load["load_id"] == "L1"
        assert load["category"] == "propulsion"
        assert load["current_kw"] == 300.0
        assert "L1" in power._loads


class TestPowerBalance:
    def test_power_balance_no_generators(self, power):
        balance = power.get_power_balance()
        assert balance["total_generation_kw"] == 0.0
        assert balance["total_load_kw"] == 0.0
        assert balance["reserve_kw"] == 0.0
        assert balance["reserve_percent"] == 0.0
        # No generation → reserve_percent=0 which is < 15 → load_shedding_needed
        assert balance["load_shedding_needed"] is True

    def test_power_balance_single_generator(self, power):
        power.update_generator("G1", current_kw=500.0, status="running")
        balance = power.get_power_balance()
        assert balance["total_generation_kw"] == 500.0
        assert balance["reserve_kw"] == 500.0  # no loads
        assert balance["reserve_percent"] == 100.0

    def test_power_balance_multiple_generators(self, power):
        power.update_generator("G1", current_kw=400.0, status="running")
        power.update_generator("G2", current_kw=300.0, status="running")
        balance = power.get_power_balance()
        assert balance["total_generation_kw"] == 700.0

    def test_power_balance_with_loads(self, power):
        power.update_generator("G1", current_kw=500.0, status="running")
        power.update_load("L1", current_kw=200.0)
        power.update_load("L2", current_kw=100.0)
        balance = power.get_power_balance()
        assert balance["total_load_kw"] == 300.0
        assert balance["reserve_kw"] == pytest.approx(200.0)
        assert balance["reserve_percent"] == pytest.approx(40.0)

    def test_power_reserve_percent(self, power):
        power.update_generator("G1", current_kw=1000.0, status="running")
        power.update_load("L1", current_kw=600.0)
        balance = power.get_power_balance()
        assert balance["reserve_percent"] == pytest.approx(40.0)

    def test_power_load_shedding_needed(self, power):
        # reserve < 15% → load shedding needed
        power.update_generator("G1", current_kw=100.0, status="running")
        power.update_load("L1", current_kw=90.0)
        balance = power.get_power_balance()
        assert balance["reserve_percent"] == pytest.approx(10.0)
        assert balance["load_shedding_needed"] is True

    def test_power_load_shedding_not_needed(self, power):
        # reserve >= 15% → no load shedding
        power.update_generator("G1", current_kw=100.0, status="running")
        power.update_load("L1", current_kw=80.0)
        balance = power.get_power_balance()
        assert balance["reserve_percent"] == pytest.approx(20.0)
        assert balance["load_shedding_needed"] is False

    def test_power_standby_generator_excluded(self, power):
        power.update_generator("G1", current_kw=500.0, status="running")
        power.update_generator("G2", current_kw=500.0, status="standby")
        balance = power.get_power_balance()
        # standby excluded from total generation
        assert balance["total_generation_kw"] == 500.0


class TestPowerFuelEfficiency:
    def test_power_fuel_efficiency_good(self, power):
        # sfc = (fuel_rate * 0.84 * 1000) / current_kw
        # sfc = (80 * 0.84 * 1000) / 500 = 134.4 → good
        power.update_generator("G1", current_kw=500.0, fuel_rate_lph=80.0, status="running")
        eff = power.get_fuel_efficiency()
        assert eff["efficiency_rating"] == "good"
        assert eff["specific_fuel_consumption"] < 200.0

    def test_power_fuel_efficiency_acceptable(self, power):
        # sfc = (130 * 0.84 * 1000) / 500 = 218.4 → acceptable (200-250)
        power.update_generator("G1", current_kw=500.0, fuel_rate_lph=130.0, status="running")
        eff = power.get_fuel_efficiency()
        assert eff["efficiency_rating"] == "acceptable"

    def test_power_fuel_efficiency_poor(self, power):
        # sfc = (160 * 0.84 * 1000) / 500 = 268.8 → poor (>=250)
        power.update_generator("G1", current_kw=500.0, fuel_rate_lph=160.0, status="running")
        eff = power.get_fuel_efficiency()
        assert eff["efficiency_rating"] == "poor"

    def test_power_fuel_efficiency_no_generation(self, power):
        eff = power.get_fuel_efficiency()
        assert eff["specific_fuel_consumption"] == 0.0
        assert eff["efficiency_rating"] == "good"


class TestPowerBatteryUpdate:
    def test_power_battery_update(self, power):
        event = {"type": "battery_update", "soc_percent": 60.0, "charging": True}
        result = asyncio.run(power.process_event(event))
        assert result["status"] == "recorded"
        assert power._battery["soc_percent"] == 60.0
        assert power._battery["charging"] is True


class TestPowerProcessEvent:
    def test_power_process_event_generator(self, power):
        event = {"type": "generator_update", "gen_id": "G1", "current_kw": 400.0, "status": "running"}
        result = asyncio.run(power.process_event(event))
        assert result["status"] == "recorded"
        assert "G1" in power._generators

    def test_power_process_event_load(self, power):
        event = {"type": "load_update", "load_id": "L1", "current_kw": 200.0, "category": "propulsion"}
        result = asyncio.run(power.process_event(event))
        assert result["status"] == "recorded"
        assert "L1" in power._loads

    def test_power_process_event_missing_gen_id(self, power):
        event = {"type": "generator_update"}
        result = asyncio.run(power.process_event(event))
        assert result["status"] == "error"

    def test_power_process_event_missing_load_id(self, power):
        event = {"type": "load_update"}
        result = asyncio.run(power.process_event(event))
        assert result["status"] == "error"

    def test_power_process_event_unknown_type(self, power):
        event = {"type": "unknown"}
        result = asyncio.run(power.process_event(event))
        assert result["status"] == "ignored"


class TestPowerGetStatus:
    def test_power_get_status(self, power):
        power.update_generator("G1", current_kw=500.0, status="running")
        power.update_load("L1", current_kw=200.0)
        status = power.get_status()
        assert status["name"] == "power_management"
        assert status["active"] is True
        assert status["initialized"] is True
        assert status["generators_running"] == 1
        assert status["total_generation_kw"] == 500.0
        assert status["total_load_kw"] == 200.0
        assert "reserve_percent" in status
        assert "battery_soc" in status
        assert "load_shedding_needed" in status
        assert "health" in status


# ══════════════════════════════════════════════════════════════
# 3. Orchestrator Integration 测试 (10+ tests)
# ══════════════════════════════════════════════════════════════

class TestOrchestratorHullIntegration:
    """编排器通过 registry 获取 hull_stress_monitor 数据并生成 action。"""

    def test_orchestrator_hull_stress_high(self, orchestrator):
        registry = get_default_registry()
        hull = HullStressMonitorChannel()
        hull.initialize()
        # stress_ratio = 210/250 = 0.84 > 0.8 → reduce_speed_hull_stress
        hull.update_sensor("S1", "cross_deck", 210.0)
        registry.register(hull)

        plan = orchestrator._build_action_plan(snapshot={})
        hull_actions = [a for a in plan if a["recommended_action"] == "reduce_speed_hull_stress"]
        assert len(hull_actions) == 1
        assert hull_actions[0]["domain"] == "structure"

    def test_orchestrator_hull_alarm(self, orchestrator):
        registry = get_default_registry()
        hull = HullStressMonitorChannel()
        hull.initialize()
        # stress > 0.8 * 250 = 200 → alarm_active
        hull.update_sensor("S1", "cross_deck", 210.0)
        registry.register(hull)

        plan = orchestrator._build_action_plan(snapshot={})
        alarm_actions = [a for a in plan if a["recommended_action"] == "emergency_hull_stress"]
        assert len(alarm_actions) == 1
        assert alarm_actions[0]["priority"] == "critical"

    def test_orchestrator_hull_normal(self, orchestrator):
        registry = get_default_registry()
        hull = HullStressMonitorChannel()
        hull.initialize()
        # stress_ratio = 100/250 = 0.4 → no hull actions
        hull.update_sensor("S1", "bow", 100.0)
        registry.register(hull)

        plan = orchestrator._build_action_plan(snapshot={})
        hull_actions = [a for a in plan
                        if a.get("recommended_action") in ("reduce_speed_hull_stress", "emergency_hull_stress")]
        assert len(hull_actions) == 0

    def test_orchestrator_hull_channel_missing(self, orchestrator):
        # No hull channel registered → graceful degradation
        plan = orchestrator._build_action_plan(snapshot={})
        assert isinstance(plan, list)
        hull_actions = [a for a in plan
                        if a.get("recommended_action") in ("reduce_speed_hull_stress", "emergency_hull_stress")]
        assert len(hull_actions) == 0

    def test_orchestrator_hull_stress_very_high_critical_priority(self, orchestrator):
        registry = get_default_registry()
        hull = HullStressMonitorChannel()
        hull.initialize()
        # stress_ratio = 230/250 = 0.92 > 0.9 → priority critical
        hull.update_sensor("S1", "cross_deck", 230.0)
        registry.register(hull)

        plan = orchestrator._build_action_plan(snapshot={})
        hull_actions = [a for a in plan if a["recommended_action"] == "reduce_speed_hull_stress"]
        assert len(hull_actions) == 1
        assert hull_actions[0]["priority"] == "critical"


class TestOrchestratorPowerIntegration:
    """编排器通过 registry 获取 power_management 数据并生成 action。"""

    def test_orchestrator_power_load_shedding(self, orchestrator):
        registry = get_default_registry()
        pwr = PowerManagementChannel()
        pwr.initialize()
        pwr.update_generator("G1", current_kw=100.0, status="running")
        pwr.update_load("L1", current_kw=90.0)  # reserve 10% < 15%
        registry.register(pwr)

        plan = orchestrator._build_action_plan(snapshot={})
        power_actions = [a for a in plan if a["recommended_action"] == "load_shedding_required"]
        assert len(power_actions) == 1
        assert power_actions[0]["domain"] == "power"

    def test_orchestrator_power_normal(self, orchestrator):
        registry = get_default_registry()
        pwr = PowerManagementChannel()
        pwr.initialize()
        pwr.update_generator("G1", current_kw=100.0, status="running")
        pwr.update_load("L1", current_kw=50.0)  # reserve 50% >= 15%
        registry.register(pwr)

        plan = orchestrator._build_action_plan(snapshot={})
        power_actions = [a for a in plan if a.get("recommended_action") == "load_shedding_required"]
        assert len(power_actions) == 0

    def test_orchestrator_power_channel_missing(self, orchestrator):
        # No power channel registered → graceful degradation
        plan = orchestrator._build_action_plan(snapshot={})
        assert isinstance(plan, list)
        power_actions = [a for a in plan if a.get("recommended_action") == "load_shedding_required"]
        assert len(power_actions) == 0


class TestOrchestratorCombined:
    """hull + power 同时告警的场景。"""

    def test_orchestrator_combined_hull_power(self, orchestrator):
        registry = get_default_registry()

        hull = HullStressMonitorChannel()
        hull.initialize()
        hull.update_sensor("S1", "cross_deck", 210.0)  # alarm triggers
        registry.register(hull)

        pwr = PowerManagementChannel()
        pwr.initialize()
        pwr.update_generator("G1", current_kw=100.0, status="running")
        pwr.update_load("L1", current_kw=90.0)  # load_shedding triggers
        registry.register(pwr)

        plan = orchestrator._build_action_plan(snapshot={})
        hull_actions = [a for a in plan
                        if a.get("recommended_action") in ("reduce_speed_hull_stress", "emergency_hull_stress")]
        power_actions = [a for a in plan if a.get("recommended_action") == "load_shedding_required"]
        assert len(hull_actions) >= 1
        assert len(power_actions) == 1

    def test_orchestrator_hull_power_with_weather(self, orchestrator):
        registry = get_default_registry()

        hull = HullStressMonitorChannel()
        hull.initialize()
        hull.update_sensor("S1", "cross_deck", 220.0)
        registry.register(hull)

        pwr = PowerManagementChannel()
        pwr.initialize()
        pwr.update_generator("G1", current_kw=100.0, status="running")
        pwr.update_load("L1", current_kw=88.0)
        registry.register(pwr)

        plan = orchestrator._build_action_plan(
            snapshot={},
            weather_risk={"risk_score": 80, "recommendation": "Storm"},
        )
        domains = {a["domain"] for a in plan}
        assert "structure" in domains
        assert "power" in domains
        assert "navigation" in domains  # weather → review_route
