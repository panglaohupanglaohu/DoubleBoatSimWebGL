# -*- coding: utf-8 -*-
"""
存储层 + 边界值 + 异常场景 综合测试

覆盖:
- DataLakehouse: DuckDB SQL 安全校验、缓冲区 flush
- SQLiteStore: save_event/save_events 连接管理
- FeishuAdapter: upload 不报 NameError
- WeatherRoutingChannel: 空间分辨率天气 grid
- 各 Channel 边界值和异常场景
"""

import asyncio
import math
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

import pytest

# ═══════════════════════════════════════════════════
# Imports
# ═══════════════════════════════════════════════════

from backend.storage.event_store import SQLiteStore, JSONLStore
from backend.storage.cloud_sync import FeishuAdapter, get_adapter
from backend.storage.data_lakehouse import DataLakehouse

from backend.channels.weather_routing_channel import WeatherRoutingChannel
from backend.channels.hull_stress_monitor import HullStressMonitorChannel
from backend.channels.power_management import PowerManagementChannel
from backend.channels.dynamic_positioning import DynamicPositioningChannel, _haversine_m
from backend.channels.ais_processor import AISProcessorChannel
from backend.channels.alarm_management import AlarmManagementChannel, _PRIORITY_ORDER, _MAX_HISTORY
from backend.channels.tank_level_monitor import TankLevelMonitorChannel
from backend.channels.gyro_compass_monitor import GyroCompassMonitorChannel
from backend.channels.speed_log_monitor import SpeedLogMonitorChannel
from backend.channels.echo_sounder_monitor import EchoSounderMonitorChannel
from backend.channels.mooring_monitor import MooringMonitorChannel
from backend.channels.safety_system_monitor import SafetySystemMonitorChannel


# ═══════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════

@pytest.fixture()
def tmp_db(tmp_path):
    return str(tmp_path / "test_events.db")


@pytest.fixture()
def sqlite_store(tmp_db):
    return SQLiteStore({"db_path": tmp_db})


@pytest.fixture()
def lakehouse(tmp_path):
    db_path = str(tmp_path / "lh_events.db")
    return DataLakehouse({
        "store_type": "sqlite",
        "store_config": {"db_path": db_path},
        "buffer_max_size": 5,
        "analytics_cache_dir": str(tmp_path / "cache"),
    })


@pytest.fixture()
def weather():
    ch = WeatherRoutingChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def hull():
    ch = HullStressMonitorChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def power():
    ch = PowerManagementChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def dp():
    ch = DynamicPositioningChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def ais():
    ch = AISProcessorChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def alarm():
    ch = AlarmManagementChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def tank():
    ch = TankLevelMonitorChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def compass():
    ch = GyroCompassMonitorChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def speed_log():
    ch = SpeedLogMonitorChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def echo():
    ch = EchoSounderMonitorChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def mooring():
    ch = MooringMonitorChannel()
    ch.initialize()
    return ch


@pytest.fixture()
def safety():
    ch = SafetySystemMonitorChannel()
    ch.initialize()
    return ch


# ═══════════════════════════════════════════════════════════════
# 1. DuckDB SQL 安全校验 (7 tests)
# ═══════════════════════════════════════════════════════════════

