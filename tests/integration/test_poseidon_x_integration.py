# -*- coding: utf-8 -*-
"""
Poseidon-X Integration Tests - 自动化集成测试

测试范围:
- LLM 配置页面功能
- Bridge Chat 交互
- Channel 注册与调用
- API 端点集成
- 前后端数据流

作者：CaptainCatamaran (自动化测试) 🐱⛵
日期：2026-03-14
"""

import pytest
import requests
import time
from typing import Dict, Any


BASE_URL = "http://localhost:8080"
FRONTEND_URL = "http://localhost:5173"


class TestLLMConfig:
    """LLM 配置页面自动化测试."""
    
    def test_config_page_accessible(self):
        """测试 LLM 配置页面可访问."""
        response = requests.get(f"{FRONTEND_URL}/poseidon-config.html")
        assert response.status_code == 200
        assert "Poseidon-X 配置中心" in response.text
        assert "LLM 提供商" in response.text
    
    def test_config_page_providers(self):
        """测试 LLM 配置页面提供商选项."""
        response = requests.get(f"{FRONTEND_URL}/poseidon-config.html")
        
        # 检查 4 个提供商
        assert "minimax" in response.text.lower()
        assert "deepseek" in response.text.lower()
        assert "openai" in response.text.lower()
        assert "local" in response.text.lower() or "ollama" in response.text.lower()
    
    def test_config_page_form_elements(self):
        """测试配置页面表单元素."""
        response = requests.get(f"{FRONTEND_URL}/poseidon-config.html")
        
        # 检查关键表单元素
        assert "apiKey" in response.text
        assert "apiEndpoint" in response.text
        assert "model" in response.text
        assert "temperature" in response.text
        assert "保存配置" in response.text or "save" in response.text.lower()


class TestBridgeChat:
    """Bridge Chat 自动化测试."""
    
    def test_digital_twin_page_accessible(self):
        """测试数字孪生页面可访问."""
        response = requests.get(f"{FRONTEND_URL}/digital-twin.html")
        assert response.status_code == 200
        assert "DoubleBoatClawSystem" in response.text
        assert "数字孪生" in response.text
    
    def test_bridge_chat_component_exists(self):
        """测试 Bridge Chat 组件存在."""
        response = requests.get(f"{FRONTEND_URL}/digital-twin.html")
        
        # 检查 Bridge Chat 相关元素
        assert "bridge-chat" in response.text.lower() or "Poseidon-X Bridge" in response.text
        assert "simple-bridge-chat.js" in response.text
    
    def test_llm_status_display(self):
        """测试 LLM 状态显示."""
        response = requests.get(f"{FRONTEND_URL}/digital-twin.html")
        
        # 检查 LLM 状态元素
        assert "llm-status" in response.text.lower() or "LLM" in response.text


class TestChannelsAPI:
    """Channel API 自动化测试."""
    
    def test_channels_endpoint_accessible(self):
        """测试 Channels API 端点可访问."""
        response = requests.get(f"{BASE_URL}/api/v1/channels")
        assert response.status_code == 200
    
    def test_channels_response_format(self):
        """测试 Channels API 响应格式."""
        response = requests.get(f"{BASE_URL}/api/v1/channels")
        data = response.json()
        
        assert "channels" in data
        assert isinstance(data["channels"], list)
    
    def test_energy_efficiency_channel_registered(self):
        """测试能效管理 Channel 已注册."""
        response = requests.get(f"{BASE_URL}/api/v1/channels")
        data = response.json()
        
        channel_names = [ch["name"] for ch in data["channels"]]
        assert "energy_efficiency" in channel_names
    
    def test_intelligent_navigation_channel_registered(self):
        """测试智能导航 Channel 已注册."""
        response = requests.get(f"{BASE_URL}/api/v1/channels")
        data = response.json()
        
        channel_names = [ch["name"] for ch in data["channels"]]
        assert "intelligent_navigation" in channel_names
    
    def test_channel_health_status(self):
        """测试 Channel 健康状态."""
        response = requests.get(f"{BASE_URL}/api/v1/channels")
        data = response.json()
        
        for channel in data["channels"]:
            assert channel["health"] == "ok"
            assert channel["initialized"] is True
    
    def test_channel_details(self):
        """测试 Channel 详细信息."""
        response = requests.get(f"{BASE_URL}/api/v1/channels")
        data = response.json()
        
        for channel in data["channels"]:
            # 检查必需字段
            assert "name" in channel
            assert "description" in channel
            assert "version" in channel
            assert "health" in channel
            
            # 检查字段类型
            assert isinstance(channel["name"], str)
            assert isinstance(channel["version"], str)


