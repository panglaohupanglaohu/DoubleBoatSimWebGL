# -*- coding: utf-8 -*-
"""
EEXI 参考线系数修正回归测试 & 新 Channel 边界测试

任务 1: 验证 EEXI 参考线系数已从错误值 (如 a=9617.9) 修正为 IMO MEPC.333(76)
任务 2: ballast_water_monitor / emission_monitor / anchor_watch_channel 边界用例
"""

import asyncio
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src/backend"))

import pytest
from channels.eexi_calculator import EEXICalculator
from channels.efficiency_models import VesselInfo, VesselType, FuelType
from channels.ballast_water_monitor import BallastWaterMonitorChannel
from channels.emission_monitor import EmissionMonitorChannel, FUEL_SULFUR_CONTENT
from channels.anchor_watch_channel import AnchorWatchChannel, _haversine_m


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
# 任务 1: EEXI 参考线系数修正回归测试
# ============================================================================

class TestEEXIReferenceLineRegression:
    """验证参考线 computed value 与 IMO MEPC.333(76) 一致 (不仅检查系数常量)。"""

    def test_bulk_carrier_reference_line_value(self):
        """Bulk Carrier DWT=82000 参考线: a=961.79 * 82000^(-0.477)。
        若旧值 a=9617.9 则结果会大 10 倍。
        """
        vessel = _make_vessel(VesselType.BULK_CARRIER, dwt=82000)
        calc = EEXICalculator(vessel)
        ref = calc.calculate_reference_line(82000)
        expected = 961.79 * (82000 ** (-0.477))
        assert ref == pytest.approx(expected, rel=1e-4)
        # 确保不是旧值 9617.9 的 10 倍结果
        wrong_expected = 9617.9 * (82000 ** (-0.477))
        assert ref < wrong_expected * 0.5, "参考线值疑似使用了旧系数 9617.9"

    def test_general_cargo_reference_line_value(self):
        """General Cargo DWT=15000 参考线: a=107.48 * 15000^(-0.216)。"""
        vessel = _make_vessel(VesselType.GENERAL_CARGO, dwt=15000)
        calc = EEXICalculator(vessel)
        ref = calc.calculate_reference_line(15000)
        expected = 107.48 * (15000 ** (-0.216))
        assert ref == pytest.approx(expected, rel=1e-4)

    def test_container_ship_reference_line_value(self):
        """Container Ship DWT=50000 参考线: a=174.22 * 50000^(-0.201)。"""
        vessel = _make_vessel(VesselType.CONTAINER_SHIP, dwt=50000)
        calc = EEXICalculator(vessel)
        ref = calc.calculate_reference_line(50000)
        expected = 174.22 * (50000 ** (-0.201))
        assert ref == pytest.approx(expected, rel=1e-4)

    def test_oil_tanker_reference_line_value(self):
        """Oil Tanker DWT=120000 参考线: a=1218.80 * 120000^(-0.488)。"""
        vessel = _make_vessel(VesselType.OIL_TANKER, dwt=120000)
        calc = EEXICalculator(vessel)
        ref = calc.calculate_reference_line(120000)
        expected = 1218.80 * (120000 ** (-0.488))
        assert ref == pytest.approx(expected, rel=1e-4)


class TestEEXICorrectionFactorDefaults:
    """验证 fj/fi/feff 新参数默认值不影响旧测试 (向后兼容)。"""

    def test_default_fj_fi_feff_same_as_explicit_defaults(self):
        """不传 fj/fi/feff 与显式传 fj=1,fi=1,feff=0 结果必须一致。"""
        calc = EEXICalculator(_make_vessel())
        r_default = calc.calculate_attained_eexi(installed_power=12000)
        r_explicit = calc.calculate_attained_eexi(
            installed_power=12000, fj=1.0, fi=1.0, feff=0.0,
        )
        assert r_default.attained_eexi == pytest.approx(r_explicit.attained_eexi, rel=1e-9)
        assert r_default.required_eexi == pytest.approx(r_explicit.required_eexi, rel=1e-9)

    def test_old_api_without_new_params_still_works(self):
        """只传 installed_power 和 specific_fuel_consumption 仍正常。"""
        calc = EEXICalculator(_make_vessel())
        result = calc.calculate_attained_eexi(
            installed_power=14280, specific_fuel_consumption=180.0,
        )
        assert result.attained_eexi > 0
        assert result.required_eexi > 0
        assert result.compliance_status in (True, False)

    def test_fj_greater_than_one_increases_eexi(self):
        """fj > 1 → attained EEXI 上升 (不利于合规)。"""
        calc = EEXICalculator(_make_vessel())
        base = calc.calculate_attained_eexi(installed_power=12000)
        higher = calc.calculate_attained_eexi(installed_power=12000, fj=1.3)
        assert higher.attained_eexi > base.attained_eexi
        assert higher.attained_eexi == pytest.approx(
            base.attained_eexi * 1.3, rel=1e-6,
        )

    def test_fi_greater_than_one_reduces_eexi(self):
        """fi > 1 → 分母增大 → attained EEXI 下降 (有利于合规)。"""
        calc = EEXICalculator(_make_vessel())
        base = calc.calculate_attained_eexi(installed_power=12000)
        lower = calc.calculate_attained_eexi(installed_power=12000, fi=1.5)
        assert lower.attained_eexi < base.attained_eexi

    def test_feff_positive_reduces_eexi(self):
        """feff > 0 → 有效功率减小 → attained EEXI 下降。"""
        calc = EEXICalculator(_make_vessel())
        base = calc.calculate_attained_eexi(installed_power=12000)
        reduced = calc.calculate_attained_eexi(installed_power=12000, feff=3000.0)
        assert reduced.attained_eexi < base.attained_eexi


