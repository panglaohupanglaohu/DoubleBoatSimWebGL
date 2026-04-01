# -*- coding: utf-8 -*-
"""
Tests for L3: COLREGs Autonomous Brain Channel
"""

import math
import pytest
from channels.colregs_brain import (
    COLREGsAutonomousBrainChannel, COLREGsMathEngine, NMPCController,
    VesselState, EncounterAssessment, COLREGRule, EncounterType,
    ManeuverAction, NMPCState,
)


@pytest.fixture
def brain():
    ch = COLREGsAutonomousBrainChannel()
    ch.initialize()
    return ch


@pytest.fixture
def own_ship():
    return VesselState(lat=31.23, lon=121.47, course=0.0, speed=12.0, heading=0.0)


class TestCOLREGsMathEngine:
    def test_normalize_angle(self):
        assert COLREGsMathEngine.normalize_angle(370) == pytest.approx(10.0)
        assert COLREGsMathEngine.normalize_angle(-10) == pytest.approx(350.0)
        assert COLREGsMathEngine.normalize_angle(0) == pytest.approx(0.0)

    def test_angle_diff(self):
        assert COLREGsMathEngine.angle_diff(10, 20) == pytest.approx(10.0)
        assert COLREGsMathEngine.angle_diff(350, 10) == pytest.approx(20.0)
        assert COLREGsMathEngine.angle_diff(10, 350) == pytest.approx(-20.0)

    def test_calculate_distance(self, own_ship):
        target = VesselState(lat=31.24, lon=121.47, course=180, speed=10, heading=180)
        d = COLREGsMathEngine.calculate_distance_nm(own_ship, target)
        assert d > 0
        assert d < 1.0  # < 1 nm

    def test_calculate_distance_same_point(self, own_ship):
        d = COLREGsMathEngine.calculate_distance_nm(own_ship, own_ship)
        assert d == pytest.approx(0.0, abs=1e-6)

    def test_calculate_relative_bearing(self, own_ship):
        target = VesselState(lat=31.24, lon=121.47, course=180, speed=10, heading=180)
        rb = COLREGsMathEngine.calculate_relative_bearing(own_ship, target)
        assert 0 <= rb < 360

    def test_calculate_cpa_tcpa(self, own_ship):
        target = VesselState(lat=31.25, lon=121.48, course=200, speed=10, heading=200)
        cpa, tcpa = COLREGsMathEngine.calculate_cpa_tcpa(own_ship, target)
        assert cpa >= 0
        assert tcpa >= 0

    def test_cpa_tcpa_same_speed_opposite(self, own_ship):
        # Targets heading straight toward own ship
        target = VesselState(lat=31.28, lon=121.47, course=180, speed=12, heading=180)
        cpa, tcpa = COLREGsMathEngine.calculate_cpa_tcpa(own_ship, target)
        assert cpa < 0.5  # Nearly head-on
        assert tcpa < 30  # Will meet soon

    def test_cpa_tcpa_stationary(self, own_ship):
        target = VesselState(lat=31.25, lon=121.48, course=0, speed=0, heading=0)
        own_stationary = VesselState(lat=31.23, lon=121.47, course=0, speed=0, heading=0)
        cpa, tcpa = COLREGsMathEngine.calculate_cpa_tcpa(own_stationary, target)
        assert tcpa == float('inf')

    def test_classify_head_on(self, own_ship):
        target = VesselState(lat=31.24, lon=121.47, course=180, speed=10, heading=180)
        enc = COLREGsMathEngine.classify_encounter(own_ship, target)
        assert enc == EncounterType.HEAD_ON

    def test_classify_crossing_starboard(self, own_ship):
        target = VesselState(lat=31.23, lon=121.49, course=270, speed=10, heading=270)
        enc = COLREGsMathEngine.classify_encounter(own_ship, target)
        assert enc in [EncounterType.CROSSING_FROM_STARBOARD, EncounterType.SAFE]

    def test_classify_safe(self, own_ship):
        # Target far behind, same direction
        target = VesselState(lat=31.20, lon=121.47, course=0, speed=5, heading=0)
        enc = COLREGsMathEngine.classify_encounter(own_ship, target)
        # Being overtaken or safe
        assert enc in [EncounterType.OVERTAKING, EncounterType.BEING_OVERTAKEN, EncounterType.SAFE]

    def test_assess_encounter(self, own_ship):
        target = VesselState(lat=31.25, lon=121.47, course=180, speed=12, heading=180)
        assessment = COLREGsMathEngine.assess_encounter(own_ship, target)
        assert isinstance(assessment, EncounterAssessment)
        assert assessment.distance_nm > 0
        assert 0 <= assessment.risk_level <= 1

    def test_determine_rule_head_on(self):
        rule, is_give_way = COLREGsMathEngine._determine_rule(EncounterType.HEAD_ON)
        assert rule == COLREGRule.RULE_14_HEAD_ON
        assert is_give_way

    def test_determine_rule_stand_on(self):
        rule, is_give_way = COLREGsMathEngine._determine_rule(EncounterType.CROSSING_FROM_PORT)
        assert rule == COLREGRule.RULE_17_STAND_ON
        assert not is_give_way

    def test_determine_rule_overtaking(self):
        rule, is_give_way = COLREGsMathEngine._determine_rule(EncounterType.OVERTAKING)
        assert rule == COLREGRule.RULE_13_OVERTAKING
        assert is_give_way

    def test_calculate_risk_no_danger(self):
        risk = COLREGsMathEngine._calculate_risk(5.0, 60.0, 10.0)
        assert risk == 0.0

    def test_calculate_risk_high(self):
        risk = COLREGsMathEngine._calculate_risk(0.1, 2.0, 0.5)
        assert risk > 0.5

    def test_calculate_risk_infinite_tcpa(self):
        risk = COLREGsMathEngine._calculate_risk(1.0, float('inf'), 5.0)
        assert risk == 0.0

    def test_recommend_action_maintain(self):
        action, course, speed = COLREGsMathEngine._recommend_action(
            EncounterType.SAFE, False, 5.0, 60.0, 10.0,
            VesselState(0, 0, 0, 10, 0), VesselState(0, 0, 0, 10, 0)
        )
        assert action == ManeuverAction.MAINTAIN

    def test_recommend_action_head_on(self):
        own = VesselState(0, 0, 0, 10, 0)
        tgt = VesselState(0.01, 0, 180, 10, 180)
        action, course, speed = COLREGsMathEngine._recommend_action(
            EncounterType.HEAD_ON, True, 0.3, 10.0, 1.5, own, tgt
        )
        assert action == ManeuverAction.ALTER_COURSE_STARBOARD
        assert course >= 30.0  # Rule 8: large enough

    def test_recommend_action_crossing(self):
        own = VesselState(0, 0, 0, 10, 0)
        tgt = VesselState(0, 0.01, 270, 10, 270)
        action, course, speed = COLREGsMathEngine._recommend_action(
            EncounterType.CROSSING_FROM_STARBOARD, True, 0.3, 8.0, 1.0, own, tgt
        )
        assert action == ManeuverAction.ALTER_COURSE_STARBOARD

    def test_recommend_action_emergency_stop(self):
        own = VesselState(0, 0, 0, 10, 0)
        tgt = VesselState(0, 0, 180, 10, 180)
        action, course, speed = COLREGsMathEngine._recommend_action(
            EncounterType.CROSSING_FROM_STARBOARD, True, 0.1, 2.0, 0.2, own, tgt
        )
        # Very close, should recommend aggressive action
        assert action in [ManeuverAction.ALTER_COURSE_STARBOARD, ManeuverAction.STOP]