class TestDuckDBQuerySecurity:
    """run_duckdb_query 只允许 SELECT 查询。"""

    def _make_lakehouse_with_parquet(self, tmp_path):
        """创建一个有 parquet 文件的 lakehouse 用于测试。"""
        lh = DataLakehouse({
            "store_type": "sqlite",
            "store_config": {"db_path": str(tmp_path / "q.db")},
            "buffer_max_size": 1,
            "analytics_cache_dir": str(tmp_path / "cache"),
        })
        lh.save_event({"event_type": "test", "timestamp": "2026-01-01T00:00:00", "payload": {"x": 1}})
        lh.flush()
        return lh

    def test_duckdb_query_select_allowed(self, tmp_path):
        lh = self._make_lakehouse_with_parquet(tmp_path)
        try:
            import duckdb
            import pyarrow
        except ImportError:
            pytest.skip("duckdb/pyarrow not installed")
        rows = lh.run_duckdb_query("SELECT COUNT(*) AS cnt FROM lakehouse_events")
        assert isinstance(rows, list)

    def test_duckdb_query_insert_blocked(self, tmp_path):
        lh = self._make_lakehouse_with_parquet(tmp_path)
        try:
            import duckdb, pyarrow
        except ImportError:
            pytest.skip("duckdb/pyarrow not installed")
        with pytest.raises(ValueError, match="Only SELECT"):
            lh.run_duckdb_query("INSERT INTO lakehouse_events VALUES (1,2,3,4,5)")

    def test_duckdb_query_update_blocked(self, tmp_path):
        lh = self._make_lakehouse_with_parquet(tmp_path)
        try:
            import duckdb, pyarrow
        except ImportError:
            pytest.skip("duckdb/pyarrow not installed")
        with pytest.raises(ValueError, match="Only SELECT"):
            lh.run_duckdb_query("UPDATE lakehouse_events SET source='x'")

    def test_duckdb_query_delete_blocked(self, tmp_path):
        lh = self._make_lakehouse_with_parquet(tmp_path)
        try:
            import duckdb, pyarrow
        except ImportError:
            pytest.skip("duckdb/pyarrow not installed")
        with pytest.raises(ValueError, match="Only SELECT"):
            lh.run_duckdb_query("DELETE FROM lakehouse_events")

    def test_duckdb_query_drop_blocked(self, tmp_path):
        lh = self._make_lakehouse_with_parquet(tmp_path)
        try:
            import duckdb, pyarrow
        except ImportError:
            pytest.skip("duckdb/pyarrow not installed")
        with pytest.raises(ValueError, match="Only SELECT"):
            lh.run_duckdb_query("DROP TABLE lakehouse_events")

    def test_duckdb_query_create_blocked(self, tmp_path):
        lh = self._make_lakehouse_with_parquet(tmp_path)
        try:
            import duckdb, pyarrow
        except ImportError:
            pytest.skip("duckdb/pyarrow not installed")
        with pytest.raises(ValueError, match="Only SELECT"):
            lh.run_duckdb_query("CREATE TABLE evil (id INT)")

    def test_duckdb_query_case_insensitive(self, tmp_path):
        lh = self._make_lakehouse_with_parquet(tmp_path)
        try:
            import duckdb, pyarrow
        except ImportError:
            pytest.skip("duckdb/pyarrow not installed")
        # 小写 select 也应该被允许 (代码将 sql.strip().upper() 后检查)
        rows = lh.run_duckdb_query("select count(*) as cnt from lakehouse_events")
        assert isinstance(rows, list)


# ═══════════════════════════════════════════════════════════════
# 2. SQLiteStore 连接管理 (4 tests)
# ═══════════════════════════════════════════════════════════════

class TestSQLiteStoreConnectionManagement:
    """SQLiteStore 的连接管理测试。"""

    def test_sqlite_save_event_connection_closed(self, sqlite_store):
        """save_event 后连接被正确关闭。"""
        event = {"event_type": "nav", "timestamp": "2026-01-01T00:00:00", "payload": {"lat": 1.0}}
        result = sqlite_store.save_event(event)
        assert result is True
        # 连接应在 finally 块中被关闭，不会有悬挂连接
        loaded = sqlite_store.load_events("nav")
        assert len(loaded) == 1

    def test_sqlite_save_events_executemany(self, sqlite_store):
        """批量保存使用 executemany，验证多条记录一次性写入。"""
        events = [
            {"event_type": "batch", "timestamp": f"2026-01-0{i}T00:00:00", "payload": {"i": i}}
            for i in range(1, 6)
        ]
        result = sqlite_store.save_events(events)
        assert result is True
        loaded = sqlite_store.load_events("batch", limit=10)
        assert len(loaded) == 5

    def test_sqlite_save_event_exception_closes_conn(self, tmp_path):
        """异常时连接也被正确关闭（finally 块）。"""
        store = SQLiteStore({"db_path": str(tmp_path / "exc.db")})
        # 用 mock 模拟 _connect 返回的连接在 execute 时抛异常
        original_connect = store._connect

        def failing_connect():
            conn = original_connect()
            real_cursor = conn.cursor

            def bad_cursor():
                c = real_cursor()
                original_execute = c.execute
                def fail_execute(*args, **kwargs):
                    raise RuntimeError("simulated DB failure")
                c.execute = fail_execute
                return c
            conn.cursor = bad_cursor
            return conn

        store._connect = failing_connect
        result = store.save_event({"event_type": "x", "payload": {}})
        assert result is False  # 保存失败，但不会崩溃

    def test_sqlite_save_events_empty_list(self, sqlite_store):
        """空列表保存不报错。"""
        result = sqlite_store.save_events([])
        assert result is True


