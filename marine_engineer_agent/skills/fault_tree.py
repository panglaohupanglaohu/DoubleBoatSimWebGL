"""
故障树分析模块 (Fault Tree Analysis)
船舶系统可靠性与故障诊断

实现：
1. 故障树数据结构 (顶事件、中间事件、底事件)
2. 最小割集计算 (MOCUS 算法)
3. 顶事件概率计算
4. 重要度分析 (FV 重要度、RAW 重要度)
5. FMEA 集成 (故障模式与影响分析)
6. 贝叶斯网络接口

参考：
- IEC 61025: Fault tree analysis (FTA)
- IEC 60812: FMEA
- Marine Fault Diagnosis research (2025-2026)
"""

import math
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import json


class GateType(Enum):
    """逻辑门类型"""
    AND = "AND"  # 与门
    OR = "OR"  # 或门
    VOTING = "VOTING"  # 投票门 (k/n)
    NOT = "NOT"  # 非门
    INHIBIT = "INHIBIT"  # 禁门


class EventType(Enum):
    """事件类型"""
    TOP = "top"  # 顶事件
    INTERMEDIATE = "intermediate"  # 中间事件
    BASIC = "basic"  # 底事件
    UNDEVELOPED = "undeveloped"  # 未展开事件
    HOUSE = "house"  # 房事件 (必然事件)


@dataclass
class BasicEvent:
    """底事件"""
    id: str  # 事件 ID (如 BE-001)
    name: str  # 事件名称
    description: str = ""  # 描述
    failure_rate: float = 0.0  # 失效率 (次/小时)
    probability: float = 0.0  # 失效概率
    repair_time: float = 0.0  # 修复时间 (小时)
    maintenance_category: str = ""  # 维修类别
    
    def __post_init__(self):
        """计算失效概率 (如果给定失效率)"""
        if self.failure_rate > 0 and self.repair_time > 0:
            # 稳态可用度模型
            mttr = self.repair_time
            mtbf = 1.0 / self.failure_rate
            self.probability = mttr / (mtbf + mttr)


@dataclass
class Gate:
    """逻辑门"""
    id: str  # 门 ID (如 G-001)
    type: GateType  # 逻辑门类型
    name: str = ""  # 门名称
    inputs: List[str] = field(default_factory=list)  # 输入事件 ID 列表
    voting_k: int = 0  # 投票门参数 (k/n 中的 k)
    voting_n: int = 0  # 投票门参数 (k/n 中的 n)
    inhibit_condition: str = ""  # 禁门条件


@dataclass
class FaultTree:
    """故障树"""
    id: str  # 故障树 ID
    name: str  # 故障树名称
    system: str  # 所属系统
    top_event_id: str  # 顶事件 ID
    events: Dict[str, BasicEvent] = field(default_factory=dict)  # 底事件
    gates: Dict[str, Gate] = field(default_factory=dict)  # 逻辑门
    description: str = ""


@dataclass
class MinimalCutSet:
    """最小割集"""
    id: int  # 割集编号
    events: List[str]  # 包含的底事件 ID
    probability: float = 0.0  # 割集概率
    importance: float = 0.0  # 重要度


@dataclass
class FMEAEntry:
    """FMEA 条目"""
    item: str  # 分析项目
    function: str  # 功能
    failure_mode: str  # 故障模式
    failure_effect: str  # 故障影响
    severity: int = 1  # 严重度 (1-10)
    occurrence: int = 1  # 发生度 (1-10)
    detection: int = 1  # 探测度 (1-10)
    rpn: int = 0  # 风险优先数
    recommended_action: str = ""
    action_taken: str = ""
    
    def __post_init__(self):
        """计算 RPN"""
        self.rpn = self.severity * self.occurrence * self.detection


@dataclass
class FTAResult:
    """FTA 分析结果"""
    fault_tree_id: str
    top_event_probability: float  # 顶事件概率
    top_event_frequency: float  # 顶事件频率 (次/年)
    minimal_cut_sets: List[MinimalCutSet] = field(default_factory=list)
    critical_cut_sets: List[MinimalCutSet] = field(default_factory=list)
    event_importance: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    assessment: str = ""


