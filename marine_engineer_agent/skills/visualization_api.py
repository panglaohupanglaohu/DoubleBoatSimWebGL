# -*- coding: utf-8 -*-
"""
Visualization API - 数据可视化接口.

提供 REST API 端点用于前端图表展示，支持时序数据聚合、实时数据流、多种数据格式。

功能:
- REST API 端点用于前端图表
- 时序数据聚合（平均/最大/最小/趋势）
- 实时数据流接口（WebSocket）
- 支持多种数据格式（JSON, CSV, PNG 图表）
- 数据导出功能

API 端点:
- GET /api/viz/timeseries - 时序数据
- GET /api/viz/aggregate - 聚合数据
- GET /api/viz/stats - 统计数据
- GET /api/viz/export/csv - CSV 导出
- GET /api/viz/export/png - PNG 图表
- WebSocket /ws/viz - 实时数据流

示例用法:
    >>> from .channels_integration import ChannelsIntegration
    >>> from .alarm_engine import AlarmEngine
    >>>
    >>> integration = ChannelsIntegration()
    >>> alarm_engine = AlarmEngine(integration)
    >>>
    >>> # 创建可视化 API
    >>> viz_api = VisualizationAPI(integration, alarm_engine, port=8081)
    >>> viz_api.start()
"""

import base64
import csv
import io
import json
import logging
import math
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import parse_qs, urlparse

try:
    from .channels_integration import ChannelsIntegration, TimeSeriesPoint
    from .alarm_engine import AlarmEngine, AlarmLevel, AlarmStats
except ImportError:
    from channels_integration import ChannelsIntegration, TimeSeriesPoint
    from alarm_engine import AlarmEngine, AlarmLevel, AlarmStats

try:
    import matplotlib
    matplotlib.use("Agg")  # 非交互式后端
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None  # type: ignore

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    WebSocketServerProtocol = Any  # type: ignore


class AggregationType(Enum):
    """聚合类型."""

    AVG = "avg"  # 平均值
    MAX = "max"  # 最大值
    MIN = "min"  # 最小值
    SUM = "sum"  # 总和
    COUNT = "count"  # 计数
    STD = "std"  # 标准差
    TREND = "trend"  # 趋势


class TimeRange(Enum):
    """时间范围."""

    HOUR_1 = "1h"  # 1 小时
    HOUR_6 = "6h"  # 6 小时
    HOUR_12 = "12h"  # 12 小时
    DAY_1 = "1d"  # 1 天
    DAY_7 = "7d"  # 7 天
    DAY_30 = "30d"  # 30 天
    CUSTOM = "custom"  # 自定义


