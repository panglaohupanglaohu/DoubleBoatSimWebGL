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
