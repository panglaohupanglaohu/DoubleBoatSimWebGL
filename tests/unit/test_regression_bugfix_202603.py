# -*- coding: utf-8 -*-
"""
回归测试: 2026-03 Bug 修复验证

覆盖:
1. COLREGs Brain Rule 13 追越/被追越分类修复
2. WPC Attitude Control 速度依赖物理模型修复
3. Marine Message Bus asyncio.iscoroutinefunction DeprecationWarning 修复
"""

import inspect
import math
import warnings

import pytest

from channels.colregs_brain import (
    COLREGsMathEngine,
    EncounterType,
    VesselState,
)
from channels.wpc_attitude_control import (
    InterceptorState,
    TFoilState,
)
from channels.marine_message_bus import MarineMessageBus


# ============================================================
# 2.1 COLREGs Brain — Rule 13 追越/被追越回归测试
# ============================================================

class TestRule13OvertakingRegression:
    """Rule 13: 追越 & 被追越分类回归测试

    COLREGs Rule 13 定义:
      从正横后 22.5° 以上追上前船的船为追越船。
      当 OWN 在 TARGET 正后方时 → OWN 是追越船 (OVERTAKING)
      当 TARGET 在 OWN 正后方时 → OWN 是被追越船 (BEING_OVERTAKEN)
    """

    # ---- OWN 追越 TARGET ----

    def test_own_overtaking_target_from_directly_astern(self):
        """OWN 从 TARGET 正后方以更高速度追上 → OVERTAKING"""
        own = VesselState(lat=31.20, lon=121.47, course=0.0, speed=15.0, heading=0.0)
        target = VesselState(lat=31.25, lon=121.47, course=0.0, speed=8.0, heading=0.0)
        enc = COLREGsMathEngine.classify_encounter(own, target)
        assert enc == EncounterType.OVERTAKING

    def test_own_overtaking_target_slight_angle(self):
        """OWN 从 TARGET 后方稍偏 → 仍属追越"""
        own = VesselState(lat=31.20, lon=121.472, course=5.0, speed=14.0, heading=5.0)
        target = VesselState(lat=31.25, lon=121.47, course=0.0, speed=8.0, heading=0.0)
        enc = COLREGsMathEngine.classify_encounter(own, target)
        assert enc == EncounterType.OVERTAKING

    def test_own_overtaking_same_course_different_speed(self):
        """两船同向，OWN 速度更高且在后方 → OVERTAKING"""
        own = VesselState(lat=31.20, lon=121.47, course=90.0, speed=18.0, heading=90.0)
        target = VesselState(lat=31.20, lon=121.50, course=90.0, speed=10.0, heading=90.0)
        enc = COLREGsMathEngine.classify_encounter(own, target)
        assert enc == EncounterType.OVERTAKING

    # ---- TARGET 追越 OWN (OWN 被追越) ----

    def test_being_overtaken_target_from_astern(self):
        """TARGET 从 OWN 正后方追上 → BEING_OVERTAKEN"""
        own = VesselState(lat=31.25, lon=121.47, course=0.0, speed=8.0, heading=0.0)
        target = VesselState(lat=31.20, lon=121.47, course=0.0, speed=15.0, heading=0.0)
        enc = COLREGsMathEngine.classify_encounter(own, target)
        assert enc == EncounterType.BEING_OVERTAKEN

    def test_being_overtaken_same_course(self):
        """两船同向，TARGET 速度更高且在后方 → BEING_OVERTAKEN"""
        own = VesselState(lat=31.20, lon=121.50, course=90.0, speed=10.0, heading=90.0)
        target = VesselState(lat=31.20, lon=121.47, course=90.0, speed=18.0, heading=90.0)
        enc = COLREGsMathEngine.classify_encounter(own, target)
        assert enc == EncounterType.BEING_OVERTAKEN

    def test_being_overtaken_slight_angle(self):
        """TARGET 从 OWN 后方稍偏追上 → BEING_OVERTAKEN"""
        own = VesselState(lat=31.25, lon=121.47, course=0.0, speed=8.0, heading=0.0)
        target = VesselState(lat=31.20, lon=121.472, course=5.0, speed=14.0, heading=5.0)
        enc = COLREGsMathEngine.classify_encounter(own, target)
        assert enc == EncounterType.BEING_OVERTAKEN

    # ---- HEAD_ON 不受影响 ----

    def test_head_on_not_affected(self):
        """对遇: 两船正对行驶 → HEAD_ON"""
        own = VesselState(lat=31.20, lon=121.47, course=0.0, speed=12.0, heading=0.0)
        target = VesselState(lat=31.25, lon=121.47, course=180.0, speed=12.0, heading=180.0)
        enc = COLREGsMathEngine.classify_encounter(own, target)
        assert enc == EncounterType.HEAD_ON

    def test_head_on_slight_offset(self):
        """对遇: 两船近似正对 (±5°偏差) → HEAD_ON"""
        own = VesselState(lat=31.20, lon=121.47, course=2.0, speed=12.0, heading=2.0)
        target = VesselState(lat=31.25, lon=121.4702, course=183.0, speed=10.0, heading=183.0)
        enc = COLREGsMathEngine.classify_encounter(own, target)
        assert enc == EncounterType.HEAD_ON

    # ---- CROSSING 不受影响 ----

    def test_crossing_from_starboard_not_affected(self):
        """交叉相遇: TARGET 从右舷方向来 → CROSSING_FROM_STARBOARD"""
        own = VesselState(lat=31.23, lon=121.47, course=0.0, speed=12.0, heading=0.0)
        target = VesselState(lat=31.23, lon=121.50, course=270.0, speed=10.0, heading=270.0)
        enc = COLREGsMathEngine.classify_encounter(own, target)
        assert enc == EncounterType.CROSSING_FROM_STARBOARD

    def test_crossing_from_port_not_affected(self):
        """交叉相遇: TARGET 从左舷方向来 → CROSSING_FROM_PORT"""
        own = VesselState(lat=31.23, lon=121.47, course=0.0, speed=12.0, heading=0.0)
        target = VesselState(lat=31.23, lon=121.44, course=90.0, speed=10.0, heading=90.0)
        enc = COLREGsMathEngine.classify_encounter(own, target)
        assert enc == EncounterType.CROSSING_FROM_PORT

    # ---- 对称性验证 ----

    def test_overtaking_symmetry(self):
        """交换 OWN/TARGET 位置，追越/被追越应互换"""
        ship_a = VesselState(lat=31.20, lon=121.47, course=0.0, speed=15.0, heading=0.0)
        ship_b = VesselState(lat=31.25, lon=121.47, course=0.0, speed=8.0, heading=0.0)

        enc_ab = COLREGsMathEngine.classify_encounter(ship_a, ship_b)
        enc_ba = COLREGsMathEngine.classify_encounter(ship_b, ship_a)

        assert enc_ab == EncounterType.OVERTAKING
        assert enc_ba == EncounterType.BEING_OVERTAKEN

    def test_head_on_symmetric(self):
        """对遇场景对称: 交换两船，仍为对遇"""
        ship_a = VesselState(lat=31.20, lon=121.47, course=0.0, speed=12.0, heading=0.0)
        ship_b = VesselState(lat=31.25, lon=121.47, course=180.0, speed=12.0, heading=180.0)

        enc_ab = COLREGsMathEngine.classify_encounter(ship_a, ship_b)
        enc_ba = COLREGsMathEngine.classify_encounter(ship_b, ship_a)

        assert enc_ab == EncounterType.HEAD_ON
        assert enc_ba == EncounterType.HEAD_ON


