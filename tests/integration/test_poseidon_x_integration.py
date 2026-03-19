# -*- coding: utf-8 -*-
"""
Poseidon-X Integration Tests - 自动化集成测试

后端 API 测试使用 starlette TestClient（无需启动服务器）。
前端页面测试需要 Vite dev server，标记为 skip。
"""

import pytest
import time
from typing import Dict, Any
from starlette.testclient import TestClient
from main import app


@pytest.fixture()
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# ==================== 前端页面测试 (需要 Vite dev server) ====================

requires_frontend = pytest.mark.skip(reason="Requires running Vite dev server on localhost:5173")


@requires_frontend
class TestLLMConfig:
    """LLM 配置页面自动化测试."""

    def test_config_page_accessible(self): ...
    def test_config_page_providers(self): ...
    def test_config_page_form_elements(self): ...


@requires_frontend
class TestBridgeChat:
    """Bridge Chat 自动化测试."""

    def test_digital_twin_page_accessible(self): ...
    def test_bridge_chat_component_exists(self): ...
    def test_llm_status_display(self): ...


@requires_frontend
class TestWebSocket:
    """WebSocket 连接自动化测试."""

    def test_websocket_endpoint_exists(self): ...


# ==================== 后端 API 测试 (TestClient, 无需服务器) ====================


class TestChannelsAPI:
    """Channel API 自动化测试."""

    def test_channels_endpoint_accessible(self, client):
        response = client.get("/api/v1/channels")
        assert response.status_code == 200

    def test_channels_response_format(self, client):
        response = client.get("/api/v1/channels")
        data = response.json()
        assert "channels" in data
        assert isinstance(data["channels"], list)

    def test_energy_efficiency_channel_registered(self, client):
        response = client.get("/api/v1/channels")
        data = response.json()
        channel_names = [ch["name"] for ch in data["channels"]]
        assert "energy_efficiency" in channel_names

    def test_intelligent_navigation_channel_registered(self, client):
        response = client.get("/api/v1/channels")
        data = response.json()
        channel_names = [ch["name"] for ch in data["channels"]]
        assert "intelligent_navigation" in channel_names

    def test_channel_health_status(self, client):
        response = client.get("/api/v1/channels")
        data = response.json()
        for channel in data["channels"]:
            assert channel["health"] == "ok"
            assert channel["initialized"] is True

    def test_channel_details(self, client):
        response = client.get("/api/v1/channels")
        data = response.json()
        for channel in data["channels"]:
            assert "name" in channel
            assert "description" in channel
            assert "version" in channel
            assert "health" in channel
            assert isinstance(channel["name"], str)
            assert isinstance(channel["version"], str)


class TestSensorsAPI:
    """传感器 API 自动化测试."""

    def test_sensors_endpoint_accessible(self, client):
        response = client.get("/api/v1/sensors")
        assert response.status_code == 200

    def test_sensors_response_format(self, client):
        response = client.get("/api/v1/sensors")
        data = response.json()
        assert "sensors" in data
        assert isinstance(data["sensors"], list)

    def test_sensors_count(self, client):
        response = client.get("/api/v1/sensors")
        data = response.json()
        assert len(data["sensors"]) >= 4

    def test_sensor_structure(self, client):
        response = client.get("/api/v1/sensors")
        data = response.json()
        for sensor in data["sensors"]:
            assert "id" in sensor
            assert "type" in sensor
            assert "description" in sensor


class TestRootAPI:
    """根路径 API 自动化测试."""

    def test_root_endpoint_accessible(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_response_format(self, client):
        response = client.get("/")
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "description" in data

    def test_root_api_info(self, client):
        response = client.get("/")
        data = response.json()
        assert "DoubleBoatClawSystem" in data["name"]
        assert data["version"] == "1.0.0"


class TestPerformance:
    """性能自动化测试."""

    def test_api_response_time(self, client):
        start_time = time.time()
        response = client.get("/api/v1/sensors")
        elapsed = time.time() - start_time
        assert elapsed < 1.0
        assert response.status_code == 200

    def test_channels_response_time(self, client):
        start_time = time.time()
        response = client.get("/api/v1/channels")
        elapsed = time.time() - start_time
        assert elapsed < 1.0
        assert response.status_code == 200

    def test_frontend_response_time(self, client):
        """前端页面响应时间 — 跳过 (需要 Vite dev server)."""
        pytest.skip("Requires running Vite dev server on localhost:5173")


class TestEndToEnd:
    """端到端自动化测试."""

    def test_full_system_startup(self, client):
        backend_response = client.get("/")
        assert backend_response.status_code == 200

        channels_response = client.get("/api/v1/channels")
        assert channels_response.status_code == 200
        assert len(channels_response.json()["channels"]) >= 1

        sensors_response = client.get("/api/v1/sensors")
        assert sensors_response.status_code == 200
        assert len(sensors_response.json()["sensors"]) >= 4

    def test_llm_config_workflow(self, client):
        """LLM 配置工作流 — 跳过前端部分。"""
        pytest.skip("Requires running Vite dev server on localhost:5173")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
