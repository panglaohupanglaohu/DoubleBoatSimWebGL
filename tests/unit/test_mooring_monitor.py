# -*- coding: utf-8 -*-
"""Tests for MooringMonitorChannel."""

import asyncio
import pytest

from src.backend.channels.mooring_monitor import MooringMonitorChannel, VALID_MOORING_MODES


def run(coro):
    return asyncio.run(coro)


class TestMooringInit:
    def test_name(self):
        ch = MooringMonitorChannel()
        assert ch.name == "mooring_monitor"

    def test_defaults(self):
        ch = MooringMonitorChannel()
        assert ch._lines == {}
        assert ch._winches == {}
        assert ch._mooring_mode == "free"
        assert ch._active is False

    def test_initialize(self):
        ch = MooringMonitorChannel()
        assert ch.initialize() is True
        assert ch._active is True
        assert ch._initialized is True

    def test_shutdown(self):
        ch = MooringMonitorChannel()
        ch.initialize()
        assert ch.shutdown() is True
        assert ch._active is False

    def test_start_stop(self):
        ch = MooringMonitorChannel()
        run(ch.start())
        assert ch._active is True
        run(ch.stop())
        assert ch._active is False


class TestUpdateLine:
    def test_secured(self):
        ch = MooringMonitorChannel()
        result = ch.update_line("L1", "bow_port", tension_kn=100.0, breaking_load_kn=500.0)
        assert result["line_id"] == "L1"
        assert result["status"] == "secured"
        assert result["load_ratio"] == 0.2

    def test_slack(self):
        ch = MooringMonitorChannel()
        result = ch.update_line("L1", "bow_port", tension_kn=3.0)
        assert result["status"] == "slack"

    def test_strained(self):
        ch = MooringMonitorChannel()
        result = ch.update_line("L1", "bow_port", tension_kn=400.0, breaking_load_kn=500.0)
        assert result["status"] == "strained"

    def test_parted(self):
        ch = MooringMonitorChannel()
        result = ch.update_line("L1", "bow_port", tension_kn=500.0, breaking_load_kn=500.0)
        assert result["status"] == "parted"

    def test_parted_exceeds_breaking(self):
        ch = MooringMonitorChannel()
        result = ch.update_line("L1", "bow_port", tension_kn=600.0, breaking_load_kn=500.0)
        assert result["status"] == "parted"

    def test_strained_boundary(self):
        ch = MooringMonitorChannel()
        # exactly 70% → should be strained (> 0.7)
        result = ch.update_line("L1", "bow_port", tension_kn=351.0, breaking_load_kn=500.0)
        assert result["status"] == "strained"

    def test_secured_below_70(self):
        ch = MooringMonitorChannel()
        result = ch.update_line("L1", "bow_port", tension_kn=349.0, breaking_load_kn=500.0)
        assert result["status"] == "secured"


class TestUpdateWinch:
    def test_basic(self):
        ch = MooringMonitorChannel()
        result = ch.update_winch("W1", "L1", brake_set=True, motor_running=False)
        assert result["winch_id"] == "W1"
        assert result["line_id"] == "L1"
        assert result["brake_set"] is True

    def test_auto_tension(self):
        ch = MooringMonitorChannel()
        ch.update_winch("W1", "L1", auto_tension=True)
        assert ch._winches["W1"]["auto_tension"] is True


class TestSetMooringMode:
    def test_valid_modes(self):
        ch = MooringMonitorChannel()
        for mode in VALID_MOORING_MODES:
            result = ch.set_mooring_mode(mode)
            assert result["status"] == "ok"
            assert result["new_mode"] == mode

    def test_invalid_mode(self):
        ch = MooringMonitorChannel()
        result = ch.set_mooring_mode("flying")
        assert result["status"] == "error"
        assert ch._mooring_mode == "free"

    def test_mode_change_tracking(self):
        ch = MooringMonitorChannel()
        result = ch.set_mooring_mode("alongside")
        assert result["old_mode"] == "free"
        assert result["new_mode"] == "alongside"


class TestGetMooringStatus:
    def test_empty(self):
        ch = MooringMonitorChannel()
        status = ch.get_mooring_status()
        assert status["mode"] == "free"
        assert status["all_secured"] is False  # no lines → False
        assert status["any_strained"] is False
        assert status["any_parted"] is False
        assert status["max_load_ratio"] == 0.0

    def test_all_secured(self):
        ch = MooringMonitorChannel()
        ch.update_line("L1", "bow_port", tension_kn=100.0)
        ch.update_line("L2", "stern_port", tension_kn=120.0)
        status = ch.get_mooring_status()
        assert status["all_secured"] is True
        assert status["any_strained"] is False
        assert status["any_parted"] is False

    def test_strained_detected(self):
        ch = MooringMonitorChannel()
        ch.update_line("L1", "bow_port", tension_kn=100.0)
        ch.update_line("L2", "stern_port", tension_kn=400.0, breaking_load_kn=500.0)
        status = ch.get_mooring_status()
        assert status["all_secured"] is False
        assert status["any_strained"] is True
        assert status["max_load_ratio"] == 0.8

    def test_parted_detected(self):
        ch = MooringMonitorChannel()
        ch.update_line("L1", "bow_port", tension_kn=500.0, breaking_load_kn=500.0)
        status = ch.get_mooring_status()
        assert status["any_parted"] is True

    def test_includes_winches(self):
        ch = MooringMonitorChannel()
        ch.update_winch("W1", "L1")
        status = ch.get_mooring_status()
        assert "W1" in status["winches"]


class TestMooringProcessEvent:
    def test_line_reading_event(self):
        ch = MooringMonitorChannel()
        result = run(ch.process_event({
            "type": "line_reading",
            "line_id": "L1",
            "position": "bow_port",
            "tension_kn": 100.0,
        }))
        assert result["event_status"] == "updated"
        assert result["line_id"] == "L1"
        assert result["status"] == "secured"

    def test_line_reading_missing_id(self):
        ch = MooringMonitorChannel()
        result = run(ch.process_event({"type": "line_reading"}))
        assert result["status"] == "error"

    def test_winch_update_event(self):
        ch = MooringMonitorChannel()
        result = run(ch.process_event({
            "type": "winch_update",
            "winch_id": "W1",
            "line_id": "L1",
            "brake_set": True,
        }))
        assert result["event_status"] == "updated"
        assert result["winch_id"] == "W1"

    def test_winch_update_missing_id(self):
        ch = MooringMonitorChannel()
        result = run(ch.process_event({"type": "winch_update"}))
        assert result["status"] == "error"

    def test_mooring_mode_event(self):
        ch = MooringMonitorChannel()
        result = run(ch.process_event({
            "type": "mooring_mode",
            "mode": "alongside",
        }))
        assert result["status"] == "ok"
        assert result["new_mode"] == "alongside"

    def test_unknown_event(self):
        ch = MooringMonitorChannel()
        result = run(ch.process_event({"type": "anchors_away"}))
        assert result["status"] == "ignored"


class TestMooringGetStatus:
    def test_status_structure(self):
        ch = MooringMonitorChannel()
        ch.initialize()
        ch.set_mooring_mode("alongside")
        ch.update_line("L1", "bow_port", tension_kn=100.0)
        status = ch.get_status()
        expected_keys = {
            "name", "active", "initialized", "health",
            "mooring_mode", "line_count", "all_secured",
            "any_parted", "max_load_ratio",
        }
        assert expected_keys.issubset(status.keys())
        assert status["name"] == "mooring_monitor"
        assert status["mooring_mode"] == "alongside"
        assert status["line_count"] == 1
        assert status["all_secured"] is True
