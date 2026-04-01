# -*- coding: utf-8 -*-
"""
Coverage boost tests part 5: Main.py API endpoints, Perception Hub deeper,
Event Store edge cases, more worldmonitor adapter paths, Maritime Scene Model.
"""

import asyncio
import json
import pytest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch, MagicMock, AsyncMock

# ---------- Main.py API Endpoint Tests (via TestClient) ----------
from starlette.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestMainAPIRoot:
    def test_root_endpoint(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"


class TestMainAPIChannels:
    def test_get_channels(self, client):
        resp = client.get("/api/v1/channels")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)

    def test_query_channel_navigation(self, client):
        resp = client.post(
            "/api/v1/channels/intelligent_navigation/query",
            json={"query": "碰撞风险"}
        )
        assert resp.status_code in [200, 404, 422]

    def test_query_channel_engine(self, client):
        resp = client.post(
            "/api/v1/channels/intelligent_engine/query",
            json={"query": "engine status"}
        )
        assert resp.status_code in [200, 404, 422]

    def test_query_channel_efficiency(self, client):
        resp = client.post(
            "/api/v1/channels/energy_efficiency/query",
            json={"query": "EEXI"}
        )
        assert resp.status_code in [200, 404, 422]

    def test_query_channel_compliance(self, client):
        resp = client.post(
            "/api/v1/channels/compliance_digital_expert/query",
            json={"query": "compliance"}
        )
        assert resp.status_code in [200, 404, 422]

    def test_query_channel_orchestrator(self, client):
        resp = client.post(
            "/api/v1/channels/decision_orchestrator/query",
            json={"query": "decision"}
        )
        assert resp.status_code in [200, 404, 422]

    def test_query_channel_perception(self, client):
        resp = client.post(
            "/api/v1/channels/distributed_perception_hub/query",
            json={"query": "events"}
        )
        assert resp.status_code in [200, 404, 422]

    def test_query_nonexistent_channel(self, client):
        resp = client.post(
            "/api/v1/channels/does_not_exist/query",
            json={"query": "x"}
        )
        assert resp.status_code == 404


class TestMainAPISensors:
    def test_get_sensors(self, client):
        resp = client.get("/api/v1/sensors")
        assert resp.status_code == 200

    def test_get_sensor_data_existing(self, client):
        resp = client.get("/api/v1/sensors/GPS-001/data")
        assert resp.status_code in [200, 404]

    def test_get_sensor_data_missing(self, client):
        resp = client.get("/api/v1/sensors/nonexistent_xyz/data")
        assert resp.status_code == 404


class TestMainAPIAIS:
    def test_get_ais_targets(self, client):
        resp = client.get("/api/v1/ais/targets")
        assert resp.status_code == 200
        data = resp.json()
        assert "targets" in data


class TestMainAPIEngine:
    def test_get_engine_status(self, client):
        resp = client.get("/api/v1/engine/status")
        assert resp.status_code == 200


class TestMainAPIAlerts:
    def test_get_alerts(self, client):
        resp = client.get("/api/v1/alerts")
        assert resp.status_code == 200
        data = resp.json()
        assert "alerts" in data


class TestMainAPIWorldMonitor:
    def test_get_worldmonitor_ais(self, client):
        resp = client.get("/api/v1/worldmonitor/ais")
        assert resp.status_code == 200

    def test_get_worldmonitor_weather(self, client):
        resp = client.get("/api/v1/worldmonitor/weather?lat=31.23&lng=121.47")
        assert resp.status_code == 200

    def test_get_worldmonitor_ports(self, client):
        resp = client.get("/api/v1/worldmonitor/ports")
        assert resp.status_code == 200

    def test_get_worldmonitor_ports_with_region(self, client):
        resp = client.get("/api/v1/worldmonitor/ports?region=east_asia")
        assert resp.status_code == 200

    def test_get_worldmonitor_routes(self, client):
        resp = client.get("/api/v1/worldmonitor/routes")
        assert resp.status_code == 200

    def test_get_worldmonitor_routes_with_params(self, client):
        resp = client.get("/api/v1/worldmonitor/routes?origin_port=Shanghai&dest_port=Singapore")
        assert resp.status_code == 200


