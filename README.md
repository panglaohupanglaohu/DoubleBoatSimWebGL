# 🚢 船舶数字孪生系统 | Ship Digital Twin System

一个基于 WebGL 的船舶数字孪生可视化平台，实现全船三维可视化、物理模拟、实时数据监控、安全态势分析和场景预演等功能。

A WebGL-based ship digital twin visualization platform featuring 3D visualization, physics simulation, real-time data monitoring, safety analysis, and scenario simulation.

---

## 🆕 最新更新 | Latest Updates (v3.1.0 - 2025-01-05)

### 🔧 渲染稳定性增强 | Rendering Stability

- **PreRenderValidator（预渲染验证器）**：
  - 主动扫描并修复所有材质的 uniform 问题
  - 使用 JavaScript Proxy 拦截 uniform 访问，确保所有值有效
  - 自动为缺失或无效的 uniform 提供默认值
  - 每帧验证，确保动态材质修改不会导致渲染错误

- **ThreeJSPatch（Three.js补丁）**：
  - 增强 Three.js 核心函数的错误处理
  - 拦截并修复潜在的 uniform 错误
  - 防止 `Cannot read properties of undefined (reading 'value')` 错误

- **透明材质支持**：
  - 完全支持透明玻璃材质（60%-86%透明度）
  - 正确处理 `MeshPhysicalMaterial` 和 `MeshStandardMaterial`
  - 优化透明物体的深度写入、混合模式和渲染顺序
  - 增强光照系统，确保透明物体在各种缩放级别都清晰可见

### 🎛️ GUI同步优化 | GUI Synchronization

- **天气预设同步**：
  - 天气预设切换时，所有GUI控件自动更新显示值
  - 使用 `updateDisplay()` 方法确保GUI与内部状态同步
  - 支持风速、风向、降雨/降雪强度、温度等参数的实时同步

- **降雨/降雪控制**：
  - 修复降雨/降雪强度设为0时仍显示的问题
  - 粒子系统可见性与强度值正确绑定
  - 温度影响降雪转换为降雨的逻辑

### 📡 MQTT传感器集成 | MQTT Sensor Integration

- **MQTTDataSource（MQTT数据源）**：
  - 完整的MQTT客户端实现（基于 Paho MQTT）
  - 支持WebSocket连接到MQTT broker
  - 自动重连机制（5秒间隔）
  - 模拟模式：当MQTT不可用时自动生成模拟数据

- **传感器数据结构**：
  - GPS定位（经纬度、速度、航向）
  - IMU姿态传感器（横摇、纵摇、艏摇、加速度）
  - 气象站（温度、湿度、气压、风速、风向）
  - 主机参数（转速、功率、温度、油压）
  - 燃油系统（油位、流量、温度、压力）
  - 舵机系统（舵角、液压压力、电机电流）
  - 推进系统（推力、螺距、效率）
  - 结构监测（应力、挠度、振动）
  - 电力系统（电压、电流、频率、功率因数）
  - 应急系统（火警、进水、电池电量）
  - AIS数据、雷达目标

- **MQTT配置页面** (`public/mqtt-config.html`)：
  - 可视化的MQTT连接配置界面
  - 传感器映射管理（Topic → 数据路径）
  - 实时数据监控仪表盘
  - 消息日志查看器
  - 支持测试映射功能
  - 自动保存配置到 localStorage

### 🧪 自动化测试系统 | Automated Testing

- **system-test.html（系统功能验证页面）**：
  - 24项自动化测试覆盖所有核心模块
  - 核心模块测试：Three.js、Cannon.js、WebGL、ES Module
  - 天气系统测试：预设切换、风速、降雨、降雪
  - 物理系统测试：浮力、稳定器、风力、波浪
  - 数据系统测试：虚拟数据源、MQTT、数据绑定
  - 模型系统测试：GLB路径、GLTFLoader、材质、Uniform
  - GUI系统测试：lil-gui、国际化、相机控制
  - 实时测试结果显示和统计汇总

### 🚀 GLB模型加载增强 | GLB Loading Enhancement

- **路径解析优化**：
  - 支持绝对路径（`/public/GLB_20251223141542.glb`）
  - 智能路径候选列表，自动尝试多个可能的路径
  - 增强错误日志，包含 HTTP 状态、响应URL、错误详情
  - 60秒加载超时，防止无限等待

- **材质预处理**：
  - 加载后自动应用白色不透明材质作为基础
  - 确保所有mesh可见并正确设置 `renderOrder`
  - 优雅降级：如果材质应用失败不会阻止模型加载

### 🔗 系统集成 | System Integration

- **主界面增强**：
  - 在信息面板添加"系统工具"链接
  - 直接访问MQTT配置和系统测试页面
  - 保持界面一致性和导航便利性

- **数据接口管理器**：
  - `DataInterfaceManager` 统一管理所有数据源
  - 支持多数据源注册和切换
  - 数据绑定和订阅模式
  - 配置导入导出功能

---

## � Documentation
> **Note**: Detailed documentation has been moved to the `docs/` directory to keep the project root clean.

