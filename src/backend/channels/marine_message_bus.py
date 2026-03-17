#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marine Message Bus - Channel Communication System

船舶 Channel 间消息传递系统

基于 VDES (VHF Data Exchange System) 和 IBS (Integrated Bridge System) 设计理念
实现 Channel 间的异步消息传递、广播、订阅机制

Author: CaptainCatamaran 🐱⛵
Date: 2026-03-13
Round: 14 - Channel Messaging & Transpacific Route Simulation
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """消息类型 - 基于 IMO SMCP (Standard Marine Communication Phrases)"""
    
    # 安全消息 (Safety)
    SAFETY_ALERT = "safety_alert"  # 安全警报
    NAVIGATION_WARNING = "navigation_warning"  # 航行警告
    WEATHER_WARNING = "weather_warning"  # 天气警告
    
    # 紧急消息 (Urgency)
    URGENCY_PAN_PAN = "urgency_pan_pan"  # 紧急 PAN-PAN
    ENGINE_PROBLEM = "engine_problem"  # 发动机问题
    STEERING_PROBLEM = "steering_problem"  # 舵机问题
    
    # 常规消息 (Routine)
    STATUS_UPDATE = "status_update"  # 状态更新
    DATA_REQUEST = "data_request"  # 数据请求
    DATA_RESPONSE = "data_response"  # 数据响应
    COMMAND = "command"  # 命令
    ACKNOWLEDGMENT = "acknowledgment"  # 确认
    
    # 系统消息 (System)
    CHANNEL_REGISTER = "channel_register"  # Channel 注册
    CHANNEL_UNREGISTER = "channel_unregister"  # Channel 注销
    HEARTBEAT = "heartbeat"  # 心跳


class MessagePriority(Enum):
    """消息优先级 - 基于 GMDSS 优先级"""
    
    DISTRESS = 0  # 遇险 (最高)
    URGENCY = 1   # 紧急
    SAFETY = 2    # 安全
    ROUTINE = 3   # 常规 (最低)


@dataclass
class MarineMessage:
    """船舶消息 - 类似 VDES 消息结构"""
    
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = MessageType.STATUS_UPDATE
    priority: MessagePriority = MessagePriority.ROUTINE
    
    # 发送方/接收方
    sender_channel: str = ""
    target_channel: str = ""  # 空表示广播
    target_channels: List[str] = field(default_factory=list)  # 多播列表
    
    # 消息内容
    subject: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    payload: Any = None
    
    # 时间戳
    timestamp: float = field(default_factory=time.time)
    expiry_time: Optional[float] = None  # 过期时间 (秒)
    
    # 元数据
    correlation_id: Optional[str] = None  # 关联 ID (用于请求 - 响应)
    reply_to: Optional[str] = None  # 回复地址
    retry_count: int = 0
    max_retries: int = 3
    
    # 状态
    delivered: bool = False
    acknowledged: bool = False
    
    def is_expired(self) -> bool:
        """检查消息是否过期"""
        if self.expiry_time is None:
            return False
        return time.time() > self.expiry_time
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'message_id': self.message_id,
            'message_type': self.message_type.value,
            'priority': self.priority.value,
            'sender_channel': self.sender_channel,
            'target_channel': self.target_channel,
            'target_channels': self.target_channels,
            'subject': self.subject,
            'content': self.content,
            'payload': self.payload,
            'timestamp': self.timestamp,
            'expiry_time': self.expiry_time,
            'correlation_id': self.correlation_id,
            'reply_to': self.reply_to,
            'delivered': self.delivered,
            'acknowledged': self.acknowledged,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MarineMessage:
        """从字典创建"""
        return cls(
            message_id=data.get('message_id', str(uuid.uuid4())),
            message_type=MessageType(data.get('message_type', 'status_update')),
            priority=MessagePriority(data.get('priority', 3)),
            sender_channel=data.get('sender_channel', ''),
            target_channel=data.get('target_channel', ''),
            target_channels=data.get('target_channels', []),
            subject=data.get('subject', ''),
            content=data.get('content', {}),
            payload=data.get('payload'),
            timestamp=data.get('timestamp', time.time()),
            expiry_time=data.get('expiry_time'),
            correlation_id=data.get('correlation_id'),
            reply_to=data.get('reply_to'),
            delivered=data.get('delivered', False),
            acknowledged=data.get('acknowledged', False),
        )


