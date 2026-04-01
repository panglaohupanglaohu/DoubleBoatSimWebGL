# DoubleBoatClawSystem

AI Native 深海远洋 CPS 系统，目标不是“把船上子系统接到一个大屏”，而是把航行、机舱、能效、感知、合规、决策、记忆统一到一个可解释、可追溯、可协同的认知闭环里。

当前版本已经从“最小演示骨架”推进到“可执行的 CPS 控制中枢雏形”：

- 导航链路具备 CPA/TCPA 风险评估和基于 COLREGs 的遭遇规则判断。
- 机舱链路具备健康评分、趋势判断、故障诊断和维护建议。
- 能效链路具备 EEXI/CII/SEEMP 的合规能力和优化建议入口。
- 感知链路具备多源事件融合、风险关联和记忆层持久化。
- 决策链路可以把跨域信号编排成任务化 action plan 和 mission brief。
- 数字孪生前端可以统一消费本地 dashboard、AI Native 协调状态和外部海事态势。

## 本轮架构改进（2026-03-25）

本轮改进重点是把系统从“单链路能力演示”推进到“跨域协同可执行架构”，核心变化如下。

- 新增 SVESSEL 扩展通道栈：
        - `autonomy_manager`：统一 MASS/LR 等级映射、自治级别切换与控制权语义。
        - `ship_shore_link`：多链路质量评估、最佳链路选择与时延预测。
        - `predictive_health`：预测性健康摘要与维护计划输出。
        - `route_optimizer`：航线优化状态接入与策略可视化。
        - `voyage_planner`：航次态势与日计划输出接口。
        - `cyber_security`：威胁态势、会话与审计摘要。

- 决策编排升级：
        - `decision_orchestrator` 由单域动作编排升级为跨域编排，动作计划可同时纳入导航、机舱、PHM、通信链路与网络安全约束。
        - 任务输出增加 MASS 等级、链路质量、威胁级别等关键 KPI 维度，前后端共享同一语义。

- API 面扩展：
        - 新增 AI Native 端点用于自治状态、自治切换、船岸通信、PHM、航线与网络安全信息读取。
        - 这些端点与现有 mission brief、decision package 形成“可观测 + 可执行 + 可回放”接口闭环。

- 运行稳定性改进：
        - 修复 `ship_shore_link` 默认配置对象复用导致的跨实例状态污染问题，避免测试序列中可用性漂移。
        - 增加多处向后兼容层（感知融合输入格式、决策动作构建签名、机舱快照接口、湖仓 flush/status 字段），降低历史测试与新架构的耦合断裂风险。

## 双智能体集合架构

当前系统不是单一 Agent 控制，而是双智能体集合并行协同：

- 船端执行智能体集合（Shipboard Execution Agent Set）
        - 目标：实时感知、实时控制、局部决策、边缘容错。
        - 关注：毫秒到秒级响应、自治级别可降级、失联可本地持续运行。

- 岸端监督智能体集合（Shore Supervision Agent Set）
        - 目标：全局监督、策略约束、合规与安全审计、远程协同接管。
        - 关注：任务一致性、跨航段优化、治理闭环、船岸协同可解释性。

两集合通过 ship-shore 链路在“共享任务图 + 共享约束 + 共享证据”层面对齐，不以 UI 对齐代替控制语义对齐。

### 控制语义分层

- L0-L1（感知与事件总线）
        - 船端主导，岸端订阅。
- L2-L3（任务图与自治执行）
        - 船端执行，岸端监督约束。
- L4（治理与安全）
        - 船岸共同生效，岸端有强约束优先权。
- L5（HMI 与操作交互）
        - 双端呈现同一任务语义，但允许不同视角。

## 模块隶属关系

下面按“主隶属 + 协同方”定义模块归属，避免模块职责漂移。

### 船端执行智能体集合（主隶属）

- intelligent_navigation
        - 主责：航行风险评估、COLREGs 规则判断、避碰动作建议。
        - 协同：decision_orchestrator、ship_shore_link。