- [**Architecture**](docs/POSEIDON-X-ARCHITECTURE.md)
- [**Project Structure**](docs/POSEIDON-X-PROJECT-STRUCTURE.md)
- [**Features Guide**](docs/FEATURES_GUIDE.md)
- [**Development Guide**](docs/DEVELOPMENT_GUIDE.md)
- [**API & Integration**](docs/POSEIDON-X-LLM集成指南.md)

## 🤖 Poseidon-X Agent System
This project now follows an **AI Native** structure.
- **Context**: See `.cursorrules` for AI coding standards.
- **Agents**: See `.agent/` for memory and workflows.
- **Tests**: Run `npm test` to verify system integrity (Puppeteer-based).

### Quick Links
- [**Refactored Demo**](./index-refactored.html)
- [**Stability Test**](./test-stability.html)

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Dev Server
```bash
npm start
```
(Opens `http://localhost:3000`)

### 3. Run Automated Tests
```bash
npm test
```
(Runs headless browser verification)

### DeepSeek 在 Poseidon-X Bridge 中的应答与调用 Agent

- **配置**：在 `poseidon-config.html` 中配置 DeepSeek API Key 与模型（如 `deepseek-chat`），保存到 `localStorage` 的 `poseidon_config`。Bridge Chat 与各 Agent 的 `LLMClient` 均从该配置读取。
- **Bridge 内应答流程**：
  1. 用户在 Bridge 输入一句话 → `BridgeChat.sendMessage(message)`。
  2. **构建上下文**：`_buildContextWindow()` 生成当前船舶状态 + 最近对话；与系统 Vibe（含「4 个智能体」等说明）一起组成 `messages`。
  3. **调用大模型**：`this.llmClient.chat(messages)` 请求 DeepSeek API（`/v1/chat/completions`），得到 `response.content` 即 Bridge 展示给用户的**自然语言答复**。
  4. **路由到 Agent**：`_routeToAgents(userMessage)` 根据关键词（如「碰撞」「主机」「库存」「安全」）生成待调用的 Agent 列表 `agentCalls`。
  5. **执行 Agent**：若有 `agentCalls`，Bridge 依次 `_invokeAgent(agentName, task)`，即调用已注册的 Agent 的 `execute(task, context)`；Agent 内部可再调用 LLM（DeepSeek）做推理并 `useTool(...)`，结果可通过事件或后续对话展示给用户。
- **小结**：DeepSeek 在 Bridge 中**直接负责**自然语言应答；**间接参与** Agent 调用——Bridge 根据用户话术决定调用哪些 Agent，各 Agent 内部再用同一 DeepSeek 配置做推理与工具调用。未来若接入 MCP，可由 DeepSeek 通过 MCP 的 Tool Use 直接选择并调用 Agent 工具，实现更细粒度的「大模型驱动 Agent」集成。

---

## ✨ 核心特性 | Core Features

### 🌊 物理模拟系统 | Physics Simulation

- **多点浮力算法**：在船体底部设置多个采样点（双体船约95个点），精确计算浮力分布
- **船底可视化**：绿色网状平面高亮显示船底位置，便于调试和观察
- **精确浮力控制**：浮力点精确位于船底，确保船底与水面接触
- **可插拔算法引擎**：支持动态添加/移除物理算法（浮力、风力、降雨、自稳）
- **波浪模拟**：基于双正弦波叠加的动态水面，支持实时参数调节
- **自稳系统**：可调节的稳定器，模拟船舶的自稳力矩和阻尼
- **物理引擎**：使用 Cannon.js 进行刚体物理模拟，支持质量、阻尼、惯性等
- **双体船支持**：支持双体船（catamaran）配置，138米长，37,000吨

### ⛈️ 天气系统 | Weather System

- **风力模拟**：侧向力、横摇力矩、阵风效果
- **降雨模拟**：积水重量、排水、能见度降低
- **海况等级**：0-9级道格拉斯海况，自动调整波浪参数
- **天气预设**：平静、中等、风暴、台风等多种预设场景
- **可视化效果**：雨粒子系统、风向指示器、能见度雾效果

### 🚪 舱室系统 | Cabin System

- **多舱室支持**：零部件仓库、数据中心、高性能计算舱、生活舱、导航控制舱、供电舱、卫星通信舱、科学实验室
- **组件命名规范**：所有舱室组件使用前缀命名（如 `DataCenter-机架框架`、`PartsWarehouse-货架`）
- **坐标系绑定**：舱室与船体坐标系绑定，自动跟随船体运动
- **场景切换**：平滑相机过渡动画，支持第一人称视角
- **视觉指示**：绿色发光标记、线框边界、文字标签
- **交互方式**：点击标记、GUI菜单、ESC键退出

### 📊 实时数据系统 | Realtime Data System

- **船内数据**：燃油、设备状态、人员位置、实验任务、仓储物资
- **船外数据**：风向风速、海上目标、环境数据
- **3D可视化**：仪表盘、状态灯、进度条、标记点
- **数据接口管理**：支持虚拟数据源和真实系统对接
- **订阅发布模式**：实时数据更新和事件通知
- **仪表盘显示**：船舶仪表盘系统，实时显示关键指标

