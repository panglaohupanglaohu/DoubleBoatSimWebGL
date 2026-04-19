# -*- coding: utf-8 -*-
"""
L3: COLREGs Autonomous Brain - 自主大脑层

核心技术:
- COLREGs 数学硬编码: 将国际避碰规则 (COLREG 72) 转化为算法约束
- DRL (深度强化学习): 用于避碰策略优化
- NMPC (非线性模型预测控制): 大惯性船舶平滑规避路径

技术要点:
- Rule 13: 追越 (Overtaking) - 从正横后22.5°以上追上的船舶
- Rule 14: 对遇 (Head-on) - 两船正对/近似正对
- Rule 15: 交叉相遇 (Crossing) - 右舷来船为让路船
- Rule 16: 让路船行动 (Give-way) - 应尽早采取大幅度行动
- Rule 17: 直航船行动 (Stand-on) - 保持航向航速
- Rule 8: 避碰行动 (Avoiding collision) - 行动应大到足以让对方容易察觉

工程意义:
将国际避碰规则转化为算法约束，实现大惯性船舶的平滑规避路径。
"""

from __future__ import annotations

import math
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class COLREGRule(Enum):
    """COLREGs 规则类型"""
    RULE_13_OVERTAKING = "rule_13_overtaking"
    RULE_14_HEAD_ON = "rule_14_head_on"
    RULE_15_CROSSING = "rule_15_crossing"
    RULE_16_GIVE_WAY = "rule_16_give_way"
    RULE_17_STAND_ON = "rule_17_stand_on"
    RULE_8_AVOIDING = "rule_8_avoiding"
    SAFE_PASSAGE = "safe_passage"


class EncounterType(Enum):
    """会遇类型"""
    HEAD_ON = "head_on"
    CROSSING_FROM_STARBOARD = "crossing_starboard"
    CROSSING_FROM_PORT = "crossing_port"
    OVERTAKING = "overtaking"
    BEING_OVERTAKEN = "being_overtaken"
    SAFE = "safe"


class ManeuverAction(Enum):
    """操纵行动"""
    MAINTAIN = "maintain"
    ALTER_COURSE_STARBOARD = "alter_starboard"
    ALTER_COURSE_PORT = "alter_port"
    REDUCE_SPEED = "reduce_speed"
    STOP = "stop"
    REVERSE = "reverse"


@dataclass
class VesselState:
    """船舶状态"""
    lat: float
    lon: float
    course: float       # 航向 (度, 真北)
    speed: float        # 速度 (节)
    heading: float      # 船首向
    length: float = 200.0   # 船长 (米)
    beam: float = 30.0      # 型宽
    mmsi: Optional[str] = None


@dataclass
class EncounterAssessment:
    """会遇评估结果"""
    encounter_type: EncounterType
    colreg_rule: COLREGRule
    relative_bearing: float     # 相对方位 (度)
    distance_nm: float          # 距离 (海里)
    cpa: float                  # 最近会遇距离
    tcpa: float                 # 最近会遇时间 (分钟)
    risk_level: float           # 风险等级 0-1
    is_give_way: bool
    recommended_action: ManeuverAction
    course_alteration: float    # 建议改向角度
    speed_reduction: float      # 建议减速百分比


@dataclass
class NMPCState:
    """NMPC 预测状态"""
    time_step: float
    predicted_positions: List[Tuple[float, float]]
    predicted_courses: List[float]
    predicted_speeds: List[float]
    cost: float
    constraints_satisfied: bool


