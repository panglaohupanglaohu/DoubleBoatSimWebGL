#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test channel registration and pipeline
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== Channel Registration Test ===")

# Import the module-level register functions
import src.backend.register_channels as rc

# Check the registry before anything
from src.backend.channels.marine_base import get_default_registry
registry = get_default_registry()

def test_channels():
    registry = get_default_registry()
    
    print("Registry channels:", registry.list_channels())
    print()
    
    # Test each channel
    test_channels = [
        'compliance_digital_expert',
        'distributed_perception_hub', 
        'decision_orchestrator'
    ]
    
    for name in test_channels:
        ch = registry.get(name)
        if ch:
            status = ch.get_status()
            print(f"{name}:")
            print(f"  - Health: {status.get('health')}")
            print(f"  - Initialized: {status.get('initialized', 'N/A')}")
            
            if name == 'compliance_digital_expert':
                snapshot = ch.build_cognitive_snapshot()
                print(f"  - Risk level: {snapshot.get('risk_level')}")
                print(f"  - Evidence count: {len(snapshot.get('evidence', []))}")
            elif name == 'distributed_perception_hub':
                captured = ch.capture_system_snapshot()
                print(f"  - Captured events: {len(captured)}")
                print(f"  - Total events: {len(ch.events)}")
                print(f"  - Fusion events: {len([e for e in ch.events if 'fusion' in e.event_type])}")
            elif name == 'decision_orchestrator':
                package = ch.build_decision_package()
                print(f"  - Risk level: {package.get('risk_level')}")
        else:
            print(f"{name}: NOT FOUND")
        print()

if __name__ == "__main__":
    # Run registration
    rc.register_energy_efficiency_channel()
    rc.register_intelligent_navigation()
    rc.register_intelligent_engine()
    rc.register_compliance_digital_expert()
    rc.register_distributed_perception_hub()
    rc.register_decision_orchestrator()
    
    print("\n=== Testing Registered Channels ===")
    test_channels()
    
    print("=== Pipeline Test Complete ===")
