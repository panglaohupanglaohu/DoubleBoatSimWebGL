# AI Native 16 小时重构计划 - 代码架构图

**架构版本**: v1.0  
**生成时间**: 2026-03-17  
**架构风格**: 面向通道的事件驱动架构 (Channel-Based Event-Driven Architecture)

---

## 1. 整体架构分层

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI Native 船舶综合信息系统                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         L3: 全闭环预测性维护与决策                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Decision Orchestrator (决策编排器)               │   │
│  │  - 汇总认知节点、感知节点、执行节点状态                             │   │
│  │  - 生成统一风险摘要、运维建议、决策包                               │   │
│  │  - 支持人工反馈闭环记录                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         L2: 感知增强与数据湖仓治理                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              Distributed Perception Hub (感知网络)                  │   │
│  │  - 多源感知融合 (NMEA2000/AIS/WorldMonitor/天气)                   │   │
│  │  - 风险关联计算 (碰撞/机械/合规/气象风险)                           │   │
│  │  - 事件流 capture+融合                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      DataLakehouse (数据湖仓)                        │   │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐      │   │
│  │  │   Local Store    │ │   Cloud Sync     │ │   Event Store    │      │   │
│  │  │  SQLite/JSONL    │ │   S3/Feishu      │ │   Parquet        │      │   │
│  │  │   (边缘缓存)     │ │   Adapter        │ │   (持久化)       │      │   │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         L1: 认知数字化与推理                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                Compliance Digital Expert (合规专家)                 │   │
│  │  - COLREGs 规范知识库                                               │   │
│  │  - CCS 智能船舶规范                                                 │   │
│  │  - ESWBS 编码映射                                                   │   │
│  │  - 统一认知输出接口 (query_compliance_status, explain_*, etc.)     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         L0: 执行节点与数据源                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                Intelligent Navigation (智能导航)                    │   │
│  │  - CPA/TCPA 计算 + COLREGs 风险评估                                │   │
│  │  - AIS 目标追踪与碰撞风险分级                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                  Intelligent Engine (智能机舱)                      │   │
│  │  - 主机/辅机健康监测                                                │   │
│  │  - 故障模式识别与建议                                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                 Energy Efficiency Manager (能效管理)               │   │
│  │  - EEXI/CII/SEEMP 合规计算                                         │   │
│  │  - 能效偏差检测与优化建议                                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    NMEA2000 Parser (数据源)                        │   │
│  │  - 实时 NMEA2000 消息解析                                          │   │
│  │  - AIS A/B 类位置报告提取                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 核心 Channel 数据流图

```
┌──────────────┐    ┌──────────────────────────┐    ┌─────────────────────────┐
│   Data       │───▶│ Distributed Perception   │───▶│                         │
│   Sources    │    │        Hub               │    │                         │
│  (NMEA2000   │    │ - 事件捕获               │    │                         │
│   AIS,       │    │ - 多源融合                 │───▶│  Data Lakehouse         │
│   Weather)   │    │ - 风险关联               │    │  - Local Store          │
│              │    │                          │    │  - Cloud Sync           │
│              │    └──────────────────────────┘    │  - Event Store          │
│              │                                     │                         │
│              │    ┌──────────────────────────┐    │                         │
│              │───▶│   Compliance Digital     │───▶│  Decision Orchestrator  │
│              │    │        Expert            │    │  - 风险汇总             │
│              │    │ - 规范知识库             │    │  - 运维建议             │
│              │    │ - 统一认知输出           │    │  - 决策包生成           │
│              │    └──────────────────────────┘    │                         │
└──────────────┘                                     └─────────────────────────┘

             ▲                                         │
             │                                         ▼
             │    ┌──────────────────────────────────────────┐
             └────│        Intelligent Navigation            │
                  │ - NAV_EVENT → 融合                       │
                  └──────────────────────────────────────────┘

                  ┌──────────────────────────────────────────┐
                  │      Intelligent Engine                  │
                  │ - ENGINE_EVENT → 融合                    │
                  └──────────────────────────────────────────┘

                  ┌──────────────────────────────────────────┐
                  │    Energy Efficiency Manager             │
                  │ - EFFICIENCY_EVENT → 融合               │
                  └──────────────────────────────────────────┘
```

