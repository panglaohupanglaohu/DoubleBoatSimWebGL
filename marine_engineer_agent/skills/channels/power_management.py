"""
船舶电力管理系统 Channel (Power Management System)

实现船舶电力管理系统的核心功能，包括发电机管理、负载分配、并车同步、
 blackout 预防等功能。基于 IMO 和船级社规范设计。

功能特性:
- 发电机状态监控 (运行/停机/故障/备用)
- 自动负载分配 (等负载/优先级/经济模式)
- 并车同步检测 (电压/频率/相位)
- Blackout 预防与恢复
- 应急发电机管理
- 负载 shedding (分级卸载)
- 电力质量监控 (电压/频率/谐波)

参考标准:
- IMO SOLAS Chapter II-1
- ABS Rules for Building and Classing Marine Vessels
- DNV GL Rules for Classification
- IEEE 45-2002 (Recommended Practice for Electric Installations on Shipboard)

作者：CaptainCatamaran 🐱⛵
版本：1.0.0
日期：2026-03-11
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any

from .base import Channel


class GeneratorState(Enum):
    """发电机运行状态"""
    STOPPED = "stopped"           # 停机
    STARTING = "starting"         # 启动中
    RUNNING = "running"           # 运行
    SYNCHRONIZING = "synchronizing"  # 并车同步中
    PARALLELED = "paralleled"     # 并车运行
    STOPPING = "stopping"         # 停机中
    FAULT = "fault"               # 故障
    MAINTENANCE = "maintenance"   # 维护


class GeneratorMode(Enum):
    """发电机控制模式"""
    MANUAL = "manual"             # 手动
    AUTO = "auto"                 # 自动
    REMOTE = "remote"             # 遥控


class LoadShareMode(Enum):
    """负载分配模式"""
    EQUAL_LOAD = "equal_load"           # 等负载分配
    PRIORITY = "priority"               # 优先级分配
    ECONOMIC = "economic"               # 经济模式 (最优燃油消耗)
    PEAK_SHAVING = "peak_shaving"       # 削峰模式


class BusState(Enum):
    """母线状态"""
    DEAD = "dead"               # 失电
    LIVE = "live"               # 带电
    BLACKOUT = "blackout"       # 全船失电


@dataclass
class Generator:
    """发电机数据类"""
    generator_id: str
    name: str
    rated_power_kw: float
    rated_voltage_v: float
    rated_frequency_hz: float
    rated_rpm: int
    state: GeneratorState = GeneratorState.STOPPED
    mode: GeneratorMode = GeneratorMode.MANUAL
    current_power_kw: float = 0.0
    current_voltage_v: float = 0.0
    current_frequency_hz: float = 0.0
    current_rpm: int = 0
    power_factor: float = 1.0
    running_hours: float = 0.0
    fuel_consumption_kg_h: float = 0.0
    cooling_water_temp_c: float = 0.0
    lube_oil_pressure_bar: float = 0.0
    exhaust_temp_c: float = 0.0
    start_attempts: int = 0
    last_maintenance_date: Optional[datetime] = None
    priority: int = 1  # 1=最高优先级
    available: bool = True
    fault_code: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "generator_id": self.generator_id,
            "name": self.name,
            "rated_power_kw": self.rated_power_kw,
            "state": self.state.value,
            "mode": self.mode.value,
            "current_power_kw": self.current_power_kw,
            "load_percent": self.load_percent,
            "current_voltage_v": self.current_voltage_v,
            "current_frequency_hz": self.current_frequency_hz,
            "power_factor": self.power_factor,
            "running_hours": self.running_hours,
            "fuel_consumption_kg_h": self.fuel_consumption_kg_h,
            "available": self.available,
            "fault_code": self.fault_code,
        }
    
    @property
    def load_percent(self) -> float:
        """负载百分比"""
        if self.rated_power_kw == 0:
            return 0.0
        return (self.current_power_kw / self.rated_power_kw) * 100


@dataclass
class SynchronizationCheck:
    """并车同步检查结果"""
    voltage_diff_v: float = 0.0
    voltage_diff_percent: float = 0.0
    frequency_diff_hz: float = 0.0
    phase_diff_deg: float = 0.0
    slip_frequency_hz: float = 0.0
    sync_allowed: bool = False
    sync_point_in_ms: int = 0
    warnings: List[str] = field(default_factory=list)
    
    # 允许并车的阈值 (典型值)
    MAX_VOLTAGE_DIFF_PERCENT = 10.0   # ±10%
    MAX_FREQUENCY_DIFF_HZ = 0.5       # ±0.5 Hz
    MAX_PHASE_DIFF_DEG = 10.0         # ±10°
    MAX_SLIP_FREQUENCY_HZ = 0.25      # ±0.25 Hz


@dataclass
class PowerAlarm:
    """电力报警数据类"""
    alarm_id: str
    timestamp: datetime
    level: AlarmLevel
    category: str
    message: str
    generator_id: Optional[str] = None
    parameter: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None
    acknowledged: bool = False
    acknowledged_time: Optional[datetime] = None
    cleared: bool = False
    cleared_time: Optional[datetime] = None


class AlarmLevel(Enum):
    """报警等级 (基于船级社规范)"""
    CRITICAL = "CRITICAL"     # 危急 - 立即跳闸/停车
    HIGH = "HIGH"             # 高 - 减速/卸载
    MEDIUM = "MEDIUM"         # 中 - 警告
    LOW = "LOW"               # 低 - 提示


@dataclass
class LoadGroup:
    """负载组 (用于分级卸载)"""
    group_id: str
    name: str
    priority: int  # 1=最重要 (应急负载), 5=最不重要
    total_power_kw: float = 0.0
    connected_power_kw: float = 0.0
    breakers: List[str] = field(default_factory=list)
    auto_shed: bool = True  # 允许自动卸载


@dataclass
class PowerSystemStatus:
    """电力系统状态汇总"""
    timestamp: datetime
    total_generated_kw: float
    total_load_kw: float
    spinning_reserve_kw: float
    reserve_percent: float
    active_generators: int
    available_generators: int
    bus_state: BusState
    bus_voltage_v: float
    bus_frequency_hz: float
    system_load_percent: float
    fuel_consumption_total_kg_h: float
    active_alarms: int
    critical_alarms: int
    blackout_risk: str  # "low", "medium", "high"
    recommendations: List[str] = field(default_factory=list)


@dataclass
class OperationResult:
    """操作结果数据类"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: str = ""
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "message": self.message,
        }


