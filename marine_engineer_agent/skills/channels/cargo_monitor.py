#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cargo Monitor Channel - 货物状态监控 Channel

监控船舶货物状态，包括：
- 冷藏集装箱温度/湿度监控
- 液货舱液位监控
- 货舱压力监控
- 货物移位检测
- 通风控制

适用于：
- 集装箱船 (冷藏箱监控)
- 油轮/化学品船 (液货舱监控)
- 散货船 (货舱状态监控)
- 气体运输船 (LNG/LPG 温度压力监控)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math
import logging

from .base import Channel

logger = logging.getLogger(__name__)


class CargoType(Enum):
    """货物类型枚举."""
    REEFER_CONTAINER = "reefer_container"  # 冷藏集装箱
    LIQUID_BULK = "liquid_bulk"  # 液体散货 (油/化学品)
    DRY_BULK = "dry_bulk"  # 干散货
    GAS_CARGO = "gas_cargo"  # 气体货物 (LNG/LPG)
    GENERAL_CARGO = "general_cargo"  # 普通货物


class AlarmLevel(Enum):
    """报警级别."""
    NORMAL = "normal"  # 正常
    WARNING = "warning"  # 警告
    CRITICAL = "critical"  # 危险
    EMERGENCY = "emergency"  # 紧急


@dataclass
class TemperatureReading:
    """温度读数."""
    value_c: float  # 温度值 (°C)
    timestamp: datetime
    sensor_id: str
    location: str  # 位置描述
    
    def is_frozen(self) -> bool:
        """检查是否冻结."""
        return self.value_c <= 0.0
    
    def to_fahrenheit(self) -> float:
        """转换为华氏度."""
        return (self.value_c * 9/5) + 32


@dataclass
class HumidityReading:
    """湿度读数."""
    value_percent: float  # 相对湿度 (%)
    timestamp: datetime
    sensor_id: str
    location: str
    
    def is_high(self, threshold: float = 80.0) -> bool:
        """检查是否高湿度."""
        return self.value_percent >= threshold
    
    def is_low(self, threshold: float = 30.0) -> bool:
        """检查是否低湿度."""
        return self.value_percent <= threshold


@dataclass
class LevelReading:
    """液位读数."""
    value_m: float  # 液位高度 (米)
    value_percent: float  # 液位百分比 (0-100%)
    timestamp: datetime
    tank_id: str
    tank_name: str
    
    def volume_m3(self, tank_capacity_m3: float) -> float:
        """计算体积 (立方米)."""
        return tank_capacity_m3 * (self.value_percent / 100.0)


@dataclass
class PressureReading:
    """压力读数."""
    value_bar: float  # 压力值 (bar)
    timestamp: datetime
    sensor_id: str
    location: str
    
    def to_psi(self) -> float:
        """转换为 PSI."""
        return self.value_bar * 14.5038
    
    def to_kpa(self) -> float:
        """转换为千帕."""
        return self.value_bar * 100.0


@dataclass
class CargoAlarm:
    """货物报警."""
    alarm_id: str
    level: AlarmLevel
    cargo_type: CargoType
    location: str
    parameter: str  # 参数类型 (temperature/humidity/level/pressure)
    message: str
    timestamp: datetime
    value: float
    threshold: float
    acknowledged: bool = False
    
    def to_dict(self) -> Dict:
        """转换为字典."""
        return {
            "alarm_id": self.alarm_id,
            "level": self.level.value,
            "cargo_type": self.cargo_type.value,
            "location": self.location,
            "parameter": self.parameter,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "threshold": self.threshold,
            "acknowledged": self.acknowledged
        }


@dataclass
class ReeferContainer:
    """冷藏集装箱."""
    container_id: str
    setpoint_c: float  # 设定温度
    current_temp_c: float  # 当前温度
    humidity_percent: float  # 湿度
    co2_percent: float  # CO2 浓度 (气调冷藏)
    o2_percent: float  # O2 浓度
    status: str  # running/stopped/alarm
    alarm_code: Optional[str] = None
    
    def temperature_deviation(self) -> float:
        """计算温度偏差."""
        return self.current_temp_c - self.setpoint_c
    
    def is_within_range(self, tolerance_c: float = 0.5) -> bool:
        """检查温度是否在容差范围内."""
        return abs(self.temperature_deviation()) <= tolerance_c


