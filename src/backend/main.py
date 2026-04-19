#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DoubleBoatClawSystem Backend - Poseidon Server

FastAPI + WebSocket 实时数据推送服务
"""

import asyncio
import functools
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Path as PathParam, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

from adapters.worldmonitor_adapter import WorldMonitorAdapter
from adapters.worldmonitor_adapter_real import WorldMonitorRealAdapter
from channels.openbridge_command_router import build_openbridge_command_result
from config_loader import get_config
from storage.data_lakehouse import create_lakehouse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("PoseidonServer")
BASE_DIR = Path(__file__).resolve().parents[2]


def _coerce_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _resolve_runtime_path(path_value: Optional[str], fallback: str) -> str:
    raw_path = path_value or fallback
    path = Path(raw_path)
    if not path.is_absolute():
        path = BASE_DIR / raw_path
    return str(path)


def build_lakehouse_config() -> Dict[str, Any]:
    """构建湖仓运行时配置，优先级：环境变量 > settings.json > 默认值。"""
    settings = get_config()
    lakehouse_settings = settings.get("lakehouse", {}) or {}
    store_config_settings = lakehouse_settings.get("store_config", {}) or {}
    cloud_config_settings = lakehouse_settings.get("cloud_config", {}) or {}

    store_type = os.getenv("POSEIDON_LAKEHOUSE_STORE_TYPE", lakehouse_settings.get("store_type", "sqlite"))
    cloud_type = os.getenv("POSEIDON_LAKEHOUSE_CLOUD_TYPE", lakehouse_settings.get("cloud_type", "local"))
    buffer_max_size = int(os.getenv("POSEIDON_LAKEHOUSE_BUFFER_MAX_SIZE", lakehouse_settings.get("buffer_max_size", 1)))
    analytics_cache_dir = _resolve_runtime_path(
        os.getenv("POSEIDON_LAKEHOUSE_ANALYTICS_CACHE_DIR"),
        lakehouse_settings.get("analytics_cache_dir", "storage/analytics_cache"),
    )

    store_config = {
        "db_path": _resolve_runtime_path(
            os.getenv("POSEIDON_LAKEHOUSE_DB_PATH"),
            store_config_settings.get("db_path", "storage/poseidon_events.db"),
        ),
        "storage_path": _resolve_runtime_path(
            os.getenv("POSEIDON_LAKEHOUSE_STORAGE_PATH"),
            store_config_settings.get("storage_path", "storage/events"),
        ),
    }

    cloud_config: Dict[str, Any] = {
        "storage_path": _resolve_runtime_path(
            os.getenv("POSEIDON_LAKEHOUSE_CLOUD_STORAGE_PATH"),
            cloud_config_settings.get("storage_path", "storage/cloud_sync"),
        ),
        "bucket_name": os.getenv("POSEIDON_LAKEHOUSE_S3_BUCKET", cloud_config_settings.get("bucket_name", "doubleboat-events")),
        "region": os.getenv("POSEIDON_LAKEHOUSE_S3_REGION", cloud_config_settings.get("region", "us-east-1")),
        "prefix": os.getenv("POSEIDON_LAKEHOUSE_S3_PREFIX", cloud_config_settings.get("prefix", "events/")),
        "endpoint_url": os.getenv("POSEIDON_LAKEHOUSE_S3_ENDPOINT_URL", cloud_config_settings.get("endpoint_url")),
        "addressing_style": os.getenv("POSEIDON_LAKEHOUSE_S3_ADDRESSING_STYLE", cloud_config_settings.get("addressing_style", "path")),
        "verify_ssl": _coerce_bool(
            os.getenv("POSEIDON_LAKEHOUSE_S3_VERIFY_SSL"),
            _coerce_bool(cloud_config_settings.get("verify_ssl"), True),
        ),
        "auto_create_bucket": _coerce_bool(
            os.getenv("POSEIDON_LAKEHOUSE_S3_AUTO_CREATE_BUCKET"),
            _coerce_bool(cloud_config_settings.get("auto_create_bucket"), False),
        ),
    }

    return {
        "buffer_max_size": buffer_max_size,
        "store_type": store_type,
        "store_config": store_config,
        "cloud_type": cloud_type,
        "cloud_config": cloud_config,
        "analytics_cache_dir": analytics_cache_dir,
    }


def probe_lakehouse_cloud_sync() -> Dict[str, Any]:
    """在启动阶段探测 lakehouse 云同步可达性。"""
    cloud_adapter = getattr(data_lakehouse, "cloud_adapter", None)
    if cloud_adapter is None:
        info = {
            "available": False,
            "configured": False,
            "message": "No cloud adapter configured",
        }
        logger.info("☁️ Lakehouse cloud sync not configured")
        return info

    try:
        bucket_info = cloud_adapter.get_bucket_info()
        bucket_name = bucket_info.get("bucket", type(cloud_adapter).__name__)
        endpoint = bucket_info.get("endpoint_url") or "local"
        if bucket_info.get("available"):
            created_suffix = " (created)" if bucket_info.get("created") else ""
            logger.info(f"☁️ Lakehouse cloud sync ready: {bucket_name} @ {endpoint}{created_suffix}")
        else:
            logger.warning(f"☁️ Lakehouse cloud sync unavailable: {bucket_name} @ {endpoint} -> {bucket_info.get('error', 'unknown error')}")
        return bucket_info
    except Exception as exc:
        logger.warning(f"☁️ Lakehouse cloud sync probe failed: {exc}")
        return {
            "available": False,
            "configured": True,
            "error": str(exc),
        }

@asynccontextmanager
async def poseidon_lifespan(app: FastAPI):
    """FastAPI lifespan hooks for startup and shutdown."""
    await start_poseidon_services()
    try:
        yield
    finally:
        await stop_poseidon_services()


# 创建 FastAPI 应用
app = FastAPI(
    title="DoubleBoatClawSystem API",
    description="Digital Twin API for Deep-Sea Scientific Facilities",
    version="1.0.0",
    lifespan=poseidon_lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 数据模型 ====================

class SensorData(BaseModel):
    """传感器数据"""
    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: str
    quality: str = "good"

class AISTarget(BaseModel):
    """AIS 目标"""
    mmsi: str
    latitude: float
    longitude: float
    course: float
    speed: float
    heading: float
    vessel_type: str
    cpa: Optional[float] = None
    tcpa: Optional[float] = None

class EngineStatus(BaseModel):
    """主机状态"""
    engine_id: str
    rpm: float
    load: float
    cooling_water_temp: float
    lube_oil_pressure: float
    fuel_consumption: float
    status: str
    alarms: List[str] = []

class Alarm(BaseModel):
    """报警"""
    alarm_id: str
    level: str  # INFO, WARNING, CRITICAL, EMERGENCY
    source: str
    message: str
    timestamp: str
    acknowledged: bool = False


class DecisionFeedbackRequest(BaseModel):
    """决策反馈请求"""
    action: str
    outcome: str
    confirmed_by: str = "operator"


class OpenBridgeCommandRequest(BaseModel):
    """OpenBridge 驾驶台命令请求"""
    command: str
    source: str = "bridge_chat"

class BridgeChatRequest(BaseModel):
    """Bridge Chat request."""
    message: str
    session_id: str = "default"
    lang: str = ""
    agent_id: str = "ship_navigator"


class BridgeChatHistoryRequest(BaseModel):
    """Get chat history."""
    session_id: str = "default"
    limit: int = 20



class MemoryAnalyticsQueryRequest(BaseModel):
    """记忆层即席分析请求。"""
    sql: str
    event_type: Optional[str] = None
    limit: int = 100000
    parquet_path: Optional[str] = None


class MemoryArchiveRequest(BaseModel):
    """记忆层归档请求。"""
    event_type: Optional[str] = None
    limit: int = 100000
    output_path: Optional[str] = None

# ==================== 内存数据存储 ====================

# 传感器数据缓存
sensor_cache: Dict[str, SensorData] = {}

# AIS 目标
ais_targets: Dict[str, AISTarget] = {}

# 主机状态
engine_status: Optional[EngineStatus] = None

# 报警列表
alarms: List[Alarm] = []
_MAX_ALARMS: int = 1000

# WebSocket 连接
active_connections: List[WebSocket] = []

# 传感器目录（接口稳定字段）
SENSOR_CATALOG: List[Dict[str, str]] = [
    {"id": "GPS-001", "type": "GPS", "description": "GPS 接收机"},
    {"id": "COMPASS-001", "type": "COMPASS", "description": "罗经"},
    {"id": "LOG-001", "type": "SPEED_LOG", "description": "计程仪"},
    {"id": "ECHO-001", "type": "ECHO_SOUNDER", "description": "测深仪"},
]

# ==================== 仿真数据生成器 ====================

class SimulationEngine:
    """仿真数据生成引擎"""
    
    def __init__(self):
        self.running = False
        self.start_time = time.time()
        
        # 初始船舶状态 — 东海海域 (长江口外)
        self.ship_position = {"lat": 30.85, "lon": 122.35}
        self.ship_course = 135.0
        self.ship_speed = 12.3
        
        # 初始 AIS 目标 (模拟 8 艘船 — 多种遭遇态势)
        self.ais_targets = {
            # 对驶船 (head-on, COLREG Rule 14)
            "123456789": {"lat": 30.90, "lon": 122.40, "course": 225.0, "speed": 10.0,
                          "name": "OCEAN GLORY", "type": "Cargo", "encounter": "head-on"},
            # 交叉相遇 — 右舷来船 (crossing, Rule 15)
            "234567890": {"lat": 30.80, "lon": 122.30, "course": 315.0, "speed": 8.5,
                          "name": "SEA EAGLE", "type": "Tanker", "encounter": "crossing-stbd"},
            # 追越船 (overtaking, Rule 13)
            "345678901": {"lat": 30.92, "lon": 122.28, "course": 90.0, "speed": 12.0,
                          "name": "PACIFIC RUNNER", "type": "Container", "encounter": "overtaking"},
            # 左舷交叉
            "456789012": {"lat": 30.78, "lon": 122.42, "course": 180.0, "speed": 15.0,
                          "name": "JADE HARMONY", "type": "Bulk", "encounter": "crossing-port"},
            # 同向航行
            "567890123": {"lat": 30.88, "lon": 122.38, "course": 45.0, "speed": 9.0,
                          "name": "STARLIGHT", "type": "Fishing", "encounter": "same-direction"},
            # 锚泊船
            "678901234": {"lat": 30.84, "lon": 122.35, "course": 0.0, "speed": 0.0,
                          "name": "HARBOR REST", "type": "Anchor", "encounter": "anchored"},
            # 限于吃水船
            "789012345": {"lat": 30.86, "lon": 122.44, "course": 270.0, "speed": 5.0,
                          "name": "DEEP DRAFT", "type": "VLCC", "encounter": "constrained"},
            # 高速船
            "890123456": {"lat": 30.82, "lon": 122.32, "course": 150.0, "speed": 25.0,
                          "name": "HYDROFOIL X", "type": "HSC", "encounter": "high-speed"},
        }
        
        # 主机初始状态
        self.engine = {
            "rpm": 120.0,
            "load": 75.0,
            "cooling_water_temp": 82.0,
            "lube_oil_pressure": 4.5,
            "fuel_consumption": 180.0,
        }

    def seed_initial_state(self) -> None:
        """在后台循环启动前写入首批缓存，避免冷启动空数据。"""
        now = datetime.now().isoformat()

        sensor_cache.update(
            {
                "GPS-001": SensorData(
                    sensor_id="GPS-001",
                    sensor_type="GPS",
                    value=0.0,
                    unit="deg",
                    timestamp=now,
                    quality="good",
                ),
                "COMPASS-001": SensorData(
                    sensor_id="COMPASS-001",
                    sensor_type="COMPASS",
                    value=self.ship_course,
                    unit="deg",
                    timestamp=now,
                    quality="good",
                ),
                "LOG-001": SensorData(
                    sensor_id="LOG-001",
                    sensor_type="SPEED_LOG",
                    value=self.ship_speed,
                    unit="kn",
                    timestamp=now,
                    quality="good",
                ),
            }
        )

        for mmsi, target in self.ais_targets.items():
            ais_targets[mmsi] = AISTarget(
                mmsi=mmsi,
                latitude=target["lat"],
                longitude=target["lon"],
                course=target["course"],
                speed=target["speed"],
                heading=target["course"],
                vessel_type=target.get("type", "Cargo"),
                cpa=0.5,
                tcpa=300.0,
            )

        global engine_status
        engine_status = EngineStatus(
            engine_id="ENG-001",
            rpm=self.engine["rpm"],
            load=self.engine["load"],
            cooling_water_temp=self.engine["cooling_water_temp"],
            lube_oil_pressure=self.engine["lube_oil_pressure"],
            fuel_consumption=self.engine["fuel_consumption"],
            status="running",
            alarms=[],
        )
    
    async def generate_sensor_data(self):
        """生成传感器数据"""
        import math
        while self.running:
            try:
                # 更新船舶位置 (模拟移动)
                dt = 1  # 1s
                t = time.time()
                self.ship_position["lat"] += 0.0001 * (self.ship_speed / 10)
                self.ship_position["lon"] += 0.0001 * (self.ship_speed / 10)
                
                # 航向缓慢变化 (模拟自动舵微调)
                self.ship_course += math.sin(t * 0.02) * 0.05
                self.ship_course = self.ship_course % 360
                
                # 生成传感器数据
                sensor_data = {
                    "GPS-001": SensorData(
                        sensor_id="GPS-001",
                        sensor_type="GPS",
                        value=0.0,
                        unit="deg",
                        timestamp=datetime.now().isoformat(),
                        quality="good"
                    ),
                    "COMPASS-001": SensorData(
                        sensor_id="COMPASS-001",
                        sensor_type="COMPASS",
                        value=self.ship_course,
                        unit="deg",
                        timestamp=datetime.now().isoformat(),
                        quality="good"
                    ),
                    "LOG-001": SensorData(
                        sensor_id="LOG-001",
                        sensor_type="SPEED_LOG",
                        value=self.ship_speed,
                        unit="kn",
                        timestamp=datetime.now().isoformat(),
                        quality="good"
                    ),
                    "WIND-001": SensorData(
                        sensor_id="WIND-001",
                        sensor_type="WIND",
                        value=12.0 + math.sin(t * 0.01) * 5.0,
                        unit="kn",
                        timestamp=datetime.now().isoformat(),
                        quality="good"
                    ),
                    "DEPTH-001": SensorData(
                        sensor_id="DEPTH-001",
                        sensor_type="DEPTH",
                        value=45.0 + math.sin(t * 0.005) * 10.0,
                        unit="m",
                        timestamp=datetime.now().isoformat(),
                        quality="good"
                    ),
                }
                
                # 更新缓存
                sensor_cache.update(sensor_data)
                
                # 更新 AIS 目标位置 (真实航迹模拟)
                for mmsi, target in self.ais_targets.items():
                    course_rad = math.radians(target["course"])
                    spd = target["speed"]
                    spd_factor = spd / 3600.0 / 60.0  # kn → deg/s (近似)
                    
                    # 锚泊船不移动
                    if target.get("encounter") == "anchored":
                        spd_factor = 0.0
                        target["course"] += math.sin(t * 0.1) * 0.01  # 缓慢摆荡
                    else:
                        target["lat"] += math.cos(course_rad) * spd_factor
                        target["lon"] += math.sin(course_rad) * spd_factor
                        # 微小航向漂移
                        target["course"] += math.sin(t * 0.03 + hash(mmsi) % 100) * 0.02
                    target["course"] = target["course"] % 360
                    
                    # 计算真实 CPA/TCPA
                    dlat = target["lat"] - self.ship_position["lat"]
                    dlon = target["lon"] - self.ship_position["lon"]
                    dist_nm = math.sqrt(dlat ** 2 + dlon ** 2) * 60.0
                    rel_speed = abs(spd - self.ship_speed) + 0.1
                    tcpa_s = max(dist_nm / rel_speed * 3600.0, 0.0)
                    cpa_nm = max(dist_nm * 0.3, 0.1)
                    
                    ais_targets[mmsi] = AISTarget(
                        mmsi=mmsi,
                        latitude=target["lat"],
                        longitude=target["lon"],
                        course=target["course"],
                        speed=spd,
                        heading=target["course"],
                        vessel_type=target.get("type", "Cargo"),
                        cpa=round(cpa_nm, 2),
                        tcpa=round(tcpa_s, 1),
                    )
                
                # 更新主机状态 (带真实波动模式)
                import random
                # RPM: 基于负载和海况的波动
                rpm_base = 120.0
                rpm_wave = math.sin(t * 0.15) * 1.5  # 海浪载荷波动
                rpm_noise = random.gauss(0, 0.3)
                self.engine["rpm"] = rpm_base + rpm_wave + rpm_noise
                
                # 负载: 随转速和海况相关
                load_base = 75.0
                load_wave = math.sin(t * 0.12) * 2.0 + math.sin(t * 0.31) * 1.0
                self.engine["load"] = load_base + load_wave + random.gauss(0, 0.5)
                
                # 冷却水温度: 热惯性 (缓慢变化)
                temp_target = 82.0 + self.engine["load"] * 0.04
                self.engine["cooling_water_temp"] += (temp_target - self.engine["cooling_water_temp"]) * 0.02
                self.engine["cooling_water_temp"] += random.gauss(0, 0.05)
                
                # 滑油压力: 与 RPM 正相关
                self.engine["lube_oil_pressure"] = 4.5 + (self.engine["rpm"] - 120) * 0.02 + random.gauss(0, 0.02)
                
                # 油耗: 与负载的二次方成正比
                self.engine["fuel_consumption"] = 35.0 + (self.engine["load"] / 100.0) ** 2 * 20.0 + random.gauss(0, 0.3)
                
                global engine_status
                engine_status = EngineStatus(
                    engine_id="ENG-001",
                    rpm=self.engine["rpm"],
                    load=self.engine["load"],
                    cooling_water_temp=self.engine["cooling_water_temp"],
                    lube_oil_pressure=self.engine["lube_oil_pressure"],
                    fuel_consumption=self.engine["fuel_consumption"],
                    status="running",
                    alarms=[]
                )
                
                # 检查报警
                await self.check_alarms()
                
                # 广播数据更新
                await self.broadcast_update()
                
                await asyncio.sleep(dt)
                
            except Exception as e:
                logger.error(f"Simulation error: {e}")
                await asyncio.sleep(1)
    
    async def check_alarms(self):
        """检查报警条件"""
        # 冷却水温度高报警
        if self.engine["cooling_water_temp"] > 85.0:
            await self.create_alarm(
                level="WARNING",
                source="ENGINE",
                message=f"Cooling water temperature high: {self.engine['cooling_water_temp']:.1f}°C"
            )
        
        # 滑油压力低报警
        if self.engine["lube_oil_pressure"] < 4.0:
            await self.create_alarm(
                level="CRITICAL",
                source="ENGINE",
                message=f"Lube oil pressure low: {self.engine['lube_oil_pressure']:.2f} bar"
            )
    
    async def create_alarm(self, level: str, source: str, message: str):
        """创建报警"""
        alarm = Alarm(
            alarm_id=f"ALM-{int(time.time())}",
            level=level,
            source=source,
            message=message,
            timestamp=datetime.now().isoformat(),
            acknowledged=False
        )
        
        # 避免重复报警
        if not any(a.message == message and not a.acknowledged for a in alarms):
            alarms.append(alarm)
            # trim oldest alarms if over capacity
            if len(alarms) > _MAX_ALARMS:
                alarms[:] = alarms[-_MAX_ALARMS:]
            logger.warning(f"🚨 Alarm created: {level} - {message}")
    
    async def broadcast_update(self):
        """广播数据更新到所有 WebSocket 连接"""
        import math
        if not active_connections:
            return
        
        t = time.time()
        # WPC 姿态仿真 (实时)
        waveH = 0.8 + abs(math.sin(t * 0.0015)) * 2.0
        wavePeriod = max(6.0 + math.sin(t * 0.003) * 3.0, 3.0)
        waveFreq = (2 * math.pi) / wavePeriod
        roll_deg = math.sin(t * waveFreq) * min(waveH * 2.6, 8.0)
        pitch_deg = math.cos(t * waveFreq * 0.9) * min(waveH * 1.4, 3.0)
        heave_m = math.sin(t * waveFreq * 1.1) * min(waveH * 0.35, 2.0)
        
        # 天气事件周期
        cycle = (t % 300) / 300.0
        if cycle < 0.3: weather_event = "clear"
        elif cycle < 0.5: weather_event = "squall_building"
        elif cycle < 0.7: weather_event = "squall"
        elif cycle < 0.85: weather_event = "fog"
        else: weather_event = "clearing"
        
        message = json.dumps({
            "type": "data_update",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "sensors": {k: v.model_dump() for k, v in sensor_cache.items()},
                "ais_targets": {k: v.model_dump() for k, v in ais_targets.items()},
                "engine": engine_status.model_dump() if engine_status else None,
                "alarms": [a.model_dump() for a in alarms[-10:]],
                "hdg": self.ship_course,
                "cog": self.ship_course + 0.4,
                "own_ship": {
                    "latitude": self.ship_position["lat"],
                    "longitude": self.ship_position["lon"],
                    "course": self.ship_course,
                    "speed": self.ship_speed,
                },
                "attitude": {
                    "roll_deg": round(roll_deg, 2),
                    "pitch_deg": round(pitch_deg, 2),
                    "heave_m": round(heave_m, 2),
                },
                "weather_event": weather_event,
            }
        })

        # fire-and-forget broadcast with timeout
        async def _safe_send(c, m):
            try:
                await asyncio.wait_for(c.send_text(m), timeout=2.0)
            except Exception:
                return c
            return None
        results = await asyncio.gather(*[_safe_send(c, message) for c in active_connections], return_exceptions=True)
        for c in results:
            if isinstance(c, Exception):
                continue
            if c is not None and c in active_connections:
                active_connections.remove(c)
    
    def start(self):
        """启动仿真引擎"""
        self.running = True
        logger.info("🚀 Simulation engine started")
    
    def stop(self):
        """停止仿真引擎"""
        self.running = False
        logger.info("🛑 Simulation engine stopped")

# 全局仿真引擎实例
sim_engine = SimulationEngine()

# WorldMonitor 方案层适配器
worldmonitor = WorldMonitorAdapter()

# WorldMonitor 真实数据适配器
try:
    worldmonitor_real = WorldMonitorRealAdapter({
        "api_key": os.getenv("WORLDMONITOR_API_KEY", "placeholder"),
        "base_url": os.getenv("WORLDMONITOR_BASE_URL", "https://api.worldmonitor.app/api/v1"),
        "cache_ttl": 30
    })
except Exception as e:
    logger.error(f"Failed to initialize WorldMonitorRealAdapter: {e}")
    worldmonitor_real = None

# AI Native 记忆层与协调状态
data_lakehouse = create_lakehouse({
    **build_lakehouse_config(),
})
coordination_status: Dict[str, Any] = {
    "running": False,
    "runs": 0,
    "last_cycle": None,
    "last_error": None,
}
coordination_task: Optional[asyncio.Task] = None
agent_team_scheduler = None

# 专用线程池：后台重型任务使用独立线程池，避免与 API 请求竞争
_bg_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="bg-heavy")
_api_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="api-sync")

# Dashboard TTL 缓存（避免重复计算）
_dashboard_cache: Dict[str, Any] = {}
_dashboard_cache_ts: float = 0.0
_DASHBOARD_CACHE_TTL: float = 3.0  # 3 秒
_dashboard_lock: Optional[asyncio.Lock] = None


def _get_dashboard_lock() -> asyncio.Lock:
    """Lazy-init dashboard lock (must be called inside event loop)."""
    global _dashboard_lock
    if _dashboard_lock is None:
        _dashboard_lock = asyncio.Lock()
    return _dashboard_lock


async def ai_native_coordination_loop():
    """周期性执行智能体协调循环。"""
    global coordination_status

    coordination_status["running"] = True
    await asyncio.sleep(30)  # initial delay to let server warm up
    while True:
        try:
            from channels.marine_base import get_default_registry

            registry = get_default_registry()
            orchestrator = registry.get("decision_orchestrator")
            if orchestrator and hasattr(orchestrator, "coordinate_agents"):
                loop = asyncio.get_event_loop()
                summary = await loop.run_in_executor(
                    _bg_executor, functools.partial(orchestrator.coordinate_agents, event_sink=data_lakehouse)
                )
                coordination_status["runs"] = summary.get("coordination_runs", coordination_status["runs"])
                coordination_status["last_cycle"] = summary
                coordination_status["last_error"] = None
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            coordination_status["running"] = False
            raise
        except Exception as exc:
            coordination_status["last_error"] = str(exc)
            logger.error(f"AI Native coordination loop failed: {exc}")
            await asyncio.sleep(30)

# ==================== API 路由 ====================

def _sync_register_all_channels():
    """在线程池中执行的同步 Channel 注册（避免阻塞事件循环）。"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from register_channels import (
        register_energy_efficiency_channel,
        register_intelligent_navigation,
        register_intelligent_engine,
        register_compliance_digital_expert,
        register_distributed_perception_hub,
        register_decision_orchestrator,
        register_rcs_control,
        register_structural_health_monitor,
        register_ship_shore_link,
        register_autonomy_manager,
        register_predictive_health,
        register_route_optimizer,
        register_voyage_planner,
        register_cyber_security,
        register_build_team_manager,
        register_execution_team_manager,
        register_weather_routing,
        register_crew_fatigue_monitor,
        register_cargo_monitor,
        register_fire_detection,
        register_vdr_recorder,
        register_dynamic_positioning,
        register_ais_processor,
        register_gyro_compass_monitor,
        register_speed_log_monitor,
        register_rudder_control_monitor,
        register_tank_level_monitor,
        register_alarm_management,
        register_autopilot_monitor,
        register_echo_sounder_monitor,
        register_propulsion_monitor,
        register_mooring_monitor,
        register_man_overboard,
        register_safety_system_monitor,
        register_lrit_reporter,
        register_navigational_lights,
        register_voyage_data_analyzer,
        register_maintenance_planner,
        register_bridge_chat,
        register_system_evolution,
        register_colregs_brain,
        register_wpc_attitude_control,
        register_hull_stress_monitor,
        register_openbridge_hmi,
        register_power_management,
        register_emission_monitor,
        register_ballast_water_monitor,
        register_anchor_watch,
        register_communication_manager,
        register_deterministic_network,
        register_visual_presentation,
        register_marine_datacenter_energy,
    )
    _registrars = [
        register_energy_efficiency_channel,
        register_intelligent_navigation,
        register_intelligent_engine,
        register_compliance_digital_expert,
        register_distributed_perception_hub,
        register_decision_orchestrator,
        register_rcs_control,
        register_structural_health_monitor,
        register_ship_shore_link,
        register_autonomy_manager,
        register_predictive_health,
        register_route_optimizer,
        register_voyage_planner,
        register_cyber_security,
        register_build_team_manager,
        register_execution_team_manager,
        register_weather_routing,
        register_crew_fatigue_monitor,
        register_cargo_monitor,
        register_fire_detection,
        register_vdr_recorder,
        register_dynamic_positioning,
        register_ais_processor,
        register_gyro_compass_monitor,
        register_speed_log_monitor,
        register_rudder_control_monitor,
        register_tank_level_monitor,
        register_alarm_management,
        register_autopilot_monitor,
        register_echo_sounder_monitor,
        register_propulsion_monitor,
        register_mooring_monitor,
        register_man_overboard,
        register_safety_system_monitor,
        register_lrit_reporter,
        register_navigational_lights,
        register_voyage_data_analyzer,
        register_maintenance_planner,
        register_bridge_chat,
        register_system_evolution,
        register_colregs_brain,
        register_wpc_attitude_control,
        register_hull_stress_monitor,
        register_openbridge_hmi,
        register_power_management,
        register_emission_monitor,
        register_ballast_water_monitor,
        register_anchor_watch,
        register_communication_manager,
        register_deterministic_network,
        register_visual_presentation,
        register_marine_datacenter_energy,
    ]
    for reg_fn in _registrars:
        try:
            reg_fn()
        except Exception as e:
            logger.warning(f"⚠️ Channel registration failed ({reg_fn.__name__}): {e}")


