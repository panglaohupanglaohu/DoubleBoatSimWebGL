# -*- coding: utf-8 -*-
"""Tests for ballast_water_monitor, emission_monitor, anchor_watch_channel and EEXI fixes."""

import asyncio
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src/backend"))

import pytest
from channels.ballast_water_monitor import BallastWaterMonitorChannel
from channels.emission_monitor import EmissionMonitorChannel
from channels.anchor_watch_channel import AnchorWatchChannel, _haversine_m
from channels.eexi_calculator import EEXICalculator
from channels.efficiency_models import VesselInfo, VesselType, FuelType, EEXIResult


# ============================================================================
# Helpers
# ============================================================================

def _run(coro):
    return asyncio.run(coro)


def _make_vessel(vessel_type=VesselType.BULK_CARRIER, dwt=82000, built_year=2015):
    return VesselInfo(
        imo_number=9876543,
        vessel_name="TestVessel",
        vessel_type=vessel_type,
        dwt=dwt,
        gross_tonnage=43500,
        length=229,
        beam=32,
        draft=14.5,
        main_engine_power=14280,
        fuel_type=FuelType.HFO,
        built_year=built_year,
    )


# ============================================================================
# EEXI 修复测试 (任务 1 & 2)
# ============================================================================

class TestEEXICoefficients:
    """验证 EEXI 参考线系数已修正为 IMO MEPC.333(76) 值。"""

    def test_bulk_carrier_coefficient_a(self):
        coeffs = EEXICalculator.REFERENCE_LINE_COEFFICIENTS[VesselType.BULK_CARRIER]
        assert coeffs["a"] == pytest.approx(961.79, abs=0.01)

    def test_bulk_carrier_coefficient_b(self):
        coeffs = EEXICalculator.REFERENCE_LINE_COEFFICIENTS[VesselType.BULK_CARRIER]
        assert coeffs["b"] == pytest.approx(-0.477, abs=0.001)

    def test_general_cargo_coefficient_a(self):
        coeffs = EEXICalculator.REFERENCE_LINE_COEFFICIENTS[VesselType.GENERAL_CARGO]
        assert coeffs["a"] == pytest.approx(107.48, abs=0.01)

    def test_general_cargo_coefficient_b(self):
        coeffs = EEXICalculator.REFERENCE_LINE_COEFFICIENTS[VesselType.GENERAL_CARGO]
        assert coeffs["b"] == pytest.approx(-0.216, abs=0.001)

    def test_lng_carrier_coefficient_a(self):
        coeffs = EEXICalculator.REFERENCE_LINE_COEFFICIENTS[VesselType.LNG_CARRIER]
        assert coeffs["a"] == pytest.approx(2253.7, abs=0.1)

    def test_lpg_carrier_coefficient_a(self):
        coeffs = EEXICalculator.REFERENCE_LINE_COEFFICIENTS[VesselType.LPG_CARRIER]
        assert coeffs["a"] == pytest.approx(3025.2, abs=0.1)

    def test_refrigerated_cargo_coefficient_a(self):
        coeffs = EEXICalculator.REFERENCE_LINE_COEFFICIENTS[VesselType.REFRIGERATED_CARGO]
        assert coeffs["a"] == pytest.approx(4600.0, abs=0.1)

    def test_chemical_tanker_same_as_oil_tanker(self):
        chem = EEXICalculator.REFERENCE_LINE_COEFFICIENTS[VesselType.CHEMICAL_TANKER]
        oil = EEXICalculator.REFERENCE_LINE_COEFFICIENTS[VesselType.OIL_TANKER]
        assert chem["a"] == oil["a"]
        assert chem["b"] == oil["b"]

    def test_oil_tanker_coefficient(self):
        coeffs = EEXICalculator.REFERENCE_LINE_COEFFICIENTS[VesselType.OIL_TANKER]
        assert coeffs["a"] == pytest.approx(1218.80, abs=0.01)

    def test_container_ship_unchanged(self):
        coeffs = EEXICalculator.REFERENCE_LINE_COEFFICIENTS[VesselType.CONTAINER_SHIP]
        assert coeffs["a"] == pytest.approx(174.22, abs=0.01)
        assert coeffs["b"] == pytest.approx(-0.201, abs=0.001)