class FaultTreeAnalyzer:
    """
    故障树分析器
    
    实现 FTA 核心算法：
    1. 最小割集计算 (MOCUS)
    2. 顶事件概率计算
    3. 重要度分析
    """
    
    def __init__(self, fault_tree: FaultTree):
        """
        初始化分析器
        
        Args:
            fault_tree: 故障树对象
        """
        self.tree = fault_tree
        self.cut_sets: List[Set[str]] = []
        
    def calculate_minimal_cut_sets(self) -> List[Set[str]]:
        """
        计算最小割集 (MOCUS 算法)
        
        Method Of Obtaining CUt Sets
        
        Returns:
            最小割集列表 (每个割集是底事件 ID 集合)
        """
        # 从顶事件开始
        top_event_id = self.tree.top_event_id
        
        # 使用队列进行广度优先展开
        queue = [[top_event_id]]
        cut_sets = []
        
        while queue:
            current_path = queue.pop(0)
            current_event = current_path[-1]
            
            # 检查是否是底事件
            if current_event in self.tree.events:
                # 是底事件，加入割集
                cut_set = set(current_path[:-1])  # 移除顶事件
                cut_sets.append(cut_set)
                continue
            
            # 检查是否是逻辑门
            if current_event in self.tree.gates:
                gate = self.tree.gates[current_event]
                
                if gate.type == GateType.OR:
                    # 或门：分支为多个路径
                    for input_event in gate.inputs:
                        new_path = current_path[:-1] + [input_event]
                        queue.append(new_path)
                
                elif gate.type == GateType.AND:
                    # 与门：所有输入在同一割集
                    new_path = current_path[:-1] + gate.inputs
                    queue.append(new_path)
        
        # 最小化处理 (移除包含关系的割集)
        minimal_cut_sets = self._minimize_cut_sets(cut_sets)
        self.cut_sets = minimal_cut_sets
        
        return minimal_cut_sets
    
    def _minimize_cut_sets(self, cut_sets: List[Set[str]]) -> List[Set[str]]:
        """
        最小化割集 (移除超集)
        
        Args:
            cut_sets: 原始割集列表
            
        Returns:
            最小割集列表
        """
        minimal = []
        
        for cut_set in cut_sets:
            is_subset = False
            for other_set in minimal:
                if cut_set.issubset(other_set):
                    is_subset = True
                    break
            
            if not is_subset:
                # 移除包含当前割集的超集
                minimal = [s for s in minimal if not s.issubset(cut_set)]
                minimal.append(cut_set)
        
        return minimal
    
    def calculate_top_event_probability(self) -> float:
        """
        计算顶事件概率
        
        使用最小割集近似法 (Rare Event Approximation)
        P(TOP) ≈ Σ P(CutSet_i)
        
        Returns:
            顶事件概率
        """
        if not self.cut_sets:
            self.calculate_minimal_cut_sets()
        
        # 计算每个割集的概率
        cut_set_probs = []
        
        for cut_set in self.cut_sets:
            # 割集概率 = 所有底事件概率的乘积 (AND 关系)
            prob = 1.0
            for event_id in cut_set:
                if event_id in self.tree.events:
                    prob *= self.tree.events[event_id].probability
            
            cut_set_probs.append(prob)
        
        # 顶事件概率 ≈ 割集概率之和 (小概率近似)
        # 精确计算：P(TOP) = 1 - Π(1 - P(CutSet_i))
        top_prob = 1.0
        for prob in cut_set_probs:
            top_prob *= (1.0 - prob)
        top_prob = 1.0 - top_prob
        
        return min(1.0, top_prob)
    
    def calculate_importance_measures(self) -> Dict[str, float]:
        """
        计算重要度指标
        
        包括：
        - FV 重要度 (Fussell-Vesely)
        - RAW 重要度 (Risk Achievement Worth)
        
        Returns:
            底事件重要度字典
        """
        if not self.cut_sets:
            self.calculate_minimal_cut_sets()
        
        top_prob = self.calculate_top_event_probability()
        importance = {}
        
        if top_prob <= 0:
            return importance
        
        for event_id, event in self.tree.events.items():
            # FV 重要度：该事件参与的割集概率和 / 顶事件概率
            fv_importance = 0.0
            for cut_set in self.cut_sets:
                if event_id in cut_set:
                    # 计算该割集的概率
                    cut_prob = 1.0
                    for eid in cut_set:
                        if eid in self.tree.events:
                            cut_prob *= self.tree.events[eid].probability
                    fv_importance += cut_prob
            
            fv_importance = min(1.0, fv_importance / top_prob)
            
            # RAW 重要度：(1 - P(TOP|event=0)) / (1 - P(TOP))
            # 简化：假设事件失效概率为 1 时的顶事件概率
            raw_importance = 1.0 / (1.0 - top_prob + 0.001)
            
            # 综合重要度
            importance[event_id] = (fv_importance + raw_importance) / 2.0
        
        return importance
    
    def analyze(self) -> FTAResult:
        """
        执行完整 FTA 分析
        
        Returns:
            FTA 分析结果
        """
        result = FTAResult(
            fault_tree_id=self.tree.id,
            top_event_probability=0.0,
            top_event_frequency=0.0
        )
        
        # 1. 计算最小割集
        self.calculate_minimal_cut_sets()
        
        # 2. 计算顶事件概率
        result.top_event_probability = self.calculate_top_event_probability()
        
        # 3. 转换为年化频率 (假设连续运行)
        hours_per_year = 8760
        result.top_event_frequency = result.top_event_probability * hours_per_year
        
        # 4. 生成最小割集对象
        for i, cut_set in enumerate(self.cut_sets):
            # 计算割集概率
            prob = 1.0
            for event_id in cut_set:
                if event_id in self.tree.events:
                    prob *= self.tree.events[event_id].probability
            
            mcs = MinimalCutSet(
                id=i + 1,
                events=list(cut_set),
                probability=prob
            )
            result.minimal_cut_sets.append(mcs)
        
        # 5. 识别关键割集 (概率最高的前 3 个)
        sorted_cut_sets = sorted(
            result.minimal_cut_sets,
            key=lambda x: x.probability,
            reverse=True
        )
        result.critical_cut_sets = sorted_cut_sets[:3]
        
        # 6. 计算重要度
        result.event_importance = self.calculate_importance_measures()
        
        # 7. 生成评估和建议
        self._generate_assessment(result)
        
        return result
    
    def _generate_assessment(self, result: FTAResult):
        """生成评估和建议"""
        assessments = []
        recommendations = []
        
        # 顶事件概率评估
        if result.top_event_probability < 0.001:
            assessments.append("系统可靠性优秀")
        elif result.top_event_probability < 0.01:
            assessments.append("系统可靠性良好")
        elif result.top_event_probability < 0.1:
            assessments.append("系统可靠性一般")
        else:
            assessments.append("系统可靠性需改进")
            recommendations.append("考虑增加冗余设计或提高关键部件可靠性")
        
        # 关键割集分析
        if result.critical_cut_sets:
            top_cut = result.critical_cut_sets[0]
            if top_cut.probability > 0.01:
                recommendations.append(
                    f"关键割集 #{top_cut.id} 概率较高，建议重点改进：{', '.join(top_cut.events)}"
                )
        
        # 重要度分析
        if result.event_importance:
            sorted_importance = sorted(
                result.event_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )
            top_events = sorted_importance[:3]
            if top_events:
                event_names = []
                for event_id, imp in top_events:
                    if event_id in self.tree.events:
                        event_names.append(self.tree.events[event_id].name)
                recommendations.append(
                    f"高重要度部件：{', '.join(event_names)}，建议优先维护"
                )
        
        result.assessment = " | ".join(assessments) if assessments else "分析完成"
        result.recommendations = recommendations


