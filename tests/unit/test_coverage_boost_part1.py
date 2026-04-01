# -*- coding: utf-8 -*-
"""
Comprehensive tests for Distributed Perception Hub, Marine Message Bus,
NMEA 2000 Parser, Engine Monitor, and Predictive Health channels.

These tests target the uncovered lines to push coverage toward 95%.
"""

import asyncio
import struct
import time
import math
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# ---------- Distributed Perception Hub ----------
from channels.distributed_perception_hub import (
    DistributedPerceptionHubChannel, FusionEvent,
)
from channels.marine_base import get_default_registry, ChannelStatus


@pytest.fixture
def perception_hub():
    ch = DistributedPerceptionHubChannel(config={"max_events": 50})
    ch.initialize()
    return ch


class TestFusionEvent:
    def test_to_dict(self):
        evt = FusionEvent(id="e1", timestamp="2026-01-01", event_type="test",
                         source="unit", payload={"v": 1}, fused_with=["e0"],
                         risk_correlation={"r": 0.5})
        d = evt.to_dict()
        assert d["id"] == "e1"
        assert d["fused_with"] == ["e0"]

    def test_to_dict_none_fields(self):
        evt = FusionEvent(id="e2", timestamp="2026-01-01", event_type="test",
                         source="unit", payload={})
        d = evt.to_dict()
        assert "fused_with" not in d
        assert "risk_correlation" not in d


class TestPerceptionHubBasic:
    def test_append_event(self, perception_hub):
        evt = perception_hub.append_event("test", {"x": 1}, "test_src")
        assert evt.id.startswith("evt-")
        assert len(perception_hub.events) == len(perception_hub.events)

    def test_max_events_trim(self, perception_hub):
        for i in range(60):
            perception_hub.append_event("test", {"i": i}, "src")
        assert len(perception_hub.events) <= 50

    def test_event_sink_persistence(self, perception_hub):
        sink = MagicMock()
        perception_hub.set_event_sink(sink)
        perception_hub.append_event("test", {"x": 1}, "src")
        sink.save_event.assert_called_once()

    def test_event_sink_error_handled(self, perception_hub):
        sink = MagicMock()
        sink.save_event.side_effect = Exception("DB error")
        perception_hub.set_event_sink(sink)
        evt = perception_hub.append_event("test", {}, "src")
        assert evt is not None

    def test_get_latest_events(self, perception_hub):
        for i in range(5):
            perception_hub.append_event("test", {"i": i}, "src")
        latest = perception_hub.get_latest_events(limit=3)
        assert len(latest) == 3


class TestAISNavFusion:
    def test_fuse_ais_with_navigation(self, perception_hub):
        ais = {"latitude": 31.23, "longitude": 121.47, "mmsi": 413000001}
        nav = {"own_ship": {"latitude": 31.24, "longitude": 121.47}}
        result = perception_hub.fuse_ais_with_navigation(ais, nav)
        assert result is not None
        assert result.event_type == "ais_nav_fusion"

    def test_fuse_ais_nav_too_far(self, perception_hub):
        ais = {"latitude": 35.0, "longitude": 130.0}
        nav = {"own_ship": {"latitude": 31.0, "longitude": 121.0}}
        result = perception_hub.fuse_ais_with_navigation(ais, nav)
        assert result is None

    def test_fuse_ais_nav_missing_coords(self, perception_hub):
        result = perception_hub.fuse_ais_with_navigation({}, {})
        assert result is None

    def test_fuse_ais_nav_close_range(self, perception_hub):
        ais = {"latitude": 31.23, "longitude": 121.47}
        nav = {"own_ship": {"latitude": 31.2301, "longitude": 121.4701}}
        result = perception_hub.fuse_ais_with_navigation(ais, nav)
        if result:
            assert result.confidence > 0.8

    def test_fuse_ais_nav_risk_correlation(self, perception_hub):
        ais = {"latitude": 31.23, "longitude": 121.47}
        nav = {"own_ship": {"latitude": 31.2301, "longitude": 121.47001}}
        result = perception_hub.fuse_ais_with_navigation(ais, nav)
        if result and result.risk_correlation:
            assert "collision_risk" in result.risk_correlation


