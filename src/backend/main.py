#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DoubleBoatClawSystem Backend - Poseidon Server

FastAPI + WebSocket 实时数据推送服务
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

from adapters.worldmonitor_adapter import WorldMonitorAdapter
from adapters.worldmonitor_adapter_real import WorldMonitorRealAdapter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("PoseidonServer")

# 创建 FastAPI 应用
app = FastAPI(
    title="DoubleBoatClawSystem API",
    description="Digital Twin API for Deep-Sea Scientific Facilities",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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

# ==================== 内存数据存储 ====================

# 传感器数据缓存
sensor_cache: Dict[str, SensorData] = {}

# AIS 目标
ais_targets: Dict[str, AISTarget] = {}

# 主机状态
engine_status: Optional[EngineStatus] = None

# 报警列表
alarms: List[Alarm] = []

# WebSocket 连接
active_connections: List[WebSocket] = []

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
    
    async def generate_sensor_data(self):
        """生成传感器数据"""
        while self.running:
            try:
                # 更新船舶位置 (模拟移动)
                dt = 0.1  # 100ms
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
            logger.warning(f"🚨 Alarm created: {level} - {message}")
    
    async def broadcast_update(self):
        """广播数据更新到所有 WebSocket 连接"""
        if not active_connections:
            return
        
        message = json.dumps({
            "type": "data_update",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "sensors": {k: v.dict() for k, v in sensor_cache.items()},
                "ais_targets": {k: v.dict() for k, v in ais_targets.items()},
                "engine": engine_status.dict() if engine_status else None,
                "alarms": [a.dict() for a in alarms[-10:]],  # 最近 10 个报警
            }
        })
        
        # 异步发送给所有连接
        disconnected = []
        for conn in active_connections:
            try:
                await conn.send_text(message)
            except Exception:
                disconnected.append(conn)
        
        # 清理断开的连接
        for conn in disconnected:
            active_connections.remove(conn)
    
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

# ==================== API 路由 ====================

@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("🚀 Starting Poseidon Server...")
    sim_engine.start()
    asyncio.create_task(sim_engine.generate_sensor_data())
    
    # 注册 Marine Channels
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from register_channels import (
            register_energy_efficiency_channel,
            register_intelligent_navigation,
            register_intelligent_engine,
            register_compliance_digital_expert,
            register_distributed_perception_hub,
            register_decision_orchestrator,
        )
        register_energy_efficiency_channel()
        register_intelligent_navigation()
        register_intelligent_engine()
        register_compliance_digital_expert()
        register_distributed_perception_hub()
        register_decision_orchestrator()
        logger.info("✅ Marine Channels registered")
    except Exception as e:
        logger.warning(f"⚠️ Channel registration skipped: {e}")
    
    logger.info("✅ Poseidon Server started")

@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    sim_engine.stop()
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
    
    channels = []
    for name in registry.list_channels():
        channel = registry.get(name)
        if channel:
            status = channel.get_status()
            channels.append({
                "name": name,
                "description": channel.description,
                "version": status.get("version", "1.0.0"),
                "health": status.get("health", "unknown"),
                "initialized": status.get("initialized", False),
                "status": status,
            })
    
    return {"channels": channels}


@app.post("/api/v1/channels/{channel_name}/query")
async def query_channel(channel_name: str, payload: dict):
    """查询 Channel 数据，用于 Bridge Chat/前端联动。"""
    from channels.marine_base import get_default_registry
    registry = get_default_registry()
    channel = registry.get(channel_name)
    if not channel:
        raise HTTPException(status_code=404, detail=f"Channel '{channel_name}' not found")

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
        return {"channel": channel_name, "result": channel.build_decision_package(), "status": channel.get_status()}

    if channel_name == "distributed_perception_hub" and hasattr(channel, "get_latest_events"):
        return {"channel": channel_name, "result": {"latest_events": channel.get_latest_events(20)}, "status": channel.get_status()}

    return {"channel": channel_name, "result": channel.get_status(), "status": channel.get_status()}

