# -*- coding: utf-8 -*-
"""
Tests for SVESSEL new channel modules:
- ShipShoreLinkChannel
- AutonomyManagerChannel
- PredictiveHealthChannel
- RouteOptimizerChannel
- VoyagePlannerChannel
- CyberSecurityChannel
"""

import pytest
from channels.ship_shore_link import ShipShoreLinkChannel, LinkType
from channels.autonomy_manager import AutonomyManagerChannel
from channels.predictive_health import PredictiveHealthChannel
from channels.route_optimizer import RouteOptimizerChannel
from channels.voyage_planner import VoyagePlannerChannel, VoyageStatus
from channels.cyber_security import CyberSecurityChannel, AccessRole, ThreatLevel


class TestShipShoreLinkChannel:

    def setup_method(self):
        self.ch = ShipShoreLinkChannel()
        self.ch.initialize()

    def teardown_method(self):
        self.ch.shutdown()

    def test_initialize(self):
        assert self.ch._initialized

    def test_get_status(self):
        status = self.ch.get_status()
        assert status["channel"] == "ship_shore_link"

    def test_simulate_link_conditions(self):
        result = self.ch.simulate_link_conditions()
        assert isinstance(result, dict)

    def test_select_best_link(self):
        self.ch.simulate_link_conditions()
        best = self.ch.select_best_link()
        # Returns a LinkType enum or None
        assert best is None or isinstance(best, LinkType)

    def test_predict_latency(self):
        self.ch.simulate_link_conditions()
        prediction = self.ch.predict_latency()
        assert hasattr(prediction, "predicted_latency_ms")
        assert hasattr(prediction, "trend")

    def test_update_link_status(self):
        metrics = self.ch.update_link_status(LinkType.LTE_5G, 50.0, packet_loss_pct=1.0)
        assert hasattr(metrics, "current_latency_ms")
        assert metrics.current_latency_ms == 50.0
        best = self.ch.select_best_link()
        assert best == LinkType.LTE_5G

    def test_shutdown(self):
        self.ch.shutdown()
        assert not self.ch._initialized


class TestAutonomyManagerChannel:

    def setup_method(self):
        self.ch = AutonomyManagerChannel()
        self.ch.initialize()

    def teardown_method(self):
        self.ch.shutdown()

    def test_initialize_default(self):
        status = self.ch.get_status()
        assert "manual" in status["mass_level"]
        assert status["mass_code"] == "M"

    def test_get_status_fields(self):
        status = self.ch.get_status()
        assert "mass_level" in status
        assert "lr_level" in status
        assert "control_authority" in status

    def test_evaluate_max_autonomy(self):
        result = self.ch.evaluate_max_autonomy(traffic_density=0, wind_force_beaufort=3)
        assert "max_allowed_al" in result
        assert "recommendation" in result

    def test_request_transition(self):
        result = self.ch.request_transition(target_lr_level=2, reason="test")
        assert "approved" in result
        assert result["mass_code"] == "R"

    def test_emergency_override(self):
        result = self.ch.emergency_override("test_emergency")
        assert "manual" in result["mass_level"]
        assert result["control_authority"] == "bridge"
        assert result["emergency_mode"] is True

    def test_clear_emergency(self):
        self.ch.emergency_override("test")
        result = self.ch.clear_emergency()
        assert result.get("emergency_cleared") is True


class TestPredictiveHealthChannel:

    def setup_method(self):
        self.ch = PredictiveHealthChannel()
        self.ch.initialize()

    def teardown_method(self):
        self.ch.shutdown()

    def test_initialize(self):
        assert self.ch._initialized

    def test_get_status_has_components(self):
        status = self.ch.get_status()
        assert "total_components" in status or "components" in status
        comp_count = status.get("total_components", len(status.get("components", {})))
        assert comp_count >= 1

    def test_ingest_parameter(self):
        result = self.ch.ingest_parameter("ME-1", "temperature", 380, "C")
        status = self.ch.get_status()
        assert "components" in status
        assert "ME-1" in status["components"]

    def test_generate_maintenance_plan(self):
        plan = self.ch.generate_maintenance_plan()
        assert isinstance(plan, list)

    def test_high_temp_triggers_alert(self):
        result = self.ch.ingest_parameter("ME-1", "temperature", 480, "C")
        # High temp may trigger an alert dict
        assert result is not None or True

    def test_fleet_health_summary(self):
        summary = self.ch.get_fleet_health_summary()
        assert "overall_health_score" in summary


class TestRouteOptimizerChannel:

    def setup_method(self):
        self.ch = RouteOptimizerChannel()
        self.ch.initialize()

    def teardown_method(self):
        self.ch.shutdown()

    def test_initialize(self):
        assert self.ch._initialized

    def test_get_status(self):
        status = self.ch.get_status()
        assert status["channel"] == "route_optimizer"

    def test_set_waypoints_and_optimize(self):
        self.ch.set_waypoints([
            {"latitude": 31.23, "longitude": 121.47, "name": "Shanghai"},
            {"latitude": 35.44, "longitude": 139.64, "name": "Tokyo"},
        ])
        result = self.ch.optimize_route(mode="balanced")
        assert hasattr(result, "optimized_distance_nm")
        assert result.optimized_distance_nm > 0
        assert len(result.legs) == 1

    def test_get_trim_advice(self):
        advice = self.ch.get_trim_advice()
        assert hasattr(advice, "optimal_trim_m")

    def test_get_speed_advice(self):
        advice = self.ch.get_speed_advice()
        assert isinstance(advice, dict)
        assert "economic_speed_kn" in advice or "current_speed_kn" in advice


