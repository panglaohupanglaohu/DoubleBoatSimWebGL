#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化测试运行脚本 (不依赖 pytest)

用法:
    python run_tests.py [选项]
    
选项:
    --all       运行所有测试 (默认)
    --api       只运行 API 测试
    --report    生成测试报告
"""

import requests
import sys
import time
from datetime import datetime
from typing import Dict, List, Any


BASE_URL = "http://localhost:8080"
FRONTEND_URL = "http://localhost:5173"


class TestResult:
    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration = 0.0


def test_api_channels():
    """测试 Channels API."""
    results = []
    
    # Test 1: API 可访问
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/api/v1/channels", timeout=5)
        passed = response.status_code == 200
        results.append(TestResult(
            "Channels API 可访问",
            passed,
            f"Status: {response.status_code}" if not passed else ""
        ))
    except Exception as e:
        results.append(TestResult("Channels API 可访问", False, str(e)))
    
    # Test 2: 响应格式
    try:
        response = requests.get(f"{BASE_URL}/api/v1/channels", timeout=5)
        data = response.json()
        passed = "channels" in data and isinstance(data["channels"], list)
        results.append(TestResult(
            "Channels 响应格式",
            passed,
            f"Missing 'channels' key" if not passed else ""
        ))
    except Exception as e:
        results.append(TestResult("Channels 响应格式", False, str(e)))
    
    # Test 3: Energy Efficiency Channel
    try:
        response = requests.get(f"{BASE_URL}/api/v1/channels", timeout=5)
        data = response.json()
        names = [ch["name"] for ch in data["channels"]]
        passed = "energy_efficiency" in names
        results.append(TestResult(
            "EnergyEfficiencyChannel 已注册",
            passed,
            f"Available: {names}" if not passed else ""
        ))
    except Exception as e:
        results.append(TestResult("EnergyEfficiencyChannel 已注册", False, str(e)))
    
    # Test 4: Intelligent Navigation Channel
    try:
        response = requests.get(f"{BASE_URL}/api/v1/channels", timeout=5)
        data = response.json()
        names = [ch["name"] for ch in data["channels"]]
        passed = "intelligent_navigation" in names
        results.append(TestResult(
            "IntelligentNavigationChannel 已注册",
            passed,
            f"Available: {names}" if not passed else ""
        ))
    except Exception as e:
        results.append(TestResult("IntelligentNavigationChannel 已注册", False, str(e)))
    
    # Test 5: Channel 健康状态
    try:
        response = requests.get(f"{BASE_URL}/api/v1/channels", timeout=5)
        data = response.json()
        all_healthy = all(ch.get("health") == "ok" for ch in data["channels"])
        results.append(TestResult(
            "所有 Channel 健康",
            all_healthy,
            f"Some channels unhealthy" if not all_healthy else ""
        ))
    except Exception as e:
        results.append(TestResult("所有 Channel 健康", False, str(e)))
    
    return results


def test_api_sensors():
    """测试 Sensors API."""
    results = []
    
    # Test 1: API 可访问
    try:
        response = requests.get(f"{BASE_URL}/api/v1/sensors", timeout=5)
        passed = response.status_code == 200
        results.append(TestResult(
            "Sensors API 可访问",
            passed,
            f"Status: {response.status_code}" if not passed else ""
        ))
    except Exception as e:
        results.append(TestResult("Sensors API 可访问", False, str(e)))
    
    # Test 2: 响应格式
    try:
        response = requests.get(f"{BASE_URL}/api/v1/sensors", timeout=5)
        data = response.json()
        passed = "sensors" in data and isinstance(data["sensors"], list)
        results.append(TestResult(
            "Sensors 响应格式",
            passed,
            "" if passed else "Missing 'sensors' key"
        ))
    except Exception as e:
        results.append(TestResult("Sensors 响应格式", False, str(e)))
    
    # Test 3: 传感器数量
    try:
        response = requests.get(f"{BASE_URL}/api/v1/sensors", timeout=5)
        data = response.json()
        count = len(data["sensors"])
        passed = count >= 4
        results.append(TestResult(
            f"传感器数量 >= 4 (实际：{count})",
            passed,
            f"Only {count} sensors" if not passed else ""
        ))
    except Exception as e:
        results.append(TestResult("传感器数量 >= 4", False, str(e)))
    
    return results


def test_frontend():
    """测试前端页面."""
    results = []
    
    # Test 1: 数字孪生页面可访问
    try:
        response = requests.get(f"{FRONTEND_URL}/digital-twin.html", timeout=5)
        passed = response.status_code == 200
        results.append(TestResult(
            "数字孪生页面可访问",
            passed,
            f"Status: {response.status_code}" if not passed else ""
        ))
    except Exception as e:
        results.append(TestResult("数字孪生页面可访问", False, str(e)))
    
    # Test 2: LLM 配置页面可访问
    try:
        response = requests.get(f"{FRONTEND_URL}/poseidon-config.html", timeout=5)
        passed = response.status_code == 200
        results.append(TestResult(
            "LLM 配置页面可访问",
            passed,
            f"Status: {response.status_code}" if not passed else ""
        ))
    except Exception as e:
        results.append(TestResult("LLM 配置页面可访问", False, str(e)))
    
    # Test 3: Bridge Chat 组件存在
    try:
        response = requests.get(f"{FRONTEND_URL}/digital-twin.html", timeout=5)
        passed = "simple-bridge-chat.js" in response.text or "bridge-chat" in response.text.lower()
        results.append(TestResult(
            "Bridge Chat 组件存在",
            passed,
            "Component not found" if not passed else ""
        ))
    except Exception as e:
        results.append(TestResult("Bridge Chat 组件存在", False, str(e)))
    
    return results


def test_performance():
    """测试性能."""
    results = []
    
    # Test 1: API 响应时间
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/v1/sensors", timeout=5)
        elapsed = time.time() - start
        passed = elapsed < 1.0
        results.append(TestResult(
            f"API 响应时间 < 1s (实际：{elapsed:.3f}s)",
            passed,
            f"Too slow: {elapsed:.3f}s" if not passed else ""
        ))
    except Exception as e:
        results.append(TestResult("API 响应时间 < 1s", False, str(e)))
    
    # Test 2: 前端响应时间
    try:
        start = time.time()
        response = requests.get(f"{FRONTEND_URL}/digital-twin.html", timeout=5)
        elapsed = time.time() - start
        passed = elapsed < 2.0
        results.append(TestResult(
            f"前端响应时间 < 2s (实际：{elapsed:.3f}s)",
            passed,
            f"Too slow: {elapsed:.3f}s" if not passed else ""
        ))
    except Exception as e:
        results.append(TestResult("前端响应时间 < 2s", False, str(e)))
    
    return results


def run_all_tests():
    """运行所有测试."""
    print("=" * 60)
    print("🧪 自动化测试开始")
    print("=" * 60)
    print()
    
    all_results = []
    
    # API 测试
    print("📡 测试 API...")
    all_results.extend(test_api_channels())
    all_results.extend(test_api_sensors())
    
    # 前端测试
    print("🌐 测试前端...")
    all_results.extend(test_frontend())
    
    # 性能测试
    print("⚡ 测试性能...")
    all_results.extend(test_performance())
    
    # 打印结果
    print()
    print("=" * 60)
    print("📊 测试结果")
    print("=" * 60)
    
    passed = sum(1 for r in all_results if r.passed)
    failed = len(all_results) - passed
    
    for result in all_results:
        status = "✅" if result.passed else "❌"
        print(f"{status} {result.name}")
        if result.message:
            print(f"   └─ {result.message}")
    
    print()
    print("=" * 60)
    print(f"总计：{len(all_results)} 个测试")
    print(f"通过：{passed} ✅")
    print(f"失败：{failed} ❌")
    print(f"通过率：{passed/len(all_results)*100:.1f}%")
    print("=" * 60)
    
    # 生成报告
    generate_report(all_results)
    
    return failed == 0


def generate_report(results: List[TestResult]):
    """生成测试报告."""
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    
    report = f"""# 🧪 自动化测试报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 测试概览

| 指标 | 数值 |
|------|------|
| 测试总数 | {len(results)} |
| 通过 | {passed} ✅ |
| 失败 | {failed} ❌ |
| 通过率 | {passed/len(results)*100:.1f}% |

## 📋 详细结果

"""
    
    for result in results:
        status = "✅" if result.passed else "❌"
        report += f"### {status} {result.name}\n\n"
        if result.message:
            report += f"```\n{result.message}\n```\n\n"
    
    # 写入文件
    report_path = "/Users/panglaohu/Downloads/DoubleBoatClawSystem/tests/reports/automation_report.md"
    import os
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n📄 测试报告已保存：{report_path}")


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