async def start_poseidon_services():
    """启动后台服务与 AI Native 协调逻辑。所有阻塞操作委托到线程池。"""
    global coordination_task
    logger.info("🚀 Starting Poseidon Server...")
    loop = asyncio.get_event_loop()

    # Token Factory — 自主 Token 工厂：确保 LLM 推理可用
    try:
        from token_factory import TokenFactory
        tf = TokenFactory.instance()
        tf_status = await tf.ensure_ready()
        if tf_status.get("ready"):
            models = tf_status.get("ollama_models", [])
            logger.info("🏭 Token Factory ready — models: %s", models)
        else:
            logger.warning("🏭 Token Factory: no LLM provider reachable, chat will use template fallback")
    except Exception as e:
        logger.warning("🏭 Token Factory init skipped: %s", e)

    # 将所有同步阻塞操作委托到线程池，避免阻塞事件循环
    await loop.run_in_executor(None, sim_engine.seed_initial_state)
    sim_engine.start()
    logger.info("🚀 Simulation engine started")

    await loop.run_in_executor(None, probe_lakehouse_cloud_sync)

    # 注册 Marine Channels（在线程池中批量执行）
    try:
        await loop.run_in_executor(None, _sync_register_all_channels)
        from channels.marine_base import get_default_registry
        registry = get_default_registry()
        perception = registry.get("distributed_perception_hub")
        if perception and hasattr(perception, "set_event_sink"):
            perception.set_event_sink(data_lakehouse)
        orchestrator = registry.get("decision_orchestrator")
        if orchestrator and hasattr(orchestrator, "set_event_sink"):
            orchestrator.set_event_sink(data_lakehouse)
        logger.info("✅ Marine Channels registered")

        # Register dual agent-set topology
        try:
            from register_channels import register_agent_sets
            await loop.run_in_executor(None, register_agent_sets)
            logger.info("✅ Dual agent-set topology registered")
        except Exception as e:
            logger.warning(f"⚠️ Agent-set registration skipped: {e}")
    except Exception as e:
        logger.warning(f"⚠️ Channel registration skipped: {e}")

    # 启动双智能体团队调度器
    try:
        from channels.agent_team_scheduler import AgentTeamScheduler
        from agent_team_api import router as agent_team_router, set_teams
        registry = get_default_registry()
        build_team = registry.get("build_team_manager")
        execution_team = registry.get("execution_team_manager")
        global agent_team_scheduler
        agent_team_scheduler = AgentTeamScheduler(
            build_team=build_team,
            execution_team=execution_team,
            channel_registry=registry,
        )
        set_teams(build_team, execution_team, agent_team_scheduler,
                  evolution_engine=registry.get("system_evolution"))
        app.include_router(agent_team_router)
        await agent_team_scheduler.start()
        logger.info("✅ Agent Team Scheduler started (build=%s, exec=%s)",
                     build_team is not None, execution_team is not None)
    except Exception as e:
        logger.warning(f"⚠️ Agent Team Scheduler skipped: {e}")

    # Agent Team Config API (Clawith-style)
    try:
        from agents.api import router as agent_config_router, init_agent_config
        from agents.team_manager import TeamManager
        from agents.teams.build_team import create_build_team
        from agents.teams.execution_team import create_execution_team
        from agents.teams.energy_team import create_energy_team

        config_team_manager = TeamManager()
        build_team_obj = create_build_team()
        config_team_manager._teams[build_team_obj.team_id] = build_team_obj
        exec_team_obj = create_execution_team()
        config_team_manager._teams[exec_team_obj.team_id] = exec_team_obj
        energy_team_obj = create_energy_team()
        config_team_manager._teams[energy_team_obj.team_id] = energy_team_obj

        init_agent_config(config_team_manager)
        app.include_router(agent_config_router)
        logger.info("Agent Config API mounted (teams: %d, agents: %d)",
                     len(config_team_manager.list_teams()),
                     sum(len(t.agents) for t in config_team_manager.list_teams()))
    except Exception as e:
        logger.warning(f"Agent Config API skipped: {e}")

    # 启动传感器数据生成
    asyncio.create_task(sim_engine.generate_sensor_data())

    # 启动 AI Native 协调循环
    coordination_task = asyncio.create_task(ai_native_coordination_loop())
    logger.info("✅ AI Native coordination loop started")

    # 启动天气数据自动采集循环
    asyncio.create_task(weather_feed_loop())
    logger.info("✅ Weather feed loop started")

    # 前端静态文件 (must be AFTER all API routers to avoid catching API requests)
    from fastapi.staticfiles import StaticFiles
    from starlette.routing import WebSocketRoute, Route
    _frontend_dir = BASE_DIR / "src" / "frontend"
    if _frontend_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")
        # StaticFiles mount("/") swallows ALL paths including websockets — bubble
        # specific routes (websocket + named API routes) to the FRONT so they win.
        priority_paths = {"/ws/datacenter"}
        priority = [r for r in app.router.routes if getattr(r, "path", None) in priority_paths]
        for r in priority:
            app.router.routes.remove(r)
            app.router.routes.insert(0, r)
        logger.info(f"✅ Frontend static files mounted from {_frontend_dir}")
    else:
        logger.warning(f"⚠️ Frontend directory not found: {_frontend_dir}")

    logger.info("✅ Poseidon Server started")


