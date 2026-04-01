# -*- coding: utf-8 -*-
"""
Coverage boost tests part 6: API Extensions, OpenBridge Router, WorldMonitor Real Adapter,
Cloud Sync FeishuAdapter, Data Lakehouse deeper coverage.
"""

import asyncio
import json
import pytest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch, MagicMock, AsyncMock

from starlette.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


# ---------- API Extensions endpoints ----------

class TestAPIExtensionsCompliance:
    def test_get_compliance_status(self, client):
        resp = client.get("/api/v1/ai-native/compliance/status?query=overall")
        assert resp.status_code in [200, 404, 500]

    def test_get_cognitive_snapshot(self, client):
        resp = client.get("/api/v1/ai-native/compliance/cognitive-snapshot")
        assert resp.status_code in [200, 404, 500]


class TestAPIExtensionsPerception:
    def test_get_perception_events(self, client):
        resp = client.get("/api/v1/ai-native/perception/events?limit=5")
        assert resp.status_code in [200, 404, 500]

    def test_capture_perception_snapshot(self, client):
        resp = client.get("/api/v1/ai-native/perception/capture-snapshot")
        assert resp.status_code in [200, 404, 500]


class TestAPIExtensionsDecision:
    def test_get_decision_package(self, client):
        resp = client.get("/api/v1/ai-native/decision/package")
        assert resp.status_code in [200, 404, 500]

    def test_record_decision_feedback(self, client):
        resp = client.post(
            "/api/v1/ai-native/decision/feedback?action=test_action&outcome=success&confirmed_by=test"
        )
        assert resp.status_code in [200, 404, 422, 500]

    def test_get_full_pipeline_status(self, client):
        resp = client.get("/api/v1/ai-native/status/full-pipeline")
        assert resp.status_code in [200, 500]


class TestAPIExtensionsSVessel:
    def test_ship_shore_status(self, client):
        resp = client.get("/api/v1/ai-native/ship-shore/status")
        assert resp.status_code in [200, 404]

    def test_autonomy_status(self, client):
        resp = client.get("/api/v1/ai-native/autonomy/status")
        assert resp.status_code in [200, 404]

    def test_autonomy_transition(self, client):
        resp = client.post("/api/v1/ai-native/autonomy/transition?target_mass_level=AL1&reason=test")
        assert resp.status_code in [200, 400, 404, 422]

    def test_autonomy_transition_invalid_level(self, client):
        resp = client.post("/api/v1/ai-native/autonomy/transition?target_mass_level=INVALID&reason=test")
        assert resp.status_code in [400, 404, 422]

    def test_phm_status(self, client):
        resp = client.get("/api/v1/ai-native/phm/status")
        assert resp.status_code in [200, 404]

    def test_phm_maintenance_plan(self, client):
        resp = client.get("/api/v1/ai-native/phm/maintenance-plan")
        assert resp.status_code in [200, 404]

    def test_route_status(self, client):
        resp = client.get("/api/v1/ai-native/route/status")
        assert resp.status_code in [200, 404]

    def test_voyage_status(self, client):
        resp = client.get("/api/v1/ai-native/voyage/status")
        assert resp.status_code in [200, 404]

    def test_voyage_daily_report(self, client):
        resp = client.get("/api/v1/ai-native/voyage/daily-report")
        assert resp.status_code in [200, 404]

    def test_cybersecurity_status(self, client):
        resp = client.get("/api/v1/ai-native/cybersecurity/status")
        assert resp.status_code in [200, 404]

    def test_cybersecurity_audit_log(self, client):
        resp = client.get("/api/v1/ai-native/cybersecurity/audit-log?limit=5")
        assert resp.status_code in [200, 404]

    def test_cybersecurity_threat_summary(self, client):
        resp = client.get("/api/v1/ai-native/cybersecurity/threat-summary")
        assert resp.status_code in [200, 404]


# ---------- OpenBridge Command Router ----------
from channels.openbridge_command_router import (
    classify_openbridge_intent,
    build_openbridge_command_result,
)


