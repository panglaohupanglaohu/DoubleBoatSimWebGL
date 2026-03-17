#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai_native_arch.py - AI Native 架构验证与概览

快速查看当前 AI Native 代码架构
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

def print_header(title):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def print_subheader(title):
    print(f"\n--- {title} ---\n")

def show_storage_modules():
    """显示存储模块"""
    print_header("STORAGE MODULES")
    
    from backend.storage.event_store import EventStore, JSONLStore, SQLiteStore
    from backend.storage.cloud_sync import CloudStorageAdapter, S3CompatibleAdapter, FeishuAdapter, LocalFileAdapter
    from backend.storage.data_lakehouse import DataLakehouse, create_lakehouse
    
    print_subheader("Event Store")
    print("  EventStore (base class)")
    print("  ├── JSONLStore")
    print("  ├── SQLiteStore")
    print("  └── ParquetStore (placeholder)")
    
    print_subheader("Cloud Sync")
    print("  CloudStorageAdapter (base class)")
    print("  ├── S3CompatibleAdapter")
    print("  ├── FeishuAdapter")
    print("  └── LocalFileAdapter")
    
    print_subheader("Data Lakehouse")
    print("  DataLakehouse class")
    print("  └─ Features:")
    print("      - SQLite/JSONL/Parquet local storage")
    print("      - S3/Feishu cloud sync")
    print("      - Event buffering")
    print("      - Time-based queries")

def show_channel_modules():
    """显示通道模块"""
    print_header("CHANNEL MODULES")
    
    from backend.channels.compliance_digital_expert import ComplianceDigitalExpertChannel
    from backend.channels.distributed_perception_hub import DistributedPerceptionHubChannel
    from backend.channels.decision_orchestrator import DecisionOrchestratorChannel
    from backend.channels.energy_efficiency_manager import EnergyEfficiencyChannel
    from backend.channels.intelligent_navigation import IntelligentNavigationChannel
    from backend.channels.intelligent_engine import IntelligentEngineChannel
    
    print_subheader("L3: Decision Orchestrator")
    print("  Responsibilities:")
    print("    - Aggregate cognition, perception, execution states")
    print("    - Generate unified risk summary, maintenance advice, decision package")
    print("    - Support human feedback loop recording")
    
    print_subheader("L2: Distributed Perception Hub")
    print("  Responsibilities:")
    print("    - Multi-source perception fusion (NMEA2000/AIS/WorldMonitor/Weather)")
    print("    - Risk correlation (collision/mechanical/compliance/weather)")
    print("    - Event stream capture + fusion")
    
    print_subheader("L1: Compliance Digital Expert")
    print("  Responsibilities:")
    print("    - COLREGs rules knowledge base")
    print("    - CCS Intelligent Ship standards")
    print("    - Unified cognitive output interface")
    
    print_subheader("L0: Execution Nodes")
    print("    - IntelligentNavigation (CPA/TCPA + COLREGs risk assessment)")
    print("    - IntelligentEngine (engine health monitoring + fault diagnosis)")
    print("    - EnergyEfficiencyManager (EEXI/CII/SEEMP compliance)")
    print("    - NMEA2000Parser (NMEA2000 message parsing)")

def show_api_endpoints():
    """显示 API 端点"""
    print_header("AI NATIVE API ENDPOINTS")
    
    endpoints = [
        "/api/v1/ai-native/compliance/status",
        "/api/v1/ai-native/compliance/cognitive-snapshot",
        "/api/v1/ai-native/perception/events",
        "/api/v1/ai-native/perception/capture-snapshot",
        "/api/v1/ai-native/decision/package",
        "/api/v1/ai-native/decision/feedback",
        "/api/v1/ai-native/status/full-pipeline",
    ]
    
    for endpoint in endpoints:
        print(f"  ✓ {endpoint}")

def show_test_results():
    """显示测试结果"""
    print_header("TEST RESULTS")
    
    import subprocess
    result = subprocess.run(
        ["python", "test_p0_modules.py"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    output = result.stdout + result.stderr
    for line in output.split('\n'):
        if '✅' in line or '❌' in line or 'Tests Passed' in line or 'Tests failed' in line:
            print(f"  {line}")
    
    result2 = subprocess.run(
        ["python", "test_data_lakehouse.py"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    output2 = result2.stdout + result2.stderr
    for line in output2.split('\n'):
        if '✅' in line or '❌' in line or 'Tests Passed' in line or 'Tests failed' in line:
            print(f"  {line}")

if __name__ == "__main__":
    print_header("AI NATIVE ARCHITECTURE OVERVIEW")
    print("\nCurrent Date:", __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("\nThis script provides a quick overview of the AI Native code architecture.")
    
    show_channel_modules()
    show_storage_modules()
    show_api_endpoints()
    show_test_results()
    
    print_header("ARCHITECTURE SUMMARY")
    print("""
L3: Decision Orchestrator (决策编排)
    └─ Aggregates cognition + perception + execution states
       Generates unified risk summary, maintenance advice, decision package

L2: Distributed Perception Hub (感知网络) + Data Lakehouse (数据湖仓)
    └─ Multi-source fusion (NMEA2000/AIS/Weather)
    └─Risk correlation + Event persistence + Cloud sync

L1: Compliance Digital Expert (合规专家)
    └─ COLREGs knowledge base + Unified cognitive output

L0: Execution Nodes (执行节点)
    └─ IntelligentNavigation + IntelligentEngine + EnergyEfficiencyManager
    └─ NMEA2000Parser (data source)

Features:
  ✓ SQLite/JSONL/Parquet local storage
  ✓ S3/Feishu cloud sync
  ✓ Event buffering
  ✓ Time-based queries
  ✓ No Hadoop required (lightweight architecture)
    """)
    
    print("\n" + "=" * 80)
    print(" AI Native Architecture Overview Complete")
    print("=" * 80)
    print()
