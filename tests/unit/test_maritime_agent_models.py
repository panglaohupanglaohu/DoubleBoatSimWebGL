# -*- coding: utf-8 -*-
"""Tests for maritime domain enhancements in agent models."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "backend"))

from agents.models import (
    AgentTemplateType,
    COLREGS_RULES,
    MASSLevel,
    SkillCategory,
    ToolCategory,
)


class TestMaritimeTemplateTypes:
    """Verify maritime-specific agent templates."""

    def test_navigator_exists(self):
        assert AgentTemplateType.NAVIGATOR.value == "navigator"

    def test_engineer_exists(self):
        assert AgentTemplateType.ENGINEER.value == "engineer"

    def test_safety_officer_exists(self):
        assert AgentTemplateType.SAFETY_OFFICER.value == "safety_officer"

    def test_helmsman_exists(self):
        assert AgentTemplateType.HELMSMAN.value == "helmsman"

    def test_all_original_templates_preserved(self):
        names = {t.value for t in AgentTemplateType}
        for expected in ("researcher", "developer", "analyst", "coordinator", "custom"):
            assert expected in names, f"{expected} template missing"


class TestMaritimeToolCategories:
    """Verify maritime tool categories."""

    def test_chart_tools(self):
        assert ToolCategory.CHART_TOOLS.value == "chart_tools"

    def test_ais_tools(self):
        assert ToolCategory.AIS_TOOLS.value == "ais_tools"

    def test_weather_tools(self):
        assert ToolCategory.WEATHER_TOOLS.value == "weather_tools"

    def test_engine_tools(self):
        assert ToolCategory.ENGINE_TOOLS.value == "engine_tools"

    def test_original_categories_preserved(self):
        names = {c.value for c in ToolCategory}
        for expected in ("browser", "code_execution", "maritime", "digital_twin"):
            assert expected in names


class TestMaritimeSkillCategories:
    """Verify maritime skill categories."""

    def test_navigation(self):
        assert SkillCategory.NAVIGATION.value == "navigation"

    def test_collision_avoidance(self):
        assert SkillCategory.COLLISION_AVOIDANCE.value == "collision_avoidance"

    def test_propulsion(self):
        assert SkillCategory.PROPULSION.value == "propulsion"

    def test_weather_analysis(self):
        assert SkillCategory.WEATHER_ANALYSIS.value == "weather_analysis"

    def test_cargo_management(self):
        assert SkillCategory.CARGO_MANAGEMENT.value == "cargo_management"

    def test_ship_communication(self):
        assert SkillCategory.SHIP_COMMUNICATION.value == "ship_communication"


class TestMASSLevels:
    """Verify IMO MASS autonomy levels per MSC.107(98)."""

    def test_degree_1(self):
        assert MASSLevel.DEGREE_1.value == 1

    def test_degree_2(self):
        assert MASSLevel.DEGREE_2.value == 2

    def test_degree_3(self):
        assert MASSLevel.DEGREE_3.value == 3

    def test_degree_4(self):
        assert MASSLevel.DEGREE_4.value == 4

    def test_four_levels(self):
        assert len(MASSLevel) == 4


class TestCOLREGSRules:
    """Verify COLREGs rule constants."""

    def test_rule_5_lookout(self):
        assert COLREGS_RULES[5] == "Look-out"

    def test_rule_14_head_on(self):
        assert COLREGS_RULES[14] == "Head-on situation"

    def test_rule_15_crossing(self):
        assert COLREGS_RULES[15] == "Crossing situation"

    def test_rule_19_restricted_visibility(self):
        assert COLREGS_RULES[19] == "Conduct in restricted visibility"

    def test_core_rules_present(self):
        for rule in (5, 6, 7, 8, 13, 14, 15, 16, 17, 18, 19):
            assert rule in COLREGS_RULES, f"Rule {rule} missing"


class TestTaskEngine:
    """Verify task engine data structures."""

    def test_task_engine_import(self):
        from agents.task_engine import AgentTask, TaskEngine, TaskStatus
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"

    def test_agent_task_creation(self):
        from agents.task_engine import AgentTask
        t = AgentTask(title="test", agent_id="a1", team_id="t1")
        assert t.task_id  # auto-generated
        assert t.created_at  # auto-set

    def test_task_engine_singleton(self):
        from agents.task_engine import get_task_engine
        e1 = get_task_engine()
        e2 = get_task_engine()
        assert e1 is e2