---

## 3. 代码组织结构

```
src/backend/
├── main.py                          # FastAPI 应用入口
├── api_extensions.py                # AI Native API 端点定义
├── register_channels.py             # Channel 注册与初始化
├── marine_channels_integration.py   # Channel 集成测试
│
├── channels/
│   ├── marine_base.py               # Channel 基类定义
│   │
│   ├── intelligent_navigation.py    # L0: 智能导航 (CPA/TCPA + COLREGs)
│   ├── intelligent_engine.py        # L0: 智能机舱 (健康监测 + 故障诊断)
│   ├── energy_efficiency_manager.py # L0: 能效管理 (EEXI/CII/SEEMP)
│   ├── nmea2000_parser.py           # L0: 数据源 (NMEA2000 解析)
│   │
│   ├── compliance_digital_expert.py # L1: 认知数字化 (COLREGs + 规范库)
│   │
│   ├── distributed_perception_hub.py # L2: 感知网络 (多源融合 + 风险关联)
│   │
│   └── decision_orchestrator.py     # L3: 决策编排 (风险汇总 + 运维建议)
│
└── storage/
    ├── data_lakehouse.py            # L2: 数据湖仓 (Local + Cloud)
    ├── event_store.py               # L2: 事件存储 (SQLite/JSONL/Parquet)
    └── cloud_sync.py                # L2: 云同步 (S3/Feishu/LocalFile)
```

---

## 4. 核心接口定义

### 4.1 感知层接口 (DistributedPerceptionHub)
```python
class DistributedPerceptionHubChannel(MarineChannel):
    # 感知融合接口
    def fuse_ais_with_navigation(ais_payload, nav_payload) -> FusionEvent
    def fuse_weather_with_efficiency(weather_payload, efficiency_payload) -> FusionEvent
    def capture_system_snapshot() -> List[FusionEvent]
    
    # 事件流接口
    def get_latest_events(limit: int = 20) -> List[Dict]
    def append_event(event_type, payload, source, confidence) -> FusionEvent
```

### 4.2 认知层接口 (ComplianceDigitalExpert)
```python
class ComplianceDigitalExpertChannel(MarineChannel):
    # 统一认知输出接口
    def query_compliance_status(query: str) -> Dict  # 支持 navigation/engine/efficiency 查询
    def explain_navigation_decision() -> Dict         # 导航风险解释
    def explain_engine_alert() -> Dict                # 机舱告警解释
    def build_cognitive_snapshot() -> Dict            # 完整认知快照
    def generate_maintenance_report() -> Dict         # 运维报告生成
```

### 4.3 决策层接口 (DecisionOrchestrator)
```python
class DecisionOrchestratorChannel(MarineChannel):
    # 决策接口
    def build_decision_package() -> Dict              # 构建决策包
    def record_feedback(action, outcome, confirmed_by) -> Dict  # 记录反馈
```

### 4.4 数据湖仓接口 (DataLakehouse)
```python
class DataLakehouse:
    # 存储接口
    def save_event(event) -> bool
    def save_batch(events) -> bool
    def query_events(event_type, limit) -> List[Dict]
    def query_events_by_time(start_time, end_time, event_type) -> List[Dict]
    def get_status() -> Dict  # 湖仓状态查询
```

---

## 5. 风险关联模型

```python
RISK_CORRELATIONS = {
    "collision_risk": ["ais_target_proximity", "weather_severity", "engine_availability"],
    "mechanical_risk": ["engine_status", "maintenance_schedule", "operational_hours"],
    "compliance_risk": ["cii_deviation", "eexi_threshold", "seemp_adherence"],
    "weather_risk": ["wave_height", "wind_speed", "visibility", "current_strength"]
}
```

---

## 6. 数据流示例 (从感知到决策)

