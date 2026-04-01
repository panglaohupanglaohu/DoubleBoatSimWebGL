# -*- coding: utf-8 -*-
"""Tests for TankLevelMonitorChannel."""

import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src/backend"))

from channels.tank_level_monitor import TankLevelMonitorChannel


@pytest.fixture
def channel():
    ch = TankLevelMonitorChannel()
    ch.initialize()
    return ch


class TestTankLevelMonitorInit:
    def test_name(self, channel):
        assert channel.name == "tank_level_monitor"

    def test_initialize(self, channel):
        assert channel._initialized is True
        assert channel._active is True

    def test_empty_tanks(self, channel):
        assert channel._tanks == {}


class TestUpdateTank:
    def test_basic_update(self, channel):
        result = channel.update_tank("T1", "fuel_oil", 100.0, 50.0)
        assert result["tank_id"] == "T1"
        assert result["level_percent"] == 50.0
        assert result["tank_count"] == 1

    def test_level_calculation(self, channel):
        channel.update_tank("T1", "fuel_oil", 200.0, 80.0)
        assert channel._tanks["T1"]["level_percent"] == 40.0

    def test_overfill_clamped(self, channel):
        channel.update_tank("T1", "fuel_oil", 100.0, 150.0)
        assert channel._tanks["T1"]["current_m3"] == 100.0
        assert channel._tanks["T1"]["level_percent"] == 100.0

    def test_negative_current_clamped(self, channel):
        channel.update_tank("T1", "fuel_oil", 100.0, -10.0)
        assert channel._tanks["T1"]["current_m3"] == 0.0

    def test_zero_capacity_safe(self, channel):
        result = channel.update_tank("T1", "fuel_oil", 0.0, 0.0)
        assert result["level_percent"] == 0.0


class TestGetTankSummary:
    def test_empty(self, channel):
        summary = channel.get_tank_summary()
        assert summary["total_fuel_m3"] == 0
        assert summary["total_fresh_water_m3"] == 0
        assert summary["low_level_alarms"] == []
        assert summary["high_level_alarms"] == []

    def test_fuel_total(self, channel):
        channel.update_tank("FO1", "fuel_oil", 100.0, 40.0)
        channel.update_tank("DO1", "diesel_oil", 50.0, 20.0)
        summary = channel.get_tank_summary()
        assert summary["total_fuel_m3"] == 60.0

    def test_fresh_water_total(self, channel):
        channel.update_tank("FW1", "fresh_water", 100.0, 80.0)
        summary = channel.get_tank_summary()
        assert summary["total_fresh_water_m3"] == 80.0

    def test_low_level_alarm(self, channel):
        channel.update_tank("FO1", "fuel_oil", 100.0, 15.0)  # 15%
        summary = channel.get_tank_summary()
        assert "FO1" in summary["low_level_alarms"]

    def test_ballast_no_low_alarm(self, channel):
        channel.update_tank("BW1", "ballast", 100.0, 10.0)  # 10% but ballast
        summary = channel.get_tank_summary()
        assert "BW1" not in summary["low_level_alarms"]

    def test_high_level_alarm_ballast(self, channel):
        channel.update_tank("BW1", "ballast", 100.0, 95.0)  # 95%
        summary = channel.get_tank_summary()
        assert "BW1" in summary["high_level_alarms"]

    def test_high_level_alarm_sewage(self, channel):
        channel.update_tank("SW1", "sewage", 50.0, 46.0)  # 92%
        summary = channel.get_tank_summary()
        assert "SW1" in summary["high_level_alarms"]

    def test_fuel_no_high_level_alarm(self, channel):
        channel.update_tank("FO1", "fuel_oil", 100.0, 95.0)  # 95% but fuel
        summary = channel.get_tank_summary()
        assert "FO1" not in summary["high_level_alarms"]


class TestEstimateFuelEndurance:
    def test_basic_endurance(self, channel):
        channel.update_tank("FO1", "fuel_oil", 100.0, 50.0)
        result = channel.estimate_fuel_endurance(consumption_m3_per_hour=0.5)
        assert result["total_fuel_m3"] == 50.0
        assert result["hours_remaining"] == 100.0
        assert result["nautical_miles_at_12kts"] == 1200.0

    def test_zero_consumption_safe(self, channel):
        channel.update_tank("FO1", "fuel_oil", 100.0, 50.0)
        result = channel.estimate_fuel_endurance(consumption_m3_per_hour=0.0)
        assert result["hours_remaining"] == 100.0  # fallback to 0.5

    def test_empty_tanks(self, channel):
        result = channel.estimate_fuel_endurance()
        assert result["total_fuel_m3"] == 0.0
        assert result["hours_remaining"] == 0.0


class TestProcessEvent:
    def test_tank_reading(self, channel):
        event = {
            "type": "tank_reading",
            "tank_id": "FO1",
            "tank_type": "fuel_oil",
            "capacity_m3": 100.0,
            "current_m3": 60.0,
        }
        result = asyncio.run(channel.process_event(event))
        assert result["status"] == "updated"
        assert result["tank_id"] == "FO1"

    def test_unknown_event(self, channel):
        result = asyncio.run(channel.process_event({"type": "unknown"}))
        assert result["status"] == "ignored"


class TestGetStatus:
    def test_basic(self, channel):
        status = channel.get_status()
        assert status["name"] == "tank_level_monitor"
        assert status["tank_count"] == 0
        assert status["total_fuel_m3"] == 0

    def test_with_tanks(self, channel):
        channel.update_tank("FO1", "fuel_oil", 100.0, 50.0)
        channel.update_tank("FW1", "fresh_water", 80.0, 40.0)
        status = channel.get_status()
        assert status["tank_count"] == 2
        assert status["total_fuel_m3"] == 50.0
        assert status["total_fresh_water_m3"] == 40.0


class TestLifecycle:
    def test_shutdown(self, channel):
        assert channel.shutdown() is True
        assert channel._active is False

    def test_start_stop(self, channel):
        asyncio.run(channel.stop())
        assert channel._active is False
        asyncio.run(channel.start())
        assert channel._active is True