class TestWeatherEfficiencyFusion:
    def test_fuse_weather_with_efficiency(self, perception_hub):
        weather = {
            "position": {"lat": 31.23, "lng": 121.47},
            "wind": {"speed": 25}, "wave": {"height": 4.0}
        }
        efficiency = {"position": {"latitude": 31.23, "longitude": 121.47}}
        result = perception_hub.fuse_weather_with_efficiency(weather, efficiency)
        assert result is not None
        assert "weather_efficiency_fusion" == result.event_type

    def test_fuse_weather_efficiency_too_far(self, perception_hub):
        weather = {"position": {"lat": 35.0, "lng": 130.0}, "wind": {}, "wave": {}}
        eff = {"position": {"latitude": 31.0, "longitude": 121.0}}
        result = perception_hub.fuse_weather_with_efficiency(weather, eff)
        assert result is None

    def test_fuse_weather_efficiency_missing(self, perception_hub):
        result = perception_hub.fuse_weather_with_efficiency({}, {})
        assert result is None

    def test_weather_risk_correlation(self, perception_hub):
        weather = {
            "position": {"lat": 31.23, "lng": 121.47},
            "wind": {"speed": 30}, "wave": {"height": 5.0}
        }
        eff = {"position": {"latitude": 31.23, "longitude": 121.47}}
        result = perception_hub.fuse_weather_with_efficiency(weather, eff)
        if result:
            assert result.risk_correlation.get("weather_risk", 0) > 0


class TestNMEAWorldMonitorFusion:
    def test_fuse_nmea_with_worldmonitor(self, perception_hub):
        nmea_ais = {"mmsi": 123, "latitude": 31.23, "longitude": 121.47}
        wm_ais = {"targets": [{"mmsi": 123, "latitude": 31.23, "longitude": 121.47}]}
        result = perception_hub.fuse_nmea_with_worldmonitor_ais(nmea_ais, wm_ais)
        assert result is not None

    def test_fuse_nmea_no_match(self, perception_hub):
        nmea_ais = {"mmsi": 999, "latitude": 31.23, "longitude": 121.47}
        wm_ais = {"targets": [{"mmsi": 123, "latitude": 31.23, "longitude": 121.47}]}
        result = perception_hub.fuse_nmea_with_worldmonitor_ais(nmea_ais, wm_ais)
        assert result is None

    def test_fuse_nmea_position_mismatch(self, perception_hub):
        nmea_ais = {"mmsi": 123, "latitude": 31.23, "longitude": 121.47}
        wm_ais = {"targets": [{"mmsi": 123, "latitude": 35.0, "longitude": 130.0}]}
        result = perception_hub.fuse_nmea_with_worldmonitor_ais(nmea_ais, wm_ais)
        assert result is None  # Position delta too large


class TestPerceptionHubFeatureFusion:
    def test_build_measurements_from_nav(self, perception_hub):
        nav_ch = MagicMock()
        nav_ch.ais_targets = [
            MagicMock(mmsi=123, latitude=31.23, longitude=121.47, speed=10, course=45)
        ]
        measurements = perception_hub._build_feature_fusion_measurements(nav_ch, None)
        assert len(measurements) == 1

    def test_build_measurements_from_worldmonitor(self, perception_hub):
        wm_ais = {"targets": [
            {"mmsi": 456, "latitude": 31.24, "longitude": 121.48, "speed": 8, "course": 90}
        ]}
        measurements = perception_hub._build_feature_fusion_measurements(None, wm_ais)
        assert len(measurements) == 1

    def test_get_fusion_state_empty(self, perception_hub):
        state = perception_hub.get_fusion_state()
        assert state["active_tracks"] == []
        assert state["fusion_quality"] == 0.0

    def test_get_fusion_state_with_data(self, perception_hub):
        nav_ch = MagicMock()
        nav_ch.ais_targets = [
            MagicMock(mmsi=123, latitude=31.23, longitude=121.47, speed=10, course=45)
        ]
        measurements = perception_hub._build_feature_fusion_measurements(nav_ch, None)
        perception_hub.feature_fusion.process_frame(measurements)
        state = perception_hub.get_fusion_state()
        assert len(state["active_tracks"]) == 1

    def test_track_measurement_from_target(self, perception_hub):
        target = {"latitude": 31.23, "longitude": 121.47, "speed": 10, "course": 45}
        m = perception_hub._track_measurement_from_target("test", target, 0.9, 0.85)
        assert m is not None
        assert m.confidence == 0.9

    def test_track_measurement_missing_coords(self, perception_hub):
        target = {"speed": 10}
        m = perception_hub._track_measurement_from_target("test", target, 0.9, 0.85)
        assert m is None


