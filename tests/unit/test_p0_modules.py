#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P0 Module Unit Tests - AI Native 16小时优化计划
"""

from backend.channels.marine_base import get_default_registry, create_registry
from backend.channels.energy_efficiency_manager import EnergyEfficiencyChannel
from backend.channels.intelligent_navigation import IntelligentNavigationChannel
from backend.channels.intelligent_engine import IntelligentEngineChannel
from backend.channels.compliance_digital_expert import ComplianceDigitalExpertChannel
from backend.channels.distributed_perception_hub import DistributedPerceptionHubChannel
from backend.channels.decision_orchestrator import DecisionOrchestratorChannel

def test_compliance_digital_expert():
    """测试 ComplianceDigitalExpertChannel"""
    registry = get_default_registry()
    
    # Register and initialize
    registry.register(ComplianceDigitalExpertChannel())
    channel = registry.get('compliance_digital_expert')
    channel.initialize()
    
    # Test get_status
    status = channel.get_status()
    assert status['name'] == 'compliance_digital_expert', "Channel name mismatch"
    assert status['initialized'] == True, "Channel not initialized"
    assert status['health'] == 'ok', "Channel not healthy"
    
    # Test build_cognitive_snapshot
    snapshot = channel.build_cognitive_snapshot()
    assert 'risk_level' in snapshot, "Missing risk_level"
    assert 'compliance_status' in snapshot, "Missing compliance_status"
    assert 'evidence' in snapshot, "Missing evidence"
    assert 'recommended_actions' in snapshot, "Missing recommended_actions"
    
    # Test query_compliance_status
    result = channel.query_compliance_status("navigation")
    assert 'risk_level' in result, "Missing risk_level in query result"
    
    print("✅ ComplianceDigitalExpertChannel tests passed")
    print(f"   Risk level: {snapshot.get('risk_level')}")
    print(f"   Evidence count: {len(snapshot.get('evidence', []))}")

def test_distributed_perception_hub():
    """测试 DistributedPerceptionHubChannel"""
    registry = get_default_registry()
    
    # Register and initialize
    registry.register(DistributedPerceptionHubChannel(config={'max_events': 500}))
    channel = registry.get('distributed_perception_hub')
    channel.initialize()
    
    # Test get_status
    status = channel.get_status()
    assert status['name'] == 'distributed_perception_hub', "Channel name mismatch"
    assert status['initialized'] == True, "Channel not initialized"
    assert status['health'] == 'ok', "Channel not healthy"
    
    # Capture events - need other channels to be registered first
    registry.register(EnergyEfficiencyChannel())
    registry.register(IntelligentNavigationChannel())
    registry.register(IntelligentEngineChannel())
    
    # Initialize them too
    for name in ['energy_efficiency', 'intelligent_navigation', 'intelligent_engine']:
        ch = registry.get(name)
        ch.initialize()
    
    captured = channel.capture_system_snapshot()
    print(f"   Captured {len(captured)} events")
    for evt in captured:
        print(f"     - [{evt.event_type}] from {evt.source}")
    
    # Test get_latest_events
    events = channel.get_latest_events(5)
    assert len(events) <= 5, "Should return max 5 events"
    assert len(events) > 0, "Should have captured events"
    
    print("✅ DistributedPerceptionHubChannel tests passed")
    print(f"   Total events in hub: {len(channel.events)}")
    print(f"   Fusion events: {len([e for e in channel.events if 'fusion' in e.event_type])}")

def test_decision_orchestrator():
    """测试 DecisionOrchestratorChannel"""
    registry = get_default_registry()
    
    # Register and initialize
    registry.register(DecisionOrchestratorChannel())
    channel = registry.get('decision_orchestrator')
    channel.initialize()
    
    # Test get_status
    status = channel.get_status()
    assert status['name'] == 'decision_orchestrator', "Channel name mismatch"
    assert status['initialized'] == True, "Channel not initialized"
    assert status['health'] == 'ok', "Channel not healthy"
    
    # Test build_decision_package
    package = channel.build_decision_package()
    assert 'risk_level' in package, "Missing risk_level"
    assert 'recommended_actions' in package, "Missing recommended_actions"
    
    # Test record_feedback
    feedback = channel.record_feedback("test_action", "success", "test_user")
    assert 'action' in feedback, "Missing action in feedback"
    assert feedback['action'] == 'test_action', "Feedback action mismatch"
    
    print("✅ DecisionOrchestratorChannel tests passed")
    print(f"   Risk level: {package.get('risk_level')}")
    print(f"   Feedback records: {len(package.get('feedback_records', []))}")

def test_full_pipeline():
    """测试完整AI Native管道"""
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
    
    print(f"Registry has {len(registry.list_channels())} channels")
    
    # Test cognitive snapshot
    comp = registry.get('compliance_digital_expert')
    snapshot = comp.build_cognitive_snapshot()
    assert snapshot['risk_level'] in ['low', 'medium', 'high', 'unknown'], "Invalid risk level"
    
    # Test perception capture
    perception = registry.get('distributed_perception_hub')
    captured = perception.capture_system_snapshot()
    assert len(captured) >= 3, f"Should capture at least 3 core events, got {len(captured)}"
    
    # Test decision package
    decision = registry.get('decision_orchestrator')
    package = decision.build_decision_package()
    assert package['risk_level'] in ['low', 'medium', 'high', 'unknown'], "Invalid risk level in package"
    
    print("✅ Full pipeline test passed")
    print(f"   Last risk level: {snapshot.get('risk_level')}")
    print(f"   Last compliance status: {snapshot.get('compliance_status')}")

if __name__ == "__main__":
    print("=== AI Native P0 Module Unit Tests ===\n")
    
    try:
        test_compliance_digital_expert()
        print()
        test_distributed_perception_hub()
        print()
        test_decision_orchestrator()
        print()
        test_full_pipeline()
        
        print("\n=== All Tests Passed ===")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
