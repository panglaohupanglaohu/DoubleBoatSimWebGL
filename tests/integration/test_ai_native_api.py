#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Native API 集成测试 — 使用 starlette TestClient (无需启动服务器)
"""

import pytest
from starlette.testclient import TestClient
from main import app


@pytest.fixture()
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


class TestAINativeDashboard:
    def test_dashboard_contains_ai_native_sections(self, client):
        response = client.get("/api/v1/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "captain_agent" in data
        assert "memory" in data
        assert "compliance" in data
        assert "perception" in data
        assert "decision" in data

    def test_coordination_status_endpoint(self, client):
        response = client.get("/api/v1/ai-native/coordination/status")
        assert response.status_code == 200
        data = response.json()
        assert "coordination" in data
        assert "memory" in data

    def test_memory_replay_endpoint(self, client):
        response = client.get(
            "/api/v1/ai-native/memory/replay",
            params={"limit": 5, "event_types": "decision_package_event,decision_feedback_event"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "event_types" in data

    def test_compliance_structure(self, client):
        response = client.get("/api/v1/dashboard")
        data = response.json()
        compliance = data["compliance"]
        assert "risk_level" in compliance
        assert "compliance_status" in compliance
        assert "recommended_actions" in compliance

    def test_perception_structure(self, client):
        response = client.get("/api/v1/dashboard")
        data = response.json()
        perception = data["perception"]
        assert "event_count" in perception
        assert "latest_events" in perception

    def test_decision_structure(self, client):
        response = client.get("/api/v1/dashboard")
        data = response.json()
        decision = data["decision"]
        assert "risk_level" in decision
        assert "compliance_status" in decision
        assert "recommended_actions" in decision
        assert "latest_events" in decision


class TestAINativeQueryEndpoints:
    def test_compliance_query(self, client):
        response = client.post(
            "/api/v1/channels/compliance_digital_expert/query",
            json={"query": "overall"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "compliance_digital_expert"
        assert "risk_level" in data["result"]

    def test_perception_query(self, client):
        response = client.post(
            "/api/v1/channels/distributed_perception_hub/query",
            json={"query": "latest events"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "distributed_perception_hub"
        assert "latest_events" in data["result"]
        assert isinstance(data["result"]["latest_events"], list)

    def test_decision_query(self, client):
        response = client.post(
            "/api/v1/channels/decision_orchestrator/query",
            json={"query": "decision package"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "decision_orchestrator"
        assert "risk_level" in data["result"]
        assert "recommended_actions" in data["result"]

    def test_channel_list_contains_ai_native_channels(self, client):
        response = client.get("/api/v1/channels")
        assert response.status_code == 200
        data = response.json()
        names = [ch["name"] for ch in data["channels"]]
        assert "compliance_digital_expert" in names
        assert "distributed_perception_hub" in names
        assert "decision_orchestrator" in names


class TestAINativeRCSSHMEndpoints:
    def test_rcs_status(self, client):
        response = client.get("/api/v1/ai-native/rcs/status")
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "rcs_control"
        result = data["result"]
        assert "foil_angle_deg" in result
        assert "trim_tab_angle_deg" in result
        assert "stability_margin" in result

    def test_shm_status(self, client):
        response = client.get("/api/v1/ai-native/shm/status")
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "structural_health_monitor"
        result = data["result"]
        assert "fatigue_damage_index" in result
        assert "life_remaining_pct" in result
        assert "strain_hotspots" in result


class TestAINativeCPSAndMemory:
    def test_cps_mission_brief(self, client):
        response = client.get("/api/v1/ai-native/cps/mission-brief")
        assert response.status_code == 200
        data = response.json()
        assert "mission_brief" in data
        assert "action_plan" in data
        assert "task_graph" in data

    def test_memory_events(self, client):
        response = client.get("/api/v1/ai-native/memory/events", params={"limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "events" in data
        assert isinstance(data["events"], list)

    def test_memory_analytics_status(self, client):
        response = client.get("/api/v1/ai-native/memory/analytics/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "storage_profile" in data
        assert "lakehouse_status" in data

    def test_fusion_state(self, client):
        response = client.get("/api/v1/ai-native/perception/fusion-state")
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "distributed_perception_hub"
        assert "fusion" in data


class TestAINativePostEndpoints:
    def test_decision_feedback_log(self, client):
        response = client.post(
            "/api/v1/ai-native/decision/feedback/log",
            json={"action": "test_action", "outcome": "success", "confirmed_by": "test"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "decision_orchestrator"
        assert "result" in data
        assert "feedback_records_count" in data

    def test_openbridge_command(self, client):
        response = client.post(
            "/api/v1/ai-native/openbridge/command",
            json={"command": "查看任务图", "source": "test"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "test"
        assert "result" in data
        result = data["result"]
        assert result["recognized_intent"] == "show_task_graph"
        assert "summary" in result
        assert "control_state" in result

    def test_openbridge_command_rcs(self, client):
        response = client.post(
            "/api/v1/ai-native/openbridge/command",
            json={"command": "rcs 姿态", "source": "bridge_chat"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["recognized_intent"] == "set_comfort_mode"

    def test_openbridge_command_shm(self, client):
        response = client.post(
            "/api/v1/ai-native/openbridge/command",
            json={"command": "结构健康", "source": "bridge_chat"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["recognized_intent"] == "show_structural_health"


class TestAINativeExtensionEndpoints:
    def test_compliance_status(self, client):
        response = client.get("/api/v1/ai-native/compliance/status")
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "compliance_digital_expert"
        assert "result" in data

    def test_cognitive_snapshot(self, client):
        response = client.get("/api/v1/ai-native/compliance/cognitive-snapshot")
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "compliance_digital_expert"
        assert "result" in data

    def test_perception_events(self, client):
        response = client.get("/api/v1/ai-native/perception/events", params={"limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "distributed_perception_hub"
        assert "result" in data
        assert "events" in data["result"]

    def test_perception_capture_snapshot(self, client):
        response = client.get("/api/v1/ai-native/perception/capture-snapshot")
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "distributed_perception_hub"
        assert "result" in data

    def test_decision_package(self, client):
        response = client.get("/api/v1/ai-native/decision/package")
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "decision_orchestrator"
        assert "result" in data

    def test_decision_feedback(self, client):
        response = client.post(
            "/api/v1/ai-native/decision/feedback",
            params={"action": "slow_down", "outcome": "accepted"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "decision_orchestrator"
        assert "result" in data
        assert "feedback_records_count" in data

    def test_full_pipeline_status(self, client):
        response = client.get("/api/v1/ai-native/status/full-pipeline")
        assert response.status_code == 200
        data = response.json()
        assert "pipeline_health" in data
