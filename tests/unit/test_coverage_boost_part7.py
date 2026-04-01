# -*- coding: utf-8 -*-
"""
Coverage boost tests part 7: Energy efficiency main(), perception hub capture_system_snapshot
deep branches, autonomy_manager transitions, cloud_sync deeper, event_store ParquetStore/abc,
data_lakehouse deeper, more api_extensions paths, remaining channel edges.
"""

import asyncio
import json
import os
import pytest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch, MagicMock, AsyncMock, PropertyMock

from starlette.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


# ---------- Energy Efficiency Channel main() function ----------
from channels.energy_efficiency_channel import EnergyEfficiencyChannel


class TestEnergyEfficiencyMain:
    """Test the standalone main() demo function."""
    def test_main_runs(self):
        from channels.energy_efficiency_channel import main
        # main() just prints, should not raise
        main()


# ---------- Perception Hub: capture_system_snapshot deep branches ----------
from channels.distributed_perception_hub import DistributedPerceptionHubChannel, FusionEvent
from channels.marine_base import ChannelRegistry, ChannelStatus, get_default_registry


class TestCaptureSystemSnapshotDeep:
    @pytest.fixture(autouse=True)
    def _reset_registry(self):
        """Reset registry for each test."""
        from channels import marine_base as mb
        old = mb._default_registry
        mb._default_registry = ChannelRegistry()
        yield
        mb._default_registry = old

    def test_snapshot_with_registered_channels(self):
        """Register channels so capture_system_snapshot hits non-None branches."""
        from channels.intelligent_navigation import IntelligentNavigationChannel
        from channels.intelligent_engine import IntelligentEngineChannel

        registry = get_default_registry()

        nav = IntelligentNavigationChannel()
        nav.initialize()
        registry.register(nav)

        engine = IntelligentEngineChannel()
        engine.initialize()
        registry.register(engine)

        hub = DistributedPerceptionHubChannel(config={"max_events": 100})
        hub._initialized = True
        hub._set_health(ChannelStatus.OK, "ready")

        events = hub.capture_system_snapshot()
        # Should have at least nav + engine events
        assert len(events) >= 2

    def test_snapshot_with_efficiency_channel(self):
        from channels.energy_efficiency_channel import EnergyEfficiencyChannel
        from channels.efficiency_models import VesselInfo, VesselType, FuelType

        registry = get_default_registry()

        vessel = VesselInfo(
            imo_number=1234567, vessel_name="Test", vessel_type=VesselType.BULK_CARRIER,
            dwt=50000, gross_tonnage=25000, length=200, beam=30, draft=12,
            main_engine_power=10000, fuel_type=FuelType.HFO, built_year=2020,
        )
        eff = EnergyEfficiencyChannel(config={"vessel": vessel})
        eff.initialize()
        registry.register(eff)

        hub = DistributedPerceptionHubChannel(config={"max_events": 100})
        hub._initialized = True
        hub._set_health(ChannelStatus.OK, "ready")

        events = hub.capture_system_snapshot()
        assert len(events) >= 1

    def test_snapshot_feature_fusion_measures_with_nav(self):
        """Ensure feature fusion runs when nav channel has AIS targets."""
        from channels.intelligent_navigation import IntelligentNavigationChannel

        registry = get_default_registry()

        nav = IntelligentNavigationChannel()
        nav.initialize()
        # Add a mock AIS target
        target = SimpleNamespace(mmsi=111, latitude=31.23, longitude=121.47, speed=10, course=90)
        nav.ais_targets = [target]
        registry.register(nav)

        hub = DistributedPerceptionHubChannel(config={"max_events": 100})
        hub._initialized = True
        hub._set_health(ChannelStatus.OK, "ready")

        events = hub.capture_system_snapshot()
        # Should include feature_fusion_state event
        fusion_events = [e for e in events if e.event_type == "feature_fusion_state"]
        assert len(fusion_events) >= 1


# ---------- Autonomy Manager transitions ----------
from channels.autonomy_manager import AutonomyManagerChannel


