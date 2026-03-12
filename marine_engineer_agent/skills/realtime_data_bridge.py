# -*- coding: utf-8 -*-
"""
Realtime Data Bridge - WebSocket 实时桥接.

提供 WebSocket 服务器功能，实现 Channel 数据的实时推送和订阅。

功能:
- WebSocket 服务器
- 订阅/发布机制
- 连接管理
- 心跳检测
- 消息广播

示例用法:
    >>> from .channels_integration import ChannelsIntegration
    >>>
    >>> # 创建集成实例
    >>> integration = ChannelsIntegration()
    >>>
    >>> # 创建实时桥接
    >>> bridge = RealtimeDataBridge(integration, host="0.0.0.0", port=8765)
    >>>
    >>> # 启动服务器
    >>> bridge.start()
    >>>
    >>> # 推送数据 (从 integration 自动推送)
    >>> integration.update_data("engine_monitor", {"rpm": 120})
    >>> # 数据会自动通过 WebSocket 推送给订阅的客户端
"""

import asyncio
import json
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional, Set

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
except ImportError:
    websockets = None  # type: ignore
    WebSocketServerProtocol = Any  # type: ignore

from .channels_integration import ChannelData, ChannelsIntegration, Event


class MessageType(Enum):
    """WebSocket 消息类型."""

    SUBSCRIBE = "subscribe"  # 订阅
    UNSUBSCRIBE = "unsubscribe"  # 取消订阅
    DATA = "data"  # 数据推送
    EVENT = "event"  # 事件通知
    PING = "ping"  # 心跳请求
    PONG = "pong"  # 心跳响应
    ERROR = "error"  # 错误消息
    ACK = "ack"  # 确认消息