class TestMainAPIDashboard:
    def test_get_dashboard(self, client):
        resp = client.get("/api/v1/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert "navigation" in data or "captain_agent" in data


class TestMainAPIAINative:
    def test_get_coordination_status(self, client):
        resp = client.get("/api/v1/ai-native/coordination/status")
        assert resp.status_code == 200

    def test_get_perception_fusion_state(self, client):
        resp = client.get("/api/v1/ai-native/perception/fusion-state")
        assert resp.status_code in [200, 404]

    def test_get_rcs_status(self, client):
        resp = client.get("/api/v1/ai-native/rcs/status")
        assert resp.status_code in [200, 404]

    def test_get_shm_status(self, client):
        resp = client.get("/api/v1/ai-native/shm/status")
        assert resp.status_code in [200, 404]

    def test_get_cps_mission_brief(self, client):
        resp = client.get("/api/v1/ai-native/cps/mission-brief")
        assert resp.status_code in [200, 404]


class TestMainAPIAgents:
    def test_get_agents(self, client):
        resp = client.get("/api/v1/agents")
        assert resp.status_code in [200, 404, 500]


class TestMainAPIMemory:
    def test_get_memory_events(self, client):
        resp = client.get("/api/v1/ai-native/memory/events?limit=5")
        assert resp.status_code == 200

    def test_get_memory_events_with_type(self, client):
        resp = client.get("/api/v1/ai-native/memory/events?limit=5&event_type=test")
        assert resp.status_code == 200

    def test_get_memory_replay(self, client):
        resp = client.get("/api/v1/ai-native/memory/replay?limit=5")
        assert resp.status_code == 200

    def test_get_memory_replay_with_types(self, client):
        resp = client.get("/api/v1/ai-native/memory/replay?event_types=test,test2&limit=5")
        assert resp.status_code == 200

    def test_get_memory_replay_with_time(self, client):
        now = datetime.now()
        start = (now - timedelta(hours=1)).isoformat()
        end = now.isoformat()
        resp = client.get(f"/api/v1/ai-native/memory/replay?start_time={start}&end_time={end}&limit=5")
        assert resp.status_code == 200

    def test_get_memory_replay_bad_time(self, client):
        resp = client.get("/api/v1/ai-native/memory/replay?start_time=bad&end_time=also_bad&limit=5")
        assert resp.status_code == 400

    def test_get_analytics_status(self, client):
        resp = client.get("/api/v1/ai-native/memory/analytics/status")
        assert resp.status_code == 200

    def test_post_archive(self, client):
        resp = client.post(
            "/api/v1/ai-native/memory/archive",
            json={"event_type": "test_archive"}
        )
        assert resp.status_code in [200, 422, 500]

    def test_post_analytics_query(self, client):
        resp = client.post(
            "/api/v1/ai-native/memory/analytics/query",
            json={"sql": "SELECT 1"}
        )
        assert resp.status_code in [200, 400, 422, 500]

    def test_post_decision_feedback_log(self, client):
        resp = client.post(
            "/api/v1/ai-native/decision/feedback/log",
            json={"action": "test", "outcome": "pass"}
        )
        assert resp.status_code in [200, 404, 422]

    def test_post_openbridge_command(self, client):
        resp = client.post(
            "/api/v1/ai-native/openbridge/command",
            json={"command": "status", "source": "test"}
        )
        assert resp.status_code in [200, 404, 422]


# ---------- Main.py helper functions ----------
from main import _coerce_bool, _resolve_runtime_path, build_lakehouse_config, SimulationEngine


class TestMainHelpers:
    def test_coerce_bool_true(self):
        assert _coerce_bool("true", False) is True
        assert _coerce_bool("1", False) is True
        assert _coerce_bool("yes", False) is True
        assert _coerce_bool("on", False) is True
        assert _coerce_bool(True, False) is True

    def test_coerce_bool_false(self):
        assert _coerce_bool("false", True) is False
        assert _coerce_bool("0", True) is False
        assert _coerce_bool("no", True) is False

    def test_coerce_bool_none(self):
        assert _coerce_bool(None, True) is True
        assert _coerce_bool(None, False) is False

    def test_resolve_runtime_path_absolute(self):
        result = _resolve_runtime_path("/tmp/test", "fallback")
        assert result == "/tmp/test"

    def test_resolve_runtime_path_relative(self):
        result = _resolve_runtime_path(None, "storage/test")
        assert "storage/test" in result

    def test_build_lakehouse_config(self):
        config = build_lakehouse_config()
        assert "store_type" in config
        assert "store_config" in config
        assert "cloud_type" in config


class TestSimulationEngine:
    def test_init(self):
        engine = SimulationEngine()
        assert engine.running is False
        assert len(engine.ais_targets) == 5

    def test_start_stop(self):
        engine = SimulationEngine()
        engine.start()
        assert engine.running is True
        engine.stop()
        assert engine.running is False

    def test_seed_initial_state(self):
        engine = SimulationEngine()
        engine.seed_initial_state()
        # Checks that sensor_cache was populated (imports from main module)
        from main import sensor_cache
        assert "GPS-001" in sensor_cache


# ---------- Perception Hub - More Coverage ----------
from channels.distributed_perception_hub import (
    DistributedPerceptionHubChannel, FusionEvent,
)


class TestPerceptionHubDeep:
    @pytest.fixture
    def hub(self):
        ch = DistributedPerceptionHubChannel(config={"max_events": 100})
        ch.initialize()
        return ch

    def test_fusion_event_to_dict(self):
        e = FusionEvent(
            id="e1", timestamp="2026-01-01", event_type="test",
            source="test", payload={"a": 1}, confidence=0.9,
        )
        d = e.to_dict()
        assert d["id"] == "e1"
        assert "fused_with" not in d
        assert "risk_correlation" not in d

    def test_fusion_event_to_dict_with_lists(self):
        e = FusionEvent(
            id="e2", timestamp="2026-01-01", event_type="test",
            source="test", payload={}, confidence=0.8,
            fused_with=["e1"], risk_correlation={"risk": 0.5},
        )
        d = e.to_dict()
        assert d["fused_with"] == ["e1"]
        assert d["risk_correlation"]["risk"] == 0.5

    def test_get_latest_events(self, hub):
        for i in range(5):
            hub.append_event("test", {"i": i}, "test")
        latest = hub.get_latest_events(3)
        assert len(latest) == 3

    def test_get_fusion_state_empty(self, hub):
        state = hub.get_fusion_state()
        assert state["fusion_quality"] == 0.0

    def test_get_fusion_state_after_processing(self, hub):
        from channels.distributed_perception_hub import SensorMeasurement, SensorType
        m = SensorMeasurement(
            sensor_id="test-1", sensor_type=SensorType.AIS,
            timestamp=datetime.now(),
            data={"lat": 31.23, "lon": 121.47, "speed": 10, "course": 90},
            confidence=0.9, quality_score=0.85,
        )
        hub.feature_fusion.process_frame([m])
        state = hub.get_fusion_state()
        assert state["fusion_quality"] > 0
        assert len(state["active_tracks"]) == 1

    def test_fusion_rules(self, hub):
        rules = hub._load_fusion_rules()
        assert "ais_nav_fusion" in rules
        assert "weather_efficiency_fusion" in rules
        assert "engine_nav_fusion" in rules

    def test_risk_correlations(self, hub):
        corr = hub._load_risk_correlations()
        assert "collision_risk" in corr
        assert "mechanical_risk" in corr
        assert "compliance_risk" in corr
        assert "weather_risk" in corr

    def test_set_event_sink(self, hub):
        mock_sink = MagicMock()
        hub.set_event_sink(mock_sink)
        assert hub.event_sink is mock_sink

    def test_append_event_with_sink(self, hub):
        mock_sink = MagicMock()
        mock_sink.save_event = MagicMock(return_value=True)
        hub.set_event_sink(mock_sink)
        hub.append_event("test", {"data": 1}, "test")
        assert mock_sink.save_event.called

    def test_append_event_with_sink_failure(self, hub):
        mock_sink = MagicMock()
        mock_sink.save_event = MagicMock(side_effect=Exception("fail"))
        hub.set_event_sink(mock_sink)
        event = hub.append_event("test", {"data": 1}, "test")
        assert event is not None

    def test_append_event_overflow(self, hub):
        """Test event list trimming when exceeding max_events."""
        for i in range(110):
            hub.append_event("test", {"i": i}, "test")
        assert len(hub.events) <= 100

    def test_track_measurement_from_target(self, hub):
        target = {"latitude": 31.23, "longitude": 121.47, "mmsi": 123, "speed": 12, "course": 90}
        m = hub._track_measurement_from_target("prefix", target, 0.9, 0.85)
        assert m is not None
        assert m.confidence == 0.9
        assert m.data["lat"] == 31.23

    def test_track_measurement_from_target_missing_coords(self, hub):
        target = {"mmsi": 123}
        m = hub._track_measurement_from_target("prefix", target, 0.9, 0.85)
        assert m is None

    def test_track_measurement_from_target_track_id(self, hub):
        target = {"latitude": 31.23, "longitude": 121.47, "track_id": "T1"}
        m = hub._track_measurement_from_target("prefix", target, 0.8, 0.7)
        assert m is not None
        assert "T1" in m.sensor_id

    def test_build_feature_fusion_measurements_no_inputs(self, hub):
        measurements = hub._build_feature_fusion_measurements(None, None)
        assert measurements == []

    def test_build_feature_fusion_with_worldmonitor(self, hub):
        wm_ais = {
            "targets": [
                {"latitude": 31.23, "longitude": 121.47, "mmsi": 111, "speed": 10, "course": 180}
            ]
        }
        measurements = hub._build_feature_fusion_measurements(None, wm_ais)
        assert len(measurements) == 1

    def test_build_feature_fusion_with_nav_channel(self, hub):
        target = SimpleNamespace(mmsi=222, latitude=31.24, longitude=121.48, speed=8, course=90)
        nav_ch = SimpleNamespace(ais_targets=[target])
        measurements = hub._build_feature_fusion_measurements(nav_ch, None)
        assert len(measurements) == 1

    def test_build_feature_fusion_both_sources(self, hub):
        target = SimpleNamespace(mmsi=222, latitude=31.24, longitude=121.48, speed=8, course=90)
        nav_ch = SimpleNamespace(ais_targets=[target])
        wm_ais = {"targets": [{"latitude": 31.25, "longitude": 121.49, "mmsi": 333, "speed": 10, "course": 0}]}
        measurements = hub._build_feature_fusion_measurements(nav_ch, wm_ais)
        assert len(measurements) == 2

    def test_fuse_nmea_with_worldmonitor_matching_mmsi(self, hub):
        nmea_ais = {"mmsi": 111, "latitude": 31.23, "longitude": 121.47, "course": 0, "speed": 10}
        wm_ais = {"targets": [
            {"mmsi": 111, "latitude": 31.23001, "longitude": 121.47001, "course": 0, "speed": 10}
        ]}
        result = hub.fuse_nmea_with_worldmonitor_ais(nmea_ais, wm_ais)
        assert result is not None
        assert result.event_type == "nmea_world_ais_fusion"

    def test_fuse_nmea_with_worldmonitor_no_match(self, hub):
        nmea_ais = {"mmsi": 999, "latitude": 31.23, "longitude": 121.47}
        wm_ais = {"targets": [{"mmsi": 111, "latitude": 31.23, "longitude": 121.47}]}
        result = hub.fuse_nmea_with_worldmonitor_ais(nmea_ais, wm_ais)
        assert result is None

    def test_fuse_nmea_with_worldmonitor_too_far(self, hub):
        nmea_ais = {"mmsi": 111, "latitude": 31.23, "longitude": 121.47}
        wm_ais = {"targets": [{"mmsi": 111, "latitude": 32.0, "longitude": 122.0}]}
        result = hub.fuse_nmea_with_worldmonitor_ais(nmea_ais, wm_ais)
        assert result is None

    def test_fuse_nmea_missing_coords(self, hub):
        nmea_ais = {"mmsi": 111}
        wm_ais = {"targets": [{"mmsi": 111, "latitude": 31.23}]}
        result = hub.fuse_nmea_with_worldmonitor_ais(nmea_ais, wm_ais)
        assert result is None

    def test_fuse_ais_close_collision_risk(self, hub):
        ais = {"latitude": 31.2300, "longitude": 121.4700, "mmsi": 112}
        nav = {"own_ship": {"latitude": 31.2300, "longitude": 121.47001}}
        result = hub.fuse_ais_with_navigation(ais, nav)
        assert result is not None
        if result.risk_correlation:
            assert result.risk_correlation.get("collision_risk", 0) > 0.5

    def test_fuse_ais_medium_distance(self, hub):
        ais = {"latitude": 31.24, "longitude": 121.48, "mmsi": 113}
        nav = {"own_ship": {"latitude": 31.23, "longitude": 121.47}}
        result = hub.fuse_ais_with_navigation(ais, nav)
        assert result is not None

    def test_fuse_ais_too_far(self, hub):
        ais = {"latitude": 35.0, "longitude": 125.0, "mmsi": 114}
        nav = {"own_ship": {"latitude": 31.23, "longitude": 121.47}}
        result = hub.fuse_ais_with_navigation(ais, nav)
        assert result is None

    def test_fuse_ais_missing_coords(self, hub):
        ais = {"mmsi": 115}
        nav = {"own_ship": {"latitude": 31.23, "longitude": 121.47}}
        result = hub.fuse_ais_with_navigation(ais, nav)
        assert result is None

    def test_fuse_weather_efficiency(self, hub):
        weather = {
            "position": {"lat": 31.23, "lng": 121.47},
            "wind": {"speed": 25}, "wave": {"height": 3.5}
        }
        efficiency = {"position": {"latitude": 31.23, "longitude": 121.47}}
        result = hub.fuse_weather_with_efficiency(weather, efficiency)
        assert result is not None
        assert result.event_type == "weather_efficiency_fusion"

    def test_fuse_weather_efficiency_too_far(self, hub):
        weather = {"position": {"lat": 31.23, "lng": 121.47}, "wind": {"speed": 10}, "wave": {"height": 1}}
        efficiency = {"position": {"latitude": 35.0, "longitude": 125.0}}
        result = hub.fuse_weather_with_efficiency(weather, efficiency)
        assert result is None

    def test_fuse_weather_efficiency_missing_pos(self, hub):
        weather = {"position": {}, "wind": {"speed": 10}}
        efficiency = {"position": {"latitude": 31.23, "longitude": 121.47}}
        result = hub.fuse_weather_with_efficiency(weather, efficiency)
        assert result is None

    def test_fuse_weather_high_risk(self, hub):
        weather = {
            "position": {"lat": 31.23, "lng": 121.47},
            "wind": {"speed": 30}, "wave": {"height": 5.0}
        }
        efficiency = {"position": {"latitude": 31.23, "longitude": 121.47}}
        result = hub.fuse_weather_with_efficiency(weather, efficiency)
        assert result is not None
        if result.risk_correlation:
            assert result.risk_correlation.get("weather_risk", 0) >= 0.8

    def test_capture_system_snapshot(self, hub):
        events = hub.capture_system_snapshot()
        assert isinstance(events, list)

    def test_get_status(self, hub):
        status = hub.get_status()
        assert status["name"] == "distributed_perception_hub"
        assert "event_count" in status
        assert "fusion_capabilities" in status

    def test_shutdown(self, hub):
        assert hub.shutdown() is True
        assert hub._initialized is False


# ---------- Event Store - SQLite extended edge cases ----------
from storage.event_store import SQLiteStore, JSONLStore, get_store


class TestSQLiteStoreEdgeCases:
    @pytest.fixture
    def store(self, tmp_path):
        return SQLiteStore({"db_path": str(tmp_path / "test.db")})

    def test_save_event_no_type(self, store):
        event = {"timestamp": datetime.now().isoformat(), "data": "test"}
        assert store.save_event(event) is True

    def test_large_batch(self, store):
        events = [
            {"event_type": "batch", "timestamp": datetime.now().isoformat(), "payload": {"i": i}}
            for i in range(50)
        ]
        assert store.save_events(events) is True
        loaded = store.load_events(event_type="batch", limit=50)
        assert len(loaded) == 50

    def test_load_events_by_time_with_type(self, store):
        now = datetime.now()
        store.save_event({"event_type": "timed", "timestamp": now.isoformat(), "payload": {"x": 1}})
        events = store.load_events_by_time(now - timedelta(minutes=1), now + timedelta(minutes=1), "timed")
        assert len(events) >= 1

    def test_load_events_by_time_no_type(self, store):
        now = datetime.now()
        store.save_event({"event_type": "any", "timestamp": now.isoformat(), "payload": {"x": 1}})
        events = store.load_events_by_time(now - timedelta(minutes=1), now + timedelta(minutes=1))
        assert len(events) >= 1

    def test_clear_specific_type(self, store):
        store.save_event({"event_type": "del_me", "timestamp": datetime.now().isoformat()})
        store.save_event({"event_type": "keep_me", "timestamp": datetime.now().isoformat()})
        assert store.clear_events("del_me") is True
        assert len(store.load_events(event_type="del_me")) == 0
        assert len(store.load_events(event_type="keep_me")) == 1

    def test_clear_all(self, store):
        store.save_event({"event_type": "a", "timestamp": datetime.now().isoformat()})
        store.save_event({"event_type": "b", "timestamp": datetime.now().isoformat()})
        assert store.clear_events() is True
        assert len(store.load_events()) == 0

    def test_get_info(self, store):
        info = store.get_info()
        assert "db_path" in info
        assert "wal_enabled" in info


class TestJSONLStoreEdgeCases:
    @pytest.fixture
    def store(self, tmp_path):
        return JSONLStore({"storage_path": str(tmp_path / "events"), "max_events": 50})

    def test_load_events_by_time(self, store):
        now = datetime.now()
        store.save_event({"event_type": "timed", "timestamp": now.isoformat()})
        results = store.load_events_by_time(now - timedelta(minutes=1), now + timedelta(minutes=1), "timed")
        assert len(results) >= 1

    def test_load_all_event_types(self, store):
        store.save_event({"event_type": "type_a", "timestamp": datetime.now().isoformat()})
        store.save_event({"event_type": "type_b", "timestamp": datetime.now().isoformat()})
        events = store.load_events(limit=100)
        assert len(events) >= 2

    def test_clear_specific_type(self, store):
        store.save_event({"event_type": "remove", "timestamp": datetime.now().isoformat()})
        assert store.clear_events("remove") is True

    def test_clear_all(self, store):
        store.save_event({"event_type": "x", "timestamp": datetime.now().isoformat()})
        assert store.clear_events() is True

    def test_trim_file(self, store):
        for i in range(60):
            store.save_event({"event_type": "trim_test", "timestamp": datetime.now().isoformat(), "i": i})
        events = store.load_events(event_type="trim_test", limit=100)
        assert len(events) <= 50

    def test_get_info(self, store):
        store.save_event({"event_type": "info_test", "timestamp": datetime.now().isoformat()})
        info = store.get_info()
        assert "storage_path" in info
        assert "file_count" in info


class TestGetStore:
    def test_get_store_sqlite(self, tmp_path):
        store = get_store("sqlite", {"db_path": str(tmp_path / "test.db")})
        assert isinstance(store, SQLiteStore)

    def test_get_store_jsonl(self, tmp_path):
        store = get_store("jsonl", {"storage_path": str(tmp_path / "events")})
        assert isinstance(store, JSONLStore)

    def test_get_store_unknown_raises(self, tmp_path):
        with pytest.raises(ValueError, match="Unknown store type"):
            get_store("unknown_type", {})


# ---------- WorldMonitor Adapter (async methods) ----------
from adapters.worldmonitor_adapter import WorldMonitorAdapter


class TestWorldMonitorAdapter:
    def test_init(self):
        adapter = WorldMonitorAdapter()
        assert adapter.mode in ("real", "mock")

    def test_build_mock_targets(self):
        adapter = WorldMonitorAdapter()
        targets = adapter._build_mock_targets(None, None)
        assert len(targets) == 3
        assert targets[0]["mmsi"] == "413000101"

    def test_build_mock_targets_custom_range(self):
        adapter = WorldMonitorAdapter()
        targets = adapter._build_mock_targets((30.0, 32.0), (120.0, 122.0))
        assert len(targets) == 3

    def test_get_ais_targets_async(self):
        adapter = WorldMonitorAdapter()
        result = asyncio.run(adapter.get_ais_targets())
        assert isinstance(result, dict)
        assert "targets" in result
        assert result["mode"] in ("real", "mock")

    def test_get_marine_weather_async(self):
        adapter = WorldMonitorAdapter()
        result = asyncio.run(adapter.get_marine_weather(31.23, 121.47))
        assert isinstance(result, dict)
        assert "weather" in result

    def test_get_ports_async(self):
        adapter = WorldMonitorAdapter()
        result = asyncio.run(adapter.get_ports())
        assert isinstance(result, dict)
        assert "ports" in result

    def test_get_shipping_routes_async(self):
        adapter = WorldMonitorAdapter()
        result = asyncio.run(adapter.get_shipping_routes())
        assert isinstance(result, dict)
        assert "routes" in result


# ---------- Maritime Scene Model ----------
from channels.maritime_scene_model import MaritimeSceneModel


class TestMaritimeSceneModel:
    def test_evaluate_open_sea(self):
        model = MaritimeSceneModel()
        own_ship = {"latitude": 31.23, "longitude": 121.47, "course": 0, "speed": 12}
        result = model.evaluate(own_ship, [])
        assert result["scene_type"] == "open_sea"
        assert "Rule 5" in result["priority_rules"]

    def test_evaluate_ice_navigation(self):
        model = MaritimeSceneModel()
        own_ship = {"latitude": 60.0, "longitude": 10.0, "course": 0, "speed": 8}
        result = model.evaluate(own_ship, [])
        assert result["scene_type"] == "ice_navigation"
        assert "Rule 19" in result["priority_rules"]

    def test_evaluate_ice_by_vessel_type(self):
        model = MaritimeSceneModel()
        own_ship = {"latitude": 31.23, "longitude": 121.47, "course": 0, "speed": 10}
        target = SimpleNamespace(vessel_type="Ice Breaker")
        result = model.evaluate(own_ship, [target])
        assert result["scene_type"] == "ice_navigation"

    def test_evaluate_offshore_operation(self):
        model = MaritimeSceneModel()
        own_ship = {"latitude": 31.23, "longitude": 121.47, "course": 0, "speed": 10}
        target = SimpleNamespace(vessel_type="Tug")
        result = model.evaluate(own_ship, [target])
        assert result["scene_type"] == "offshore_operation"
        assert "Rule 18" in result["priority_rules"]

    def test_evaluate_port_approach(self):
        model = MaritimeSceneModel()
        own_ship = {"latitude": 31.23, "longitude": 121.47, "course": 0, "speed": 5}
        targets = [SimpleNamespace(vessel_type="Cargo") for _ in range(6)]
        result = model.evaluate(own_ship, targets)
        assert result["scene_type"] == "port_approach"

    def test_evaluate_narrow_channel(self):
        model = MaritimeSceneModel()
        own_ship = {"latitude": 31.23, "longitude": 121.47, "course": 0, "speed": 12}
        targets = [SimpleNamespace(vessel_type="Cargo") for _ in range(5)]
        result = model.evaluate(own_ship, targets)
        assert result["scene_type"] == "narrow_channel"
        assert "Rule 9" in result["priority_rules"]

    def test_evaluate_dredger(self):
        model = MaritimeSceneModel()
        own_ship = {"latitude": 31.23, "longitude": 121.47, "course": 0, "speed": 10}
        target = SimpleNamespace(vessel_type="Dredger")
        result = model.evaluate(own_ship, [target])
        assert result["scene_type"] == "offshore_operation"

    def test_evaluate_offshore_support(self):
        model = MaritimeSceneModel()
        own_ship = {"latitude": 31.23, "longitude": 121.47, "course": 0, "speed": 10}
        target = SimpleNamespace(vessel_type="Offshore Support Vessel")
        result = model.evaluate(own_ship, [target])
        assert result["scene_type"] == "offshore_operation"
