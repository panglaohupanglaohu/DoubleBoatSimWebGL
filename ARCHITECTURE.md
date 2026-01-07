# 船舶数字孪生系统 - 技术架构文档

## 📋 项目概述

**目标**：实现全船三维可视化查看、船内外数据实时显示、安全态势汇总显示、船岸孪生交互以及多场景模拟预演的智能可视化平台。

## 🏗️ 系统架构

### 核心模块划分

```
DoubleBoatDT/
├── src/
│   ├── core/                          # 核心系统
│   │   ├── Application.js             # 主应用程序类
│   │   ├── SceneManager.js            # 场景管理器
│   │   └── CameraController.js        # 摄像机控制器
│   │
│   ├── physics/                       # 物理模拟系统
│   │   ├── PhysicsWorld.js            # 物理世界管理
│   │   ├── SimulatorEngine.js         # 模拟器引擎（可插拔）
│   │   └── algorithms/                # 模拟算法库
│   │       ├── BuoyancyAlgorithm.js   # 浮力算法
│   │       ├── WindAlgorithm.js       # 风力算法
│   │       ├── RainAlgorithm.js       # 降雨算法
│   │       └── WaveAlgorithm.js       # 波浪算法
│   │
│   ├── weather/                       # 天气系统
│   │   ├── WeatherSystem.js           # 天气系统管理
│   │   ├── WindSimulator.js           # 风力模拟器
│   │   ├── RainSimulator.js           # 降雨模拟器
│   │   └── SeaStateSimulator.js       # 海况模拟器
│   │
│   ├── ship/                          # 船舶系统
│   │   ├── ShipModel.js               # 船舶模型
│   │   ├── CabinSystem.js             # 舱室系统
│   │   ├── EquipmentSystem.js         # 设备系统
│   │   └── cabins/                    # 舱室定义
│   │       ├── PartsWarehouse.js      # 零部件仓库
│   │       ├── DataCenter.js          # 数据中心
│   │       └── AccommodationCabin.js  # 住宿舱室
│   │
│   ├── data/                          # 数据系统
│   │   ├── DataInterfaceManager.js    # 数据接口管理器
│   │   ├── VirtualDataSource.js       # 虚拟数据源
│   │   ├── GraphQLClient.js           # GraphQL客户端
│   │   └── DataSyncManager.js         # 数据同步管理器
│   │
│   ├── monitoring/                    # 监控系统
│   │   ├── RealtimeMonitor.js         # 实时监控
│   │   ├── SafetyMonitor.js           # 安全态势监控
│   │   ├── indicators/                # 指标定义
│   │   │   ├── FuelIndicator.js       # 燃油指标
│   │   │   ├── EquipmentIndicator.js  # 设备指标
│   │   │   └── PersonnelIndicator.js  # 人员指标
│   │   └── visualizers/               # 可视化组件
│   │       ├── HUDDisplay.js          # HUD显示
│   │       ├── Gauge.js               # 仪表盘
│   │       └── StatusPanel.js         # 状态面板
│   │
│   ├── scenario/                      # 场景预演系统
│   │   ├── ScenarioEngine.js          # 场景引擎
│   │   ├── FirstPersonController.js   # 第一人称控制器
│   │   ├── PathfindingSystem.js       # 路径规划系统
│   │   └── scenarios/                 # 场景定义
│   │       ├── RainstormLeakage.js    # 暴雨漏水场景
│   │       └── TyphoonScenario.js     # 台风场景
│   │
│   ├── sync/                          # 船岸同步系统
│   │   ├── ShipShoreSyncManager.js    # 船岸同步管理器
│   │   ├── DataCompressor.js          # 数据压缩器
│   │   ├── PriorityQueue.js           # 优先级队列
│   │   └── BatchTransmitter.js        # 批次传输器
│   │
│   ├── ui/                            # UI系统
│   │   ├── UIManager.js               # UI管理器
│   │   ├── ConfigPanel.js             # 配置面板
│   │   ├── DataInterfaceEditor.js     # 数据接口编辑器
│   │   └── ScenarioPanel.js           # 场景控制面板
│   │
│   └── utils/                         # 工具库
│       ├── EventEmitter.js            # 事件发射器
│       ├── Logger.js                  # 日志系统
│       └── MathUtils.js               # 数学工具
│
├── public/
│   ├── models/                        # 3D模型
│   │   ├── ship/                      # 船舶模型
│   │   ├── equipment/                 # 设备模型
│   │   └── environment/               # 环境模型
│   └── config/                        # 配置文件
│       ├── ship-config.json           # 船舶配置
│       ├── equipment-config.json      # 设备配置
│       └── scenario-config.json       # 场景配置
│
└── index.html                         # 入口文件
```

## 🔧 核心技术方案

### 1. 模拟器引擎（可插拔架构）

