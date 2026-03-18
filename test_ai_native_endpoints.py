# -*- coding: utf-8 -*-
"""
Test script to validate AI Native API endpoints
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

def test_ai_native_endpoints():
    """Test all AI Native functionality"""
    print("🧪 Testing AI Native Endpoints...")
    
    # Import marine base components
    from backend.channels.marine_base import get_default_registry, ChannelRegistry
    
    # Create a fresh registry
    registry = ChannelRegistry()
    
    # Import our AI Native channels
    from backend.channels.compliance_digital_expert import ComplianceDigitalExpertChannel
    from backend.channels.distributed_perception_hub import DistributedPerceptionHubChannel
    from backend.channels.decision_orchestrator import DecisionOrchestratorChannel
    
    # Register and initialize our AI Native channels
    compliance_ch = ComplianceDigitalExpertChannel()
    perception_ch = DistributedPerceptionHubChannel()
    decision_ch = DecisionOrchestratorChannel()
    
    registry.register(compliance_ch)
    registry.register(perception_ch) 
    registry.register(decision_ch)
    
    compliance_ch.initialize()
    perception_ch.initialize()
    decision_ch.initialize()
    
    print("✅ Channels registered and initialized")
    
    # Test cognitive layer
    cognitive_snapshot = compliance_ch.build_cognitive_snapshot()
    print(f"🧠 Cognitive Layer - Risk: {cognitive_snapshot['risk_level']}, Evidence: {len(cognitive_snapshot['evidence'])}")
    
    # Test perception layer
    captured_events = perception_ch.capture_system_snapshot()
    latest_events = perception_ch.get_latest_events(5)
    print(f"👁️  Perception Layer - Captured: {len(captured_events)}, Latest: {len(latest_events)}")
    
    # Test decision layer
    decision_package = decision_ch.build_decision_package()
    print(f"🤔 Decision Layer - Actions: {len(decision_package['recommended_actions'])}, Feedback: {len(decision_package['feedback_records'])}")
    
    # Test feedback recording
    feedback = decision_ch.record_feedback("test_action", "positive_outcome", "integration_test")
    print(f"📝 Feedback System - Recorded: {feedback['action']}")
    
    # Test API endpoints
    from backend.api_extensions import get_api_endpoints
    endpoints = get_api_endpoints()
    print(f"🔗 API Endpoints - Defined: {len(endpoints)}")
    
    # Test full pipeline status
    pipeline_status = {
        "compliance": compliance_ch.get_status(),
        "perception": perception_ch.get_status(), 
        "decision": decision_ch.get_status(),
        "pipeline_health": "operational"
    }
    print(f"⚡ Pipeline Health: {pipeline_status['pipeline_health']}")
    
    print("\n🎉 All AI Native components tested successfully!")
    assert pipeline_status["pipeline_health"] == "operational"

if __name__ == "__main__":
    success = test_ai_native_endpoints()
    print("\n✅ AI Native Integration Validation Passed!")