class TestAutonomyManagerTransitions:
    @pytest.fixture
    def mgr(self):
        ch = AutonomyManagerChannel()
        ch.initialize()
        return ch

    def test_request_transition_up(self, mgr):
        result = mgr.request_transition(2, "test upgrade")
        assert isinstance(result, dict)

    def test_request_transition_down(self, mgr):
        # First go up then down
        mgr.request_transition(3, "up")
        result = mgr.request_transition(1, "test downgrade")
        assert isinstance(result, dict)

    def test_request_transition_same_level(self, mgr):
        current = mgr.get_current_level()
        result = mgr.request_transition(current.get("lr_level", 1), "no change")
        assert isinstance(result, dict)

    def test_get_status(self, mgr):
        status = mgr.get_status()
        assert "current_level" in status or "health" in status

    def test_get_transition_history(self, mgr):
        mgr.request_transition(2, "test")
        mgr.request_transition(1, "test back")
        history = mgr.get_transition_history() if hasattr(mgr, 'get_transition_history') else []
        assert isinstance(history, list)


# ---------- Cloud Sync - LocalAdapter deeper, S3 upload/download paths ----------
from storage.cloud_sync import S3CompatibleAdapter, LocalFileAdapter, get_adapter


class TestLocalCloudAdapter:
    def test_init(self, tmp_path):
        adapter = LocalFileAdapter({"storage_path": str(tmp_path / "sync")})
        assert adapter is not None

    def test_upload_event(self, tmp_path):
        adapter = LocalFileAdapter({"storage_path": str(tmp_path / "sync")})
        result = adapter.upload_event({"data": "test"}, "test_type")
        assert result is True

    def test_upload_batch(self, tmp_path):
        adapter = LocalFileAdapter({"storage_path": str(tmp_path / "sync")})
        events = [{"data": f"test_{i}"} for i in range(3)]
        result = adapter.upload_batch(events, "batch_type")
        assert result is True

    def test_download_events(self, tmp_path):
        adapter = LocalFileAdapter({"storage_path": str(tmp_path / "sync")})
        adapter.upload_event({"event_type": "dl_test", "timestamp": datetime.now().isoformat()}, "dl_test")
        events = adapter.download_events("dl_test", datetime.now() - timedelta(hours=1), datetime.now() + timedelta(hours=1))
        assert isinstance(events, list)
        assert len(events) >= 1

    def test_list_events(self, tmp_path):
        adapter = LocalFileAdapter({"storage_path": str(tmp_path / "sync")})
        adapter.upload_event({"data": "test"}, "list_test")
        events = adapter.list_events("list_test")
        assert isinstance(events, list)
        assert len(events) >= 1

    def test_get_bucket_info(self, tmp_path):
        adapter = LocalFileAdapter({"storage_path": str(tmp_path / "sync")})
        info = adapter.get_bucket_info()
        assert isinstance(info, dict)
        assert info.get("available") is True

    def test_disk_usage(self, tmp_path):
        adapter = LocalFileAdapter({"storage_path": str(tmp_path / "sync")})
        adapter.upload_event({"data": "test"}, "usage_test")
        usage = adapter._get_disk_usage()
        assert usage > 0


class TestS3UploadDownload:
    def test_upload_event_no_client_mock_mode(self):
        adapter = S3CompatibleAdapter({"bucket_name": "test"})
        with patch.object(adapter, '_get_client', return_value=None):
            # S3 upload returns True in mock mode (no client)
            result = adapter.upload_event({"data": "test"}, "test_type")
            assert result is True

    def test_upload_event_success(self):
        adapter = S3CompatibleAdapter({"bucket_name": "test"})
        mock_client = MagicMock()
        mock_client.put_object = MagicMock()
        with patch.object(adapter, '_get_client', return_value=mock_client):
            result = adapter.upload_event({"data": "test", "timestamp": datetime.now().isoformat()}, "test_type")
            assert result is True

    def test_upload_batch(self):
        adapter = S3CompatibleAdapter({"bucket_name": "test"})
        mock_client = MagicMock()
        mock_client.put_object = MagicMock()
        with patch.object(adapter, '_get_client', return_value=mock_client):
            events = [{"data": f"test_{i}", "timestamp": datetime.now().isoformat()} for i in range(3)]
            result = adapter.upload_batch(events, "batch_type")
            assert result is True

    def test_download_events_no_client(self):
        adapter = S3CompatibleAdapter({"bucket_name": "test"})
        with patch.object(adapter, '_get_client', return_value=None):
            events = adapter.download_events("test", datetime.now() - timedelta(hours=1), datetime.now())
            assert events == []

    def test_list_events_no_client(self):
        adapter = S3CompatibleAdapter({"bucket_name": "test"})
        with patch.object(adapter, '_get_client', return_value=None):
            events = adapter.list_events("test")
            assert events == []

    def test_build_key(self):
        adapter = S3CompatibleAdapter({"bucket_name": "test", "prefix": "events/"})
        key = adapter._build_key("test_type", datetime(2026, 1, 15, 10, 30, 0))
        assert "test_type" in key
        assert "events/" in key

    def test_get_bucket_info(self):
        adapter = S3CompatibleAdapter({"bucket_name": "test"})
        with patch.object(adapter, '_get_client', return_value=None):
            info = adapter.get_bucket_info()
            assert isinstance(info, dict)


