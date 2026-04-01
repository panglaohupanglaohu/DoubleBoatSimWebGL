# -*- coding: utf-8 -*-
"""
Tests for BilgeWaterMonitorChannel and CommunicationManagerChannel.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "backend"))

import pytest
from channels.bilge_water_monitor import BilgeWaterMonitorChannel
from channels.communication_manager import CommunicationManagerChannel


# ============================================================
#  Helper
# ============================================================

def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.run(coro)


# ============================================================
#  Bilge Water Monitor — 25+ tests
# ============================================================

class TestBilgeWaterMonitor:
    """BilgeWaterMonitorChannel 测试套件。"""

    def _make(self):
        ch = BilgeWaterMonitorChannel()
        ch.initialize()
        return ch

    # ---- init ----

    def test_bilge_init(self):
        ch = BilgeWaterMonitorChannel()
        assert ch.name == "bilge_water_monitor"
        assert ch._active is False
        assert ch._compartments == {}
        assert ch._oily_water_separator["operational"] is True
        assert ch._oily_water_separator["oil_content_output_ppm"] == 0.0
        assert ch._discharge_limit_ppm == 15.0

    # ---- update_compartment ----

    def test_bilge_update_compartment(self):
        ch = self._make()
        result = ch.update_compartment("C1", 30.0, 5.0)
        assert result["comp_id"] == "C1"
        assert result["level_percent"] == 30.0
        assert result["oil_content_ppm"] == 5.0
        assert result["alarm_active"] is False
        assert "C1" in ch._compartments

    def test_bilge_update_multiple_compartments(self):
        ch = self._make()
        ch.update_compartment("C1", 20.0, 2.0)
        ch.update_compartment("C2", 50.0, 8.0)
        ch.update_compartment("C3", 10.0, 1.0)
        assert len(ch._compartments) == 3
        assert set(ch._compartments.keys()) == {"C1", "C2", "C3"}

    # ---- bilge status ----

    def test_bilge_status_no_compartments(self):
        ch = self._make()
        status = ch.get_bilge_status()
        assert status["compartments"] == []
        assert status["any_alarm"] is False
        assert status["discharge_permitted"] is True

    def test_bilge_status_normal(self):
        ch = self._make()
        ch.update_compartment("C1", 30.0, 5.0)
        status = ch.get_bilge_status()
        assert len(status["compartments"]) == 1
        assert status["any_alarm"] is False

    # ---- alarm ----

    def test_bilge_alarm_high_level(self):
        ch = self._make()
        result = ch.update_compartment("C1", 85.0, 5.0)
        assert result["alarm_active"] is True
        status = ch.get_bilge_status()
        assert status["any_alarm"] is True

    def test_bilge_alarm_high_oil(self):
        ch = self._make()
        result = ch.update_compartment("C1", 30.0, 20.0)
        assert result["alarm_active"] is True
        status = ch.get_bilge_status()
        assert status["any_alarm"] is True

    def test_bilge_alarm_both(self):
        ch = self._make()
        result = ch.update_compartment("C1", 90.0, 25.0)
        assert result["alarm_active"] is True

    def test_bilge_no_alarm_below_limits(self):
        ch = self._make()
        result = ch.update_compartment("C1", 50.0, 10.0)
        assert result["alarm_active"] is False

    # ---- OWS ----

    def test_bilge_ows_operational(self):
        ch = self._make()
        status = ch.get_bilge_status()
        assert status["ows_status"]["operational"] is True

    def test_bilge_ows_not_operational(self):
        ch = self._make()
        ch._oily_water_separator["operational"] = False
        status = ch.get_bilge_status()
        assert status["ows_status"]["operational"] is False

    # ---- discharge ----

    def test_bilge_discharge_permitted(self):
        ch = self._make()
        # OWS operational, output 0 ppm → permitted
        status = ch.get_bilge_status()
        assert status["discharge_permitted"] is True

    def test_bilge_discharge_not_permitted_ows_off(self):
        ch = self._make()
        ch._oily_water_separator["operational"] = False
        status = ch.get_bilge_status()
        assert status["discharge_permitted"] is False

    def test_bilge_discharge_not_permitted_high_oil(self):
        ch = self._make()
        ch._oily_water_separator["oil_content_output_ppm"] = 20.0
        status = ch.get_bilge_status()
        assert status["discharge_permitted"] is False

    # ---- MARPOL compliance ----

    def test_bilge_marpol_compliant(self):
        ch = self._make()
        ch.update_compartment("C1", 30.0, 5.0)
        comp = ch.check_marpol_compliance()
        assert comp["compliant"] is True
        assert comp["violations"] == []

    def test_bilge_marpol_violation_oil(self):
        ch = self._make()
        ch.update_compartment("C1", 30.0, 20.0)
        comp = ch.check_marpol_compliance()
        assert comp["compliant"] is False
        assert len(comp["violations"]) >= 1

    def test_bilge_marpol_violations_list(self):
        ch = self._make()
        ch.update_compartment("C1", 30.0, 20.0)
        ch._oily_water_separator["operational"] = False
        ch._oily_water_separator["oil_content_output_ppm"] = 20.0
        comp = ch.check_marpol_compliance()
        assert comp["compliant"] is False
        # 3 violations: C1 oil > 15, OWS not operational, OWS output > 15
        assert len(comp["violations"]) == 3

    # ---- event processing ----

    def test_bilge_process_event_reading(self):
        ch = self._make()
        result = _run(ch.process_event({
            "type": "bilge_reading",
            "comp_id": "C2",
            "level_percent": 45.0,
            "oil_content_ppm": 3.0,
        }))
        assert result["status"] == "updated"
        assert result["compartment"]["comp_id"] == "C2"
        assert "C2" in ch._compartments

    def test_bilge_process_event_ows(self):
        ch = self._make()
        result = _run(ch.process_event({
            "type": "ows_update",
            "operational": False,
            "oil_content_output_ppm": 18.0,
        }))
        assert result["status"] == "updated"
        assert result["ows"]["operational"] is False
        assert result["ows"]["oil_content_output_ppm"] == 18.0

    def test_bilge_process_event_unknown(self):
        ch = self._make()
        result = _run(ch.process_event({"type": "unknown"}))
        assert result["status"] == "ignored"

    def test_bilge_process_event_reading_no_comp_id(self):
        ch = self._make()
        result = _run(ch.process_event({"type": "bilge_reading"}))
        assert result["status"] == "error"

    # ---- get_status ----

    def test_bilge_get_status(self):
        ch = self._make()
        ch.update_compartment("C1", 30.0, 5.0)
        status = ch.get_status()
        assert status["name"] == "bilge_water_monitor"
        assert status["active"] is True
        assert status["initialized"] is True
        assert status["compartment_count"] == 1
        assert "any_alarm" in status
        assert "discharge_permitted" in status
        assert "marpol_compliant" in status

    # ---- pump tracking ----

    def test_bilge_pump_running_tracking(self):
        ch = self._make()
        low = ch.update_compartment("C1", 50.0)
        assert low["pump_running"] is False
        high = ch.update_compartment("C2", 70.0)
        assert high["pump_running"] is True

    # ---- boundary values ----

    def test_bilge_oil_content_boundary_15ppm(self):
        ch = self._make()
        # Exactly 15 ppm → NOT above limit → no alarm
        result = ch.update_compartment("C1", 30.0, 15.0)
        assert result["alarm_active"] is False
        comp = ch.check_marpol_compliance()
        assert comp["compliant"] is True

    def test_bilge_level_boundary_80(self):
        ch = self._make()
        # Exactly 80% → NOT above limit → no alarm
        result = ch.update_compartment("C1", 80.0, 5.0)
        assert result["alarm_active"] is False
        # 80.1% → alarm
        result2 = ch.update_compartment("C2", 80.1, 5.0)
        assert result2["alarm_active"] is True

    def test_bilge_marpol_oil_content_max(self):
        ch = self._make()
        ch.update_compartment("C1", 30.0, 5.0)
        ch.update_compartment("C2", 30.0, 12.0)
        comp = ch.check_marpol_compliance()
        assert comp["oil_content_max_ppm"] == 12.0

    def test_bilge_pump_boundary_60(self):
        ch = self._make()
        at60 = ch.update_compartment("C1", 60.0)
        assert at60["pump_running"] is False
        above60 = ch.update_compartment("C2", 60.1)
        assert above60["pump_running"] is True


# ============================================================
#  Communication Manager — 26 tests
# ============================================================

class TestCommunicationManager:
    """CommunicationManagerChannel 测试套件。"""

    def _make(self):
        ch = CommunicationManagerChannel()
        ch.initialize()
        return ch

    def _make_gmdss(self):
        """Helper: create channel with full GMDSS-compliant set."""
        ch = self._make()
        ch.add_system("VHF-1", "vhf", 156.8)
        ch.add_system("MF-1", "mf", 2182.0)
        ch.add_system("Inmarsat-C", "inmarsat", 1537.0)
        return ch

    # ---- init ----

    def test_comms_init(self):
        ch = CommunicationManagerChannel()
        assert ch.name == "communication_manager"
        assert ch._active is False
        assert ch._systems == {}
        assert ch._distress_active is False

    # ---- add_system ----

    def test_comms_add_system_vhf(self):
        ch = self._make()
        result = ch.add_system("VHF-1", "vhf", 156.8)
        assert result["system_name"] == "VHF-1"
        assert result["type"] == "vhf"
        assert result["status"] == "operational"
        assert result["signal_strength"] == 100

    def test_comms_add_system_inmarsat(self):
        ch = self._make()
        result = ch.add_system("Inmarsat-C", "inmarsat", 1537.0)
        assert result["type"] == "inmarsat"

    def test_comms_add_multiple_systems(self):
        ch = self._make()
        ch.add_system("VHF-1", "vhf")
        ch.add_system("MF-1", "mf")
        ch.add_system("Inmarsat-C", "inmarsat")
        assert len(ch._systems) == 3

    # ---- update_system_status ----

    def test_comms_update_status_operational(self):
        ch = self._make()
        ch.add_system("VHF-1", "vhf")
        result = ch.update_system_status("VHF-1", "operational", 95)
        assert result["status"] == "operational"
        assert result["signal_strength"] == 95

    def test_comms_update_status_degraded(self):
        ch = self._make()
        ch.add_system("VHF-1", "vhf")
        result = ch.update_system_status("VHF-1", "degraded", 40)
        assert result["status"] == "degraded"
        assert result["signal_strength"] == 40

    def test_comms_update_status_failed(self):
        ch = self._make()
        ch.add_system("VHF-1", "vhf")
        result = ch.update_system_status("VHF-1", "failed", 0)
        assert result["status"] == "failed"
        assert result["signal_strength"] == 0

    def test_comms_update_nonexistent(self):
        ch = self._make()
        result = ch.update_system_status("NOEXIST", "failed")
        assert "error" in result

    # ---- comms status ----

    def test_comms_status_no_systems(self):
        ch = self._make()
        status = ch.get_comms_status()
        assert status["systems"] == []
        assert status["operational_count"] == 0
        assert status["gmdss_compliant"] is False

    def test_comms_status_all_operational(self):
        ch = self._make_gmdss()
        status = ch.get_comms_status()
        assert status["operational_count"] == 3
        assert status["degraded_count"] == 0
        assert status["failed_count"] == 0

    def test_comms_status_mixed(self):
        ch = self._make_gmdss()
        ch.update_system_status("MF-1", "degraded", 30)
        ch.add_system("HF-1", "hf")
        ch.update_system_status("HF-1", "failed", 0)
        status = ch.get_comms_status()
        assert status["operational_count"] == 2  # VHF-1, Inmarsat-C
        assert status["degraded_count"] == 1     # MF-1
        assert status["failed_count"] == 1       # HF-1

    def test_comms_operational_count(self):
        ch = self._make()
        ch.add_system("VHF-1", "vhf")
        ch.add_system("VHF-2", "vhf")
        ch.update_system_status("VHF-2", "failed", 0)
        status = ch.get_comms_status()
        assert status["operational_count"] == 1

    def test_comms_degraded_count(self):
        ch = self._make()
        ch.add_system("VHF-1", "vhf")
        ch.add_system("MF-1", "mf")
        ch.update_system_status("VHF-1", "degraded", 30)
        ch.update_system_status("MF-1", "degraded", 25)
        status = ch.get_comms_status()
        assert status["degraded_count"] == 2

    def test_comms_failed_count(self):
        ch = self._make()
        ch.add_system("VHF-1", "vhf")
        ch.add_system("MF-1", "mf")
        ch.update_system_status("VHF-1", "failed", 0)
        ch.update_system_status("MF-1", "failed", 0)
        status = ch.get_comms_status()
        assert status["failed_count"] == 2

    # ---- GMDSS compliance ----

    def test_comms_gmdss_compliant(self):
        ch = self._make_gmdss()
        status = ch.get_comms_status()
        assert status["gmdss_compliant"] is True

    def test_comms_gmdss_not_compliant_no_vhf(self):
        ch = self._make()
        ch.add_system("MF-1", "mf")
        ch.add_system("Inmarsat-C", "inmarsat")
        status = ch.get_comms_status()
        assert status["gmdss_compliant"] is False

    def test_comms_gmdss_not_compliant_no_satellite(self):
        ch = self._make()
        ch.add_system("VHF-1", "vhf")
        ch.add_system("MF-1", "mf")
        status = ch.get_comms_status()
        assert status["gmdss_compliant"] is False

    def test_comms_gmdss_not_compliant_no_mf_hf(self):
        ch = self._make()
        ch.add_system("VHF-1", "vhf")
        ch.add_system("Inmarsat-C", "inmarsat")
        status = ch.get_comms_status()
        assert status["gmdss_compliant"] is False

    def test_comms_gmdss_with_hf_only(self):
        ch = self._make()
        ch.add_system("VHF-1", "vhf")
        ch.add_system("HF-1", "hf")
        ch.add_system("VSAT-1", "vsat")
        status = ch.get_comms_status()
        assert status["gmdss_compliant"] is True

    # ---- distress ----

    def test_comms_activate_distress(self):
        ch = self._make()
        result = ch.activate_distress()
        assert result["distress_active"] is True
        assert result["position"] is None
        assert ch._distress_active is True

    def test_comms_activate_distress_with_position(self):
        ch = self._make()
        pos = {"lat": 31.23, "lon": 121.47}
        result = ch.activate_distress(position=pos)
        assert result["distress_active"] is True
        assert result["position"] == pos

    def test_comms_distress_not_active_default(self):
        ch = self._make()
        assert ch._distress_active is False
        status = ch.get_status()
        assert status["distress_active"] is False

    # ---- event processing ----

    def test_comms_process_event_status(self):
        ch = self._make()
        ch.add_system("VHF-1", "vhf")
        result = _run(ch.process_event({
            "type": "comms_status_update",
            "system_name": "VHF-1",
            "status": "degraded",
            "signal_strength": 45,
        }))
        assert result["status"] == "updated"
        assert result["system"]["status"] == "degraded"
        assert result["system"]["signal_strength"] == 45

    def test_comms_process_event_distress(self):
        ch = self._make()
        result = _run(ch.process_event({
            "type": "distress_alert",
            "position": {"lat": 31.0, "lon": 121.0},
        }))
        assert result["status"] == "distress_activated"
        assert ch._distress_active is True

    def test_comms_process_event_unknown(self):
        ch = self._make()
        result = _run(ch.process_event({"type": "foo"}))
        assert result["status"] == "ignored"

    # ---- get_status ----

    def test_comms_get_status(self):
        ch = self._make_gmdss()
        status = ch.get_status()
        assert status["name"] == "communication_manager"
        assert status["active"] is True
        assert status["initialized"] is True
        assert status["systems_count"] == 3
        assert status["operational_count"] == 3
        assert status["gmdss_compliant"] is True
        assert status["distress_active"] is False
        assert "health" in status

    # ---- signal strength tracking ----

    def test_comms_signal_strength_tracking(self):
        ch = self._make()
        ch.add_system("VHF-1", "vhf")
        assert ch._systems["VHF-1"]["signal_strength"] == 100
        ch.update_system_status("VHF-1", "degraded", 55)
        assert ch._systems["VHF-1"]["signal_strength"] == 55
        ch.update_system_status("VHF-1", "operational", 90)
        assert ch._systems["VHF-1"]["signal_strength"] == 90

    def test_comms_process_event_auto_add_system(self):
        """When a comms_status_update arrives for an unknown system, it is auto-added."""
        ch = self._make()
        result = _run(ch.process_event({
            "type": "comms_status_update",
            "system_name": "NEW-SAT",
            "status": "operational",
            "signal_strength": 80,
            "frequency_mhz": 1537.0,
        }))
        assert result["status"] == "updated"
        assert "NEW-SAT" in ch._systems
