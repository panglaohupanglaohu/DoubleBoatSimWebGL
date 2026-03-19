# Test Case Collection

本文件定义当前仓库的测试集合结构，也是后续新增测试时的归档入口。

## 目录规则

- `tests/unit`：单元测试，验证单个模块或单条能力链路
- `tests/integration`：集成测试，验证多模块协同和关键业务回归
- `tests/manual`：手工验证脚本，不参与默认 pytest 收集

## 当前 Unit Test 集合

- `tests/unit/test_cps_mission_brief.py`
  - 覆盖 scene-aware COLREGs、task graph、learning state、fusion state、RCS/SHM、OpenBridge 命令解析
- `tests/unit/test_data_lakehouse.py`
  - 覆盖 DataLakehouse 存储状态、事件写入和查询（SQLite WAL、Parquet 归档、DuckDB 即席分析、S3/MinIO 云同步）
- `tests/unit/test_storage_modules.py`
  - 覆盖 JSONLStore 和 SQLiteStore
- `tests/unit/test_p0_modules.py`
  - 覆盖 P0 核心通道和最小全链路构建
- `tests/unit/test_ai_native_channels.py`
  - 覆盖 AI Native 核心通道的注册、初始化和事件行为
- `tests/unit/test_backend.py`
  - 覆盖后端基础行为
- `tests/unit/test_calculators.py`
  - 覆盖 EEXI/CII/SEEMP 计算器：EEXICalculator、CIICalculator、SEEMPManager，以及不同船型和燃料类型的计算结果验证
- `tests/unit/test_energy_efficiency_channel.py`
  - 覆盖能效通道逻辑
- `tests/unit/test_feature_fusion_layer.py`
  - 覆盖特征融合层
- `tests/unit/test_compliance_efficiency.py`
  - 覆盖 ComplianceReporter（IMO DCS/EU MRV 报告生成、年度合规报告、JSON 导出、年份过滤、空航次边界）和 EfficiencyAdvisor（引擎工况分析、CII/EEXI 评级建议、行动计划预算控制）
- `tests/unit/test_intelligent_engine_channel.py`
  - 覆盖智能机舱通道
- `tests/unit/test_messagebus_config_engine.py`
  - 覆盖 MarineMessageBus（消息注册、路由、安全告警）、ConfigLoader、EngineMonitorChannel（告警等级、健康评分）、MaritimeSceneModel（场景语义）
- `tests/unit/test_rcs_shm_openbridge.py`
  - 覆盖 RCSControlChannel（控制量范围、字段完整性、生命周期）、StructuralHealthMonitorChannel（疲劳指数、寿命余度、应变热点）、OpenBridge 命令路由（全域意图分类、边界输入、结果结构）

## 当前 Integration Test 集合

- `tests/integration/test_ai_native_endpoints.py`
  - 覆盖 AI Native 关键 endpoint 定义与核心通道联动
- `tests/integration/test_ai_native_api.py`
  - 覆盖 AI Native API 层：Dashboard 结构、Channel 查询、RCS/SHM 状态端点、CPS Mission Brief、Memory 事件/回放/分析状态、Fusion State、OpenBridge 命令（任务图/RCS/SHM）、Decision Feedback Log、Compliance/Perception/Decision 扩展端点、Full Pipeline Status
- `tests/integration/test_nmea2000_engine_flow.py`
  - 覆盖 NMEA2000 解析器 → 智能机舱数据流的端到端管道
- `tests/integration/test_poseidon_x_integration.py`
  - 覆盖 Poseidon-X 集成链路（Channel API、Sensors API、Root API、性能、端到端启动）
- `tests/integration/test_api.py`
  - 覆盖基础 API 集成（默认排除于 CI 回归，避免环境依赖问题）
- `tests/integration/test_worldmonitor_placeholder_api.py`
  - 覆盖 WorldMonitor placeholder API（AIS、天气、港口、航线）

## 当前 Manual Test 集合

- `tests/manual/manual_api_extensions.py`
- `tests/manual/manual_full_pipeline.py`
- `tests/manual/manual_pipeline_direct.py`
- `tests/manual/manual_channel_registration.py`

这些脚本用于手工检查、打印型验证或临时联调，不应作为默认 CI 回归集合的一部分。

## 默认回归命令

最小交付验收：

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/unit/test_cps_mission_brief.py tests/integration/test_ai_native_endpoints.py
```

默认 pytest 收集：

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests
```