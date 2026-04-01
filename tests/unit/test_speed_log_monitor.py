# -*- coding: utf-8 -*-
"""
Tests for L2: Speed Log Monitor — 计程仪监控
"""

import asyncio
import time
import pytest
from channels.speed_log_monitor import SpeedLogMonitorChannel


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture
def channel():
    ch = SpeedLogMonitorChannel()
    ch.initialize()
    return ch


class TestInstantiation:
    def test_default_status(self, channel):
        status = channel.get_status()
        assert status["name"] == "speed_log_monitor"
        assert status["active"] is True
        assert status["sensor_count"] == 0
        assert status["average_speed_knots"] is None
        assert status["agreement"] is True
        assert status["distance_run_nm"] == 0.0

    def test_uninitialized(self):
        ch = SpeedLogMonitorChannel()
        status = ch.get_status()
        assert status["active"] is False

    def test_shutdown(self, channel):
        assert channel.shutdown() is True
        assert channel.get_status()["active"] is False


class TestUpdateSensor:
    def test_add_single_sensor(self, channel):
        result = channel.update_sensor("STW-1", "stw", 12.5)
        assert result["sensor_id"] == "STW-1"
        assert result["speed_knots"] == 12.5
        assert result["sensor_count"] == 1

    def test_add_multiple_sensors(self, channel):
        channel.update_sensor("STW-1", "stw", 12.0)
        channel.update_sensor("SOG-1", "sog", 12.3)
        channel.update_sensor("DOP-1", "doppler", 11.9)
        assert channel.get_status()["sensor_count"] == 3


class TestSpeedConsensus:
    def test_no_sensors(self, channel):
        consensus = channel.get_speed_consensus()
        assert consensus["average_speed_knots"] is None
        assert consensus["sensors_used"] == 0
        assert consensus["agreement"] is True

    def test_single_sensor(self, channel):
        channel.update_sensor("STW-1", "stw", 10.0)
        consensus = channel.get_speed_consensus()
        assert consensus["average_speed_knots"] == 10.0
        assert consensus["sensors_used"] == 1
        assert consensus["agreement"] is True

    def test_agreeing_sensors(self, channel):
        channel.update_sensor("STW-1", "stw", 12.0)
        channel.update_sensor("SOG-1", "sog", 12.5)
        channel.update_sensor("DOP-1", "doppler", 12.2)
        consensus = channel.get_speed_consensus()
        assert consensus["agreement"] is True
        assert consensus["sensors_used"] == 3

    def test_disagreeing_sensor(self, channel):
        channel.update_sensor("STW-1", "stw", 12.0)
        channel.update_sensor("SOG-1", "sog", 12.2)
        channel.update_sensor("DOP-1", "doppler", 15.0)  # > 1 knot off
        # DOP-1 should be marked warning
        consensus = channel.get_speed_consensus()
        assert consensus["sensors_used"] < 3


class TestDistance:
    def test_initial_distance(self, channel):
        result = channel.update_distance()
        assert result["distance_run_nm"] == 0.0

    def test_distance_accumulation(self, channel):
        channel.update_sensor("STW-1", "stw", 10.0)
        # Set last update to 1 hour ago
        channel._last_distance_update = time.time() - 3600
        result = channel.update_distance()
        # Should have run ~10 nm in 1 hour at 10 knots
        assert 9.9 < result["distance_run_nm"] < 10.1

    def test_no_sensors_no_distance(self, channel):
        channel._last_distance_update = time.time() - 3600
        result = channel.update_distance()
        assert result["distance_run_nm"] == 0.0


class TestProcessEvent:
    def test_speed_reading_event(self, channel):
        result = _run(channel.process_event({
            "type": "speed_reading",
            "sensor_id": "EM-1",
            "sensor_type": "em_log",
            "speed_knots": 8.0,
        }))
        assert result["status"] == "updated"
        assert result["sensor_id"] == "EM-1"

    def test_unknown_event(self, channel):
        result = _run(channel.process_event({"type": "unknown"}))
        assert result["status"] == "ignored"


class TestStartStop:
    def test_start_stop(self, channel):
        _run(channel.stop())
        assert channel.get_status()["active"] is False
        _run(channel.start())
        assert channel.get_status()["active"] is True
