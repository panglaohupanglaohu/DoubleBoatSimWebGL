# -*- coding: utf-8 -*-
"""Tests for PropulsionMonitorChannel."""

import asyncio
import pytest

from src.backend.channels.propulsion_monitor import PropulsionMonitorChannel


def run(coro):
    return asyncio.run(coro)


class TestPropulsionInit:
    def test_name(self):
        ch = PropulsionMonitorChannel()
        assert ch.name == "propulsion_monitor"

    def test_defaults(self):
        ch = PropulsionMonitorChannel()
        assert ch._engines == {}
        assert ch._propulsors == {}
        assert ch._active is False

    def test_initialize(self):
        ch = PropulsionMonitorChannel()
        assert ch.initialize() is True
        assert ch._active is True
        assert ch._initialized is True

    def test_shutdown(self):
        ch = PropulsionMonitorChannel()
        ch.initialize()
        assert ch.shutdown() is True
        assert ch._active is False

    def test_start_stop(self):
        ch = PropulsionMonitorChannel()
        run(ch.start())
        assert ch._active is True
        run(ch.stop())
        assert ch._active is False


class TestUpdateEngine:
    def test_basic_running(self):
        ch = PropulsionMonitorChannel()
        result = ch.update_engine("ME1", rpm=120, current_kw=1500.0)
        assert result["engine_id"] == "ME1"
        assert result["status"] == "running"
        assert result["engine_count"] == 1

    def test_standby_zero_rpm(self):
        ch = PropulsionMonitorChannel()
        result = ch.update_engine("ME1", rpm=0)
        assert result["status"] == "standby"

    def test_alarm_exhaust_high(self):
        ch = PropulsionMonitorChannel()
        result = ch.update_engine("ME1", rpm=100, exhaust_temp_c=460.0)
        assert result["status"] == "alarm"

    def test_alarm_lub_oil_low(self):
        ch = PropulsionMonitorChannel()
        result = ch.update_engine("ME1", rpm=100, lub_oil_pressure_bar=2.5)
        assert result["status"] == "alarm"

    def test_alarm_coolant_high(self):
        ch = PropulsionMonitorChannel()
        result = ch.update_engine("ME1", rpm=100, coolant_temp_c=96.0)
        assert result["status"] == "alarm"

    def test_multiple_engines(self):
        ch = PropulsionMonitorChannel()
        ch.update_engine("ME1", rpm=120)
        result = ch.update_engine("ME2", rpm=110)
        assert result["engine_count"] == 2


class TestUpdatePropulsor:
    def test_basic(self):
        ch = PropulsionMonitorChannel()
        result = ch.update_propulsor("WJ1", rpm=500, thrust_kn=50.0)
        assert result["propulsor_id"] == "WJ1"
        assert result["status"] == "running"
        assert result["propulsor_count"] == 1

    def test_standby(self):
        ch = PropulsionMonitorChannel()
        result = ch.update_propulsor("WJ1", rpm=0)
        assert result["status"] == "standby"

    def test_propeller_type(self):
        ch = PropulsionMonitorChannel()
        ch.update_propulsor("P1", prop_type="propeller", rpm=100, pitch_percent=80.0)
        assert ch._propulsors["P1"]["type"] == "propeller"
        assert ch._propulsors["P1"]["pitch_percent"] == 80.0


class TestGetPropulsionStatus:
    def test_empty(self):
        ch = PropulsionMonitorChannel()
        status = ch.get_propulsion_status()
        assert status["total_power_kw"] == 0.0
        assert status["total_thrust_kn"] == 0.0
        assert status["any_alarm"] is False
        assert status["efficiency_percent"] == 0.0
        assert status["engines"] == {}
        assert status["propulsors"] == {}

    def test_with_engines_and_propulsors(self):
        ch = PropulsionMonitorChannel()
        ch.update_engine("ME1", rated_kw=2000.0, current_kw=1500.0, rpm=120)
        ch.update_engine("ME2", rated_kw=2000.0, current_kw=1000.0, rpm=100)
        ch.update_propulsor("WJ1", rpm=500, thrust_kn=50.0)
        ch.update_propulsor("WJ2", rpm=450, thrust_kn=45.0)
        status = ch.get_propulsion_status()
        assert status["total_power_kw"] == 2500.0
        assert status["total_thrust_kn"] == 95.0
        assert status["efficiency_percent"] == 62.5  # 2500/4000*100
        assert status["any_alarm"] is False

    def test_alarm_detection(self):
        ch = PropulsionMonitorChannel()
        ch.update_engine("ME1", rpm=120, exhaust_temp_c=460.0)
        status = ch.get_propulsion_status()
        assert status["any_alarm"] is True

    def test_standby_engine_not_counted_in_power(self):
        ch = PropulsionMonitorChannel()
        ch.update_engine("ME1", rated_kw=2000.0, current_kw=1500.0, rpm=120)
        ch.update_engine("ME2", rated_kw=2000.0, current_kw=0.0, rpm=0)
        status = ch.get_propulsion_status()
        assert status["total_power_kw"] == 1500.0
        assert status["efficiency_percent"] == 75.0  # 1500/2000*100


