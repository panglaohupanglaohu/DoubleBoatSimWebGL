# -*- coding: utf-8 -*-
"""
Alarm Engine - 报警规则引擎.

实现四级报警系统，支持可配置的报警规则、历史记录与统计、通知回调机制。

功能:
- 四级报警系统（正常/警告/危险/紧急）
- 可配置的报警规则（阈值、变化率、组合条件）
- 报警历史记录与统计
- 报警通知回调机制
- 支持 Channel 数据触发

报警级别:
- NORMAL(0): 正常状态
- WARNING(1): 警告 - 需要注意但未达危险
- CRITICAL(2): 危险 - 需要立即关注
- EMERGENCY(3): 紧急 - 严重影响系统安全

示例用法:
    >>> from .channels_integration import ChannelsIntegration
    >>>
    >>> # 创建报警引擎
    >>> engine = AlarmEngine(integration)
    >>>
    >>> # 添加报警规则
    >>> engine.add_rule(
    ...     name="engine_high_temp",
    ...     channel="engine_monitor",
    ...     metric="temperature",
    ...     condition=">",
    ...     threshold=90.0,
    ...     level=AlarmLevel.CRITICAL,
    ...     message="发动机温度过高"
    ... )
    >>>
    >>> # 添加变化率规则
    >>> engine.add_rate_rule(
    ...     name="rpm_sudden_change",
    ...     channel="engine_monitor",
    ...     metric="rpm",
    ...     rate_threshold=50.0,  # 每分钟变化超过 50
    ...     window_seconds=60,
    ...     level=AlarmLevel.WARNING,
    ...     message="发动机转速突变"
    ... )
    >>>
    >>> # 数据更新时自动检查
    >>> integration.update_data("engine_monitor", {"temperature": 95.0, "rpm": 120})
    >>> # 自动触发报警
"""

import json
import sqlite3
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum
from pathlib import Path
from typing import Any, Callable, Optional

try:
    from .channels_integration import ChannelsIntegration, ChannelData
except ImportError:
    from channels_integration import ChannelsIntegration, ChannelData


class AlarmLevel(IntEnum):
    """报警级别枚举."""

    NORMAL = 0  # 正常
    WARNING = 1  # 警告
    CRITICAL = 2  # 危险
    EMERGENCY = 3  # 紧急

    def __str__(self) -> str:
        """转换为字符串."""
        return self.name.lower()

    @classmethod
    def from_string(cls, s: str) -> "AlarmLevel":
        """从字符串转换."""
        return cls[s.upper()]


class ConditionType:
    """条件类型常量."""

    GREATER = ">"  # 大于
    GREATER_EQUAL = ">="  # 大于等于
    LESS = "<"  # 小于
    LESS_EQUAL = "<="  # 小于等于
    EQUAL = "=="  # 等于
    NOT_EQUAL = "!="  # 不等于
    BETWEEN = "between"  # 在范围内
    OUTSIDE = "outside"  # 在范围外