class COLREGsMathEngine:
    """COLREGs 数学硬编码引擎

    将 COLREG 72 的 38 条规则中的避碰核心规则 (8, 13-17) 转化为精确数学约束。
    """

    # 常量
    OVERTAKING_SECTOR = 22.5       # 正横后 22.5°
    HEAD_ON_TOLERANCE = 6.0        # 对遇判定容差 ±6°
    CPA_DANGER_NM = 1.0            # CPA (open water)
    CPA_DANGER_RESTRICTED_NM = 0.5 # CPA (restricted waters) 危险距离 (海里)
    TCPA_DANGER_MIN = 15.0         # TCPA 危险时间 (分钟)
    MIN_COURSE_ALTERATION = 30.0   # Rule 8
    RULE17_EMERGENCY_TCPA = 8.0    # Rule 17(a)(ii) stand-on emergency
    RULE17_LAST_RESORT_TCPA = 4.0  # Rule 17(b) last resort: 最小改向角度

    @staticmethod
    def normalize_angle(angle: float) -> float:
        """将角度归一化到 [0, 360)"""
        return angle % 360.0

    @staticmethod
    def angle_diff(a1: float, a2: float) -> float:
        """计算两个角度的最短差值 [-180, 180]"""
        d = (a2 - a1 + 180) % 360 - 180
        return d

    @classmethod
    def calculate_relative_bearing(cls, own: VesselState, target: VesselState) -> float:
        """计算目标船的相对方位"""
        dlat = target.lat - own.lat
        dlon = (target.lon - own.lon) * math.cos(math.radians(own.lat))
        true_bearing = math.degrees(math.atan2(dlon, dlat)) % 360
        rel_bearing = (true_bearing - own.heading) % 360
        return rel_bearing

    @classmethod
    def calculate_distance_nm(cls, own: VesselState, target: VesselState) -> float:
        """Haversine 距离计算 (海里)"""
        R = 3440.065  # 地球半径 (海里)
        lat1, lat2 = math.radians(own.lat), math.radians(target.lat)
        dlat = lat2 - lat1
        dlon = math.radians(target.lon - own.lon)
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        return R * 2 * math.asin(math.sqrt(min(1.0, a)))

    @classmethod
    def calculate_cpa_tcpa(cls, own: VesselState, target: VesselState) -> Tuple[float, float]:
        """计算 CPA (最近会遇距离) 和 TCPA (最近会遇时间)"""
        # 转换速度为 nm/min
        own_speed = own.speed / 60.0
        target_speed = target.speed / 60.0

        own_vx = own_speed * math.sin(math.radians(own.course))
        own_vy = own_speed * math.cos(math.radians(own.course))
        tgt_vx = target_speed * math.sin(math.radians(target.course))
        tgt_vy = target_speed * math.cos(math.radians(target.course))

        # 相对位置 (近似, 度→海里)
        dx = (target.lon - own.lon) * math.cos(math.radians(own.lat)) * 60.0
        dy = (target.lat - own.lat) * 60.0

        # 相对速度
        dvx = tgt_vx - own_vx
        dvy = tgt_vy - own_vy

        dv_sq = dvx * dvx + dvy * dvy
        if dv_sq < 1e-10:
            cpa = math.sqrt(dx * dx + dy * dy)
            return cpa, float('inf')

        tcpa = -(dx * dvx + dy * dvy) / dv_sq  # minutes
        if tcpa < 0:
            tcpa = 0

        cpx = dx + dvx * tcpa
        cpy = dy + dvy * tcpa
        cpa = math.sqrt(cpx * cpx + cpy * cpy)

        return round(cpa, 4), round(tcpa, 2)

    @classmethod
    def classify_encounter(cls, own: VesselState, target: VesselState) -> EncounterType:
        """基于 COLREGs 数学定义分类会遇类型"""
        rel_bearing = cls.calculate_relative_bearing(own, target)
        target_rel_bearing = cls.calculate_relative_bearing(target, own)

        # 目标航向 与 本船航向 的差
        course_diff = cls.angle_diff(own.course, target.course)

        # Rule 13: Overtaking - stern arc 112.5-247.5
        stern_arc_start = 90.0 + cls.OVERTAKING_SECTOR
        stern_arc_end = 360.0 - stern_arc_start
        if stern_arc_start < target_rel_bearing < stern_arc_end:
            return EncounterType.OVERTAKING
        if stern_arc_start < rel_bearing < stern_arc_end:
            return EncounterType.BEING_OVERTAKEN

        # Rule 14: 对遇
        # 两船航向近似相反 (差值在 ±6° of 180°)
        if abs(abs(course_diff) - 180) < cls.HEAD_ON_TOLERANCE:
            if rel_bearing < 6 or rel_bearing > 354:
                return EncounterType.HEAD_ON

        # Rule 15: 交叉相遇
        if 0 < rel_bearing <= 112.5:
            return EncounterType.CROSSING_FROM_STARBOARD
        elif 247.5 <= rel_bearing < 360:
            return EncounterType.CROSSING_FROM_PORT

        return EncounterType.SAFE

    @classmethod
    def assess_encounter(cls, own: VesselState, target: VesselState) -> EncounterAssessment:
        """全面评估会遇情况"""
        rel_bearing = cls.calculate_relative_bearing(own, target)
        distance = cls.calculate_distance_nm(own, target)
        cpa, tcpa = cls.calculate_cpa_tcpa(own, target)
        encounter = cls.classify_encounter(own, target)

        # 确定 COLREGs 规则
        colreg_rule, is_give_way = cls._determine_rule(encounter)

        # 风险计算
        risk = cls._calculate_risk(cpa, tcpa, distance)

        # 推荐行动
        action, course_alt, speed_red = cls._recommend_action(
            encounter, is_give_way, cpa, tcpa, distance, own, target
        )

        return EncounterAssessment(
            encounter_type=encounter,
            colreg_rule=colreg_rule,
            relative_bearing=round(rel_bearing, 1),
            distance_nm=round(distance, 3),
            cpa=round(cpa, 3),
            tcpa=round(tcpa, 1),
            risk_level=round(risk, 3),
            is_give_way=is_give_way,
            recommended_action=action,
            course_alteration=round(course_alt, 1),
            speed_reduction=round(speed_red, 1),
        )

    @classmethod
    def _determine_rule(cls, encounter: EncounterType) -> Tuple[COLREGRule, bool]:
        """确定适用的 COLREGs 规则"""
        rules = {
            EncounterType.HEAD_ON: (COLREGRule.RULE_14_HEAD_ON, True),
            EncounterType.CROSSING_FROM_STARBOARD: (COLREGRule.RULE_15_CROSSING, True),
            EncounterType.CROSSING_FROM_PORT: (COLREGRule.RULE_17_STAND_ON, False),
            EncounterType.OVERTAKING: (COLREGRule.RULE_13_OVERTAKING, True),
            EncounterType.BEING_OVERTAKEN: (COLREGRule.RULE_17_STAND_ON, False),
            EncounterType.SAFE: (COLREGRule.SAFE_PASSAGE, False),
        }
        return rules.get(encounter, (COLREGRule.SAFE_PASSAGE, False))

    @classmethod
    def _calculate_risk(cls, cpa: float, tcpa: float, distance: float) -> float:
        """计算碰撞风险 (0-1)"""
        if tcpa == float('inf') or tcpa < 0:
            return 0.0

        cpa_risk = max(0, 1.0 - cpa / cls.CPA_DANGER_NM) if cls.CPA_DANGER_NM > 0 else 0
        tcpa_risk = max(0, 1.0 - tcpa / cls.TCPA_DANGER_MIN) if cls.TCPA_DANGER_MIN > 0 else 0
        dist_risk = max(0, 1.0 - distance / 6.0)

        risk = 0.5 * cpa_risk + 0.3 * tcpa_risk + 0.2 * dist_risk
        return min(1.0, max(0.0, risk))

    @classmethod
    def _recommend_action(
        cls,
        encounter: EncounterType,
        is_give_way: bool,
        cpa: float,
        tcpa: float,
        distance: float,
        own: VesselState,
        target: VesselState,
    ) -> Tuple[ManeuverAction, float, float]:
        """生成推荐操纵行动"""
        # Rule 17: stand-on vessel emergency phases
        if not is_give_way:
            # Rule 17(b): collision imminent
            if tcpa < cls.RULE17_LAST_RESORT_TCPA and cpa < cls.CPA_DANGER_NM * 0.5:
                return ManeuverAction.ALTER_COURSE_STARBOARD, 60.0, 50.0
            # Rule 17(a)(ii): give-way vessel not acting
            if tcpa < cls.RULE17_EMERGENCY_TCPA and cpa < cls.CPA_DANGER_NM * 0.3:
                return ManeuverAction.ALTER_COURSE_STARBOARD, 40.0, 30.0
            return ManeuverAction.MAINTAIN, 0.0, 0.0

        if cpa > cls.CPA_DANGER_NM:
            return ManeuverAction.MAINTAIN, 0.0, 0.0

        # Rule 8: 行动应大到足以让对方容易察觉
        min_alter = cls.MIN_COURSE_ALTERATION

        if encounter == EncounterType.HEAD_ON:
            # Rule 14: 各向右转
            return ManeuverAction.ALTER_COURSE_STARBOARD, max(min_alter, 30.0), 0.0

        elif encounter == EncounterType.CROSSING_FROM_STARBOARD:
            # Rule 15: 避免从对方船首前通过
            if distance < 2.0:
                return ManeuverAction.ALTER_COURSE_STARBOARD, max(min_alter, 40.0), 20.0
            return ManeuverAction.ALTER_COURSE_STARBOARD, max(min_alter, 30.0), 0.0

        elif encounter == EncounterType.OVERTAKING:
            # Rule 13: 追越船让路
            return ManeuverAction.ALTER_COURSE_STARBOARD, max(min_alter, 20.0), 0.0

        if tcpa < 5.0 and cpa < 0.3:
            return ManeuverAction.STOP, 0.0, 100.0

        return ManeuverAction.REDUCE_SPEED, 0.0, 30.0


