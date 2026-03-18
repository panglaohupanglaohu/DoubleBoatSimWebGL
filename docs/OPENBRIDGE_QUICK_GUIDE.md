# OpenBridge Quick Guide

本页用于快速说明当前版本 OpenBridge 命令入口、支持范围和最短联调路径。

## 入口

- UI 入口：`http://localhost:5173/digital-twin.html` 右下角 `Poseidon-X Bridge`
- API 入口：`POST /api/v1/ai-native/openbridge/command`

## 最小使用流程

### 1. 启动系统

```bash
source venv/bin/activate
python src/backend/main.py --host 0.0.0.0 --port 8080
```

```bash
npm run dev -- --host 0.0.0.0
```

### 2. 打开数字孪生

访问：`http://localhost:5173/digital-twin.html`

### 3. 在桥楼输入命令

可直接输入：

- `任务图`
- `碰撞风险`
- `舒适控制`
- `结构健康`
- `主机状态`

未配置外部 LLM 时，本地命令语义仍可使用；配置 LLM 后，通用问答会继续走外部模型。

## API 调用示例

```bash
curl -X POST http://localhost:8080/api/v1/ai-native/openbridge/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "请切到舒适控制并给出当前任务图摘要",
    "source": "bridge_chat"
  }'
```

## 当前支持的语义意图

- `show_task_graph`：任务图、mission brief、行动计划
- `show_collision_risk`：碰撞风险、COLREGs、导航风险
- `set_comfort_mode`：舒适控制、RCS、减摇、姿态
- `show_structural_health`：结构健康、SHM、疲劳、寿命
- `show_engine_health`：主机状态、机舱健康、维护建议
- `general_assist`：通用辅助问答

## 返回字段说明

- `recognized_intent`：识别出的命令意图
- `execution_mode`：当前执行模式
- `summary`：面向值班员的摘要
- `operator_action`：建议操作
- `task_graph`：任务图摘要
- `control_state.rcs`：RCS 控制摘要
- `control_state.shm`：SHM 结构健康摘要
- `focus_items`：当前命令下最值得关注的条目

## 联调检查点

- `GET /api/v1/dashboard` 返回 `decision`、`rcs`、`shm`
- `GET /api/v1/ai-native/cps/mission-brief` 返回 `task_graph`
- `GET /api/v1/ai-native/rcs/status` 返回控制目标
- `GET /api/v1/ai-native/shm/status` 返回疲劳和寿命余度
- `POST /api/v1/ai-native/openbridge/command` 返回语义摘要

## 当前边界

- 当前版本是“语义命令编排 + 状态摘要”，不是直接写入真实执行机构的控制系统
- OpenBridge UI 目前以数字孪生驾驶台和桥楼聊天为主，还不是完整独立控制台
- 外部 LLM 不是命令链路的必需项，只影响通用问答体验