class TestNMPCController:
    def test_predict_trajectory(self, own_ship):
        nmpc = NMPCController()
        courses = [own_ship.course] * 10
        speeds = [own_ship.speed] * 10
        state = nmpc.predict_trajectory(own_ship, courses, speeds)
        assert len(state.predicted_positions) > 1
        assert state.constraints_satisfied

    def test_predict_with_course_change(self, own_ship):
        nmpc = NMPCController()
        courses = [own_ship.course + 30] * 10
        speeds = [own_ship.speed] * 10
        state = nmpc.predict_trajectory(own_ship, courses, speeds)
        # Course should gradually change due to rudder rate limit
        assert state.predicted_courses[-1] != own_ship.course

    def test_predict_with_speed_reduction(self, own_ship):
        nmpc = NMPCController()
        courses = [own_ship.course] * 10
        speeds = [own_ship.speed * 0.5] * 10
        state = nmpc.predict_trajectory(own_ship, courses, speeds)
        assert state.predicted_speeds[-1] < own_ship.speed

    def test_optimize_avoidance_maintain(self, own_ship):
        nmpc = NMPCController()
        target = VesselState(lat=32.0, lon=122.0, course=90, speed=10, heading=90)
        assessment = COLREGsMathEngine.assess_encounter(own_ship, target)
        result = nmpc.optimize_avoidance(own_ship, target, assessment)
        assert result["action"] in ["maintain", "alter_starboard"]

    def test_optimize_avoidance_give_way(self, own_ship):
        nmpc = NMPCController()
        target = VesselState(lat=31.25, lon=121.47, course=180, speed=12, heading=180)
        assessment = EncounterAssessment(
            encounter_type=EncounterType.HEAD_ON,
            colreg_rule=COLREGRule.RULE_14_HEAD_ON,
            relative_bearing=0, distance_nm=1.0, cpa=0.2, tcpa=5.0,
            risk_level=0.8, is_give_way=True,
            recommended_action=ManeuverAction.ALTER_COURSE_STARBOARD,
            course_alteration=30.0, speed_reduction=0.0,
        )
        result = nmpc.optimize_avoidance(own_ship, target, assessment)
        assert result["action"] == "alter_starboard"
        assert "candidates_evaluated" in result

    def test_optimize_avoidance_reduce_speed(self, own_ship):
        nmpc = NMPCController()
        target = VesselState(lat=31.25, lon=121.47, course=180, speed=12, heading=180)
        assessment = EncounterAssessment(
            encounter_type=EncounterType.CROSSING_FROM_STARBOARD,
            colreg_rule=COLREGRule.RULE_15_CROSSING,
            relative_bearing=45, distance_nm=0.5, cpa=0.1, tcpa=2.0,
            risk_level=0.9, is_give_way=True,
            recommended_action=ManeuverAction.REDUCE_SPEED,
            course_alteration=0.0, speed_reduction=30.0,
        )
        result = nmpc.optimize_avoidance(own_ship, target, assessment)
        assert result["action"] == "reduce_speed"

    def test_optimize_avoidance_stop(self, own_ship):
        nmpc = NMPCController()
        target = VesselState(lat=31.25, lon=121.47, course=180, speed=12, heading=180)
        assessment = EncounterAssessment(
            encounter_type=EncounterType.HEAD_ON,
            colreg_rule=COLREGRule.RULE_14_HEAD_ON,
            relative_bearing=0, distance_nm=0.2, cpa=0.05, tcpa=1.0,
            risk_level=0.95, is_give_way=True,
            recommended_action=ManeuverAction.STOP,
            course_alteration=0.0, speed_reduction=100.0,
        )
        result = nmpc.optimize_avoidance(own_ship, target, assessment)
        assert result["action"] == "stop"


