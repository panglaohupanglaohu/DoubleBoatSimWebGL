# Marine DataCenter — AI 能耗管理系统设计文档

> **第一性原理 (First Principles, Musk-style)**: 船载数据中心 ≠ 陆基机房。
> 必须从能耗物理本质出发: **E = Σ(P_load · η_conv · κ_cool · τ_util)**
> 破除"按陆基机房思维建设"的传统范式。

---

## 1. 系统架构图

### 1.1 总体架构 (5 层)

```
┌──────────────────────────────────────────────────────────────────────┐
│ L4 · DARWIN RATCHET 棘轮自演进                                        │
│   - 遗产账本 (heritage_ledger)  - 演进只增不减                         │
│   - 与全局 Darwin (system-evolution.html) 联动                        │
└────────────────────────────────▲─────────────────────────────────────┘
                                 │ evolve()
┌──────────────────────────────────────────────────────────────────────┐
│ L3 · CLOSED LOOP 闭环 (监控 → 决策 → 调整 → 验证)                     │
│   - SkillLibrary  (Lobster-style 运维沉淀)                            │
│   - PolicyEngine  (open_source 开源 / save_outgo 节流)                │
│   - Closed-loop tick → PUE 反馈                                       │
└────────────────────────────────▲─────────────────────────────────────┘
                                 │ analyze
┌──────────────────────────────────────────────────────────────────────┐
│ L2 · 4-VIEW AI 四视角并发分析                                          │
│   ┌────────┐ ┌────────┐ ┌──────────────┐ ┌──────────┐                │
│   │ DEVICE │ │FACILITY│ │  ENVIRONMENT │ │ PROCESS  │                │
│   │ 设备   │ │ 设施   │ │   环境       │ │  流程    │                │
│   └────────┘ └────────┘ └──────────────┘ └──────────┘                │
└────────────────────────────────▲─────────────────────────────────────┘
                                 │
┌──────────────────────────────────────────────────────────────────────┐
│ L1 · CHANNEL HUB (信息汇总)                                            │
│   marine_datacenter_energy  (MarineChannel)                           │
└────────────────────────────────▲─────────────────────────────────────┘
                                 │ ingest
┌──────────────────────────────────────────────────────────────────────┐
│ L0 · IoT EDGE (物联网边缘)                                             │
│   ┌──────────┐ ┌──────────┐ ┌─────────────┐ ┌────────────┐           │
│   │ LoRa-TH  │ │ MC-RFID  │ │ PLC-Agent   │ │ PowerMeter │           │
│   │ 温湿度    │ │ 资产盘点  │ │ 单板机推理   │ │  电力监测   │           │
│   └──────────┘ └──────────┘ └─────────────┘ └────────────┘           │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.2 前端架构

```
[浏览器]
  └─ marine-datacenter.html  (科技化暗色 HUD UI)
       ├─ KPI Strip          ← /api/v1/datacenter/status
       ├─ 4-View Cards       ← /api/v1/datacenter/four-view
       ├─ PUE Gauge          ← status.current_pue
       ├─ IoT Hub Panel      ← /api/v1/datacenter/iot/hub + /sensors
       ├─ Skill Library      ← /api/v1/datacenter/skills
       ├─ Policy Library     ← /api/v1/datacenter/policies
       ├─ Heritage Ledger    ← /api/v1/datacenter/heritage
       ├─ Event Stream       ← /api/v1/datacenter/events
       ├─ Closed-Loop Btn    → POST /api/v1/datacenter/loop/tick
       └─ Darwin Evolve Btn  → POST /api/v1/datacenter/evolve