### 🛡️ 安全态势监控 | Safety Monitoring

- **主机监控**：温度、转速、功率、振动、健康度
- **燃油系统**：油位、流量、消耗率、压力
- **舵机推进**：舵角、推进器状态、效率、健康度
- **结构应力**：船首/船中/船尾应力、应变、疲劳
- **应急设备**：消防泵、救生艇、灭火器、应急发电机状态
- **报警系统**：多级报警（正常/警告/严重），实时状态指示
- **3D可视化**：状态指示灯（绿色/黄色/红色），实时更新（200ms间隔）

### 🎬 场景预演系统 | Scenario Simulation

- **暴雨漏水场景**：模拟漏水、积水、应急响应
- **第一人称视角**：WASD移动、鼠标视角控制
- **巡检路径**：路径规划、自动导航、路径可视化
- **设备故障模拟**：故障注入、故障响应、维修流程
- **场景效果**：漏水粒子系统、积水3D平面、路径可视化（绿色线条+标记点）
- **场景管理**：预定义场景存储，支持动态启动和停止

### 📡 船岸数据同步 | Ship-Shore Synchronization

- **批次传输**：静态数据（5秒）和动态数据（1秒）分批发送
- **数据压缩**：超过阈值（1KB）自动压缩，减少网络传输
- **优先级管理**：P0紧急/P1重要/P2正常/P3低优四级优先级
- **数据筛选**：变化超过阈值（1%）才发送，减少冗余数据
- **网络模拟**：支持延迟和丢包率模拟
- **传输队列**：智能队列管理，确保关键数据优先传输
- **统计数据**：实时收集传输统计，支持查看和分析

---

## 🚀 快速开始 | Quick Start

### 环境要求 | Requirements

- **Node.js** (可选，用于 npm 启动)
- **Python 3** (可选，用于简单 HTTP 服务器)
- **现代浏览器** (Chrome、Firefox、Edge 等，支持 WebGL)

### 安装依赖 | Install Dependencies

```bash
npm install
```

### 启动服务器 | Start Server

#### 方法 1：使用 npm（推荐）

```bash
# 默认端口（通常是 3000）
npm start

# 或指定端口 8000
npm run start:8000
```

#### 方法 2：使用 Python（无需 Node.js）

```bash
python -m http.server 8000
```

### 访问应用 | Access Application

- **重构版应用（推荐）**：`http://localhost:8000/index-refactored.html` ⭐
- **原始版本**：`http://localhost:8000/index.html`
- **稳定性测试**：`http://localhost:8000/test-stability.html`

> ⚠️ **重要提示**：本项目必须在 HTTP(S) 服务器环境下运行，直接双击打开 HTML 文件会因为 CORS 和 ES Modules 限制而无法正常工作。

---

## 🎮 功能详解 | Features

### 🌊 物理模拟系统

#### 浮力算法

系统在船体底部设置多个浮力采样点，每个点根据其在水下的深度计算浮力：

```
F = depth × buoyancyCoeff × density
```

**最新改进**：
- ✅ 浮力点精确位于船底（`Y = -shipSize.y * 0.5`）
- ✅ 船底网状平面可视化（绿色网格）
- ✅ 浮力系数优化（40,000,000），确保船底与水面接触
- ✅ 吃水深度设置为 0 米（船底与水面接触）

#### 双体船配置

- **船体尺寸**：138米长（Z轴）× 85米宽（X轴）× 95米高（Y轴）
- **船体质量**：37,000,000 kg（37,000吨）
- **浮力点分布**：沿Z轴（长度方向）均匀分布，两列平行（左列和右列）
- **浮力点数量**：约95个点（每列约46个位置 + 中心线关键点）

### 🚪 舱室系统

#### 进入舱室

1. **点击船体上的舱室标记**：
   - 🟢 查找绿色发光球体（呼吸闪烁）
   - 📝 点击舱室名称标签进入
   - ⬜ 可见绿色线框边界

2. **通过GUI菜单切换**：
   - 打开 "舱室系统 | Cabin System" 面板
   - 下拉菜单选择舱室
   - 或点击"退出舱室"按钮

3. **按ESC键退出**：
   - 在舱室内按 ESC 键
   - 自动返回船外视角

#### 可用舱室

- **零部件仓库** (Parts Warehouse)：货架系统、零部件箱、库存展示
- **数据中心** (Data Center)：服务器机架、监控屏幕、LED指示灯
- **高性能计算舱** (High Performance Computing Cabin)：服务器机架、冷却系统、控制面板
- **生活舱** (Living Cabin)：床铺、桌子、储物柜
- **导航控制舱** (Navigation Control Cabin)：导航设备、控制台
- **供电舱** (Power Supply Cabin)：发电机、配电柜
- **卫星通信舱** (Satellite Communication Cabin)：通信设备、天线
- **科学实验室** (Science Lab)：实验设备、工作台

#### 组件命名规范

所有舱室组件使用前缀命名，便于识别和管理：

