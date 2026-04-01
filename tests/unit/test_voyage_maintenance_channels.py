# -*- coding: utf-8 -*-
"""
Unit tests for VoyageDataAnalyzerChannel and MaintenancePlannerChannel.
"""

import asyncio

import pytest

from backend.channels.voyage_data_analyzer import VoyageDataAnalyzerChannel
from backend.channels.maintenance_planner import MaintenancePlannerChannel


def run(coro):
    return asyncio.run(coro)


# ============================================================
# VoyageDataAnalyzerChannel Tests
# ============================================================

class TestVoyageInstantiation:

    def test_default_state(self):
        ch = VoyageDataAnalyzerChannel()
        assert ch.name == "voyage_data_analyzer"
        assert ch._voyage is None
        assert ch._kpi_data["distance_nm"] == 0.0

    def test_initialize(self):
        ch = VoyageDataAnalyzerChannel()
        assert ch.initialize() is True
        assert ch._active is True
        assert ch._initialized is True

    def test_shutdown(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        assert ch.shutdown() is True
        assert ch._active is False

    def test_get_status_no_voyage(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        status = ch.get_status()
        assert status["name"] == "voyage_data_analyzer"
        assert status["active_voyage"] is False
        assert status["voyage_id"] is None


class TestVoyageLifecycle:

    def test_start_voyage(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        result = ch.start_voyage("V001", "Shanghai", "Singapore", eta="2026-04-01")
        assert result["status"] == "voyage_started"
        assert result["voyage"]["voyage_id"] == "V001"
        assert result["voyage"]["departure_port"] == "Shanghai"
        assert ch._voyage is not None

    def test_end_voyage(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        ch.start_voyage("V001", "Shanghai", "Singapore")
        ch.update_kpi(distance_nm=100, fuel_mt=5)
        result = ch.end_voyage()
        assert result["status"] == "voyage_ended"
        assert result["kpi"]["distance_nm"] == 100.0
        assert result["fuel_efficiency"] == pytest.approx(0.05)
        assert ch._voyage is None

    def test_end_voyage_no_active(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        result = ch.end_voyage()
        assert result["status"] == "error"


class TestVoyageKPI:

    def test_update_kpi_distance(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        ch.start_voyage("V001", "A", "B")
        result = ch.update_kpi(distance_nm=50)
        assert result["kpi"]["distance_nm"] == 50.0

    def test_update_kpi_fuel(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        ch.start_voyage("V001", "A", "B")
        ch.update_kpi(fuel_mt=3)
        ch.update_kpi(fuel_mt=2)
        assert ch._kpi_data["fuel_consumed_mt"] == 5.0

    def test_update_kpi_speed(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        ch.start_voyage("V001", "A", "B")
        ch.update_kpi(distance_nm=50, speed_knots=12)
        ch.update_kpi(distance_nm=50, speed_knots=14)
        assert ch._kpi_data["max_speed_knots"] == 14.0
        assert ch._kpi_data["avg_speed_knots"] > 0

    def test_fuel_efficiency_zero_distance(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        ch.start_voyage("V001", "A", "B")
        kpi = ch.get_voyage_kpi()
        assert kpi["fuel_efficiency"] is None

    def test_fuel_efficiency_normal(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        ch.start_voyage("V001", "A", "B")
        ch.update_kpi(distance_nm=200, fuel_mt=10)
        kpi = ch.get_voyage_kpi()
        assert kpi["fuel_efficiency"] == pytest.approx(0.05)

    def test_voyage_progress_with_total_distance(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        ch.start_voyage("V001", "A", "B")
        ch._voyage["total_distance"] = 1000
        ch.update_kpi(distance_nm=250)
        kpi = ch.get_voyage_kpi()
        assert kpi["voyage_progress_percent"] == pytest.approx(25.0)

    def test_voyage_progress_without_total_distance(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        ch.start_voyage("V001", "A", "B")
        ch.update_kpi(distance_nm=100)
        kpi = ch.get_voyage_kpi()
        assert kpi["voyage_progress_percent"] is None

    def test_estimated_arrival_uses_eta(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        ch.start_voyage("V001", "A", "B", eta="2026-05-01")
        kpi = ch.get_voyage_kpi()
        assert kpi["estimated_arrival"] == "2026-05-01"

    def test_get_voyage_kpi_structure(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        ch.start_voyage("V001", "A", "B")
        kpi = ch.get_voyage_kpi()
        assert "voyage_info" in kpi
        assert "kpi" in kpi
        assert "fuel_efficiency" in kpi
        assert "estimated_arrival" in kpi
        assert "voyage_progress_percent" in kpi


class TestVoyageEvents:

    def test_voyage_start_event(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        result = run(ch.process_event({
            "type": "voyage_start",
            "voyage_id": "V100",
            "departure_port": "Busan",
            "arrival_port": "Rotterdam",
            "eta": "2026-06-01",
        }))
        assert result["status"] == "voyage_started"
        assert ch._voyage["voyage_id"] == "V100"

    def test_voyage_end_event(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        ch.start_voyage("V100", "A", "B")
        result = run(ch.process_event({"type": "voyage_end"}))
        assert result["status"] == "voyage_ended"

    def test_kpi_update_event(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        ch.start_voyage("V100", "A", "B")
        result = run(ch.process_event({
            "type": "kpi_update",
            "distance_nm": 30,
            "fuel_mt": 1.5,
            "speed_knots": 11,
        }))
        assert result["status"] == "kpi_updated"
        assert result["kpi"]["distance_nm"] == 30.0

    def test_unknown_event(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        result = run(ch.process_event({"type": "unknown_xyz"}))
        assert result["status"] == "ignored"


class TestVoyageStartStop:

    def test_start_stop(self):
        ch = VoyageDataAnalyzerChannel()
        ch.initialize()
        run(ch.start())
        assert ch._active is True
        run(ch.stop())
        assert ch._active is False


# ============================================================
# MaintenancePlannerChannel Tests
# ============================================================

class TestMaintenanceInstantiation:

    def test_default_state(self):
        ch = MaintenancePlannerChannel()
        assert ch.name == "maintenance_planner"
        assert ch._equipment == {}
        assert ch._work_orders == []

    def test_initialize(self):
        ch = MaintenancePlannerChannel()
        assert ch.initialize() is True
        assert ch._active is True

    def test_shutdown(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        assert ch.shutdown() is True
        assert ch._active is False

    def test_get_status_empty(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        status = ch.get_status()
        assert status["name"] == "maintenance_planner"
        assert status["total_equipment"] == 0
        assert status["due_count"] == 0
        assert status["overdue_count"] == 0
        assert status["open_work_orders"] == 0


class TestEquipmentRegistration:

    def test_register_equipment(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        result = ch.register_equipment("E001", "Main Engine", "engine")
        assert result["status"] == "registered"
        assert result["equipment"]["equip_id"] == "E001"
        assert result["equipment"]["status"] == "ok"
        assert "E001" in ch._equipment

    def test_register_with_custom_interval(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        result = ch.register_equipment("E002", "Radar", "navigation", maintenance_interval_hours=250)
        assert result["equipment"]["maintenance_interval_hours"] == 250


class TestRunningHoursUpdate:

    def test_update_hours_ok(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        ch.register_equipment("E001", "Main Engine", "engine", maintenance_interval_hours=500)
        result = ch.update_running_hours("E001", 400)
        assert result["status"] == "updated"
        assert result["equipment"]["status"] == "ok"

    def test_update_hours_due(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        ch.register_equipment("E001", "Main Engine", "engine", maintenance_interval_hours=500)
        result = ch.update_running_hours("E001", 500)
        assert result["equipment"]["status"] == "maintenance_due"

    def test_update_hours_overdue(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        ch.register_equipment("E001", "Main Engine", "engine", maintenance_interval_hours=500)
        # 超过 10% → overdue: 500 * 1.1 = 550
        result = ch.update_running_hours("E001", 560)
        assert result["equipment"]["status"] == "overdue"

    def test_update_hours_not_found(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        result = ch.update_running_hours("MISSING", 100)
        assert result["status"] == "error"

    def test_after_maintenance_reset(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        ch.register_equipment("E001", "ME", "engine", maintenance_interval_hours=500)
        ch.update_running_hours("E001", 500)
        assert ch._equipment["E001"]["status"] == "maintenance_due"
        ch.record_maintenance("E001")
        assert ch._equipment["E001"]["status"] == "ok"
        assert ch._equipment["E001"]["last_maintenance_hours"] == 500


class TestRecordMaintenance:

    def test_record_maintenance_resets(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        ch.register_equipment("E001", "ME", "engine", maintenance_interval_hours=100)
        ch.update_running_hours("E001", 100)
        result = ch.record_maintenance("E001")
        assert result["status"] == "maintenance_recorded"
        assert result["equipment"]["last_maintenance_hours"] == 100
        assert result["equipment"]["status"] == "ok"

    def test_record_maintenance_not_found(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        result = ch.record_maintenance("MISSING")
        assert result["status"] == "error"


class TestWorkOrders:

    def test_create_work_order(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        result = ch.create_work_order("E001", "Replace filter", priority=2)
        assert result["status"] == "work_order_created"
        assert result["work_order"]["equip_id"] == "E001"
        assert result["work_order"]["priority"] == 2
        assert result["work_order"]["status"] == "open"
        assert len(ch._work_orders) == 1

    def test_priority_clamped(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        r1 = ch.create_work_order("E1", "a", priority=0)
        assert r1["work_order"]["priority"] == 1
        r2 = ch.create_work_order("E1", "b", priority=10)
        assert r2["work_order"]["priority"] == 5


class TestMaintenanceSummary:

    def test_summary_counts(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        ch.register_equipment("E1", "A", "engine", 100)
        ch.register_equipment("E2", "B", "navigation", 200)
        ch.register_equipment("E3", "C", "safety", 50)
        ch.update_running_hours("E1", 100)   # due
        ch.update_running_hours("E2", 250)   # overdue (200*1.1=220 < 250)
        ch.create_work_order("E1", "Fix")
        summary = ch.get_maintenance_summary()
        assert summary["total_equipment"] == 3
        assert summary["due_count"] == 1
        assert summary["overdue_count"] == 1
        assert summary["open_work_orders"] == 1
        assert summary["next_maintenance"] is not None

    def test_next_maintenance_closest(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        ch.register_equipment("E1", "A", "engine", 500)
        ch.register_equipment("E2", "B", "engine", 100)
        ch.update_running_hours("E1", 100)  # 400 remaining
        ch.update_running_hours("E2", 50)   # 50 remaining
        summary = ch.get_maintenance_summary()
        assert summary["next_maintenance"]["equip_id"] == "E2"


class TestMaintenanceEvents:

    def test_equipment_update_event(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        ch.register_equipment("E1", "ME", "engine", 500)
        result = run(ch.process_event({
            "type": "equipment_update",
            "equip_id": "E1",
            "running_hours": 500,
        }))
        assert result["status"] == "updated"

    def test_maintenance_complete_event(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        ch.register_equipment("E1", "ME", "engine", 500)
        ch.update_running_hours("E1", 500)
        result = run(ch.process_event({
            "type": "maintenance_complete",
            "equip_id": "E1",
        }))
        assert result["status"] == "maintenance_recorded"

    def test_work_order_event(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        result = run(ch.process_event({
            "type": "work_order",
            "equip_id": "E1",
            "description": "Oil change",
            "priority": 4,
        }))
        assert result["status"] == "work_order_created"

    def test_unknown_event(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        result = run(ch.process_event({"type": "xyz"}))
        assert result["status"] == "ignored"

    def test_equipment_update_missing_fields(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        result = run(ch.process_event({"type": "equipment_update"}))
        assert result["status"] == "error"

    def test_maintenance_complete_missing_id(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        result = run(ch.process_event({"type": "maintenance_complete"}))
        assert result["status"] == "error"


class TestMaintenanceStartStop:

    def test_start_stop(self):
        ch = MaintenancePlannerChannel()
        ch.initialize()
        run(ch.start())
        assert ch._active is True
        run(ch.stop())
        assert ch._active is False
