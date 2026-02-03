# Poseidon-X 项目结构

## 🌊 完整的 Software 3.0 智能船舶系统架构

---

## 📂 目录树

```
DoubleBoatSimWebGL/
│
├── 📱 核心系统（src/poseidon/）
│   ├── 🎯 PoseidonX.js                    # 主系统入口（统一API）
│   ├── 📖 demo.js                         # 演示程序（9个Demo）
│   ├── 📦 index.js                        # 导出文件（统一导出）
│   │
│   ├── 🖥️ layer1-interface/               # Layer 1: For End User (1)
│   │   │                                  # 统一全知交互界面
│   │   ├── BridgeChat.js                 # 🌊 舰桥对话中心
│   │   │                                  #    - 多模态输入（语音/文本/手势）
│   │   │                                  #    - 自然语言查询
│   │   │                                  #    - 智能路由到Agent
│   │   │
│   │   ├── DigitalTwinMap.js             # 🗺️ 数字孪生海图
│   │   │                                  #    - 3D实时渲染
│   │   │                                  #    - AIS目标可视化
│   │   │                                  #    - AI智能高亮
│   │   │                                  #    - AR增强现实（未来）
│   │   │
│   │   └── ContextWindow.js              # 🧠 上下文窗口（RAM）
│   │                                      #    - 传感器数据→文本
│   │                                      #    - 智能压缩
│   │                                      #    - 优先级管理
│   │
│   ├── 🤖 layer2-agents/                  # Layer 2: For End User (N)
│   │   │                                  # The AI Crew（数字船员）
│   │   ├── AgentBase.js                  # 🔷 智能体基类
│   │   │                                  #    - Vibe（人格定义）
│   │   │                                  #    - Tool Use（工具使用）
│   │   │                                  #    - Memory（记忆系统）
│   │   │
│   │   ├── NavigatorAgent.js             # ⚓ 领航员智能体
│   │   │                                  #    Vibe: "极致安全与效率的追求者"
│   │   │                                  #    职责: 避碰、路径规划、气象路由
│   │   │                                  #    工具: CPA计算、风险评估、航线优化
│   │   │                                  #    知识: COLREGs国际海上避碰规则
│   │   │
│   │   ├── EngineerAgent.js              # ⚙️ 轮机长智能体
│   │   │                                  #    Vibe: "能听懂机器呻吟的老轨"
│   │   │                                  #    职责: PHM、能效、预测性维护
│   │   │                                  #    工具: 排温分析、健康评分、维护计划
│   │   │                                  #    知识: 设备规格、故障模式
│   │   │
│   │   ├── StewardAgent.js               # 🏠 大管家智能体
│   │   │                                  #    Vibe: "细致入微的后勤总管"
│   │   │                                  #    职责: 仓储、伙食、环境控制
│   │   │                                  #    工具: 库存管理、菜单生成、环境监控
│   │   │                                  #    知识: 消耗速率、饮食偏好
│   │   │
│   │   ├── SafetyAgent.js                # 🛡️ 安全官智能体
│   │   │                                  #    Vibe: "永不眨眼的守望者"
│   │   │                                  #    职责: 视觉监控、应急响应
│   │   │                                  #    工具: 视频分析、警报触发、逃生路线
│   │   │                                  #    知识: 应急程序、响应时间标准
│   │   │                                  #    权限: 紧急情况下可直接触发警报
│   │   │
│   │   └── AgentOrchestrator.js          # 🎭 编排系统（LangGraph风格）
│   │                                      #    - 智能路由
│   │                                      #    - 多Agent协作
│   │                                      #    - 工作流管理
│   │
│   └── 🧬 layer3-platform/                # Layer 3: For Developer (X)
│       │                                  # Intelligence Foundry（智能工厂）
│       ├── VibeGenerator.js              # 🧬 Vibe生成器
│       │                                  #    输入: 自然语言需求
│       │                                  #    输出: Agent代码+配置+测试
│       │                                  #    集成: Cursor Composer + Replit
│       │
│       ├── SimulationValidator.js        # 🔬 仿真验证器（编译器）
│       │                                  #    场景: 暴风雨、大雾、设备故障...
│       │                                  #    测试: 1000+ 虚拟航行
│       │                                  #    标准: 85%通过率
│       │
│       └── LLMJudge.js                   # ⚖️ AI裁判 + 数据闭环
│                                          #    评估: 正确性、合规性、决策质量
│                                          #    闭环: 实船数据→测试用例→优化
│                                          #    法规: COLREGs, ISM, SOLAS
│
├── 🎨 演示和测试
│   ├── poseidon-x-demo.html              # 交互式Web演示页面
│   │                                      #    - 可视化控制面板
│   │                                      #    - 实时状态监控
│   │                                      #    - 控制台输出
│   │
│   └── src/poseidon/demo.js              # 9个演示程序
│                                          #    - 基础使用
│                                          #    - 任务执行
│                                          #    - 并行任务
│                                          #    - Digital Twin
│                                          #    - 应急场景
│                                          #    - 开发模式
│
├── 🐳 部署配置
│   ├── Dockerfile.agent                   # Agent Docker镜像
│   ├── docker-compose.yml                 # 本地开发环境
│   ├── .env.example                       # 环境变量模板
│   └── deployment/
│       └── navigator-agent.yaml           # K8s部署配置（示例）
│
├── 📚 文档（3000+ 行）
│   ├── POSEIDON-X-ARCHITECTURE.md        # 详细架构文档（620+行）
│   ├── README-POSEIDON-X.md              # 项目说明（460+行）
│   ├── QUICK-START-POSEIDON-X.md         # 快速开始指南（310+行）
│   ├── VIBE-CODING-GUIDE.md              # Vibe Coding教程（620+行）
│   └── POSEIDON-X-REFACTORING-SUMMARY.md # 重构总结报告
│
└── 🔧 原有系统（保留，可选择性集成）
    ├── src/ship/ShipController.js         # 原船舶控制器
    ├── src/physics/                       # 物理引擎
    ├── src/data/                          # 数据接口
    └── ...                                # 其他模块
```