- `DataCenter-机架框架`
- `DataCenter-机架组`
- `DataCenter-服务器单元-1`
- `DataCenter-LED指示灯-1`
- `DataCenter-主显示屏`
- `PartsWarehouse-货架-1-1`
- `PartsWarehouse-支撑柱-1-1-1`
- `HPCCabin-服务器机架-1-1`
- `HPCCabin-冷却系统-1`

#### 坐标系绑定

- ✅ 舱室使用局部坐标（相对于船体中心）
- ✅ 舱室添加到船体 mesh 中（`shipController.mesh.add(cabinMesh)`）
- ✅ 自动跟随船体的位置和旋转
- ✅ 舱室与船体从外部看是一体的

### 📊 实时数据显示

#### 船内数据 (Onboard)

- **⛽ 燃油**：3D仪表盘，实时显示燃油量（位置：左前方）
- **🏗️ 设备状态**：吊机状态灯（绿色=正常）、加速度数值（位置：右中部）
- **👥 人员位置**：实时人员分布标记（位置：中部）
- **🧪 实验任务**：进度条显示任务完成状态（位置：左后方）
- **📦 仓储物资**：库存状态指示器（位置：右后方）

#### 船外数据 (Offboard)

- **🌬️ 风向风速**：动态箭头指示，随天气系统变化（位置：上方）
- **🚢 海上目标**：周围船只和障碍物标记（位置：周围海域）

> 💡 **提示**：环绕相机查看船体各角度，所有数据对象都有明显的3D可视化

### 🛡️ 安全态势监控

系统实时监控以下关键指标：

- **主机状态**：温度、转速、功率、振动、健康度
- **燃油系统**：油位、流量、消耗率、压力
- **舵机推进**：舵角、推进器状态、效率、健康度
- **结构应力**：船首/船中/船尾应力、应变、疲劳
- **应急设备**：消防泵、救生艇、灭火器、应急发电机状态

**报警级别**：
- 🟢 **正常**：所有指标在正常范围内
- 🟡 **警告**：指标超出正常范围，需要关注
- 🔴 **严重**：指标达到危险值，需要立即处理

**初始化**：系统在页面加载后1.5秒自动初始化

### 🎬 场景预演系统

#### 可用场景

- **暴雨漏水场景** (`heavyRainLeak`)：模拟漏水、积水、应急响应
  - 起始点：住宿舱室
  - 路径：走廊1 → 走廊2 → 漏水点（货仓）
  - 效果：暴雨、漏水粒子系统、积水3D平面

#### 第一人称视角

- **WASD**：前后左右移动
- **鼠标**：视角控制（需要点击页面后激活）
- **移动速度**：5.0 m/s（可调节）

#### 路径可视化

- 系统支持定义巡检路径点
- 自动导航到下一个路径点
- 路径可视化显示（绿色线条 + 标记点）

**初始化**：系统在页面加载后2秒自动初始化

### 📡 船岸数据同步

#### 功能特性

- **静态数据批次传输**：每5秒发送一次（船体信息、设备规格、结构信息）
- **动态数据批次传输**：每1秒发送一次（位置、姿态、速度、各系统状态）
- **数据压缩**：超过1KB自动压缩，减少网络传输
- **数据筛选**：变化超过1%才发送，减少冗余数据
- **优先级管理**：
  - P0（紧急）：报警、故障 → 立即发送
  - P1（重要）：关键设备状态 → 5秒内发送
  - P2（正常）：常规监控数据 → 批次发送
  - P3（低优）：日志、统计 → 压缩后发送
- **网络模拟**：支持延迟和丢包率模拟
- **传输队列**：智能队列管理，确保关键数据优先传输
- **统计数据**：实时收集传输统计，支持查看和分析

**初始化**：系统在页面加载后2.5秒自动初始化并连接

---

## 🛠️ 技术架构 | Architecture

### 技术栈 | Tech Stack

- **Three.js** (r165) - 3D 渲染引擎
- **Cannon-es** (v0.20.0) - 物理引擎
- **lil-gui** (v0.19.2) - 参数控制面板
- **GLSL Shaders** - 自定义水面着色器
- **ES Modules** - 原生 ES6 模块化
- **事件驱动架构** - EventEmitter 模式
- **i18n 双语系统** - 中英文双语界面

### 项目结构 | Project Structure

