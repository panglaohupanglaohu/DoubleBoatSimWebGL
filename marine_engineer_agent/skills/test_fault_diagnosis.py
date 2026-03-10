#!/usr/bin/env python3
"""
船舶故障诊断技能单元测试
测试 fault_diagnosis.py 中的关键词提取和匹配功能
"""

import unittest
import sys
import os

# 添加父目录到路径以导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fault_diagnosis import _extract_fault_keywords, _match_fault_solutions


class TestFaultKeywordExtraction(unittest.TestCase):
    """测试故障关键词提取功能"""
    
    def test_colon_separator(self):
        """测试冒号分隔符"""
        result = _extract_fault_keywords("柴油机：排气温度过高")
        self.assertIn("柴油机", result)
        self.assertIn("排气温度过高", result)
    
    def test_dash_separator(self):
        """测试破折号分隔符"""
        result = _extract_fault_keywords("柴油机 - 排气温度过高")
        self.assertIn("柴油机", result)
        self.assertIn("排气温度过高", result)
    
    def test_space_separator(self):
        """测试空格分隔符"""
        result = _extract_fault_keywords("柴油机 排气温度过高")
        self.assertIn("柴油机", result)
        self.assertIn("排气温度过高", result)
    
    def test_mixed_separators(self):
        """测试混合分隔符"""
        result = _extract_fault_keywords("柴油机：排气温度 - 过高")
        self.assertIn("柴油机", result)
        self.assertIn("排气温度", result)
        self.assertIn("过高", result)
    
    def test_stop_words_filtered(self):
        """测试停用词过滤"""
        result = _extract_fault_keywords("柴油机的问题是排气温度过高")
        self.assertNotIn("的", result)
        self.assertNotIn("是", result)
        self.assertNotIn("问题", result)
    
    def test_short_words_filtered(self):
        """测试单字符过滤"""
        result = _extract_fault_keywords("柴油机温度高")
        # 单字符应该被过滤
        for keyword in result:
            self.assertGreater(len(keyword), 1)
    
    def test_empty_input(self):
        """测试空输入"""
        result = _extract_fault_keywords("")
        self.assertEqual(result, [])
    
    def test_only_stop_words(self):
        """测试只有停用词"""
        result = _extract_fault_keywords("的是有的")
        self.assertEqual(result, [])


class TestFaultSolutionMatching(unittest.TestCase):
    """测试故障解决方案匹配功能"""
    
    def setUp(self):
        """准备测试数据"""
        self.sample_docs = [
            {
                "content": "柴油机排气温度过高的原因：1. 喷油器故障 2. 进气不足 3. 负荷过大",
                "source": "柴油机故障手册"
            },
            {
                "content": "冷却系统故障可能导致发动机过热，检查水泵和散热器",
                "source": "冷却系统维护指南"
            },
            {
                "content": "润滑油压力低的原因：油泵故障、油位低、滤清器堵塞",
                "source": "润滑系统手册"
            }
        ]
    
    def test_single_keyword_match(self):
        """测试单关键词匹配"""
        keywords = ["柴油机"]
        results = _match_fault_solutions(keywords, self.sample_docs)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["confidence"], "中")
    
    def test_multiple_keyword_match(self):
        """测试多关键词匹配"""
        keywords = ["柴油机", "排气温度"]
        results = _match_fault_solutions(keywords, self.sample_docs)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["confidence"], "高")
        self.assertGreaterEqual(results[0]["match_count"], 2)
    
    def test_no_match(self):
        """测试无匹配情况"""
        keywords = ["雷达", "导航"]
        results = _match_fault_solutions(keywords, self.sample_docs)
        self.assertEqual(len(results), 0)
    
    def test_sorted_by_match_count(self):
        """测试结果按匹配数排序"""
        keywords = ["柴油机", "故障", "系统"]
        results = _match_fault_solutions(keywords, self.sample_docs)
        if len(results) > 1:
            for i in range(len(results) - 1):
                self.assertGreaterEqual(
                    results[i]["match_count"],
                    results[i + 1]["match_count"]
                )
    
    def test_matched_keywords_tracking(self):
        """测试匹配关键词追踪"""
        keywords = ["柴油机", "排气温度"]
        results = _match_fault_solutions(keywords, self.sample_docs)
        if len(results) > 0:
            self.assertIn("matched_keywords", results[0])
            self.assertIsInstance(results[0]["matched_keywords"], list)


class TestConfidenceEvaluation(unittest.TestCase):
    """测试置信度评估逻辑"""
    
    def setUp(self):
        """准备测试数据"""
        self.sample_docs = [
            {"content": "柴油机排气温度过高", "source": "手册 A"},
            {"content": "排气系统维护", "source": "手册 B"}
        ]
    
    def test_high_confidence(self):
        """测试高置信度（匹配数>=2）"""
        keywords = ["柴油机", "排气"]
        results = _match_fault_solutions(keywords, self.sample_docs)
        if len(results) > 0 and results[0]["match_count"] >= 2:
            self.assertEqual(results[0]["confidence"], "高")
    
    def test_medium_confidence(self):
        """测试中置信度（匹配数=1）"""
        keywords = ["柴油机"]
        results = _match_fault_solutions(keywords, self.sample_docs)
        if len(results) > 0 and results[0]["match_count"] == 1:
            self.assertEqual(results[0]["confidence"], "中")


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 船舶故障诊断技能单元测试")
    print("=" * 70)
    
    # 运行测试
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 70)
    print("✅ 测试完成")
    print("=" * 70)