@dataclass
class CargoTank:
    """货物舱/ tank."""
    tank_id: str
    tank_name: str
    cargo_type: CargoType
    capacity_m3: float  # 容量 (立方米)
    current_level_m: float  # 当前液位
    current_level_percent: float  # 当前液位百分比
    temperature_c: float  # 货物温度
    pressure_bar: float  # 舱内压力
    ullage_m: float  # 空档高度
    
    def volume_m3(self) -> float:
        """计算当前体积."""
        return self.capacity_m3 * (self.current_level_percent / 100.0)
    
    def remaining_capacity_m3(self) -> float:
        """计算剩余容量."""
        return self.capacity_m3 - self.volume_m3()
    
    def is_nearly_full(self, threshold_percent: float = 95.0) -> bool:
        """检查是否接近满载."""
        return self.current_level_percent >= threshold_percent
    
    def is_nearly_empty(self, threshold_percent: float = 5.0) -> bool:
        """检查是否接近空舱."""
        return self.current_level_percent <= threshold_percent


@dataclass
class VentilationStatus:
    """通风状态."""
    cargo_hold_id: str
    fan_running: bool
    ventilation_rate_m3h: float  # 通风量 (m³/h)
    inlet_temp_c: float  # 进气温度
    outlet_temp_c: float  # 排气温度
    inlet_humidity_percent: float  # 进气湿度
    outlet_humidity_percent: float  # 排气湿度
    dew_point_c: float  # 露点温度
    
    def should_ventilate(self) -> bool:
        """判断是否需要通风."""
        # 如果舱内湿度高于外界，应通风
        return self.outlet_humidity_percent > self.inlet_humidity_percent
    
    def condensation_risk(self) -> bool:
        """检查结露风险."""
        # 如果舱壁温度低于露点，有结露风险
        return self.inlet_temp_c < self.dew_point_c