# ============================================================================
# 任务 2-1: BallastWaterMonitor 边界测试
# ============================================================================

class TestBallastWaterBoundary:
    """压载水监测边界条件测试。"""

    def _make_channel(self):
        ch = BallastWaterMonitorChannel()
        ch.initialize()
        return ch

    # ---- D-2 合规: 微生物刚好在阈值上下 ----

    def test_d2_threshold_exactly_at_limit(self):
        """阈值常量 D2_VIABLE_ORGANISMS_50UM 应为 10 个/m³。"""
        assert BallastWaterMonitorChannel.D2_VIABLE_ORGANISMS_50UM == 10
        assert BallastWaterMonitorChannel.D2_VIABLE_ORGANISMS_10UM == 10

    def test_compliance_treated_tank_at_threshold(self):
        """已处理的满载舱在阈值边界上应合规。"""
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "tank_status", "tank_id": "T1",
            "level_percent": 100.0, "treated": True,
        }))
        compliance = ch.check_bwm_compliance()
        assert compliance["compliant"] is True

    def test_compliance_untreated_tank_at_threshold(self):
        """未处理舱 (level > 0) 应不合规。"""
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "tank_status", "tank_id": "T1",
            "level_percent": 1.0, "treated": False,
        }))
        compliance = ch.check_bwm_compliance()
        assert compliance["compliant"] is False

    def test_compliance_untreated_but_empty_tank_is_compliant(self):
        """未处理但液位 0% 的舱应合规 (空舱无需处理)。"""
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "tank_status", "tank_id": "T1",
            "level_percent": 0.0, "treated": False,
        }))
        compliance = ch.check_bwm_compliance()
        assert compliance["compliant"] is True
        assert len(compliance["untreated_tanks"]) == 0

    # ---- 空 tank 列表 ----

    def test_empty_tank_list_compliance(self):
        """无注册舱时合规 (No tanks registered)。"""
        ch = self._make_channel()
        compliance = ch.check_bwm_compliance()
        assert compliance["compliant"] is True
        assert compliance["details"] == "No tanks registered"

    def test_empty_tank_list_status(self):
        """无舱时 status.tanks 应为空列表。"""
        ch = self._make_channel()
        status = ch.get_status()
        assert status["tanks"] == []
        assert status["total_capacity"] == 0.0

    # ---- 多 tank 部分处理部分未处理 ----

    def test_multi_tank_partial_treatment_not_compliant(self):
        """3 个舱中 1 个未处理 → 不合规。"""
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "tank_status", "tank_id": "T1",
            "level_percent": 80, "treated": True,
        }))
        _run(ch.process_event({
            "type": "tank_status", "tank_id": "T2",
            "level_percent": 60, "treated": False,
        }))
        _run(ch.process_event({
            "type": "tank_status", "tank_id": "T3",
            "level_percent": 90, "treated": True,
        }))
        compliance = ch.check_bwm_compliance()
        assert compliance["compliant"] is False
        assert compliance["untreated_tanks"] == ["T2"]
        assert compliance["total_tanks"] == 3
        assert compliance["treated_tanks"] == 2

    def test_multi_tank_all_treated_compliant(self):
        """所有舱已处理 → 合规。"""
        ch = self._make_channel()
        for tid in ("T1", "T2", "T3"):
            _run(ch.process_event({
                "type": "tank_status", "tank_id": tid,
                "level_percent": 70, "treated": True,
            }))
        compliance = ch.check_bwm_compliance()
        assert compliance["compliant"] is True
        assert compliance["untreated_tanks"] == []

    def test_multi_tank_treatment_event_fixes_compliance(self):
        """处理事件完成后, 原先不合规变为合规。"""
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "tank_status", "tank_id": "T1",
            "level_percent": 50, "treated": False,
        }))
        assert ch.check_bwm_compliance()["compliant"] is False
        _run(ch.process_event({
            "type": "treatment_event", "tank_id": "T1",
            "method": "UV", "status": "completed",
        }))
        assert ch.check_bwm_compliance()["compliant"] is True


