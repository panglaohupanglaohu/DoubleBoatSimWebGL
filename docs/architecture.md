# 🏗️ 系统架构文档

**版本**: 1.0.0  
**日期**: 2026-03-13 19:00  
**作者**: Sovereign (首席架构师)

---

## 1. 总体架构

### 1.1 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户交互层 (Frontend)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Digital Twin Dashboard (Three.js + HTML5)          │   │
│  │  - 3D 双体船模型渲染                                   │   │
│  │  - 实时数据叠加显示                                    │   │
│  │  - 报警可视化                                         │   │
│  │  - 鼠标交互 (旋转/缩放)                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ↕ HTTP/WebSocket                   │
├─────────────────────────────────────────────────────────────┤
│                    数据处理层 (Backend)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Poseidon Server (FastAPI + Python)                 │   │
│  │  ┌──────────────┐  ┌──────────────┐                │   │
│  │  │ REST API     │  │ WebSocket    │                │   │
│  │  │ - /api/v1/*  │  │ - /ws        │                │   │
│  │  │ - 传感器数据  │  │ - 实时推送    │                │   │
│  │  │ - AIS 目标    │  │ - 订阅管理    │                │   │
│  │  │ - 主机状态    │  │              │                │   │
│  │  └──────────────┘  └──────────────┘                │   │
│  │  ┌──────────────┐  ┌──────────────┐                │   │
│  │  │ Simulation   │  │ Alarm        │                │   │
│  │  │ Engine       │  │ Engine       │                │   │
│  │  │ - AIS 模拟    │  │ - 阈值检测    │                │   │
│  │  │ - NMEA 模拟   │  │ - 报警生成    │                │   │
│  │  │ - 传感器模拟  │  │ - 报警管理    │                │   │
│  │  └──────────────┘  └──────────────┘                │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ↕ 内存存储                         │
├─────────────────────────────────────────────────────────────┤
│                    数据存储层 (In-Memory)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Sensor Cache │  │ AIS Targets  │  │ Alarms       │    │
│  │ (Dict)       │  │ (Dict)       │  │ (List)       │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 组件关系

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│  FastAPI    │────▶│ Simulation  │
│   (Three.js)│◀────│   Server    │◀────│   Engine    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  WebSocket  │────▶│   Alarm     │────▶│   Memory    │
│   Client    │◀────│   Engine    │◀────│   Store     │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## 2. 核心模块设计

### 2.1 前端模块

#### 2.1.1 Three.js 渲染引擎

**职责**:
- 3D 场景管理 (Scene, Camera, Renderer)
- 双体船模型渲染
- 水面效果模拟
- 鼠标交互控制

**核心类**:
```javascript
class DigitalTwinRenderer {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(...);
        this.renderer = new THREE.WebGLRenderer(...);
    }
    
    createCatamaran() { /* 创建双体船模型 */ }
    createWater() { /* 创建水面 */ }
    animate() { /* 渲染循环 */ }
}
```

#### 2.1.2 WebSocket 客户端

**职责**:
- 连接后端 WebSocket 服务器
- 订阅数据更新
- 实时更新 UI

**核心方法**:
```javascript
function connectWebSocket() {
    ws = new WebSocket('ws://localhost:8081/ws');
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateUI(data.data);
    };
}
```

#### 2.1.3 UI 组件

**组件列表**:
- `StatusBar` - 顶部状态栏 (连接状态/时间)
- `DataPanel` - 左侧数据面板 (导航/主机数据)
- `AlarmPanel` - 右侧报警面板
- `AisPanel` - 底部 AIS 目标列表

---

### 2.2 后端模块

#### 2.2.1 FastAPI 服务器

**职责**:
- REST API 端点
- WebSocket 连接管理
- 仿真数据生成
- 报警检测

**核心端点**:
```python
@app.get("/")              # 根路径
@app.get("/health")        # 健康检查
@app.get("/api/v1/sensors")          # 传感器列表
@app.get("/api/v1/ais/targets")      # AIS 目标
@app.get("/api/v1/engine/status")    # 主机状态
@app.get("/api/v1/alerts")           # 报警列表
@app.websocket("/ws")                # WebSocket 连接
```

#### 2.2.2 仿真引擎

**职责**:
- 生成 AIS 目标数据
- 生成 NMEA 传感器数据
- 生成主机工况数据
- 检测报警条件

**核心类**:
```python
class SimulationEngine:
    def __init__(self):
        self.ship_position = {"lat": 31.2304, "lon": 121.4737}
        self.ais_targets = {...}  # 5 个模拟目标
        self.engine = {...}       # 主机参数
    
    async def generate_sensor_data(self):
        while self.running:
            # 更新位置
            # 更新 AIS 目标
            # 更新主机状态
            # 检查报警
            # 广播更新
            await asyncio.sleep(0.1)
```

#### 2.2.3 报警引擎

**职责**:
- 阈值检测
- 报警生成
- 报警分级 (INFO/WARNING/CRITICAL/EMERGENCY)
- 报警确认

**报警规则**:
```python
# 冷却水温度高
if engine_temp > 85.0:
    create_alarm("WARNING", "ENGINE", "Cooling water temperature high")

# 滑油压力低
if lube_oil_pressure < 4.0:
    create_alarm("CRITICAL", "ENGINE", "Lube oil pressure low")
```

---

### 2.3 数据模型

#### 2.3.1 传感器数据

```python
class SensorData(BaseModel):
    sensor_id: str          # 传感器 ID
    sensor_type: str        # 传感器类型 (GPS/COMPASS/LOG)
    value: float            # 测量值
    unit: str               # 单位
    timestamp: str          # 时间戳
    quality: str = "good"   # 数据质量