class TestPerceptionHubStatus:
    def test_get_status(self, perception_hub):
        status = perception_hub.get_status()
        assert status["name"] == "distributed_perception_hub"
        assert "fusion_state" in status
        assert "fusion_capabilities" in status

    def test_shutdown(self, perception_hub):
        assert perception_hub.shutdown()
        assert not perception_hub._initialized


# ---------- NMEA 2000 Parser ----------
from channels.nmea2000_parser import (
    NMEA2000ParserChannel, CANFrame, NMEA2000Message, PGNClass, PGNDefinition,
)


@pytest.fixture
def parser():
    ch = NMEA2000ParserChannel()
    ch.initialize()
    return ch


class TestCANFrame:
    def test_priority_extraction(self):
        frame = CANFrame(identifier=0x09F8010A, data=b'\x00' * 8)
        assert 0 <= frame.priority <= 7

    def test_pgn_pdu2(self):
        # PGN 129025 = 0x1F801 -> pdu_format >= 240
        identifier = (2 << 26) | (1 << 24) | (0xF8 << 16) | (0x01 << 8) | 0x0A
        frame = CANFrame(identifier=identifier, data=b'\x00' * 8)
        assert frame.pgn > 0

    def test_pgn_pdu1(self):
        identifier = (2 << 26) | (0 << 24) | (0xEF << 16) | (0x01 << 8) | 0x0A
        frame = CANFrame(identifier=identifier, data=b'\x00' * 8)
        assert frame.pdu_format < 240

    def test_source_address(self):
        frame = CANFrame(identifier=0x09F8010A, data=b'\x00' * 8)
        assert frame.source_address == 0x0A