- intelligent_engine
        - 主责：机舱健康评分、告警、故障诊断、维护建议。
        - 协同：predictive_health、decision_orchestrator。

- energy_efficiency_channel
        - 主责：能效状态、EEXI/CII 约束输入、优化建议。
        - 协同：compliance_digital_expert、route_optimizer。

- distributed_perception_hub
        - 主责：多源事件采集与融合、风险关联、事件标准化。
        - 协同：data_lakehouse、decision_orchestrator。

- route_optimizer
        - 主责：船端路径优化与航行策略候选生成。
        - 协同：voyage_planner、intelligent_navigation。

- predictive_health
        - 主责：设备退化趋势、维护窗口、预测性健康输出。
        - 协同：intelligent_engine、decision_orchestrator。

### 岸端监督智能体集合（主隶属）

- cyber_security
        - 主责：威胁态势、会话与审计、访问控制治理。
        - 协同：decision_orchestrator、openbridge_hmi。

- compliance_digital_expert
        - 主责：规则解释、合规快照、证据链生成。
        - 协同：energy_efficiency_channel、decision_orchestrator。

- voyage_planner
        - 主责：航次级监督、计划一致性、航段状态管理。
        - 协同：route_optimizer、ship_shore_link。

### 船岸共享控制平面（双隶属）

- decision_orchestrator
        - 主责：跨域任务图编排、行动优先级、反馈闭环。
        - 船端语义：执行计划。
        - 岸端语义：监督约束。

- autonomy_manager
        - 主责：MASS/LR 等级映射、自治切换、控制权转移。
        - 船端语义：当前执行权限。
        - 岸端语义：监督与接管边界。

- ship_shore_link
        - 主责：链路质量评估、时延预测、冗余切换。
        - 船端语义：执行连续性保障。
        - 岸端语义：协同与接管可达性保障。

- data_lakehouse
        - 主责：事件持久化、回放、分析查询、云边同步。
        - 船端语义：边缘记忆。
        - 岸端语义：审计与策略复盘。

- openbridge_hmi / captain-cockpit / digital-twin
        - 主责：统一任务语义的人机呈现，不改变控制权本体。
        - 船端语义：操作执行。
        - 岸端语义：监督确认。

## 双集合文本架构图

### 图 A：双智能体集合总览（控制与监督）

```text
                                                                                                 ┌──────────────────────────────────────────┐
                                                                                                 │ Shore Supervision Agent Set              │
                                                                                                 │ 监督/治理/审计/策略约束                  │
                                                                                                 │                                          │
                                                                                                 │ compliance_digital_expert                │
                                                                                                 │ cyber_security                           │
                                                                                                 │ voyage_planner                           │
                                                                                                 └───────────────┬──────────────────────────┘
                                                                                                                                                                 │ policy/constraints/evidence
                                                                                                                                                                 │
                                                                                 ship_shore_link + autonomy_manager + data_lakehouse
                                                                                                                                                                 │
                                                                                                                                                                 │ execution state/telemetry/feedback
                                                                                                 ┌───────────────▼──────────────────────────┐
                                                                                                 │ Shipboard Execution Agent Set            │
                                                                                                 │ 感知/控制/局部决策/边缘容错              │
                                                                                                 │                                          │
                                                                                                 │ distributed_perception_hub               │
                                                                                                 │ intelligent_navigation                   │
                                                                                                 │ intelligent_engine                       │
                                                                                                 │ energy_efficiency_channel                │
                                                                                                 │ predictive_health                        │
                                                                                                 │ route_optimizer                          │
                                                                                                 └───────────────┬──────────────────────────┘
                                                                                                                                                                 │
                                                                                                                                                                 ▼
                                                                                                         decision_orchestrator (shared control plane)
                                                                                                                                                                 │
                                                                                                                                                                 ▼
                                                                                                 openbridge_hmi / captain-cockpit / digital-twin
```