class PowerManagementChannel(Channel):
    """
    船舶电力管理系统 Channel
    
    实现船舶电力管理系统的核心功能:
    - 发电机监控与管理
    - 负载分配与优化
    - 并车同步控制
    - Blackout 预防
    - 应急电源管理
    """
    
    name = "power_management"
    description = "船舶电力管理系统 (发电机/负载/并车/blackout 预防)"
    
    def __init__(self, name: str = "power_management"):
        self.generators: Dict[str, Generator] = {}
        self.load_groups: Dict[str, LoadGroup] = {}
        self.alarms: Dict[str, PowerAlarm] = {}
        self.bus_state = BusState.DEAD
        self.bus_voltage_v = 0.0
        self.bus_frequency_hz = 0.0
        self.total_load_kw = 0.0
        self.load_share_mode = LoadShareMode.EQUAL_LOAD
        self.blackout_prevention_enabled = True
        self.auto_start_enabled = True
        self.sync_check_results: Dict[str, SynchronizationCheck] = {}
        
        # 配置参数
        self.config = {
            "min_spinning_reserve_percent": 20.0,  # 最小旋转备用
            "max_generator_load_percent": 90.0,    # 最大允许负载
            "start_delay_seconds": 10,              # 启动延时
            "stop_delay_seconds": 30,               # 停机延时
            "blackout_restart_delay_seconds": 5,   # 黑启动延时
            "emergency_generator_auto_start_seconds": 45,  # 应急发电机自启动时间
        }
    
    def register_generator(self, generator: Generator) -> OperationResult:
        """注册发电机"""
        self.generators[generator.generator_id] = generator
        return OperationResult(
            success=True,
            data={"generator_id": generator.generator_id, "name": generator.name},
            message=f"发电机 {generator.name} 已注册"
        )
    
    def start_generator(self, generator_id: str) -> OperationResult:
        """启动发电机"""
        if generator_id not in self.generators:
            return OperationResult(
                success=False,
                error=f"发电机 {generator_id} 未找到",
                message="发电机未注册"
            )
        
        gen = self.generators[generator_id]
        
        if not gen.available:
            return OperationResult(
                success=False,
                error=f"发电机 {gen.name} 不可用",
                message="发电机处于维护或故障状态"
            )
        
        if gen.state != GeneratorState.STOPPED:
            return OperationResult(
                success=False,
                error=f"发电机 {gen.name} 当前状态为 {gen.state.value}",
                message="发电机无法启动"
            )
        
        # 模拟启动过程
        gen.state = GeneratorState.STARTING
        gen.start_attempts += 1
        
        # 启动成功后
        gen.state = GeneratorState.RUNNING
        gen.current_voltage_v = gen.rated_voltage_v * 0.98  # 初始电压略低
        gen.current_frequency_hz = gen.rated_frequency_hz * 1.02  # 初始频率略高
        gen.current_rpm = gen.rated_rpm
        
        return OperationResult(
            success=True,
            data=gen.to_dict(),
            message=f"发电机 {gen.name} 启动成功"
        )
    
    def stop_generator(self, generator_id: str) -> OperationResult:
        """停止发电机"""
        if generator_id not in self.generators:
            return OperationResult(
                success=False,
                error=f"发电机 {generator_id} 未找到",
                message="发电机未注册"
            )
        
        gen = self.generators[generator_id]
        
        if gen.state not in [GeneratorState.RUNNING, GeneratorState.PARALLELED]:
            return OperationResult(
                success=False,
                error=f"发电机 {gen.name} 当前状态为 {gen.state.value}",
                message="发电机无法停止"
            )
        
        # 先卸载
        gen.current_power_kw = 0.0
        gen.state = GeneratorState.STOPPING
        
        # 停机
        gen.state = GeneratorState.STOPPED
        gen.current_voltage_v = 0.0
        gen.current_frequency_hz = 0.0
        gen.current_rpm = 0
        
        return OperationResult(
            success=True,
            data=gen.to_dict(),
            message=f"发电机 {gen.name} 已停止"
        )
    
    def check_synchronization(self, generator_id: str) -> OperationResult:
        """
        检查发电机并车同步条件
        
        并车条件 (典型值):
        - 电压差 < ±10%
        - 频率差 < ±0.5 Hz
        - 相位差 < ±10°
        - 滑差频率 < ±0.25 Hz
        """
        if generator_id not in self.generators:
            return OperationResult(
                success=False,
                error=f"发电机 {generator_id} 未找到",
                message="发电机未注册"
            )
        
        gen = self.generators[generator_id]
        
        if gen.state not in [GeneratorState.RUNNING, GeneratorState.SYNCHRONIZING]:
            return OperationResult(
                success=False,
                error=f"发电机 {gen.name} 状态为 {gen.state.value}",
                message="发电机未准备好并车"
            )
        
        # 计算同步参数
        voltage_diff_v = abs(gen.current_voltage_v - self.bus_voltage_v)
        voltage_diff_percent = (voltage_diff_v / self.bus_voltage_v) * 100 if self.bus_voltage_v > 0 else 100
        frequency_diff_hz = abs(gen.current_frequency_hz - self.bus_frequency_hz)
        
        # 简化的相位差计算 (实际需要相位角测量)
        phase_diff_deg = abs(frequency_diff_hz * 360 / gen.rated_frequency_hz) * 10
        
        slip_frequency_hz = frequency_diff_hz
        
        # 创建检查结果
        check = SynchronizationCheck(
            voltage_diff_v=voltage_diff_v,
            voltage_diff_percent=voltage_diff_percent,
            frequency_diff_hz=frequency_diff_hz,
            phase_diff_deg=phase_diff_deg,
            slip_frequency_hz=slip_frequency_hz,
        )
        
        # 判断是否允许并车
        warnings = []
        sync_allowed = True
        
        if voltage_diff_percent > SynchronizationCheck.MAX_VOLTAGE_DIFF_PERCENT:
            sync_allowed = False
            warnings.append(f"电压差过大：{voltage_diff_percent:.1f}% (允许：±{SynchronizationCheck.MAX_VOLTAGE_DIFF_PERCENT}%)")
        
        if frequency_diff_hz > SynchronizationCheck.MAX_FREQUENCY_DIFF_HZ:
            sync_allowed = False
            warnings.append(f"频率差过大：{frequency_diff_hz:.2f} Hz (允许：±{SynchronizationCheck.MAX_FREQUENCY_DIFF_HZ} Hz)")
        
        if phase_diff_deg > SynchronizationCheck.MAX_PHASE_DIFF_DEG:
            sync_allowed = False
            warnings.append(f"相位差过大：{phase_diff_deg:.1f}° (允许：±{SynchronizationCheck.MAX_PHASE_DIFF_DEG}°)")
        
        if slip_frequency_hz > SynchronizationCheck.MAX_SLIP_FREQUENCY_HZ:
            warnings.append(f"滑差频率偏高：{slip_frequency_hz:.3f} Hz (建议：<{SynchronizationCheck.MAX_SLIP_FREQUENCY_HZ} Hz)")
        
        check.sync_allowed = sync_allowed
        check.warnings = warnings
        
        # 计算同步点 (简化的预测)
        if sync_allowed and slip_frequency_hz > 0:
            check.sync_point_in_ms = int((360 - phase_diff_deg) / (slip_frequency_hz * 360) * 1000)
        
        self.sync_check_results[generator_id] = check
        
        return OperationResult(
            success=sync_allowed,
            data={
                "voltage_diff_percent": voltage_diff_percent,
                "frequency_diff_hz": frequency_diff_hz,
                "phase_diff_deg": phase_diff_deg,
                "slip_frequency_hz": slip_frequency_hz,
                "sync_allowed": sync_allowed,
                "sync_point_in_ms": check.sync_point_in_ms,
                "warnings": warnings,
            },
            message="并车同步检查完成" + (" - 允许并车" if sync_allowed else " - 禁止并车")
        )
    
    def synchronize_generator(self, generator_id: str) -> OperationResult:
        """执行发电机并车"""
        # 先检查同步条件
        check_result = self.check_synchronization(generator_id)
        
        if not check_result.success:
            return OperationResult(
                success=False,
                error=check_result.error,
                data=check_result.data,
                message="并车失败 - 同步条件不满足"
            )
        
        gen = self.generators[generator_id]
        gen.state = GeneratorState.SYNCHRONIZING
        
        # 模拟并车过程
        gen.state = GeneratorState.PARALLELED
        
        return OperationResult(
            success=True,
            data=gen.to_dict(),
            message=f"发电机 {gen.name} 并车成功"
        )
    
    def distribute_load(self, total_load_kw: float) -> OperationResult:
        """
        负载分配
        
        支持模式:
        - EQUAL_LOAD: 等负载分配 (所有并车发电机负载率相同)
        - PRIORITY: 优先级分配 (优先使用高优先级发电机)
        - ECONOMIC: 经济模式 (最优燃油消耗组合)
        """
        # 获取并车运行的发电机
        paralleled_gens = [
            g for g in self.generators.values()
            if g.state == GeneratorState.PARALLELED and g.available
        ]
        
        if not paralleled_gens:
            return OperationResult(
                success=False,
                error="没有并车运行的发电机",
                message="无法进行负载分配"
            )
        
        self.total_load_kw = total_load_kw
        
        if self.load_share_mode == LoadShareMode.EQUAL_LOAD:
            return self._equal_load_distribution(total_load_kw, paralleled_gens)
        elif self.load_share_mode == LoadShareMode.PRIORITY:
            return self._priority_load_distribution(total_load_kw, paralleled_gens)
        elif self.load_share_mode == LoadShareMode.ECONOMIC:
            return self._economic_load_distribution(total_load_kw, paralleled_gens)
        else:
            return OperationResult(
                success=False,
                error=f"未知的负载分配模式：{self.load_share_mode.value}",
                message="负载分配失败"
            )
    
    def _equal_load_distribution(self, total_load_kw: float, generators: List[Generator]) -> OperationResult:
        """等负载分配"""
        total_rated_kw = sum(g.rated_power_kw for g in generators)
        target_load_percent = (total_load_kw / total_rated_kw) * 100 if total_rated_kw > 0 else 0
        
        allocations = []
        for gen in generators:
            target_power = gen.rated_power_kw * target_load_percent / 100
            # 限制在最大允许负载内
            target_power = min(target_power, gen.rated_power_kw * self.config["max_generator_load_percent"] / 100)
            gen.current_power_kw = target_power
            allocations.append({
                "generator_id": gen.generator_id,
                "name": gen.name,
                "power_kw": target_power,
                "load_percent": gen.load_percent,
            })
        
        return OperationResult(
            success=True,
            data={
                "mode": "equal_load",
                "total_load_kw": total_load_kw,
                "allocations": allocations,
            },
            message=f"等负载分配完成 - 目标负载率 {target_load_percent:.1f}%"
        )
    
    def _priority_load_distribution(self, total_load_kw: float, generators: List[Generator]) -> OperationResult:
        """优先级负载分配"""
        # 按优先级排序 (1=最高)
        sorted_gens = sorted(generators, key=lambda g: g.priority)
        
        remaining_load = total_load_kw
        allocations = []
        
        for gen in sorted_gens:
            if remaining_load <= 0:
                gen.current_power_kw = 0.0
            else:
                # 优先使用高优先级发电机
                max_power = gen.rated_power_kw * self.config["max_generator_load_percent"] / 100
                assigned_power = min(remaining_load, max_power)
                gen.current_power_kw = assigned_power
                remaining_load -= assigned_power
            
            allocations.append({
                "generator_id": gen.generator_id,
                "name": gen.name,
                "priority": gen.priority,
                "power_kw": gen.current_power_kw,
                "load_percent": gen.load_percent,
            })
        
        if remaining_load > 0:
            return OperationResult(
                success=False,
                error=f"负载分配不足 - 剩余 {remaining_load:.1f} kW 未分配",
                data={"allocations": allocations, "unassigned_kw": remaining_load},
                message="需要启动更多发电机"
            )
        
        return OperationResult(
            success=True,
            data={
                "mode": "priority",
                "total_load_kw": total_load_kw,
                "allocations": allocations,
            },
            message="优先级负载分配完成"
        )
    
    def _economic_load_distribution(self, total_load_kw: float, generators: List[Generator]) -> OperationResult:
        """经济负载分配 (简化版 - 基于燃油消耗率)"""
        # 实际应用中需要查询发电机的燃油消耗曲线
        # 这里简化为: 优先使用运行小时数少的发电机 (平衡磨损)
        sorted_gens = sorted(generators, key=lambda g: g.running_hours)
        
        return self._priority_load_distribution(total_load_kw, sorted_gens)
    
    def check_spinning_reserve(self) -> OperationResult:
        """检查旋转备用"""
        paralleled_gens = [
            g for g in self.generators.values()
            if g.state == GeneratorState.PARALLELED and g.available
        ]
        
        total_rated_kw = sum(g.rated_power_kw for g in paralleled_gens)
        total_current_kw = sum(g.current_power_kw for g in paralleled_gens)
        available_gens = [
            g for g in self.generators.values()
            if g.state == GeneratorState.STOPPED and g.available
        ]
        standby_capacity_kw = sum(g.rated_power_kw for g in available_gens)
        
        spinning_reserve_kw = total_rated_kw - total_current_kw
        reserve_percent = (spinning_reserve_kw / total_rated_kw) * 100 if total_rated_kw > 0 else 0
        
        min_reserve = self.config["min_spinning_reserve_percent"]
        reserve_adequate = reserve_percent >= min_reserve
        
        return OperationResult(
            success=reserve_adequate,
            data={
                "spinning_reserve_kw": spinning_reserve_kw,
                "reserve_percent": reserve_percent,
                "min_required_percent": min_reserve,
                "adequate": reserve_adequate,
                "standby_capacity_kw": standby_capacity_kw,
                "active_generators": len(paralleled_gens),
                "available_standby": len(available_gens),
            },
            message="旋转备用充足" if reserve_adequate else f"旋转备用不足 - 当前 {reserve_percent:.1f}%, 要求 {min_reserve}%"
        )
    
    def perform_load_shedding(self, target_reduction_kw: float) -> OperationResult:
        """
        执行负载卸载 (分级卸载)
        
        负载分级:
        - Group 1: 应急负载 (导航、通信、消防) - 不允许卸载
        - Group 2: 重要负载 (主机辅机、舵机) - 紧急情况卸载
        - Group 3: 必要负载 (照明、通风) - 中等情况卸载
        - Group 4: 舒适负载 (空调、娱乐) - 优先卸载
        - Group 5: 非必要负载 - 首先卸载
        """
        if not self.load_groups:
            return OperationResult(
                success=False,
                error="未配置负载组",
                message="无法执行负载卸载"
            )
        
        # 按优先级从低到高排序 (先卸载低优先级负载)
        sorted_groups = sorted(self.load_groups.values(), key=lambda g: -g.priority)
        
        shed_groups = []
        remaining_reduction = target_reduction_kw
        
        for group in sorted_groups:
            if remaining_reduction <= 0:
                break
            
            if group.auto_shed and group.connected_power_kw > 0:
                shed_power = min(group.connected_power_kw, remaining_reduction)
                group.connected_power_kw -= shed_power
                remaining_reduction -= shed_power
                shed_groups.append({
                    "group_id": group.group_id,
                    "name": group.name,
                    "priority": group.priority,
                    "shed_power_kw": shed_power,
                })
        
        if remaining_reduction > 0:
            return OperationResult(
                success=False,
                error=f"负载卸载不足 - 剩余 {remaining_reduction:.1f} kW 未卸载",
                data={"shed_groups": shed_groups, "remaining_kw": remaining_reduction},
                message="需要手动干预 - 低优先级负载已全部卸载"
            )
        
        return OperationResult(
            success=True,
            data={
                "target_reduction_kw": target_reduction_kw,
                "shed_groups": shed_groups,
                "total_shed_kw": target_reduction_kw,
            },
            message=f"负载卸载完成 - 共卸载 {target_reduction_kw:.1f} kW"
        )
    
    def detect_blackout(self) -> OperationResult:
        """检测 blackout 状态"""
        paralleled_gens = [
            g for g in self.generators.values()
            if g.state in [GeneratorState.PARALLELED, GeneratorState.RUNNING]
        ]
        
        if not paralleled_gens:
            self.bus_state = BusState.BLACKOUT
            return OperationResult(
                success=True,
                data={"blackout_detected": True, "bus_state": "blackout"},
                message="⚠️ 检测到全船失电 (BLACKOUT)"
            )
        
        # 检查母线电压和频率
        if self.bus_voltage_v < self.config.get("min_voltage_v", 300) or self.bus_frequency_hz < 45:
            self.bus_state = BusState.BLACKOUT
            return OperationResult(
                success=True,
                data={"blackout_detected": True, "bus_state": "blackout"},
                message="⚠️ 检测到母线失电"
            )
        
        self.bus_state = BusState.LIVE
        return OperationResult(
            success=True,
            data={"blackout_detected": False, "bus_state": "live"},
            message="电力系统正常"
        )
    
    def blackout_recovery(self) -> OperationResult:
        """
        Blackout 恢复程序
        
        步骤:
        1. 检测 blackout
        2. 启动应急发电机 (如配置)
        3. 恢复重要负载
        4. 启动主发电机
        5. 逐步恢复全部负载
        """
        # 步骤 1: 检测 blackout
        blackout_result = self.detect_blackout()
        if not blackout_result.data.get("blackout_detected"):
            return OperationResult(
                success=False,
                error="未检测到 blackout",
                message="无需执行黑启动程序"
            )
        
        recovery_steps = []
        
        # 步骤 2: 启动应急发电机
        emergency_gens = [g for g in self.generators.values() if "emergency" in g.name.lower() or g.priority == 1]
        if emergency_gens:
            emergency_gen = emergency_gens[0]
            self.start_generator(emergency_gen.generator_id)
            recovery_steps.append(f"启动应急发电机：{emergency_gen.name}")
        
        # 步骤 3: 恢复重要负载 (Group 1-2)
        important_groups = [g for g in self.load_groups.values() if g.priority <= 2]
        for group in important_groups:
            group.connected_power_kw = group.total_power_kw * 0.5  # 先恢复 50%
            recovery_steps.append(f"恢复重要负载组：{group.name}")
        
        # 步骤 4: 启动主发电机
        main_gens = [g for g in self.generators.values() if g.priority >= 2 and g.available]
        for gen in main_gens[:2]:  # 启动前 2 台
            self.start_generator(gen.generator_id)
            self.synchronize_generator(gen.generator_id)
            recovery_steps.append(f"启动并并车主发电机：{gen.name}")
        
        # 步骤 5: 逐步恢复负载
        for group in sorted(self.load_groups.values(), key=lambda g: g.priority):
            group.connected_power_kw = group.total_power_kw
            recovery_steps.append(f"恢复负载组：{group.name}")
        
        self.bus_state = BusState.LIVE
        
        return OperationResult(
            success=True,
            data={
                "recovery_completed": True,
                "steps": recovery_steps,
                "bus_state": "live",
            },
            message="✅ Blackout 恢复完成"
        )
    
    def create_alarm(self, level: AlarmLevel, category: str, message: str,
                     generator_id: Optional[str] = None,
                     parameter: Optional[str] = None,
                     value: Optional[float] = None,
                     threshold: Optional[float] = None) -> PowerAlarm:
        """创建报警"""
        alarm = PowerAlarm(
            alarm_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(),
            level=level,
            category=category,
            message=message,
            generator_id=generator_id,
            parameter=parameter,
            value=value,
            threshold=threshold,
        )
        self.alarms[alarm.alarm_id] = alarm
        return alarm
    
    def acknowledge_alarm(self, alarm_id: str) -> OperationResult:
        """确认报警"""
        if alarm_id not in self.alarms:
            return OperationResult(
                success=False,
                error=f"报警 {alarm_id} 未找到",
                message="报警确认失败"
            )
        
        alarm = self.alarms[alarm_id]
        alarm.acknowledged = True
        alarm.acknowledged_time = datetime.now()
        
        return OperationResult(
            success=True,
            data={"alarm_id": alarm_id, "acknowledged_time": alarm.acknowledged_time.isoformat()},
            message="报警已确认"
        )
    
    def get_active_alarms(self) -> List[PowerAlarm]:
        """获取活跃报警"""
        return [
            a for a in self.alarms.values()
            if not a.acknowledged and not a.cleared
        ]
    
    def get_system_status(self) -> PowerSystemStatus:
        """获取电力系统状态汇总"""
        paralleled_gens = [
            g for g in self.generators.values()
            if g.state == GeneratorState.PARALLELED and g.available
        ]
        
        total_generated_kw = sum(g.current_power_kw for g in paralleled_gens)
        total_rated_kw = sum(g.rated_power_kw for g in paralleled_gens)
        spinning_reserve_kw = total_rated_kw - total_generated_kw
        reserve_percent = (spinning_reserve_kw / total_rated_kw) * 100 if total_rated_kw > 0 else 0
        
        active_alarms = self.get_active_alarms()
        critical_alarms = [a for a in active_alarms if a.level == AlarmLevel.CRITICAL]
        
        # 评估 blackout 风险
        if reserve_percent < 10:
            blackout_risk = "high"
        elif reserve_percent < 20:
            blackout_risk = "medium"
        else:
            blackout_risk = "low"
        
        # 生成建议
        recommendations = []
        if reserve_percent < self.config["min_spinning_reserve_percent"]:
            recommendations.append(f"建议启动备用发电机 - 当前旋转备用 {reserve_percent:.1f}%")
        if len(paralleled_gens) == 1:
            recommendations.append("单机运行 - 建议并车第二台发电机以提高可靠性")
        if critical_alarms:
            recommendations.append(f"存在 {len(critical_alarms)} 个危急报警 - 立即处理")
        
        return PowerSystemStatus(
            timestamp=datetime.now(),
            total_generated_kw=total_generated_kw,
            total_load_kw=self.total_load_kw,
            spinning_reserve_kw=spinning_reserve_kw,
            reserve_percent=reserve_percent,
            active_generators=len(paralleled_gens),
            available_generators=len([g for g in self.generators.values() if g.available]),
            bus_state=self.bus_state,
            bus_voltage_v=self.bus_voltage_v,
            bus_frequency_hz=self.bus_frequency_hz,
            system_load_percent=(self.total_load_kw / total_rated_kw * 100) if total_rated_kw > 0 else 0,
            fuel_consumption_total_kg_h=sum(g.fuel_consumption_kg_h for g in paralleled_gens),
            active_alarms=len(active_alarms),
            critical_alarms=len(critical_alarms),
            blackout_risk=blackout_risk,
            recommendations=recommendations,
        )
    
    def run_simulation(self) -> PowerSystemStatus:
        """运行电力系统仿真"""
        import random
        
        # 仿真 3 台发电机
        if not self.generators:
            self.register_generator(Generator(
                generator_id="G1",
                name="主发电机 #1",
                rated_power_kw=1000,
                rated_voltage_v=400,
                rated_frequency_hz=50,
                rated_rpm=1500,
                priority=1,
            ))
            self.register_generator(Generator(
                generator_id="G2",
                name="主发电机 #2",
                rated_power_kw=1000,
                rated_voltage_v=400,
                rated_frequency_hz=50,
                rated_rpm=1500,
                priority=2,
            ))
            self.register_generator(Generator(
                generator_id="G3",
                name="应急发电机",
                rated_power_kw=500,
                rated_voltage_v=400,
                rated_frequency_hz=50,
                rated_rpm=1500,
                priority=1,
            ))
        
        # 启动主发电机
        for gen_id in ["G1", "G2"]:
            gen = self.generators[gen_id]
            if gen.state == GeneratorState.STOPPED:
                self.start_generator(gen_id)
                self.synchronize_generator(gen_id)
        
        # 仿真负载
        total_load = random.uniform(800, 1500)
        self.distribute_load(total_load)
        
        # 设置母线参数
        self.bus_state = BusState.LIVE
        self.bus_voltage_v = 400
        self.bus_frequency_hz = 50
        
        # 更新发电机运行参数
        for gen in self.generators.values():
            if gen.state == GeneratorState.PARALLELED:
                gen.running_hours += 0.1
                gen.fuel_consumption_kg_h = gen.current_power_kw * 0.21  # 简化：210 g/kWh
                gen.cooling_water_temp_c = 75 + random.uniform(-5, 10)
                gen.lube_oil_pressure_bar = 3.5 + random.uniform(-0.3, 0.3)
                gen.exhaust_temp_c = 350 + random.uniform(-30, 50)
        
        # 随机生成报警 (小概率)
        if random.random() < 0.1:
            gen = random.choice(list(self.generators.values()))
            if gen.state == GeneratorState.PARALLELED:
                self.create_alarm(
                    level=AlarmLevel.MEDIUM,
                    category="温度",
                    message=f"{gen.name} 冷却水温度偏高",
                    generator_id=gen.generator_id,
                    parameter="冷却水温度",
                    value=gen.cooling_water_temp_c,
                    threshold=85.0,
                )
        
        return self.get_system_status()
    
    def can_handle(self, url: str) -> bool:
        """检查 URL 是否属于电力管理系统相关。
        
        Power Management Channel 不处理 URL，始终返回 False。
        此方法仅为了满足 Channel 基类的抽象方法要求。
        """
        return False
    
    def call(self, action: str, **kwargs) -> OperationResult:
        """Channel 调用接口"""
        actions = {
            "start_generator": self.start_generator,
            "stop_generator": self.stop_generator,
            "check_synchronization": self.check_synchronization,
            "synchronize_generator": self.synchronize_generator,
            "distribute_load": self.distribute_load,
            "check_spinning_reserve": self.check_spinning_reserve,
            "perform_load_shedding": self.perform_load_shedding,
            "detect_blackout": self.detect_blackout,
            "blackout_recovery": self.blackout_recovery,
            "get_system_status": lambda **kw: OperationResult(
                success=True,
                data=self.get_system_status().__dict__,
                message="电力系统状态查询完成"
            ),
            "run_simulation": lambda **kw: OperationResult(
                success=True,
                data=self.run_simulation().__dict__,
                message="电力系统仿真完成"
            ),
            "get_active_alarms": lambda **kw: OperationResult(
                success=True,
                data=[a.__dict__ for a in self.get_active_alarms()],
                message=f"获取到 {len(self.get_active_alarms())} 个活跃报警"
            ),
            "acknowledge_alarm": self.acknowledge_alarm,
        }
        
        if action not in actions:
            return OperationResult(
                success=False,
                error=f"未知动作：{action}",
                message=f"支持的动作：{list(actions.keys())}"
            )
        
        try:
            result = actions[action](**kwargs)
            return result
        except Exception as e:
            return OperationResult(
                success=False,
                error=str(e),
                message=f"执行 {action} 失败"
            )


# 导出
__all__ = [
    "PowerManagementChannel",
    "Generator",
    "GeneratorState",
    "GeneratorMode",
    "LoadShareMode",
    "BusState",
    "PowerAlarm",
    "AlarmLevel",
    "LoadGroup",
    "PowerSystemStatus",
    "SynchronizationCheck",
]