async def weather_feed_loop():
    """后台任务：每 60 秒从 worldmonitor 获取天气数据注入 weather_routing channel。"""
    while True:
        await asyncio.sleep(60)
        try:
            from channels.marine_base import get_default_registry

            registry = get_default_registry()
            wr_channel = registry.get("weather_routing")
            weather = await worldmonitor.get_marine_weather(lat=31.2, lng=121.5)
            if weather and wr_channel:
                await wr_channel.process_event({
                    "type": "weather_forecast",
                    "wind_speed": weather.get("wind_speed", 0),
                    "wave_height": weather.get("wave_height", 0),
                    "visibility": weather.get("visibility", 10),
                    "region": "current_route",
                })
        except Exception:
            pass  # 非关键任务，不崩溃


async def stop_poseidon_services():
    """关闭后台服务与 AI Native 协调逻辑。"""
    global coordination_task, agent_team_scheduler
    sim_engine.stop()
    if agent_team_scheduler:
        await agent_team_scheduler.stop()
        agent_team_scheduler = None
    if coordination_task:
        coordination_task.cancel()
        try:
            await coordination_task
        except asyncio.CancelledError:
            pass
        coordination_task = None
    data_lakehouse.shutdown()
    logger.info("🛑 Poseidon Server stopped")

@app.get("/")
async def root():
    """根路径"""
    from channels.marine_base import get_default_registry
    registry = get_default_registry()
    
    return {
        "name": "DoubleBoatClawSystem API",
        "version": "1.0.0",
        "description": "Digital Twin API for Deep-Sea Scientific Facilities",
        "registered_channels": len(registry.list_channels()),
        "endpoints": {
            "GET /api/v1/sensors": "获取传感器列表",
            "GET /api/v1/channels": "获取已注册 Channel 列表",
            "GET /api/v1/ais/targets": "获取 AIS 目标",
            "GET /api/v1/engine/status": "获取主机状态",
            "GET /api/v1/alerts": "获取报警列表",
            "WS /ws": "WebSocket 连接",
        }
    }

@app.get("/api/v1/channels")
async def get_channels():
    """获取已注册 Channel 列表"""
    from channels.marine_base import get_default_registry
    registry = get_default_registry()

    def _collect():
        channels = []
        for name in registry.list_channels():
            channel = registry.get(name)
            if channel:
                try:
                    status = channel.get_status()
                except Exception as e:
                    logger.debug(f"Channel status error: {e}")
                    status = {"health": "error"}
                channels.append({
                    "name": name,
                    "description": channel.description,
                    "version": status.get("version", "1.0.0"),
                    "health": status.get("health", "unknown"),
                    "initialized": status.get("initialized", False),
                    "status": status,
                })
        return channels

    loop = asyncio.get_event_loop()
    channels = await loop.run_in_executor(_api_executor, _collect)
    return {"channels": channels}


@app.post("/api/v1/channels/{channel_name}/query")
async def query_channel(channel_name: str = PathParam(..., min_length=1, max_length=100), payload: dict = {}):
    """查询 Channel 数据，用于 Bridge Chat/前端联动。"""
    def _query():
        from channels.marine_base import get_default_registry
        registry = get_default_registry()
        channel = registry.get(channel_name)
        if not channel:
            return None

        query = (payload or {}).get("query", "")

        if channel_name == "intelligent_navigation" and hasattr(channel, "query_navigation_status"):
            return {"channel": channel_name, "result": channel.query_navigation_status(query), "status": channel.get_status()}

        if channel_name == "intelligent_engine" and hasattr(channel, "query_engine_status"):
            return {"channel": channel_name, "result": channel.query_engine_status(query), "status": channel.get_status()}

        if channel_name == "energy_efficiency":
            status = channel.get_status()
            result = {
                "vessel": status.get("vessel"),
                "health": status.get("health"),
                "health_message": status.get("health_message"),
            }
            return {"channel": channel_name, "result": result, "status": status}

        if channel_name == "compliance_digital_expert" and hasattr(channel, "query_compliance_status"):
            return {"channel": channel_name, "result": channel.query_compliance_status(query), "status": channel.get_status()}

        if channel_name == "decision_orchestrator" and hasattr(channel, "build_decision_package"):
            return {"channel": channel_name, "result": getattr(channel, "latest_package", {}), "status": channel.get_status()}

        if channel_name == "distributed_perception_hub" and hasattr(channel, "get_latest_events"):
            return {"channel": channel_name, "result": {"latest_events": channel.get_latest_events(20)}, "status": channel.get_status()}

        return {"channel": channel_name, "result": channel.get_status(), "status": channel.get_status()}

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_api_executor, _query)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Channel '{channel_name}' not found")
    return result

@app.get("/api/v1/sensors")
async def get_sensors():
    """获取传感器列表"""
    sensors: List[Dict[str, Any]] = []
    for item in SENSOR_CATALOG:
        row: Dict[str, Any] = dict(item)
        latest = sensor_cache.get(item["id"])
        if latest:
            row.update(
                {
                    "latest_value": latest.value,
                    "unit": latest.unit,
                    "timestamp": latest.timestamp,
                    "quality": latest.quality,
                }
            )
        sensors.append(row)

    return {
        "sensors": sensors
    }

@app.get("/api/v1/sensors/{sensor_id}/data")
async def get_sensor_data(sensor_id: str = PathParam(..., min_length=1, max_length=100)):
    """获取传感器数据"""
    if sensor_id not in sensor_cache:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor_cache[sensor_id]

@app.get("/api/v1/ais/targets")
async def get_ais_targets():
    """获取 AIS 目标"""
    return {"targets": [t.model_dump() for t in ais_targets.values()]}


@app.get("/api/v1/s100/layers")
async def get_s100_layers():
    """S-100 数据层 API — 提供 S-101/S-102/S-104/S-111/S-124 模拟数据"""
    import math
    now = datetime.now()
    tide_phase = math.sin(now.timestamp() / 3600 * math.pi / 6)  # ~12h cycle
    ship_lat = sim_engine.ship_position["lat"]
    ship_lon = sim_engine.ship_position["lon"]

    # S-104 Water Level (tidal prediction)
    water_level = {
        "tide_height_m": round(1.2 + tide_phase * 0.8, 2),
        "hat_m": 2.1,
        "lat_m": -0.3,
        "depth": round(22.5 + tide_phase * 0.8, 1),
        "reference_station": "Shanghai Wusongkou",
        "timestamp": now.isoformat(),
    }

    # S-111 Surface Currents
    currents = []
    for i in range(9):
        lat_off = (i // 3 - 1) * 0.03
        lon_off = (i % 3 - 1) * 0.03
        currents.append({
            "lat": round(ship_lat + lat_off, 4),
            "lon": round(ship_lon + lon_off, 4),
            "speed_kn": round(0.3 + abs(math.sin(now.timestamp() / 1800 + i)) * 0.5, 2),
            "direction_deg": round((120 + i * 15 + tide_phase * 30) % 360, 1),
        })

    # S-124 Navigation Warnings
    warnings = [
        {
            "id": "NW-2026-0412",
            "type": "restricted_area",
            "lat": round(ship_lat + 0.03, 4),
            "lon": round(ship_lon + 0.02, 4),
            "radius_nm": 0.5,
            "message": "航行限制区域 - 海底管线施工",
            "valid_from": "2026-03-15",
            "valid_to": "2026-05-30",
        },
        {
            "id": "NW-2026-0398",
            "type": "works_in_progress",
            "lat": round(ship_lat - 0.04, 4),
            "lon": round(ship_lon - 0.06, 4),
            "radius_nm": 0.3,
            "message": "港口疏浚作业 - 减速慢行",
            "valid_from": "2026-02-01",
            "valid_to": "2026-06-30",
        },
    ]

    # S-102 Bathymetry summary
    bathymetry = {
        "min_depth_m": 3.2,
        "max_depth_m": 48.7,
        "mean_depth_m": 22.5,
        "grid_resolution_m": 2.0,
        "coverage": f"{ship_lat-0.1:.2f}N-{ship_lat+0.1:.2f}N, {ship_lon-0.1:.2f}E-{ship_lon+0.1:.2f}E",
    }

    return {
        "s100_version": "5.2.0",
        "timestamp": now.isoformat(),
        "ship_position": {"lat": ship_lat, "lon": ship_lon},
        "water_level": water_level,
        "currents": currents,
        "warnings": warnings,
        "bathymetry": bathymetry,
        "active_layers": ["S-101", "S-102", "S-104", "S-111", "S-124"],
    }


@app.get("/api/v1/s100/cpa")
async def get_cpa_analysis():
    """CPA/TCPA 避碰分析 API"""
    import math
    results = []
    ship_lat = sim_engine.ship_position["lat"]
    ship_lon = sim_engine.ship_position["lon"]
    ship_cog = sim_engine.ship_course + 0.4
    ship_sog = sim_engine.ship_speed

    for mmsi, target in ais_targets.items():
        # Relative position in nm
        d_lon = (target.longitude - ship_lon) * math.cos(math.radians(ship_lat)) * 60
        d_lat = (target.latitude - ship_lat) * 60
        # Relative velocity in nm/min
        own_vx = (ship_sog / 60) * math.sin(math.radians(ship_cog))
        own_vy = (ship_sog / 60) * math.cos(math.radians(ship_cog))
        tgt_vx = (target.speed / 60) * math.sin(math.radians(target.course))
        tgt_vy = (target.speed / 60) * math.cos(math.radians(target.course))
        dvx = tgt_vx - own_vx
        dvy = tgt_vy - own_vy
        dv_sq = dvx * dvx + dvy * dvy
        rng = math.sqrt(d_lon ** 2 + d_lat ** 2)
        bearing = (math.degrees(math.atan2(d_lon, d_lat)) + 360) % 360

        if dv_sq < 1e-10:
            cpa, tcpa = rng, 9999
        else:
            tcpa = max(0, -(d_lon * dvx + d_lat * dvy) / dv_sq)
            cpx = d_lon + dvx * tcpa
            cpy = d_lat + dvy * tcpa
            cpa = math.sqrt(cpx ** 2 + cpy ** 2)

        risk = "danger" if tcpa < 10 and cpa < 0.5 else ("caution" if tcpa < 20 and cpa < 1.0 else "safe")
        results.append({
            "mmsi": mmsi,
            "cpa_nm": round(cpa, 3),
            "tcpa_min": round(tcpa, 1),
            "range_nm": round(rng, 3),
            "bearing_deg": round(bearing, 1),
            "risk_level": risk,
        })

    results.sort(key=lambda r: ({"danger": 0, "caution": 1, "safe": 2}[r["risk_level"]], r["cpa_nm"]))
    return {"targets": results, "count": len(results)}


@app.get("/api/v1/engine/status")
async def get_engine_status():
    """获取主机状态"""
    try:
        from channels.marine_base import get_default_registry
        registry = get_default_registry()
        channel = registry.get("intelligent_engine")
        if channel:
            status = channel.get_status()
            latest = status.get("latest_snapshot") or {}
            return {
                "engine_id": "ME-1",
                "health_score": status.get("engine_health_score"),
                "alerts": status.get("alerts", []),
                "trend": status.get("trend", {}),
                **latest,
            }
    except Exception:
        pass
    if not engine_status:
        return {
            "engine_id": "ENG-001",
            "status": "initializing",
            "rpm": None,
            "load": None,
            "cooling_water_temp": None,
            "lube_oil_pressure": None,
            "fuel_consumption": None,
            "alerts": [],
        }
    return engine_status


@app.get("/api/v1/engine/telemetry")
async def get_engine_telemetry():
    """详细机舱遥测 — 缸级数据、涡轮增压器、排气系统"""
    import math
    t = time.time()

    rpm_base = 720 + math.sin(t * 0.1) * 15 + math.sin(t * 0.37) * 5
    load_base = 65 + math.sin(t * 0.08) * 12

    cylinders = []
    for i in range(6):
        phase = i * math.pi / 3
        cyl_temp = 380 + math.sin(t * 0.15 + phase) * 25 + (load_base - 60) * 0.8
        cyl_press = 140 + math.sin(t * 0.12 + phase) * 8 + (rpm_base - 720) * 0.05
        cylinders.append({
            "cylinder": i + 1,
            "exhaust_temp_c": round(cyl_temp, 1),
            "peak_pressure_bar": round(cyl_press, 1),
            "firing_order": [1, 5, 3, 6, 2, 4][i],
            "deviation_pct": round(math.sin(t * 0.3 + phase * 2) * 3.5, 1),
        })

    tc_rpm = rpm_base * 35 + math.sin(t * 0.5) * 500
    tc_boost = 1.8 + (load_base - 50) * 0.012 + math.sin(t * 0.2) * 0.1

    return {
        "timestamp": datetime.now().isoformat(),
        "main_engine": {
            "rpm": round(rpm_base, 1),
            "load_pct": round(load_base, 1),
            "power_kw": round(rpm_base * load_base * 0.12, 0),
            "sfoc_g_kwh": round(175 + (load_base - 75) ** 2 * 0.02, 1),
        },
        "cylinders": cylinders,
        "turbocharger": {
            "rpm": round(tc_rpm, 0),
            "boost_pressure_bar": round(tc_boost, 2),
            "inlet_temp_c": round(35 + load_base * 0.2, 1),
            "outlet_temp_c": round(180 + load_base * 1.2 + math.sin(t * 0.25) * 10, 1),
        },
        "cooling": {
            "jacket_water_inlet_c": round(36 + math.sin(t * 0.05) * 2, 1),
            "jacket_water_outlet_c": round(78 + load_base * 0.15 + math.sin(t * 0.06) * 3, 1),
            "charge_air_temp_c": round(40 + load_base * 0.1, 1),
        },
        "lubrication": {
            "oil_pressure_bar": round(4.2 + rpm_base * 0.001 - load_base * 0.005 + math.sin(t * 0.08) * 0.3, 2),
            "oil_temp_c": round(55 + load_base * 0.2 + math.sin(t * 0.04) * 3, 1),
            "viscosity_cst": round(13.5 - (55 + load_base * 0.2 - 50) * 0.05, 1),
        },
        "fuel": {
            "consumption_kg_h": round(rpm_base * load_base * 0.00021, 1),
            "inlet_temp_c": round(125 + math.sin(t * 0.03) * 5, 1),
            "viscosity_cst": round(12.0 + math.sin(t * 0.02) * 1.5, 1),
            "density_kg_m3": 991.0,
        },
        "exhaust": {
            "avg_temp_c": round(sum(c["exhaust_temp_c"] for c in cylinders) / 6, 1),
            "max_deviation_c": round(max(abs(c["deviation_pct"]) for c in cylinders) * 8, 1),
            "economizer_inlet_c": round(250 + load_base * 0.5, 1),
            "economizer_outlet_c": round(170 + load_base * 0.2, 1),
        },
    }


@app.get("/api/v1/weather")
async def get_weather():
    """获取实时气象数据 (模拟/WorldMonitor) — 含天气事件周期"""
    import math
    t = time.time()
    
    # ── 天气事件系统 (90s 基础周期) ──
    cycle = (t % 300) / 300.0  # 5 分钟完整天气循环
    # 四个天气阶段: 0-0.3 晴好, 0.3-0.5 起风, 0.5-0.7 暴风雨, 0.7-1.0 雾散
    weather_event = "clear"
    event_intensity = 0.0
    if cycle < 0.3:
        weather_event = "clear"
        event_intensity = 0.0
    elif cycle < 0.5:
        weather_event = "squall_building"
        event_intensity = (cycle - 0.3) / 0.2
    elif cycle < 0.7:
        weather_event = "squall"
        event_intensity = 1.0 - abs(cycle - 0.6) * 5.0  # peak at 0.6
        event_intensity = max(0.5, event_intensity)
    elif cycle < 0.85:
        weather_event = "fog"
        event_intensity = (0.85 - cycle) / 0.15
    else:
        weather_event = "clearing"
        event_intensity = (1.0 - cycle) / 0.15
    
    # 基础天气 + 事件叠加
    base_wind = 8.0 + math.sin(t * 0.002) * 5.0 + math.sin(t * 0.0073) * 2.0
    squall_boost = event_intensity * 12.0 if weather_event in ("squall_building", "squall") else 0.0
    wind_speed = base_wind + squall_boost
    wind_dir = (220 + math.sin(t * 0.001) * 30) % 360
    if weather_event == "squall":
        wind_dir = (wind_dir + event_intensity * 40) % 360  # 风向急转
    
    base_wave = 0.8 + abs(math.sin(t * 0.0015)) * 2.5
    wave_height = base_wave + squall_boost * 0.3
    wave_period = 6.0 + math.sin(t * 0.003) * 3.0 - event_intensity * 2.0
    wave_dir = (wind_dir + 15 + math.sin(t * 0.005) * 10) % 360
    
    base_vis = max(2.0, 12.0 - wave_height * 1.5 + math.sin(t * 0.004) * 3.0)
    fog_factor = event_intensity * 8.0 if weather_event == "fog" else 0.0
    rain_vis_drop = event_intensity * 5.0 if weather_event == "squall" else 0.0
    visibility = max(0.3, base_vis - fog_factor - rain_vis_drop)
    
    temp_air = 18.0 + math.sin(t * 0.0001) * 5.0 - (event_intensity * 3.0 if weather_event == "squall" else 0.0)
    temp_sea = 15.0 + math.sin(t * 0.00008) * 3.0
    pressure = 1013.25 + math.sin(t * 0.0003) * 8.0 - (event_intensity * 12.0 if weather_event in ("squall_building", "squall") else 0.0)
    humidity = 75 + math.sin(t * 0.0005) * 15 + (event_intensity * 15 if weather_event in ("squall", "fog") else 0.0)

    # 降水判定 — 暴风雨时强降雨
    rain_prob = max(0, (wind_speed - 12) / 8 + (3.0 - visibility) / 5)
    if weather_event == "squall":
        rain_prob = max(rain_prob, event_intensity * 0.9)
    rain_intensity = max(0.0, min(1.0, rain_prob))
    precip_type = "rain" if rain_intensity > 0.1 and temp_air > 2 else "snow" if rain_intensity > 0.1 else "none"

    # 海况等级 (Douglas scale)
    if wave_height < 0.1:
        sea_state = 0
    elif wave_height < 0.5:
        sea_state = 2
    elif wave_height < 1.25:
        sea_state = 3
    elif wave_height < 2.5:
        sea_state = 4
    elif wave_height < 4.0:
        sea_state = 5
    else:
        sea_state = 6

    # 蒲福风级
    beaufort = min(12, int(wind_speed / 1.5))

    return {
        "timestamp": datetime.now().isoformat(),
        "wind": {
            "speed_ms": round(wind_speed, 1),
            "speed_kn": round(wind_speed * 1.944, 1),
            "direction_deg": round(wind_dir, 1),
            "beaufort": beaufort,
        },
        "wave": {
            "significant_height_m": round(wave_height, 2),
            "period_s": round(wave_period, 1),
            "direction_deg": round(wave_dir, 1),
            "sea_state": sea_state,
        },
        "visibility_km": round(visibility, 1),
        "temperature": {
            "air_c": round(temp_air, 1),
            "sea_c": round(temp_sea, 1),
        },
        "pressure_hpa": round(pressure, 1),
        "humidity_pct": round(humidity, 0),
        "precipitation": {
            "type": precip_type,
            "intensity": round(rain_intensity, 2),
        },
        "event": {
            "type": weather_event,
            "intensity": round(event_intensity, 2),
            "cycle_pct": round(cycle * 100, 1),
        },
    }


@app.get("/api/v1/alerts")
async def get_alerts():
    """获取报警列表"""
    return {"alerts": [a.model_dump() for a in alarms]}


@app.get("/api/v1/voyage")
async def get_voyage():
    """获取当前航次信息和航路点"""
    import math
    t = time.time()
    lat = sim_engine.ship_position["lat"]
    lon = sim_engine.ship_position["lon"]
    course = sim_engine.ship_course
    speed = sim_engine.ship_speed

    # 预定义航路点 (上海 → 济州岛 → 博多)
    waypoints = [
        {"name": "WP0 上海港", "lat": 30.85, "lon": 122.35, "status": "passed"},
        {"name": "WP1 长江口外", "lat": 31.10, "lon": 122.80, "status": "passed"},
        {"name": "WP2 东海中间", "lat": 31.60, "lon": 124.20, "status": "next"},
        {"name": "WP3 济州海峡", "lat": 33.00, "lon": 126.50, "status": "planned"},
        {"name": "WP4 博多港", "lat": 33.60, "lon": 130.40, "status": "planned"},
    ]

    # 到下一个航路点的距离/ETA
    next_wp = waypoints[2]
    dlat = next_wp["lat"] - lat
    dlon = next_wp["lon"] - lon
    dist_nm = math.sqrt(dlat ** 2 + dlon ** 2) * 60.0
    eta_hours = dist_nm / max(speed, 0.1)

    return {
        "voyage_id": "VY-2026-0418",
        "vessel": "PoseidonX WPC-01",
        "departure": {"port": "上海港", "time": "2026-04-18T06:00:00+08:00"},
        "destination": {"port": "博多港", "eta": f"{eta_hours:.1f}h"},
        "current_position": {"lat": round(lat, 6), "lon": round(lon, 6)},
        "course_deg": round(course, 1),
        "speed_kn": round(speed, 1),
        "distance_to_next_wp_nm": round(dist_nm, 1),
        "eta_next_wp_hours": round(eta_hours, 1),
        "total_distance_nm": 520,
        "completed_nm": round(520 - dist_nm * 2.5, 1),
        "waypoints": waypoints,
    }


@app.get("/api/v1/ballast")
async def get_ballast_status():
    """压载水舱状态"""
    import math
    t = time.time()
    tanks = [
        {"id": "FP", "name": "首尖舱 (Fore Peak)", "capacity_m3": 200,
         "level_pct": round(65 + math.sin(t * 0.01) * 5 + math.sin(t * 0.003) * 3, 1)},
        {"id": "AP", "name": "尾尖舱 (Aft Peak)", "capacity_m3": 200,
         "level_pct": round(78 + math.sin(t * 0.008 + 1) * 4, 1)},
        {"id": "PS_DB", "name": "左舷双层底 (Port DB)", "capacity_m3": 200,
         "level_pct": round(45 + math.sin(t * 0.012 + 2) * 6, 1)},
        {"id": "SB_DB", "name": "右舷双层底 (Stbd DB)", "capacity_m3": 200,
         "level_pct": round(52 + math.sin(t * 0.009 + 3) * 5, 1)},
    ]
    total_vol = sum(tk["capacity_m3"] * tk["level_pct"] / 100 for tk in tanks)
    total_cap = sum(tk["capacity_m3"] for tk in tanks)
    return {
        "timestamp": datetime.now().isoformat(),
        "tanks": tanks,
        "total_volume_m3": round(total_vol, 1),
        "total_capacity_m3": total_cap,
        "total_pct": round(total_vol / total_cap * 100, 1),
        "trim_correction_needed": abs(tanks[0]["level_pct"] - tanks[1]["level_pct"]) > 20,
    }


@app.get("/api/v1/crew")
async def get_crew_status():
    """船员及值班状态"""
    import math
    t = time.time()
    hour = datetime.now().hour
    
    # 值班制度 (三班两运)
    watches = [
        {"period": "0000-0400", "name": "Middle Watch", "cn": "中夜更"},
        {"period": "0400-0800", "name": "Morning Watch", "cn": "上午更"},
        {"period": "0800-1200", "name": "Forenoon Watch", "cn": "午前更"},
        {"period": "1200-1600", "name": "Afternoon Watch", "cn": "午后更"},
        {"period": "1600-1800", "name": "1st Dog Watch", "cn": "日暮更"},
        {"period": "1800-2000", "name": "2nd Dog Watch", "cn": "前夜更"},
        {"period": "2000-0000", "name": "First Watch", "cn": "后夜更"},
    ]
    if hour < 4: wi = 0
    elif hour < 8: wi = 1
    elif hour < 12: wi = 2
    elif hour < 16: wi = 3
    elif hour < 18: wi = 4
    elif hour < 20: wi = 5
    else: wi = 6
    
    crew = [
        {"name": "Capt. 王明远", "role": "Master", "status": "on_bridge", "fatigue": round(0.2 + math.sin(t * 0.001) * 0.1, 2)},
        {"name": "C/O 赵海洋", "role": "Chief Officer", "status": "on_watch" if wi in [1, 3, 5] else "rest"},
        {"name": "2/O 李航", "role": "Second Officer", "status": "on_watch" if wi in [0, 2, 4] else "rest"},
        {"name": "3/O 陈波", "role": "Third Officer", "status": "on_watch" if wi in [1, 4, 6] else "rest"},
        {"name": "C/E 张伟", "role": "Chief Engineer", "status": "engine_room", "fatigue": round(0.25 + math.sin(t * 0.0008) * 0.08, 2)},
        {"name": "2/E 刘大海", "role": "Second Engineer", "status": "on_watch" if wi in [0, 2, 5] else "rest"},
        {"name": "AB 陈强", "role": "Helmsman", "status": "helm"},
    ]
    
    return {
        "timestamp": datetime.now().isoformat(),
        "current_watch": watches[wi],
        "total_crew": 25,
        "on_duty": sum(1 for c in crew if c["status"] not in ["rest"]),
        "crew": crew,
    }


@app.get("/api/v1/performance")
async def get_ship_performance():
    """船舶性能数据 — 速度-功率曲线、推进效率"""
    import math
    t = time.time()
    rpm = sim_engine.engine["rpm"]
    load = sim_engine.engine["load"]
    speed = sim_engine.ship_speed
    
    # 速度-功率曲线 (理论曲线 + 实际点)
    speed_power_curve = []
    for v in range(4, 19):
        theoretical_power = (v ** 3) * 0.18  # 简化立方定律
        speed_power_curve.append({
            "speed_kn": v,
            "power_kw": round(theoretical_power, 0),
        })
    
    actual_power = round((speed ** 3) * 0.18 * (1 + math.sin(t * 0.1) * 0.05), 1)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "current": {
            "speed_kn": round(speed, 1),
            "power_kw": actual_power,
            "rpm": round(rpm, 1),
            "slip_pct": round(3.5 + math.sin(t * 0.2) * 1.5, 1),
            "propeller_efficiency": round(0.65 + math.sin(t * 0.15) * 0.03, 3),
            "hull_efficiency": round(1.05 + math.sin(t * 0.08) * 0.02, 3),
        },
        "speed_power_curve": speed_power_curve,
        "fuel_efficiency": {
            "sfoc_g_kwh": round(175 + (load - 75) ** 2 * 0.015, 1),
            "daily_consumption_mt": round(actual_power * 24 * 175 / 1e6, 2),
            "eeoi_gCO2_tnm": round(3.206 * actual_power * 175 / (speed * 8500 + 0.1) / 1e3, 3),
        },
        "sea_margin_pct": round(15 + math.sin(t * 0.05) * 5, 1),
        "fouling_factor": round(1.0 + (t % 86400) / 86400 * 0.05, 3),
    }