---

## 🎯 文件功能说明

### 核心系统文件

| 文件 | 大小 | 功能 | 关键方法 |
|------|------|------|----------|
| `PoseidonX.js` | ~400行 | 主系统，统一API | `initialize()`, `executeTask()` |
| `BridgeChat.js` | ~360行 | 舰桥对话，多模态输入 | `sendMessage()`, `toggleVoiceInput()` |
| `DigitalTwinMap.js` | ~280行 | 3D可视化，智能高亮 | `addAISTarget()`, `highlight()` |
| `ContextWindow.js` | ~280行 | 上下文管理，智能压缩 | `addSensorData()`, `getContext()` |
| `NavigatorAgent.js` | ~430行 | 领航员，避碰决策 | `execute()`, `_handleCollisionQuery()` |
| `EngineerAgent.js` | ~340行 | 轮机长，PHM诊断 | `execute()`, `_handleMainEngineQuery()` |
| `StewardAgent.js` | ~280行 | 大管家，仓储伙食 | `execute()`, `updateInventory()` |
| `SafetyAgent.js` | ~350行 | 安全官，应急响应 | `execute()`, `monitorCamera()` |
| `AgentOrchestrator.js` | ~320行 | 编排系统，智能路由 | `executeTask()`, `executeParallel()` |
| `VibeGenerator.js` | ~250行 | 代码生成器 | `generateAgent()` |
| `SimulationValidator.js` | ~320行 | 仿真验证器 | `validateAgent()` |
| `LLMJudge.js` | ~280行 | AI裁判，评估闭环 | `evaluate()` |

---

## 🔄 数据流图

### 用户查询流程

```
用户输入
  │
  │ "右舷那艘船有风险吗？"
  ↓
┌─────────────────────────────┐
│ Layer 1: Bridge Chat       │
│ - 接收输入（文本/语音）     │
│ - 添加到对话历史            │
└─────────────────────────────┘
  │
  ↓
┌─────────────────────────────┐
│ Context Window             │
│ - 获取全船状态              │
│ - 构建上下文（传感器→文本）│
└─────────────────────────────┘
  │
  ↓
┌─────────────────────────────┐
│ Agent Orchestrator         │
│ - 智能路由（关键词匹配）    │
│ - 选择: Navigator Agent    │
└─────────────────────────────┘
  │
  ↓
┌─────────────────────────────┐
│ Navigator Agent            │
│ 1. 感知: 读取AIS数据        │
│ 2. 推理: 调用LLM分析        │
│ 3. 行动: 使用工具计算CPA    │
│ 4. 响应: 生成专业建议       │
└─────────────────────────────┘
  │
  ↓
┌─────────────────────────────┐
│ Digital Twin Map           │
│ - 高亮目标船舶              │
│ - 显示CPA/TCPA             │
└─────────────────────────────┘
  │
  ↓
用户看到回复
"无风险，CPA 2.5海里，建议在其船尾通过。"
```

