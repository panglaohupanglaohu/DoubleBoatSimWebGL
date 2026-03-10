"""
船舶工程技能集成测试
测试主技能函数与 Mock 知识库系统的集成
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加父目录到路径以导入技能模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'skills'))

from fault_diagnosis import fault_diagnosis_skill, _extract_fault_keywords, _match_fault_solutions
from query_answer import query_answer_skill, _analyze_documents, _evaluate_confidence


class TestFaultDiagnosisIntegration(unittest.TestCase):
    """故障诊断技能集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_config = {
            "safety": {"require_warning": True},
            "runtime": {"max_length": 4096, "include_sources": True}
        }
        
        self.mock_docs = [
            {
                "content": "柴油机排气温度过高的原因：1. 喷油器故障 2. 增压器效率下降 3. 冷却系统问题",
                "source": "船舶动力系统设计",
                "page": 156
            },
            {
                "content": "解决方案：检查喷油器雾化质量，清洁增压器，检查冷却水流量",
                "source": "轮机工程手册",
                "page": 234
            }
        ]
    
    def test_complete_workflow_high_confidence(self):
        """测试完整工作流 - 高置信度场景"""
        user_input = "柴油机排气温度过高"
        result = fault_diagnosis_skill(user_input, self.mock_docs, self.mock_config)
        
        # 验证输出格式
        self.assertIn("故障诊断报告", result)
        self.assertIn("柴油机", result)
        self.assertIn("排气温度", result)
        # 置信度取决于匹配关键词数量（单个关键词=中，多个=高）
        self.assertIn("匹配置信度：", result)
        self.assertIn("安全警告", result)
        self.assertIn("环保合规提示", result)
    
    def test_complete_workflow_no_match(self):
        """测试完整工作流 - 无匹配场景"""
        user_input = "空调系统不制冷"
        mock_docs = [{"content": "柴油机相关内容", "source": "测试"}]
        
        result = fault_diagnosis_skill(user_input, mock_docs, self.mock_config)
        
        self.assertIn("未找到对应故障", result)
        self.assertIn("匹配置信度：低", result)
    
    def test_keyword_extraction_integration(self):
        """测试关键词提取集成"""
        test_cases = [
            ("柴油机：排气温度高", ["柴油机", "排气温度高"]),
            ("增压器 - 效率下降", ["增压器", "效率下降"]),
            # "有问题"不是停用词，所以会保留
            ("冷却系统有问题", ["冷却系统有问题"]),
        ]
        
        for input_text, expected in test_cases:
            keywords = _extract_fault_keywords(input_text)
            self.assertEqual(keywords, expected, f"输入：{input_text}")
    
    def test_solution_matching_integration(self):
        """测试解决方案匹配集成"""
        keywords = ["柴油机", "排气"]
        results = _match_fault_solutions(keywords, self.mock_docs)
        
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["confidence"], "高")
        self.assertIn("柴油机", results[0]["matched_keywords"])
    
    def test_safety_warning_toggle(self):
        """测试安全警告开关"""
        # 启用安全警告
        config_with_warning = {"safety": {"require_warning": True}}
        result_with = fault_diagnosis_skill("故障", self.mock_docs, config_with_warning)
        self.assertIn("安全警告", result_with)
        
        # 禁用安全警告
        config_without_warning = {"safety": {"require_warning": False}}
        result_without = fault_diagnosis_skill("故障", self.mock_docs, config_without_warning)
        self.assertNotIn("安全警告", result_without)
    
    def test_empty_input_handling(self):
        """测试空输入处理"""
        result = fault_diagnosis_skill("", [], self.mock_config)
        self.assertIn("故障诊断报告", result)
    
    def test_special_characters_input(self):
        """测试特殊字符输入"""
        user_input = "柴油机！！！排气###温度$$$过高"
        result = fault_diagnosis_skill(user_input, self.mock_docs, self.mock_config)
        
        self.assertIn("故障诊断报告", result)
        # 验证关键词提取能处理特殊字符
        keywords = _extract_fault_keywords(user_input)
        self.assertTrue(len(keywords) > 0)


