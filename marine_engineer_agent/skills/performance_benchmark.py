"""
性能基准测试模块

测量 fault_diagnosis_skill 和 query_answer_skill 的响应时间，
分析关键词匹配算法复杂度，识别性能瓶颈。

:author: marine_engineer_agent
:version: 1.0.0
:since: 2026-03-10
"""

import time
import statistics
from typing import List, Dict, Any, Callable
from dataclasses import dataclass, field
import logging
import sys
import os

# 添加父目录到路径以导入技能模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fault_diagnosis import fault_diagnosis_skill, _extract_fault_keywords, _match_fault_solutions
from query_answer import query_answer_skill, _analyze_documents, _evaluate_confidence

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """基准测试结果数据类"""
    function_name: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    std_dev_ms: float
    median_time_ms: float
    p95_time_ms: float = 0.0
    p99_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """导出为字典"""
        return {
            "function_name": self.function_name,
            "iterations": self.iterations,
            "total_time_ms": round(self.total_time_ms, 3),
            "avg_time_ms": round(self.avg_time_ms, 3),
            "min_time_ms": round(self.min_time_ms, 3),
            "max_time_ms": round(self.max_time_ms, 3),
            "std_dev_ms": round(self.std_dev_ms, 3),
            "median_time_ms": round(self.median_time_ms, 3),
            "p95_time_ms": round(self.p95_time_ms, 3),
            "p99_time_ms": round(self.p99_time_ms, 3)
        }


@dataclass
class ComplexityAnalysis:
    """算法复杂度分析结果"""
    algorithm_name: str
    input_sizes: List[int]
    execution_times: List[float]
    estimated_complexity: str
    notes: str = ""


def run_benchmark(
    func: Callable,
    args_list: List[tuple],
    iterations: int = 100,
    warmup_iterations: int = 10
) -> BenchmarkResult:
    """
    运行基准测试
    
    :param func: 要测试的函数
    :param args_list: 参数列表，每个元素是函数的参数元组
    :param iterations: 测试迭代次数
    :param warmup_iterations: 预热迭代次数
    :return: BenchmarkResult 对象
    """
    func_name = func.__name__
    logger.info(f"开始基准测试：{func_name} ({iterations} 次迭代)")
    
    # 预热阶段
    logger.info(f"预热阶段：{warmup_iterations} 次迭代")
    for i in range(warmup_iterations):
        args = args_list[i % len(args_list)]
        func(*args)
    
    # 正式测试
    execution_times: List[float] = []
    
    for i in range(iterations):
        args = args_list[i % len(args_list)]
        
        start_time = time.perf_counter()
        func(*args)
        end_time = time.perf_counter()
        
        elapsed_ms = (end_time - start_time) * 1000
        execution_times.append(elapsed_ms)
    
    # 计算统计指标
    total_time = sum(execution_times)
    avg_time = total_time / len(execution_times)
    min_time = min(execution_times)
    max_time = max(execution_times)
    std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0.0
    median_time = statistics.median(execution_times)
    
    # 计算百分位数
    sorted_times = sorted(execution_times)
    p95_idx = int(len(sorted_times) * 0.95)
    p99_idx = int(len(sorted_times) * 0.99)
    p95_time = sorted_times[min(p95_idx, len(sorted_times) - 1)]
    p99_time = sorted_times[min(p99_idx, len(sorted_times) - 1)]
    
    result = BenchmarkResult(
        function_name=func_name,
        iterations=iterations,
        total_time_ms=total_time,
        avg_time_ms=avg_time,
        min_time_ms=min_time,
        max_time_ms=max_time,
        std_dev_ms=std_dev,
        median_time_ms=median_time,
        p95_time_ms=p95_time,
        p99_time_ms=p99_time
    )
    
    logger.info(f"基准测试完成：{func_name}")
    logger.info(f"  平均响应时间：{avg_time:.3f} ms")
    logger.info(f"  最小响应时间：{min_time:.3f} ms")
    logger.info(f"  最大响应时间：{max_time:.3f} ms")
    logger.info(f"  标准差：{std_dev:.3f} ms")
    
    return result


def analyze_keyword_extraction_complexity() -> ComplexityAnalysis:
    """
    分析关键词提取算法的时间复杂度
    
    测试不同输入长度下的执行时间，估算算法复杂度。
    
    :return: ComplexityAnalysis 对象
    """
    logger.info("分析关键词提取算法复杂度...")
    
    # 准备不同长度的测试输入
    input_sizes = [10, 20, 50, 100, 200, 500, 1000]
    execution_times = []
    
    for size in input_sizes:
        # 生成测试输入
        test_input = "故障 " + " ".join([f"关键词{i}" for i in range(size)])
        
        # 测量执行时间
        iterations = 50
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            _extract_fault_keywords(test_input)
            end = time.perf_counter()
            times.append((end - start) * 1000)
        
        avg_time = sum(times) / len(times)
        execution_times.append(avg_time)
        logger.info(f"  输入长度 {size}: 平均 {avg_time:.4f} ms")
    
    # 估算复杂度
    # 如果时间增长与输入长度成正比，则为 O(n)
    # 如果时间增长与输入长度的平方成正比，则为 O(n²)
    if len(execution_times) >= 2:
        ratio = execution_times[-1] / execution_times[0] if execution_times[0] > 0 else 0
        size_ratio = input_sizes[-1] / input_sizes[0]
        
        if ratio < size_ratio * 1.5:
            complexity = "O(n) - 线性复杂度"
        elif ratio < size_ratio * size_ratio * 1.5:
            complexity = "O(n log n) 或 O(n²) - 需要优化"
        else:
            complexity = "O(n²) 或更高 - 严重性能问题"
    else:
        complexity = "无法确定"
    
    return ComplexityAnalysis(
        algorithm_name="关键词提取算法",
        input_sizes=input_sizes,
        execution_times=execution_times,
        estimated_complexity=complexity,
        notes="使用正则表达式分割，过滤停用词"
    )


