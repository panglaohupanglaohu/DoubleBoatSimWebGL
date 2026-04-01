# -*- coding: utf-8 -*-
"""
Tests for L2: Gyro Compass Monitor — 电罗经监控
"""

import asyncio
import math
import pytest
from channels.gyro_compass_monitor import GyroCompassMonitorChannel


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture
def channel():
    ch = GyroCompassMonitorChannel()
    ch.initialize()
    return ch


class TestInstantiation:
    def test_default_status(self, channel):
        status = channel.get_status()
        assert status["name"] == "gyro_compass_monitor"
        assert status["active"] is True
        assert status["compass_count"] == 0
        assert status["consensus_heading"] is None
        assert status["agreement"] is True

    def test_uninitialized(self):
        ch = GyroCompassMonitorChannel()
        status = ch.get_status()
        assert status["active"] is False

    def test_shutdown(self, channel):
        assert channel.shutdown() is True
        assert channel.get_status()["active"] is False


class TestUpdateCompass:
    def test_add_single_compass(self, channel):
        result = channel.update_compass("GYRO-1", "gyro", 45.0)
        assert result["compass_id"] == "GYRO-1"
        assert result["heading_deg"] == 45.0
        assert result["compass_count"] == 1

    def test_add_multiple_compasses(self, channel):
        channel.update_compass("GYRO-1", "gyro", 90.0)
        channel.update_compass("MAG-1", "magnetic", 91.0)
        channel.update_compass("GPS-1", "gps", 89.5)
        assert channel.get_status()["compass_count"] == 3

    def test_heading_wraps_360(self, channel):
        result = channel.update_compass("GYRO-1", "gyro", 365.0)
        assert result["heading_deg"] == 5.0

    def test_heading_negative_wraps(self, channel):
        result = channel.update_compass("GYRO-1", "gyro", -10.0)
        assert result["heading_deg"] == 350.0


class TestHeadingConsensus:
    def test_no_compasses(self, channel):
        consensus = channel.get_heading_consensus()
        assert consensus["consensus_heading"] is None
        assert consensus["compasses_used"] == 0
        assert consensus["agreement"] is True

    def test_single_compass(self, channel):
        channel.update_compass("GYRO-1", "gyro", 180.0)
        consensus = channel.get_heading_consensus()
        assert consensus["consensus_heading"] == 180.0
        assert consensus["compasses_used"] == 1
        assert consensus["agreement"] is True

    def test_agreeing_compasses(self, channel):
        channel.update_compass("GYRO-1", "gyro", 90.0)
        channel.update_compass("GYRO-2", "gyro", 91.0)
        channel.update_compass("MAG-1", "magnetic", 89.5)
        consensus = channel.get_heading_consensus()
        assert consensus["agreement"] is True
        assert consensus["compasses_used"] == 3
        assert abs(consensus["consensus_heading"] - 90.17) < 1.0

    def test_disagreeing_compass(self, channel):
        channel.update_compass("GYRO-1", "gyro", 90.0)
        channel.update_compass("GYRO-2", "gyro", 91.0)
        channel.update_compass("MAG-1", "magnetic", 100.0)  # > 3 deg off
        # MAG-1 should be marked warning and excluded from ok consensus
        consensus = channel.get_heading_consensus()
        assert "MAG-1" in consensus["unreliable_compasses"]

    def test_vector_average_across_north(self, channel):
        """向量平均法处理 360→0 循环。"""
        channel.update_compass("GYRO-1", "gyro", 359.0)
        channel.update_compass("GYRO-2", "gyro", 1.0)
        consensus = channel.get_heading_consensus()
        # Average of 359 and 1 should be ~0
        assert consensus["consensus_heading"] < 5.0 or consensus["consensus_heading"] > 355.0
        assert consensus["agreement"] is True


class TestProcessEvent:
    def test_compass_reading_event(self, channel):
        result = _run(channel.process_event({
            "type": "compass_reading",
            "compass_id": "GYRO-1",
            "compass_type": "satellite",
            "heading_deg": 270.0,
            "rate_of_turn_deg_s": 0.5,
        }))
        assert result["status"] == "updated"
        assert result["compass_id"] == "GYRO-1"

    def test_unknown_event(self, channel):
        result = _run(channel.process_event({"type": "unknown"}))
        assert result["status"] == "ignored"


class TestStartStop:
    def test_start_stop(self, channel):
        _run(channel.stop())
        assert channel.get_status()["active"] is False
        _run(channel.start())
        assert channel.get_status()["active"] is True


class TestVectorAverage:
    def test_simple_average(self):
        avg = GyroCompassMonitorChannel._compute_vector_average([0, 90, 180, 270])
        # Should be undefined direction — near 0 magnitude, but returns some value
        # For 4 cardinal directions, the vector sum is ~0, atan2(0,0) = 0
        assert 0 <= avg < 360

    def test_north_average(self):
        avg = GyroCompassMonitorChannel._compute_vector_average([355, 5])
        assert avg < 10 or avg > 350

    def test_south_average(self):
        avg = GyroCompassMonitorChannel._compute_vector_average([170, 190])
        assert 175 < avg < 185


class TestAngularDiff:
    def test_simple_diff(self):
        assert GyroCompassMonitorChannel._angular_diff(10, 20) == 10

    def test_across_north(self):
        assert GyroCompassMonitorChannel._angular_diff(350, 10) == 20

    def test_same_angle(self):
        assert GyroCompassMonitorChannel._angular_diff(45, 45) == 0