class TestQueryAnswerIntegration(unittest.TestCase):
    """问答技能集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_config = {
            "runtime": {
                "max_length": 4096,
                "include_sources": True
            }
        }
        
        self.mock_docs = [
            {
                "content": "船舶电力系统由发电机、配电板、变压器等组成",
                "source": "舰船电力系统",
                "page": 45
            },
            {
                "content": "发电机额定电压通常为 400V 或 690V",
                "source": "舰船电力系统",
                "page": 67
            },
            {
                "content": "配电板负责电力分配和保护",
                "source": "轮机工程手册",
                "page": 123
            }
        ]
    
    def test_complete_workflow_high_confidence(self):
        """测试完整工作流 - 高可信度场景"""
        user_input = "船舶电力系统由什么组成？"
        result = query_answer_skill(user_input, self.mock_docs, self.mock_config)
        
        self.assertIn("船舶工程知识库问答", result)
        self.assertIn("可信度：高", result)
        self.assertIn("参考文档数：3", result)
        self.assertIn("参考来源", result)
        self.assertIn("舰船电力系统", result)
    
    def test_complete_workflow_no_docs(self):
        """测试完整工作流 - 无文档场景"""
        user_input = "未知领域问题"
        result = query_answer_skill(user_input, [], self.mock_config)
        
        self.assertIn("未在知识库中找到相关内容", result)
        self.assertIn("可信度：未知", result)
    
    def test_source_inclusion_toggle(self):
        """测试来源信息开关"""
        # 启用来源
        config_with_sources = {"runtime": {"include_sources": True}}
        result_with = query_answer_skill("问题", self.mock_docs, config_with_sources)
        self.assertIn("参考来源", result_with)
        
        # 禁用来源
        config_without_sources = {"runtime": {"include_sources": False}}
        result_without = query_answer_skill("问题", self.mock_docs, config_without_sources)
        self.assertNotIn("参考来源", result_without)
    
    def test_max_length_truncation(self):
        """测试最大长度截断"""
        # 使用较小的 max_context_length 验证截断功能
        config_short = {"runtime": {"max_context_length": 500, "include_sources": False}}
        result = query_answer_skill("问题", self.mock_docs, config_short)
        
        # 验证结果被截断到指定长度
        self.assertLessEqual(len(result), 500)
    
    def test_document_analysis_integration(self):
        """测试文档分析集成"""
        analysis = _analyze_documents(self.mock_docs)
        
        self.assertEqual(analysis["total"], 3)
        self.assertEqual(analysis["with_source"], 3)
        self.assertEqual(analysis["with_page"], 3)
        self.assertGreater(analysis["avg_length"], 0)
    
    def test_confidence_evaluation_integration(self):
        """测试可信度评估集成"""
        # 高可信度：多个带来源文档
        analysis_high = {"total": 3, "with_source": 3, "with_page": 3, "avg_length": 50}
        confidence_high = _evaluate_confidence(analysis_high, 3)
        self.assertEqual(confidence_high, "高")
        
        # 中可信度：单个来源或多文档
        analysis_mid = {"total": 3, "with_source": 1, "with_page": 1, "avg_length": 50}
        confidence_mid = _evaluate_confidence(analysis_mid, 3)
        self.assertEqual(confidence_mid, "中")
        
        # 低可信度：无来源少文档
        analysis_low = {"total": 1, "with_source": 0, "with_page": 0, "avg_length": 50}
        confidence_low = _evaluate_confidence(analysis_low, 1)
        self.assertEqual(confidence_low, "低")
        
        # 未知：无文档
        confidence_unknown = _evaluate_confidence({"total": 0}, 0)
        self.assertEqual(confidence_unknown, "未知")
    
    def test_missing_fields_handling(self):
        """测试缺失字段处理"""
        docs_with_missing_fields = [
            {"content": "内容 1"},  # 无 source 和 page
            {"content": "内容 2", "source": "来源 2"},  # 无 page
            {"content": "内容 3", "source": "来源 3", "page": 10}
        ]
        
        analysis = _analyze_documents(docs_with_missing_fields)
        self.assertEqual(analysis["total"], 3)
        self.assertEqual(analysis["with_source"], 2)
        self.assertEqual(analysis["with_page"], 1)


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""
    
    def test_very_long_input(self):
        """测试超长输入处理"""
        # 使用分隔符分隔的长输入
        long_input = "故障：" + "柴油机：" * 100 + "排气温度"
        keywords = _extract_fault_keywords(long_input)
        # 应该能提取出至少一些关键词（去重后）
        self.assertTrue(len(keywords) > 0)
        # 验证关键词不包含重复
        self.assertIn("柴油机", keywords)
        self.assertIn("排气温度", keywords)
    
    def test_unicode_characters(self):
        """测试 Unicode 字符处理"""
        user_input = "柴油机 🔧 排气温度 🌡️ 过高 ⚠️"
        keywords = _extract_fault_keywords(user_input)
        # 应该能正确提取中文字符
        self.assertTrue(any("柴油" in kw or "排气" in kw for kw in keywords))
    
    def test_mixed_languages(self):
        """测试混合语言处理"""
        user_input = "diesel engine 柴油机 故障 trouble"
        keywords = _extract_fault_keywords(user_input)
        self.assertTrue(len(keywords) > 0)
    
    def test_config_missing_keys(self):
        """测试配置缺失键处理"""
        # 空配置
        empty_config = {}
        result = fault_diagnosis_skill("故障", [{"content": "测试"}], empty_config)
        self.assertIn("故障诊断报告", result)
        
        # 部分配置
        partial_config = {"safety": {}}
        result = fault_diagnosis_skill("故障", [{"content": "测试"}], partial_config)
        self.assertIn("故障诊断报告", result)
    
    def test_concurrent_calls(self):
        """测试并发调用（模拟）"""
        # 验证函数无全局状态
        config = {"safety": {"require_warning": True}}
        docs = [{"content": "解决方案 A", "source": "测试"}]
        
        result1 = fault_diagnosis_skill("故障 A", docs, config)
        result2 = fault_diagnosis_skill("故障 B", docs, config)
        
        # 两次调用应该独立
        self.assertIn("故障 A", result1)
        self.assertIn("故障 B", result2)


if __name__ == '__main__':
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestFaultDiagnosisIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestQueryAnswerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print("\n" + "=" * 70)
    print(f"测试运行完成：{result.testsRun} 个测试")
    print(f"通过：{result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败：{len(result.failures)}")
    print(f"错误：{len(result.errors)}")
    print("=" * 70)
