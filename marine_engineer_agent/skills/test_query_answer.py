#!/usr/bin/env python3
"""
船舶工程问答技能单元测试
测试 query_answer.py 中的文档分析和可信度评估功能
"""

import unittest
import sys
import os

# 添加父目录到路径以导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from query_answer import _analyze_documents, _evaluate_confidence


class TestDocumentAnalysis(unittest.TestCase):
    """测试文档分析功能"""
    
    def test_empty_documents(self):
        """测试空文档列表"""
        result = _analyze_documents([])
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["with_source"], 0)
        self.assertEqual(result["with_page"], 0)
        self.assertEqual(result["avg_length"], 0)
    
    def test_documents_with_sources(self):
        """测试带来源的文档"""
        docs = [
            {"content": "内容 1", "source": "来源 A", "page": 10},
            {"content": "内容 2", "source": "来源 B", "page": 20},
            {"content": "内容 3", "source": "来源 C"}
        ]
        result = _analyze_documents(docs)
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["with_source"], 3)
        self.assertEqual(result["with_page"], 2)
    
    def test_average_length_calculation(self):
        """测试平均长度计算"""
        docs = [
            {"content": "12345"},  # 5 字符
            {"content": "1234567890"}  # 10 字符
        ]
        result = _analyze_documents(docs)
        self.assertEqual(result["avg_length"], 7.5)
    
    def test_missing_fields(self):
        """测试缺失字段处理"""
        docs = [
            {"content": "内容 1"},
            {"content": "内容 2", "source": "来源 B"},
            {"content": "内容 3", "page": 30}
        ]
        result = _analyze_documents(docs)
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["with_source"], 1)
        self.assertEqual(result["with_page"], 1)


class TestConfidenceEvaluation(unittest.TestCase):
    """测试可信度评估功能"""
    
    def test_no_documents(self):
        """测试无文档情况"""
        doc_analysis = {"total": 0, "with_source": 0, "with_page": 0, "avg_length": 0}
        result = _evaluate_confidence(doc_analysis, 0)
        self.assertEqual(result, "未知")
    
    def test_high_confidence(self):
        """测试高可信度（>=2 个带来源的文档）"""
        doc_analysis = {"total": 3, "with_source": 2, "with_page": 2, "avg_length": 100}
        result = _evaluate_confidence(doc_analysis, 3)
        self.assertEqual(result, "高")
    
    def test_high_confidence_many_sources(self):
        """测试高可信度（多个来源）"""
        doc_analysis = {"total": 5, "with_source": 4, "with_page": 3, "avg_length": 150}
        result = _evaluate_confidence(doc_analysis, 5)
        self.assertEqual(result, "高")
    
    def test_medium_confidence_with_source(self):
        """测试中可信度（有 1 个来源）"""
        doc_analysis = {"total": 2, "with_source": 1, "with_page": 0, "avg_length": 80}
        result = _evaluate_confidence(doc_analysis, 2)
        self.assertEqual(result, "中")
    
    def test_medium_confidence_many_docs(self):
        """测试中可信度（文档数量>=3）"""
        doc_analysis = {"total": 5, "with_source": 0, "with_page": 0, "avg_length": 50}
        result = _evaluate_confidence(doc_analysis, 5)
        self.assertEqual(result, "中")
    
    def test_low_confidence(self):
        """测试低可信度（少文档且无来源）"""
        doc_analysis = {"total": 1, "with_source": 0, "with_page": 0, "avg_length": 30}
        result = _evaluate_confidence(doc_analysis, 1)
        self.assertEqual(result, "低")
    
    def test_edge_case_single_source(self):
        """测试边界情况：单个文档带来源"""
        doc_analysis = {"total": 1, "with_source": 1, "with_page": 1, "avg_length": 100}
        result = _evaluate_confidence(doc_analysis, 1)
        self.assertEqual(result, "中")


class TestIntegration(unittest.TestCase):
    """集成测试：文档分析 + 可信度评估"""
    
    def test_full_workflow_high_quality(self):
        """测试完整工作流：高质量文档"""
        docs = [
            {"content": "柴油机工作原理详解" * 10, "source": "柴油机手册", "page": 15},
            {"content": "柴油机维护指南" * 10, "source": "维护手册", "page": 30},
            {"content": "柴油机故障排除" * 10, "source": "故障手册", "page": 45}
        ]
        
        doc_analysis = _analyze_documents(docs)
        confidence = _evaluate_confidence(doc_analysis, len(docs))
        
        self.assertEqual(doc_analysis["total"], 3)
        self.assertEqual(doc_analysis["with_source"], 3)
        self.assertEqual(confidence, "高")
    
    def test_full_workflow_low_quality(self):
        """测试完整工作流：低质量文档"""
        docs = [
            {"content": "简短内容"},
            {"content": "另一段简短内容"}
        ]
        
        doc_analysis = _analyze_documents(docs)
        confidence = _evaluate_confidence(doc_analysis, len(docs))
        
        self.assertEqual(doc_analysis["total"], 2)
        self.assertEqual(doc_analysis["with_source"], 0)
        self.assertEqual(confidence, "低")


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 船舶工程问答技能单元测试")
    print("=" * 70)
    
    # 运行测试
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 70)
    print("✅ 测试完成")
    print("=" * 70)
