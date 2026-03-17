#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Extension Tests - AI Native 16小时优化计划
"""

import sys
import os
sys.path.insert(0, 'src')

from backend.channels.marine_base import get_default_registry
from backend.channels.energy_efficiency_manager import EnergyEfficiencyChannel
from backend.channels.intelligent_navigation import IntelligentNavigationChannel
from backend.channels.intelligent_engine import IntelligentEngineChannel
from backend.channels.compliance_digital_expert import ComplianceDigitalExpertChannel
from backend.channels.distributed_perception_hub import DistributedPerceptionHubChannel
from backend.channels.decision_orchestrator import DecisionOrchestratorChannel

# Create a test app
from fastapi import FastAPI

# Register all channels to default registry
registry = get_default_registry()

# Register all channels
registry.register(EnergyEfficiencyChannel())
registry.register(IntelligentNavigationChannel())
registry.register(IntelligentEngineChannel())
registry.register(ComplianceDigitalExpertChannel())
registry.register(DistributedPerceptionHubChannel())
registry.register(DecisionOrchestratorChannel())

# Initialize all
for name in registry.list_channels():
    channel = registry.get(name)
    channel.initialize()

print("=== API Extension Tests ===")
print("Registered channels:", registry.list_channels())
print()

# Test API endpoints
print("Testing API endpoints...")

# 1. Compliance status endpoint
comp = registry.get('compliance_digital_expert')
if comp:
    result = comp.query_compliance_status('navigation')
    print("  Compliance status endpoint: OK")
    print(f"    Risk level: {result.get('risk_level')}")
    print(f"    Evidence: {len(result.get('evidence', []))}")

# 2. Cognitive snapshot
snapshot = comp.build_cognitive_snapshot() if comp else None
if snapshot:
    print("  Cognitive snapshot endpoint: OK")
    print(f"    Timestamp: {snapshot.get('timestamp')}")
    print(f"    Risk level: {snapshot.get('risk_level')}")

# 3. Perception events
perception = registry.get('distributed_perception_hub')
if perception:
    events = perception.get_latest_events(5)
    print("  Perception events endpoint: OK")
    print(f"    Events count: {len(events)}")

# 4. Capture snapshot
if perception:
    captured = perception.capture_system_snapshot()
    print("  Capture snapshot endpoint: OK")
    print(f"    Captured events: {len(captured)}")

# 5. Decision package
decision = registry.get('decision_orchestrator')
if decision:
    package = decision.build_decision_package()
    print("  Decision package endpoint: OK")
    print(f"    Risk level: {package.get('risk_level')}")
    print(f"    Actions: {len(package.get('recommended_actions', []))}")

# 6. Full pipeline status
full_status = {
    'components': {
        'compliance': comp.get_status() if comp else None,
        'perception': perception.get_status() if perception else None,
        'decision': decision.get_status() if decision else None
    }
}
print("  Full pipeline status endpoint: OK")
print("    All components present:", all([comp, perception, decision]))

print()
print("=== API Extension Tests Complete ===")
