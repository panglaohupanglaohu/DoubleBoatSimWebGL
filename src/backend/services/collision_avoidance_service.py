# -*- coding: utf-8 -*-
"""
collision_avoidance_service.py — 碰撞检测与自动避让服务

核心功能:
1. 基于 AIS 目标与本船状态的实时碰撞检测 (CPA/TCPA)
2. 基于 COLREGs 规则的自动避让决策
3. 平滑的航向/航速调整执行
4. 风险等级评估与告警

集成方式:
- 在 main.py 的 SimulationEngine.generate_sensor_data() 循环中调用
- 或作为独立服务由 ship_state_service 调度

依赖:
- channels.colregs_brain.COLREGsMathEngine (CPA/TCPA 计算)
- channels.colregs_brain.VesselState, EncounterType, ManeuverAction
"""

from __future__ import annotations

import math
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ==================== 常量定义 ====================

# 安全阈值
CPA_SAFE_NM = 2.0        # 安全 CPA 阈值 (海里)
CPA_CAUTION_NM = 1.0     # 警戒 CPA 阈值 (海里)
CPA_DANGER_NM = 0.5      # 危险 CPA 阈值 (海里)
TCPA_SAFE_MIN = 30.0     # 安全 TCPA 阈值 (分钟)
TCPA_CAUTION_MIN = 15.0  # 警戒 TCPA 阈值 (分钟)
TCPA_DANGER_MIN = 8.0    # 危险 TCPA 阈值 (分钟)

# 避让参数
MIN_COURSE_CHANGE = 15.0   # 最小航向改变量 (度)
MAX_COURSE_CHANGE = 45.0   # 最大航向改变量 (度)
MIN_SPEED_REDUCTION = 2.0  # 最小减速量 (节)
MAX_SPEED_REDUCTION = 8.0  # 最大减速量 (节)
COURSE_SMOOTHING = 0.3     # 航向平滑系数 (0-1, 越大响应越快)
SPEED_SMOOTHING = 0.2      # 航速平滑系数

# 避让恢复参数
RECOVERY_CPA_THRESHOLD = 3.0   # CPA 大于此值认为已安全，可恢复原航向
RECOVERY_TCPA_THRESHOLD = 60.0 # TCPA 大于此值认为已安全
RECOVERY_COURSE_RATE = 0.05    # 恢复原航向的速率


class RiskLevel(Enum):
    """风险等级"""
    SAFE = "safe"
    CAUTION = "caution"
    DANGER = "danger"
    EMERGENCY = "emergency"


class AvoidanceState(Enum):
    """避让系统状态"""
    IDLE = "idle"                    # 无风险，正常航行
    MONITORING = "monitoring"        # 有警戒目标，持续监控
    AVOIDING = "avoiding"            # 正在执行避让动作
    RECOVERING = "recovering"        # 风险解除，正在恢复原航向
    EMERGENCY = "emergency"          # 紧急情况，大幅避让


@dataclass
class CollisionRisk:
    """碰撞风险评估结果"""
    target_mmsi: str
    target_name: str
    cpa_nm: float                    # 最近会遇距离 (海里)
    tcpa_min: float                  # 到达最近会遇点时间 (分钟)
    range_nm: float                  # 当前距离 (海里)
    bearing_deg: float               # 相对方位 (度)
    risk_level: RiskLevel            # 风险等级
    encounter_type: str              # 会遇类型 (head-on, crossing, overtaking)
    is_give_way: bool                # 本船是否为让路船
    suggested_action: str            # 建议动作描述
    course_change: float             # 建议航向改变量 (度, 正=右转)
    speed_change: float              # 建议航速改变量 (节, 负=减速)


@dataclass
class AvoidanceCommand:
    """避让指令"""
    action_type: str                 # turn_starboard, turn_port, slow_down, maintain
    course_target: Optional[float]   # 目标航向 (度)
    speed_target: Optional[float]    # 目标航速 (节)
    course_change: float             # 航向改变量
    speed_change: float              # 航速改变量
    reason: str                      # 避让原因
    risk_level: RiskLevel            # 触发风险等级
    timestamp: float                 # 指令生成时间


