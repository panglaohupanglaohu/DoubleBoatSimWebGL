# AI Native 16 小时重构计划 - 代码架构图

**架构版本**: v2.0  
**生成时间**: 2026-03-26  
**架构风格**: 面向通道的事件驱动架构 (Channel-Based Event-Driven Architecture)  
**Channel 总数**: 46 个 MarineChannel 模块 (L0–L5 六层)

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
├── channels/                        # 46 个 MarineChannel 模块
│   ├── marine_base.py               # Channel 基类定义
│   ├── marine_message_bus.py        # 内部消息总线
│   │
│   │   ── L0: 执行节点与数据源 ──
│   ├── intelligent_navigation.py    # L0: 智能导航 (CPA/TCPA + COLREGs)
│   ├── intelligent_engine.py        # L0: 智能机舱 (健康监测 + 故障诊断)
│   ├── energy_efficiency_manager.py # L0: 能效管理 (EEXI/CII/SEEMP)
│   ├── nmea2000_parser.py           # L0: 数据源 (NMEA2000 解析)
│   ├── deterministic_network.py     # L0: 确定性网络 (TSN 时间敏感)
│   │
│   │   ── L1: 认知数字化与推理 ──
│   ├── compliance_digital_expert.py # L1: 认知数字化 (COLREGs + 规范库)
│   ├── nats_event_bus.py            # L1: NATS 事件总线 (发布/订阅)
│   │
│   │   ── L2: 感知增强与传感器/合规 ──
│   ├── distributed_perception_hub.py # L2: 感知网络 (多源融合 + 风险关联)
│   ├── structural_health_monitor.py # L2: 结构健康监测 (弯矩/扭转/疲劳)
│   ├── ballast_water_monitor.py     # L2: 压载水管理 (BWM Convention D-2 合规)
│   ├── emission_monitor.py          # L2: 排放监测 (SOx ECA 排放合规)
│   ├── anchor_watch_channel.py      # L2: 锚泊监控 (走锚检测)
│   ├── cargo_monitor.py             # L2: 货舱监控 (货物状态 + 稳性)
│   ├── fire_detection_channel.py    # L2: 火灾探测 (烟雾/温度/火焰)
│   ├── bilge_water_monitor.py       # L2: 舱底水监测 (MARPOL 合规)
│   ├── gyro_compass_monitor.py      # L2: 电罗经监控 (一致性校验)
│   ├── speed_log_monitor.py         # L2: 计程仪监控 (航速测量)
│   ├── echo_sounder_monitor.py      # L2: 测深仪监控 (水深 + 搁浅预警)
│   ├── tank_level_monitor.py        # L2: 液舱液位监控 (燃油/淡水/压载)
│   ├── hull_stress_monitor.py       # L2: 船体应力监测 (应力/变形)
│   ├── rudder_control_monitor.py    # L2: 舵机监控 (SOLAS 合规)
│   ├── mooring_monitor.py           # L2: 系泊监控 (缆绳张力/绞车)
│   │
│   │   ── L3: 决策/导航/自治 ──
│   ├── decision_orchestrator.py     # L3: 决策编排 (跨域任务图 + 行动计划)
│   ├── colregs_brain.py             # L3: COLREGs 自主大脑 (避碰决策)
│   ├── weather_routing_channel.py   # L3: 气象导航 (天气预报 + 航线风险 + 空间分辨率)
│   ├── predictive_health.py         # L3: 预测性健康 (退化趋势 + 维护窗口)
│   ├── route_optimizer.py           # L3: 航线优化 (路径策略)
│   ├── voyage_planner.py            # L3: 航次计划 (航段管理)
│   ├── vdr_recorder.py              # L3: VDR 航行数据记录仪 (SOLAS 合规记录)
│   ├── ais_processor.py             # L3: AIS 独立处理器 (目标追踪 + MMSI 查询)
│   ├── alarm_management.py          # L3: 集中告警管理 (告警分级 + 确认)
│   ├── man_overboard.py             # L3: MOB 落水告警 (紧急响应)
│   ├── safety_system_monitor.py     # L3: 安全系统综合监控 (SOLAS 合规)
│   │
│   │   ── L4: 控制与自治执行 ──
│   ├── rcs_control.py               # L4: RCS 姿态控制 (T-Foil/Trim Tab)
│   ├── wpc_attitude_control.py      # L4: 穿浪双体船姿态控制
│   ├── autonomy_manager.py          # L4: 自治等级管理 (MASS/LR 映射)
│   ├── ship_shore_link.py           # L4: 船岸通信链路 (多链路质量/冗余)
│   ├── cyber_security.py            # L4: 网络安全 (威胁态势/审计)
│   ├── dynamic_positioning.py       # L4: 动态定位 (DP 定点控制)
│   ├── autopilot_monitor.py         # L4: 自动舵监控 (航向保持)
│   ├── propulsion_monitor.py        # L4: 推进系统监控 (主机/推进器)
│   ├── power_management.py          # L4: 电力管理 (发电/配电/负载)
│   │
│   │   ── L5: 人机交互 ──
│   ├── openbridge_hmi.py            # L5: OpenBridge HMI (桥楼交互)
│   ├── crew_fatigue_monitor.py      # L5: 船员疲劳监控 (值班追踪 + 疲劳评分)
│   ├── communication_manager.py     # L5: 通信管理 (GMDSS 合规)
│   │
│   │   ── 系统持续构建 ──
│   ├── build_team_manager.py        # 构建智能体团队管理器
│   └── execution_team_manager.py    # 执行智能体团队管理器
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
        energy_efficiency,
        weather_routing_channel,
        alarm_management,
        safety_system_monitor
      ]

