import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "src", "backend"))


def test_navigation_colregs_assessment_contains_rule_and_role():
    from channels.intelligent_navigation import AISTarget, CollisionRisk, IntelligentNavigationChannel

    channel = IntelligentNavigationChannel({"dcpa_limit": 0.5, "tcpa_limit": 30.0})
    assert channel.initialize()
    channel.update_own_ship(latitude=31.2304, longitude=121.4737, course=0, speed=12)
    target = AISTarget(
        mmsi=413000888,
        latitude=31.2320,
        longitude=121.4737,
        course=180,
        speed=11,
        heading=180,
    )
    channel.add_ais_target(target)

    assessment = channel.classify_colregs_encounter(
        target,
        CollisionRisk(
            target_mmsi=413000888,
            cpa=0.12,
            tcpa=5.0,
            risk_level="warning",
            bearing=0.0,
            range=0.18,
            dcpa_limit=0.5,
            tcpa_limit=30.0,
        ),
    )

    assert assessment["rule"]
    assert assessment["role"] in {"both_give_way", "give_way", "stand_on"}


def test_datalakehouse_query_flushes_buffer_before_read():
    import tempfile

    from storage.data_lakehouse import create_lakehouse

    with tempfile.TemporaryDirectory() as temp_dir:
        lakehouse = create_lakehouse(
            {
                "store_type": "sqlite",
                "store_config": {"db_path": os.path.join(temp_dir, "events.db")},
                "buffer_max_size": 10,
            }
        )
        lakehouse.save_event(
            {
                "id": "evt-buffered",
                "timestamp": "2026-03-18T08:00:00",
                "event_type": "decision_package_event",
                "source": "decision_orchestrator",
                "payload": {"risk_level": "medium"},
                "confidence": 1.0,
            }
        )

        events = lakehouse.query_events(limit=5)
        assert any(
            event.get("event_type") == "decision_package_event"
            and event.get("source") == "decision_orchestrator"
            and event.get("payload", {}).get("risk_level") == "medium"
            for event in events
        )


def test_decision_package_contains_action_plan_and_mission_brief():
    import register_channels as rc
    from channels.marine_base import get_default_registry

    rc.register_energy_efficiency_channel()
    rc.register_intelligent_navigation()
    rc.register_intelligent_engine()
    rc.register_compliance_digital_expert()
    rc.register_distributed_perception_hub()
    rc.register_decision_orchestrator()

    registry = get_default_registry()
    orchestrator = registry.get("decision_orchestrator")

    package = orchestrator.build_decision_package()
    assert package["mission_brief"]
    assert package["action_plan"]
    assert package["autonomy_mode"] in {"advisory", "supervised_autonomy"}