```
DoubleBoatSimWebGL/
├── index.html                      # 主入口页面（原始版本）
├── index-refactored.html          # 重构版演示页面 ⭐ 推荐使用
├── test-stability.html            # 稳定性测试页面
├── package.json                    # 项目配置
├── README.md                       # 项目说明（本文档）
│
├── src/                            # 源代码目录
│   ├── main.js                    # 原始主逻辑（兼容版本）
│   ├── demo-refactored.js         # 重构版主程序 ⭐ 核心文件
│   ├── waves.js                   # 波浪函数和Shader
│   │
│   ├── physics/                   # 物理模拟系统
│   │   ├── SimulatorEngine.js     # 可插拔算法引擎
│   │   └── algorithms/            # 物理算法
│   │       ├── BuoyancyAlgorithm.js    # 浮力算法
│   │       ├── WindAlgorithm.js        # 风力算法
│   │       ├── RainAlgorithm.js        # 降雨算法
│   │       └── StabilizerAlgorithm.js  # 自稳算法
│   │
│   ├── weather/                   # 天气系统
│   │   └── WeatherSystem.js       # 天气系统管理
│   │
│   ├── ship/                      # 船舶系统
│   │   ├── ShipController.js     # 船舶控制器
│   │   ├── ShipStabilityAnalyzer.js # 稳定性分析器
│   │   └── cabins/                # 舱室定义
│   │       ├── CabinBase.js       # 舱室基类
│   │       ├── CabinManager.js    # 舱室管理器
│   │       ├── PartsWarehouse.js  # 零部件仓库
│   │       ├── DataCenter.js      # 数据中心
│   │       ├── HighPerformanceComputingCabin.js
│   │       ├── LivingCabin.js
│   │       ├── NavigationControlCabin.js
│   │       ├── PowerSupplyCabin.js
│   │       ├── SatelliteCommCabin.js
│   │       └── ScienceLabCabin.js
│   │
│   ├── data/                      # 数据系统
│   │   ├── DataInterfaceManager.js # 数据接口管理器
│   │   ├── VirtualDataSource.js   # 虚拟数据源
│   │   ├── MQTTDataSource.js      # MQTT数据源 ⭐ 新增
│   │   ├── RealtimeDisplaySystem.js # 实时显示系统
│   │   └── ShipShoreSync.js       # 船岸数据同步
│   │
│   ├── monitoring/                # 监控系统
│   │   ├── SafetyMonitor.js       # 安全态势监控
│   │   └── ShipDashboardDisplay.js # 仪表盘显示
│   │
│   ├── simulation/                # 场景预演系统
│   │   ├── ScenarioSimulator.js   # 场景模拟器
│   │   ├── InspectionScenario.js  # 巡检场景
│   │   └── FireDrillScenario.js   # 消防演练场景
│   │
│   ├── tests/                     # 测试与验证系统 ⭐ 增强
│   │   ├── ShipStabilityTest.js   # 稳定性测试
│   │   ├── PreRenderValidator.js  # 预渲染验证器 ⭐ 新增
│   │   └── ThreeJSPatch.js        # Three.js补丁 ⭐ 新增
│   │
│   └── utils/                     # 工具库
│       ├── EventEmitter.js        # 事件发射器
│       └── i18n.js                # 国际化工具
│
├── public/                         # 静态资源
│   ├── GLB_20251223141542.glb    # 船舶 GLB 模型
│   ├── favicon.svg                # 网站图标
│   ├── gui-enhancements.css       # GUI样式
│   ├── mqtt-config.html           # MQTT传感器配置页面 ⭐ 新增
│   ├── system-test.html           # 系统功能测试页面 ⭐ 新增
│   └── lib/                       # 本地库备份
│       ├── three.module.js
│       ├── cannon-es.js
│       ├── GLTFLoader.js
│       ├── OrbitControls.js
│       └── lil-gui.esm.min.js
│
└── docs/                           # 文档目录（各种 .md 文件）
    ├── ARCHITECTURE.md            # 架构文档
    ├── DEVELOPMENT_GUIDE.md       # 开发指南
    ├── FEATURES_GUIDE.md          # 功能指南
    ├── GUI_USAGE.md               # GUI使用说明
    ├── I18N_GUIDE.md              # 国际化指南
    ├── MODULES_IMPLEMENTATION_SUMMARY.md # 模块实现总结
    └── TEST_README.md              # 测试系统说明
```

### 核心实现原理 | Core Implementation

#### 1. 可插拔算法引擎

系统采用可插拔算法架构，支持动态添加/移除物理算法：

```javascript
// 注册算法
simulatorEngine.registerAlgorithm(new BuoyancyAlgorithm());
simulatorEngine.registerAlgorithm(new WindAlgorithm());
simulatorEngine.registerAlgorithm(new RainAlgorithm());
simulatorEngine.registerAlgorithm(new StabilizerAlgorithm());

// 统一更新
simulatorEngine.update(deltaTime, shipState, environment);
```

**算法优先级**：
- Buoyancy: 100（最高）
- Stabilizer: 90
- Wind: 80
- Rain: 70

#### 2. 波浪函数

波浪高度由两个正弦波叠加：

```
h(x, z, t) = A * sin(kx + ωt) + 0.55A * sin(k(x + 0.45z) + 1.35ωt)
```

其中：
- `A`：振幅
- `k = 2π / λ`：波数
- `ω = k * v`：角频率
- `λ`：波长
- `v`：波速

#### 3. 多点浮力计算

在船体底部设置多个采样点，每个点根据其在水下的深度计算浮力：

```
F = depth × buoyancyCoeff × density
```

同时施加速度相关的阻尼力：

```
F_drag = -velocity × dragCoeff
```

**最新改进**：
- 浮力点精确位于船底（`Y = -shipSize.y * 0.5`）
- 船底网状平面可视化（绿色网格）
- 浮力系数优化（40,000,000），确保船底与水面接触

#### 4. 自稳系统