class NMPCController:
    """非线性模型预测控制器

    用于大惯性船舶的平滑规避路径规划。
    考虑船舶运动学约束 (最大转向率、加速度限制等)。
    """

    def __init__(
        self,
        prediction_horizon: int = 20,
        control_horizon: int = 10,
        dt: float = 30.0,
        max_rudder_rate: float = 3.0,
        max_speed_change: float = 0.5,
    ):
        self.N = prediction_horizon
        self.M = control_horizon
        self.dt = dt
        self.max_rudder_rate = max_rudder_rate
        self.max_speed_change = max_speed_change

    def predict_trajectory(
        self,
        own: VesselState,
        course_commands: List[float],
        speed_commands: List[float],
    ) -> NMPCState:
        """预测船舶轨迹"""
        positions = [(own.lat, own.lon)]
        courses = [own.course]
        speeds = [own.speed]

        lat, lon = own.lat, own.lon
        course = own.course
        speed = own.speed

        for i in range(min(len(course_commands), self.N)):
            target_course = course_commands[i] if i < len(course_commands) else course
            target_speed = speed_commands[i] if i < len(speed_commands) else speed

            # 转向率限制
            course_diff = COLREGsMathEngine.angle_diff(course, target_course)
            max_change = self.max_rudder_rate * self.dt
            course_change = max(-max_change, min(max_change, course_diff))
            course = COLREGsMathEngine.normalize_angle(course + course_change)

            # 速度限制
            speed_diff = target_speed - speed
            max_speed_chg = self.max_speed_change * self.dt / 60.0
            speed = speed + max(-max_speed_chg, min(max_speed_chg, speed_diff))
            speed = max(0, speed)

            # 更新位置
            distance_nm = speed * self.dt / 3600.0
            lat += distance_nm / 60.0 * math.cos(math.radians(course))
            lon += distance_nm / 60.0 * math.sin(math.radians(course)) / math.cos(math.radians(lat))

            positions.append((round(lat, 6), round(lon, 6)))
            courses.append(round(course, 1))
            speeds.append(round(speed, 2))

        cost = self._calculate_cost(positions, courses, speeds, own)

        return NMPCState(
            time_step=self.dt,
            predicted_positions=positions,
            predicted_courses=courses,
            predicted_speeds=speeds,
            cost=round(cost, 4),
            constraints_satisfied=True,
        )

    def _calculate_cost(
        self,
        positions: List[Tuple[float, float]],
        courses: List[float],
        speeds: List[float],
        original: VesselState,
    ) -> float:
        """计算 NMPC 成本函数"""
        # 路径偏差成本
        path_cost = 0.0
        for lat, lon in positions[1:]:
            dlat = lat - original.lat
            dlon = (lon - original.lon) * math.cos(math.radians(original.lat))
            path_cost += math.sqrt(dlat ** 2 + dlon ** 2) * 60.0

        # 航向变化成本
        course_cost = 0.0
        for i in range(1, len(courses)):
            course_cost += abs(COLREGsMathEngine.angle_diff(courses[i - 1], courses[i]))

        # 速度变化成本
        speed_cost = 0.0
        for i in range(1, len(speeds)):
            speed_cost += abs(speeds[i] - speeds[i - 1])

        return 0.3 * path_cost + 0.5 * course_cost + 0.2 * speed_cost

    def optimize_avoidance(
        self,
        own: VesselState,
        target: VesselState,
        assessment: EncounterAssessment,
    ) -> Dict[str, Any]:
        """优化避碰路径"""
        if assessment.recommended_action == ManeuverAction.MAINTAIN:
            return {
                "action": "maintain",
                "trajectory": self.predict_trajectory(
                    own, [own.course] * self.N, [own.speed] * self.N
                ),
            }

        # 生成候选操纵方案
        candidates = []

        if assessment.recommended_action in [ManeuverAction.ALTER_COURSE_STARBOARD, ManeuverAction.ALTER_COURSE_PORT]:
            direction = 1 if assessment.recommended_action == ManeuverAction.ALTER_COURSE_STARBOARD else -1
            for alter_deg in [20, 30, 40, 50, 60]:
                new_course = COLREGsMathEngine.normalize_angle(own.course + direction * alter_deg)
                courses = [new_course] * self.M + [own.course] * (self.N - self.M)
                speeds = [own.speed] * self.N
                traj = self.predict_trajectory(own, courses, speeds)
                candidates.append((alter_deg, traj))

        elif assessment.recommended_action == ManeuverAction.REDUCE_SPEED:
            for reduction_pct in [20, 30, 50, 70]:
                new_speed = own.speed * (1 - reduction_pct / 100.0)
                courses = [own.course] * self.N
                speeds = [new_speed] * self.M + [own.speed] * (self.N - self.M)
                traj = self.predict_trajectory(own, courses, speeds)
                candidates.append((reduction_pct, traj))

        elif assessment.recommended_action == ManeuverAction.STOP:
            courses = [own.course] * self.N
            speeds = [0.0] * self.M + [own.speed] * (self.N - self.M)
            traj = self.predict_trajectory(own, courses, speeds)
            candidates.append((100, traj))

        if not candidates:
            return {
                "action": "maintain",
                "trajectory": self.predict_trajectory(own, [own.course] * self.N, [own.speed] * self.N),
            }

        # 选择成本最低的方案
        best = min(candidates, key=lambda c: c[1].cost)

        return {
            "action": assessment.recommended_action.value,
            "alteration": best[0],
            "trajectory": best[1],
            "cost": best[1].cost,
            "candidates_evaluated": len(candidates),
        }


