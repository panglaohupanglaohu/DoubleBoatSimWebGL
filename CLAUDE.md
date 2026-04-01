# 深海远洋双体船舶智能综合信息系统 (PoseidonX)

## 项目概述

- **项目路径**: `/Users/panglaohu/Downloads/DoubleBoatClawSystem`
- **项目类型**: AI Native 海事 CPS 信息系统
- **后端**: Python 3.14 + FastAPI, 入口 `src/backend/main.py`
- **前端**: Three.js 数字孪生 + MapLibre GL 海图 + OpenBridge HMI
- **存储**: SQLite WAL + DuckDB + Parquet + S3/MinIO
- **测试**: pytest (1203+ 单元测试), 需要 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`
- **Python 环境**: `source venv/bin/activate`

## 关键命令

```bash
# 激活环境
source venv/bin/activate

# 运行测试
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short

# 启动后端
cd src/backend && python main.py --port 8080

# 启动前端
npx vite --config vite.config.mjs
```

## 代码结构

```
src/backend/
├── main.py                    # FastAPI 入口 (Poseidon 服务)
├── channels/                  # 46 个 MarineChannel 模块
│   ├── marine_base.py         # MarineChannel 基类 (所有 Channel 继承)
│   ├── marine_message_bus.py  # 内部消息总线
│   ├── decision_orchestrator.py  # L3 决策编排
│   ├── colregs_brain.py       # L3 COLREGs 避碰
│   ├── intelligent_engine.py  # L3 机舱诊断
│   ├── wpc_attitude_control.py   # L4 穿浪双体船姿态
│   ├── openbridge_hmi.py      # L5 OpenBridge HMI
│   └── ...                    # 其他 Channel
├── storage/                   # 数据湖仓 + 事件存储 + 云同步
└── adapters/                  # WorldMonitor 适配器

src/frontend/
├── digital-twin/              # 数字孪生 (Three.js)
│   ├── layer1-interface/      # UI 组件
│   ├── layer2-agents/         # 前端 Agent
│   └── layer3-platform/       # LLM/仿真平台
└── *.html                     # 页面入口

tests/
├── unit/                      # 单元测试
└── integration/               # 集成测试
```

## 7-Agent 团队

| Agent | 角色 | 命令 | 配置文件 |
|-------|------|------|---------|
| `chief_director` | 项目总监 | `claude --agent chief_director` | `.claude/agents/chief_director.md` |
| `system_architect` | 架构设计师 | `claude --agent system_architect` | `.claude/agents/system_architect.md` |
| `marine_researcher` | 海洋研究员 | `claude --agent marine_researcher` | `.claude/agents/marine_researcher.md` |
| `dev_lead` | 开发主管 | `claude --agent dev_lead` | `.claude/agents/dev_lead.md` |
| `code_writer` | 代码开发者 | `claude --agent code_writer` | `.claude/agents/code_writer.md` |
| `qa_engineer` | 测试工程师 | `claude --agent qa_engineer` | `.claude/agents/qa_engineer.md` |
| `doc_writer` | 文档工程师 | `claude --agent doc_writer` | `.claude/agents/doc_writer.md` |

### 协作流程

```
用户需求 → chief_director (任务拆解)
    ├→ marine_researcher (领域分析) → system_architect (架构设计)
    │                                       ↓
    ├→ dev_lead (任务分配) → code_writer (代码实现)
    │                                       ↓
    ├→ qa_engineer (测试验证) ←─────────────┘
    │           ↓
    └→ doc_writer (文档更新) ←── 所有 Agent 的产出
```

### 在终端启动 Agent

```bash
# 在终端中启动单个 Agent
claude --agent chief_director

# 在 VS Code 中，也可以通过 Tasks 面板启动
# 每个 Agent 有对应的 VS Code Task
```

### Agent 间协作方式

Agent 之间通过 **文件系统** 协作:
- 任务跟踪: `.claude/agent_workspaces/` 目录
- 代码变更: 直接修改 `src/` 下的源文件
- 测试结果: 运行 pytest 获取实时状态
- 文档: `docs/` 目录
- 架构决策: `docs/architecture/` 目录

## 团队规则

1. **修改前运行测试** — 确认基线是绿色的
2. **修改后运行测试** — 确认没有回归
3. **向后兼容** — 新参数必须有默认值
4. **Channel 规范** — 所有 Channel 继承 `MarineChannel`，实现 `process_event()` 和 `get_status()`
5. **pytest 环境** — 必须使用 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`