通过计算船体上方向与世界上方向的夹角，施加恢复力矩：

```
torque = (bodyUp × worldUp) × angle × stiffness - angularVelocity × damping
```

有效刚度受摇晃增强系数影响：

```
effectiveStiffness = stiffness / wobbleBoost
```

---

## 🎮 交互说明 | User Guide

### 相机控制 | Camera Controls

- **鼠标左键拖动**：旋转视角
- **鼠标右键拖动** 或 **Shift + 左键拖动**：平移视角
- **鼠标滚轮**：缩放视角
- **双击物体**：聚焦到物体

### GUI 控制面板 | GUI Control Panel

#### 🌊 波浪参数 | Wave Parameters

- `amplitude`：波浪振幅（波高）
- `wavelength`：波长
- `speed`：波浪速度
- `steepness`：波浪陡度

#### ⚓ 浮力与稳定性 | Buoyancy & Stability

**核心物理参数：**

- **`buoyancyCoeff`（浮力系数）**：默认 40,000,000
  - 控制船体受到的浮力强度
  - 值越大，船体越容易浮起
  - 💡 **最新优化**：确保船底与水面接触

- **`dragCoeff`（阻尼系数）**：范围 0-20，默认 6
  - 控制船体在水中运动时受到的阻力
  - 值越大，船体运动越平稳

- **`density`（水密度）**：范围 0.5-2.0，默认 1.0
  - 模拟不同水体密度（淡水约 1.0，海水约 1.025）

- **`Boat mass`（船体质量）**：默认 37,000,000 kg（37,000吨）
  - 直接影响船体的惯性和重力
  - **配置**：138米长双体船，37,000吨

**姿态控制参数：**

- **`Draft depth`（吃水深度）**：默认 0 米
  - 0：船体底部刚好接触水面 ✅ **最新设置**
  - 正值：船体压入水面下的深度
  - 负值：船体悬浮在水面之上

- **`Stabilizer on/off`（自稳系统开关）**：默认启用
  - 启用时会施加自稳力矩，使船体自动恢复直立

- **`Stabilizer stiff`（自稳刚度）**：范围 0-15，默认 12.0
  - 控制船体恢复直立的力度
  - 针对17级台风优化，使用更高刚度

- **`Stabilizer damp`（自稳阻尼）**：范围 0-10，默认 6.0
  - 抑制船体在恢复直立过程中的振荡

- **`Wobble boost`（摇晃增强系数）**：范围 0.2-5.0，默认 0.8
  - 1.0：正常自稳效果
  - >1.0：减弱自稳，船体更容易摇晃
  - <1.0：增强自稳，船体更加稳定
  - 重构版降低摇晃增强，提高稳定性

#### ⚙️ 算法管理 | Algorithm Management

- **Buoyancy (P100)**：浮力算法，优先级最高
- **Stabilizer (P90)**：自稳算法
- **Wind (P80)**：风力算法
- **Rain (P70)**：降雨算法
- 每个算法可独立启用/禁用

#### 🌤️ 天气控制 | Weather Control

- **风速**：0-50 m/s
- **风向**：0-360 度
- **降雨强度**：0-100%
- **海况等级**：0-9 级（道格拉斯海况）
- **天气预设**：平静、中等、风暴、台风

#### 👁️ 显示选项 | Display Options

- **显示天气指示器**：显示风向箭头、雨粒子
- **水面线框**：以线框模式渲染水面
- **显示坐标轴**：显示船体坐标轴辅助器
- **聚焦船体**：相机聚焦到船体
- **显示物理体**：显示 Cannon.js 物理碰撞体（绿色线框）
- **船底网状平面**：显示船底位置（绿色网格）✅ **新增**

---

## 🔧 开发指南 | Development

### 更换船舶模型

将新的 GLB 模型放入 `public/` 目录，并在 `src/ship/ShipController.js` 中更新路径：

```javascript
const shipController = new ShipController(scene, world, {
  glbPath: 'public/your-model.glb',
  desiredSize: { x: 85, y: 95, z: 138 }, // 目标尺寸（宽度、高度、长度）
  catamaran: { enabled: true } // 双体船配置
});
```

### 添加新的物理算法

创建新算法类并注册：

```javascript
class MyAlgorithm extends SimulationAlgorithm {
  constructor() {
    super('MyAlgorithm', 60); // 名称和优先级
  }
  
  update(deltaTime, shipState, environment) {
    // 计算力和力矩
    return {
      force: new CANNON.Vec3(0, 100, 0),
      torque: new CANNON.Vec3(0, 0, 0)
    };
  }
}

// 注册算法
simulatorEngine.registerAlgorithm(new MyAlgorithm());
```

### 添加新的舱室

创建新舱室类：

```javascript
class MyCabin extends CabinBase {
  constructor(config = {}) {
    super({
      id: 'my-cabin',
      name: 'My Cabin | 我的舱室',
      ...config
    });
  }
  
  build(scene, shipPosition, shipRotation) {
    const cabinGroup = new THREE.Group();
    cabinGroup.name = 'MyCabin';
    
    // 创建舱室内的3D对象
    // 注意：组件名称使用前缀，如 'MyCabin-组件名'
    
    return cabinGroup;
  }
}

// 在 CabinManager 中注册
cabinManager.addCabin(new MyCabin());
```

