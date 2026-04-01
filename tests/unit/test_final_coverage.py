# -*- coding: utf-8 -*-
"""
最终测试覆盖推进 — LRIT/灯光深度测试 + 跨Channel集成场景

覆盖:
- LRIT Reporter 深度测试 (12+ tests)
- Navigational Lights 深度测试 (15+ tests)
- 跨 Channel 集成场景测试 (10+ tests)
"""

import asyncio
import time
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from backend.channels.lrit_reporter import LRITReporterChannel
from backend.channels.navigational_lights import NavigationalLightsChannel
from backend.channels.decision_orchestrator import DecisionOrchestratorChannel


# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════

def _run(coro):
    """Run an async coroutine synchronously."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _mock_registry_with(channels: Dict[str, Any]):
    """Create a mock registry that returns given channel mocks by name."""
    registry = MagicMock()
    registry.get = lambda name: channels.get(name)
    return registry


# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════

@pytest.fixture()
def lrit():
    ch = LRITReporterChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def lights():
    ch = NavigationalLightsChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def orchestrator():
    ch = DecisionOrchestratorChannel()
    ch.initialize()
    return ch


# ═══════════════════════════════════════════════════════════════
# 1. LRIT Reporter 深度测试 (12+ tests)
# ═══════════════════════════════════════════════════════════════

class TestLRITSetShipInfo:
    """test_lrit_set_ship_info: 设置船舶信息。"""

    def test_lrit_set_ship_info(self, lrit):
        result = lrit.set_ship_info(
            imo_number=1234567, mmsi=412345678,
            flag_state="CN", ship_name="PoseidonX",
        )
        assert result["status"] == "ship_info_set"
        assert result["ship_info"]["imo_number"] == 1234567
        assert result["ship_info"]["mmsi"] == 412345678
        assert result["ship_info"]["flag_state"] == "CN"
        assert result["ship_info"]["ship_name"] == "PoseidonX"

    def test_lrit_set_ship_info_updates_internal(self, lrit):
        lrit.set_ship_info(9999999, 123456789, "PA", "TestVessel")
        assert lrit._ship_info["imo_number"] == 9999999
        assert lrit._ship_info["flag_state"] == "PA"


class TestLRITGenerateReport:
    """test_lrit_generate_report: 生成报告包含完整信息。"""

    def test_lrit_generate_report(self, lrit):
        lrit.set_ship_info(1234567, 412345678, "CN", "PoseidonX")
        report = lrit.generate_report(31.23, 121.47)
        assert report["ship_info"]["imo_number"] == 1234567
        assert report["position"]["lat"] == 31.23
        assert report["position"]["lon"] == 121.47
        assert "timestamp" in report
        assert "epoch" in report

    def test_lrit_generate_report_default_ship_info(self, lrit):
        report = lrit.generate_report(0.0, 0.0)
        assert report["ship_info"]["imo_number"] is None
        assert report["position"]["lat"] == 0.0


class TestLRITReportUpdatesLastTime:
    """test_lrit_report_updates_last_time: 报告后更新 last_report_time。"""

    def test_lrit_report_updates_last_time(self, lrit):
        assert lrit._last_report_time is None
        lrit.generate_report(31.0, 121.0)
        assert lrit._last_report_time is not None
        assert isinstance(lrit._last_report_time, float)

    def test_lrit_report_updates_last_time_increases(self, lrit):
        lrit.generate_report(31.0, 121.0)
        t1 = lrit._last_report_time
        time.sleep(0.01)
        lrit.generate_report(31.1, 121.1)
        t2 = lrit._last_report_time
        assert t2 > t1


class TestLRITReportHistoryMax50:
    """test_lrit_report_history_max_50: 历史不超过 50 条。"""

    def test_lrit_report_history_max_50(self, lrit):
        for i in range(60):
            lrit.generate_report(float(i), float(i))
        history = lrit.get_report_history()
        assert len(history) == 50


class TestLRITCheckReportingDue:
    """check_reporting_due 系列测试。"""

    def test_lrit_check_reporting_due_never_reported(self, lrit):
        result = lrit.check_reporting_due()
        assert result["reporting_due"] is True
        assert result["reason"] == "no_previous_report"
        assert result["elapsed_hours"] is None

    def test_lrit_check_reporting_due_recent(self, lrit):
        lrit.generate_report(31.0, 121.0)
        result = lrit.check_reporting_due()
        assert result["reporting_due"] is False
        assert result["elapsed_hours"] is not None
        assert result["elapsed_hours"] < 1.0

    def test_lrit_check_reporting_due_overdue(self, lrit):
        lrit.generate_report(31.0, 121.0)
        # Simulate 7 hours ago
        lrit._last_report_time = time.time() - 7 * 3600
        result = lrit.check_reporting_due()
        assert result["reporting_due"] is True
        assert result["elapsed_hours"] >= 6.0


class TestLRITCustomInterval:
    """test_lrit_custom_interval: 自定义报告间隔。"""

    def test_lrit_custom_interval(self, lrit):
        lrit._reporting_interval_hours = 1.0
        lrit.generate_report(31.0, 121.0)
        # 1.5 hours ago
        lrit._last_report_time = time.time() - 1.5 * 3600
        result = lrit.check_reporting_due()
        assert result["reporting_due"] is True
        assert result["interval_hours"] == 1.0

    def test_lrit_custom_interval_not_due(self, lrit):
        lrit._reporting_interval_hours = 12.0
        lrit.generate_report(31.0, 121.0)
        # 5 hours ago — still within 12h
        lrit._last_report_time = time.time() - 5 * 3600
        result = lrit.check_reporting_due()
        assert result["reporting_due"] is False


class TestLRITProcessEventAutoReport:
    """test_lrit_process_event_auto_report: 事件自动判断并生成报告。"""

    def test_lrit_process_event_auto_report_first_time(self, lrit):
        event = {"type": "lrit_position_update", "lat": 31.0, "lon": 121.0}
        result = _run(lrit.process_event(event))
        assert result["status"] == "report_generated"
        assert result["report"]["position"]["lat"] == 31.0

    def test_lrit_process_event_not_due(self, lrit):
        lrit.generate_report(31.0, 121.0)
        event = {"type": "lrit_position_update", "lat": 31.1, "lon": 121.1}
        result = _run(lrit.process_event(event))
        assert result["status"] == "not_due"

    def test_lrit_process_event_missing_coords(self, lrit):
        event = {"type": "lrit_position_update"}
        result = _run(lrit.process_event(event))
        assert result["status"] == "error"

    def test_lrit_process_event_unknown_type(self, lrit):
        event = {"type": "unknown_event"}
        result = _run(lrit.process_event(event))
        assert result["status"] == "ignored"


class TestLRITEmptyShipInfo:
    """test_lrit_empty_ship_info: 无 ship_info 时报告仍能生成。"""

    def test_lrit_empty_ship_info(self, lrit):
        # Default ship_info has None fields
        report = lrit.generate_report(10.0, 20.0)
        assert report["ship_info"]["imo_number"] is None
        assert report["ship_info"]["mmsi"] is None
        assert report["position"]["lat"] == 10.0

    def test_lrit_get_status_without_report(self, lrit):
        status = lrit.get_status()
        assert status["name"] == "lrit_reporter"
        assert status["reports_sent"] == 0
        assert status["reporting_due"] is True


# ═══════════════════════════════════════════════════════════════
# 2. Navigational Lights 深度测试 (15+ tests)
# ═══════════════════════════════════════════════════════════════

class TestLightsUnderwayConfiguration:
    """test_lights_underway_configuration: underway 需要的灯。"""

    def test_lights_underway_configuration(self, lights):
        config = lights.get_light_configuration()
        assert config["vessel_status"] == "underway"
        assert "masthead" in config["required_lights"]
        assert "sidelight_port" in config["required_lights"]
        assert "sidelight_stbd" in config["required_lights"]
        assert "stern" in config["required_lights"]


class TestLightsAtAnchorConfiguration:
    """test_lights_at_anchor_configuration: 锚泊灯。"""

    def test_lights_at_anchor_configuration(self, lights):
        lights.set_vessel_status("at_anchor")
        config = lights.get_light_configuration()
        assert config["vessel_status"] == "at_anchor"
        assert "anchor" in config["required_lights"]


class TestLightsNUCConfiguration:
    """test_lights_nuc_configuration: 失控灯。"""

    def test_lights_nuc_configuration(self, lights):
        lights.set_vessel_status("nuc")
        config = lights.get_light_configuration()
        assert config["vessel_status"] == "nuc"
        assert "all_round_red" in config["required_lights"]


class TestLightsMooredConfiguration:
    """test_lights_moored_configuration: 系泊灯。"""

    def test_lights_moored_configuration(self, lights):
        lights.set_vessel_status("moored")
        config = lights.get_light_configuration()
        assert config["vessel_status"] == "moored"
        assert "anchor" in config["required_lights"]


class TestLightsTowingConfiguration:
    """test_lights_towing_configuration: 拖轮灯。"""

    def test_lights_towing_configuration(self, lights):
        lights.set_vessel_status("towing")
        config = lights.get_light_configuration()
        assert config["vessel_status"] == "towing"
        assert "towing" in config["required_lights"]
        assert config["required_lights"].count("masthead") == 2


class TestLightsFishingConfiguration:
    """test_lights_fishing_configuration: 渔船灯。"""

    def test_lights_fishing_configuration(self, lights):
        lights.set_vessel_status("fishing")
        config = lights.get_light_configuration()
        assert config["vessel_status"] == "fishing"
        assert "all_round_red" in config["required_lights"]
        assert "all_round_white" in config["required_lights"]


class TestLightsRestrictedConfiguration:
    """test_lights_restricted_configuration: 操纵受限灯。"""

    def test_lights_restricted_configuration(self, lights):
        lights.set_vessel_status("restricted_maneuverability")
        config = lights.get_light_configuration()
        assert config["vessel_status"] == "restricted_maneuverability"
        # red-white-red
        assert config["required_lights"].count("all_round_red") == 2
        assert "all_round_white" in config["required_lights"]


class TestLightsComplianceAllOn:
    """test_lights_compliance_all_on: 全部亮→合规。"""

    def test_lights_compliance_all_on(self, lights):
        # Underway requires: masthead, sidelight_port, sidelight_stbd, stern
        lights.update_light("L1", "masthead", "on")
        lights.update_light("L2", "sidelight_port", "on")
        lights.update_light("L3", "sidelight_stbd", "on")
        lights.update_light("L4", "stern", "on")
        compliance = lights.check_colreg_compliance()
        assert compliance["compliant"] is True
        assert len(compliance["violations"]) == 0


class TestLightsComplianceMissing:
    """test_lights_compliance_missing: 缺灯→不合规+违规列表。"""

    def test_lights_compliance_missing(self, lights):
        # Only masthead — missing port, stbd, stern
        lights.update_light("L1", "masthead", "on")
        compliance = lights.check_colreg_compliance()
        assert compliance["compliant"] is False
        assert "sidelight_port" in compliance["violations"]
        assert "sidelight_stbd" in compliance["violations"]
        assert "stern" in compliance["violations"]


class TestLightsFaultyDetection:
    """test_lights_faulty_detection: 故障灯识别。"""

    def test_lights_faulty_detection(self, lights):
        lights.update_light("L1", "masthead", "on")
        lights.update_light("L2", "sidelight_port", "fault")
        lights.update_light("L3", "sidelight_stbd", "on")
        lights.update_light("L4", "stern", "on")
        compliance = lights.check_colreg_compliance()
        assert compliance["compliant"] is False
        assert "L2" in compliance["faulty_lights"]


class TestLightsVesselStatusChange:
    """test_lights_vessel_status_change: 状态变更后配置变化。"""

    def test_lights_vessel_status_change(self, lights):
        config1 = lights.get_light_configuration()
        assert config1["vessel_status"] == "underway"
        lights.set_vessel_status("at_anchor")
        config2 = lights.get_light_configuration()
        assert config2["vessel_status"] == "at_anchor"
        assert config1["required_lights"] != config2["required_lights"]

    def test_lights_invalid_status(self, lights):
        result = lights.set_vessel_status("invalid_status")
        assert result["status"] == "error"
        # vessel_status should remain unchanged
        assert lights._vessel_status == "underway"


class TestLightsBrightnessTracking:
    """test_lights_brightness_tracking: 亮度跟踪。"""

    def test_lights_brightness_tracking(self, lights):
        lights.update_light("L1", "masthead", "on", brightness=75.0)
        assert lights._lights["L1"]["brightness_percent"] == 75.0

    def test_lights_brightness_default(self, lights):
        lights.update_light("L1", "masthead", "on")
        assert lights._lights["L1"]["brightness_percent"] == 100.0


class TestLightsMultipleUpdates:
    """test_lights_multiple_updates: 多次更新。"""

    def test_lights_multiple_updates(self, lights):
        lights.update_light("L1", "masthead", "on")
        assert lights._lights["L1"]["status"] == "on"
        lights.update_light("L1", "masthead", "off")
        assert lights._lights["L1"]["status"] == "off"
        lights.update_light("L1", "masthead", "fault")
        assert lights._lights["L1"]["status"] == "fault"


class TestLightsProcessEventLight:
    """test_lights_process_event_light: light 事件处理。"""

    def test_lights_process_event_light(self, lights):
        event = {
            "type": "light_status_update",
            "light_id": "L1",
            "light_type": "masthead",
            "status": "on",
            "brightness": 90.0,
        }
        result = _run(lights.process_event(event))
        assert result["status"] == "updated"
        assert result["light_id"] == "L1"
        assert lights._lights["L1"]["brightness_percent"] == 90.0

    def test_lights_process_event_missing_fields(self, lights):
        event = {"type": "light_status_update"}
        result = _run(lights.process_event(event))
        assert result["status"] == "error"

    def test_lights_process_event_unknown(self, lights):
        event = {"type": "unknown_event"}
        result = _run(lights.process_event(event))
        assert result["status"] == "ignored"


class TestLightsProcessEventVessel:
    """test_lights_process_event_vessel: vessel 状态事件处理。"""

    def test_lights_process_event_vessel(self, lights):
        event = {"type": "vessel_status_change", "vessel_status": "at_anchor"}
        result = _run(lights.process_event(event))
        assert result["status"] == "vessel_status_set"
        assert lights._vessel_status == "at_anchor"

    def test_lights_process_event_vessel_missing(self, lights):
        event = {"type": "vessel_status_change"}
        result = _run(lights.process_event(event))
        assert result["status"] == "error"

    def test_lights_get_status(self, lights):
        status = lights.get_status()
        assert status["name"] == "navigational_lights"
        assert "compliant" in status
        assert "vessel_status" in status


# ═══════════════════════════════════════════════════════════════
# 3. 跨 Channel 集成场景测试 (10+ tests)
# ═══════════════════════════════════════════════════════════════

class TestIntegrationStormScenario:
    """暴风雨场景: weather_risk高 + hull_stress高 + autopilot off_course + crew_fatigue低。"""

    def test_integration_storm_scenario(self, orchestrator):
        hull_ch = MagicMock()
        hull_ch.get_structural_health.return_value = {
            "stress_ratio": 0.92, "alarm_active": True,
        }
        ap_ch = MagicMock()
        ap_ch.get_autopilot_status.return_value = {"on_course": False}

        registry = _mock_registry_with({
            "hull_stress_monitor": hull_ch,
            "autopilot_monitor": ap_ch,
        })

        with patch(
            "backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orchestrator._build_action_plan(
                snapshot={},
                weather_risk={"risk_score": 90, "recommendation": "Typhoon approaching"},
                crew_fatigue={"fatigue_scores": {"OOW": 25, "AB1": 40}},
            )

        action_ids = {a["recommended_action"] for a in plan}
        # Weather
        assert "review_route" in action_ids
        # Hull stress critical
        assert "reduce_speed_hull_stress" in action_ids
        assert "emergency_hull_stress" in action_ids
        # Autopilot
        assert "off_course_warning" in action_ids
        # Crew fatigue — OOW=25 and AB1=40 both below 50
        fatigue_actions = [a for a in plan if a["recommended_action"] == "recommend_watch_change"]
        assert len(fatigue_actions) == 2


class TestIntegrationPortArrivalScenario:
    """进港场景: echo_sounder 浅水 + rudder active + mooring 准备。"""

    def test_integration_port_arrival_scenario(self, orchestrator):
        echo_ch = MagicMock()
        echo_ch.get_depth_status.return_value = {
            "grounding_risk": False, "shallow_alarm": True,
        }
        rudder_ch = MagicMock()
        rudder_ch.get_status.return_value = {"solas_compliant": True}
        moor_ch = MagicMock()
        moor_ch.get_mooring_status.return_value = {"any_parted": False}

        registry = _mock_registry_with({
            "echo_sounder_monitor": echo_ch,
            "rudder_control_monitor": rudder_ch,
            "mooring_monitor": moor_ch,
        })

        with patch(
            "backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orchestrator._build_action_plan(snapshot={})

        action_ids = {a["recommended_action"] for a in plan}
        assert "shallow_water_warning" in action_ids
        # Rudder OK and mooring OK → no alarm
        assert "steering_fault" not in action_ids
        assert "mooring_line_parted" not in action_ids


class TestIntegrationEmergencyScenario:
    """紧急场景: comms distress + fire alarm + propulsion alarm → 多个紧急 action。"""

    def test_integration_emergency_scenario(self, orchestrator):
        comms_ch = MagicMock()
        comms_ch.get_status.return_value = {
            "gmdss_compliant": True, "distress_active": True,
        }
        alarm_ch = MagicMock()
        alarm_ch.get_alarm_summary.return_value = {"emergency_count": 2}
        prop_ch = MagicMock()
        prop_ch.get_propulsion_status.return_value = {
            "any_alarm": True, "efficiency_percent": 15,
        }

        registry = _mock_registry_with({
            "communication_manager": comms_ch,
            "alarm_management": alarm_ch,
            "propulsion_monitor": prop_ch,
        })

        with patch(
            "backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orchestrator._build_action_plan(snapshot={})

        action_ids = {a["recommended_action"] for a in plan}
        assert "distress_active" in action_ids
        assert "emergency_alarm_active" in action_ids
        assert "propulsion_alarm" in action_ids
        assert "low_propulsion_efficiency" in action_ids
        # All critical or high
        priorities = {a["priority"] for a in plan if a["recommended_action"] in action_ids}
        assert "low" not in priorities


class TestIntegrationNormalOperations:
    """正常航行: 所有指标正常 → 无告警 action (baseline monitor)。"""

    def test_integration_normal_operations(self, orchestrator):
        hull_ch = MagicMock()
        hull_ch.get_structural_health.return_value = {
            "stress_ratio": 0.3, "alarm_active": False,
        }
        power_ch = MagicMock()
        power_ch.get_power_balance.return_value = {
            "load_shedding_needed": False, "reserve_percent": 45.0,
        }
        echo_ch = MagicMock()
        echo_ch.get_depth_status.return_value = {
            "grounding_risk": False, "shallow_alarm": False,
        }
        prop_ch = MagicMock()
        prop_ch.get_propulsion_status.return_value = {
            "any_alarm": False, "efficiency_percent": 85,
        }
        gyro_ch = MagicMock()
        gyro_ch.get_heading_consensus.return_value = {"agreement": True}
        ap_ch = MagicMock()
        ap_ch.get_autopilot_status.return_value = {"on_course": True}
        moor_ch = MagicMock()
        moor_ch.get_mooring_status.return_value = {"any_parted": False}
        comms_ch = MagicMock()
        comms_ch.get_status.return_value = {
            "gmdss_compliant": True, "distress_active": False,
        }
        bilge_ch = MagicMock()
        bilge_ch.get_status.return_value = {"marpol_compliant": True}
        rudder_ch = MagicMock()
        rudder_ch.get_status.return_value = {"solas_compliant": True}
        tank_ch = MagicMock()
        tank_ch.get_tank_summary.return_value = {
            "low_level_alarms": [], "tanks": {},
        }
        alarm_ch = MagicMock()
        alarm_ch.get_alarm_summary.return_value = {"emergency_count": 0}

        registry = _mock_registry_with({
            "hull_stress_monitor": hull_ch,
            "power_management": power_ch,
            "echo_sounder_monitor": echo_ch,
            "propulsion_monitor": prop_ch,
            "gyro_compass_monitor": gyro_ch,
            "autopilot_monitor": ap_ch,
            "mooring_monitor": moor_ch,
            "communication_manager": comms_ch,
            "bilge_water_monitor": bilge_ch,
            "rudder_control_monitor": rudder_ch,
            "tank_level_monitor": tank_ch,
            "alarm_management": alarm_ch,
        })

        with patch(
            "backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orchestrator._build_action_plan(snapshot={})

        # Should fall through to baseline monitor
        assert len(plan) == 1
        assert plan[0]["id"] == "ops-monitor"
        assert plan[0]["priority"] == "low"


class TestIntegrationPowerFailure:
    """电力故障: power load_shedding + propulsion alarm。"""

    def test_integration_power_failure(self, orchestrator):
        power_ch = MagicMock()
        power_ch.get_power_balance.return_value = {
            "load_shedding_needed": True, "reserve_percent": 8.0,
        }
        prop_ch = MagicMock()
        prop_ch.get_propulsion_status.return_value = {
            "any_alarm": True, "efficiency_percent": 10,
        }

        registry = _mock_registry_with({
            "power_management": power_ch,
            "propulsion_monitor": prop_ch,
        })

        with patch(
            "backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orchestrator._build_action_plan(snapshot={})

        action_ids = {a["recommended_action"] for a in plan}
        assert "load_shedding_required" in action_ids
        assert "propulsion_alarm" in action_ids
        assert "low_propulsion_efficiency" in action_ids


class TestIntegrationNavigationFailure:
    """导航故障: gyro disagreement + autopilot off course + echo grounding。"""

    def test_integration_navigation_failure(self, orchestrator):
        gyro_ch = MagicMock()
        gyro_ch.get_heading_consensus.return_value = {"agreement": False}
        ap_ch = MagicMock()
        ap_ch.get_autopilot_status.return_value = {"on_course": False}
        echo_ch = MagicMock()
        echo_ch.get_depth_status.return_value = {
            "grounding_risk": True, "shallow_alarm": True,
        }

        registry = _mock_registry_with({
            "gyro_compass_monitor": gyro_ch,
            "autopilot_monitor": ap_ch,
            "echo_sounder_monitor": echo_ch,
        })

        with patch(
            "backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orchestrator._build_action_plan(snapshot={})

        action_ids = {a["recommended_action"] for a in plan}
        assert "heading_disagreement" in action_ids
        assert "off_course_warning" in action_ids
        assert "grounding_risk_alert" in action_ids
        assert "shallow_water_warning" in action_ids
        # grounding_risk should be critical
        grounding = [a for a in plan if a["recommended_action"] == "grounding_risk_alert"]
        assert grounding[0]["priority"] == "critical"


class TestIntegrationComplianceCheck:
    """合规总检: MARPOL + GMDSS + SOLAS rudder + lights → 各合规状态。"""

    def test_integration_compliance_check_all_non_compliant(self, orchestrator):
        bilge_ch = MagicMock()
        bilge_ch.get_status.return_value = {"marpol_compliant": False}
        comms_ch = MagicMock()
        comms_ch.get_status.return_value = {
            "gmdss_compliant": False, "distress_active": False,
        }
        rudder_ch = MagicMock()
        rudder_ch.get_status.return_value = {"solas_compliant": False}

        registry = _mock_registry_with({
            "bilge_water_monitor": bilge_ch,
            "communication_manager": comms_ch,
            "rudder_control_monitor": rudder_ch,
        })

        with patch(
            "backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orchestrator._build_action_plan(snapshot={})

        action_ids = {a["recommended_action"] for a in plan}
        assert "marpol_violation_bilge" in action_ids
        assert "gmdss_non_compliant" in action_ids
        assert "steering_fault" in action_ids

    def test_integration_compliance_check_all_compliant(self, orchestrator):
        bilge_ch = MagicMock()
        bilge_ch.get_status.return_value = {"marpol_compliant": True}
        comms_ch = MagicMock()
        comms_ch.get_status.return_value = {
            "gmdss_compliant": True, "distress_active": False,
        }
        rudder_ch = MagicMock()
        rudder_ch.get_status.return_value = {"solas_compliant": True}

        registry = _mock_registry_with({
            "bilge_water_monitor": bilge_ch,
            "communication_manager": comms_ch,
            "rudder_control_monitor": rudder_ch,
        })

        with patch(
            "backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orchestrator._build_action_plan(snapshot={})

        action_ids = {a["recommended_action"] for a in plan}
        assert "marpol_violation_bilge" not in action_ids
        assert "gmdss_non_compliant" not in action_ids
        assert "steering_fault" not in action_ids


class TestIntegrationMooringEmergency:
    """系泊紧急: mooring line parted + hull stress high。"""

    def test_integration_mooring_emergency(self, orchestrator):
        moor_ch = MagicMock()
        moor_ch.get_mooring_status.return_value = {"any_parted": True}
        hull_ch = MagicMock()
        hull_ch.get_structural_health.return_value = {
            "stress_ratio": 0.85, "alarm_active": False,
        }

        registry = _mock_registry_with({
            "mooring_monitor": moor_ch,
            "hull_stress_monitor": hull_ch,
        })

        with patch(
            "backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orchestrator._build_action_plan(snapshot={})

        action_ids = {a["recommended_action"] for a in plan}
        assert "mooring_line_parted" in action_ids
        assert "reduce_speed_hull_stress" in action_ids
        mooring_action = [a for a in plan if a["recommended_action"] == "mooring_line_parted"]
        assert mooring_action[0]["priority"] == "critical"


class TestIntegrationTankFuelLow:
    """燃油低 + alarm emergency → 多重告警。"""

    def test_integration_tank_and_alarm(self, orchestrator):
        tank_ch = MagicMock()
        tank_ch.get_tank_summary.return_value = {
            "low_level_alarms": ["FO1"],
            "tanks": {"FO1": {"type": "fuel_oil"}},
        }
        alarm_ch = MagicMock()
        alarm_ch.get_alarm_summary.return_value = {"emergency_count": 1}

        registry = _mock_registry_with({
            "tank_level_monitor": tank_ch,
            "alarm_management": alarm_ch,
        })

        with patch(
            "backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orchestrator._build_action_plan(snapshot={})

        action_ids = {a["recommended_action"] for a in plan}
        assert "low_fuel_warning" in action_ids
        assert "emergency_alarm_active" in action_ids


class TestIntegrationActionPlanPrioritySort:
    """验证 action plan 按优先级排序 (critical → high → medium → low)。"""

    def test_integration_action_plan_priority_sort(self, orchestrator):
        echo_ch = MagicMock()
        echo_ch.get_depth_status.return_value = {
            "grounding_risk": True, "shallow_alarm": True,
        }
        gyro_ch = MagicMock()
        gyro_ch.get_heading_consensus.return_value = {"agreement": False}

        registry = _mock_registry_with({
            "echo_sounder_monitor": echo_ch,
            "gyro_compass_monitor": gyro_ch,
        })

        with patch(
            "backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orchestrator._build_action_plan(snapshot={})

        # Verify sorted: critical actions before high actions
        priorities = [a["priority"] for a in plan]
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        for i in range(len(priorities) - 1):
            assert priority_order[priorities[i]] <= priority_order[priorities[i + 1]]