@app.get("/api/v1/worldmonitor/ais")
async def get_worldmonitor_ais():
    """获取 WorldMonitor AIS 数据"""
    if worldmonitor_real:
        try:
            targets = await worldmonitor_real.get_ais_targets()
            return {
                "source": "real",
                "mode": "connected",
                "targets": [t.to_dict() for t in targets],
                "count": len(targets),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"WorldMonitor real AIS failed: {e}, falling back to placeholder")
    
    # fallback to placeholder
    return await worldmonitor.get_ais_targets()


@app.get("/api/v1/worldmonitor/weather")
async def get_worldmonitor_weather(lat: float = Query(..., ge=-90, le=90), lng: float = Query(..., ge=-180, le=180)):
    """获取 WorldMonitor 海洋气象数据"""
    if worldmonitor_real:
        try:
            weather = await worldmonitor_real.get_marine_weather(lat, lng)
            return {
                "source": "real", 
                "mode": "connected",
                "weather": weather.to_dict() if weather else None,
                "position": {"lat": lat, "lng": lng},
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"WorldMonitor real weather failed: {e}, falling back to placeholder")
    
    # fallback to placeholder
    return await worldmonitor.get_marine_weather(lat, lng)


@app.get("/api/v1/worldmonitor/ports")
async def get_worldmonitor_ports(region: Optional[str] = Query(default=None, max_length=200)):
    """获取 WorldMonitor 港口态势"""
    if worldmonitor_real:
        try:
            ports = await worldmonitor_real.get_ports(region)
            return {
                "source": "real",
                "mode": "connected", 
                "ports": ports,
                "count": len(ports),
                "region": region,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"WorldMonitor real ports failed: {e}, falling back to placeholder")
    
    # fallback to placeholder
    return await worldmonitor.get_ports()


@app.get("/api/v1/worldmonitor/routes")
async def get_worldmonitor_routes(origin_port: Optional[str] = Query(default=None, max_length=200), dest_port: Optional[str] = Query(default=None, max_length=200)):
    """获取 WorldMonitor 航线态势"""
    if worldmonitor_real:
        try:
            routes = await worldmonitor_real.get_shipping_routes(origin_port, dest_port)
            return {
                "source": "real",
                "mode": "connected",
                "routes": routes,
                "count": len(routes),
                "origin": origin_port,
                "destination": dest_port,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"WorldMonitor real routes failed: {e}, falling back to placeholder")
    
    # fallback to placeholder
    return await worldmonitor.get_shipping_routes()


# ─────────────────────────────────────────────────────────────────────
# Marine DataCenter Energy API — 船载数据中心 AI 能耗管理
# (4 视角 / IoT Hub / Skill库 / 策略 / 闭环 / Darwin 棘轮)
# ─────────────────────────────────────────────────────────────────────

def _dc_channel():
    from channels.marine_base import get_default_registry
    ch = get_default_registry().get("marine_datacenter_energy")
    if not ch:
        raise HTTPException(status_code=503, detail="marine_datacenter_energy not registered")
    return ch


@app.get("/api/v1/datacenter/status")
async def dc_status():
    """获取数据中心 AI 能耗管理总状态."""
    return _dc_channel().get_status()


@app.get("/api/v1/datacenter/perspective/{name}")
async def dc_perspective(name: str):
    """单视角分析: device|facility|environment|process."""
    from channels.marine_datacenter_energy import DCPerspective
    try:
        return _dc_channel().analyze_perspective(DCPerspective(name))
    except ValueError:
        raise HTTPException(status_code=400, detail=f"unknown perspective: {name}")


@app.get("/api/v1/datacenter/four-view")
async def dc_four_view():
    """4 视角并发分析."""
    return _dc_channel().four_view_overview()


@app.get("/api/v1/datacenter/iot/hub")
async def dc_iot_hub():
    """IoT Hub 汇总 (LoRa/MC-RFID/PLC-Agent)."""
    return _dc_channel().hub_summary()


@app.get("/api/v1/datacenter/iot/sensors")
async def dc_iot_sensors():
    """所有传感器列表."""
    ch = _dc_channel()
    return {"sensors": [
        {"sensor_id": s.sensor_id, "kind": s.kind.value, "location": s.location,
         "value": s.value, "unit": s.unit, "battery_pct": s.battery_pct, "rssi": s.rssi}
        for s in ch.sensors.values()
    ]}


class IoTIngestPayload(BaseModel):
    sensor_id: str
    value: float


@app.post("/api/v1/datacenter/iot/ingest")
async def dc_iot_ingest(payload: IoTIngestPayload):
    return _dc_channel().ingest_sensor(payload.sensor_id, payload.value)


# ── Sensing Layer (Page 2) — LoRA 热场 / 热岛 / PLC 闭环 / 棘轮 ──

@app.get("/api/v1/datacenter/sensing/field")
async def dc_sensing_field():
    """LoRA 热场: 所有传感器 + X/Y/Z + 分类 (normal/warm/hotspot/overcool)."""
    return _dc_channel().sensor_field()


@app.get("/api/v1/datacenter/sensing/heat-island")
async def dc_sensing_heat_island():
    """AI 热岛检测: Δ≥3°C & T>31°C 的局部聚集 + 冷量过剩区."""
    return _dc_channel().detect_heat_island()


class PLCFanPayload(BaseModel):
    device_hint: str = "crac"
    delta_hz: float = 2.0


@app.post("/api/v1/datacenter/sensing/plc/fan")
async def dc_sensing_plc_fan(payload: PLCFanPayload):
    """PLC 端 Agent 调整 CRAC/风机频率 (毫秒级 demo)."""
    return _dc_channel().plc_adjust_fan(payload.device_hint, payload.delta_hz)


class RatchetPayload(BaseModel):
    note: str = "cooling optimum captured"


@app.post("/api/v1/datacenter/sensing/ratchet")
async def dc_sensing_ratchet(payload: RatchetPayload):
    """棘轮锁定当前热场优化 → DarwinHeritage."""
    return _dc_channel().ratchet_lock_cooling(payload.note)


@app.get("/api/v1/datacenter/skills")
async def dc_skills():
    """运维技能库 (Lobster-style sediment)."""
    ch = _dc_channel()
    return {"skills": [
        {"skill_id": s.skill_id, "title": s.title, "trigger": s.trigger, "action": s.action,
         "author": s.author, "confidence": round(s.confidence, 3),
         "success_count": s.success_count, "fail_count": s.fail_count, "tags": s.tags}
        for s in ch.skills.values()
    ]}


class SkillAddPayload(BaseModel):
    skill_id: str
    title: str
    trigger: str
    action: str
    author: str = "ops_team"
    tags: List[str] = []


