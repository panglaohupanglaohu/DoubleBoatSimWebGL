"""
船舶工程智能体配置模块测试

测试 marine_config.py 中的配置类：
- SafetyConfig
- RuntimeConfig
- MarineEngineerConfig
- get_config() 工厂函数

:author: marine_engineer_agent
:version: 1.0.0
:since: 2026-03-10
"""

import unittest
from typing import Dict, Any

# 导入被测试模块
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from marine_config import (
    SafetyConfig,
    RuntimeConfig,
    MarineEngineerConfig,
    get_config
)


class TestSafetyConfig(unittest.TestCase):
    """测试 SafetyConfig 数据类"""
    
    def test_default_values(self) -> None:
        """测试默认值"""
        config = SafetyConfig()
        self.assertTrue(config.require_warning)
        self.assertTrue(config.require_ppe)
        self.assertTrue(config.require_loto)
    
    def test_from_dict(self) -> None:
        """测试从字典创建"""
        config_dict: Dict[str, Any] = {
            "require_warning": False,
            "require_ppe": True,
            "require_loto": False
        }
        config = SafetyConfig.from_dict(config_dict)
        self.assertFalse(config.require_warning)
        self.assertTrue(config.require_ppe)
        self.assertFalse(config.require_loto)
    
    def test_from_dict_partial(self) -> None:
        """测试从部分字典创建（使用默认值）"""
        config_dict: Dict[str, Any] = {
            "require_warning": False
        }
        config = SafetyConfig.from_dict(config_dict)
        self.assertFalse(config.require_warning)
        self.assertTrue(config.require_ppe)  # 默认值
        self.assertTrue(config.require_loto)  # 默认值
    
    def test_validate_success(self) -> None:
        """测试验证成功"""
        config = SafetyConfig()
        # 不应抛出异常
        config.validate()
    
    def test_validate_invalid_type(self) -> None:
        """测试验证失败（类型错误）"""
        config = SafetyConfig(require_warning="invalid")  # type: ignore
        with self.assertRaises(ValueError):
            config.validate()


class TestRuntimeConfig(unittest.TestCase):
    """测试 RuntimeConfig 数据类"""
    
    def test_default_values(self) -> None:
        """测试默认值"""
        config = RuntimeConfig()
        self.assertEqual(config.max_context_length, 4096)
        self.assertTrue(config.include_sources)
        self.assertEqual(config.log_level, "INFO")
    
    def test_from_dict(self) -> None:
        """测试从字典创建"""
        config_dict: Dict[str, Any] = {
            "max_context_length": 8192,
            "include_sources": False,
            "log_level": "DEBUG"
        }
        config = RuntimeConfig.from_dict(config_dict)
        self.assertEqual(config.max_context_length, 8192)
        self.assertFalse(config.include_sources)
        self.assertEqual(config.log_level, "DEBUG")
    
    def test_validate_success(self) -> None:
        """测试验证成功"""
        config = RuntimeConfig()
        config.validate()
    
    def test_validate_max_length_too_small(self) -> None:
        """测试验证失败（max_context_length 太小）"""
        config = RuntimeConfig(max_context_length=50)
        with self.assertRaises(ValueError):
            config.validate()
    
    def test_validate_max_length_too_large(self) -> None:
        """测试验证失败（max_context_length 太大）"""
        config = RuntimeConfig(max_context_length=200000)
        with self.assertRaises(ValueError):
            config.validate()
    
    def test_validate_invalid_log_level(self) -> None:
        """测试验证失败（无效日志级别）"""
        config = RuntimeConfig(log_level="INVALID")
        with self.assertRaises(ValueError):
            config.validate()


