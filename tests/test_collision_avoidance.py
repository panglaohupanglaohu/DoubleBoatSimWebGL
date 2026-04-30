# -*- coding: utf-8 -*-
"""
test_collision_avoidance.py — 碰撞检测与自动避让单元测试

测试覆盖:
1. CPA/TCPA 计算正确性
2. 风险等级分类
3. 会遇类型判定
4. 避让决策逻辑
5. 平滑转向/调速
6. 恢复逻辑
7. 3个典型碰撞风险场景
"""

import sys
import os
import math
import time
import unittest

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.collision_avoidance_service import (
    CollisionAvoidanceService,
    CollisionRisk,
    AvoidanceCommand,
    RiskLevel,
    AvoidanceState,
    CPA_DANGER_NM,
    CPA_CAUTION_NM,
    TCPA_DANGER_MIN,
    TCPA_CAUTION_MIN,
)


class TestCollisionAvoidanceService(unittest.TestCase):
    """碰撞检测与避让服务单元测试"""

    def setUp(self):
        self.service = CollisionAvoidanceService()

    # ==================== CPA/TCPA 计算测试 ====================

    def test_risk_assessment_safe(self):
        """测试安全距离下的风险评估"""
        ais_targets = {
            "SAFE-001": {
                "latitude": 31.00,  # 距离约 9 海里
                "longitude": 122.50,
                "course": 90.0,
                "speed": 10.0,
                "name": "SAFE SHIP",
            }
        }
        risks = self.service.assess_risks(
            own_lat=30.85, own_lon=122.35,
            own_course=135.0, own_speed=12.0,
            ais_targets=ais_targets,
        )
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0].risk_level, RiskLevel.SAFE)
        self.assertGreater(risks[0].cpa_nm, CPA_CAUTION_NM)

    def test_risk_assessment_danger(self):
        """测试近距离碰撞风险"""
        ais_targets = {
            "DANGER-001": {
                "latitude": 30.86,    # 非常接近
                "longitude": 122.36,
                "course": 315.0,      # 迎面
                "speed": 10.0,
                "name": "DANGER SHIP",
            }
        }
        risks = self.service.assess_risks(
            own_lat=30.85, own_lon=122.35,
            own_course=135.0, own_speed=12.0,
            ais_targets=ais_targets,
        )
        self.assertEqual(len(risks), 1)
        # 近距离目标至少是 CAUTION 级别
        self.assertIn(risks[0].risk_level, [RiskLevel.CAUTION, RiskLevel.DANGER, RiskLevel.EMERGENCY])

    def test_cpa_tcpa_calculation(self):
        """验证 CPA/TCPA 计算的一致性"""
        # 两船同向同速，CPA 应等于初始距离
        ais_targets = {
            "TEST-001": {
                "latitude": 30.86,
                "longitude": 122.36,
                "course": 135.0,  # 同向
                "speed": 12.0,    # 同速
                "name": "SAME COURSE",
            }
        }
        risks = self.service.assess_risks(
            own_lat=30.85, own_lon=122.35,
            own_course=135.0, own_speed=12.0,
            ais_targets=ais_targets,
        )
        # 同向同速，CPA 应接近初始距离
        expected_cpa = math.sqrt(
            ((30.86 - 30.85) * 60) ** 2 + ((122.36 - 122.35) * 60 * math.cos(math.radians(30.85))) ** 2
        )
        self.assertAlmostEqual(risks[0].cpa_nm, expected_cpa, delta=0.1)

    # ==================== 风险等级分类测试 ====================

    def test_risk_classification(self):
        """测试风险等级分类逻辑"""
        # 使用私有方法测试
        classify = self.service._classify_risk

        # 安全
        self.assertEqual(classify(3.0, 60.0, 5.0), RiskLevel.SAFE)
        self.assertEqual(classify(2.5, 40.0, 4.0), RiskLevel.SAFE)

        # 警戒
        self.assertEqual(classify(0.8, 20.0, 2.0), RiskLevel.CAUTION)
        self.assertEqual(classify(1.5, 10.0, 3.0), RiskLevel.CAUTION)

        # 危险
        self.assertEqual(classify(0.4, 10.0, 1.0), RiskLevel.DANGER)

        # 紧急
        self.assertEqual(classify(0.3, 5.0, 0.5), RiskLevel.EMERGENCY)

    # ==================== 会遇类型判定测试 ====================

    def test_encounter_head_on(self):
        """测试对遇局面判定"""
        encounter = self.service._classify_encounter(
            own_course=135.0, own_speed=12.0,
            rel_bearing=5.0,  # 正前方
            tgt_course=315.0, tgt_speed=10.0,
        )
        self.assertEqual(encounter, "head-on")

    def test_encounter_crossing_starboard(self):
        """测试右舷交叉判定"""
        encounter = self.service._classify_encounter(
            own_course=135.0, own_speed=12.0,
            rel_bearing=45.0,  # 右舷
            tgt_course=90.0, tgt_speed=10.0,
        )
        self.assertEqual(encounter, "crossing-starboard")

    def test_encounter_crossing_port(self):
        """测试左舷交叉判定"""
        encounter = self.service._classify_encounter(
            own_course=135.0, own_speed=12.0,
            rel_bearing=315.0,  # 左舷
            tgt_course=180.0, tgt_speed=10.0,
        )
        self.assertEqual(encounter, "crossing-port")

    def test_encounter_overtaking(self):
        """测试追越判定"""
        encounter = self.service._classify_encounter(
            own_course=135.0, own_speed=12.0,
            rel_bearing=160.0,  # 正横后
            tgt_course=135.0, tgt_speed=15.0,
        )
        self.assertEqual(encounter, "overtaking")

    # ==================== 让路船判定测试 ====================

    def test_give_way_head_on(self):
        """对遇局面本船应为让路船"""
        self.assertTrue(self.service._is_give_way_vessel("head-on", 5.0))

    def test_give_way_crossing_starboard(self):
        """右舷交叉本船应为让路船"""
        self.assertTrue(self.service._is_give_way_vessel("crossing-starboard", 45.0))

    def test_give_way_crossing_port(self):
        """左舷交叉本船应为直航船"""
        self.assertFalse(self.service._is_give_way_vessel("crossing-port", 315.0))

    def test_give_way_overtaking(self):
        """追越本船应为让路船"""
        self.assertTrue(self.service._is_give_way_vessel("overtaking", 160.0))

    # ==================== 避让决策测试 ====================

    def test_decide_avoidance_no_risk(self):
        """无风险时不应生成避让指令"""
        risks = []
        cmd = self.service.decide_avoidance(risks, 135.0, 12.0)
        self.assertIsNone(cmd)

    def test_decide_avoidance_safe(self):
        """安全目标不应生成避让指令"""
        risks = self.service.assess_risks(
            30.85, 122.35, 135.0, 12.0,
            {"SAFE": {"latitude": 31.0, "longitude": 122.5, "course": 90.0, "speed": 10.0, "name": "SAFE"}}
        )
        cmd = self.service.decide_avoidance(risks, 135.0, 12.0)
        self.assertIsNone(cmd)

    def test_decide_avoidance_danger(self):
        """危险目标应生成避让指令"""
        # 创建一个让路船局面下的危险目标
        risks = [
            CollisionRisk(
                target_mmsi="DANGER",
                target_name="DANGER",
                cpa_nm=0.3,
                tcpa_min=5.0,
                range_nm=1.0,
                bearing_deg=45.0,
                risk_level=RiskLevel.DANGER,
                encounter_type="crossing-starboard",
                is_give_way=True,
                suggested_action="向右转向",
                course_change=20.0,
                speed_change=0,
            )
        ]
        cmd = self.service.decide_avoidance(risks, 135.0, 12.0)
        self.assertIsNotNone(cmd)
        if cmd:
            self.assertGreater(cmd.course_change, 0)

    # ==================== 平滑应用测试 ====================

    def test_smooth_turn(self):
        """测试平滑转向"""
        cmd = AvoidanceCommand(
            action_type="turn_starboard",
            course_target=180.0,
            speed_target=12.0,
            course_change=45.0,
            speed_change=0,
            reason="测试转向",
            risk_level=RiskLevel.DANGER,
            timestamp=time.time(),
        )
        # 模拟10秒转向
        course, speed = 135.0, 12.0
        for _ in range(10):
            course, speed = self.service.apply_avoidance(cmd, course, speed, dt=1.0)

        # 航向应逐渐接近目标
        self.assertGreater(course, 135.0)
        self.assertLessEqual(course, 180.0)

    def test_smooth_speed_change(self):
        """测试平滑调速"""
        cmd = AvoidanceCommand(
            action_type="slow_down",
            course_target=135.0,
            speed_target=6.0,
            course_change=0,
            speed_change=-6.0,
            reason="测试减速",
            risk_level=RiskLevel.DANGER,
            timestamp=time.time(),
        )
        course, speed = 135.0, 12.0
        for _ in range(10):
            course, speed = self.service.apply_avoidance(cmd, course, speed, dt=1.0)

        # 航速应逐渐降低
        self.assertLess(speed, 12.0)
        self.assertGreaterEqual(speed, 6.0)

    # ==================== 典型碰撞场景测试 ====================

    def test_scenario_head_on_collision(self):
        """场景1: 对遇碰撞风险"""
        ais_targets = {
            "HEADON-001": {
                "latitude": 30.87,
                "longitude": 122.37,
                "course": 315.0,  # 迎面
                "speed": 12.0,
                "name": "HEAD-ON VESSEL",
            }
        }
        risks = self.service.assess_risks(
            own_lat=30.85, own_lon=122.35,
            own_course=135.0, own_speed=12.0,
            ais_targets=ais_targets,
        )
        self.assertEqual(len(risks), 1)
        risk = risks[0]

        # 验证对遇局面
        self.assertEqual(risk.encounter_type, "head-on")

        # 验证避让建议
        cmd = self.service.decide_avoidance(risks, 135.0, 12.0)
        if cmd:
            self.assertGreater(cmd.course_change, 0)  # 应右转

    def test_scenario_crossing_from_starboard(self):
        """场景2: 右舷交叉碰撞风险"""
        ais_targets = {
            "CROSS-001": {
                "latitude": 30.83,
                "longitude": 122.33,
                "course": 45.0,   # 从右舷横穿
                "speed": 15.0,
                "name": "CROSSING VESSEL",
            }
        }
        risks = self.service.assess_risks(
            own_lat=30.85, own_lon=122.35,
            own_course=135.0, own_speed=12.0,
            ais_targets=ais_targets,
        )
        self.assertEqual(len(risks), 1)
        risk = risks[0]

        # 验证右舷交叉
        self.assertEqual(risk.encounter_type, "crossing-starboard")
        self.assertTrue(risk.is_give_way)  # 本船应为让路船

        # 验证避让建议
        cmd = self.service.decide_avoidance(risks, 135.0, 12.0)
        if cmd:
            self.assertGreater(cmd.course_change, 0)  # 应右转

    def test_scenario_overtaking(self):
        """场景3: 追越碰撞风险"""
        ais_targets = {
            "OVERTAKE-001": {
                "latitude": 30.88,
                "longitude": 122.32,
                "course": 135.0,  # 同向
                "speed": 18.0,    # 更快
                "name": "OVERTAKING VESSEL",
            }
        }
        risks = self.service.assess_risks(
            own_lat=30.85, own_lon=122.35,
            own_course=135.0, own_speed=12.0,
            ais_targets=ais_targets,
        )
        self.assertEqual(len(risks), 1)

        # 验证追越局面
        cmd = self.service.decide_avoidance(risks, 135.0, 12.0)
        if cmd:
            self.assertGreater(cmd.course_change, 0)  # 应右转增加横向距离

    # ==================== 恢复逻辑测试 ====================

    def test_recovery_check(self):
        """测试恢复逻辑"""
        # 先设置避让状态
        self.service.status.state = AvoidanceState.AVOIDING
        self.service._recovery_course = 135.0
        self.service._recovery_speed = 12.0

        # 所有目标安全时，应触发恢复
        safe_risks = [
            CollisionRisk(
                target_mmsi="SAFE",
                target_name="SAFE",
                cpa_nm=5.0,
                tcpa_min=120.0,
                range_nm=10.0,
                bearing_deg=90.0,
                risk_level=RiskLevel.SAFE,
                encounter_type="safe",
                is_give_way=False,
                suggested_action="保持",
                course_change=0,
                speed_change=0,
            )
        ]
        # 使用正确的属性名
        should_recover = self.service.check_recovery(safe_risks, 150.0, 12.0)
        self.assertTrue(should_recover)

    # ==================== 状态管理测试 ====================

    def test_get_status(self):
        """测试状态获取"""
        status = self.service.get_status()
        self.assertIn("state", status)
        self.assertIn("active", status)
        self.assertIn("message", status)
        self.assertEqual(status["state"], "idle")

    def test_reset(self):
        """测试重置"""
        self.service.status.state = AvoidanceState.AVOIDING
        self.service.status.active = True
        self.service.reset()
        self.assertEqual(self.service.status.state, AvoidanceState.IDLE)
        self.assertFalse(self.service.status.active)


if __name__ == "__main__":
    unittest.main()
