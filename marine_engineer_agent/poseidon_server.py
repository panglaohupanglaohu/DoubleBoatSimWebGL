#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Poseidon Server - Poseidon 数字孪生服务器.

提供 REST API 和 WebSocket 接口，用于访问和管理 Marine Channel 数据。

功能:
- REST API 路由
- Channel 数据管理
- WebSocket 实时推送
- 数据持久化
- 系统监控

示例用法:
    >>> # 启动服务器
    >>> python poseidon_server.py --port 8080 --ws-port 8765
    >>>
    >>> # API 访问
    >>> curl http://localhost:8080/api/channels
    >>> curl http://localhost:8080/api/data/engine_monitor
    >>> curl http://localhost:8080/api/events
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

# 添加父目录到路径以支持导入
sys.path.insert(0, str(Path(__file__).parent))

from .channels_integration import (
    ChannelsIntegration,
    ChannelData,
    Event,
    DataType,
)
from .realtime_data_bridge import RealtimeDataBridge


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("PoseidonServer")


class PoseidonAPIHandler(BaseHTTPRequestHandler):
    """Poseidon REST API 处理器."""

    # 类变量，由服务器设置
    server_instance: Optional["PoseidonServer"] = None

    def log_message(self, format: str, *args) -> None:
        """自定义日志格式."""
        logger.info(f"{self.address_string()} - {format % args}")

    def _set_headers(self, status: int = 200, content_type: str = "application/json") -> None:
        """设置响应头.

        Args:
            status: HTTP 状态码.
            content_type: 内容类型.
        """
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, data: Any, status: int = 200) -> None:
        """发送 JSON 响应.

        Args:
            data: 数据.
            status: HTTP 状态码.
        """
        self._set_headers(status)
        response = json.dumps(data, ensure_ascii=False, default=str)
        self.wfile.write(response.encode("utf-8"))

    def _send_error(self, message: str, status: int = 400) -> None:
        """发送错误响应.

        Args:
            message: 错误消息.
            status: HTTP 状态码.
        """
        self._send_json({"error": message}, status)

    def do_OPTIONS(self) -> None:
        """处理 CORS 预检请求."""
        self._set_headers(204)

    def do_GET(self) -> None:
        """处理 GET 请求."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # 路由匹配
        if path == "/":
            self._handle_root()
        elif path == "/api/health":
            self._handle_health()
        elif path == "/api/channels":
            self._handle_get_channels()
        elif path.startswith("/api/data/"):
            channel_name = path.split("/api/data/")[1]
            self._handle_get_data(channel_name)
        elif path == "/api/data":
            self._handle_get_all_data()
        elif path == "/api/timeseries":
            self._handle_get_timeseries(query)
        elif path == "/api/events":
            self._handle_get_events(query)
        elif path == "/api/status":
            self._handle_get_status()
        else:
            self._send_error("Not Found", 404)

    def do_POST(self) -> None:
        """处理 POST 请求."""
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_error("Invalid JSON")
            return

        # 路由匹配
        if path.startswith("/api/data/"):
            channel_name = path.split("/api/data/")[1]
            self._handle_update_data(channel_name, data)
        elif path == "/api/events":
            self._handle_create_event(data)
        elif path == "/api/events/acknowledge":
            event_id = data.get("event_id")
            if event_id:
                self._handle_acknowledge_event(event_id)
            else:
                self._send_error("Missing event_id")
        else:
            self._send_error("Not Found", 404)

    def _handle_root(self) -> None:
        """处理根路径请求."""
        self._send_json({
            "name": "Poseidon Server",
            "version": "1.0.0",
            "description": "Marine Channels Integration Server",
            "endpoints": {
                "GET /api/health": "健康检查",
                "GET /api/channels": "获取所有 Channel",
                "GET /api/data": "获取所有数据",
                "GET /api/data/{channel}": "获取特定 Channel 数据",
                "POST /api/data/{channel}": "更新 Channel 数据",
                "GET /api/timeseries": "查询时序数据",
                "GET /api/events": "查询事件",
                "POST /api/events": "创建事件",
                "POST /api/events/acknowledge": "确认事件",
                "GET /api/status": "获取服务器状态",
            },
            "websocket": f"ws://{self.server.host}:{self.server.ws_port}",
        })

    def _handle_health(self) -> None:
        """处理健康检查."""
        self._send_json({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": datetime.now() - self.server.start_time if hasattr(self.server, "start_time") else None,
        })

    def _handle_get_channels(self) -> None:
        """处理获取所有 Channel."""
        if not self.server_instance:
            self._send_error("Server not initialized", 500)
            return

        channels = list(self.server_instance.integration.channels.keys())
        self._send_json({
            "channels": channels,
            "count": len(channels),
        })

    def _handle_get_data(self, channel_name: str) -> None:
        """处理获取 Channel 数据.

        Args:
            channel_name: Channel 名称.
        """
        if not self.server_instance:
            self._send_error("Server not initialized", 500)
            return

        data = self.server_instance.integration.get_channel_data(channel_name)
        if data:
            self._send_json(data.to_dict())
        else:
            self._send_error(f"Channel '{channel_name}' 无数据", 404)

    def _handle_get_all_data(self) -> None:
        """处理获取所有数据."""
        if not self.server_instance:
            self._send_error("Server not initialized", 500)
            return

        data = self.server_instance.integration.get_aggregated_data()
        self._send_json({
            "data": data,
            "timestamp": datetime.now().isoformat(),
        })

    def _handle_get_timeseries(self, query: dict) -> None:
        """处理查询时序数据.

        Args:
            query: 查询参数.
        """
        if not self.server_instance:
            self._send_error("Server not initialized", 500)
            return

        channel_name = query.get("channel", [None])[0]
        metric_name = query.get("metric", [None])[0]
        limit = int(query.get("limit", [1000])[0])

        data = self.server_instance.integration.get_time_series(
            channel_name=channel_name,
            metric_name=metric_name,
            limit=limit,
        )

        self._send_json({
            "data": [point.to_dict() for point in data],
            "count": len(data),
        })

    def _handle_get_events(self, query: dict) -> None:
        """处理查询事件.

        Args:
            query: 查询参数.
        """
        if not self.server_instance:
            self._send_error("Server not initialized", 500)
            return

        channel_name = query.get("channel", [None])[0]
        event_type = query.get("type", [None])[0]
        severity = query.get("severity", [None])[0]
        limit = int(query.get("limit", [100])[0])

        events = self.server_instance.integration.get_events(
            channel_name=channel_name,
            event_type=event_type,
            severity=severity,
            limit=limit,
        )

        self._send_json({
            "events": [event.to_dict() for event in events],
            "count": len(events),
        })

    def _handle_update_data(self, channel_name: str, data: dict) -> None:
        """处理更新 Channel 数据.

        Args:
            channel_name: Channel 名称.
            data: 数据内容.
        """
        if not self.server_instance:
            self._send_error("Server not initialized", 500)
            return

        try:
            # 检查 Channel 是否存在
            if channel_name not in self.server_instance.integration.channels:
                self._send_error(f"未知的 Channel: {channel_name}", 404)
                return

            # 更新数据
            channel_data = self.server_instance.integration.update_data(
                channel_name=channel_name,
                data=data,
            )

            self._send_json({
                "success": True,
                "data": channel_data.to_dict(),
            })
        except Exception as e:
            self._send_error(str(e), 500)

    def _handle_create_event(self, data: dict) -> None:
        """处理创建事件.

        Args:
            data: 事件数据.
        """
        if not self.server_instance:
            self._send_error("Server not initialized", 500)
            return

        try:
            event = Event(
                event_type=data.get("event_type", "custom"),
                channel_name=data.get("channel_name", "unknown"),
                severity=data.get("severity", "info"),
                message=data.get("message", ""),
                data=data.get("data"),
            )

            self.server_instance.integration.record_event(event)

            # 通过 WebSocket 广播
            if self.server_instance.bridge:
                self.server_instance.bridge.broadcast_event(event)

            self._send_json({
                "success": True,
                "event": event.to_dict(),
            })
        except Exception as e:
            self._send_error(str(e), 500)

    def _handle_acknowledge_event(self, event_id: int) -> None:
        """处理确认事件.

        Args:
            event_id: 事件 ID.
        """
        if not self.server_instance:
            self._send_error("Server not initialized", 500)
            return

        success = self.server_instance.integration.acknowledge_event(event_id)
        if success:
            self._send_json({"success": True, "message": "事件已确认"})
        else:
            self._send_error("事件不存在", 404)

    def _handle_get_status(self) -> None:
        """处理获取服务器状态."""
        if not self.server_instance:
            self._send_error("Server not initialized", 500)
            return

        status = {
            "integration": self.server_instance.integration.get_status(),
            "bridge": self.server_instance.bridge.get_status() if self.server_instance.bridge else None,
            "server": {
                "start_time": self.server_instance.start_time.isoformat() if hasattr(self.server_instance, "start_time") else None,
                "http_port": self.server_instance.http_port,
                "ws_port": self.server_instance.ws_port,
            },
        }

        self._send_json(status)


class PoseidonServer:
    """Poseidon 服务器.

    整合 ChannelsIntegration 和 RealtimeDataBridge，
    提供统一的 REST API 和 WebSocket 接口。

    示例用法:
        >>> server = PoseidonServer(http_port=8080, ws_port=8765)
        >>> server.start()
        >>> # 服务器运行中...
        >>> server.stop()
    """

    def __init__(
        self,
        db_path: str = "poseidon.db",
        http_port: int = 8080,
        ws_port: int = 8765,
        host: str = "0.0.0.0",
        cache_size: int = 10000,
        enable_ws: bool = True,
    ):
        """初始化 Poseidon 服务器.

        Args:
            db_path: 数据库路径.
            http_port: HTTP 端口.
            ws_port: WebSocket 端口.
            host: 监听地址.
            cache_size: 缓存大小.
            enable_ws: 是否启用 WebSocket.
        """
        self.db_path = db_path
        self.http_port = http_port
        self.ws_port = ws_port
        self.host = host
        self.cache_size = cache_size
        self.enable_ws = enable_ws

        # 创建集成实例
        self.integration = ChannelsIntegration(
            db_path=db_path,
            cache_size=cache_size,
        )

        # 创建 WebSocket 桥接
        self.bridge: Optional[RealtimeDataBridge] = None
        if enable_ws:
            self.bridge = RealtimeDataBridge(
                self.integration,
                host=host,
                port=ws_port,
            )

        # HTTP 服务器
        self.http_server: Optional[HTTPServer] = None

        # 启动时间
        self.start_time = datetime.now()

        # 设置 API 处理器的服务器实例
        PoseidonAPIHandler.server_instance = self

    def register_channel(self, name: str, channel: Any) -> None:
        """注册 Channel.

        Args:
            name: Channel 名称.
            channel: Channel 实例.
        """
        self.integration.register_channel(name, channel)
        logger.info(f"✅ Channel '{name}' 已注册到 Poseidon Server")

    def start(self) -> None:
        """启动服务器."""
        logger.info("🚀 启动 Poseidon Server...")

        # 启动 WebSocket 服务器
        if self.enable_ws and self.bridge:
            self.bridge.start()
            logger.info(f"📡 WebSocket 服务器：ws://{self.host}:{self.ws_port}")

        # 启动 HTTP 服务器
        self.http_server = HTTPServer((self.host, self.http_port), PoseidonAPIHandler)
        logger.info(f"🌐 HTTP API 服务器：http://{self.host}:{self.http_port}")

        logger.info("✅ Poseidon Server 启动完成")
        logger.info(f"📊 访问 http://{self.host}:{self.http_port} 查看 API 文档")

        # 运行 HTTP 服务器
        try:
            self.http_server.serve_forever()
        except KeyboardInterrupt:
            logger.info("\n🛑 收到中断信号，正在关闭...")
            self.stop()

    def stop(self) -> None:
        """停止服务器."""
        logger.info("🛑 停止 Poseidon Server...")

        # 停止 HTTP 服务器
        if self.http_server:
            self.http_server.shutdown()
            self.http_server.server_close()

        # 停止 WebSocket 服务器
        if self.bridge:
            self.bridge.stop()

        logger.info("✅ Poseidon Server 已停止")


def main():
    """主函数."""
    parser = argparse.ArgumentParser(description="Poseidon Server - Marine Channels Integration")
    parser.add_argument("--db", default="poseidon.db", help="数据库路径")
    parser.add_argument("--http-port", type=int, default=8080, help="HTTP 端口")
    parser.add_argument("--ws-port", type=int, default=8765, help="WebSocket 端口")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--cache-size", type=int, default=10000, help="缓存大小")
    parser.add_argument("--no-ws", action="store_true", help="禁用 WebSocket")
    parser.add_argument("--demo", action="store_true", help="运行演示模式")

    args = parser.parse_args()

    # 创建服务器
    server = PoseidonServer(
        db_path=args.db,
        http_port=args.http_port,
        ws_port=args.ws_port,
        host=args.host,
        cache_size=args.cache_size,
        enable_ws=not args.no_ws,
    )

    # 演示模式：注册一些测试 Channel
    if args.demo:
        logger.info("🎭 运行演示模式...")
        # 这里可以注册实际的 Channel
        # 例如：from channels.engine_monitor import EngineMonitorChannel
        # server.register_channel("engine_monitor", EngineMonitorChannel())

    # 启动服务器
    server.start()


if __name__ == "__main__":
    main()
