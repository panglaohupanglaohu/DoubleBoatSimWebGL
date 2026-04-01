# PoseidonX Claude Code Agent 团队工作区

## 概述

本目录是 7 个 Claude Code 智能体的独立工作空间。  
智能体的目标项目是父目录: `/Users/panglaohu/Downloads/DoubleBoatClawSystem`

## 使用方法

```bash
# 进入本目录
cd /Users/panglaohu/Downloads/DoubleBoatClawSystem/claude-agent-team

# 启动单个 Agent
claude --agent chief_director     # 项目总监
claude --agent system_architect   # 架构设计师
claude --agent marine_researcher  # 海洋研究员
claude --agent dev_lead           # 开发主管
claude --agent code_writer        # 代码开发者
claude --agent qa_engineer        # 测试工程师
claude --agent doc_writer         # 文档工程师
```

## Agent 团队

| Agent | 角色 | 职责 |
|-------|------|------|
| `chief_director` | 项目总监 | 任务分解、进度跟踪、质量把控、跨 Agent 协调 |
| `system_architect` | 架构设计师 | L0-L5 架构、技术选型、接口规范 |
| `marine_researcher` | 海洋研究员 | WPC/COLREGs/EEXI 领域专家 |
| `dev_lead` | 开发主管 | 代码审查、任务分配 |
| `code_writer` | 代码开发者 | 功能开发、Bug 修复、单元测试 |
| `qa_engineer` | 测试工程师 | 测试执行、回归测试、Bug 报告 |
| `doc_writer` | 文档工程师 | 架构文档、API 文档 |

## 目标项目

```
/Users/panglaohu/Downloads/DoubleBoatClawSystem/
├── src/backend/          # Python 3.14 FastAPI 后端
│   ├── main.py           # 入口
│   ├── channels/         # 46 个 MarineChannel
│   ├── storage/          # 数据湖仓
│   └── adapters/         # 外部适配器
├── src/frontend/         # Three.js 数字孪生
├── tests/                # pytest 1203+ 测试
└── config/               # 配置文件
```

## 关键命令

```bash
# 激活 Python 环境
source /Users/panglaohu/Downloads/DoubleBoatClawSystem/venv/bin/activate

# 运行测试
cd /Users/panglaohu/Downloads/DoubleBoatClawSystem
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short

# 启动后端
cd /Users/panglaohu/Downloads/DoubleBoatClawSystem/src/backend && python main.py --port 8080
```
