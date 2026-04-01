# -*- coding: utf-8 -*-
"""Dual Agent-Set coordination protocol: message types, envelope, in-memory bus."""

from __future__ import annotations

import logging
import uuid
from collections import deque
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CoordinationMessageType(Enum):
    """Message types exchanged between Shore and Shipboard agent sets."""
    POLICY_UPDATE = "policy_update"
    COMPLIANCE_CONSTRAINT = "compliance_constraint"
    VOYAGE_DIRECTIVE = "voyage_directive"
    SECURITY_ADVISORY = "security_advisory"
    OVERRIDE_COMMAND = "override_command"
    EXECUTION_STATE = "execution_state"
    TELEMETRY_REPORT = "telemetry_report"
    ANOMALY_ALERT = "anomaly_alert"
    DECISION_FEEDBACK = "decision_feedback"
    EVIDENCE_UPLOAD = "evidence_upload"
    HEARTBEAT = "heartbeat"
    ACK = "ack"
    HANDSHAKE = "handshake"


class EnvelopeDirection(Enum):
    """Direction of a coordination envelope."""
    DOWNLINK = "shore_to_ship"
    UPLINK = "ship_to_shore"


@dataclass
class CoordinationEnvelope:
    """Message envelope exchanged between shore and shipboard agent sets."""
    envelope_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    direction: EnvelopeDirection = EnvelopeDirection.DOWNLINK
    msg_type: CoordinationMessageType = CoordinationMessageType.HEARTBEAT
    sender_set: str = ""
    sender_channel: str = ""
    target_set: str = ""
    target_channel: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    ttl_seconds: float = 300.0
    priority: int = 3

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["direction"] = self.direction.value
        d["msg_type"] = self.msg_type.value
        return d


class CoordinationBus:
    """In-memory bus for inter-set message exchange using bounded deques."""

    def __init__(self, *, max_size: int = 4096) -> None:
        self._downlink: deque[CoordinationEnvelope] = deque(maxlen=max_size)
        self._uplink: deque[CoordinationEnvelope] = deque(maxlen=max_size)
        self._max_size = max_size
        self._stats: Dict[str, int] = {
            "downlink_posted": 0,
            "uplink_posted": 0,
            "downlink_polled": 0,
            "uplink_polled": 0,
            "dropped": 0,
        }

    def post(self, envelope: CoordinationEnvelope) -> None:
        """Route envelope to the correct queue based on direction."""
        if envelope.direction == EnvelopeDirection.DOWNLINK:
            was_full = len(self._downlink) == self._max_size
            self._downlink.append(envelope)
            self._stats["downlink_posted"] += 1
            if was_full:
                self._stats["dropped"] += 1
        else:
            was_full = len(self._uplink) == self._max_size
            self._uplink.append(envelope)
            self._stats["uplink_posted"] += 1
            if was_full:
                self._stats["dropped"] += 1

    def poll_downlink(self, limit: int = 64) -> List[CoordinationEnvelope]:
        """Pop up to limit envelopes from the downlink queue."""
        result: List[CoordinationEnvelope] = []
        count = min(limit, len(self._downlink))
        for _ in range(count):
            result.append(self._downlink.popleft())
        self._stats["downlink_polled"] += count
        return result

    def poll_uplink(self, limit: int = 64) -> List[CoordinationEnvelope]:
        """Pop up to limit envelopes from the uplink queue."""
        result: List[CoordinationEnvelope] = []
        count = min(limit, len(self._uplink))
        for _ in range(count):
            result.append(self._uplink.popleft())
        self._stats["uplink_polled"] += count
        return result

    def pending_downlink(self) -> int:
        return len(self._downlink)

    def pending_uplink(self) -> int:
        return len(self._uplink)

    def stats(self) -> Dict[str, Any]:
        return {
            **self._stats,
            "downlink_pending": self.pending_downlink(),
            "uplink_pending": self.pending_uplink(),
        }

    def clear(self) -> None:
        """Clear all queues and reset stats."""
        self._downlink.clear()
        self._uplink.clear()
        self._stats = {k: 0 for k in self._stats}


def create_coordination_bus(*, max_size: int = 4096) -> CoordinationBus:
    """Factory function to create a CoordinationBus."""
    return CoordinationBus(max_size=max_size)