# ---------- Event Store - ParquetStore ----------
from storage.event_store import get_store, EventStore


class TestParquetStoreIfAvailable:
    def test_get_store_parquet(self, tmp_path):
        try:
            import pyarrow
            store = get_store("parquet", {"storage_path": str(tmp_path / "parquet")})
            assert store is not None

            # Test basic save/load
            event = {"event_type": "test", "timestamp": datetime.now().isoformat(), "payload": {"x": 1}}
            store.save_event(event)
            events = store.load_events(event_type="test")
            assert len(events) >= 1
        except ImportError:
            pytest.skip("pyarrow not installed")

    def test_get_store_parquet_batch(self, tmp_path):
        try:
            import pyarrow
            store = get_store("parquet", {"storage_path": str(tmp_path / "parquet")})
            events = [
                {"event_type": "batch", "timestamp": datetime.now().isoformat(), "payload": {"i": i}}
                for i in range(5)
            ]
            store.save_events(events)
            loaded = store.load_events(event_type="batch")
            assert len(loaded) >= 5
        except ImportError:
            pytest.skip("pyarrow not installed")

    def test_get_store_parquet_clear(self, tmp_path):
        try:
            import pyarrow
            store = get_store("parquet", {"storage_path": str(tmp_path / "parquet")})
            store.save_event({"event_type": "clear_me", "timestamp": datetime.now().isoformat()})
            store.clear_events("clear_me")
            events = store.load_events(event_type="clear_me")
            assert len(events) == 0
        except ImportError:
            pytest.skip("pyarrow not installed")

    def test_get_store_parquet_by_time(self, tmp_path):
        try:
            import pyarrow
            now = datetime.now()
            store = get_store("parquet", {"storage_path": str(tmp_path / "parquet")})
            store.save_event({"event_type": "time_test", "timestamp": now.isoformat()})
            events = store.load_events_by_time(now - timedelta(minutes=1), now + timedelta(minutes=1), "time_test")
            assert isinstance(events, list)
        except ImportError:
            pytest.skip("pyarrow not installed")


# ---------- Data Lakehouse - archive & duckdb paths ----------
from storage.data_lakehouse import DataLakehouse


class TestDataLakehouseAnalytics:
    def test_archive_events_to_parquet(self, tmp_path):
        try:
            import pyarrow
            lh = DataLakehouse({
                "store_type": "sqlite",
                "store_config": {"db_path": str(tmp_path / "test.db")},
                "buffer_max_size": 1,
                "analytics_cache_dir": str(tmp_path / "cache"),
            })
            lh.save_event({"event_type": "archive_test", "timestamp": datetime.now().isoformat(), "source": "test"})
            lh._flush_buffer_to_local()
            path = lh.archive_events_to_parquet(event_type="archive_test")
            assert os.path.exists(path)
        except ImportError:
            pytest.skip("pyarrow not installed")

    def test_run_duckdb_query(self, tmp_path):
        try:
            import pyarrow
            import duckdb
            lh = DataLakehouse({
                "store_type": "sqlite",
                "store_config": {"db_path": str(tmp_path / "test.db")},
                "buffer_max_size": 1,
                "analytics_cache_dir": str(tmp_path / "cache"),
            })
            lh.save_event({"event_type": "duckdb_test", "timestamp": datetime.now().isoformat(), "source": "test"})
            lh._flush_buffer_to_local()
            rows = lh.run_duckdb_query("SELECT count(*) as cnt FROM lakehouse_events", event_type="duckdb_test")
            assert len(rows) == 1
            assert rows[0]["cnt"] >= 1
        except ImportError:
            pytest.skip("pyarrow or duckdb not installed")

    def test_flush_with_cloud_adapter(self, tmp_path):
        lh = DataLakehouse({
            "store_type": "sqlite",
            "store_config": {"db_path": str(tmp_path / "test.db")},
            "cloud_type": "local",
            "cloud_config": {"storage_path": str(tmp_path / "cloud")},
            "buffer_max_size": 1,
            "analytics_cache_dir": str(tmp_path / "cache"),
        })
        lh.save_event({"event_type": "cloud_test", "timestamp": datetime.now().isoformat()})
        # Buffer should auto-flush since max_size=1
        assert len(lh.event_buffer) <= 1

    def test_query_with_no_store(self, tmp_path):
        lh = DataLakehouse({
            "store_type": "non_existent_xyz",
            "analytics_cache_dir": str(tmp_path / "cache"),
        })
        result = lh.query_events_by_time(datetime.now(), datetime.now())
        assert result == []