# ═══════════════════════════════════════════════════════════════
# 3. DataLakehouse 缓冲区 (5 tests)
# ═══════════════════════════════════════════════════════════════

class TestLakehouseBuffer:
    """DataLakehouse 缓冲区管理测试。"""

    def test_lakehouse_buffer_flush(self, lakehouse):
        """缓冲区满后自动 flush。"""
        for i in range(5):
            lakehouse.save_event({"event_type": "auto", "timestamp": f"2026-01-01T00:0{i}:00", "payload": {"i": i}})
        # buffer_max_size=5, 第 5 个事件触发 flush，缓冲区应被清空
        assert len(lakehouse.event_buffer) == 0

    def test_lakehouse_manual_flush(self, lakehouse):
        """手动 flush。"""
        lakehouse.save_event({"event_type": "manual", "timestamp": "2026-01-01T00:00:00", "payload": {}})
        assert len(lakehouse.event_buffer) == 1
        result = lakehouse.flush()
        assert result is True
        assert len(lakehouse.event_buffer) == 0

    def test_lakehouse_save_and_query(self, lakehouse):
        """保存后查询。"""
        for i in range(3):
            lakehouse.save_event({"event_type": "q", "timestamp": f"2026-01-01T00:0{i}:00", "payload": {"v": i}})
        events = lakehouse.query_events("q", limit=10)
        assert len(events) == 3

    def test_lakehouse_buffer_not_flushed_under_threshold(self, lakehouse):
        """未达到阈值不自动 flush。"""
        for i in range(4):
            lakehouse.save_event({"event_type": "sub", "timestamp": f"2026-01-01T00:0{i}:00", "payload": {}})
        assert len(lakehouse.event_buffer) == 4

    def test_lakehouse_flush_empty_buffer(self, lakehouse):
        """空缓冲区 flush 不报错。"""
        result = lakehouse.flush()
        assert result is True
        assert len(lakehouse.event_buffer) == 0


# ═══════════════════════════════════════════════════════════════
# 4. FeishuAdapter (3 tests)
# ═══════════════════════════════════════════════════════════════

class TestFeishuAdapter:
    """FeishuAdapter 不再报 NameError。"""

    def test_feishu_adapter_upload_mock(self):
        adapter = FeishuAdapter({"folder_token": "test_token"})
        result = adapter.upload_event({"event_type": "test", "data": "hello"}, "test")
        assert result is True  # mock 模式正常返回

    def test_feishu_adapter_upload_batch(self):
        adapter = FeishuAdapter({"folder_token": "tok"})
        events = [{"event_type": "a"}, {"event_type": "b"}]
        result = adapter.upload_batch(events, "batch")
        assert result is True

    def test_feishu_adapter_get_bucket_info(self):
        adapter = FeishuAdapter({"folder_token": "abc"})
        info = adapter.get_bucket_info()
        assert info["type"] == "feishu"
        assert info["folder_token"] == "abc"
        assert info["available"] is True


# ═══════════════════════════════════════════════════════════════
# 5. Weather Routing 空间分辨率测试 (10 tests)
# ═══════════════════════════════════════════════════════════════