### 图 B：模块归属与主数据流（Who owns what）

```text
[Shipboard Owner]
        distributed_perception_hub -> decision_orchestrator
        intelligent_navigation      -> decision_orchestrator
        intelligent_engine          -> predictive_health -> decision_orchestrator
        energy_efficiency_channel   -> compliance_digital_expert -> decision_orchestrator
        route_optimizer             -> voyage_planner (shore sync)

[Shore Owner]
        cyber_security              -> decision_orchestrator (governance constraints)
        compliance_digital_expert   -> decision_orchestrator (rule/evidence)
        voyage_planner              -> decision_orchestrator (voyage-level constraints)

[Shared Control Plane]
        ship_shore_link   : connectivity, latency, failover, RCC reachability
        autonomy_manager  : MASS/LR mapping, authority transfer, autonomy transition
        data_lakehouse    : event memory, replay, analytics, cloud-edge sync
        decision_orchestrator : task graph, action plan, feedback closure

[Northbound Interaction Layer]
        openbridge_hmi / captain-cockpit / digital-twin
        (shared mission semantics, different operational viewpoints)
```

## 系统持续构建模块（System Continuous Build）

在双智能体集合之上，系统新增一个上层能力模块：系统持续构建。

该模块不替代船端执行与岸端监督，而是为两者提供“自动化生成 + 持续改进”能力，包括：

- 自动化生成：自动任务拆解、代码生成、测试补全、文档更新、配置修复。
- 持续改进：性能与质量回归、缺陷闭环、架构演进建议、规范一致性治理。
- 运行保障：版本化变更记录、可回溯验证证据、跨角色协作可审计。

### 在整体架构中的位置

```text
双智能体集合（执行/监督）
                                ▲
                                │ 反馈、指标、缺陷、需求变更
                                │
系统持续构建模块（7 Agent Team）
                                │
                                ▼
自动化生成与持续改进产物
(代码/测试/文档/配置/流程)
```

## 7 Agent 职责矩阵（系统持续构建模块）

下表为 Director/Architect/Marine/Dev/Code/QA/Doc 与当前核心模块的一一职责映射。

| Agent 角色 | 在系统持续构建中的主责 | 对应模块（主） | 持续改进输出 |
|---|---|---|---|
| Director (Chief Director) | 目标分解、优先级编排、跨 Agent 节奏与验收门禁 | `decision_orchestrator`, `cps/mission-brief`, `coordination/status` | 冲刺目标、里程碑、验收清单、风险闭环 |
| Architect (System Architect) | 架构边界、接口契约、依赖治理、演进路径 | `api_extensions`, `register_channels`, `main.py` | 架构蓝图、接口规范、兼容策略、重构路线 |
| Marine (Marine Researcher) | 海事规则与场景知识注入、业务可行性校核 | `intelligent_navigation`, `maritime_scene_model`, `route_optimizer`, `voyage_planner` | 场景规则库、航行策略建议、约束模型 |
| Dev (Development Lead) | 任务分派、实现协同、代码一致性把控 | `channels/*`, `storage/*`, `frontend/*` 协同面 | 实施计划、模块集成方案、交付编排 |
| Code (Code Writer) | 功能实现、兼容修复、接口落地、测试对齐 | `autonomy_manager`, `ship_shore_link`, `predictive_health`, `cyber_security`, `data_lakehouse` | 可运行代码、补丁、回归修复、实现说明 |
| QA (QA Engineer) | 测试策略、回归验证、质量基线维护 | `tests/unit/*`, `tests/integration/*`, `scripts/run_tests.py` | 测试矩阵、失败归因、质量报告、发布门禁 |
| Doc (Documentation Writer) | 架构文档、API 文档、操作指南与变更说明 | `README.md`, `docs/`, `reports/` | 文档增量、版本说明、知识库维护 |

### 角色协作链（持续构建闭环）

