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
    assert assessment["contextual_rule"]
    assert assessment["role"] in {"both_give_way", "give_way", "stand_on"}


def test_navigation_report_contains_scene_context_and_rule18_for_restricted_target():
    from channels.intelligent_navigation import AISTarget, CollisionRisk, IntelligentNavigationChannel

    channel = IntelligentNavigationChannel({"dcpa_limit": 0.5, "tcpa_limit": 30.0})
    assert channel.initialize()
    channel.update_own_ship(latitude=31.2304, longitude=121.4737, course=5, speed=6)
    channel.add_ais_target(
        AISTarget(
            mmsi=413009999,
            latitude=31.2312,
            longitude=121.4741,
            course=8,
            speed=4,
            heading=10,
            vessel_type="Tug",
            nav_status="restricted_manoeuvrability",
        )
    )

    assessment = channel.classify_colregs_encounter(
        channel.ais_targets[0],
        CollisionRisk(
            target_mmsi=413009999,
            cpa=0.2,
            tcpa=8.0,
            risk_level="warning",
            bearing=20.0,
            range=0.4,
            dcpa_limit=0.5,
            tcpa_limit=30.0,
        ),
    )
    report = channel.generate_navigation_report()

    assert report["scene_context"]["scene_type"] in {"port_approach", "offshore_operation", "narrow_channel", "open_sea"}
    assert assessment["contextual_rule"] == "Rule 18"


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
    assert package["task_graph"]["nodes"]
    assert package["autonomy_mode"] in {"advisory", "supervised_autonomy"}


def test_cognitive_snapshot_contains_learning_state():
    import register_channels as rc
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    if registry.get("energy_efficiency") is None:
        rc.register_energy_efficiency_channel()
    if registry.get("intelligent_navigation") is None:
        rc.register_intelligent_navigation()
    if registry.get("intelligent_engine") is None:
        rc.register_intelligent_engine()
    if registry.get("compliance_digital_expert") is None:
        rc.register_compliance_digital_expert()
    if registry.get("distributed_perception_hub") is None:
        rc.register_distributed_perception_hub()
    if registry.get("decision_orchestrator") is None:
        rc.register_decision_orchestrator()

    compliance = registry.get("compliance_digital_expert")
    orchestrator = registry.get("decision_orchestrator")

    orchestrator.record_feedback("ops-monitor", "success", "test")
    snapshot = compliance.build_cognitive_snapshot()

    assert snapshot["learning_state"]["feedback_events"] >= 1
    assert "COLREGs" in snapshot["learning_state"]["rule_confidence"]
    assert snapshot["expert_cognition"]["learning"]["closed_loop_feedback"] is True


def test_perception_status_exposes_feature_fusion_tracks():
    import register_channels as rc
    from channels.intelligent_navigation import AISTarget
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    if registry.get("intelligent_navigation") is None:
        rc.register_intelligent_navigation()
    if registry.get("distributed_perception_hub") is None:
        rc.register_distributed_perception_hub()

    navigation = registry.get("intelligent_navigation")
    perception = registry.get("distributed_perception_hub")

    navigation.update_own_ship(latitude=31.2304, longitude=121.4737, course=12, speed=10)
    navigation.add_ais_target(
        AISTarget(
            mmsi=413000501,
            latitude=31.2311,
            longitude=121.4742,
            course=18,
            speed=9.8,
            heading=20,
        )
    )

    perception.capture_system_snapshot()
    status = perception.get_status()

    assert "fusion_state" in status
    assert status["fusion_state"]["active_tracks"]


def test_rcs_and_shm_channels_return_status():
    import register_channels as rc
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    if registry.get("intelligent_navigation") is None:
        rc.register_intelligent_navigation()
    if registry.get("distributed_perception_hub") is None:
        rc.register_distributed_perception_hub()
    if registry.get("rcs_control") is None:
        rc.register_rcs_control()
    if registry.get("structural_health_monitor") is None:
        rc.register_structural_health_monitor()

    rcs = registry.get("rcs_control")
    shm = registry.get("structural_health_monitor")

    rcs_status = rcs.get_status()
    shm_status = shm.get_status()

    assert rcs_status["foil_angle_deg"] >= 0
    assert shm_status["fatigue_damage_index"] >= 0


def test_openbridge_command_parser_returns_rcs_summary():
    from channels.openbridge_command_router import build_openbridge_command_result

    dashboard = {
        "rcs": {
            "foil_angle_deg": 4.2,
            "trim_tab_angle_deg": 3.1,
            "comfort_target_msdv": 0.41,
        },
        "shm": {
            "fatigue_damage_index": 0.21,
            "life_remaining_pct": 88.4,
        },
        "navigation": {"report": {"overall_status": "caution", "collision_risks": []}},
        "engine": {"health_score": 92, "alerts": []},
        "decision": {"task_graph": {"nodes": []}},
    }
    mission = {
        "task_graph": {"nodes": [{"id": "mission"}], "execution_order": ["task:1"]},
        "autonomy_mode": "supervised_autonomy",
    }

    result = build_openbridge_command_result("请切到舒适控制", dashboard, mission)

    assert result["recognized_intent"] == "set_comfort_mode"
    assert result["control_state"]["rcs"]["foil_angle_deg"] == 4.2