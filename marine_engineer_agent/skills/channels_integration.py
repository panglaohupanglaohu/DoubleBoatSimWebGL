# -*- coding: utf-8 -*-
"""
Channels Integration - Channel 数据聚合器.

将 8 个 Marine Channels 的数据统一聚合、转换和验证，
为 Poseidon 数字孪生系统提供标准化的数据接口。

功能:
- Channel 注册与管理
- 数据聚合与格式转换
- 数据验证与清洗
- 统一数据查询接口

示例用法:
    >>> integration = ChannelsIntegration()
    >>> # 注册 Channel
    >>> integration.register_channel("engine_monitor", EngineMonitorChannel())
    >>> # 更新数据
    >>> integration.update_data("engine_monitor", {"rpm": 120, "load": 85})
    >>> # 获取聚合数据
    >>> data = integration.get_aggregated_data()
    >>> # 查询特定 Channel 数据
    >>> engine_data = integration.get_channel_data("engine_monitor")
"""

import json
import sqlite3
from collections import OrderedDict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

from .channels.base import Channel


class DataType(Enum):
    """数据类型枚举."""

    POSITION = "position"  # 位置数据
    STATUS = "status"  # 状态数据
    ALARM = "alarm"  # 报警数据
    SENSOR = "sensor"  # 传感器数据
    NAVIGATION = "navigation"  # 导航数据
    WEATHER = "weather"  # 气象数据
    CARGO = "cargo"  # 货物数据
    POWER = "power"  # 电力数据
    CUSTOM = "custom"  # 自定义数据