def analyze_keyword_matching_complexity() -> ComplexityAnalysis:
    """
    分析关键词匹配算法的时间复杂度
    
    测试不同关键词数量和文档数量下的执行时间。
    
    :return: ComplexityAnalysis 对象
    """
    logger.info("分析关键词匹配算法复杂度...")
    
    # 准备测试数据
    test_cases = [
        {"keywords": 5, "docs": 10},
        {"keywords": 10, "docs": 20},
        {"keywords": 20, "docs": 50},
        {"keywords": 50, "docs": 100},
        {"keywords": 100, "docs": 200},
    ]
    
    input_sizes = []
    execution_times = []
    
    for case in test_cases:
        # 生成测试数据
        keywords = [f"keyword{i}" for i in range(case["keywords"])]
        docs = [
            {"content": f"content with keyword{j} and keyword{k}"}
            for j in range(case["docs"])
            for k in range(min(3, case["keywords"]))
        ]
        
        # 测量执行时间
        iterations = 20
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            _match_fault_solutions(keywords, docs)
            end = time.perf_counter()
            times.append((end - start) * 1000)
        
        avg_time = sum(times) / len(times)
        total_size = case["keywords"] * case["docs"]
        input_sizes.append(total_size)
        execution_times.append(avg_time)
        logger.info(f"  关键词 {case['keywords']} × 文档 {case['docs']}: 平均 {avg_time:.4f} ms")
    
    # 估算复杂度 (应该是 O(k * d)，k=关键词数，d=文档数)
    complexity = "O(k × d) - 线性复杂度 (k=关键词数，d=文档数)"
    
    return ComplexityAnalysis(
        algorithm_name="关键词匹配算法",
        input_sizes=input_sizes,
        execution_times=execution_times,
        estimated_complexity=complexity,
        notes="遍历所有关键词和文档，简单字符串匹配"
    )


def generate_benchmark_report(
    fault_result: BenchmarkResult,
    query_result: BenchmarkResult,
    keyword_extract_analysis: ComplexityAnalysis,
    keyword_match_analysis: ComplexityAnalysis
) -> str:
    """
    生成基准测试报告
    
    :param fault_result: fault_diagnosis_skill 测试结果
    :param query_result: query_answer_skill 测试结果
    :param keyword_extract_analysis: 关键词提取复杂度分析
    :param keyword_match_analysis: 关键词匹配复杂度分析
    :return: 格式化的报告字符串
    """
    report = f"""
================================================================================
📊 性能基准测试报告
================================================================================

测试时间：{time.strftime('%Y-%m-%d %H:%M:%S')}
测试环境：Python {sys.version.split()[0]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 fault_diagnosis_skill 性能指标
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  测试迭代次数：    {fault_result.iterations}
  总执行时间：      {fault_result.total_time_ms:.3f} ms
  平均响应时间：    {fault_result.avg_time_ms:.3f} ms
  最小响应时间：    {fault_result.min_time_ms:.3f} ms
  最大响应时间：    {fault_result.max_time_ms:.3f} ms
  中位数响应时间：  {fault_result.median_time_ms:.3f} ms
  标准差：          {fault_result.std_dev_ms:.3f} ms
  P95 响应时间：     {fault_result.p95_time_ms:.3f} ms
  P99 响应时间：     {fault_result.p99_time_ms:.3f} ms

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 query_answer_skill 性能指标
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  测试迭代次数：    {query_result.iterations}
  总执行时间：      {query_result.total_time_ms:.3f} ms
  平均响应时间：    {query_result.avg_time_ms:.3f} ms
  最小响应时间：    {query_result.min_time_ms:.3f} ms
  最大响应时间：    {query_result.max_time_ms:.3f} ms
  中位数响应时间：  {query_result.median_time_ms:.3f} ms
  标准差：          {query_result.std_dev_ms:.3f} ms
  P95 响应时间：     {query_result.p95_time_ms:.3f} ms
  P99 响应时间：     {query_result.p99_time_ms:.3f} ms

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 算法复杂度分析
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【关键词提取算法】
  算法名称：  {keyword_extract_analysis.algorithm_name}
  时间复杂度：{keyword_extract_analysis.estimated_complexity}
  备注：      {keyword_extract_analysis.notes}
  
  输入长度与执行时间关系:
"""
    
    for size, time_ms in zip(keyword_extract_analysis.input_sizes, 
                             keyword_extract_analysis.execution_times):
        report += f"    输入长度 {size:4d}: {time_ms:.4f} ms\n"
    
    report += f"""
【关键词匹配算法】
  算法名称：  {keyword_match_analysis.algorithm_name}
  时间复杂度：{keyword_match_analysis.estimated_complexity}
  备注：      {keyword_match_analysis.notes}
  
  输入规模与执行时间关系:
"""
    
    for size, time_ms in zip(keyword_match_analysis.input_sizes,
                             keyword_match_analysis.execution_times):
        report += f"    规模 {size:6d}: {time_ms:.4f} ms\n"
    
    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 性能优化建议
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 关键词提取优化:
   - 预编译正则表达式，避免重复编译
   - 使用集合 (set) 进行停用词查找，O(1) 复杂度
   - 考虑使用更高效的字符串分割方法