```text
Director
        -> Architect (定义边界与契约)
        -> Marine (注入海事规则与场景)
        -> Dev (拆分实现任务)
        -> Code (落地实现与修复)
        -> QA (验证与门禁)
        -> Doc (沉淀文档与报告)
        -> Director (验收与下一轮规划)
```

该闭环即系统持续构建模块的执行主路径，用于持续增强当前系统的自动化生成与持续改进能力。

### 持续构建执行入口（直接开干）

- 持续构建 SOP：docs/process/SYSTEM_CONTINUOUS_BUILD_SOP.md
- 持续构建主循环：scripts/system_continuous_build_loop.sh
- 每小时状态汇报：scripts/hourly_status_report.sh

启动主循环：

```bash
bash scripts/system_continuous_build_loop.sh
```

手动触发一次小时汇报：

```bash
bash scripts/hourly_status_report.sh
```

如需对接 OpenClaw 的 marine_engineer 作为研究员知识源，可在启动前配置：

```bash
export MARINE_FEED_CMD="openclaw ask marine_engineer --prompt 'Provide latest maritime tech/regulatory update for architecture handoff'"
bash scripts/system_continuous_build_loop.sh
```

输出证据目录：

- logs/team_logs/system_continuous_build.log
- reports/status/HOURLY_STATUS_REPORT_*.md

## 当前交付状态

当前分支已完成本轮多小时冲刺的核心交付，状态为“可运行、可验证、可联调”：

- ECF feedback loop 已闭环，反馈事件会进入认知快照和 decision feedback 记录。
- Orchestration graph 已落地，后端输出 `task_graph`，前端驾驶台和 3D twin 可消费。
- Feature fusion 已接入数字孪生，支持融合轨迹状态查询和场景标记。
- Lightweight lakehouse 已支持 SQLite WAL 热数据、Parquet 归档、DuckDB 即席分析，以及 S3/MinIO 兼容云同步。
- Maritime scene model 已接入导航链路，COLREGs 判断具备 scene-aware contextual rule。
- RCS control loop 第一版已接入，输出 T-Foil、Trim Tabs、roll/heave 控制目标。
- SHM monitoring chain 第一版已接入，输出弯矩、扭转、疲劳损伤和寿命余度。
- OpenBridge HMI 第一版已接入，桥楼聊天和驾驶台可共享任务图、控制摘要和结构健康摘要。

