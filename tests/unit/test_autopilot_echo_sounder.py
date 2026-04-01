# -*- coding: utf-8 -*-
"""
Autopilot Monitor + Echo Sounder Monitor 全面测试

覆盖:
- AutopilotMonitorChannel: 模式切换、航向设置、偏差计算、事件处理
- EchoSounderMonitorChannel: 深度更新、龙骨余量、告警、趋势分析、事件处理
"""

import asyncio
import pytest

from src.backend.channels.autopilot_monitor import AutopilotMonitorChannel, VALID_MODES
from src.backend.channels.echo_sounder_monitor import EchoSounderMonitorChannel, _MAX_HISTORY


def run(coro):
    return asyncio.run(coro)


# ─────────────────────────── Autopilot Monitor ───────────────────────────


class TestAutopilotInit:
    def test_ap_init(self):
        ap = AutopilotMonitorChannel()
        assert ap._mode == "standby"
        assert ap._set_heading_deg == 0.0
        assert ap._actual_heading_deg == 0.0
        assert ap._cross_track_error_m == 0.0
        assert ap._rudder_limit_deg == 15.0
        assert "proportional" in ap._gain_settings


class TestAutopilotModes:
    def test_ap_set_mode_heading_hold(self):
        ap = AutopilotMonitorChannel()
        result = ap.set_mode("heading_hold")
        assert result["status"] == "ok"
        assert result["new_mode"] == "heading_hold"
        assert ap._mode == "heading_hold"

    def test_ap_set_mode_track_control(self):
        ap = AutopilotMonitorChannel()
        result = ap.set_mode("track_control")
        assert result["status"] == "ok"
        assert result["new_mode"] == "track_control"

    def test_ap_set_mode_invalid(self):
        ap = AutopilotMonitorChannel()
        result = ap.set_mode("torpedo_mode")
        assert result["status"] == "error"
        assert "invalid mode" in result["reason"]
        assert ap._mode == "standby"


class TestAutopilotHeading:
    def test_ap_set_heading(self):
        ap = AutopilotMonitorChannel()
        result = ap.set_heading(90.0)
        assert result["status"] == "ok"
        assert result["set_heading_deg"] == 90.0

    def test_ap_set_heading_normalize(self):
        ap = AutopilotMonitorChannel()
        result = ap.set_heading(450.0)
        assert result["set_heading_deg"] == pytest.approx(90.0)

    def test_ap_update_navigation(self):
        ap = AutopilotMonitorChannel()
        result = ap.update_navigation(actual_heading=180.0, cross_track_error=5.5)
        assert result["status"] == "ok"
        assert result["actual_heading_deg"] == 180.0
        assert result["cross_track_error_m"] == 5.5


class TestAutopilotHeadingError:
    def test_ap_heading_error_small(self):
        ap = AutopilotMonitorChannel()
        ap.set_heading(100.0)
        ap.update_navigation(actual_heading=97.0)
        error = ap._heading_error()
        assert error == pytest.approx(3.0)

    def test_ap_heading_error_wrap_360(self):
        """set=350, actual=10 → error should be -20 (ship overshot clockwise)."""
        ap = AutopilotMonitorChannel()
        ap.set_heading(350.0)
        ap.update_navigation(actual_heading=10.0)
        error = ap._heading_error()
        assert error == pytest.approx(-20.0)

    def test_ap_heading_error_wrap_negative(self):
        """set=10, actual=350 → error should be +20."""
        ap = AutopilotMonitorChannel()
        ap.set_heading(10.0)
        ap.update_navigation(actual_heading=350.0)
        error = ap._heading_error()
        assert error == pytest.approx(20.0)


class TestAutopilotOnCourse:
    def test_ap_on_course_true(self):
        ap = AutopilotMonitorChannel()
        ap.set_heading(90.0)
        ap.update_navigation(actual_heading=92.0)
        status = ap.get_autopilot_status()
        assert status["on_course"] is True

    def test_ap_on_course_false(self):
        ap = AutopilotMonitorChannel()
        ap.set_heading(90.0)
        ap.update_navigation(actual_heading=110.0)
        status = ap.get_autopilot_status()
        assert status["on_course"] is False


class TestAutopilotCrossTrack:
    def test_ap_cross_track_error(self):
        ap = AutopilotMonitorChannel()
        ap.update_navigation(actual_heading=0.0, cross_track_error=12.5)
        status = ap.get_autopilot_status()
        assert status["cross_track_error_m"] == 12.5


