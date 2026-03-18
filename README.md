# DoubleBoatClawSystem

AI Native 深海远洋 CPS 系统，目标不是“把船上子系统接到一个大屏”，而是把航行、机舱、能效、感知、合规、决策、记忆统一到一个可解释、可追溯、可协同的认知闭环里。

当前版本已经从“最小演示骨架”推进到“可执行的 CPS 控制中枢雏形”：

- 导航链路具备 CPA/TCPA 风险评估和基于 COLREGs 的遭遇规则判断。
- 机舱链路具备健康评分、趋势判断、故障诊断和维护建议。
- 能效链路具备 EEXI/CII/SEEMP 的合规能力和优化建议入口。
- 感知链路具备多源事件融合、风险关联和记忆层持久化。
- 决策链路可以把跨域信号编排成任务化 action plan 和 mission brief。
- 数字孪生前端可以统一消费本地 dashboard、AI Native 协调状态和外部海事态势。

## 当前交付状态

当前分支已完成本轮 18 小时冲刺的核心交付，状态为“可运行、可验证、可联调”：

- ECF feedback loop 已闭环，反馈事件会进入认知快照和 decision feedback 记录。
- Orchestration graph 已落地，后端输出 `task_graph`，前端驾驶台和 3D twin 可消费。
- Feature fusion 已接入数字孪生，支持融合轨迹状态查询和场景标记。
- Lightweight lakehouse 已可用于近期事件查询、回放和 memory profile 展示。
- Maritime scene model 已接入导航链路，COLREGs 判断具备 scene-aware contextual rule。
- RCS control loop 第一版已接入，输出 T-Foil、Trim Tabs、roll/heave 控制目标。
- SHM monitoring chain 第一版已接入，输出弯矩、扭转、疲劳损伤和寿命余度。
- OpenBridge HMI 第一版已接入，桥楼聊天和驾驶台可共享任务图、控制摘要和结构健康摘要。

当前已验证通过：

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/unit/test_cps_mission_brief.py tests/integration/test_ai_native_endpoints.py
```

结果：`9 passed`

## 当前执行计划

- 18 小时压缩执行计划：`docs/AI_NATIVE_CPS_18H_EXECUTION_PLAN.md`
- 4 小时改写计划：`docs/AI_NATIVE_CPS_4H_REWRITE_PLAN.md`
- OpenBridge 使用说明：`docs/OPENBRIDGE_QUICK_GUIDE.md`
- Test case 集合：`tests/TEST_CASE_COLLECTION.md`

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
- 事件持久化
- 查询 / 回放 / 记忆概况

### 5. 决策编排器

文件：`src/backend/channels/decision_orchestrator.py`

能力：

- 汇总跨域状态
- 生成 `mission_brief`
- 生成任务化 `action_plan`
- 记录反馈，形成闭环

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
- `GET /api/v1/ai-native/cps/mission-brief`
- `GET /api/v1/ai-native/perception/fusion-state`
- `GET /api/v1/ai-native/rcs/status`
- `GET /api/v1/ai-native/shm/status`
- `POST /api/v1/ai-native/openbridge/command`

### 外部态势

- `GET /api/v1/worldmonitor/ais`
- `GET /api/v1/worldmonitor/weather?lat=<lat>&lng=<lng>`
- `GET /api/v1/worldmonitor/ports`
- `GET /api/v1/worldmonitor/routes`

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

### 3. 启动前端

```bash
npm run dev -- --host 0.0.0.0
```

### 4. 打开交付入口

- 数字孪生：`http://localhost:5173/digital-twin.html`
- 前端首页：`http://localhost:5173/`
- 后端文档：`http://localhost:8080/docs`
- WebSocket：`ws://localhost:8080/ws`

### 5. 验证核心接口

建议至少检查以下接口：

- `GET /api/v1/dashboard`
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
- 数字孪生页面能看到 task graph、fusion tracks、RCS、SHM 卡片
- `Poseidon-X Bridge` 可响应任务图、碰撞风险、舒适控制、结构健康、主机状态等命令

## OpenBridge 命令入口

桥楼命令现在有两条入口：

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