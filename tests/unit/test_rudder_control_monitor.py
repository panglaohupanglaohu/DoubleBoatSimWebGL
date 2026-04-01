# -*- coding: utf-8 -*-
"""Tests for RudderControlMonitorChannel."""

import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src/backend"))

from channels.rudder_control_monitor import RudderControlMonitorChannel


@pytest.fixture
def channel():
    ch = RudderControlMonitorChannel()
    ch.initialize()
    return ch


class TestRudderControlMonitorInit:
    def test_name(self, channel):
        assert channel.name == "rudder_control_monitor"

    def test_initialize(self, channel):
        assert channel._initialized is True
        assert channel._active is True

    def test_defaults(self, channel):
        assert channel._max_rudder_angle == 35.0
        assert channel._response_time_limit_s == 28.0
        assert channel._rudders == {}


class TestUpdateRudder:
    def test_basic_update(self, channel):
        result = channel.update_rudder("R1", 10.0, ordered_angle_deg=10.0)
        assert result["rudder_id"] == "R1"
        assert result["angle_deg"] == 10.0
        assert result["rudder_status"] == "ok"
        assert result["rudder_count"] == 1

    def test_angle_clamping(self, channel):
        result = channel.update_rudder("R1", 50.0)
        assert result["angle_deg"] == 35.0

    def test_negative_angle_clamping(self, channel):
        result = channel.update_rudder("R1", -50.0)
        assert result["angle_deg"] == -35.0

    def test_angle_mismatch_warning(self, channel):
        result = channel.update_rudder("R1", 10.0, ordered_angle_deg=15.0)
        assert result["rudder_status"] == "warning"

    def test_small_angle_mismatch_ok(self, channel):
        result = channel.update_rudder("R1", 10.0, ordered_angle_deg=11.5)
        assert result["rudder_status"] == "ok"

    def test_pressure_warning_low(self, channel):
        result = channel.update_rudder("R1", 10.0, pressure_bar=50.0)
        assert result["rudder_status"] == "warning"

    def test_pressure_warning_high(self, channel):
        result = channel.update_rudder("R1", 10.0, pressure_bar=300.0)
        assert result["rudder_status"] == "warning"

    def test_response_time_fault(self, channel):
        result = channel.update_rudder("R1", 10.0, response_time_s=30.0)
        assert result["rudder_status"] == "fault"


class TestGetSteeringStatus:
    def test_empty(self, channel):
        status = channel.get_steering_status()
        assert status["rudders"] == {}
        assert status["any_fault"] is False
        assert status["angle_mismatch"] is False
        assert status["solas_compliant"] is True
        assert status["average_response_time_s"] == 0.0

    def test_with_rudders(self, channel):
        channel.update_rudder("R1", 5.0, response_time_s=3.0)
        channel.update_rudder("R2", -5.0, response_time_s=4.0)
        status = channel.get_steering_status()
        assert len(status["rudders"]) == 2
        assert status["solas_compliant"] is True
        assert status["average_response_time_s"] == 3.5

    def test_fault_detection(self, channel):
        channel.update_rudder("R1", 5.0, response_time_s=30.0)
        status = channel.get_steering_status()
        assert status["any_fault"] is True
        assert status["solas_compliant"] is False


class TestProcessEvent:
    def test_rudder_reading(self, channel):
        event = {
            "type": "rudder_reading",
            "rudder_id": "R1",
            "angle_deg": 15.0,
            "ordered_angle_deg": 15.0,
            "pressure_bar": 150.0,
            "response_time_s": 5.0,
        }
        result = asyncio.run(channel.process_event(event))
        assert result["status"] == "updated"
        assert result["rudder_id"] == "R1"

    def test_unknown_event(self, channel):
        result = asyncio.run(channel.process_event({"type": "unknown"}))
        assert result["status"] == "ignored"


class TestGetStatus:
    def test_basic_status(self, channel):
        status = channel.get_status()
        assert status["name"] == "rudder_control_monitor"
        assert status["rudder_count"] == 0
        assert status["any_fault"] is False
        assert status["solas_compliant"] is True

    def test_status_with_fault(self, channel):
        channel.update_rudder("R1", 10.0, response_time_s=30.0)
        status = channel.get_status()
        assert status["rudder_count"] == 1
        assert status["any_fault"] is True
        assert status["solas_compliant"] is False


class TestLifecycle:
    def test_shutdown(self, channel):
        assert channel.shutdown() is True
        assert channel._active is False
        assert channel._initialized is False

    def test_start_stop(self, channel):
        asyncio.run(channel.stop())
        assert channel._active is False
        asyncio.run(channel.start())
        assert channel._active is True