2. 关键词匹配优化:
   - 使用 Aho-Corasick 算法进行多模式匹配
   - 对文档建立倒排索引，加速关键词查找
   - 使用缓存存储频繁查询的结果

3. 整体架构优化:
   - 考虑异步处理，提高并发能力
   - 实现结果缓存，减少重复计算
   - 使用更高效的字符串拼接方法 (join vs +)

4. 日志系统优化:
   - 使用异步日志，避免阻塞主线程
   - 实现日志缓冲，减少 I/O 操作
   - 根据日志级别动态调整详细程度

================================================================================
"""
    
    return report


def main():
    """主函数：执行完整的基准测试"""
    logger.info("=" * 60)
    logger.info("开始性能基准测试")
    logger.info("=" * 60)
    
    # 准备测试数据
    fault_test_inputs = [
        ("柴油机排气温度过高", [
            {"content": "柴油机排气温度过高的原因：燃油喷射系统故障", "source": "test1"},
            {"content": "排气温度异常检查冷却系统", "source": "test2"},
            {"content": "涡轮增压器故障导致排气温度升高", "source": "test3"},
        ], {"safety": {"require_warning": True}, "runtime": {"max_context_length": 4096}}),
        ("主机滑油压力过低", [
            {"content": "滑油压力低检查油泵和滤器", "source": "test1"},
            {"content": "滑油系统泄漏导致压力下降", "source": "test2"},
        ], {"safety": {"require_warning": True}, "runtime": {"max_context_length": 4096}}),
        ("锅炉水位异常", [
            {"content": "锅炉水位过高或过低的处理方法", "source": "test1"},
            {"content": "给水系统故障导致水位异常", "source": "test2"},
            {"content": "水位计故障检查方法", "source": "test3"},
        ], {"safety": {"require_warning": True}, "runtime": {"max_context_length": 4096}}),
    ]
    
    query_test_inputs = [
        ("船舶柴油机的工作原理是什么", [
            {"content": "柴油机通过压缩空气产生高温，喷入燃油自燃", "source": "test1"},
            {"content": "四冲程柴油机工作循环：进气、压缩、做功、排气", "source": "test2"},
        ], {"runtime": {"max_context_length": 4096, "include_sources": True}}),
        ("什么是 MARPOL 公约", [
            {"content": "MARPOL 是国际防止船舶造成污染公约", "source": "test1"},
            {"content": "MARPOL 有 6 个附则，涵盖不同类型的污染", "source": "test2"},
        ], {"runtime": {"max_context_length": 4096, "include_sources": True}}),
    ]
    
    # 运行基准测试
    logger.info("\n测试 fault_diagnosis_skill...")
    fault_result = run_benchmark(
        fault_diagnosis_skill,
        fault_test_inputs,
        iterations=100,
        warmup_iterations=10
    )
    
    logger.info("\n测试 query_answer_skill...")
    query_result = run_benchmark(
        query_answer_skill,
        query_test_inputs,
        iterations=100,
        warmup_iterations=10
    )
    
    # 分析算法复杂度
    logger.info("\n分析算法复杂度...")
    keyword_extract_analysis = analyze_keyword_extraction_complexity()
    keyword_match_analysis = analyze_keyword_matching_complexity()
    
    # 生成报告
    report = generate_benchmark_report(
        fault_result,
        query_result,
        keyword_extract_analysis,
        keyword_match_analysis
    )
    
    print(report)
    
    # 保存报告到文件
    report_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../tasks/performance_benchmark_report.md"
    )
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"\n报告已保存到：{report_path}")
    
    return {
        "fault_diagnosis": fault_result.to_dict(),
        "query_answer": query_result.to_dict(),
        "keyword_extraction_complexity": keyword_extract_analysis.estimated_complexity,
        "keyword_matching_complexity": keyword_match_analysis.estimated_complexity
    }


if __name__ == "__main__":
    results = main()
    print("\n📊 测试结果摘要:")
    print(f"  fault_diagnosis_skill 平均响应时间：{results['fault_diagnosis']['avg_time_ms']:.3f} ms")
    print(f"  query_answer_skill 平均响应时间：{results['query_answer']['avg_time_ms']:.3f} ms")