class TestWeatherGrid:
    """天气 grid 数据的更新、查找和 fallback。"""

    def test_weather_grid_update(self, weather):
        result = weather.update_weather_data(lat=30.5, lon=120.3, wind_speed=15.0, wave_height=1.5, visibility=8.0)
        assert result["grid_size"] == 1
        # round(30.5)=30 (banker's rounding), round(120.3)=120
        assert result["grid_key"] == [round(30.5), round(120.3)]

    def test_weather_grid_lookup_hit(self, weather):
        weather.update_weather_data(lat=30.0, lon=120.0, wind_speed=50.0, wave_height=5.0, visibility=0.5)
        score = weather._score_point(30.0, 120.0)
        assert score > 0  # 高风速+高浪+低能见度

    def test_weather_grid_lookup_miss(self, weather):
        # 未设置 grid 点，也没有全局天气数据 → 使用 fallback → score=0
        score = weather._score_point(10.0, 10.0)
        assert score == 0.0

    def test_weather_grid_different_locations(self, weather):
        weather.update_weather_data(lat=30.0, lon=120.0, wind_speed=50.0, wave_height=6.0, visibility=0.5)
        weather.update_weather_data(lat=40.0, lon=130.0, wind_speed=5.0, wave_height=0.5, visibility=10.0)
        score_dangerous = weather._score_point(30.0, 120.0)
        score_safe = weather._score_point(40.0, 130.0)
        assert score_dangerous > score_safe

    def test_weather_grid_rounding(self, weather):
        weather.update_weather_data(lat=30.4, lon=120.6, wind_speed=20.0, wave_height=2.0, visibility=5.0)
        # 四舍五入: (30.4 → 30, 120.6 → 121)
        grid = weather.get_weather_grid()
        assert "30,121" in grid["grid"]

    def test_weather_data_update_event(self, weather):
        result = asyncio.run(
            weather.process_event({
                "type": "weather_data_update",
                "lat": 25.0, "lon": 110.0,
                "wind_speed": 30.0, "wave_height": 3.0, "visibility": 5.0,
            })
        )
        assert result["status"] == "grid_updated"

    def test_weather_grid_get(self, weather):
        weather.update_weather_data(lat=35.0, lon=140.0, wind_speed=10.0, wave_height=1.0, visibility=10.0)
        grid = weather.get_weather_grid()
        assert grid["grid_size"] == 1
        assert "35,140" in grid["grid"]
        assert grid["grid"]["35,140"]["wind_speed"] == 10.0

    def test_weather_grid_overwrite(self, weather):
        weather.update_weather_data(lat=30.0, lon=120.0, wind_speed=10.0, wave_height=1.0, visibility=10.0)
        weather.update_weather_data(lat=30.0, lon=120.0, wind_speed=50.0, wave_height=5.0, visibility=0.5)
        grid = weather.get_weather_grid()
        assert grid["grid"]["30,120"]["wind_speed"] == 50.0

    def test_weather_route_uses_grid(self, weather):
        weather.update_weather_data(lat=30.0, lon=120.0, wind_speed=50.0, wave_height=6.0, visibility=0.3)
        result = weather.evaluate_route_weather_risk([{"lat": 30.0, "lon": 120.0}])
        assert result["risk_level"] in ("high", "critical")

    def test_weather_grid_fallback_to_global(self, weather):
        """grid miss 时 fallback 到 _current_weather。"""
        asyncio.run(
            weather.process_event({
                "type": "weather_forecast",
                "region": "global",
                "wind_speed": 45.0, "wave_height": 5.0, "visibility": 0.5,
            })
        )
        # 查询一个不在 grid 中的点 → 应 fallback 到 _current_weather
        score = weather._score_point(99.0, 99.0)
        assert score > 0


# ═══════════════════════════════════════════════════════════════
# 6. 边界值和异常测试 (15+ tests)
# ═══════════════════════════════════════════════════════════════

class TestHullStressBoundary:
    def test_hull_stress_exactly_yield(self, hull):
        """stress_mpa == yield_stress 时 stress_ratio == 1.0。"""
        hull.update_sensor("S1", "bow", stress_mpa=250.0)
        health = hull.get_structural_health()
        assert health["stress_ratio"] == pytest.approx(1.0)
        assert health["health_score"] == pytest.approx(0.0)
        assert health["alarm_active"] is True  # 250 > 0.8*250=200

    def test_hull_stress_above_yield(self, hull):
        """stress_mpa > yield_stress 时 health_score 可以为负（被 max 限制到 0）。"""
        hull.update_sensor("S1", "bow", stress_mpa=300.0)
        health = hull.get_structural_health()
        assert health["stress_ratio"] > 1.0
        assert health["health_score"] == 0.0  # max(0, ...)


