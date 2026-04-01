# -*- coding: utf-8 -*-
"""Unit tests for the dual Agent-Set architecture:
  - CoordinationBus & Protocol
  - AgentSet base class
  - ShoreSupervisionSet
  - ShipboardExecutionSet
  - AgentSetCoordinator
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "backend"))

import pytest
from channels.agent_set_protocol import (
    CoordinationBus,
    CoordinationEnvelope,
    CoordinationMessageType,
    EnvelopeDirection,
    create_coordination_bus,
)
from channels.agent_set_base import AgentSet
from channels.shore_supervision_set import ShoreSupervisionSet, SupervisionCycleResult
from channels.shipboard_execution_set import (
    ShipboardExecutionSet,
    ExecutionCycleResult,
    ExecutionMode,
)
from channels.agent_set_coordinator import AgentSetCoordinator
from channels.marine_base import MarineChannel, ChannelStatus


# ═══════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════

class StubChannel(MarineChannel):
    """Minimal stub for testing agent sets."""
    def __init__(self, name="stub", health="ok", extra_status=None):
        super().__init__()
        self.name = name
        self._initialized = False
        self._extra = extra_status or {}
        self._desired_health = health

    def initialize(self) -> bool:
        self._initialized = True
        if self._desired_health == "ok":
            self._set_health(ChannelStatus.OK, "stub ready")
        elif self._desired_health == "warn":
            self._set_health(ChannelStatus.WARN, "stub warn")
        elif self._desired_health == "error":
            self._set_health(ChannelStatus.ERROR, "stub error")
        return True

    def get_status(self):
        base = {"name": self.name, "health": self._desired_health}
        base.update(self._extra)
        return base

    def shutdown(self) -> bool:
        self._initialized = False
        return True


# ═══════════════════════════════════════════════════════════
# CoordinationBus Tests
# ═══════════════════════════════════════════════════════════

class TestCoordinationBus:
    def test_create_bus(self):
        bus = create_coordination_bus(max_size=128)
        assert bus.pending_downlink() == 0
        assert bus.pending_uplink() == 0

    def test_post_downlink(self):
        bus = CoordinationBus(max_size=64)
        env = CoordinationEnvelope(direction=EnvelopeDirection.DOWNLINK, payload={"x": 1})
        bus.post(env)
        assert bus.pending_downlink() == 1
        assert bus.pending_uplink() == 0

    def test_post_uplink(self):
        bus = CoordinationBus(max_size=64)
        env = CoordinationEnvelope(direction=EnvelopeDirection.UPLINK, payload={"y": 2})
        bus.post(env)
        assert bus.pending_uplink() == 1
        assert bus.pending_downlink() == 0

    def test_poll_downlink(self):
        bus = CoordinationBus()
        for i in range(5):
            bus.post(CoordinationEnvelope(
                direction=EnvelopeDirection.DOWNLINK, payload={"i": i}
            ))
        polled = bus.poll_downlink(limit=3)
        assert len(polled) == 3
        assert bus.pending_downlink() == 2
        assert polled[0].payload == {"i": 0}

    def test_poll_uplink(self):
        bus = CoordinationBus()
        for i in range(4):
            bus.post(CoordinationEnvelope(
                direction=EnvelopeDirection.UPLINK, payload={"j": i}
            ))
        polled = bus.poll_uplink(limit=10)
        assert len(polled) == 4
        assert bus.pending_uplink() == 0

    def test_stats(self):
        bus = CoordinationBus()
        bus.post(CoordinationEnvelope(direction=EnvelopeDirection.DOWNLINK))
        bus.post(CoordinationEnvelope(direction=EnvelopeDirection.UPLINK))
        bus.poll_downlink(1)
        stats = bus.stats()
        assert stats["downlink_posted"] == 1
        assert stats["uplink_posted"] == 1
        assert stats["downlink_polled"] == 1
        assert stats["downlink_pending"] == 0
        assert stats["uplink_pending"] == 1

    def test_clear(self):
        bus = CoordinationBus()
        bus.post(CoordinationEnvelope(direction=EnvelopeDirection.DOWNLINK))
        bus.post(CoordinationEnvelope(direction=EnvelopeDirection.UPLINK))
        bus.clear()
        assert bus.pending_downlink() == 0
        assert bus.pending_uplink() == 0
        assert bus.stats()["downlink_posted"] == 0

    def test_bounded_deque_drops(self):
        bus = CoordinationBus(max_size=2)
        for i in range(4):
            bus.post(CoordinationEnvelope(
                direction=EnvelopeDirection.DOWNLINK, payload={"i": i}
            ))
        assert bus.pending_downlink() == 2
        assert bus.stats()["dropped"] == 2
        polled = bus.poll_downlink(10)
        assert polled[0].payload == {"i": 2}


class TestCoordinationEnvelope:
    def test_defaults(self):
        env = CoordinationEnvelope()
        assert len(env.envelope_id) == 12
        assert env.direction == EnvelopeDirection.DOWNLINK
        assert env.msg_type == CoordinationMessageType.HEARTBEAT
        assert env.priority == 3

    def test_to_dict(self):
        env = CoordinationEnvelope(
            msg_type=CoordinationMessageType.POLICY_UPDATE,
            sender_set="shore",
            payload={"key": "val"},
        )
        d = env.to_dict()
        assert d["msg_type"] == "policy_update"
        assert d["direction"] == "shore_to_ship"
        assert d["payload"] == {"key": "val"}

    def test_custom_fields(self):
        env = CoordinationEnvelope(
            direction=EnvelopeDirection.UPLINK,
            msg_type=CoordinationMessageType.ANOMALY_ALERT,
            sender_set="ship",
            target_set="shore",
            payload={"alert": True},
            priority=1,
            ttl_seconds=60.0,
        )
        assert env.direction == EnvelopeDirection.UPLINK
        assert env.priority == 1
        assert env.ttl_seconds == 60.0


class TestMessageTypes:
    def test_all_types_exist(self):
        expected = {
            "POLICY_UPDATE", "COMPLIANCE_CONSTRAINT", "VOYAGE_DIRECTIVE",
            "SECURITY_ADVISORY", "OVERRIDE_COMMAND", "EXECUTION_STATE",
            "TELEMETRY_REPORT", "ANOMALY_ALERT", "DECISION_FEEDBACK",
            "EVIDENCE_UPLOAD", "HEARTBEAT", "ACK", "HANDSHAKE",
        }
        actual = {t.name for t in CoordinationMessageType}
        assert actual == expected

    def test_direction_values(self):
        assert EnvelopeDirection.DOWNLINK.value == "shore_to_ship"
        assert EnvelopeDirection.UPLINK.value == "ship_to_shore"


# ═══════════════════════════════════════════════════════════
# AgentSet Base Tests
# ═══════════════════════════════════════════════════════════

class TestAgentSetBase:
    def test_add_channel(self):
        bus = create_coordination_bus()
        agent_set = AgentSet(coordination_bus=bus)
        agent_set.set_id = "test"
        ch = StubChannel(name="ch1")
        assert agent_set.add_channel(ch) is True
        assert "ch1" in agent_set.list_members()

    def test_add_invalid_channel(self):
        agent_set = AgentSet()
        agent_set.set_id = "test"
        assert agent_set.add_channel(None) is False

    def test_remove_channel(self):
        agent_set = AgentSet()
        agent_set.set_id = "test"
        ch = StubChannel(name="ch1")
        agent_set.add_channel(ch)
        assert agent_set.remove_channel("ch1") is True
        assert agent_set.remove_channel("nonexistent") is False
        assert "ch1" not in agent_set.list_members()

    def test_get_channel(self):
        agent_set = AgentSet()
        agent_set.set_id = "test"
        ch = StubChannel(name="ch1")
        agent_set.add_channel(ch)
        assert agent_set.get_channel("ch1") is ch
        assert agent_set.get_channel("nope") is None

    def test_initialize_all_members(self):
        bus = create_coordination_bus()
        agent_set = AgentSet(coordination_bus=bus)
        agent_set.set_id = "test"
        for i in range(3):
            agent_set.add_channel(StubChannel(name=f"ch{i}"))
        assert agent_set.initialize() is True
        assert agent_set._initialized is True
        for ch in agent_set._members.values():
            assert ch._initialized is True

    def test_get_status_aggregate(self):
        bus = create_coordination_bus()
        agent_set = AgentSet(coordination_bus=bus)
        agent_set.set_id = "test"
        agent_set.add_channel(StubChannel(name="a"))
        agent_set.add_channel(StubChannel(name="b"))
        agent_set.initialize()
        status = agent_set.get_status()
        assert status["set_id"] == "test"
        assert status["member_count"] == 2
        assert "a" in status["members"]
        assert status["bus_stats"] is not None

    def test_shutdown(self):
        bus = create_coordination_bus()
        agent_set = AgentSet(coordination_bus=bus)
        agent_set.set_id = "test"
        agent_set.add_channel(StubChannel(name="x"))
        agent_set.initialize()
        assert agent_set.shutdown() is True
        assert agent_set._initialized is False

    def test_send_envelope_without_bus(self):
        agent_set = AgentSet()
        agent_set.set_id = "test"
        env = CoordinationEnvelope(payload={"test": 1})
        agent_set.send_envelope(env)  # should not raise

    def test_receive_envelopes_ship(self):
        bus = create_coordination_bus()
        agent_set = AgentSet(coordination_bus=bus)
        agent_set.set_id = "ship"
        bus.post(CoordinationEnvelope(direction=EnvelopeDirection.DOWNLINK, payload={"d": 1}))
        envelopes = agent_set.receive_envelopes(limit=10)
        assert len(envelopes) == 1
        assert envelopes[0].payload == {"d": 1}

    def test_receive_envelopes_shore(self):
        bus = create_coordination_bus()
        agent_set = AgentSet(coordination_bus=bus)
        agent_set.set_id = "shore"
        bus.post(CoordinationEnvelope(direction=EnvelopeDirection.UPLINK, payload={"u": 1}))
        envelopes = agent_set.receive_envelopes(limit=10)
        assert len(envelopes) == 1
        assert envelopes[0].payload == {"u": 1}


# ═══════════════════════════════════════════════════════════
# ShoreSupervisionSet Tests
# ═══════════════════════════════════════════════════════════

class TestShoreSupervisionSet:
    def _make_shore(self):
        bus = create_coordination_bus()
        shore = ShoreSupervisionSet(coordination_bus=bus)
        shore.add_channel(StubChannel(name="compliance_digital_expert",
                                       extra_status={"risk_level": "low"}))
        shore.add_channel(StubChannel(name="cyber_security",
                                       extra_status={"threat_level": "none"}))
        shore.add_channel(StubChannel(name="voyage_planner"))
        shore.initialize()
        return shore, bus

    def test_init(self):
        shore = ShoreSupervisionSet()
        assert shore.set_id == "shore"
        assert shore.name == "shore_supervision_set"
        assert len(shore.member_channel_names) == 3

    def test_initialize(self):
        shore, bus = self._make_shore()
        assert shore._initialized is True

    def test_supervision_cycle_low_risk(self):
        shore, bus = self._make_shore()
        result = shore.run_supervision_cycle()
        assert isinstance(result, SupervisionCycleResult)
        assert result.cycle_id == 1
        assert result.compliance_risk == "low"
        assert result.threat_level == "none"
        assert result.constraints_pushed == 0
        assert result.policies_pushed == 0

    def test_supervision_cycle_high_risk(self):
        bus = create_coordination_bus()
        shore = ShoreSupervisionSet(coordination_bus=bus)
        shore.add_channel(StubChannel(name="compliance_digital_expert",
                                       extra_status={"risk_level": "high"}))
        shore.add_channel(StubChannel(name="cyber_security",
                                       extra_status={"threat_level": "critical"}))
        shore.add_channel(StubChannel(name="voyage_planner"))
        shore.initialize()
        result = shore.run_supervision_cycle()
        assert result.constraints_pushed == 1
        assert result.policies_pushed == 1
        # Downlink should have 2 envelopes (constraint + advisory)
        assert bus.pending_downlink() == 2

    def test_push_policy(self):
        shore, bus = self._make_shore()
        shore.push_policy({"max_speed": 15}, target_channel="route_optimizer")
        assert bus.pending_downlink() == 1
        env = bus.poll_downlink(1)[0]
        assert env.msg_type == CoordinationMessageType.POLICY_UPDATE
        assert env.payload == {"max_speed": 15}

    def test_push_voyage_directive(self):
        shore, bus = self._make_shore()
        shore.push_voyage_directive({"waypoint": [30.0, 122.0]})
        env = bus.poll_downlink(1)[0]
        assert env.msg_type == CoordinationMessageType.VOYAGE_DIRECTIVE

    def test_get_status(self):
        shore, bus = self._make_shore()
        shore.run_supervision_cycle()
        status = shore.get_status()
        assert status["set_id"] == "shore"
        assert status["supervision_cycles"] == 1
        assert status["last_cycle"] is not None

    def test_uplink_processing(self):
        bus = create_coordination_bus()
        shore = ShoreSupervisionSet(coordination_bus=bus)
        shore.add_channel(StubChannel(name="compliance_digital_expert"))
        shore.add_channel(StubChannel(name="cyber_security"))
        shore.add_channel(StubChannel(name="voyage_planner"))
        shore.initialize()
        # Simulate uplink from ship
        bus.post(CoordinationEnvelope(
            direction=EnvelopeDirection.UPLINK,
            msg_type=CoordinationMessageType.TELEMETRY_REPORT,
            sender_set="ship",
            payload={"sensor_data": True},
        ))
        result = shore.run_supervision_cycle()
        assert result.uplink_processed == 1


# ═══════════════════════════════════════════════════════════
# ShipboardExecutionSet Tests
# ═══════════════════════════════════════════════════════════

class TestShipboardExecutionSet:
    def _make_ship(self):
        bus = create_coordination_bus()
        ship = ShipboardExecutionSet(coordination_bus=bus)
        for name in ship.member_channel_names:
            ship.add_channel(StubChannel(name=name))
        ship.initialize()
        return ship, bus

    def test_init(self):
        ship = ShipboardExecutionSet()
        assert ship.set_id == "ship"
        assert ship.name == "shipboard_execution_set"
        assert len(ship.member_channel_names) == 6

    def test_initialize(self):
        ship, bus = self._make_ship()
        assert ship._initialized is True
        status = ship.get_status()
        assert status["execution_mode"] == "normal"

    def test_execution_cycle_normal(self):
        ship, bus = self._make_ship()
        result = ship.run_execution_cycle()
        assert isinstance(result, ExecutionCycleResult)
        assert result.cycle_id == 1
        assert result.mode == "normal"
        assert result.anomalies_detected == 0
        assert result.telemetry_sent >= 1
        # Should have posted uplink envelopes (telemetry + execution state)
        assert bus.pending_uplink() >= 2

    def test_execution_cycle_with_anomalies(self):
        bus = create_coordination_bus()
        ship = ShipboardExecutionSet(coordination_bus=bus)
        ship.add_channel(StubChannel(name="distributed_perception_hub", health="error"))
        ship.add_channel(StubChannel(name="intelligent_navigation", health="ok"))
        ship.add_channel(StubChannel(name="intelligent_engine", health="warn"))
        ship.add_channel(StubChannel(name="energy_efficiency", health="ok"))
        ship.add_channel(StubChannel(name="predictive_health", health="ok"))
        ship.add_channel(StubChannel(name="route_optimizer", health="ok"))
        ship.initialize()
        result = ship.run_execution_cycle()
        assert result.anomalies_detected >= 1

    def test_degraded_mode(self):
        bus = create_coordination_bus()
        ship = ShipboardExecutionSet(coordination_bus=bus)
        ship.add_channel(StubChannel(name="distributed_perception_hub", health="error"))
        ship.add_channel(StubChannel(name="intelligent_navigation", health="warn"))
        ship.add_channel(StubChannel(name="intelligent_engine", health="ok"))
        ship.add_channel(StubChannel(name="energy_efficiency", health="ok"))
        ship.add_channel(StubChannel(name="predictive_health", health="ok"))
        ship.add_channel(StubChannel(name="route_optimizer", health="ok"))
        ship.initialize()
        ship.run_execution_cycle()
        assert ship._mode in (ExecutionMode.DEGRADED, ExecutionMode.EMERGENCY)

    def test_emergency_mode(self):
        bus = create_coordination_bus()
        ship = ShipboardExecutionSet(coordination_bus=bus)
        for name in ship.member_channel_names:
            ship.add_channel(StubChannel(name=name, health="error"))
        ship.initialize()
        ship.run_execution_cycle()
        assert ship._mode == ExecutionMode.EMERGENCY

    def test_apply_downlink(self):
        bus = create_coordination_bus()
        ship = ShipboardExecutionSet(coordination_bus=bus)
        for name in ship.member_channel_names:
            ship.add_channel(StubChannel(name=name))
        ship.initialize()
        # Post a downlink directive
        bus.post(CoordinationEnvelope(
            direction=EnvelopeDirection.DOWNLINK,
            msg_type=CoordinationMessageType.POLICY_UPDATE,
            sender_set="shore",
            payload={"max_speed": 12},
        ))
        result = ship.run_execution_cycle()
        assert result.downlink_applied == 1
        assert len(ship._applied_policies) == 1

    def test_report_telemetry(self):
        ship, bus = self._make_ship()
        ship.report_telemetry({"speed": 10.5, "heading": 180})
        assert bus.pending_uplink() == 1
        env = bus.poll_uplink(1)[0]
        assert env.msg_type == CoordinationMessageType.TELEMETRY_REPORT
        assert env.payload["speed"] == 10.5

    def test_report_execution_state(self):
        ship, bus = self._make_ship()
        ship.report_execution_state()
        env = bus.poll_uplink(1)[0]
        assert env.msg_type == CoordinationMessageType.EXECUTION_STATE
        assert "mode" in env.payload

    def test_report_decision_feedback(self):
        ship, bus = self._make_ship()
        ship.report_decision_feedback({"accepted": True, "reason": "safe"})
        env = bus.poll_uplink(1)[0]
        assert env.msg_type == CoordinationMessageType.DECISION_FEEDBACK

    def test_get_status_extended(self):
        ship, bus = self._make_ship()
        ship.run_execution_cycle()
        status = ship.get_status()
        assert "execution_mode" in status
        assert "execution_cycles" in status
        assert "last_cycle" in status
        assert status["execution_cycles"] == 1

    def test_execution_mode_enum(self):
        assert ExecutionMode.NORMAL.value == "normal"
        assert ExecutionMode.AUTONOMOUS.value == "autonomous"
        assert ExecutionMode.EMERGENCY.value == "emergency"


# ═══════════════════════════════════════════════════════════
# AgentSetCoordinator Tests
# ═══════════════════════════════════════════════════════════

class TestAgentSetCoordinator:
    def _make_coordinator(self):
        bus = create_coordination_bus()
        shore = ShoreSupervisionSet(coordination_bus=bus)
        for n in shore.member_channel_names:
            shore.add_channel(StubChannel(name=n))
        shore.initialize()

        ship = ShipboardExecutionSet(coordination_bus=bus)
        for n in ship.member_channel_names:
            ship.add_channel(StubChannel(name=n))
        ship.initialize()

        coord = AgentSetCoordinator(shore_set=shore, ship_set=ship, bus=bus)
        coord.initialize()
        return coord, shore, ship, bus

    def test_init(self):
        coord = AgentSetCoordinator()
        assert coord.name == "agent_set_coordinator"
        coord.initialize()
        assert coord._initialized is True

    def test_relay_cycle(self):
        coord, shore, ship, bus = self._make_coordinator()
        result = coord.relay_cycle()
        assert result["relay_cycle"] == 1
        assert "shore_policies_pushed" in result
        assert "ship_downlink_applied" in result

    def test_multiple_relay_cycles(self):
        coord, shore, ship, bus = self._make_coordinator()
        for _ in range(5):
            coord.relay_cycle()
        assert coord._relay_cycles == 5

    def test_get_status(self):
        coord, shore, ship, bus = self._make_coordinator()
        status = coord.get_status()
        assert status["name"] == "agent_set_coordinator"
        assert "bus_stats" in status
        assert status["shore_set"] is not None
        assert status["ship_set"] is not None

    def test_full_status(self):
        coord, shore, ship, bus = self._make_coordinator()
        coord.relay_cycle()
        fs = coord.full_status()
        assert "coordinator" in fs
        assert "bus" in fs
        assert fs["coordinator"]["relay_cycles"] == 1

    def test_get_bus(self):
        coord, shore, ship, bus = self._make_coordinator()
        assert coord.get_bus() is bus

    def test_get_sets(self):
        coord, shore, ship, bus = self._make_coordinator()
        assert coord.get_shore_set() is shore
        assert coord.get_ship_set() is ship

    def test_shutdown(self):
        coord, shore, ship, bus = self._make_coordinator()
        assert coord.shutdown() is True
        assert coord._initialized is False

    def test_standalone_no_sets(self):
        coord = AgentSetCoordinator()
        coord.initialize()
        result = coord.relay_cycle()
        assert result["relay_cycle"] == 1
        assert result["shore_policies_pushed"] == 0


# ═══════════════════════════════════════════════════════════
# End-to-End Integration
# ═══════════════════════════════════════════════════════════

class TestE2ECoordination:
    def test_shore_to_ship_downlink(self):
        """Shore pushes policy -> ship receives it in execution cycle."""
        bus = create_coordination_bus()
        shore = ShoreSupervisionSet(coordination_bus=bus)
        for n in shore.member_channel_names:
            shore.add_channel(StubChannel(name=n))
        shore.initialize()

        ship = ShipboardExecutionSet(coordination_bus=bus)
        for n in ship.member_channel_names:
            ship.add_channel(StubChannel(name=n))
        ship.initialize()

        # Shore pushes a policy
        shore.push_policy({"emission_limit": 50})
        assert bus.pending_downlink() == 1

        # Ship runs execution cycle, picks up downlink
        result = ship.run_execution_cycle()
        assert result.downlink_applied == 1
        assert bus.pending_downlink() == 0

    def test_ship_to_shore_uplink(self):
        """Ship reports telemetry -> shore processes it in supervision cycle."""
        bus = create_coordination_bus()
        shore = ShoreSupervisionSet(coordination_bus=bus)
        for n in shore.member_channel_names:
            shore.add_channel(StubChannel(name=n))
        shore.initialize()

        ship = ShipboardExecutionSet(coordination_bus=bus)
        for n in ship.member_channel_names:
            ship.add_channel(StubChannel(name=n))
        ship.initialize()

        # Ship runs execution cycle (generates uplink telemetry)
        ship.run_execution_cycle()
        uplink_count = bus.pending_uplink()
        assert uplink_count >= 2  # telemetry + execution state

        # Shore processes uplink
        result = shore.run_supervision_cycle()
        assert result.uplink_processed == uplink_count

    def test_full_relay_via_coordinator(self):
        """Coordinator orchestrates full shore->ship->shore relay."""
        bus = create_coordination_bus()
        shore = ShoreSupervisionSet(coordination_bus=bus)
        for n in shore.member_channel_names:
            shore.add_channel(StubChannel(name=n))
        shore.initialize()

        ship = ShipboardExecutionSet(coordination_bus=bus)
        for n in ship.member_channel_names:
            ship.add_channel(StubChannel(name=n))
        ship.initialize()

        coord = AgentSetCoordinator(shore_set=shore, ship_set=ship, bus=bus)
        coord.initialize()

        result = coord.relay_cycle()
        assert result["relay_cycle"] == 1
        # After relay, bus should have residual uplink from ship
        # (shore supervision runs first, then ship execution generates uplink)

    def test_high_risk_triggers_constraint_to_ship(self):
        """High compliance risk -> shore constraint -> ship applies it."""
        bus = create_coordination_bus()
        shore = ShoreSupervisionSet(coordination_bus=bus)
        shore.add_channel(StubChannel(name="compliance_digital_expert",
                                       extra_status={"risk_level": "critical"}))
        shore.add_channel(StubChannel(name="cyber_security",
                                       extra_status={"threat_level": "none"}))
        shore.add_channel(StubChannel(name="voyage_planner"))
        shore.initialize()

        ship = ShipboardExecutionSet(coordination_bus=bus)
        for n in ship.member_channel_names:
            ship.add_channel(StubChannel(name=n))
        ship.initialize()

        coord = AgentSetCoordinator(shore_set=shore, ship_set=ship, bus=bus)
        coord.initialize()

        result = coord.relay_cycle()
        assert result["shore_constraints_pushed"] == 1
        # Ship should have applied the downlink constraint
        assert result["ship_downlink_applied"] == 1
