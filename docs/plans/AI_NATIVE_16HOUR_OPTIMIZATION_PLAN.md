# AI Native 深海远洋船舶系统 - 16 小时项目优化计划（CaptainCatamaran 重构版）

**重构时间**: 2026-03-15 10:55  
**重构人**: CaptainCatamaran  
**依据**: 用户提供的《AI Native 深海远洋船舶综合信息系统设计蓝图》 + 当前项目实装代码状态  
**目标**: 把原先偏“模块堆叠”的冲刺计划，重构为围绕**认知闭环**推进的 AI Native 架构实施计划。

---

## 0. 当前可复用基础（基于现场硬审计）

项目已存在并可复用的核心能力：

### 已有后端模块
- `src/backend/channels/energy_efficiency_manager.py`
- `src/backend/channels/intelligent_navigation.py`
- `src/backend/channels/intelligent_engine.py`
- `src/backend/channels/nmea2000_parser.py`
- `src/backend/channels/engine_monitor.py`
- `src/backend/channels/marine_message_bus.py`

### 已有系统能力
- FastAPI 后端可启动
- 3 个核心 Channel 已能注册：
  - `energy_efficiency`
  - `intelligent_navigation`
  - `intelligent_engine`
- `digital-twin.html` / `poseidon-config.html` 页面可访问
- 基础 API / Dashboard / query 接口可用

### 当前短板
- 还没有“船舶合规数字专家”模块
- 多模态感知仍偏模拟/规则化，未形成感知融合网络
- 数据层还是内存缓存 + API 结构，未形成真正的湖仓/云存储闭环
- 维护建议与异常分析已存在，但还没有形成“闭环自学习”
- 前端 HMI 还不是 AI Native 的认知界面

---

## 1. 新目标：从“功能模块集合”切换为“AI Native 认知闭环”

本次 16 小时优化，目标不再是继续横向堆模块，而是围绕以下 3 个主闭环推进：

1. **船舶合规数字专家（认知/推理入口）**
2. **分布式感知网络（数据与感知入口）**
3. **全场景决策与运维生成（执行与学习闭环）**

这 3 个部分分别对应：
- 感知（Perception）
- 记忆（Memory / Lakehouse）
- 思维（Reasoning）
- 执行（Action）
- 学习（Learning）

---

## 2. 16 小时优化总策略

### 原则 1：优先做“闭环”而不是“新名词”
优先保证从：
`感知 -> 存储 -> 分析 -> 决策 -> 报告 -> 反馈`
至少跑通一条最小闭环。

### 原则 2：最大化复用现有代码
- `intelligent_navigation.py` → 作为 CAS / CRI / COLREGs 推理骨架
- `intelligent_engine.py` → 作为 IER / 运维生成骨架
- `energy_efficiency_manager.py` → 作为能效 / 合规决策骨架
- `nmea2000_parser.py` → 作为实时感知入口骨架
- `digital-twin.html` + dashboard API → 作为 AI Native HMI 初始落点

### 原则 3：把“AI Native”拆成可落地的软件增量
不是一次把 YOLO、KG、DRL、Lakehouse 全做完，而是先做：
- 接口
- 状态机
- 数据模型
- 规则/知识骨架
- 可替换推理层

---

## 3. 三大模块的实施设计

# A. 船舶合规数字专家（P0）

## 目标
构建一个新的“合规与认知中枢”模块，使系统能够：
- 汇总 COLREGs / CCS 智能船舶规范 / ESWBS / 船端工程知识
- 将 `marine_engineer_agent` 的知识沉淀为顶层逻辑
- 为导航、机舱、能效、运维生成提供统一解释层

## 建议新增模块
- `src/backend/channels/compliance_digital_expert.py`

## 核心职责
1. **规范知识抽象**
   - COLREGs 规则条目
   - 船级社规范条目
   - ESWBS 编码映射
   - 主机/船体/能效维护知识片段

2. **统一推理接口**
   - `query_compliance_status()`
   - `explain_navigation_decision()`
   - `explain_engine_alert()`
   - `generate_maintenance_report()`

3. **顶层逻辑编排**
   - 将导航风险、机舱告警、能效偏差归一到同一认知模型
   - 输出面向船员/工程师的自然语言结论

## 最小实现（本轮 16 小时内）
- 用 Python 数据结构 + 规则模板实现第一版知识骨架
- 接入现有 3 个 Channel 的状态
- 输出统一“合规 / 风险 / 建议 / 引用规则”结果

## 暂不追求
- 真正的大规模知识图谱数据库
- 完整几十万页文档 ingestion
- 真实 LLM 自动蒸馏全规范语料

---

# B. 分布式感知网络（P0）

## 目标
把当前“模块各自维护状态”升级为一层统一的数据采集与存储骨架，支持后续多模态融合。

## 建议新增模块
- `src/backend/channels/distributed_perception_hub.py`
- `src/backend/storage/cloud_sync.py`
- `src/backend/storage/event_store.py`

## 数据来源
- `nmea2000_parser.py`
- engine snapshots
- navigation targets / collision risks
- efficiency metrics
- 未来可扩展视频/视觉检测结果

## 目标结构
### 船端边缘层
- 本地缓存实时事件
- 支持低延迟 CRI / engine / efficiency 更新

### 云存储层（可先简化）
底层不强行上 HDFS/Kudu，先抽象成：
- 本地事件存储（JSONL / SQLite / Parquet 任一种）
- 远端对象存储接口占位（S3 兼容 / 云盘 / OSS 风格接口）

## 最小实现（本轮 16 小时内）
- 抽象统一 Event schema：
  - `navigation_event`
  - `engine_event`
  - `efficiency_event`
  - `maintenance_event`