# ============================================================
# 2.2 WPC Attitude Control — 速度依赖物理模型测试
# ============================================================

class TestTFoilSpeedDependentRegression:
    """T-foil 升力随速度变化的物理模型回归测试

    升力公式: L = 0.5 * rho * v² * S * Cl
    速度翻倍 → 升力增至 4 倍 (v² 关系)
    """

    def test_lift_increases_with_speed_squared(self):
        """15 节 vs 30 节 → 升力比约 4 倍"""
        foil_slow = TFoilState(foil_id="test_slow")
        foil_fast = TFoilState(foil_id="test_fast")

        foil_slow.set_angle(10.0, speed_knots=15.0)
        foil_fast.set_angle(10.0, speed_knots=30.0)

        ratio = foil_fast.lift_force_kn / foil_slow.lift_force_kn
        assert ratio == pytest.approx(4.0, rel=0.01)

    def test_lift_at_different_speeds(self):
        """多个速度点验证 v² 依赖"""
        foil = TFoilState(foil_id="test")
        lifts = {}
        for speed in [10, 20, 30, 40]:
            foil.set_angle(10.0, speed_knots=float(speed))
            lifts[speed] = foil.lift_force_kn

        # 20 kts vs 10 kts → 4x
        assert lifts[20] / lifts[10] == pytest.approx(4.0, rel=0.01)
        # 30 kts vs 10 kts → 9x
        assert lifts[30] / lifts[10] == pytest.approx(9.0, rel=0.01)
        # 40 kts vs 10 kts → 16x
        assert lifts[40] / lifts[10] == pytest.approx(16.0, rel=0.01)

    def test_zero_angle_gives_zero_lift(self):
        """角度为 0 → Cl=0 → 升力为 0"""
        foil = TFoilState(foil_id="test")
        foil.set_angle(0.0, speed_knots=25.0)
        assert foil.lift_force_kn == 0.0

    def test_default_speed_backward_compatible(self):
        """不传 speed_knots 不应报错 (默认 25 节)"""
        foil = TFoilState(foil_id="test")
        actual = foil.set_angle(10.0)  # 无 speed_knots 参数
        assert actual == 10.0
        assert foil.lift_force_kn > 0

    def test_negative_angle_negative_lift(self):
        """负攻角产生负升力 (向下)"""
        foil = TFoilState(foil_id="test")
        foil.set_angle(-10.0, speed_knots=25.0)
        assert foil.lift_force_kn < 0

    def test_drag_always_positive(self):
        """阻力无论攻角正负都为正"""
        foil = TFoilState(foil_id="test")
        foil.set_angle(-10.0, speed_knots=25.0)
        assert foil.drag_force_kn > 0

        foil.set_angle(10.0, speed_knots=25.0)
        assert foil.drag_force_kn > 0