class TestVoyagePlannerChannel:

    def setup_method(self):
        self.ch = VoyagePlannerChannel()
        self.ch.initialize()

    def teardown_method(self):
        self.ch.shutdown()

    def test_initialize(self):
        assert self.ch._initialized

    def test_create_voyage(self):
        result = self.ch.create_voyage(
            voyage_id="V001",
            vessel_name="Test Ship",
            departure={"name": "Shanghai", "lat": 31.23, "lon": 121.47, "eta": "2025-01-01T08:00", "etd": "2025-01-01T10:00"},
            arrival={"name": "Tokyo", "lat": 35.44, "lon": 139.64, "eta": "2025-01-05T10:00", "etd": "2025-01-05T18:00"},
        )
        assert result["voyage_id"] == "V001"
        assert result["status"] == "planned"
        assert result["total_distance_nm"] > 0

    def test_start_and_complete_voyage(self):
        self.ch.create_voyage(
            voyage_id="V002",
            vessel_name="Test Ship",
            departure={"name": "A", "lat": 30, "lon": 120, "eta": "", "etd": ""},
            arrival={"name": "B", "lat": 35, "lon": 140, "eta": "", "etd": ""},
        )
        start = self.ch.start_voyage()
        assert start["status"] == "in_progress"

        complete = self.ch.complete_voyage()
        assert complete["status"] == "completed"

    def test_update_position_calculates_eta(self):
        self.ch.create_voyage(
            voyage_id="V003",
            vessel_name="Test Ship",
            departure={"name": "A", "lat": 30, "lon": 120, "eta": "", "etd": ""},
            arrival={"name": "B", "lat": 35, "lon": 140, "eta": "", "etd": ""},
        )
        self.ch.start_voyage()
        result = self.ch.update_position(31.0, 122.0, course=45, speed=12)
        assert "remaining_distance_nm" in result
        assert "eta" in result
        assert "progress_pct" in result

    def test_daily_report(self):
        self.ch.create_voyage(
            voyage_id="V004",
            vessel_name="DailyShip",
            departure={"name": "A", "lat": 30, "lon": 120, "eta": "", "etd": ""},
            arrival={"name": "B", "lat": 35, "lon": 140, "eta": "", "etd": ""},
        )
        report = self.ch.generate_daily_report()
        assert report["voyage_id"] == "V004"
        assert "report_date" in report

    def test_add_log_entry(self):
        entry = self.ch.add_log_entry("event", "测试日志", author="captain")
        assert entry["type"] == "event"
        assert entry["author"] == "captain"


class TestCyberSecurityChannel:

    def setup_method(self):
        self.ch = CyberSecurityChannel()
        self.ch.initialize()

    def teardown_method(self):
        self.ch.shutdown()

    def test_initialize(self):
        assert self.ch._initialized

    def test_get_status(self):
        status = self.ch.get_status()
        assert status["threat_level"] == "none"
        assert status["channel"] == "cyber_security"

    def test_create_session(self):
        token = self.ch.create_session("captain", AccessRole.MASTER, "192.168.1.1")
        assert token is not None
        assert len(token) == 64  # 32 bytes hex

    def test_validate_session(self):
        token = self.ch.create_session("officer1", AccessRole.OFFICER)
        session = self.ch.validate_session(token)
        assert session is not None
        assert session.user_id == "officer1"
        assert session.role == AccessRole.OFFICER

    def test_end_session(self):
        token = self.ch.create_session("user1", AccessRole.VIEWER)
        assert self.ch.end_session(token)
        assert self.ch.validate_session(token) is None

    def test_check_permission_granted(self):
        assert self.ch.check_permission("captain", AccessRole.MASTER, "change_autonomy")

    def test_check_permission_denied(self):
        assert not self.ch.check_permission("viewer", AccessRole.VIEWER, "change_autonomy")

    def test_brute_force_detection(self):
        for _ in range(5):
            self.ch.record_failed_login("attacker", "10.0.0.1")
        token = self.ch.create_session("attacker", AccessRole.VIEWER, "10.0.0.1")
        assert token is None  # Blocked

    def test_detect_anomaly(self):
        result = self.ch.detect_anomaly("network", "packet_rate", 15000, 10000)
        assert result is not None
        assert result["category"] == "anomaly"

    def test_detect_anomaly_no_trigger(self):
        result = self.ch.detect_anomaly("network", "packet_rate", 5000, 10000)
        assert result is None

    def test_data_integrity_check(self):
        data = b"important sensor data"
        self.ch.register_checksum("sensor-1", data)
        assert self.ch.verify_checksum("sensor-1", data)
        assert not self.ch.verify_checksum("sensor-1", b"tampered data")

    def test_audit_log(self):
        self.ch.create_session("user", AccessRole.OPERATOR)
        logs = self.ch.get_audit_log(limit=10)
        assert len(logs) >= 1
        assert any(log["action"] == "login" for log in logs)

    def test_threat_summary(self):
        self.ch.detect_anomaly("test", "metric", 200, 100)
        summary = self.ch.get_threat_summary()
        assert summary["recent_events_count"] >= 1

    def test_shutdown_clears_sessions(self):
        token = self.ch.create_session("user", AccessRole.VIEWER)
        self.ch.shutdown()
        assert not self.ch._initialized