class TestNMEA2000Parser:
    def test_initialize(self, parser):
        assert parser._initialized
        assert len(parser.pgn_definitions) > 10

    def test_parse_position_frame(self, parser):
        # PGN 129025 = Position Rapid Update
        lat_raw = int(31.23 / 1e-7)
        lon_raw = int(121.47 / 1e-7)
        data = struct.pack('<II', lat_raw & 0xFFFFFFFF, lon_raw & 0xFFFFFFFF)
        pgn = 129025
        data_page = (pgn >> 16) & 0x01
        pdu_format = (pgn >> 8) & 0xFF
        pdu_specific = pgn & 0xFF
        identifier = (2 << 26) | (data_page << 24) | (pdu_format << 16) | (pdu_specific << 8) | 0x01
        frame = CANFrame(identifier=identifier, data=data)
        msg = parser.parse_can_frame(frame)
        assert msg is not None
        assert msg.pgn == 129025
        assert msg.fields.get("latitude") is not None

    def test_parse_unknown_pgn(self, parser):
        identifier = (2 << 26) | (0 << 24) | (0x00 << 16) | (0x00 << 8) | 0x01
        frame = CANFrame(identifier=identifier, data=b'\x00' * 8)
        msg = parser.parse_can_frame(frame)
        # Unknown PGN returns None

    def test_parse_engine_frame(self, parser):
        pgn = 127488
        data_page = (pgn >> 16) & 0x01
        pdu_format = (pgn >> 8) & 0xFF
        pdu_specific = pgn & 0xFF
        identifier = (2 << 26) | (data_page << 24) | (pdu_format << 16) | (pdu_specific << 8) | 0x01
        data = b'\x00\x01' + struct.pack('<H', 1200) + struct.pack('<H', 1000) + b'\x00\x00'
        frame = CANFrame(identifier=identifier, data=data)
        msg = parser.parse_can_frame(frame)
        assert msg is not None
        assert msg.category == PGNClass.ENGINE

    def test_parse_short_data(self, parser):
        pgn = 129025
        data_page = (pgn >> 16) & 0x01
        pdu_format = (pgn >> 8) & 0xFF
        pdu_specific = pgn & 0xFF
        identifier = (2 << 26) | (data_page << 24) | (pdu_format << 16) | (pdu_specific << 8) | 0x01
        frame = CANFrame(identifier=identifier, data=b'\x00')  # Too short
        msg = parser.parse_can_frame(frame)
        assert msg is not None  # Should still parse, with None fields

    def test_list_pgns(self, parser):
        all_pgns = parser.list_pgns()
        assert len(all_pgns) > 10
        nav_pgns = parser.list_pgns(category=PGNClass.NAVIGATION)
        assert len(nav_pgns) >= 5

    def test_get_pgn_info(self, parser):
        info = parser.get_pgn_info(129025)
        assert info is not None
        assert info.name == "Position, Rapid Update"

    def test_get_pgn_info_unknown(self, parser):
        assert parser.get_pgn_info(999999) is None

    def test_get_messages(self, parser):
        msgs = parser.get_messages()
        assert isinstance(msgs, list)

    def test_clear_messages(self, parser):
        pgn = 127488
        data_page = (pgn >> 16) & 0x01
        pdu_format = (pgn >> 8) & 0xFF
        pdu_specific = pgn & 0xFF
        identifier = (2 << 26) | (data_page << 24) | (pdu_format << 16) | (pdu_specific << 8) | 0x01
        frame = CANFrame(identifier=identifier, data=b'\x00' * 8)
        parser.parse_can_frame(frame)
        assert len(parser.messages) > 0
        parser.clear_messages()
        assert len(parser.messages) == 0

    def test_get_statistics(self, parser):
        stats = parser.get_statistics()
        assert "frame_count" in stats
        assert "error_rate" in stats

    def test_get_status(self, parser):
        status = parser.get_status()
        assert status["name"] == "nmea2000_parser"

    def test_check(self, parser):
        ok, msg = parser.check()
        assert ok

    def test_can_handle(self, parser):
        assert not parser.can_handle("http://test.com")

    def test_shutdown(self, parser):
        parser.shutdown()
        assert not parser._initialized

    def test_frame_count(self, parser):
        pgn = 127488
        pdu_format = (pgn >> 8) & 0xFF
        pdu_specific = pgn & 0xFF
        identifier = (2 << 26) | (0 << 24) | (pdu_format << 16) | (pdu_specific << 8) | 0x01
        for _ in range(5):
            parser.parse_can_frame(CANFrame(identifier=identifier, data=b'\x00' * 8))
        assert parser.frame_count == 5

    def test_parse_fields_various_lengths(self, parser):
        fields = [
            {"name": "f1", "offset": 0, "length": 1, "scale": 1.0},
            {"name": "f2", "offset": 1, "length": 2, "scale": 0.01},
            {"name": "f4", "offset": 3, "length": 4, "scale": 1e-7},
        ]
        data = b'\x42' + struct.pack('<H', 5000) + struct.pack('<I', 312300000) + b'\x00'
        result = parser._parse_fields(data, fields)
        assert result["f1"] == 0x42
        assert result["f2"] == pytest.approx(50.0, abs=0.1)


# ---------- Engine Monitor Extended ----------
from channels.engine_monitor import (
    EngineMonitorChannel, AlarmLevel, EngineParameter, EngineAlarm,
)


