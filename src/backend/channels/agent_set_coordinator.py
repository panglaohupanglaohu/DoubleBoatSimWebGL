# -*- coding: utf-8 -*-
"""AgentSetCoordinator: top-level coordinator owning the CoordinationBus
and mediating between ShoreSupervisionSet and ShipboardExecutionSet."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelPriority, ChannelStatus
from .agent_set_protocol import CoordinationBus, create_coordination_bus

logger = logging.getLogger(__name__)


class AgentSetCoordinator(MarineChannel):
    """Dual agent-set coordinator.

    Owns the CoordinationBus and references to both agent sets.
    Provides a unified status view and relay cycle.
    """

    name = "agent_set_coordinator"
    description = "Dual agent-set coordinator (shore <-> ship)"
    version = "1.0.0"
    priority = ChannelPriority.P0
    dependencies: List[str] = []

    def __init__(
        self,
        shore_set: Optional[MarineChannel] = None,
        ship_set: Optional[MarineChannel] = None,
        bus: Optional[CoordinationBus] = None,
        bus_max_size: int = 4096,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self.config = config or {}
        self._config = self.config
        self._shore = shore_set
        self._ship = ship_set
        self._bus = bus or create_coordination_bus(max_size=bus_max_size)
        self._relay_cycles: int = 0

    def initialize(self) -> bool:
        self._initialized = True
        self._set_health(ChannelStatus.OK, "AgentSetCoordinator ready")
        logger.info("AgentSetCoordinator initialized (shore=%s, ship=%s)",
                     self._shore is not None, self._ship is not None)
        return True

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "health_message": self._health.message,
            "relay_cycles": self._relay_cycles,
            "bus_stats": self._bus.stats(),
            "shore_set": self._shore.get_status() if self._shore else None,
            "ship_set": self._ship.get_status() if self._ship else None,
        }

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True

    def get_bus(self) -> CoordinationBus:
        return self._bus

    def get_shore_set(self) -> Optional[MarineChannel]:
        return self._shore

    def get_ship_set(self) -> Optional[MarineChannel]:
        return self._ship

    def relay_cycle(self) -> Dict[str, int]:
        """Run one relay cycle: trigger shore supervision then ship execution."""
        self._relay_cycles += 1
        shore_result = None
        ship_result = None

        if self._shore and hasattr(self._shore, "run_supervision_cycle"):
            try:
                shore_result = self._shore.run_supervision_cycle()
            except Exception as exc:
                logger.warning("Shore supervision cycle error: %s", exc)

        if self._ship and hasattr(self._ship, "run_execution_cycle"):
            try:
                ship_result = self._ship.run_execution_cycle()
            except Exception as exc:
                logger.warning("Ship execution cycle error: %s", exc)

        return {
            "relay_cycle": self._relay_cycles,
            "shore_policies_pushed": getattr(shore_result, "policies_pushed", 0) if shore_result else 0,
            "shore_constraints_pushed": getattr(shore_result, "constraints_pushed", 0) if shore_result else 0,
            "ship_downlink_applied": getattr(ship_result, "downlink_applied", 0) if ship_result else 0,
            "ship_anomalies": getattr(ship_result, "anomalies_detected", 0) if ship_result else 0,
            "bus_downlink_pending": self._bus.pending_downlink(),
            "bus_uplink_pending": self._bus.pending_uplink(),
        }

    def full_status(self) -> Dict[str, Any]:
        """Aggregate status from both sets + bus stats."""
        return {
            "coordinator": {
                "health": self._health.status.value,
                "relay_cycles": self._relay_cycles,
            },
            "bus": self._bus.stats(),
            "shore_set": self._shore.get_status() if self._shore else None,
            "ship_set": self._ship.get_status() if self._ship else None,
        }
