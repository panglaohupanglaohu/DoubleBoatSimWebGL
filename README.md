# 🚢 DoubleBoatClawSystem

**深远海双体船智能信息系统 - 数字孪生平台**

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 📋 项目概述

DoubleBoatClawSystem 是一个面向深远海大科学设施的智能信息系统，基于数字孪生技术实现：

- 🌊 **双体船 3D 可视化** - WebGL 实时渲染
- 📡 **多源数据集成** - AIS/NMEA/传感器数据融合
- 🤖 **AI Agent 原生** - 自然语言交互与智能决策
- 🚨 **实时报警监控** - 四级报警系统
- 📊 **设备健康管理** - PHM 预测性维护

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户交互层 (Frontend)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Digital Twin Dashboard (Three.js + React)          │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    智能服务层 (Agent Layer)                  │
│  领航员 Agent │ 轮机长 Agent │ 安全官 Agent                 │
├─────────────────────────────────────────────────────────────┤
│                    数据处理层 (Backend)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Poseidon Server (Python FastAPI + WebSocket)       │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    设备接口层 (Data Sources)                 │
│  AIS 数据源 │ NMEA 解析器 │ 仿真传感器                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- Git

### 1. 克隆项目

```bash
cd /Users/panglaohu/Downloads/DoubleBoatClawSystem
```

### 2. 安装后端依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -e ".[dev]"
```

### 3. 安装前端依赖

```bash
npm install
```

### 4. 启动后端服务器

```bash
# 启动 Poseidon Server
python src/backend/main.py --host 0.0.0.0 --port 8080
```

### 5. 启动前端开发服务器

```bash
# 启动 Vite 开发服务器
npm run dev
```

### 6. 访问系统

- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8080
- **API 文档**: http://localhost:8080/docs

---

## 📁 项目结构

```
DoubleBoatClawSystem/
├── README.md                    # 本文件
├── 12HOUR_SPRINT_PLAN.md        # 12 小时冲刺计划
├── package.json                 # 前端依赖
├── pyproject.toml               # 后端依赖
├── docs/                        # 文档
│   ├── requirements_analysis.md # 需求分析
│   ├── gap_analysis.md          # 差距分析
│   └── architecture.md          # 架构设计
├── src/                         # 源代码
│   ├── frontend/                # 前端代码
│   │   ├── digital-twin/        # 数字孪生 3D
│   │   ├── dashboard/           # 仪表盘 UI
│   │   └── components/          # 组件
│   ├── backend/                 # 后端代码
│   │   ├── api/                 # REST API
│   │   ├── websocket/           # WebSocket
│   │   ├── channels/            # Channel 实现
│   │   ├── alarm/               # 报警引擎
│   │   └── phm/                 # PHM 模块
│   └── simulation/              # 仿真环境
│       ├── ais/                 # AIS 模拟
│       ├── nmea/                # NMEA 模拟
│       └── sensor/              # 传感器模拟
├── tests/                       # 测试用例
│   ├── unit/                    # 单元测试
│   ├── integration/             # 集成测试
│   └── e2e/                     # 端到端测试
├── config/                      # 配置文件
└── scripts/                     # 部署脚本
```

---

## 🎯 核心功能

### 1. 数字孪生可视化

- 3D 双体船模型 (Three.js)
- 实时数据叠加
- 可交互视角 (旋转/缩放/平移)

### 2. AIS 船舶追踪

- 实时 AIS 目标显示
- CPA/TCPA 碰撞预警
- 航迹预测

### 3. 主机监控

- RPM/温度/压力实时数据
- 燃油消耗分析
- 四级报警系统

### 4. 导航数据

- GPS 位置
- 航向/航速
- 水深/测深

### 5. 自然语言交互

- 语音/文本查询
- 智能问答
- 指令执行

---

## 🧪 测试

### 运行单元测试

```bash
# Python 测试
pytest tests/unit/ -v

# JavaScript 测试
npm test
```

### 运行集成测试

```bash
pytest tests/integration/ -v
```

### 运行端到端测试

```bash
pytest tests/e2e/ -v
```

---

## 📊 API 接口

### REST API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/sensors` | GET | 获取传感器列表 |
| `/api/v1/sensors/{id}/data` | GET | 获取传感器数据 |
| `/api/v1/ais/targets` | GET | 获取 AIS 目标 |
| `/api/v1/engine/status` | GET | 获取主机状态 |
| `/api/v1/alerts` | GET | 获取报警列表 |
| `/api/v1/commands` | POST | 发送控制指令 |

### WebSocket

- **连接**: `ws://localhost:8765`
- **订阅**: `{"action": "subscribe", "channel": "navigation_data"}`
- **推送**: `{"type": "data_update", "channel": "...", "data": {...}}`

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 👥 团队

**Poseidon-X 智能船舶系统团队**

- **CaptainCatamaran** 🐱⛵ - 总协调
- **Sovereign** - 首席架构师
- **Deep-Sea Coder** - 技术开发
- **Sentinels** - 安全审计
- **Deployment Master** - 交付经理

---

## 📬 联系方式

- **项目主页**: https://github.com/your-org/double-boat-claw-system
- **问题反馈**: https://github.com/your-org/double-boat-claw-system/issues

---

## 🗓️ 开发日志

### 2026-03-13 - 12 小时冲刺启动

- ✅ 需求分析完成
- ✅ 差距分析完成
- ✅ 项目骨架创建
- ⏳ 开发中...

---

*Last updated: 2026-03-13 18:55*
