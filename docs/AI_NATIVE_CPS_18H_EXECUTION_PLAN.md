# AI Native 深海远洋 CPS 18 小时执行计划

**版本**: v1.0  
**时间窗口**: 18 小时连续冲刺  
**目标**: 在现有代码基线上，把 ECF、CPS、数字孪生、轻量湖仓、COLREGs、协作层、RCS、SHM、OpenBridge 的关键缺口压缩到 18 小时内完成一轮可验收交付。

## 1. 冲刺原则

18 小时不是把 18 天的工作量硬塞进去，而是把范围重组为：

- P0: 必须完成，且完成后能形成闭环演示。
- P1: 必须有代码落地，但允许先做可扩展骨架。
- P2: 必须形成接口和前端展示，不要求达到生产级控制精度。

本次冲刺的完成标准不是“概念齐全”，而是：

- 后端形成统一任务图和统一状态源。
- 前端数字孪生能直接消费融合、场景、任务、控制、结构健康数据。
- 轻量 Lakehouse 方案定型并写入实现和文档。
- COLREGs、海事场景、OpenBridge 控制入口形成可演示链路。
- RCS 和 SHM 至少具备第一版数据链路、接口、展示和回归测试。

## 2. 总体验收范围

### P0 必达

- ECF 闭环学习落地
- 前后端统一协作图
- Feature Fusion 接入数字孪生
- 轻量 Lakehouse 定型
- MaritimeSceneModel 场景语义层
- COLREGs 规则扩展
- 集成验证和文档更新

### P1 必达

- IER/AR 场景叠层第一版
- OpenBridge 统一控制屏第一版
- NLP 命令语义统一到后端任务图

### P2 必达

- RCS 第一版控制量输出和数字孪生展示
- SHM 第一版结构健康链路和展示

## 3. 小时级计划

### Hour 0-1: 收敛架构和边界

- 冻结本轮范围，明确 18 小时内的降级策略。
- 新增执行计划文档、验收标准和开发顺序。
- 标记当前 todo 的 P0/P1/P2 优先级。

**交付物**:

- `docs/AI_NATIVE_CPS_18H_EXECUTION_PLAN.md`
- 更新后的 README 入口

### Hour 1-3: ECF 闭环和统一协作图

- 为 `ComplianceDigitalExpert` 增加学习状态结构：规则置信度、反馈计数、最近闭环结果。
- 为 `DecisionOrchestrator` 增加统一 task graph 输出，替代前端单独关键词编排的主地位。
- 给 `BridgeChat` 和前端聚合器预留任务图消费接口。

**完成定义**:

- `/ai-native/cps/mission-brief` 返回统一任务图摘要。
- 反馈事件能够影响学习状态，而不是只写日志。

### Hour 3-5: 轻量 Lakehouse 定型

- 明确并固化 `SQLite WAL + Parquet + DuckDB + S3-compatible sync` 方案。
- 为 `DataLakehouse` 增加存储模式、归档策略和分析入口元信息。
- 更新文档，明确“不使用 Hadoop”的工程决策。

**完成定义**:

- 状态接口能直接返回当前 store profile、archive policy、query mode。
- README 和架构文档反映轻量方案。

### Hour 5-8: Feature Fusion 接入数字孪生

- 把 `FeatureFusionLayer` 接到 `DistributedPerceptionHub` 的实际输出链路。
- 增加融合轨迹 API。
- 数字孪生海图显示 fused track、risk ellipse、confidence、source sensors。

**完成定义**:

- 前端不是只看导航风险高亮，而是直接显示融合目标。
- 有基础测试覆盖融合输出结构。

### Hour 8-10: MaritimeSceneModel + COLREGs 扩展

- 新增海事场景模型，表达港区、狭水道、冰区、离岸平台区、分道通航、受限水域。
- 扩展导航规则引擎，加入 Rule 18、受限场景规则和场景上下文。
- 决策包和合规快照引用场景语义，而不是只引用 CPA/TCPA。

**完成定义**:

- 导航报告包含 `scene_context`。
- `colregs_assessments` 包含场景限制和优先通行角色。

### Hour 10-12: IER/AR 第一版叠层

- 数字孪生海图增加场景图层、危险水域和特殊目标模板。
- 增加离岸、入港、冰山、海峡四种场景叠层规则。
- 增加目标堆叠优先级：CPA、TCPA、risk、occlusion、scene priority。

**完成定义**:

- 前端可视化能切换场景模式。
- 场景目标不再是纯 AIS 方块。

### Hour 12-14: OpenBridge HMI + NLP 统一语义

- 用现有 `BridgeChat + DigitalTwinMap + mission brief` 组装 OpenBridge 第一版布局。
- 将前端动作命令统一映射到后端 task graph，不再以关键词直接调用为主。
- 增加任务卡、告警区、上下文区和控制区。

**完成定义**:

- 用户命令走 `NLP -> task graph -> backend action -> HMI update`。
- 数字孪生和控制区同步显示任务状态。

### Hour 14-16: RCS + SHM 第一版

- 加入 RCS 状态模型：`foil_angle_deg`、`trim_tab_angle_deg`、`roll_rate_cmd`、`heave_damping_gain`、`comfort_target_msdv`。
- 加入 SHM 状态模型：应变、弯矩、扭转、疲劳损伤、寿命余度。
- 数字孪生新增 RCS/SHM 面板或合并控制窗。

**完成定义**:

- 后端接口能返回 RCS/SHM 数据。
- 前端可视化能展示关键数值和告警。

### Hour 16-18: 联调、测试、文档、收尾

- 跑聚焦测试和新增接口测试。
- 更新 README、架构文档、执行计划状态。
- 生成交付摘要和已知风险。

**完成定义**:

- 聚焦测试通过。
- 文档与代码一致。
- 能给出剩余风险和下一阶段建议。

## 4. 对应总 Todo 的落地映射

| Todo | 优先级 | 时间窗 | 输出 |
|------|--------|--------|------|
| Close ECF feedback loop | P0 | Hour 1-3 | 学习状态、反馈回写 |
| Unify orchestration graph | P0 | Hour 1-3 | 统一 task graph |
| Finalize lightweight lakehouse | P0 | Hour 3-5 | 轻量存储定型 |
| Expose fusion to twin | P0 | Hour 5-8 | 融合轨迹 + twin overlay |
| Add maritime scene model | P0 | Hour 8-10 | 场景语义层 |
| Expand COLREGs coverage | P0 | Hour 8-10 | 场景化规则输出 |
| Upgrade OpenBridge HMI | P1 | Hour 12-14 | 统一控制屏第一版 |
| Implement RCS control loop | P2 | Hour 14-16 | RCS 状态与展示 |
| Build SHM monitoring chain | P2 | Hour 14-16 | SHM 状态与展示 |
| Run integrated validation | P0 | Hour 16-18 | 测试与交付摘要 |

## 5. 强制降级策略

如果在 18 小时内遭遇阻塞，按以下顺序降级，但不允许破坏主闭环：

1. RCS 先做状态模型和显示，不做高保真控制器。
2. SHM 先做结构监测链路和寿命指标，不做复杂有限元反演。
3. IER 先做场景叠层和优先级，不做真实 AR 标定。
4. OpenBridge 先做统一布局和任务卡，不做完整工业设计规范复刻。

## 6. 18 小时结束时必须能展示的内容

- 一个统一的 AI Native 任务图和 mission brief。
- 一个能展示融合目标、场景语义、COLREGs 风险的数字孪生前端。
- 一个明确不依赖 Hadoop 的轻量 Lakehouse 方案。
- 一个能展示 RCS 和 SHM 第一版状态的控制界面。
- 一套通过的聚焦测试和更新后的交付文档。

## 7. 当前启动动作

当前从 P0 第一包开始，执行顺序如下：

1. ECF 闭环学习模型
2. 统一 task graph
3. 轻量 Lakehouse 状态扩展
4. Fusion API 和 twin overlay
