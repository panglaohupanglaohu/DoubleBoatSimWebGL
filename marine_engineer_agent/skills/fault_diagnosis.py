"""
船舶设备故障诊断技能模块

基于知识库检索结果，对船舶设备故障进行诊断并提供解决方案。
支持关键词提取、权重匹配、置信度评估等功能。

:author: marine_engineer_agent
:version: 2.0.0
:since: 2026-03-09
"""

from typing import List, Dict, Optional, Any, Union
from datetime import datetime
import logging
import re

# 导入配置类
from marine_config import MarineEngineerConfig

# 导入性能优化模块
from performance_cache import (
    extract_keywords,
    extract_chinese_terms,
    clean_text,
    timed_cache,
    compute_hash,
    compute_docs_hash,
    perf_monitor,
    timed_operation
)

# 配置模块日志
logger = logging.getLogger(__name__)


def fault_diagnosis_skill(
    user_input: str,
    relevant_docs: List[Dict[str, Any]],
    config: Optional[Union[MarineEngineerConfig, Dict[str, Any]]] = None
) -> str:
    """
    船舶设备故障诊断技能：基于知识库给出故障原因和解决方案
    
    :param user_input: 故障描述（如"柴油机排气温度过高"）
    :param relevant_docs: 知识库检索结果，每个文档包含 content/source/page 等字段
    :param config: 智能体配置对象或字典（向后兼容），包含 safety 和 runtime 配置
    :return: 格式化的故障诊断报告
    """
    logger.info(f"故障诊断请求：{user_input}")
    
    # 配置对象标准化：支持 MarineEngineerConfig 或字典（向后兼容）
    if config is None:
        config_obj = MarineEngineerConfig()
    elif isinstance(config, MarineEngineerConfig):
        config_obj = config
    else:
        # 向后兼容：字典配置转换为配置对象
        config_obj = MarineEngineerConfig.from_dict(config)
    
    # 提取故障关键词（改进版：支持多种分隔符）
    fault_keywords: List[str] = _extract_fault_keywords(user_input)
    
    # 从知识库中匹配故障解决方案（带权重排序）
    matched_results: List[Dict[str, Any]] = _match_fault_solutions(
        fault_keywords, relevant_docs
    )
    
    if not matched_results:
        diagnosis_result: str = "未找到对应故障的解决方案"
        confidence: str = "低"
    else:
        diagnosis_result = matched_results[0]["content"]
        confidence = matched_results[0]["confidence"]
    
    # 获取安全配置
    require_safety_warning: bool = config_obj.safety.require_warning
    
    # 结构化输出诊断结果
    result: str = f"""
================================================================================
🔧 船舶设备故障诊断报告
================================================================================

📋 故障描述：{user_input}
🔍 提取关键词：{', '.join(fault_keywords)}
📊 匹配置信度：{confidence}
⏰ 诊断时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 诊断结果：
{diagnosis_result}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ 处理建议：
1. 确认故障部件是否符合船舶工程维护规范
2. 如需实操指导，请提供设备型号和具体故障现象
3. 操作前务必遵循海事安全操作规范
"""
    
    # 添加安全警告（如配置要求）
    if require_safety_warning:
        result += """
🛡️ 安全警告：
- 操作前确保已穿戴适当的个人防护装备 (PPE)
- 遵循锁闭/挂牌 (LOTO) 程序
- 确保工作区域通风良好
- 如有疑问，请咨询资深工程师或设备制造商
"""
    
    # 添加环保合规提示
    result += """
🌱 环保合规提示：
- 处理废油/废液时遵循 MARPOL 公约要求
- 记录所有维护活动以备检查
- 使用环保型制冷剂和灭火剂（如适用）

================================================================================
"""
    
    return result


@timed_cache(maxsize=500, ttl=300)
def _extract_fault_keywords(user_input: str) -> List[str]:
    """
    提取故障关键词（支持多种分隔符，带缓存）
    
    使用预编译正则表达式分割用户输入，过滤停用词和无效字符。
    结果会被缓存 5 分钟，相同输入直接返回缓存结果。
    
    :param user_input: 用户输入的故障描述
    :return: 关键词列表，已过滤停用词和空字符串
    """
    # 支持的分隔符：冒号、破折号、空格（保持原有逻辑）
    separators: str = r'[：\-:\s]+'
    parts: List[str] = re.split(separators, user_input.strip())
    
    # 过滤空字符串和常见停用词
    stop_words: set = {"的", "是", "有", "出现", "发生", "问题", "故障", "请", "问", "如何", "怎么"}
    stop_chars: set = set("".join(stop_words))
    
    keywords: List[str] = []
    for p in parts:
        if not p or p in stop_words or len(p) <= 1:
            continue
        # 检查是否所有字符都是停用词字符（如"的是有的"）
        if all(c in stop_chars for c in p):
            continue
        keywords.append(p)
    
    return keywords


def _match_fault_solutions(
    keywords: List[str],
    relevant_docs: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    匹配故障解决方案（带权重排序）
    
    根据关键词在文档中的匹配数量计算置信度：
    - 2 个及以上关键词匹配 = 高置信度
    - 1 个关键词匹配 = 中置信度
    - 无匹配 = 低置信度
    
    :param keywords: 故障关键词列表
    :param relevant_docs: 相关文档列表，每个文档包含 content 字段
    :return: 匹配结果列表，按匹配数量降序排序
    """
    # 生成缓存键
    keywords_hash = compute_hash('|'.join(sorted(keywords)))
    docs_hash = compute_docs_hash(relevant_docs)
    cache_key = f"{keywords_hash}|{docs_hash}"
    
    # 使用优化的匹配逻辑
    results: List[Dict[str, Any]] = []
    
    for doc in relevant_docs:
        content: str = doc.get("content", "")
        
        # 使用优化的字符串匹配
        match_count: int = sum(1 for kw in keywords if kw in content)
        
        if match_count > 0:
            confidence: str = (
                "高" if match_count >= 2
                else "中" if match_count == 1
                else "低"
            )
            matched_keywords: List[str] = [kw for kw in keywords if kw in content]
            
            results.append({
                "content": content,
                "confidence": confidence,
                "match_count": match_count,
                "matched_keywords": matched_keywords
            })
    
    # 按匹配数量排序
    results.sort(key=lambda x: x["match_count"], reverse=True)
    
    return results
