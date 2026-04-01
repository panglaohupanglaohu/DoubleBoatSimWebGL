# -*- coding: utf-8 -*-
"""
Tests for VDR Recorder, Dynamic Positioning, and AIS Processor channels.
"""

import asyncio
import math
import time
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from backend.channels.vdr_recorder import VDRRecorderChannel, VDR_REQUIRED_ITEMS, _EVENT_TO_VDR_ITEM
from backend.channels.dynamic_positioning import DynamicPositioningChannel, _haversine_m
from backend.channels.ais_processor import AISProcessorChannel


# ═══════════════════════════════════════════════════════════════
# Helper
# ═══════════════════════════════════════════════════════════════

def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.run(coro)


# ═══════════════════════════════════════════════════════════════
# VDR Recorder Channel Tests (20+)
# ═══════════════════════════════════════════════════════════════

class TestVDRRecorderChannel:

    def _make_vdr(self):
        ch = VDRRecorderChannel()
        ch.initialize()
        return ch

    # ---- init ----

    def test_vdr_init(self):
        ch = VDRRecorderChannel()
        assert ch._recording_buffer == []
        assert ch._recording is False
        assert ch._active is False
        assert ch._rolling_window_hours == 12.0

    def test_vdr_initialize(self):
        ch = VDRRecorderChannel()
        assert ch.initialize() is True
        assert ch._active is True
        assert ch._recording is True
        assert ch._initialized is True

    # ---- record events ----

    def test_vdr_record_navigation_event(self):
        ch = self._make_vdr()
        result = _run(ch.process_event({"type": "position_update", "lat": 31.0, "lon": 121.0}))
        assert result["status"] == "recorded"
        assert result["vdr_item"] == "position"
        assert result["buffer_size"] == 1

    def test_vdr_record_engine_event(self):
        ch = self._make_vdr()
        result = _run(ch.process_event({"type": "engine_update", "rpm": 1200}))
        assert result["status"] == "recorded"
        assert result["vdr_item"] == "engine_status"

    def test_vdr_record_alarm_event(self):
        ch = self._make_vdr()
        result = _run(ch.process_event({"type": "alarm_update", "code": "F01"}))
        assert result["status"] == "recorded"
        assert result["vdr_item"] == "alarm_status"

    def test_vdr_record_all_mapped_event_types(self):
        ch = self._make_vdr()
        for event_type, vdr_item in _EVENT_TO_VDR_ITEM.items():
            result = _run(ch.process_event({"type": event_type, "value": 1}))
            assert result["status"] == "recorded"
            assert result["vdr_item"] == vdr_item

    def test_vdr_unmapped_event_ignored(self):
        ch = self._make_vdr()
        result = _run(ch.process_event({"type": "unknown_event"}))
        assert result["status"] == "ignored"

    # ---- recording status ----

    def test_vdr_recording_status(self):
        ch = self._make_vdr()
        _run(ch.process_event({"type": "position_update", "lat": 1.0, "lon": 2.0}))
        status = ch.get_recording_status()
        assert "recording" in status
        assert status["recording"] is True
        assert "items_coverage" in status
        assert "covered_items" in status
        assert "buffer_size" in status
        assert status["buffer_size"] == 1
        assert "oldest_record" in status
        assert "newest_record" in status

    def test_vdr_recording_status_empty(self):
        ch = self._make_vdr()
        status = ch.get_recording_status()
        assert status["buffer_size"] == 0
        assert status["oldest_record"] is None
        assert status["newest_record"] is None

    # ---- data coverage ----

    def test_vdr_data_coverage(self):
        ch = self._make_vdr()
        # Record 3 distinct VDR items
        _run(ch.process_event({"type": "position_update", "lat": 1}))
        _run(ch.process_event({"type": "speed_update", "speed": 10}))
        _run(ch.process_event({"type": "heading_update", "heading": 90}))
        status = ch.get_recording_status()
        expected_coverage = 3 / len(VDR_REQUIRED_ITEMS)
        assert abs(status["items_coverage"] - expected_coverage) < 1e-9

    # ---- integrity ----

    def test_vdr_verify_integrity_complete(self):
        ch = self._make_vdr()
        # Record every mapped event type to cover all required items that have mappings
        for event_type in _EVENT_TO_VDR_ITEM:
            _run(ch.process_event({"type": event_type, "v": 1}))
        result = ch.verify_data_integrity()
        # "date_time" has no event mapping, so it will be missing
        covered_via_events = set(_EVENT_TO_VDR_ITEM.values())
        expected_missing = [item for item in VDR_REQUIRED_ITEMS if item not in covered_via_events]
        assert result["missing_items"] == expected_missing

    def test_vdr_verify_integrity_incomplete(self):
        ch = self._make_vdr()
        _run(ch.process_event({"type": "position_update", "lat": 1}))
        result = ch.verify_data_integrity()
        assert result["complete"] is False
        assert len(result["missing_items"]) > 0
        assert "position" not in result["missing_items"]

    # ---- rolling window ----

    def test_vdr_rolling_window_trim(self):
        ch = self._make_vdr()
        # Insert a record with an old timestamp (13 hours ago)
        old_time = (datetime.now() - timedelta(hours=13)).isoformat()
        ch._recording_buffer.append({
            "timestamp": old_time,
            "vdr_item": "position",
            "event_type": "position_update",
            "data": {},
        })
        assert len(ch._recording_buffer) == 1
        # Trigger trim
        ch._trim_rolling_window()
        assert len(ch._recording_buffer) == 0

    def test_vdr_rolling_window_keeps_recent(self):
        ch = self._make_vdr()
        _run(ch.process_event({"type": "position_update", "lat": 1}))
        ch._trim_rolling_window()
        assert len(ch._recording_buffer) == 1

    # ---- export capsule ----

    def test_vdr_export_capsule(self):
        ch = self._make_vdr()
        _run(ch.process_event({"type": "position_update", "lat": 1}))
        _run(ch.process_event({"type": "speed_update", "speed": 10}))
        # All records are "now", so a wide range should capture all
        start = (datetime.now() - timedelta(hours=1)).isoformat()
        end = (datetime.now() + timedelta(hours=1)).isoformat()
        capsule = ch.export_capsule(start, end)
        assert len(capsule) == 2

    def test_vdr_export_capsule_empty_range(self):
        ch = self._make_vdr()
        _run(ch.process_event({"type": "position_update", "lat": 1}))
        # Range in the past
        start = (datetime.now() - timedelta(hours=10)).isoformat()
        end = (datetime.now() - timedelta(hours=9)).isoformat()
        capsule = ch.export_capsule(start, end)
        assert capsule == []

    # ---- process_event routing ----

    def test_vdr_process_event(self):
        ch = self._make_vdr()
        result = _run(ch.process_event({"type": "wind_update", "wind_speed": 15}))
        assert result["status"] == "recorded"
        assert result["vdr_item"] == "wind"

    # ---- get_status ----

    def test_vdr_get_status(self):
        ch = self._make_vdr()
        status = ch.get_status()
        assert status["name"] == "vdr_recorder"
        assert status["active"] is True
        assert status["initialized"] is True
        assert "recording" in status
        assert "buffer_size" in status
        assert "data_coverage" in status
        assert "rolling_window_hours" in status

    # ---- multiple events same type ----

    def test_vdr_multiple_events_same_type(self):
        ch = self._make_vdr()
        for i in range(5):
            _run(ch.process_event({"type": "position_update", "lat": i}))
        assert len(ch._recording_buffer) == 5
        # Coverage should still count "position" only once
        covered = ch._covered_items()
        assert "position" in covered

    # ---- custom rolling window ----

    def test_vdr_custom_rolling_window(self):
        ch = VDRRecorderChannel()
        ch._rolling_window_hours = 1.0
        ch.initialize()
        # Insert a record 2 hours old
        old_time = (datetime.now() - timedelta(hours=2)).isoformat()
        ch._recording_buffer.append({
            "timestamp": old_time,
            "vdr_item": "position",
            "event_type": "position_update",
            "data": {},
        })
        ch._trim_rolling_window()
        assert len(ch._recording_buffer) == 0

    # ---- shutdown ----

    def test_vdr_shutdown(self):
        ch = self._make_vdr()
        assert ch.shutdown() is True
        assert ch._active is False
        assert ch._recording is False
        assert ch._initialized is False

    # ---- start / stop ----

    def test_vdr_start_stop(self):
        ch = VDRRecorderChannel()
        _run(ch.start())
        assert ch._active is True
        assert ch._recording is True
        _run(ch.stop())
        assert ch._active is False
        assert ch._recording is False