class TestInterceptorSpeedDependentRegression:
    """拦截板力随速度变化的回归测试"""

    def test_force_increases_with_speed_squared(self):
        """15 节 vs 30 节 → 力的比约 4 倍"""
        ic_slow = InterceptorState(interceptor_id="test_slow", side="port")
        ic_fast = InterceptorState(interceptor_id="test_fast", side="port")

        ic_slow.set_extension(150.0, speed_knots=15.0)
        ic_fast.set_extension(150.0, speed_knots=30.0)

        ratio = ic_fast.force_kn / ic_slow.force_kn
        assert ratio == pytest.approx(4.0, rel=0.01)

    def test_default_speed_backward_compatible(self):
        """不传 speed_knots 不应报错 (默认 25 节)"""
        ic = InterceptorState(interceptor_id="test", side="port")
        actual = ic.set_extension(150.0)  # 无 speed_knots 参数
        assert actual == 150.0
        assert ic.force_kn > 0

    def test_zero_extension_zero_force(self):
        """伸出量为 0 → 力为 0"""
        ic = InterceptorState(interceptor_id="test", side="port")
        ic.set_extension(0.0, speed_knots=25.0)
        assert ic.force_kn == 0.0

    def test_force_at_multiple_speeds(self):
        """多个速度点验证 v² 依赖 (拦截板)"""
        ic = InterceptorState(interceptor_id="test", side="starboard")
        forces = {}
        for speed in [10, 20, 30]:
            ic.set_extension(200.0, speed_knots=float(speed))
            forces[speed] = ic.force_kn

        assert forces[20] / forces[10] == pytest.approx(4.0, rel=0.01)
        assert forces[30] / forces[10] == pytest.approx(9.0, rel=0.01)


# ============================================================
# 2.3 Marine Message Bus — asyncio DeprecationWarning 兼容性
# ============================================================

class TestMessageBusAsyncioCompat:
    """确认 marine_message_bus 不使用已弃用的 asyncio.iscoroutinefunction"""

    def test_uses_inspect_not_asyncio(self):
        """源码应使用 inspect.iscoroutinefunction 而非 asyncio.iscoroutinefunction"""
        import channels.marine_message_bus as mbmod
        source = inspect.getsource(mbmod)
        assert "inspect.iscoroutinefunction" in source
        assert "asyncio.iscoroutinefunction" not in source

    def test_no_deprecation_warning_on_import(self):
        """导入 marine_message_bus 不应触发 DeprecationWarning"""
        import importlib
        import channels.marine_message_bus as mbmod
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            importlib.reload(mbmod)
            deprecation_warnings = [
                x for x in w
                if issubclass(x.category, DeprecationWarning)
                and "iscoroutinefunction" in str(x.message)
            ]
            assert len(deprecation_warnings) == 0, (
                f"DeprecationWarning for iscoroutinefunction found: {deprecation_warnings}"
            )

    def test_message_bus_instantiation(self):
        """MarineMessageBus 应可正常实例化无异常"""
        bus = MarineMessageBus()
        assert bus is not None
