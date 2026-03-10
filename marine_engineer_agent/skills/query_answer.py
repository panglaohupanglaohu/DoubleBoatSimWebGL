"""
船舶工程问答技能模块

基于知识库检索结果，回答船舶工程相关问题。
支持文档分析、可信度评估、来源追踪等功能。

:author: marine_engineer_agent
:version: 2.0.0
:since: 2026-03-09
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import logging

# 导入配置类
from marine_config import MarineEngineerConfig

# 导入性能优化模块
from performance_cache import (
    join_strings,
    timed_cache,
    perf_monitor,
    timed_operation
)

# 配置模块日志
logger = logging.getLogger(__name__)


def query_answer_skill(
    user_input: str,
    relevant_docs: List[Dict[str, Any]],
    config: Optional[Union[MarineEngineerConfig, Dict[str, Any]]] = None
) -> str:
    """
    船舶工程问答技能：基于知识库回答用户问题
    
    :param user_input: 用户问题（如"船舶柴油机的工作原理是什么"）
    :param relevant_docs: 知识库检索结果，每个文档包含 content/source/page 等字段
    :param config: 智能体配置对象或字典（向后兼容），包含 runtime 配置
    :return: 格式化的问答结果
    """
    logger.info(f"问答请求：{user_input}")
    
    # 配置对象标准化：支持 MarineEngineerConfig 或字典（向后兼容）
    if config is None:
        config_obj = MarineEngineerConfig()
    elif isinstance(config, MarineEngineerConfig):
        config_obj = config
    else:
        # 向后兼容：字典配置转换为配置对象
        config_obj = MarineEngineerConfig.from_dict(config)
    
    # 评估文档相关性
    doc_analysis: Dict[str, Any] = _analyze_documents(relevant_docs)
    
    # 拼接知识库内容（使用优化的字符串拼接）
    context: str = (
        join_strings([doc["content"] for doc in relevant_docs], separator='\n')
        if relevant_docs
        else ""
    )
    
    # 评估答案可信度
    confidence: str = _evaluate_confidence(doc_analysis, len(relevant_docs))
    
    # 构建回答模板（确保基于知识库，不编造）
    if not context:
        answer_content: str = "未在知识库中找到相关内容，请补充更详细的问题描述。"
        confidence = "未知"
    else:
        answer_content = context
    
    # 获取配置参数
    max_length: int = config_obj.runtime.max_context_length
    include_sources: bool = config_obj.runtime.include_sources
    
    # 构建回答
    answer_template: str = f"""
================================================================================
📚 船舶工程知识库问答
================================================================================

❓ 问题：{user_input}
⏰ 回答时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 可信度：{confidence}
📄 参考文档数：{len(relevant_docs)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 回答：
{answer_content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # 添加来源信息（如配置要求）
    if include_sources and relevant_docs:
        answer_template += """
📖 参考来源：
"""
        for i, doc in enumerate(relevant_docs[:5], 1):  # 最多显示 5 个来源
            source: str = doc.get("source", "未知来源")
            page: Optional[int] = doc.get("page")
            page_info: str = f" (第{page}页)" if page else ""
            answer_template += f"  [{i}] {source}{page_info}\n"
        
        answer_template += """
注：完整参考文献列表可在知识库中查询。
"""
    else:
        answer_template += """
注：以上回答基于船舶工程培训文档，如需更详细信息，请补充问题描述。
"""
    
    # 添加免责声明
    answer_template += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ 免责声明：
- 本回答基于知识库文档，仅供参考
- 实际操作请遵循设备制造商指南和海事安全规范
- 关键决策请咨询持证工程师或相关专业人士

================================================================================
"""
    
    # 控制回答长度
    return answer_template[:max_length]


def _analyze_documents(relevant_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    分析文档质量和相关性
    
    统计文档总数、带来源文档数、带页码文档数、平均长度等指标。
    
    :param relevant_docs: 文档列表，每个文档包含 content/source/page 字段
    :return: 分析结果字典，包含 total/with_source/with_page/avg_length
    """
    if not relevant_docs:
        return {
            "total": 0,
            "with_source": 0,
            "with_page": 0,
            "avg_length": 0
        }
    
    with_source: int = sum(1 for doc in relevant_docs if doc.get("source"))
    with_page: int = sum(1 for doc in relevant_docs if doc.get("page"))
    avg_length: float = (
        sum(len(doc.get("content", "")) for doc in relevant_docs) / len(relevant_docs)
    )
    
    return {
        "total": len(relevant_docs),
        "with_source": with_source,
        "with_page": with_page,
        "avg_length": avg_length
    }


def _evaluate_confidence(doc_analysis: Dict[str, Any], doc_count: int) -> str:
    """
    评估答案可信度
    
    基于文档数量和质量评估可信度等级：
    - 2 个及以上带来源文档 = 高可信度
    - 1 个带来源文档或 3 个及以上文档 = 中可信度
    - 其他情况 = 低可信度
    - 无文档 = 未知
    
    :param doc_analysis: 文档分析结果，包含 with_source 等字段
    :param doc_count: 文档总数
    :return: 可信度等级（高/中/低/未知）
    """
    if doc_count == 0:
        return "未知"
    
    # 有多个带来源的文档 = 高可信度
    if doc_analysis["with_source"] >= 2:
        return "高"
    
    # 有来源或文档数量多 = 中可信度
    if doc_analysis["with_source"] >= 1 or doc_count >= 3:
        return "中"
    
    # 否则 = 低可信度
    return "低"