# ============================================================================
# 任务 2-2: EmissionMonitor 边界测试
# ============================================================================

class TestEmissionMonitorBoundary:
    """排放监测边界条件测试。"""

    def _make_channel(self):
        ch = EmissionMonitorChannel()
        ch.initialize()
        return ch

    # ---- ECA 合规: SOx 0.10% 边界值 ----

    def test_eca_sox_exactly_at_limit_mgo(self):
        """MGO 硫含量 0.10% 恰好等于 ECA 限值 → 合规。"""
        ch = self._make_channel()
        ch._in_eca = True
        ch._fuel_type = "MGO"
        compliance = ch.check_eca_compliance()
        assert FUEL_SULFUR_CONTENT["MGO"] == 0.10
        assert compliance["sulfur_content_percent"] == 0.10
        assert compliance["limit_percent"] == 0.10
        assert compliance["compliant"] is True

    def test_eca_sox_hfo_exceeds_limit(self):
        """HFO 硫含量 3.50% 远超 ECA 0.10% → 不合规。"""
        ch = self._make_channel()
        ch._in_eca = True
        ch._fuel_type = "HFO"
        compliance = ch.check_eca_compliance()
        assert compliance["compliant"] is False
        assert compliance["sulfur_content_percent"] == 3.50

    def test_eca_sox_lng_zero_sulfur(self):
        """LNG 硫含量 0.00% → ECA 合规。"""
        ch = self._make_channel()
        ch._in_eca = True
        ch._fuel_type = "LNG"
        compliance = ch.check_eca_compliance()
        assert compliance["compliant"] is True
        assert compliance["sulfur_content_percent"] == 0.00

    # ---- 燃料切换后合规状态变化 ----

    def test_fuel_switch_hfo_to_mgo_restores_eca_compliance(self):
        """进入 ECA 后从 HFO 切换到 MGO → 合规状态从 False 变 True。"""
        ch = self._make_channel()
        # 进入 ECA
        _run(ch.process_event({
            "type": "eca_entry", "region": "Baltic Sea",
        }))
        ch._fuel_type = "HFO"
        assert ch.check_eca_compliance()["compliant"] is False

        # 切换到 MGO
        _run(ch.process_event({
            "type": "fuel_switch", "from_fuel": "HFO", "to_fuel": "MGO",
        }))
        assert ch._fuel_type == "MGO"
        assert ch.check_eca_compliance()["compliant"] is True

    def test_fuel_switch_log_recorded(self):
        """每次切换都被记入日志。"""
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "fuel_switch", "from_fuel": "VLSFO", "to_fuel": "MGO",
        }))
        _run(ch.process_event({
            "type": "fuel_switch", "from_fuel": "MGO", "to_fuel": "LNG",
        }))
        assert len(ch._fuel_switch_log) == 2
        assert ch._fuel_switch_log[0]["to_fuel"] == "MGO"
        assert ch._fuel_switch_log[1]["to_fuel"] == "LNG"

    # ---- 全球限制 0.50% 测试 ----

    def test_global_sox_vlsfo_at_limit(self):
        """VLSFO 硫含量 0.50% 恰好等于全球限值 → 合规。"""
        ch = self._make_channel()
        ch._in_eca = False
        ch._fuel_type = "VLSFO"
        compliance = ch.check_eca_compliance()
        assert FUEL_SULFUR_CONTENT["VLSFO"] == 0.50
        assert compliance["limit_percent"] == 0.50
        assert compliance["compliant"] is True

    def test_global_sox_hfo_exceeds(self):
        """HFO 硫含量 3.50% 超全球限值 0.50% → 不合规。"""
        ch = self._make_channel()
        ch._in_eca = False
        ch._fuel_type = "HFO"
        compliance = ch.check_eca_compliance()
        assert compliance["compliant"] is False

    def test_global_sox_lsfo_at_limit(self):
        """LSFO 硫含量 0.50% 恰好等于全球限值 → 合规。"""
        ch = self._make_channel()
        ch._in_eca = False
        ch._fuel_type = "LSFO"
        compliance = ch.check_eca_compliance()
        assert FUEL_SULFUR_CONTENT["LSFO"] == 0.50
        assert compliance["compliant"] is True