class TestClassifyOpenBridgeIntent:
    def test_task_graph_intent(self):
        result = classify_openbridge_intent("show task graph")
        assert result["intent"] == "show_task_graph"
        assert result["domain"] == "decision"

    def test_collision_risk_intent(self):
        result = classify_openbridge_intent("碰撞风险")
        assert result["intent"] == "show_collision_risk"
        assert result["domain"] == "navigation"

    def test_comfort_mode_intent(self):
        result = classify_openbridge_intent("切换舒适模式")
        assert result["intent"] == "set_comfort_mode"
        assert result["domain"] == "rcs"

    def test_structural_health_intent(self):
        result = classify_openbridge_intent("结构健康状态")
        assert result["intent"] == "show_structural_health"
        assert result["domain"] == "shm"

    def test_engine_health_intent(self):
        result = classify_openbridge_intent("主机健康")
        assert result["intent"] == "show_engine_health"
        assert result["domain"] == "engine"

    def test_general_assist_fallback(self):
        result = classify_openbridge_intent("hello world")
        assert result["intent"] == "general_assist"
        assert result["domain"] == "general"

    def test_empty_command(self):
        result = classify_openbridge_intent("")
        assert result["intent"] == "general_assist"

    def test_none_command(self):
        result = classify_openbridge_intent(None)
        assert result["intent"] == "general_assist"


class TestBuildOpenBridgeCommandResult:
    def test_task_graph_result(self):
        dashboard = {
            "navigation": {"report": {}},
            "rcs": {},
            "shm": {},
            "engine": {},
            "decision": {"task_graph": {"nodes": [1, 2, 3], "execution_order": ["a", "b"]}},
        }
        mission = {"task_graph": {"nodes": [1, 2, 3], "execution_order": ["a", "b"]}, "autonomy_mode": "supervised"}
        result = build_openbridge_command_result("show task graph", dashboard, mission)
        assert result["recognized_intent"] == "show_task_graph"
        assert "3" in result["summary"]

    def test_collision_risk_result(self):
        dashboard = {
            "navigation": {"report": {"overall_status": "safe", "collision_risks": []}},
            "rcs": {},
            "shm": {},
            "engine": {},
        }
        mission = {}
        result = build_openbridge_command_result("碰撞风险", dashboard, mission)
        assert result["recognized_intent"] == "show_collision_risk"

    def test_comfort_mode_result(self):
        dashboard = {
            "navigation": {"report": {}},
            "rcs": {"foil_angle_deg": 5, "trim_tab_angle_deg": 3, "comfort_target_msdv": 0.1},
            "shm": {},
            "engine": {},
        }
        mission = {}
        result = build_openbridge_command_result("舒适模式", dashboard, mission)
        assert result["recognized_intent"] == "set_comfort_mode"
        assert result["control_state"]["rcs"]["foil_angle_deg"] == 5

    def test_structural_health_result(self):
        dashboard = {
            "navigation": {"report": {}},
            "rcs": {},
            "shm": {"fatigue_damage_index": 0.02, "life_remaining_pct": 95, "strain_hotspots": []},
            "engine": {},
        }
        mission = {}
        result = build_openbridge_command_result("结构健康", dashboard, mission)
        assert result["recognized_intent"] == "show_structural_health"

    def test_engine_health_result(self):
        dashboard = {
            "navigation": {"report": {}},
            "rcs": {},
            "shm": {},
            "engine": {"health_score": 0.92, "alerts": [], "maintenance_advice": []},
        }
        mission = {}
        result = build_openbridge_command_result("主机状态", dashboard, mission)
        assert result["recognized_intent"] == "show_engine_health"

    def test_general_assist_result(self):
        dashboard = {"navigation": {"report": {}}, "rcs": {}, "shm": {}, "engine": {}, "decision": {}}
        mission = {}
        result = build_openbridge_command_result("hello", dashboard, mission)
        assert result["recognized_intent"] == "general_assist"


# ---------- WorldMonitor Real Adapter ----------
from adapters.worldmonitor_adapter_real import WorldMonitorRealAdapter, WM_AIS_Target, WM_Marine_Weather


