#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voyage Planner - 航次计划管理

参考 SVESSEL Onboard 功能:
- Route Monitoring (航线监控)
- eLogbook (电子航海日志)
- Daily Report (日报)

参考 DFFAS FOC 岸基系统:
- 航次计划与执行监控
- ETA 动态更新
- 港口逻辑与靠离泊窗口管理
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
import math

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority


class VoyageStatus(Enum):
    """航次状态."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class PortCallType(Enum):
    """港口作业类型."""
    LOADING = "loading"
    DISCHARGING = "discharging"
    BUNKERING = "bunkering"
    CREW_CHANGE = "crew_change"
    REPAIR = "repair"
    TRANSIT = "transit"


@dataclass
class PortCall:
    """港口靠泊计划."""
    port_id: str
    port_name: str
    country: str
    latitude: float
    longitude: float
    call_type: PortCallType
    eta: str                     # ISO 格式
    etd: str                     # ISO 格式
    berth: str = ""
    pilot_required: bool = True
    draft_limit_m: float = 15.0
    notes: str = ""
    actual_arrival: Optional[str] = None
    actual_departure: Optional[str] = None


@dataclass
class VoyagePlan:
    """航次计划."""
    voyage_id: str
    vessel_name: str
    departure_port: PortCall
    arrival_port: PortCall
    intermediate_ports: List[PortCall] = field(default_factory=list)
    status: VoyageStatus = VoyageStatus.PLANNED
    total_distance_nm: float = 0.0
    cargo_type: str = ""
    cargo_weight_mt: float = 0.0
    created_at: str = ""
    updated_at: str = ""


@dataclass
class LogEntry:
    """电子航海日志条目 (参考 SVESSEL eLogbook)."""
    timestamp: str
    entry_type: str    # "position", "weather", "event", "engine", "safety"
    content: str
    position_lat: Optional[float] = None
    position_lon: Optional[float] = None
    course: Optional[float] = None
    speed: Optional[float] = None
    author: str = "system"


class VoyagePlannerChannel(MarineChannel):
    """航次计划管理 Channel.

    对标 SVESSEL Onboard Route Monitoring + eLogbook + Daily Report。
    管理航次生命周期、ETA 动态更新、电子日志、日报生成。
    """

    name = "voyage_planner"
    description = "航次计划管理 - 航次生命周期、ETA动态更新与电子航海日志"
    version = "1.0.0"
    priority = ChannelPriority.P1
    dependencies = ["route_optimizer", "intelligent_navigation"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_voyage: Optional[VoyagePlan] = None
        self._voyage_history: List[VoyagePlan] = []
        self._logbook: List[LogEntry] = []
        self._daily_reports: List[Dict] = []
        self._current_position: Dict[str, float] = {"lat": 0, "lon": 0, "course": 0, "speed": 0}

    def initialize(self) -> bool:
        self._initialized = True
        self._set_health(ChannelStatus.OK, "Voyage planner ready")
        return True

    def create_voyage(
        self,
        voyage_id: str,
        vessel_name: str,
        departure: Dict,
        arrival: Dict,
        intermediate: Optional[List[Dict]] = None,
        cargo_type: str = "",
        cargo_weight_mt: float = 0.0,
    ) -> Dict[str, Any]:
        """创建新航次计划."""
        dep_port = self._make_port_call(departure)
        arr_port = self._make_port_call(arrival)
        inter_ports = [self._make_port_call(p) for p in (intermediate or [])]

        dist = self._calc_total_distance(dep_port, arr_port, inter_ports)

        now = datetime.now().isoformat()
        self._current_voyage = VoyagePlan(
            voyage_id=voyage_id,
            vessel_name=vessel_name,
            departure_port=dep_port,
            arrival_port=arr_port,
            intermediate_ports=inter_ports,
            total_distance_nm=round(dist, 1),
            cargo_type=cargo_type,
            cargo_weight_mt=cargo_weight_mt,
            created_at=now,
            updated_at=now,
        )

        self._add_log("event", f"航次 {voyage_id} 创建: {dep_port.port_name} → {arr_port.port_name}")
        return self._voyage_summary()

    @staticmethod
    def _make_port_call(data: Dict) -> PortCall:
        call_type_map = {
            "loading": PortCallType.LOADING,
            "discharging": PortCallType.DISCHARGING,
            "bunkering": PortCallType.BUNKERING,
            "crew_change": PortCallType.CREW_CHANGE,
            "repair": PortCallType.REPAIR,
            "transit": PortCallType.TRANSIT,
        }
        return PortCall(
            port_id=data.get("id", ""),
            port_name=data.get("name", "Unknown"),
            country=data.get("country", ""),
            latitude=float(data.get("lat", 0)),
            longitude=float(data.get("lon", 0)),
            call_type=call_type_map.get(data.get("type", "transit"), PortCallType.TRANSIT),
            eta=data.get("eta", ""),
            etd=data.get("etd", ""),
            berth=data.get("berth", ""),
            pilot_required=data.get("pilot", True),
            draft_limit_m=float(data.get("draft_limit", 15.0)),
            notes=data.get("notes", ""),
        )

    def start_voyage(self) -> Dict[str, Any]:
        """开始航次."""
        if self._current_voyage is None:
            return {"error": "无当前航次"}
        self._current_voyage.status = VoyageStatus.IN_PROGRESS
        self._current_voyage.departure_port.actual_departure = datetime.now().isoformat()
        self._current_voyage.updated_at = datetime.now().isoformat()
        self._add_log("event", "航次开始，离港")
        return self._voyage_summary()

    def update_position(
        self, lat: float, lon: float, course: float = 0, speed: float = 0
    ) -> Dict[str, Any]:
        """更新当前位置, 自动计算 ETA."""
        self._current_position = {"lat": lat, "lon": lon, "course": course, "speed": speed}

        result: Dict[str, Any] = {"position": self._current_position}

        if self._current_voyage and self._current_voyage.status == VoyageStatus.IN_PROGRESS:
            arr = self._current_voyage.arrival_port
            remaining = self._haversine_nm(lat, lon, arr.latitude, arr.longitude)
            eta_hours = remaining / max(speed, 0.1) if speed > 0.5 else float('inf')

            if eta_hours < float('inf'):
                eta_time = datetime.now() + timedelta(hours=eta_hours)
                result["remaining_distance_nm"] = round(remaining, 1)
                result["eta"] = eta_time.isoformat()
                result["eta_hours"] = round(eta_hours, 1)
            else:
                result["remaining_distance_nm"] = round(remaining, 1)
                result["eta"] = "N/A"

            # 进度百分比
            total = self._current_voyage.total_distance_nm
            if total > 0:
                progress = max(0, min(100, (1 - remaining / total) * 100))
                result["progress_pct"] = round(progress, 1)

        return result

    def complete_voyage(self) -> Dict[str, Any]:
        """完成航次."""
        if self._current_voyage is None:
            return {"error": "无当前航次"}
        self._current_voyage.status = VoyageStatus.COMPLETED
        self._current_voyage.arrival_port.actual_arrival = datetime.now().isoformat()
        self._current_voyage.updated_at = datetime.now().isoformat()
        self._add_log("event", "航次完成，到港")
        self._voyage_history.append(self._current_voyage)
        summary = self._voyage_summary()
        self._current_voyage = None
        return summary

    def _add_log(self, entry_type: str, content: str) -> LogEntry:
        """添加航海日志条目."""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            entry_type=entry_type,
            content=content,
            position_lat=self._current_position.get("lat"),
            position_lon=self._current_position.get("lon"),
            course=self._current_position.get("course"),
            speed=self._current_position.get("speed"),
        )
        self._logbook.append(entry)
        if len(self._logbook) > 1000:
            self._logbook = self._logbook[-1000:]
        return entry

    def add_log_entry(self, entry_type: str, content: str, author: str = "officer") -> Dict:
        """手动添加日志条目."""
        entry = self._add_log(entry_type, content)
        entry.author = author
        return {
            "timestamp": entry.timestamp,
            "type": entry.entry_type,
            "content": entry.content,
            "author": entry.author,
        }

    def generate_daily_report(self) -> Dict[str, Any]:
        """生成日报 (SVESSEL Daily Report)."""
        now = datetime.now()
        today_entries = [
            e for e in self._logbook
            if e.timestamp[:10] == now.strftime("%Y-%m-%d")
        ]

        report = {
            "report_date": now.strftime("%Y-%m-%d"),
            "generated_at": now.isoformat(),
            "vessel_name": self._current_voyage.vessel_name if self._current_voyage else "N/A",
            "voyage_id": self._current_voyage.voyage_id if self._current_voyage else "N/A",
            "voyage_status": self._current_voyage.status.value if self._current_voyage else "none",
            "position": self._current_position,
            "log_entries_today": len(today_entries),
            "entries": [
                {"time": e.timestamp, "type": e.entry_type, "content": e.content}
                for e in today_entries[-20:]
            ],
        }

        if self._current_voyage and self._current_voyage.status == VoyageStatus.IN_PROGRESS:
            arr = self._current_voyage.arrival_port
            remaining = self._haversine_nm(
                self._current_position["lat"], self._current_position["lon"],
                arr.latitude, arr.longitude,
            )
            speed = self._current_position.get("speed", 0)
            report["remaining_nm"] = round(remaining, 1)
            report["destination"] = arr.port_name
            if speed > 0.5:
                report["eta_hours"] = round(remaining / speed, 1)

        self._daily_reports.append(report)
        return report

    def _voyage_summary(self) -> Dict[str, Any]:
        """航次摘要."""
        v = self._current_voyage
        if v is None:
            return {"status": "no_active_voyage"}
        return {
            "voyage_id": v.voyage_id,
            "vessel_name": v.vessel_name,
            "status": v.status.value,
            "departure": {"port": v.departure_port.port_name, "eta": v.departure_port.eta},
            "arrival": {"port": v.arrival_port.port_name, "eta": v.arrival_port.eta},
            "intermediate_ports": [
                {"port": p.port_name, "eta": p.eta, "type": p.call_type.value}
                for p in v.intermediate_ports
            ],
            "total_distance_nm": v.total_distance_nm,
            "cargo": {"type": v.cargo_type, "weight_mt": v.cargo_weight_mt},
            "created_at": v.created_at,
        }

    def _calc_total_distance(
        self, dep: PortCall, arr: PortCall, intermediates: List[PortCall]
    ) -> float:
        all_ports = [dep] + intermediates + [arr]
        total = 0.0
        for i in range(len(all_ports) - 1):
            total += self._haversine_nm(
                all_ports[i].latitude, all_ports[i].longitude,
                all_ports[i + 1].latitude, all_ports[i + 1].longitude,
            )
        return total

    @staticmethod
    def _haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 3440.065
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def get_status(self) -> Dict[str, Any]:
        return {
            "channel": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": "ok" if self._initialized else "off",
            "health_message": f"Voyage: {self._current_voyage.voyage_id if self._current_voyage else 'none'}",
            "current_voyage": self._voyage_summary(),
            "logbook_entries": len(self._logbook),
            "completed_voyages": len(self._voyage_history),
            "daily_reports_generated": len(self._daily_reports),
        }

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shut down")
        return True