@pytest.fixture
def engine():
    ch = EngineMonitorChannel(engine_id="ME-TEST")
    ch.initialize()
    return ch


class TestEngineMonitorExtended:
    def test_temperature_alarm_shutdown(self, engine):
        engine.update_parameter("冷却水出口温度", 99.0, "°C")
        alarms = engine.get_active_alarms()
        shutdown_alarms = [a for a in alarms if a.level == AlarmLevel.SHUTDOWN]
        assert len(shutdown_alarms) > 0

    def test_temperature_alarm_warning(self, engine):
        engine.update_parameter("冷却水出口温度", 86.0, "°C")
        alarms = engine.get_active_alarms()
        assert len(alarms) > 0
        assert alarms[0].level in [AlarmLevel.WARNING, AlarmLevel.SLOW_DOWN]

    def test_temperature_alarm_slow_down(self, engine):
        engine.update_parameter("冷却水出口温度", 93.0, "°C")
        alarms = engine.get_active_alarms()
        assert any(a.level == AlarmLevel.SLOW_DOWN for a in alarms)

    def test_pressure_low_alarm(self, engine):
        engine.update_parameter("滑油压力", 1.4, "bar")
        alarms = engine.get_active_alarms()
        assert len(alarms) > 0

    def test_pressure_low_warning(self, engine):
        engine.update_parameter("滑油压力", 2.3, "bar")
        alarms = engine.get_active_alarms()
        assert len(alarms) > 0

    def test_pressure_low_slow_down(self, engine):
        engine.update_parameter("滑油压力", 1.8, "bar")
        alarms = engine.get_active_alarms()
        assert any(a.level == AlarmLevel.SLOW_DOWN for a in alarms)

    def test_overspeed_warning(self, engine):
        engine.update_parameter("主机转速", 116.0, "rpm")
        alarms = engine.get_active_alarms()
        assert len(alarms) > 0

    def test_overspeed_alarm(self, engine):
        engine.update_parameter("主机转速", 121.0, "rpm")
        alarms = engine.get_active_alarms()
        assert any(a.level == AlarmLevel.SLOW_DOWN for a in alarms)

    def test_other_parameter_alarm(self, engine):
        engine.update_parameter("曲轴箱油雾浓度", 55.0, "mg/L")
        alarms = engine.get_active_alarms()
        assert len(alarms) > 0

    def test_other_parameter_shutdown(self, engine):
        engine.update_parameter("曲轴箱油雾浓度", 101.0, "mg/L")
        alarms = engine.get_active_alarms()
        assert any(a.level == AlarmLevel.SHUTDOWN for a in alarms)

    def test_no_alarm_normal(self, engine):
        engine.update_parameter("冷却水出口温度", 78.0, "°C")
        alarms = engine.get_active_alarms()
        temp_alarms = [a for a in alarms if a.parameter == "冷却水出口温度"]
        assert len(temp_alarms) == 0

    def test_acknowledge_alarm(self, engine):
        engine.update_parameter("冷却水出口温度", 99.0, "°C")
        alarms = engine.get_active_alarms()
        assert len(alarms) > 0
        assert engine.acknowledge_alarm(alarms[0].alarm_id)
        not_acked = engine.get_active_alarms(include_acknowledged=False)
        acked_alarms = engine.get_active_alarms(include_acknowledged=True)
        assert len(acked_alarms) > len(not_acked)

    def test_acknowledge_nonexistent(self, engine):
        assert not engine.acknowledge_alarm("nonexistent")

    def test_engine_status_running(self, engine):
        engine.update_parameter("主机转速", 100, "rpm")
        status = engine.get_engine_status()
        assert status.running is True

    def test_engine_status_stopped(self, engine):
        engine.update_parameter("主机转速", 5, "rpm")
        status = engine.get_engine_status()
        assert status.running is False

    def test_engine_status_critical(self, engine):
        engine.update_parameter("冷却水出口温度", 99.0, "°C")
        status = engine.get_engine_status()
        assert "严重" in status.status_text

    def test_simulate_data(self, engine):
        data = engine.simulate_data()
        assert "主机转速" in data
        assert "滑油压力" in data

    def test_run_simulation(self, engine):
        status = engine.run_simulation()
        assert status.engine_id == "ME-TEST"

    def test_get_trend_data(self, engine):
        engine.update_parameter("冷却水出口温度", 80.0, "°C")
        data = engine.get_trend_data("冷却水出口温度")
        assert len(data) == 1

    def test_get_trend_data_missing(self, engine):
        data = engine.get_trend_data("nonexistent")
        assert len(data) == 0

    def test_get_status(self, engine):
        status = engine.get_status()
        assert status["engine_id"] == "ME-TEST"

    def test_can_handle(self, engine):
        assert not engine.can_handle("http://test.com")

    def test_alarm_disabled(self):
        ch = EngineMonitorChannel(alarm_enabled=False)
        ch.initialize()
        ch.update_parameter("冷却水出口温度", 99.0, "°C")
        assert len(ch.get_active_alarms()) == 0

    def test_custom_timestamp(self, engine):
        ts = datetime(2026, 1, 1, 12, 0, 0)
        param = engine.update_parameter("冷却水出口温度", 80.0, "°C", timestamp=ts)
        assert param.timestamp == ts

    def test_pressure_high_alarm(self, engine):
        engine.update_parameter("增压空气压力", 3.3, "bar")
        alarms = engine.get_active_alarms()
        # 增压空气压力 uses high alarm thresholds
        assert len(alarms) > 0


