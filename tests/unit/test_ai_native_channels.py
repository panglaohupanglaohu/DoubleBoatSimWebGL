#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Native 新增核心模块单元测试
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "backend"))

from channels.marine_base import get_default_registry
from register_channels import (
    register_energy_efficiency_channel,
    register_intelligent_navigation,
    register_intelligent_engine,
    register_compliance_digital_expert,
    register_distributed_perception_hub,
    register_decision_orchestrator,
)


def reset_registry():
    registry = get_default_registry()
    registry._channels.clear()
    return registry


def bootstrap_all_channels():
    reset_registry()
    register_energy_efficiency_channel()
    register_intelligent_navigation()
    register_intelligent_engine()
    register_compliance_digital_expert()
    register_distributed_perception_hub()
    register_decision_orchestrator()
    return get_default_registry()


class TestComplianceDigitalExpertChannel:
    def test_registered_and_initialized(self):
        registry = bootstrap_all_channels()
        ch = registry.get("compliance_digital_expert")
        assert ch is not None
        status = ch.get_status()
        assert status["initialized"] is True
        assert status["health"] == "ok"

    def test_query_compliance_status_structure(self):
        registry = bootstrap_all_channels()
        ch = registry.get("compliance_digital_expert")
        result = ch.query_compliance_status("overall")
        assert "risk_level" in result
        assert "compliance_status" in result
        assert "recommended_actions" in result
        assert "maintenance_report" in result
        assert result["focus"] == "overall"

    def test_navigation_explanation(self):
        registry = bootstrap_all_channels()
        ch = registry.get("compliance_digital_expert")
        result = ch.explain_navigation_decision()
        assert result["focus"] == "navigation"
        assert isinstance(result["rules"], list)
        assert len(result["rules"]) >= 2


class TestDistributedPerceptionHubChannel:
    def test_capture_initial_events(self):
        registry = bootstrap_all_channels()
        ch = registry.get("distributed_perception_hub")
        status = ch.get_status()
        assert status["initialized"] is True
        assert status["event_count"] >= 3
        event_types = [evt["event_type"] for evt in status["latest_events"]]
        assert "navigation_event" in event_types
        assert "engine_event" in event_types
        assert "efficiency_event" in event_types

    def test_append_event(self):
        registry = bootstrap_all_channels()
        ch = registry.get("distributed_perception_hub")
        before = len(ch.events)
        event = ch.append_event("maintenance_event", {"severity": "warning"}, "test")
        assert len(ch.events) == before + 1
        assert event.event_type == "maintenance_event"
        assert event.source == "test"


class TestDecisionOrchestratorChannel:
    def test_build_decision_package(self):
        registry = bootstrap_all_channels()
        ch = registry.get("decision_orchestrator")
        package = ch.build_decision_package()
        assert "risk_level" in package
        assert "compliance_status" in package
        assert "recommended_actions" in package
        assert "latest_events" in package
        assert isinstance(package["latest_events"], list)

    def test_record_feedback(self):
        registry = bootstrap_all_channels()
        ch = registry.get("decision_orchestrator")
        record = ch.record_feedback("check engine", "completed", confirmed_by="operator")
        assert record["action"] == "check engine"
        assert ch.get_status()["feedback_records_count"] >= 1


def test_registry_contains_ai_native_channels():
    registry = bootstrap_all_channels()
    channels = registry.list_channels()
    assert "compliance_digital_expert" in channels
    assert "distributed_perception_hub" in channels
    assert "decision_orchestrator" in channels
