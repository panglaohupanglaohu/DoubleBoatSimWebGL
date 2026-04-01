# -*- coding: utf-8 -*-
"""
L0: Deterministic Network Infrastructure - 确定性网络基础设施

万兆确定性光纤环网 + Zonal DC (区域直流配电) + 加固型 COTS 硬件监控

技术要点:
- 双冗余光纤环网 (Ring A / Ring B)，RSTP 快速自愈 < 50ms
- 时间敏感网络 (TSN) IEEE 802.1Qbv 时间感知调度
- Zonal DC 配电架构：直流母线 + 区域隔离 + 故障自愈
- 加固型 COTS (Commercial Off-The-Shelf) 硬件健康监控
- IEC 61162-450 (Ethernet Ship Network) 标准兼容

工程意义:
实现毫秒级故障隔离与电力恢复，保障 AI 算力在极端海况下永不掉线。
"""

from __future__ import annotations

import logging
import time
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class LinkStatus(Enum):
    """链路状态"""
    UP = "up"
    DOWN = "down"
    DEGRADED = "degraded"
    TESTING = "testing"


class ZoneStatus(Enum):
    """区域配电状态"""
    NORMAL = "normal"
    ISOLATED = "isolated"
    BACKUP = "backup"
    FAULT = "fault"


class NetworkProtocol(Enum):
    """网络协议类型"""
    RSTP = "rstp"           # 快速生成树协议
    PRP = "prp"             # 并行冗余协议 (IEC 62439-3)
    HSR = "hsr"             # 高可用无缝冗余
    TSN = "tsn"             # 时间敏感网络


@dataclass
class FiberLink:
    """光纤链路"""
    link_id: str
    ring: str                   # "A" or "B"
    source_node: str
    target_node: str
    status: LinkStatus = LinkStatus.UP
    bandwidth_gbps: float = 10.0    # 万兆
    latency_us: float = 5.0         # 微秒
    error_rate: float = 0.0
    last_switchover: Optional[datetime] = None
    total_switchovers: int = 0
    uptime_seconds: float = 0.0


@dataclass
class NetworkNode:
    """网络节点"""
    node_id: str
    node_type: str              # "switch", "router", "endpoint"
    zone: str                   # 区域标识
    ring_a_connected: bool = True
    ring_b_connected: bool = True
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    temperature: float = 35.0
    status: LinkStatus = LinkStatus.UP


@dataclass
class ZonalDCBus:
    """区域直流母线"""
    zone_id: str
    voltage_v: float = 750.0       # DC 750V 标准
    current_a: float = 0.0
    power_kw: float = 0.0
    status: ZoneStatus = ZoneStatus.NORMAL
    battery_soc: float = 100.0     # 电池荷电状态 %
    fault_isolated: bool = False
    recovery_time_ms: float = 0.0  # 故障恢复时间


@dataclass
class TSNSchedule:
    """TSN 时间感知调度条目"""
    stream_id: str
    priority: int               # 0-7, 7为最高
    cycle_time_us: float        # 调度周期 (微秒)
    max_latency_us: float       # 最大允许延迟
    jitter_us: float = 0.0     # 抖动
    bandwidth_mbps: float = 100.0


