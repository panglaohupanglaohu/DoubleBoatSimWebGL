# -*- coding: utf-8 -*-
"""
Marine Channels Integration - Marine Channels 深度集成.

将 8 个 Marine Channels 接入报警引擎，实现 Channel 数据到 Poseidon 的实时同步，
添加数据质量检查与异常检测，实现 Channel 间联动逻辑。

8 个 Marine Channels:
1. nmea_parser - NMEA 0183 语句解析
2. vessel_ais - AIS 目标追踪
3. engine_monitor - 发动机工况监控
4. power_management - 电力管理系统
5. navigation_data - 导航传感器数据
6. cargo_monitor - 货物监控
7. weather_routing - 气象导航
8. web - 通用网页数据

功能:
- 将 8 个 Channels 接入报警引擎
- 实现 Channel 数据到 Poseidon 的实时同步
- 添加数据质量检查与异常检测
- 实现 Channel 间联动逻辑（如：Engine + Cargo + Weather）

示例用法:
    >>> from .channels_integration import ChannelsIntegration
    >>> from .alarm_engine import AlarmEngine
    >>> from .poseidon_server import PoseidonServer
    >>>
    >>> # 创建核心组件
    >>> integration = ChannelsIntegration()
    >>> alarm_engine = AlarmEngine(integration)
    >>> server = PoseidonServer(integration=integration)
    >>>
    >>> # 创建 Marine Channels 集成
    >>> marine_integration = MarineChannelsIntegration(
    ...     integration=integration,
    ...     alarm_engine=alarm_engine,
    ...     server=server
    ... )
    >>>
    >>> # 配置报警规则
    >>> marine_integration.setup_alarm_rules()
    >>>
    >>> # 配置联动逻辑
    >>> marine_integration.setup_channel_linkages()
    >>>
    >>> # 启动集成
    >>> marine_integration.start()
"""

import json
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Callable, Optional

try:
    from .channels_integration import ChannelsIntegration, ChannelData
    from .alarm_engine import AlarmEngine, AlarmLevel, AlarmRecord
except ImportError:
    from channels_integration import ChannelsIntegration, ChannelData
    from alarm_engine import AlarmEngine, AlarmLevel, AlarmRecord

if TYPE_CHECKING:
    from .poseidon_server import PoseidonServer