@app.post("/api/v1/datacenter/skills")
async def dc_add_skill(payload: SkillAddPayload):
    return _dc_channel().add_skill(payload.skill_id, payload.title, payload.trigger,
                                    payload.action, payload.author, payload.tags)


class SkillReinforcePayload(BaseModel):
    success: bool


@app.post("/api/v1/datacenter/skills/{skill_id}/reinforce")
async def dc_reinforce_skill(skill_id: str, payload: SkillReinforcePayload):
    return _dc_channel().reinforce_skill(skill_id, payload.success)


@app.get("/api/v1/datacenter/policies")
async def dc_policies():
    """节能策略库 (开源/节流)."""
    ch = _dc_channel()
    return {"policies": [
        {"policy_id": p.policy_id, "kind": p.kind.value, "title": p.title,
         "rationale": p.rationale, "estimated_saving_kwh_day": p.estimated_saving_kwh_day,
         "applied": p.applied, "fitness": p.fitness}
        for p in ch.policies.values()
    ]}


class PolicyApplyPayload(BaseModel):
    policy_id: str
    fitness: float = 0.85


@app.post("/api/v1/datacenter/policies/apply")
async def dc_apply_policy(payload: PolicyApplyPayload):
    return _dc_channel().apply_policy(payload.policy_id, payload.fitness)


@app.post("/api/v1/datacenter/loop/tick")
async def dc_loop_tick():
    """触发一次闭环 (监控→决策→调整→验证)."""
    return _dc_channel().closed_loop_tick()


class EvolvePayload(BaseModel):
    title: str
    category: str = "general"
    delta_pue: float = -0.005
    delta_kwh_day: float = 1.0


@app.post("/api/v1/datacenter/evolve")
async def dc_evolve(payload: EvolvePayload):
    """Darwin 棘轮: 永远只增不减."""
    return _dc_channel().evolve(payload.title, payload.category,
                                 payload.delta_pue, payload.delta_kwh_day)


@app.get("/api/v1/datacenter/heritage")
async def dc_heritage():
    """演进遗产账本."""
    return {"heritage": _dc_channel().heritage_ledger()}


@app.get("/api/v1/datacenter/events")
async def dc_events(limit: int = 50):
    """最近闭环事件流."""
    ch = _dc_channel()
    return {"events": ch.events[-limit:]}


@app.get("/api/v1/datacenter/pue-history")
async def dc_pue_history(limit: int = 240):
    """PUE 时间序列 (用于趋势图)."""
    return {"history": _dc_channel().get_pue_history(limit)}


@app.get("/api/v1/datacenter/sankey")
async def dc_sankey():
    """能流 Sankey 数据."""
    return _dc_channel().energy_sankey()


@app.get("/api/v1/datacenter/recommend")
async def dc_recommend(top_n: int = 5):
    """AI 推荐 top-N 节能策略."""
    return {"recommendations": _dc_channel().recommend_actions(top_n)}


@app.get("/api/v1/datacenter/benchmark")
async def dc_benchmark():
    """与行业基准对比."""
    return _dc_channel().benchmark()


@app.get("/api/v1/datacenter/cost")
async def dc_cost():
    """节能 → 钱 / CO₂ 折算."""
    return _dc_channel().cost_summary()


@app.get("/api/v1/datacenter/devices")
async def dc_devices():
    """设备列表."""
    return {"devices": _dc_channel().list_devices()}


@app.get("/api/v1/datacenter/devices/{device_id}")
async def dc_device_detail(device_id: str):
    """单设备详情."""
    d = _dc_channel().get_device_detail(device_id)
    if not d:
        raise HTTPException(status_code=404, detail=f"device {device_id} not found")
    return d


class AutoLoopPayload(BaseModel):
    enabled: bool
    interval_s: int = 45


@app.post("/api/v1/datacenter/auto-loop")
async def dc_auto_loop(payload: AutoLoopPayload):
    """启用/停用自动闭环."""
    return _dc_channel().set_auto_loop(payload.enabled, payload.interval_s)


class AIInsightPayload(BaseModel):
    focus: str = ""


@app.post("/api/v1/datacenter/ai-insight")
async def dc_ai_insight(payload: AIInsightPayload):
    """AI 洞察 (template, 可被前端拼到 LLM)."""
    return _dc_channel().ai_insight(payload.focus)


@app.get("/api/v1/datacenter/forecast")
async def dc_forecast(hours: int = 24, step_min: int = 30):
    """24h PUE 预测 (基于负载日变化 + 已应用策略)."""
    return _dc_channel().forecast_pue(hours=hours, sample_step_min=step_min)


@app.get("/api/v1/datacenter/anomalies")
async def dc_anomalies(z_threshold: float = 2.0):
    """异常检测: 热点 / 设备过载 / 传感器离线 / PUE 漂移."""
    return _dc_channel().detect_anomalies(z_threshold=z_threshold)


class WhatIfPayload(BaseModel):
    scenarios: List[Dict[str, Any]] = []


@app.post("/api/v1/datacenter/what-if")
async def dc_what_if(payload: WhatIfPayload):
    """What-If 模拟: 估算一组假设策略的 PUE / 节能 / 投资回收期."""
    return _dc_channel().what_if(payload.scenarios)


@app.post("/api/v1/datacenter/simulate-tick")
async def dc_simulate_tick():
    """触发一次时序 tick (随机抖动 + PUE 历史写入), 用于演示动态曲线."""
    return _dc_channel().simulate_tick()


@app.get("/api/v1/datacenter/musk-audit")
async def dc_musk_audit():
    """马斯克五步工作法 (质疑/删除/简化/加速/自动化) 推演."""
    return _dc_channel().musk_five_step_audit()


@app.websocket("/ws/datacenter/sensing")
async def dc_sensing_ws(websocket: WebSocket):
    """Page-2 极智感知层实时流: LoRA 热场 + 热岛 + PUE."""
    await websocket.accept()
    import asyncio as _asyncio
    try:
        ch = _dc_channel()
        while True:
            try:
                ch.simulate_tick()
            except Exception:
                pass
            field = ch.sensor_field()
            heat = ch.detect_heat_island()
            payload = {
                "type": "sensing_tick",
                "ts": time.time(),
                "field": field,
                "heat_island": heat,
                "pue": ch.current_pue,
                "baseline_pue": ch.baseline_pue,
                "target_pue": ch.target_pue,
                "ratchet": {
                    "evolution_round": ch._evolution_round,
                    "heritage_count": len(ch.heritage),
                    "latest": (ch.heritage[-1].title if ch.heritage else None),
                    "cumulative_kwh_day": round(sum(h.delta_kwh_day for h in ch.heritage), 2),
                },
            }
            await websocket.send_json(payload)
            await _asyncio.sleep(1.5)
    except Exception:
        return


@app.websocket("/ws/datacenter")
async def dc_websocket(websocket: WebSocket):
    """实时推送数据中心状态 (status + pue + recent event)."""
    await websocket.accept()
    try:
        ch = _dc_channel()
        last_evt_idx = len(ch.events)
        # 同时启动后台自动闭环 tick (lazy)
        import asyncio as _asyncio
        async def _auto_tick():
            while True:
                await _asyncio.sleep(ch.auto_loop_interval_s)
                if ch.auto_loop_enabled:
                    try:
                        ch.closed_loop_tick()
                    except Exception:
                        pass
        # ensure single background task
        if not getattr(ch, "_auto_task", None):
            ch._auto_task = _asyncio.create_task(_auto_tick())
        while True:
            # 让曲线动起来: 每次推送前做一次轻量 tick (设备/温度/PUE 抖动)
            try:
                ch.simulate_tick()
            except Exception:
                pass
            payload = {
                "type": "tick",
                "ts": time.time(),
                "status": ch.get_status(),
                "pue_point": {"ts": time.time(), "pue": ch.current_pue},
            }
            # pipe new events
            if len(ch.events) > last_evt_idx:
                payload["new_events"] = ch.events[last_evt_idx:]
                last_evt_idx = len(ch.events)
            await websocket.send_json(payload)
            await _asyncio.sleep(2)
    except Exception:
        return


@app.get("/api/v1/dashboard")
async def get_dashboard():
    """聚合 Dashboard 数据，供前端统一展示。"""
    from channels.marine_base import get_default_registry
    registry = get_default_registry()

    def _collect_dashboard():
        nav = registry.get("intelligent_navigation")
        engine = registry.get("intelligent_engine")
        efficiency = registry.get("energy_efficiency")
        compliance = registry.get("compliance_digital_expert")
        perception = registry.get("distributed_perception_hub")
        orchestrator = registry.get("decision_orchestrator")
        rcs = registry.get("rcs_control")
        shm = registry.get("structural_health_monitor")
        # Phase 3: 演进驱动的扩展 Channel
        evo = registry.get("system_evolution")
        propulsion = registry.get("propulsion_monitor")
        safety = registry.get("safety_system_monitor")
        colregs = registry.get("colregs_brain")
        mob = registry.get("man_overboard")
        hull = registry.get("hull_stress_monitor")
        cyber = registry.get("cyber_security")
        autonomy = registry.get("autonomy_manager")
        vdr = registry.get("vdr_recorder")
        wpc = registry.get("wpc_attitude_control")

        nav_status = nav.get_status() if nav else {}
        nav_report = nav.generate_navigation_report() if nav and hasattr(nav, "generate_navigation_report") else {}
        engine_st = engine.get_status() if engine else {}
        eff_status = efficiency.get_status() if efficiency else {}

        efficiency_summary = {
            "health": eff_status.get("health"),
            "health_message": eff_status.get("health_message"),
            "vessel": eff_status.get("vessel"),
            "recommendations_count": len(getattr(efficiency, "get_recommendations", lambda: [])()) if efficiency else 0,
        }

        # 只取 latest_package 的摘要，避免返回巨型 dict
        latest_pkg = getattr(orchestrator, "latest_package", None) or {}
        pkg_summary = {
            "generated_at": latest_pkg.get("generated_at"),
            "risk_level": latest_pkg.get("risk_level"),
            "autonomy_mode": latest_pkg.get("autonomy_mode"),
            "action_count": len(latest_pkg.get("action_plan", [])),
        }

        # channels 只取 health 字符串，用 try 保护
        channel_names = registry.list_channels()[:20]
        channel_list = []
        for n in channel_names:
            ch = registry.get(n)
            if ch:
                try:
                    h = ch.get_status().get("health", "unknown")
                except Exception as e:
                    logger.debug(f"Channel health check error: {e}")
                    h = "error"
                channel_list.append({"name": n, "health": h})

        return {
            "captain_agent": {
                "name": "decision_orchestrator",
                "status": orchestrator.get_status() if orchestrator else {},
                "last_decision_package": pkg_summary,
                "coordination": coordination_status,
            },
            "navigation": {
                "own_ship": nav_status.get("own_ship", {}),
                "report": nav_report,
            },
            "engine": {
                "health_score": engine_st.get("engine_health_score"),
                "alerts": engine_st.get("alerts", []),
                "latest": engine_st.get("latest_snapshot"),
                "trend": engine_st.get("trend", {}),
                "maintenance_advice": engine.get_maintenance_advice() if engine and hasattr(engine, "get_maintenance_advice") else [],
            },
            "efficiency": efficiency_summary,
            "compliance": compliance.query_compliance_status("overall") if compliance and hasattr(compliance, "query_compliance_status") else {},
            "perception": perception.get_status() if perception else {},
            "decision": pkg_summary,
            "rcs": rcs.get_status() if rcs else {},
            "shm": shm.get_status() if shm else {},
            "memory": {
                "store_type": data_lakehouse.config.get("store_type", "sqlite"),
                "buffer_size": len(data_lakehouse.event_buffer),
            },
            "worldmonitor": {
                "mode": "connected" if worldmonitor_real else worldmonitor.mode,
                "enabled": worldmonitor_real is not None,
                "status": "ready" if worldmonitor_real else "placeholder",
                "data_source": "real" if worldmonitor_real else "mock",
            },
            "channels": channel_list,
            # Phase 3: 演进引擎 + 扩展 Channel 数据
            "evolution": {
                "rating": evo.get_compliance_rating() if evo and hasattr(evo, "get_compliance_rating") else {},
                "escalation": evo.get_escalation_status() if evo and hasattr(evo, "get_escalation_status") else {},
                "active_zones": evo.get_active_zones() if evo and hasattr(evo, "get_active_zones") else [],
                "trend": evo.get_trend_analysis() if evo and hasattr(evo, "get_trend_analysis") else {},
            } if evo else {},
            "propulsion": propulsion.get_status() if propulsion else {},
            "safety": {
                "status": safety.get_status() if safety else {},
                "epirb": safety.epirb_check() if safety and hasattr(safety, "epirb_check") else {},
                "sart": safety.sart_check() if safety and hasattr(safety, "sart_check") else {},
            },
            "colregs": colregs.get_status() if colregs else {},
            "mob": mob.get_status() if mob else {},
            "hull_stress": hull.get_status() if hull else {},
            "cyber": {
                "status": cyber.get_status() if cyber else {},
                "network_segmentation": cyber.check_network_segmentation() if cyber and hasattr(cyber, "check_network_segmentation") else {},
            },
            "autonomy": autonomy.get_status() if autonomy else {},
            "vdr": vdr.get_status() if vdr else {},
            "wpc": wpc.get_status() if wpc else {},
        }

    loop = asyncio.get_event_loop()
    # 使用 TTL 缓存减少重复计算
    global _dashboard_cache, _dashboard_cache_ts
    now = time.monotonic()
    if _dashboard_cache and (now - _dashboard_cache_ts) < _DASHBOARD_CACHE_TTL:
        return _dashboard_cache
    result = await loop.run_in_executor(_api_executor, _collect_dashboard)
    _dashboard_cache = result
    _dashboard_cache_ts = time.monotonic()
    return result


@app.get("/api/v1/ai-native/coordination/status")
async def get_ai_native_coordination_status():
    """获取 AI Native 协调状态和记忆层状态。"""
    return {
        "coordination": coordination_status,
        "memory": {
            "store_type": data_lakehouse.config.get("store_type", "sqlite"),
            "buffer_size": len(data_lakehouse.event_buffer),
        },
    }


@app.get("/api/v1/ai-native/perception/fusion-state")
async def get_ai_native_fusion_state():
    """返回当前特征融合轨迹状态，供数字孪生消费。"""
    def _collect():
        from channels.marine_base import get_default_registry
        registry = get_default_registry()
        perception = registry.get("distributed_perception_hub")
        if not perception or not hasattr(perception, "get_fusion_state"):
            return None
        return {"channel": "distributed_perception_hub", "fusion": perception.get_fusion_state()}
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_api_executor, _collect)
    if result is None:
        raise HTTPException(status_code=404, detail="Perception fusion state not found")
    return result


@app.get("/api/v1/ai-native/rcs/status")
async def get_ai_native_rcs_status():
    def _collect():
        from channels.marine_base import get_default_registry
        registry = get_default_registry()
        rcs = registry.get("rcs_control")
        if not rcs:
            return None
        return {"channel": "rcs_control", "result": rcs.get_status()}
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_api_executor, _collect)
    if result is None:
        raise HTTPException(status_code=404, detail="RCS control not found")
    return result


@app.get("/api/v1/ai-native/shm/status")
async def get_ai_native_shm_status():
    def _collect():
        from channels.marine_base import get_default_registry
        registry = get_default_registry()
        shm = registry.get("structural_health_monitor")
        if not shm:
            return None
        return {"channel": "structural_health_monitor", "result": shm.get_status()}
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_api_executor, _collect)
    if result is None:
        raise HTTPException(status_code=404, detail="Structural health monitor not found")
    return result


@app.get("/api/v1/ai-native/cps/mission-brief")
async def get_cps_mission_brief():
    """返回面向驾驶台和总师的 CPS 任务摘要。"""
    def _collect():
        from channels.marine_base import get_default_registry
        registry = get_default_registry()
        orchestrator = registry.get("decision_orchestrator")
        if not orchestrator:
            return None
        package = getattr(orchestrator, "latest_package", None) or {}
        return {
            "generated_at": package.get("generated_at"),
            "mission_brief": package.get("mission_brief"),
            "action_plan": package.get("action_plan", []),
            "task_graph": package.get("task_graph", {}),
            "autonomy_mode": package.get("autonomy_mode"),
            "memory_profile": data_lakehouse.get_memory_profile(limit=30),
        }
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_api_executor, _collect)
    if result is None:
        raise HTTPException(status_code=404, detail="Decision orchestrator not found")
    return result


