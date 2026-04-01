# -*- coding: utf-8 -*-
"""
L2: Cargo Monitor Channel - 货物监控

监测各货舱的货物状态 (重量、温度、湿度)，
跟踪装卸事件，并进行简化稳性估算。

简化稳性模型:
- GM = KM - KG
- KM ≈ KB + BM, 其中 BM ≈ B² / (12 × T)
- KB ≈ T / 2
- KG 基于货物重心分布加权平均
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class CargoMonitorChannel(MarineChannel):
    """货物监控 Channel — 货物状态、装卸事件与简化稳性估算。"""

    name = "cargo_monitor"
    description = "货物监控与简化稳性估算"
    version = "1.0.0"
    priority = ChannelPriority.P1

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        # 货舱数据: hold_id -> {cargo_type, weight_tons, temperature, humidity, kg_height}
        self._holds: Dict[str, Dict[str, Any]] = {}
        # 装卸记录
        self._loading_events: List[Dict[str, Any]] = []
        # 船舶参数 (可通过 config 覆盖)
        cfg = config or {}
        self._beam: float = cfg.get("beam", 26.0)
        self._draft: float = cfg.get("draft", 5.5)
        self._lightship_weight: float = cfg.get("lightship_weight", 15000.0)
        self._lightship_kg: float = cfg.get("lightship_kg", 6.0)

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "Cargo monitor ready")
        return True

    def get_status(self) -> Dict[str, Any]:
        total_weight = sum(h.get("weight_tons", 0.0) for h in self._holds.values())
        stability = self.check_stability()
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "holds": list(self._holds.values()),
            "total_weight": total_weight,
            "gm_estimate": stability["gm"],
            "trim": stability["trim"],
            "stability_status": stability["status"],
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

        if event_type == "cargo_status":
            return self._handle_cargo_status(event)
        elif event_type == "loading_event":
            return self._handle_loading_event(event)
        elif event_type == "stability_check":
            return self._handle_stability_check(event)

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    # ---- event handlers ----

    def _handle_cargo_status(self, event: dict) -> dict:
        hold_id = event.get("hold_id")
        if hold_id is None:
            return {"status": "error", "reason": "hold_id is required"}

        self._holds[hold_id] = {
            "hold_id": hold_id,
            "cargo_type": event.get("cargo_type", "unknown"),
            "weight_tons": event.get("weight_tons", 0.0),
            "temperature": event.get("temperature"),
            "humidity": event.get("humidity"),
            "kg_height": event.get("kg_height", self._draft * 0.6),
            "updated_at": datetime.now().isoformat(),
        }
        return {"status": "updated", "hold_id": hold_id}

    def _handle_loading_event(self, event: dict) -> dict:
        hold_id = event.get("hold_id")
        if hold_id is None:
            return {"status": "error", "reason": "hold_id is required"}

        operation = event.get("operation", "load")
        weight_change = event.get("weight_change", 0.0)

        record = {
            "hold_id": hold_id,
            "operation": operation,
            "weight_change": weight_change,
            "timestamp": datetime.now().isoformat(),
        }
        self._loading_events.append(record)

        # 更新货舱重量
        if hold_id in self._holds:
            if operation == "load":
                self._holds[hold_id]["weight_tons"] += weight_change
            elif operation == "unload":
                self._holds[hold_id]["weight_tons"] = max(
                    0.0, self._holds[hold_id]["weight_tons"] - weight_change
                )
            self._holds[hold_id]["updated_at"] = datetime.now().isoformat()

        return {"status": "recorded", "operation": operation, "hold_id": hold_id}

    def _handle_stability_check(self, event: dict) -> dict:
        stability = self.check_stability()
        return {**stability, "event_status": "checked"}

    # ---- core algorithms ----

    def check_stability(self) -> Dict[str, Any]:
        """简化稳性估算。

        GM = KM - KG
        KM = KB + BM
        KB ≈ T / 2
        BM ≈ B² / (12 × T)
        KG = Σ(wi × kgi) / Σ(wi)  (包含空船)
        """
        T = self._draft
        B = self._beam

        if T <= 0:
            return {"gm": 0.0, "km": 0.0, "kg": 0.0, "trim": 0.0, "status": "error"}

        KB = T / 2.0
        BM = (B ** 2) / (12.0 * T)
        KM = KB + BM

        # 加权 KG
        total_weight = self._lightship_weight
        moment = self._lightship_weight * self._lightship_kg

        for hold in self._holds.values():
            w = hold.get("weight_tons", 0.0)
            kg_h = hold.get("kg_height", T * 0.6)
            total_weight += w
            moment += w * kg_h

        KG = moment / total_weight if total_weight > 0 else 0.0
        GM = KM - KG

        # 简化纵倾估算 (基于货物前后分布不均匀度)
        trim = self._estimate_trim()

        if GM < 0.15:
            status = "critical"
        elif GM < 0.5:
            status = "warning"
        else:
            status = "ok"

        return {
            "gm": round(GM, 3),
            "km": round(KM, 3),
            "kg": round(KG, 3),
            "trim": round(trim, 3),
            "status": status,
        }

    def _estimate_trim(self) -> float:
        """简化纵倾估算 — 基于前后货舱重量差。"""
        forward_weight = 0.0
        aft_weight = 0.0
        for hold in self._holds.values():
            hold_id = hold.get("hold_id", "")
            w = hold.get("weight_tons", 0.0)
            # 简单规则: hold id 含 'F'/'1'/'2' 归前部, 含 'A'/'4'/'5' 归后部
            if any(c in str(hold_id).upper() for c in ("F", "1", "2")):
                forward_weight += w
            elif any(c in str(hold_id).upper() for c in ("A", "4", "5")):
                aft_weight += w
            else:
                forward_weight += w / 2
                aft_weight += w / 2

        total = forward_weight + aft_weight
        if total <= 0:
            return 0.0
        # 归一化差值作为纵倾指标 (正值 = 尾倾)
        return (aft_weight - forward_weight) / total