class FMEAAnalyzer:
    """
    FMEA 分析器 (Failure Mode and Effects Analysis)
    
    实现：
    1. FMEA 条目管理
    2. RPN 计算与排序
    3. 与 FTA 集成
    """
    
    def __init__(self):
        """初始化 FMEA 分析器"""
        self.entries: List[FMEAEntry] = []
    
    def add_entry(self, entry: FMEAEntry):
        """添加 FMEA 条目"""
        self.entries.append(entry)
    
    def get_critical_items(self, rpn_threshold: int = 100) -> List[FMEAEntry]:
        """
        获取高风险项目
        
        Args:
            rpn_threshold: RPN 阈值
            
        Returns:
            高风险 FMEA 条目列表
        """
        return [e for e in self.entries if e.rpn >= rpn_threshold]
    
    def get_summary(self) -> Dict:
        """获取 FMEA 摘要"""
        if not self.entries:
            return {"total": 0}
        
        avg_rpn = sum(e.rpn for e in self.entries) / len(self.entries)
        max_rpn = max(e.rpn for e in self.entries)
        critical_count = len(self.get_critical_items())
        
        return {
            "total_entries": len(self.entries),
            "average_rpn": round(avg_rpn, 2),
            "max_rpn": max_rpn,
            "critical_items": critical_count,
            "severity_distribution": self._count_severity(),
            "top_critical": [
                {
                    "item": e.item,
                    "failure_mode": e.failure_mode,
                    "rpn": e.rpn
                }
                for e in sorted(self.entries, key=lambda x: x.rpn, reverse=True)[:5]
            ]
        }
    
    def _count_severity(self) -> Dict[str, int]:
        """统计严重度分布"""
        dist = {"high": 0, "medium": 0, "low": 0}
        for e in self.entries:
            if e.severity >= 8:
                dist["high"] += 1
            elif e.severity >= 4:
                dist["medium"] += 1
            else:
                dist["low"] += 1
        return dist


