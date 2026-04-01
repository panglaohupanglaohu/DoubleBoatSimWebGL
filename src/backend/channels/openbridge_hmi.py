# -*- coding: utf-8 -*-
"""
L5: OpenBridge Interaction & Cloud-Edge Collaboration - 交互与协同层

核心技术:
- OpenBridge 4.0+: 统一船舶 HMI 设计标准
- AR-CAS (Augmented Reality Collision Avoidance System): AR 态势增强
- KOGNIFAI 云边协同: 边缘推理 + 云端训练的分层架构

技术要点:
- 统一全船视觉语言 (Design Tokens + Component Library)
- AR 视锥与物理视野毫秒级对齐
- 认知负荷量化评估 (NASA-TLX)
- OOW (Officer On Watch) 注意力引导
- 云边数据同步策略 (Delta Sync)

工程意义:
统一全船视觉语言；AR 视锥与物理视野毫秒级对齐，降低操作员认知负荷。
"""

from __future__ import annotations

import math
import time
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """OpenBridge 警报等级 (IEC 62923)"""
    EMERGENCY = "emergency"
    ALARM = "alarm"
    WARNING = "warning"
    CAUTION = "caution"
    INFORMATION = "information"


class WorkContext(Enum):
    """操作员工作上下文"""
    VOYAGE = "voyage"
    DOCKING = "docking"
    ANCHORING = "anchoring"
    EMERGENCY = "emergency"
    MONITORING = "monitoring"


class CognitiveState(Enum):
    """操作员认知状态"""
    ALERT = "alert"
    NORMAL = "normal"
    FATIGUED = "fatigued"
    OVERLOADED = "overloaded"


@dataclass
class DesignToken:
    """OpenBridge 设计令牌"""
    name: str
    category: str            # "color", "typography", "spacing", "icon"
    value: Any
    context: str = "default"


@dataclass
class AROverlay:
    """AR 叠加元素"""
    overlay_id: str
    target_mmsi: Optional[str] = None
    target_name: str = ""
    bearing: float = 0.0         # 方位 (度)
    distance_nm: float = 0.0     # 距离 (海里)
    cpa: float = 0.0             # CPA
    tcpa: float = 0.0            # TCPA (分钟)
    risk_level: float = 0.0      # 风险等级 0-1
    ar_position: Tuple[float, float] = (0.0, 0.0)  # 像素坐标
    visible: bool = True
    color: str = "#00FF00"


@dataclass
class NASATLXScore:
    """NASA-TLX 认知负荷评分"""
    mental_demand: float = 50.0     # 0-100
    physical_demand: float = 20.0
    temporal_demand: float = 50.0
    performance: float = 70.0
    effort: float = 50.0
    frustration: float = 30.0

    @property
    def overall(self) -> float:
        """加权总分"""
        return round((self.mental_demand + self.physical_demand +
                      self.temporal_demand + (100 - self.performance) +
                      self.effort + self.frustration) / 6, 1)


@dataclass
class CloudEdgeSyncState:
    """云边同步状态"""
    last_sync: Optional[datetime] = None
    pending_uploads: int = 0
    pending_downloads: int = 0
    sync_latency_ms: float = 0.0
    bandwidth_kbps: float = 0.0
    mode: str = "delta"             # "full", "delta", "compressed"
    edge_model_version: str = "1.0.0"
    cloud_model_version: str = "1.0.0"
    models_in_sync: bool = True


