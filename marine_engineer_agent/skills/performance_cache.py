"""
性能优化缓存模块

提供 LRU 缓存、正则表达式预编译和字符串优化功能。
用于提升 fault_diagnosis 和 query_answer 技能的性能。

:author: marine_engineer_agent
:version: 1.0.0
:since: 2026-03-10
"""

import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Callable, TypeVar
from functools import lru_cache, wraps
from collections import OrderedDict
import time

# ============================================================================
# 正则表达式预编译
# ============================================================================

# 关键词提取模式 - 匹配单词边界
KEYWORD_PATTERN = re.compile(r'\b(\w+)\b', re.UNICODE)

# 中文分词模式 - 匹配中文字符
CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fff]+')

# 标点符号清理模式
PUNCTUATION_PATTERN = re.compile(r'[^\w\s\u4e00-\u9fff]')

# 空白字符清理模式
WHITESPACE_PATTERN = re.compile(r'\s+')

# 数字匹配模式
NUMBER_PATTERN = re.compile(r'\d+\.?\d*')

# 单位匹配模式 (如 rpm, °C, bar, kPa 等)
UNIT_PATTERN = re.compile(r'(rpm|°C|°F|bar|kPa|MPa|kW|HP|L|h|m|s|ms|%)\b', re.IGNORECASE)


def extract_keywords(text: str) -> List[str]:
    """
    提取文本中的关键词 (使用预编译正则)
    
    :param text: 输入文本
    :return: 关键词列表 (去重)
    """
    # 清理标点符号
    cleaned = PUNCTUATION_PATTERN.sub(' ', text)
    
    # 提取单词
    matches = KEYWORD_PATTERN.findall(cleaned)
    
    # 去重并过滤短词
    keywords = [w.lower() for w in matches if len(w) > 2]
    return list(dict.fromkeys(keywords))


def extract_chinese_terms(text: str) -> List[str]:
    """
    提取中文术语 (使用预编译正则)
    
    :param text: 输入文本
    :return: 中文术语列表
    """
    return CHINESE_PATTERN.findall(text)


def clean_text(text: str) -> str:
    """
    清理文本 (使用预编译正则)
    
    :param text: 输入文本
    :return: 清理后的文本
    """
    # 清理标点
    text = PUNCTUATION_PATTERN.sub(' ', text)
    # 规范化空白
    text = WHITESPACE_PATTERN.sub(' ', text)
    return text.strip()


# ============================================================================
# LRU 缓存装饰器
# ============================================================================

T = TypeVar('T')


def timed_cache(maxsize: int = 128, ttl: int = 1800):
    """
    带 TTL 的 LRU 缓存装饰器
    
    :param maxsize: 最大缓存条目数
    :param ttl: 缓存生存时间 (秒)，默认 30 分钟
    :return: 装饰器函数
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache: OrderedDict = OrderedDict()
        timestamps: Dict[str, float] = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # 生成缓存键
            key = _make_cache_key(args, kwargs)
            current_time = time.time()
            
            # 检查缓存是否过期
            if key in cache:
                if current_time - timestamps[key] < ttl:
                    # 命中缓存，更新 LRU 顺序
                    cache.move_to_end(key)
                    return cache[key]
                else:
                    # 缓存过期，删除
                    del cache[key]
                    del timestamps[key]
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            if len(cache) >= maxsize:
                # 删除最旧的条目
                oldest_key = next(iter(cache))
                del cache[oldest_key]
                del timestamps[oldest_key]
            
            cache[key] = result
            timestamps[key] = current_time
            
            return result
        
        def cache_clear() -> None:
            """清空缓存"""
            cache.clear()
            timestamps.clear()
        
        def cache_info() -> Dict[str, Any]:
            """返回缓存信息"""
            return {
                'size': len(cache),
                'maxsize': maxsize,
                'ttl': ttl,
                'keys': list(cache.keys())[:10]  # 仅返回前 10 个键
            }
        
        wrapper.cache_clear = cache_clear  # type: ignore
        wrapper.cache_info = cache_info  # type: ignore
        
        return wrapper
    
    return decorator


def _make_cache_key(args: Tuple, kwargs: Dict) -> str:
    """
    生成缓存键
    
    :param args: 位置参数
    :param kwargs: 关键字参数
    :return: 缓存键字符串
    """
    key_parts = []
    
    # 处理位置参数
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        elif isinstance(arg, (list, tuple)):
            key_parts.append(str(hash(tuple(arg))))
        elif isinstance(arg, dict):
            key_parts.append(str(hash(tuple(sorted(arg.items())))))
        else:
            key_parts.append(str(id(arg)))
    
    # 处理关键字参数
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (str, int, float, bool)):
            key_parts.append(f"{k}={v}")
        elif isinstance(v, (list, tuple)):
            key_parts.append(f"{k}={hash(tuple(v))}")
        elif isinstance(v, dict):
            key_parts.append(f"{k}={hash(tuple(sorted(v.items())))}")
        else:
            key_parts.append(f"{k}={id(v)}")
    
    # 生成哈希
    key_string = '|'.join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


# ============================================================================
# 字符串优化函数
# ============================================================================

def join_strings(strings: List[str], separator: str = '') -> str:
    """
    高效字符串拼接 (使用 join 代替 +)
    
    :param strings: 字符串列表
    :param separator: 分隔符
    :return: 拼接后的字符串
    """
    return separator.join(strings)


def build_report(sections: List[Dict[str, Any]]) -> str:
    """
    构建诊断报告 (使用高效的字符串拼接)
    
    :param sections: 报告段落列表
    :return: 完整报告文本
    """
    parts = []
    
    for section in sections:
        title = section.get('title', '')
        content = section.get('content', '')
        
        if title:
            parts.append(f"## {title}\n")
        if content:
            parts.append(f"{content}\n")
    
    return join_strings(parts, separator='\n')


def format_list(items: List[str], bullet: str = '- ') -> str:
    """
    格式化列表为文本 (使用高效的字符串拼接)
    
    :param items: 列表项
    :param bullet: 项目符号
    :return: 格式化文本
    """
    lines = [f"{bullet}{item}" for item in items]
    return join_strings(lines, separator='\n')


# ============================================================================
# 性能监控
# ============================================================================

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.timings: Dict[str, List[float]] = {}
    
    def record(self, operation: str, duration_ms: float) -> None:
        """
        记录操作耗时
        
        :param operation: 操作名称
        :param duration_ms: 耗时 (毫秒)
        """
        if operation not in self.timings:
            self.timings[operation] = []
        self.timings[operation].append(duration_ms)
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """
        获取操作统计信息
        
        :param operation: 操作名称
        :return: 统计信息 (avg, min, max, count)
        """
        if operation not in self.timings or not self.timings[operation]:
            return {'avg': 0, 'min': 0, 'max': 0, 'count': 0}
        
        timings = self.timings[operation]
        return {
            'avg': sum(timings) / len(timings),
            'min': min(timings),
            'max': max(timings),
            'count': len(timings)
        }
    
    def reset(self) -> None:
        """重置所有统计"""
        self.timings.clear()


# 全局性能监控实例
perf_monitor = PerformanceMonitor()


def timed_operation(operation_name: str):
    """
    操作耗时监控装饰器
    
    :param operation_name: 操作名称
    :return: 装饰器函数
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            start_time = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                perf_monitor.record(operation_name, duration_ms)
        
        return wrapper
    return decorator