# ═══════════════════════════════════════════════════════════════
# Dynamic Positioning Channel Tests (20+)
# ═══════════════════════════════════════════════════════════════

class TestDynamicPositioningChannel:

    def _make_dp(self):
        ch = DynamicPositioningChannel()
        ch.initialize()
        return ch

    # ---- init ----

    def test_dp_init(self):
        ch = DynamicPositioningChannel()
        assert ch._dp_mode == "standby"
        assert ch._station is None
        assert ch._active is False
        assert ch._excursion_limit_m == 25.0

    def test_dp_initialize(self):
        ch = DynamicPositioningChannel()
        assert ch.initialize() is True
        assert ch._active is True
        assert ch._initialized is True

    # ---- set station ----

    def test_dp_set_station(self):
        ch = self._make_dp()
        result = ch.set_station(31.0, 121.0, heading=45.0)
        assert result["status"] == "station_set"
        assert result["station"]["lat"] == 31.0
        assert result["station"]["lon"] == 121.0
        assert result["station"]["heading"] == 45.0

    def test_dp_set_station_activates_mode(self):
        ch = self._make_dp()
        assert ch._dp_mode == "standby"
        ch.set_station(31.0, 121.0)
        assert ch._dp_mode == "station_keeping"

    # ---- compute position error ----

    def test_dp_compute_position_error_no_station(self):
        ch = self._make_dp()
        result = ch.compute_position_error()
        assert "error" in result
        assert result["distance_m"] == 0.0

    def test_dp_compute_position_error(self):
        ch = self._make_dp()
        ch.set_station(31.0, 121.0)
        ch._current_position = {"lat": 31.001, "lon": 121.001, "heading": 0.0}
        result = ch.compute_position_error()
        assert result["distance_m"] > 0
        assert "heading_error_deg" in result
        assert "within_limit" in result

    def test_dp_compute_position_error_zero(self):
        ch = self._make_dp()
        ch.set_station(31.0, 121.0, heading=90.0)
        ch._current_position = {"lat": 31.0, "lon": 121.0, "heading": 90.0}
        result = ch.compute_position_error()
        assert result["distance_m"] == 0.0
        assert result["heading_error_deg"] == 0.0
        assert result["within_limit"] is True

    # ---- thruster allocation ----

    def test_dp_compute_thruster_allocation(self):
        ch = self._make_dp()
        ch.set_station(31.0, 121.0)
        ch._current_position = {"lat": 31.0001, "lon": 121.0001, "heading": 0.0}
        result = ch.compute_thruster_allocation()
        assert result["allocated"] is True
        assert "thrust_ratio" in result
        assert "bearing_deg" in result
        assert len(result["thrusters"]) == 4

    def test_dp_compute_thruster_allocation_no_station(self):
        ch = self._make_dp()
        result = ch.compute_thruster_allocation()
        assert result["allocated"] is False
        assert result["reason"] == "no station set"

    def test_dp_thruster_tunnel_vs_azimuth(self):
        ch = self._make_dp()
        ch.set_station(31.0, 121.0, heading=90.0)
        ch._current_position = {"lat": 31.001, "lon": 121.001, "heading": 0.0}
        result = ch.compute_thruster_allocation()
        for t in result["thrusters"]:
            if t["type"] == "tunnel":
                # Tunnel thrusters should get heading_ratio based thrust
                assert t["thrust_pct"] >= 0
            elif t["type"] == "azimuth":
                # Azimuth thrusters should get distance-based thrust
                assert t["thrust_pct"] >= 0
                assert "azimuth_deg" in t

    # ---- excursion alert ----

    def test_dp_excursion_alert(self):
        ch = self._make_dp()
        ch.set_station(31.0, 121.0)
        # Move far from station (approx 100m+ offset)
        result = _run(ch.process_event({
            "type": "position_update",
            "lat": 31.001,
            "lon": 121.001,
        }))
        assert result["status"] == "processed"
        # ~157m offset, well above 25m limit
        assert result["alarm"] is True
        assert result["excursion_m"] > 25.0

    # ---- process event ----

    def test_dp_process_position_update(self):
        ch = self._make_dp()
        result = _run(ch.process_event({
            "type": "position_update",
            "lat": 31.0,
            "lon": 121.0,
            "heading": 45.0,
        }))
        assert result["status"] == "processed"
        assert ch._current_position["lat"] == 31.0
        assert ch._current_position["heading"] == 45.0

    def test_dp_process_position_update_missing_coords(self):
        ch = self._make_dp()
        result = _run(ch.process_event({"type": "position_update"}))
        assert result["status"] == "error"

    def test_dp_process_set_station_event(self):
        ch = self._make_dp()
        result = _run(ch.process_event({
            "type": "set_station",
            "lat": 31.0,
            "lon": 121.0,
            "heading": 90.0,
        }))
        assert result["status"] == "station_set"
        assert ch._dp_mode == "station_keeping"

    def test_dp_process_set_station_missing_coords(self):
        ch = self._make_dp()
        result = _run(ch.process_event({"type": "set_station"}))
        assert result["status"] == "error"

    def test_dp_process_wind_update(self):
        ch = self._make_dp()
        result = _run(ch.process_event({"type": "wind_update", "wind_speed": 15.0}))
        assert result["status"] == "processed"
        assert ch._wind_speed == 15.0

    def test_dp_process_unknown_event(self):
        ch = self._make_dp()
        result = _run(ch.process_event({"type": "unknown"}))
        assert result["status"] == "ignored"

    # ---- capability plot ----

    def test_dp_get_capability_plot(self):
        ch = self._make_dp()
        result = ch.get_capability_plot()
        assert result["max_thrust_kn"] == 400.0
        assert result["wind_force_kn"] == 0.0
        assert result["current_force_kn"] == 0.0
        assert result["capable"] is True
        assert result["utilisation_pct"] == 0.0

    def test_dp_get_capability_plot_with_environment(self):
        ch = self._make_dp()
        result = ch.get_capability_plot(wind_speed=20.0, current_speed=3.0)
        assert result["wind_force_kn"] == 0.05 * 20.0 ** 2  # 20.0
        assert result["current_force_kn"] == 0.1 * 3.0 ** 2  # 0.9
        assert result["total_env_force_kn"] == 20.9
        assert result["capable"] is True
        assert result["utilisation_pct"] > 0

    def test_dp_get_capability_plot_over_capacity(self):
        ch = self._make_dp()
        # Wind speed high enough to exceed capability
        # max_thrust = 400, wind_force = 0.05 * v^2 → v = sqrt(400/0.05) = ~89.4
        result = ch.get_capability_plot(wind_speed=100.0)
        assert result["capable"] is False
        assert result["utilisation_pct"] > 100.0

    # ---- get_status ----

    def test_dp_get_status(self):
        ch = self._make_dp()
        status = ch.get_status()
        assert status["name"] == "dynamic_positioning"
        assert status["active"] is True
        assert status["dp_mode"] == "standby"
        assert status["station"] is None
        assert "excursion_m" in status
        assert "excursion_limit_m" in status
        assert "thrusters" in status
        assert len(status["thrusters"]) == 4

    # ---- haversine ----

    def test_dp_haversine_known_values(self):
        # Same point → 0
        assert _haversine_m(0, 0, 0, 0) == 0.0
        # ~111 km per degree of latitude at equator
        dist = _haversine_m(0, 0, 1, 0)
        assert 111_000 < dist < 111_400

    def test_dp_haversine_symmetry(self):
        d1 = _haversine_m(31.0, 121.0, 32.0, 122.0)
        d2 = _haversine_m(32.0, 122.0, 31.0, 121.0)
        assert abs(d1 - d2) < 0.01

    # ---- custom excursion limit ----

    def test_dp_custom_excursion_limit(self):
        ch = self._make_dp()
        ch._excursion_limit_m = 50.0
        ch.set_station(31.0, 121.0)
        ch._current_position = {"lat": 31.0003, "lon": 121.0003, "heading": 0.0}
        error = ch.compute_position_error()
        dist = error["distance_m"]
        # With 50m limit, ~47m offset should be within limit
        assert error["within_limit"] == (dist <= 50.0)

    # ---- standby mode ----

    def test_dp_standby_mode(self):
        ch = self._make_dp()
        # No station set, standby → position update should NOT alarm
        result = _run(ch.process_event({
            "type": "position_update",
            "lat": 50.0,
            "lon": 50.0,
        }))
        assert result["alarm"] is False

    # ---- shutdown ----

    def test_dp_shutdown(self):
        ch = self._make_dp()
        ch.set_station(31.0, 121.0)
        assert ch.shutdown() is True
        assert ch._active is False
        assert ch._dp_mode == "standby"

    # ---- start / stop ----

    def test_dp_start_stop(self):
        ch = DynamicPositioningChannel()
        _run(ch.start())
        assert ch._active is True
        _run(ch.stop())
        assert ch._active is False
        assert ch._dp_mode == "standby"