class TestGetEngineHealth:
    def test_healthy_engine(self):
        ch = PropulsionMonitorChannel()
        ch.update_engine("ME1", exhaust_temp_c=350.0, lub_oil_pressure_bar=4.5, coolant_temp_c=80.0, rpm=120)
        health = ch.get_engine_health("ME1")
        assert health["health_score"] == 100.0
        assert health["exhaust_temp_normal"] is True
        assert health["lub_oil_normal"] is True
        assert health["coolant_normal"] is True

    def test_unhealthy_engine(self):
        ch = PropulsionMonitorChannel()
        ch.update_engine("ME1", exhaust_temp_c=460.0, lub_oil_pressure_bar=2.5, coolant_temp_c=96.0, rpm=120)
        health = ch.get_engine_health("ME1")
        assert health["health_score"] == 0.0
        assert health["exhaust_temp_normal"] is False
        assert health["lub_oil_normal"] is False
        assert health["coolant_normal"] is False

    def test_partial_health(self):
        ch = PropulsionMonitorChannel()
        ch.update_engine("ME1", exhaust_temp_c=460.0, lub_oil_pressure_bar=4.5, coolant_temp_c=80.0, rpm=120)
        health = ch.get_engine_health("ME1")
        assert health["health_score"] == pytest.approx(66.7, abs=0.1)
        assert health["exhaust_temp_normal"] is False
        assert health["lub_oil_normal"] is True
        assert health["coolant_normal"] is True

    def test_engine_not_found(self):
        ch = PropulsionMonitorChannel()
        health = ch.get_engine_health("GHOST")
        assert "error" in health


class TestPropulsionProcessEvent:
    def test_engine_update_event(self):
        ch = PropulsionMonitorChannel()
        result = run(ch.process_event({
            "type": "engine_update",
            "engine_id": "ME1",
            "rpm": 120,
            "current_kw": 1500.0,
        }))
        assert result["event_status"] == "updated"
        assert result["engine_id"] == "ME1"
        assert result["status"] == "running"

    def test_engine_update_missing_id(self):
        ch = PropulsionMonitorChannel()
        result = run(ch.process_event({"type": "engine_update"}))
        assert result["status"] == "error"

    def test_propulsor_update_event(self):
        ch = PropulsionMonitorChannel()
        result = run(ch.process_event({
            "type": "propulsor_update",
            "propulsor_id": "WJ1",
            "rpm": 500,
            "thrust_kn": 50.0,
        }))
        assert result["event_status"] == "updated"
        assert result["propulsor_id"] == "WJ1"

    def test_propulsor_update_missing_id(self):
        ch = PropulsionMonitorChannel()
        result = run(ch.process_event({"type": "propulsor_update"}))
        assert result["status"] == "error"

    def test_unknown_event(self):
        ch = PropulsionMonitorChannel()
        result = run(ch.process_event({"type": "warp_drive"}))
        assert result["status"] == "ignored"


class TestPropulsionGetStatus:
    def test_status_structure(self):
        ch = PropulsionMonitorChannel()
        ch.initialize()
        ch.update_engine("ME1", rpm=120, current_kw=1500.0, rated_kw=2000.0)
        status = ch.get_status()
        expected_keys = {
            "name", "active", "initialized", "health",
            "engines_running", "total_power_kw", "total_thrust_kn",
            "any_alarm", "efficiency_percent",
        }
        assert expected_keys.issubset(status.keys())
        assert status["name"] == "propulsion_monitor"
        assert status["engines_running"] == 1