```
1. 数据采集
   └─ NMEA2000 → AIS Position Report (PGN 129038/129039)
   └─ WorldMonitor → Weather Data
   └─ IntelligentNavigation → Own Ship Position + AIS Targets
   
2. 感知融合
   └─ fuse_ais_with_navigation(ais_payload, nav_payload)
   └─ fuse_weather_with_efficiency(weather_payload, efficiency_payload)
   └─ Capture FusionEvent with confidence score
   
3. 事件存储
   └─ DistributedPerceptionHub.events.append(fusion_event)
   └─ DataLakehouse.save_event(fusion_event.to_dict())
   
4. 认知聚合
   └─ ComplianceDigitalExpert.build_cognitive_snapshot()
   └─ query_compliance_status() => risk_level, evidence, actions
   
5. 决策编排
   └─ DecisionOrchestrator.build_decision_package()
   └─ combine cognitive snapshot + latest events + recommended actions
   
6. 输出
   └─ API /api/v1/ai-native/decision/package
   └─ API /api/v1/ai-native/compliance/status
   └─ 前端页面显示风险摘要 + 运维建议
```

---

## 7. 认知输出结构

```python
{
    "timestamp": "2026-03-17T04:00:00",
    "risk_level": "low" | "medium" | "high",
    "compliance_status": "compliant" | "attention_required",
    "evidence": [
        "navigation:warning",
        "engine:temperature_alert"
    ],
    "recommended_actions": [
        "依据 COLREGs 规则复核避碰动作与瞭望状态",
        "执行机舱点检并确认故障诊断结果"
    ],
    "maintenance_report": {
        "title": "AI Native 运维摘要",
        "actions": ["Check engine temperature sensor calibration"]
    },
    "rules": [
        " COLREGs Rule 7: 使用一切适当手段判断碰撞危险",
        " COLREGs Rule 8: 避碰行动应及早、明显并有效"
    ],
    "navigation": {...},
    "engine": {...},
    "efficiency": {...}
}
```

---

## 8. 简化版模块依赖图

```
┌──────────────────────────────────────────────────────────────────┐
│                    AI Native Architecture                        │
└──────────────────────────────────────────────────────────────────┘

L3: DecisionOrchestrator
   └─ depends on: [
        compliance_digital_expert,
        distributed_perception_hub,
        intelligent_navigation,
        intelligent_engine,
        energy_efficiency
      ]

L2: DistributedPerceptionHub
   └─ depends on: [
        intelligent_navigation,
        intelligent_engine,
        energy_efficiency,
        nmea2000_parser,
        worldmonitor_real
      ]
   └─ uses: [
        data_lakehouse for event persistence,
        cloud_sync for remote storage
      ]

L1: ComplianceDigitalExpert
   └─ depends on: [
        intelligent_navigation,
        intelligent_engine,
        energy_efficiency
      ]
   └─ knowledge_base: [
        COLREGs_Rules,
        CCS_Intelligent_Ship,
        ESWBS_Code
      ]

L0: IntelligentNavigation
L0: IntelligentEngine
L0: EnergyEfficiencyManager
L0: NMEA2000Parser
```

---

## 9. 扩展建议 (Phase 2+)

| 功能 | 模块 | 优先级 |
|------|------|--------|
| YOLOv5 机舱视觉检测 | vision_detector.py | P1 |
| COLREGs 知识图谱 | knowledge_graph.py | P1 |
| 贝叶斯 CRI 评判 | bayesian_cri_evaluator.py | P2 |
| DRL 路径规划 | drl_path_planner.py | P2 |
| LSTM 预测性维护 | lstm_predictor.py | P3 |
| Sklearn 故障诊断 | sklearn_fdd.py | P3 |

---

## 10. 实时性能目标

| 指标 | 目标 | 验证方法 |
|------|------|----------|
| API 响应时间 | < 100ms | `scripts/run_tests.py` |
| 数据处理吞吐 | > 1000 TPS | `test_data_lakehouse.py` |
| 事件融合延迟 | < 3 秒 | 分布式感知网络 warmup 测试 |
| 并发用户支持 | > 10 | FastAPI 测试 |

---

**架构总结**：采用**轻量级、模块化、事件驱动**的设计原则，避免 Hadoop 等重量级组件，优先保证快速落地与可验证性，逐步迭代至 MASS Level 4 的自主航行能力。