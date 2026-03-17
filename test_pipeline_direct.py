#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct pipeline test - AI Native 16小时优化计划半小时状态汇报证据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from backend.channels.marine_base import get_default_registry
from backend.channels.energy_efficiency_manager import EnergyEfficiencyChannel
from backend.channels.intelligent_navigation import IntelligentNavigationChannel
from backend.channels.intelligent_engine import IntelligentEngineChannel
from backend.channels.compliance_digital_expert import ComplianceDigitalExpertChannel
from backend.channels.distributed_perception_hub import DistributedPerceptionHubChannel
from backend.channels.decision_orchestrator import DecisionOrchestratorChannel

# Create a fresh registry
registry = get_default_registry()

# Register channels
registry.register(EnergyEfficiencyChannel())
registry.register(IntelligentNavigationChannel())
registry.register(IntelligentEngineChannel())
registry.register(ComplianceDigitalExpertChannel())
registry.register(DistributedPerceptionHubChannel())
registry.register(DecisionOrchestratorChannel())

# Initialize all
for name in registry.list_channels():
    ch = registry.get(name)
    if ch:
        ch.initialize()

print("=== AI Native Full Pipeline Test ===")
print("Registry has {} channels\n".format(len(registry.list_channels())))

# Test cognitive snapshot
comp = registry.get('compliance_digital_expert')
if comp:
    snapshot = comp.build_cognitive_snapshot()
    print("Cognitive Snapshot (as of {}):".format(snapshot.get("timestamp")))
    print("  Risk level: {}".format(snapshot.get("risk_level")))
    print("  Compliance status: {}".format(snapshot.get("compliance_status")))
    print("  Evidence count: {}".format(len(snapshot.get("evidence", []))))
    print("  Recommended actions: {}".format(len(snapshot.get("recommended_actions", []))))
else:
    print("ERROR: compliance_digital_expert not found")

# Test perception capture
perception = registry.get('distributed_perception_hub')
if perception:
    captured = perception.capture_system_snapshot()
    print("\nPerception capture: {} events".format(len(captured)))
    for evt in captured[:5]:
        print("  - [{}] {} (conf: {})".format(evt.event_type, evt.source, evt.confidence))
    print("  Total events in hub: {}".format(len(perception.events)))
    print("  Fusion events: {}".format(len([e for e in perception.events if "fusion" in e.event_type])))
else:
    print("ERROR: distributed_perception_hub not found")

# Test decision package
decision = registry.get('decision_orchestrator')
if decision:
    package = decision.build_decision_package()
    print("\nDecision package:")
    print("  Risk level: {}".format(package.get("risk_level")))
    print("  Recommended actions: {} items".format(len(package.get("recommended_actions", []))))
else:
    print("ERROR: decision_orchestrator not found")

print("\n=== Pipeline Test Complete ===")