# ============================================================================
# 缓存工具函数
# ============================================================================

def compute_hash(text: str) -> str:
    """
    计算文本哈希值
    
    :param text: 输入文本
    :return: MD5 哈希值 (16 进制)
    """
    return hashlib.md5(text.encode()).hexdigest()


def compute_docs_hash(docs: List[Dict[str, Any]]) -> str:
    """
    计算文档集合哈希值
    
    :param docs: 文档列表
    :return: 组合哈希值
    """
    doc_hashes = []
    for doc in docs:
        # 使用文档的关键字段生成哈希
        doc_key = f"{doc.get('title', '')}|{doc.get('content', '')[:100]}"
        doc_hashes.append(compute_hash(doc_key))
    
    return compute_hash('|'.join(sorted(doc_hashes)))


# ============================================================================
# 测试函数
# ============================================================================

def run_cache_tests() -> Dict[str, Any]:
    """运行缓存模块测试"""
    results = {
        'regex_tests': [],
        'cache_tests': [],
        'string_tests': []
    }
    
    # 测试正则表达式
    test_text = "发动机温度过高，转速 2500rpm，油压 3.5bar"
    keywords = extract_keywords(test_text)
    results['regex_tests'].append({
        'test': 'extract_keywords',
        'input': test_text,
        'output': keywords,
        'passed': len(keywords) > 0
    })
    
    chinese_terms = extract_chinese_terms(test_text)
    results['regex_tests'].append({
        'test': 'extract_chinese_terms',
        'input': test_text,
        'output': chinese_terms,
        'passed': len(chinese_terms) > 0
    })
    
    # 测试缓存
    @timed_cache(maxsize=100, ttl=60)
    def test_func(x: int) -> int:
        return x * 2
    
    result1 = test_func(5)
    result2 = test_func(5)  # 应该命中缓存
    cache_info = test_func.cache_info()  # type: ignore
    
    results['cache_tests'].append({
        'test': 'timed_cache',
        'result1': result1,
        'result2': result2,
        'cache_info': cache_info,
        'passed': result1 == result2 == 10
    })
    
    # 测试字符串拼接
    test_strings = ['Hello', 'World', 'Test']
    joined = join_strings(test_strings, separator=' ')
    results['string_tests'].append({
        'test': 'join_strings',
        'input': test_strings,
        'output': joined,
        'passed': joined == 'Hello World Test'
    })
    
    return results


if __name__ == '__main__':
    import json
    test_results = run_cache_tests()
    print(json.dumps(test_results, indent=2, ensure_ascii=False))