@dataclass
class AlarmRule:
    """报警规则.

    Attributes:
        id: 规则 ID.
        name: 规则名称.
        channel: Channel 名称.
        metric: 指标名称.
        condition: 条件类型.
        threshold: 阈值 (单值).
        threshold_min: 最小阈值 (用于 between/outside).
        threshold_max: 最大阈值 (用于 between/outside).
        level: 报警级别.
        message: 报警消息模板.
        enabled: 是否启用.
        cooldown_seconds: 冷却时间 (秒).
        created_at: 创建时间.
    """

    id: str
    name: str
    channel: str
    metric: str
    condition: str = ConditionType.GREATER
    threshold: Optional[float] = None
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    level: AlarmLevel = AlarmLevel.WARNING
    message: str = ""
    enabled: bool = True
    cooldown_seconds: int = 60
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典."""
        return {
            "id": self.id,
            "name": self.name,
            "channel": self.channel,
            "metric": self.metric,
            "condition": self.condition,
            "threshold": self.threshold,
            "threshold_min": self.threshold_min,
            "threshold_max": self.threshold_max,
            "level": self.level.name,
            "message": self.message,
            "enabled": self.enabled,
            "cooldown_seconds": self.cooldown_seconds,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class RateRule:
    """变化率报警规则.

    Attributes:
        id: 规则 ID.
        name: 规则名称.
        channel: Channel 名称.
        metric: 指标名称.
        rate_threshold: 变化率阈值 (单位时间内的变化量).
        window_seconds: 时间窗口 (秒).
        level: 报警级别.
        message: 报警消息.
        enabled: 是否启用.
        cooldown_seconds: 冷却时间.
        created_at: 创建时间.
    """

    id: str
    name: str
    channel: str
    metric: str
    rate_threshold: float
    window_seconds: int = 60
    level: AlarmLevel = AlarmLevel.WARNING
    message: str = ""
    enabled: bool = True
    cooldown_seconds: int = 60
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典."""
        return {
            "id": self.id,
            "name": self.name,
            "channel": self.channel,
            "metric": self.metric,
            "rate_threshold": self.rate_threshold,
            "window_seconds": self.window_seconds,
            "level": self.level.name,
            "message": self.message,
            "enabled": self.enabled,
            "cooldown_seconds": self.cooldown_seconds,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class CompositeRule:
    """组合条件报警规则.

    支持多个条件的逻辑组合 (AND/OR).

    Attributes:
        id: 规则 ID.
        name: 规则名称.
        rules: 子规则 ID 列表.
        logic: 逻辑运算符 ("AND" 或 "OR").
        level: 报警级别.
        message: 报警消息.
        enabled: 是否启用.
        cooldown_seconds: 冷却时间.
        created_at: 创建时间.
    """

    id: str
    name: str
    rules: list[str]  # 子规则 ID 列表
    logic: str = "AND"  # "AND" 或 "OR"
    level: AlarmLevel = AlarmLevel.CRITICAL
    message: str = ""
    enabled: bool = True
    cooldown_seconds: int = 60
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典."""
        return {
            "id": self.id,
            "name": self.name,
            "rules": self.rules,
            "logic": self.logic,
            "level": self.level.name,
            "message": self.message,
            "enabled": self.enabled,
            "cooldown_seconds": self.cooldown_seconds,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class AlarmRecord:
    """报警记录.

    Attributes:
        id: 记录 ID.
        rule_id: 触发规则 ID.
        rule_name: 规则名称.
        channel: Channel 名称.
        level: 报警级别.
        message: 报警消息.
        value: 触发值.
        context: 上下文数据.
        timestamp: 报警时间.
        acknowledged: 是否已确认.
        resolved: 是否已解决.
        resolved_at: 解决时间.
    """

    id: str
    rule_id: str
    rule_name: str
    channel: str
    level: AlarmLevel
    message: str
    value: Optional[float] = None
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    resolved: bool = False
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典."""
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "channel": self.channel,
            "level": self.level.name,
            "message": self.message,
            "value": self.value,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


@dataclass
class AlarmStats:
    """报警统计.

    Attributes:
        total_alarms: 总报警数.
        by_level: 按级别统计.
        by_channel: 按 Channel 统计.
        by_rule: 按规则统计.
        unacknowledged: 未确认数.
        unresolved: 未解决数.
        last_24h: 最近 24 小时统计.
    """

    total_alarms: int = 0
    by_level: dict[str, int] = field(default_factory=dict)
    by_channel: dict[str, int] = field(default_factory=dict)
    by_rule: dict[str, int] = field(default_factory=dict)
    unacknowledged: int = 0
    unresolved: int = 0
    last_24h: int = 0

    def to_dict(self) -> dict[str, Any]:
        """转换为字典."""
        return {
            "total_alarms": self.total_alarms,
            "by_level": self.by_level,
            "by_channel": self.by_channel,
            "by_rule": self.by_rule,
            "unacknowledged": self.unacknowledged,
            "unresolved": self.unresolved,
            "last_24h": self.last_24h,
        }


class AlarmEngine:
    """报警规则引擎.

    功能:
    - 管理报警规则（阈值、变化率、组合条件）
    - 实时数据检查与报警触发
    - 报警历史记录与持久化
    - 报警统计与分析
    - 通知回调机制

    示例用法:
        >>> integration = ChannelsIntegration()
        >>> engine = AlarmEngine(integration)
        >>>
        >>> # 添加阈值规则
        >>> engine.add_rule(
        ...     name="high_temp",
        ...     channel="engine_monitor",
        ...     metric="temperature",
        ...     condition=">",
        ...     threshold=90.0,
        ...     level=AlarmLevel.CRITICAL,
        ...     message="发动机温度过高：{value}°C"
        ... )
        >>>
        >>> # 添加变化率规则
        >>> engine.add_rate_rule(
        ...     name="rpm_spike",
        ...     channel="engine_monitor",
        ...     metric="rpm",
        ...     rate_threshold=50.0,
        ...     window_seconds=60,
        ...     level=AlarmLevel.WARNING
        ... )
        >>>
        >>> # 添加通知回调
        >>> def on_alarm(record: AlarmRecord):
        ...     print(f"🚨 报警：{record.message}")
        >>> engine.add_callback(on_alarm)
    """

    def __init__(
        self,
        integration: ChannelsIntegration,
        db_path: str = "poseidon.db",
        check_interval: float = 1.0,
    ):
        """初始化报警引擎.

        Args:
            integration: ChannelsIntegration 实例.
            db_path: SQLite 数据库路径.
            check_interval: 检查间隔 (秒).
        """
        self.integration = integration
        self.db_path = db_path

        # 规则存储
        self.rules: dict[str, AlarmRule] = {}
        self.rate_rules: dict[str, RateRule] = {}
        self.composite_rules: dict[str, CompositeRule] = {}

        # 报警记录
        self.alarms: list[AlarmRecord] = []
        self.active_alarms: dict[str, AlarmRecord] = {}  # rule_id -> alarm

        # 冷却时间跟踪
        self.last_alarm_time: dict[str, datetime] = {}

        # 变化率跟踪 (用于 rate rules)
        self.metric_history: dict[str, list[tuple[datetime, float]]] = defaultdict(list)

        # 回调函数
        self.callbacks: list[Callable[[AlarmRecord], None]] = []

        # 线程控制
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # 初始化数据库
        self._init_database()

        # 注册数据更新回调
        self.integration.add_callback("global", self._on_data_update)

    def _init_database(self) -> None:
        """初始化 SQLite 数据库."""
        db_path = Path(self.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 创建 alarm_rules 表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alarm_rules (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                channel TEXT NOT NULL,
                metric TEXT NOT NULL,
                config_json TEXT NOT NULL,
                enabled BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # 创建 alarm_records 表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alarm_records (
                id TEXT PRIMARY KEY,
                rule_id TEXT NOT NULL,
                rule_name TEXT NOT NULL,
                channel TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                value REAL,
                context_json TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                acknowledged BOOLEAN DEFAULT FALSE,
                resolved BOOLEAN DEFAULT FALSE,
                resolved_at DATETIME,
                FOREIGN KEY (rule_id) REFERENCES alarm_rules(id)
            )
        """
        )

        # 创建索引
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_alarm_rule ON alarm_records(rule_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_alarm_channel ON alarm_records(channel)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_alarm_level ON alarm_records(level)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_alarm_timestamp ON alarm_records(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_alarm_ack ON alarm_records(acknowledged)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_alarm_resolved ON alarm_records(resolved)"
        )

        conn.commit()
        conn.close()

    def _generate_id(self, prefix: str) -> str:
        """生成唯一 ID.

        Args:
            prefix: ID 前缀.

        Returns:
            唯一 ID.
        """
        import uuid

        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def add_rule(
        self,
        name: str,
        channel: str,
        metric: str,
        condition: str = ConditionType.GREATER,
        threshold: Optional[float] = None,
        threshold_min: Optional[float] = None,
        threshold_max: Optional[float] = None,
        level: AlarmLevel = AlarmLevel.WARNING,
        message: str = "",
        cooldown_seconds: int = 60,
    ) -> str:
        """添加阈值报警规则.

        Args:
            name: 规则名称.
            channel: Channel 名称.
            metric: 指标名称.
            condition: 条件类型.
            threshold: 阈值.
            threshold_min: 最小阈值 (用于 between/outside).
            threshold_max: 最大阈值 (用于 between/outside).
            level: 报警级别.
            message: 报警消息模板.
            cooldown_seconds: 冷却时间.

        Returns:
            规则 ID.
        """
        rule_id = self._generate_id("rule")
        rule = AlarmRule(
            id=rule_id,
            name=name,
            channel=channel,
            metric=metric,
            condition=condition,
            threshold=threshold,
            threshold_min=threshold_min,
            threshold_max=threshold_max,
            level=level,
            message=message or f"{name}: 触发报警",
            cooldown_seconds=cooldown_seconds,
        )

        with self._lock:
            self.rules[rule_id] = rule
            self._persist_rule(rule, "threshold")

        print(f"✅ 报警规则已添加：{name} ({rule_id})")
        return rule_id

    def add_rate_rule(
        self,
        name: str,
        channel: str,
        metric: str,
        rate_threshold: float,
        window_seconds: int = 60,
        level: AlarmLevel = AlarmLevel.WARNING,
        message: str = "",
        cooldown_seconds: int = 60,
    ) -> str:
        """添加变化率报警规则.

        Args:
            name: 规则名称.
            channel: Channel 名称.
            metric: 指标名称.
            rate_threshold: 变化率阈值.
            window_seconds: 时间窗口.
            level: 报警级别.
            message: 报警消息.
            cooldown_seconds: 冷却时间.

        Returns:
            规则 ID.
        """
        rule_id = self._generate_id("rate")
        rule = RateRule(
            id=rule_id,
            name=name,
            channel=channel,
            metric=metric,
            rate_threshold=rate_threshold,
            window_seconds=window_seconds,
            level=level,
            message=message or f"{name}: 变化率异常",
            cooldown_seconds=cooldown_seconds,
        )

        with self._lock:
            self.rate_rules[rule_id] = rule
            self._persist_rule(rule, "rate")

        print(f"✅ 变化率规则已添加：{name} ({rule_id})")
        return rule_id

    def add_composite_rule(
        self,
        name: str,
        rule_ids: list[str],
        logic: str = "AND",
        level: AlarmLevel = AlarmLevel.CRITICAL,
        message: str = "",
        cooldown_seconds: int = 60,
    ) -> str:
        """添加组合条件报警规则.

        Args:
            name: 规则名称.
            rule_ids: 子规则 ID 列表.
            logic: 逻辑运算符 ("AND" 或 "OR").
            level: 报警级别.
            message: 报警消息.
            cooldown_seconds: 冷却时间.

        Returns:
            规则 ID.

        Raises:
            ValueError: 如果子规则不存在或逻辑运算符无效.
        """
        if logic not in ("AND", "OR"):
            raise ValueError("逻辑运算符必须是 'AND' 或 'OR'")

        for rule_id in rule_ids:
            if rule_id not in self.rules and rule_id not in self.rate_rules:
                raise ValueError(f"子规则不存在：{rule_id}")

        rule_id = self._generate_id("composite")
        rule = CompositeRule(
            id=rule_id,
            name=name,
            rules=rule_ids,
            logic=logic,
            level=level,
            message=message or f"{name}: 组合条件触发",
            cooldown_seconds=cooldown_seconds,
        )

        with self._lock:
            self.composite_rules[rule_id] = rule
            self._persist_rule(rule, "composite")

        print(f"✅ 组合规则已添加：{name} ({rule_id})")
        return rule_id

    def _persist_rule(self, rule: Any, rule_type: str) -> None:
        """持久化规则到数据库.

        Args:
            rule: 规则对象.
            rule_type: 规则类型.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        config = rule.to_dict()
        cursor.execute(
            """
            INSERT OR REPLACE INTO alarm_rules (id, name, type, channel, metric, config_json, enabled)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                rule.id,
                rule.name,
                rule_type,
                rule.channel,
                rule.metric,
                json.dumps(config, ensure_ascii=False),
                rule.enabled,
            ),
        )

        conn.commit()
        conn.close()

    def remove_rule(self, rule_id: str) -> bool:
        """移除规则.

        Args:
            rule_id: 规则 ID.

        Returns:
            是否成功移除.
        """
        with self._lock:
            if rule_id in self.rules:
                del self.rules[rule_id]
            elif rule_id in self.rate_rules:
                del self.rate_rules[rule_id]
            elif rule_id in self.composite_rules:
                del self.composite_rules[rule_id]
            else:
                return False

            # 从数据库删除
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM alarm_rules WHERE id = ?", (rule_id,))
            conn.commit()
            conn.close()

            print(f"❌ 规则已移除：{rule_id}")
            return True

    def enable_rule(self, rule_id: str, enabled: bool = True) -> bool:
        """启用/禁用规则.

        Args:
            rule_id: 规则 ID.
            enabled: 是否启用.

        Returns:
            是否成功.
        """
        with self._lock:
            rule = None
            if rule_id in self.rules:
                rule = self.rules[rule_id]
            elif rule_id in self.rate_rules:
                rule = self.rate_rules[rule_id]
            elif rule_id in self.composite_rules:
                rule = self.composite_rules[rule_id]

            if rule:
                rule.enabled = enabled

                # 更新数据库
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE alarm_rules SET enabled = ? WHERE id = ?",
                    (enabled, rule_id),
                )
                conn.commit()
                conn.close()

                return True
            return False

    def add_callback(self, callback: Callable[[AlarmRecord], None]) -> None:
        """添加报警通知回调.

        Args:
            callback: 回调函数，接收 AlarmRecord 参数.
        """
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[[AlarmRecord], None]) -> None:
        """移除回调函数.

        Args:
            callback: 要移除的回调函数.
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def _on_data_update(self, data: ChannelData) -> None:
        """数据更新回调.

        Args:
            data: Channel 数据.
        """
        self.check_channel(data.channel_name, data.data)

    def check_channel(self, channel_name: str, data: dict[str, Any]) -> None:
        """检查 Channel 数据是否触发报警.

        Args:
            channel_name: Channel 名称.
            data: 数据内容.
        """
        with self._lock:
            # 检查阈值规则
            for rule in self.rules.values():
                if rule.channel == channel_name and rule.enabled:
                    self._check_threshold_rule(rule, data)

            # 检查变化率规则
            for rule in self.rate_rules.values():
                if rule.channel == channel_name and rule.enabled:
                    self._check_rate_rule(rule, data)

            # 检查组合规则
            for rule in self.composite_rules.values():
                if rule.enabled:
                    self._check_composite_rule(rule)

    def _check_threshold_rule(self, rule: AlarmRule, data: dict[str, Any]) -> None:
        """检查阈值规则.

        Args:
            rule: 规则对象.
            data: 数据内容.
        """
        if rule.metric not in data:
            return

        value = data[rule.metric]
        if not isinstance(value, (int, float)):
            return

        triggered = False

        # 检查条件
        if rule.condition == ConditionType.GREATER:
            triggered = value > rule.threshold
        elif rule.condition == ConditionType.GREATER_EQUAL:
            triggered = value >= rule.threshold
        elif rule.condition == ConditionType.LESS:
            triggered = value < rule.threshold
        elif rule.condition == ConditionType.LESS_EQUAL:
            triggered = value <= rule.threshold
        elif rule.condition == ConditionType.EQUAL:
            triggered = value == rule.threshold
        elif rule.condition == ConditionType.NOT_EQUAL:
            triggered = value != rule.threshold
        elif rule.condition == ConditionType.BETWEEN:
            triggered = rule.threshold_min <= value <= rule.threshold_max
        elif rule.condition == ConditionType.OUTSIDE:
            triggered = value < rule.threshold_min or value > rule.threshold_max

        if triggered:
            self._trigger_alarm(rule, value, data)

    def _check_rate_rule(self, rule: RateRule, data: dict[str, Any]) -> None:
        """检查变化率规则.

        Args:
            rule: 规则对象.
            data: 数据内容.
        """
        if rule.metric not in data:
            return

        value = data[rule.metric]
        if not isinstance(value, (int, float)):
            return

        now = datetime.now()
        key = f"{rule.channel}:{rule.metric}"

        # 添加到历史记录
        self.metric_history[key].append((now, value))

        # 清理旧数据
        cutoff = now - timedelta(seconds=rule.window_seconds)
        self.metric_history[key] = [
            (t, v) for t, v in self.metric_history[key] if t >= cutoff
        ]

        # 需要至少 2 个数据点
        if len(self.metric_history[key]) < 2:
            return

        # 计算变化率
        oldest = self.metric_history[key][0]
        newest = self.metric_history[key][-1]
        time_diff = (newest[0] - oldest[0]).total_seconds()

        if time_diff <= 0:
            return

        rate = abs(newest[1] - oldest[1]) / time_diff * 60  # 每分钟变化量

        if rate >= rule.rate_threshold:
            self._trigger_alarm(rule, rate, data, context={"rate": rate, "window": rule.window_seconds})

    def _check_composite_rule(self, rule: CompositeRule) -> None:
        """检查组合规则.

        Args:
            rule: 规则对象.
        """
        # 检查所有子规则是否触发
        triggered_count = 0
        for sub_rule_id in rule.rules:
            if sub_rule_id in self.active_alarms:
                triggered_count += 1

        # 根据逻辑判断
        if rule.logic == "AND":
            triggered = triggered_count == len(rule.rules)
        else:  # OR
            triggered = triggered_count > 0

        if triggered:
            # 获取所有触发的子规则信息
            context = {
                "triggered_rules": [
                    self.active_alarms[rid].to_dict()
                    for rid in rule.rules
                    if rid in self.active_alarms
                ]
            }
            self._trigger_alarm(rule, None, {}, context=context)

    def _trigger_alarm(
        self,
        rule: Any,
        value: Optional[float],
        data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """触发报警.

        Args:
            rule: 规则对象.
            value: 触发值.
            data: 数据内容.
            context: 上下文数据.
        """
        # 检查冷却时间
        now = datetime.now()
        if rule.id in self.last_alarm_time:
            last_time = self.last_alarm_time[rule.id]
            if (now - last_time).total_seconds() < rule.cooldown_seconds:
                return  # 冷却期内，不触发

        # 创建报警记录
        alarm_id = self._generate_id("alarm")
        alarm = AlarmRecord(
            id=alarm_id,
            rule_id=rule.id,
            rule_name=rule.name,
            channel=rule.channel,
            level=rule.level,
            message=self._format_message(rule, value, data),
            value=value,
            context=context or {},
        )

        # 存储报警
        self.alarms.append(alarm)
        self.active_alarms[rule.id] = alarm
        self.last_alarm_time[rule.id] = now

        # 持久化
        self._persist_alarm(alarm)

        # 触发回调
        for callback in self.callbacks:
            try:
                callback(alarm)
            except Exception as e:
                print(f"⚠️ 报警回调执行失败：{e}")

        print(f"🚨 报警触发 [{rule.level}]: {alarm.message}")

    def _format_message(
        self, rule: Any, value: Optional[float], data: dict[str, Any]
    ) -> str:
        """格式化报警消息.

        Args:
            rule: 规则对象.
            value: 触发值.
            data: 数据内容.

        Returns:
            格式化后的消息.
        """
        message = rule.message
        if "{value}" in message and value is not None:
            message = message.replace("{value}", f"{value:.2f}")
        if "{channel}" in message:
            message = message.replace("{channel}", rule.channel)
        if "{metric}" in message:
            message = message.replace("{metric}", rule.metric)
        return message

    def _persist_alarm(self, alarm: AlarmRecord) -> None:
        """持久化报警记录.

        Args:
            alarm: 报警记录.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO alarm_records (id, rule_id, rule_name, channel, level, message, value, context_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                alarm.id,
                alarm.rule_id,
                alarm.rule_name,
                alarm.channel,
                alarm.level.name,
                alarm.message,
                alarm.value,
                json.dumps(alarm.context, ensure_ascii=False),
            ),
        )

        conn.commit()
        conn.close()

    def acknowledge_alarm(self, alarm_id: str) -> bool:
        """确认报警.

        Args:
            alarm_id: 报警 ID.

        Returns:
            是否成功确认.
        """
        with self._lock:
            for alarm in self.alarms:
                if alarm.id == alarm_id:
                    alarm.acknowledged = True

                    # 更新数据库
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE alarm_records SET acknowledged = TRUE WHERE id = ?",
                        (alarm_id,),
                    )
                    conn.commit()
                    conn.close()

                    return True
            return False

    def resolve_alarm(self, alarm_id: str) -> bool:
        """解决报警.

        Args:
            alarm_id: 报警 ID.

        Returns:
            是否成功解决.
        """
        with self._lock:
            for alarm in self.alarms:
                if alarm.id == alarm_id:
                    alarm.resolved = True
                    alarm.resolved_at = datetime.now()

                    # 从活动报警中移除
                    if alarm.rule_id in self.active_alarms:
                        del self.active_alarms[alarm.rule_id]

                    # 更新数据库
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE alarm_records
                        SET resolved = TRUE, resolved_at = ?
                        WHERE id = ?
                    """,
                        (alarm.resolved_at.isoformat(), alarm_id),
                    )
                    conn.commit()
                    conn.close()

                    return True
            return False

    def get_alarms(
        self,
        channel_name: Optional[str] = None,
        level: Optional[AlarmLevel] = None,
        acknowledged: Optional[bool] = None,
        resolved: Optional[bool] = None,
        limit: int = 100,
    ) -> list[AlarmRecord]:
        """查询报警记录.

        Args:
            channel_name: Channel 名称.
            level: 报警级别.
            acknowledged: 是否已确认.
            resolved: 是否已解决.
            limit: 返回数量限制.

        Returns:
            报警记录列表.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT id, rule_id, rule_name, channel, level, message, value, context_json, timestamp, acknowledged, resolved, resolved_at FROM alarm_records WHERE 1=1"
        params = []

        if channel_name:
            query += " AND channel = ?"
            params.append(channel_name)
        if level:
            query += " AND level = ?"
            params.append(level.name)
        if acknowledged is not None:
            query += " AND acknowledged = ?"
            params.append(acknowledged)
        if resolved is not None:
            query += " AND resolved = ?"
            params.append(resolved)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [
            AlarmRecord(
                id=row[0],
                rule_id=row[1],
                rule_name=row[2],
                channel=row[3],
                level=AlarmLevel.from_string(row[4]),
                message=row[5],
                value=row[6],
                context=json.loads(row[7]) if row[7] else {},
                timestamp=datetime.fromisoformat(row[8]),
                acknowledged=row[9],
                resolved=row[10],
                resolved_at=datetime.fromisoformat(row[11]) if row[11] else None,
            )
            for row in rows
        ]

    def get_active_alarms(self) -> list[AlarmRecord]:
        """获取活动报警（未解决）.

        Returns:
            活动报警列表.
        """
        return [alarm for alarm in self.alarms if not alarm.resolved]

    def get_stats(self) -> AlarmStats:
        """获取报警统计.

        Returns:
            报警统计对象.
        """
        stats = AlarmStats()
        now = datetime.now()
        last_24h = now - timedelta(hours=24)

        for alarm in self.alarms:
            stats.total_alarms += 1

            # 按级别统计
            level_name = alarm.level.name
            stats.by_level[level_name] = stats.by_level.get(level_name, 0) + 1

            # 按 Channel 统计
            stats.by_channel[alarm.channel] = stats.by_channel.get(alarm.channel, 0) + 1

            # 按规则统计
            stats.by_rule[alarm.rule_name] = stats.by_rule.get(alarm.rule_name, 0) + 1

            # 未确认/未解决统计
            if not alarm.acknowledged:
                stats.unacknowledged += 1
            if not alarm.resolved:
                stats.unresolved += 1

            # 最近 24 小时
            if alarm.timestamp >= last_24h:
                stats.last_24h += 1

        return stats

    def get_rules(self) -> dict[str, Any]:
        """获取所有规则.

        Returns:
            规则字典.
        """
        return {
            "threshold_rules": [r.to_dict() for r in self.rules.values()],
            "rate_rules": [r.to_dict() for r in self.rate_rules.values()],
            "composite_rules": [r.to_dict() for r in self.composite_rules.values()],
        }

    def start(self) -> None:
        """启动报警引擎（后台检查线程）."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._check_loop, daemon=True)
        self._thread.start()
        print("🚀 报警引擎已启动")

    def stop(self) -> None:
        """停止报警引擎."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        print("🛑 报警引擎已停止")

    def _check_loop(self) -> None:
        """后台检查循环."""
        while self._running:
            try:
                # 获取所有 Channel 的最新数据
                aggregated = self.integration.get_aggregated_data()
                for channel_name, channel_data in aggregated.items():
                    if isinstance(channel_data, dict) and "data" in channel_data:
                        self.check_channel(channel_name, channel_data["data"])
            except Exception as e:
                print(f"⚠️ 报警检查失败：{e}")

            time.sleep(1.0)  # 每秒检查一次


# 导出
__all__ = [
    "AlarmEngine",
    "AlarmLevel",
    "AlarmRule",
    "RateRule",
    "CompositeRule",
    "AlarmRecord",
    "AlarmStats",
    "ConditionType",
]
