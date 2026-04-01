#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ship-Shore Communication Link Manager - 船岸通信链路管理

参考 SHI SVESSEL BIG (onBoard Integrated Gateway) 架构:
- 多链路管理 (LTE/5G, VSAT, Inmarsat)
- 链路质量监测与自动切换
- 网络延迟预测与补偿
- 数据传输优先级队列

参考 DFFAS 联合体岸基 FOC 通信系统:
- 船-岸之间稳定通信
- 紧急情况下从 FOC 切换到远程操作
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import random
import math

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority


class LinkType(Enum):
    """通信链路类型."""
    LTE_5G = "lte_5g"
    VSAT = "vsat"
    INMARSAT = "inmarsat"
    WIFI = "wifi"
    VHF_DATA = "vhf_data"


class LinkStatus(Enum):
    """链路状态."""
    CONNECTED = "connected"
    DEGRADED = "degraded"
    DISCONNECTED = "disconnected"
    SWITCHING = "switching"


@dataclass
class LinkProfile:
    """链路配置参数."""
    link_type: LinkType
    max_bandwidth_kbps: float
    typical_latency_ms: float
    max_range_km: float
    priority: int  # 1=最高优先
    cost_per_mb: float  # 美元/MB
    encryption: str = "AES-256"
    is_available: bool = True


@dataclass
class LinkMetrics:
    """链路实时测量指标."""
    link_type: LinkType
    status: LinkStatus = LinkStatus.DISCONNECTED
    current_latency_ms: float = 0.0
    packet_loss_pct: float = 0.0
    bandwidth_usage_pct: float = 0.0
    signal_strength_dbm: float = -80.0
    jitter_ms: float = 0.0
    uptime_seconds: float = 0.0
    bytes_sent: int = 0
    bytes_received: int = 0
    last_heartbeat: Optional[datetime] = None
    error_count: int = 0


@dataclass
class LatencyPrediction:
    """网络延迟预测 (参考论文中网络时延预测和补偿技术)."""
    predicted_latency_ms: float
    confidence: float
    trend: str  # "stable", "increasing", "decreasing"
    compensation_strategy: str
    samples_used: int = 0


# 默认链路参数 (基于实际海上通信系统)
def build_default_link_profiles() -> Dict[LinkType, LinkProfile]:
    """Build fresh link profile objects for each channel instance.

    This avoids cross-instance state leakage when tests mutate availability.
    """
    return {
        LinkType.LTE_5G: LinkProfile(
            link_type=LinkType.LTE_5G,
            max_bandwidth_kbps=50000,
            typical_latency_ms=30,
            max_range_km=50,
            priority=1,
            cost_per_mb=0.01,
        ),
        LinkType.VSAT: LinkProfile(
            link_type=LinkType.VSAT,
            max_bandwidth_kbps=4096,
            typical_latency_ms=600,
            max_range_km=99999,
            priority=2,
            cost_per_mb=0.10,
        ),
        LinkType.INMARSAT: LinkProfile(
            link_type=LinkType.INMARSAT,
            max_bandwidth_kbps=492,
            typical_latency_ms=800,
            max_range_km=99999,
            priority=3,
            cost_per_mb=1.50,
        ),
    }