class CargoMonitorChannel(Channel):
    """
    货物状态监控 Channel.
    
    功能:
    - 冷藏集装箱温度/湿度监控
    - 液货舱液位监控
    - 货舱压力监控
    - 货物移位检测
    - 通风控制建议
    - 多级报警管理
    """
    
    name = "cargo_monitor"
    description = "货物状态监控 (冷藏箱/液货舱)"
    
    def __init__(self):
        """初始化货物监控 Channel."""
        self._reefer_containers: Dict[str, ReeferContainer] = {}
        self._cargo_tanks: Dict[str, CargoTank] = {}
        self._ventilation_status: Dict[str, VentilationStatus] = {}
        self._alarms: List[CargoAlarm] = []
        self._alarm_counter = 0
        
        # 默认报警阈值
        self._temp_warning_deviation = 2.0  # 温度警告偏差 (°C)
        self._temp_critical_deviation = 5.0  # 温度危险偏差 (°C)
        self._humidity_warning_high = 85.0  # 高湿度警告 (%)
        self._humidity_warning_low = 25.0  # 低湿度警告 (%)
        self._level_warning_high = 90.0  # 高液位警告 (%)
        self._level_critical_high = 95.0  # 高液位危险 (%)
        self._pressure_warning_high = 0.5  # 高压警告 (bar)
        self._pressure_critical_high = 1.0  # 高压危险 (bar)
        
        logger.info("CargoMonitorChannel initialized")
    
    def can_handle(self, url: str) -> bool:
        """Check if this channel can handle the given URL.
        
        Cargo monitor channel handles cargo-related data URLs.
        
        Args:
            url: URL to check.
            
        Returns:
            True if this channel can process the URL.
        """
        # Cargo monitor doesn't handle URLs directly, returns False
        return False
    
    # ==================== 冷藏集装箱管理 ====================
    
    def register_reefer_container(
        self,
        container_id: str,
        setpoint_c: float,
        current_temp_c: float,
        humidity_percent: float,
        co2_percent: float = 0.0,
        o2_percent: float = 21.0,
        status: str = "running"
    ) -> ReeferContainer:
        """
        注册冷藏集装箱.
        
        Args:
            container_id: 集装箱编号
            setpoint_c: 设定温度 (°C)
            current_temp_c: 当前温度 (°C)
            humidity_percent: 湿度 (%)
            co2_percent: CO2 浓度 (%)
            o2_percent: O2 浓度 (%)
            status: 运行状态
            
        Returns:
            ReeferContainer 对象
        """
        container = ReeferContainer(
            container_id=container_id,
            setpoint_c=setpoint_c,
            current_temp_c=current_temp_c,
            humidity_percent=humidity_percent,
            co2_percent=co2_percent,
            o2_percent=o2_percent,
            status=status
        )
        self._reefer_containers[container_id] = container
        logger.info(f"Registered reefer container {container_id}")
        
        # 检查初始状态
        self._check_reefer_temperature(container)
        self._check_reefer_humidity(container)
        
        return container
    
    def update_reefer_temperature(
        self,
        container_id: str,
        temperature_c: float
    ) -> Optional[ReeferContainer]:
        """
        更新冷藏箱温度.
        
        Args:
            container_id: 集装箱编号
            temperature_c: 新温度值
            
        Returns:
            更新后的 ReeferContainer，如果不存在则返回 None
        """
        container = self._reefer_containers.get(container_id)
        if not container:
            logger.warning(f"Reefer container {container_id} not found")
            return None
        
        container.current_temp_c = temperature_c
        self._check_reefer_temperature(container)
        
        return container
    
    def update_reefer_humidity(
        self,
        container_id: str,
        humidity_percent: float
    ) -> Optional[ReeferContainer]:
        """
        更新冷藏箱湿度.
        
        Args:
            container_id: 集装箱编号
            humidity_percent: 新湿度值
            
        Returns:
            更新后的 ReeferContainer，如果不存在则返回 None
        """
        container = self._reefer_containers.get(container_id)
        if not container:
            logger.warning(f"Reefer container {container_id} not found")
            return None
        
        container.humidity_percent = humidity_percent
        self._check_reefer_humidity(container)
        
        return container
    
    def get_reefer_container(self, container_id: str) -> Optional[ReeferContainer]:
        """获取冷藏集装箱信息."""
        return self._reefer_containers.get(container_id)
    
    def get_all_reefers(self) -> Dict[str, ReeferContainer]:
        """获取所有冷藏集装箱."""
        return self._reefer_containers.copy()
    
    def _check_reefer_temperature(self, container: ReeferContainer) -> None:
        """检查冷藏箱温度并生成报警."""
        deviation = container.temperature_deviation()
        
        if abs(deviation) >= self._temp_critical_deviation:
            self._add_alarm(
                level=AlarmLevel.CRITICAL,
                cargo_type=CargoType.REEFER_CONTAINER,
                location=container.container_id,
                parameter="temperature",
                message=f"冷藏箱温度严重偏差：{deviation:+.1f}°C",
                value=container.current_temp_c,
                threshold=container.setpoint_c
            )
        elif abs(deviation) >= self._temp_warning_deviation:
            self._add_alarm(
                level=AlarmLevel.WARNING,
                cargo_type=CargoType.REEFER_CONTAINER,
                location=container.container_id,
                parameter="temperature",
                message=f"冷藏箱温度偏差：{deviation:+.1f}°C",
                value=container.current_temp_c,
                threshold=container.setpoint_c
            )
    
    def _check_reefer_humidity(self, container: ReeferContainer) -> None:
        """检查冷藏箱湿度并生成报警."""
        if container.humidity_percent >= self._humidity_warning_high:
            self._add_alarm(
                level=AlarmLevel.WARNING,
                cargo_type=CargoType.REEFER_CONTAINER,
                location=container.container_id,
                parameter="humidity",
                message=f"冷藏箱湿度过高：{container.humidity_percent:.1f}%",
                value=container.humidity_percent,
                threshold=self._humidity_warning_high
            )
        elif container.humidity_percent <= self._humidity_warning_low:
            self._add_alarm(
                level=AlarmLevel.WARNING,
                cargo_type=CargoType.REEFER_CONTAINER,
                location=container.container_id,
                parameter="humidity",
                message=f"冷藏箱湿度过低：{container.humidity_percent:.1f}%",
                value=container.humidity_percent,
                threshold=self._humidity_warning_low
            )
    
    # ==================== 液货舱管理 ====================
    
    def register_cargo_tank(
        self,
        tank_id: str,
        tank_name: str,
        cargo_type: CargoType,
        capacity_m3: float,
        current_level_m: float = 0.0,
        current_level_percent: float = 0.0,
        temperature_c: float = 20.0,
        pressure_bar: float = 0.0
    ) -> CargoTank:
        """
        注册液货舱.
        
        Args:
            tank_id: 舱室 ID
            tank_name: 舱室名称
            cargo_type: 货物类型
            capacity_m3: 容量 (m³)
            current_level_m: 当前液位 (m)
            current_level_percent: 当前液位百分比
            temperature_c: 货物温度
            pressure_bar: 舱内压力
            
        Returns:
            CargoTank 对象
        """
        ullage_m = self._calculate_ullage(current_level_m, capacity_m3)
        
        tank = CargoTank(
            tank_id=tank_id,
            tank_name=tank_name,
            cargo_type=cargo_type,
            capacity_m3=capacity_m3,
            current_level_m=current_level_m,
            current_level_percent=current_level_percent,
            temperature_c=temperature_c,
            pressure_bar=pressure_bar,
            ullage_m=ullage_m
        )
        self._cargo_tanks[tank_id] = tank
        logger.info(f"Registered cargo tank {tank_name} ({tank_id})")
        
        # 检查初始状态
        self._check_tank_level(tank)
        self._check_tank_pressure(tank)
        
        return tank
    
    def update_tank_level(
        self,
        tank_id: str,
        level_m: float,
        level_percent: float
    ) -> Optional[CargoTank]:
        """
        更新液货舱液位.
        
        Args:
            tank_id: 舱室 ID
            level_m: 新液位 (m)
            level_percent: 新液位百分比
            
        Returns:
            更新后的 CargoTank，如果不存在则返回 None
        """
        tank = self._cargo_tanks.get(tank_id)
        if not tank:
            logger.warning(f"Cargo tank {tank_id} not found")
            return None
        
        tank.current_level_m = level_m
        tank.current_level_percent = level_percent
        tank.ullage_m = self._calculate_ullage(level_m, tank.capacity_m3)
        
        self._check_tank_level(tank)
        
        return tank
    
    def update_tank_pressure(
        self,
        tank_id: str,
        pressure_bar: float
    ) -> Optional[CargoTank]:
        """
        更新液货舱压力.
        
        Args:
            tank_id: 舱室 ID
            pressure_bar: 新压力值 (bar)
            
        Returns:
            更新后的 CargoTank，如果不存在则返回 None
        """
        tank = self._cargo_tanks.get(tank_id)
        if not tank:
            logger.warning(f"Cargo tank {tank_id} not found")
            return None
        
        tank.pressure_bar = pressure_bar
        self._check_tank_pressure(tank)
        
        return tank
    
    def update_tank_temperature(
        self,
        tank_id: str,
        temperature_c: float
    ) -> Optional[CargoTank]:
        """
        更新液货舱温度.
        
        Args:
            tank_id: 舱室 ID
            temperature_c: 新温度值 (°C)
            
        Returns:
            更新后的 CargoTank，如果不存在则返回 None
        """
        tank = self._cargo_tanks.get(tank_id)
        if not tank:
            logger.warning(f"Cargo tank {tank_id} not found")
            return None
        
        tank.temperature_c = temperature_c
        return tank
    
    def get_cargo_tank(self, tank_id: str) -> Optional[CargoTank]:
        """获取液货舱信息."""
        return self._cargo_tanks.get(tank_id)
    
    def get_all_tanks(self) -> Dict[str, CargoTank]:
        """获取所有液货舱."""
        return self._cargo_tanks.copy()
    
    def get_total_cargo_volume(self) -> float:
        """计算总货物体积 (m³)."""
        return sum(tank.volume_m3() for tank in self._cargo_tanks.values())
    
    def get_total_remaining_capacity(self) -> float:
        """计算总剩余容量 (m³)."""
        return sum(tank.remaining_capacity_m3() for tank in self._cargo_tanks.values())
    
    def _calculate_ullage(self, level_m: float, capacity_m3: float) -> float:
        """计算空档高度."""
        # 简化计算：假设 tank 为规则形状
        if capacity_m3 <= 0:
            return 0.0
        # 这里应该根据 tank 的实际几何形状计算
        # 简化处理：假设高度与体积成正比
        max_height = math.pow(capacity_m3, 1/3)  # 估算最大高度
        return max(0.0, max_height - level_m)
    
    def _check_tank_level(self, tank: CargoTank) -> None:
        """检查液货舱液位并生成报警."""
        if tank.current_level_percent >= self._level_critical_high:
            self._add_alarm(
                level=AlarmLevel.CRITICAL,
                cargo_type=tank.cargo_type,
                location=tank.tank_name,
                parameter="level",
                message=f"液货舱液位过高：{tank.current_level_percent:.1f}%",
                value=tank.current_level_percent,
                threshold=self._level_critical_high
            )
        elif tank.current_level_percent >= self._level_warning_high:
            self._add_alarm(
                level=AlarmLevel.WARNING,
                cargo_type=tank.cargo_type,
                location=tank.tank_name,
                parameter="level",
                message=f"液货舱液位警告：{tank.current_level_percent:.1f}%",
                value=tank.current_level_percent,
                threshold=self._level_warning_high
            )
    
    def _check_tank_pressure(self, tank: CargoTank) -> None:
        """检查液货舱压力并生成报警."""
        if tank.pressure_bar >= self._pressure_critical_high:
            self._add_alarm(
                level=AlarmLevel.EMERGENCY,
                cargo_type=tank.cargo_type,
                location=tank.tank_name,
                parameter="pressure",
                message=f"液货舱压力危险：{tank.pressure_bar:.2f} bar",
                value=tank.pressure_bar,
                threshold=self._pressure_critical_high
            )
        elif tank.pressure_bar >= self._pressure_warning_high:
            self._add_alarm(
                level=AlarmLevel.WARNING,
                cargo_type=tank.cargo_type,
                location=tank.tank_name,
                parameter="pressure",
                message=f"液货舱压力警告：{tank.pressure_bar:.2f} bar",
                value=tank.pressure_bar,
                threshold=self._pressure_warning_high
            )
    
    # ==================== 通风管理 ====================
    
    def register_ventilation(
        self,
        cargo_hold_id: str,
        fan_running: bool,
        ventilation_rate_m3h: float,
        inlet_temp_c: float,
        outlet_temp_c: float,
        inlet_humidity_percent: float,
        outlet_humidity_percent: float,
        dew_point_c: float
    ) -> VentilationStatus:
        """
        注册货舱通风状态.
        
        Args:
            cargo_hold_id: 货舱 ID
            fan_running: 风机是否运行
            ventilation_rate_m3h: 通风量 (m³/h)
            inlet_temp_c: 进气温度
            outlet_temp_c: 排气温度
            inlet_humidity_percent: 进气湿度
            outlet_humidity_percent: 排气湿度
            dew_point_c: 露点温度
            
        Returns:
            VentilationStatus 对象
        """
        status = VentilationStatus(
            cargo_hold_id=cargo_hold_id,
            fan_running=fan_running,
            ventilation_rate_m3h=ventilation_rate_m3h,
            inlet_temp_c=inlet_temp_c,
            outlet_temp_c=outlet_temp_c,
            inlet_humidity_percent=inlet_humidity_percent,
            outlet_humidity_percent=outlet_humidity_percent,
            dew_point_c=dew_point_c
        )
        self._ventilation_status[cargo_hold_id] = status
        logger.info(f"Registered ventilation for cargo hold {cargo_hold_id}")
        
        return status
    
    def get_ventilation_recommendation(self, cargo_hold_id: str) -> Dict:
        """
        获取通风建议.
        
        Args:
            cargo_hold_id: 货舱 ID
            
        Returns:
            通风建议字典
        """
        status = self._ventilation_status.get(cargo_hold_id)
        if not status:
            return {"error": "Cargo hold not found"}
        
        recommendation = {
            "cargo_hold_id": cargo_hold_id,
            "current_fan_status": "running" if status.fan_running else "stopped",
            "should_ventilate": status.should_ventilate(),
            "condensation_risk": status.condensation_risk(),
            "recommendation": ""
        }
        
        if status.condensation_risk():
            recommendation["recommendation"] = "停止通风 - 存在结露风险"
            recommendation["action"] = "stop_fan"
        elif status.should_ventilate():
            recommendation["recommendation"] = "启动通风 - 降低舱内湿度"
            recommendation["action"] = "start_fan"
        else:
            recommendation["recommendation"] = "保持当前状态"
            recommendation["action"] = "maintain"
        
        return recommendation
    
    # ==================== 报警管理 ====================
    
    def _add_alarm(
        self,
        level: AlarmLevel,
        cargo_type: CargoType,
        location: str,
        parameter: str,
        message: str,
        value: float,
        threshold: float
    ) -> CargoAlarm:
        """添加报警."""
        self._alarm_counter += 1
        alarm = CargoAlarm(
            alarm_id=f"CARGO_{self._alarm_counter:04d}",
            level=level,
            cargo_type=cargo_type,
            location=location,
            parameter=parameter,
            message=message,
            timestamp=datetime.now(),
            value=value,
            threshold=threshold
        )
        self._alarms.append(alarm)
        logger.warning(f"Alarm {alarm.alarm_id}: {message}")
        return alarm
    
    def get_alarms(
        self,
        level: Optional[AlarmLevel] = None,
        acknowledged: Optional[bool] = None
    ) -> List[CargoAlarm]:
        """
        获取报警列表.
        
        Args:
            level: 按级别筛选
            acknowledged: 按确认状态筛选
            
        Returns:
            报警列表
        """
        alarms = self._alarms.copy()
        
        if level is not None:
            alarms = [a for a in alarms if a.level == level]
        
        if acknowledged is not None:
            alarms = [a for a in alarms if a.acknowledged == acknowledged]
        
        return alarms
    
    def acknowledge_alarm(self, alarm_id: str) -> bool:
        """
        确认报警.
        
        Args:
            alarm_id: 报警 ID
            
        Returns:
            是否成功确认
        """
        for alarm in self._alarms:
            if alarm.alarm_id == alarm_id:
                alarm.acknowledged = True
                logger.info(f"Acknowledged alarm {alarm_id}")
                return True
        return False
    
    def get_active_alarms(self) -> List[CargoAlarm]:
        """获取未确认的报警."""
        return [a for a in self._alarms if not a.acknowledged]
    
    def clear_alarms(self) -> int:
        """清除所有已确认的报警."""
        initial_count = len(self._alarms)
        self._alarms = [a for a in self._alarms if not a.acknowledged]
        cleared_count = initial_count - len(self._alarms)
        logger.info(f"Cleared {cleared_count} acknowledged alarms")
        return cleared_count
    
    # ==================== 配置管理 ====================
    
    def configure_thresholds(
        self,
        temp_warning_deviation: Optional[float] = None,
        temp_critical_deviation: Optional[float] = None,
        humidity_warning_high: Optional[float] = None,
        humidity_warning_low: Optional[float] = None,
        level_warning_high: Optional[float] = None,
        level_critical_high: Optional[float] = None,
        pressure_warning_high: Optional[float] = None,
        pressure_critical_high: Optional[float] = None
    ) -> None:
        """
        配置报警阈值.
        
        Args:
            temp_warning_deviation: 温度警告偏差 (°C)
            temp_critical_deviation: 温度危险偏差 (°C)
            humidity_warning_high: 高湿度警告 (%)
            humidity_warning_low: 低湿度警告 (%)
            level_warning_high: 高液位警告 (%)
            level_critical_high: 高液位危险 (%)
            pressure_warning_high: 高压警告 (bar)
            pressure_critical_high: 高压危险 (bar)
        """
        if temp_warning_deviation is not None:
            self._temp_warning_deviation = temp_warning_deviation
        if temp_critical_deviation is not None:
            self._temp_critical_deviation = temp_critical_deviation
        if humidity_warning_high is not None:
            self._humidity_warning_high = humidity_warning_high
        if humidity_warning_low is not None:
            self._humidity_warning_low = humidity_warning_low
        if level_warning_high is not None:
            self._level_warning_high = level_warning_high
        if level_critical_high is not None:
            self._level_critical_high = level_critical_high
        if pressure_warning_high is not None:
            self._pressure_warning_high = pressure_warning_high
        if pressure_critical_high is not None:
            self._pressure_critical_high = pressure_critical_high
        
        logger.info("Updated cargo monitor thresholds")
    
    # ==================== 状态报告 ====================
    
    def get_status_report(self) -> Dict:
        """
        获取货物状态报告.
        
        Returns:
            状态报告字典
        """
        reefer_status = []
        for container in self._reefer_containers.values():
            reefer_status.append({
                "container_id": container.container_id,
                "setpoint_c": container.setpoint_c,
                "current_temp_c": container.current_temp_c,
                "deviation_c": container.temperature_deviation(),
                "humidity_percent": container.humidity_percent,
                "status": container.status,
                "alarm_code": container.alarm_code,
                "within_range": container.is_within_range()
            })
        
        tank_status = []
        for tank in self._cargo_tanks.values():
            tank_status.append({
                "tank_id": tank.tank_id,
                "tank_name": tank.tank_name,
                "cargo_type": tank.cargo_type.value,
                "capacity_m3": tank.capacity_m3,
                "current_volume_m3": tank.volume_m3(),
                "level_percent": tank.current_level_percent,
                "temperature_c": tank.temperature_c,
                "pressure_bar": tank.pressure_bar,
                "nearly_full": tank.is_nearly_full(),
                "nearly_empty": tank.is_nearly_empty()
            })
        
        active_alarms = self.get_active_alarms()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "reefer_containers": {
                "count": len(self._reefer_containers),
                "status": reefer_status
            },
            "cargo_tanks": {
                "count": len(self._cargo_tanks),
                "total_volume_m3": self.get_total_cargo_volume(),
                "total_remaining_capacity_m3": self.get_total_remaining_capacity(),
                "status": tank_status
            },
            "ventilation": {
                "count": len(self._ventilation_status)
            },
            "alarms": {
                "total": len(self._alarms),
                "active": len(active_alarms),
                "critical": len([a for a in active_alarms if a.level == AlarmLevel.CRITICAL]),
                "emergency": len([a for a in active_alarms if a.level == AlarmLevel.EMERGENCY])
            }
        }
    
    def simulate_cargo_data(self) -> Dict:
        """
        生成仿真货物数据 (用于测试).
        
        Returns:
            仿真数据字典
        """
        import random
        
        # 生成冷藏箱数据
        container_id = f"MSKU{random.randint(100000, 999999)}"
        setpoint = random.choice([-20, -18, -5, 0, 2, 5, 10, 15])
        current_temp = setpoint + random.uniform(-1.5, 1.5)
        
        self.register_reefer_container(
            container_id=container_id,
            setpoint_c=setpoint,
            current_temp_c=current_temp,
            humidity_percent=random.uniform(40, 70),
            status="running"
        )
        
        # 生成液货舱数据
        tank_id = f"TANK_{random.randint(1, 10)}"
        capacity = random.choice([5000, 10000, 15000, 20000])
        level_percent = random.uniform(30, 85)
        
        self.register_cargo_tank(
            tank_id=tank_id,
            tank_name=f"Cargo Tank {tank_id}",
            cargo_type=CargoType.LIQUID_BULK,
            capacity_m3=capacity,
            current_level_percent=level_percent,
            current_level_m=level_percent / 100 * math.pow(capacity, 1/3),
            temperature_c=random.uniform(15, 35),
            pressure_bar=random.uniform(0, 0.3)
        )
        
        return self.get_status_report()