### 传感器数据流

```
物理传感器（2000+）
  │
  ├── NMEA (GPS, AIS, Gyro...)
  ├── Modbus (主机, 泵, 发电机...)
  └── CCTV (视频流)
  │
  ↓
┌─────────────────────────────┐
│ 数据采集层                  │
│ - ROS 2 通信总线            │
│ - OPC UA 协议               │
└─────────────────────────────┘
  │
  ↓
┌─────────────────────────────┐
│ Context Window             │
│ - 原始数据 → 文本           │
│   温度=380°C → "主机排温380°C，
│                 正常范围350-400°C"
└─────────────────────────────┘
  │
  ↓
┌─────────────────────────────┐
│ LLM (GPT-4/Claude)         │
│ - 阅读上下文                │
│ - 推理分析                  │
│ - 生成建议                  │
└─────────────────────────────┘
  │
  ↓
Agent 执行决策
```

---

## 🎭 Agent 协作图

```
                    用户查询
                       ↓
              ┌────────────────┐
              │ Bridge Chat    │
              │  (统一入口)    │
              └────────────────┘
                       ↓
              ┌────────────────┐
              │  Orchestrator  │
              │   (智能路由)   │
              └────────────────┘
                       ↓
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
  ┌─────────┐    ┌──────────┐   ┌─────────┐
  │Navigator│    │ Engineer │   │ Steward │
  │  Agent  │    │  Agent   │   │  Agent  │
  └─────────┘    └──────────┘   └─────────┘
        ↓              ↓              ↓
  ┌─────────┐    ┌──────────┐   ┌─────────┐
  │ AIS数据 │    │ 传感器   │   │ RFID库存│
  │ 雷达    │    │ 主机     │   │ 舱室环境│
  └─────────┘    └──────────┘   └─────────┘

  所有Agent都可以访问 ┌────────────┐
                      │ Safety     │
                      │ Agent      │
                      │ (最高权限) │
                      └────────────┘
                            ↓
                      ┌────────────┐
                      │ CCTV视频流 │
                      │ 应急系统   │
                      └────────────┘
```

---

## 🧬 开发平台流程

```
开发者需求（自然语言）
  │
  │ "创建一个监控海水淡化的Agent"
  ↓
┌─────────────────────────────┐
│ X1: Vibe Generator         │
│ - 解析需求                  │
│ - 生成Agent代码             │
│ - 生成工具定义              │
│ - 生成Dockerfile            │
└─────────────────────────────┘
  │
  ↓
  生成的Agent代码
  │
  ↓
┌─────────────────────────────┐
│ X2: Simulation Validator   │
│ - 加载Agent                 │
│ - 运行100+场景测试          │
│ - 检查响应时间/准确性       │
└─────────────────────────────┘
  │
  ├─→ 通过 ✅
  │     ↓
  │   ┌─────────────────────────────┐
  │   │ X3: LLM Judge              │
  │   │ - 评估合规性（COLREGs）    │
  │   │ - 评估决策质量             │
  │   │ - 生成优化建议             │
  │   └─────────────────────────────┘
  │     │
  │     ├─→ 通过 ✅ → 部署到船上
  │     └─→ 失败 ❌ ↓
  │
  └─→ 失败 ❌
        ↓
  优化Vibe，重新生成
        ↓
  回到 X1
```

---

## 📊 层级功能矩阵

| 功能类别 | Layer 1 | Layer 2 | Layer 3 |
|----------|---------|---------|---------|
| **目标用户** | 终端用户（船长、船员） | 终端用户 | 开发者 |
| **核心价值** | 简化交互 | 智能决策 | 快速开发 |
| **技术特点** | 多模态输入 | Agent自主推理 | 代码生成 |
| **交付物** | UI界面 | 数字船员 | 开发工具 |
| **学习成本** | 零（自然语言） | 零（自动化） | 低（Vibe描述） |
| **可扩展性** | 固定 | 高（新增Agent） | 极高（自动生成） |

---

## 🔧 关键依赖

### 运行时依赖

```json
{
  "three": "^0.182.0",        // 3D渲染
  "cannon-es": "^0.20.0",     // 物理引擎
  "lil-gui": "^0.21.0"        // UI控制面板
}
```

### 开发依赖

```json
{
  "serve": "^14.2.0"          // 本地开发服务器
}
```

### 外部服务（可选）

