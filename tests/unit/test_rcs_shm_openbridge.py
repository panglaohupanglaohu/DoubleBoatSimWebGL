# -*- coding: utf-8 -*-
"""
RCS Control / Structural Health Monitor / OpenBridge Command Router 单元测试
"""

import pytest
from channels.rcs_control import RCSControlChannel
from channels.structural_health_monitor import StructuralHealthMonitorChannel
from channels.openbridge_command_router import (
    classify_openbridge_intent,
    build_openbridge_command_result,
)
from channels.marine_base import ChannelStatus


class TestRCSControl:
    def test_init(self):
        ch = RCSControlChannel()
        assert ch.name == "rcs_control"

    def test_initialize(self):
        ch = RCSControlChannel()
        assert ch.initialize() is True

    def test_shutdown(self):
        ch = RCSControlChannel()
        ch.initialize()
        assert ch.shutdown() is True

    def test_compute_control_state(self):
        ch = RCSControlChannel()
        ch.initialize()
        state = ch.compute_control_state()
        assert isinstance(state, dict)
        assert "foil_angle_deg" in state
        assert "trim_tab_angle_deg" in state
        assert "stability_margin" in state

    def test_compute_control_state_all_fields(self):
        ch = RCSControlChannel()
        ch.initialize()
        state = ch.compute_control_state()
        expected_keys = {
            "control_mode", "foil_angle_deg", "trim_tab_angle_deg",
            "roll_rate_cmd", "heave_damping_gain", "comfort_target_msdv",
            "stability_margin", "traffic_factor", "risk_basis",
        }
        assert expected_keys.issubset(set(state.keys()))

    def test_compute_control_state_value_ranges(self):
        ch = RCSControlChannel()
        ch.initialize()
        state = ch.compute_control_state()
        # foil angle: 1.5 (safe, 0 traffic) to 1.5+5.5+1.5=8.5 (danger, full traffic)
        assert 1.0 <= state["foil_angle_deg"] <= 9.0
        # trim tab angle: 1.0 to 1.0+4.0+1.2=6.2
        assert 0.5 <= state["trim_tab_angle_deg"] <= 7.0
        # stability_margin: max(0.1, 1.0 - weight*0.45); always positive
        assert 0.0 < state["stability_margin"] <= 1.0
        # traffic_factor: 0.0 to 1.0
        assert 0.0 <= state["traffic_factor"] <= 1.0
        # comfort_target_msdv: max(0.15, 0.55 - 0.2*weight)
        assert 0.0 < state["comfort_target_msdv"] <= 0.6

    def test_compute_control_state_types(self):
        ch = RCSControlChannel()
        ch.initialize()
        state = ch.compute_control_state()
        assert isinstance(state["foil_angle_deg"], float)
        assert isinstance(state["trim_tab_angle_deg"], float)
        assert isinstance(state["stability_margin"], float)
        assert isinstance(state["control_mode"], str)
        assert isinstance(state["risk_basis"], str)

    def test_get_status(self):
        ch = RCSControlChannel()
        ch.initialize()
        status = ch.get_status()
        assert isinstance(status, dict)
        assert "health" in status

    def test_get_status_contains_control_fields(self):
        ch = RCSControlChannel()
        ch.initialize()
        status = ch.get_status()
        assert "foil_angle_deg" in status
        assert "trim_tab_angle_deg" in status
        assert "stability_margin" in status
        assert status["name"] == "rcs_control"
        assert status["initialized"] is True

    def test_shutdown_marks_uninitialized(self):
        ch = RCSControlChannel()
        ch.initialize()
        assert ch._initialized is True
        ch.shutdown()
        assert ch._initialized is False

    def test_health_after_initialize(self):
        ch = RCSControlChannel()
        ch.initialize()
        assert ch._health.status == ChannelStatus.OK

    def test_health_after_shutdown(self):
        ch = RCSControlChannel()
        ch.initialize()
        ch.shutdown()
        assert ch._health.status == ChannelStatus.OFF