class TestCOLREGsBrainChannel:
    def test_initialize(self, brain):
        assert brain._initialized

    def test_assess_situation(self, brain, own_ship):
        targets = [
            VesselState(lat=31.25, lon=121.47, course=180, speed=12, heading=180),
            VesselState(lat=31.23, lon=121.50, course=270, speed=8, heading=270),
        ]
        assessments = brain.assess_situation(own_ship, targets)
        assert len(assessments) == 2
        for a in assessments:
            assert isinstance(a, EncounterAssessment)

    def test_plan_avoidance_safe(self, brain, own_ship):
        targets = [
            VesselState(lat=32.0, lon=122.0, course=90, speed=5, heading=90),
        ]
        result = brain.plan_avoidance(own_ship, targets)
        assert result["action"] == "maintain"

    def test_plan_avoidance_dangerous(self, brain, own_ship):
        targets = [
            VesselState(lat=31.24, lon=121.47, course=180, speed=12, heading=180),
        ]
        result = brain.plan_avoidance(own_ship, targets)
        # Should detect this as head-on situation
        assert "assessments" in result or "encounter" in result

    def test_get_status(self, brain):
        status = brain.get_status()
        assert status["name"] == "colregs_brain"
        assert "active_assessments" in status

    def test_shutdown(self, brain):
        assert brain.shutdown()
        assert not brain._initialized