@dataclass
class WebSocketMessage:
    """WebSocket 消息.

    Attributes:
        type: 消息类型.
        channel: Channel 名称 (可选).
        data: 消息数据.
        timestamp: 时间戳.
        client_id: 客户端 ID (可选).
    """

    type: MessageType
    channel: Optional[str] = None
    data: Optional[dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    client_id: Optional[str] = None

    def to_json(self) -> str:
        """转换为 JSON 字符串.

        Returns:
            JSON 字符串.
        """
        return json.dumps(
            {
                "type": self.type.value,
                "channel": self.channel,
                "data": self.data,
                "timestamp": self.timestamp.isoformat(),
                "client_id": self.client_id,
            },
            ensure_ascii=False,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "WebSocketMessage":
        """从 JSON 字符串解析.

        Args:
            json_str: JSON 字符串.

        Returns:
            WebSocketMessage 对象.
        """
        data_dict = json.loads(json_str)
        return cls(
            type=MessageType(data_dict["type"]),
            channel=data_dict.get("channel"),
            data=data_dict.get("data"),
            timestamp=datetime.fromisoformat(data_dict["timestamp"]),
            client_id=data_dict.get("client_id"),
        )


@dataclass
class ClientConnection:
    """客户端连接信息.

    Attributes:
        client_id: 客户端唯一标识.
        websocket: WebSocket 连接对象.
        subscriptions: 订阅的 Channel 列表.
        connected_at: 连接时间.
        last_ping: 最后心跳时间.
        message_count: 消息计数.
    """

    client_id: str
    websocket: WebSocketServerProtocol
    subscriptions: Set[str] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.now)
    last_ping: datetime = field(default_factory=datetime.now)
    message_count: int = 0


class RealtimeDataBridge:
    """WebSocket 实时数据桥接.

    功能:
    - WebSocket 服务器管理
    - 客户端连接管理
    - 订阅/发布机制
    - 数据实时推送
    - 心跳检测

    示例用法:
        >>> integration = ChannelsIntegration()
        >>> bridge = RealtimeDataBridge(integration, port=8765)
        >>> bridge.start()
        >>> # 服务器运行中...
        >>> bridge.stop()
    """

    def __init__(
        self,
        integration: ChannelsIntegration,
        host: str = "0.0.0.0",
        port: int = 8765,
        ping_interval: int = 30,
        ping_timeout: int = 10,
        max_clients: int = 100,
    ):
        """初始化实时数据桥接.

        Args:
            integration: ChannelsIntegration 实例.
            host: 服务器监听地址.
            port: 服务器监听端口.
            ping_interval: 心跳间隔 (秒).
            ping_timeout: 心跳超时 (秒).
            max_clients: 最大客户端数量.
        """
        self.integration = integration
        self.host = host
        self.port = port
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.max_clients = max_clients

        # 客户端管理
        self.clients: dict[str, ClientConnection] = {}
        self._client_counter = 0

        # 服务器状态
        self._server = None
        self._running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None

        # 日志
        self.logger = logging.getLogger(__name__)

        # 注册数据更新回调
        self.integration.add_callback("global", self._on_data_update)

    def _generate_client_id(self) -> str:
        """生成客户端唯一 ID.

        Returns:
            客户端 ID.
        """
        self._client_counter += 1
        return f"client-{self._client_counter:04d}"

    async def _handle_connection(self, websocket: WebSocketServerProtocol) -> None:
        """处理 WebSocket 连接.

        Args:
            websocket: WebSocket 连接对象.
        """
        client_id = self._generate_client_id()
        client = ClientConnection(client_id=client_id, websocket=websocket)

        # 检查最大客户端数
        if len(self.clients) >= self.max_clients:
            await websocket.send(
                WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"message": "达到最大客户端数量"},
                ).to_json()
            )
            await websocket.close()
            return

        # 添加客户端
        self.clients[client_id] = client
        self.logger.info(f"🔌 客户端连接：{client_id} (当前：{len(self.clients)}个)")

        # 发送欢迎消息
        await websocket.send(
            WebSocketMessage(
                type=MessageType.ACK,
                data={
                    "message": "连接成功",
                    "client_id": client_id,
                    "subscriptions": [],
                },
            ).to_json()
        )

        try:
            async for message in websocket:
                await self._handle_message(client, message)
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"🔌 客户端断开：{client_id}")
        finally:
            # 移除客户端
            if client_id in self.clients:
                del self.clients[client_id]
            self.logger.info(f"📊 当前客户端数：{len(self.clients)}")

    async def _handle_message(
        self, client: ClientConnection, message: str
    ) -> None:
        """处理客户端消息.

        Args:
            client: 客户端连接.
            message: 消息内容.
        """
        try:
            msg = WebSocketMessage.from_json(message)
            client.message_count += 1
            client.last_ping = datetime.now()

            if msg.type == MessageType.SUBSCRIBE:
                await self._handle_subscribe(client, msg)
            elif msg.type == MessageType.UNSUBSCRIBE:
                await self._handle_unsubscribe(client, msg)
            elif msg.type == MessageType.PING:
                await self._handle_ping(client)
            else:
                await client.websocket.send(
                    WebSocketMessage(
                        type=MessageType.ERROR,
                        data={"message": f"未知消息类型：{msg.type}"},
                    ).to_json()
                )

        except json.JSONDecodeError:
            await client.websocket.send(
                WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"message": "无效的 JSON 格式"},
                ).to_json()
            )
        except Exception as e:
            self.logger.error(f"⚠️ 处理消息失败：{e}")
            await client.websocket.send(
                WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"message": str(e)},
                ).to_json()
            )

    async def _handle_subscribe(
        self, client: ClientConnection, message: WebSocketMessage
    ) -> None:
        """处理订阅请求.

        Args:
            client: 客户端连接.
            message: 订阅消息.
        """
        channel = message.channel
        if not channel:
            await client.websocket.send(
                WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"message": "订阅需要指定 channel"},
                ).to_json()
            )
            return

        # 特殊处理：订阅所有 Channel
        if channel == "*":
            client.subscriptions = set(self.integration.channels.keys())
        elif channel in self.integration.channels:
            client.subscriptions.add(channel)
        else:
            await client.websocket.send(
                WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"message": f"未知的 Channel: {channel}"},
                ).to_json()
            )
            return

        # 发送确认
        await client.websocket.send(
            WebSocketMessage(
                type=MessageType.ACK,
                data={
                    "message": f"已订阅：{channel}",
                    "subscriptions": list(client.subscriptions),
                },
            ).to_json()
        )

        self.logger.info(f"📡 客户端 {client.client_id} 订阅：{channel}")

    async def _handle_unsubscribe(
        self, client: ClientConnection, message: WebSocketMessage
    ) -> None:
        """处理取消订阅请求.

        Args:
            client: 客户端连接.
            message: 取消订阅消息.
        """
        channel = message.channel
        if channel and channel in client.subscriptions:
            client.subscriptions.remove(channel)
            await client.websocket.send(
                WebSocketMessage(
                    type=MessageType.ACK,
                    data={
                        "message": f"已取消订阅：{channel}",
                        "subscriptions": list(client.subscriptions),
                    },
                ).to_json()
            )
        elif channel == "*":
            client.subscriptions.clear()
            await client.websocket.send(
                WebSocketMessage(
                    type=MessageType.ACK,
                    data={
                        "message": "已取消所有订阅",
                        "subscriptions": [],
                    },
                ).to_json()
            )

    async def _handle_ping(self, client: ClientConnection) -> None:
        """处理心跳请求.

        Args:
            client: 客户端连接.
        """
        await client.websocket.send(
            WebSocketMessage(type=MessageType.PONG).to_json()
        )

    def _on_data_update(self, data: ChannelData) -> None:
        """数据更新回调.

        Args:
            data: Channel 数据.
        """
        # 广播给订阅的客户端
        self._broadcast_to_subscribers(data.channel_name, data.to_dict())

    def _broadcast_to_subscribers(
        self, channel_name: str, data: dict[str, Any]
    ) -> None:
        """广播数据给订阅的客户端.

        Args:
            channel_name: Channel 名称.
            data: 数据内容.
        """
        message = WebSocketMessage(
            type=MessageType.DATA,
            channel=channel_name,
            data=data,
        ).to_json()

        # 异步发送
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._broadcast_async(message, channel_name), self._loop
            )

    async def _broadcast_async(self, message: str, channel_name: str) -> None:
        """异步广播消息.

        Args:
            message: 消息内容.
            channel_name: Channel 名称.
        """
        disconnected = []

        for client_id, client in self.clients.items():
            if channel_name in client.subscriptions or "*" in client.subscriptions:
                try:
                    await client.websocket.send(message)
                except Exception:
                    disconnected.append(client_id)

        # 清理断开的客户端
        for client_id in disconnected:
            if client_id in self.clients:
                del self.clients[client_id]

    def broadcast_event(self, event: Event) -> None:
        """广播事件.

        Args:
            event: 事件对象.
        """
        message = WebSocketMessage(
            type=MessageType.EVENT,
            channel=event.channel_name,
            data=event.to_dict(),
        ).to_json()

        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._broadcast_all_async(message), self._loop
            )

    async def _broadcast_all_async(self, message: str) -> None:
        """广播给所有客户端.

        Args:
            message: 消息内容.
        """
        disconnected = []

        for client_id, client in self.clients.items():
            try:
                await client.websocket.send(message)
            except Exception:
                disconnected.append(client_id)

        for client_id in disconnected:
            if client_id in self.clients:
                del self.clients[client_id]

    def _run_server(self) -> None:
        """运行 WebSocket 服务器 (在独立线程中)."""
        if websockets is None:
            self.logger.error("❌ websockets 库未安装，请运行：pip install websockets")
            return

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        async def handler(websocket: WebSocketServerProtocol) -> None:
            await self._handle_connection(websocket)

        self._server = websockets.serve(
            handler,
            self.host,
            self.port,
            ping_interval=self.ping_interval,
            ping_timeout=self.ping_timeout,
        )

        self._loop.run_until_complete(self._server)
        self._running = True
        self.logger.info(f"🚀 WebSocket 服务器启动：ws://{self.host}:{self.port}")
        self._loop.run_forever()

    def start(self) -> None:
        """启动 WebSocket 服务器."""
        if self._running:
            self.logger.warning("⚠️ 服务器已在运行中")
            return

        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()

        # 等待服务器启动
        import time

        time.sleep(0.5)

    def stop(self) -> None:
        """停止 WebSocket 服务器."""
        if not self._running:
            return

        self._running = False

        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)

        if self._thread:
            self._thread.join(timeout=2.0)

        self.logger.info("🛑 WebSocket 服务器已停止")

    def get_status(self) -> dict[str, Any]:
        """获取服务器状态.

        Returns:
            状态字典.
        """
        return {
            "running": self._running,
            "host": self.host,
            "port": self.port,
            "connected_clients": len(self.clients),
            "max_clients": self.max_clients,
            "clients": [
                {
                    "client_id": client.client_id,
                    "subscriptions": list(client.subscriptions),
                    "connected_at": client.connected_at.isoformat(),
                    "message_count": client.message_count,
                }
                for client in self.clients.values()
            ],
        }

    def get_client_count(self) -> int:
        """获取当前连接的客户端数量.

        Returns:
            客户端数量.
        """
        return len(self.clients)


# 导出
__all__ = [
    "RealtimeDataBridge",
    "WebSocketMessage",
    "ClientConnection",
    "MessageType",
]