class TestMarineEngineerConfig(unittest.TestCase):
    """测试 MarineEngineerConfig 主配置类"""
    
    def test_default_config(self) -> None:
        """测试默认配置"""
        config = MarineEngineerConfig.default()
        self.assertIsInstance(config.safety, SafetyConfig)
        self.assertIsInstance(config.runtime, RuntimeConfig)
        self.assertEqual(config.features, {})
    
    def test_from_dict_full(self) -> None:
        """测试从完整字典创建"""
        config_dict: Dict[str, Any] = {
            "safety": {
                "require_warning": True,
                "require_ppe": False,
                "require_loto": True
            },
            "runtime": {
                "max_context_length": 8192,
                "include_sources": True,
                "log_level": "WARNING"
            },
            "features": {
                "enable_logging": True,
                "enable_debug": False
            }
        }
        config = MarineEngineerConfig.from_dict(config_dict)
        
        self.assertTrue(config.safety.require_warning)
        self.assertFalse(config.safety.require_ppe)
        self.assertTrue(config.safety.require_loto)
        
        self.assertEqual(config.runtime.max_context_length, 8192)
        self.assertTrue(config.runtime.include_sources)
        self.assertEqual(config.runtime.log_level, "WARNING")
        
        self.assertTrue(config.features["enable_logging"])
        self.assertFalse(config.features["enable_debug"])
    
    def test_from_dict_empty(self) -> None:
        """测试从空字典创建（全部使用默认值）"""
        config = MarineEngineerConfig.from_dict({})
        self.assertTrue(config.safety.require_warning)
        self.assertEqual(config.runtime.max_context_length, 4096)
        self.assertEqual(config.features, {})
    
    def test_to_dict(self) -> None:
        """测试导出为字典"""
        config = MarineEngineerConfig(
            safety=SafetyConfig(require_warning=False),
            runtime=RuntimeConfig(max_context_length=2048),
            features={"test_feature": True}
        )
        
        config_dict = config.to_dict()
        
        self.assertFalse(config_dict["safety"]["require_warning"])
        self.assertEqual(config_dict["runtime"]["max_context_length"], 2048)
        self.assertTrue(config_dict["features"]["test_feature"])
    
    def test_validate_success(self) -> None:
        """测试验证成功"""
        config = MarineEngineerConfig.default()
        config.validate()
    
    def test_validate_invalid_feature(self) -> None:
        """测试验证失败（功能开关类型错误）"""
        config = MarineEngineerConfig(
            features={"invalid_feature": "not_a_bool"}  # type: ignore
        )
        with self.assertRaises(ValueError):
            config.validate()


class TestGetConfig(unittest.TestCase):
    """测试 get_config() 工厂函数"""
    
    def test_get_config_none(self) -> None:
        """测试获取默认配置（None 输入）"""
        config = get_config(None)
        self.assertIsInstance(config, MarineEngineerConfig)
        self.assertTrue(config.safety.require_warning)
    
    def test_get_config_dict(self) -> None:
        """测试获取自定义配置"""
        config_dict: Dict[str, Any] = {
            "runtime": {"max_context_length": 16384}
        }
        config = get_config(config_dict)
        self.assertEqual(config.runtime.max_context_length, 16384)
    
    def test_get_config_default(self) -> None:
        """测试获取默认配置（无参数）"""
        config = get_config()
        self.assertIsInstance(config, MarineEngineerConfig)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_config_round_trip(self) -> None:
        """测试配置序列化/反序列化"""
        original = MarineEngineerConfig(
            safety=SafetyConfig(require_warning=False, require_ppe=True),
            runtime=RuntimeConfig(max_context_length=8192, log_level="DEBUG"),
            features={"feature_a": True, "feature_b": False}
        )
        
        # 导出为字典
        config_dict = original.to_dict()
        
        # 从字典重新创建
        restored = MarineEngineerConfig.from_dict(config_dict)
        
        # 验证值相同
        self.assertEqual(
            original.safety.require_warning,
            restored.safety.require_warning
        )
        self.assertEqual(
            original.safety.require_ppe,
            restored.safety.require_ppe
        )
        self.assertEqual(
            original.runtime.max_context_length,
            restored.runtime.max_context_length
        )
        self.assertEqual(
            original.runtime.log_level,
            restored.runtime.log_level
        )
        self.assertEqual(original.features, restored.features)


if __name__ == "__main__":
    unittest.main()