@dataclass
class Subscription:
    """订阅配置"""
    
    channel_id: str
    message_types: Set[MessageType] = field(default_factory=set)
    callback: Optional[Callable[[MarineMessage], None]] = None
    priority_filter: Optional[MessagePriority] = None  # 只接收此优先级及以上
    active: bool = True


class MarineMessageBus:
    """
    船舶消息总线
    
    功能:
    - 发布/订阅模式
    - 点对点消息
    - 广播/多播
    - 优先级队列
    - 消息过期
    - 确认机制
    
    设计参考:
    - VDES (VHF Data Exchange System)
    - IBS (Integrated Bridge System)
    - IMO SMCP (Standard Marine Communication Phrases)
    """
    
    def __init__(self, name: str = "marine_message_bus"):
        self.name = name
        self._subscriptions: Dict[str, List[Subscription]] = defaultdict(list)
        self._channel_registry: Dict[str, Any] = {}
        self._message_queue: List[MarineMessage] = []
        self._processed_ids: Set[str] = set()
        self._message_log: List[MarineMessage] = []
        self._stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'messages_delivered': 0,
            'messages_expired': 0,
            'broadcasts': 0,
            'unicasts': 0,
            'multicasts': 0,
        }
        self._lock = None  # Lazy init in async methods
    
    def register_channel(self, channel_id: str, channel_obj: Any = None) -> bool:
        """
        注册 Channel
        
        Args:
            channel_id: Channel ID (如 'weather_routing', 'engine_monitor')
            channel_obj: Channel 对象引用 (可选)
        
        Returns:
            bool: 注册是否成功
        """
        if channel_id in self._channel_registry:
            logger.warning(f"Channel {channel_id} already registered")
            return False
        
        self._channel_registry[channel_id] = channel_obj
        logger.info(f"Channel registered: {channel_id}")
        return True
    
    def unregister_channel(self, channel_id: str) -> bool:
        """注销 Channel"""
        if channel_id not in self._channel_registry:
            return False
        
        del self._channel_registry[channel_id]
        self._subscriptions.pop(channel_id, None)
        logger.info(f"Channel unregistered: {channel_id}")
        return True
    
    def subscribe(
        self,
        channel_id: str,
        message_types: Optional[Set[MessageType]] = None,
        callback: Optional[Callable[[MarineMessage], None]] = None,
        priority_filter: Optional[MessagePriority] = None,
    ) -> str:
        """
        订阅消息
        
        Args:
            channel_id: 订阅方 Channel ID
            message_types: 关注的消息类型 (None 表示全部)
            callback: 消息回调函数
            priority_filter: 优先级过滤 (只接收此优先级及以上)
        
        Returns:
            str: 订阅 ID
        """
        subscription = Subscription(
            channel_id=channel_id,
            message_types=message_types or set(MessageType),
            callback=callback,
            priority_filter=priority_filter,
        )
        
        self._subscriptions[channel_id].append(subscription)
        logger.debug(f"Channel {channel_id} subscribed to {message_types}")
        
        return subscription.channel_id
    
    def unsubscribe(self, channel_id: str, subscription_id: Optional[str] = None) -> bool:
        """取消订阅"""
        if channel_id not in self._subscriptions:
            return False
        
        if subscription_id:
            self._subscriptions[channel_id] = [
                s for s in self._subscriptions[channel_id]
                if s.channel_id != subscription_id
            ]
        else:
            self._subscriptions.pop(channel_id, None)
        
        return True
    
    async def publish(self, message: MarineMessage) -> List[str]:
        """
        发布消息 (异步)
        
        Args:
            message: 要发布的消息
        
        Returns:
            List[str]: 成功接收消息的 Channel ID 列表
        """
        if self._lock is None:
            self._lock = asyncio.Lock()
        async with self._lock:
            # 检查消息是否过期
            if message.is_expired():
                self._stats['messages_expired'] += 1
                logger.warning(f"Message expired: {message.message_id}")
                return []
            
            # 检查是否重复处理
            if message.message_id in self._processed_ids:
                logger.debug(f"Message already processed: {message.message_id}")
                return []
            
            self._processed_ids.add(message.message_id)
            self._message_log.append(message)
            self._stats['messages_sent'] += 1
            
            # 确定接收方
            recipients = self._get_recipients(message)
            
            if not recipients:
                logger.debug(f"No recipients for message: {message.message_id}")
                return []
            
            # 分发消息
            delivered_to = []
            for recipient_id in recipients:
                if self._deliver_message(message, recipient_id):
                    delivered_to.append(recipient_id)
                    self._stats['messages_delivered'] += 1
            
            message.delivered = len(delivered_to) > 0
            return delivered_to
    
    def publish_sync(self, message: MarineMessage) -> List[str]:
        """发布消息 (同步)"""
        if message.is_expired():
            self._stats['messages_expired'] += 1
            return []
        
        if message.message_id in self._processed_ids:
            return []
        
        self._processed_ids.add(message.message_id)
        self._message_log.append(message)
        self._stats['messages_sent'] += 1
        
        recipients = self._get_recipients(message)
        delivered_to = []
        
        for recipient_id in recipients:
            if self._deliver_message_sync(message, recipient_id):
                delivered_to.append(recipient_id)
                self._stats['messages_delivered'] += 1
        
        message.delivered = len(delivered_to) > 0
        return delivered_to
    
    def _get_recipients(self, message: MarineMessage) -> Set[str]:
        """获取消息接收方"""
        recipients = set()
        
        # 广播 (target_channel 为空且 target_channels 为空)
        if not message.target_channel and not message.target_channels:
            recipients.update(self._channel_registry.keys())
            recipients.discard(message.sender_channel)
            self._stats['broadcasts'] += 1
        
        # 点对点
        elif message.target_channel:
            if message.target_channel in self._channel_registry:
                recipients.add(message.target_channel)
            self._stats['unicasts'] += 1
        
        # 多播
        elif message.target_channels:
            for channel_id in message.target_channels:
                if channel_id in self._channel_registry:
                    recipients.add(channel_id)
            self._stats['multicasts'] += 1
        
        return recipients
    
    def _deliver_message(self, message: MarineMessage, channel_id: str) -> bool:
        """异步分发消息"""
        if channel_id not in self._subscriptions:
            return False
        
        for subscription in self._subscriptions[channel_id]:
            if not subscription.active:
                continue
            
            # 消息类型过滤
            if message.message_type not in subscription.message_types:
                continue
            
            # 优先级过滤
            if subscription.priority_filter:
                if message.priority.value > subscription.priority_filter.value:
                    continue
            
            # 调用回调
            if subscription.callback:
                try:
                    if asyncio.iscoroutinefunction(subscription.callback):
                        asyncio.create_task(subscription.callback(message))
                    else:
                        subscription.callback(message)
                except Exception as e:
                    logger.error(f"Callback error for {channel_id}: {e}")
                    return False
        
        return True
    
    def _deliver_message_sync(self, message: MarineMessage, channel_id: str) -> bool:
        """同步分发消息"""
        if channel_id not in self._subscriptions:
            return False
        
        for subscription in self._subscriptions[channel_id]:
            if not subscription.active:
                continue
            
            if message.message_type not in subscription.message_types:
                continue
            
            if subscription.priority_filter:
                if message.priority.value > subscription.priority_filter.value:
                    continue
            
            if subscription.callback:
                try:
                    subscription.callback(message)
                except Exception as e:
                    logger.error(f"Callback error for {channel_id}: {e}")
                    return False
        
        return True
    
    def create_message(
        self,
        message_type: MessageType,
        sender: str,
        subject: str,
        content: Dict[str, Any],
        target: Optional[str] = None,
        targets: Optional[List[str]] = None,
        priority: MessagePriority = MessagePriority.ROUTINE,
        expiry_seconds: Optional[float] = None,
        correlation_id: Optional[str] = None,
    ) -> MarineMessage:
        """
        创建消息
        
        Args:
            message_type: 消息类型
            sender: 发送方 Channel ID
            subject: 主题
            content: 内容字典
            target: 目标 Channel (单播)
            targets: 目标 Channel 列表 (多播)
            priority: 优先级
            expiry_seconds: 过期时间 (秒)
            correlation_id: 关联 ID
        
        Returns:
            MarineMessage: 创建的消息
        """
        expiry_time = None
        if expiry_seconds:
            expiry_time = time.time() + expiry_seconds
        
        return MarineMessage(
            message_type=message_type,
            priority=priority,
            sender_channel=sender,
            target_channel=target or "",
            target_channels=targets or [],
            subject=subject,
            content=content,
            expiry_time=expiry_time,
            correlation_id=correlation_id,
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self._stats,
            'registered_channels': len(self._channel_registry),
            'subscribed_channels': len(self._subscriptions),
            'message_log_size': len(self._message_log),
        }
    
    def get_message_log(
        self,
        limit: int = 100,
        message_type: Optional[MessageType] = None,
        sender: Optional[str] = None,
    ) -> List[MarineMessage]:
        """获取消息日志"""
        filtered = self._message_log
        
        if message_type:
            filtered = [m for m in filtered if m.message_type == message_type]
        
        if sender:
            filtered = [m for m in filtered if m.sender_channel == sender]
        
        return filtered[-limit:]
    
    def clear_log(self) -> int:
        """清除消息日志"""
        count = len(self._message_log)
        self._message_log.clear()
        self._processed_ids.clear()
        return count