class TestSensorsAPI:
    """传感器 API 自动化测试."""
    
    def test_sensors_endpoint_accessible(self):
        """测试传感器 API 端点可访问."""
        response = requests.get(f"{BASE_URL}/api/v1/sensors")
        assert response.status_code == 200
    
    def test_sensors_response_format(self):
        """测试传感器 API 响应格式."""
        response = requests.get(f"{BASE_URL}/api/v1/sensors")
        data = response.json()
        
        assert "sensors" in data
        assert isinstance(data["sensors"], list)
    
    def test_sensors_count(self):
        """测试传感器数量."""
        response = requests.get(f"{BASE_URL}/api/v1/sensors")
        data = response.json()
        
        # 至少应该有 4 个传感器 (GPS/COMPASS/LOG/ECHO)
        assert len(data["sensors"]) >= 4
    
    def test_sensor_structure(self):
        """测试传感器数据结构."""
        response = requests.get(f"{BASE_URL}/api/v1/sensors")
        data = response.json()
        
        for sensor in data["sensors"]:
            assert "id" in sensor
            assert "type" in sensor
            assert "description" in sensor


class TestRootAPI:
    """根路径 API 自动化测试."""
    
    def test_root_endpoint_accessible(self):
        """测试根路径端点可访问."""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
    
    def test_root_response_format(self):
        """测试根路径响应格式."""
        response = requests.get(f"{BASE_URL}/")
        data = response.json()
        
        assert "name" in data
        assert "version" in data
        assert "description" in data
    
    def test_root_api_info(self):
        """测试 API 信息完整性."""
        response = requests.get(f"{BASE_URL}/")
        data = response.json()
        
        assert "DoubleBoatClawSystem" in data["name"]
        assert data["version"] == "1.0.0"


class TestWebSocket:
    """WebSocket 连接自动化测试."""
    
    def test_websocket_endpoint_exists(self):
        """测试 WebSocket 端点存在."""
        # 检查 HTML 中是否有 WebSocket 连接代码
        response = requests.get(f"{FRONTEND_URL}/digital-twin.html")
        
        # WebSocket 连接应该在页面中
        assert "ws://" in response.text or "websocket" in response.text.lower()


class TestPerformance:
    """性能自动化测试."""
    
    def test_api_response_time(self):
        """测试 API 响应时间."""
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/api/v1/sensors")
        elapsed = time.time() - start_time
        
        # API 响应时间应小于 1 秒
        assert elapsed < 1.0
        assert response.status_code == 200
    
    def test_channels_response_time(self):
        """测试 Channels API 响应时间."""
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/api/v1/channels")
        elapsed = time.time() - start_time
        
        # API 响应时间应小于 1 秒
        assert elapsed < 1.0
        assert response.status_code == 200
    
    def test_frontend_response_time(self):
        """测试前端页面响应时间."""
        start_time = time.time()
        response = requests.get(f"{FRONTEND_URL}/digital-twin.html")
        elapsed = time.time() - start_time
        
        # 前端响应时间应小于 2 秒
        assert elapsed < 2.0
        assert response.status_code == 200


class TestEndToEnd:
    """端到端自动化测试."""
    
    def test_full_system_startup(self):
        """测试完整系统启动."""
        # 1. 后端可访问
        backend_response = requests.get(f"{BASE_URL}/")
        assert backend_response.status_code == 200
        
        # 2. 前端可访问
        frontend_response = requests.get(f"{FRONTEND_URL}/digital-twin.html")
        assert frontend_response.status_code == 200
        
        # 3. Channel 已注册
        channels_response = requests.get(f"{BASE_URL}/api/v1/channels")
        assert channels_response.status_code == 200
        assert len(channels_response.json()["channels"]) >= 1
        
        # 4. 传感器数据可用
        sensors_response = requests.get(f"{BASE_URL}/api/v1/sensors")
        assert sensors_response.status_code == 200
        assert len(sensors_response.json()["sensors"]) >= 4
    
    def test_llm_config_workflow(self):
        """测试 LLM 配置工作流."""
        # 1. 配置页面可访问
        config_response = requests.get(f"{FRONTEND_URL}/poseidon-config.html")
        assert config_response.status_code == 200
        
        # 2. 配置页面包含必要元素
        assert "LLM" in config_response.text
        assert "API" in config_response.text
        
        # 3. 数字孪生页面显示 LLM 状态
        twin_response = requests.get(f"{FRONTEND_URL}/digital-twin.html")
        assert twin_response.status_code == 200
        assert "LLM" in twin_response.text or "llm" in twin_response.text


# ==================== 测试报告生成 ====================

def generate_test_report(results):
    """生成测试报告."""
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    
    report = f"""
# 自动化测试报告

**生成时间**: {time.strftime("%Y-%m-%d %H:%M:%S")}
**测试总数**: {total}
**通过**: {passed}
**失败**: {failed}
**通过率**: {passed/total*100:.1f}%

## 测试结果

"""
    
    for result in results:
        status = "✅" if result["passed"] else "❌"
        report += f"{status} {result['name']}\n"
    
    return report


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
