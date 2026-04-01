#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for distributed_perception_hub zero-value safety."""

from channels.distributed_perception_hub import DistributedPerceptionHubChannel


def _make_hub():
    hub = DistributedPerceptionHubChannel()
    hub.initialize()
    return hub


class TestTrackMeasurementZeroValues:
    """Test _track_measurement_from_target with zero coords."""

    def test_zero_lat_zero_lon_is_valid(self):
        hub = _make_hub()
        target = {"latitude": 0, "longitude": 0, "mmsi": "123456"}
        result = hub._track_measurement_from_target("test", target, 0.9, 0.9)
        assert result is not None
        assert result.data["lat"] == 0
        assert result.data["lon"] == 0

    def test_lat_none_is_rejected(self):
        hub = _make_hub()
        target = {"latitude": None, "longitude": 120.0}
        result = hub._track_measurement_from_target("test", target, 0.9, 0.9)
        assert result is None

    def test_lon_none_is_rejected(self):
        hub = _make_hub()
        target = {"latitude": 31.0, "longitude": None}
        result = hub._track_measurement_from_target("test", target, 0.9, 0.9)
        assert result is None

    def test_both_none_is_rejected(self):
        hub = _make_hub()
        target = {"latitude": None, "longitude": None}
        result = hub._track_measurement_from_target("test", target, 0.9, 0.9)
        assert result is None

    def test_normal_coords(self):
        hub = _make_hub()
        target = {"latitude": 31.23, "longitude": 121.47, "speed": 12.5, "course": 45.0}
        result = hub._track_measurement_from_target("nav", target, 0.92, 0.88)
        assert result is not None
        assert result.data["lat"] == 31.23
        assert result.data["lon"] == 121.47
        assert result.data["speed"] == 12.5

    def test_missing_lat_key_is_rejected(self):
        hub = _make_hub()
        target = {"longitude": 121.0}
        result = hub._track_measurement_from_target("test", target, 0.9, 0.9)
        assert result is None


class TestFuseAisNavZeroValues:
    """Test fuse_ais_with_navigation with zero coordinates."""

    def test_ais_zero_coords_valid(self):
        hub = _make_hub()
        ais = {"latitude": 0.0, "longitude": 0.0, "mmsi": "999"}
        nav = {"own_ship": {"latitude": 0.001, "longitude": 0.001}}
        result = hub.fuse_ais_with_navigation(ais, nav)
        assert result is not None
        assert result.event_type == "ais_nav_fusion"

    def test_ais_lat_none_rejected(self):
        hub = _make_hub()
        ais = {"latitude": None, "longitude": 120.0}
        nav = {"own_ship": {"latitude": 31.0, "longitude": 121.0}}
        result = hub.fuse_ais_with_navigation(ais, nav)
        assert result is None

    def test_nav_lon_none_rejected(self):
        hub = _make_hub()
        ais = {"latitude": 31.0, "longitude": 121.0}
        nav = {"own_ship": {"latitude": 31.0, "longitude": None}}
        result = hub.fuse_ais_with_navigation(ais, nav)
        assert result is None

    def test_weather_efficiency_zero_coords(self):
        hub = _make_hub()
        weather = {"position": {"lat": 0.0, "lng": 0.0}, "wind": {"speed": 10}}
        efficiency = {"position": {"latitude": 0.001, "longitude": 0.001}}
        result = hub.fuse_weather_with_efficiency(weather, efficiency)
        assert result is not None
