# -*- coding: utf-8 -*-
"""Tests for LRIT Reporter and Navigational Lights channels + bus integration."""

import asyncio
import sys
import os
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src/backend"))

from channels.lrit_reporter import LRITReporterChannel
from channels.navigational_lights import NavigationalLightsChannel
from channels.alarm_management import AlarmManagementChannel
from channels.man_overboard import ManOverboardChannel
from channels.fire_detection_channel import FireDetectionChannel
from channels.marine_message_bus import MarineMessageBus, MarineMessage


# ── LRIT Reporter ──────────────────────────────────────────────


class TestLRITReporter:
    def test_init_defaults(self):
        ch = LRITReporterChannel()
        assert ch.name == "lrit_reporter"
        assert ch._reporting_interval_hours == 6.0
        assert ch._last_report_time is None
        assert len(ch._report_history) == 0

    def test_set_ship_info(self):
        ch = LRITReporterChannel()
        result = ch.set_ship_info(1234567, 412345678, "CN", "Ocean Star")
        assert result["status"] == "ship_info_set"
        assert ch._ship_info["imo_number"] == 1234567
        assert ch._ship_info["flag_state"] == "CN"

    def test_generate_report(self):
        ch = LRITReporterChannel()
        ch.set_ship_info(1234567, 412345678, "CN", "Ocean Star")
        report = ch.generate_report(31.0, 121.0)
        assert report["position"]["lat"] == 31.0
        assert report["position"]["lon"] == 121.0
        assert report["ship_info"]["imo_number"] == 1234567
        assert ch._last_report_time is not None
        assert len(ch._report_history) == 1

    def test_check_reporting_due_no_previous(self):
        ch = LRITReporterChannel()
        result = ch.check_reporting_due()
        assert result["reporting_due"] is True
        assert result["reason"] == "no_previous_report"

    def test_check_reporting_not_due(self):
        ch = LRITReporterChannel()
        ch._last_report_time = time.time()
        result = ch.check_reporting_due()
        assert result["reporting_due"] is False

    def test_check_reporting_due_after_interval(self):
        ch = LRITReporterChannel()
        ch._last_report_time = time.time() - 7 * 3600  # 7 hours ago
        result = ch.check_reporting_due()
        assert result["reporting_due"] is True

    def test_get_report_history(self):
        ch = LRITReporterChannel()
        ch.generate_report(1.0, 2.0)
        ch.generate_report(3.0, 4.0)
        history = ch.get_report_history()
        assert len(history) == 2

    def test_process_event_position_update_due(self):
        ch = LRITReporterChannel()
        result = asyncio.run(ch.process_event({"type": "lrit_position_update", "lat": 10.0, "lon": 20.0}))
        assert result["status"] == "report_generated"

    def test_process_event_position_update_not_due(self):
        ch = LRITReporterChannel()
        ch._last_report_time = time.time()
        result = asyncio.run(ch.process_event({"type": "lrit_position_update", "lat": 10.0, "lon": 20.0}))
        assert result["status"] == "not_due"

    def test_process_event_missing_coords(self):
        ch = LRITReporterChannel()
        result = asyncio.run(ch.process_event({"type": "lrit_position_update"}))
        assert result["status"] == "error"

    def test_process_event_unknown(self):
        ch = LRITReporterChannel()
        result = asyncio.run(ch.process_event({"type": "unknown"}))
        assert result["status"] == "ignored"

    def test_get_status(self):
        ch = LRITReporterChannel()
        ch.initialize()
        status = ch.get_status()
        assert status["name"] == "lrit_reporter"
        assert status["reporting_interval_hours"] == 6.0
        assert status["reports_sent"] == 0
        assert status["reporting_due"] is True


# ── Navigational Lights ─────────────────────────────────────────