```

### 1.3 后端架构

```
src/backend/
  ├─ channels/marine_datacenter_energy.py   ← MarineDataCenterEnergyChannel
  │     ├─ DCDevice / IoTSensor / OpsSkill
  │     ├─ EnergyPolicy / DarwinHeritage
  │     ├─ analyze_perspective(p)
  │     ├─ four_view_overview()
  │     ├─ closed_loop_tick()
  │     ├─ evolve(...)
  │     └─ process_event(event)
  │
  ├─ register_channels.py
  │     └─ register_marine_datacenter_energy()
  │
  └─ main.py
        └─ /api/v1/datacenter/* 全套 13 个 REST 端点
```

---

## 2. 详细设计

### 2.1 四视角 (Perspectives)

| 视角 | 关注点 | 输入数据 | 输出洞察 |
|------|--------|---------|---------|
| **device** 设备 | 单机功耗、利用率、效率得分 | rated_kw, cpu_util, intake_temp | 推理节点 DVFS 节能 8-15% |
| **facility** 设施 | IT/CRAC/UPS 占比、PUE | 设施级聚合 | 冷热通道封闭可降 PUE 0.10-0.15 |
| **environment** 环境 | 温湿度、热点、船摇、盐雾 | LoRa-TH 传感网 | 触发 skl-th-1 热点冷却技能 |
| **process** 流程 | 利用率、策略覆盖、SOP 成熟度 | 调度+策略库 | 推荐夜间任务批合并 |

### 2.2 IoT Hub

| 类型 | 协议 | 用途 |
|------|------|------|
| LoRa-TH | LoRaWAN | 低功耗温湿度 (机柜前后/冷热通道) |
| MC-RFID | Multi-Channel RFID | 设备资产快速盘点, 闪过即扫 |
| PLC-Agent | Modbus/EtherCAT + 边缘LLM | 单板机本地推理, 自治节能 |
| PowerMeter | DL/T-645 | 主母线电力监测 |

### 2.3 运维 Skill 库 (Lobster 龙虾风格)

每条 Skill 包含:
- `trigger`: 自然语言触发条件
- `action`: 处置动作
- `confidence`: Bayesian 平滑置信度 = (success+1)/(success+fail+2)
- `reinforce(success)`: 强化学习更新

### 2.4 策略引擎

两类:
- **open_source 开源**: 余热回收、光伏、船摇能量回收
- **save_outgo 节流**: DVFS、冷热通道封闭、夜间批合并

应用策略 → PUE 自动下降 (save_outgo: -0.02·fitness; open_source: -0.015·fitness)。

### 2.5 闭环算法

```python
def closed_loop_tick():
    snap = four_view_overview()                # 1. 监控
    decided = max(unapplied_policies,          # 2. 决策
                  key=lambda p: p.estimated_saving)
    adjust_result = apply_policy(decided.id)   # 3. 调整
    verified = current_pue < baseline_pue      # 4. 验证
    record_event(...)                          # 闭环留痕
```

### 2.6 Darwin 棘轮

```python
def evolve(title, category, delta_pue, delta_kwh_day):
    heritage.append(DarwinHeritage(...))   # 永不删除
    evolution_round += 1
    current_pue += delta_pue               # 单调下降
```

---

## 3. API 文档

Base URL: `http://localhost:8080`

### 3.1 状态 / 监控

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/datacenter/status` | 总状态 (PUE / 节能 / CO₂ / 遗产) |
| GET | `/api/v1/datacenter/perspective/{name}` | 单视角 (device/facility/environment/process) |
| GET | `/api/v1/datacenter/four-view` | 四视角并发 |
| GET | `/api/v1/datacenter/events?limit=50` | 闭环事件流 |

### 3.2 IoT

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/datacenter/iot/hub` | Hub 汇总 |
| GET | `/api/v1/datacenter/iot/sensors` | 全部传感器 |
| POST | `/api/v1/datacenter/iot/ingest` | 上报传感数据 `{sensor_id, value}` |

### 3.3 Skill (运维沉淀)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/datacenter/skills` | 技能列表 |
| POST | `/api/v1/datacenter/skills` | 新增技能 `{skill_id,title,trigger,action,...}` |
| POST | `/api/v1/datacenter/skills/{id}/reinforce` | 强化学习 `{success: true/false}` |

### 3.4 Policy (开源/节流)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/datacenter/policies` | 策略列表 |
| POST | `/api/v1/datacenter/policies/apply` | 应用策略 `{policy_id, fitness}` |

### 3.5 闭环 / Darwin

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/datacenter/loop/tick` | 触发一次闭环 |
| POST | `/api/v1/datacenter/evolve` | 棘轮演进 `{title,category,delta_pue,delta_kwh_day}` |
| GET | `/api/v1/datacenter/heritage` | 遗产账本 (只增不减) |

### 3.6 Channel 通用入口 (process_event)

通过 `/api/v1/channels/marine_datacenter_energy/query` 也可以提交 event:

```json
{ "type": "four_view" }
{ "type": "perspective_query", "perspective": "facility" }
{ "type": "closed_loop_tick" }
{ "type": "evolve", "title": "...", "delta_pue": -0.01, "delta_kwh_day": 2.5 }
```

---

## 4. 8 小时快速实现计划

| 时段 | 内容 | 产出 | 状态 |
|------|------|------|------|
| H+0 ~ H+1 | 第一性原理拆解 + 4 视角设计 | 数据模型 (DCDevice/IoTSensor/OpsSkill/Policy/Heritage) | ✅ |
| H+1 ~ H+2 | Channel 实现 + analyze_perspective + four_view | `marine_datacenter_energy.py` | ✅ |
| H+2 ~ H+3 | 闭环 + Skill 强化学习 + Policy 引擎 | closed_loop_tick / evolve | ✅ |
| H+3 ~ H+4 | API 13 个端点 + Channel 注册 | `main.py` 路由 + `register_channels.py` | ✅ |
| H+4 ~ H+6 | 科技化前端页面 (HUD + 网格 + KPI + 4视角卡) | `marine-datacenter.html` | ✅ |
| H+6 ~ H+7 | Darwin 棘轮联动 + 设计文档 | `darwin-ratchet.js` 新增条目 + 本文档 | ✅ |
| H+7 ~ H+8 | 测试 / 验证 / 集成 | 后端启动 + 端点 smoke test | ⏳ |

---

## 5. 开始干 — 立即体验

```bash
# 1. 重启后端 (会自动注册 marine_datacenter_energy Channel)
source venv/bin/activate
cd src/backend && python main.py --port 8080

# 2. 访问页面
open http://localhost:8080/marine-datacenter.html

# 3. 体验:
#    - 点击 "▶ 监控→决策→调整→验证 (单次闭环)" 看 PUE 自动下降
#    - 点击 "🧬 棘轮演进 +1" 看 Darwin 遗产账本累积
#    - 在 Skill 卡上点 ✓/✗ 训练运维知识库
#    - 在 Policy 卡上点 "应用" 看节能效果
```

---

## 6. 最牛逼的 AI 体现

| AI 能力 | 体现 |
|---------|------|
| **第一性原理推理** | 拆解能耗为物理基本量, 不是"按机房抄作业" |
| **多视角并发分析** | 4 视角同时给出洞察, 解决单一指标盲区 |
| **运维知识沉淀** | Lobster-style Skill 库, 自学习 + 反馈 + 置信度更新 |
| **AI 闭环** | 监控→决策→调整→验证 全自动, 决策由策略库 + 模型评分 |
| **Darwin 棘轮** | 进化只增不减, 锁定每一次 PUE 改善, 永不回退 |
| **边缘智能** | PLC-Agent 端侧推理, 单板机本地决策, 不依赖云端 |
| **能源开源** | 余热回收 + 光伏 + 船摇能量回收, 颠覆"只能耗能"的思维 |
| **统一 LLM 入口** | 与桥楼聊天共享 `/api/v1/bridge-chat/send` (智能体团队默认模型) |

---

## 7. 与现有系统的集成点

- **Darwin 棘轮**: `darwin-ratchet.js` HERITAGE 新增 `marine-datacenter-v1`
- **桥楼 LLM**: 复用 `/api/v1/bridge-chat/send`, 共享智能体团队配置
- **Channel 总线**: 与现有 47+ Channel 通过 `MarineChannel` 基类统一
- **存储**: 事件流可对接 `data_lakehouse` (后续可选)
- **前端导航**: 可挂入数字孪生下拉菜单 (后续可选)