@dataclass
class TimeSeriesData:
    """时序数据容器.

    Attributes:
        channel: Channel 名称.
        metric: 指标名称.
        points: 数据点列表.
        start_time: 开始时间.
        end_time: 结束时间.
    """

    channel: str
    metric: str
    points: list[dict[str, Any]] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典."""
        return {
            "channel": self.channel,
            "metric": self.metric,
            "points": self.points,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "count": len(self.points),
        }


@dataclass
class AggregateResult:
    """聚合结果.

    Attributes:
        channel: Channel 名称.
        metric: 指标名称.
        avg: 平均值.
        max: 最大值.
        min: 最小值.
        sum: 总和.
        count: 计数.
        std: 标准差.
        trend: 趋势 (正=上升，负=下降).
        start_time: 开始时间.
        end_time: 结束时间.
    """

    channel: str
    metric: str
    avg: Optional[float] = None
    max: Optional[float] = None
    min: Optional[float] = None
    sum: Optional[float] = None
    count: int = 0
    std: Optional[float] = None
    trend: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典."""
        return {
            "channel": self.channel,
            "metric": self.metric,
            "avg": round(self.avg, 4) if self.avg is not None else None,
            "max": round(self.max, 4) if self.max is not None else None,
            "min": round(self.min, 4) if self.min is not None else None,
            "sum": round(self.sum, 4) if self.sum is not None else None,
            "count": self.count,
            "std": round(self.std, 4) if self.std is not None else None,
            "trend": round(self.trend, 6) if self.trend is not None else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


class VisualizationAPI:
    """数据可视化 API.

    功能:
    - REST API 端点
    - 时序数据聚合
    - 实时 WebSocket 推送
    - 图表生成
    - 数据导出

    示例用法:
        >>> integration = ChannelsIntegration()
        >>> alarm_engine = AlarmEngine(integration)
        >>> viz = VisualizationAPI(integration, alarm_engine, port=8081)
        >>> viz.start()
    """

    def __init__(
        self,
        integration: ChannelsIntegration,
        alarm_engine: Optional[AlarmEngine] = None,
        host: str = "0.0.0.0",
        port: int = 8081,
        db_path: str = "poseidon.db",
    ):
        """初始化可视化 API.

        Args:
            integration: ChannelsIntegration 实例.
            alarm_engine: AlarmEngine 实例（可选）.
            host: 监听地址.
            port: HTTP 端口.
            db_path: SQLite 数据库路径.
        """
        self.integration = integration
        self.alarm_engine = alarm_engine
        self.host = host
        self.port = port
        self.db_path = db_path

        # HTTP 服务器
        self.http_server: Optional[HTTPServer] = None
        self._http_thread: Optional[threading.Thread] = None

        # WebSocket 服务器
        self.ws_server = None
        self.ws_clients: set = set()
        self._ws_thread: Optional[threading.Thread] = None
        self._ws_running = False

        # 日志
        self.logger = logging.getLogger("VisualizationAPI")

        # 设置 API 处理器的实例
        VisualizationAPIHandler.viz_instance = self

    def _get_time_range(self, range_str: str) -> tuple[datetime, datetime]:
        """解析时间范围.

        Args:
            range_str: 时间范围字符串.

        Returns:
            (开始时间，结束时间) 元组.
        """
        end_time = datetime.now()

        if range_str == "1h":
            start_time = end_time - timedelta(hours=1)
        elif range_str == "6h":
            start_time = end_time - timedelta(hours=6)
        elif range_str == "12h":
            start_time = end_time - timedelta(hours=12)
        elif range_str == "1d":
            start_time = end_time - timedelta(days=1)
        elif range_str == "7d":
            start_time = end_time - timedelta(days=7)
        elif range_str == "30d":
            start_time = end_time - timedelta(days=30)
        else:
            start_time = end_time - timedelta(hours=1)  # 默认 1 小时

        return start_time, end_time

    def get_timeseries(
        self,
        channel_name: str,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        time_range: str = "1h",
        limit: int = 1000,
    ) -> list[TimeSeriesData]:
        """获取时序数据.

        Args:
            channel_name: Channel 名称.
            metric_name: 指标名称（可选，None 表示所有）.
            start_time: 开始时间.
            end_time: 结束时间.
            time_range: 时间范围.
            limit: 返回数量限制.

        Returns:
            时序数据列表.
        """
        if start_time is None or end_time is None:
            start_time, end_time = self._get_time_range(time_range)

        points = self.integration.get_time_series(
            channel_name=channel_name,
            metric_name=metric_name,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

        # 按 metric 分组
        metrics_data: dict[str, TimeSeriesData] = {}
        for point in points:
            key = point.metric_name
            if key not in metrics_data:
                metrics_data[key] = TimeSeriesData(
                    channel=channel_name,
                    metric=key,
                    start_time=start_time,
                    end_time=end_time,
                )

            metrics_data[key].points.append({
                "timestamp": point.timestamp.isoformat(),
                "value": point.value,
                "unit": point.unit,
            })

        return list(metrics_data.values())

    def get_aggregate(
        self,
        channel_name: str,
        metric_name: Optional[str] = None,
        time_range: str = "1h",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> list[AggregateResult]:
        """获取聚合数据.

        Args:
            channel_name: Channel 名称.
            metric_name: 指标名称（可选）.
            time_range: 时间范围.
            start_time: 开始时间.
            end_time: 结束时间.

        Returns:
            聚合结果列表.
        """
        if start_time is None or end_time is None:
            start_time, end_time = self._get_time_range(time_range)

        points = self.integration.get_time_series(
            channel_name=channel_name,
            metric_name=metric_name,
            start_time=start_time,
            end_time=end_time,
            limit=10000,
        )

        # 按 metric 分组计算
        metrics_values: dict[str, list[float]] = {}
        for point in points:
            key = point.metric_name
            if key not in metrics_values:
                metrics_values[key] = []
            metrics_values[key].append(point.value)

        results = []
        for metric, values in metrics_values.items():
            if not values:
                continue

            result = AggregateResult(
                channel=channel_name,
                metric=metric,
                avg=sum(values) / len(values),
                max=max(values),
                min=min(values),
                sum=sum(values),
                count=len(values),
                start_time=start_time,
                end_time=end_time,
            )

            # 计算标准差
            if len(values) > 1:
                mean = result.avg
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                result.std = math.sqrt(variance)

            # 计算趋势（简单线性回归斜率）
            if len(values) > 1:
                n = len(values)
                x_mean = n / 2
                y_mean = result.avg
                numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
                denominator = sum((i - x_mean) ** 2 for i in range(n))
                if denominator != 0:
                    result.trend = numerator / denominator

            results.append(result)

        return results

    def get_alarm_stats(self) -> Optional[dict[str, Any]]:
        """获取报警统计.

        Returns:
            报警统计字典，如果未配置 alarm_engine 则返回 None.
        """
        if not self.alarm_engine:
            return None

        stats = self.alarm_engine.get_stats()
        return stats.to_dict()

    def get_active_alarms(self) -> list[dict[str, Any]]:
        """获取活动报警.

        Returns:
            活动报警列表.
        """
        if not self.alarm_engine:
            return []

        alarms = self.alarm_engine.get_active_alarms()
        return [alarm.to_dict() for alarm in alarms]

    def export_csv(
        self,
        channel_name: str,
        metric_name: Optional[str] = None,
        time_range: str = "1h",
    ) -> str:
        """导出 CSV 数据.

        Args:
            channel_name: Channel 名称.
            metric_name: 指标名称.
            time_range: 时间范围.

        Returns:
            CSV 字符串.
        """
        data = self.get_timeseries(
            channel_name=channel_name,
            metric_name=metric_name,
            time_range=time_range,
        )

        output = io.StringIO()
        writer = csv.writer(output)

        # 写入表头
        writer.writerow(["timestamp", "channel", "metric", "value", "unit"])

        # 写入数据
        for ts_data in data:
            for point in ts_data.points:
                writer.writerow([
                    point["timestamp"],
                    ts_data.channel,
                    ts_data.metric,
                    point["value"],
                    point.get("unit", ""),
                ])

        return output.getvalue()

    def generate_chart(
        self,
        channel_name: str,
        metric_name: str,
        time_range: str = "1h",
        title: Optional[str] = None,
        width: int = 800,
        height: int = 600,
    ) -> Optional[bytes]:
        """生成 PNG 图表.

        Args:
            channel_name: Channel 名称.
            metric_name: 指标名称.
            time_range: 时间范围.
            title: 图表标题.
            width: 宽度（像素）.
            height: 高度（像素）.

        Returns:
            PNG 数据（字节），如果 matplotlib 不可用则返回 None.
        """
        if not MATPLOTLIB_AVAILABLE or plt is None:
            return None

        data = self.get_timeseries(
            channel_name=channel_name,
            metric_name=metric_name,
            time_range=time_range,
        )

        if not data or not data[0].points:
            return None

        ts_data = data[0]

        # 准备数据
        timestamps = [datetime.fromisoformat(p["timestamp"]) for p in ts_data.points]
        values = [p["value"] for p in ts_data.points]

        # 创建图表
        fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)

        ax.plot(timestamps, values, marker="o", linestyle="-", markersize=3)

        # 格式化 x 轴时间
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        plt.xticks(rotation=45)

        # 设置标签
        ax.set_xlabel("时间")
        ax.set_ylabel(f"{metric_name} ({ts_data.points[0].get('unit', '')})")
        ax.set_title(title or f"{channel_name} - {metric_name}")

        # 添加网格
        ax.grid(True, alpha=0.3)

        # 自动调整布局
        plt.tight_layout()

        # 保存到字节
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100)
        buf.seek(0)
        png_data = buf.getvalue()

        plt.close(fig)

        return png_data

    def broadcast_to_ws(self, data: dict[str, Any]) -> None:
        """广播数据到 WebSocket 客户端.

        Args:
            data: 数据字典.
        """
        if not self._ws_running:
            return

        message = json.dumps(data, ensure_ascii=False)

        disconnected = set()
        for client in self.ws_clients:
            try:
                # 异步发送
                import asyncio
                loop = asyncio.new_event_loop()
                loop.run_until_complete(client.send(message))
                loop.close()
            except Exception:
                disconnected.add(client)

        # 清理断开的客户端
        self.ws_clients -= disconnected

    def _run_http_server(self) -> None:
        """运行 HTTP 服务器."""
        self.http_server = HTTPServer((self.host, self.port), VisualizationAPIHandler)
        self.logger.info(f"🌐 Visualization API: http://{self.host}:{self.port}")
        self.http_server.serve_forever()

    def _run_ws_server(self) -> None:
        """运行 WebSocket 服务器."""
        if not WEBSOCKETS_AVAILABLE:
            self.logger.warning("⚠️ websockets 库未安装，WebSocket 不可用")
            return

        async def handler(websocket: WebSocketServerProtocol) -> None:
            self.ws_clients.add(websocket)
            self.logger.info(f"🔌 WebSocket 客户端连接 (当前：{len(self.ws_clients)}个)")

            try:
                async for message in websocket:
                    # 处理客户端消息（订阅等）
                    try:
                        data = json.loads(message)
                        # 可以添加订阅逻辑
                        await websocket.send(json.dumps({
                            "type": "ack",
                            "message": "消息已接收",
                        }))
                    except json.JSONDecodeError:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "无效的 JSON",
                        }))
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self.ws_clients.discard(websocket)
                self.logger.info(f"🔌 WebSocket 客户端断开 (当前：{len(self.ws_clients)}个)")

        self._ws_running = True
        self.ws_server = websockets.serve(handler, self.host, self.port + 1)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.ws_server)
        self.logger.info(f"📡 WebSocket: ws://{self.host}:{self.port + 1}")
        loop.run_forever()

    def start(self) -> None:
        """启动服务器."""
        # 启动 HTTP 服务器
        self._http_thread = threading.Thread(target=self._run_http_server, daemon=True)
        self._http_thread.start()

        # 启动 WebSocket 服务器
        self._ws_thread = threading.Thread(target=self._run_ws_server, daemon=True)
        self._ws_thread.start()

        self.logger.info("✅ Visualization API 已启动")

    def stop(self) -> None:
        """停止服务器."""
        self._ws_running = False

        if self.http_server:
            self.http_server.shutdown()

        self.logger.info("🛑 Visualization API 已停止")