@app.get("/api/v1/agents")
async def get_agents():
    """
    Retrieve the list of agents from pixel-agents.json.
    """
    try:
        # Define the path to pixel-agents.json in the project root
        agents_file = BASE_DIR / "pixel-agents.json"

        # Check if the file exists
        if not agents_file.exists():
            raise HTTPException(status_code=404, detail="Agents file not found")

        # Read and parse the file
        with agents_file.open("r", encoding="utf-8") as f:
            agents_data = json.load(f)

        return agents_data

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse agents file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/api/v1/ai-native/memory/events")
async def get_ai_native_memory_events(limit: int = Query(default=20, ge=1, le=1000), event_type: Optional[str] = Query(default=None, max_length=200)):
    """查询 AI Native 记忆层事件。"""
    def _query():
        events = data_lakehouse.query_events(event_type=event_type, limit=limit)
        return {"count": len(events), "event_type": event_type, "events": events}
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_api_executor, _query)


@app.get("/api/v1/ai-native/memory/replay")
async def replay_ai_native_memory(
    limit: int = Query(default=20, ge=1, le=1000),
    event_types: Optional[str] = Query(default=None, max_length=500),
    start_time: Optional[str] = Query(default=None, max_length=200),
    end_time: Optional[str] = Query(default=None, max_length=200),
):
    """按事件类型与时间窗口回放 AI Native 记忆层。"""
    selected_types = [item.strip() for item in (event_types or "").split(",") if item.strip()]

    def _replay():
        if start_time and end_time:
            try:
                evts = data_lakehouse.query_events_by_time(
                    datetime.fromisoformat(start_time),
                    datetime.fromisoformat(end_time),
                )
            except ValueError as exc:
                return {"error": f"Invalid datetime range: {exc}"}
        else:
            evts = data_lakehouse.query_events(limit=max(limit * 3, limit))
        filtered = evts
        if selected_types:
            filtered = [e for e in evts if e.get("event_type") in selected_types]
        filtered = filtered[:limit]
        return {"count": len(filtered), "limit": limit, "event_types": selected_types, "events": filtered}

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_api_executor, _replay)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/api/v1/ai-native/memory/analytics/status")
async def get_ai_native_memory_analytics_status():
    """返回 AI Native 湖仓分析能力状态。"""
    def _collect():
        return {
            "status": "ready",
            "storage_profile": data_lakehouse.get_storage_profile(),
            "lakehouse_status": data_lakehouse.get_status(),
        }
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_api_executor, _collect)


@app.post("/api/v1/ai-native/memory/archive")
async def archive_ai_native_memory(payload: MemoryArchiveRequest):
    """将 AI Native 记忆层事件归档为 Parquet。"""
    def _archive():
        return data_lakehouse.archive_events_to_parquet(
            output_path=payload.output_path,
            event_type=payload.event_type,
            limit=payload.limit,
        )
    loop = asyncio.get_event_loop()
    try:
        parquet_path = await loop.run_in_executor(_api_executor, _archive)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to archive events: {exc}")
    return {
        "status": "archived",
        "event_type": payload.event_type,
        "limit": payload.limit,
        "parquet_path": parquet_path,
    }


@app.post("/api/v1/ai-native/memory/analytics/query")
async def query_ai_native_memory_analytics(payload: MemoryAnalyticsQueryRequest):
    """基于 DuckDB 执行 AI Native 记忆层即席分析。"""
    def _query():
        return data_lakehouse.run_duckdb_query(
            payload.sql,
            parquet_path=payload.parquet_path,
            event_type=payload.event_type,
            limit=payload.limit,
        )
    loop = asyncio.get_event_loop()
    try:
        rows = await loop.run_in_executor(_api_executor, _query)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Analytics query failed: {exc}")
    return {
        "count": len(rows),
        "event_type": payload.event_type,
        "rows": rows,
    }


@app.post("/api/v1/ai-native/decision/feedback/log")
async def log_decision_feedback(payload: DecisionFeedbackRequest):
    """记录决策反馈并回写到 AI Native 记忆层。"""
    def _log():
        from channels.marine_base import get_default_registry
        registry = get_default_registry()
        orchestrator = registry.get("decision_orchestrator")
        if not orchestrator:
            return None
        feedback = orchestrator.record_feedback(payload.action, payload.outcome, payload.confirmed_by)
        return {
            "channel": "decision_orchestrator",
            "result": feedback,
            "feedback_records_count": len(getattr(orchestrator, "feedback_records", [])),
            "recent_feedback": data_lakehouse.query_events(event_type="decision_feedback_event", limit=10),
        }
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_api_executor, _log)
    if result is None:
        raise HTTPException(status_code=404, detail="Decision orchestrator not found")
    return result


@app.post("/api/v1/ai-native/openbridge/command")
async def execute_openbridge_command(payload: OpenBridgeCommandRequest):
    """将桥楼自然语言命令映射到任务图和控制状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    orchestrator = registry.get("decision_orchestrator")
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Decision orchestrator not found")

    dashboard = await get_dashboard()
    mission = await get_cps_mission_brief()
    result = build_openbridge_command_result(payload.command, dashboard, mission)
    feedback = orchestrator.record_feedback(
        action=f"openbridge:{result['recognized_intent']}",
        outcome=result["execution_mode"],
        confirmed_by=payload.source,
    )

    return {
        "source": payload.source,
        "result": result,
        "feedback": feedback,
    }

@app.post("/api/v1/bridge-chat/send")
async def bridge_chat_send(payload: BridgeChatRequest):
    """Handle bridge chat message — Navigator LLM first, template fallback.
    Creates a build_system task only when message explicitly requests it.
    """
    # Try LLM with selected agent first
    llm_result = await _navigator_llm_chat(payload.message, payload.session_id, agent_id=payload.agent_id)

    # Only create build_system task when message explicitly mentions build/PM/task delegation
    task_id = None
    msg_text = (payload.message or "").strip()
    _build_keywords = ["build团队", "Build团队", "build team", "PM发", "PM智能体", "开发任务", "开发团队",
                        "构建团队", "提交任务", "分配任务", "发一个任务", "创建任务", "新建任务"]
    _is_build_request = any(kw in msg_text for kw in _build_keywords)
    if _is_build_request and len(msg_text) >= 4:
        try:
            from agents.api import _te, _generate_workflow, _start_harness_monitor, _start_claude_session, _tm
            from agents.task_engine import AgentTask

            title = msg_text.split("\n")[0][:120]

            # ── 关键: 将 Captain Agent 的回话指令附加到任务描述 ──
            # LLM reply 中包含安全指令(SOLAS/ISM/IEC等)必须传递给PM
            task_description = msg_text
            if llm_result and llm_result.get("reply"):
                captain_reply = llm_result["reply"]
                task_description = (
                    f"{msg_text}\n\n"
                    f"---\n\n"
                    f"## Captain Agent 安全指令 (必须遵循)\n\n"
                    f"{captain_reply}\n"
                )

            engine = _te()
            if not engine._running:
                await engine.start()

            # Dedup: skip if identical title already exists in this session (pending/running)
            _dominated = False
            for _t in engine.get_team_tasks("build_system"):
                if (_t.title == title
                        and _t.status in ("pending", "running")
                        and _t.metadata.get("session_id") == payload.session_id):
                    task_id = _t.task_id
                    _dominated = True
                    break

            if not _dominated:
                task = AgentTask(
                    agent_id="build_pm",
                    team_id="build_system",
                    title=title,
                    description=task_description,
                    priority=2,
                    metadata={"source": "bridge_chat", "session_id": payload.session_id, "agent_id": payload.agent_id},
                )
                wf = _generate_workflow(task, "build_system")
                if wf:
                    task.metadata["workflow"] = wf
                await engine.submit_task(task)
                task_id = task.task_id
                # Auto-start the workflow with Claude Code CLI
                if wf:
                    import uuid as _uuid
                    from agents.api import _sr
                    first_step = wf[0]
                    if first_step.get("status") == "active" and first_step.get("agent_id"):
                        sr = _sr()
                        skill = sr.get_by_slug("code_implementation")
                        cfg = dict(skill.config or {}) if skill else {}
                        tm = _tm()
                        agent = tm.get_agent("build_system", first_step["agent_id"])
                        if agent:
                            from agents.api import _build_step_prompt
                            sid = str(_uuid.uuid4())[:12]
                            step_prompt = _build_step_prompt(task, first_step, wf)
                            _start_claude_session(sid, step_prompt, cfg, agent, task.task_id)
                            first_step["session_id"] = sid
                            task.metadata["workflow"] = wf
                    await engine.start_task(task.task_id)
                    _start_harness_monitor(task.task_id, "build_system")
                logger.info(f"[BridgeChat] Created task {task_id}: {title[:40]}")
            else:
                logger.info(f"[BridgeChat] Dedup: reusing existing task {task_id}")
        except Exception as e:
            logger.warning(f"[BridgeChat] Failed to auto-create task: {e}")

    # Also check LLM reply for task-routing intent (LLM may promise to forward
    # even when user message didn't contain build keywords)
    if llm_result and not task_id:
        _reply_text = (llm_result.get("reply") or "")
        _reply_task_kw = ["转达给build", "转发给build", "提交给build", "Build团队PM",
                          "build团队PM", "转达给PM", "任务已创建", "任务已提交",
                          "转达给开发", "转发给开发", "通知build", "分配给build"]
        if any(kw in _reply_text for kw in _reply_task_kw):
            try:
                from agents.api import _te
                from agents.task_engine import AgentTask

                title = msg_text.split("\n")[0][:120] if msg_text else "Bridge Chat Task"
                engine = _te()
                if not engine._running:
                    await engine.start()

                # ── 同样附加 Captain Agent 的回话指令到 LLM-route 任务 ──
                llm_route_desc = msg_text
                if _reply_text:
                    llm_route_desc = (
                        f"{msg_text}\n\n"
                        f"---\n\n"
                        f"## Captain Agent 安全指令 (必须遵循)\n\n"
                        f"{_reply_text}\n"
                    )

                task = AgentTask(
                    agent_id="build_pm",
                    team_id="build_system",
                    title=title,
                    description=llm_route_desc,
                    priority=2,
                    metadata={"source": "bridge_chat_llm_route", "session_id": payload.session_id,
                              "agent_id": payload.agent_id},
                )
                await engine.submit_task(task)
                task_id = task.task_id
                logger.info(f"[BridgeChat] LLM-routed task {task_id}: {title[:40]}")
            except Exception as e:
                logger.warning(f"[BridgeChat] LLM-route task creation failed: {e}")

    if llm_result:
        if task_id:
            llm_result["task_id"] = task_id
        return llm_result

    # Fallback to template-based bridge_chat channel
    try:
        from channels.marine_base import get_default_registry

        registry = get_default_registry()
        chat_ch = registry.get("bridge_chat")
        if not chat_ch:
            return {"reply": "Bridge Chat channel 未注册，请检查后端配置。", "urgency": "normal", "source": "error"}

        result = await chat_ch.process_event({
            "type": "chat_message",
            "message": payload.message,
            "session_id": payload.session_id,
            "lang": payload.lang,
        })
        result["source"] = "bridge_chat_template"
        if task_id:
            result["task_id"] = task_id
    except Exception as e:
        logger.warning(f"[BridgeChat] Template fallback failed: {e}")
        return {"reply": f"系统暂时无法处理请求: {str(e)[:100]}", "urgency": "normal", "source": "error"}
    return result


@app.get("/api/v1/bridge-chat/history")
async def bridge_chat_history(session_id: str = "default", limit: int = 20):
    """Get chat history."""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    chat_ch = registry.get("bridge_chat")
    if not chat_ch:
        raise HTTPException(status_code=404, detail="Bridge Chat channel not found")
    
    return {"session_id": session_id, "messages": chat_ch.get_session_history(session_id, limit)}


@app.delete("/api/v1/bridge-chat/session/{session_id}")
async def bridge_chat_clear_session(session_id: str = PathParam(..., min_length=1, max_length=100)):
    """Clear chat session."""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    chat_ch = registry.get("bridge_chat")
    if not chat_ch:
        raise HTTPException(status_code=404, detail="Bridge Chat channel not found")
    
    chat_ch.clear_session(session_id)
    return {"status": "ok", "session_id": session_id}


@app.get("/api/v1/bridge-chat/status")
async def bridge_chat_status():
    """Get Bridge Chat channel status."""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    chat_ch = registry.get("bridge_chat")
    if not chat_ch:
        raise HTTPException(status_code=404, detail="Bridge Chat channel not found")
    
    return chat_ch.get_status()


@app.get("/api/v1/ai-native/weather-routing/status")
async def get_ai_native_weather_routing_status():
    """获取气象导航状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("weather_routing")
    if not channel:
        raise HTTPException(status_code=404, detail="Weather routing channel not found")
    return {"channel": "weather_routing", "result": channel.get_status()}


@app.get("/api/v1/ai-native/crew/fatigue-status")
async def get_ai_native_crew_fatigue_status():
    """获取船员疲劳监测状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("crew_fatigue")
    if not channel:
        raise HTTPException(status_code=404, detail="Crew fatigue monitor not found")
    return {"channel": "crew_fatigue", "result": channel.get_status()}


@app.get("/api/v1/ai-native/weather-routing/recommendations")
async def get_ai_native_weather_routing_recommendations():
    """获取气象导航建议列表。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("weather_routing")
    if not channel:
        raise HTTPException(status_code=404, detail="Weather routing channel not found")
    recommendations = channel.generate_weather_recommendations()
    return {"channel": "weather_routing", "recommendations": recommendations}


@app.get("/api/weather-routing/grid")
async def get_weather_routing_grid():
    """获取天气网格数据。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("weather_routing")
    if not channel:
        raise HTTPException(status_code=404, detail="Weather routing channel not found")
    return {"channel": "weather_routing", "result": channel.get_weather_grid()}


@app.get("/api/compass/status")
async def get_compass_status():
    """获取电罗经监控状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("gyro_compass_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Gyro compass monitor channel not found")
    return {"channel": "gyro_compass_monitor", "result": channel.get_heading_consensus()}


@app.get("/api/speed-log/status")
async def get_speed_log_status():
    """获取计程仪监控状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("speed_log_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Speed log monitor channel not found")
    return {"channel": "speed_log_monitor", "result": channel.get_speed_consensus()}


@app.get("/api/v1/ai-native/anchor/status")
async def get_ai_native_anchor_status():
    """获取锚泊监控状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("anchor_watch")
    if not channel:
        raise HTTPException(status_code=404, detail="Anchor watch channel not found")
    return {"channel": "anchor_watch", "result": channel.get_status()}


@app.get("/api/v1/ai-native/crew/recommendations")
async def get_ai_native_crew_recommendations():
    """获取船员疲劳建议列表。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("crew_fatigue")
    if not channel:
        raise HTTPException(status_code=404, detail="Crew fatigue monitor not found")
    recommendations = channel.get_fatigue_recommendations()
    return {"channel": "crew_fatigue", "recommendations": recommendations}


@app.get("/api/v1/ai-native/cargo/status")
async def get_ai_native_cargo_status():
    """获取货物监控状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("cargo_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Cargo monitor channel not found")
    return {"channel": "cargo_monitor", "result": channel.get_status()}


@app.get("/api/v1/ai-native/fire/status")
async def get_ai_native_fire_status():
    """获取火灾探测状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("fire_detection")
    if not channel:
        raise HTTPException(status_code=404, detail="Fire detection channel not found")
    return {"channel": "fire_detection", "result": channel.get_status()}


@app.get("/api/vdr/status")
async def get_vdr_status():
    """获取 VDR 录制状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("vdr_recorder")
    if not channel:
        raise HTTPException(status_code=404, detail="VDR recorder channel not found")
    return {"channel": "vdr_recorder", "result": channel.get_recording_status()}


@app.get("/api/vdr/integrity")
async def get_vdr_integrity():
    """获取 VDR 数据完整性检查。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("vdr_recorder")
    if not channel:
        raise HTTPException(status_code=404, detail="VDR recorder channel not found")
    return {"channel": "vdr_recorder", "result": channel.verify_data_integrity()}


@app.get("/api/dp/status")
async def get_dp_status():
    """获取动态定位状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("dynamic_positioning")
    if not channel:
        raise HTTPException(status_code=404, detail="DP channel not found")
    return {"channel": "dynamic_positioning", "result": channel.get_status()}


class SetStationRequest(BaseModel):
    lat: float
    lon: float
    heading: float = 0.0


@app.post("/api/dp/set-station")
async def set_dp_station(payload: SetStationRequest):
    """设定 DP 目标站位。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("dynamic_positioning")
    if not channel:
        raise HTTPException(status_code=404, detail="DP channel not found")
    result = channel.set_station(payload.lat, payload.lon, payload.heading)
    return {"channel": "dynamic_positioning", "result": result}


@app.get("/api/ais/targets")
async def get_ais_targets():
    """获取所有活跃 AIS 目标。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("ais_processor")
    if not channel:
        raise HTTPException(status_code=404, detail="AIS processor channel not found")
    return {"channel": "ais_processor", "targets": channel.get_target_table()}