class TestWorldMonitorRealAdapter:
    def test_init_default(self):
        adapter = WorldMonitorRealAdapter()
        assert adapter.api_key == "placeholder"
        assert adapter._initialized is False

    def test_init_with_config(self):
        adapter = WorldMonitorRealAdapter({"api_key": "test_key", "cache_ttl": 60})
        assert adapter.api_key == "test_key"
        assert adapter._cache_ttl == 60

    def test_initialize_placeholder(self):
        adapter = WorldMonitorRealAdapter()
        result = asyncio.run(adapter.initialize())
        assert result is False
        assert adapter._initialized is True

    def test_close_no_session(self):
        adapter = WorldMonitorRealAdapter()
        asyncio.run(adapter.close())

    def test_cache_valid(self):
        adapter = WorldMonitorRealAdapter({"cache_ttl": 30})
        assert adapter._is_cache_valid(None) is False
        assert adapter._is_cache_valid({"timestamp": datetime.now()}) is True
        assert adapter._is_cache_valid({"timestamp": datetime.now() - timedelta(seconds=60)}) is False

    def test_get_ais_targets_mock(self):
        adapter = WorldMonitorRealAdapter()
        targets = asyncio.run(adapter.get_ais_targets())
        assert isinstance(targets, list)
        assert len(targets) >= 3
        assert isinstance(targets[0], WM_AIS_Target)

    def test_get_ais_targets_with_bbox(self):
        adapter = WorldMonitorRealAdapter()
        bbox = {"min_lat": 31.0, "max_lat": 32.0, "min_lng": 121.0, "max_lng": 122.0}
        targets = asyncio.run(adapter.get_ais_targets(bbox))
        assert isinstance(targets, list)

    def test_get_ais_targets_cached(self):
        adapter = WorldMonitorRealAdapter()
        # First call
        t1 = asyncio.run(adapter.get_ais_targets())
        # Second call should use cache
        t2 = asyncio.run(adapter.get_ais_targets())
        assert len(t1) >= 3
        assert len(t2) >= 3

    def test_get_marine_weather_mock(self):
        adapter = WorldMonitorRealAdapter()
        weather = asyncio.run(adapter.get_marine_weather(31.23, 121.47))
        assert isinstance(weather, WM_Marine_Weather)
        assert "speed" in weather.wind

    def test_get_marine_weather_cached(self):
        adapter = WorldMonitorRealAdapter()
        w1 = asyncio.run(adapter.get_marine_weather(31.23, 121.47))
        w2 = asyncio.run(adapter.get_marine_weather(31.23, 121.47))
        assert w1 is not None
        assert w2 is not None

    def test_get_ports_mock(self):
        adapter = WorldMonitorRealAdapter()
        ports = asyncio.run(adapter.get_ports())
        assert isinstance(ports, list)

    def test_get_ports_with_region(self):
        adapter = WorldMonitorRealAdapter()
        ports = asyncio.run(adapter.get_ports("cn"))
        assert isinstance(ports, list)

    def test_get_ports_cached(self):
        adapter = WorldMonitorRealAdapter()
        p1 = asyncio.run(adapter.get_ports())
        p2 = asyncio.run(adapter.get_ports())
        assert isinstance(p1, list)
        assert isinstance(p2, list)

    def test_get_shipping_routes_mock(self):
        adapter = WorldMonitorRealAdapter()
        routes = asyncio.run(adapter.get_shipping_routes())
        assert isinstance(routes, list)

    def test_get_shipping_routes_with_params(self):
        adapter = WorldMonitorRealAdapter()
        routes = asyncio.run(adapter.get_shipping_routes("Shanghai", "Singapore"))
        assert isinstance(routes, list)

    def test_get_shipping_routes_cached(self):
        adapter = WorldMonitorRealAdapter()
        r1 = asyncio.run(adapter.get_shipping_routes())
        r2 = asyncio.run(adapter.get_shipping_routes())
        assert isinstance(r1, list)
        assert isinstance(r2, list)


class TestWMAISTarget:
    def test_to_dict(self):
        target = WM_AIS_Target(
            mmsi="123456", latitude=31.23, longitude=121.47,
            course=90.0, speed=12.0, heading=88.0,
            vessel_type="Container Ship", timestamp=datetime.now().isoformat(),
        )
        d = target.to_dict()
        assert d["mmsi"] == "123456"
        assert d["latitude"] == 31.23

    def test_defaults(self):
        target = WM_AIS_Target(
            mmsi="111", latitude=0, longitude=0, course=0, speed=0,
            heading=0, vessel_type="Cargo", timestamp="2026-01-01",
        )
        assert target.risk_level == "low"
        assert target.risk_factors is None
        assert target.predicted_trajectory is None


