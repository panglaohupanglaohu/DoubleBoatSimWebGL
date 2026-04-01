# -*- coding: utf-8 -*-
"""
Unit tests for CargoMonitorChannel and FireDetectionChannel.
"""

import asyncio

import pytest

from backend.channels.cargo_monitor import CargoMonitorChannel
from backend.channels.fire_detection_channel import FireDetectionChannel


def run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.run(coro)


# ============================================================
# CargoMonitorChannel Tests
# ============================================================

class TestCargoMonitorInstantiation:
    """实例化和默认状态。"""

    def test_default_state(self):
        ch = CargoMonitorChannel()
        assert ch.name == "cargo_monitor"
        assert ch._active is False
        assert ch._holds == {}
        assert ch._loading_events == []

    def test_initialize_activates(self):
        ch = CargoMonitorChannel()
        assert ch.initialize() is True
        assert ch._active is True
        assert ch._initialized is True

    def test_shutdown(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        assert ch.shutdown() is True
        assert ch._active is False
        assert ch._initialized is False

    def test_custom_config(self):
        ch = CargoMonitorChannel(config={"beam": 30.0, "draft": 6.0, "lightship_weight": 20000.0})
        assert ch._beam == 30.0
        assert ch._draft == 6.0
        assert ch._lightship_weight == 20000.0

    def test_get_status_empty(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        status = ch.get_status()
        assert status["name"] == "cargo_monitor"
        assert status["active"] is True
        assert status["total_weight"] == 0.0
        assert status["holds"] == []


class TestCargoStatus:
    """cargo_status 事件 — 记录货舱。"""

    def test_cargo_status_records_hold(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        result = run(ch.process_event({
            "type": "cargo_status",
            "hold_id": "H1",
            "cargo_type": "iron_ore",
            "weight_tons": 500.0,
            "temperature": 25.0,
            "humidity": 60.0,
        }))
        assert result["status"] == "updated"
        assert result["hold_id"] == "H1"
        assert "H1" in ch._holds
        assert ch._holds["H1"]["cargo_type"] == "iron_ore"
        assert ch._holds["H1"]["weight_tons"] == 500.0

    def test_cargo_status_missing_hold_id(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        result = run(ch.process_event({"type": "cargo_status"}))
        assert result["status"] == "error"
        assert "hold_id" in result["reason"]

    def test_cargo_status_defaults(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        run(ch.process_event({"type": "cargo_status", "hold_id": "H2"}))
        hold = ch._holds["H2"]
        assert hold["cargo_type"] == "unknown"
        assert hold["weight_tons"] == 0.0

    def test_unknown_event_ignored(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        result = run(ch.process_event({"type": "bogus_event"}))
        assert result["status"] == "ignored"


class TestLoadingEvent:
    """loading_event — 装货/卸货重量变化。"""

    def _setup_hold(self, ch, hold_id="H1", weight=1000.0):
        run(ch.process_event({
            "type": "cargo_status",
            "hold_id": hold_id,
            "weight_tons": weight,
        }))

    def test_load_increases_weight(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        self._setup_hold(ch, "H1", 1000.0)
        result = run(ch.process_event({
            "type": "loading_event",
            "hold_id": "H1",
            "operation": "load",
            "weight_change": 200.0,
        }))
        assert result["status"] == "recorded"
        assert ch._holds["H1"]["weight_tons"] == 1200.0

    def test_unload_decreases_weight(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        self._setup_hold(ch, "H1", 1000.0)
        run(ch.process_event({
            "type": "loading_event",
            "hold_id": "H1",
            "operation": "unload",
            "weight_change": 300.0,
        }))
        assert ch._holds["H1"]["weight_tons"] == 700.0

    def test_unload_does_not_go_negative(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        self._setup_hold(ch, "H1", 100.0)
        run(ch.process_event({
            "type": "loading_event",
            "hold_id": "H1",
            "operation": "unload",
            "weight_change": 500.0,
        }))
        assert ch._holds["H1"]["weight_tons"] == 0.0

    def test_loading_event_records_history(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        self._setup_hold(ch, "H1", 100.0)
        run(ch.process_event({
            "type": "loading_event",
            "hold_id": "H1",
            "operation": "load",
            "weight_change": 50.0,
        }))
        assert len(ch._loading_events) == 1
        assert ch._loading_events[0]["operation"] == "load"

    def test_loading_event_missing_hold_id(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        result = run(ch.process_event({"type": "loading_event"}))
        assert result["status"] == "error"

    def test_loading_nonexistent_hold(self):
        """loading_event on a hold not yet registered — records event but no crash."""
        ch = CargoMonitorChannel()
        ch.initialize()
        result = run(ch.process_event({
            "type": "loading_event",
            "hold_id": "MISSING",
            "operation": "load",
            "weight_change": 100.0,
        }))
        assert result["status"] == "recorded"


class TestStabilityCheck:
    """stability_check 与 check_stability。"""

    def test_stability_check_event(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        result = run(ch.process_event({"type": "stability_check"}))
        # Fixed: event_status="checked" alongside stability's own "status"
        assert result["event_status"] == "checked"
        assert result["status"] in ("ok", "warning", "critical", "error")
        assert "gm" in result
        assert "km" in result
        assert "kg" in result
        assert "trim" in result

    def test_check_stability_ok(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        stability = ch.check_stability()
        # Default lightship should yield ok GM
        assert stability["gm"] > 0.5
        assert stability["status"] == "ok"

    def test_check_stability_gm_critical(self):
        """Set KG very high so GM < 0.15 → critical."""
        ch = CargoMonitorChannel(config={"lightship_kg": 50.0, "beam": 10.0, "draft": 5.5})
        ch.initialize()
        stability = ch.check_stability()
        assert stability["status"] == "critical"
        assert stability["gm"] < 0.15

    def test_check_stability_with_cargo(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        run(ch.process_event({
            "type": "cargo_status",
            "hold_id": "H1",
            "weight_tons": 2000.0,
            "kg_height": 4.0,
        }))
        stability = ch.check_stability()
        assert stability["gm"] > 0
        assert stability["status"] in ("ok", "warning", "critical")


class TestCargoMultipleHolds:
    """多货舱状态汇总。"""

    def test_multiple_holds_total_weight(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        for i in range(1, 4):
            run(ch.process_event({
                "type": "cargo_status",
                "hold_id": f"H{i}",
                "weight_tons": 100.0 * i,
            }))
        status = ch.get_status()
        assert status["total_weight"] == 600.0  # 100+200+300
        assert len(status["holds"]) == 3

    def test_trim_estimation_forward_aft(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        # H1 → forward, H4 → aft
        run(ch.process_event({"type": "cargo_status", "hold_id": "H1", "weight_tons": 1000.0}))
        run(ch.process_event({"type": "cargo_status", "hold_id": "H4", "weight_tons": 500.0}))
        stability = ch.check_stability()
        # More weight forward ⇒ negative trim (bow-heavy)
        assert stability["trim"] < 0


class TestCargoEmptyHold:
    """空舱检查不崩溃。"""

    def test_empty_holds_stability(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        stability = ch.check_stability()
        assert stability["status"] in ("ok", "warning", "critical")

    def test_empty_get_status(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        status = ch.get_status()
        assert status["total_weight"] == 0.0
        assert status["holds"] == []


class TestCargoBoundary:
    """边界: 零重量、负重量处理。"""

    def test_zero_weight_cargo(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        run(ch.process_event({"type": "cargo_status", "hold_id": "H1", "weight_tons": 0.0}))
        assert ch._holds["H1"]["weight_tons"] == 0.0
        stability = ch.check_stability()
        assert isinstance(stability["gm"], float)

    def test_negative_weight_cargo(self):
        """Negative weight should not crash — the channel stores whatever is given."""
        ch = CargoMonitorChannel()
        ch.initialize()
        run(ch.process_event({"type": "cargo_status", "hold_id": "H1", "weight_tons": -100.0}))
        assert ch._holds["H1"]["weight_tons"] == -100.0
        # check_stability still runs
        stability = ch.check_stability()
        assert isinstance(stability["gm"], float)

    def test_zero_draft_stability(self):
        ch = CargoMonitorChannel(config={"draft": 0.0})
        ch.initialize()
        stability = ch.check_stability()
        assert stability["status"] == "error"
        assert stability["gm"] == 0.0

    def test_zero_weight_loading(self):
        ch = CargoMonitorChannel()
        ch.initialize()
        run(ch.process_event({"type": "cargo_status", "hold_id": "H1", "weight_tons": 100.0}))
        run(ch.process_event({
            "type": "loading_event",
            "hold_id": "H1",
            "operation": "load",
            "weight_change": 0.0,
        }))
        assert ch._holds["H1"]["weight_tons"] == 100.0

    def test_start_stop(self):
        ch = CargoMonitorChannel()
        run(ch.start())
        assert ch._active is True
        run(ch.stop())
        assert ch._active is False


# ============================================================
# FireDetectionChannel Tests
# ============================================================

class TestFireDetectionInstantiation:
    """实例化和默认状态。"""

    def test_default_state(self):
        ch = FireDetectionChannel()
        assert ch.name == "fire_detection"
        assert ch._active is False
        assert ch._zones == {}
        assert ch._active_alarms == {}
        assert ch._alarm_history == []
        assert ch._alarm_counter == 0

    def test_initialize(self):
        ch = FireDetectionChannel()
        assert ch.initialize() is True
        assert ch._active is True
        assert ch._initialized is True

    def test_shutdown(self):
        ch = FireDetectionChannel()
        ch.initialize()
        assert ch.shutdown() is True
        assert ch._active is False
        assert ch._initialized is False

    def test_get_status_empty(self):
        ch = FireDetectionChannel()
        ch.initialize()
        status = ch.get_status()
        assert status["name"] == "fire_detection"
        assert status["active"] is True
        assert status["zones"] == {}
        assert status["active_alarms"] == []
        assert status["alarm_history_count"] == 0


class TestSensorReading:
    """sensor_reading — 记录传感器数据。"""

    def test_records_sensor_data(self):
        ch = FireDetectionChannel()
        ch.initialize()
        result = run(ch.process_event({
            "type": "sensor_reading",
            "zone_id": "engine_room",
            "temperature": 45.0,
            "smoke_level": 0.1,
            "co_ppm": 10.0,
        }))
        assert result["status"] == "recorded"
        assert result["zone_id"] == "engine_room"
        assert "engine_room" in ch._zones
        assert ch._zones["engine_room"]["temperature"] == 45.0

    def test_missing_zone_id(self):
        ch = FireDetectionChannel()
        ch.initialize()
        result = run(ch.process_event({"type": "sensor_reading"}))
        assert result["status"] == "error"
        assert "zone_id" in result["reason"]

    def test_sensor_defaults(self):
        ch = FireDetectionChannel()
        ch.initialize()
        run(ch.process_event({"type": "sensor_reading", "zone_id": "Z1"}))
        zone = ch._zones["Z1"]
        assert zone["temperature"] == 0.0
        assert zone["smoke_level"] == 0.0
        assert zone["co_ppm"] == 0.0

    def test_sensor_auto_risk_detection(self):
        """High-temperature reading should auto-trigger alarm."""
        ch = FireDetectionChannel()
        ch.initialize()
        result = run(ch.process_event({
            "type": "sensor_reading",
            "zone_id": "cargo_hold",
            "temperature": 90.0,
            "smoke_level": 0.0,
            "co_ppm": 0.0,
        }))
        assert result["status"] == "risk_detected"
        assert len(ch._active_alarms) == 1

    def test_unknown_event_ignored(self):
        ch = FireDetectionChannel()
        ch.initialize()
        result = run(ch.process_event({"type": "bogus"}))
        assert result["status"] == "ignored"


class TestAlarmTrigger:
    """alarm_trigger — 触发告警。"""

    def test_trigger_alarm(self):
        ch = FireDetectionChannel()
        ch.initialize()
        result = run(ch.process_event({
            "type": "alarm_trigger",
            "zone_id": "bridge",
            "alarm_type": "smoke_detector",
        }))
        assert result["status"] == "alarm_triggered"
        assert "alarm" in result
        assert result["alarm"]["zone_id"] == "bridge"
        assert result["alarm"]["alarm_type"] == "smoke_detector"
        assert len(ch._active_alarms) == 1

    def test_trigger_alarm_missing_zone_id(self):
        ch = FireDetectionChannel()
        ch.initialize()
        result = run(ch.process_event({"type": "alarm_trigger"}))
        assert result["status"] == "error"

    def test_trigger_alarm_default_type(self):
        ch = FireDetectionChannel()
        ch.initialize()
        result = run(ch.process_event({
            "type": "alarm_trigger",
            "zone_id": "deck",
        }))
        assert result["alarm"]["alarm_type"] == "manual"


class TestAlarmAcknowledge:
    """alarm_acknowledge — 确认告警。"""

    def _trigger(self, ch, zone_id="bridge"):
        result = run(ch.process_event({
            "type": "alarm_trigger",
            "zone_id": zone_id,
        }))
        return result["alarm"]["alarm_id"]

    def test_acknowledge_alarm(self):
        ch = FireDetectionChannel()
        ch.initialize()
        alarm_id = self._trigger(ch)
        result = run(ch.process_event({
            "type": "alarm_acknowledge",
            "alarm_id": alarm_id,
        }))
        assert result["status"] == "acknowledged"
        assert alarm_id not in ch._active_alarms
        assert len(ch._alarm_history) == 1
        assert ch._alarm_history[0]["acknowledged"] is True

    def test_acknowledge_missing_alarm_id(self):
        ch = FireDetectionChannel()
        ch.initialize()
        result = run(ch.process_event({"type": "alarm_acknowledge"}))
        assert result["status"] == "error"

    def test_acknowledge_nonexistent_alarm(self):
        ch = FireDetectionChannel()
        ch.initialize()
        result = run(ch.process_event({
            "type": "alarm_acknowledge",
            "alarm_id": "FIRE-9999",
        }))
        assert result["status"] == "error"
        assert "not found" in result["reason"]


class TestEvaluateFireRisk:
    """evaluate_fire_risk 阈值判定。"""

    def _set_zone(self, ch, zone_id, temp=25.0, smoke=0.0, co=0.0):
        run(ch.process_event({
            "type": "sensor_reading",
            "zone_id": zone_id,
            "temperature": temp,
            "smoke_level": smoke,
            "co_ppm": co,
        }))

    def test_high_temperature(self):
        ch = FireDetectionChannel()
        ch.initialize()
        ch._zones["Z1"] = {"zone_id": "Z1", "temperature": 85.0, "smoke_level": 0.0, "co_ppm": 0.0}
        risk = ch.evaluate_fire_risk("Z1")
        assert risk["fire_risk"] is True
        assert any("温度" in r for r in risk["reasons"])

    def test_high_smoke(self):
        ch = FireDetectionChannel()
        ch.initialize()
        ch._zones["Z1"] = {"zone_id": "Z1", "temperature": 25.0, "smoke_level": 0.7, "co_ppm": 0.0}
        risk = ch.evaluate_fire_risk("Z1")
        assert risk["fire_risk"] is True
        assert any("烟雾" in r for r in risk["reasons"])

    def test_high_co(self):
        ch = FireDetectionChannel()
        ch.initialize()
        ch._zones["Z1"] = {"zone_id": "Z1", "temperature": 25.0, "smoke_level": 0.0, "co_ppm": 60.0}
        risk = ch.evaluate_fire_risk("Z1")
        assert risk["fire_risk"] is True
        assert any("CO" in r for r in risk["reasons"])

    def test_normal_values(self):
        ch = FireDetectionChannel()
        ch.initialize()
        ch._zones["Z1"] = {"zone_id": "Z1", "temperature": 25.0, "smoke_level": 0.1, "co_ppm": 5.0}
        risk = ch.evaluate_fire_risk("Z1")
        assert risk["fire_risk"] is False
        assert len(risk["reasons"]) == 0

    def test_exact_threshold_not_fire(self):
        """Values exactly at threshold should NOT trigger (> not >=)."""
        ch = FireDetectionChannel()
        ch.initialize()
        ch._zones["Z1"] = {"zone_id": "Z1", "temperature": 80.0, "smoke_level": 0.5, "co_ppm": 50.0}
        risk = ch.evaluate_fire_risk("Z1")
        assert risk["fire_risk"] is False

    def test_all_thresholds_exceeded(self):
        ch = FireDetectionChannel()
        ch.initialize()
        ch._zones["Z1"] = {"zone_id": "Z1", "temperature": 100.0, "smoke_level": 1.0, "co_ppm": 100.0}
        risk = ch.evaluate_fire_risk("Z1")
        assert risk["fire_risk"] is True
        assert len(risk["reasons"]) == 3

    def test_unknown_zone(self):
        ch = FireDetectionChannel()
        ch.initialize()
        risk = ch.evaluate_fire_risk("nonexistent")
        assert risk["fire_risk"] is False
        assert "zone not found" in risk["message"]


class TestFireMultiZoneAlarms:
    """多区域同时告警。"""

    def test_multiple_zones_multiple_alarms(self):
        ch = FireDetectionChannel()
        ch.initialize()
        run(ch.process_event({"type": "alarm_trigger", "zone_id": "engine_room"}))
        run(ch.process_event({"type": "alarm_trigger", "zone_id": "cargo_hold_1"}))
        run(ch.process_event({"type": "alarm_trigger", "zone_id": "cargo_hold_2"}))
        assert len(ch._active_alarms) == 3
        status = ch.get_status()
        assert len(status["active_alarms"]) == 3

    def test_acknowledge_one_keeps_others(self):
        ch = FireDetectionChannel()
        ch.initialize()
        r1 = run(ch.process_event({"type": "alarm_trigger", "zone_id": "Z1"}))
        r2 = run(ch.process_event({"type": "alarm_trigger", "zone_id": "Z2"}))
        run(ch.process_event({"type": "alarm_acknowledge", "alarm_id": r1["alarm"]["alarm_id"]}))
        assert len(ch._active_alarms) == 1
        assert r2["alarm"]["alarm_id"] in ch._active_alarms


class TestFireAcknowledgeRemovesFromActive:
    """确认后告警从 active 移除。"""

    def test_acknowledge_removes_and_archives(self):
        ch = FireDetectionChannel()
        ch.initialize()
        r = run(ch.process_event({"type": "alarm_trigger", "zone_id": "Z1"}))
        alarm_id = r["alarm"]["alarm_id"]
        assert alarm_id in ch._active_alarms
        run(ch.process_event({"type": "alarm_acknowledge", "alarm_id": alarm_id}))
        assert alarm_id not in ch._active_alarms
        assert len(ch._alarm_history) == 1

    def test_acknowledge_all_restores_health(self):
        ch = FireDetectionChannel()
        ch.initialize()
        r = run(ch.process_event({"type": "alarm_trigger", "zone_id": "Z1"}))
        run(ch.process_event({"type": "alarm_acknowledge", "alarm_id": r["alarm"]["alarm_id"]}))
        assert ch._health.status == ChannelStatus.OK


class TestFireBoundary:
    """边界: 未知 zone_id 不崩溃。"""

    def test_evaluate_unknown_zone(self):
        ch = FireDetectionChannel()
        ch.initialize()
        risk = ch.evaluate_fire_risk("does_not_exist")
        assert risk["fire_risk"] is False

    def test_get_status_with_zones(self):
        ch = FireDetectionChannel()
        ch.initialize()
        run(ch.process_event({
            "type": "sensor_reading",
            "zone_id": "Z1",
            "temperature": 25.0,
        }))
        status = ch.get_status()
        assert "Z1" in status["zones"]
        assert "fire_risk" in status["zones"]["Z1"]

    def test_start_stop(self):
        ch = FireDetectionChannel()
        run(ch.start())
        assert ch._active is True
        run(ch.stop())
        assert ch._active is False

    def test_alarm_counter_increments(self):
        ch = FireDetectionChannel()
        ch.initialize()
        run(ch.process_event({"type": "alarm_trigger", "zone_id": "A"}))
        run(ch.process_event({"type": "alarm_trigger", "zone_id": "B"}))
        assert ch._alarm_counter == 2
        ids = list(ch._active_alarms.keys())
        assert ids[0] != ids[1]


# Need ChannelStatus for health assertion
from backend.channels.marine_base import ChannelStatus
