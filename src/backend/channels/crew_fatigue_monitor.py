# -*- coding: utf-8 -*-
"""
L5: Crew Fatigue Monitor - 船员疲劳监测

基于值班记录、休息质量和工作负荷评估船员疲劳状态，
生成预警和换班建议，符合 STCW 公约休息时间要求。

疲劳评分规则:
- 基础分 100 (完全清醒)
- 连续工作 > 4h → 每小时扣 10 分
- 休息 < 6h → 扣 20 分
- 高强度事件 → 每个扣 5 分
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class CrewFatigueMonitorChannel(MarineChannel):
    """船员疲劳监测 Channel — 跟踪值班、休息和工作负荷。"""

    name = "crew_fatigue"
    description = "船员疲劳监测与预警"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._watch_records: Dict[str, List[Dict[str, Any]]] = {}
        self._rest_records: Dict[str, List[Dict[str, Any]]] = {}
        self._workload_events: Dict[str, List[Dict[str, Any]]] = {}
        self._active_watch: List[Dict[str, Any]] = []
        self._watch_changes_count: int = 0

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Crew fatigue monitor ready")
        return True

    def get_status(self) -> Dict[str, Any]:
        all_crew = set(self._watch_records) | set(self._rest_records) | set(self._workload_events)
        fatigue_scores = {cid: self.calculate_fatigue_score(cid) for cid in all_crew}
        risk_alerts = self._build_risk_alerts(fatigue_scores)
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "active_watch": self._active_watch,
            "fatigue_scores": fatigue_scores,
            "risk_alerts": risk_alerts,
            "total_crew_tracked": len(all_crew),
            "watch_changes_count": self._watch_changes_count,
        }

    def shutdown(self) -> bool:
        self._active = False
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True

    async def start(self):
        self._active = True
        self._set_health(ChannelStatus.OK, "Running")

    async def stop(self):
        self._active = False

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")

        if event_type == "watch_change":
            return self._handle_watch_change(event)
        elif event_type == "rest_record":
            return self._handle_rest_record(event)
        elif event_type == "workload_event":
            return self._handle_workload_event(event)

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    # ---- event handlers ----

    def _handle_watch_change(self, event: dict) -> dict:
        crew_id = event.get("crew_id")
        if crew_id is None:
            return {"status": "error", "reason": "crew_id is required"}

        record = {
            "crew_id": crew_id,
            "position": event.get("position", "unknown"),
            "start_time": event.get("start_time", datetime.now().isoformat()),
            "end_time": event.get("end_time"),
        }

        self._watch_records.setdefault(crew_id, []).append(record)
        self._watch_changes_count += 1

        # 更新当前值班列表
        if record["end_time"] is None:
            if not any(w.get("crew_id") == crew_id for w in self._active_watch):
                self._active_watch.append({"crew_id": crew_id, "position": record["position"]})
        else:
            self._active_watch = [w for w in self._active_watch if w.get("crew_id") != crew_id]

        score = self.calculate_fatigue_score(crew_id)
        return {"status": "recorded", "crew_id": crew_id, "fatigue_score": score}

    def _handle_rest_record(self, event: dict) -> dict:
        crew_id = event.get("crew_id")
        if crew_id is None:
            return {"status": "error", "reason": "crew_id is required"}

        record = {
            "crew_id": crew_id,
            "rest_start": event.get("rest_start", datetime.now().isoformat()),
            "rest_end": event.get("rest_end"),
            "quality": event.get("quality", "normal"),
        }

        self._rest_records.setdefault(crew_id, []).append(record)
        score = self.calculate_fatigue_score(crew_id)
        return {"status": "recorded", "crew_id": crew_id, "fatigue_score": score}

    def _handle_workload_event(self, event: dict) -> dict:
        crew_id = event.get("crew_id")
        if crew_id is None:
            return {"status": "error", "reason": "crew_id is required"}

        record = {
            "crew_id": crew_id,
            "event_type": event.get("event_type", "general"),
            "intensity": event.get("intensity", "normal"),
            "timestamp": datetime.now().isoformat(),
        }

        self._workload_events.setdefault(crew_id, []).append(record)
        score = self.calculate_fatigue_score(crew_id)
        return {"status": "recorded", "crew_id": crew_id, "fatigue_score": score}

    # ---- core algorithms ----

    def calculate_fatigue_score(self, crew_id: str) -> float:
        score = 100.0

        # 连续工作时间扣分
        watches = self._watch_records.get(crew_id, [])
        if watches:
            latest = watches[-1]
            start_str = latest.get("start_time")
            end_str = latest.get("end_time")
            if start_str and end_str is None:
                try:
                    start_dt = datetime.fromisoformat(start_str)
                    hours_on = (datetime.now() - start_dt).total_seconds() / 3600
                except (ValueError, TypeError):
                    hours_on = 0.0
            elif start_str and end_str:
                try:
                    start_dt = datetime.fromisoformat(start_str)
                    end_dt = datetime.fromisoformat(end_str)
                    hours_on = (end_dt - start_dt).total_seconds() / 3600
                except (ValueError, TypeError):
                    hours_on = 0.0
            else:
                hours_on = 0.0

            if hours_on > 4:
                score -= (hours_on - 4) * 10

        # 休息不足扣分
        rests = self._rest_records.get(crew_id, [])
        if rests:
            latest_rest = rests[-1]
            rest_start = latest_rest.get("rest_start")
            rest_end = latest_rest.get("rest_end")
            quality = latest_rest.get("quality", "normal")
            if rest_start and rest_end:
                try:
                    rs = datetime.fromisoformat(rest_start)
                    re = datetime.fromisoformat(rest_end)
                    rest_hours = (re - rs).total_seconds() / 3600
                except (ValueError, TypeError):
                    rest_hours = 8.0
            else:
                rest_hours = 8.0

            if rest_hours < 6:
                score -= 20
            if quality == "poor":
                score -= 10
        else:
            # 无休息记录 — 视为休息不足
            if watches:
                score -= 20

        # 高强度事件扣分
        workloads = self._workload_events.get(crew_id, [])
        high_count = sum(1 for w in workloads if w.get("intensity") == "high")
        score -= high_count * 5

        return max(0.0, min(100.0, score))

    def get_fatigue_recommendations(self) -> List[Dict[str, Any]]:
        all_crew = set(self._watch_records) | set(self._rest_records) | set(self._workload_events)
        recommendations: List[Dict[str, Any]] = []

        for crew_id in all_crew:
            score = self.calculate_fatigue_score(crew_id)
            if score < 40:
                msg = "建议立即换班"
                level = "critical"
            elif score < 60:
                msg = "注意疲劳风险，建议30分钟内换班"
                level = "warning"
            elif score < 80:
                msg = "状态正常，继续监控"
                level = "normal"
            else:
                msg = "状态良好"
                level = "good"

            recommendations.append({
                "crew_id": crew_id,
                "fatigue_score": score,
                "level": level,
                "recommendation": msg,
            })

        return recommendations

    # ---- helpers ----

    def _build_risk_alerts(self, fatigue_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []
        for crew_id, score in fatigue_scores.items():
            if score < 40:
                alerts.append({
                    "crew_id": crew_id,
                    "score": score,
                    "level": "critical",
                    "message": f"船员 {crew_id} 疲劳评分 {score:.0f}，建议立即换班",
                })
            elif score < 60:
                alerts.append({
                    "crew_id": crew_id,
                    "score": score,
                    "level": "warning",
                    "message": f"船员 {crew_id} 疲劳评分 {score:.0f}，注意疲劳风险",
                })
        return alerts
