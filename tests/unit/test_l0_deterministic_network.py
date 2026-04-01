# -*- coding: utf-8 -*-
"""
Tests for L0: Deterministic Network Infrastructure Channel
"""

import pytest
from channels.deterministic_network import (
    DeterministicNetworkChannel, FiberLink, NetworkNode, ZonalDCBus,
    TSNSchedule, LinkStatus, ZoneStatus, NetworkProtocol,
)


@pytest.fixture
def network():
    ch = DeterministicNetworkChannel()
    ch.initialize()
    return ch


class TestDeterministicNetworkInit:
    def test_initialize(self, network):
        assert network._initialized
        assert network._health.status.value == "ok"

    def test_dual_ring_setup(self, network):
        assert len(network._links) > 0
        ring_a = [l for l in network._links.values() if l.ring == "A"]
        ring_b = [l for l in network._links.values() if l.ring == "B"]
        assert len(ring_a) == len(ring_b)

    def test_nodes_created(self, network):
        assert len(network._nodes) >= 5

    def test_zonal_dc_setup(self, network):
        assert len(network._zones) >= 4
        for zone in network._zones.values():
            assert zone.voltage_v == 750.0
            assert zone.status == ZoneStatus.NORMAL

    def test_tsn_schedules_setup(self, network):
        assert len(network._tsn_schedules) >= 5
        nav_sched = network._tsn_schedules.get("nav_critical")
        assert nav_sched is not None
        assert nav_sched.priority == 7

    def test_custom_config(self):
        ch = DeterministicNetworkChannel(config={"protocol": "prp"})
        ch.initialize()
        assert ch._protocol == NetworkProtocol.PRP


class TestLinkFault:
    def test_simulate_link_fault(self, network):
        link_id = list(network._links.keys())[0]
        result = network.simulate_link_fault(link_id)
        assert "recovery_time_ms" in result
        assert result["recovery_time_ms"] <= 50  # RSTP < 50ms

    def test_fault_unknown_link(self, network):
        result = network.simulate_link_fault("nonexistent")
        assert "error" in result

    def test_prp_hitless_switchover(self):
        ch = DeterministicNetworkChannel(config={"protocol": "prp"})
        ch.initialize()
        link_id = list(ch._links.keys())[0]
        result = ch.simulate_link_fault(link_id)
        assert result["recovery_time_ms"] == 0.0
        assert result["switchover_type"] == "hitless_prp"

    def test_hsr_hitless_switchover(self):
        ch = DeterministicNetworkChannel(config={"protocol": "hsr"})
        ch.initialize()
        link_id = list(ch._links.keys())[0]
        result = ch.simulate_link_fault(link_id)
        assert result["recovery_time_ms"] == 0.0

    def test_fault_log_recorded(self, network):
        link_id = list(network._links.keys())[0]
        network.simulate_link_fault(link_id)
        assert len(network._fault_log) == 1
        assert network._fault_log[0]["link_id"] == link_id

    def test_restore_link(self, network):
        link_id = list(network._links.keys())[0]
        network.simulate_link_fault(link_id)
        assert network._links[link_id].status == LinkStatus.DOWN
        assert network.restore_link(link_id)
        assert network._links[link_id].status == LinkStatus.UP

    def test_restore_nonexistent(self, network):
        assert not network.restore_link("nonexistent")

    def test_multiple_faults(self, network):
        links = list(network._links.keys())[:3]
        for lid in links:
            network.simulate_link_fault(lid)
        assert network._switchover_count == 3


class TestZonalDC:
    def test_isolate_zone(self, network):
        zone_id = list(network._zones.keys())[0]
        result = network.isolate_zone_fault(zone_id)
        assert result["isolated"]
        assert result["recovery_time_ms"] < 10  # < 10ms

    def test_isolate_unknown_zone(self, network):
        result = network.isolate_zone_fault("nonexistent")
        assert "error" in result

    def test_restore_zone(self, network):
        zone_id = list(network._zones.keys())[0]
        network.isolate_zone_fault(zone_id)
        assert network._zones[zone_id].status == ZoneStatus.ISOLATED
        assert network.restore_zone(zone_id)
        assert network._zones[zone_id].status == ZoneStatus.NORMAL

    def test_restore_nonexistent_zone(self, network):
        assert not network.restore_zone("nonexistent")


class TestTSN:
    def test_get_tsn_latency(self, network):
        latency = network.get_tsn_latency("nav_critical")
        assert latency is not None
        assert latency > 0

    def test_get_tsn_latency_unknown(self, network):
        assert network.get_tsn_latency("nonexistent") is None


class TestNetworkStatus:
    def test_get_topology(self, network):
        topo = network.get_network_topology()
        assert "nodes" in topo
        assert "links" in topo
        assert "rings" in topo

    def test_get_zonal_dc_status(self, network):
        status = network.get_zonal_dc_status()
        assert len(status) >= 4

    def test_calculate_availability(self, network):
        avail = network.calculate_availability()
        assert avail == 1.0  # All links up

    def test_availability_with_fault(self, network):
        link_id = list(network._links.keys())[0]
        network.simulate_link_fault(link_id)
        avail = network.calculate_availability()
        assert avail > 0.5  # Redundant ring available

    def test_get_status(self, network):
        status = network.get_status()
        assert status["name"] == "deterministic_network"
        assert status["availability"] == 1.0
        assert status["protocol"] == "rstp"

    def test_shutdown(self, network):
        assert network.shutdown()
        assert not network._initialized