@app.get("/api/ais/target/{mmsi}")
async def get_ais_target(mmsi: int = PathParam(..., ge=0, le=999999999)):
    """查询单个 AIS 目标。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("ais_processor")
    if not channel:
        raise HTTPException(status_code=404, detail="AIS processor channel not found")
    target = channel.get_target(mmsi)
    if target is None:
        raise HTTPException(status_code=404, detail=f"Target MMSI {mmsi} not found")
    return {"channel": "ais_processor", "target": target}


@app.get("/api/hull/status")
async def get_hull_status():
    """获取船体结构健康状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("hull_stress_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Hull stress monitor channel not found")
    return {"channel": "hull_stress_monitor", "result": channel.get_structural_health()}


@app.get("/api/hull/fatigue")
async def get_hull_fatigue():
    """获取船体疲劳评估。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("hull_stress_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Hull stress monitor channel not found")
    return {"channel": "hull_stress_monitor", "result": channel.get_fatigue_assessment()}


@app.get("/api/power/status")
async def get_power_status():
    """获取电力平衡状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("power_management")
    if not channel:
        raise HTTPException(status_code=404, detail="Power management channel not found")
    return {"channel": "power_management", "result": channel.get_power_balance()}


@app.get("/api/power/efficiency")
async def get_power_efficiency():
    """获取燃油效率分析。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("power_management")
    if not channel:
        raise HTTPException(status_code=404, detail="Power management channel not found")
    return {"channel": "power_management", "result": channel.get_fuel_efficiency()}


@app.get("/api/bilge/status")
async def get_bilge_status():
    """获取舱底水状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("bilge_water_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Bilge water monitor channel not found")
    return {"channel": "bilge_water_monitor", "result": channel.get_bilge_status()}


@app.get("/api/bilge/compliance")
async def get_bilge_compliance():
    """获取 MARPOL 合规状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("bilge_water_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Bilge water monitor channel not found")
    return {"channel": "bilge_water_monitor", "result": channel.check_marpol_compliance()}


@app.get("/api/comms/status")
async def get_comms_status():
    """获取通信系统状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("communication_manager")
    if not channel:
        raise HTTPException(status_code=404, detail="Communication manager channel not found")
    return {"channel": "communication_manager", "result": channel.get_comms_status()}


@app.get("/api/rudder/status")
async def get_rudder_status():
    """获取舵机综合状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("rudder_control_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Rudder control monitor channel not found")
    return {"channel": "rudder_control_monitor", "result": channel.get_steering_status()}


@app.get("/api/tanks/summary")
async def get_tanks_summary():
    """获取液舱综合摘要。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("tank_level_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Tank level monitor channel not found")
    return {"channel": "tank_level_monitor", "result": channel.get_tank_summary()}


@app.get("/api/tanks/fuel-endurance")
async def get_fuel_endurance():
    """获取燃油续航估算。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("tank_level_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Tank level monitor channel not found")
    return {"channel": "tank_level_monitor", "result": channel.estimate_fuel_endurance()}


@app.get("/api/alarms/active")
async def get_active_alarms_api():
    """获取所有活跃告警。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("alarm_management")
    if not channel:
        raise HTTPException(status_code=404, detail="Alarm management channel not found")
    return {"channel": "alarm_management", "alarms": channel.get_active_alarms()}


@app.get("/api/alarms/summary")
async def get_alarms_summary():
    """获取告警摘要。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("alarm_management")
    if not channel:
        raise HTTPException(status_code=404, detail="Alarm management channel not found")
    return {"channel": "alarm_management", "result": channel.get_alarm_summary()}


@app.get("/api/autopilot/status")
async def get_autopilot_status():
    """获取自动舵状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("autopilot_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Autopilot monitor channel not found")
    return {"channel": "autopilot_monitor", "result": channel.get_autopilot_status()}


@app.get("/api/depth/status")
async def get_depth_status():
    """获取测深仪状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("echo_sounder_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Echo sounder monitor channel not found")
    return {"channel": "echo_sounder_monitor", "result": channel.get_depth_status()}


@app.get("/api/propulsion/status")
async def get_propulsion_status():
    """获取推进系统状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("propulsion_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Propulsion monitor channel not found")
    return {"channel": "propulsion_monitor", "result": channel.get_propulsion_status()}


@app.get("/api/propulsion/engine/{engine_id}")
async def get_engine_health(engine_id: str = PathParam(..., min_length=1, max_length=100)):
    """获取单台主机健康评估。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("propulsion_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Propulsion monitor channel not found")
    result = channel.get_engine_health(engine_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"channel": "propulsion_monitor", "result": result}


# ==================== K-TCS Thruster Control System API ====================

_tcs_state = {
    "mode": "individual",  # individual / auto_crossing / dp_mode
    "pitch_mode": "fixed",  # fixed / controllable / feathering
    "emergency_stop": False,
    "thrusters": {
        "bow_tunnel": {
            "id": "bow_tunnel", "name": "Bow Tunnel Thruster", "type": "tunnel",
            "position": "fore", "azimuth_deg": 90, "azimuth_set": 90,
            "rpm": 0, "rpm_max": 1450, "power_kw": 0, "power_max": 1500,
            "load_pct": 0, "torque_nm": 0, "pitch_deg": 0,
            "motor_type": "permanent_magnet", "polar_class": "PC6",
            "status": "standby", "clutch": "disengaged",
            "temp_motor": 42.0, "temp_bearing": 38.5,
            "vibration_mm_s": 0.8, "hydraulic_bar": 220,
        },
        "stern_azimuth": {
            "id": "stern_azimuth", "name": "Stern Azimuth Thruster", "type": "azimuth",
            "position": "aft", "azimuth_deg": 180, "azimuth_set": 180,
            "rpm": 0, "rpm_max": 1200, "power_kw": 0, "power_max": 2500,
            "load_pct": 0, "torque_nm": 0, "pitch_deg": 0,
            "motor_type": "permanent_magnet", "polar_class": "PC6",
            "status": "standby", "clutch": "disengaged",
            "temp_motor": 40.0, "temp_bearing": 36.2,
            "vibration_mm_s": 0.6, "hydraulic_bar": 225,
        },
        "port_main": {
            "id": "port_main", "name": "Port Main Propulsion", "type": "main",
            "position": "aft_port", "azimuth_deg": 180, "azimuth_set": 180,
            "rpm": 185, "rpm_max": 250, "power_kw": 7820, "power_max": 10000,
            "load_pct": 78, "torque_nm": 40350, "pitch_deg": 22,
            "motor_type": "permanent_magnet", "polar_class": "PC6",
            "status": "running", "clutch": "engaged",
            "temp_motor": 68.5, "temp_bearing": 52.3,
            "vibration_mm_s": 2.1, "hydraulic_bar": 235,
        },
        "stbd_main": {
            "id": "stbd_main", "name": "Starboard Main Propulsion", "type": "main",
            "position": "aft_stbd", "azimuth_deg": 180, "azimuth_set": 180,
            "rpm": 183, "rpm_max": 250, "power_kw": 7680, "power_max": 10000,
            "load_pct": 77, "torque_nm": 40080, "pitch_deg": 22,
            "motor_type": "permanent_magnet", "polar_class": "PC6",
            "status": "running", "clutch": "engaged",
            "temp_motor": 67.2, "temp_bearing": 51.8,
            "vibration_mm_s": 1.9, "hydraulic_bar": 232,
        },
    },
    "controllers": {
        "A": {"status": "active", "heartbeat": True, "cpu_pct": 12},
        "B": {"status": "standby", "heartbeat": True, "cpu_pct": 5},
        "C": {"status": "standby", "heartbeat": True, "cpu_pct": 4},
    },
    "power_split": {"fore_pct": 0, "aft_pct": 100},
    "battery": {"soc_pct": 87, "voltage": 690, "current_a": 42, "status": "charging"},
    "efficiency_pct": 94.2,
    "space_saved_pct": 30,
}

import random as _rnd

def _tcs_simulate_tick():
    """Simulate small telemetry fluctuations."""
    for tid, t in _tcs_state["thrusters"].items():
        if t["status"] == "running":
            t["rpm"] = max(0, t["rpm"] + _rnd.randint(-2, 2))
            t["power_kw"] = max(0, int(t["power_max"] * (t["rpm"] / max(1, t["rpm_max"])) + _rnd.randint(-50, 50)))
            t["load_pct"] = min(100, max(0, round(t["power_kw"] / max(1, t["power_max"]) * 100)))
            t["torque_nm"] = int(t["power_kw"] * 9549 / max(1, t["rpm"]))
            t["temp_motor"] += _rnd.uniform(-0.3, 0.3)
            t["temp_bearing"] += _rnd.uniform(-0.2, 0.2)
            t["vibration_mm_s"] = round(max(0.1, t["vibration_mm_s"] + _rnd.uniform(-0.1, 0.1)), 1)
            t["hydraulic_bar"] = max(180, min(260, t["hydraulic_bar"] + _rnd.randint(-2, 2)))
            # Azimuth drift sim
            diff = t["azimuth_set"] - t["azimuth_deg"]
            if abs(diff) > 0.5:
                t["azimuth_deg"] += diff * 0.3
    _tcs_state["efficiency_pct"] = round(max(80, min(99, _tcs_state["efficiency_pct"] + _rnd.uniform(-0.3, 0.3))), 1)
    _tcs_state["battery"]["soc_pct"] = max(10, min(100, _tcs_state["battery"]["soc_pct"] + _rnd.choice([-1, 0, 0, 0, 1])))


@app.get("/api/v1/tcs/status")
async def tcs_status():
    """K-TCS full system status with simulated telemetry."""
    _tcs_simulate_tick()
    return _tcs_state


@app.post("/api/v1/tcs/mode")
async def tcs_set_mode(payload: Dict[str, Any] = Body(...)):
    """Set control mode: individual / auto_crossing / dp_mode."""
    mode = payload.get("mode", "individual")
    if mode not in ("individual", "auto_crossing", "dp_mode"):
        raise HTTPException(status_code=400, detail="Invalid mode")
    _tcs_state["mode"] = mode
    if mode == "auto_crossing":
        _tcs_state["power_split"] = {"fore_pct": 15, "aft_pct": 85}
    elif mode == "dp_mode":
        _tcs_state["power_split"] = {"fore_pct": 40, "aft_pct": 60}
    else:
        _tcs_state["power_split"] = {"fore_pct": 0, "aft_pct": 100}
    return {"mode": mode, "power_split": _tcs_state["power_split"]}


@app.post("/api/v1/tcs/pitch")
async def tcs_set_pitch(payload: Dict[str, Any] = Body(...)):
    """Set pitch mode: fixed / controllable / feathering."""
    pitch = payload.get("pitch_mode", "fixed")
    if pitch not in ("fixed", "controllable", "feathering"):
        raise HTTPException(status_code=400, detail="Invalid pitch mode")
    _tcs_state["pitch_mode"] = pitch
    return {"pitch_mode": pitch}


@app.post("/api/v1/tcs/azimuth")
async def tcs_set_azimuth(payload: Dict[str, Any] = Body(...)):
    """Set azimuth angle for a thruster."""
    tid = payload.get("thruster_id", "")
    angle = payload.get("angle", 0)
    if tid not in _tcs_state["thrusters"]:
        raise HTTPException(status_code=404, detail="Thruster not found")
    _tcs_state["thrusters"][tid]["azimuth_set"] = angle % 360
    return {"thruster_id": tid, "azimuth_set": angle % 360}


@app.post("/api/v1/tcs/emergency")
async def tcs_emergency(payload: Dict[str, Any] = Body(...)):
    """Emergency stop toggle."""
    stop = payload.get("stop", True)
    _tcs_state["emergency_stop"] = stop
    if stop:
        for t in _tcs_state["thrusters"].values():
            t["rpm"] = 0
            t["power_kw"] = 0
            t["load_pct"] = 0
            t["torque_nm"] = 0
            t["status"] = "emergency_stop"
            t["clutch"] = "disengaged"
    return {"emergency_stop": stop}


@app.post("/api/v1/tcs/thruster")
async def tcs_thruster_control(payload: Dict[str, Any] = Body(...)):
    """Start/stop/edit an individual thruster or add a new one."""
    action = payload.get("action", "")  # start, stop, edit, add, remove
    tid = payload.get("thruster_id", "")

    if action == "add":
        name = payload.get("name", tid.replace("_", " ").title())
        t_type = payload.get("type", "main")
        position = payload.get("position", "aft")
        rpm_max = int(payload.get("rpm_max", 250))
        power_max = int(payload.get("power_max", 10000))
        _tcs_state["thrusters"][tid] = {
            "id": tid, "name": name, "type": t_type,
            "position": position, "azimuth_deg": 180, "azimuth_set": 180,
            "rpm": 0, "rpm_max": rpm_max, "power_kw": 0, "power_max": power_max,
            "load_pct": 0, "torque_nm": 0, "pitch_deg": 0,
            "motor_type": payload.get("motor_type", "permanent_magnet"),
            "polar_class": payload.get("polar_class", "PC6"),
            "status": "standby", "clutch": "disengaged",
            "temp_motor": 35.0, "temp_bearing": 32.0,
            "vibration_mm_s": 0.5, "hydraulic_bar": 220,
        }
        return {"ok": True, "action": "add", "thruster_id": tid}

    if tid not in _tcs_state["thrusters"]:
        raise HTTPException(status_code=404, detail="Thruster not found")
    t = _tcs_state["thrusters"][tid]

    if action == "start":
        rpm_target = int(payload.get("rpm", t["rpm_max"] * 0.74))
        t["status"] = "running"
        t["clutch"] = "engaged"
        t["rpm"] = min(rpm_target, t["rpm_max"])
        t["power_kw"] = int(t["power_max"] * (t["rpm"] / max(1, t["rpm_max"])))
        t["load_pct"] = round(t["power_kw"] / max(1, t["power_max"]) * 100)
        t["torque_nm"] = int(t["power_kw"] * 9549 / max(1, t["rpm"]))
        return {"ok": True, "action": "start", "thruster_id": tid, "rpm": t["rpm"], "load_pct": t["load_pct"]}

    elif action == "stop":
        t["status"] = "standby"
        t["clutch"] = "disengaged"
        t["rpm"] = 0
        t["power_kw"] = 0
        t["load_pct"] = 0
        t["torque_nm"] = 0
        return {"ok": True, "action": "stop", "thruster_id": tid}

    elif action == "edit":
        for k in ("name", "rpm_max", "power_max", "motor_type", "polar_class", "type", "position"):
            if k in payload:
                t[k] = payload[k]
        if "rpm" in payload and t["status"] == "running":
            t["rpm"] = min(int(payload["rpm"]), t["rpm_max"])
            t["power_kw"] = int(t["power_max"] * (t["rpm"] / max(1, t["rpm_max"])))
            t["load_pct"] = round(t["power_kw"] / max(1, t["power_max"]) * 100)
            t["torque_nm"] = int(t["power_kw"] * 9549 / max(1, t["rpm"]))
        return {"ok": True, "action": "edit", "thruster_id": tid}

    elif action == "remove":
        del _tcs_state["thrusters"][tid]
        return {"ok": True, "action": "remove", "thruster_id": tid}

    raise HTTPException(status_code=400, detail="Unknown action: " + action)


@app.get("/api/mooring/status")
async def get_mooring_status():
    """获取系泊状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("mooring_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Mooring monitor channel not found")
    return {"channel": "mooring_monitor", "result": channel.get_mooring_status()}


@app.get("/api/mob/status")
async def get_mob_status():
    """获取 MOB 落水告警状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("man_overboard")
    if not channel:
        raise HTTPException(status_code=404, detail="Man overboard channel not found")
    return {"channel": "man_overboard", "result": channel.get_mob_status()}


class MOBActivateRequest(BaseModel):
    lat: float
    lon: float


@app.post("/api/mob/activate")
async def activate_mob(req: MOBActivateRequest):
    """激活 MOB 落水告警。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("man_overboard")
    if not channel:
        raise HTTPException(status_code=404, detail="Man overboard channel not found")
    return {"channel": "man_overboard", "result": channel.activate_mob(req.lat, req.lon)}


@app.post("/api/mob/deactivate")
async def deactivate_mob():
    """取消 MOB 落水告警。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("man_overboard")
    if not channel:
        raise HTTPException(status_code=404, detail="Man overboard channel not found")
    return {"channel": "man_overboard", "result": channel.deactivate_mob()}


@app.get("/api/safety/status")
async def get_safety_status():
    """获取安全系统综合状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("safety_system_monitor")
    if not channel:
        raise HTTPException(status_code=404, detail="Safety system monitor channel not found")
    return {"channel": "safety_system_monitor", "result": channel.get_safety_status()}