@dataclass
class ChannelData:
    """Channel 数据容器.

    Attributes:
        channel_name: Channel 名称.
        data_type: 数据类型.
        data: 数据内容 (字典).
        timestamp: 数据时间戳.
        metadata: 元数据.
    """

    channel_name: str
    data_type: DataType
    data: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典.

        Returns:
            字典表示.
        """
        return {
            "channel_name": self.channel_name,
            "data_type": self.data_type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """转换为 JSON 字符串.

        Returns:
            JSON 字符串.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class TimeSeriesPoint:
    """时序数据点.

    Attributes:
        channel_name: Channel 名称.
        metric_name: 指标名称.
        value: 指标值.
        unit: 单位.
        timestamp: 时间戳.
        tags: 标签.
    """

    channel_name: str
    metric_name: str
    value: float
    unit: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    tags: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典.

        Returns:
            字典表示.
        """
        return {
            "channel_name": self.channel_name,
            "metric_name": self.metric_name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
        }


@dataclass
class Event:
    """事件记录.

    Attributes:
        event_type: 事件类型.
        channel_name: Channel 名称.
        severity: 严重程度.
        message: 事件消息.
        data: 事件数据.
        timestamp: 事件时间.
        acknowledged: 是否已确认.
    """

    event_type: str
    channel_name: str
    severity: str
    message: str
    data: Optional[dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False

    def to_dict(self) -> dict[str, Any]:
        """转换为字典.

        Returns:
            字典表示.
        """
        return {
            "event_type": self.event_type,
            "channel_name": self.channel_name,
            "severity": self.severity,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
        }


class LRUCache:
    """LRU 缓存实现.

    使用 OrderedDict 实现简单的 LRU 缓存。
    """

    def __init__(self, max_size: int = 1000):
        """初始化 LRU 缓存.

        Args:
            max_size: 最大缓存条目数.
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, Any] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值.

        Args:
            key: 缓存键.

        Returns:
            缓存值，如果不存在则返回 None.
        """
        if key not in self.cache:
            return None
        # 移动到末尾 (最近使用)
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: str, value: Any) -> None:
        """存入缓存值.

        Args:
            key: 缓存键.
            value: 缓存值.
        """
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        # 如果超出最大大小，删除最旧的条目
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def clear(self) -> None:
        """清空缓存."""
        self.cache.clear()


class ChannelsIntegration:
    """Channel 数据聚合器.

    功能:
    - 注册和管理多个 Channel
    - 统一数据格式转换
    - 数据验证与清洗
    - 数据持久化 (SQLite)
    - 内存缓存

    示例用法:
        >>> integration = ChannelsIntegration(db_path="poseidon.db")
        >>> # 注册 Channel
        >>> from .channels.engine_monitor import EngineMonitorChannel
        >>> engine = EngineMonitorChannel(engine_id="ME-1")
        >>> integration.register_channel("engine_monitor", engine)
        >>>
        >>> # 更新数据
        >>> integration.update_data(
        ...     "engine_monitor",
        ...     {"rpm": 120, "load": 85, "temperature": 78.5}
        ... )
        >>>
        >>> # 获取数据
        >>> data = integration.get_channel_data("engine_monitor")
        >>> print(f"Engine RPM: {data['rpm']}")
        >>>
        >>> # 获取聚合数据
        >>> all_data = integration.get_aggregated_data()
    """

    def __init__(
        self,
        db_path: str = "poseidon.db",
        cache_size: int = 10000,
        enable_cache: bool = True,
    ):
        """初始化 Channel 数据聚合器.

        Args:
            db_path: SQLite 数据库路径.
            cache_size: 缓存大小.
            enable_cache: 是否启用缓存.
        """
        self.db_path = db_path
        self.channels: dict[str, Channel] = {}
        self.channel_data: dict[str, ChannelData] = {}
        self.time_series: list[TimeSeriesPoint] = []
        self.events: list[Event] = []
        self.callbacks: dict[str, list[Callable]] = {}

        # 缓存
        self.enable_cache = enable_cache
        self.cache = LRUCache(max_size=cache_size) if enable_cache else None

        # 初始化数据库
        self._init_database()

    def _init_database(self) -> None:
        """初始化 SQLite 数据库."""
        db_path = Path(self.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 创建 channel_data 表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS channel_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT NOT NULL,
                data_type TEXT NOT NULL,
                data_json TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """
        )

        # 创建 time_series_data 表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS time_series_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                unit TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        """
        )

        # 创建 events 表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                channel_name TEXT NOT NULL,
                severity TEXT,
                message TEXT NOT NULL,
                data_json TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                acknowledged BOOLEAN DEFAULT FALSE
            )
        """
        )

        # 创建索引
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_channel_name ON channel_data(channel_name)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON channel_data(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_data_type ON channel_data(data_type)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_ts_channel_metric ON time_series_data(channel_name, metric_name)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_ts_timestamp ON time_series_data(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_event_channel ON events(channel_name)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_event_timestamp ON events(timestamp)"
        )

        conn.commit()
        conn.close()

    def register_channel(self, name: str, channel: Channel) -> None:
        """注册 Channel.

        Args:
            name: Channel 名称.
            channel: Channel 实例.
        """
        self.channels[name] = channel
        self.callbacks[name] = []
        print(f"✅ Channel '{name}' 已注册")

    def unregister_channel(self, name: str) -> bool:
        """注销 Channel.

        Args:
            name: Channel 名称.

        Returns:
            是否成功注销.
        """
        if name in self.channels:
            del self.channels[name]
            if name in self.callbacks:
                del self.callbacks[name]
            print(f"❌ Channel '{name}' 已注销")
            return True
        return False

    def add_callback(self, channel_name: str, callback: Callable) -> None:
        """添加数据更新回调.

        Args:
            channel_name: Channel 名称.
            callback: 回调函数.
        """
        if channel_name not in self.callbacks:
            self.callbacks[channel_name] = []
        self.callbacks[channel_name].append(callback)

    def update_data(
        self,
        channel_name: str,
        data: dict[str, Any],
        data_type: Optional[DataType] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ChannelData:
        """更新 Channel 数据.

        Args:
            channel_name: Channel 名称.
            data: 数据内容.
            data_type: 数据类型 (自动推断如果未提供).
            metadata: 元数据.

        Returns:
            ChannelData 对象.

        Raises:
            ValueError: 如果 Channel 未注册.
        """
        if channel_name not in self.channels:
            raise ValueError(f"Channel '{channel_name}' 未注册")

        # 自动推断数据类型
        if data_type is None:
            data_type = self._infer_data_type(channel_name, data)

        # 创建 ChannelData 对象
        channel_data = ChannelData(
            channel_name=channel_name,
            data_type=data_type,
            data=data,
            metadata=metadata or {},
        )

        # 存储数据
        self.channel_data[channel_name] = channel_data

        # 存入缓存
        if self.enable_cache and self.cache:
            cache_key = f"channel:{channel_name}"
            self.cache.put(cache_key, channel_data)

        # 持久化到数据库
        self._persist_channel_data(channel_data)

        # 提取时序数据
        self._extract_time_series(channel_name, data)

        # 触发回调
        self._trigger_callbacks(channel_name, channel_data)

        return channel_data

    def _infer_data_type(self, channel_name: str, data: dict[str, Any]) -> DataType:
        """自动推断数据类型.

        Args:
            channel_name: Channel 名称.
            data: 数据内容.

        Returns:
            推断的数据类型.
        """
        # 根据 Channel 名称推断
        channel_type_map = {
            "nmea_parser": DataType.NAVIGATION,
            "vessel_ais": DataType.POSITION,
            "engine_monitor": DataType.STATUS,
            "power_management": DataType.POWER,
            "navigation_data": DataType.NAVIGATION,
            "cargo_monitor": DataType.CARGO,
            "weather_routing": DataType.WEATHER,
            "web": DataType.CUSTOM,
        }

        if channel_name in channel_type_map:
            return channel_type_map[channel_name]

        # 根据数据内容推断
        if "latitude" in data or "longitude" in data:
            return DataType.POSITION
        if "alarm" in data or "status" in data:
            return DataType.STATUS
        if "temperature" in data or "pressure" in data:
            return DataType.SENSOR

        return DataType.CUSTOM

    def _extract_time_series(
        self, channel_name: str, data: dict[str, Any]
    ) -> None:
        """从数据中提取时序数据点.

        Args:
            channel_name: Channel 名称.
            data: 数据内容.
        """
        timestamp = datetime.now()

        for key, value in data.items():
            if isinstance(value, (int, float)):
                point = TimeSeriesPoint(
                    channel_name=channel_name,
                    metric_name=key,
                    value=float(value),
                    unit=self._guess_unit(key),
                    timestamp=timestamp,
                )
                self.time_series.append(point)

                # 限制内存中的时序数据量
                if len(self.time_series) > 100000:
                    self.time_series = self.time_series[-50000:]

    def _guess_unit(self, metric_name: str) -> Optional[str]:
        """猜测指标单位.

        Args:
            metric_name: 指标名称.

        Returns:
            单位字符串.
        """
        unit_map = {
            "rpm": "rpm",
            "speed": "knots",
            "temperature": "°C",
            "pressure": "bar",
            "load": "%",
            "fuel": "kg/h",
            "voltage": "V",
            "current": "A",
            "frequency": "Hz",
            "latitude": "°",
            "longitude": "°",
            "course": "°",
            "heading": "°",
        }

        metric_lower = metric_name.lower()
        for key, unit in unit_map.items():
            if key in metric_lower:
                return unit
        return None

    def _persist_channel_data(self, channel_data: ChannelData) -> None:
        """持久化 Channel 数据到 SQLite.

        Args:
            channel_data: Channel 数据对象.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO channel_data (channel_name, data_type, data_json, metadata)
            VALUES (?, ?, ?, ?)
        """,
            (
                channel_data.channel_name,
                channel_data.data_type.value,
                channel_data.to_json(),
                json.dumps(channel_data.metadata, ensure_ascii=False),
            ),
        )

        conn.commit()
        conn.close()

    def _trigger_callbacks(self, channel_name: str, data: ChannelData) -> None:
        """触发数据更新回调.

        Args:
            channel_name: Channel 名称.
            data: Channel 数据.
        """
        if channel_name in self.callbacks:
            for callback in self.callbacks[channel_name]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"⚠️ 回调执行失败：{e}")

    def get_channel_data(
        self, channel_name: str, from_cache: bool = True
    ) -> Optional[ChannelData]:
        """获取 Channel 数据.

        Args:
            channel_name: Channel 名称.
            from_cache: 是否从缓存获取.

        Returns:
            ChannelData 对象，如果不存在则返回 None.
        """
        # 尝试从缓存获取
        if from_cache and self.enable_cache and self.cache:
            cache_key = f"channel:{channel_name}"
            cached = self.cache.get(cache_key)
            if cached:
                return cached

        # 从内存获取
        if channel_name in self.channel_data:
            return self.channel_data[channel_name]

        # 从数据库获取最新记录
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT data_json FROM channel_data
            WHERE channel_name = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """,
            (channel_name,),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            data_dict = json.loads(row[0])
            return ChannelData(
                channel_name=data_dict["channel_name"],
                data_type=DataType(data_dict["data_type"]),
                data=data_dict["data"],
                timestamp=datetime.fromisoformat(data_dict["timestamp"]),
                metadata=data_dict.get("metadata", {}),
            )

        return None

    def get_aggregated_data(self) -> dict[str, Any]:
        """获取所有 Channel 的聚合数据.

        Returns:
            聚合数据字典.
        """
        result = {}
        for channel_name in self.channels:
            data = self.get_channel_data(channel_name)
            if data:
                result[channel_name] = data.to_dict()
        return result

    def get_time_series(
        self,
        channel_name: Optional[str] = None,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> list[TimeSeriesPoint]:
        """查询时序数据.

        Args:
            channel_name: Channel 名称 (可选).
            metric_name: 指标名称 (可选).
            start_time: 开始时间 (可选).
            end_time: 结束时间 (可选).
            limit: 返回数量限制.

        Returns:
            时序数据点列表.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT channel_name, metric_name, metric_value, unit, timestamp, tags FROM time_series_data WHERE 1=1"
        params = []

        if channel_name:
            query += " AND channel_name = ?"
            params.append(channel_name)
        if metric_name:
            query += " AND metric_name = ?"
            params.append(metric_name)
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [
            TimeSeriesPoint(
                channel_name=row[0],
                metric_name=row[1],
                value=row[2],
                unit=row[3],
                timestamp=datetime.fromisoformat(row[4]),
                tags=json.loads(row[5]) if row[5] else {},
            )
            for row in rows
        ]

    def record_event(self, event: Event) -> None:
        """记录事件.

        Args:
            event: 事件对象.
        """
        self.events.append(event)

        # 持久化到数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO events (event_type, channel_name, severity, message, data_json, acknowledged)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                event.event_type,
                event.channel_name,
                event.severity,
                event.message,
                json.dumps(event.data, ensure_ascii=False) if event.data else None,
                event.acknowledged,
            ),
        )

        conn.commit()
        conn.close()

    def get_events(
        self,
        channel_name: Optional[str] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> list[Event]:
        """查询事件.

        Args:
            channel_name: Channel 名称 (可选).
            event_type: 事件类型 (可选).
            severity: 严重程度 (可选).
            limit: 返回数量限制.

        Returns:
            事件列表.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT event_type, channel_name, severity, message, data_json, timestamp, acknowledged FROM events WHERE 1=1"
        params = []

        if channel_name:
            query += " AND channel_name = ?"
            params.append(channel_name)
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        if severity:
            query += " AND severity = ?"
            params.append(severity)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [
            Event(
                event_type=row[0],
                channel_name=row[1],
                severity=row[2],
                message=row[3],
                data=json.loads(row[4]) if row[4] else None,
                timestamp=datetime.fromisoformat(row[5]),
                acknowledged=row[6],
            )
            for row in rows
        ]

    def acknowledge_event(self, event_id: int) -> bool:
        """确认事件.

        Args:
            event_id: 事件 ID.

        Returns:
            是否成功确认.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE events SET acknowledged = TRUE WHERE id = ?", (event_id,)
        )

        affected = cursor.rowcount
        conn.commit()
        conn.close()

        return affected > 0

    def get_status(self) -> dict[str, Any]:
        """获取集成状态.

        Returns:
            状态字典.
        """
        return {
            "registered_channels": list(self.channels.keys()),
            "active_channels": len(self.channel_data),
            "cache_enabled": self.enable_cache,
            "cache_size": len(self.cache.cache) if self.cache else 0,
            "time_series_count": len(self.time_series),
            "events_count": len(self.events),
            "database": self.db_path,
        }


# 导出
__all__ = [
    "ChannelsIntegration",
    "ChannelData",
    "TimeSeriesPoint",
    "Event",
    "DataType",
    "LRUCache",
]
