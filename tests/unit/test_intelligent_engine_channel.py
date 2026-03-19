# -*- coding: utf-8 -*-
"""
测试 IntelligentEngineChannel - 智能机舱模块。

验证主机健康评估、告警、趋势分析和维护建议功能。
"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from types import SimpleNamespace

import pytest
from backend.channels.intelligent_engine import IntelligentEngineChannel, EngineSnapshot
from backend.channels.marine_base import ChannelStatus, ChannelPriority


class TestIntelligentEngineChannel:
    """IntelligentEngineChannel 测试用例。"""

    @pytest.fixture
    def channel(self) -> IntelligentEngineChannel:
        return IntelligentEngineChannel(config={"max_snapshots": 5})

    def test_channel_initialization_defaults(self, channel):
        assert channel.name == "intelligent_engine"
        assert channel.description == "智能机舱 (健康评估 + 趋势分析 + 故障预警)"
        assert channel.version == "1.0.0"
        assert channel.priority == ChannelPriority.P0
        assert channel.dependencies == ["engine_monitor"]
        assert channel._initialized is False
        assert len(channel.snapshots) == 1  # seeded demo data

    def test_initialize_sets_ok_health(self, channel):
        result = channel.initialize()

        assert result is True
        assert channel._initialized is True
        assert channel.get_health().status == ChannelStatus.OK
        assert "智能机舱系统就绪" in channel.get_health().message

    def test_get_status_contains_expected_fields(self, channel):
        channel.initialize()
        status = channel.get_status()

        assert status["name"] == "intelligent_engine"
        assert status["version"] == "1.0.0"
        assert status["initialized"] is True
        assert status["health"] == "ok"
        assert isinstance(status["engine_health_score"], int)
        assert isinstance(status["alerts"], list)
        assert isinstance(status["trend"], dict)
        assert status["latest_snapshot"]["rpm"] == 720

    def test_shutdown_sets_off(self, channel):
        channel.initialize()
        result = channel.shutdown()

        assert result is True
        assert channel._initialized is False
        assert channel.get_health().status == ChannelStatus.OFF

    def test_health_score_stays_high_for_normal_data(self, channel):
        channel.update_snapshot(750, 70, 80.0, 3.3, 480)
        score = channel.calculate_health_score()

        assert score >= 85
        assert channel.get_health().status == ChannelStatus.OK

    def test_health_score_degrades_for_hot_engine(self, channel):
        channel.update_snapshot(820, 88, 96.0, 3.0, 520)
        score = channel.calculate_health_score()

        assert score < 85
        assert any("冷却水温度过高" in a["message"] for a in channel.get_alerts())

    def test_critical_alerts_for_multiple_issues(self, channel):
        channel.update_snapshot(910, 93, 97.0, 1.6, 640)
        alerts = channel.get_alerts()
        messages = " | ".join(a["message"] for a in alerts)

        assert len(alerts) >= 3
        assert "冷却水温度过高" in messages
        assert "滑油压力过低" in messages
        assert "主机高负载" in messages
        assert channel.get_health().status in (ChannelStatus.WARN, ChannelStatus.ERROR)

    def test_trend_summary_detects_changes(self, channel):
        channel.update_snapshot(700, 65, 77.0, 3.5, 450)
        channel.update_snapshot(710, 66, 78.0, 3.4, 455)
        channel.update_snapshot(730, 68, 80.0, 3.3, 465)
        channel.update_snapshot(760, 72, 82.0, 3.1, 480)
        channel.update_snapshot(790, 75, 84.0, 2.9, 500)

        trend = channel.get_trend_summary()
        assert trend["rpm"] == "rising"
        assert trend["temp"] == "rising"
        assert trend["pressure"] == "worsening"

    def test_maintenance_advice_matches_detected_risks(self, channel):
        channel.update_snapshot(905, 92, 90.0, 2.2, 610)
        advice = channel.get_maintenance_advice()

        joined = "\n".join(advice)
        assert "冷却水回路" in joined
        assert "滑油" in joined
        assert "降载运行" in joined

    def test_query_engine_status_health_response(self, channel):
        channel.update_snapshot(740, 71, 79.0, 3.2, 470)
        text = channel.query_engine_status("主机健康状态怎么样？")

        assert "当前主机健康度" in text
        assert "RPM" in text
        assert "当前无机舱告警" in text or "当前告警" in text

    def test_query_engine_status_maintenance_response(self, channel):
        channel.update_snapshot(910, 94, 96.0, 1.7, 650)
        text = channel.query_engine_status("给我维护建议")

        assert text.startswith("维护建议：")
        assert "检查" in text or "评估" in text

    def test_query_engine_status_trend_response(self, channel):
        channel.update_snapshot(700, 65, 77.0, 3.5, 450)
        channel.update_snapshot(790, 75, 84.0, 2.9, 500)
        text = channel.query_engine_status("趋势如何？")

        assert "趋势分析" in text
        assert "RPM" in text

    def test_snapshot_cap_is_respected(self, channel):
        for i in range(10):
            channel.update_snapshot(700 + i, 60 + i, 75 + i * 0.5, 3.5 - i * 0.1, 450 + i * 5)

        assert len(channel.snapshots) == 5

    def test_nmea2000_ingest_builds_snapshot_from_multiple_pgns(self, channel):
        base_count = len(channel.snapshots)
        rapid = SimpleNamespace(pgn=127488, fields={"engine_instance": 0, "speed": 742.5})
        dynamic = SimpleNamespace(pgn=127489, fields={"engine_instance": 0, "engine_load": 74.0, "fuel_rate": 486.0})
        transmission = SimpleNamespace(pgn=127493, fields={"engine_instance": 0, "oil_pressure": 320000.0, "oil_temp": 358.15})

        assert channel.ingest_nmea2000_message(rapid) is False
        assert channel.ingest_nmea2000_message(dynamic) is False
        assert channel.ingest_nmea2000_message(transmission) is True

        latest = channel.get_latest_snapshot()
        assert len(channel.snapshots) == base_count + 1
        assert latest.rpm == 742.5
        assert latest.load == 74.0
        assert round(latest.oil_pressure, 1) == 3.2
        assert round(latest.coolant_temp, 1) == 85.0
        assert latest.fuel_rate == 486.0

    def test_fault_diagnosis_returns_expected_findings(self, channel):
        channel.update_snapshot(910, 95, 97.0, 1.6, 650)
        findings = channel.diagnose_faults()
        fault_types = {item["fault_type"] for item in findings}

        assert "cooling_system_abnormal" in fault_types
        assert "lubrication_system_abnormal" in fault_types
        assert "overload_or_combustion_inefficiency" in fault_types
        
        # Check newly added fields
        for finding in findings:
            assert "supporting_features" in finding
            assert "timestamp" in finding

    def test_nmea2000_ingest_builds_snapshot_from_pgn_127489_full(self, channel):
        base_count = len(channel.snapshots)
        rapid = SimpleNamespace(pgn=127488, fields={"engine_instance": 0, "speed": 745.0})
        dynamic_full = SimpleNamespace(pgn=127489, fields={
            "engine_instance": 0, 
            "engine_load": 75.0, 
            "fuel_rate": 490.0,
            "oil_pressure": 325000.0,
            "coolant_temp": 360.15
        })
        # first ingest rapid -> rpm
        assert channel.ingest_nmea2000_message(rapid) is False
        # then ingest dynamic -> generates snapshot because all fields present
        assert channel.ingest_nmea2000_message(dynamic_full) is True

        latest = channel.get_latest_snapshot()
        assert len(channel.snapshots) == base_count + 1
        assert latest.rpm == 745.0
        assert latest.load == 75.0
        assert round(latest.oil_pressure, 2) == 3.25
        assert round(latest.coolant_temp, 1) == 87.0
        assert latest.fuel_rate == 490.0

    def test_query_engine_status_fault_response(self, channel):
        channel.update_snapshot(910, 95, 97.0, 1.6, 650)
        text = channel.query_engine_status("请做一下故障诊断")

        assert text.startswith("故障诊断：")
        assert "cooling_system_abnormal" in text


class TestEngineSnapshot:
    def test_snapshot_to_dict_rounding(self):
        snap = EngineSnapshot(
            rpm=721.27,
            load=68.84,
            coolant_temp=78.56,
            oil_pressure=3.456,
            fuel_rate=465.44,
        )

        data = snap.to_dict()
        assert data["rpm"] == 721.3
        assert data["load"] == 68.8
        assert data["coolant_temp"] == 78.6
        assert data["oil_pressure"] == 3.46
        assert data["fuel_rate"] == 465.4
        assert "timestamp" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
