# -*- coding: utf-8 -*-
"""
Cargo Orbit Telemetry Channel - 货船轨道遥测上报

继承 MarineChannel，通过 process_event 上报 cargo 当前 lat/lon。
与 CargoShipOrbitChannel 配合使用，将货船在 3D 场景中的
圆周运动位置 (x, z) 转换为地理坐标 (lat, lon) 并上报。
"""

from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Any, Dict, Optional

from channels.marine_base import MarineChannel, ChannelPriority, ChannelStatus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 坐标转换常量
# ---------------------------------------------------------------------------

# 模拟场景原点 (双体船位置) 的地理坐标
# 设定在上海港外海约 31.23°N, 121.47°E
ORIGIN_LAT: float = 31.2304
ORIGIN_LON: float = 121.4737

# 场景单位 → 经纬度转换因子
# 1 场景单位 ≈ 0.0001 度 (约 11 米)
SCENE_TO_DEG: float = 0.0001


def _scene_to_geo(x: float, z: float) -> tuple[float, float]:
    """将场景坐标 (x, z) 转换为地理坐标 (lat, lon)。

    场景坐标系: x 轴向东 (lon 增加), z 轴向北 (lat 增加)。

    Args:
        x: 场景 X 坐标 (东向)
        z: 场景 Z 坐标 (北向)

    Returns:
        (latitude, longitude) 元组
    """
    lat = ORIGIN_LAT + z * SCENE_TO_DEG
    lon = ORIGIN_LON + x * SCENE_TO_DEG
    return (round(lat, 6), round(lon, 6))


# ---------------------------------------------------------------------------
# Cargo Orbit Telemetry Channel
# ---------------------------------------------------------------------------

class CargoOrbitTelemetryChannel(MarineChannel):
    """货船轨道遥测上报 Channel。

    接收 cargo_orbit_telemetry 类型的事件，将货船在场景中的
    圆周运动位置 (x, z) 转换为地理坐标 (lat, lon) 并记录/上报。

    支持的事件类型:
      - "cargo_orbit_telemetry": 上报货船遥测数据
        需包含字段: x, z (场景坐标), angle_deg (当前角度), distance (距双体船距离)
      - "get_latest_telemetry": 获取最新遥测数据
    """

    name = "cargo_orbit_telemetry"
    description = "货船轨道遥测上报 — 将场景坐标转换为地理坐标并上报"
    version = "1.0.0"
    priority = ChannelPriority.P2  # 辅助功能
    dependencies: list[str] = [
        "cargo_ship_orbit",  # 依赖货船轨道控制 Channel
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self._config = config or {}
        self._active: bool = False

        # 最新遥测数据缓存
        self._latest_telemetry: Dict[str, Any] = {
            "latitude": ORIGIN_LAT,
            "longitude": ORIGIN_LON,
            "angle_deg": 0.0,
            "distance": 0.0,
            "heading_deg": 0.0,
            "timestamp": None,
        }

        # 遥测历史记录
        self._telemetry_history: list[Dict[str, Any]] = []

        # 最大历史记录数
        self._max_history: int = 1000

        logger.info("📡 CargoOrbitTelemetryChannel initialized (origin=%.4f, %.4f)",
                     ORIGIN_LAT, ORIGIN_LON)

    # ── MarineChannel 接口 ───────────────────────────────────

    def initialize(self) -> bool:
        """初始化遥测 Channel。"""
        self._initialized = True
        self._active = True
        self._set_health(ChannelStatus.OK, "货船轨道遥测就绪")
        logger.info("📡 Cargo orbit telemetry initialized")
        return True

    def shutdown(self) -> bool:
        """关闭遥测 Channel。"""
        self._initialized = False
        self._active = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True

    def get_status(self) -> Dict[str, Any]:
        """获取 Channel 当前状态。"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "priority": self.priority.value,
            "initialized": self._initialized,
            "active": self._active,
            "health": self._health.status.value if self._health else "unknown",
            "health_message": self._health.message if self._health else "",
            "latest_telemetry": dict(self._latest_telemetry),
            "history_count": len(self._telemetry_history),
            "origin": {"lat": ORIGIN_LAT, "lon": ORIGIN_LON},
        }

    def process_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理外部事件。

        支持的事件类型:
          - "cargo_orbit_telemetry": 上报货船遥测数据
            需包含: x (float), z (float), angle_deg (float), distance (float)
          - "get_latest_telemetry": 获取最新遥测数据

        Args:
            event: 事件字典，必须包含 "type" 字段

        Returns:
            处理结果字典
        """
        event_type = event.get("type", "")

        if event_type == "cargo_orbit_telemetry":
            return self._handle_telemetry(event)

        elif event_type == "get_latest_telemetry":
            return {
                "status": "ok",
                "action": "get_latest_telemetry",
                "telemetry": dict(self._latest_telemetry),
            }

        return {"status": "ignored", "reason": f"unknown event type: {event_type}"}

    # ── 内部处理方法 ─────────────────────────────────────────

    def _handle_telemetry(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """处理遥测上报事件。

        将场景坐标 (x, z) 转换为地理坐标 (lat, lon)，
        并记录到历史缓存中。

        Args:
            event: 遥测事件字典

        Returns:
            处理结果字典
        """
        x = event.get("x", 0.0)
        z = event.get("z", 0.0)
        angle_deg = event.get("angle_deg", 0.0)
        distance = event.get("distance", 0.0)
        heading_deg = event.get("heading_deg", 0.0)

        # 坐标转换
        lat, lon = _scene_to_geo(x, z)

        now = datetime.now()

        # 更新最新遥测
        self._latest_telemetry = {
            "latitude": lat,
            "longitude": lon,
            "angle_deg": round(angle_deg, 2),
            "distance": round(distance, 2),
            "heading_deg": round(heading_deg, 2),
            "timestamp": now.isoformat(),
            "scene_x": round(x, 2),
            "scene_z": round(z, 2),
        }

        # 记录历史
        self._telemetry_history.append(dict(self._latest_telemetry))
        if len(self._telemetry_history) > self._max_history:
            self._telemetry_history = self._telemetry_history[-self._max_history:]

        logger.debug("📡 Telemetry: lat=%.6f, lon=%.6f, angle=%.1f°, dist=%.1f",
                     lat, lon, angle_deg, distance)

        return {
            "status": "ok",
            "action": "telemetry_reported",
            "latitude": lat,
            "longitude": lon,
            "angle_deg": round(angle_deg, 2),
            "distance": round(distance, 2),
        }

    # ── 公共方法 ─────────────────────────────────────────────

    def get_latest_telemetry(self) -> Dict[str, Any]:
        """获取最新遥测数据。

        Returns:
            最新遥测数据字典
        """
        return dict(self._latest_telemetry)

    def get_telemetry_history(self, limit: int = 10) -> list[Dict[str, Any]]:
        """获取遥测历史记录。

        Args:
            limit: 返回的最大记录数

        Returns:
            遥测历史记录列表 (最新的在前)
        """
        return list(reversed(self._telemetry_history[-limit:]))

    def reset_history(self) -> None:
        """清空遥测历史记录。"""
        self._telemetry_history.clear()
        logger.info("📡 Telemetry history cleared")


__all__ = ["CargoOrbitTelemetryChannel", "_scene_to_geo", "ORIGIN_LAT", "ORIGIN_LON"]
