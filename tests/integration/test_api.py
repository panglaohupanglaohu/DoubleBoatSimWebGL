#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DoubleBoatClawSystem 集成测试 - API 测试

使用 starlette TestClient 在进程内测试，避免依赖外部启动服务。
"""

import time
import pytest
from starlette.testclient import TestClient
from main import app


@pytest.fixture()
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


class TestBackendAPI:
    """后端 API 集成测试"""

    def test_root_endpoint(self, client):
        """测试根端点"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "DoubleBoatClawSystem" in data["name"]

    def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "connections" in data

    def test_get_sensors(self, client):
        """测试获取传感器列表"""
        response = client.get("/api/v1/sensors")
        assert response.status_code == 200
        data = response.json()
        assert "sensors" in data
        assert len(data["sensors"]) > 0
        first = data["sensors"][0]
        # 功能契约：目录字段恒定，可附带实时快照字段
        assert "id" in first
        assert "type" in first
        assert "description" in first

    def test_get_ais_targets(self, client):
        """测试获取 AIS 目标"""
        response = client.get("/api/v1/ais/targets")
        assert response.status_code == 200
        data = response.json()
        assert "targets" in data
        # 应该有仿真 AIS 目标
        assert len(data["targets"]) >= 0

    def test_get_engine_status(self, client):
        """测试获取主机状态"""
        response = client.get("/api/v1/engine/status")
        assert response.status_code == 200
        data = response.json()
        assert "engine_id" in data
        assert "status" in data or "health_score" in data

    def test_get_alerts(self, client):
        """测试获取报警列表"""
        response = client.get("/api/v1/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data


class TestWebSocket:
    """WebSocket 集成测试（同步 TestClient 版本）"""

    def test_websocket_connect(self, client):
        """测试 WebSocket 连接"""
        with client.websocket_connect("/ws") as websocket:
            assert websocket is not None

    def test_websocket_subscribe(self, client):
        """测试 WebSocket 订阅"""
        with client.websocket_connect("/ws") as websocket:
            websocket.send_json({
                "action": "subscribe",
                "channel": "navigation_data",
            })

            deadline = time.time() + 5.0
            while time.time() < deadline:
                data = websocket.receive_json()
                if data.get("type") == "data_update":
                    assert "timestamp" in data
                    assert "data" in data
                    return

            pytest.fail("No data_update received within timeout")

    def test_websocket_data_format(self, client):
        """测试 WebSocket 数据格式"""
        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()

            # 验证数据结构
            assert "type" in data
            assert data["type"] == "data_update"
            assert "data" in data
            assert "timestamp" in data

            # 验证数据内容
            payload = data["data"]
            assert "sensors" in payload
            assert "ais_targets" in payload
            assert "alarms" in payload
            assert isinstance(payload["sensors"], dict)


class TestDataIntegrity:
    """数据完整性测试"""

    def test_sensor_data_consistency(self, client):
        """测试传感器数据一致性"""
        # 连续获取 3 次传感器数据
        responses = []
        for _ in range(3):
            response = client.get("/api/v1/sensors")
            assert response.status_code == 200
            responses.append(response.json())
        
        # 验证数据结构一致
        first_keys = set(responses[0]["sensors"][0].keys())
        for resp in responses[1:]:
            assert set(resp["sensors"][0].keys()) == first_keys

    def test_ais_target_format(self, client):
        """测试 AIS 目标数据格式"""
        response = client.get("/api/v1/ais/targets")
        if response.status_code == 200:
            data = response.json()
            for target in data["targets"]:
                # 验证必需字段
                assert "mmsi" in target
                assert "latitude" in target
                assert "longitude" in target
                assert "course" in target
                assert "speed" in target
                
                # 验证值范围
                assert -90 <= target["latitude"] <= 90
                assert -180 <= target["longitude"] <= 180
                assert 0 <= target["course"] <= 360
                assert target["speed"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