# 便捷函数
def create_safety_alert(
    sender: str,
    alert_type: str,
    message: str,
    position: Optional[Dict[str, float]] = None,
) -> MarineMessage:
    """创建安全警报消息"""
    content = {
        'alert_type': alert_type,
        'message': message,
    }
    if position:
        content['position'] = position
    
    bus = MarineMessageBus()
    return bus.create_message(
        message_type=MessageType.SAFETY_ALERT,
        sender=sender,
        subject=f"SAFETY ALERT: {alert_type}",
        content=content,
        priority=MessagePriority.SAFETY,
    )


def create_engine_problem(
    sender: str,
    problem_type: str,
    severity: str,
    details: Dict[str, Any],
) -> MarineMessage:
    """创建发动机问题消息"""
    bus = MarineMessageBus()
    return bus.create_message(
        message_type=MessageType.ENGINE_PROBLEM,
        sender=sender,
        subject=f"ENGINE PROBLEM: {problem_type}",
        content={
            'problem_type': problem_type,
            'severity': severity,
            'details': details,
        },
        priority=MessagePriority.URGENCY,
    )


if __name__ == "__main__":
    # 简单测试
    bus = MarineMessageBus()
    
    # 注册 Channel
    bus.register_channel("weather_routing")
    bus.register_channel("engine_monitor")
    bus.register_channel("navigation_data")
    
    # 订阅消息
    def on_safety_alert(msg: MarineMessage):
        print(f"🚨 Safety Alert: {msg.subject}")
    
    bus.subscribe("navigation_data", {MessageType.SAFETY_ALERT}, on_safety_alert)
    
    # 发布消息
    alert = bus.create_message(
        message_type=MessageType.SAFETY_ALERT,
        sender="weather_routing",
        subject="Storm Warning",
        content={"storm_type": "tropical", "severity": "high"},
        priority=MessagePriority.SAFETY,
    )
    
    recipients = bus.publish_sync(alert)
    print(f"✅ Message delivered to: {recipients}")
    print(f"📊 Stats: {bus.get_stats()}")
