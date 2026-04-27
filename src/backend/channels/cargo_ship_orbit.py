# -*- coding: utf-8 -*-
"""
Cargo Ship Orbit Channel - 货船绕双体船轨道运动控制

实现货船以双体船为圆心做圆周运动的控制逻辑。
通过 MarineChannel 架构集成到 PoseidonX 系统中。
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from channels.marine_base import MarineChannel, ChannelPriority, ChannelStatus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class OrbitConfig:
    """轨道运动配置参数。"""
    radius: float = 80.0           # 轨道半径 (场景单位，与前端3D场景匹配)
    speed_deg_per_sec: float = 0.3  # 角速度 (度/秒) — 慢速，约 0.005 rad/帧 @60fps
    initial_angle_deg: float = 0.0  # 初始角度 (度)
    height_offset: float = 0.0      # 高度偏移 (米)
    enabled: bool = True            # 是否启用轨道运动
    auto_start: bool = True         # 是否自动启动

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OrbitState:
    """轨道运动状态。"""
    current_angle_deg: float = 0.0
    elapsed_seconds: float = 0.0
    is_running: bool = False
    last_update: Optional[str] = None
    total_orbits: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Cargo Ship Orbit Channel
# ---------------------------------------------------------------------------

class CargoShipOrbitChannel(MarineChannel):
    """
    货船轨道运动控制 Channel。
    
    控制货船以双体船为圆心做匀速圆周运动。
    通过 tick() 方法计算��船的新位置，供前端3D场景使用。
    """
    
    name = "cargo_ship_orbit"
    description = "货船绕双体船轨道运动控制"
    version = "1.0.0"
    priority = ChannelPriority.P2  # 辅助功能，不影响核心功能
    dependencies: List[str] = [
        "wpc_attitude_control",  # 依赖双体船姿态控制，确保双体船已初始化
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.config = config or {}
        self._config = self.config
        
        # 轨道配置
        orbit_cfg = self.config.get("orbit", {})
        self.orbit_config = OrbitConfig(
            radius=orbit_cfg.get("radius", 80.0),
            speed_deg_per_sec=orbit_cfg.get("speed_deg_per_sec", 0.3),
            initial_angle_deg=orbit_cfg.get("initial_angle_deg", 0.0),
            height_offset=orbit_cfg.get("height_offset", 0.0),
            enabled=orbit_cfg.get("enabled", True),
            auto_start=orbit_cfg.get("auto_start", True),
        )
        
        # 轨道状态
        self.orbit_state = OrbitState(
            current_angle_deg=self.orbit_config.initial_angle_deg,
            is_running=self.orbit_config.auto_start and self.orbit_config.enabled,
        )
        
        # 双体船位置 (由外部更新)
        self._catamaran_position: Dict[str, float] = {"x": 0.0, "y": 0.0, "z": 0.0}
        
        # 货船当前位置 (计算结果)
        self._cargo_ship_position: Dict[str, float] = {"x": 0.0, "y": 0.0, "z": 0.0}
        
        # 货船朝向角度 (始终朝向运动方向)
        self._cargo_ship_heading: float = 0.0
        
        # 事件日志
        self.event_log: List[Dict[str, Any]] = []
        
        logger.info("🚢 CargoShipOrbitChannel initialized (radius=%.1fm, speed=%.2f°/s)",
                     self.orbit_config.radius, self.orbit_config.speed_deg_per_sec)
    
    # ── MarineChannel 接口 ───────────────────────────────────
    
    def initialize(self) -> bool:
        """初始化轨道控制。"""
        self._initialized = True
        
        if self.orbit_config.enabled:
            self.orbit_state.is_running = self.orbit_config.auto_start
            self._set_health(
                ChannelStatus.OK,
                f"货船轨道运动就绪 (半径={self.orbit_config.radius}m, 速度={self.orbit_config.speed_deg_per_sec}°/s)"
            )
            logger.info("🚢 Cargo ship orbit initialized: radius=%.1fm, speed=%.2f°/s",
                         self.orbit_config.radius, self.orbit_config.speed_deg_per_sec)
        else:
            self._set_health(ChannelStatus.OK, "货船轨道运动已禁用")
        
        return True
    
    def shutdown(self) -> bool:
        """关闭轨道控制。"""
        self._initialized = False
        self.orbit_state.is_running = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """获取 Channel 当前状态。"""
        return self.to_dict()
    
    def process_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        处理外部事件。
        
        支持的事件类型:
          - "start_orbit": 启动轨道运动
          - "stop_orbit": 停止轨道运动
          - "set_radius": 设置轨道半径 (需提供 radius 参数)
          - "set_speed": 设置轨道角速度 (需提供 speed_deg_per_sec 参数)
          - "reset_orbit": 重置轨道到初始状态
          - "update_catamaran": 更新双体船位置 (需提供 x, y, z 参数)
          - "tick": 触发一次位置更新
        
        Args:
            event: 事件字典，必须包含 "type" 字段
            
        Returns:
            处理结果字典，或 None 如果事件类型不支持
        """
        event_type = event.get("type", "")
        
        if event_type == "start_orbit":
            ok = self.start_orbit()
            return {"status": "ok" if ok else "error", "action": "start_orbit"}
        
        elif event_type == "stop_orbit":
            ok = self.stop_orbit()
            return {"status": "ok" if ok else "error", "action": "stop_orbit"}
        
        elif event_type == "set_radius":
            radius = event.get("radius", 80.0)
            try:
                self.set_orbit_radius(radius)
                return {"status": "ok", "action": "set_radius", "radius": radius}
            except ValueError as e:
                return {"status": "error", "action": "set_radius", "message": str(e)}
        
        elif event_type == "set_speed":
            speed = event.get("speed_deg_per_sec", 0.3)
            try:
                self.set_orbit_speed(speed)
                return {"status": "ok", "action": "set_speed", "speed_deg_per_sec": speed}
            except ValueError as e:
                return {"status": "error", "action": "set_speed", "message": str(e)}
        
        elif event_type == "reset_orbit":
            self.reset_orbit()
            return {"status": "ok", "action": "reset_orbit"}
        
        elif event_type == "update_catamaran":
            x = event.get("x", 0.0)
            y = event.get("y", 0.0)
            z = event.get("z", 0.0)
            self.update_catamaran_position(x, y, z)
            return {"status": "ok", "action": "update_catamaran", "position": {"x": x, "y": y, "z": z}}
        
        elif event_type == "tick":
            now = event.get("now")
            result = self.tick(now=now)
            return {"status": "ok", "action": "tick", "result": result}
        
        return None
    
    # ── 核心逻辑 ─────────────────────────────────────────────
    
    def tick(self, now: Optional[datetime] = None, channel_registry: Optional[Dict] = None) -> Dict[str, Any]:
        """
        定时更新货船位置。
        
        计算货船在轨道上的新位置，基于双体船位置和当前角度。
        
        Args:
            now: 当前时间
            channel_registry: Channel 注册表 (可选)
            
        Returns:
            包含货船新位置和状态的字典
        """
        now = now or datetime.now()
        
        # 如果未启用或未运行，返回当前位置
        if not self.orbit_config.enabled or not self.orbit_state.is_running:
            return {
                "running": self.orbit_state.is_running,
                "enabled": self.orbit_config.enabled,
                "cargo_position": self._cargo_ship_position,
                "cargo_heading": self._cargo_ship_heading,
                "catamaran_position": self._catamaran_position,
            }
        
        # 计算时间增量
        if self.orbit_state.last_update:
            try:
                last = datetime.fromisoformat(self.orbit_state.last_update)
                delta_seconds = (now - last).total_seconds()
            except (ValueError, TypeError):
                delta_seconds = 1.0
        else:
            delta_seconds = 1.0
        
        # 限制最大时间步长 (防止跳帧)
        delta_seconds = min(delta_seconds, 5.0)
        
        # 更新角度
        angle_change = self.orbit_config.speed_deg_per_sec * delta_seconds
        self.orbit_state.current_angle_deg = (self.orbit_state.current_angle_deg + angle_change) % 360.0
        
        # 更新状态
        self.orbit_state.elapsed_seconds += delta_seconds
        self.orbit_state.last_update = now.isoformat()
        self.orbit_state.total_orbits = self.orbit_state.elapsed_seconds * self.orbit_config.speed_deg_per_sec / 360.0
        
        # 计算货船位置
        angle_rad = math.radians(self.orbit_state.current_angle_deg)
        cx = self._catamaran_position["x"]
        cz = self._catamaran_position["z"]
        cy = self._catamaran_position["y"]
        
        self._cargo_ship_position = {
            "x": cx + self.orbit_config.radius * math.cos(angle_rad),
            "y": cy + self.orbit_config.height_offset,
            "z": cz + self.orbit_config.radius * math.sin(angle_rad),
        }
        
        # 货船朝向 (运动方向切线方向)
        # 切线方向 = 当前角度 + 90°
        heading_deg = (self.orbit_state.current_angle_deg + 90.0) % 360.0
        self._cargo_ship_heading = heading_deg
        
        # 记录事件
        self.event_log.append({
            "time": now.isoformat(),
            "angle_deg": self.orbit_state.current_angle_deg,
            "position": dict(self._cargo_ship_position),
            "heading": heading_deg,
        })
        
        # 限制日志大小
        if len(self.event_log) > 1000:
            self.event_log = self.event_log[-500:]
        
        return {
            "running": True,
            "enabled": True,
            "angle_deg": self.orbit_state.current_angle_deg,
            "cargo_position": self._cargo_ship_position,
            "cargo_heading": self._cargo_ship_heading,
            "catamaran_position": self._catamaran_position,
            "total_orbits": round(self.orbit_state.total_orbits, 2),
            "elapsed_seconds": round(self.orbit_state.elapsed_seconds, 1),
        }
    
    # ── 公共方法 ─────────────────────────────────────────────
    
    def update_catamaran_position(self, x: float, y: float, z: float) -> None:
        """
        更新双体船位置。
        
        由外部 (如 WPC 姿态控制 Channel) 调用，更新双体船当前位置。
        
        Args:
            x: X 坐标
            y: Y 坐标 (高度)
            z: Z 坐标
        """
        self._catamaran_position = {"x": x, "y": y, "z": z}
    
    def get_cargo_position(self) -> Dict[str, float]:
        """获取货船当前位置。"""
        return dict(self._cargo_ship_position)
    
    def get_cargo_heading(self) -> float:
        """获取货船朝向角度 (度)。"""
        return self._cargo_ship_heading
    
    def get_orbit_state(self) -> Dict[str, Any]:
        """获取完整轨道状态。"""
        return {
            "config": self.orbit_config.to_dict(),
            "state": self.orbit_state.to_dict(),
            "cargo_position": self._cargo_ship_position,
            "cargo_heading": self._cargo_ship_heading,
            "catamaran_position": self._catamaran_position,
        }
    
    def start_orbit(self) -> bool:
        """启动轨道运动。"""
        if not self.orbit_config.enabled:
            logger.warning("🚢 Cannot start orbit: orbit is disabled")
            return False
        self.orbit_state.is_running = True
        self._set_health(ChannelStatus.OK, "货船轨道运动已启动")
        logger.info("🚢 Cargo ship orbit started")
        return True
    
    def stop_orbit(self) -> bool:
        """停止轨道运动。"""
        self.orbit_state.is_running = False
        self._set_health(ChannelStatus.OK, "货船轨道运动已停止")
        logger.info("🚢 Cargo ship orbit stopped")
        return True
    
    def set_orbit_radius(self, radius: float) -> None:
        """设置轨道半径。"""
        if radius <= 0:
            raise ValueError("Radius must be positive")
        self.orbit_config.radius = radius
        logger.info("🚢 Orbit radius set to %.1fm", radius)
    
    def set_orbit_speed(self, speed_deg_per_sec: float) -> None:
        """设置轨道角速度。"""
        if speed_deg_per_sec <= 0:
            raise ValueError("Speed must be positive")
        self.orbit_config.speed_deg_per_sec = speed_deg_per_sec
        logger.info("🚢 Orbit speed set to %.2f°/s", speed_deg_per_sec)
    
    def reset_orbit(self) -> None:
        """重置轨道到初始状态。"""
        self.orbit_state.current_angle_deg = self.orbit_config.initial_angle_deg
        self.orbit_state.elapsed_seconds = 0.0
        self.orbit_state.total_orbits = 0.0
        self.orbit_state.last_update = None
        logger.info("🚢 Orbit reset to initial state")
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化 Channel 状态。"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "priority": self.priority.value,
            "initialized": self._initialized,
            "health": self._health.status.value if self._health else "unknown",
            "health_message": self._health.message if self._health else "",
            "orbit_config": self.orbit_config.to_dict(),
            "orbit_state": self.orbit_state.to_dict(),
            "cargo_position": self._cargo_ship_position,
            "cargo_heading": self._cargo_ship_heading,
            "catamaran_position": self._catamaran_position,
        }


__all__ = ["CargoShipOrbitChannel", "OrbitConfig", "OrbitState"]