# -*- coding: utf-8 -*-
"""Tests for AlarmManagementChannel."""

import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src/backend"))

from channels.alarm_management import AlarmManagementChannel


@pytest.fixture
def channel():
    ch = AlarmManagementChannel()
    ch.initialize()
    return ch


class TestAlarmManagementInit:
    def test_name(self, channel):
        assert channel.name == "alarm_management"

    def test_initialize(self, channel):
        assert channel._initialized is True
        assert channel._active is True

    def test_empty(self, channel):
        assert channel._alarms == {}
        assert len(channel._alarm_history) == 0


class TestRaiseAlarm:
    def test_basic_raise(self, channel):
        result = channel.raise_alarm("A1", "engine", "alarm", "Engine overheat")
        assert result["alarm_id"] == "A1"
        assert result["raised"] is True
        assert result["total_active"] == 1

    def test_invalid_priority_defaults_to_caution(self, channel):
        channel.raise_alarm("A1", "engine", "invalid_priority", "Test")
        assert channel._alarms["A1"]["priority"] == "caution"

    def test_alarm_fields(self, channel):
        channel.raise_alarm("A1", "navigation", "emergency", "Collision risk")
        alarm = channel._alarms["A1"]
        assert alarm["source_channel"] == "navigation"
        assert alarm["active"] is True
        assert alarm["acknowledged"] is False
        assert alarm["silenced"] is False
        assert alarm["acknowledge_time"] is None


class TestAcknowledgeAlarm:
    def test_acknowledge(self, channel):
        channel.raise_alarm("A1", "engine", "alarm", "Test")
        result = channel.acknowledge_alarm("A1")
        assert result["acknowledged"] is True
        assert channel._alarms["A1"]["acknowledged"] is True
        assert channel._alarms["A1"]["acknowledge_time"] is not None

    def test_acknowledge_not_found(self, channel):
        result = channel.acknowledge_alarm("NONEXISTENT")
        assert result["acknowledged"] is False
        assert result["reason"] == "not found"


class TestSilenceAlarm:
    def test_silence(self, channel):
        channel.raise_alarm("A1", "engine", "alarm", "Test")
        result = channel.silence_alarm("A1")
        assert result["silenced"] is True
        assert channel._alarms["A1"]["silenced"] is True

    def test_silence_not_found(self, channel):
        result = channel.silence_alarm("NONEXISTENT")
        assert result["silenced"] is False


class TestClearAlarm:
    def test_clear(self, channel):
        channel.raise_alarm("A1", "engine", "alarm", "Test")
        result = channel.clear_alarm("A1")
        assert result["cleared"] is True
        assert "A1" not in channel._alarms
        assert len(channel._alarm_history) == 1

    def test_clear_not_found(self, channel):
        result = channel.clear_alarm("NONEXISTENT")
        assert result["cleared"] is False

    def test_history_limit(self, channel):
        for i in range(110):
            channel.raise_alarm(f"A{i}", "test", "caution", f"Test {i}")
        for i in range(110):
            channel.clear_alarm(f"A{i}")
        assert len(channel._alarm_history) == 100


class TestGetActiveAlarms:
    def test_empty(self, channel):
        assert channel.get_active_alarms() == []

    def test_sorted_by_priority(self, channel):
        channel.raise_alarm("A1", "nav", "caution", "Low")
        channel.raise_alarm("A2", "engine", "emergency", "Critical")
        channel.raise_alarm("A3", "comms", "warning", "Mid")
        active = channel.get_active_alarms()
        assert active[0]["alarm_id"] == "A2"  # emergency first
        assert active[1]["alarm_id"] == "A3"  # warning
        assert active[2]["alarm_id"] == "A1"  # caution


class TestGetAlarmSummary:
    def test_empty_summary(self, channel):
        summary = channel.get_alarm_summary()
        assert summary["total_active"] == 0
        assert summary["emergency_count"] == 0
        assert summary["alarm_count"] == 0
        assert summary["warning_count"] == 0
        assert summary["caution_count"] == 0
        assert summary["unacknowledged_count"] == 0
        assert summary["oldest_unacknowledged"] is None

    def test_counts(self, channel):
        channel.raise_alarm("A1", "nav", "emergency", "E1")
        channel.raise_alarm("A2", "nav", "alarm", "A2")
        channel.raise_alarm("A3", "nav", "warning", "W1")
        channel.raise_alarm("A4", "nav", "caution", "C1")
        summary = channel.get_alarm_summary()
        assert summary["total_active"] == 4
        assert summary["emergency_count"] == 1
        assert summary["alarm_count"] == 1
        assert summary["warning_count"] == 1
        assert summary["caution_count"] == 1
        assert summary["unacknowledged_count"] == 4

    def test_oldest_unacknowledged(self, channel):
        channel.raise_alarm("A1", "nav", "alarm", "First")
        channel.raise_alarm("A2", "nav", "alarm", "Second")
        channel.acknowledge_alarm("A1")
        summary = channel.get_alarm_summary()
        assert summary["unacknowledged_count"] == 1
        assert summary["oldest_unacknowledged"]["alarm_id"] == "A2"


class TestProcessEvent:
    def test_raise_alarm_event(self, channel):
        event = {
            "type": "raise_alarm",
            "alarm_id": "A1",
            "source_channel": "engine",
            "priority": "alarm",
            "description": "Overheat",
        }
        result = asyncio.run(channel.process_event(event))
        assert result["status"] == "raised"
        assert result["alarm_id"] == "A1"

    def test_acknowledge_alarm_event(self, channel):
        channel.raise_alarm("A1", "engine", "alarm", "Test")
        event = {"type": "acknowledge_alarm", "alarm_id": "A1"}
        result = asyncio.run(channel.process_event(event))
        assert result["status"] == "acknowledged"

    def test_clear_alarm_event(self, channel):
        channel.raise_alarm("A1", "engine", "alarm", "Test")
        event = {"type": "clear_alarm", "alarm_id": "A1"}
        result = asyncio.run(channel.process_event(event))
        assert result["status"] == "cleared"

    def test_unknown_event(self, channel):
        result = asyncio.run(channel.process_event({"type": "unknown"}))
        assert result["status"] == "ignored"


class TestGetStatus:
    def test_basic(self, channel):
        status = channel.get_status()
        assert status["name"] == "alarm_management"
        assert status["total_active"] == 0
        assert status["emergency_count"] == 0
        assert status["unacknowledged_count"] == 0

    def test_with_alarms(self, channel):
        channel.raise_alarm("A1", "nav", "emergency", "E1")
        channel.raise_alarm("A2", "nav", "warning", "W1")
        status = channel.get_status()
        assert status["total_active"] == 2
        assert status["emergency_count"] == 1
        assert status["unacknowledged_count"] == 2


class TestLifecycle:
    def test_shutdown(self, channel):
        assert channel.shutdown() is True
        assert channel._active is False

    def test_start_stop(self, channel):
        asyncio.run(channel.stop())
        assert channel._active is False
        asyncio.run(channel.start())
        assert channel._active is True