- 将 3 个现有 Channel 的核心状态写入事件流
- 增加一个“云同步适配器”接口，不要求真实上云，但保留挂接点

## 暂不追求
- 完整 Lakehouse 产品化
- 大规模图像/声呐数据处理
- 实时视觉模型训练

---

# C. 全场景决策与运维生成（P0）

## 目标
在现有项目代码基础上，形成“异常发现 -> 原因解释 -> 运维报告 -> 建议动作 -> 反馈记录”的闭环。

## 建议新增/增强内容
### 增强 `intelligent_engine.py`
- 告警分级：advisory / warning / critical
- 故障模式映射：
  - 冷却异常
  - 润滑异常
  - 负载异常
  - 燃油效率恶化

### 增强 `energy_efficiency_manager.py`
- 增加事件输出
- 让 CII / EEXI / 建议进入统一事件流

### 增强 `intelligent_navigation.py`
- 增加风险解释结构
- 输出 COLREGs 规则引用

### 新增决策编排层
- `src/backend/channels/decision_orchestrator.py`

职责：
- 汇总 3 大 Channel 状态
- 调用 `compliance_digital_expert`
- 自动生成：
  - 运维报告
  - 风险摘要
  - 建议动作清单
  - 需要追踪的反馈记录

## 闭环自学习（本轮定义为“弱闭环”）
本轮不做真正 RL 在线训练，而做：
- 每次异常都记录：输入状态 / 系统判断 / 建议动作 / 人工确认位
- 为未来 RL / 监督学习积累训练样本

即：
**先实现可学习的数据闭环，再谈模型闭环。**

---

## 4. 16 小时时间切片（重构版）

### 阶段 1（0-2h）：认知骨架建模
**目标**：把“船舶合规数字专家”最小版搭起来

交付：
- `compliance_digital_expert.py`
- 规范/规则基础数据结构
- 与 navigation / engine / efficiency 的状态对接接口
- 基础单测

### 阶段 2（2-6h）：分布式感知与事件流
**目标**：建立统一事件模型

交付：
- `distributed_perception_hub.py`
- `event_store.py`
- `cloud_sync.py`（接口级）
- 将 3 个核心 Channel 写入事件流
- 事件回放/查看 API

### 阶段 3（6-10h）：全场景决策编排
**目标**：形成统一的 AI Native 决策层

交付：
- `decision_orchestrator.py`
- Dashboard 增加综合认知摘要
- 维护报告生成接口
- 风险解释 / 合规说明输出

### 阶段 4（10-13h）：前端 HMI 升级
**目标**：把“认知输出”放到前端界面

交付：
- `digital-twin.html` 增加认知摘要区
- Bridge Chat 可直接查询：
  - 合规状态
  - 机舱解释
  - 导航风险解释
  - 运维建议

### 阶段 5（13-15h）：验证与回归
**目标**：确认闭环可运行

交付：
- 新增单测 / 集成测试
- 跑通最小闭环：
  - 输入事件 -> 风险判断 -> 报告生成 -> 事件记录

### 阶段 6（15-16h）：收尾与可交付状态
**目标**：沉淀为可继续迭代的骨架

交付：
- 文档更新
- 剩余风险清单
- 下一轮 RL / 视觉 / Lakehouse 升级路线

---

## 5. 任务优先级

## P0（本轮必须完成）
- `compliance_digital_expert.py`
- `distributed_perception_hub.py`
- 统一事件 schema
- `decision_orchestrator.py`
- 前后端最小认知闭环

## P1（本轮尽量完成）
- `cloud_sync.py` 真正接一个云存储目标
- 增强 query API
- 更多运维报告模板
- 前端认知看板优化

## P2（本轮不强求）
- 真正知识图谱数据库
- YOLO / Swin Transformer 真模型接入
- DRL 真实在线决策
- 船端/岸基双端协同训练

---

## 6. 产出验收标准

### 真交付必须满足
1. 有明确代码文件
2. 有至少一条测试或运行证据
3. 能在 API / 页面 / 报告中看到效果

### 不计入“已完成”的内容
- 纯计划
- 纯汇报
- 纯分析
- 纯催办

---

## 7. 每半小时汇报规则（本计划强绑定）

每次汇报必须包含：
- **文件改动**：具体文件路径
- **测试结果**：通过/失败/未执行
- **运行结果**：API / 页面 / 脚本验证
- **当前阻塞**：技术/环境/设计
- **下一个 30 分钟目标**

如果连续 30 分钟没有硬产出：
- 必须直接报告 **任务失速**
- 不允许用计划、分析、空泛描述替代进展

---

## 8. CaptainCatamaran 的执行纪律

本轮我不再把“写很多文档”视为推进。
只有以下才算进度：
- 新代码
- 新测试
- 新接口
- 新运行结果
- 新可验证闭环

---

## 9. 当前启动建议（下一步立刻执行）

### 第一优先
1. 新建 `compliance_digital_expert.py`
2. 定义统一认知输出结构：
   - `risk_level`
   - `compliance_status`
   - `evidence`
   - `recommended_actions`
   - `maintenance_report`

### 第二优先
3. 新建 `distributed_perception_hub.py`
4. 把 navigation / engine / efficiency 的状态写入事件流

### 第三优先
5. 新建 `decision_orchestrator.py`
6. 新增聚合 API 给前端消费

---

**这版计划的核心变化**：
- 不再以“功能模块罗列”为主
- 改为以“认知闭环”推进
- 强制每 30 分钟提供证据型状态汇报
- 将 CaptainCatamaran 的职责从“写计划/做报告”收缩为“把闭环落地并留痕”
