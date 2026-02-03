# Poseidon-X 智能船舶系统架构文档

## 🌊 Software 3.0 Edition - 我们不写功能，我们培育智能体

---

## 📋 目录

1. [架构概述](#架构概述)
2. [设计理念](#设计理念)
3. [Layer 1: 统一交互界面](#layer-1-统一交互界面)
4. [Layer 2: AI Crew 智能体](#layer-2-ai-crew-智能体)
5. [Layer 3: Intelligence Foundry 开发平台](#layer-3-intelligence-foundry-开发平台)
6. [技术栈](#技术栈)
7. [部署架构](#部署架构)
8. [开发指南](#开发指南)

---

## 架构概述

Poseidon-X 是基于 **1 + N + X** 架构的智能船舶系统：

```
┌─────────────────────────────────────────────────────────────┐
│                    Poseidon-X Architecture                   │
│                      (Software 3.0)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├── Layer 1: For End User (1)
                              │   └── The Omniscient Interface
                              │       ├── Bridge Chat (舰桥对话)
                              │       ├── Digital Twin Map (数字孪生)
                              │       └── Context Window (RAM)
                              │
                              ├── Layer 2: For End User (N)
                              │   └── The AI Crew (智能船员)
                              │       ├── Navigator Agent (领航员)
                              │       ├── Engineer Agent (轮机长)
                              │       ├── Steward Agent (大管家)
                              │       ├── Safety Agent (安全官)
                              │       └── Agent Orchestrator (编排系统)
                              │
                              └── Layer 3: For Developer (X)
                                  └── The Intelligence Foundry (兵工厂)
                                      ├── Vibe Generator (生成器)
                                      ├── Simulation Validator (编译器)
                                      └── LLM Judge (裁判 + 数据闭环)
```

---

## 设计理念

### 从"功能堆砌"到"智能体生态"

**传统方式（Hard-coded Features）**：
```javascript
function calculateCollisionRisk(ship1, ship2) {
  const cpa = /* 复杂计算 */;
  if (cpa < 0.5) {
    alert("Collision risk!");
  }
}
```

**Software 3.0 方式（Cultivate Agents）**：
```javascript
const navigatorAgent = new NavigatorAgent({
  vibe: "极致安全与效率的追求者，时刻计算最优解。",
  tools: ['calculateCPA', 'assessCollisionRisk', 'generateAvoidanceManeuver']
});

await navigatorAgent.execute("右舷那艘集装箱船有碰撞风险吗？", shipContext);
// Agent 自主推理，调用工具，生成专业建议
```

### 核心原则

1. **Vibe 优先**：每个 Agent 都有自己的"人格"（Vibe），决定其行为风格
2. **Tool Use**：Agent 不是写死的函数，而是会使用工具的智能体
3. **Memory**：Agent 有短期和长期记忆，能够学习和进化
4. **Orchestration**：多个 Agent 协作，类似 LangGraph 的状态图
5. **Validation**：所有 Agent 必须在仿真器中通过测试才能上船

---

## Layer 1: 统一交互界面

### 1.1 Bridge Chat - 舰桥对话中心

**文件**：`src/poseidon/layer1-interface/BridgeChat.js`

**功能**：
- 多模态输入（语音 🎤、文本 ⌨️、手势 🤚）
- 自然语言查询：船长不需要学习复杂菜单，直接问问题
- 智能路由：自动分发任务到合适的 Agent

**示例对话**：
```
船长：Poseidon，右舷那艘集装箱船有碰撞风险吗？
Poseidon：正在查询 Navigator Agent... 
          无风险，CPA 为 2.5 海里，TCPA 18 分钟。
          建议在其船尾通过以节省燃油。
```

**核心代码**：
```javascript
// Bridge Chat 自动路由到合适的 Agent
const response = await bridgeChat.sendMessage(userQuery);

// 内部：智能路由
const agent = orchestrator.routeTask(userQuery); // → Navigator Agent
const result = await agent.execute(userQuery, shipContext);
```

### 1.2 Digital Twin Map - 数字孪生海图

**文件**：`src/poseidon/layer1-interface/DigitalTwinMap.js`

**功能**：
- 3D 实时渲染船舶和周边环境
- AIS 目标可视化
- 智能高亮（AI 自动标记风险区域）
- AR 增强现实投影（未来支持 Vision Pro/XR）

**示例**：
```javascript
// 添加 AIS 目标
digitalTwinMap.addAISTarget('413123456', {
  name: 'EVER GIVEN',
  position: { x: 50, z: 30 },
  distance: 2.5 // NM
});

// AI 高亮风险区域
digitalTwinMap.highlight(targetShip, '碰撞风险');
```

### 1.3 Context Window - 上下文窗口（RAM）

**文件**：`src/poseidon/layer1-interface/ContextWindow.js`

**功能**：
- 全船传感器数据 → 文本/Embedding
- 实时喂给 LLM 的上下文
- 智能压缩（优先级管理）

**数据流**：
```
Sensors → Raw Data → Text → Context Window → LLM
NMEA      温度=95°C   "主机排温 95°C"  [RAM]     GPT-4
Modbus                "正常范围 350-400°C"
```

---

## Layer 2: AI Crew 智能体

### 2.1 Navigator Agent - 领航员智能体

**文件**：`src/poseidon/layer2-agents/NavigatorAgent.js`

**Vibe**：
> "极致安全与效率的追求者，时刻计算最优解。"

**职责**：
- ⚓ 航行路径规划
- 🚢 避碰决策（遵守 COLREGs 国际海上避碰规则）
- 🌦️ 气象路由优化
- ⛽ 纵倾优化（减少阻力）

**工具**：
- `calculateCPA`: 计算最近会遇距离/时间
- `assessCollisionRisk`: 评估碰撞风险
- `generateAvoidanceManeuver`: 生成避碰建议
- `optimizeRoute`: 优化航线（燃油经济性）

**示例**：
```javascript
const navigator = new NavigatorAgent();
const result = await navigator.execute(
  "右舷那艘集装箱船有碰撞风险吗？", 
  { aisTargets, currentCourse }
);
// → { cpa: 2.5, tcpa: 18, riskLevel: 'low', recommendation: '...' }
```

### 2.2 Engineer Agent - 轮机长智能体

**文件**：`src/poseidon/layer2-agents/EngineerAgent.js`

**Vibe**：
> "经验丰富的老轨，能听懂机器的呻吟。"

**职责**：
- ⚙️ 设备健康管理（PHM）
- 📊 能效监控与优化
- 🔧 预测性维护
- 🩺 故障诊断

**工具**：
- `analyzeExhaustTemp`: 分析排温异常
- `calculateHealthScore`: 计算设备健康评分
- `generateMaintenancePlan`: 生成维护计划
- `analyzeFuelConsumption`: 燃油消耗分析

**示例**：
```javascript
const engineer = new EngineerAgent();
const result = await engineer.execute(
  "主机排温异常吗？", 
  { cylinderTemps: [370, 380, 385, 375, 372, 368] }
);
// → "3 号缸排温偏高 4%，建议下次停泊时检查喷油嘴"
```

### 2.3 Steward Agent - 大管家智能体

**文件**：`src/poseidon/layer2-agents/StewardAgent.js`

**Vibe**：
> "细致入微的后勤总管，不仅管物，更管人。"

**职责**：
- 📦 仓储管理（RFID 智能仓库）
- 🍽️ 伙食管理（菜单生成、营养均衡）
- 🌡️ 环境控制（舱室温湿度、CO2、照明）
- 💊 船员福祉（疲劳监测、健康建议）

**工具**：
- `generateMenu`: 生成菜单
- `checkInventory`: 检查库存
- `monitorCabinEnvironment`: 监控舱室环境
- `detectCrewFatigue`: 检测船员疲劳

### 2.4 Safety Agent - 安全官智能体

**文件**：`src/poseidon/layer2-agents/SafetyAgent.js`

**Vibe**：
> "永不眨眼的守望者，安全是最高指令。"

**职责**：
- 📹 视觉监控（CCTV 视频流分析）
- 🚨 应急响应（MOB 人员落水、火灾、烟雾）
- 🔍 安全巡检（自动检测违规行为）
- 📋 应急预案执行

**工具**：
- `analyzeVideoFrame`: 分析视频帧（计算机视觉）
- `triggerAlert`: 触发警报
- `generateEvacuationRoute`: 生成逃生路线
- `assessSafetySituation`: 评估安全态势

**示例（MOB 场景）**：
```javascript
const safety = new SafetyAgent();
const result = await safety.execute("人员落水！", context);
// → 自动执行：
//    ✅ 启动全船警报
//    ✅ 通知船长
//    ✅ 记录 GPS 位置
//    ✅ 生成救援方案
//    ⏱️ 响应时间: 1.2 秒 ✅ (< 2秒标准)
```

### 2.5 Agent Orchestrator - 编排系统

**文件**：`src/poseidon/layer2-agents/AgentOrchestrator.js`

**功能**：
- 协调多个 Agent 协作（类似 LangGraph）
- 智能路由任务到最合适的 Agent
- 管理工作流（复杂多步骤任务）

**示例**：
```javascript
const orchestrator = new AgentOrchestrator();

// 注册 Agents
orchestrator.registerAgent('navigator', navigatorAgent);
orchestrator.registerAgent('engineer', engineerAgent);
orchestrator.registerAgent('safety', safetyAgent);

// 自动路由
await orchestrator.executeTask("右舷那艘船有碰撞风险吗？");
// → 自动路由到 Navigator Agent

// 并行执行
await orchestrator.executeParallel([
  "检查主机状态",
  "评估碰撞风险",
  "检查库存"
]);
// → 同时调用 Engineer, Navigator, Steward
```

---

## Layer 3: Intelligence Foundry 开发平台

### 3.1 Vibe Generator - 生成器

**文件**：`src/poseidon/layer3-platform/VibeGenerator.js`

**功能**：从自然语言需求生成 Agent 代码

**示例**：
```javascript
const generator = new VibeGenerator();

const generation = await generator.generateAgent(
  `创建一个能够通过分析排气颜色（视觉）和排温（传感器）
   来判断燃烧效率的 Agent。`
);

// 输出：
// ✅ Agent 代码（JavaScript）
// ✅ 工具定义（计算机视觉模型调用）
// ✅ Dockerfile
// ✅ 部署配置
// ✅ 测试代码
```

### 3.2 Simulation Validator - 仿真验证器（编译器）

**文件**：`src/poseidon/layer3-platform/SimulationValidator.js`

**功能**：这是 Software 3.0 的"编译器"

**流程**：
```
1. 生成的 Agent → 仿真器
2. 生成 1000 种海况（暴风雨、夜间、大雾、设备故障）
3. Vibe Check: Agent 表现如何？
4. 通过 ✅ → 部署到船上
   失败 ❌ → 退回 Vibe Generator 重新生成
```

**示例**：
```javascript
const validator = new SimulationValidator();

const report = await validator.validateAgent(navigatorAgent, ['all']);

// 报告：
// ✅ 通过 85 / 100 场景 (85%)
// ❌ 失败场景：
//    - 暴风雨 + 夜间（响应时间过长）
//    - 设备故障（未触发备用系统）
```

### 3.3 LLM Judge - AI 裁判 + 数据闭环

**文件**：`src/poseidon/layer3-platform/LLMJudge.js`

**功能**：评估 Agent 表现 + 实船数据回流

**评估维度**：
- ✅ **正确性**（30%）：响应是否准确
- ✅ **合规性**（30%）：是否符合海事法规（COLREGs, ISM, SOLAS）
- ✅ **决策质量**（25%）：决策是否合理
- ✅ **及时性**（15%）：响应是否够快

**数据闭环**：
```
实船运行 → 船长接管控制（特殊情况）
           ↓
       数据回传 → LLM Judge 分析
           ↓
   生成新的测试用例 → 下一代 Agent 训练
```

**示例**：
```javascript
const judge = new LLMJudge();

const evaluation = await judge.evaluate(agentExecution, context);

// 评估报告：
// 📊 综合评分: 87.5 / 100 ✅
// ✅ 正确性: 90 / 100
// ✅ 合规性: 95 / 100 (符合 COLREGs Rule 15)
// ✅ 决策质量: 85 / 100
// ✅ 及时性: 78 / 100

// 建议：
// 💡 提高响应速度（当前 3.2s，建议 < 2s）
```

---

## 技术栈

### 前端（Layer 1）
- **渲染**：Three.js r165
- **物理**：Cannon-es 0.20.0
- **UI**：lil-gui + 自定义 HTML/CSS

### 后端（Layer 2 + 3）
- **LLM**：OpenAI GPT-4 / Anthropic Claude
- **编排**：LangGraph (概念实现)
- **部署**：Docker + Kubernetes (K3s)

### 船端（Edge）
- **硬件**：加固型工业服务器（Moxa/Bachmann）
- **OS**：Linux + K3s
- **通信**：ROS 2（机器人操作系统）

### 岸端（Cloud）
- **仿真**：NVIDIA Isaac Sim (OceanSim)
- **评估**：LangSmith + LLM-as-a-Judge
- **数据库**：PostgreSQL + Vector DB (Pinecone/Qdrant)

---

## 部署架构

### 船端（Edge - 实时性高）
```
┌─────────────────────────────────────┐
│       Ship Edge Computing           │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  K3s Cluster                 │  │
│  │                              │  │
│  │  ┌─────────┐  ┌──────────┐ │  │
│  │  │Navigator│  │ Engineer │ │  │
│  │  │ Agent   │  │  Agent   │ │  │
│  │  └─────────┘  └──────────┘ │  │
│  │                              │  │
│  │  ┌─────────┐  ┌──────────┐ │  │
│  │  │ Safety  │  │ Steward  │ │  │
│  │  │ Agent   │  │  Agent   │ │  │
│  │  └─────────┘  └──────────┘ │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  ROS 2 通信总线              │  │
│  └──────────────────────────────┘  │
│           ↓          ↓              │
│     传感器(2000+)  执行器          │
└─────────────────────────────────────┘
```

### 岸端（Cloud - 算力强）
```
┌─────────────────────────────────────┐
│         Shore Cloud                 │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Intelligence Foundry        │  │
│  │                              │  │
│  │  • Vibe Generator            │  │
│  │  • Simulation Validator      │  │
│  │  • LLM Judge                 │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  NVIDIA Isaac Sim            │  │
│  │  (OceanSim)                  │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  数据闭环系统                │  │
│  │  • 实船数据收集              │  │
│  │  • 测试用例生成              │  │
│  │  • Agent 持续优化            │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## 开发指南

### 创建新的 Agent（Vibe Coding 方式）

#### 方式 1: 使用 Vibe Generator（推荐）
```javascript
const generator = new VibeGenerator();

const myAgent = await generator.generateAgent(`
  创建一个监控海水淡化装置的 Agent。
  它能：
  1. 实时监控产水量和水质（TDS）
  2. 检测膜污堵情况
  3. 预测滤芯更换时间
  4. 优化反渗透压力以节省能耗
`);

// 自动生成完整代码！
```

#### 方式 2: 手动继承 AgentBase
```javascript
import { AgentBase } from './layer2-agents/AgentBase.js';

export class WaterMakerAgent extends AgentBase {
  constructor(config = {}) {
    super({
      ...config,
      id: 'watermaker-agent',
      name: 'WaterMaker Agent',
      role: 'watermaker',
      vibe: `你是海水淡化装置的专家...`,
      deploymentLocation: 'edge'
    });
    
    this._registerTools();
  }
  
  _registerTools() {
    this.registerTool('checkTDS', async (params) => {
      // 检查水质
      return { tds: 150, quality: 'good' };
    }, 'Check water quality (TDS)');
  }
  
  async execute(task, context) {
    // 实现执行逻辑
  }
}
```

### 测试 Agent

```javascript
// 1. 单元测试
const agent = new NavigatorAgent();
const result = await agent.execute("测试任务", mockContext);
assert(result.type === 'expected_type');

// 2. 仿真验证
const validator = new SimulationValidator();
const report = await validator.validateAgent(agent, ['all']);
assert(report.passRate >= 0.85); // 85% 通过率

// 3. LLM 评估
const judge = new LLMJudge();
const evaluation = await judge.evaluate(execution, context);
assert(evaluation.passed === true);
```

### 部署 Agent

```bash
# 1. 构建 Docker 镜像
docker build -t poseidon-x/navigator-agent:v1 .

# 2. 部署到 K3s
kubectl apply -f deployment/navigator-agent.yaml

# 3. 验证部署
kubectl get pods -l app=navigator-agent
```

---

## 性能目标

- ⚡ **响应时间**：< 2 秒（关键任务如 MOB）
- 🎯 **准确率**：> 95%（合规性检查）
- 🔄 **可用性**：99.9%（24/7 运行）
- 📊 **吞吐量**：100+ 传感器/秒

---

## 安全与合规

### 海事法规
- ✅ **COLREGs**：国际海上避碰规则
- ✅ **ISM Code**：国际安全管理规则
- ✅ **SOLAS**：海上人命安全公约

### 数据安全
- 🔐 传输加密（TLS）
- 🔒 数据脱敏（敏感信息）
- 📝 操作日志审计

---

## 未来路线图

### Phase 1（当前）
- ✅ Layer 1 基础交互界面
- ✅ Layer 2 核心 4 个 Agent
- ✅ Layer 3 开发平台雏形

### Phase 2
- 🔜 集成真实 LLM API（OpenAI/Anthropic）
- 🔜 NVIDIA Isaac Sim 集成
- 🔜 ROS 2 通信总线

### Phase 3
- 🔜 AR 增强现实（Vision Pro/XR）
- 🔜 边缘 AI 加速（NVIDIA Jetson）
- 🔜 船队管理（多船协同）

---

## 贡献指南

我们欢迎贡献！请阅读 [CONTRIBUTING.md](./CONTRIBUTING.md)。

---

## 许可证

MIT License

---

## 联系方式

- 📧 Email: poseidon-x@example.com
- 💬 Discord: [Poseidon-X Community](https://discord.gg/poseidon-x)
- 🐙 GitHub: [github.com/poseidon-x](https://github.com/poseidon-x)

---

**Poseidon-X** - *我们不写死功能，我们培育智能体。* 🌊🤖
