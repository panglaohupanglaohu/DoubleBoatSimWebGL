# -*- coding: utf-8 -*-
"""Shore Supervision Agent Set: governance, compliance audit, voyage planning.

Orchestrates compliance_digital_expert, cyber_security, and voyage_planner.
Implements the supervision cycle: collect -> audit -> constrain -> dispatch.
Sends policy/constraints/evidence downward to shipboard set via CoordinationBus.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
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


@dataclass
class SupervisionCycleResult:
    """Result of one supervision cycle."""
    cycle_id: int = 0
    timestamp: str = ""
    compliance_risk: str = "low"
    threat_level: str = "none"
    voyage_status: str = "unknown"
    policies_pushed: int = 0
    constraints_pushed: int = 0
    uplink_processed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ShoreSupervisionSet(AgentSet):
    """Shore-side supervision agent set.

    Members: compliance_digital_expert, cyber_security, voyage_planner.
    """

    name = "shore_supervision_set"
    description = "Shore Supervision Agent Set (compliance / security / voyage)"
    version = "1.0.0"
    priority = ChannelPriority.P0
    set_id = "shore"
    member_channel_names = [
        "compliance_digital_expert",
        "cyber_security",
        "voyage_planner",
    ]

    def __init__(
        self,
        coordination_bus: Optional[CoordinationBus] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(coordination_bus=coordination_bus, config=config)
        self._cycle_count: int = 0
        self._last_result: Optional[SupervisionCycleResult] = None

    # ---- MarineChannel overrides ----

    def initialize(self) -> bool:
        super().initialize()
        self._set_health(ChannelStatus.OK, "Shore Supervision Set ready")
        logger.info("Shore Supervision Set initialized with %d members",
                     len(self._members))
        return True

    def get_status(self) -> Dict[str, Any]:
        base = super().get_status()
        base["supervision_cycles"] = self._cycle_count
        base["last_cycle"] = self._last_result.to_dict() if self._last_result else None
        return base

    # ---- Supervision cycle ----

    def run_supervision_cycle(self) -> SupervisionCycleResult:
        """Execute one supervision cycle: collect -> audit -> constrain -> dispatch."""
        self._cycle_count += 1
        ts = datetime.now().isoformat()
        policies_pushed = 0
        constraints_pushed = 0

        # 1. Collect member statuses
        compliance_status = self._get_member_status_safe("compliance_digital_expert")
        security_status = self._get_member_status_safe("cyber_security")
        voyage_status = self._get_member_status_safe("voyage_planner")

        compliance_risk = compliance_status.get("risk_level", "low")
        threat_level = security_status.get("threat_level", "none")
        voyage_state = voyage_status.get("health", "unknown")

        # 2. Push constraints if compliance risk is elevated
        if compliance_risk in ("high", "critical"):
            self.push_compliance_constraint({
                "risk_level": compliance_risk,
                "source": "compliance_digital_expert",
                "timestamp": ts,
            })
            constraints_pushed += 1

        # 3. Push security advisory if threat detected
        if threat_level in ("high", "critical"):
            self.push_security_advisory({
                "threat_level": threat_level,
                "source": "cyber_security",
                "timestamp": ts,
            })
            policies_pushed += 1

        # 4. Process uplink messages from ship
        uplink_processed = 0
        envelopes = self.receive_envelopes(limit=64)
        for env in envelopes:
            self._handle_uplink(env)
            uplink_processed += 1

        result = SupervisionCycleResult(
            cycle_id=self._cycle_count,
            timestamp=ts,
            compliance_risk=compliance_risk,
            threat_level=threat_level,
            voyage_status=voyage_state,
            policies_pushed=policies_pushed,
            constraints_pushed=constraints_pushed,
            uplink_processed=uplink_processed,
        )
        self._last_result = result
        logger.info("Shore supervision cycle #%d: risk=%s threat=%s policies=%d constraints=%d",
                     self._cycle_count, compliance_risk, threat_level,
                     policies_pushed, constraints_pushed)
        return result

    # ---- Downlink helpers ----

    def push_policy(self, policy: Dict[str, Any], *, target_channel: str = "") -> None:
        """Send a POLICY_UPDATE envelope to the shipboard set."""
        envelope = CoordinationEnvelope(
            direction=EnvelopeDirection.DOWNLINK,
            msg_type=CoordinationMessageType.POLICY_UPDATE,
            sender_set="shore",
            sender_channel="shore_supervision_set",
            target_set="ship",
            target_channel=target_channel,
            payload=policy,
            priority=2,
        )
        self.send_envelope(envelope)

    def push_compliance_constraint(self, constraint: Dict[str, Any]) -> None:
        """Send a COMPLIANCE_CONSTRAINT envelope to the shipboard set."""
        envelope = CoordinationEnvelope(
            direction=EnvelopeDirection.DOWNLINK,
            msg_type=CoordinationMessageType.COMPLIANCE_CONSTRAINT,
            sender_set="shore",
            sender_channel="compliance_digital_expert",
            target_set="ship",
            payload=constraint,
            priority=1,
        )
        self.send_envelope(envelope)

    def push_security_advisory(self, advisory: Dict[str, Any]) -> None:
        """Send a SECURITY_ADVISORY envelope to the shipboard set."""
        envelope = CoordinationEnvelope(
            direction=EnvelopeDirection.DOWNLINK,
            msg_type=CoordinationMessageType.SECURITY_ADVISORY,
            sender_set="shore",
            sender_channel="cyber_security",
            target_set="ship",
            payload=advisory,
            priority=1,
        )
        self.send_envelope(envelope)

    def push_voyage_directive(self, directive: Dict[str, Any]) -> None:
        """Send a VOYAGE_DIRECTIVE envelope to the shipboard set."""
        envelope = CoordinationEnvelope(
            direction=EnvelopeDirection.DOWNLINK,
            msg_type=CoordinationMessageType.VOYAGE_DIRECTIVE,
            sender_set="shore",
            sender_channel="voyage_planner",
            target_set="ship",
            payload=directive,
            priority=2,
        )
        self.send_envelope(envelope)

    # ---- Internal ----

    def _get_member_status_safe(self, name: str) -> Dict[str, Any]:
        ch = self._members.get(name)
        if ch:
            try:
                return ch.get_status()
            except Exception as exc:
                logger.warning("Shore set: %s status error: %s", name, exc)
        return {"health": "unavailable"}

    def _handle_uplink(self, envelope: CoordinationEnvelope) -> None:
        """Process an uplink envelope from the shipboard set."""
        logger.debug("Shore set received uplink: %s from %s",
                      envelope.msg_type.value, envelope.sender_channel)