```

#### 2.3.2 AIS 目标

```python
class AISTarget(BaseModel):
    mmsi: str               # MMSI 编码
    latitude: float         # 纬度
    longitude: float        # 经度
    course: float           # 航向
    speed: float            # 航速
    heading: float          # 船首向
    vessel_type: str        # 船舶类型
    cpa: Optional[float]    # 最近会遇距离
    tcpa: Optional[float]   # 最近会遇时间
```

#### 2.3.3 主机状态

```python
class EngineStatus(BaseModel):
    engine_id: str                  # 主机 ID
    rpm: float                      # 转速
    load: float                     # 负载
    cooling_water_temp: float       # 冷却水温度
    lube_oil_pressure: float        # 滑油压力
    fuel_consumption: float         # 燃油消耗
    status: str                     # 运行状态
    alarms: List[str] = []          # 报警列表
```

#### 2.3.4 报警

```python
class Alarm(BaseModel):
    alarm_id: str           # 报警 ID
    level: str              # 报警级别
    source: str             # 报警来源
    message: str            # 报警消息
    timestamp: str          # 时间戳
    acknowledged: bool      # 是否已确认
```

---

## 3. 数据流设计

### 3.1 实时数据流

```
Simulation Engine
    │
    │ (生成数据)
    ▼
Memory Store (sensor_cache, ais_targets, engine_status)
    │
    │ (广播)
    ▼
WebSocket Server
    │
    │ (推送)
    ▼
WebSocket Client (Browser)
    │
    │ (更新 UI)
    ▼
Three.js Renderer + Data Panels
```

### 3.2 报警处理流

```
Simulation Engine
    │
    │ (检测阈值)
    ▼
Alarm Engine
    │
    │ (创建报警)
    ▼
Alarms List
    │
    │ (广播)
    ▼
WebSocket Clients
    │
    │ (显示报警)
    ▼
Alarm Panel (UI)
```

### 3.3 用户交互流

```
User (Mouse/Keyboard)
    │
    │ (旋转/缩放)
    ▼
Three.js Event Handlers
    │
    │ (更新相机)
    ▼
Camera Position
    │
    │ (渲染)
    ▼
WebGL Renderer
    │
    │ (显示)
    ▼
Canvas
```

---

## 4. 性能设计

### 4.1 性能指标

| 指标 | 目标值 | 实测值 |
|------|--------|--------|
| 数据更新延迟 | < 100ms | ~100ms |
| 界面刷新频率 | ≥ 10Hz | 60fps |
| WebSocket 连接数 | ≥ 10 | 未测试 |
| 并发传感器 | ≥ 50 | 仿真中 |

### 4.2 优化策略

1. **数据推送优化**
   - 使用 WebSocket 代替轮询
   - 只推送变化的数据
   - 限制推送频率 (10Hz)

2. **渲染优化**
   - 使用 LOD (Level of Detail)
   - 减少 Draw Calls
   - 使用 Instanced Rendering

3. **内存优化**
   - 限制缓存大小
   - 定期清理旧数据
   - 使用对象池

---

## 5. 安全设计

### 5.1 网络安全

- CORS 配置 (允许所有来源 - 开发环境)
- WebSocket 连接验证
- API 限流 (待实现)

### 5.2 数据安全

- 输入验证 (Pydantic 模型)
- 异常处理
- 日志记录

### 5.3 待实现的安全功能

- [ ] 用户认证 (JWT)
- [ ] 访问控制 (RBAC)
- [ ] 数据加密 (TLS)
- [ ] 审计日志

---

## 6. 扩展性设计

### 6.1 水平扩展

- 无状态设计 (易于多实例部署)
- 内存存储 → Redis (共享状态)
- WebSocket 连接 → 负载均衡

### 6.2 垂直扩展

- 模块化设计 (易于添加新功能)
- 插件式 Channel (易于接入新数据源)
- 配置驱动 (易于调整参数)

### 6.3 未来扩展方向

1. **数据源扩展**
   - NMEA2000 支持
   - Modbus TCP 支持
   - OPC-UA 支持

2. **功能扩展**
   - PHM 模块
   - 自然语言交互
   - 多链路管理

3. **部署扩展**
   - Docker 容器化
   - Kubernetes 编排
   - 云端部署

---

## 7. 部署架构

### 7.1 开发环境

```
┌─────────────────┐
│  Developer PC   │
│  ┌───────────┐  │
│  │ Frontend  │  │
│  │ (Vite)    │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │ Backend   │  │
│  │ (FastAPI) │  │
│  └───────────┘  │
└─────────────────┘
```

### 7.2 生产环境 (规划)

```
┌─────────────────┐
│  Load Balancer  │
│    (Nginx)      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│ App 1 │ │ App 2 │  (FastAPI 集群)
└───┬───┘ └──┬────┘
    │         │
    └────┬────┘
         │
    ┌────▼────┐
    │  Redis  │  (共享状态)
    └─────────┘
```

---

## 8. 监控与运维

### 8.1 监控指标

- API 响应时间
- WebSocket 连接数
- 数据更新延迟
- 报警数量
- CPU/内存使用率

### 8.2 日志策略

- INFO: 正常操作日志
- WARNING: 警告信息
- ERROR: 错误信息
- DEBUG: 调试信息 (开发环境)

### 8.3 故障恢复

- 自动重连 (WebSocket)
- 数据缓存 (断线续传)
- 健康检查 (自动重启)

---

**架构文档完成！** 🎉