class ShipShoreLinkChannel(MarineChannel):
    """船岸通信链路管理 Channel.

    对标 SVESSEL BIG 网关 + DFFAS FOC 通信系统架构。
    实现多链路管理、自动切换、延迟预测与补偿。
    """

    name = "ship_shore_link"
    description = "船岸通信链路管理 - 多链路监测、自动切换与延迟补偿"
    version = "1.0.0"
    priority = ChannelPriority.P0
    dependencies = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._links: Dict[LinkType, LinkMetrics] = {}
        self._link_profiles: Dict[LinkType, LinkProfile] = build_default_link_profiles()
        self._active_link: Optional[LinkType] = None
        self._latency_history: List[Tuple[datetime, float]] = []
        self._switch_history: List[Dict] = []
        self._shore_connected: bool = False
        self._distance_to_shore_km: float = 0.0
        self._max_latency_samples = 60

    def initialize(self) -> bool:
        for link_type, profile in self._link_profiles.items():
            self._links[link_type] = LinkMetrics(link_type=link_type)
        self._initialized = True
        self._set_health(ChannelStatus.OK, "Ship-shore link manager initialized")
        return True

    def update_link_status(
        self,
        link_type: LinkType,
        latency_ms: float,
        packet_loss_pct: float = 0.0,
        signal_strength_dbm: float = -70.0,
        bandwidth_usage_pct: float = 30.0,
    ) -> LinkMetrics:
        """更新链路实时指标."""
        metrics = self._links.get(link_type)
        if metrics is None:
            metrics = LinkMetrics(link_type=link_type)
            self._links[link_type] = metrics

        metrics.current_latency_ms = latency_ms
        metrics.packet_loss_pct = max(0.0, min(100.0, packet_loss_pct))
        metrics.signal_strength_dbm = signal_strength_dbm
        metrics.bandwidth_usage_pct = max(0.0, min(100.0, bandwidth_usage_pct))
        metrics.last_heartbeat = datetime.now()

        # 根据信号判定链路状态
        if signal_strength_dbm > -85 and packet_loss_pct < 5:
            metrics.status = LinkStatus.CONNECTED
        elif signal_strength_dbm > -95 and packet_loss_pct < 15:
            metrics.status = LinkStatus.DEGRADED
        else:
            metrics.status = LinkStatus.DISCONNECTED

        # 记录延迟历史
        now = datetime.now()
        self._latency_history.append((now, latency_ms))
        if len(self._latency_history) > self._max_latency_samples:
            self._latency_history = self._latency_history[-self._max_latency_samples:]

        return metrics

    def get_active_link(self) -> Optional[LinkType]:
        """返回当前活跃链路."""
        return self._active_link

    def select_best_link(self) -> Optional[LinkType]:
        """自动选择最佳链路 (基于质量评分)."""
        best_link = None
        best_score = -1.0

        for link_type, metrics in self._links.items():
            if metrics.status == LinkStatus.DISCONNECTED:
                continue
            profile = self._link_profiles.get(link_type)
            if profile is None or not profile.is_available:
                continue

            # 综合评分: 延迟(40%) + 带宽(20%) + 信号(20%) + 丢包(20%)
            latency_score = max(0, 1.0 - metrics.current_latency_ms / 2000)
            bw_score = 1.0 - metrics.bandwidth_usage_pct / 100
            signal_score = max(0, (metrics.signal_strength_dbm + 100) / 50)
            loss_score = 1.0 - metrics.packet_loss_pct / 100
            score = latency_score * 0.4 + bw_score * 0.2 + signal_score * 0.2 + loss_score * 0.2

            if score > best_score:
                best_score = score
                best_link = link_type

        old_link = self._active_link
        if best_link is not None and best_link != old_link:
            self._active_link = best_link
            self._switch_history.append({
                "timestamp": datetime.now().isoformat(),
                "from_link": old_link.value if old_link else None,
                "to_link": best_link.value,
                "reason": "quality_based_selection",
            })
        elif best_link is None and self._active_link is not None:
            self._active_link = None

        return self._active_link

    def predict_latency(self) -> LatencyPrediction:
        """网络延迟预测 (滑动窗口 + 加权平均)."""
        if len(self._latency_history) < 3:
            return LatencyPrediction(
                predicted_latency_ms=500.0,
                confidence=0.3,
                trend="unknown",
                compensation_strategy="fixed_buffer",
                samples_used=len(self._latency_history),
            )

        samples = [lat for _, lat in self._latency_history[-20:]]
        n = len(samples)

        # 指数加权平均
        weights = [math.exp(i / n) for i in range(n)]
        total_weight = sum(weights)
        ewa = sum(s * w for s, w in zip(samples, weights)) / total_weight

        # 趋势检测: 前半段与后半段均值对比
        mid = n // 2
        first_half = sum(samples[:mid]) / max(mid, 1)
        second_half = sum(samples[mid:]) / max(n - mid, 1)
        diff = second_half - first_half

        if diff > 30:
            trend = "increasing"
            compensation = "predictive_extrapolation"
        elif diff < -30:
            trend = "decreasing"
            compensation = "adaptive_reduction"
        else:
            trend = "stable"
            compensation = "ewa_smoothing"

        # 置信度: 基于方差
        variance = sum((s - ewa) ** 2 for s in samples) / n
        std_dev = math.sqrt(variance)
        confidence = max(0.3, min(0.99, 1.0 - std_dev / max(ewa, 1)))

        return LatencyPrediction(
            predicted_latency_ms=round(ewa, 1),
            confidence=round(confidence, 3),
            trend=trend,
            compensation_strategy=compensation,
            samples_used=n,
        )

    def set_distance_to_shore(self, distance_km: float) -> None:
        """更新离岸距离, 影响链路可用性."""
        self._distance_to_shore_km = max(0.0, distance_km)
        for link_type, profile in self._link_profiles.items():
            metrics = self._links.get(link_type)
            if metrics is None:
                continue
            if self._distance_to_shore_km > profile.max_range_km:
                metrics.status = LinkStatus.DISCONNECTED
                profile.is_available = False
            else:
                profile.is_available = True

    def simulate_link_conditions(self) -> Dict[str, Any]:
        """模拟当前海况下的通信状况 (用于仿真和演示)."""
        dist = self._distance_to_shore_km

        for link_type, profile in self._link_profiles.items():
            if dist > profile.max_range_km:
                self.update_link_status(link_type, 9999, 100, -120, 0)
                continue

            range_factor = min(1.0, dist / max(profile.max_range_km, 1))
            base_lat = profile.typical_latency_ms
            jitter = random.uniform(-0.1, 0.15) * base_lat
            latency = base_lat * (1 + range_factor * 0.5) + jitter
            loss = range_factor * 8 + random.uniform(0, 2)
            signal = -60 - range_factor * 35 + random.uniform(-3, 3)
            bw = 20 + range_factor * 40 + random.uniform(-5, 10)

            self.update_link_status(link_type, max(5, latency), loss, signal, bw)

        self.select_best_link()
        return self.get_link_summary()

    def get_link_summary(self) -> Dict[str, Any]:
        """获取所有链路摘要."""
        links = {}
        for link_type, metrics in self._links.items():
            profile = self._link_profiles.get(link_type)
            links[link_type.value] = {
                "status": metrics.status.value,
                "latency_ms": round(metrics.current_latency_ms, 1),
                "packet_loss_pct": round(metrics.packet_loss_pct, 2),
                "signal_dbm": round(metrics.signal_strength_dbm, 1),
                "bandwidth_usage_pct": round(metrics.bandwidth_usage_pct, 1),
                "max_bandwidth_kbps": profile.max_bandwidth_kbps if profile else 0,
                "last_heartbeat": metrics.last_heartbeat.isoformat() if metrics.last_heartbeat else None,
            }

        prediction = self.predict_latency()
        best_link_type = self._active_link.value if self._active_link else None
        best_link_latency = prediction.predicted_latency_ms
        best_link_quality = None
        if self._active_link and self._active_link.value in links:
            active_metrics = links[self._active_link.value]
            loss = float(active_metrics.get("packet_loss_pct", 0.0))
            latency = float(active_metrics.get("latency_ms", best_link_latency or 0.0))
            quality = max(0.0, min(1.0, (100.0 - (loss * 2.0) - (latency / 20.0)) / 100.0))
            best_link_quality = round(quality, 3)

        return {
            "active_link": self._active_link.value if self._active_link else None,
            "best_link_type": best_link_type,
            "best_link_latency": best_link_latency,
            "best_link_quality": best_link_quality,
            "distance_to_shore_km": round(self._distance_to_shore_km, 1),
            "shore_connected": self._active_link is not None,
            "links": links,
            "latency_prediction": {
                "predicted_ms": prediction.predicted_latency_ms,
                "confidence": prediction.confidence,
                "trend": prediction.trend,
                "compensation": prediction.compensation_strategy,
            },
            "switch_count": len(self._switch_history),
            "recent_switches": self._switch_history[-3:] if self._switch_history else [],
        }

    def get_status(self) -> Dict[str, Any]:
        summary = self.get_link_summary()
        return {
            "channel": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": "ok" if summary["shore_connected"] else "warn",
            "health_message": f"Active: {summary['active_link'] or 'none'}, "
                              f"Distance: {summary['distance_to_shore_km']} km",
            **summary,
        }

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shut down")
        return True