**重要提示**：
- ✅ 组件名称使用前缀（如 `MyCabin-组件名`）
- ✅ 舱室使用局部坐标（相对于船体中心）
- ✅ 舱室会自动绑定到船体坐标系

### 调整物理参数

在 `src/demo-refactored.js` 的 `config` 对象中调整默认值：

```javascript
const config = {
  boatSize: { x: 85, y: 95, z: 138 }, // 宽度、高度、长度
  boatMass: 37000000, // 37,000吨
  draftDepth: 0, // 吃水深度（0米 = 船底与水面接触）
  buoyancy: {
    buoyancyCoeff: 40000000, // 浮力系数（确保船底与水面接触）
    dragCoeff: 6,
    density: 1.0
  },
  stabilizer: {
    enableStabilizer: true,
    uprightStiffness: 12.0,
    uprightDamping: 6.0,
    wobbleBoost: 0.8
  }
};
```

---

## 🧪 测试系统 | Test System

项目包含完整的船体稳定性自动化测试系统：

**测试页面 | Test Page**:
```
http://localhost:8000/test-stability.html
```

**测试功能 | Test Features**:
- ✅ 7种不同的稳定性测试场景（基础稳定性、波浪响应、风力影响、降雨影响、极端天气、参数变化、扰动恢复）
- ✅ 自动化的物理模拟和指标收集
- ✅ 可视化的测试报告和统计
- ✅ 双语界面支持
- ✅ JSON 报告导出

**快速测试 | Quick Test**:
1. 访问测试页面
2. 点击 "运行所有测试 | Run All Tests"（完整测试，约1-2分钟）
3. 或点击 "快速测试 | Quick Test"（基础测试，约10秒）
4. 查看测试结果和详细报告

**测试指标 | Test Metrics**:
- 最大倾斜角度、最大下沉深度
- 最大漂移距离、振荡幅度
- 恢复时间、是否倾覆
- 最终姿态和位置

详细文档：[TEST_README.md](./TEST_README.md)

---

## 📚 文档 | Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - 系统架构设计文档
- **[DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md)** - 开发指南
- **[FEATURES_GUIDE.md](./FEATURES_GUIDE.md)** - 功能使用指南
- **[GUI_USAGE.md](./GUI_USAGE.md)** - GUI使用说明
- **[I18N_GUIDE.md](./I18N_GUIDE.md)** - 国际化指南
- **[MODULES_IMPLEMENTATION_SUMMARY.md](./MODULES_IMPLEMENTATION_SUMMARY.md)** - 模块实现总结
- **[PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)** - 项目总结
- **[REFACTORING_CHANGELOG.md](./REFACTORING_CHANGELOG.md)** - 重构更新日志

---

## 🌍 国际化支持 | Internationalization

### 当前状态：双语模式

本项目所有界面文本采用**中英文双语显示**模式：
- ✅ GUI 控制面板全部双语
- ✅ 状态显示信息双语
- ✅ HTML 界面文本双语
- ✅ 统一格式：`中文 | English`

**示例**：
```
🌊 波浪参数 | Wave Parameters
风速 | Wind Speed (m/s)
🔄 重置船体 | Reset Boat
```

### 为什么使用双语？

1. **适合国际合作**：中英文用户都能理解
2. **技术准备**：为将来的多语言支持做准备
3. **专业术语**：同时展示中英文，减少歧义

### 未来计划

- 📋 Phase 1：双语模式（✅ 已完成）
- 🔄 Phase 2：添加语言切换功能
- 🌐 Phase 3：支持更多语言（日语、韩语等）

详细文档：[I18N_GUIDE.md](./I18N_GUIDE.md)

---

## 🎯 参数调节建议 | Parameter Tuning Tips

### 🎯 平稳大船（如货轮、邮轮）

- `boatMass`: 50000+
- `buoyancyCoeff`: 800+
- `dragCoeff`: 10-15
- `wobbleBoost`: 0.5-0.8

### ⛵ 灵活小船（如快艇、帆船）

- `boatMass`: 5000-10000
- `buoyancyCoeff`: 300-500
- `dragCoeff`: 3-6
- `wobbleBoost`: 1.5-2.5

### 🌊 极端天气测试（17级台风）

- `amplitude`: 2.0+（大浪）
- `wobbleBoost`: 0.8（降低摇晃，提高稳定性）
- `Stabilizer stiff`: 12.0+（提高自稳刚度）
- `Stabilizer damp`: 6.0+（提高阻尼）

### 🚢 双体船配置（重构版默认）

- `boatMass`: 37,000,000 kg（37,000吨）
- `boatSize`: { x: 85, y: 95, z: 138 }（138米长）
- `buoyancyCoeff`: 40,000,000 ✅ **最新优化**
- `draftDepth`: 0米 ✅ **船底与水面接触**
- `catamaran`: { enabled: true }

---

## 📈 性能指标 | Performance Metrics