@dataclass
class AvoidanceStatus:
    """避让系统状态"""
    state: AvoidanceState = AvoidanceState.IDLE
    active: bool = False
    current_command: Optional[AvoidanceCommand] = None
    original_course: Optional[float] = None
    original_speed: Optional[float] = None
    current_course: Optional[float] = None
    current_speed: Optional[float] = None
    high_risk_targets: List[Dict[str, Any]] = field(default_factory=list)
    last_assessment_time: Optional[float] = None
    message: str = "系统就绪"


class CollisionAvoidanceService:
    """
    碰撞检测与自动避让服务

    工作流程:
    1. assess_risks(): 对所有 AIS 目标进行 CPA/TCPA 计算和风险评级
    2. decide_avoidance(): 基于最高风险目标生成避让指令
    3. apply_avoidance(): 平滑应用避让指令到本船航向/航速
    4. check_recovery(): 检查是否可恢复原航向
    """

    def __init__(self):
        self.status = AvoidanceStatus()
        self._last_course = None
        self._last_speed = None
        self._recovery_course = None
        self._recovery_speed = None
        self._avoidance_start_time = 0.0
        logger.info("🚢 CollisionAvoidanceService initialized")

    def assess_risks(
        self,
        own_lat: float,
        own_lon: float,
        own_course: float,
        own_speed: float,
        ais_targets: Dict[str, Any],
    ) -> List[CollisionRisk]:
        """
        评估所有 AIS 目标的碰撞风险

        Args:
            own_lat: 本船纬度
            own_lon: 本船经度
            own_course: 本船航向 (度)
            own_speed: 本船航速 (节)
            ais_targets: AIS 目标字典 {mmsi: {latitude, longitude, course, speed, ...}}

        Returns:
            按风险等级排序的 CollisionRisk 列表
        """
        risks = []

        for mmsi, target in ais_targets.items():
            try:
                # 计算相对位置
                d_lon = (target["longitude"] - own_lon) * math.cos(math.radians(own_lat)) * 60
                d_lat = (target["latitude"] - own_lat) * 60
                range_nm = math.sqrt(d_lon ** 2 + d_lat ** 2)
                bearing = (math.degrees(math.atan2(d_lon, d_lat)) + 360) % 360

                # 计算相对速度
                own_vx = (own_speed / 60) * math.sin(math.radians(own_course))
                own_vy = (own_speed / 60) * math.cos(math.radians(own_course))
                tgt_speed = target.get("speed", 0)
                tgt_course = target.get("course", 0)
                tgt_vx = (tgt_speed / 60) * math.sin(math.radians(tgt_course))
                tgt_vy = (tgt_speed / 60) * math.cos(math.radians(tgt_course))

                dvx = tgt_vx - own_vx
                dvy = tgt_vy - own_vy
                dv_sq = dvx * dvx + dvy * dvy

                if dv_sq < 1e-10:
                    cpa = range_nm
                    tcpa = 9999.0
                else:
                    tcpa = max(0, -(d_lon * dvx + d_lat * dvy) / dv_sq)
                    cpx = d_lon + dvx * tcpa
                    cpy = d_lat + dvy * tcpa
                    cpa = math.sqrt(cpx ** 2 + cpy ** 2)

                # 风险等级判定
                risk_level = self._classify_risk(cpa, tcpa, range_nm)

                # 会遇类型判定
                encounter_type = self._classify_encounter(
                    own_course, own_speed, bearing, tgt_course, tgt_speed
                )

                # 本船是否为让路船
                is_give_way = self._is_give_way_vessel(encounter_type, bearing)

                # 生成建议动作
                suggested_action, course_change, speed_change = self._generate_suggestion(
                    risk_level, encounter_type, is_give_way, cpa, tcpa
                )

                target_name = target.get("name", f"TGT-{mmsi[-3:]}")
                risks.append(CollisionRisk(
                    target_mmsi=mmsi,
                    target_name=target_name,
                    cpa_nm=round(cpa, 3),
                    tcpa_min=round(tcpa, 1),
                    range_nm=round(range_nm, 3),
                    bearing_deg=round(bearing, 1),
                    risk_level=risk_level,
                    encounter_type=encounter_type,
                    is_give_way=is_give_way,
                    suggested_action=suggested_action,
                    course_change=course_change,
                    speed_change=speed_change,
                ))
            except Exception as e:
                logger.warning(f"Risk assessment failed for target {mmsi}: {e}")
                continue

        # 按风险等级和 CPA 排序
        risk_order = {
            RiskLevel.EMERGENCY: 0,
            RiskLevel.DANGER: 1,
            RiskLevel.CAUTION: 2,
            RiskLevel.SAFE: 3,
        }
        risks.sort(key=lambda r: (risk_order.get(r.risk_level, 99), r.cpa_nm))

        return risks

    def _classify_risk(self, cpa: float, tcpa: float, range_nm: float) -> RiskLevel:
        """根据 CPA/TCPA 判定风险等级"""
        if cpa < CPA_DANGER_NM and tcpa < TCPA_DANGER_MIN:
            return RiskLevel.EMERGENCY
        if cpa < CPA_DANGER_NM and tcpa < TCPA_CAUTION_MIN:
            return RiskLevel.DANGER
        if cpa < CPA_CAUTION_NM and tcpa < TCPA_CAUTION_MIN:
            return RiskLevel.CAUTION
        if cpa < CPA_SAFE_NM and tcpa < TCPA_SAFE_MIN:
            return RiskLevel.CAUTION
        return RiskLevel.SAFE

    def _classify_encounter(
        self,
        own_course: float,
        own_speed: float,
        rel_bearing: float,
        tgt_course: float,
        tgt_speed: float,
    ) -> str:
        """分类会遇类型 (简化版 COLREGs)"""
        # 航向差
        course_diff = (tgt_course - own_course + 180) % 360 - 180

        # 对遇: 航向近似相反，目标在正前方
        if abs(abs(course_diff) - 180) < 10 and (rel_bearing < 10 or rel_bearing > 350):
            return "head-on"

        # 追越: 目标从后方接近
        if 112.5 < rel_bearing < 247.5:
            return "overtaking"

        # 被追越: 本船从后方接近目标
        tgt_rel_bearing = (rel_bearing + 180) % 360
        if 112.5 < tgt_rel_bearing < 247.5:
            return "being-overtaken"

        # 交叉相遇
        if 0 < rel_bearing <= 112.5:
            return "crossing-starboard"
        if 247.5 <= rel_bearing < 360:
            return "crossing-port"

        return "safe"

    def _is_give_way_vessel(self, encounter_type: str, rel_bearing: float) -> bool:
        """判断本船是否为让路船"""
        if encounter_type == "head-on":
            return True  # 对遇双方都是让路船
        if encounter_type == "crossing-starboard":
            return True  # 右舷交叉，本船为让路船
        if encounter_type == "crossing-port":
            return False  # 左舷交叉，本船为直航船
        if encounter_type == "overtaking":
            return True  # 追越，本船为让路船
        if encounter_type == "being-overtaken":
            return False  # 被追越，本船为直航船
        return False

    def _generate_suggestion(
        self,
        risk_level: RiskLevel,
        encounter_type: str,
        is_give_way: bool,
        cpa: float,
        tcpa: float,
    ) -> Tuple[str, float, float]:
        """生成避让建议"""
        if risk_level == RiskLevel.SAFE:
            return "保持当前航向航速", 0, 0

        if not is_give_way:
            return "保向保速 (直航船)", 0, 0

        # 计算需要的航向改变量
        required_course_change = min(
            MAX_COURSE_CHANGE,
            max(MIN_COURSE_CHANGE, (CPA_SAFE_NM - cpa) * 20)
        )

        # 计算需要的减速量
        required_speed_reduction = min(
            MAX_SPEED_REDUCTION,
            max(MIN_SPEED_REDUCTION, (CPA_SAFE_NM - cpa) * 10)
        )

        if encounter_type == "head-on":
            return (
                f"对遇局面: 向右转向 {required_course_change:.0f}°",
                required_course_change,
                0,
            )
        elif encounter_type == "crossing-starboard":
            return (
                f"右舷交叉: 向右转向 {required_course_change:.0f}° 或减速 {required_speed_reduction:.0f} 节",
                required_course_change,
                -required_speed_reduction,
            )
        elif encounter_type == "overtaking":
            return (
                f"追越: 向右转向 {required_course_change:.0f}° 增加横向距离",
                required_course_change,
                0,
            )
        elif encounter_type == "crossing-port":
            return "左舷交叉: 保向保速", 0, 0
        else:
            return (
                f"建议向右转向 {required_course_change:.0f}°",
                required_course_change,
                0,
            )

    def decide_avoidance(
        self,
        risks: List[CollisionRisk],
        current_course: float,
        current_speed: float,
    ) -> Optional[AvoidanceCommand]:
        """
        基于风险评估结果生成避让指令

        策略:
        1. 只对让路船局面执行避让
        2. 优先处理最高风险目标
        3. 避让动作平滑、符合 COLREGs
        """
        if not risks:
            return None

        # 找到最高风险且本船为让路船的目标
        highest_risk = None
        for risk in risks:
            if risk.risk_level in (RiskLevel.DANGER, RiskLevel.EMERGENCY, RiskLevel.CAUTION):
                if risk.is_give_way:
                    highest_risk = risk
                    break

        if not highest_risk:
            # 没有需要避让的目标
            if self.status.state == AvoidanceState.AVOIDING:
                self.status.state = AvoidanceState.RECOVERING
                self.status.message = "风险解除，正在恢复航向"
            return None

        # 生成避让指令
        new_course = (current_course + highest_risk.course_change) % 360
        new_speed = max(1.0, current_speed + highest_risk.speed_change)

        command = AvoidanceCommand(
            action_type="turn_starboard" if highest_risk.course_change > 0 else "turn_port"
            if highest_risk.course_change < 0 else "maintain",
            course_target=new_course,
            speed_target=new_speed,
            course_change=highest_risk.course_change,
            speed_change=highest_risk.speed_change,
            reason=highest_risk.suggested_action,
            risk_level=highest_risk.risk_level,
            timestamp=datetime.now().timestamp(),
        )

        self.status.current_command = command
        self.status.state = AvoidanceState.AVOIDING
        self.status.active = True
        self.status.message = f"避让中: {command.reason}"

        logger.warning(
            f"🚨 避让指令: {command.reason} | "
            f"航向 {current_course:.1f}° → {new_course:.1f}° | "
            f"航速 {current_speed:.1f} → {new_speed:.1f} kn"
        )

        return command

    def apply_avoidance(
        self,
        command: Optional[AvoidanceCommand],
        current_course: float,
        current_speed: float,
        dt: float = 1.0,
    ) -> Tuple[float, float]:
        """
        平滑应用避让指令

        Returns:
            (new_course, new_speed) 平滑后的航向和航速
        """
        if command is None:
            # 无指令，检查是否需要恢复
            return self._apply_recovery(current_course, current_speed, dt)

        # 保存原始航向航速
        if self._recovery_course is None:
            self._recovery_course = current_course
        if self._recovery_speed is None:
            self._recovery_speed = current_speed

        # 平滑转向
        target_course = command.course_target
        course_diff = (target_course - current_course + 180) % 360 - 180
        course_step = course_diff * COURSE_SMOOTHING * dt

        new_course = (current_course + course_step) % 360

        # 平滑调速
        target_speed = command.speed_target
        speed_diff = target_speed - current_speed
        speed_step = speed_diff * SPEED_SMOOTHING * dt
        new_speed = current_speed + speed_step

        self.status.current_course = new_course
        self.status.current_speed = new_speed

        return new_course, new_speed

    def _apply_recovery(
        self,
        current_course: float,
        current_speed: float,
        dt: float = 1.0,
    ) -> Tuple[float, float]:
        """恢复原始航向航速"""
        if self._recovery_course is None:
            return current_course, current_speed

        # 平滑恢复航向
        course_diff = (self._recovery_course - current_course + 180) % 360 - 180
        if abs(course_diff) < 0.5:
            new_course = self._recovery_course
            self.status.state = AvoidanceState.IDLE
            self.status.active = False
            self.status.message = "已恢复原始航向"
            self._recovery_course = None
            self._recovery_speed = None
        else:
            course_step = course_diff * RECOVERY_COURSE_RATE * dt
            new_course = (current_course + course_step) % 360
            self.status.state = AvoidanceState.RECOVERING
            self.status.message = f"恢复航向中 ({abs(course_diff):.1f}° 剩余)"

        # 平滑恢复航速
        if self._recovery_speed is not None:
            speed_diff = self._recovery_speed - current_speed
            if abs(speed_diff) < 0.1:
                new_speed = self._recovery_speed
            else:
                new_speed = current_speed + speed_diff * SPEED_SMOOTHING * dt
        else:
            new_speed = current_speed

        self.status.current_course = new_course
        self.status.current_speed = new_speed

        return new_course, new_speed

    def check_recovery(
        self,
        risks: List[CollisionRisk],
        current_course: float,
        current_speed: float,
    ) -> bool:
        """
        检查是否可以恢复原始航向

        条件:
        - 所有目标 CPA > RECOVERY_CPA_THRESHOLD
        - 或所有目标 TCPA > RECOVERY_TCPA_THRESHOLD
        - 且没有 DANGER/EMERGENCY 级别的风险
        """
        if self.status.state != AvoidanceState.AVOIDING:
            return False

        # 检查是否有高风险目标
        has_high_risk = any(
            r.risk_level in (RiskLevel.DANGER, RiskLevel.EMERGENCY)
            for r in risks
        )

        if has_high_risk:
            return False

        # 检查是否所有目标都已安全
        all_safe = all(
            r.cpa_nm > RECOVERY_CPA_THRESHOLD or r.tcpa_min > RECOVERY_TCPA_THRESHOLD
            for r in risks
        )

        if all_safe:
            logger.info("✅ 所有目标已安全，开始恢复航向")
            self.status.state = AvoidanceState.RECOVERING
            self.status.message = "风险解除，正在恢复航向"
            return True

        return False

    def get_status(self) -> Dict[str, Any]:
        """获取避让系统状态"""
        return {
            "state": self.status.state.value,
            "active": self.status.active,
            "message": self.status.message,
            "current_command": {
                "action_type": self.status.current_command.action_type,
                "course_target": self.status.current_command.course_target,
                "speed_target": self.status.current_command.speed_target,
                "reason": self.status.current_command.reason,
                "risk_level": self.status.current_command.risk_level.value,
            } if self.status.current_command else None,
            "original_course": self.status.original_course,
            "original_speed": self.status.original_speed,
            "current_course": self.status.current_course,
            "current_speed": self.status.current_speed,
            "high_risk_targets": self.status.high_risk_targets,
            "timestamp": datetime.now().isoformat(),
        }

    def reset(self):
        """重置避让系统"""
        self.status = AvoidanceStatus()
        self._recovery_course = None
        self._recovery_speed = None
        logger.info("🔄 CollisionAvoidanceService reset")