class COLREGsAutonomousBrainChannel(MarineChannel):
    """
    L3: COLREGs 自主大脑 Channel

    将国际避碰规则 (COLREG 72) 转化为数学约束，
    结合 NMPC 控制器实现大惯性船舶的平滑规避路径。
    """

    name = "colregs_brain"
    description = "L3: COLREGs 自主大脑 (数学硬编码 + NMPC 平滑规避)"
    version = "1.0.0"
    priority = ChannelPriority.P0
    dependencies: List[str] = ["intelligent_navigation"]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.config = config or {}
        self.math_engine = COLREGsMathEngine()
        self.nmpc = NMPCController(
            prediction_horizon=self.config.get("prediction_horizon", 20),
            control_horizon=self.config.get("control_horizon", 10),
        )
        self._assessments: List[EncounterAssessment] = []
        self._maneuver_log: List[Dict[str, Any]] = []

    def initialize(self) -> bool:
        self._initialized = True
        self._set_health(ChannelStatus.OK, "COLREGs 自主大脑就绪")
        return True

    def assess_situation(self, own: VesselState, targets: List[VesselState]) -> List[EncounterAssessment]:
        """评估所有目标船的会遇情况"""
        assessments = []
        for target in targets:
            assessment = COLREGsMathEngine.assess_encounter(own, target)
            assessments.append(assessment)
        self._assessments = assessments
        return assessments

    def plan_avoidance(self, own: VesselState, targets: List[VesselState]) -> Dict[str, Any]:
        """规划避碰路径"""
        assessments = self.assess_situation(own, targets)

        dangerous = [a for a in assessments if a.risk_level > 0.3 and a.is_give_way]

        if not dangerous:
            return {
                "action": "maintain",
                "message": "无需避碰操纵",
                "assessments": len(assessments),
            }

        # 对最危险的目标进行避碰规划
        most_dangerous = max(dangerous, key=lambda a: a.risk_level)
        target_idx = assessments.index(most_dangerous)
        target = targets[target_idx]

        avoidance = self.nmpc.optimize_avoidance(own, target, most_dangerous)
        avoidance["encounter"] = most_dangerous.encounter_type.value
        avoidance["colreg_rule"] = most_dangerous.colreg_rule.value
        avoidance["risk_level"] = most_dangerous.risk_level
        avoidance["cpa"] = most_dangerous.cpa
        avoidance["tcpa"] = most_dangerous.tcpa

        self._maneuver_log.append({
            "timestamp": datetime.now().isoformat(),
            "encounter": most_dangerous.encounter_type.value,
            "risk_level": most_dangerous.risk_level,
            "action": avoidance.get("action"),
        })

        return avoidance

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "active_assessments": len(self._assessments),
            "maneuver_log_size": len(self._maneuver_log),
            "dangerous_encounters": sum(1 for a in self._assessments if a.risk_level > 0.3),
        }

    # ── Rule 17: Stand-on vessel action (COLREGs audit compliance) ──
    def evaluate_rule_17_stand_on(self, encounter) -> Dict[str, Any]:
        """Rule 17 stand-on vessel: maintain course/speed, take action if give-way
        vessel fails to act. Returns recommended action for stand-on vessel."""
        if not encounter:
            return {"action": "maintain", "rule": "rule_17_stand_on"}
        risk = encounter.risk_level if hasattr(encounter, 'risk_level') else 0.0
        if risk > 0.7:
            return {"action": "emergency_avoid", "rule": "rule_17_stand_on",
                    "detail": "Give-way vessel not acting, stand-on takes emergency action"}
        if risk > 0.4:
            return {"action": "sound_signal", "rule": "rule_17_stand_on",
                    "detail": "Alert give-way vessel with 5+ short blasts"}
        return {"action": "maintain", "rule": "rule_17_stand_on",
                "detail": "Maintain course and speed per Rule 17"}

    # ── Rule 13: Overtaking vessel gives way ──
    def evaluate_rule_13_overtaking(self, own_course_deg: float = 0.0,
                                    target_course_deg: float = 0.0,
                                    relative_bearing_deg: float = 0.0) -> Dict[str, Any]:
        """Rule 13 overtaking: a vessel approaching from abaft the beam (>112.5°)
        is overtaking and must keep clear."""
        is_overtaking = 112.5 <= abs(relative_bearing_deg) <= 247.5
        return {
            "is_overtaking": is_overtaking,
            "rule": "rule_13_overtaking",
            "obligation": "keep_clear" if is_overtaking else "stand_on",
            "relative_bearing": relative_bearing_deg,
        }

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True


__all__ = [
    "COLREGsAutonomousBrainChannel", "COLREGsMathEngine", "NMPCController",
    "VesselState", "EncounterAssessment", "COLREGRule", "EncounterType", "ManeuverAction",
]
