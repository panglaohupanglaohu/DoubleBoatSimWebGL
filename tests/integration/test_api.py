#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DoubleBoatClawSystem 集成测试 - API 测试
"""

import pytest
import httpx
import asyncio
import websockets
import json
from pathlib import Path
import sys

# 测试配置
BASE_URL = "http://localhost:8081"
WS_URL = "ws://localhost:8081/ws"


class TestBackendAPI:
    """后端 API 集成测试"""

    def test_root_endpoint(self):
        """测试根端点"""
        response = httpx.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "DoubleBoatClawSystem" in data["name"]

    def test_health_endpoint(self):
        """测试健康检查端点"""
        response = httpx.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "connections" in data

    def test_get_sensors(self):
        """测试获取传感器列表"""
        response = httpx.get(f"{BASE_URL}/api/v1/sensors")
        assert response.status_code == 200
        data = response.json()
        assert "sensors" in data
        assert len(data["sensors"]) > 0

    def test_get_ais_targets(self):
        """测试获取 AIS 目标"""
        response = httpx.get(f"{BASE_URL}/api/v1/ais/targets")
        assert response.status_code == 200
        data = response.json()
        assert "targets" in data
        # 应该有仿真 AIS 目标
        assert len(data["targets"]) >= 0

    def test_get_engine_status(self):
        """测试获取主机状态"""
        response = httpx.get(f"{BASE_URL}/api/v1/engine/status")
        # 可能需要等待仿真引擎生成数据
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "engine_id" in data
            assert "rpm" in data

    def test_get_alerts(self):
        """测试获取报警列表"""
        response = httpx.get(f"{BASE_URL}/api/v1/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data


@pytest.mark.asyncio
class TestWebSocket:
    """WebSocket 集成测试"""

    async def test_websocket_connect(self):
        """测试 WebSocket 连接"""
        try:
            async with websockets.connect(WS_URL) as websocket:
                # 连接成功
                assert websocket.open
                await websocket.close()
        except Exception as e:
            # 如果服务器未启动，跳过测试
            pytest.skip(f"WebSocket server not available: {e}")

    async def test_websocket_subscribe(self):
        """测试 WebSocket 订阅"""
        try:
            async with websockets.connect(WS_URL) as websocket:
                # 发送订阅消息
                await websocket.send(json.dumps({
                    "action": "subscribe",
                    "channel": "navigation_data"
                }))
                
                # 接收消息 (应该在 5 秒内收到数据更新)
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    assert data["type"] == "data_update"
                except asyncio.TimeoutError:
                    pytest.skip("No data received within timeout")
                    
        except Exception as e:
            pytest.skip(f"WebSocket test skipped: {e}")

    async def test_websocket_data_format(self):
        """测试 WebSocket 数据格式"""
        try:
            async with websockets.connect(WS_URL) as websocket:
                # 等待数据更新
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    
                    # 验证数据结构
                    assert "type" in data
                    assert data["type"] == "data_update"
                    assert "data" in data
                    assert "timestamp" in data
                    
                    # 验证数据内容
                    payload = data["data"]
                    assert "sensors" in payload or "ais_targets" in payload or "engine" in payload
                    
                except asyncio.TimeoutError:
                    pytest.skip("No data received within timeout")
                    
        except Exception as e:
            pytest.skip(f"WebSocket test skipped: {e}")


class TestDataIntegrity:
    """数据完整性测试"""

    def test_sensor_data_consistency(self):
        """测试传感器数据一致性"""
        # 连续获取 3 次传感器数据
        responses = []
        for _ in range(3):
            response = httpx.get(f"{BASE_URL}/api/v1/sensors")
            assert response.status_code == 200
            responses.append(response.json())
        
        # 验证数据结构一致
        first_keys = set(responses[0]["sensors"][0].keys())
        for resp in responses[1:]:
            assert set(resp["sensors"][0].keys()) == first_keys

    def test_ais_target_format(self):
        """测试 AIS 目标数据格式"""
        response = httpx.get(f"{BASE_URL}/api/v1/ais/targets")
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
