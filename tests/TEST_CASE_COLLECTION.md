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
  - 覆盖 DataLakehouse 存储状态、事件写入和查询
- `tests/unit/test_storage_modules.py`
  - 覆盖 JSONLStore 和 SQLiteStore
- `tests/unit/test_p0_modules.py`
  - 覆盖 P0 核心通道和最小全链路构建
- `tests/unit/test_ai_native_channels.py`
  - 覆盖 AI Native 核心通道的注册、初始化和事件行为
- `tests/unit/test_backend.py`
  - 覆盖后端基础行为
- `tests/unit/test_energy_efficiency_channel.py`
  - 覆盖能效通道逻辑
- `tests/unit/test_feature_fusion_layer.py`
  - 覆盖特征融合层
- `tests/unit/test_intelligent_engine_channel.py`
  - 覆盖智能机舱通道

## 当前 Integration Test 集合

- `tests/integration/test_ai_native_endpoints.py`
  - 覆盖 AI Native 关键 endpoint 定义与核心通道联动
- `tests/integration/test_ai_native_api.py`
  - 覆盖 AI Native API 层
- `tests/integration/test_poseidon_x_integration.py`
  - 覆盖 Poseidon-X 集成链路
- `tests/integration/test_api.py`
  - 覆盖基础 API 集成
- `tests/integration/test_worldmonitor_placeholder_api.py`
  - 覆盖 WorldMonitor placeholder API

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