# -*- coding: utf-8 -*-
"""
DecisionOrchestratorChannel 集成测试

覆盖:
- 天气风险 → action_plan
- 船员疲劳 → action_plan
- 优雅降级（Channel 缺失 / None 参数）
- mission_brief 新字段
- 向后兼容（不传新参数）
"""

import pytest
from backend.channels.decision_orchestrator import DecisionOrchestratorChannel


@pytest.fixture()
def orchestrator():
    ch = DecisionOrchestratorChannel()
    ch.initialize()
    return ch


# ── 1. 天气风险 ──────────────────────────────────────────────

class TestWeatherRiskActions:
    """当 weather_risk 达到阈值时，action_plan 应包含 review_route。"""

    def test_high_weather_risk_triggers_review_route(self, orchestrator):
        plan = orchestrator._build_action_plan(
            snapshot={},
            weather_risk={"risk_score": 80, "recommendation": "Storm ahead"},
        )
        review_actions = [a for a in plan if a["recommended_action"] == "review_route"]
        assert len(review_actions) == 1
        assert review_actions[0]["domain"] == "navigation"
        assert review_actions[0]["priority"] == "critical"

    def test_moderate_weather_risk_triggers_review_route(self, orchestrator):
        plan = orchestrator._build_action_plan(
            snapshot={},
            weather_risk={"risk_score": 65, "recommendation": "Moderate swell"},
        )
        review_actions = [a for a in plan if a["recommended_action"] == "review_route"]
        assert len(review_actions) == 1
        assert review_actions[0]["priority"] == "high"

    def test_low_weather_risk_no_review_route(self, orchestrator):
        plan = orchestrator._build_action_plan(
            snapshot={},
            weather_risk={"risk_score": 40},
        )
        review_actions = [a for a in plan if a["recommended_action"] == "review_route"]
        assert len(review_actions) == 0

    def test_boundary_weather_risk_60_no_review(self, orchestrator):
        plan = orchestrator._build_action_plan(
            snapshot={},
            weather_risk={"risk_score": 60},
        )
        review_actions = [a for a in plan if a["recommended_action"] == "review_route"]
        assert len(review_actions) == 0


# ── 2. 船员疲劳 ──────────────────────────────────────────────

class TestCrewFatigueActions:
    """当疲劳分 < 50 时，action_plan 应包含 recommend_watch_change。"""

    def test_low_fatigue_triggers_watch_change(self, orchestrator):
        plan = orchestrator._build_action_plan(
            snapshot={},
            crew_fatigue={"fatigue_scores": {"officer_A": 35}},
        )
        watch_actions = [a for a in plan if a["recommended_action"] == "recommend_watch_change"]
        assert len(watch_actions) == 1
        assert watch_actions[0]["domain"] == "crew"

    def test_critical_fatigue_below_30(self, orchestrator):
        plan = orchestrator._build_action_plan(
            snapshot={},
            crew_fatigue={"fatigue_scores": {"officer_A": 20}},
        )
        watch_actions = [a for a in plan if a["recommended_action"] == "recommend_watch_change"]
        assert len(watch_actions) == 1
        assert watch_actions[0]["priority"] == "critical"

    def test_multiple_fatigued_crew(self, orchestrator):
        plan = orchestrator._build_action_plan(
            snapshot={},
            crew_fatigue={"fatigue_scores": {"A": 30, "B": 40, "C": 80}},
        )
        watch_actions = [a for a in plan if a["recommended_action"] == "recommend_watch_change"]
        # A (30<50) and B (40<50) should trigger, C (80>=50) should not
        assert len(watch_actions) == 2

    def test_fatigue_above_50_no_action(self, orchestrator):
        plan = orchestrator._build_action_plan(
            snapshot={},
            crew_fatigue={"fatigue_scores": {"officer_A": 75}},
        )
        watch_actions = [a for a in plan if a["recommended_action"] == "recommend_watch_change"]
        assert len(watch_actions) == 0

    def test_fatigue_boundary_50_no_action(self, orchestrator):
        plan = orchestrator._build_action_plan(
            snapshot={},
            crew_fatigue={"fatigue_scores": {"officer_A": 50}},
        )
        watch_actions = [a for a in plan if a["recommended_action"] == "recommend_watch_change"]
        assert len(watch_actions) == 0


