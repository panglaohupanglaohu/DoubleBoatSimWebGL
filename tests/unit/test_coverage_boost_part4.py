# -*- coding: utf-8 -*-
"""
Coverage boost tests part 4: Register Channels, WorldMonitor Adapter,
Main.py endpoints, more perception hub fusion, more event_store/cloud_sync paths.
"""

import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


# ---------- Register Channels (all register_* functions) ----------
import channels.marine_base as mb
from channels.marine_base import ChannelRegistry
from register_channels import (
    register_intelligent_engine,
    register_compliance_digital_expert,
    register_distributed_perception_hub,
    register_decision_orchestrator,
    register_rcs_control,
    register_structural_health_monitor,
    register_ship_shore_link,
    register_autonomy_manager,
    register_predictive_health,
    register_route_optimizer,
    register_voyage_planner,
    register_cyber_security,
    register_deterministic_network,
    register_nats_event_bus,
    register_colregs_brain,
    register_wpc_attitude_control,
    register_openbridge_hmi,
    list_registered_channels,
)


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset the default registry before each test to avoid conflicts."""
    mb._default_registry = ChannelRegistry()
    yield
    mb._default_registry = ChannelRegistry()


class TestRegisterAllChannels:
    def test_register_intelligent_engine(self):
        ch = register_intelligent_engine()
        assert ch is not None
        assert ch.name == "intelligent_engine"

    def test_register_compliance_digital_expert(self):
        ch = register_compliance_digital_expert()
        assert ch is not None
        assert ch.name == "compliance_digital_expert"

    def test_register_distributed_perception_hub(self):
        ch = register_distributed_perception_hub()
        assert ch is not None
        assert ch.name == "distributed_perception_hub"

    def test_register_decision_orchestrator(self):
        ch = register_decision_orchestrator()
        assert ch is not None
        assert ch.name == "decision_orchestrator"

    def test_register_rcs_control(self):
        ch = register_rcs_control()
        assert ch is not None
        assert ch.name == "rcs_control"

    def test_register_structural_health_monitor(self):
        ch = register_structural_health_monitor()
        assert ch is not None
        assert ch.name == "structural_health_monitor"

    def test_register_ship_shore_link(self):
        ch = register_ship_shore_link()
        assert ch is not None
        assert ch.name == "ship_shore_link"

    def test_register_autonomy_manager(self):
        ch = register_autonomy_manager()
        assert ch is not None
        assert ch.name == "autonomy_manager"

    def test_register_predictive_health(self):
        ch = register_predictive_health()
        assert ch is not None
        assert ch.name == "predictive_health"

    def test_register_route_optimizer(self):
        ch = register_route_optimizer()
        assert ch is not None
        assert ch.name == "route_optimizer"

    def test_register_voyage_planner(self):
        ch = register_voyage_planner()
        assert ch is not None
        assert ch.name == "voyage_planner"

    def test_register_cyber_security(self):
        ch = register_cyber_security()
        assert ch is not None
        assert ch.name == "cyber_security"

    def test_register_deterministic_network(self):
        ch = register_deterministic_network()
        assert ch is not None
        assert ch.name == "deterministic_network"

    def test_register_nats_event_bus(self):
        ch = register_nats_event_bus()
        assert ch is not None
        assert ch.name == "nats_event_bus"

    def test_register_colregs_brain(self):
        ch = register_colregs_brain()
        assert ch is not None
        assert ch.name == "colregs_brain"

    def test_register_wpc_attitude_control(self):
        ch = register_wpc_attitude_control()
        assert ch is not None
        assert ch.name == "wpc_attitude_control"

    def test_register_openbridge_hmi(self):
        ch = register_openbridge_hmi()
        assert ch is not None
        assert ch.name == "openbridge_hmi"

    def test_list_registered_channels(self):
        register_cyber_security()
        register_rcs_control()
        list_registered_channels()  # Should not raise


# ---------- WorldMonitor Adapter ----------
from adapters.worldmonitor_adapter_real import WM_AIS_Target, WM_Marine_Weather


class TestWorldMonitorDataClasses:
    def test_ais_target(self):
        t = WM_AIS_Target(
            mmsi="123456789",
            latitude=31.23, longitude=121.47,
            course=180, speed=12.5, heading=178,
            vessel_type="Cargo", timestamp="2026-03-24T12:00:00",
        )
        d = t.to_dict()
        assert d["mmsi"] == "123456789"
        assert d["latitude"] == 31.23
        assert d["risk_level"] == "low"

    def test_ais_target_with_risk(self):
        t = WM_AIS_Target(
            mmsi="999", latitude=31.0, longitude=121.0,
            course=0, speed=0, heading=0,
            vessel_type="Tanker", timestamp="2026-01-01T00:00:00",
            risk_level="high",
            risk_factors=["close_range", "high_speed"],
        )
        d = t.to_dict()
        assert d["risk_level"] == "high"
        assert d["risk_factors"] == ["close_range", "high_speed"]

    def test_marine_weather(self):
        w = WM_Marine_Weather(
            position={"lat": 31.23, "lng": 121.47},
            wind={"speed": 25, "direction": 180, "gust": 35},
            wave={"height": 3.5, "period": 8, "direction": 200},
            current={"speed": 2.0, "direction": 90},
            visibility=5.0,
            timestamp="2026-03-24T12:00:00",
        )
        assert w.visibility == 5.0
        assert w.wind["speed"] == 25


# ---------- Perception Hub - Fusion Functions ----------
from channels.distributed_perception_hub import DistributedPerceptionHubChannel


class TestPerceptionFusion:
    @pytest.fixture
    def hub(self):
        ch = DistributedPerceptionHubChannel()
        ch.initialize()
        return ch

    def test_fuse_ais_close_range(self, hub):
        ais = {"latitude": 31.23, "longitude": 121.47, "mmsi": 111}
        nav = {"own_ship": {"latitude": 31.2301, "longitude": 121.4701}}
        result = hub.fuse_ais_with_navigation(ais, nav)
        assert result is not None
        assert result.confidence > 0.7
        if result.risk_correlation:
            assert "collision_risk" in result.risk_correlation

    def test_fuse_ais_medium_range(self, hub):
        ais = {"latitude": 31.245, "longitude": 121.47}
        nav = {"own_ship": {"latitude": 31.23, "longitude": 121.47}}
        result = hub.fuse_ais_with_navigation(ais, nav)
        assert result is not None

    def test_fuse_weather_with_efficiency(self, hub):
        weather = {
            "wind_speed_kts": 25.0,
            "wave_height_m": 3.5,
            "current_speed_kts": 2.0,
            "wind_direction": 180,
        }
        efficiency = {
            "fuel_rate_kg_h": 1200,
            "speed_kts": 12,
            "eexi": 5.5,
            "cii_rating": "C",
        }
        result = hub.fuse_weather_with_efficiency(weather, efficiency)
        # May return None if validation fails or returns FusionEvent
        assert result is None or result.event_type is not None


# ---------- Event Store - JSONL extended edge cases ----------
from storage.event_store import JSONLStore


class TestJSONLStoreEdgeCases:
    @pytest.fixture
    def store(self, tmp_path):
        return JSONLStore({"storage_path": str(tmp_path / "events")})

    def test_save_event_unknown_type(self, store):
        event = {"timestamp": datetime.now().isoformat(), "data": "no type"}
        result = store.save_event(event)
        assert result is True

    def test_load_events_with_limit(self, store):
        for i in range(10):
            store.save_event({"event_type": "lim", "timestamp": datetime.now().isoformat(), "i": i})
        events = store.load_events(event_type="lim", limit=3)
        assert len(events) == 3

    def test_clear_nonexistent_type(self, store):
        result = store.clear_events(event_type="nonexistent")
        assert result is True  # No file to delete


# ---------- Cloud Sync - S3 adapter key/prefix tests ----------
from storage.cloud_sync import S3CompatibleAdapter


class TestS3AdapterPaths:
    def test_build_key_different_types(self):
        adapter = S3CompatibleAdapter({"prefix": "data/"})
        for etype in ["navigation", "engine", "weather"]:
            key = adapter._build_key(etype, datetime(2026, 6, 15, 10, 30))
            assert etype in key

    def test_build_key_empty_type(self):
        adapter = S3CompatibleAdapter({"prefix": "data/"})
        key = adapter._build_key("", datetime(2026, 1, 1))
        assert "unknown" in key

    def test_build_event_prefix_unknown(self):
        adapter = S3CompatibleAdapter({"prefix": "events/"})
        prefix = adapter._build_event_prefix("")
        assert "unknown" in prefix

    def test_event_with_string_last_modified(self):
        adapter = S3CompatibleAdapter({})
        event = {"data": "test"}
        enriched = adapter._event_with_metadata(event, "key", "2026-01-01T00:00:00")
        assert enriched["cloud_last_modified"] == "2026-01-01T00:00:00"

    def test_extract_event_timestamp_uploaded_at(self):
        adapter = S3CompatibleAdapter({})
        event = {"uploaded_at": "2026-03-24T12:00:00"}
        result = adapter._extract_event_timestamp(event)
        assert result is not None

    def test_extract_event_timestamp_bad_format(self):
        adapter = S3CompatibleAdapter({})
        event = {"timestamp": "not-a-date"}
        result = adapter._extract_event_timestamp(event)
        assert result is None

    def test_extract_event_timestamp_with_fallback(self):
        adapter = S3CompatibleAdapter({})
        fallback = datetime(2026, 1, 1)
        result = adapter._extract_event_timestamp({}, fallback)
        assert result is not None

    def test_serialize_preserves_existing_fields(self):
        adapter = S3CompatibleAdapter({})
        data = {"event_type": "custom", "uploaded_at": "2026-01-01"}
        result = adapter._serialize_event(data, "test")
        parsed = json.loads(result.decode("utf-8"))
        assert parsed["event_type"] == "custom"  # Not overwritten
        assert parsed["uploaded_at"] == "2026-01-01"


# ---------- Config Loader advanced ----------
from config_loader import ConfigLoader, get_config, get_backend_url


class TestConfigLoaderAdvanced:
    def test_get_config_function(self):
        cl = get_config()
        assert isinstance(cl, ConfigLoader)

    def test_get_backend_url_function(self):
        url = get_backend_url()
        assert isinstance(url, str)

    def test_load_and_get(self):
        cl = ConfigLoader()
        val = cl.get("nonexistent.deeply.nested", "default")
        assert val == "default"