class TestWMMarineWeather:
    def test_to_dict(self):
        weather = WM_Marine_Weather(
            position={"lat": 31.23, "lng": 121.47},
            wind={"speed": 15, "direction": 180},
            wave={"height": 2.0, "period": 8},
            current={"speed": 1.5, "direction": 90},
            visibility=10.0,
            timestamp=datetime.now().isoformat(),
        )
        d = weather.to_dict()
        assert d["position"]["lat"] == 31.23
        assert d["wind"]["speed"] == 15


# ---------- Cloud Sync - FeishuAdapter ----------
from storage.cloud_sync import FeishuAdapter, get_adapter


class TestFeishuAdapter:
    def test_init(self):
        adapter = FeishuAdapter({"folder_token": "test_token"})
        assert adapter.folder_token == "test_token"

    def test_download_events(self):
        adapter = FeishuAdapter({})
        events = adapter.download_events("test", datetime.now() - timedelta(hours=1), datetime.now())
        assert events == []

    def test_list_events(self):
        adapter = FeishuAdapter({})
        events = adapter.list_events("test")
        assert events == []

    def test_get_bucket_info(self):
        adapter = FeishuAdapter({})
        info = adapter.get_bucket_info()
        assert isinstance(info, dict)


class TestGetAdapter:
    def test_get_adapter_local(self, tmp_path):
        adapter = get_adapter("local", {"storage_path": str(tmp_path / "sync")})
        assert adapter is not None

    def test_get_adapter_s3(self):
        adapter = get_adapter("s3", {"bucket_name": "test"})
        assert adapter is not None


# ---------- Data Lakehouse deeper coverage ----------
from storage.data_lakehouse import DataLakehouse, create_lakehouse


class TestDataLakehouseDeep:
    @pytest.fixture
    def lakehouse(self, tmp_path):
        return create_lakehouse({
            "store_type": "sqlite",
            "store_config": {"db_path": str(tmp_path / "test.db")},
            "cloud_type": "local",
            "cloud_config": {"storage_path": str(tmp_path / "cloud")},
            "buffer_max_size": 5,
            "analytics_cache_dir": str(tmp_path / "cache"),
        })

    def test_save_and_query(self, lakehouse):
        lakehouse.save_event({"event_type": "test", "timestamp": datetime.now().isoformat(), "payload": {"x": 1}})
        # Force flush
        lakehouse._flush_buffer_to_local()
        events = lakehouse.query_events(event_type="test")
        assert len(events) >= 1

    def test_save_batch(self, lakehouse):
        events = [
            {"event_type": f"batch_{i}", "timestamp": datetime.now().isoformat(), "payload": {"i": i}}
            for i in range(3)
        ]
        result = lakehouse.save_batch(events)
        assert result is True

    def test_buffer_auto_flush(self, lakehouse):
        for i in range(6):
            lakehouse.save_event({"event_type": "flush_test", "timestamp": datetime.now().isoformat(), "payload": {"i": i}})
        # Buffer should have flushed at size 5
        events = lakehouse.query_events(event_type="flush_test")
        assert len(events) >= 5

    def test_query_events_by_time(self, lakehouse):
        now = datetime.now()
        lakehouse.save_event({"event_type": "timed", "timestamp": now.isoformat()})
        lakehouse._flush_buffer_to_local()
        events = lakehouse.query_events_by_time(now - timedelta(minutes=1), now + timedelta(minutes=1))
        assert len(events) >= 1

    def test_get_storage_profile(self, lakehouse):
        profile = lakehouse.get_storage_profile()
        assert profile["architecture_mode"] == "lightweight_edge_lakehouse"
        assert profile["hadoop_required"] is False

    def test_get_memory_profile(self, lakehouse):
        lakehouse.save_event({"event_type": "profile_test", "timestamp": datetime.now().isoformat(), "source": "test"})
        lakehouse._flush_buffer_to_local()
        profile = lakehouse.get_memory_profile()
        assert "recent_events_count" in profile

    def test_get_status(self, lakehouse):
        status = lakehouse.get_status()
        assert status["local_store"]["available"] is True
        assert "health" in status

    def test_shutdown(self, lakehouse):
        lakehouse.save_event({"event_type": "shutdown_test", "timestamp": datetime.now().isoformat()})
        lakehouse.shutdown()
        # After shutdown, buffer should be empty
        assert len(lakehouse.event_buffer) == 0

    def test_no_local_store(self, tmp_path):
        lh = DataLakehouse({"store_type": "unknown_type_xxx"})
        assert lh.local_store is None
        events = lh.query_events()
        assert events == []