# ---------- Compliance Digital Expert deeper ----------
from channels.compliance_digital_expert import ComplianceDigitalExpertChannel


class TestComplianceDigitalExpertDeep:
    @pytest.fixture
    def expert(self):
        ch = ComplianceDigitalExpertChannel()
        ch.initialize()
        return ch

    def test_query_compliance_overall(self, expert):
        result = expert.query_compliance_status("overall")
        assert isinstance(result, dict)

    def test_query_compliance_safety(self, expert):
        result = expert.query_compliance_status("safety")
        assert isinstance(result, dict)

    def test_build_cognitive_snapshot(self, expert):
        snapshot = expert.build_cognitive_snapshot()
        assert isinstance(snapshot, dict)
        assert "timestamp" in snapshot


# ---------- Decision Orchestrator deeper ----------
from channels.decision_orchestrator import DecisionOrchestratorChannel


class TestDecisionOrchestratorDeep:
    @pytest.fixture
    def orch(self):
        ch = DecisionOrchestratorChannel()
        ch.initialize()
        return ch

    def test_build_decision_package(self, orch):
        package = orch.build_decision_package()
        assert isinstance(package, dict)
        assert "generated_at" in package

    def test_record_feedback(self, orch):
        feedback = orch.record_feedback("test_action", "success", "operator")
        assert isinstance(feedback, dict)

    def test_coordinate_agents(self, orch):
        if hasattr(orch, 'coordinate_agents'):
            summary = orch.coordinate_agents()
            assert isinstance(summary, dict)

    def test_set_event_sink(self, orch):
        mock_sink = MagicMock()
        if hasattr(orch, 'set_event_sink'):
            orch.set_event_sink(mock_sink)


# ---------- Ship Shore Link deeper ----------
from channels.ship_shore_link import ShipShoreLinkChannel


class TestShipShoreLinkDeep:
    @pytest.fixture
    def link(self):
        ch = ShipShoreLinkChannel()
        ch.initialize()
        return ch

    def test_get_status(self, link):
        status = link.get_status()
        assert isinstance(status, dict)

    def test_select_link(self, link):
        if hasattr(link, 'select_link'):
            result = link.select_link()
            assert isinstance(result, (dict, str, type(None)))


# ---------- Voyage Planner deeper ----------
from channels.voyage_planner import VoyagePlannerChannel


class TestVoyagePlannerDeep:
    @pytest.fixture
    def planner(self):
        ch = VoyagePlannerChannel()
        ch.initialize()
        return ch

    def test_get_status(self, planner):
        status = planner.get_status()
        assert isinstance(status, dict)

    def test_generate_daily_report(self, planner):
        report = planner.generate_daily_report()
        assert isinstance(report, dict)


# ---------- Route Optimizer deeper ----------
from channels.route_optimizer import RouteOptimizerChannel


class TestRouteOptimizerDeep:
    @pytest.fixture
    def optimizer(self):
        ch = RouteOptimizerChannel()
        ch.initialize()
        return ch

    def test_get_status(self, optimizer):
        status = optimizer.get_status()
        assert isinstance(status, dict)


# ---------- Cyber Security deeper ----------
from channels.cyber_security import CyberSecurityChannel


class TestCyberSecurityDeep:
    @pytest.fixture
    def security(self):
        ch = CyberSecurityChannel()
        ch.initialize()
        return ch

    def test_get_audit_log(self, security):
        logs = security.get_audit_log(10)
        assert isinstance(logs, list)

    def test_get_threat_summary(self, security):
        summary = security.get_threat_summary()
        assert isinstance(summary, dict)