当前已验证通过：

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/unit/test_cps_mission_brief.py tests/integration/test_ai_native_endpoints.py
```

结果：`9 passed`

本轮新增湖仓验证：

```bash
PYTHONPATH=src/backend PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/unit/test_data_lakehouse.py
```

结果：`6 passed`

新增能力已覆盖：Parquet 存储回放、DuckDB analytics query、S3/MinIO 兼容适配器列举/下载、memory analytics API。

## 当前执行计划

- 18 小时压缩执行计划：`docs/AI_NATIVE_CPS_18H_EXECUTION_PLAN.md`
- 4 小时改写计划：`docs/AI_NATIVE_CPS_4H_REWRITE_PLAN.md`
- OpenBridge 使用说明：`docs/OPENBRIDGE_QUICK_GUIDE.md`
- Test case 集合：`tests/TEST_CASE_COLLECTION.md`

## 文档与归档目录约定

当前仓库已经完成第一轮 Markdown 清理，根目录只保留 `README.md` 作为总入口。后续所有文档整理都应遵循下面的目录语义。

- `README.md`
        - 项目总入口，只保留系统概览、启动方法、交付验收流程、目录约定和关键链接
- `docs/`
        - 项目知识库主目录，放仍然需要持续维护和反复查阅的文档
- `docs/architecture/`
        - 架构、目录结构、系统集成、通道关系等结构型知识
- `docs/plans/`
        - 计划类文档，例如冲刺计划、阶段计划、改写方案
- `docs/process/`
        - 过程规范类文档，例如纪律、协议、复盘、流程约束
- `docs/analysis/`
        - 分析类文档，例如问题分析、任务拆解、专项技术分析
- `docs/guides/`
        - 使用说明、快速开始、操作指南等面向使用者的文档
- `reports/`
        - 执行知识库主目录，放结果型和过程型汇报文档
- `reports/execution/`
        - 交付报告、修复报告、验证报告、集成报告、阶段总结等执行结果文档
- `reports/status/`
        - 当前轮次的状态报告目录，存放本轮执行中产生的 `STATUS_REPORT_*`、`PROGRESS_REPORT_*`、`HOURLY_STATUS_REPORT*` 等过程快照
- `reports/archived_status/`
        - 历史状态报告归档目录，存放已过阶段、不再作为当前执行面板使用的旧状态快照
- `tests/reports/`
        - 自动化测试输出目录，只放测试运行产物和自动生成报告，不放人工项目汇报

归档规则：

- 根目录原则上不再新增任何 Markdown 文档，唯一例外是 `README.md`
- 新增架构、计划、规范、分析、指南类文档时，必须进入 `docs/` 对应子目录
- 新增交付报告、验证报告、修复报告、集成报告时，必须进入 `reports/execution/`
- 新增状态快照、阶段进展、小时汇报时，必须进入 `reports/status/`
- 旧状态报告从当前执行面退出后，再转入 `reports/archived_status/`

## 系统目标

系统围绕 4 个核心能力设计：

- Perception：统一采集导航、机舱、能效、AIS、天气、外部海事事件。
- Memory：事件进入湖仓，支持查询、回放、近期态势概览。
- Thinking：合规专家和决策编排器把碎片状态转成规则化判断和任务化动作。
- Learning：通过 decision feedback 记录反馈闭环，为后续策略优化保留证据。

## 当前架构

```text
Bridge UI / Digital Twin
        |
HTTP + WebSocket
        |
FastAPI Poseidon Core
        |
+----------------------------+
| compliance_digital_expert  |
| distributed_perception_hub |
| decision_orchestrator      |
+----------------------------+
        |
+----------------------------+
| navigation | engine | energy |
+----------------------------+
        |