class TestNavigationalLights:
    def test_init_defaults(self):
        ch = NavigationalLightsChannel()
        assert ch.name == "navigational_lights"
        assert ch._vessel_status == "underway"
        assert len(ch._lights) == 0

    def test_update_light(self):
        ch = NavigationalLightsChannel()
        result = ch.update_light("L1", "masthead", "on", 100.0)
        assert result["status"] == "updated"
        assert ch._lights["L1"]["type"] == "masthead"

    def test_set_vessel_status_valid(self):
        ch = NavigationalLightsChannel()
        result = ch.set_vessel_status("at_anchor")
        assert result["status"] == "vessel_status_set"
        assert ch._vessel_status == "at_anchor"

    def test_set_vessel_status_invalid(self):
        ch = NavigationalLightsChannel()
        result = ch.set_vessel_status("flying")
        assert result["status"] == "error"

    def test_get_light_configuration_compliant(self):
        ch = NavigationalLightsChannel()
        ch.update_light("L1", "masthead", "on")
        ch.update_light("L2", "sidelight_port", "on")
        ch.update_light("L3", "sidelight_stbd", "on")
        ch.update_light("L4", "stern", "on")
        config = ch.get_light_configuration()
        assert config["compliant"] is True
        assert len(config["missing_lights"]) == 0

    def test_get_light_configuration_missing(self):
        ch = NavigationalLightsChannel()
        ch.update_light("L1", "masthead", "on")
        config = ch.get_light_configuration()
        assert config["compliant"] is False
        assert "sidelight_port" in config["missing_lights"]

    def test_check_colreg_compliance_with_fault(self):
        ch = NavigationalLightsChannel()
        ch.update_light("L1", "masthead", "on")
        ch.update_light("L2", "sidelight_port", "on")
        ch.update_light("L3", "sidelight_stbd", "on")
        ch.update_light("L4", "stern", "fault")
        compliance = ch.check_colreg_compliance()
        assert compliance["compliant"] is False
        assert "L4" in compliance["faulty_lights"]

    def test_anchor_lights(self):
        ch = NavigationalLightsChannel()
        ch.set_vessel_status("at_anchor")
        ch.update_light("A1", "anchor", "on")
        config = ch.get_light_configuration()
        assert config["compliant"] is True

    def test_nuc_lights(self):
        ch = NavigationalLightsChannel()
        ch.set_vessel_status("nuc")
        ch.update_light("R1", "all_round_red", "on")
        ch.update_light("R2", "all_round_red", "on")
        config = ch.get_light_configuration()
        assert config["compliant"] is True

    def test_process_event_light_update(self):
        ch = NavigationalLightsChannel()
        result = asyncio.run(ch.process_event({
            "type": "light_status_update",
            "light_id": "L1",
            "light_type": "masthead",
            "status": "on",
        }))
        assert result["status"] == "updated"

    def test_process_event_vessel_status_change(self):
        ch = NavigationalLightsChannel()
        result = asyncio.run(ch.process_event({
            "type": "vessel_status_change",
            "vessel_status": "at_anchor",
        }))
        assert result["status"] == "vessel_status_set"

    def test_process_event_missing_light_id(self):
        ch = NavigationalLightsChannel()
        result = asyncio.run(ch.process_event({
            "type": "light_status_update",
            "light_type": "masthead",
        }))
        assert result["status"] == "error"

    def test_process_event_unknown(self):
        ch = NavigationalLightsChannel()
        result = asyncio.run(ch.process_event({"type": "blah"}))
        assert result["status"] == "ignored"

    def test_get_status(self):
        ch = NavigationalLightsChannel()
        ch.initialize()
        status = ch.get_status()
        assert status["name"] == "navigational_lights"
        assert status["vessel_status"] == "underway"
        assert status["light_count"] == 0


# ── Bus Integration ──────────────────────────────────────────────


class TestBusIntegration:
    def test_alarm_management_publishes_to_bus(self):
        bus = MarineMessageBus()
        ch = AlarmManagementChannel(bus=bus)
        ch.initialize()
        ch.raise_alarm("A1", "test", "alarm", "test alarm")
        assert bus._stats["messages_sent"] == 1
        assert bus._message_log[-1].subject == "alarm.raised"

    def test_alarm_management_no_bus(self):
        ch = AlarmManagementChannel()
        ch.initialize()
        result = ch.raise_alarm("A1", "test", "alarm", "test alarm")
        assert result["raised"] is True

    def test_mob_publishes_to_bus(self):
        bus = MarineMessageBus()
        ch = ManOverboardChannel(bus=bus)
        ch.initialize()
        ch.activate_mob(31.0, 121.0)
        assert bus._stats["messages_sent"] == 1
        msg = bus._message_log[-1]
        assert msg.subject == "mob.activated"

    def test_mob_no_bus(self):
        ch = ManOverboardChannel()
        ch.initialize()
        result = ch.activate_mob(31.0, 121.0)
        assert result["status"] == "mob_activated"

    def test_fire_detection_publishes_to_bus(self):
        bus = MarineMessageBus()
        ch = FireDetectionChannel(bus=bus)
        ch.initialize()
        ch._create_alarm("engine_room", "manual")
        assert bus._stats["messages_sent"] == 1
        msg = bus._message_log[-1]
        assert msg.subject == "fire.alarm"

    def test_fire_detection_no_bus(self):
        ch = FireDetectionChannel()
        ch.initialize()
        alarm = ch._create_alarm("bridge", "manual")
        assert alarm["alarm_id"] == "FIRE-0001"