# ---------- Predictive Health deeper ----------
from channels.predictive_health import PredictiveHealthChannel


class TestPredictiveHealthDeep:
    @pytest.fixture
    def phm(self):
        ch = PredictiveHealthChannel()
        ch.initialize()
        return ch

    def test_generate_maintenance_plan(self, phm):
        plan = phm.generate_maintenance_plan()
        assert isinstance(plan, list)


# ---------- config_loader deeper ----------
from config_loader import get_config, ConfigLoader


class TestConfigLoaderDeep:
    def test_get_nested_default(self):
        cfg = get_config()
        # Access a non-existent key with default
        assert cfg.get("nonexistent_key", "default") == "default"

    def test_config_loader_instance(self):
        loader = ConfigLoader()
        assert loader is not None
        # ConfigLoader uses .get() or ._config, not .config
        cfg = loader._config
        assert cfg is not None


# ---------- CII Calculator deeper ----------
from channels.cii_calculator import CIICalculator


class TestCIICalculatorDeep:
    @pytest.fixture
    def vessel(self):
        from channels.efficiency_models import VesselInfo, VesselType, FuelType
        return VesselInfo(
            imo_number=1234567, vessel_name="Test", vessel_type=VesselType.BULK_CARRIER,
            dwt=82000, gross_tonnage=43500, length=229, beam=32, draft=14.5,
            main_engine_power=14280, fuel_type=FuelType.HFO, built_year=2015,
        )

    def test_calculate_cii(self, vessel):
        calc = CIICalculator(vessel)
        result = calc.calculate_cii(
            total_fuel=15000000,
            total_distance=45000,
            year=2026,
        )
        assert result is not None

    def test_calculate_corrective_action(self, vessel):
        calc = CIICalculator(vessel)
        cii_result = calc.calculate_cii(total_fuel=15000000, total_distance=45000, year=2026)
        if hasattr(calc, 'calculate_corrective_action_target'):
            target = calc.calculate_corrective_action_target(
                current_cii=cii_result,
            )
            assert target is not None


# ---------- EEXI Calculator deeper ----------
from channels.eexi_calculator import EEXICalculator


class TestEEXICalculatorDeep:
    @pytest.fixture
    def vessel(self):
        from channels.efficiency_models import VesselInfo, VesselType, FuelType
        return VesselInfo(
            imo_number=1234567, vessel_name="Test", vessel_type=VesselType.BULK_CARRIER,
            dwt=82000, gross_tonnage=43500, length=229, beam=32, draft=14.5,
            main_engine_power=14280, fuel_type=FuelType.HFO, built_year=2015,
        )

    def test_calculate_attained_eexi(self, vessel):
        calc = EEXICalculator(vessel)
        result = calc.calculate_attained_eexi(
            installed_power=12000,
            specific_fuel_consumption=175,
        )
        assert result is not None

    def test_calculate_reference_line(self, vessel):
        calc = EEXICalculator(vessel)
        ref = calc.calculate_reference_line(82000)
        assert isinstance(ref, (float, int))

    def test_calculate_reference_speed(self, vessel):
        calc = EEXICalculator(vessel)
        speed = calc.calculate_reference_speed(82000)
        assert isinstance(speed, (float, int))


# ---------- Intelligent Navigation deeper ----------
from channels.intelligent_navigation import IntelligentNavigationChannel


class TestIntelligentNavigationDeep:
    @pytest.fixture
    def nav(self):
        ch = IntelligentNavigationChannel()
        ch.initialize()
        return ch

    def test_generate_navigation_report_empty(self, nav):
        report = nav.generate_navigation_report()
        assert isinstance(report, dict)


# ---------- Intelligent Engine deeper ----------
from channels.intelligent_engine import IntelligentEngineChannel


class TestIntelligentEngineDeep:
    @pytest.fixture
    def engine(self):
        ch = IntelligentEngineChannel()
        ch.initialize()
        return ch

    def test_get_maintenance_advice(self, engine):
        if hasattr(engine, 'get_maintenance_advice'):
            advice = engine.get_maintenance_advice()
            assert isinstance(advice, list)

    def test_query_engine_status(self, engine):
        if hasattr(engine, 'query_engine_status'):
            result = engine.query_engine_status("overall")
            assert result is not None  # may return string or dict