L3: WeatherRoutingChannel
   └─ depends on: [
        route_optimizer,
        decision_orchestrator
      ]
   └─ event_types: [
        weather_forecast,
        route_candidate,
        weather_alert
      ]

L3: VDRRecorder
   └─ depends on: [
        intelligent_navigation,
        intelligent_engine,
        distributed_perception_hub
      ]
   └─ event_types: [
        vdr_snapshot,
        vdr_integrity_check
      ]

L3: AISProcessor
   └─ depends on: [
        nmea2000_parser,
        intelligent_navigation
      ]
   └─ event_types: [
        ais_target_update,
        ais_target_lost
      ]

L3: AlarmManagement
   └─ depends on: [
        distributed_perception_hub,
        decision_orchestrator
      ]
   └─ event_types: [
        alarm_raised,
        alarm_acknowledged,
        alarm_cleared
      ]

L3: ManOverboard
   └─ depends on: [
        intelligent_navigation,
        communication_manager,
        alarm_management
      ]
   └─ event_types: [
        mob_activated,
        mob_deactivated,
        mob_position_update
      ]

L3: SafetySystemMonitor
   └─ depends on: [
        fire_detection_channel,
        bilge_water_monitor,
        alarm_management
      ]
   └─ event_types: [
        safety_status_update,
        safety_violation
      ]

L5: CrewFatigueMonitor
   └─ depends on: [
        autonomy_manager,
        decision_orchestrator
      ]
   └─ event_types: [
        watch_change,
        rest_record,
        workload_event
      ]

L5: CommunicationManager
   └─ depends on: [
        ship_shore_link,
        alarm_management
      ]
   └─ event_types: [
        gmdss_status,
        comm_link_change
      ]

L4: DynamicPositioning
   └─ depends on: [
        intelligent_navigation,
        propulsion_monitor,
        rudder_control_monitor
      ]
   └─ event_types: [
        dp_station_set,
        dp_deviation,
        dp_mode_change
      ]

L4: AutopilotMonitor
   └─ depends on: [
        intelligent_navigation,
        gyro_compass_monitor,
        rudder_control_monitor
      ]
   └─ event_types: [
        autopilot_mode_change,
        heading_deviation
      ]

L4: PropulsionMonitor
   └─ depends on: [
        intelligent_engine,
        power_management
      ]
   └─ event_types: [
        propulsion_status,
        engine_parameter_change
      ]

L4: PowerManagement
   └─ depends on: [
        intelligent_engine,
        energy_efficiency
      ]
   └─ event_types: [
        power_load_change,
        generator_event
      ]

L2: BallastWaterMonitor
   └─ depends on: [distributed_perception_hub]
   └─ event_types: [bwm_status, bwm_compliance_alert]

L2: EmissionMonitor
   └─ depends on: [energy_efficiency, distributed_perception_hub]
   └─ event_types: [emission_reading, eca_violation]

L2: AnchorWatchChannel
   └─ depends on: [intelligent_navigation]
   └─ event_types: [anchor_set, anchor_drag_alert]

L2: CargoMonitor
   └─ depends on: [distributed_perception_hub]
   └─ event_types: [cargo_status, stability_alert]

L2: FireDetectionChannel
   └─ depends on: [alarm_management]
   └─ event_types: [fire_alarm, smoke_detection]

L2: BilgeWaterMonitor
   └─ depends on: [distributed_perception_hub]
   └─ event_types: [bilge_level, marpol_violation]

L2: GyroCompassMonitor
   └─ depends on: [nmea2000_parser]
   └─ event_types: [heading_update, compass_error]

L2: SpeedLogMonitor
   └─ depends on: [nmea2000_parser]
   └─ event_types: [speed_update, calibration_alert]

L2: EchoSounderMonitor
   └─ depends on: [nmea2000_parser, intelligent_navigation]
   └─ event_types: [depth_update, grounding_alert]

L2: TankLevelMonitor
   └─ depends on: [distributed_perception_hub]
   └─ event_types: [tank_level, fuel_endurance_update]

L2: HullStressMonitor
   └─ depends on: [structural_health_monitor]
   └─ event_types: [stress_reading, fatigue_alert]