class DeterministicNetworkChannel(MarineChannel):
    """
    L0: 确定性网络基础设施 Channel

    实现万兆确定性光纤环网、Zonal DC 配电和 TSN 时间感知调度。
    保障船舶 AI 算力在极端海况下的确定性通信。

    核心指标:
    - 环网切换时间 < 50ms (RSTP/PRP)
    - TSN 确定性延迟 < 100μs
    - Zonal DC 故障隔离 < 10ms
    - 系统可用性 > 99.999%
    """

    name = "deterministic_network"
    description = "L0: 确定性网络基础设施 (万兆光纤环网 + Zonal DC + TSN)"
    version = "1.0.0"
    priority = ChannelPriority.P0
    dependencies: List[str] = []

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.config = config or {}
        self._links: Dict[str, FiberLink] = {}
        self._nodes: Dict[str, NetworkNode] = {}
        self._zones: Dict[str, ZonalDCBus] = {}
        self._tsn_schedules: Dict[str, TSNSchedule] = {}
        self._protocol = NetworkProtocol(self.config.get("protocol", "rstp"))
        self._fault_log: List[Dict[str, Any]] = []
        self._switchover_count = 0
        self._last_fault_time: Optional[datetime] = None

    def initialize(self) -> bool:
        """初始化确定性网络"""
        self._setup_dual_ring()
        self._setup_zonal_dc()
        self._setup_tsn_schedules()
        self._initialized = True
        self._set_health(ChannelStatus.OK, "确定性网络基础设施就绪")
        return True

    def _setup_dual_ring(self) -> None:
        """初始化双冗余光纤环网"""
        nodes = self.config.get("nodes", [
            {"id": "BR-SW1", "type": "switch", "zone": "bridge"},
            {"id": "ER-SW1", "type": "switch", "zone": "engine_room"},
            {"id": "CR-SW1", "type": "switch", "zone": "cargo"},
            {"id": "AC-SW1", "type": "switch", "zone": "accommodation"},
            {"id": "CORE-SW1", "type": "switch", "zone": "core"},
        ])

        for node_cfg in nodes:
            node = NetworkNode(
                node_id=node_cfg["id"],
                node_type=node_cfg.get("type", "switch"),
                zone=node_cfg.get("zone", "general"),
            )
            self._nodes[node.node_id] = node

        node_ids = list(self._nodes.keys())
        for i in range(len(node_ids)):
            next_i = (i + 1) % len(node_ids)
            for ring in ["A", "B"]:
                link_id = f"{ring}-{node_ids[i]}-{node_ids[next_i]}"
                self._links[link_id] = FiberLink(
                    link_id=link_id,
                    ring=ring,
                    source_node=node_ids[i],
                    target_node=node_ids[next_i],
                    bandwidth_gbps=10.0,
                    latency_us=5.0 + (i * 0.5),
                )

    def _setup_zonal_dc(self) -> None:
        """设置 Zonal DC 配电系统"""
        zones = self.config.get("dc_zones", [
            {"id": "zone_bridge", "voltage": 750.0},
            {"id": "zone_engine", "voltage": 750.0},
            {"id": "zone_cargo", "voltage": 750.0},
            {"id": "zone_accommodation", "voltage": 750.0},
        ])

        for zone_cfg in zones:
            self._zones[zone_cfg["id"]] = ZonalDCBus(
                zone_id=zone_cfg["id"],
                voltage_v=zone_cfg.get("voltage", 750.0),
                battery_soc=100.0,
            )

    def _setup_tsn_schedules(self) -> None:
        """设置 TSN 时间感知调度"""
        schedules = [
            TSNSchedule("nav_critical", priority=7, cycle_time_us=125, max_latency_us=50, bandwidth_mbps=1000),
            TSNSchedule("engine_telemetry", priority=6, cycle_time_us=250, max_latency_us=100, bandwidth_mbps=500),
            TSNSchedule("ais_data", priority=5, cycle_time_us=1000, max_latency_us=500, bandwidth_mbps=100),
            TSNSchedule("video_surveillance", priority=3, cycle_time_us=8000, max_latency_us=5000, bandwidth_mbps=2000),
            TSNSchedule("crew_internet", priority=1, cycle_time_us=50000, max_latency_us=50000, bandwidth_mbps=1000),
        ]
        for sched in schedules:
            self._tsn_schedules[sched.stream_id] = sched

    def simulate_link_fault(self, link_id: str) -> Dict[str, Any]:
        """模拟链路故障并执行自动切换"""
        link = self._links.get(link_id)
        if not link:
            return {"error": f"Link {link_id} not found"}

        fault_time = datetime.now()
        link.status = LinkStatus.DOWN

        recovery_info = self._execute_switchover(link, fault_time)

        self._fault_log.append({
            "timestamp": fault_time.isoformat(),
            "link_id": link_id,
            "ring": link.ring,
            "recovery_time_ms": recovery_info["recovery_time_ms"],
            "switchover_type": recovery_info["switchover_type"],
        })

        return recovery_info

    def _execute_switchover(self, failed_link: FiberLink, fault_time: datetime) -> Dict[str, Any]:
        """执行环网切换"""
        self._switchover_count += 1
        self._last_fault_time = fault_time

        alt_ring = "B" if failed_link.ring == "A" else "A"
        alt_links = [l for l in self._links.values() if l.ring == alt_ring]

        all_alt_up = all(l.status == LinkStatus.UP for l in alt_links)

        if self._protocol == NetworkProtocol.PRP:
            recovery_time_ms = 0.0
            switchover_type = "hitless_prp"
        elif self._protocol == NetworkProtocol.HSR:
            recovery_time_ms = 0.0
            switchover_type = "hitless_hsr"
        else:
            recovery_time_ms = 25.0 if all_alt_up else 45.0
            switchover_type = "rstp_convergence"

        failed_link.last_switchover = fault_time
        failed_link.total_switchovers += 1

        return {
            "recovery_time_ms": recovery_time_ms,
            "switchover_type": switchover_type,
            "alternate_ring": alt_ring,
            "alternate_ring_healthy": all_alt_up,
            "total_switchovers": self._switchover_count,
        }

    def isolate_zone_fault(self, zone_id: str) -> Dict[str, Any]:
        """区域直流故障隔离"""
        zone = self._zones.get(zone_id)
        if not zone:
            return {"error": f"Zone {zone_id} not found"}

        zone.fault_isolated = True
        zone.status = ZoneStatus.ISOLATED
        zone.recovery_time_ms = 8.0  # < 10ms 隔离

        other_zones = {zid: z for zid, z in self._zones.items() if zid != zone_id}
        for z in other_zones.values():
            if z.status == ZoneStatus.NORMAL:
                z.status = ZoneStatus.NORMAL  # 不受影响

        return {
            "zone_id": zone_id,
            "isolated": True,
            "recovery_time_ms": zone.recovery_time_ms,
            "affected_zones": 0,
            "healthy_zones": sum(1 for z in other_zones.values() if z.status == ZoneStatus.NORMAL),
        }

    def restore_zone(self, zone_id: str) -> bool:
        """恢复隔离区域"""
        zone = self._zones.get(zone_id)
        if not zone:
            return False
        zone.fault_isolated = False
        zone.status = ZoneStatus.NORMAL
        return True

    def restore_link(self, link_id: str) -> bool:
        """恢复链路"""
        link = self._links.get(link_id)
        if not link:
            return False
        link.status = LinkStatus.UP
        return True

    def get_tsn_latency(self, stream_id: str) -> Optional[float]:
        """获取 TSN 流的确定性延迟"""
        schedule = self._tsn_schedules.get(stream_id)
        if not schedule:
            return None
        jitter = math.sin(time.time()) * schedule.jitter_us
        return schedule.max_latency_us + jitter

    def get_network_topology(self) -> Dict[str, Any]:
        """获取网络拓扑"""
        return {
            "nodes": {nid: {"type": n.node_type, "zone": n.zone, "status": n.status.value}
                      for nid, n in self._nodes.items()},
            "links": {lid: {"ring": l.ring, "status": l.status.value,
                           "bandwidth_gbps": l.bandwidth_gbps, "latency_us": l.latency_us}
                      for lid, l in self._links.items()},
            "rings": {
                "A": {"links_up": sum(1 for l in self._links.values() if l.ring == "A" and l.status == LinkStatus.UP),
                      "links_total": sum(1 for l in self._links.values() if l.ring == "A")},
                "B": {"links_up": sum(1 for l in self._links.values() if l.ring == "B" and l.status == LinkStatus.UP),
                      "links_total": sum(1 for l in self._links.values() if l.ring == "B")},
            }
        }

    def get_zonal_dc_status(self) -> Dict[str, Any]:
        """获取 Zonal DC 配电状态"""
        return {
            zone_id: {
                "voltage_v": z.voltage_v,
                "current_a": z.current_a,
                "power_kw": z.power_kw,
                "status": z.status.value,
                "battery_soc": z.battery_soc,
                "fault_isolated": z.fault_isolated,
            }
            for zone_id, z in self._zones.items()
        }

    def calculate_availability(self) -> float:
        """计算系统可用性"""
        total_links = len(self._links)
        if total_links == 0:
            return 0.0
        up_links = sum(1 for l in self._links.values() if l.status == LinkStatus.UP)
        ring_a_up = sum(1 for l in self._links.values() if l.ring == "A" and l.status == LinkStatus.UP)
        ring_b_up = sum(1 for l in self._links.values() if l.ring == "B" and l.status == LinkStatus.UP)
        ring_a_total = sum(1 for l in self._links.values() if l.ring == "A")
        ring_b_total = sum(1 for l in self._links.values() if l.ring == "B")

        if ring_a_total == 0 or ring_b_total == 0:
            return up_links / total_links

        ring_a_avail = ring_a_up / ring_a_total
        ring_b_avail = ring_b_up / ring_b_total
        combined = 1.0 - (1.0 - ring_a_avail) * (1.0 - ring_b_avail)
        return round(combined, 6)

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "protocol": self._protocol.value,
            "availability": self.calculate_availability(),
            "topology": self.get_network_topology(),
            "zonal_dc": self.get_zonal_dc_status(),
            "tsn_streams": len(self._tsn_schedules),
            "total_switchovers": self._switchover_count,
            "fault_log_size": len(self._fault_log),
        }

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True


__all__ = ["DeterministicNetworkChannel", "FiberLink", "NetworkNode", "ZonalDCBus", "TSNSchedule"]
