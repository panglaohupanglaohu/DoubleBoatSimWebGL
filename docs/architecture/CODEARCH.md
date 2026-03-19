# AI Native 代码架构 - 命令行参考手册

## 快速验证命令

### 1. Channel 注册测试
```bash
cd /Users/panglaohu/Downloads/DoubleBoatClawSystem
source venv/bin/activate
python src/backend/register_channels.py
```

### 2. P0 通道测试 (认知专家/感知网络/决策编排)
```bash
python test_p0_modules.py
```

### 3. 湖仓存储测试
```bash
python test_data_lakehouse.py
```

### 4. API 扩展测试
```bash
python test_api_extensions.py
```

### 5. 自动化测试套件
```bash
python scripts/run_tests.py
```

---

## 核心模块调用示例

### ComplianceDigitalExpert
```python
from src.backend.channels.compliance_digital_expert import ComplianceDigitalExpertChannel

comp = ComplianceDigitalExpertChannel()
comp.initialize()

# 查询合规状态
result = comp.query_compliance_status("navigation")

# 获取认知快照
snapshot = comp.build_cognitive_snapshot()

# 生成维护报告
report = comp.generate_maintenance_report()
```

### DistributedPerceptionHub
```python
from src.backend.channels.distributed_perception_hub import DistributedPerceptionHubChannel

hub = DistributedPerceptionHubChannel()
hub.initialize()

# 捕获系统快照
events = hub.capture_system_snapshot()

# 获取最新事件
latest = hub.get_latest_events(5)
```

### DataLakehouse
```python
from src.backend.storage.data_lakehouse import create_lakehouse

lakehouse = create_lakehouse({
    "store_type": "sqlite",
    "store_config": {"db_path": "./storage/events.db"}
})

# 保存事件
lakehouse.save_event({"event_type": "nav_event", "payload": {...}})

# 查询事件
events = lakehouse.query_events("nav_event", limit=10)

# 获取状态
status = lakehouse.get_status()
```

### DecisionOrchestrator
```python
from src.backend.channels.decision_orchestrator import DecisionOrchestratorChannel

orchestrator = DecisionOrchestratorChannel()
orchestrator.initialize()

# 构建决策包
package = orchestrator.build_decision_package()

# 记录反馈
feedback = orchestrator.record_feedback("action_1", "success", "user")
```

---

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

---

## 架构分层总结

| Layer | 模块 | 职责 |
|-------|------|------|
| L0 | `intelligent_navigation`, `intelligent_engine`, `energy_efficiency_manager` | 执行节点与数据源 |
| L1 | `compliance_digital_expert` | 认知数字化 (COLREGs法规 + 规范库) |
| L2 | `distributed_perception_hub`, `data_lakehouse` | 感知增强 + 数据湖仓治理 |
| L3 | `decision_orchestrator` | 全闭环预测性维护与决策 |

---

## 扩展开发指南

### 新增感知融合规则
1. 在 `distributed_perception_hub.py` 添加新融合方法
2. 在 `RISK_CORRELATIONS` 中添加风险关联
3. 在 `capture_system_snapshot` 中注册调用

### 新增存储后端
1. 继承 `EventStore` 或 `CloudStorageAdapter`
2. 实现抽象方法
3. 在 `get_store()` 或 `get_adapter()` 中注册

### 新增 API 端点
1. 在 `api_extensions.py` 添加路由函数
2. 在 `main.py` 中注册 FastAPI 路由
3. 添加前端页面组件

---

## 性能验证命令

```bash
# 总体测试
python scripts/run_tests.py

# 单元测试
python test_p0_modules.py
python test_data_lakehouse.py

# API 测试
python test_api_extensions.py
```

测试输出示例：
```
=== All Tests Passed ===
总计：13 个测试
通过：13 ✅
失败：0 ❌
通过率：100.0%
```