@dataclass
class DataQualityMetrics:
    """数据质量指标.

    Attributes:
        channel: Channel 名称.
        completeness: 完整性 (0-1).
        accuracy: 准确性 (0-1).
        timeliness: 及时性 (0-1).
        consistency: 一致性 (0-1).
        anomaly_count: 异常数量.
        last_check: 最后检查时间.
    """

    channel: str
    completeness: float = 1.0
    accuracy: float = 1.0
    timeliness: float = 1.0
    consistency: float = 1.0
    anomaly_count: int = 0
    last_check: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典."""
        return {
            "channel": self.channel,
            "completeness": round(self.completeness, 4),
            "accuracy": round(self.accuracy, 4),
            "timeliness": round(self.timeliness, 4),
            "consistency": round(self.consistency, 4),
            "anomaly_count": self.anomaly_count,
            "last_check": self.last_check.isoformat(),
            "overall_score": round(
                (self.completeness + self.accuracy + self.timeliness + self.consistency) / 4,
                4,
            ),
        }


@dataclass
class ChannelLinkage:
    """Channel 联动规则.

    Attributes:
        id: 联动 ID.
        name: 联动名称.
        source_channels: 源 Channel 列表.
        target_channel: 目标 Channel.
        condition: 触发条件.
        action: 执行动作.
        enabled: 是否启用.
    """

    id: str
    name: str
    source_channels: list[str]
    target_channel: str
    condition: Callable[[dict[str, Any]], bool]
    action: Callable[[dict[str, Any]], None]
    enabled: bool = True


class MarineChannelsIntegration:
    """Marine Channels 深度集成.

    功能:
    - 配置 8 个 Marine Channels 的报警规则
    - 实现数据质量检查
    - 实现异常检测
    - 实现 Channel 间联动逻辑
    - 实时数据同步到 Poseidon

    示例用法:
        >>> integration = ChannelsIntegration()
        >>> alarm_engine = AlarmEngine(integration)
        >>> server = PoseidonServer(integration=integration)
        >>>
        >>> marine = MarineChannelsIntegration(integration, alarm_engine, server)
        >>> marine.setup_alarm_rules()
        >>> marine.setup_channel_linkages()
        >>> marine.start()
    """

    def __init__(
        self,
        integration: ChannelsIntegration,
        alarm_engine: AlarmEngine,
        server: Optional["PoseidonServer"] = None,
    ):
        """初始化 Marine Channels 集成.

        Args:
            integration: ChannelsIntegration 实例.
            alarm_engine: AlarmEngine 实例.
            server: PoseidonServer 实例（可选）.
        """
        self.integration = integration
        self.alarm_engine = alarm_engine
        self.server = server

        # 数据质量指标
        self.quality_metrics: dict[str, DataQualityMetrics] = {}

        # Channel 联动规则
        self.linkages: list[ChannelLinkage] = []

        # 异常检测配置
        self.anomaly_detection: dict[str, dict[str, Any]] = {}

        # 线程控制
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # 8 个 Marine Channels 配置
        self.marine_channels = [
            "nmea_parser",
            "vessel_ais",
            "engine_monitor",
            "power_management",
            "navigation_data",
            "cargo_monitor",
            "weather_routing",
            "web",
        ]

        # 初始化数据质量指标
        for channel in self.marine_channels:
            self.quality_metrics[channel] = DataQualityMetrics(channel=channel)

        # 注册数据更新回调
        self.integration.add_callback("global", self._on_data_update)

    def setup_alarm_rules(self) -> None:
        """配置所有 Marine Channels 的报警规则."""
        print("🔧 配置 Marine Channels 报警规则...")

        # 1. NMEA Parser 报警规则
        self._setup_nmea_alarms()

        # 2. Vessel AIS 报警规则
        self._setup_ais_alarms()

        # 3. Engine Monitor 报警规则
        self._setup_engine_alarms()

        # 4. Power Management 报警规则
        self._setup_power_alarms()

        # 5. Navigation Data 报警规则
        self._setup_navigation_alarms()

        # 6. Cargo Monitor 报警规则
        self._setup_cargo_alarms()

        # 7. Weather Routing 报警规则
        self._setup_weather_alarms()

        # 8. Web Channel 报警规则
        self._setup_web_alarms()

        print(f"✅ 已配置 {len(self.alarm_engine.rules) + len(self.alarm_engine.rate_rules)} 个报警规则")

    def _setup_nmea_alarms(self) -> None:
        """配置 NMEA Parser 报警规则."""
        # GPS 信号丢失
        self.alarm_engine.add_rule(
            name="nmea_gps_signal_loss",
            channel="nmea_parser",
            metric="gps_quality",
            condition="<",
            threshold=1,
            level=AlarmLevel.WARNING,
            message="GPS 信号质量差：{value}",
            cooldown_seconds=300,
        )

        # 航向数据异常
        self.alarm_engine.add_rule(
            name="nmea_heading_invalid",
            channel="nmea_parser",
            metric="heading",
            condition="outside",
            threshold_min=0,
            threshold_max=360,
            level=AlarmLevel.WARNING,
            message="航向数据超出范围：{value}°",
            cooldown_seconds=60,
        )

        # 速度突变
        self.alarm_engine.add_rate_rule(
            name="nmea_speed_sudden_change",
            channel="nmea_parser",
            metric="speed",
            rate_threshold=10.0,  # 每分钟变化超过 10 节
            window_seconds=60,
            level=AlarmLevel.WARNING,
            message="船速突变",
            cooldown_seconds=120,
        )

    def _setup_ais_alarms(self) -> None:
        """配置 Vessel AIS 报警规则."""
        # 碰撞风险（CPA 过小）
        self.alarm_engine.add_rule(
            name="ais_collision_risk",
            channel="vessel_ais",
            metric="cpa",
            condition="<",
            threshold=0.5,  # 0.5 海里
            level=AlarmLevel.CRITICAL,
            message="碰撞风险：CPA={value} 海里",
            cooldown_seconds=60,
        )

        # TCPA 过小（时间紧迫）
        self.alarm_engine.add_rule(
            name="ais_tcpa_urgent",
            channel="vessel_ais",
            metric="tcpa",
            condition="<",
            threshold=300,  # 5 分钟
            level=AlarmLevel.EMERGENCY,
            message="紧急碰撞风险：TCPA={value} 秒",
            cooldown_seconds=30,
        )

        # AIS 目标数量过多
        self.alarm_engine.add_rule(
            name="ais_too_many_targets",
            channel="vessel_ais",
            metric="target_count",
            condition=">",
            threshold=100,
            level=AlarmLevel.WARNING,
            message="AIS 目标过多：{value} 个",
            cooldown_seconds=300,
        )

    def _setup_engine_alarms(self) -> None:
        """配置 Engine Monitor 报警规则."""
        # 高温报警
        self.alarm_engine.add_rule(
            name="engine_high_temperature",
            channel="engine_monitor",
            metric="temperature",
            condition=">",
            threshold=90.0,
            level=AlarmLevel.CRITICAL,
            message="发动机高温：{value}°C",
            cooldown_seconds=120,
        )

        # 低油压报警
        self.alarm_engine.add_rule(
            name="engine_low_oil_pressure",
            channel="engine_monitor",
            metric="oil_pressure",
            condition="<",
            threshold=2.0,
            level=AlarmLevel.CRITICAL,
            message="机油压力过低：{value} bar",
            cooldown_seconds=60,
        )

        # 超速报警
        self.alarm_engine.add_rule(
            name="engine_overspeed",
            channel="engine_monitor",
            metric="rpm",
            condition=">",
            threshold=2500,
            level=AlarmLevel.EMERGENCY,
            message="发动机超速：{value} rpm",
            cooldown_seconds=60,
        )

        # 高负荷报警
        self.alarm_engine.add_rule(
            name="engine_overload",
            channel="engine_monitor",
            metric="load",
            condition=">",
            threshold=95.0,
            level=AlarmLevel.WARNING,
            message="发动机高负荷：{value}%",
            cooldown_seconds=180,
        )

        # 转速突变
        self.alarm_engine.add_rate_rule(
            name="engine_rpm_sudden_change",
            channel="engine_monitor",
            metric="rpm",
            rate_threshold=500.0,
            window_seconds=60,
            level=AlarmLevel.WARNING,
            message="发动机转速突变",
            cooldown_seconds=120,
        )

    def _setup_power_alarms(self) -> None:
        """配置 Power Management 报警规则."""
        # 低电压报警
        self.alarm_engine.add_rule(
            name="power_low_voltage",
            channel="power_management",
            metric="voltage",
            condition="<",
            threshold=200,
            level=AlarmLevel.CRITICAL,
            message="电压过低：{value}V",
            cooldown_seconds=60,
        )

        # 高电压报警
        self.alarm_engine.add_rule(
            name="power_high_voltage",
            channel="power_management",
            metric="voltage",
            condition=">",
            threshold=250,
            level=AlarmLevel.CRITICAL,
            message="电压过高：{value}V",
            cooldown_seconds=60,
        )

        # 频率异常
        self.alarm_engine.add_rule(
            name="power_frequency_abnormal",
            channel="power_management",
            metric="frequency",
            condition="outside",
            threshold_min=47,
            threshold_max=53,
            level=AlarmLevel.WARNING,
            message="频率异常：{value}Hz",
            cooldown_seconds=120,
        )

        # 高电流报警
        self.alarm_engine.add_rule(
            name="power_high_current",
            channel="power_management",
            metric="current",
            condition=">",
            threshold=100,
            level=AlarmLevel.WARNING,
            message="电流过高：{value}A",
            cooldown_seconds=180,
        )

    def _setup_navigation_alarms(self) -> None:
        """配置 Navigation Data 报警规则."""
        # 偏航报警
        self.alarm_engine.add_rule(
            name="navigation_cross_track_error",
            channel="navigation_data",
            metric="cross_track_error",
            condition=">",
            threshold=0.5,
            level=AlarmLevel.WARNING,
            message="偏航：XTE={value} 海里",
            cooldown_seconds=120,
        )

        # 浅水报警
        self.alarm_engine.add_rule(
            name="navigation_shallow_water",
            channel="navigation_data",
            metric="depth",
            condition="<",
            threshold=10.0,
            level=AlarmLevel.CRITICAL,
            message="浅水警告：水深={value} 米",
            cooldown_seconds=60,
        )

        # 速度异常
        self.alarm_engine.add_rule(
            name="navigation_speed_anomaly",
            channel="navigation_data",
            metric="speed",
            condition=">",
            threshold=30.0,
            level=AlarmLevel.WARNING,
            message="航速异常：{value} 节",
            cooldown_seconds=180,
        )

    def _setup_cargo_alarms(self) -> None:
        """配置 Cargo Monitor 报警规则."""
        # 货舱高温
        self.alarm_engine.add_rule(
            name="cargo_high_temperature",
            channel="cargo_monitor",
            metric="temperature",
            condition=">",
            threshold=40.0,
            level=AlarmLevel.WARNING,
            message="货舱温度过高：{value}°C",
            cooldown_seconds=300,
        )

        # 湿度过高
        self.alarm_engine.add_rule(
            name="cargo_high_humidity",
            channel="cargo_monitor",
            metric="humidity",
            condition=">",
            threshold=80.0,
            level=AlarmLevel.WARNING,
            message="货舱湿度过高：{value}%",
            cooldown_seconds=300,
        )

        # 液位过高
        self.alarm_engine.add_rule(
            name="cargo_high_level",
            channel="cargo_monitor",
            metric="level",
            condition=">",
            threshold=95.0,
            level=AlarmLevel.CRITICAL,
            message="货舱液位过高：{value}%",
            cooldown_seconds=120,
        )

    def _setup_weather_alarms(self) -> None:
        """配置 Weather Routing 报警规则."""
        # 大风报警
        self.alarm_engine.add_rule(
            name="weather_high_wind",
            channel="weather_routing",
            metric="wind_speed",
            condition=">",
            threshold=20.0,
            level=AlarmLevel.WARNING,
            message="大风警告：风速={value} m/s",
            cooldown_seconds=600,
        )

        # 大浪报警
        self.alarm_engine.add_rule(
            name="weather_high_waves",
            channel="weather_routing",
            metric="wave_height",
            condition=">",
            threshold=4.0,
            level=AlarmLevel.CRITICAL,
            message="大浪警告：波高={value} 米",
            cooldown_seconds=600,
        )

        # 低能见度
        self.alarm_engine.add_rule(
            name="weather_low_visibility",
            channel="weather_routing",
            metric="visibility",
            condition="<",
            threshold=1.0,
            level=AlarmLevel.WARNING,
            message="低能见度：{value} 公里",
            cooldown_seconds=300,
        )

    def _setup_web_alarms(self) -> None:
        """配置 Web Channel 报警规则."""
        # 数据更新延迟
        self.alarm_engine.add_rule(
            name="web_data_stale",
            channel="web",
            metric="update_delay",
            condition=">",
            threshold=300,  # 5 分钟
            level=AlarmLevel.WARNING,
            message="Web 数据更新延迟：{value} 秒",
            cooldown_seconds=300,
        )

    def setup_channel_linkages(self) -> None:
        """配置 Channel 间联动逻辑."""
        print("🔗 配置 Channel 联动逻辑...")

        # 联动 1: Engine + Cargo + Weather -> 航速建议
        self._add_linkage(
            name="speed_recommendation",
            source_channels=["engine_monitor", "cargo_monitor", "weather_routing"],
            target_channel="navigation_data",
            condition=self._check_speed_recommendation,
            action=self._apply_speed_recommendation,
        )

        # 联动 2: Weather + Navigation -> 航线调整建议
        self._add_linkage(
            name="route_adjustment",
            source_channels=["weather_routing", "navigation_data"],
            target_channel="navigation_data",
            condition=self._check_route_adjustment,
            action=self._apply_route_adjustment,
        )

        # 联动 3: Engine + Power -> 能耗优化
        self._add_linkage(
            name="power_optimization",
            source_channels=["engine_monitor", "power_management"],
            target_channel="power_management",
            condition=self._check_power_optimization,
            action=self._apply_power_optimization,
        )

        # 联动 4: AIS + Navigation -> 碰撞规避
        self._add_linkage(
            name="collision_avoidance",
            source_channels=["vessel_ais", "navigation_data"],
            target_channel="navigation_data",
            condition=self._check_collision_avoidance,
            action=self._apply_collision_avoidance,
        )

        print(f"✅ 已配置 {len(self.linkages)} 个联动规则")

    def _add_linkage(
        self,
        name: str,
        source_channels: list[str],
        target_channel: str,
        condition: Callable[[dict[str, Any]], bool],
        action: Callable[[dict[str, Any]], None],
    ) -> None:
        """添加联动规则.

        Args:
            name: 联动名称.
            source_channels: 源 Channel 列表.
            target_channel: 目标 Channel.
            condition: 触发条件函数.
            action: 执行动作函数.
        """
        import uuid

        linkage = ChannelLinkage(
            id=f"linkage-{uuid.uuid4().hex[:8]}",
            name=name,
            source_channels=source_channels,
            target_channel=target_channel,
            condition=condition,
            action=action,
        )
        self.linkages.append(linkage)

    def _check_speed_recommendation(self, data: dict[str, Any]) -> bool:
        """检查航速建议条件.

        条件：恶劣天气 + 高负荷 -> 建议降速
        """
        weather = data.get("weather_routing", {})
        engine = data.get("engine_monitor", {})

        wind_speed = weather.get("wind_speed", 0)
        wave_height = weather.get("wave_height", 0)
        engine_load = engine.get("load", 0)

        return (wind_speed > 15 or wave_height > 3) and engine_load > 80

    def _apply_speed_recommendation(self, data: dict[str, Any]) -> None:
        """应用航速建议."""
        print("🔗 联动触发：建议降低航速以应对恶劣天气")
        # 这里可以发送通知或自动调整

    def _check_route_adjustment(self, data: dict[str, Any]) -> bool:
        """检查航线调整条件.

        条件：前方恶劣天气 + 当前航线 -> 建议调整航线
        """
        weather = data.get("weather_routing", {})
        navigation = data.get("navigation_data", {})

        wind_speed = weather.get("wind_speed", 0)
        wave_height = weather.get("wave_height", 0)

        return wind_speed > 20 or wave_height > 4

    def _apply_route_adjustment(self, data: dict[str, Any]) -> None:
        """应用航线调整建议."""
        print("🔗 联动触发：建议调整航线以避开恶劣天气")

    def _check_power_optimization(self, data: dict[str, Any]) -> bool:
        """检查能耗优化条件.

        条件：发动机低效区 + 电力富余 -> 建议优化
        """
        engine = data.get("engine_monitor", {})
        power = data.get("power_management", {})

        engine_load = engine.get("load", 0)
        voltage = power.get("voltage", 0)

        return engine_load < 40 and voltage > 230

    def _apply_power_optimization(self, data: dict[str, Any]) -> None:
        """应用能耗优化建议."""
        print("🔗 联动触发：建议优化能耗配置")

    def _check_collision_avoidance(self, data: dict[str, Any]) -> bool:
        """检查碰撞规避条件.

        条件：AIS 碰撞风险 + 当前航向 -> 需要规避
        """
        ais = data.get("vessel_ais", {})
        navigation = data.get("navigation_data", {})

        cpa = ais.get("cpa", 999)
        tcpa = ais.get("tcpa", 9999)

        return cpa < 0.5 and tcpa < 600

    def _apply_collision_avoidance(self, data: dict[str, Any]) -> None:
        """应用碰撞规避动作."""
        print("🔗 联动触发：碰撞规避警报！建议立即转向")
        # 这里可以触发紧急报警

    def check_data_quality(self, channel_name: str, data: dict[str, Any]) -> DataQualityMetrics:
        """检查数据质量.

        Args:
            channel_name: Channel 名称.
            data: 数据内容.

        Returns:
            数据质量指标.
        """
        metrics = self.quality_metrics.get(channel_name, DataQualityMetrics(channel=channel_name))
        metrics.last_check = datetime.now()

        # 1. 完整性检查
        expected_fields = self._get_expected_fields(channel_name)
        if expected_fields:
            actual_fields = set(data.keys())
            metrics.completeness = len(actual_fields & set(expected_fields)) / len(expected_fields)

        # 2. 准确性检查（范围验证）
        accuracy_checks = self._get_accuracy_checks(channel_name)
        if accuracy_checks:
            accurate_count = 0
            for field, (min_val, max_val) in accuracy_checks.items():
                if field in data:
                    value = data[field]
                    if isinstance(value, (int, float)) and min_val <= value <= max_val:
                        accurate_count += 1
            metrics.accuracy = accurate_count / len(accuracy_checks) if accuracy_checks else 1.0

        # 3. 及时性检查
        # （通过数据更新时间戳检查，这里简化处理）
        metrics.timeliness = 1.0

        # 4. 一致性检查
        # （检查数据是否在合理范围内变化）
        metrics.consistency = 1.0

        # 5. 异常检测
        if self._detect_anomaly(channel_name, data):
            metrics.anomaly_count += 1

        return metrics

    def _get_expected_fields(self, channel_name: str) -> list[str]:
        """获取 Channel 的预期字段."""
        field_map = {
            "nmea_parser": ["latitude", "longitude", "speed", "heading", "gps_quality"],
            "vessel_ais": ["mmsi", "latitude", "longitude", "course", "speed", "cpa", "tcpa"],
            "engine_monitor": ["rpm", "load", "temperature", "oil_pressure", "fuel_consumption"],
            "power_management": ["voltage", "current", "frequency", "power_factor"],
            "navigation_data": ["latitude", "longitude", "speed", "course", "heading", "depth"],
            "cargo_monitor": ["temperature", "humidity", "level", "pressure"],
            "weather_routing": ["wind_speed", "wind_direction", "wave_height", "visibility"],
            "web": ["data", "timestamp"],
        }
        return field_map.get(channel_name, [])

    def _get_accuracy_checks(self, channel_name: str) -> dict[str, tuple[float, float]]:
        """获取 Channel 的准确性检查范围."""
        checks_map = {
            "nmea_parser": {
                "latitude": (-90, 90),
                "longitude": (-180, 180),
                "heading": (0, 360),
                "gps_quality": (0, 5),
            },
            "engine_monitor": {
                "rpm": (0, 3000),
                "load": (0, 100),
                "temperature": (0, 150),
                "oil_pressure": (0, 10),
            },
            "power_management": {
                "voltage": (180, 260),
                "frequency": (45, 65),
                "current": (0, 200),
            },
            "weather_routing": {
                "wind_speed": (0, 50),
                "wave_height": (0, 20),
                "visibility": (0, 50),
            },
        }
        return checks_map.get(channel_name, {})

    def _detect_anomaly(self, channel_name: str, data: dict[str, Any]) -> bool:
        """检测数据异常.

        Args:
            channel_name: Channel 名称.
            data: 数据内容.

        Returns:
            是否检测到异常.
        """
        # 简单的阈值异常检测
        thresholds = self.anomaly_detection.get(channel_name, {})

        for metric, (min_val, max_val) in thresholds.items():
            if metric in data:
                value = data[metric]
                if isinstance(value, (int, float)) and (value < min_val or value > max_val):
                    return True

        return False

    def _on_data_update(self, data: ChannelData) -> None:
        """数据更新回调.

        Args:
            data: Channel 数据.
        """
        # 检查数据质量
        self.check_data_quality(data.channel_name, data.data)

        # 检查联动规则
        self._check_linkages()

    def _check_linkages(self) -> None:
        """检查所有联动规则."""
        # 获取所有 Channel 的最新数据
        aggregated = self.integration.get_aggregated_data()

        for linkage in self.linkages:
            if not linkage.enabled:
                continue

            # 检查是否所有源 Channel 都有数据
            source_data = {}
            all_present = True
            for channel in linkage.source_channels:
                if channel in aggregated:
                    channel_data = aggregated[channel]
                    if isinstance(channel_data, dict) and "data" in channel_data:
                        source_data[channel] = channel_data["data"]
                    else:
                        all_present = False
                else:
                    all_present = False

            if not all_present:
                continue

            # 检查条件
            try:
                if linkage.condition(source_data):
                    linkage.action(source_data)
            except Exception as e:
                print(f"⚠️ 联动检查失败 ({linkage.name}): {e}")

    def get_quality_report(self) -> dict[str, Any]:
        """获取数据质量报告.

        Returns:
            质量报告字典.
        """
        return {
            "channels": {
                name: metrics.to_dict()
                for name, metrics in self.quality_metrics.items()
            },
            "timestamp": datetime.now().isoformat(),
        }

    def start(self) -> None:
        """启动 Marine Channels 集成."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

        print("🚀 Marine Channels 集成已启动")

    def stop(self) -> None:
        """停止 Marine Channels 集成."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        print("🛑 Marine Channels 集成已停止")

    def _monitor_loop(self) -> None:
        """后台监控循环."""
        while self._running:
            try:
                # 定期检查数据质量
                aggregated = self.integration.get_aggregated_data()
                for channel_name, channel_data in aggregated.items():
                    if isinstance(channel_data, dict) and "data" in channel_data:
                        self.check_data_quality(channel_name, channel_data["data"])

                # 检查联动规则
                self._check_linkages()
            except Exception as e:
                print(f"⚠️ Marine Channels 监控失败：{e}")

            time.sleep(5.0)  # 每 5 秒检查一次


# 导出
__all__ = [
    "MarineChannelsIntegration",
    "DataQualityMetrics",
    "ChannelLinkage",
]