class TestEEXICorrectionFactors:
    """验证 calculate_attained_eexi 可接受修正系数参数。"""

    def test_default_parameters_backward_compatible(self):
        calc = EEXICalculator(_make_vessel())
        result = calc.calculate_attained_eexi(installed_power=12000)
        assert result.attained_eexi > 0
        assert result.required_eexi > 0

    def test_fj_increases_eexi(self):
        calc = EEXICalculator(_make_vessel())
        base = calc.calculate_attained_eexi(installed_power=12000)
        higher = calc.calculate_attained_eexi(installed_power=12000, fj=1.5)
        assert higher.attained_eexi > base.attained_eexi

    def test_fi_increases_denominator(self):
        calc = EEXICalculator(_make_vessel())
        base = calc.calculate_attained_eexi(installed_power=12000)
        lower = calc.calculate_attained_eexi(installed_power=12000, fi=2.0)
        assert lower.attained_eexi < base.attained_eexi

    def test_feff_reduces_eexi(self):
        calc = EEXICalculator(_make_vessel())
        base = calc.calculate_attained_eexi(installed_power=12000)
        reduced = calc.calculate_attained_eexi(installed_power=12000, feff=2000.0)
        assert reduced.attained_eexi < base.attained_eexi

    def test_feff_cannot_exceed_power(self):
        calc = EEXICalculator(_make_vessel())
        result = calc.calculate_attained_eexi(installed_power=12000, feff=20000.0)
        # effective power clamped to 0 → attained_eexi == 0
        assert result.attained_eexi == pytest.approx(0.0)


# ============================================================================
# BallastWaterMonitorChannel 测试 (任务 3)
# ============================================================================

class TestBallastWaterMonitor:
    def _make_channel(self):
        ch = BallastWaterMonitorChannel()
        ch.initialize()
        return ch

    def test_init_and_status(self):
        ch = self._make_channel()
        status = ch.get_status()
        assert status["name"] == "ballast_water"
        assert status["active"] is True
        assert status["tanks"] == []
        assert status["compliance_status"]["compliant"] is True

    def test_tank_status_event(self):
        ch = self._make_channel()
        result = _run(ch.process_event({
            "type": "tank_status", "tank_id": "T1",
            "level_percent": 80, "salinity": 35, "temperature": 18, "treated": True,
        }))
        assert result["status"] == "processed"
        assert len(ch.get_status()["tanks"]) == 1

    def test_tank_status_missing_id(self):
        ch = self._make_channel()
        result = _run(ch.process_event({"type": "tank_status"}))
        assert result["status"] == "error"

    def test_treatment_event_completes(self):
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "tank_status", "tank_id": "T1", "level_percent": 50, "treated": False,
        }))
        _run(ch.process_event({
            "type": "treatment_event", "tank_id": "T1", "method": "UV", "status": "completed",
        }))
        assert ch._tanks["T1"]["treated"] is True

    def test_exchange_record(self):
        ch = self._make_channel()
        result = _run(ch.process_event({
            "type": "exchange_record", "tank_id": "T1",
            "position_lat": 31.0, "position_lon": 122.0, "volume_m3": 500,
        }))
        assert result["status"] == "processed"

    def test_exchange_record_missing_position(self):
        ch = self._make_channel()
        result = _run(ch.process_event({
            "type": "exchange_record", "tank_id": "T1",
        }))
        assert result["status"] == "error"

    def test_compliance_untreated_tanks(self):
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "tank_status", "tank_id": "T1", "level_percent": 80, "treated": False,
        }))
        compliance = ch.check_bwm_compliance()
        assert compliance["compliant"] is False
        assert "T1" in compliance["untreated_tanks"]

    def test_shutdown(self):
        ch = self._make_channel()
        ch.shutdown()
        assert ch._active is False

    def test_unknown_event(self):
        ch = self._make_channel()
        result = _run(ch.process_event({"type": "unknown"}))
        assert result["status"] == "ignored"


# ============================================================================
# EmissionMonitorChannel 测试 (任务 4)
# ============================================================================

class TestEmissionMonitor:
    def _make_channel(self):
        ch = EmissionMonitorChannel()
        ch.initialize()
        return ch

    def test_init_and_status(self):
        ch = self._make_channel()
        status = ch.get_status()
        assert status["name"] == "emission_monitor"
        assert status["active"] is True

    def test_exhaust_reading(self):
        ch = self._make_channel()
        result = _run(ch.process_event({
            "type": "exhaust_reading",
            "nox_ppm": 200, "sox_ppm": 50, "co2_percent": 5.2, "particulate_mg_m3": 0.5,
        }))
        assert result["status"] == "processed"
        assert result["emissions"]["nox_ppm"] == 200

    def test_fuel_switch(self):
        ch = self._make_channel()
        result = _run(ch.process_event({
            "type": "fuel_switch", "from_fuel": "HFO", "to_fuel": "MGO",
        }))
        assert result["status"] == "processed"
        assert ch._fuel_type == "MGO"

    def test_fuel_switch_missing_to_fuel(self):
        ch = self._make_channel()
        result = _run(ch.process_event({"type": "fuel_switch"}))
        assert result["status"] == "error"

    def test_eca_entry(self):
        ch = self._make_channel()
        result = _run(ch.process_event({
            "type": "eca_entry", "region": "Baltic Sea",
            "entry_time": "2026-01-01T10:00:00", "applicable_limit": 0.10,
        }))
        assert result["status"] == "processed"
        assert ch._in_eca is True

    def test_eca_entry_missing_region(self):
        ch = self._make_channel()
        result = _run(ch.process_event({"type": "eca_entry"}))
        assert result["status"] == "error"

    def test_eca_compliance_hfo_in_eca(self):
        ch = self._make_channel()
        ch._fuel_type = "HFO"
        ch._in_eca = True
        compliance = ch.check_eca_compliance()
        assert compliance["compliant"] is False

    def test_eca_compliance_mgo_in_eca(self):
        ch = self._make_channel()
        ch._fuel_type = "MGO"
        ch._in_eca = True
        compliance = ch.check_eca_compliance()
        assert compliance["compliant"] is True

    def test_global_compliance_vlsfo(self):
        ch = self._make_channel()
        ch._fuel_type = "VLSFO"
        ch._in_eca = False
        compliance = ch.check_eca_compliance()
        assert compliance["compliant"] is True

    def test_shutdown(self):
        ch = self._make_channel()
        ch.shutdown()
        assert ch._active is False

    def test_unknown_event(self):
        ch = self._make_channel()
        result = _run(ch.process_event({"type": "xyz"}))
        assert result["status"] == "ignored"