- **LLM API**: OpenAI GPT-4 / Anthropic Claude
- **Vector DB**: Pinecone / Qdrant (长期记忆)
- **Monitoring**: LangSmith (Agent性能追踪)
- **Simulation**: NVIDIA Isaac Sim (物理仿真)

---

## 🎯 部署拓扑

### 开发环境

```
本地电脑
  │
  ├── Browser (http://127.0.0.1:8080)
  │   └── poseidon-x-demo.html
  │
  └── Node.js Server (npm start)
      └── 提供静态文件
```

### 生产环境（船端 Edge）

```
船载服务器（加固型工业服务器）
  │
  ├── K3s Cluster
  │   ├── Navigator Agent Pod
  │   ├── Engineer Agent Pod
  │   ├── Steward Agent Pod
  │   ├── Safety Agent Pod
  │   └── Orchestrator Pod
  │
  ├── ROS 2 通信总线
  │   └── 连接 2000+ 传感器
  │
  └── PostgreSQL + Redis
      └── Agent 记忆存储
```

### 生产环境（岸端 Cloud）

```
云服务器
  │
  ├── Intelligence Foundry
  │   ├── Vibe Generator (生成新Agent)
  │   ├── Simulation Validator (测试)
  │   └── LLM Judge (评估)
  │
  ├── NVIDIA Isaac Sim
  │   └── OceanSim 物理仿真
  │
  └── 数据闭环系统
      └── 实船数据收集+分析
```

---

## 📈 可扩展性

### 新增 Agent（5分钟）

```bash
# 方式1: Vibe Generator（推荐）
const generation = await poseidon.generateAgent(`
  创建一个监控XX的Agent...
`);

# 方式2: 手动继承
class MyAgent extends AgentBase {
  constructor() {
    super({ vibe: "..." });
  }
}

# 方式3: 从模板复制
cp NavigatorAgent.js MyAgent.js
# 修改 Vibe 和 工具定义
```

### 新增工具（1分钟）

```javascript
agent.registerTool('myTool', async (params) => {
  // 工具实现
  return result;
}, 'Tool description');
```

### 新增测试场景（2分钟）

```javascript
validator.scenarios.set('my_scenario', {
  name: '我的测试场景',
  type: 'custom',
  difficulty: 'medium',
  conditions: { /* 场景条件 */ },
  successCriteria: (result) => { /* 判断逻辑 */ }
});
```

---

## 🎓 代码质量

### 设计模式

- ✅ **事件驱动**：所有组件继承 `EventEmitter`
- ✅ **依赖注入**：通过构造函数配置
- ✅ **单一职责**：每个Agent专注一个领域
- ✅ **开闭原则**：易扩展，不修改基类
- ✅ **策略模式**：工具可插拔

### 代码规范

- ✅ 完整的 JSDoc 注释
- ✅ 清晰的变量命名
- ✅ 模块化设计
- ✅ 错误处理
- ✅ 日志输出

---

## 🚀 启动命令速查

```bash
# 基础演示
npm start
# 浏览器打开 http://127.0.0.1:8080/poseidon-x-demo.html

# Docker开发环境
docker-compose up -d

# K8s生产部署
kubectl apply -f deployment/navigator-agent.yaml

# 查看日志
docker-compose logs -f navigator-agent
kubectl logs -f deployment/navigator-agent -n poseidon-x
```

---

## 📞 获取帮助

| 问题类型 | 资源 |
|----------|------|
| 快速开始 | [QUICK-START-POSEIDON-X.md](./QUICK-START-POSEIDON-X.md) |
| 架构理解 | [POSEIDON-X-ARCHITECTURE.md](./POSEIDON-X-ARCHITECTURE.md) |
| 开发Agent | [VIBE-CODING-GUIDE.md](./VIBE-CODING-GUIDE.md) |
| 重构总结 | [POSEIDON-X-REFACTORING-SUMMARY.md](./POSEIDON-X-REFACTORING-SUMMARY.md) |
| 代码示例 | `src/poseidon/demo.js` |

---

## 🎉 重构完成！

**Poseidon-X** 智能船舶系统已完整构建，包含：

- ✅ **3层架构**（1+N+X）
- ✅ **12个核心组件**
- ✅ **4个AI智能体**
- ✅ **26个文件**（~8,300行代码）
- ✅ **5份完整文档**（~3,000行）
- ✅ **完整部署方案**（Docker + K8s）
- ✅ **交互式演示**（poseidon-x-demo.html）

**下一步**: 启动演示页面体验 Software 3.0 的魅力！ 🌊🤖