class OpenBridgeHMIChannel(MarineChannel):
    """
    L5: OpenBridge HMI + AR-CAS + 云边协同 Channel

    实现:
    - OpenBridge 4.0+ 设计体系 (Design Tokens + 组件库)
    - AR-CAS 态势增强 (AR 叠加 + 碰撞预警)
    - 认知负荷评估 (NASA-TLX)
    - 注意力引导 (Priority Alerting)
    - KOGNIFAI 云边协同 (Delta Sync + Model OTA)
    """

    name = "openbridge_hmi"
    description = "L5: OpenBridge HMI + AR-CAS 态势增强 + 云边协同"
    version = "1.0.0"
    priority = ChannelPriority.P1
    dependencies: List[str] = ["colregs_brain", "deterministic_network"]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.config = config or {}
        self._design_tokens: Dict[str, DesignToken] = {}
        self._ar_overlays: Dict[str, AROverlay] = {}
        self._alert_queue: List[Dict[str, Any]] = []
        self._work_context = WorkContext.MONITORING
        self._cognitive_state = CognitiveState.NORMAL
        self._tlx_score = NASATLXScore()
        self._cloud_edge = CloudEdgeSyncState()
        self._attention_priorities: List[str] = []
        self._interaction_log: List[Dict[str, Any]] = []

    def initialize(self) -> bool:
        self._load_design_tokens()
        self._initialized = True
        self._set_health(ChannelStatus.OK, "OpenBridge HMI 就绪")
        return True

    def _load_design_tokens(self) -> None:
        """加载 OpenBridge 设计令牌"""
        tokens = [
            DesignToken("ob-color-alert-emergency", "color", "#FF0000", "dark"),
            DesignToken("ob-color-alert-alarm", "color", "#FF6600", "dark"),
            DesignToken("ob-color-alert-warning", "color", "#FFCC00", "dark"),
            DesignToken("ob-color-alert-caution", "color", "#00CCFF", "dark"),
            DesignToken("ob-color-primary", "color", "#0066CC", "dark"),
            DesignToken("ob-color-background", "color", "#1A1A2E", "dark"),
            DesignToken("ob-color-text", "color", "#E0E0FF", "dark"),
            DesignToken("ob-typography-heading", "typography", {"family": "Inter", "size": 18, "weight": 600}),
            DesignToken("ob-typography-body", "typography", {"family": "Inter", "size": 14, "weight": 400}),
            DesignToken("ob-spacing-unit", "spacing", 8),
            DesignToken("ob-icon-vessel", "icon", "vessel-symbol"),
            DesignToken("ob-icon-alert", "icon", "alert-triangle"),
        ]
        for token in tokens:
            self._design_tokens[token.name] = token

    def add_ar_overlay(self, target_mmsi: str, target_name: str,
                       bearing: float, distance_nm: float,
                       cpa: float, tcpa: float, risk_level: float) -> AROverlay:
        """添加 AR 叠加目标"""
        overlay_id = f"ar-{target_mmsi}"

        # AR 视锥到像素映射 (简化: 假设 120° FOV, 1920px 宽)
        fov_deg = 120.0
        screen_width = 1920
        rel_bearing = bearing % 360
        if rel_bearing > 180:
            rel_bearing -= 360
        pixel_x = screen_width / 2 + (rel_bearing / (fov_deg / 2)) * (screen_width / 2)
        pixel_y = 540 - (distance_nm / 10.0) * 200  # 距离映射

        color = self._risk_to_color(risk_level)

        overlay = AROverlay(
            overlay_id=overlay_id,
            target_mmsi=target_mmsi,
            target_name=target_name,
            bearing=bearing,
            distance_nm=distance_nm,
            cpa=cpa,
            tcpa=tcpa,
            risk_level=risk_level,
            ar_position=(round(pixel_x, 1), round(max(0, pixel_y), 1)),
            visible=True,
            color=color,
        )

        self._ar_overlays[overlay_id] = overlay
        return overlay

    def _risk_to_color(self, risk: float) -> str:
        """风险等级到颜色映射"""
        if risk > 0.8:
            return "#FF0000"  # emergency red
        elif risk > 0.6:
            return "#FF6600"  # alarm orange
        elif risk > 0.4:
            return "#FFCC00"  # warning yellow
        elif risk > 0.2:
            return "#00CCFF"  # caution blue
        return "#00FF00"      # safe green

    def push_alert(self, severity: AlertSeverity, title: str, message: str,
                   source: str = "", auto_dismiss: bool = False) -> Dict[str, Any]:
        """推送警报 (IEC 62923 兼容)"""
        alert = {
            "id": f"alert-{len(self._alert_queue)+1}",
            "severity": severity.value,
            "title": title,
            "message": message,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "acknowledged": False,
            "auto_dismiss": auto_dismiss,
        }
        self._alert_queue.append(alert)

        # 更新认知负荷
        if severity in [AlertSeverity.EMERGENCY, AlertSeverity.ALARM]:
            self._tlx_score.mental_demand = min(100, self._tlx_score.mental_demand + 15)
            self._tlx_score.temporal_demand = min(100, self._tlx_score.temporal_demand + 10)
        elif severity == AlertSeverity.WARNING:
            self._tlx_score.mental_demand = min(100, self._tlx_score.mental_demand + 5)

        self._update_cognitive_state()
        return alert

    def acknowledge_alert(self, alert_id: str) -> bool:
        """确认警报"""
        for alert in self._alert_queue:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                self._tlx_score.mental_demand = max(0, self._tlx_score.mental_demand - 5)
                self._update_cognitive_state()
                return True
        return False

    def _update_cognitive_state(self) -> None:
        """评估操作员认知状态"""
        overall = self._tlx_score.overall
        if overall > 80:
            self._cognitive_state = CognitiveState.OVERLOADED
        elif overall > 60:
            self._cognitive_state = CognitiveState.FATIGUED
        elif overall > 30:
            self._cognitive_state = CognitiveState.NORMAL
        else:
            self._cognitive_state = CognitiveState.ALERT

    def get_attention_guidance(self) -> List[Dict[str, Any]]:
        """生成注意力引导优先级列表"""
        priorities = []
        unacked = [a for a in self._alert_queue if not a["acknowledged"]]

        severity_order = {
            "emergency": 0, "alarm": 1, "warning": 2, "caution": 3, "information": 4
        }
        unacked.sort(key=lambda a: severity_order.get(a["severity"], 5))

        for alert in unacked[:5]:
            priorities.append({
                "type": "alert",
                "id": alert["id"],
                "severity": alert["severity"],
                "title": alert["title"],
                "priority": severity_order.get(alert["severity"], 5),
            })

        dangerous_ar = sorted(
            [o for o in self._ar_overlays.values() if o.risk_level > 0.3],
            key=lambda o: -o.risk_level
        )
        for overlay in dangerous_ar[:3]:
            priorities.append({
                "type": "ar_target",
                "id": overlay.overlay_id,
                "target": overlay.target_name,
                "risk": overlay.risk_level,
                "priority": int((1 - overlay.risk_level) * 5),
            })

        self._attention_priorities = [p["id"] for p in priorities]
        return priorities

    def set_work_context(self, context: str) -> bool:
        """设置工作上下文"""
        try:
            self._work_context = WorkContext(context)
            return True
        except ValueError:
            return False

    def update_cloud_edge_sync(self, uploads: int = 0, downloads: int = 0,
                                latency_ms: float = 0.0, bandwidth_kbps: float = 0.0) -> Dict[str, Any]:
        """更新云边同步状态"""
        self._cloud_edge.last_sync = datetime.now()
        self._cloud_edge.pending_uploads += uploads
        self._cloud_edge.pending_downloads += downloads
        self._cloud_edge.sync_latency_ms = latency_ms
        self._cloud_edge.bandwidth_kbps = bandwidth_kbps

        if latency_ms > 5000:
            self._cloud_edge.mode = "compressed"
        elif latency_ms > 1000:
            self._cloud_edge.mode = "delta"
        else:
            self._cloud_edge.mode = "full"

        return {
            "mode": self._cloud_edge.mode,
            "latency_ms": self._cloud_edge.sync_latency_ms,
            "pending": self._cloud_edge.pending_uploads + self._cloud_edge.pending_downloads,
            "models_in_sync": self._cloud_edge.models_in_sync,
        }

    def simulate_model_ota(self, new_version: str) -> Dict[str, Any]:
        """模拟模型 OTA 更新"""
        old_version = self._cloud_edge.edge_model_version
        self._cloud_edge.edge_model_version = new_version
        self._cloud_edge.cloud_model_version = new_version
        self._cloud_edge.models_in_sync = True
        return {
            "old_version": old_version,
            "new_version": new_version,
            "in_sync": True,
        }

    def get_nasa_tlx(self) -> Dict[str, Any]:
        """获取 NASA-TLX 认知负荷评分"""
        return {
            "mental_demand": self._tlx_score.mental_demand,
            "physical_demand": self._tlx_score.physical_demand,
            "temporal_demand": self._tlx_score.temporal_demand,
            "performance": self._tlx_score.performance,
            "effort": self._tlx_score.effort,
            "frustration": self._tlx_score.frustration,
            "overall": self._tlx_score.overall,
            "cognitive_state": self._cognitive_state.value,
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "work_context": self._work_context.value,
            "ar_overlays": len(self._ar_overlays),
            "active_alerts": len([a for a in self._alert_queue if not a["acknowledged"]]),
            "cognitive_state": self._cognitive_state.value,
            "nasa_tlx_overall": self._tlx_score.overall,
            "cloud_edge": {
                "mode": self._cloud_edge.mode,
                "models_in_sync": self._cloud_edge.models_in_sync,
                "edge_version": self._cloud_edge.edge_model_version,
            },
            "design_tokens": len(self._design_tokens),
        }

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True


__all__ = [
    "OpenBridgeHMIChannel", "AROverlay", "NASATLXScore",
    "CloudEdgeSyncState", "AlertSeverity", "WorkContext", "CognitiveState",
]