class TestAutopilotStatus:
    def test_ap_status_structure(self):
        ap = AutopilotMonitorChannel()
        ap.initialize()
        ap.set_mode("heading_hold")
        ap.set_heading(45.0)
        ap.update_navigation(actual_heading=44.0)
        status = ap.get_autopilot_status()
        expected_keys = {
            "mode", "set_heading", "actual_heading", "heading_error",
            "cross_track_error_m", "rudder_limit", "on_course", "gain_settings",
        }
        assert expected_keys.issubset(status.keys())
        assert status["mode"] == "heading_hold"
        assert status["set_heading"] == 45.0

    def test_ap_get_status(self):
        ap = AutopilotMonitorChannel()
        ap.initialize()
        status = ap.get_status()
        expected_keys = {
            "name", "active", "initialized", "health",
            "mode", "heading_error", "on_course", "cross_track_error_m",
        }
        assert expected_keys.issubset(status.keys())
        assert status["name"] == "autopilot_monitor"
        assert status["active"] is True
        assert status["initialized"] is True


class TestAutopilotEvents:
    def test_ap_process_event_update(self):
        ap = AutopilotMonitorChannel()
        result = run(ap.process_event({
            "type": "autopilot_update",
            "actual_heading": 270.0,
            "cross_track_error": 3.3,
        }))
        assert result["status"] == "ok"
        assert result["event_status"] == "updated"
        assert result["actual_heading_deg"] == 270.0

    def test_ap_process_event_set_heading(self):
        ap = AutopilotMonitorChannel()
        result = run(ap.process_event({
            "type": "set_heading",
            "heading_deg": 135.0,
        }))
        assert result["status"] == "ok"
        assert result["set_heading_deg"] == 135.0

    def test_ap_process_event_set_mode(self):
        ap = AutopilotMonitorChannel()
        result = run(ap.process_event({
            "type": "set_mode",
            "mode": "wind_steering",
        }))
        assert result["status"] == "ok"
        assert result["new_mode"] == "wind_steering"

    def test_ap_process_event_unknown(self):
        ap = AutopilotMonitorChannel()
        result = run(ap.process_event({"type": "launch_missiles"}))
        assert result["status"] == "ignored"


class TestAutopilotRudderAndGain:
    def test_ap_rudder_limit(self):
        ap = AutopilotMonitorChannel()
        assert ap._rudder_limit_deg == 15.0
        status = ap.get_autopilot_status()
        assert status["rudder_limit"] == 15.0

    def test_ap_gain_settings(self):
        ap = AutopilotMonitorChannel()
        gains = ap._gain_settings
        assert gains["proportional"] == 1.0
        assert gains["derivative"] == 0.5
        assert gains["counter_rudder"] == 0.3
        status = ap.get_autopilot_status()
        assert status["gain_settings"] == gains


# ─────────────────────────── Echo Sounder Monitor ───────────────────────────


class TestEchoInit:
    def test_echo_init(self):
        es = EchoSounderMonitorChannel()
        assert es._current_depth_m == 0.0
        assert es._draught_m == 5.0
        assert es._safety_contour_m == 10.0
        assert es._shallow_alarm_m == 8.0
        assert es._depth_history == []


class TestEchoDepthUpdate:
    def test_echo_update_depth(self):
        es = EchoSounderMonitorChannel()
        result = es.update_depth(25.0)
        assert result["status"] == "ok"
        assert result["current_depth_m"] == 25.0
        assert result["shallow_alarm"] is False
        assert es._current_depth_m == 25.0

    def test_echo_update_with_offset(self):
        es = EchoSounderMonitorChannel()
        result = es.update_depth(20.0, transducer_offset_m=1.5)
        assert result["current_depth_m"] == 21.5

    def test_echo_zero_depth(self):
        es = EchoSounderMonitorChannel()
        result = es.update_depth(0.0)
        assert result["current_depth_m"] == 0.0
        assert result["shallow_alarm"] is True


class TestEchoUnderkeelClearance:
    def test_echo_underkeel_clearance(self):
        es = EchoSounderMonitorChannel()
        es.update_depth(15.0)
        status = es.get_depth_status()
        # underkeel = 15 - 5 = 10
        assert status["underkeel_clearance_m"] == 10.0

    def test_echo_underkeel_negative(self):
        """深度 < 吃水 → 负龙骨余量（搁浅）。"""
        es = EchoSounderMonitorChannel()
        es.update_depth(3.0)
        status = es.get_depth_status()
        assert status["underkeel_clearance_m"] == -2.0
        assert status["grounding_risk"] is True


