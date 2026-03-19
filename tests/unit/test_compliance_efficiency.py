# -*- coding: utf-8 -*-
"""
ComplianceReporter / EfficiencyAdvisor 单元测试
"""

import json
import pytest
from datetime import datetime, timedelta

from channels.efficiency_models import (
    VesselInfo, VesselType, FuelType, CIIRating, CIIResult,
    VoyageData, EngineData, EEXIResult, EfficiencyRecommendation,
)
from channels.compliance_reporter import ComplianceReporter
from channels.efficiency_advisor import EfficiencyAdvisor


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
def sample_voyages():
    return [
        VoyageData(
            voyage_id="V-001",
            departure_port="Shanghai",
            arrival_port="Singapore",
            departure_time=datetime(2026, 1, 1),
            arrival_time=datetime(2026, 1, 5),
            distance_nm=2200,
            fuel_consumed=350000,
            fuel_type=FuelType.HFO,
            cargo_weight=70000,
            average_speed=12.0,
        ),
        VoyageData(
            voyage_id="V-002",
            departure_port="Singapore",
            arrival_port="Rotterdam",
            departure_time=datetime(2026, 2, 1),
            arrival_time=datetime(2026, 2, 15),
            distance_nm=8400,
            fuel_consumed=1200000,
            fuel_type=FuelType.HFO,
            cargo_weight=75000,
            average_speed=13.5,
        ),
    ]


# ───────────────────── ComplianceReporter ─────────────────────


class TestComplianceReporter:
    def test_init(self, bulk_vessel):
        reporter = ComplianceReporter(bulk_vessel)
        assert reporter.vessel is bulk_vessel
        assert reporter.cii_calculator is not None
        assert reporter.eexi_calculator is not None

    def test_generate_imodcs_report_structure(self, bulk_vessel, sample_voyages):
        reporter = ComplianceReporter(bulk_vessel)
        report = reporter.generate_imodcs_report(sample_voyages, 2026)

        assert report["report_type"] == "IMO DCS"
        assert report["reporting_period"] == "2026"
        assert "vessel_info" in report
        assert report["vessel_info"]["imo_number"] == 9876543
        assert report["vessel_info"]["vessel_type"] == VesselType.BULK_CARRIER.value

    def test_generate_imodcs_report_fuel_data(self, bulk_vessel, sample_voyages):
        reporter = ComplianceReporter(bulk_vessel)
        report = reporter.generate_imodcs_report(sample_voyages, 2026)

        assert report["total_distance_nm"] > 0
        assert report["total_time_at_sea_hours"] > 0
        assert report["transport_work_dwt_nm"] > 0
        assert "fuel_consumption" in report

    def test_generate_imodcs_report_cii_result(self, bulk_vessel, sample_voyages):
        reporter = ComplianceReporter(bulk_vessel)
        report = reporter.generate_imodcs_report(sample_voyages, 2026)

        cii = report["cii_result"]
        assert "attained_cii" in cii
        assert "required_cii" in cii
        assert "rating" in cii
        assert cii["compliance_status"] in ("Compliant", "Non-compliant")

    def test_generate_imodcs_report_empty_voyages(self, bulk_vessel):
        reporter = ComplianceReporter(bulk_vessel)
        report = reporter.generate_imodcs_report([], 2026)

        assert report["total_distance_nm"] == 0.0
        assert report["total_time_at_sea_hours"] == 0.0

    def test_generate_imodcs_report_wrong_year_filtered(self, bulk_vessel, sample_voyages):
        reporter = ComplianceReporter(bulk_vessel)
        report = reporter.generate_imodcs_report(sample_voyages, 2025)

        assert report["total_distance_nm"] == 0.0

    def test_generate_eumrv_report_structure(self, bulk_vessel, sample_voyages):
        reporter = ComplianceReporter(bulk_vessel)
        report = reporter.generate_eumrv_report(sample_voyages, 2026)

        assert report["report_type"] == "EU MRV"
        assert report["reporting_period"] == "2026"
        assert report["number_of_voyages"] == 2
        assert report["submission_deadline"] == "2027-04-30"
        assert report["total_distance_nm"] > 0

    def test_generate_eumrv_report_empty_year(self, bulk_vessel, sample_voyages):
        reporter = ComplianceReporter(bulk_vessel)
        report = reporter.generate_eumrv_report(sample_voyages, 2025)

        assert report["number_of_voyages"] == 0
        assert report["total_distance_nm"] == 0

    def test_generate_annual_compliance_report(self, bulk_vessel, sample_voyages):
        reporter = ComplianceReporter(bulk_vessel)
        report = reporter.generate_annual_compliance_report(2026, sample_voyages)

        assert report.report_id.startswith("ACR-9876543-2026")
        assert report.vessel_info is bulk_vessel
        assert report.cii_result is not None
        assert report.reporting_period == "2026"
        assert isinstance(report.compliance_status, bool)

    def test_generate_annual_compliance_report_with_eexi(self, bulk_vessel, sample_voyages):
        reporter = ComplianceReporter(bulk_vessel)
        eexi = reporter.eexi_calculator.calculate_attained_eexi(
            installed_power=bulk_vessel.main_engine_power
        )
        report = reporter.generate_annual_compliance_report(
            2026, sample_voyages, eexi_result=eexi
        )

        assert report.eexi_result is not None
        assert report.eexi_result.attained_eexi > 0

    def test_export_report_to_json(self, bulk_vessel, sample_voyages):
        reporter = ComplianceReporter(bulk_vessel)
        report = reporter.generate_annual_compliance_report(2026, sample_voyages)
        json_str = reporter.export_report_to_json(report)

        parsed = json.loads(json_str)
        assert parsed["report_id"].startswith("ACR-")
        assert parsed["vessel_info"]["imo_number"] == 9876543
        assert "cii_result" in parsed
        assert isinstance(parsed["compliance_status"], bool)

    def test_export_report_to_json_valid_format(self, bulk_vessel, sample_voyages):
        reporter = ComplianceReporter(bulk_vessel)
        report = reporter.generate_annual_compliance_report(2026, sample_voyages)
        json_str = reporter.export_report_to_json(report)

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
        assert "report_type" in parsed
        assert "generation_date" in parsed