WorldMonitor + Local Lakehouse
```

## 关键模块

### 1. 智能导航

文件：`src/backend/channels/intelligent_navigation.py`

能力：

- CPA/TCPA 计算
- 风险分级
- COLREGs 遭遇分类
- 避碰建议
- 面向控制层的导航报告

输出重点：

- `collision_risks`
- `colregs_assessments`
- `recommended_manoeuvres`
- `risk_index`

### 2. 智能机舱

文件：`src/backend/channels/intelligent_engine.py`

能力：

- 主机健康评分
- 趋势分析
- 告警生成
- 故障诊断
- 维护建议

### 3. 能效与合规

文件：

- `src/backend/channels/energy_efficiency_channel.py`
- `src/backend/channels/compliance_digital_expert.py`

能力：

- EEXI / CII / SEEMP 能力入口
- 统一认知快照
- 规则、证据、建议的结构化输出
- 工程参数和跨域约束聚合

### 4. 分布式感知与记忆层

文件：

- `src/backend/channels/distributed_perception_hub.py`
- `src/backend/storage/data_lakehouse.py`

能力：

- 多源事件融合
- 风险关联
- SQLite WAL 热数据存储
- Parquet 归档导出
- DuckDB 即席分析查询
- S3 / MinIO 兼容对象存储同步
- 查询 / 回放 / 记忆概况

### 5. 决策编排器

文件：`src/backend/channels/decision_orchestrator.py`

能力：

- 汇总跨域状态
- 生成 `mission_brief`
- 生成任务化 `action_plan`
- 记录反馈，形成闭环

### 6. 气象航线避险

文件：`src/backend/channels/weather_routing_channel.py`

能力：

- 天气预报缓存
- 航线风险评估
- 避险建议

输出重点：

- `risk_score`
- `risk_level`
- `recommendations`

### 7. 船员疲劳监控

文件：`src/backend/channels/crew_fatigue_monitor.py`

能力：

- 值班追踪
- 疲劳评分
- 轮班建议

输出重点：

- `fatigue_scores`
- `risk_alerts`
- `recommendations`

## 核心 API

### 运行态

- `GET /health`
- `GET /api/v1/dashboard`
- `GET /api/v1/channels`

### AI Native / CPS

- `GET /api/v1/ai-native/compliance/status`
- `GET /api/v1/ai-native/compliance/cognitive-snapshot`
- `GET /api/v1/ai-native/perception/events`
- `GET /api/v1/ai-native/perception/capture-snapshot`
- `GET /api/v1/ai-native/decision/package`
- `POST /api/v1/ai-native/decision/feedback`
- `GET /api/v1/ai-native/status/full-pipeline`
- `GET /api/v1/ai-native/coordination/status`
- `GET /api/v1/ai-native/memory/events`
- `GET /api/v1/ai-native/memory/replay`
- `GET /api/v1/ai-native/memory/analytics/status`
- `POST /api/v1/ai-native/memory/archive`
- `POST /api/v1/ai-native/memory/analytics/query`
- `GET /api/v1/ai-native/cps/mission-brief`
- `GET /api/v1/ai-native/perception/fusion-state`
- `GET /api/v1/ai-native/rcs/status`
- `GET /api/v1/ai-native/shm/status`
- `POST /api/v1/ai-native/openbridge/command`
- `GET /api/v1/ai-native/weather-routing/status`
- `GET /api/v1/ai-native/weather-routing/recommendations`
- `GET /api/v1/ai-native/crew/fatigue-status`
- `GET /api/v1/ai-native/crew/recommendations`
- `GET /api/v1/ai-native/anchor/status`
- `GET /api/v1/ai-native/cargo/status`
- `GET /api/v1/ai-native/fire/status`
- `POST /api/v1/ai-native/decision/feedback/log`

### 设备与子系统 API

- `GET /api/vdr/status` — VDR 状态
- `GET /api/vdr/integrity` — VDR 数据完整性
- `GET /api/dp/status` — 动态定位状态
- `POST /api/dp/set-station` — 设定 DP 定点
- `GET /api/ais/targets` — AIS 目标列表
- `GET /api/ais/target/{mmsi}` — 单个 AIS 目标查询
- `GET /api/hull/status` — 船体应力状态
- `GET /api/hull/fatigue` — 船体疲劳分析
- `GET /api/power/status` — 电力系统状态
- `GET /api/power/efficiency` — 电力效率
- `GET /api/bilge/status` — 舱底水状态
- `GET /api/bilge/compliance` — MARPOL 舱底水合规
- `GET /api/comms/status` — 通信系统 GMDSS 状态
- `GET /api/compass/status` — 电罗经状态
- `GET /api/speed-log/status` — 计程仪状态
- `GET /api/weather-routing/grid` — 气象导航网格
- `GET /api/rudder/status` — 舵机状态
- `GET /api/tanks/summary` — 液舱汇总
- `GET /api/tanks/fuel-endurance` — 燃油续航
- `GET /api/alarms/active` — 当前活跃告警
- `GET /api/alarms/summary` — 告警摘要
- `GET /api/autopilot/status` — 自动舵状态
- `GET /api/depth/status` — 测深仪状态
- `GET /api/propulsion/status` — 推进系统状态
- `GET /api/propulsion/engine/{engine_id}` — 单台主机状态
- `GET /api/mooring/status` — 系泊状态
- `GET /api/mob/status` — MOB 落水告警状态
- `POST /api/mob/activate` — 激活 MOB 告警
- `POST /api/mob/deactivate` — 解除 MOB 告警
- `GET /api/safety/status` — 安全系统综合状态

### 外部态势

- `GET /api/v1/worldmonitor/ais`
- `GET /api/v1/worldmonitor/weather?lat=<lat>&lng=<lng>`
- `GET /api/v1/worldmonitor/ports`
- `GET /api/v1/worldmonitor/routes`

WorldMonitor 真实数据接入默认读取环境变量 `WORLDMONITOR_API_KEY`。若未配置（或为 `placeholder`），服务会自动进入 mock 模式，不会阻塞接口。

- 日志识别：启动阶段会出现 `WorldMonitor API key is not configured - using mock mode`，请求阶段会出现 `WorldMonitor: using mock ... data (no API key)`。
- 对测试环境影响：可继续联调与回归，但返回为模拟数据（含随机性），不适合作为真实海事态势精度基准。
- 对生产环境影响：接口仍可用但数据不代表真实外部态势；上线前应配置有效 API key 并在启动日志中确认未进入 mock。

## 交付验收流程

按下面顺序执行，可以完成当前交付版本的本地启动和核心验收。

### 1. 准备环境

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
npm install
```