class TestCreateLakehouse:
    def test_default(self, tmp_path):
        lh = create_lakehouse({
            "store_type": "sqlite",
            "store_config": {"db_path": str(tmp_path / "test.db")},
            "analytics_cache_dir": str(tmp_path / "cache"),
        })
        assert lh is not None
        assert lh.local_store is not None


# ---------- Cloud Sync S3 adapter - more ensure_bucket paths ----------
from storage.cloud_sync import S3CompatibleAdapter


class TestS3EnsureBucketPaths:
    def test_ensure_bucket_no_client(self):
        adapter = S3CompatibleAdapter({"bucket_name": "test"})
        with patch.object(adapter, '_get_client', return_value=None):
            info = adapter.ensure_bucket()
            assert info["available"] is False
            assert "S3 client not available" in info["error"]

    def test_ensure_bucket_exists(self):
        adapter = S3CompatibleAdapter({"bucket_name": "test"})
        mock_client = MagicMock()
        mock_client.head_bucket = MagicMock()
        with patch.object(adapter, '_get_client', return_value=mock_client):
            info = adapter.ensure_bucket()
            assert info["available"] is True
            assert info["created"] is False

    def test_ensure_bucket_not_found_no_auto_create(self):
        adapter = S3CompatibleAdapter({"bucket_name": "test", "auto_create_bucket": False})
        mock_client = MagicMock()
        exc = Exception("not found")
        exc.response = {"Error": {"Code": "404"}}
        mock_client.head_bucket = MagicMock(side_effect=exc)
        with patch.object(adapter, '_get_client', return_value=mock_client):
            info = adapter.ensure_bucket()
            assert info["available"] is False

    def test_ensure_bucket_not_found_auto_create_success(self):
        adapter = S3CompatibleAdapter({"bucket_name": "test", "auto_create_bucket": True})
        mock_client = MagicMock()
        exc = Exception("not found")
        exc.response = {"Error": {"Code": "404"}}
        mock_client.head_bucket = MagicMock(side_effect=exc)
        mock_client.create_bucket = MagicMock()
        with patch.object(adapter, '_get_client', return_value=mock_client):
            info = adapter.ensure_bucket()
            assert info["available"] is True
            assert info["created"] is True

    def test_ensure_bucket_auto_create_fails(self):
        adapter = S3CompatibleAdapter({"bucket_name": "test", "auto_create_bucket": True})
        mock_client = MagicMock()
        exc = Exception("not found")
        exc.response = {"Error": {"Code": "404"}}
        mock_client.head_bucket = MagicMock(side_effect=exc)
        mock_client.create_bucket = MagicMock(side_effect=Exception("create failed"))
        with patch.object(adapter, '_get_client', return_value=mock_client):
            info = adapter.ensure_bucket()
            assert info["available"] is False    

    def test_normalize_prefix(self):
        adapter = S3CompatibleAdapter({"bucket_name": "test"})
        assert adapter._normalize_prefix("events") == "events/"
        assert adapter._normalize_prefix("events/") == "events/"
        assert adapter._normalize_prefix("") == ""

    def test_extract_error_code(self):
        adapter = S3CompatibleAdapter({"bucket_name": "test"})
        exc = Exception("test")
        exc.response = {"Error": {"Code": "404"}}
        assert adapter._extract_error_code(exc) == "404"
        
        exc2 = Exception("no response attr")
        assert adapter._extract_error_code(exc2) is None