# ==================== 示例用法 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🚢 Cargo Monitor Channel - 货物状态监控演示")
    print("=" * 60)
    
    # 初始化监控
    monitor = CargoMonitorChannel()
    
    # 注册冷藏集装箱
    print("\n📦 注册冷藏集装箱")
    monitor.register_reefer_container(
        container_id="MSKU123456",
        setpoint_c=-18.0,
        current_temp_c=-17.5,
        humidity_percent=55.0,
        status="running"
    )
    
    monitor.register_reefer_container(
        container_id="TRLU789012",
        setpoint_c=2.0,
        current_temp_c=4.5,  # 温度偏差
        humidity_percent=88.0,  # 高湿度
        status="running"
    )
    
    # 注册液货舱
    print("\n🛢️ 注册液货舱")
    monitor.register_cargo_tank(
        tank_id="TANK_1",
        tank_name="No.1 Cargo Oil Tank",
        cargo_type=CargoType.LIQUID_BULK,
        capacity_m3=10000,
        current_level_m=8.5,
        current_level_percent=85.0,
        temperature_c=25.0,
        pressure_bar=0.2
    )
    
    monitor.register_cargo_tank(
        tank_id="TANK_2",
        tank_name="No.2 Cargo Oil Tank",
        cargo_type=CargoType.LIQUID_BULK,
        capacity_m3=10000,
        current_level_m=9.6,
        current_level_percent=96.0,  # 高液位警告
        temperature_c=28.0,
        pressure_bar=0.8  # 高压警告
    )
    
    # 注册通风状态
    print("\n💨 注册通风状态")
    monitor.register_ventilation(
        cargo_hold_id="HOLD_1",
        fan_running=True,
        ventilation_rate_m3h=5000,
        inlet_temp_c=20.0,
        outlet_temp_c=25.0,
        inlet_humidity_percent=60.0,
        outlet_humidity_percent=75.0,
        dew_point_c=18.0
    )
    
    # 获取通风建议
    print("\n📋 通风建议")
    rec = monitor.get_ventilation_recommendation("HOLD_1")
    print(f"  货舱：{rec['cargo_hold_id']}")
    print(f"  建议：{rec['recommendation']}")
    print(f"  结露风险：{'是' if rec['condensation_risk'] else '否'}")
    
    # 获取状态报告
    print("\n📊 货物状态报告")
    report = monitor.get_status_report()
    print(f"  冷藏箱数量：{report['reefer_containers']['count']}")
    print(f"  液货舱数量：{report['cargo_tanks']['count']}")
    print(f"  总货物体积：{report['cargo_tanks']['total_volume_m3']:.0f} m³")
    print(f"  剩余容量：{report['cargo_tanks']['total_remaining_capacity_m3']:.0f} m³")
    print(f"  活跃报警：{report['alarms']['active']}")
    
    # 获取报警
    print("\n🚨 活跃报警")
    alarms = monitor.get_active_alarms()
    for alarm in alarms:
        print(f"  [{alarm.level.value.upper()}] {alarm.alarm_id}: {alarm.message}")
    
    # 确认报警
    if alarms:
        print("\n✅ 确认报警")
        monitor.acknowledge_alarm(alarms[0].alarm_id)
        print(f"  已确认报警：{alarms[0].alarm_id}")
    
    print("\n" + "=" * 60)
    print("✅ 演示完成")
    print("=" * 60)
