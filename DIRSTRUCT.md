# AI Native 代码目录结构 (2026-03-17)

```
src/
├── backend/                          # 后端核心代码
│   ├── main.py                       # FastAPI 应用入口
│   ├── api_extensions.py             # AI Native API 端点定义
│   ├── register_channels.py          # Channel 注册与初始化
│   ├── marine_channels_integration.py # Channel 集成测试
│   │
│   ├── channels/                     # 核心 Channel 模块
│   │   ├── marine_base.py            # Channel 基类定义
│   │   ├── marine_message_bus.py     # 消息总线
│   │   ├── nmea2000_parser.py        # L0: NMEA2000 数据源
│   │   ├── engine_monitor.py         # L0: 机舱监控
│   │   │
│   │   ├── intelligent_navigation.py # L0: 智能导航 (CPA/TCPA + COLREGs)
│   │   ├── intelligent_engine.py     # L0: 智能机舱 (健康监测 + 故障诊断)
│   │   └── energy_efficiency_manager.py # L0: 能效管理 (EEXI/CII/SEEMP)
│   │   │
│   │   ├── compliance_digital_expert.py # L1: 认知数字化 (COLREGs + 规范库)
│   │   ├── distributed_perception_hub.py # L2: 感知网络 (多源融合 + 风险关联)
│   │   └── decision_orchestrator.py # L3: 决策编排 (风险汇总 + 运维建议)
│   │
│   ├── storage/                      # 数据存储模块 (新增)
│   │   ├── event_store.py            # SQLite/JSONL/Parquet 事件存储
│   │   ├── cloud_sync.py             # S3/Feishu/LocalFile 云同步
│   │   └── data_lakehouse.py         # 数据湖仓整合 (SQLite + Cloud)
│   │
│   ├── adapters/                     # 外部系统适配器
│   │   ├── worldmonitor_adapter.py   # WorldMonitor 模拟适配器
│   │   └── worldmonitor_adapter_real.py # WorldMonitor 真实数据适配器
│   │
│   ├── alarm/                        # 告警模块 (预留)
│   │
│   ├── websocket/                    # WebSocket 服务 (预留)
│   │
│   └── phm/                          # PHM (预测性健康维护) (预留)
│
├── frontend/                         # 前端界面代码
│   ├── index.html                    # 主界面入口
│   ├── poseidon-config.html          # Poseidon X 配置页面
│   │
│   └── digital-twin/                 # 数字孪生模块
│       ├── digital-twin.html         # 数字孪生主页面
│       ├── main.js                   # 主入口
│       ├── index.js                  # 索引
│       ├── demo.js                   # 演示代码
│       ├── waves.js                  # 海浪动画
│       │
│       ├── layer1-interface/         # L1: 接口层 (预留)
│       ├── layer2-agents/            # L2: 代理层 (预留)
│       └── layer3-platform/          # L3: 平台层 (预留)
│       │
│       ├── DataAggregator.js         # 数据聚合器
│       ├── MarineEngineeringChannels.js # 海洋工程 Channel
│       ├── MarineEngineeringModule.js # 海洋工程模块
│       ├── NavigationMonitor.js      # 导航监控
│       ├── PoseidonX.js              # Poseidon X 集成
│       ├── PoseidonXChannels.js      # Poseidon X Channel
│       ├── PoseidonXIntegration.js   # Poseidon X 集成
│       └── simple-bridge-chat.js     # 桥梁聊天组件
│
└── simulation/                       # 仿真模块 (预留)
    ├── nmea/                         # NMEA2000 仿真 (空)
    ├── ais/                          # AIS 仿真 (空)
    └── sensor/                       # 传感器仿真 (空)
```

## 新增数据湖仓模块

```
src/backend/storage/
├── event_store.py      # Local Store: SQLite/JSONL/Parquet
├── cloud_sync.py       # Cloud Adapter: S3/Feishu/LocalFile
└── data_lakehouse.py   # Lakehouse Integrator
```

## Layer 映射关系

| Layer | 模块 | 说明 |
|-------|------|------|
| L0 | `intelligent_navigation` | 智能导航 (CPA/TCPA + COLREGs 风险评估) |
| L0 | `intelligent_engine` | 智能机舱 (健康监测 + 故障诊断) |
| L0 | `energy_efficiency_manager` | 能效管理 (EEXI/CII/SEEMP 合规计算) |
| L0 | `nmea2000_parser` | 数据源 (NMEA2000 消息解析) |
| L1 | `compliance_digital_expert` | 认知数字化 (COLREGs 规范库 + 统一认知输出) |
| L2 | `distributed_perception_hub` | 感知网络 (多源融合 + 风险关联) |
| L2 | `data_lakehouse` | 数据湖仓 (SQLite/JSONL + 云同步) |
| L3 | `decision_orchestrator` | 决策编排 (风险汇总 + 运维建议) |

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/ai-native/compliance/status` | GET | 查询合规状态 |
| `/api/v1/ai-native/compliance/cognitive-snapshot` | GET | 获取认知快照 |
| `/api/v1/ai-native/perception/events` | GET | 获取感知事件流 |
| `/api/v1/ai-native/perception/capture-snapshot` | GET | 捕获感知快照 |
| `/api/v1/ai-native/decision/package` | GET | 获取决策包 |
| `/api/v1/ai-native/decision/feedback` | POST | 记录决策反馈 |
| `/api/v1/ai-native/status/full-pipeline` | GET | 完整 AI Native 状态 |

## 运行命令

```bash
# 注册并测试 Channel
python src/backend/register_channels.py

# 测试 P0 模块 (认知/感知/决策)
python test_p0_modules.py

# 测试数据湖仓
python test_data_lakehouse.py

# 运行自动化测试套件
python scripts/run_tests.py
```

## 测试验证

```bash
# 总体测试
python scripts/run_tests.py
# => 13/13 tests passed ✅

# P0 模块测试
python test_p0_modules.py
# => 4/4 tests passed ✅

# 湖仓测试
python test_data_lakehouse.py
# => 2/2 tests passed ✅
```

---

**状态**: AI Native 16 小时重构计划 L0-L3 阶段已完成，数据湖仓模块已实现，无需 Hadoop 部署。