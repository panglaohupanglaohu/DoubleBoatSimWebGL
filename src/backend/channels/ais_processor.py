# -*- coding: utf-8 -*-
"""
L2: AIS Processor Channel - 独立 AIS 处理器

独立 AIS 消息解析和目标管理。
支持 ITU-R M.1371 定义的常见消息类型。
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority

logger = logging.getLogger(__name__)


class AISProcessorChannel(MarineChannel):
    """AIS 处理器 Channel — 消息解析与目标跟踪。"""

    name = "ais_processor"
    description = "AIS 消息解析与目标管理"
    version = "1.0.0"
    priority = ChannelPriority.P0

    def __init__(self, config=None, **kwargs):
        super().__init__(**(config or {}), **kwargs)
        self._active: bool = False
        self._targets: Dict[int, dict] = {}
        self._target_timeout_class_a: float = 180.0   # 3 分钟
        self._target_timeout_class_b: float = 360.0   # 6 分钟

    def initialize(self) -> bool:
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "AIS processor ready")
        return True

    def get_status(self) -> Dict[str, Any]:
        self._cleanup_expired()
        class_a = sum(1 for t in self._targets.values() if t.get("target_class") == "A")
        class_b = len(self._targets) - class_a
        return {
            "name": self.name,
            "active": self._active,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "active_targets": len(self._targets),
            "class_a_count": class_a,
            "class_b_count": class_b,
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

        if event_type != "ais_message":
            return {"status": "ignored", "reason": f"expected ais_message, got {event_type}"}

        msg_type = event.get("msg_type")
        payload = event.get("payload", {})
        if msg_type is None:
            return {"status": "error", "reason": "msg_type is required"}

        decoded = self.decode_message(msg_type, payload)
        if decoded.get("error"):
            return {"status": "error", "reason": decoded["error"]}

        mmsi = decoded.get("mmsi")
        if mmsi is not None:
            self.update_target(mmsi, decoded)

        return {"status": "processed", "msg_type": msg_type, "mmsi": mmsi}

    # ---- public helpers ----

    def decode_message(self, msg_type: int, payload: dict) -> dict:
        """解析 AIS 消息。"""
        if msg_type in (1, 2, 3):
            # 动态位置报告 (Class A)
            return {
                "mmsi": payload.get("mmsi"),
                "lat": payload.get("lat"),
                "lon": payload.get("lon"),
                "sog": payload.get("sog", 0.0),
                "cog": payload.get("cog", 0.0),
                "heading": payload.get("heading", 0.0),
                "nav_status": payload.get("nav_status", 0),
                "turn_rate": payload.get("turn_rate", 0.0),
                "msg_type": msg_type,
                "target_class": "A",
            }
        elif msg_type == 5:
            # 静态报告 (Class A)
            return {
                "mmsi": payload.get("mmsi"),
                "imo": payload.get("imo"),
                "callsign": payload.get("callsign", ""),
                "name": payload.get("name", ""),
                "ship_type": payload.get("ship_type", 0),
                "destination": payload.get("destination", ""),
                "eta": payload.get("eta", ""),
                "draught": payload.get("draught", 0.0),
                "msg_type": msg_type,
                "target_class": "A",
            }
        elif msg_type in (18, 19):
            # Class B 位置报告
            return {
                "mmsi": payload.get("mmsi"),
                "lat": payload.get("lat"),
                "lon": payload.get("lon"),
                "sog": payload.get("sog", 0.0),
                "cog": payload.get("cog", 0.0),
                "msg_type": msg_type,
                "target_class": "B",
            }
        elif msg_type == 21:
            # AtoN 报告
            return {
                "mmsi": payload.get("mmsi"),
                "lat": payload.get("lat"),
                "lon": payload.get("lon"),
                "name": payload.get("name", ""),
                "aid_type": payload.get("aid_type", 0),
                "msg_type": msg_type,
                "target_class": "AtoN",
            }
        elif msg_type == 24:
            # Class B 静态报告
            return {
                "mmsi": payload.get("mmsi"),
                "name": payload.get("name", ""),
                "ship_type": payload.get("ship_type", 0),
                "callsign": payload.get("callsign", ""),
                "msg_type": msg_type,
                "target_class": "B",
            }
        else:
            return {"error": f"unsupported msg_type: {msg_type}"}

    def update_target(self, mmsi: int, data: dict) -> dict:
        """更新或插入目标。"""
        now = datetime.now().isoformat()
        if mmsi in self._targets:
            self._targets[mmsi].update(data)
            self._targets[mmsi]["last_update"] = now
        else:
            data["last_update"] = now
            self._targets[mmsi] = data
        return self._targets[mmsi]

    def get_target_table(self) -> List[dict]:
        """返回所有活跃目标列表。"""
        self._cleanup_expired()
        return [{"mmsi": mmsi, **data} for mmsi, data in self._targets.items()]

    def get_target(self, mmsi: int) -> Optional[dict]:
        """查询单个目标。"""
        self._cleanup_expired()
        target = self._targets.get(mmsi)
        if target is None:
            return None
        return {"mmsi": mmsi, **target}

    # ---- internal ----

    def _cleanup_expired(self):
        """清理过期目标。"""
        now = datetime.now()
        expired = []
        for mmsi, data in self._targets.items():
            last_update = data.get("last_update")
            if last_update is None:
                expired.append(mmsi)
                continue
            try:
                ts = datetime.fromisoformat(last_update)
            except (ValueError, TypeError):
                expired.append(mmsi)
                continue
            target_class = data.get("target_class", "A")
            timeout = self._target_timeout_class_a if target_class == "A" else self._target_timeout_class_b
            if (now - ts).total_seconds() > timeout:
                expired.append(mmsi)
        for mmsi in expired:
            del self._targets[mmsi]