class TestStructuralHealthMonitor:
    def test_init(self):
        ch = StructuralHealthMonitorChannel()
        assert ch.name == "structural_health_monitor"

    def test_initialize(self):
        ch = StructuralHealthMonitorChannel()
        assert ch.initialize() is True

    def test_shutdown(self):
        ch = StructuralHealthMonitorChannel()
        ch.initialize()
        assert ch.shutdown() is True

    def test_compute_health_state(self):
        ch = StructuralHealthMonitorChannel()
        ch.initialize()
        state = ch.compute_health_state()
        assert isinstance(state, dict)
        assert "fatigue_damage_index" in state
        assert "life_remaining_pct" in state

    def test_compute_health_state_all_fields(self):
        ch = StructuralHealthMonitorChannel()
        ch.initialize()
        state = ch.compute_health_state()
        expected_keys = {
            "longitudinal_bending_moment_kNm", "torsion_kNm",
            "fatigue_damage_index", "life_remaining_pct",
            "fbg_status", "strain_hotspots",
        }
        assert expected_keys.issubset(set(state.keys()))

    def test_compute_health_state_value_ranges(self):
        ch = StructuralHealthMonitorChannel()
        ch.initialize()
        state = ch.compute_health_state()
        # fatigue_damage_index: min(0.95, 0.12 + ...) so between 0 and 0.95
        assert 0.0 <= state["fatigue_damage_index"] <= 0.95
        # life_remaining_pct: max(35.0, ...)
        assert 35.0 <= state["life_remaining_pct"] <= 100.0
        # bending moment and torsion should be positive
        assert state["longitudinal_bending_moment_kNm"] > 0
        assert state["torsion_kNm"] > 0

    def test_compute_health_state_strain_hotspots(self):
        ch = StructuralHealthMonitorChannel()
        ch.initialize()
        state = ch.compute_health_state()
        hotspots = state["strain_hotspots"]
        assert isinstance(hotspots, list)
        assert len(hotspots) == 3
        zones = {h["zone"] for h in hotspots}
        assert "bridge_joint" in zones
        assert "port_bow" in zones
        assert "starboard_bow" in zones
        for h in hotspots:
            assert "microstrain" in h
            assert isinstance(h["microstrain"], float)
            assert h["microstrain"] > 0

    def test_compute_health_state_fbg_online(self):
        ch = StructuralHealthMonitorChannel()
        ch.initialize()
        state = ch.compute_health_state()
        assert state["fbg_status"] == "online"

    def test_get_status(self):
        ch = StructuralHealthMonitorChannel()
        ch.initialize()
        status = ch.get_status()
        assert isinstance(status, dict)
        assert "health" in status

    def test_get_status_contains_health_fields(self):
        ch = StructuralHealthMonitorChannel()
        ch.initialize()
        status = ch.get_status()
        assert "fatigue_damage_index" in status
        assert "life_remaining_pct" in status
        assert "strain_hotspots" in status
        assert status["name"] == "structural_health_monitor"
        assert status["initialized"] is True

    def test_shutdown_marks_uninitialized(self):
        ch = StructuralHealthMonitorChannel()
        ch.initialize()
        ch.shutdown()
        assert ch._initialized is False

    def test_health_after_initialize(self):
        ch = StructuralHealthMonitorChannel()
        ch.initialize()
        assert ch._health.status == ChannelStatus.OK

    def test_health_after_shutdown(self):
        ch = StructuralHealthMonitorChannel()
        ch.initialize()
        ch.shutdown()
        assert ch._health.status == ChannelStatus.OFF