- **渲染帧率**：≥60 FPS（桌面浏览器）、≥30 FPS（移动设备）
- **物理更新**：60 Hz 固定时间步长
- **算法执行**：< 1ms（4个算法）
- **内存占用**：~150 MB
- **网络延迟**：船岸同步 < 500ms（模拟）
- **初始化时间**：各模块延迟初始化，总时间约3-4秒

---

## ⚠️ 重要提示 | Important Notes

### 初始化时间

系统采用延迟初始化策略，各模块按顺序初始化：
- 舱室系统：延迟3秒初始化
- 实时数据系统：延迟1秒初始化
- 仪表盘显示：延迟1.2秒初始化
- 安全监控系统：延迟1.5秒初始化
- 场景预演系统：延迟2秒初始化
- 船岸数据同步：延迟2.5秒初始化

**请耐心等待控制台出现"✅ initialized"消息！**

### 推荐使用重构版

- **重构版** (`index-refactored.html`)：包含所有最新功能，推荐使用 ⭐
- **原始版** (`index.html`)：基础功能，用于兼容性测试

### 查找技巧

如果看不到功能：
1. 打开F12控制台查看日志
2. 旋转相机360度环绕船体
3. 使用调试命令手动测试
4. 查看相关文档的故障排查部分

### 视觉提示

- 🟢 **绿色** = 舱室入口、正常状态、船底网状平面
- 🟡 **黄色** = 警告状态
- 🔴 **红色** = 故障状态
- ✨ **闪烁** = 可交互对象

---

## 🔄 最新更新 | Latest Updates

### v3.1.0 (2026-01-05) - 全面功能验证和优化

#### ✅ 新增：MQTT传感器数据系统

- **MQTTDataSource.js**：新增MQTT数据源类，支持真实传感器数据接入
  - 支持WebSocket MQTT协议连接
  - 自动重连和模拟数据模式
  - 传感器映射配置（主题→数据路径）
  - 支持GPS、IMU、气象站、主机参数、燃油系统等12种传感器类型
  
- **mqtt-config.html**：新增可视化传感器配置页面
  - 直观的MQTT连接配置界面
  - 传感器映射的可视化管理
  - 实时数据监控和消息日志
  - 支持测试数据生成

#### ✅ 新增：系统功能验证测试

- **system-test.html**：新增综合功能测试页面
  - 24项自动化测试覆盖所有核心模块
  - 测试类别：核心模块、天气系统、物理系统、数据系统、模型系统、界面系统
  - 可视化测试结果和日志
  - 支持单项测试和全量测试

#### ✅ 天气系统优化

- 修复天气预设切换问题，新增`preset`属性getter/setter
- 新增**降雪预设**（snow）：温度-5°C、降雪强度30mm/h
- 优化`setWeatherPreset`方法，支持温度和降雪参数
- 修复i18n国际化配置，添加snow预设翻译

#### ✅ 模型加载优化

- 优化`_getModelPaths`方法，改进GLB路径解析逻辑
- 支持从配置路径动态提取文件名
- 增加多种候选路径策略，提高加载成功率
- 改进日志输出，便于调试路径问题

#### ✅ 代码质量改进

- 修复WeatherSystem中presets的同步问题
- 优化ShipController的路径处理逻辑
- 添加更多详细的日志输出便于调试

---

### v3.0.0-all-modules (2025-12-29)

#### ✅ 物理模拟系统改进

- **船底可视化**：添加绿色网状平面，高亮显示船底位置
- **浮力点优化**：浮力点精确位于船底（`Y = -shipSize.y * 0.5`）
- **浮力系数调整**：从 7,000,000 调整为 40,000,000，确保船底与水面接触
- **吃水深度**：从 11米 调整为 0米（船底与水面接触）

#### ✅ 舱室系统改进

- **组件命名规范**：所有舱室组件使用前缀命名（如 `DataCenter-机架框架`）
- **坐标系绑定**：舱室与船体坐标系绑定，自动跟随船体运动
- **命名示例**：
  - `DataCenter-机架框架`、`DataCenter-服务器单元-1`
  - `PartsWarehouse-货架-1-1`、`PartsWarehouse-支撑柱-1-1-1`
  - `HPCCabin-服务器机架-1-1`、`HPCCabin-冷却系统-1`

---

## 🙏 致谢 | Acknowledgments

- [Three.js](https://threejs.org/) - 强大的 3D 渲染库
- [Cannon-es](https://pmndrs.github.io/cannon-es/) - 轻量级物理引擎
- [lil-gui](https://lil-gui.georgealways.com/) - 简洁的参数控制面板

---

## 📄 许可 | License

本项目仅供学习和演示使用。

---

**当前分支**: PCrefactor  
**版本**: v3.1.0  
**最后更新**: 2026-01-05

**注意**：本项目需要在 HTTP(S) 服务器环境下运行，直接双击打开 HTML 文件会因为 CORS 和 ES Modules 限制而无法正常工作。

**Note**: This project requires an HTTP(S) server environment to run. Opening HTML files directly will fail due to CORS and ES Modules restrictions.