# ============================================================================
# 任务 2-3: AnchorWatch 边界测试
# ============================================================================

class TestAnchorWatchBoundary:
    """锚泊监控边界条件测试。"""

    def _make_channel(self):
        ch = AnchorWatchChannel()
        ch.initialize()
        return ch

    # ---- 走锚检测: 距离刚好等于 swing_radius ----

    def test_drift_exactly_at_swing_radius_no_dragging(self):
        """drift == swing_radius → 不走锚 (严格大于才走锚)。"""
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "anchor_drop",
            "position_lat": 0.0, "position_lon": 0.0,
            "depth": 20.0, "chain_length": 100.0,
        }))
        # 手动设置 drift_distance 精确等于 swing_radius
        ch._drift_distance = ch._swing_radius
        result = ch.check_dragging()
        assert result["dragging"] is False
        assert ch._alarm_status == "normal"

    def test_drift_just_above_swing_radius_is_dragging(self):
        """drift > swing_radius (微超) → 走锚。"""
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "anchor_drop",
            "position_lat": 0.0, "position_lon": 0.0,
            "depth": 20.0, "chain_length": 100.0,
        }))
        ch._drift_distance = ch._swing_radius + 0.01
        result = ch.check_dragging()
        assert result["dragging"] is True
        assert ch._alarm_status == "dragging"

    def test_drift_just_below_swing_radius_no_dragging(self):
        """drift < swing_radius (微差) → 不走锚。"""
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "anchor_drop",
            "position_lat": 0.0, "position_lon": 0.0,
            "depth": 20.0, "chain_length": 100.0,
        }))
        ch._drift_distance = ch._swing_radius - 0.01
        result = ch.check_dragging()
        assert result["dragging"] is False

    # ---- 起锚后 anchored 状态重置 ----

    def test_anchor_weigh_resets_all_state(self):
        """起锚后所有锚泊相关状态必须清零。"""
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "anchor_drop",
            "position_lat": 31.0, "position_lon": 122.0,
            "depth": 25.0, "chain_length": 120.0,
        }))
        assert ch._anchored is True
        assert ch._swing_radius > 0

        _run(ch.process_event({"type": "anchor_weigh"}))
        assert ch._anchored is False
        assert ch._anchor_position is None
        assert ch._drift_distance == 0.0
        assert ch._alarm_status == "normal"
        assert ch._swing_radius == 0.0
        assert ch._depth == 0.0
        assert ch._chain_length == 0.0
        assert ch._anchor_time is None

    def test_anchor_weigh_then_check_dragging_safe(self):
        """起锚后调用 check_dragging 不崩溃且返回 not dragging。"""
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "anchor_drop",
            "position_lat": 31.0, "position_lon": 122.0,
            "depth": 20.0, "chain_length": 100.0,
        }))
        _run(ch.process_event({"type": "anchor_weigh"}))
        result = ch.check_dragging()
        assert result["dragging"] is False
        assert result["details"] == "Not anchored"

    # ---- 无锚时 position_update 不崩溃 ----

    def test_position_update_before_anchor_drop(self):
        """未抛锚时收到 position_update 不应崩溃。"""
        ch = self._make_channel()
        result = _run(ch.process_event({
            "type": "position_update", "lat": 31.0, "lon": 122.0,
        }))
        assert result["status"] == "processed"
        assert result["dragging"] is False
        assert result["drift_distance"] == 0.0

    def test_position_update_after_weigh(self):
        """起锚后收到 position_update 不应崩溃。"""
        ch = self._make_channel()
        _run(ch.process_event({
            "type": "anchor_drop",
            "position_lat": 0.0, "position_lon": 0.0,
            "depth": 10.0, "chain_length": 50.0,
        }))
        _run(ch.process_event({"type": "anchor_weigh"}))
        result = _run(ch.process_event({
            "type": "position_update", "lat": 1.0, "lon": 1.0,
        }))
        assert result["status"] == "processed"
        assert result["dragging"] is False

    def test_swing_radius_depth_equals_chain(self):
        """depth == chain_length → radius = chain_length (clamp)。"""
        radius = AnchorWatchChannel._calculate_swing_radius(50.0, 50.0)
        assert radius == 50.0

    def test_swing_radius_zero_depth(self):
        """depth=0 → radius = chain_length。"""
        radius = AnchorWatchChannel._calculate_swing_radius(0.0, 100.0)
        assert radius == pytest.approx(100.0)