class TestOpenBridgeCommandRouter:
    def test_classify_navigation_intent(self):
        result = classify_openbridge_intent("change course to 180")
        assert isinstance(result, dict)
        assert "intent" in result
        assert "domain" in result

    def test_classify_engine_intent(self):
        result = classify_openbridge_intent("increase engine speed")
        assert isinstance(result, dict)
        assert "intent" in result

    def test_classify_task_graph_intent(self):
        for cmd in ["show task graph", "任务图", "mission brief", "查看计划"]:
            result = classify_openbridge_intent(cmd)
            assert result["intent"] == "show_task_graph"
            assert result["domain"] == "decision"

    def test_classify_collision_risk_intent(self):
        for cmd in ["碰撞风险", "colregs check", "ais targets", "避碰"]:
            result = classify_openbridge_intent(cmd)
            assert result["intent"] == "show_collision_risk"
            assert result["domain"] == "navigation"

    def test_classify_rcs_intent(self):
        for cmd in ["舒适模式", "减摇", "foil angle", "rcs 平稳", "trim tabs", "姿态控制"]:
            result = classify_openbridge_intent(cmd)
            assert result["intent"] == "set_comfort_mode", f"命令 '{cmd}' 未匹配到 set_comfort_mode"
            assert result["domain"] == "rcs"

    def test_classify_shm_intent(self):
        for cmd in ["结构健康", "shm report", "疲劳损伤", "应变监测", "寿命余度", "弯矩"]:
            result = classify_openbridge_intent(cmd)
            assert result["intent"] == "show_structural_health", f"命令 '{cmd}' 未匹配到 show_structural_health"
            assert result["domain"] == "shm"

    def test_classify_engine_health_intent(self):
        for cmd in ["主机状态", "机舱健康", "engine maintenance", "维护建议"]:
            result = classify_openbridge_intent(cmd)
            assert result["intent"] == "show_engine_health"
            assert result["domain"] == "engine"

    def test_classify_fallback_general_intent(self):
        result = classify_openbridge_intent("hello")
        assert result["intent"] == "general_assist"
        assert result["domain"] == "general"

    def test_classify_empty_command(self):
        result = classify_openbridge_intent("")
        assert result["intent"] == "general_assist"

    def test_classify_none_command(self):
        result = classify_openbridge_intent(None)
        assert result["intent"] == "general_assist"

    def test_classify_result_has_required_fields(self):
        result = classify_openbridge_intent("show task graph")
        assert "intent" in result
        assert "domain" in result
        assert "mode" in result
        assert "operator_action" in result
        assert isinstance(result["operator_action"], str)
        assert len(result["operator_action"]) > 0

    def test_build_command_result(self):
        dashboard = {"captain_agent": {}, "compliance": {}, "perception": {}}
        mission = {"mission_brief": {}, "action_plan": []}
        result = build_openbridge_command_result("check weather", dashboard, mission)
        assert isinstance(result, dict)
        assert "command" in result
        assert result["command"] == "check weather"
        assert "recognized_intent" in result

    def test_build_command_result_structure(self):
        dashboard = {}
        mission = {"autonomy_mode": "supervised"}
        result = build_openbridge_command_result("任务图", dashboard, mission)
        required_keys = {
            "command", "recognized_intent", "domain", "execution_mode",
            "operator_action", "summary", "task_graph", "control_state", "focus_items",
        }
        assert required_keys.issubset(set(result.keys()))

    def test_build_command_result_rcs_domain(self):
        dashboard = {
            "rcs": {"foil_angle_deg": 4.5, "trim_tab_angle_deg": 3.2, "comfort_target_msdv": 0.35}
        }
        mission = {}
        result = build_openbridge_command_result("rcs 平稳", dashboard, mission)
        assert result["recognized_intent"] == "set_comfort_mode"
        assert result["control_state"]["rcs"]["foil_angle_deg"] == 4.5
        assert result["control_state"]["rcs"]["trim_tab_angle_deg"] == 3.2

    def test_build_command_result_shm_domain(self):
        dashboard = {
            "shm": {
                "fatigue_damage_index": 0.35,
                "life_remaining_pct": 72.5,
                "strain_hotspots": [{"zone": "bridge_joint", "microstrain": 145.0}],
            }
        }
        mission = {}
        result = build_openbridge_command_result("疲劳损伤", dashboard, mission)
        assert result["recognized_intent"] == "show_structural_health"
        assert result["control_state"]["shm"]["fatigue_damage_index"] == 0.35
        assert result["control_state"]["shm"]["life_remaining_pct"] == 72.5

    def test_build_command_result_task_graph(self):
        dashboard = {}
        mission = {
            "autonomy_mode": "semi-auto",
            "task_graph": {
                "nodes": [{"id": f"n{i}"} for i in range(7)],
                "execution_order": ["n0", "n1", "n2"],
            },
        }
        result = build_openbridge_command_result("任务", dashboard, mission)
        assert result["task_graph"]["node_count"] == 7
        assert result["task_graph"]["execution_order"] == ["n0", "n1", "n2"]
