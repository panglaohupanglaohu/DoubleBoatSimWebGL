# PM分解 — project_manager

任务: 给build团队的PM发一个任务，navigation-v2.html页面的chat AI ，添加智能体选择，如果智能体选择的LLM模型可用就高亮并且显示名称
步骤: pm_decompose
Agent: build_pm

---

📋 任务: 63a94127-5b7
🤖 Agent: PM (project_manager)
📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
⏱️ 超时: 300s
────────────────────────────────────────────────────────────
📝 提示词:
  你是 PoseidonX 系统的 PM (project_manager)。
  请执行以下开发任务:
  
  你是项目经理 (PM)。请对以下任务进行分解和规划:
  
  ## 任务
  给build团队的PM发一个任务，navigation-v2.html页面的chat AI ，添加智能体选择，如果智能体选择的LLM模型可用就高亮并且显示名称
  给build团队的PM发一个任务，navigation-v2.html页面的chat AI ，添加智能体选择，如果智能体选择的LLM模型可用就高亮并且显示名称
  
  ## 要求
  1. 分析任务需求，拆解为可执行的子步骤
  2. 识别技术风险和依赖关系
  3. 为后续研究人员、架构师、开发者提供清晰的指导
  4. 输出一份结构化的任务分解文档 (Markdown 格式)
  
  项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  后端: src/backend/ (Python FastAPI)
  前端: src/frontend/ (HTML + JS)
  
  
  项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  后端: src/backend/ (Python FastAPI)
  前端: src/frontend/ (HTML + JS)
  完成后运行: PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short
  
────────────────────────────────────────────────────────────
⏳ 正在启动 Claude Code CLI...

<think>
作为 PM 需要先分析任务需求，查看 navigation-v2.html 的现有 chat AI 实现和后端 API 来理解当前架构，然后才能制定详细的任务分解。
</think>

# PoseidonX 任务分解文档

## 任务概述
在 `navigation-v2.html` 页面的 Chat AI 组件中添加智能体选择功能，支持 LLM 模型选择并显示可用性状态。

---

## 需求分析

### 核心功能
1. **智能体选择器 UI** - 下拉菜单或卡片列表展示可用智能体
2. **可用性检测** - 实时检测 LLM 模型连接状态
3. **视觉反馈** - 可用模型高亮显示 + 显示模型名称
4. **状态同步** - 前端状态与后端模型池同步

### 技术依赖
- 后端：`model_pool.json` 模型配置 + 模型健康检查 API
- 前端：Chat AI 组件 + 状态轮询机制

---

## 任务分解

### Phase 1: 需求调研与架构分析 (Researcher)
**负责人**: `marine_researcher`

#### 子任务
1.1 分析现有 `navigation-v2.html` 的 Chat AI 实现
   - 查看当前聊天界面结构
   - 识别消息传递机制
   - 确定 UI 组件位置

1.2 调研后端模型池架构
   - 查看 `config/model_pool.json` 配置格式
   - 分析模型健康检查 API 接口
   - 确定状态返回格式

1.3 研究现有智能体系统
   - 查看 `src/backend/agents/skill_registry.py`
   - 分析智能体与 LLM 的映射关系

**产出**: 架构分析报告 + 接口定义

---

### Phase 2: 架构设计 (System Architect)
**负责人**: `system_architect`

#### 子任务
2.1 设计前端组件架构
```
ChatAIComponent
├── AgentSelector (新组件)
│   ├── AgentList (渲染智能体列表)
│   ├── AgentItem (单个智能体卡片)
│   └── StatusIndicator (可用性状态)
└── MessagePanel (现有组件，扩展)
```

2.2 设计后端 API 接口
```python
GET /api/models/status
Response: {
  "models": [
    {"id": "agent_1", "name": "导航助手", "llm": "claude-3", "available": true},
    {"id": "agent_2", "name": "气象顾问", "llm": "gpt-4", "available": false}
  ]
}
```

2.3 定义状态同步机制
- 轮询间隔：5 秒
- WebSocket 推送 (可选)
- 本地缓存策略

**产出**: 架构设计文档 + API 接口定义

---

### Phase 3: 后端实现 (Developer)
**负责人**: `code_writer`

#### 子任务
3.1 创建模型状态 API
- 文件：`src/backend/channels/api_models.py` (新建)
- 功能：
  - 读取 `model_pool.json`
  - 检测 LLM 连接状态
  - 返回智能体 + 模型状态

3.2 集成到主 API
- 文件：`src/backend/main.py`
- 添加路由：`GET /api/models/status`

3.3 单元测试
- 文件：`tests/unit/test_api_models.py`
- 覆盖场景：
  - 模型池读取
  - 连接状态检测
  - 错误处理

**技术风险**: 
- LLM API 调用可能超时 → 设置 3 秒超时
- 模型池配置缺失 → 提供默认配置

---

### Phase 4: 前端实现 (Developer)
**负责人**: `code_writer`

#### 子任务
4.1 创建 AgentSelector 组件
- 文件：`src/frontend/js/agent-selector.js` (新建)
- 功能：
  - 从 API 获取智能体列表
  - 渲染可用/不可用状态
  - 点击选择智能体

4.2 集成到 navigation-v2.html
- 在 Chat AI 区域添加选择器容器
- 初始化 AgentSelector 组件
- 绑定事件处理器

4.3 实现状态可视化
- 可用：绿色高亮 + ✓ 图标
- 不可用：灰色 + × 图标
- 加载状态：旋转动画

4.4 状态轮询机制
- 每 5 秒刷新模型状态
- 实时更新 UI
- 错误重试机制

**技术风险**:
- 跨域问题 → 配置 CORS
- 异步加载 → 使用 Promise 链

---

### Phase 5: 测试与验收 (QA Engineer)
**负责人**: `qa_engineer`

#### 子任务
5.1 单元测试
- 后端 API 测试
- 前端组件测试

5.2 集成测试
- 端到端流程测试
- 状态同步测试

5.3 UI/UX 验收
- 视觉一致性
- 交互流畅度

**执行命令**:
```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short
```

---

## 依赖关系图

```
Phase 1 (Researcher)
    ↓
Phase 2 (Architect) ← 依赖 Phase 1 输出
    ↓
    ├→ Phase 3 (Backend)
    └→ Phase 4 (Frontend) ← 依赖 Phase 2 输出 + Phase 3 API
         ↓
Phase 5 (QA) ← 依赖 Phase 3 + Phase 4 输出
```

---

## 时间估算

| Phase | 负责人 | 预估时间 |
|-------|--------|----------|
| 1 | marine_researcher | 2 小时 |
| 2 | system_architect | 3 小时 |
| 3 | code_writer (Backend) | 4 小时 |
| 4 | code_writer (Frontend) | 5 小时 |
| 5 | qa_engineer | 3 小时 |
| **总计** | | **17 小时** |

---

## 验收标准

1. ✅ Chat AI 界面显示智能体选择器
2. ✅ 可用模型绿色高亮 + 显示名称
3. ✅ 不可用模型灰色显示 + 提示"不可用"
4. ✅ 状态每 5 秒自动刷新
5. ✅ 选择智能体后聊天使用对应模型
6. ✅ 所有测试通过

---

## 下一步行动

**立即执行**:
1. 启动 `marine_researcher` 进行 Phase 1 分析
2. 启动 `system_architect` 进行 Phase 2 设计

**准备材料**:
- 当前 `navigation-v2.html` 代码
- `config/model_pool.json` 配置
- 后端 API 文档
