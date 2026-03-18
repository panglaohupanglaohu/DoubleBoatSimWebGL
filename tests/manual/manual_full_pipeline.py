#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Pipeline Test - AI Native 16小时优化计划半小时状态汇报证据
"""

import sys
import os
sys.path.insert(0, 'src')

# Import the register_channels module to populate the registry
import backend.register_channels as rc

# This import triggers the module-level registration in register_channels.py
# which populates the _default_registry
from backend.channels.marine_base import get_default_registry

print("Registry after import:", get_default_registry())
print("Channels:", get_default_registry().list_channels())

# Run the registration manually
print("\n=== Running registration ===")
rc.register_energy_efficiency_channel()
rc.register_intelligent_navigation()
rc.register_intelligent_engine()
rc.register_compliance_digital_expert()
rc.register_distributed_perception_hub()
rc.register_decision_orchestrator()

registry = get_default_registry()
print("\nRegistry has {} channels".format(len(registry.list_channels())))

print("\n=== AI Native Full Pipeline Test ===")

# Test cognitive snapshot
comp = registry.get('compliance_digital_expert')
if comp:
    snapshot = comp.build_cognitive_snapshot()
    print("\nCognitive Snapshot (as of {}):".format(snapshot.get("timestamp")))
    print("  Risk level: {}".format(snapshot.get("risk_level")))
    print("  Compliance status: {}".format(snapshot.get("compliance_status")))
    print("  Evidence count: {}".format(len(snapshot.get("evidence", []))))
    print("  Actions: {}".format(len(snapshot.get("recommended_actions", []))))
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