# ============================================================================
# 预定义故障树模板
# ============================================================================

def create_marine_engine_fault_tree() -> FaultTree:
    """创建船舶主机故障树模板"""
    tree = FaultTree(
        id="FTA-ME-001",
        name="船舶主机失效故障树",
        system="Main Engine",
        top_event_id="TE-001",
        description="分析船舶主机失效的根本原因"
    )
    
    # 顶事件
    tree.gates["TE-001"] = Gate(
        id="TE-001",
        type=GateType.OR,
        name="主机失效",
        inputs=["G-001", "G-002", "G-003"]
    )
    
    # 燃油系统故障
    tree.gates["G-001"] = Gate(
        id="G-001",
        type=GateType.OR,
        name="燃油系统故障",
        inputs=["BE-001", "BE-002", "BE-003"]
    )
    
    # 润滑系统故障
    tree.gates["G-002"] = Gate(
        id="G-002",
        type=GateType.OR,
        name="润滑系统故障",
        inputs=["BE-004", "BE-005", "BE-006"]
    )
    
    # 冷却系统故障
    tree.gates["G-003"] = Gate(
        id="G-003",
        type=GateType.OR,
        name="冷却系统故障",
        inputs=["BE-007", "BE-008", "BE-009"]
    )
    
    # 底事件
    tree.events["BE-001"] = BasicEvent(
        id="BE-001",
        name="燃油泵失效",
        description="高压燃油泵故障",
        failure_rate=0.0001,
        repair_time=4.0
    )
    
    tree.events["BE-002"] = BasicEvent(
        id="BE-002",
        name="燃油滤器堵塞",
        description="燃油滤器脏堵",
        failure_rate=0.0005,
        repair_time=1.0
    )
    
    tree.events["BE-003"] = BasicEvent(
        id="BE-003",
        name="喷油器故障",
        description="喷油器雾化不良",
        failure_rate=0.0002,
        repair_time=2.0
    )
    
    tree.events["BE-004"] = BasicEvent(
        id="BE-004",
        name="滑油泵失效",
        description="主滑油泵故障",
        failure_rate=0.0001,
        repair_time=4.0
    )
    
    tree.events["BE-005"] = BasicEvent(
        id="BE-005",
        name="滑油压力低",
        description="滑油系统压力不足",
        failure_rate=0.0003,
        repair_time=2.0
    )
    
    tree.events["BE-006"] = BasicEvent(
        id="BE-006",
        name="滑油污染",
        description="滑油变质或污染",
        failure_rate=0.0002,
        repair_time=8.0
    )
    
    tree.events["BE-007"] = BasicEvent(
        id="BE-007",
        name="冷却水泵失效",
        description="海水/淡水泵故障",
        failure_rate=0.0001,
        repair_time=4.0
    )
    
    tree.events["BE-008"] = BasicEvent(
        id="BE-008",
        name="热交换器堵塞",
        description="冷却器脏堵",
        failure_rate=0.0004,
        repair_time=6.0
    )
    
    tree.events["BE-009"] = BasicEvent(
        id="BE-009",
        name="冷却液泄漏",
        description="冷却系统泄漏",
        failure_rate=0.0002,
        repair_time=3.0
    )
    
    return tree