# ============================================================================
# AnchorWatchChannel 测试 (任务 5)
# ============================================================================

class TestAnchorWatch:
    def _make_channel(self):
        ch = AnchorWatchChannel()
        ch.initialize()
        return ch

    def test_init_and_status(self):
        ch = self._make_channel()
        status = ch.get_status()
        assert status["name"] == "anchor_watch"
        assert status["anchored"] is False
        assert status["alarm_status"] == "normal"

    def test_anchor_drop(self):
        ch = self._make_channel()
        result = _run(ch.process_event({
            "type": "anchor_drop",
            "position_lat": 31.0, "position_lon": 122.0,
            "depth": 20.0, "chain_length": 100.0,
        }))
        assert result["status"] == "processed"
        assert result["anchored"] is True
        assert result["swing_radius"] > 0

    def test_anchor_drop_missing_position(self):
        ch = self._make_channel()
        result = _run(ch.process_event({"type": "anchor_drop"}))
        assert result["status"] == "error"

    def test_position_update_no_drift(self):
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "anchor_drop",
            "position_lat": 31.0, "position_lon": 122.0,
            "depth": 20.0, "chain_length": 100.0,
        }))
        result = _run(ch.process_event({
            "type": "position_update", "lat": 31.0, "lon": 122.0,
        }))
        assert result["dragging"] is False

    def test_position_update_dragging(self):
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "anchor_drop",
            "position_lat": 31.0, "position_lon": 122.0,
            "depth": 20.0, "chain_length": 100.0,
        }))
        # Move far away → should trigger dragging
        result = _run(ch.process_event({
            "type": "position_update", "lat": 32.0, "lon": 123.0,
        }))
        assert result["dragging"] is True
        assert ch._alarm_status == "dragging"

    def test_position_update_missing_coords(self):
        ch = self._make_channel()
        result = _run(ch.process_event({"type": "position_update"}))
        assert result["status"] == "error"

    def test_anchor_weigh(self):
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "anchor_drop",
            "position_lat": 31.0, "position_lon": 122.0,
            "depth": 20.0, "chain_length": 100.0,
        }))
        result = _run(ch.process_event({"type": "anchor_weigh"}))
        assert result["anchored"] is False
        assert ch._anchored is False

    def test_check_dragging_not_anchored(self):
        ch = self._make_channel()
        result = ch.check_dragging()
        assert result["dragging"] is False

    def test_swing_radius_calculation(self):
        radius = AnchorWatchChannel._calculate_swing_radius(20.0, 100.0)
        expected = math.sqrt(100.0**2 - 20.0**2)
        assert radius == pytest.approx(expected, rel=1e-6)

    def test_swing_radius_chain_shorter_than_depth(self):
        radius = AnchorWatchChannel._calculate_swing_radius(50.0, 30.0)
        assert radius == 30.0  # clamped to chain_length

    def test_haversine_zero(self):
        assert _haversine_m(0, 0, 0, 0) == pytest.approx(0.0)

    def test_shutdown(self):
        ch = self._make_channel()
        ch.shutdown()
        assert ch._active is False

    def test_unknown_event(self):
        ch = self._make_channel()
        result = _run(ch.process_event({"type": "something_else"}))
        assert result["status"] == "ignored"

    def test_position_update_not_anchored(self):
        ch = self._make_channel()
        result = _run(ch.process_event({
            "type": "position_update", "lat": 31.0, "lon": 122.0,
        }))
        assert result["status"] == "processed"
        assert result["dragging"] is False
