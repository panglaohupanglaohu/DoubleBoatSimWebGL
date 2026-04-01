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

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Path as PathParam
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
        
        # 初始船舶状态
        self.ship_position = {"lat": 31.2304, "lon": 121.4737}
        self.ship_course = 135.0
        self.ship_speed = 12.3
        
        # 初始 AIS 目标 (模拟 5 艘船)
        self.ais_targets = {
            "123456789": {"lat": 31.25, "lon": 121.50, "course": 225.0, "speed": 10.0},
            "234567890": {"lat": 31.20, "lon": 121.45, "course": 315.0, "speed": 8.5},
            "345678901": {"lat": 31.28, "lon": 121.42, "course": 90.0, "speed": 12.0},
            "456789012": {"lat": 31.18, "lon": 121.52, "course": 180.0, "speed": 15.0},
            "567890123": {"lat": 31.26, "lon": 121.48, "course": 45.0, "speed": 9.0},
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
                vessel_type="Cargo",
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
        while self.running:
            try:
                # 更新船舶位置 (模拟移动)
                dt = 1  # 1s
                self.ship_position["lat"] += 0.0001 * (self.ship_speed / 10)
                self.ship_position["lon"] += 0.0001 * (self.ship_speed / 10)
                
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
                }
                
                # 更新缓存
                sensor_cache.update(sensor_data)
                
                # 更新 AIS 目标位置
                for mmsi, target in self.ais_targets.items():
                    target["lat"] += 0.00005 * (target["speed"] / 10)
                    target["lon"] += 0.00005 * (target["speed"] / 10)
                    
                    ais_targets[mmsi] = AISTarget(
                        mmsi=mmsi,
                        latitude=target["lat"],
                        longitude=target["lon"],
                        course=target["course"],
                        speed=target["speed"],
                        heading=target["course"],
                        vessel_type="Cargo",
                        cpa=0.5,  # 模拟 CPA
                        tcpa=300.0,  # 模拟 TCPA (秒)
                    )
                
                # 更新主机状态 (带一点波动)
                import random
                self.engine["rpm"] = 120.0 + random.uniform(-2, 2)
                self.engine["load"] = 75.0 + random.uniform(-3, 3)
                self.engine["cooling_water_temp"] = 82.0 + random.uniform(-1, 1)
                self.engine["lube_oil_pressure"] = 4.5 + random.uniform(-0.1, 0.1)
                
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
        if not active_connections:
            return
        
        message = json.dumps({
            "type": "data_update",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "sensors": {k: v.model_dump() for k, v in sensor_cache.items()},
                "ais_targets": {k: v.model_dump() for k, v in ais_targets.items()},
                "engine": engine_status.model_dump() if engine_status else None,
                "alarms": [a.model_dump() for a in alarms[-10:]],  # 最近 10 个报警
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
        set_teams(build_team, execution_team, agent_team_scheduler)
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

        config_team_manager = TeamManager()
        build_team_obj = create_build_team()
        config_team_manager._teams[build_team_obj.team_id] = build_team_obj
        exec_team_obj = create_execution_team()
        config_team_manager._teams[exec_team_obj.team_id] = exec_team_obj

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
    _frontend_dir = BASE_DIR / "src" / "frontend"
    if _frontend_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")
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

@app.get("/api/v1/alerts")
async def get_alerts():
    """获取报警列表"""
    return {"alerts": [a.model_dump() for a in alarms]}


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

# 导入并注册 AI Native API 端点
try:
    from api_extensions import register_ai_native_endpoints
    register_ai_native_endpoints(app)
    logger.info("✅ AI Native API 端点注册成功")
except ImportError as e:
    logger.warning(f"⚠️ 未能导入 AI Native API 端点: {e}")
except Exception as e:
    logger.error(f"❌ AI Native API 端点注册失败: {e}")

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