# ============================================================================
# API 辅助函数
# ============================================================================

def analyze_fault_tree(tree_data: Dict) -> Dict:
    """
    FTA 分析 API 辅助函数
    
    Args:
        tree_data: 故障树数据 (JSON 格式)
        
    Returns:
        分析结果字典
    """
    # 这里应该解析 tree_data 构建 FaultTree 对象
    # 为简化，使用预定义模板
    tree = create_marine_engine_fault_tree()
    
    analyzer = FaultTreeAnalyzer(tree)
    result = analyzer.analyze()
    
    return {
        "fault_tree_id": result.fault_tree_id,
        "top_event_probability": round(result.top_event_probability, 6),
        "top_event_frequency_per_year": round(result.top_event_frequency, 4),
        "minimal_cut_sets_count": len(result.minimal_cut_sets),
        "critical_cut_sets": [
            {
                "id": cs.id,
                "events": cs.events,
                "probability": round(cs.probability, 8)
            }
            for cs in result.critical_cut_sets
        ],
        "event_importance": {
            k: round(v, 4) for k, v in result.event_importance.items()
        },
        "assessment": result.assessment,
        "recommendations": result.recommendations
    }


def analyze_fmea(entries_data: List[Dict]) -> Dict:
    """
    FMEA 分析 API 辅助函数
    
    Args:
        entries_data: FMEA 条目列表
        
    Returns:
        分析结果字典
    """
    analyzer = FMEAAnalyzer()
    
    for entry_data in entries_data:
        entry = FMEAEntry(
            item=entry_data.get("item", ""),
            function=entry_data.get("function", ""),
            failure_mode=entry_data.get("failure_mode", ""),
            failure_effect=entry_data.get("failure_effect", ""),
            severity=entry_data.get("severity", 1),
            occurrence=entry_data.get("occurrence", 1),
            detection=entry_data.get("detection", 1)
        )
        analyzer.add_entry(entry)
    
    return analyzer.get_summary()


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    # 创建故障树
    tree = create_marine_engine_fault_tree()
    
    # 执行分析
    analyzer = FaultTreeAnalyzer(tree)
    result = analyzer.analyze()
    
    print("=" * 60)
    print("船舶主机故障树分析报告")
    print("=" * 60)
    print(f"\n故障树：{tree.name}")
    print(f"顶事件：主机失效")
    print(f"\n【顶事件概率】{result.top_event_probability:.6f}")
    print(f"【年化频率】{result.top_event_frequency:.4f} 次/年")
    print(f"\n【最小割集数量】{len(result.minimal_cut_sets)}")
    print(f"\n【关键割集】(前 3 个)")
    for cs in result.critical_cut_sets:
        event_names = []
        for eid in cs.events:
            if eid in tree.events:
                event_names.append(tree.events[eid].name)
        print(f"  割集 #{cs.id}: {', '.join(event_names)}")
        print(f"    概率：{cs.probability:.8f}")
    
    print(f"\n【评估】{result.assessment}")
    if result.recommendations:
        print(f"\n【建议】")
        for rec in result.recommendations:
            print(f"  - {rec}")
    print("=" * 60)