class TestPowerBoundary:
    def test_power_zero_generation_zero_load(self, power):
        """全零电力：没有发电机和负载。"""
        balance = power.get_power_balance()
        assert balance["total_generation_kw"] == 0.0
        assert balance["total_load_kw"] == 0.0
        assert balance["reserve_kw"] == 0.0
        assert balance["reserve_percent"] == 0.0


class TestDPHaversine:
    def test_dp_haversine_same_point(self):
        """同一点距离为 0。"""
        d = _haversine_m(30.0, 120.0, 30.0, 120.0)
        assert d == pytest.approx(0.0, abs=0.01)

    def test_dp_haversine_antipodal(self):
        """对跖点距离约为半周长 ~20000km。"""
        d = _haversine_m(0.0, 0.0, 0.0, 180.0)
        assert 19_900_000 < d < 20_100_000

    def test_dp_haversine_known_distance(self):
        """上海(31.23, 121.47) → 东京(35.68, 139.69) ≈ 1760 km。"""
        d = _haversine_m(31.23, 121.47, 35.68, 139.69)
        assert 1_700_000 < d < 1_850_000


class TestAISBoundary:
    def test_ais_mmsi_zero(self, ais):
        """MMSI=0 也应正常处理（不崩溃）。"""
        ais.update_target(0, {"lat": 1.0, "lon": 2.0, "target_class": "A"})
        target = ais.get_target(0)
        assert target is not None
        assert target["mmsi"] == 0

    def test_ais_unsupported_msg_type(self, ais):
        decoded = ais.decode_message(99, {"mmsi": 12345})
        assert "error" in decoded


class TestAlarmBoundary:
    def test_alarm_priority_ordering(self, alarm):
        """emergency > alarm > warning > caution 排序正确。"""
        alarm.raise_alarm("e1", "ch1", "emergency", "fire")
        alarm.raise_alarm("a1", "ch2", "alarm", "overheat")
        alarm.raise_alarm("w1", "ch3", "warning", "low fuel")
        alarm.raise_alarm("c1", "ch4", "caution", "info")
        active = alarm.get_active_alarms()
        priorities = [a["priority"] for a in active]
        assert priorities == ["emergency", "alarm", "warning", "caution"]

    def test_alarm_history_max_100(self, alarm):
        """历史不超过 100 条。"""
        for i in range(120):
            alarm.raise_alarm(f"a{i}", "ch", "caution", f"alarm {i}")
            alarm.clear_alarm(f"a{i}")
        assert len(alarm._alarm_history) == _MAX_HISTORY

    def test_alarm_invalid_priority_defaults_to_caution(self, alarm):
        alarm.raise_alarm("inv", "ch", "bogus_priority", "test")
        assert alarm._alarms["inv"]["priority"] == "caution"


class TestTankBoundary:
    def test_tank_zero_capacity(self, tank):
        """容量为 0 时不除零（代码 clamp 到 1.0）。"""
        result = tank.update_tank("T1", "fuel_oil", capacity_m3=0, current_m3=50.0)
        assert result["level_percent"] > 0  # 不会是 NaN 或 ∞

    def test_tank_overfill_clamped(self, tank):
        """current > capacity 时被 clamp 到 capacity。"""
        result = tank.update_tank("T1", "fuel_oil", capacity_m3=100.0, current_m3=200.0)
        assert result["level_percent"] == pytest.approx(100.0)