class VisualizationAPIHandler(BaseHTTPRequestHandler):
    """Visualization API HTTP 处理器."""

    # 类变量，由服务器实例设置
    viz_instance: Optional[VisualizationAPI] = None

    def log_message(self, format: str, *args) -> None:
        """自定义日志格式."""
        if self.viz_instance:
            self.viz_instance.logger.info(f"{self.address_string()} - {format % args}")

    def _set_headers(self, status: int = 200, content_type: str = "application/json") -> None:
        """设置响应头."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, data: Any, status: int = 200) -> None:
        """发送 JSON 响应."""
        self._set_headers(status)
        response = json.dumps(data, ensure_ascii=False, default=str)
        self.wfile.write(response.encode("utf-8"))

    def _send_error(self, message: str, status: int = 400) -> None:
        """发送错误响应."""
        self._send_json({"error": message}, status)

    def _send_png(self, data: bytes) -> None:
        """发送 PNG 响应."""
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def _send_csv(self, data: str) -> None:
        """发送 CSV 响应."""
        self.send_response(200)
        self.send_header("Content-Type", "text/csv; charset=utf-8")
        self.send_header("Content-Length", str(len(data.encode("utf-8"))))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data.encode("utf-8"))

    def do_OPTIONS(self) -> None:
        """处理 CORS 预检请求."""
        self._set_headers(204)

    def do_GET(self) -> None:
        """处理 GET 请求."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if not self.viz_instance:
            self._send_error("Server not initialized", 500)
            return

        # 路由匹配
        if path == "/":
            self._handle_root()
        elif path == "/api/viz/timeseries":
            self._handle_timeseries(query)
        elif path == "/api/viz/aggregate":
            self._handle_aggregate(query)
        elif path == "/api/viz/stats":
            self._handle_stats()
        elif path == "/api/viz/alarms":
            self._handle_alarms()
        elif path == "/api/viz/export/csv":
            self._handle_export_csv(query)
        elif path == "/api/viz/export/png":
            self._handle_export_png(query)
        elif path == "/api/viz/channels":
            self._handle_channels()
        else:
            self._send_error("Not Found", 404)

    def _handle_root(self) -> None:
        """处理根路径请求."""
        self._send_json({
            "name": "Visualization API",
            "version": "1.0.0",
            "description": "Marine Channels Data Visualization API",
            "endpoints": {
                "GET /api/viz/timeseries": "获取时序数据",
                "GET /api/viz/aggregate": "获取聚合数据",
                "GET /api/viz/stats": "获取统计数据",
                "GET /api/viz/alarms": "获取活动报警",
                "GET /api/viz/export/csv": "导出 CSV",
                "GET /api/viz/export/png": "导出 PNG 图表",
                "GET /api/viz/channels": "获取所有 Channel",
                "WebSocket /ws/viz": "实时数据流 (端口 +1)",
            },
        })

    def _handle_timeseries(self, query: dict) -> None:
        """处理时序数据请求."""
        channel_name = query.get("channel", [None])[0]
        if not channel_name:
            self._send_error("缺少 channel 参数")
            return

        metric_name = query.get("metric", [None])[0]
        time_range = query.get("range", ["1h"])[0]
        limit = int(query.get("limit", [1000])[0])

        data = self.viz_instance.get_timeseries(
            channel_name=channel_name,
            metric_name=metric_name,
            time_range=time_range,
            limit=limit,
        )

        self._send_json({
            "data": [d.to_dict() for d in data],
            "count": len(data),
        })

    def _handle_aggregate(self, query: dict) -> None:
        """处理聚合数据请求."""
        channel_name = query.get("channel", [None])[0]
        if not channel_name:
            self._send_error("缺少 channel 参数")
            return

        metric_name = query.get("metric", [None])[0]
        time_range = query.get("range", ["1h"])[0]

        results = self.viz_instance.get_aggregate(
            channel_name=channel_name,
            metric_name=metric_name,
            time_range=time_range,
        )

        self._send_json({
            "data": [r.to_dict() for r in results],
            "count": len(results),
        })

    def _handle_stats(self) -> None:
        """处理统计请求."""
        # Channel 统计
        channels = list(self.viz_instance.integration.channels.keys())
        aggregated = self.viz_instance.integration.get_aggregated_data()

        stats = {
            "channels": {
                "total": len(channels),
                "active": len(aggregated),
                "names": channels,
            },
            "time_series": {
                "count": len(self.viz_instance.integration.time_series),
            },
        }

        # 报警统计
        if self.viz_instance.alarm_engine:
            stats["alarms"] = self.viz_instance.get_alarm_stats()

        self._send_json(stats)

    def _handle_alarms(self) -> None:
        """处理报警请求."""
        if not self.viz_instance.alarm_engine:
            self._send_json({"alarms": []})
            return

        alarms = self.viz_instance.get_active_alarms()
        self._send_json({
            "alarms": alarms,
            "count": len(alarms),
        })

    def _handle_export_csv(self, query: dict) -> None:
        """处理 CSV 导出请求."""
        channel_name = query.get("channel", [None])[0]
        if not channel_name:
            self._send_error("缺少 channel 参数")
            return

        metric_name = query.get("metric", [None])[0]
        time_range = query.get("range", ["1h"])[0]

        csv_data = self.viz_instance.export_csv(
            channel_name=channel_name,
            metric_name=metric_name,
            time_range=time_range,
        )

        self._send_csv(csv_data)

    def _handle_export_png(self, query: dict) -> None:
        """处理 PNG 导出请求."""
        if not MATPLOTLIB_AVAILABLE:
            self._send_error("matplotlib 未安装", 503)
            return

        channel_name = query.get("channel", [None])[0]
        if not channel_name:
            self._send_error("缺少 channel 参数")
            return

        metric_name = query.get("metric", [None])[0]
        if not metric_name:
            self._send_error("缺少 metric 参数")
            return

        time_range = query.get("range", ["1h"])[0]
        title = query.get("title", [None])[0]
        width = int(query.get("width", [800])[0])
        height = int(query.get("height", [600])[0])

        png_data = self.viz_instance.generate_chart(
            channel_name=channel_name,
            metric_name=metric_name,
            time_range=time_range,
            title=title,
            width=width,
            height=height,
        )

        if png_data:
            self._send_png(png_data)
        else:
            self._send_error("无数据可生成图表", 404)

    def _handle_channels(self) -> None:
        """处理 Channel 列表请求."""
        channels = list(self.viz_instance.integration.channels.keys())
        self._send_json({
            "channels": channels,
            "count": len(channels),
        })


# 导出
__all__ = [
    "VisualizationAPI",
    "TimeSeriesData",
    "AggregateResult",
    "AggregationType",
    "TimeRange",
]