@app.get("/api/lrit/status")
async def get_lrit_status():
    """获取 LRIT 报告状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("lrit_reporter")
    if not channel:
        raise HTTPException(status_code=404, detail="LRIT reporter channel not found")
    return {"channel": "lrit_reporter", "result": channel.get_status()}


@app.get("/api/lrit/history")
async def get_lrit_history():
    """获取 LRIT 报告历史。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("lrit_reporter")
    if not channel:
        raise HTTPException(status_code=404, detail="LRIT reporter channel not found")
    return {"channel": "lrit_reporter", "history": channel.get_report_history()}


@app.get("/api/lights/status")
async def get_lights_status():
    """获取航行灯配置状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("navigational_lights")
    if not channel:
        raise HTTPException(status_code=404, detail="Navigational lights channel not found")
    return {"channel": "navigational_lights", "result": channel.get_light_configuration()}


@app.get("/api/lights/compliance")
async def get_lights_compliance():
    """获取航行灯 COLREG 合规状态。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("navigational_lights")
    if not channel:
        raise HTTPException(status_code=404, detail="Navigational lights channel not found")
    return {"channel": "navigational_lights", "result": channel.check_colreg_compliance()}


@app.get("/api/voyage/kpi")
async def get_voyage_kpi():
    """获取航次 KPI 数据。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("voyage_data_analyzer")
    if not channel:
        raise HTTPException(status_code=404, detail="Voyage data analyzer channel not found")
    return {"channel": "voyage_data_analyzer", "result": channel.get_voyage_kpi()}


@app.get("/api/maintenance/summary")
async def get_maintenance_summary():
    """获取维修计划汇总。"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    channel = registry.get("maintenance_planner")
    if not channel:
        raise HTTPException(status_code=404, detail="Maintenance planner channel not found")
    return {"channel": "maintenance_planner", "result": channel.get_maintenance_summary()}


@app.get("/api/overview")
async def get_system_overview():
    """系统综合概览 - 一次获取所有模块状态"""
    from channels.marine_base import get_default_registry

    registry = get_default_registry()
    overview = {"timestamp": datetime.now().isoformat(), "channels": {}}
    for name in registry.list_channels():
        channel = registry.get(name)
        if channel:
            try:
                overview["channels"][name] = channel.get_status()
            except Exception:
                overview["channels"][name] = {"status": "error"}
    overview["total_channels"] = len(overview["channels"])
    return overview



@app.get("/api/v1/agent-sets/status")
async def agent_sets_status():
    """Return aggregated status of both agent sets and coordination bus."""
    try:
        from channels.marine_base import get_default_registry
        registry = get_default_registry()
        coordinator = registry.get("agent_set_coordinator")
        if coordinator:
            return JSONResponse(coordinator.full_status())
        return JSONResponse({"error": "Agent-set coordinator not registered"}, status_code=404)
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.get("/api/v1/agent-sets/{set_id}/status")
async def agent_set_detail(set_id: str = PathParam(..., min_length=1, max_length=100)):
    """Return status of a specific agent set (shore or ship)."""
    try:
        from channels.marine_base import get_default_registry
        registry = get_default_registry()
        name = "shore_supervision_set" if set_id == "shore" else "shipboard_execution_set"
        agent_set = registry.get(name)
        if agent_set:
            return JSONResponse(agent_set.get_status())
        return JSONResponse({"error": f"Agent set '{set_id}' not found"}, status_code=404)
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.post("/api/v1/agent-sets/relay")
async def trigger_relay_cycle():
    """Manually trigger one coordination relay cycle."""
    try:
        from channels.marine_base import get_default_registry
        registry = get_default_registry()
        coordinator = registry.get("agent_set_coordinator")
        if coordinator:
            result = coordinator.relay_cycle()
            return JSONResponse(result)
        return JSONResponse({"error": "Agent-set coordinator not registered"}, status_code=404)
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 连接"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"📡 WebSocket client connected. Total: {len(active_connections)}")

    # 连接建立后立即推送一帧，减少前端首屏等待。
    await sim_engine.broadcast_update()
    
    try:
        while True:
            # 接收客户端消息 (订阅/取消订阅)
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "subscribe":
                channel = message.get("channel")
                logger.info(f"Client subscribed to: {channel}")
            elif message.get("action") == "unsubscribe":
                channel = message.get("channel")
                logger.info(f"Client unsubscribed from: {channel}")
    
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"📡 WebSocket client disconnected. Total: {len(active_connections)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)



# ==================== Cross-Team Task Routing ====================

async def _maybe_create_cross_team_task(reply: str, agent_id: str, original_message: str) -> None:
    """Detect task delegation intent in LLM reply and auto-create task in target team.

    When an execution_system agent (e.g. Captain) mentions delegating work to
    the build team (PM, Developer, etc.), automatically submit a real task to
    the build_system TaskEngine so it appears in the build team's task list.
    """
    import re
    try:
        from agents.api import _team_manager
        from agents.task_engine import AgentTask, get_task_engine
    except ImportError:
        return

    if not _team_manager:
        return

    # Only trigger for execution_system agents
    source_team_id = None
    for team in _team_manager.list_teams():
        if team.get_agent(agent_id):
            source_team_id = team.team_id
            break
    if source_team_id != "execution_system":
        return

    # Detect delegation keywords targeting build team
    build_keywords = [
        "PM智能体", "PM", "build", "开发任务", "开发团队",
        "构建团队", "Developer", "Researcher", "Architect", "Tester",
        "提交任务", "分配任务", "传达", "转发", "发送至",
    ]
    has_delegation = any(kw in reply for kw in build_keywords)
    if not has_delegation:
        return

    # Verify build_system team exists
    build_team = _team_manager.get_team("build_system")
    if not build_team:
        return

    # Extract task title from reply — look for **title** pattern or first sentence
    title_match = re.search(r'\*\*(.+?)\*\*', reply)
    if title_match:
        title = title_match.group(1)[:128]
    else:
        # Use first meaningful line as title
        lines = [l.strip() for l in reply.split('\n') if l.strip() and len(l.strip()) > 5]
        title = lines[0][:128] if lines else original_message[:128]

    # Determine target agent — default to PM
    target_agent_id = "build_pm"
    agent_map = {
        "Developer": "build_developer", "Researcher": "build_researcher",
        "Architect": "build_architect", "Tester": "build_tester",
        "Doc Writer": "build_doc_writer", "Deployer": "build_deployer",
    }
    for name, aid in agent_map.items():
        if name in reply and build_team.get_agent(aid):
            target_agent_id = aid
            break

    # Determine priority
    priority = 2  # normal
    if any(kw in reply for kw in ["紧急", "高优先", "critical", "urgent"]):
        priority = 1
    elif any(kw in reply for kw in ["非航行", "低优先", "low"]):
        priority = 3

    # Create task in build_system TaskEngine
    engine = get_task_engine()
    if not engine._running:
        await engine.start()

    task = AgentTask(
        agent_id=target_agent_id,
        team_id="build_system",
        title=title,
        description=f"[跨团队任务] 来源: {agent_id}\n\n用户原始消息: {original_message}\n\nAgent 回复摘要: {reply[:500]}",
        priority=priority,
        metadata={
            "source_team": "execution_system",
            "source_agent": agent_id,
            "cross_team": True,
            "original_message": original_message,
        },
    )
    await engine.submit_task(task)
    logger.info("Cross-team task created: %s → build_system/%s (task_id=%s)",
                agent_id, target_agent_id, task.task_id)


# ==================== Navigator LLM Chat ====================

async def _navigator_llm_chat(message: str, session_id: str = "default", agent_id: str = "ship_navigator") -> Optional[Dict[str, Any]]:
    """Try to chat via the selected agent + LLM.

    Returns a dict with {reply, urgency, source, ...} on success, or None if LLM unavailable.
    Falls back to None so callers can use the template-based bridge_chat channel.
    """
    try:
        from agents.chat_harness import get_chat_harness
        from agents.api import _team_manager
    except ImportError:
        return None

    harness = get_chat_harness()

    # Resolve agent profile for system prompt
    agent_prompt = ""
    agent_name = agent_id
    if _team_manager:
        for team in _team_manager.list_teams():
            agent = team.get_agent(agent_id)
            if agent:
                agent_prompt = agent.system_prompt or ""
                agent_name = agent.name or agent_id
                break

    # Build real-time ship context for the system prompt
    ship = sim_engine.ship_position
    ctx_lines = []
    if agent_prompt:
        ctx_lines.append(agent_prompt)
    else:
        ctx_lines.append(f"你是 PoseidonX 系统的智能体 {agent_name}。")
    ctx_lines.append("回答时使用中文，简洁专业。")
    ctx_lines.append("")
    ctx_lines.append(f"== 当前船舶状态 ==")
    ctx_lines.append(f"位置: {ship['lat']:.4f}°N, {ship['lon']:.4f}°E")
    ctx_lines.append(f"航向: {sim_engine.ship_course:.1f}°T")
    ctx_lines.append(f"航速: {sim_engine.ship_speed:.1f} kn")

    # AIS targets
    if ais_targets:
        ctx_lines.append(f"\n== AIS 目标 ({len(ais_targets)} 艘) ==")
        for mmsi, t in list(ais_targets.items())[:10]:
            ctx_lines.append(
                f"  MMSI {mmsi}: {t.latitude:.4f}°N {t.longitude:.4f}°E, "
                f"COG {t.course:.0f}°, SOG {t.speed:.1f} kn"
            )

    # Alarms
    active_alarms = [a for a in alarms if a.level in ("danger", "warning")]
    if active_alarms:
        ctx_lines.append(f"\n== 活跃告警 ({len(active_alarms)} 条) ==")
        for a in active_alarms[-5:]:
            ctx_lines.append(f"  [{a.level}] {a.message}")

    system_prompt = "\n".join(ctx_lines)

    try:
        result = await harness.chat(
            message,
            agent_id=agent_id,
            session_id=f"nav_llm_{session_id}",
            system_prompt=system_prompt,
        )
        if result.error:
            logger.debug("Navigator LLM returned error, falling back: %s", result.error[:100])
            return None

        reply = result.response.strip()
        if not reply:
            return None

        # Determine urgency from content
        urgency = "normal"
        danger_keywords = ["紧急", "危险", "碰撞", "告警", "MOB", "MAYDAY", "emergency", "collision"]
        if any(kw in reply.lower() for kw in danger_keywords):
            urgency = "critical"

        # Note: cross-team task routing removed — bridge_chat_send creates
        # the task directly, no need for duplicate detection from LLM reply.

        return {
            "reply": reply,
            "urgency": urgency,
            "source": "agent_llm",
            "agent_id": agent_id,
            "agent_name": agent_name,
            "model": result.model,
            "provider": result.provider,
            "latency_ms": round(result.latency_ms, 1),
            "session_id": session_id,
        }
    except Exception as exc:
        logger.debug("Navigator LLM chat failed: %s", exc)
        return None


@app.websocket("/ws/navigation")
async def ws_navigation(websocket: WebSocket):
    """Navigation page WebSocket."""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"Navigation WS connected. Total: {len(active_connections)}")

    try:
        init_data = {
            "type": "init",
            "ship": {
                "lat": sim_engine.ship_position["lat"],
                "lon": sim_engine.ship_position["lon"],
                "hdg": sim_engine.ship_course,
                "sog": sim_engine.ship_speed,
                "cog": sim_engine.ship_course + 0.4,
            },
            "ais": [
                {
                    "mmsi": mmsi,
                    "lat": t.latitude,
                    "lon": t.longitude,
                    "cog": t.course,
                    "sog": t.speed,
                    "name": f"TARGET-{mmsi[-3:]}",
                }
                for mmsi, t in ais_targets.items()
            ],
            "alarms": [
                {"level": a.level, "message": a.message, "time": a.timestamp}
                for a in alarms[-10:]
            ],
        }
        await websocket.send_json(init_data)
    except Exception as e:
        logger.warning(f"Nav WS init send failed: {e}")

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            action = data.get("action", "")

            if action == "chat":
                msg_text = data.get("message", "")
                sid = data.get("session_id", "default")
                agent_id = data.get("agent_id", "ship_navigator")
                # Try LLM with selected agent first
                llm_result = await _navigator_llm_chat(msg_text, sid, agent_id=agent_id)
                if llm_result:
                    await websocket.send_json({"type": "chat_reply", **llm_result})
                else:
                    # Fallback to template-based bridge_chat
                    from channels.marine_base import get_default_registry
                    registry = get_default_registry()
                    chat_ch = registry.get("bridge_chat")
                    if chat_ch:
                        result = await chat_ch.process_event({
                            "type": "chat_message",
                            "message": msg_text,
                            "session_id": sid,
                        })
                        result["source"] = "bridge_chat_template"
                        await websocket.send_json({"type": "chat_reply", **result})

            elif action == "subscribe":
                logger.info(f"Nav WS: subscribe to {data.get('channel')}")

    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.info(f"Navigation WS disconnected. Total: {len(active_connections)}")
    except Exception as e:
        logger.error(f"Navigation WS error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


# ==================== Shore & Sim WebSocket ====================

@app.websocket("/ws/shore")
async def ws_shore(websocket: WebSocket):
    """Ship-shore communication WebSocket — fleet positions, comms link status."""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"Shore WS connected. Total: {len(active_connections)}")
    try:
        from channels.marine_base import get_default_registry
        registry = get_default_registry()
        comms_ch = registry.get("ship_shore_comms")
        init_payload = {"type": "init", "link_status": "connected", "timestamp": datetime.now().isoformat()}
        if comms_ch:
            try:
                status = comms_ch.get_status()
                init_payload["comms"] = status
            except Exception:
                pass
        await websocket.send_json(init_payload)
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            action = msg.get("action", "")
            if action == "send_command":
                await websocket.send_json({
                    "type": "command_ack",
                    "command": msg.get("command", ""),
                    "status": "received",
                    "timestamp": datetime.now().isoformat(),
                })
            elif action == "subscribe":
                logger.info(f"Shore WS: subscribe to {msg.get('channel')}")
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.info(f"Shore WS disconnected. Total: {len(active_connections)}")
    except Exception as e:
        logger.error(f"Shore WS error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


@app.websocket("/ws/sim")
async def ws_sim(websocket: WebSocket):
    """Simulation / training WebSocket — scenario events, fault injection feedback."""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"Sim WS connected. Total: {len(active_connections)}")
    try:
        await websocket.send_json({
            "type": "init",
            "scenario": "standby",
            "timestamp": datetime.now().isoformat(),
        })
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            action = msg.get("action", "")
            if action == "inject_fault":
                await websocket.send_json({
                    "type": "fault_ack",
                    "fault": msg.get("fault_type", "unknown"),
                    "severity": msg.get("severity", "medium"),
                    "status": "injected",
                    "timestamp": datetime.now().isoformat(),
                })
            elif action == "start_scenario":
                await websocket.send_json({
                    "type": "scenario_started",
                    "scenario": msg.get("scenario", "default"),
                    "timestamp": datetime.now().isoformat(),
                })
            elif action == "subscribe":
                logger.info(f"Sim WS: subscribe to {msg.get('channel')}")
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.info(f"Sim WS disconnected. Total: {len(active_connections)}")
    except Exception as e:
        logger.error(f"Sim WS error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


# ==================== 健康检查 ====================

@app.get("/health")
async def health_check():
    """健康检查 — 轻量级，不调用任何阻塞操作"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "connections": len(active_connections),
        "sensors": len(sensor_cache),
        "ais_targets": len(ais_targets),
        "alarms": len(alarms),
        "ai_native": coordination_status,
    }

# ==================== API Extensions ====================

# 导入并注册海事服务 API 端点（页面对接）
try:
    from api_marine_services import router as marine_services_router
    app.include_router(marine_services_router)
    logger.info("✅ Marine Services API 端点注册成功")
except ImportError as e:
    logger.warning(f"⚠️ 未能导入 Marine Services API 端点: {e}")
except Exception as e:
    logger.error(f"❌ Marine Services API 端点注册失败: {e}")

# 导入并注册 AI Native API 端点
try:
    from api_extensions import register_ai_native_endpoints
    register_ai_native_endpoints(app)
    logger.info("✅ AI Native API 端点注册成功")
except ImportError as e:
    logger.warning(f"⚠️ 未能导入 AI Native API 端点: {e}")
except Exception as e:
    logger.error(f"❌ AI Native API 端点注册失败: {e}")

# 导入并注册 Token Factory（自主 Token 工厂）
try:
    from token_factory import TokenFactory, register_token_factory_routes
    register_token_factory_routes(app)
except ImportError as e:
    logger.warning(f"⚠️ 未能导入 Token Factory: {e}")
except Exception as e:
    logger.error(f"❌ Token Factory 注册失败: {e}")

# ======================= 前端静态文件 (moved to startup, see start_poseidon_services) ========================

# ==================== 主程序 ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Poseidon Server")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=8080, help="HTTP 端口")
    parser.add_argument("--ws-port", type=int, default=8765, help="WebSocket 端口 (未使用)")
    
    args = parser.parse_args()
    
    logger.info(f"🌐 Starting server on {args.host}:{args.port}")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info",
    )
