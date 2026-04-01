# -*- coding: utf-8 -*-
"""Shipboard Execution Agent Set: perception, navigation, engine, edge autonomy.

Orchestrates distributed_perception_hub, intelligent_navigation, intelligent_engine,
energy_efficiency, predictive_health, route_optimizer.
Implements the execution cycle: sense -> decide -> act -> report.
Reports execution state/telemetry/feedback upward to shore via CoordinationBus.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .agent_set_base import AgentSet
from .agent_set_protocol import (
    CoordinationBus,
    CoordinationEnvelope,
    CoordinationMessageType,
    EnvelopeDirection,
)
from .marine_base import ChannelPriority, ChannelStatus

logger = logging.getLogger(__name__)


class ExecutionMode(str, Enum):
    """Shipboard execution operating mode."""
    NORMAL = "normal"
    DEGRADED = "degraded"
    AUTONOMOUS = "autonomous"
    EMERGENCY = "emergency"
    STANDBY = "standby"


@dataclass
class ExecutionCycleResult:
    """Result of one execution cycle."""
    cycle_id: int = 0
    timestamp: str = ""
    mode: str = "normal"
    telemetry_sent: int = 0
    downlink_applied: int = 0
    anomalies_detected: int = 0
    member_summary: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ShipboardExecutionSet(AgentSet):
    """Shipboard execution agent set.

    Members: distributed_perception_hub, intelligent_navigation,
    intelligent_engine, energy_efficiency, predictive_health, route_optimizer.
    """

    name = "shipboard_execution_set"
    description = "Shipboard Execution Agent Set (perception / navigation / engine / edge)"
    version = "1.0.0"
    priority = ChannelPriority.P0
    set_id = "ship"
    member_channel_names = [
        "distributed_perception_hub",
        "intelligent_navigation",
        "intelligent_engine",
        "energy_efficiency",
        "predictive_health",
        "route_optimizer",
    ]

    def __init__(
        self,
        coordination_bus: Optional[CoordinationBus] = None,
        config: Optional[Dict[str, Any]] = None,
        decision_orchestrator: Optional[Any] = None,
    ) -> None:
        super().__init__(coordination_bus=coordination_bus, config=config)
        self._orchestrator = decision_orchestrator
        self._mode = ExecutionMode.NORMAL
        self._cycle_count: int = 0
        self._last_result: Optional[ExecutionCycleResult] = None
        self._applied_policies: List[Dict[str, Any]] = []
    def initialize(self) -> bool:
        super().initialize()
        self._set_health(ChannelStatus.OK, "Shipboard Execution Set ready")
        logger.info("Shipboard Execution Set initialized with %d members",
                     len(self._members))
        return True

    def get_status(self) -> Dict[str, Any]:
        base = super().get_status()
        base["execution_mode"] = self._mode.value
        base["execution_cycles"] = self._cycle_count
        base["last_cycle"] = self._last_result.to_dict() if self._last_result else None
        base["applied_policies"] = len(self._applied_policies)
        base["has_orchestrator"] = self._orchestrator is not None
        return base

    def run_execution_cycle(self) -> ExecutionCycleResult:
        """Execute one cycle: sense -> decide -> act -> report."""
        self._cycle_count += 1
        ts = datetime.now().isoformat()
        anomalies = 0

        # 1. Apply downlink directives from shore
        downlink_applied = self.apply_downlink_directives()

        # 2. Collect member statuses (sense)
        member_summary = {}
        for ch_name in self.member_channel_names:
            st = self._get_member_status_safe(ch_name)
            health = st.get("health", "unavailable")
            member_summary[ch_name] = health
            if health in ("error", "warn"):
                anomalies += 1

        # 3. Evaluate execution mode
        self._evaluate_mode(member_summary, anomalies)

        # 4. Report telemetry upward
        telemetry_sent = 0
        self.report_telemetry({
            "cycle_id": self._cycle_count,
            "mode": self._mode.value,
            "member_summary": member_summary,
            "anomalies": anomalies,
            "timestamp": ts,
        })
        telemetry_sent += 1

        # 5. Report execution state
        self.report_execution_state()
        telemetry_sent += 1

        # 6. Report anomalies if any
        if anomalies > 0:
            self._report_anomalies(member_summary, ts)

        result = ExecutionCycleResult(
            cycle_id=self._cycle_count,
            timestamp=ts,
            mode=self._mode.value,
            telemetry_sent=telemetry_sent,
            downlink_applied=downlink_applied,
            anomalies_detected=anomalies,
            member_summary=member_summary,
        )
        self._last_result = result
        logger.info("Shipboard execution cycle #%d: mode=%s downlink=%d anomalies=%d",
                     self._cycle_count, self._mode.value, downlink_applied, anomalies)
        return result
    def report_execution_state(self) -> None:
        """Post an EXECUTION_STATE envelope to shore."""
        member_states = {}
        for ch_name in self.member_channel_names:
            st = self._get_member_status_safe(ch_name)
            member_states[ch_name] = st.get("health", "unknown")
        envelope = CoordinationEnvelope(
            direction=EnvelopeDirection.UPLINK,
            msg_type=CoordinationMessageType.EXECUTION_STATE,
            sender_set="ship",
            sender_channel="shipboard_execution_set",
            target_set="shore",
            payload={
                "mode": self._mode.value,
                "cycle": self._cycle_count,
                "member_states": member_states,
            },
            priority=3,
        )
        self.send_envelope(envelope)

    def report_telemetry(self, telemetry: Dict[str, Any]) -> None:
        """Post a TELEMETRY_REPORT envelope to shore."""
        envelope = CoordinationEnvelope(
            direction=EnvelopeDirection.UPLINK,
            msg_type=CoordinationMessageType.TELEMETRY_REPORT,
            sender_set="ship",
            sender_channel="shipboard_execution_set",
            target_set="shore",
            payload=telemetry,
            priority=3,
        )
        self.send_envelope(envelope)

    def report_decision_feedback(self, feedback: Dict[str, Any]) -> None:
        """Post a DECISION_FEEDBACK envelope to shore."""
        envelope = CoordinationEnvelope(
            direction=EnvelopeDirection.UPLINK,
            msg_type=CoordinationMessageType.DECISION_FEEDBACK,
            sender_set="ship",
            sender_channel="decision_orchestrator",
            target_set="shore",
            payload=feedback,
            priority=2,
        )
        self.send_envelope(envelope)

    def apply_downlink_directives(self) -> int:
        """Drain downlink queue, dispatch to members. Returns count applied."""
        envelopes = self.receive_envelopes(limit=64)
        applied = 0
        for env in envelopes:
            self._apply_directive(env)
            applied += 1
        return applied

    def get_control_plane_status(self) -> Dict[str, Any]:
        """Delegate to decision_orchestrator.get_status()."""
        if self._orchestrator:
            try:
                return self._orchestrator.get_status()
            except Exception as exc:
                logger.warning("Orchestrator status error: %s", exc)
        return {"status": "unavailable"}
    def _get_member_status_safe(self, name: str) -> Dict[str, Any]:
        ch = self._members.get(name)
        if ch:
            try:
                return ch.get_status()
            except Exception as exc:
                logger.warning("Ship set: %s status error: %s", name, exc)
        return {"health": "unavailable"}

    def _apply_directive(self, envelope: CoordinationEnvelope) -> None:
        """Apply a single downlink directive."""
        logger.debug("Ship set applying directive: %s from %s",
                      envelope.msg_type.value, envelope.sender_channel)
        self._applied_policies.append({
            "envelope_id": envelope.envelope_id,
            "msg_type": envelope.msg_type.value,
            "payload": envelope.payload,
            "applied_at": datetime.now().isoformat(),
        })
        if len(self._applied_policies) > 200:
            self._applied_policies = self._applied_policies[-200:]

        if self._orchestrator and hasattr(self._orchestrator, "apply_policy"):
            try:
                self._orchestrator.apply_policy(envelope)
            except Exception as exc:
                logger.warning("Orchestrator apply_policy error: %s", exc)

    def _evaluate_mode(self, member_summary: Dict[str, str], anomalies: int) -> None:
        """Evaluate and update execution mode based on member health."""
        error_count = sum(1 for v in member_summary.values() if v == "error")
        if error_count >= 3:
            self._mode = ExecutionMode.EMERGENCY
            self._set_health(ChannelStatus.ERROR,
                           f"Emergency: {error_count} members in error")
        elif error_count >= 1 or anomalies >= 2:
            self._mode = ExecutionMode.DEGRADED
            self._set_health(ChannelStatus.WARN,
                           f"Degraded: {anomalies} anomalies")
        else:
            if self._mode in (ExecutionMode.EMERGENCY, ExecutionMode.DEGRADED):
                self._mode = ExecutionMode.NORMAL
            self._set_health(ChannelStatus.OK, "Shipboard execution operational")

        if self._bus:
            stats = self._bus.stats()
            if (stats.get("downlink_posted", 0) == 0
                    and self._cycle_count > 5
                    and self._mode == ExecutionMode.NORMAL):
                self._mode = ExecutionMode.AUTONOMOUS
                logger.warning("No downlink received after %d cycles - autonomous mode",
                               self._cycle_count)

    def _report_anomalies(self, member_summary: Dict[str, str], ts: str) -> None:
        """Report ANOMALY_ALERT for members with errors or warnings."""
        problem_members = {k: v for k, v in member_summary.items()
                          if v in ("error", "warn")}
        envelope = CoordinationEnvelope(
            direction=EnvelopeDirection.UPLINK,
            msg_type=CoordinationMessageType.ANOMALY_ALERT,
            sender_set="ship",
            sender_channel="shipboard_execution_set",
            target_set="shore",
            payload={
                "anomaly_count": len(problem_members),
                "affected_members": problem_members,
                "execution_mode": self._mode.value,
                "timestamp": ts,
            },
            priority=1,
        )
        self.send_envelope(envelope)
