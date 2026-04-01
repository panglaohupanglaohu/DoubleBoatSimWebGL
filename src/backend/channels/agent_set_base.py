# -*- coding: utf-8 -*-
"""AgentSet base class: a logical group of MarineChannels acting as a composite Channel."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelPriority, ChannelStatus
from .agent_set_protocol import (
    CoordinationBus,
    CoordinationEnvelope,
    EnvelopeDirection,
)

logger = logging.getLogger(__name__)


class AgentSet(MarineChannel):
    """Base class for Shore Supervision / Shipboard Execution agent sets.

    An AgentSet groups related MarineChannels and coordinates them
    through a shared CoordinationBus.
    """

    set_id: str = ""
    member_channel_names: List[str] = []

    def __init__(
        self,
        coordination_bus: Optional[CoordinationBus] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self.config = config or {}
        self._config = self.config
        self._bus = coordination_bus
        self._members: Dict[str, MarineChannel] = {}

    # ---- Member management ----

    def add_channel(self, channel: MarineChannel) -> bool:
        """Add a channel to this agent set."""
        if not channel or not hasattr(channel, "name"):
            return False
        self._members[channel.name] = channel
        logger.debug("AgentSet[%s] added member: %s", self.set_id, channel.name)
        return True

    def remove_channel(self, name: str) -> bool:
        """Remove a channel from this agent set by name."""
        if name in self._members:
            del self._members[name]
            return True
        return False

    def get_channel(self, name: str) -> Optional[MarineChannel]:
        """Get a member channel by name."""
        return self._members.get(name)

    def list_members(self) -> List[str]:
        """Return list of member channel names."""
        return list(self._members.keys())

    # ---- MarineChannel interface ----

    def initialize(self) -> bool:
        """Initialize this agent set and all its members."""
        ok = True
        for name, ch in self._members.items():
            try:
                if not ch._initialized:
                    ch.initialize()
            except Exception as exc:
                logger.warning("AgentSet[%s] failed to init member %s: %s",
                               self.set_id, name, exc)
                ok = False
        self._initialized = True
        if ok:
            self._set_health(ChannelStatus.OK,
                             f"AgentSet[{self.set_id}] ready with {len(self._members)} members")
        else:
            self._set_health(ChannelStatus.WARN,
                             f"AgentSet[{self.set_id}] partially ready")
        return True

    def get_status(self) -> Dict[str, Any]:
        """Return aggregate status of this agent set."""
        member_status = {}
        for name, ch in self._members.items():
            try:
                st = ch.get_status()
                member_status[name] = st.get("health", "unknown")
            except Exception as e:
                logger.debug(f"Agent set error: {e}")
                member_status[name] = "error"
        return {
            "name": self.name,
            "set_id": self.set_id,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "health_message": self._health.message,
            "member_count": len(self._members),
            "members": self.list_members(),
            "member_status": member_status,
            "bus_stats": self._bus.stats() if self._bus else None,
        }

    def shutdown(self) -> bool:
        """Shutdown all members and this agent set."""
        for name, ch in self._members.items():
            try:
                ch.shutdown()
            except Exception as exc:
                logger.warning("AgentSet[%s] failed to shutdown member %s: %s",
                               self.set_id, name, exc)
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True

    # ---- Coordination ----

    def set_coordination_bus(self, bus: CoordinationBus) -> None:
        """Bind or replace the coordination bus."""
        self._bus = bus

    def send_envelope(self, envelope: CoordinationEnvelope) -> None:
        """Post an envelope to the coordination bus."""
        if self._bus:
            self._bus.post(envelope)
        else:
            logger.warning("AgentSet[%s] has no bus, envelope dropped", self.set_id)

    def receive_envelopes(self, limit: int = 64) -> List[CoordinationEnvelope]:
        """Poll envelopes addressed to this set.

        Ship set polls downlink; Shore set polls uplink.
        """
        if not self._bus:
            return []
        if self.set_id == "ship":
            return self._bus.poll_downlink(limit)
        elif self.set_id == "shore":
            return self._bus.poll_uplink(limit)
        return []