L2: RudderControlMonitor
   └─ depends on: [nmea2000_parser]
   └─ event_types: [rudder_angle, solas_compliance]

L2: MooringMonitor
   └─ depends on: [distributed_perception_hub]
   └─ event_types: [line_tension, winch_status]

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

## 9. 双智能体集合架构 (Dual Agent-Set)

系统采用岸基监督 / 船载执行双智能体集合架构，通过 CoordinationBus 实现协调通信。

### 9.1 架构概览

```
┌─────────────────────────────────────┐
│        AgentSetCoordinator          │  ← 顶层协调器
│  owns CoordinationBus (deque×2)     │
└──────┬────────────────────┬─────────┘
       │ DOWNLINK           │ UPLINK
       ▼                    │
┌──────────────────┐  ┌─────┴────────────┐
│ ShoreSupervision │  │ ShipboardExecution│
│     Set          │  │      Set          │
│                  │  │                   │
│ • compliance     │  │ • perception_hub  │
│ • cyber_security │  │ • navigation      │
│ • voyage_planner │  │ • engine          │
│                  │  │ • energy_eff      │
│ Cycle: collect → │  │ • pred_health     │
│  audit → push    │  │ • route_optimizer │
└──────────────────┘  │                   │
                      │ Cycle: sense →    │
                      │  decide → act →   │
                      │  report           │
                      └───────────────────┘
```

### 9.2 核心模块

| 模块 | 文件 | 职责 |
|------|------|------|
| CoordinationBus | `agent_set_protocol.py` | 双向有界队列消息总线 (downlink / uplink) |
| AgentSet | `agent_set_base.py` | 复合 Channel 基类, 管理成员 + 总线绑定 |
| ShoreSupervisionSet | `shore_supervision_set.py` | 岸基监督: 合规审计, 安全威胁, 航次指令 |
| ShipboardExecutionSet | `shipboard_execution_set.py` | 船载执行: 感知融合, 遥测上报, 模式切换 |
| AgentSetCoordinator | `agent_set_coordinator.py` | 协调器: relay_cycle 驱动双向数据流 |

### 9.3 消息类型 (CoordinationMessageType)

| 方向 | 消息类型 | 用途 |
|------|---------|------|
| ↓ Downlink | POLICY_UPDATE | 政策更新 |
| ↓ Downlink | COMPLIANCE_CONSTRAINT | 合规约束 |
| ↓ Downlink | VOYAGE_DIRECTIVE | 航次指令 |
| ↓ Downlink | SECURITY_ADVISORY | 安全公告 |
| ↓ Downlink | OVERRIDE_COMMAND | 远程覆写 |
| ↑ Uplink | EXECUTION_STATE | 执行状态 |
| ↑ Uplink | TELEMETRY_REPORT | 遥测数据 |
| ↑ Uplink | ANOMALY_ALERT | 异常告警 |
| ↑ Uplink | DECISION_FEEDBACK | 决策反馈 |
| ↑ Uplink | EVIDENCE_UPLOAD | 证据上传 |
| ↔ Both | HEARTBEAT / ACK / HANDSHAKE | 链路管理 |

### 9.4 船载执行模式 (ExecutionMode)

| 模式 | 触发条件 |
|------|---------|
| NORMAL | 所有成员健康 |
| DEGRADED | 1+ 成员 error 或 2+ 异常 |
| EMERGENCY | 3+ 成员 error |
| AUTONOMOUS | 连续 5+ 周期无 downlink |
| STANDBY | 手动置入 |

### 9.5 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/agent-sets/status` | 双集合全局状态 |
| GET | `/api/v1/agent-sets/{set_id}/status` | 单集合状态 (shore/ship) |
| POST | `/api/v1/agent-sets/relay` | 触发一次 relay cycle |

---

## 10. 扩展建议 (Phase 2+)

| 功能 | 模块 | 优先级 |
|------|------|--------|
| YOLOv5 机舱视觉检测 | vision_detector.py | P1 |
| COLREGs 知识图谱 | knowledge_graph.py | P1 |
| 贝叶斯 CRI 评判 | bayesian_cri_evaluator.py | P2 |
| DRL 路径规划 | drl_path_planner.py | P2 |
| LSTM 预测性维护 | lstm_predictor.py | P3 |
| Sklearn 故障诊断 | sklearn_fdd.py | P3 |

---

## 11. 实时性能目标

| 指标 | 目标 | 验证方法 |
|------|------|----------|
| API 响应时间 | < 100ms | `scripts/run_tests.py` |
| 数据处理吞吐 | > 1000 TPS | `test_data_lakehouse.py` |
| 事件融合延迟 | < 3 秒 | 分布式感知网络 warmup 测试 |
| 并发用户支持 | > 10 | FastAPI 测试 |

---

**架构总结**：采用**轻量级、模块化、事件驱动**的设计原则，避免 Hadoop 等重量级组件，优先保证快速落地与可验证性，逐步迭代至 MASS Level 4 的自主航行能力。