# -*- coding: utf-8 -*-
"""
MOB + Safety System Monitor + 编排器最终整合测试

覆盖:
  - ManOverboardChannel: 激活/取消/搜救模式/生存估算/事件处理
  - SafetySystemMonitorChannel: 系统注册/水密门/SOLAS/检查/事件处理
  - DecisionOrchestratorChannel: echo_sounder/propulsion/gyro/autopilot/mooring 整合
"""

from __future__ import annotations

import asyncio
import time
from types import SimpleNamespace
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from src.backend.channels.man_overboard import (
    ManOverboardChannel,
    VALID_SEARCH_PATTERNS,
    _estimate_survival_hours,
)
from src.backend.channels.safety_system_monitor import (
    SafetySystemMonitorChannel,
    VALID_CATEGORIES,
    VALID_SYSTEM_STATUSES,
    VALID_DOOR_STATUSES,
)
from src.backend.channels.decision_orchestrator import (
    DecisionOrchestratorChannel,
)


def _run(coro):
    """Run an async coroutine synchronously."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ────────────────────────────────── MOB Tests ──────────────────────────────────


class TestManOverboard:
    """ManOverboardChannel 单元测试 (18 tests)."""

    def _make(self) -> ManOverboardChannel:
        ch = ManOverboardChannel()
        ch.initialize()
        return ch

    def test_mob_init(self):
        ch = ManOverboardChannel()
        assert ch._mob_active is False
        assert ch._mob_position is None
        assert ch._search_pattern == "none"

    def test_mob_activate(self):
        ch = self._make()
        result = ch.activate_mob(31.0, 121.5)
        assert result["status"] == "mob_activated"
        assert ch._mob_active is True
        assert ch._mob_position["lat"] == 31.0
        assert ch._mob_position["lon"] == 121.5

    def test_mob_activate_sets_search_pattern(self):
        ch = self._make()
        ch.activate_mob(31.0, 121.5)
        assert ch._search_pattern == "williamson_turn"

    def test_mob_deactivate(self):
        ch = self._make()
        ch.activate_mob(31.0, 121.5)
        result = ch.deactivate_mob()
        assert result["status"] == "mob_deactivated"
        assert ch._mob_active is False
        assert ch._mob_position is None
        assert ch._search_pattern == "none"

    def test_mob_double_activate(self):
        ch = self._make()
        ch.activate_mob(31.0, 121.5)
        result = ch.activate_mob(32.0, 122.0)
        assert result["status"] == "mob_activated"
        assert ch._mob_position["lat"] == 32.0

    def test_mob_add_marker(self):
        ch = self._make()
        ch.activate_mob(31.0, 121.5)
        result = ch.add_mob_marker(31.01, 121.51)
        assert result["status"] == "marker_added"
        assert result["total_markers"] == 1

    def test_mob_multiple_markers(self):
        ch = self._make()
        ch.activate_mob(31.0, 121.5)
        ch.add_mob_marker(31.01, 121.51)
        ch.add_mob_marker(31.02, 121.52)
        result = ch.add_mob_marker(31.03, 121.53)
        assert result["total_markers"] == 3

    def test_mob_status_structure(self):
        ch = self._make()
        ch.activate_mob(31.0, 121.5)
        status = ch.get_mob_status()
        assert "mob_active" in status
        assert "mob_position" in status
        assert "elapsed_minutes" in status
        assert "search_pattern" in status
        assert "markers_count" in status
        assert "survival_estimate" in status

    def test_mob_elapsed_minutes(self):
        ch = self._make()
        ch.activate_mob(31.0, 121.5)
        # Force activation timestamp to 120 seconds ago
        ch._mob_activated_at = time.time() - 120
        elapsed = ch._elapsed_minutes()
        assert 1.5 <= elapsed <= 2.5

    def test_mob_elapsed_minutes_inactive(self):
        ch = self._make()
        assert ch._elapsed_minutes() == 0.0

    def test_mob_set_search_pattern(self):
        ch = self._make()
        result = ch.set_search_pattern("anderson_turn")
        assert result["status"] == "pattern_set"
        assert ch._search_pattern == "anderson_turn"

    def test_mob_search_patterns_all(self):
        ch = self._make()
        for pattern in VALID_SEARCH_PATTERNS:
            result = ch.set_search_pattern(pattern)
            assert result["status"] == "pattern_set"

    def test_mob_search_pattern_invalid(self):
        ch = self._make()
        result = ch.set_search_pattern("invalid_pattern")
        assert result["status"] == "error"

    def test_mob_survival_estimate(self):
        ch = self._make()
        ch._water_temp_c = 5.0
        status = ch.get_mob_status()
        assert status["survival_estimate"]["water_temp_c"] == 5.0
        assert status["survival_estimate"]["estimated_hours"] > 0

    def test_mob_survival_cold(self):
        hours = _estimate_survival_hours(1.0)
        assert hours == 0.75

    def test_mob_survival_warm(self):
        hours = _estimate_survival_hours(30.0)
        assert hours == 24.0

    def test_mob_process_event_alert(self):
        ch = self._make()
        result = _run(ch.process_event({"type": "mob_alert", "lat": 31.0, "lon": 121.5}))
        assert result["status"] == "mob_activated"
        assert ch._mob_active is True

    def test_mob_process_event_cancel(self):
        ch = self._make()
        ch.activate_mob(31.0, 121.5)
        result = _run(ch.process_event({"type": "mob_cancel"}))
        assert result["status"] == "mob_deactivated"

    def test_mob_process_event_missing_coords(self):
        ch = self._make()
        result = _run(ch.process_event({"type": "mob_alert"}))
        assert result["status"] == "error"

    def test_mob_process_event_unknown(self):
        ch = self._make()
        result = _run(ch.process_event({"type": "some_other"}))
        assert result["status"] == "ignored"

    def test_mob_get_status(self):
        ch = self._make()
        ch.activate_mob(31.0, 121.5)
        status = ch.get_status()
        assert status["name"] == "man_overboard"
        assert status["mob_active"] is True
        assert "health" in status
        assert "elapsed_minutes" in status


# ──────────────────────── Safety System Monitor Tests ──────────────────────────


class TestSafetySystemMonitor:
    """SafetySystemMonitorChannel 单元测试 (18 tests)."""

    def _make(self) -> SafetySystemMonitorChannel:
        ch = SafetySystemMonitorChannel()
        ch.initialize()
        return ch

    def test_safety_init(self):
        ch = SafetySystemMonitorChannel()
        assert ch._active is False
        assert ch._systems == {}
        assert ch._watertight_doors == {}

    def test_safety_init_active_after_initialize(self):
        ch = self._make()
        assert ch._active is True
        assert ch._initialized is True

    def test_safety_add_system(self):
        ch = self._make()
        result = ch.update_system("liferaft_01", "life_saving", "ready")
        assert result["status"] == "updated"
        assert "liferaft_01" in ch._systems

    def test_safety_update_system_ready(self):
        ch = self._make()
        ch.update_system("fire_pump_01", "fire_fighting", "not_ready")
        ch.update_system("fire_pump_01", "fire_fighting", "ready")
        assert ch._systems["fire_pump_01"]["status"] == "ready"

    def test_safety_update_system_fault(self):
        ch = self._make()
        ch.update_system("liferaft_01", "life_saving", "fault")
        assert ch._systems["liferaft_01"]["status"] == "fault"

    def test_safety_invalid_category(self):
        ch = self._make()
        result = ch.update_system("x", "invalid_cat", "ready")
        assert result["status"] == "error"

    def test_safety_invalid_status(self):
        ch = self._make()
        result = ch.update_system("x", "life_saving", "broken")
        assert result["status"] == "error"

    def test_safety_multiple_systems(self):
        ch = self._make()
        ch.update_system("liferaft_01", "life_saving", "ready")
        ch.update_system("fire_pump_01", "fire_fighting", "ready")
        ch.update_system("door_01", "watertight", "ready")
        assert len(ch._systems) == 3

    def test_safety_door_closed(self):
        ch = self._make()
        result = ch.update_watertight_door("WT_D01", "Frame 42", "closed")
        assert result["status"] == "updated"
        assert ch._watertight_doors["WT_D01"]["alarm_active"] is False

    def test_safety_door_open(self):
        ch = self._make()
        ch.update_watertight_door("WT_D01", "Frame 42", "open")
        assert ch._watertight_doors["WT_D01"]["alarm_active"] is True

    def test_safety_door_invalid(self):
        ch = self._make()
        result = ch.update_watertight_door("WT_D01", "Frame 42", "broken")
        assert result["status"] == "error"

    def test_safety_watertight_integrity(self):
        ch = self._make()
        ch.update_watertight_door("WT_D01", "Frame 42", "closed")
        ch.update_watertight_door("WT_D02", "Frame 56", "closed")
        safety = ch.get_safety_status()
        assert safety["watertight_integrity"] is True

    def test_safety_watertight_breach(self):
        ch = self._make()
        ch.update_watertight_door("WT_D01", "Frame 42", "closed")
        ch.update_watertight_door("WT_D02", "Frame 56", "open")
        safety = ch.get_safety_status()
        assert safety["watertight_integrity"] is False

    def test_safety_solas_ready(self):
        ch = self._make()
        ch.update_system("liferaft_01", "life_saving", "ready")
        ch.update_watertight_door("WT_D01", "Frame 42", "closed")
        safety = ch.get_safety_status()
        assert safety["solas_ready"] is True

    def test_safety_solas_not_ready_fault(self):
        ch = self._make()
        ch.update_system("liferaft_01", "life_saving", "fault")
        ch.update_watertight_door("WT_D01", "Frame 42", "closed")
        safety = ch.get_safety_status()
        assert safety["solas_ready"] is False

    def test_safety_solas_not_ready_door(self):
        ch = self._make()
        ch.update_system("liferaft_01", "life_saving", "ready")
        ch.update_watertight_door("WT_D01", "Frame 42", "open")
        safety = ch.get_safety_status()
        assert safety["solas_ready"] is False

    def test_safety_inspection_tracking(self):
        ch = self._make()
        ch.update_system("liferaft_01", "life_saving", "inspection_due",
                         next_inspection="2026-06-01")
        safety = ch.get_safety_status()
        assert "liferaft_01" in safety["inspections_due"]

    def test_safety_process_event_system(self):
        ch = self._make()
        result = _run(ch.process_event({
            "type": "safety_system_update",
            "system_id": "fire_pump_01",
            "category": "fire_fighting",
            "status": "ready",
        }))
        assert result["status"] == "updated"

    def test_safety_process_event_door(self):
        ch = self._make()
        result = _run(ch.process_event({
            "type": "watertight_door_update",
            "door_id": "WT_D01",
            "location": "Frame 42",
            "door_status": "closed",
        }))
        assert result["status"] == "updated"

    def test_safety_process_event_missing_fields(self):
        ch = self._make()
        result = _run(ch.process_event({
            "type": "safety_system_update",
            "system_id": "x",
        }))
        assert result["status"] == "error"

    def test_safety_process_event_unknown(self):
        ch = self._make()
        result = _run(ch.process_event({"type": "unknown_type"}))
        assert result["status"] == "ignored"

    def test_safety_get_status(self):
        ch = self._make()
        ch.update_system("liferaft_01", "life_saving", "ready")
        status = ch.get_status()
        assert status["name"] == "safety_system_monitor"
        assert "solas_ready" in status
        assert "watertight_integrity" in status
        assert "systems_count" in status


# ──────────────── Orchestrator Final Integration Tests ────────────────────────


def _mock_registry_with(channels: Dict[str, Any]):
    """Create a mock registry that returns given channel mocks by name."""
    registry = MagicMock()
    registry.get = lambda name: channels.get(name)
    return registry


class TestOrchestratorEchoSounder:
    """Echo sounder → grounding_risk / shallow_water 整合."""

    def _build_with_echo(self, grounding_risk=False, shallow_alarm=False):
        echo_ch = MagicMock()
        echo_ch.get_depth_status.return_value = {
            "grounding_risk": grounding_risk,
            "shallow_alarm": shallow_alarm,
        }
        registry = _mock_registry_with({"echo_sounder_monitor": echo_ch})

        orch = DecisionOrchestratorChannel()
        orch.initialize()
        with patch(
            "src.backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orch._build_action_plan({})
        return plan

    def test_orch_echo_grounding_risk(self):
        plan = self._build_with_echo(grounding_risk=True)
        actions = [a["recommended_action"] for a in plan]
        assert "grounding_risk_alert" in actions

    def test_orch_echo_shallow(self):
        plan = self._build_with_echo(shallow_alarm=True)
        actions = [a["recommended_action"] for a in plan]
        assert "shallow_water_warning" in actions

    def test_orch_echo_both(self):
        plan = self._build_with_echo(grounding_risk=True, shallow_alarm=True)
        actions = [a["recommended_action"] for a in plan]
        assert "grounding_risk_alert" in actions
        assert "shallow_water_warning" in actions

    def test_orch_echo_normal(self):
        plan = self._build_with_echo(grounding_risk=False, shallow_alarm=False)
        actions = [a["recommended_action"] for a in plan]
        assert "grounding_risk_alert" not in actions
        assert "shallow_water_warning" not in actions


class TestOrchestratorPropulsion:
    """Propulsion → propulsion_alarm / low_propulsion_efficiency 整合."""

    def _build_with_propulsion(self, any_alarm=False, efficiency_percent=90):
        prop_ch = MagicMock()
        prop_ch.get_propulsion_status.return_value = {
            "any_alarm": any_alarm,
            "efficiency_percent": efficiency_percent,
        }
        registry = _mock_registry_with({"propulsion_monitor": prop_ch})

        orch = DecisionOrchestratorChannel()
        orch.initialize()
        with patch(
            "src.backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orch._build_action_plan({})
        return plan

    def test_orch_propulsion_alarm(self):
        plan = self._build_with_propulsion(any_alarm=True)
        actions = [a["recommended_action"] for a in plan]
        assert "propulsion_alarm" in actions

    def test_orch_propulsion_low_efficiency(self):
        plan = self._build_with_propulsion(efficiency_percent=20)
        actions = [a["recommended_action"] for a in plan]
        assert "low_propulsion_efficiency" in actions

    def test_orch_propulsion_normal(self):
        plan = self._build_with_propulsion(any_alarm=False, efficiency_percent=90)
        actions = [a["recommended_action"] for a in plan]
        assert "propulsion_alarm" not in actions
        assert "low_propulsion_efficiency" not in actions


class TestOrchestratorGyro:
    """Gyro compass → heading_disagreement 整合."""

    def _build_with_gyro(self, agreement=True):
        gyro_ch = MagicMock()
        gyro_ch.get_heading_consensus.return_value = {"agreement": agreement}
        registry = _mock_registry_with({"gyro_compass_monitor": gyro_ch})

        orch = DecisionOrchestratorChannel()
        orch.initialize()
        with patch(
            "src.backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orch._build_action_plan({})
        return plan

    def test_orch_gyro_disagreement(self):
        plan = self._build_with_gyro(agreement=False)
        actions = [a["recommended_action"] for a in plan]
        assert "heading_disagreement" in actions

    def test_orch_gyro_agreement(self):
        plan = self._build_with_gyro(agreement=True)
        actions = [a["recommended_action"] for a in plan]
        assert "heading_disagreement" not in actions


class TestOrchestratorAutopilot:
    """Autopilot → off_course_warning 整合."""

    def _build_with_autopilot(self, on_course=True):
        ap_ch = MagicMock()
        ap_ch.get_autopilot_status.return_value = {"on_course": on_course}
        registry = _mock_registry_with({"autopilot_monitor": ap_ch})

        orch = DecisionOrchestratorChannel()
        orch.initialize()
        with patch(
            "src.backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orch._build_action_plan({})
        return plan

    def test_orch_autopilot_off_course(self):
        plan = self._build_with_autopilot(on_course=False)
        actions = [a["recommended_action"] for a in plan]
        assert "off_course_warning" in actions

    def test_orch_autopilot_on_course(self):
        plan = self._build_with_autopilot(on_course=True)
        actions = [a["recommended_action"] for a in plan]
        assert "off_course_warning" not in actions


class TestOrchestratorMooring:
    """Mooring → mooring_line_parted 整合."""

    def _build_with_mooring(self, any_parted=False):
        moor_ch = MagicMock()
        moor_ch.get_mooring_status.return_value = {"any_parted": any_parted}
        registry = _mock_registry_with({"mooring_monitor": moor_ch})

        orch = DecisionOrchestratorChannel()
        orch.initialize()
        with patch(
            "src.backend.channels.decision_orchestrator.get_default_registry",
            return_value=registry,
        ):
            plan = orch._build_action_plan({})
        return plan

    def test_orch_mooring_parted(self):
        plan = self._build_with_mooring(any_parted=True)
        actions = [a["recommended_action"] for a in plan]
        assert "mooring_line_parted" in actions

    def test_orch_mooring_secured(self):
        plan = self._build_with_mooring(any_parted=False)
        actions = [a["recommended_action"] for a in plan]
        assert "mooring_line_parted" not in actions
