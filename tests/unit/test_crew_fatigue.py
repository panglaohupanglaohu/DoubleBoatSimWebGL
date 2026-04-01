# -*- coding: utf-8 -*-
"""
Tests for L5: Crew Fatigue Monitor Channel — 船员疲劳监测
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from channels.crew_fatigue_monitor import CrewFatigueMonitorChannel


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture
def channel():
    ch = CrewFatigueMonitorChannel()
    ch.initialize()
    return ch


# ---- 1. 实例化和默认状态 ----

class TestInstantiationAndStatus:
    def test_default_status(self, channel):
        status = channel.get_status()
        assert status["name"] == "crew_fatigue"
        assert status["active"] is True
        assert status["fatigue_scores"] == {}
        assert status["risk_alerts"] == []
        assert status["total_crew_tracked"] == 0
        assert status["watch_changes_count"] == 0
        assert status["active_watch"] == []

    def test_uninitialized_channel(self):
        ch = CrewFatigueMonitorChannel()
        status = ch.get_status()
        assert status["active"] is False
        assert status["total_crew_tracked"] == 0

    def test_shutdown(self, channel):
        result = channel.shutdown()
        assert result is True
        status = channel.get_status()
        assert status["active"] is False


# ---- 2. watch_change 事件 ----

class TestWatchChange:
    def test_record_watch_change(self, channel):
        result = _run(channel.process_event({
            "type": "watch_change",
            "crew_id": "officer_1",
            "position": "bridge",
            "start_time": datetime.now().isoformat(),
        }))
        assert result["status"] == "recorded"
        assert result["crew_id"] == "officer_1"
        assert "fatigue_score" in result

    def test_active_watch_tracking(self, channel):
        _run(channel.process_event({
            "type": "watch_change",
            "crew_id": "officer_1",
            "position": "bridge",
        }))
        status = channel.get_status()
        assert len(status["active_watch"]) == 1
        assert status["active_watch"][0]["crew_id"] == "officer_1"

    def test_end_watch_removes_from_active(self, channel):
        now = datetime.now()
        _run(channel.process_event({
            "type": "watch_change",
            "crew_id": "officer_1",
            "position": "bridge",
            "start_time": now.isoformat(),
        }))
        _run(channel.process_event({
            "type": "watch_change",
            "crew_id": "officer_1",
            "position": "bridge",
            "start_time": now.isoformat(),
            "end_time": (now + timedelta(hours=4)).isoformat(),
        }))
        status = channel.get_status()
        active_ids = [w["crew_id"] for w in status["active_watch"]]
        assert "officer_1" not in active_ids

    def test_watch_changes_count(self, channel):
        for _ in range(3):
            _run(channel.process_event({
                "type": "watch_change",
                "crew_id": "officer_1",
                "position": "bridge",
            }))
        status = channel.get_status()
        assert status["watch_changes_count"] == 3


# ---- 3. rest_record 事件 ----

class TestRestRecord:
    def test_record_rest(self, channel):
        now = datetime.now()
        result = _run(channel.process_event({
            "type": "rest_record",
            "crew_id": "officer_1",
            "rest_start": now.isoformat(),
            "rest_end": (now + timedelta(hours=8)).isoformat(),
            "quality": "good",
        }))
        assert result["status"] == "recorded"
        assert result["crew_id"] == "officer_1"

    def test_rest_record_default_quality(self, channel):
        now = datetime.now()
        _run(channel.process_event({
            "type": "rest_record",
            "crew_id": "officer_1",
            "rest_start": now.isoformat(),
            "rest_end": (now + timedelta(hours=7)).isoformat(),
        }))
        status = channel.get_status()
        assert status["total_crew_tracked"] == 1


# ---- 4. workload_event 事件 ----

class TestWorkloadEvent:
    def test_record_workload(self, channel):
        result = _run(channel.process_event({
            "type": "workload_event",
            "crew_id": "officer_1",
            "event_type": "emergency",
            "intensity": "high",
        }))
        assert result["status"] == "recorded"
        assert result["crew_id"] == "officer_1"

    def test_workload_default_intensity(self, channel):
        result = _run(channel.process_event({
            "type": "workload_event",
            "crew_id": "officer_2",
        }))
        assert result["status"] == "recorded"


# ---- 5. 疲劳评分计算 ----

class TestFatigueScoreCalculation:
    def test_work_over_4h_deducts(self, channel):
        """连续工作 > 4h → 每小时扣 10 分"""
        now = datetime.now()
        start = now - timedelta(hours=6)
        _run(channel.process_event({
            "type": "watch_change",
            "crew_id": "test_crew",
            "position": "engine",
            "start_time": start.isoformat(),
        }))
        score = channel.calculate_fatigue_score("test_crew")
        # 6h on duty: (6-4)*10 = 20 deduction, and no rest = -20 more
        assert score < 80

    def test_work_under_4h_no_deduction(self, channel):
        """连续工作 < 4h → 工作时间不扣分"""
        now = datetime.now()
        start = now - timedelta(hours=2)
        end = now
        _run(channel.process_event({
            "type": "watch_change",
            "crew_id": "test_crew",
            "position": "engine",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
        }))
        # 只有 watch 记录无 rest → 扣 20 分休息不足
        score = channel.calculate_fatigue_score("test_crew")
        assert score == pytest.approx(80.0)

    def test_rest_under_6h_deducts_20(self, channel):
        """休息 < 6h → 扣 20 分"""
        now = datetime.now()
        _run(channel.process_event({
            "type": "rest_record",
            "crew_id": "test_crew",
            "rest_start": (now - timedelta(hours=4)).isoformat(),
            "rest_end": now.isoformat(),
            "quality": "normal",
        }))
        score = channel.calculate_fatigue_score("test_crew")
        assert score == pytest.approx(80.0)

    def test_poor_rest_quality_deducts(self, channel):
        """休息质量差 → 额外扣分"""
        now = datetime.now()
        _run(channel.process_event({
            "type": "rest_record",
            "crew_id": "test_crew",
            "rest_start": (now - timedelta(hours=4)).isoformat(),
            "rest_end": now.isoformat(),
            "quality": "poor",
        }))
        score = channel.calculate_fatigue_score("test_crew")
        # 4h rest < 6h → -20, poor quality → -10
        assert score == pytest.approx(70.0)

    def test_high_intensity_deducts_5(self, channel):
        """高强度事件 → 每个扣 5 分"""
        for _ in range(3):
            _run(channel.process_event({
                "type": "workload_event",
                "crew_id": "test_crew",
                "intensity": "high",
            }))
        score = channel.calculate_fatigue_score("test_crew")
        assert score == pytest.approx(85.0)

    def test_normal_intensity_no_deduction(self, channel):
        """正常强度事件 → 不扣分"""
        _run(channel.process_event({
            "type": "workload_event",
            "crew_id": "test_crew",
            "intensity": "normal",
        }))
        score = channel.calculate_fatigue_score("test_crew")
        assert score == pytest.approx(100.0)

    def test_score_range_0_to_100(self, channel):
        """评分范围 0-100"""
        score = channel.calculate_fatigue_score("nonexistent")
        assert 0 <= score <= 100

    def test_score_floor_zero(self, channel):
        """极端疲劳不会低于 0"""
        now = datetime.now()
        start = now - timedelta(hours=20)
        _run(channel.process_event({
            "type": "watch_change",
            "crew_id": "exhausted",
            "position": "bridge",
            "start_time": start.isoformat(),
        }))
        for _ in range(20):
            _run(channel.process_event({
                "type": "workload_event",
                "crew_id": "exhausted",
                "intensity": "high",
            }))
        score = channel.calculate_fatigue_score("exhausted")
        assert score == 0.0


# ---- 6. 疲劳建议 ----

class TestFatigueRecommendations:
    def test_critical_fatigue_recommends_change(self, channel):
        """评分 < 40 → 建议立即换班"""
        now = datetime.now()
        start = now - timedelta(hours=15)
        _run(channel.process_event({
            "type": "watch_change",
            "crew_id": "tired_crew",
            "position": "bridge",
            "start_time": start.isoformat(),
        }))
        recs = channel.get_fatigue_recommendations()
        tired_rec = next(r for r in recs if r["crew_id"] == "tired_crew")
        assert tired_rec["level"] == "critical"
        assert "立即换班" in tired_rec["recommendation"]

    def test_good_fatigue_status(self, channel):
        """评分 > 80 → 状态良好"""
        now = datetime.now()
        _run(channel.process_event({
            "type": "rest_record",
            "crew_id": "rested_crew",
            "rest_start": (now - timedelta(hours=8)).isoformat(),
            "rest_end": now.isoformat(),
            "quality": "good",
        }))
        recs = channel.get_fatigue_recommendations()
        rested_rec = next(r for r in recs if r["crew_id"] == "rested_crew")
        assert rested_rec["level"] == "good"
        assert "状态良好" in rested_rec["recommendation"]

    def test_warning_level(self, channel):
        """评分 40-60 → warning"""
        now = datetime.now()
        start = now - timedelta(hours=10)
        _run(channel.process_event({
            "type": "watch_change",
            "crew_id": "fatigued",
            "position": "bridge",
            "start_time": start.isoformat(),
        }))
        recs = channel.get_fatigue_recommendations()
        rec = next(r for r in recs if r["crew_id"] == "fatigued")
        assert rec["level"] in ("warning", "critical")

    def test_no_crew_empty_recommendations(self, channel):
        recs = channel.get_fatigue_recommendations()
        assert recs == []


# ---- 7. 多人员同时追踪 ----

class TestMultiCrewTracking:
    def test_track_multiple_crew_members(self, channel):
        for i in range(5):
            _run(channel.process_event({
                "type": "watch_change",
                "crew_id": f"crew_{i}",
                "position": "bridge",
            }))
        status = channel.get_status()
        assert status["total_crew_tracked"] == 5
        assert len(status["fatigue_scores"]) == 5

    def test_independent_scores(self, channel):
        """不同船员的疲劳评分独立计算"""
        now = datetime.now()
        _run(channel.process_event({
            "type": "watch_change",
            "crew_id": "crew_a",
            "position": "bridge",
            "start_time": (now - timedelta(hours=12)).isoformat(),
        }))
        _run(channel.process_event({
            "type": "rest_record",
            "crew_id": "crew_b",
            "rest_start": (now - timedelta(hours=8)).isoformat(),
            "rest_end": now.isoformat(),
        }))
        score_a = channel.calculate_fatigue_score("crew_a")
        score_b = channel.calculate_fatigue_score("crew_b")
        assert score_a < score_b

    def test_risk_alerts_only_for_fatigued(self, channel):
        now = datetime.now()
        _run(channel.process_event({
            "type": "watch_change",
            "crew_id": "fatigued",
            "position": "bridge",
            "start_time": (now - timedelta(hours=15)).isoformat(),
        }))
        _run(channel.process_event({
            "type": "rest_record",
            "crew_id": "rested",
            "rest_start": (now - timedelta(hours=8)).isoformat(),
            "rest_end": now.isoformat(),
        }))
        status = channel.get_status()
        alert_crew_ids = [a["crew_id"] for a in status["risk_alerts"]]
        assert "fatigued" in alert_crew_ids
        assert "rested" not in alert_crew_ids


# ---- 8. 空 crew_id 异常处理 ----

class TestEmptyCrewId:
    def test_watch_change_no_crew_id(self, channel):
        result = _run(channel.process_event({
            "type": "watch_change",
            "position": "bridge",
        }))
        assert result["status"] == "error"
        assert "crew_id" in result["reason"]

    def test_rest_record_no_crew_id(self, channel):
        result = _run(channel.process_event({
            "type": "rest_record",
            "rest_start": datetime.now().isoformat(),
        }))
        assert result["status"] == "error"
        assert "crew_id" in result["reason"]

    def test_workload_event_no_crew_id(self, channel):
        result = _run(channel.process_event({
            "type": "workload_event",
            "intensity": "high",
        }))
        assert result["status"] == "error"
        assert "crew_id" in result["reason"]


# ---- 9. 未知事件和边界 ----

class TestEdgeCases:
    def test_unknown_event_type(self, channel):
        result = _run(channel.process_event({"type": "party_on_deck"}))
        assert result["status"] == "ignored"

    def test_empty_event(self, channel):
        result = _run(channel.process_event({}))
        assert result["status"] == "ignored"

    def test_start_stop(self, channel):
        _run(channel.start())
        status = channel.get_status()
        assert status["active"] is True
        _run(channel.stop())
        status = channel.get_status()
        assert status["active"] is False

    def test_nonexistent_crew_score(self, channel):
        score = channel.calculate_fatigue_score("ghost")
        assert score == 100.0
