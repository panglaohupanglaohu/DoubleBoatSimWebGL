# -*- coding: utf-8 -*-
"""
Engine Monitor Channel — 船舶主机工况监控.

监控船舶主发动机 (Main Engine) 的运行参数，包括温度、压力、转速、燃油消耗等。
提供实时数据采集、趋势分析、异常检测和报警功能。

参考标准:
- IMO MARPOL Annex VI (排放监控)
- ISO 19847/19848 (船载数据交换)
- 船级社规范 (DNV/ABS/LR) 机舱自动化要求
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from .base import Channel


class AlarmLevel(Enum):
    """报警级别定义.

    根据 IMO 和船级社规范，机舱报警分为 4 级:
    - A 级：红色，立即停车 (Shutdown)
    - B 级：橙色，减速运行 (Slow Down)
    - C 级：黄色，持续监控 (Warning)
    - D 级：蓝色，记录备案 (Info)
    """

    SHUTDOWN = "A"  # 红色 - 立即停车
    SLOW_DOWN = "B"  # 橙色 - 减速运行
    WARNING = "C"  # 黄色 - 持续监控
    INFO = "D"  # 蓝色 - 记录备案


@dataclass
class EngineParameter:
    """主机单个参数数据.

    Attributes:
        name: 参数名称 (如 '冷却水温度', '滑油压力').
        value: 当前值.
        unit: 单位 (如 '°C', 'bar', 'rpm').
        timestamp: 数据采集时间戳.
        status: 状态 ('normal', 'warning', 'alarm').
    """

    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "normal"


@dataclass
class EngineAlarm:
    """主机报警记录.

    Attributes:
        alarm_id: 报警唯一标识.
        parameter: 触发报警的参数名称.
        level: 报警级别 (A/B/C/D).
        message: 报警描述信息.
        value: 触发报警时的参数值.
        threshold: 报警阈值.
        timestamp: 报警发生时间.
        acknowledged: 是否已确认.
    """

    alarm_id: str
    parameter: str
    level: AlarmLevel
    message: str
    value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False


@dataclass
class EngineStatus:
    """主机整体状态汇总.

    Attributes:
        engine_id: 主机编号 (如 'ME-1', 'ME-2').
        running: 是否运行中.
        rpm: 当前转速 (rpm).
        load: 负载百分比 (%).
        fuel_consumption: 燃油消耗率 (g/kWh).
        total_alarms: 当前活跃报警数量.
        critical_alarms: 严重报警数量 (A/B 级).
        status_text: 状态描述文本.
        last_updated: 最后更新时间.
    """

    engine_id: str
    running: bool
    rpm: float
    load: float
    fuel_consumption: float
    total_alarms: int
    critical_alarms: int
    status_text: str
    last_updated: datetime = field(default_factory=datetime.now)


class EngineMonitorChannel(Channel):
    """船舶主机工况监控 Channel.

    功能特性:
    - 温度监控：冷却水、滑油、排气、增压空气
    - 压力监控：滑油、燃油、增压空气、启动空气
    - 转速监控：主机 RPM、螺旋桨转速
    - 燃油监控：消耗率、累计消耗
    - 报警管理：分级报警、自动检测、历史追溯
    - 趋势分析：参数趋势、性能评估

    典型应用场景:
    - 机舱自动化系统 (AMS) 集成
    - 远程主机状态监控
    - 预防性维护提醒
    - 燃油效率优化分析

    数据来源:
    - PLC/控制器 (Modbus TCP/RTU)
    - NMEA 2000 网络
    - 船载传感器直接采集
    - 仿真数据 (测试模式)

    示例用法:
        >>> monitor = EngineMonitorChannel(engine_id="ME-1")
        >>> # 更新参数
        >>> monitor.update_parameter("冷却水出口温度", 78.5, "°C")
        >>> monitor.update_parameter("滑油压力", 3.2, "bar")
        >>> # 获取报警
        >>> alarms = monitor.get_active_alarms()
        >>> # 获取状态汇总
        >>> status = monitor.get_engine_status()
        >>> print(f"主机状态：{status.status_text}")
    """

    name = "engine_monitor"
    description = "船舶主机工况监控 (温度/压力/转速/报警)"
    backends = []
    tier = 0  # zero-config, 内置解析器

    def __init__(
        self,
        engine_id: str = "ME-1",
        alarm_enabled: bool = True,
        data_retention_hours: int = 24,
    ):
        """初始化主机监控器.

        Args:
            engine_id: 主机编号标识.
            alarm_enabled: 是否启用报警检测.
            data_retention_hours: 历史数据保留时长 (小时).
        """
        self.engine_id = engine_id
        self.alarm_enabled = alarm_enabled
        self.data_retention_hours = data_retention_hours

        # 参数存储
        self.parameters: dict[str, EngineParameter] = {}

        # 报警存储
        self.alarms: list[EngineAlarm] = []
        self._alarm_counter = 0

        # 报警阈值配置 (默认值，可根据实际主机调整)
        self.thresholds = self._init_thresholds()

        # 运行状态
        self._running = False
        self._last_update: Optional[datetime] = None

    def _init_thresholds(self) -> dict:
        """初始化报警阈值配置.

        返回典型中速柴油机的报警阈值参考值。
        实际使用时应根据主机制造商规格调整。

        Returns:
            包含各参数报警阈值的字典.
        """
        return {
            # 温度参数 (°C)
            "冷却水出口温度": {"warning": 85.0, "alarm": 92.0, "shutdown": 98.0},
            "滑油出口温度": {"warning": 65.0, "alarm": 72.0, "shutdown": 78.0},
            "排气温度": {"warning": 420.0, "alarm": 480.0, "shutdown": 520.0},
            "增压空气温度": {"warning": 55.0, "alarm": 65.0, "shutdown": 75.0},
            "燃油温度": {"warning": 135.0, "alarm": 145.0, "shutdown": 150.0},
            # 压力参数 (bar)
            "滑油压力": {"low_warning": 2.5, "low_alarm": 2.0, "shutdown": 1.5},
            "燃油压力": {"low_warning": 3.0, "low_alarm": 2.5, "shutdown": 2.0},
            "启动空气压力": {"low_warning": 15.0, "low_alarm": 12.0, "shutdown": 10.0},
            "增压空气压力": {"warning": 2.8, "alarm": 3.2, "shutdown": 3.5},
            # 转速参数 (rpm)
            "主机转速": {"overspeed_warning": 115.0, "overspeed_alarm": 120.0},  # % 额定转速
            # 其他参数
            "曲轴箱油雾浓度": {"warning": 30.0, "alarm": 50.0, "shutdown": 100.0},  # mg/L
        }

    def update_parameter(
        self, name: str, value: float, unit: str, timestamp: Optional[datetime] = None
    ) -> EngineParameter:
        """更新主机参数值.

        Args:
            name: 参数名称.
            value: 参数值.
            unit: 单位.
            timestamp: 时间戳 (默认当前时间).

        Returns:
            更新后的参数对象.
        """
        ts = timestamp or datetime.now()

        # 创建参数对象
        param = EngineParameter(
            name=name, value=value, unit=unit, timestamp=ts, status="normal"
        )

        # 检查报警
        if self.alarm_enabled and name in self.thresholds:
            alarm = self._check_alarm(param)
            if alarm:
                param.status = (
                    "alarm"
                    if alarm.level
                    in [AlarmLevel.SHUTDOWN, AlarmLevel.SLOW_DOWN]
                    else "warning"
                )

        # 存储参数
        self.parameters[name] = param
        self._last_update = ts

        return param

    def _check_alarm(self, param: EngineParameter) -> Optional[EngineAlarm]:
        """检查参数是否触发报警.

        Args:
            param: 待检查的参数对象.

        Returns:
            如果触发报警则返回 EngineAlarm 对象，否则返回 None.
        """
        thresholds = self.thresholds.get(param.name, {})

        # 温度类参数 (只检查高报警)
        if "温度" in param.name or param.name in ["排气温度", "冷却水出口温度", "滑油出口温度"]:
            if "shutdown" in thresholds and param.value >= thresholds["shutdown"]:
                return self._create_alarm(
                    param, AlarmLevel.SHUTDOWN, "过高 (停车阈值)"
                )
            if "alarm" in thresholds and param.value >= thresholds["alarm"]:
                return self._create_alarm(param, AlarmLevel.SLOW_DOWN, "过高 (减速阈值)")
            if "warning" in thresholds and param.value >= thresholds["warning"]:
                return self._create_alarm(param, AlarmLevel.WARNING, "过高 (警告)")

        # 压力类参数 (只检查低报警)
        elif "压力" in param.name or param.name in ["滑油压力", "燃油压力", "启动空气压力", "增压空气压力"]:
            if "shutdown" in thresholds and param.value <= thresholds["shutdown"]:
                return self._create_alarm(
                    param, AlarmLevel.SHUTDOWN, "过低 (停车阈值)"
                )
            if "low_alarm" in thresholds and param.value <= thresholds["low_alarm"]:
                return self._create_alarm(param, AlarmLevel.SLOW_DOWN, "过低 (减速阈值)")
            if "low_warning" in thresholds and param.value <= thresholds["low_warning"]:
                return self._create_alarm(param, AlarmLevel.WARNING, "过低 (警告)")

        # 转速类参数 (检查超速)
        elif "转速" in param.name or param.name == "主机转速":
            if "overspeed_alarm" in thresholds and param.value >= thresholds[
                "overspeed_alarm"
            ]:
                return self._create_alarm(param, AlarmLevel.SLOW_DOWN, "超速 (减速)")
            if "overspeed_warning" in thresholds and param.value >= thresholds[
                "overspeed_warning"
            ]:
                return self._create_alarm(param, AlarmLevel.WARNING, "超速 (警告)")

        # 其他参数 (默认检查高报警)
        else:
            if "shutdown" in thresholds and param.value >= thresholds["shutdown"]:
                return self._create_alarm(
                    param, AlarmLevel.SHUTDOWN, "过高 (停车阈值)"
                )
            if "alarm" in thresholds and param.value >= thresholds["alarm"]:
                return self._create_alarm(param, AlarmLevel.SLOW_DOWN, "过高 (减速阈值)")
            if "warning" in thresholds and param.value >= thresholds["warning"]:
                return self._create_alarm(param, AlarmLevel.WARNING, "过高 (警告)")

        return None

    def _create_alarm(
        self, param: EngineParameter, level: AlarmLevel, reason: str
    ) -> EngineAlarm:
        """创建报警记录.

        Args:
            param: 触发报警的参数.
            level: 报警级别.
            reason: 报警原因描述.

        Returns:
            EngineAlarm 对象.
        """
        self._alarm_counter += 1
        alarm_id = f"{self.engine_id}-ALM-{self._alarm_counter:04d}"

        alarm = EngineAlarm(
            alarm_id=alarm_id,
            parameter=param.name,
            level=level,
            message=f"{param.name} {reason}: {param.value}{param.unit}",
            value=param.value,
            threshold=self.thresholds[param.name].get(
                "shutdown"
                if level == AlarmLevel.SHUTDOWN
                else "alarm" if level == AlarmLevel.SLOW_DOWN else "warning",
                0,
            ),
            timestamp=param.timestamp,
            acknowledged=False,
        )

        self.alarms.append(alarm)
        return alarm

    def get_active_alarms(
        self, include_acknowledged: bool = False
    ) -> list[EngineAlarm]:
        """获取当前活跃报警.

        Args:
            include_acknowledged: 是否包含已确认的报警.

        Returns:
            活跃报警列表，按级别排序 (A 级优先).
        """
        active = [
            alm for alm in self.alarms if include_acknowledged or not alm.acknowledged
        ]

        # 按级别排序 (SHUTDOWN > SLOW_DOWN > WARNING > INFO)
        level_order = {
            AlarmLevel.SHUTDOWN: 0,
            AlarmLevel.SLOW_DOWN: 1,
            AlarmLevel.WARNING: 2,
            AlarmLevel.INFO: 3,
        }

        return sorted(active, key=lambda x: level_order[x.level])

    def acknowledge_alarm(self, alarm_id: str) -> bool:
        """确认报警.

        Args:
            alarm_id: 报警 ID.

        Returns:
            是否成功确认.
        """
        for alarm in self.alarms:
            if alarm.alarm_id == alarm_id:
                alarm.acknowledged = True
                return True
        return False

    def get_engine_status(self) -> EngineStatus:
        """获取主机状态汇总.

        Returns:
            EngineStatus 对象.
        """
        # 统计报警
        active_alarms = self.get_active_alarms()
        critical = sum(
            1 for alm in active_alarms if alm.level in [AlarmLevel.SHUTDOWN, AlarmLevel.SLOW_DOWN]
        )

        # 提取关键参数
        rpm = self.parameters.get("主机转速", EngineParameter("主机转速", 0, "rpm")).value
        load = self.parameters.get("负载百分比", EngineParameter("负载百分比", 0, "%")).value
        fuel = self.parameters.get(
            "燃油消耗率", EngineParameter("燃油消耗率", 0, "g/kWh")
        ).value

        # 判断运行状态
        self._running = rpm > 10  # 假设转速>10rpm 视为运行中

        # 生成状态文本
        if critical > 0:
            status_text = f"⚠️ 严重报警 ({critical}个)"
        elif len(active_alarms) > 0:
            status_text = f"⚡ 警告 ({len(active_alarms)}个)"
        elif self._running:
            status_text = "🟢 正常运行"
        else:
            status_text = "🔵 停机状态"

        return EngineStatus(
            engine_id=self.engine_id,
            running=self._running,
            rpm=rpm,
            load=load,
            fuel_consumption=fuel,
            total_alarms=len(active_alarms),
            critical_alarms=critical,
            status_text=status_text,
            last_updated=self._last_update or datetime.now(),
        )

    def get_trend_data(
        self, parameter_name: str, hours: int = 24
    ) -> list[EngineParameter]:
        """获取参数趋势数据.

        Args:
            parameter_name: 参数名称.
            hours: 时间范围 (小时).

        Returns:
            参数历史数据列表，按时间排序.
        """
        # 实际实现应从数据库查询历史数据
        # 这里仅返回当前值作为示例
        if parameter_name in self.parameters:
            return [self.parameters[parameter_name]]
        return []

    def simulate_data(self) -> dict[str, float]:
        """生成仿真数据 (用于测试).

        Returns:
            包含各参数仿真值的字典.
        """
        import random

        base_rpm = 120  # 额定转速
        load_factor = random.uniform(0.6, 0.9)  # 负载因子

        return {
            "主机转速": base_rpm * load_factor,
            "负载百分比": load_factor * 100,
            "冷却水出口温度": 75 + random.uniform(0, 15),
            "滑油出口温度": 55 + random.uniform(0, 12),
            "排气温度": 350 + random.uniform(0, 80),
            "滑油压力": 3.5 + random.uniform(-0.5, 0.5),
            "燃油压力": 4.0 + random.uniform(-0.3, 0.3),
            "增压空气压力": 2.2 + random.uniform(0, 0.5),
            "燃油消耗率": 180 + random.uniform(-10, 20),
        }

    def run_simulation(self) -> EngineStatus:
        """运行仿真数据更新.

        Returns:
            更新后的主机状态.
        """
        data = self.simulate_data()

        for name, value in data.items():
            unit = (
                "rpm"
                if name == "主机转速"
                else "%"
                if name == "负载百分比"
                else "°C"
                if "温度" in name
                else "bar"
                if "压力" in name
                else "g/kWh"
            )
            self.update_parameter(name, value, unit)

        return self.get_engine_status()

    def can_handle(self, url: str) -> bool:
        """Check if this channel can handle the given URL.

        Engine monitor doesn't process URLs, always returns False.

        Args:
            url: URL to check.

        Returns:
            False (this channel doesn't handle URLs).
        """
        return False
