# -*- coding: utf-8 -*-
"""
EEXI / CII / SEEMP 计算器单元测试
"""

import pytest
from datetime import datetime

from channels.efficiency_models import (
    VesselInfo, VesselType, FuelType, CIIRating,
    VoyageData, EnergySavingMeasureType,
)
from channels.eexi_calculator import EEXICalculator
from channels.cii_calculator import CIICalculator
from channels.seemp_manager import SEEMPManager


@pytest.fixture()
def bulk_vessel():
    return VesselInfo(
        imo_number=9876543,
        vessel_name="Test Bulk",
        vessel_type=VesselType.BULK_CARRIER,
        dwt=82000,
        gross_tonnage=43500,
        length=229,
        beam=32,
        draft=14.5,
        main_engine_power=14280,
        fuel_type=FuelType.HFO,
        built_year=2015,
    )


@pytest.fixture()
def sample_voyage():
    return VoyageData(
        voyage_id="V-001",
        departure_port="Shanghai",
        arrival_port="Singapore",
        departure_time=datetime(2026, 1, 1),
        arrival_time=datetime(2026, 1, 5),
        distance_nm=2200,
        fuel_consumed=350,
        fuel_type=FuelType.HFO,
        cargo_weight=70000,
        average_speed=12.0,
    )


# ────────────────── EEXI Calculator ──────────────────


class TestEEXICalculator:
    def test_init(self, bulk_vessel):
        calc = EEXICalculator(bulk_vessel)
        assert calc.vessel is bulk_vessel

    def test_reference_line(self, bulk_vessel):
        calc = EEXICalculator(bulk_vessel)
        ref = calc.calculate_reference_line(bulk_vessel.dwt)
        assert isinstance(ref, float)
        assert ref > 0

    def test_reference_speed(self, bulk_vessel):
        calc = EEXICalculator(bulk_vessel)
        speed = calc.calculate_reference_speed(bulk_vessel.dwt)
        assert isinstance(speed, float)
        assert speed > 0

    def test_reduction_factor(self, bulk_vessel):
        calc = EEXICalculator(bulk_vessel)
        factor = calc.get_reduction_factor()
        assert 0 <= factor <= 1

    def test_attained_eexi(self, bulk_vessel):
        calc = EEXICalculator(bulk_vessel)
        result = calc.calculate_attained_eexi(
            installed_power=14280,
            specific_fuel_consumption=180.0,
        )
        assert result.attained_eexi > 0
        assert result.required_eexi > 0
        assert isinstance(result.compliance_status, bool)
        assert result.calculation_date is not None

    def test_required_power_for_compliance(self, bulk_vessel):
        calc = EEXICalculator(bulk_vessel)
        max_power = calc.calculate_required_power_for_compliance()
        assert isinstance(max_power, float)
        assert max_power > 0

    def test_compliance_margin(self, bulk_vessel):
        calc = EEXICalculator(bulk_vessel)
        result = calc.calculate_attained_eexi(installed_power=14280)
        assert hasattr(result, "margin")


# ────────────────── CII Calculator ──────────────────


class TestCIICalculator:
    def test_init(self, bulk_vessel):
        calc = CIICalculator(bulk_vessel)
        assert calc.vessel is bulk_vessel

    def test_reference_line(self, bulk_vessel):
        calc = CIICalculator(bulk_vessel)
        ref = calc.get_reference_line()
        assert isinstance(ref, float)
        assert ref > 0

    def test_required_cii(self, bulk_vessel):
        calc = CIICalculator(bulk_vessel)
        req = calc.get_required_cii(2026)
        assert isinstance(req, float)
        assert req > 0

    def test_calculate_cii_from_fuel(self, bulk_vessel):
        calc = CIICalculator(bulk_vessel)
        result = calc.calculate_cii(
            total_fuel=3000,
            total_distance=15000,
            year=2026,
        )
        assert result.attained_cii > 0
        assert result.required_cii > 0
        assert result.rating in CIIRating
        assert result.cii_ratio > 0

    def test_calculate_cii_from_voyages(self, bulk_vessel, sample_voyage):
        calc = CIICalculator(bulk_vessel)
        result = calc.calculate_cii_from_voyages([sample_voyage], 2026)
        assert result.attained_cii > 0
        assert result.rating in CIIRating

    def test_rating_thresholds(self, bulk_vessel):
        calc = CIICalculator(bulk_vessel)
        # Very low fuel → A rating
        result = calc.calculate_cii(total_fuel=100, total_distance=50000, year=2026)
        assert result.rating in {CIIRating.A, CIIRating.B}


# ────────────────── SEEMP Manager ──────────────────


class TestSEEMPManager:
    def test_init(self, bulk_vessel):
        mgr = SEEMPManager(bulk_vessel)
        assert mgr.vessel is bulk_vessel

    def test_create_measure(self, bulk_vessel):
        mgr = SEEMPManager(bulk_vessel)
        m = mgr.create_measure(EnergySavingMeasureType.SPEED_OPTIMIZATION)
        assert m.measure_id
        assert m.measure_type == EnergySavingMeasureType.SPEED_OPTIMIZATION
        assert m.expected_savings >= 0

    def test_combined_savings(self, bulk_vessel):
        mgr = SEEMPManager(bulk_vessel)
        m1 = mgr.create_measure(EnergySavingMeasureType.SPEED_OPTIMIZATION)
        m2 = mgr.create_measure(EnergySavingMeasureType.HULL_CLEANING)
        # Mark as completed so they count
        mgr.update_measure_status(m1.measure_id, "completed")
        mgr.update_measure_status(m2.measure_id, "completed")
        savings = mgr.calculate_combined_savings()
        assert isinstance(savings, float)
        assert savings > 0

    def test_three_year_plan(self, bulk_vessel):
        mgr = SEEMPManager(bulk_vessel)
        mgr.create_measure(EnergySavingMeasureType.SPEED_OPTIMIZATION)
        plan = mgr.get_three_year_plan(start_year=2026)
        assert isinstance(plan, dict)

    def test_export_json(self, bulk_vessel):
        mgr = SEEMPManager(bulk_vessel)
        mgr.create_measure(EnergySavingMeasureType.SPEED_OPTIMIZATION)
        json_str = mgr.export_to_json()
        import json
        data = json.loads(json_str)
        assert "measures" in data or isinstance(data, list)

    def test_verification_report(self, bulk_vessel):
        mgr = SEEMPManager(bulk_vessel)
        mgr.create_measure(EnergySavingMeasureType.HULL_CLEANING)
        report = mgr.generate_verification_report()
        assert isinstance(report, dict)
