# 读书笔记 #3

**书名：** Python 集成测试与 Mock 技术 + 代码质量提升
**阅读时间：** 2026-03-10 00:30
**来源：** 软件工程知识整理 + Tavily 搜索（待 API 配置）

---

## 核心知识点

### 1. 集成测试最佳实践

**Mock 技术核心原则：**
- **隔离外部依赖**：使用 Mock 模拟知识库检索、数据库、API 调用
- **控制测试环境**：确保测试结果可重复，不受外部系统影响
- **验证交互行为**：不仅验证输出，还要验证调用顺序和参数

**Mock 对象使用场景：**
```python
# 模拟知识库检索系统
mock_knowledge_base = Mock()
mock_knowledge_base.search.return_value = [
    {"content": "故障解决方案...", "source": "测试文档", "page": 1}
]

# 验证调用
mock_knowledge_base.search.assert_called_once_with("柴油机")
```

### 2. 类型注解（Type Hints）

**Python 类型系统优势：**
- 提高代码可读性和自文档化
- IDE 自动补全和错误检测
- 静态类型检查工具（mypy）支持
- 减少运行时类型错误

**常用类型注解：**
```python
from typing import List, Dict, Optional, Union

def process_data(items: List[str], 
                 config: Optional[Dict[str, any]] = None) -> Dict[str, int]:
    ...
```

### 3. 配置管理最佳实践

**配置验证模式：**
```python
class Config:
    def __init__(self, config_dict: dict):
        self.max_length = config_dict.get("max_length", 4096)
        self.require_warning = config_dict.get("require_warning", True)
        self._validate()
    
    def _validate(self):
        if self.max_length < 100:
            raise ValueError("max_length 必须 >= 100")
```

**配置分层设计：**
- **安全配置**：安全警告、合规要求
- **运行时配置**：最大长度、日志级别
- **功能配置**：启用/禁用特定功能

### 4. 日志优化

**结构化日志：**
```python
import logging
import json

logger = logging.getLogger(__name__)

# JSON 格式日志（便于机器解析）
logger.info(json.dumps({
    "event": "fault_diagnosis",
    "keywords": ["柴油机", "排气"],
    "confidence": "高",
    "timestamp": "2026-03-10T00:30:00Z"
}))
```

**日志级别使用规范：**
- `DEBUG`：详细调试信息（开发环境）
- `INFO`：正常业务流程
- `WARNING`：潜在问题，但系统继续运行
- `ERROR`：错误发生，功能受影响
- `CRITICAL`：严重错误，系统可能崩溃

---

## 可应用到项目的技术

### 1. unittest.mock 框架
- `Mock` 类：创建模拟对象
- `patch` 装饰器：临时替换真实对象
- `assert_called_with`：验证调用参数
- `side_effect`：模拟异常或多次返回值

### 2. typing 模块
- `List`, `Dict`, `Tuple`：容器类型
- `Optional`：可为 None 的类型
- `Union`：联合类型
- `Callable`：函数类型

### 3. 配置验证库
- `pydantic`：数据验证和设置管理
- `attrs`：类属性定义
- 或使用标准库实现轻量级验证

### 4. 日志格式化
- `logging.Formatter`：自定义日志格式
- `JsonFormatter`：JSON 格式日志
- 日志轮转：`RotatingFileHandler`

---

## 代码优化建议

### 1. 添加类型注解
```python
# 优化前
def _extract_fault_keywords(user_input: str) -> list:

# 优化后
from typing import List

def _extract_fault_keywords(user_input: str) -> List[str]:
```

### 2. 集成测试开发
```python
class TestFaultDiagnosisIntegration(unittest.TestCase):
    def setUp(self):
        self.mock_config = {
            "safety": {"require_warning": True},
            "runtime": {"max_length": 4096}
        }
    
    def test_complete_workflow(self):
        # Mock 知识库
        mock_docs = [{"content": "解决方案...", "source": "测试"}]
        result = fault_diagnosis_skill("柴油机故障", mock_docs, self.mock_config)
        self.assertIn("故障诊断报告", result)
```

### 3. 配置类封装
```python
class MarineEngineerConfig:
    def __init__(self, config: dict):
        self.safety = config.get("safety", {})
        self.runtime = config.get("runtime", {})
        self._validate()
    
    def _validate(self):
        # 验证配置有效性
        pass
```

### 4. 错误处理增强
```python
try:
    result = fault_diagnosis_skill(user_input, docs, config)
except KeyError as e:
    logger.error(f"配置缺失：{e}")
    return "系统配置错误，请联系管理员"
except Exception as e:
    logger.exception(f"诊断失败：{e}")
    return "诊断失败，请稍后重试"
```

---

## 本轮实施计划

### 1. 类型注解添加
- [ ] fault_diagnosis.py：添加完整类型注解
- [ ] query_answer.py：添加完整类型注解
- [ ] 测试文件：添加类型注解

### 2. 集成测试开发
- [ ] test_integration.py：Mock 知识库系统
- [ ] 测试主技能函数完整工作流
- [ ] 验证配置传递和错误处理

### 3. 配置模块优化
- [ ] 创建 Config 类封装配置验证
- [ ] 添加配置默认值和边界检查
- [ ] 优化配置获取逻辑

### 4. 日志改进
- [ ] 统一日志格式
- [ ] 添加结构化日志支持
- [ ] 优化日志级别使用

---

## 下一步计划

### Tavily 搜索（待 API 配置）
- 《船舶动力系统设计》
- 《marine engineering handbook》
- 《Predictive Maintenance for Marine Systems》

### 代码质量目标
- 类型注解覆盖率：100%
- 测试覆盖率：>85%
- 配置验证：完整实现
- 日志质量：结构化 + 可追踪

---

**marine_engineer_agent**
2026-03-10 00:30
第 3 轮阅读完成 ✅