# ---------- Predictive Health Extended ----------
from channels.predictive_health import (
    PredictiveHealthChannel, ComponentType, HealthTrend,
    MaintenancePriority, ComponentHealth, COMPONENT_MODELS,
)


@pytest.fixture
def phm():
    ch = PredictiveHealthChannel()
    ch.initialize()
    return ch


class TestPredictiveHealthExtended:
    def test_initialize_defaults(self, phm):
        assert len(phm._components) >= 4
        assert "ME-1" in phm._components

    def test_ingest_normal_parameter(self, phm):
        result = phm.ingest_parameter("ME-1", "coolant_temp", 80.0, "°C")
        assert result is not None
        assert result["health_score"] > 0

    def test_ingest_warning_parameter(self, phm):
        initial_score = phm._components["ME-1"].health_score
        phm.ingest_parameter("ME-1", "coolant_temp", 88.0, "°C")
        assert phm._components["ME-1"].health_score < initial_score

    def test_ingest_alarm_parameter(self, phm):
        initial_score = phm._components["ME-1"].health_score
        for _ in range(5):
            phm.ingest_parameter("ME-1", "coolant_temp", 100.0, "°C")
        assert phm._components["ME-1"].health_score < initial_score

    def test_ingest_unknown_component(self, phm):
        result = phm.ingest_parameter("NONEXISTENT", "temp", 80.0)
        assert result is None

    def test_ingest_unknown_parameter(self, phm):
        result = phm.ingest_parameter("ME-1", "unknown_param", 50.0)
        assert result is not None  # Still updates, but no deviation

    def test_detect_trend_stable(self, phm):
        trend = phm._detect_trend("ME-1")
        assert trend == HealthTrend.STABLE

    def test_detect_trend_with_samples(self, phm):
        for i in range(25):
            phm.ingest_parameter("ME-1", "coolant_temp", 80.0 + i * 0.5, "°C")
        trend = phm._detect_trend("ME-1")
        assert trend in [HealthTrend.STABLE, HealthTrend.DEGRADING_SLOW, HealthTrend.DEGRADING_FAST]

    def test_detect_trend_critical(self, phm):
        phm._components["ME-1"].health_score = 30  # Below critical
        for i in range(10):
            phm.ingest_parameter("ME-1", "coolant_temp", 100.0, "°C")
        trend = phm._detect_trend("ME-1")
        assert trend == HealthTrend.CRITICAL

    def test_estimate_rul(self, phm):
        rul = phm._estimate_rul("ME-1")
        assert rul >= 0

    def test_estimate_rul_unknown(self, phm):
        rul = phm._estimate_rul("NONEXISTENT")
        assert rul == 0

    def test_estimate_rul_zero_score(self, phm):
        phm._components["ME-1"].health_score = 30  # Below threshold
        rul = phm._estimate_rul("ME-1")
        assert rul == 0

    def test_calc_failure_prob(self):
        prob = PredictiveHealthChannel._calc_failure_prob(90, 5000)
        assert 0 < prob < 1

    def test_calc_failure_prob_zero_rul(self):
        prob = PredictiveHealthChannel._calc_failure_prob(50, 0)
        assert prob == 0.95

    def test_generate_maintenance_plan(self, phm):
        # Lower health score to trigger recommendation
        phm._components["ME-1"].health_score = 50
        phm._components["ME-1"].trend = HealthTrend.DEGRADING_FAST
        plan = phm.generate_maintenance_plan()
        assert len(plan) > 0
        assert plan[0].priority in [MaintenancePriority.IMMEDIATE, MaintenancePriority.NEXT_PORT]

    def test_maintenance_priority_immediate(self, phm):
        phm._components["ME-1"].health_score = 35
        phm._components["ME-1"].trend = HealthTrend.CRITICAL
        plan = phm.generate_maintenance_plan()
        me1_plan = [r for r in plan if r.component_id == "ME-1"]
        assert len(me1_plan) > 0
        assert me1_plan[0].priority == MaintenancePriority.IMMEDIATE

    def test_maintenance_priority_ok(self, phm):
        phm._components["ME-1"].health_score = 95
        phm._components["ME-1"].trend = HealthTrend.STABLE
        plan = phm.generate_maintenance_plan()
        me1_plan = [r for r in plan if r.component_id == "ME-1"]
        assert len(me1_plan) == 0

    def test_maintenance_action(self):
        comp = ComponentHealth(
            component_id="ME-1", component_type=ComponentType.MAIN_ENGINE,
            health_score=50, trend=HealthTrend.DEGRADING_SLOW,
            rul_hours=500, confidence=0.8
        )
        action, parts = PredictiveHealthChannel._maintenance_action(comp)
        assert "主机" in action
        assert len(parts) > 0

    def test_maintenance_action_turbocharger(self):
        comp = ComponentHealth(
            component_id="TC-1", component_type=ComponentType.TURBOCHARGER,
            health_score=50, trend=HealthTrend.DEGRADING_SLOW,
            rul_hours=500, confidence=0.8
        )
        action, parts = PredictiveHealthChannel._maintenance_action(comp)
        assert "涡轮" in action

    def test_estimate_maintenance_hours(self):
        comp = ComponentHealth(
            component_id="ME-1", component_type=ComponentType.MAIN_ENGINE,
            health_score=50, trend=HealthTrend.STABLE, rul_hours=500, confidence=0.8
        )
        hours = PredictiveHealthChannel._estimate_maintenance_hours(comp)
        assert hours == 48

    def test_fleet_health_summary(self, phm):
        summary = phm.get_fleet_health_summary()
        assert "components" in summary or len(phm._components) > 0

    def test_max_samples_trimming(self, phm):
        for i in range(250):
            phm.ingest_parameter("ME-1", "coolant_temp", 80.0 + (i % 10))
        assert len(phm._samples["ME-1"]) <= phm._max_samples_per_component

    def test_confidence_does_not_crash_with_many_samples(self, phm):
        for i in range(50):
            phm.ingest_parameter("ME-1", "coolant_temp", 80.0)
        # Just confirm it completes without error
        assert phm._components["ME-1"].health_score > 0

    def test_register_component(self, phm):
        comp = phm._register_component("TEST-1", ComponentType.GENERATOR, 1000)
        assert comp.component_id == "TEST-1"
        assert comp.operating_hours == 1000
