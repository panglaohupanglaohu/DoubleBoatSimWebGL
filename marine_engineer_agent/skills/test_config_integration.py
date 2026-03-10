"""
配置集成测试模块

测试 fault_diagnosis 和 query_answer 技能与 MarineEngineerConfig 的集成。
验证向后兼容性和配置对象传递。

:author: marine_engineer_agent
:version: 1.0.0
:since: 2026-03-10
"""

import unittest
from typing import List, Dict, Any

from marine_config import MarineEngineerConfig
from fault_diagnosis import fault_diagnosis_skill
from query_answer import query_answer_skill


class TestConfigIntegration(unittest.TestCase):
    """测试配置类集成"""
    
    def setUp(self):
        """准备测试数据"""
        self.test_docs: List[Dict[str, Any]] = [
            {
                "content": "柴油机排气温度过高的原因：1. 燃油喷射系统故障 2. 冷却系统问题 3. 涡轮增压器故障",
                "source": "柴油机维护手册",
                "page": 42
            },
            {
                "content": "解决方案：检查燃油喷射正时，清理冷却系统，检查涡轮增压器叶片",
                "source": "故障诊断指南",
                "page": 15
            }
        ]
    
    def test_fault_diagnosis_with_config_object(self):
        """测试故障诊断使用配置对象"""
        config = MarineEngineerConfig()
        result = fault_diagnosis_skill("柴油机排气温度过高", self.test_docs, config)
        
        self.assertIn("故障诊断报告", result)
        self.assertIn("柴油机", result)
        self.assertIn("安全警告", result)  # 默认 require_warning=True
    
    def test_fault_diagnosis_with_dict_config(self):
        """测试故障诊断使用字典配置（向后兼容）"""
        config_dict = {
            "safety": {"require_warning": True},
            "runtime": {"max_context_length": 4096}
        }
        result = fault_diagnosis_skill("柴油机排气温度过高", self.test_docs, config_dict)
        
        self.assertIn("故障诊断报告", result)
        self.assertIn("安全警告", result)
    
    def test_fault_diagnosis_with_none_config(self):
        """测试故障诊断使用 None 配置（使用默认值）"""
        result = fault_diagnosis_skill("柴油机排气温度过高", self.test_docs, None)
        
        self.assertIn("故障诊断报告", result)
        self.assertIn("安全警告", result)
    
    def test_fault_diagnosis_disable_warning(self):
        """测试禁用安全警告"""
        config = MarineEngineerConfig()
        config.safety.require_warning = False
        
        result = fault_diagnosis_skill("柴油机排气温度过高", self.test_docs, config)
        
        self.assertIn("故障诊断报告", result)
        self.assertNotIn("安全警告", result)
    
    def test_query_answer_with_config_object(self):
        """测试问答使用配置对象"""
        config = MarineEngineerConfig()
        result = query_answer_skill("柴油机工作原理", self.test_docs, config)
        
        self.assertIn("知识库问答", result)
        self.assertIn("参考来源", result)  # 默认 include_sources=True
    
    def test_query_answer_with_dict_config(self):
        """测试问答使用字典配置（向后兼容）"""
        config_dict = {
            "runtime": {
                "max_context_length": 4096,
                "include_sources": True
            }
        }
        result = query_answer_skill("柴油机工作原理", self.test_docs, config_dict)
        
        self.assertIn("知识库问答", result)
        self.assertIn("参考来源", result)
    
    def test_query_answer_with_none_config(self):
        """测试问答使用 None 配置（使用默认值）"""
        result = query_answer_skill("柴油机工作原理", self.test_docs, None)
        
        self.assertIn("知识库问答", result)
        self.assertIn("参考来源", result)
    
    def test_query_answer_disable_sources(self):
        """测试禁用来源信息"""
        config = MarineEngineerConfig()
        config.runtime.include_sources = False
        
        result = query_answer_skill("柴油机工作原理", self.test_docs, config)
        
        self.assertIn("知识库问答", result)
        self.assertNotIn("参考来源", result)
    
    def test_query_answer_max_length(self):
        """测试最大长度限制"""
        config = MarineEngineerConfig()
        config.runtime.max_context_length = 100
        
        result = query_answer_skill("柴油机工作原理", self.test_docs, config)
        
        self.assertLessEqual(len(result), 100)
    
    def test_config_validation_integration(self):
        """测试配置验证集成"""
        # 创建无效配置
        invalid_dict = {
            "runtime": {
                "max_context_length": 50  # 太小，应该 >= 100
            }
        }
        
        # 应该抛出异常
        with self.assertRaises(ValueError):
            MarineEngineerConfig.from_dict(invalid_dict)
    
    def test_full_workflow_with_custom_config(self):
        """测试完整工作流使用自定义配置"""
        config = MarineEngineerConfig()
        config.safety.require_warning = True
        config.safety.require_ppe = True
        config.runtime.max_context_length = 8192
        config.runtime.include_sources = True
        
        # 故障诊断
        diagnosis = fault_diagnosis_skill("柴油机排气温度过高", self.test_docs, config)
        self.assertIn("故障诊断报告", diagnosis)
        
        # 问答
        answer = query_answer_skill("柴油机工作原理", self.test_docs, config)
        self.assertIn("知识库问答", answer)


class TestBackwardCompatibility(unittest.TestCase):
    """测试向后兼容性"""
    
    def test_old_dict_format_still_works(self):
        """测试旧的字典格式仍然有效"""
        # 旧格式配置
        old_config = {
            "safety": {
                "require_warning": True
            },
            "runtime": {
                "max_context_length": 4096,
                "include_sources": True
            }
        }
        
        docs = [{"content": "测试内容", "source": "测试"}]
        
        # 应该正常工作
        result1 = fault_diagnosis_skill("测试故障", docs, old_config)
        result2 = query_answer_skill("测试问题", docs, old_config)
        
        self.assertIn("故障诊断报告", result1)
        self.assertIn("知识库问答", result2)
    
    def test_partial_dict_config(self):
        """测试部分字典配置（使用默认值）"""
        partial_config = {
            "safety": {"require_warning": False}
            # runtime 使用默认值
        }
        
        docs = [{"content": "测试内容"}]
        
        result = fault_diagnosis_skill("测试故障", docs, partial_config)
        
        # 不应包含安全警告
        self.assertNotIn("安全警告", result)


if __name__ == "__main__":
    unittest.main()