### 2. 启动后端

```bash
source venv/bin/activate
python src/backend/main.py --host 0.0.0.0 --port 8080
```

Lakehouse 运行时配置默认读取 `config/settings.json` 里的 `lakehouse` 段；若需要切换到 MinIO / S3 兼容对象存储，可在启动前覆盖环境变量：

```bash
export POSEIDON_LAKEHOUSE_CLOUD_TYPE=s3
export POSEIDON_LAKEHOUSE_S3_ENDPOINT_URL=http://127.0.0.1:9000
export POSEIDON_LAKEHOUSE_S3_BUCKET=doubleboat-events
export POSEIDON_LAKEHOUSE_S3_REGION=us-east-1
export POSEIDON_LAKEHOUSE_S3_ADDRESSING_STYLE=path
export POSEIDON_LAKEHOUSE_S3_VERIFY_SSL=false
export POSEIDON_LAKEHOUSE_S3_AUTO_CREATE_BUCKET=true
python src/backend/main.py --host 0.0.0.0 --port 8080
```

常用覆盖项还包括：

- `POSEIDON_LAKEHOUSE_S3_AUTO_CREATE_BUCKET`
- `POSEIDON_LAKEHOUSE_DB_PATH`
- `POSEIDON_LAKEHOUSE_STORAGE_PATH`
- `POSEIDON_LAKEHOUSE_CLOUD_STORAGE_PATH`
- `POSEIDON_LAKEHOUSE_ANALYTICS_CACHE_DIR`
- `POSEIDON_LAKEHOUSE_BUFFER_MAX_SIZE`

若启用 `POSEIDON_LAKEHOUSE_S3_AUTO_CREATE_BUCKET=true`，服务启动时会先探测目标 bucket；对 MinIO / S3 兼容对象存储，如果 bucket 不存在，会尝试自动创建，并将结果写入启动日志与 `/health` 的 `cloud_sync` 字段。

### 3. 启动前端

```bash
npm run dev -- --host 0.0.0.0
```

### 4. 打开交付入口

- 船长智能中控台：`http://localhost:5173/captain-cockpit.html`
- 前端首页（默认跳转到船长智能中控台）：`http://localhost:5173/`
- 数字孪生独立页：`http://localhost:5173/digital-twin.html`
- 后端文档：`http://localhost:8080/docs`
- WebSocket：`ws://localhost:8080/ws`

### 5. 验证核心接口

建议至少检查以下接口：

- `GET /api/v1/dashboard`
- `GET /health`（现在包含 `cloud_sync` 和 `lakehouse_health`，可直接查看对象存储是否可达）
- `GET /api/v1/ai-native/cps/mission-brief`
- `GET /api/v1/ai-native/perception/fusion-state`
- `GET /api/v1/ai-native/rcs/status`
- `GET /api/v1/ai-native/shm/status`
- `POST /api/v1/ai-native/openbridge/command`

### 6. 运行核心回归

