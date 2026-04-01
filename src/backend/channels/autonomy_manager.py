#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autonomy Manager - 自主等级管理

参考 IMO MASS (Maritime Autonomous Surface Ships) 框架:
- M: 具有自动化过程和决策支持的人工航行
- R: 有船员在船的远程控制船舶
- RU: 无船员在船的远程控制船舶
- A: 完全自主船舶

参考 LR (Lloyd's Register) AL0-AL6 自主等级:
- AL0: 手动
- AL1: 船上决策支持
- AL2: 船上/岸基决策支持
- AL3: 人类监督下的主动决策和行动
- AL4: 人类介入的主动决策和行动  
- AL5: 完全自主的无监督操作
- AL6: 完全自主

参考 SHI SAS 系统在 15000TEU 集装箱船上的实证:
- 实时 CRI (碰撞风险指数) 评估
- 半径50km内障碍物识别
- 每5秒提示避碰路径
- 岸基控制中心通过 AR 实时监控
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority


class MASSLevel(Enum):
    """IMO MASS 自主等级 (参考丹麦 DMA 标准)."""
    M = "manual"          # 人工航行 + 自动化辅助
    R = "remote_crewed"   # 有船员在船的远程控制
    RU = "remote_uncrewed"  # 无船员在船的远程控制
    A = "autonomous"      # 完全自主


class LRAutonomyLevel(Enum):
    """Lloyd's Register AL0-AL6 自主等级."""
    AL0 = 0  # Manual - 人工操作
    AL1 = 1  # On-ship decision support - 船上决策支持
    AL2 = 2  # On/off-ship decision support - 船上/岸基决策支持
    AL3 = 3  # Active human in the loop - 人类监督下主动决策
    AL4 = 4  # Human on the loop, operator in command - 人类介入
    AL5 = 5  # Fully autonomous unsupervised - 完全自主无监督
    AL6 = 6  # Fully autonomous - 完全自主


class ControlAuthority(Enum):
    """控制权归属."""
    BRIDGE = "bridge"           # 船桥 (船长/值班驾驶员)
    ENGINE_ROOM = "engine_room" # 机舱
    SHORE_FOC = "shore_foc"     # 岸基 FOC (Fleet Operation Center)
    AUTONOMOUS = "autonomous"   # 系统自主
    SHARED = "shared"           # 共享 (人机共融)


@dataclass
class AutonomyTransition:
    """自主等级切换记录."""
    timestamp: str
    from_level: str
    to_level: str
    authority: str
    reason: str
    approved_by: str


@dataclass
class OperationalConstraint:
    """操作约束条件."""
    constraint_type: str   # "weather", "traffic", "equipment", "regulatory"
    description: str
    max_autonomy_level: int  # 此约束下允许的最高 LR AL 等级
    active: bool = True


class AutonomyManagerChannel(MarineChannel):
    """自主等级管理 Channel.

    对标 SHI SAS 自主航行系统 + IMO MASS 框架 + LR AL0-AL6 等级。
    管理自主等级切换、控制权转移、操作约束评估。
    """

    name = "autonomy_manager"
    description = "自主等级管理 - IMO MASS/LR AL 等级管控与控制权转移"
    version = "1.0.0"
    priority = ChannelPriority.P0
    dependencies = ["intelligent_navigation", "intelligent_engine", "ship_shore_link"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mass_level: MASSLevel = MASSLevel.M
        self._lr_level: LRAutonomyLevel = LRAutonomyLevel.AL1
        self._control_authority: ControlAuthority = ControlAuthority.BRIDGE
        self._constraints: List[OperationalConstraint] = []
        self._transition_history: List[AutonomyTransition] = []
        self._override_active: bool = False
        self._emergency_mode: bool = False

    def initialize(self) -> bool:
        self._constraints = self._default_constraints()
        self._initialized = True
        self._set_health(ChannelStatus.OK, "Autonomy manager initialized at AL1/M")
        return True

    def _default_constraints(self) -> List[OperationalConstraint]:
        """默认操作约束."""
        return [
            OperationalConstraint(
                constraint_type="traffic",
                description="高密度交通区域 (目标>10) 限制自主等级",
                max_autonomy_level=3,
                active=True,
            ),
            OperationalConstraint(
                constraint_type="weather",
                description="恶劣天气 (风力>7级/浪高>4m) 限制自主等级",
                max_autonomy_level=2,
                active=True,
            ),
            OperationalConstraint(
                constraint_type="equipment",
                description="关键设备故障时降级到人工控制",
                max_autonomy_level=1,
                active=True,
            ),
            OperationalConstraint(
                constraint_type="regulatory",
                description="港口/TSS水域需人工确认",
                max_autonomy_level=2,
                active=True,
            ),
            OperationalConstraint(
                constraint_type="communication",
                description="通信链路断开时限制远程控制",
                max_autonomy_level=1,
                active=True,
            ),
        ]

    def get_current_level(self) -> Dict[str, Any]:
        """获取当前自主等级状态."""
        return {
            "mass_level": self._mass_level.value,
            "mass_code": self._mass_level.name,
            "mass_description": self._mass_level_description(),
            "lr_level": self._lr_level.value,
            "lr_description": self._lr_level_description(),
            "control_authority": self._control_authority.value,
            "override_active": self._override_active,
            "emergency_mode": self._emergency_mode,
        }

    def _mass_level_description(self) -> str:
        descriptions = {
            MASSLevel.M: "人工航行，自动化过程和决策支持辅助",
            MASSLevel.R: "有船员在船的远程控制",
            MASSLevel.RU: "无船员在船的远程控制",
            MASSLevel.A: "完全自主航行",
        }
        return descriptions.get(self._mass_level, "未知")

    def _lr_level_description(self) -> str:
        descriptions = {
            LRAutonomyLevel.AL0: "手动操作 - 所有决策由人完成",
            LRAutonomyLevel.AL1: "船上决策支持 - 系统提供信息辅助",
            LRAutonomyLevel.AL2: "船上/岸基决策支持 - 双端信息辅助",
            LRAutonomyLevel.AL3: "人类监督下主动决策 - SAS模式",
            LRAutonomyLevel.AL4: "人类介入 - 操作员在环路中监控",
            LRAutonomyLevel.AL5: "完全自主无监督",
            LRAutonomyLevel.AL6: "完全自主 - 系统完全自主决策与行动",
        }
        return descriptions.get(self._lr_level, "未知")

    def evaluate_max_autonomy(
        self,
        traffic_density: int = 0,
        wind_force_beaufort: int = 0,
        wave_height_m: float = 0.0,
        equipment_health: float = 100.0,
        in_port_area: bool = False,
        shore_link_connected: bool = True,
        visibility_nm: float = 10.0,
    ) -> Dict[str, Any]:
        """根据当前条件评估允许的最高自主等级."""
        max_al = 6  # 从最高开始，逐步约束

        active_constraints = []

        # 交通密度约束
        if traffic_density > 10:
            max_al = min(max_al, 3)
            active_constraints.append(f"高密度交通({traffic_density}目标) → AL≤3")
        elif traffic_density > 5:
            max_al = min(max_al, 4)
            active_constraints.append(f"中密度交通({traffic_density}目标) → AL≤4")

        # 天气约束
        if wind_force_beaufort > 7 or wave_height_m > 4.0:
            max_al = min(max_al, 2)
            active_constraints.append(f"恶劣天气(风{wind_force_beaufort}级/浪{wave_height_m}m) → AL≤2")
        elif wind_force_beaufort > 5 or wave_height_m > 2.5:
            max_al = min(max_al, 3)
            active_constraints.append(f"中等天气 → AL≤3")

        # 设备健康约束
        if equipment_health < 60:
            max_al = min(max_al, 1)
            active_constraints.append(f"设备健康分低({equipment_health}) → AL≤1")
        elif equipment_health < 80:
            max_al = min(max_al, 3)
            active_constraints.append(f"设备健康注意({equipment_health}) → AL≤3")

        # 港口/TSS约束
        if in_port_area:
            max_al = min(max_al, 2)
            active_constraints.append("港口/TSS 水域 → AL≤2")

        # 通信链路约束
        if not shore_link_connected:
            max_al = min(max_al, 1)
            active_constraints.append("通信链路断开 → AL≤1")

        # 能见度约束
        if visibility_nm < 1.0:
            max_al = min(max_al, 2)
            active_constraints.append(f"低能见度({visibility_nm}nm) → AL≤2")
        elif visibility_nm < 3.0:
            max_al = min(max_al, 3)
            active_constraints.append(f"能见度受限({visibility_nm}nm) → AL≤3")

        return {
            "max_allowed_al": max_al,
            "current_al": self._lr_level.value,
            "within_limits": self._lr_level.value <= max_al,
            "active_constraints": active_constraints,
            "recommendation": self._recommend_level(max_al),
        }

    def _recommend_level(self, max_al: int) -> str:
        """推荐操作建议."""
        if max_al >= 5:
            return "条件允许完全自主航行"
        elif max_al >= 3:
            return "建议 SAS 监督模式 (AL3)，操作员保持监控"
        elif max_al >= 2:
            return "建议人机共融模式 (AL2)，船桥/岸基双端决策支持"
        elif max_al >= 1:
            return "建议切回手动模式 (AL1)，系统仅提供辅助信息"
        return "紧急降级至手动 (AL0)"

    def request_transition(
        self,
        target_lr_level: int,
        reason: str = "",
        requested_by: str = "system",
    ) -> Dict[str, Any]:
        """请求自主等级切换."""
        target = LRAutonomyLevel(min(6, max(0, target_lr_level)))

        # 安全检查: 不允许在紧急模式下升级
        if self._emergency_mode and target.value > self._lr_level.value:
            return {
                "approved": False,
                "reason": "紧急模式下禁止升级自主等级",
                "current_level": self._lr_level.value,
            }

        old_level = self._lr_level
        self._lr_level = target

        # 同步更新 MASS 等级
        if target.value <= 1:
            self._mass_level = MASSLevel.M
        elif target.value <= 3:
            self._mass_level = MASSLevel.R
        elif target.value <= 5:
            self._mass_level = MASSLevel.RU
        else:
            self._mass_level = MASSLevel.A

        # 同步控制权
        if target.value <= 1:
            self._control_authority = ControlAuthority.BRIDGE
        elif target.value <= 3:
            self._control_authority = ControlAuthority.SHARED
        else:
            self._control_authority = ControlAuthority.AUTONOMOUS

        transition = AutonomyTransition(
            timestamp=datetime.now().isoformat(),
            from_level=f"AL{old_level.value}",
            to_level=f"AL{target.value}",
            authority=self._control_authority.value,
            reason=reason or "operator_request",
            approved_by=requested_by,
        )
        self._transition_history.append(transition)

        self._set_health(
            ChannelStatus.OK,
            f"Autonomy level: AL{target.value} ({self._mass_level.value})",
        )

        return {
            "approved": True,
            "from_level": old_level.value,
            "to_level": target.value,
            "mass_level": self._mass_level.value,
            "mass_code": self._mass_level.name,
            "control_authority": self._control_authority.value,
        }

    def emergency_override(self, reason: str = "emergency") -> Dict[str, Any]:
        """紧急降级到 AL0 手动模式 (参考 DFFAS 紧急 FOC 切换)."""
        self._emergency_mode = True
        self._override_active = True
        result = self.request_transition(0, reason=reason, requested_by="emergency_system")
        self._control_authority = ControlAuthority.BRIDGE
        return {
            **result,
            "emergency_mode": True,
            "message": "紧急降级至手动控制 - 船桥完全接管",
        }

    def clear_emergency(self) -> Dict[str, Any]:
        """解除紧急模式."""
        self._emergency_mode = False
        self._override_active = False
        return {
            "emergency_cleared": True,
            "current_level": self._lr_level.value,
            "message": "紧急模式已解除，可恢复自主等级",
        }

    def transfer_control(self, to: str) -> Dict[str, Any]:
        """控制权转移 (参考 DFFAS FOC 手柄切换)."""
        authority_map = {
            "bridge": ControlAuthority.BRIDGE,
            "engine_room": ControlAuthority.ENGINE_ROOM,
            "shore_foc": ControlAuthority.SHORE_FOC,
            "autonomous": ControlAuthority.AUTONOMOUS,
            "shared": ControlAuthority.SHARED,
        }
        new_auth = authority_map.get(to)
        if new_auth is None:
            return {"success": False, "reason": f"Unknown authority: {to}"}

        old_auth = self._control_authority
        self._control_authority = new_auth
        return {
            "success": True,
            "from_authority": old_auth.value,
            "to_authority": new_auth.value,
            "timestamp": datetime.now().isoformat(),
        }

    def get_status(self) -> Dict[str, Any]:
        level_info = self.get_current_level()
        return {
            "channel": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": "ok" if not self._emergency_mode else "warn",
            "health_message": f"AL{self._lr_level.value}/{self._mass_level.value}",
            **level_info,
            "transition_count": len(self._transition_history),
            "recent_transitions": [
                {
                    "timestamp": t.timestamp,
                    "from": t.from_level,
                    "to": t.to_level,
                    "reason": t.reason,
                }
                for t in self._transition_history[-5:]
            ],
            "constraints_count": len(self._constraints),
        }

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shut down")
        return True