class TestEchoAlarms:
    def test_echo_shallow_alarm_triggered(self):
        es = EchoSounderMonitorChannel()
        result = es.update_depth(5.0)  # < 8.0
        assert result["shallow_alarm"] is True

    def test_echo_shallow_alarm_not_triggered(self):
        es = EchoSounderMonitorChannel()
        result = es.update_depth(20.0)  # > 8.0
        assert result["shallow_alarm"] is False

    def test_echo_grounding_risk_true(self):
        es = EchoSounderMonitorChannel()
        es.update_depth(6.0)  # underkeel = 6 - 5 = 1 < 2
        status = es.get_depth_status()
        assert status["grounding_risk"] is True

    def test_echo_grounding_risk_false(self):
        es = EchoSounderMonitorChannel()
        es.update_depth(20.0)  # underkeel = 20 - 5 = 15 > 2
        status = es.get_depth_status()
        assert status["grounding_risk"] is False


class TestEchoDepthTrend:
    def test_echo_depth_trend_shoaling(self):
        es = EchoSounderMonitorChannel()
        for d in [30, 28, 26, 24, 22, 20, 18, 16, 14, 12]:
            es.update_depth(float(d))
        status = es.get_depth_status()
        assert status["depth_trend"] == "shoaling"

    def test_echo_depth_trend_deepening(self):
        es = EchoSounderMonitorChannel()
        for d in [10, 12, 14, 16, 18, 20, 22, 24, 26, 28]:
            es.update_depth(float(d))
        status = es.get_depth_status()
        assert status["depth_trend"] == "deepening"

    def test_echo_depth_trend_steady(self):
        es = EchoSounderMonitorChannel()
        for _ in range(10):
            es.update_depth(20.0)
        status = es.get_depth_status()
        assert status["depth_trend"] == "steady"

    def test_echo_depth_trend_insufficient_data(self):
        es = EchoSounderMonitorChannel()
        es.update_depth(20.0)
        es.update_depth(21.0)
        status = es.get_depth_status()
        # < 3 readings → steady
        assert status["depth_trend"] == "steady"


class TestEchoHistory:
    def test_echo_depth_history_max(self):
        es = EchoSounderMonitorChannel()
        for i in range(150):
            es.update_depth(float(i))
        assert len(es._depth_history) == _MAX_HISTORY
        assert es._depth_history[0]["depth_m"] == 50.0
        assert es._depth_history[-1]["depth_m"] == 149.0


class TestEchoCustomConfig:
    def test_echo_custom_draught(self):
        es = EchoSounderMonitorChannel()
        es._draught_m = 8.0
        es.update_depth(12.0)
        status = es.get_depth_status()
        assert status["draught_m"] == 8.0
        assert status["underkeel_clearance_m"] == 4.0

    def test_echo_custom_safety_contour(self):
        es = EchoSounderMonitorChannel()
        es._safety_contour_m = 15.0
        status = es.get_depth_status()
        assert status["safety_contour_m"] == 15.0

    def test_echo_custom_shallow_alarm(self):
        es = EchoSounderMonitorChannel()
        es._shallow_alarm_m = 12.0
        result = es.update_depth(10.0)  # 10 < 12
        assert result["shallow_alarm"] is True


class TestEchoStatus:
    def test_echo_get_status(self):
        es = EchoSounderMonitorChannel()
        es.initialize()
        es.update_depth(25.0)
        status = es.get_status()
        expected_keys = {
            "name", "active", "initialized", "health",
            "current_depth_m", "underkeel_clearance_m",
            "shallow_alarm", "grounding_risk",
        }
        assert expected_keys.issubset(status.keys())
        assert status["name"] == "echo_sounder_monitor"
        assert status["active"] is True
        assert status["current_depth_m"] == 25.0

    def test_echo_process_event(self):
        es = EchoSounderMonitorChannel()
        result = run(es.process_event({
            "type": "depth_reading",
            "depth_m": 18.0,
            "transducer_offset_m": 0.5,
        }))
        assert result["status"] == "ok"
        assert result["event_status"] == "updated"
        assert result["current_depth_m"] == 18.5

    def test_echo_process_event_unknown(self):
        es = EchoSounderMonitorChannel()
        result = run(es.process_event({"type": "sonar_ping"}))
        assert result["status"] == "ignored"
