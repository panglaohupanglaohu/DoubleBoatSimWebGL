# 🌊 Poseidon 数字孪生集成方案

**集成目标：** 将 marine_engineer_agent 智能体技能集成到 DoubleBoatSimWebGL 数字孪生项目

**创建日期：** 2026-03-10  
**版本：** v1.0

---

## 📋 集成架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    DoubleBoatSimWebGL 前端                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ marine-     │  │ diagnostic  │  │ ai-panel    │             │
│  │ dashboard   │  │             │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                          │                                      │
│                    (HTTP/WebSocket)                             │
└──────────────────────────┼──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│              Poseidon API Gateway (扩展版)                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  poseidon_server.py (扩展支持数字孪生 API)                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│  ┌───────────────────────┼───────────────────────────────────┐ │
│  │           marine_engineer_agent 技能模块                   │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │ │
│  │  │ fault_      │  │ query_      │  │ performance │       │ │
│  │  │ diagnosis   │  │ answer      │  │ _cache      │       │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │ │
│  │  ┌─────────────┐  ┌─────────────┐                        │ │
│  │  │ marine_     │  │ twin_       │  ← 新增数字孪生技能     │ │
│  │  │ config      │  │ controller  │                        │ │
│  │  └─────────────┘  └─────────────┘                        │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    知识库 & 数据源                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ 船舶知识    │  │ 故障库      │  │ 传感器数据  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 集成内容

### 1. API 服务扩展

**文件：** `agents/marine_engineer/poseidon_server_twins.py`

**新增 API 端点：**

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/twins/scene` | GET | 获取数字孪生场景状态 |
| `/api/v1/twins/scene/apply` | POST | 应用场景配置 |
| `/api/v1/twins/boat/control` | POST | 船只控制 |
| `/api/v1/twins/sensor/data` | GET | 传感器数据查询 |
| `/api/v1/twins/diagnosis` | POST | 设备故障诊断 |
| `/api/v1/twins/decision` | POST | 智能决策建议 |

---

### 2. 前端集成

**文件：** `DoubleBoatSimWebGL/public/ai-controller.js`

**修改内容：**
- API 地址改为 Poseidon 服务：`http://127.0.0.1:8080`
- 调用智能体技能进行决策
- 支持自然语言场景控制

---

### 3. 智能体技能扩展

**文件：** `agents/marine_engineer/skills/twins_controller.py`

**新增技能：**
- 场景生成与配置
- 船只运动控制
- 传感器数据模拟
- 故障注入与诊断

---

## 📁 文件清单

### 新建文件

| 文件 | 路径 | 说明 |
|------|------|------|
| `poseidon_server_twins.py` | `agents/marine_engineer/` | 数字孪生 API 服务 |
| `twins_controller.py` | `agents/marine_engineer/skills/` | 数字孪生控制技能 |
| `test_twins_controller.py` | `agents/marine_engineer/skills/` | 测试用例 |
| `twins_api_spec.md` | `agents/marine_engineer/` | API 接口文档 |

### 修改文件

| 文件 | 路径 | 修改内容 |
|------|------|----------|
| `ai-controller.js` | `DoubleBoatSimWebGL/public/` | API 地址、调用逻辑 |
| `ai-panel.html` | `DoubleBoatSimWebGL/public/` | UI 增强 |
| `poseidon_server.py` | `agents/marine_engineer/` | 扩展 API 端点 |

---

## 🚀 实施步骤

### 第 1 步：创建数字孪生控制技能 ✅
```bash
cd /Users/panglaohu/clawd/agents/marine_engineer/skills
# 创建 twins_controller.py
```

### 第 2 步：扩展 Poseidon API 服务 ✅
```bash
# 扩展 poseidon_server.py 添加数字孪生端点
```

### 第 3 步：修改前端控制器
```bash
cd /Users/panglaohu/Downloads/DoubleBoatSimWebGL/public
# 修改 ai-controller.js
```

### 第 4 步：测试集成
```bash
# 启动 Poseidon 服务
python3 poseidon_server_twins.py

# 打开数字孪生页面测试
open http://localhost:8080/twins/
```

---

## 🎮 功能场景

### 场景 1：自然语言控制
```
用户输入："把波浪调大，切换到暴风雨模式"
→ AI 解析意图
→ 调用场景配置 API
→ 应用天气预设 + 调整波浪参数
```

### 场景 2：故障诊断
```
用户输入："主机转速异常下降"
→ AI 检索故障知识库
→ 分析可能原因
→ 给出诊断报告和解决方案
```

### 场景 3：智能决策
```
用户输入："当前海况适合继续航行吗？"
→ AI 分析传感器数据
→ 评估风险等级
→ 给出航行建议
```

---

## 📊 预期效果

| 功能 | 集成前 | 集成后 |
|------|--------|--------|
| 场景控制 | 硬编码预设 | AI 智能决策 |
| 故障诊断 | 简单规则 | 知识库驱动 |
| 交互方式 | 按钮点击 | 自然语言 |
| 决策能力 | 无 | 智能体驱动 |

---

**下一步：** 开始实施第 1 步 - 创建数字孪生控制技能