由于当前虚拟环境里存在第三方 `pytest` 插件冲突，建议关闭自动插件加载后运行：

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/unit/test_cps_mission_brief.py tests/integration/test_ai_native_endpoints.py
```

通过标准：

- 测试结果为 `9 passed`
- 船长智能中控台能看到嵌入式数字孪生主视图、原生 WorldMonitor 海图、决策摘要和 OpenBridge 命令台
- 船长智能中控台与数字孪生页能直接看到 lakehouse 云同步状态和 analytics readiness
- 船长智能中控台提供 Lakehouse Analytics 预设面板，可直接查看事件类型、事件来源和时间分桶统计
- 数字孪生独立页能看到 task graph、fusion tracks、RCS、SHM 卡片
- `Poseidon-X Bridge` 可响应任务图、碰撞风险、舒适控制、结构健康、主机状态等命令

## OpenBridge 命令入口

桥楼命令现在有两条入口：

- 船长智能中控台右侧 `OpenBridge 命令台`
- 数字孪生页面右下角 `Poseidon-X Bridge` 聊天面板
- 后端语义命令接口 `POST /api/v1/ai-native/openbridge/command`
- 独立使用说明：`docs/OPENBRIDGE_QUICK_GUIDE.md`

请求体示例：

```json
{
        "command": "请切到舒适控制并给出当前任务图摘要",
        "source": "bridge_chat"
}
```

当前支持的命令意图包括：

- 任务图查询：`任务图`、`mission brief`、`行动计划`
- 避碰态势查询：`碰撞风险`、`COLREGs`、`导航风险`
- 舒适控制查询：`舒适控制`、`RCS`、`减摇`、`姿态`
- 结构健康查询：`结构健康`、`SHM`、`疲劳`、`寿命`
- 主机健康查询：`主机状态`、`机舱健康`、`维护建议`

接口返回内容包含：

- `recognized_intent`
- `execution_mode`
- `summary`
- `operator_action`
- `task_graph` 摘要
- `control_state.rcs`
- `control_state.shm`

## 当前改写重点

本轮优化聚焦 4 个方向：

- 把导航输出从“风险数字”升级为“规则 + 角色 + 动作”。
- 把决策输出从“摘要文本”升级为“可执行 action plan”。
- 把湖仓从“只存不看”升级为“可直接给协调层消费的记忆概况”。
- 把 WorldMonitor 从“空占位”升级为“可驱动前端和联调的真实结构 mock”。

## 测试

完整测试可继续按仓库既有方式执行；当前交付版本的最小验收回归以“交付验收流程”中的命令为准。

## 测试归类规范

后续开发必须遵循下面的测试组织方式，避免测试脚本再次散落到根目录：

- `tests/unit`：放可被 pytest 直接收集的单元测试，文件名必须是 `test_*.py`
- `tests/integration`：放可被 pytest 直接收集的集成测试，覆盖跨模块联动和关键回归
- `tests/manual`：放手工验证脚本、打印型检查脚本、临时调试脚本，文件名不要使用 `test_*.py`
- 根目录不再新增任何 `test_*.py` 文件，新的测试必须进入 `tests/` 体系
- 新增测试时，优先补到已有 test case 集合中；只有在主题明确且不可复用时，才新增测试文件
- 如果测试依赖全局 registry、路径注入或环境准备，统一放到 `tests/conftest.py`，不要在每个文件里重复写一份环境胶水代码
- 更新验收命令、架构脚本或文档时，必须同步使用 `tests/unit/...` 和 `tests/integration/...` 的新路径

当前 test case 集合索引见：`tests/TEST_CASE_COLLECTION.md`

## GitHub 提交说明

仓库内代码已可本地修改和验证，但是否能真正推送到 GitHub 取决于：

- 本地是否配置了远端仓库
- 当前终端是否有可用凭据
- 用户是否允许直接推送

如果远端和凭据已就绪，可直接执行正常的 `git add` / `git commit` / `git push` 流程。