# ═══════════════════════════════════════════════════════════════
# AIS Processor Channel Tests (20+)
# ═══════════════════════════════════════════════════════════════

class TestAISProcessorChannel:

    def _make_ais(self):
        ch = AISProcessorChannel()
        ch.initialize()
        return ch

    # ---- init ----

    def test_ais_init(self):
        ch = AISProcessorChannel()
        assert ch._targets == {}
        assert ch._active is False
        assert ch._target_timeout_class_a == 180.0
        assert ch._target_timeout_class_b == 360.0

    def test_ais_initialize(self):
        ch = AISProcessorChannel()
        assert ch.initialize() is True
        assert ch._active is True

    # ---- decode messages ----

    def test_ais_decode_type1_position_report(self):
        ch = self._make_ais()
        result = ch.decode_message(1, {
            "mmsi": 123456789,
            "lat": 31.0,
            "lon": 121.0,
            "sog": 12.5,
            "cog": 180.0,
            "heading": 179.0,
        })
        assert result["mmsi"] == 123456789
        assert result["lat"] == 31.0
        assert result["sog"] == 12.5
        assert result["target_class"] == "A"
        assert result["msg_type"] == 1

    def test_ais_decode_type2(self):
        ch = self._make_ais()
        result = ch.decode_message(2, {"mmsi": 111222333, "lat": 30.0, "lon": 120.0})
        assert result["target_class"] == "A"
        assert result["msg_type"] == 2

    def test_ais_decode_type3(self):
        ch = self._make_ais()
        result = ch.decode_message(3, {"mmsi": 111222333, "lat": 30.0, "lon": 120.0})
        assert result["target_class"] == "A"
        assert result["msg_type"] == 3

    def test_ais_decode_type5_static(self):
        ch = self._make_ais()
        result = ch.decode_message(5, {
            "mmsi": 123456789,
            "imo": 9876543,
            "callsign": "ABCD",
            "name": "TEST VESSEL",
            "ship_type": 70,
            "destination": "SHANGHAI",
            "draught": 10.5,
        })
        assert result["mmsi"] == 123456789
        assert result["imo"] == 9876543
        assert result["name"] == "TEST VESSEL"
        assert result["target_class"] == "A"

    def test_ais_decode_type18_classb(self):
        ch = self._make_ais()
        result = ch.decode_message(18, {
            "mmsi": 987654321,
            "lat": 32.0,
            "lon": 122.0,
            "sog": 5.0,
            "cog": 90.0,
        })
        assert result["mmsi"] == 987654321
        assert result["target_class"] == "B"
        assert result["msg_type"] == 18

    def test_ais_decode_type19(self):
        ch = self._make_ais()
        result = ch.decode_message(19, {"mmsi": 987654321, "lat": 32.0, "lon": 122.0})
        assert result["target_class"] == "B"

    def test_ais_decode_type21_aton(self):
        ch = self._make_ais()
        result = ch.decode_message(21, {
            "mmsi": 555555555,
            "lat": 33.0,
            "lon": 123.0,
            "name": "BUOY 42",
            "aid_type": 3,
        })
        assert result["mmsi"] == 555555555
        assert result["name"] == "BUOY 42"
        assert result["target_class"] == "AtoN"

    def test_ais_decode_type24_classb_static(self):
        ch = self._make_ais()
        result = ch.decode_message(24, {
            "mmsi": 987654321,
            "name": "SMALL BOAT",
            "ship_type": 36,
            "callsign": "WXYZ",
        })
        assert result["mmsi"] == 987654321
        assert result["target_class"] == "B"
        assert result["name"] == "SMALL BOAT"

    def test_ais_decode_unsupported_type(self):
        ch = self._make_ais()
        result = ch.decode_message(99, {"mmsi": 123})
        assert "error" in result
        assert "unsupported" in result["error"]

    # ---- target management ----

    def test_ais_update_target_new(self):
        ch = self._make_ais()
        decoded = {"lat": 31.0, "lon": 121.0, "target_class": "A"}
        result = ch.update_target(123456789, decoded)
        assert "last_update" in result
        assert ch._targets[123456789]["lat"] == 31.0

    def test_ais_update_target_existing(self):
        ch = self._make_ais()
        ch.update_target(123456789, {"lat": 31.0, "lon": 121.0, "target_class": "A"})
        ch.update_target(123456789, {"lat": 31.5, "lon": 121.5, "target_class": "A"})
        # MMSI dedup: should still be one target
        assert len(ch._targets) == 1
        assert ch._targets[123456789]["lat"] == 31.5

    def test_ais_get_target_table(self):
        ch = self._make_ais()
        ch.update_target(111, {"target_class": "A", "lat": 1})
        ch.update_target(222, {"target_class": "B", "lat": 2})
        table = ch.get_target_table()
        assert len(table) == 2
        mmsis = {t["mmsi"] for t in table}
        assert mmsis == {111, 222}

    def test_ais_get_target_by_mmsi(self):
        ch = self._make_ais()
        ch.update_target(123456789, {"target_class": "A", "name": "VESSEL"})
        target = ch.get_target(123456789)
        assert target is not None
        assert target["mmsi"] == 123456789

    def test_ais_get_target_not_found(self):
        ch = self._make_ais()
        target = ch.get_target(999999999)
        assert target is None

    # ---- cleanup expired ----

    def test_ais_cleanup_expired_class_a(self):
        ch = self._make_ais()
        # Insert a target with old timestamp (>180s ago)
        old_time = (datetime.now() - timedelta(seconds=200)).isoformat()
        ch._targets[111] = {"target_class": "A", "last_update": old_time}
        ch._cleanup_expired()
        assert 111 not in ch._targets

    def test_ais_cleanup_expired_class_b(self):
        ch = self._make_ais()
        # Class B timeout is 360s
        old_time = (datetime.now() - timedelta(seconds=400)).isoformat()
        ch._targets[222] = {"target_class": "B", "last_update": old_time}
        ch._cleanup_expired()
        assert 222 not in ch._targets

    def test_ais_cleanup_keeps_fresh(self):
        ch = self._make_ais()
        fresh_time = datetime.now().isoformat()
        ch._targets[333] = {"target_class": "A", "last_update": fresh_time}
        ch._cleanup_expired()
        assert 333 in ch._targets

    def test_ais_cleanup_class_b_within_timeout(self):
        ch = self._make_ais()
        # Class B at 200s is within its 360s timeout
        recent = (datetime.now() - timedelta(seconds=200)).isoformat()
        ch._targets[444] = {"target_class": "B", "last_update": recent}
        ch._cleanup_expired()
        assert 444 in ch._targets

    def test_ais_cleanup_no_last_update(self):
        ch = self._make_ais()
        ch._targets[555] = {"target_class": "A"}
        ch._cleanup_expired()
        assert 555 not in ch._targets

    # ---- process_event ----

    def test_ais_process_event(self):
        ch = self._make_ais()
        result = _run(ch.process_event({
            "type": "ais_message",
            "msg_type": 1,
            "payload": {"mmsi": 123456789, "lat": 31.0, "lon": 121.0},
        }))
        assert result["status"] == "processed"
        assert result["mmsi"] == 123456789

    def test_ais_process_event_wrong_type(self):
        ch = self._make_ais()
        result = _run(ch.process_event({"type": "position_update"}))
        assert result["status"] == "ignored"

    def test_ais_process_event_no_msg_type(self):
        ch = self._make_ais()
        result = _run(ch.process_event({"type": "ais_message"}))
        assert result["status"] == "error"

    def test_ais_process_event_unsupported_msg_type(self):
        ch = self._make_ais()
        result = _run(ch.process_event({
            "type": "ais_message",
            "msg_type": 99,
            "payload": {"mmsi": 111},
        }))
        assert result["status"] == "error"

    # ---- get_status ----

    def test_ais_get_status(self):
        ch = self._make_ais()
        ch.update_target(111, {"target_class": "A"})
        ch.update_target(222, {"target_class": "B"})
        status = ch.get_status()
        assert status["name"] == "ais_processor"
        assert status["active"] is True
        assert status["active_targets"] == 2
        assert status["class_a_count"] == 1
        assert status["class_b_count"] == 1

    # ---- multiple targets ----

    def test_ais_multiple_targets(self):
        ch = self._make_ais()
        for i in range(10):
            ch.update_target(100 + i, {"target_class": "A", "lat": i})
        assert len(ch._targets) == 10
        table = ch.get_target_table()
        assert len(table) == 10

    # ---- target class detection ----

    def test_ais_target_class_detection(self):
        ch = self._make_ais()
        # Type 1 → Class A
        decoded_a = ch.decode_message(1, {"mmsi": 111, "lat": 1, "lon": 1})
        assert decoded_a["target_class"] == "A"
        # Type 18 → Class B
        decoded_b = ch.decode_message(18, {"mmsi": 222, "lat": 2, "lon": 2})
        assert decoded_b["target_class"] == "B"
        # Type 21 → AtoN
        decoded_aton = ch.decode_message(21, {"mmsi": 333, "lat": 3, "lon": 3})
        assert decoded_aton["target_class"] == "AtoN"

    # ---- shutdown ----

    def test_ais_shutdown(self):
        ch = self._make_ais()
        assert ch.shutdown() is True
        assert ch._active is False
        assert ch._initialized is False

    # ---- start / stop ----

    def test_ais_start_stop(self):
        ch = AISProcessorChannel()
        _run(ch.start())
        assert ch._active is True
        _run(ch.stop())
        assert ch._active is False

    # ---- defaults for missing payload fields ----

    def test_ais_decode_type1_defaults(self):
        ch = self._make_ais()
        result = ch.decode_message(1, {"mmsi": 111})
        assert result["sog"] == 0.0
        assert result["cog"] == 0.0
        assert result["heading"] == 0.0
        assert result["nav_status"] == 0

    def test_ais_decode_type5_defaults(self):
        ch = self._make_ais()
        result = ch.decode_message(5, {"mmsi": 111})
        assert result["callsign"] == ""
        assert result["name"] == ""
        assert result["ship_type"] == 0
        assert result["draught"] == 0.0