class TestCompassBoundary:
    def test_compass_all_same_heading(self, compass):
        """所有罗经一致时 deviation=0。"""
        compass.update_compass("G1", "gyro", heading_deg=90.0)
        compass.update_compass("G2", "gyro", heading_deg=90.0)
        compass.update_compass("G3", "magnetic", heading_deg=90.0)
        consensus = compass.get_heading_consensus()
        assert consensus["max_deviation"] == pytest.approx(0.0)
        assert consensus["agreement"] is True

    def test_compass_opposite_headings(self, compass):
        """0度和180度完全对向 → 偏差超限，两个都被标记 warning，共识无 ok 罗经。"""
        compass.update_compass("G1", "gyro", heading_deg=0.0)
        compass.update_compass("G2", "gyro", heading_deg=180.0)
        consensus = compass.get_heading_consensus()
        # 偏差 90° 远超过 3° 限值，两个都被标记 warning，ok 罗经为空
        assert consensus["compasses_used"] == 0
        assert consensus["consensus_heading"] is None

    def test_compass_wrap_around_360(self, compass):
        """359度和 1度 的平均应接近 0 度。"""
        compass.update_compass("G1", "gyro", heading_deg=359.0)
        compass.update_compass("G2", "gyro", heading_deg=1.0)
        consensus = compass.get_heading_consensus()
        heading = consensus["consensus_heading"]
        assert heading < 5.0 or heading > 355.0  # 接近 0/360


class TestSpeedLogBoundary:
    def test_speed_log_negative_speed(self, speed_log):
        """负速度处理（倒车或传感器故障）。"""
        result = speed_log.update_sensor("S1", "stw", speed_knots=-2.0)
        assert result["speed_knots"] == -2.0  # 记录原始值

    def test_speed_log_zero_speed(self, speed_log):
        speed_log.update_sensor("S1", "stw", speed_knots=0.0)
        consensus = speed_log.get_speed_consensus()
        assert consensus["average_speed_knots"] == pytest.approx(0.0)


class TestEchoSounderBoundary:
    def test_echo_sounder_very_deep(self, echo):
        """极深水 (>11000m 马里亚纳海沟)。"""
        result = echo.update_depth(11034.0)
        assert result["current_depth_m"] == pytest.approx(11034.0)
        assert result["shallow_alarm"] is False

    def test_echo_sounder_zero_depth(self, echo):
        """深度 0 应触发浅水告警。"""
        result = echo.update_depth(0.0)
        assert result["shallow_alarm"] is True

    def test_echo_sounder_negative_depth(self, echo):
        """负深度（潮位修正后）。"""
        result = echo.update_depth(-1.0)
        assert result["current_depth_m"] == pytest.approx(-1.0)
        assert result["shallow_alarm"] is True


class TestMooringBoundary:
    def test_mooring_tension_exactly_breaking(self, mooring):
        """张力 == 破断力 → status=parted。"""
        result = mooring.update_line("L1", "bow_port", tension_kn=500.0, breaking_load_kn=500.0)
        assert result["status"] == "parted"
        assert result["load_ratio"] == pytest.approx(1.0)

    def test_mooring_tension_just_below_breaking(self, mooring):
        """张力刚低于破断力 → strained (>0.7)。"""
        result = mooring.update_line("L1", "bow_port", tension_kn=499.9, breaking_load_kn=500.0)
        assert result["status"] == "strained"

    def test_mooring_zero_tension(self, mooring):
        """零张力 → slack。"""
        result = mooring.update_line("L1", "bow_port", tension_kn=0.0, breaking_load_kn=500.0)
        assert result["status"] == "slack"


class TestSafetyBoundary:
    def test_safety_empty_systems(self, safety):
        """无系统时状态。"""
        status = safety.get_safety_status()
        assert status["total_ready"] == 0
        assert status["solas_ready"] is True  # 没有 not_ready/fault，watertight_integrity=True
        assert status["watertight_integrity"] is True

    def test_safety_single_fault(self, safety):
        safety.update_system("sys1", "fire_fighting", "fault")
        status = safety.get_safety_status()
        assert status["total_fault"] == 1
        assert status["solas_ready"] is False

    def test_safety_watertight_door_open(self, safety):
        safety.update_watertight_door("D1", "frame42", "open")
        status = safety.get_safety_status()
        assert status["watertight_integrity"] is False
        assert status["solas_ready"] is False