# ───────────────────── EfficiencyAdvisor ─────────────────────


class TestEfficiencyAdvisor:
    def test_init(self, bulk_vessel):
        advisor = EfficiencyAdvisor(bulk_vessel)
        assert advisor.vessel is bulk_vessel
        assert advisor.cii_calculator is not None
        assert advisor.eexi_calculator is not None

    def test_analyze_engine_data_no_data(self, bulk_vessel):
        advisor = EfficiencyAdvisor(bulk_vessel)
        result = advisor.analyze_engine_data([])
        assert result["status"] == "no_data"
        assert result["recommendations"] == []

    def test_analyze_engine_data_old_data(self, bulk_vessel):
        """Data older than time window should be excluded."""
        advisor = EfficiencyAdvisor(bulk_vessel)
        old = EngineData(
            timestamp=datetime.now() - timedelta(hours=48),
            engine_rpm=100,
            engine_load=50,
            fuel_rate=200,
        )
        result = advisor.analyze_engine_data([old], time_window_hours=24)
        assert result["status"] == "no_recent_data"

    def test_analyze_engine_data_normal(self, bulk_vessel):
        advisor = EfficiencyAdvisor(bulk_vessel)
        now = datetime.now()
        data = [
            EngineData(timestamp=now - timedelta(hours=i), engine_rpm=100, engine_load=60, fuel_rate=200)
            for i in range(5)
        ]
        result = advisor.analyze_engine_data(data, time_window_hours=24)

        assert result["status"] == "analyzed"
        assert result["data_points"] == 5
        assert result["average_rpm"] == 100
        assert result["average_load"] == 60
        assert result["average_fuel_rate"] == 200
        assert result["recommendations"] == []

    def test_analyze_engine_data_high_load_recommendation(self, bulk_vessel):
        advisor = EfficiencyAdvisor(bulk_vessel)
        now = datetime.now()
        data = [
            EngineData(timestamp=now, engine_rpm=120, engine_load=90, fuel_rate=400)
        ]
        result = advisor.analyze_engine_data(data, time_window_hours=24)

        assert result["status"] == "analyzed"
        recs = result["recommendations"]
        assert any(r["id"] == "ENG-001" for r in recs)

    def test_analyze_engine_data_high_sfc_recommendation(self, bulk_vessel):
        advisor = EfficiencyAdvisor(bulk_vessel)
        now = datetime.now()
        data = [
            EngineData(
                timestamp=now, engine_rpm=100, engine_load=60,
                fuel_rate=200, specific_fuel_consumption=210,
            )
        ]
        result = advisor.analyze_engine_data(data, time_window_hours=24)

        recs = result["recommendations"]
        assert any(r["id"] == "ENG-002" for r in recs)

    def test_analyze_engine_data_low_load_recommendation(self, bulk_vessel):
        advisor = EfficiencyAdvisor(bulk_vessel)
        now = datetime.now()
        data = [
            EngineData(timestamp=now, engine_rpm=50, engine_load=25, fuel_rate=80)
        ]
        result = advisor.analyze_engine_data(data, time_window_hours=24)

        recs = result["recommendations"]
        assert any(r["id"] == "ENG-003" for r in recs)

    def test_generate_recommendations_default(self, bulk_vessel):
        advisor = EfficiencyAdvisor(bulk_vessel)
        recs = advisor.generate_recommendations()

        assert isinstance(recs, list)
        assert len(recs) >= 3  # at least the 3 generic recommendations
        assert all(isinstance(r, EfficiencyRecommendation) for r in recs)

    def test_generate_recommendations_poor_cii(self, bulk_vessel):
        advisor = EfficiencyAdvisor(bulk_vessel)
        poor_cii = CIIResult(
            attained_cii=12.0,
            required_cii=6.0,
            cii_ratio=2.0,
            rating=CIIRating.E,
            rating_threshold=8.0,
            compliance_status=False,
            calculation_period="2026",
            total_fuel=2000000,
            total_distance=10000,
            total_co2=6228000,
            transport_work=820000000,
        )
        recs = advisor.generate_recommendations(current_cii=poor_cii)

        # Should have CII improvement rec plus generic ones
        assert len(recs) > 3
        cii_recs = [r for r in recs if r.category == "CII Improvement"]
        assert len(cii_recs) >= 1
        assert cii_recs[0].priority == "high"

    def test_generate_recommendations_moderate_cii(self, bulk_vessel):
        advisor = EfficiencyAdvisor(bulk_vessel)
        c_cii = CIIResult(
            attained_cii=5.5,
            required_cii=6.0,
            cii_ratio=0.917,
            rating=CIIRating.C,
            rating_threshold=6.0,
            compliance_status=True,
            calculation_period="2026",
            total_fuel=1550000,
            total_distance=10600,
            total_co2=4826700,
            transport_work=869200000,
        )
        recs = advisor.generate_recommendations(current_cii=c_cii)

        maintenance_recs = [r for r in recs if r.category == "CII Maintenance"]
        assert len(maintenance_recs) >= 1
        assert maintenance_recs[0].priority == "medium"

    def test_generate_recommendations_noncompliant_eexi(self, bulk_vessel):
        advisor = EfficiencyAdvisor(bulk_vessel)
        bad_eexi = EEXIResult(
            attained_eexi=10.0,
            required_eexi=8.0,
            compliance_status=False,
            margin=-25.0,
            reference_line=10.0,
            reduction_factor=0.20,
        )
        recs = advisor.generate_recommendations(current_eexi=bad_eexi)

        eexi_recs = [r for r in recs if r.category == "EEXI Compliance"]
        assert len(eexi_recs) >= 1
        assert eexi_recs[0].priority == "high"

    def test_create_action_plan_structure(self, bulk_vessel):
        advisor = EfficiencyAdvisor(bulk_vessel)
        plan = advisor.create_action_plan(budget=1000000, timeline_months=24)

        assert plan["vessel"] == "Test Bulk"
        assert plan["budget"] == 1000000
        assert plan["timeline_months"] == 24
        assert isinstance(plan["selected_measures"], list)
        assert plan["total_investment"] >= 0
        assert plan["remaining_budget"] >= 0
        assert plan["total_investment"] + plan["remaining_budget"] == plan["budget"]

    def test_create_action_plan_respects_budget(self, bulk_vessel):
        advisor = EfficiencyAdvisor(bulk_vessel)
        # With a very small budget, only zero-cost items should be selected
        plan = advisor.create_action_plan(budget=100, timeline_months=12)

        for m in plan["selected_measures"]:
            assert m["cost"] <= 100

    def test_create_action_plan_improvement_positive(self, bulk_vessel):
        advisor = EfficiencyAdvisor(bulk_vessel)
        plan = advisor.create_action_plan()

        assert plan["total_expected_improvement"] > 0
        assert len(plan["selected_measures"]) > 0