# ── 3. 优雅降级 ──────────────────────────────────────────────

class TestGracefulDegradation:
    """当 Channel 缺失或参数为 None 时不崩溃。"""

    def test_no_weather_routing_channel(self, orchestrator):
        # Registry 中无 weather_routing — build_decision_package 不崩溃
        pkg = orchestrator.build_decision_package()
        assert "action_plan" in pkg
        assert "weather_risk" in pkg

    def test_no_crew_fatigue_channel(self, orchestrator):
        pkg = orchestrator.build_decision_package()
        assert "crew_fatigue_alert" in pkg

    def test_weather_risk_none(self, orchestrator):
        plan = orchestrator._build_action_plan(snapshot={}, weather_risk=None)
        assert isinstance(plan, list)

    def test_crew_fatigue_none(self, orchestrator):
        plan = orchestrator._build_action_plan(snapshot={}, crew_fatigue=None)
        assert isinstance(plan, list)

    def test_both_none(self, orchestrator):
        plan = orchestrator._build_action_plan(snapshot={}, weather_risk=None, crew_fatigue=None)
        assert isinstance(plan, list)


# ── 4. mission_brief 新字段 ──────────────────────────────────

class TestMissionBriefFields:
    """mission_brief 应包含 weather_summary 和 crew_fatigue_warning。"""

    def test_weather_summary_present(self, orchestrator):
        pkg = orchestrator.build_decision_package()
        brief = pkg["mission_brief"]
        assert "weather_summary" in brief
        assert "risk_level" in brief["weather_summary"]

    def test_crew_fatigue_warning_present(self, orchestrator):
        pkg = orchestrator.build_decision_package()
        brief = pkg["mission_brief"]
        assert "crew_fatigue_warning" in brief
        assert "alerts" in brief["crew_fatigue_warning"]

    def test_weather_summary_with_data(self, orchestrator):
        """当无 weather_routing channel 时，weather_summary 仍有默认值。"""
        pkg = orchestrator.build_decision_package()
        ws = pkg["mission_brief"]["weather_summary"]
        assert ws["risk_level"] in ("unknown", "low", "medium", "high", "critical")

    def test_crew_fatigue_warning_with_data(self, orchestrator):
        pkg = orchestrator.build_decision_package()
        cfw = pkg["mission_brief"]["crew_fatigue_warning"]
        assert isinstance(cfw.get("total_crew", cfw.get("alerts")), (int, list))


# ── 5. 向后兼容 ──────────────────────────────────────────────

class TestBackwardCompatibility:
    """不传 weather_risk / crew_fatigue 参数时旧接口正常工作。"""

    def test_no_weather_risk_param(self, orchestrator):
        plan = orchestrator._build_action_plan(snapshot={})
        assert isinstance(plan, list)

    def test_no_crew_fatigue_param(self, orchestrator):
        plan = orchestrator._build_action_plan(snapshot={}, nav_report={}, engine_status={})
        assert isinstance(plan, list)

    def test_legacy_snapshot_only(self, orchestrator):
        snapshot = {
            "navigation_event": {
                "payload": {"colregs_assessments": []},
            },
            "engine_event": {
                "payload": {"alerts": []},
            },
        }
        plan = orchestrator._build_action_plan(snapshot)
        assert isinstance(plan, list)
        # Should still produce at least the baseline monitor action
        assert len(plan) >= 1

    def test_combined_old_and_new(self, orchestrator):
        plan = orchestrator._build_action_plan(
            snapshot={},
            nav_report={"colregs_assessments": []},
            engine_status={"alerts": []},
            weather_risk={"risk_score": 90},
            crew_fatigue={"fatigue_scores": {"X": 25}},
        )
        review = [a for a in plan if a["recommended_action"] == "review_route"]
        watch = [a for a in plan if a["recommended_action"] == "recommend_watch_change"]
        assert len(review) == 1
        assert len(watch) == 1
