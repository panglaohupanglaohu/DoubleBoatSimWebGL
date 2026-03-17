# -*- coding: utf-8 -*-
"""
Efficiency Advisor - 能效优化建议
"""

from .efficiency_models import EfficiencyRecommendation, VesselInfo, VoyageData, EngineData, CIIRating, EEXIResult
from .cii_calculator import CIICalculator
from .eexi_calculator import EEXICalculator
from .seemp_manager import SEEMPManager
from typing import Optional, Dict, Any, List


class EfficiencyAdvisor:
    """能效优化顾问.
    
    基于船舶数据和运营情况，提供个性化的能效优化建议。
    """
    
    def __init__(self, vessel: VesselInfo):
        """初始化能效顾问.
        
        Args:
            vessel: 船舶基本信息
        """
        self.vessel = vessel
        self.cii_calculator = CIICalculator(vessel)
        self.eexi_calculator = EEXICalculator(vessel)
        self.seemp_manager = SEEMPManager(vessel)
    
    def analyze_engine_data(
        self,
        engine_data: List[EngineData],
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """分析主机工况数据.
        
        Args:
            engine_data: 主机数据列表
            time_window_hours: 分析时间窗口 (小时)
            
        Returns:
            分析结果字典
        """
        if not engine_data:
            return {"status": "no_data", "recommendations": []}
        
        # 筛选时间窗口内的数据
        cutoff = datetime.now() - timedelta(hours=time_window_hours)
        recent_data = [d for d in engine_data if d.timestamp >= cutoff]
        
        if not recent_data:
            return {"status": "no_recent_data", "recommendations": []}
        
        # 计算统计值
        avg_rpm = sum(d.engine_rpm for d in recent_data) / len(recent_data)
        avg_load = sum(d.engine_load for d in recent_data) / len(recent_data)
        avg_fuel_rate = sum(d.fuel_rate for d in recent_data) / len(recent_data)
        
        # 计算特定燃油消耗 (如数据可用)
        sfc_values = [d.specific_fuel_consumption for d in recent_data if d.specific_fuel_consumption]
        avg_sfc = sum(sfc_values) / len(sfc_values) if sfc_values else None
        
        # 生成建议
        recommendations = []
        
        if avg_load > 85:
            recommendations.append({
                "id": "ENG-001",
                "category": "Engine Operation",
                "title": "降低发动机负载",
                "description": f"当前平均负载 {avg_load:.1f}% 较高。考虑降低航速 10-15% 可显著减少燃油消耗。",
                "expected_improvement": 15.0,
                "priority": "high"
            })
        
        if avg_sfc and avg_sfc > 190:
            recommendations.append({
                "id": "ENG-002",
                "category": "Engine Efficiency",
                "title": "优化发动机工况",
                "description": f"当前 SFC {avg_sfc:.1f} g/kWh 偏高。检查发动机调校、涡轮增压器和燃油喷射系统。",
                "expected_improvement": 5.0,
                "priority": "medium"
            })
        
        if avg_load < 40:
            recommendations.append({
                "id": "ENG-003",
                "category": "Engine Operation",
                "title": "避免低负载运行",
                "description": f"当前平均负载 {avg_load:.1f}% 过低。长期低负载运行会降低发动机效率并增加维护需求。",
                "expected_improvement": 3.0,
                "priority": "low"
            })
        
        return {
            "status": "analyzed",
            "time_window": f"{time_window_hours}h",
            "data_points": len(recent_data),
            "average_rpm": avg_rpm,
            "average_load": avg_load,
            "average_fuel_rate": avg_fuel_rate,
            "average_sfc": avg_sfc,
            "recommendations": recommendations
        }
    
    def generate_recommendations(
        self,
        current_cii: Optional[CIIResult] = None,
        current_eexi: Optional[EEXIResult] = None
    ) -> List[EfficiencyRecommendation]:
        """生成能效优化建议.
        
        Args:
            current_cii: 当前 CII 结果
            current_eexi: 当前 EEXI 结果
            
        Returns:
            建议列表
        """
        recommendations = []
        rec_id = 1
        
        # 基于 CII 评级的建议
        if current_cii:
            if current_cii.rating in [CIIRating.D, CIIRating.E]:
                target = self.cii_calculator.calculate_corrective_action_target(current_cii)
                
                recommendations.append(EfficiencyRecommendation(
                    recommendation_id=f"EFF-{rec_id:03d}",
                    category="CII Improvement",
                    title=f"紧急：改善 CII 评级至{target['target_rating']}",
                    description=f"需要减少 {target['fuel_reduction_kg']:.0f} kg 燃油 ({target['reduction_percentage']:.1f}%) 以达到目标评级。建议措施：{', '.join(target['measures_needed'][:3])}",
                    expected_improvement=target['reduction_percentage'],
                    implementation_difficulty="hard" if target['reduction_percentage'] > 15 else "medium",
                    estimated_cost=0,
                    priority="high",
                    references=["IMO MEPC.346(78) Annex 6"]
                ))
                rec_id += 1
            
            elif current_cii.rating == CIIRating.C:
                recommendations.append(EfficiencyRecommendation(
                    recommendation_id=f"EFF-{rec_id:03d}",
                    category="CII Maintenance",
                    title="保持 CII C 级评级",
                    description="当前评级为 C 级 (合规)。建议实施预防性措施以避免降级。",
                    expected_improvement=5.0,
                    implementation_difficulty="easy",
                    estimated_cost=50000,
                    priority="medium",
                    references=["IMO MEPC.346(78) Annex 8"]
                ))
                rec_id += 1
        
        # 基于 EEXI 的建议
        if current_eexi and not current_eexi.compliance_status:
            required_power = self.eexi_calculator.calculate_required_power_for_compliance()
            
            recommendations.append(EfficiencyRecommendation(
                recommendation_id=f"EFF-{rec_id:03d}",
                category="EEXI Compliance",
                title="紧急：实施功率限制以满足 EEXI",
                description=f"当前 EEXI 不合规。需要将功率限制在 {required_power:.0f} kW 以下，或实施节能措施。",
                expected_improvement=20.0,
                implementation_difficulty="medium",
                estimated_cost=10000,
                priority="high",
                references=["IMO MEPC.346(78) Annex 4"]
            ))
            rec_id += 1
        
        # 通用建议
        recommendations.extend([
            EfficiencyRecommendation(
                recommendation_id=f"EFF-{rec_id:03d}",
                category="Operational",
                title="实施气象定线",
                description="使用气象定线服务优化航线，避开不利海况和洋流。",
                expected_improvement=3.0,
                implementation_difficulty="easy",
                estimated_cost=20000,
                priority="medium",
                references=["IMO SEEMP Guidelines"]
            ),
            EfficiencyRecommendation(
                recommendation_id=f"EFF-{rec_id + 1:03d}",
                category="Maintenance",
                title="定期船体清洁",
                description="每 6 个月进行船体和螺旋桨清洁，减少生物附着阻力。",
                expected_improvement=5.0,
                implementation_difficulty="easy",
                estimated_cost=50000,
                priority="medium",
                references=["ISO 19030:2016"]
            ),
            EfficiencyRecommendation(
                recommendation_id=f"EFF-{rec_id + 2:03d}",
                category="Technical",
                title="评估节能装置 (ESD)",
                description="考虑安装预旋导轮、舵球等节能装置，预期节能 5-10%。",
                expected_improvement=7.0,
                implementation_difficulty="hard",
                estimated_cost=500000,
                priority="low",
                references=["ClassNK ESD Guidelines"]
            )
        ])
        
        return recommendations
    
    def create_action_plan(
        self,
        budget: float = 1000000,
        timeline_months: int = 24
    ) -> Dict[str, Any]:
        """创建能效改进行动计划.
        
        Args:
            budget: 预算 (USD)
            timeline_months: 时间线 (月)
            
        Returns:
            行动计划字典
        """
        recommendations = self.generate_recommendations()
        
        # 按优先级和成本效益排序
        scored_recs = []
        for rec in recommendations:
            if rec.estimated_cost > 0:
                cost_effectiveness = rec.expected_improvement / (rec.estimated_cost / 1000000)
            else:
                cost_effectiveness = rec.expected_improvement * 10  # 零成本方案优先级高
            
            priority_score = {"high": 3, "medium": 2, "low": 1}.get(rec.priority, 1)
            total_score = cost_effectiveness * priority_score
            
            scored_recs.append((rec, total_score))
        
        scored_recs.sort(key=lambda x: x[1], reverse=True)
        
        # 选择符合预算的措施
        selected = []
        remaining_budget = budget
        total_improvement = 0.0
        
        for rec, score in scored_recs:
            if rec.estimated_cost <= remaining_budget:
                selected.append(rec)
                remaining_budget -= rec.estimated_cost
                total_improvement += rec.expected_improvement
        
        return {
            "vessel": self.vessel.vessel_name,
            "budget": budget,
            "timeline_months": timeline_months,
            "selected_measures": [
                {
                    "id": r.recommendation_id,
                    "title": r.title,
                    "cost": r.estimated_cost,
                    "improvement": r.expected_improvement,
                    "priority": r.priority
                }
                for r in selected
            ],
            "total_investment": budget - remaining_budget,
            "total_expected_improvement": total_improvement,
            "remaining_budget": remaining_budget
        }


# ============================================================================
# 合规报告生成器
# ============================================================================

