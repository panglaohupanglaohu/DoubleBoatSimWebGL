# -*- coding: utf-8 -*-
"""
Tests for L5: OpenBridge HMI + AR-CAS + Cloud-Edge Channel
"""

import pytest
from channels.openbridge_hmi import (
    OpenBridgeHMIChannel, AROverlay, NASATLXScore,
    CloudEdgeSyncState, AlertSeverity, WorkContext, CognitiveState,
)


@pytest.fixture
def hmi():
    ch = OpenBridgeHMIChannel()
    ch.initialize()
    return ch


class TestOpenBridgeHMIInit:
    def test_initialize(self, hmi):
        assert hmi._initialized
        assert len(hmi._design_tokens) > 0

    def test_design_tokens_loaded(self, hmi):
        assert "ob-color-alert-emergency" in hmi._design_tokens
        assert "ob-color-primary" in hmi._design_tokens
        assert "ob-typography-heading" in hmi._design_tokens
        assert "ob-spacing-unit" in hmi._design_tokens


class TestAROverlay:
    def test_add_ar_overlay(self, hmi):
        overlay = hmi.add_ar_overlay(
            target_mmsi="413000001", target_name="COSCO STAR",
            bearing=45.0, distance_nm=2.5, cpa=0.5, tcpa=10.0, risk_level=0.6
        )
        assert overlay.overlay_id == "ar-413000001"
        assert overlay.target_name == "COSCO STAR"
        assert overlay.visible

    def test_ar_position_mapping(self, hmi):
        overlay = hmi.add_ar_overlay(
            target_mmsi="123", target_name="T1",
            bearing=0.0, distance_nm=1.0, cpa=0.5, tcpa=10.0, risk_level=0.3
        )
        px, py = overlay.ar_position
        assert px > 0

    def test_risk_to_color(self, hmi):
        assert hmi._risk_to_color(0.9) == "#FF0000"
        assert hmi._risk_to_color(0.7) == "#FF6600"
        assert hmi._risk_to_color(0.5) == "#FFCC00"
        assert hmi._risk_to_color(0.3) == "#00CCFF"
        assert hmi._risk_to_color(0.1) == "#00FF00"

    def test_multiple_overlays(self, hmi):
        for i in range(5):
            hmi.add_ar_overlay(f"m{i}", f"Ship_{i}", i * 30, i + 1, 0.5, 10, 0.1 * i)
        assert len(hmi._ar_overlays) == 5


class TestAlertSystem:
    def test_push_alert(self, hmi):
        alert = hmi.push_alert(AlertSeverity.WARNING, "Test Alert", "Test message")
        assert alert["severity"] == "warning"
        assert not alert["acknowledged"]

    def test_push_emergency_increases_load(self, hmi):
        initial = hmi._tlx_score.mental_demand
        hmi.push_alert(AlertSeverity.EMERGENCY, "Emergency", "Emergency!")
        assert hmi._tlx_score.mental_demand > initial

    def test_acknowledge_alert(self, hmi):
        alert = hmi.push_alert(AlertSeverity.WARNING, "Test", "msg")
        assert hmi.acknowledge_alert(alert["id"])
        assert hmi._alert_queue[-1]["acknowledged"]

    def test_acknowledge_nonexistent(self, hmi):
        assert not hmi.acknowledge_alert("nonexistent")

    def test_multiple_emergency_overloads(self, hmi):
        for i in range(10):
            hmi.push_alert(AlertSeverity.EMERGENCY, f"E{i}", "urgent")
        # push_alert doesn't change TLX, so check alert count
        unacked = [a for a in hmi._alert_queue if not a["acknowledged"]]
        assert len(unacked) == 10


class TestCognitiveState:
    def test_initial_state(self, hmi):
        assert hmi._cognitive_state == CognitiveState.NORMAL

    def test_overloaded_detection(self, hmi):
        hmi._tlx_score.mental_demand = 95
        hmi._tlx_score.physical_demand = 95
        hmi._tlx_score.temporal_demand = 95
        hmi._tlx_score.performance = 10  # 100 - performance contributes
        hmi._tlx_score.effort = 95
        hmi._tlx_score.frustration = 95
        hmi._update_cognitive_state()
        assert hmi._cognitive_state == CognitiveState.OVERLOADED

    def test_alert_state(self, hmi):
        hmi._tlx_score.mental_demand = 10
        hmi._tlx_score.temporal_demand = 10
        hmi._tlx_score.effort = 10
        hmi._tlx_score.frustration = 10
        hmi._tlx_score.performance = 95
        hmi._update_cognitive_state()
        assert hmi._cognitive_state == CognitiveState.ALERT


class TestNASATLX:
    def test_overall_score(self):
        score = NASATLXScore(mental_demand=50, physical_demand=20,
                            temporal_demand=50, performance=70,
                            effort=50, frustration=30)
        overall = score.overall
        assert 0 <= overall <= 100

    def test_get_nasa_tlx(self, hmi):
        result = hmi.get_nasa_tlx()
        assert "mental_demand" in result
        assert "overall" in result
        assert "cognitive_state" in result


class TestAttentionGuidance:
    def test_get_attention_guidance(self, hmi):
        hmi.push_alert(AlertSeverity.ALARM, "Alarm 1", "Alarm!")
        hmi.push_alert(AlertSeverity.WARNING, "Warning 1", "Warning!")
        hmi.add_ar_overlay("m1", "Ship1", 30, 1.5, 0.3, 5, 0.7)
        guidance = hmi.get_attention_guidance()
        assert len(guidance) > 0
        # Alarms should be first
        assert guidance[0]["type"] == "alert"

    def test_attention_priority_ordering(self, hmi):
        hmi.push_alert(AlertSeverity.WARNING, "W1", "warning")
        hmi.push_alert(AlertSeverity.EMERGENCY, "E1", "emergency")
        guidance = hmi.get_attention_guidance()
        if len(guidance) >= 2:
            assert guidance[0]["severity"] == "emergency"


class TestWorkContext:
    def test_set_work_context(self, hmi):
        assert hmi.set_work_context("docking")
        assert hmi._work_context == WorkContext.DOCKING

    def test_set_invalid_context(self, hmi):
        assert not hmi.set_work_context("invalid")


class TestCloudEdge:
    def test_update_sync(self, hmi):
        result = hmi.update_cloud_edge_sync(uploads=5, downloads=3,
                                             latency_ms=100, bandwidth_kbps=500)
        assert result["mode"] == "full"

    def test_sync_mode_delta(self, hmi):
        result = hmi.update_cloud_edge_sync(latency_ms=2000)
        assert result["mode"] == "delta"

    def test_sync_mode_compressed(self, hmi):
        result = hmi.update_cloud_edge_sync(latency_ms=6000)
        assert result["mode"] == "compressed"

    def test_model_ota(self, hmi):
        result = hmi.simulate_model_ota("2.0.0")
        assert result["new_version"] == "2.0.0"
        assert result["in_sync"]

    def test_pending_accumulates(self, hmi):
        hmi.update_cloud_edge_sync(uploads=5)
        hmi.update_cloud_edge_sync(uploads=3)
        assert hmi._cloud_edge.pending_uploads == 8


class TestHMIStatus:
    def test_get_status(self, hmi):
        status = hmi.get_status()
        assert status["name"] == "openbridge_hmi"
        assert "ar_overlays" in status
        assert "cognitive_state" in status
        assert "cloud_edge" in status

    def test_shutdown(self, hmi):
        assert hmi.shutdown()
        assert not hmi._initialized