@app.get("/api/v1/sensors")
async def get_sensors():
    """获取传感器列表"""
    return {
        "sensors": [
            {"id": "GPS-001", "type": "GPS", "description": "GPS 接收机"},
            {"id": "COMPASS-001", "type": "COMPASS", "description": "罗经"},
            {"id": "LOG-001", "type": "SPEED_LOG", "description": "计程仪"},
            {"id": "ECHO-001", "type": "ECHO_SOUNDER", "description": "测深仪"},
        ]
    }

@app.get("/api/v1/sensors/{sensor_id}/data")
async def get_sensor_data(sensor_id: str):
    """获取传感器数据"""
    if sensor_id not in sensor_cache:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor_cache[sensor_id]

@app.get("/api/v1/ais/targets")
async def get_ais_targets():
    """获取 AIS 目标"""
    return {"targets": [t.dict() for t in ais_targets.values()]}

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
        raise HTTPException(status_code=404, detail="Engine status not available")
    return engine_status

@app.get("/api/v1/alerts")
async def get_alerts():
    """获取报警列表"""
    return {"alerts": [a.dict() for a in alarms]}


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
async def get_worldmonitor_weather(lat: float, lng: float):
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
async def get_worldmonitor_ports(region: Optional[str] = None):
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
async def get_worldmonitor_routes(origin_port: Optional[str] = None, dest_port: Optional[str] = None):
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

    nav = registry.get("intelligent_navigation")
    engine = registry.get("intelligent_engine")
    efficiency = registry.get("energy_efficiency")
    compliance = registry.get("compliance_digital_expert")
    perception = registry.get("distributed_perception_hub")
    orchestrator = registry.get("decision_orchestrator")

    nav_status = nav.get_status() if nav else {}
    nav_report = nav.generate_navigation_report() if nav and hasattr(nav, "generate_navigation_report") else {}
    engine_status = engine.get_status() if engine else {}
    eff_status = efficiency.get_status() if efficiency else {}

    efficiency_summary = {
        "health": eff_status.get("health"),
        "health_message": eff_status.get("health_message"),
        "vessel": eff_status.get("vessel"),
        "recommendations_count": len(getattr(efficiency, "get_recommendations", lambda: [])()) if efficiency else 0,
    }

    return {
        "navigation": {
            "own_ship": nav_status.get("own_ship", {}),
            "report": nav_report,
        },
        "engine": {
            "health_score": engine_status.get("engine_health_score"),
            "alerts": engine_status.get("alerts", []),
            "latest": engine_status.get("latest_snapshot"),
            "trend": engine_status.get("trend", {}),
            "maintenance_advice": engine.get_maintenance_advice() if engine and hasattr(engine, "get_maintenance_advice") else [],
        },
        "efficiency": efficiency_summary,
        "compliance": compliance.query_compliance_status("overall") if compliance and hasattr(compliance, "query_compliance_status") else {},
        "perception": perception.get_status() if perception else {},
        "decision": orchestrator.build_decision_package() if orchestrator and hasattr(orchestrator, "build_decision_package") else {},
        "worldmonitor": {
            "mode": "connected" if worldmonitor_real else worldmonitor.mode,
            "enabled": worldmonitor_real is not None,
            "status": "ready" if worldmonitor_real else "placeholder",
            "data_source": "real" if worldmonitor_real else "mock",
            "last_update": datetime.now().isoformat() if worldmonitor_real else None,
            "endpoints": {
                "ais": "/api/v1/worldmonitor/ais",
                "weather": "/api/v1/worldmonitor/weather?lat=<lat>&lng=<lng>",
                "ports": "/api/v1/worldmonitor/ports",
                "routes": "/api/v1/worldmonitor/routes",
            },
        },
        "channels": [
            {
                "name": c["name"],
                "health": c["health"],
                "description": c["description"],
            }
            for c in (await get_channels())["channels"]
        ]
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 连接"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"📡 WebSocket client connected. Total: {len(active_connections)}")
    
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
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "connections": len(active_connections),
        "sensors": len(sensor_cache),
        "ais_targets": len(ais_targets),
        "alarms": len(alarms),
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