```javascript
// 算法接口定义
interface ISimulationAlgorithm {
  name: string;
  priority: number;
  initialize(config): void;
  update(deltaTime, shipState, environment): ForceResult;
  dispose(): void;
}

// 力结果定义
interface ForceResult {
  force: Vector3;      // 作用力
  torque: Vector3;     // 力矩
  metadata: any;       // 元数据
}
```

**特点**：
- 算法可动态添加/移除
- 支持优先级排序
- 每个算法独立计算，最后合并结果

### 2. 天气系统与船体交互

**天气影响模型**：
- 风力 → 侧向力、横摇力矩
- 降雨 → 视野影响、甲板积水（重量增加）
- 海况 → 波浪力、俯仰/横摇力矩

### 3. 舱室系统与场景切换

**舱室定义**：
```javascript
interface Cabin {
  id: string;
  name: string;
  type: 'warehouse' | 'datacenter' | 'accommodation';
  bounds: BoundingBox;
  camera: CameraConfig;
  objects: GameObject[];
  interactable: boolean;
}
```

**切换策略**：
- 平滑相机过渡（Tween动画）
- LOD（细节层次）管理
- 遮挡剔除优化

### 4. 数据接口配置系统

**可视化连线方案**：
- 使用节点编辑器（类似 Blueprint）
- 数据源节点 ↔ 数据处理节点 ↔ 可视化节点
- 支持 GraphQL、REST API、WebSocket

**GraphQL Schema 示例**：
```graphql
type Ship {
  id: ID!
  name: String!
  fuel: FuelData!
  equipment: [Equipment!]!
  environment: EnvironmentData!
}

type FuelData {
  level: Float!        # 0-100%
  flowRate: Float!     # L/h
  remaining: Float!    # L
  timestamp: DateTime!
}
```

### 5. 第一人称视角系统

**功能**：
- WASD 移动、鼠标视角控制
- 碰撞检测
- 路径规划与导航提示
- 交互系统（检查、维修）

### 6. 船岸数据同步

**批次传输策略**：

**批次1 - 静态数据**（低频，5分钟）：
- 船体结构数据
- 设备配置
- 人员配置

**批次2 - 动态数据**（高频，1秒）：
- 位置姿态
- 传感器数据
- 设备状态

**优先级策略**：
```
P0（紧急）：报警、故障 → 立即发送
P1（重要）：关键设备状态 → 5秒内发送
P2（正常）：常规监控数据 → 批次发送
P3（低优）：日志、统计 → 压缩后发送
```

## 📊 数据流架构

```
[真实传感器] → [数据采集层] → [数据接口管理器] 
                                      ↓
                               [虚拟数据源]（开发阶段）
                                      ↓
                          [数据处理层（过滤、转换）]
                                      ↓
                          [数据分发层（订阅模式）]
                                      ↓
           ┌─────────────────────────┼─────────────────────────┐
           ↓                         ↓                         ↓
    [实时监控系统]            [安全态势系统]            [场景预演系统]
           ↓                         ↓                         ↓
    [可视化渲染层]                                      [船岸同步系统]
```

## 🎯 实施计划

### Phase 1：核心重构（Week 1-2）
1. ✅ 重构模拟器引擎为可插拔架构
2. ✅ 实现天气系统（风、雨）
3. ✅ 天气对船体的影响算法

### Phase 2：舱室与数据系统（Week 3-4）
4. 构建舱室系统和场景切换
5. 设计数据接口配置系统
6. 实现虚拟数据源

### Phase 3：监控与可视化（Week 5-6）
7. 实时数据显示系统
8. 安全态势监控系统
9. HUD 和可视化组件

### Phase 4：场景预演（Week 7-8）
10. 第一人称控制器
11. 路径规划系统
12. 暴雨漏水场景实现

### Phase 5：船岸同步（Week 9-10）
13. 数据压缩和优先级管理
14. 批次传输系统
15. 船岸双向同步

### Phase 6：集成与优化（Week 11-12）
16. UI 整合
17. 性能优化
18. 测试与文档

## 🛠️ 技术栈

- **渲染**：Three.js r165
- **物理**：Cannon-es 0.20.0
- **UI**：lil-gui + 自定义 HTML/CSS
- **数据通信**：GraphQL + WebSocket
- **状态管理**：事件驱动架构
- **路径规划**：A* 算法
- **数据压缩**：MessagePack / Protobuf

## 📈 性能目标

- 渲染帧率：≥60 FPS（桌面）、≥30 FPS（移动）
- 物理模拟：60Hz 固定时间步长
- 数据延迟：船岸同步 < 500ms
- 场景切换：< 1秒过渡动画

## 🔐 安全考虑

- 数据传输加密（TLS）
- 数据接口访问控制
- 敏感数据脱敏
- 操作日志审计

