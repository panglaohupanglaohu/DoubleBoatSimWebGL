# -*- coding: utf-8 -*-
"""
SEEMP Manager - 船舶能效管理计划
"""

from .efficiency_models import SEEMPMeasure, VesselInfo, EnergySavingMeasureType, CIIResult, CIIRating
from .cii_calculator import CIICalculator
from typing import Optional, Dict, Any, List
from datetime import datetime


class SEEMPManager:
    """SEEMP (Ship Energy Efficiency Management Plan) 管理器.
    
    SEEMP Part III 是强制性的船舶能效管理计划，包括:
    1. CII 计算方法
    2. 要求年度 CII 值
    3. 三年实施计划
    4. 自我评估和改进程序
    
    参考：IMO MEPC.346(78) Annex 8
    """
    
    # 标准能效措施库
    STANDARD_MEASURES = {
        EnergySavingMeasureType.HULL_CLEANING: {
            "description": "定期船体和螺旋桨清洁，减少摩擦阻力",
            "expected_savings": 5.0,  # %
            "cost": 50000,  # USD
            "payback_months": 6
        },
        EnergySavingMeasureType.PROPELLER_OPTIMIZATION: {
            "description": "螺旋桨抛光、修复或升级高效螺旋桨",
            "expected_savings": 5.0,
            "cost": 150000,
            "payback_months": 12
        },
        EnergySavingMeasureType.SPEED_OPTIMIZATION: {
            "description": "优化航速，实施经济航速策略",
            "expected_savings": 10.0,
            "cost": 0,
            "payback_months": 1
        },
        EnergySavingMeasureType.WEATHER_ROUTING: {
            "description": "使用气象定线系统优化航线",
            "expected_savings": 3.0,
            "cost": 20000,
            "payback_months": 6
        },
        EnergySavingMeasureType.TRIM_OPTIMIZATION: {
            "description": "优化船舶纵倾，减少阻力",
            "expected_savings": 2.0,
            "cost": 30000,
            "payback_months": 12
        },
        EnergySavingMeasureType.AIR_LUBRICATION: {
            "description": "安装船底空气润滑系统",
            "expected_savings": 7.0,
            "cost": 2000000,
            "payback_months": 36
        },
        EnergySavingMeasureType.WIND_ASSIST: {
            "description": "安装风力助推装置 (旋筒/风帆)",
            "expected_savings": 10.0,
            "cost": 3000000,
            "payback_months": 60
        },
        EnergySavingMeasureType.WASTE_HEAT_RECOVERY: {
            "description": "安装废热回收系统发电",
            "expected_savings": 8.0,
            "cost": 1500000,
            "payback_months": 48
        },
        EnergySavingMeasureType.SHAFT_GENERATOR: {
            "description": "安装轴带发电机",
            "expected_savings": 5.0,
            "cost": 500000,
            "payback_months": 24
        },
        EnergySavingMeasureType.BATTERY_HYBRID: {
            "description": "安装电池混合动力系统",
            "expected_savings": 15.0,
            "cost": 5000000,
            "payback_months": 72
        },
        EnergySavingMeasureType.SOLAR_PANEL: {
            "description": "安装太阳能电池板",
            "expected_savings": 2.0,
            "cost": 200000,
            "payback_months": 60
        },
        EnergySavingMeasureType.LED_LIGHTING: {
            "description": "升级 LED 照明系统",
            "expected_savings": 1.0,
            "cost": 50000,
            "payback_months": 12
        },
        EnergySavingMeasureType.HVAC_OPTIMIZATION: {
            "description": "优化暖通空调系统效率",
            "expected_savings": 2.0,
            "cost": 100000,
            "payback_months": 24
        },
        EnergySavingMeasureType.ENGINE_DERATING: {
            "description": "发动机降功率运行",
            "expected_savings": 15.0,
            "cost": 10000,
            "payback_months": 1
        },
        EnergySavingMeasureType.VFD_INSTALLATION: {
            "description": "安装变频驱动泵和风机",
            "expected_savings": 5.0,
            "cost": 300000,
            "payback_months": 36
        },
    }
    
    def __init__(self, vessel: VesselInfo):
        """初始化 SEEMP 管理器.
        
        Args:
            vessel: 船舶基本信息
        """
        self.vessel = vessel
        self.measures: List[SEEMPMeasure] = []
        self.cii_calculator = CIICalculator(vessel)
    
    def create_measure(
        self,
        measure_type: EnergySavingMeasureType,
        measure_id: Optional[str] = None,
        custom_description: Optional[str] = None,
        custom_savings: Optional[float] = None,
        custom_cost: Optional[float] = None,
        planned_date: Optional[datetime] = None,
        responsible_person: Optional[str] = None
    ) -> SEEMPMeasure:
        """创建新的能效措施.
        
        Args:
            measure_type: 措施类型
            measure_id: 措施编号 (可选，自动生成)
            custom_description: 自定义描述
            custom_savings: 自定义预期节能 (%)
            custom_cost: 自定义成本
            planned_date: 计划实施日期
            responsible_person: 负责人
            
        Returns:
            SEEMPMeasure: 创建的能效措施
        """
        # 获取标准措施信息
        std_info = self.STANDARD_MEASURES.get(measure_type, {})
        
        # 生成措施编号
        if measure_id is None:
            measure_id = f"ESM-{len(self.measures) + 1:03d}"
        
        # 创建措施
        measure = SEEMPMeasure(
            measure_id=measure_id,
            measure_type=measure_type,
            description=custom_description or std_info.get("description", ""),
            expected_savings=custom_savings or std_info.get("expected_savings", 0.0),
            implementation_cost=custom_cost or std_info.get("cost", 0.0),
            payback_period=std_info.get("payback_months", 12),
            planned_date=planned_date,
            responsible_person=responsible_person
        )
        
        self.measures.append(measure)
        return measure
    
    def get_three_year_plan(self, start_year: int = 2026) -> Dict[str, Any]:
        """获取三年实施计划.
        
        Args:
            start_year: 起始年份
            
        Returns:
            三年计划字典
        """
        plan = {
            "vessel_name": self.vessel.vessel_name,
            "imo_number": self.vessel.imo_number,
            "plan_period": f"{start_year}-{start_year + 2}",
            "generation_date": datetime.now().isoformat(),
            "measures": [],
            "yearly_targets": [],
            "total_investment": 0.0,
            "total_expected_savings": 0.0
        }
        
        # 按年份组织措施
        for year in range(start_year, start_year + 3):
            year_plan = {
                "year": year,
                "measures": [],
                "required_cii": self.cii_calculator.get_required_cii(year),
                "target_rating": "C"
            }
            
            for measure in self.measures:
                if measure.planned_date and measure.planned_date.year == year:
                    year_plan["measures"].append({
                        "id": measure.measure_id,
                        "type": measure.measure_type.value,
                        "description": measure.description,
                        "expected_savings": measure.expected_savings,
                        "cost": measure.implementation_cost,
                        "status": measure.implementation_status
                    })
                    plan["total_investment"] += measure.implementation_cost
                    plan["total_expected_savings"] += measure.expected_savings
            
            plan["yearly_targets"].append(year_plan)
        
        # 汇总措施
        for measure in self.measures:
            plan["measures"].append({
                "id": measure.measure_id,
                "type": measure.measure_type.value,
                "description": measure.description,
                "expected_savings": measure.expected_savings,
                "cost": measure.implementation_cost,
                "payback_months": measure.payback_period,
                "planned_date": measure.planned_date.isoformat() if measure.planned_date else None,
                "status": measure.implementation_status,
                "responsible_person": measure.responsible_person
            })
        
        return plan
    
    def update_measure_status(
        self,
        measure_id: str,
        status: str,
        actual_date: Optional[datetime] = None
    ) -> bool:
        """更新措施实施状态.
        
        Args:
            measure_id: 措施编号
            status: 新状态
            actual_date: 实际实施日期
            
        Returns:
            是否更新成功
        """
        for measure in self.measures:
            if measure.measure_id == measure_id:
                measure.implementation_status = status
                if actual_date:
                    measure.actual_date = actual_date
                return True
        return False
    
    def calculate_combined_savings(self) -> float:
        """计算综合节能效果.
        
        考虑措施之间的协同效应，不简单相加。
        
        Returns:
            综合节能百分比
        """
        if not self.measures:
            return 0.0
        
        # 按状态筛选已完成的措施
        completed_measures = [
            m for m in self.measures
            if m.implementation_status == "completed"
        ]
        
        if not completed_measures:
            return 0.0
        
        # 使用递减效应模型：后续措施效果递减 10%
        total_savings = 0.0
        remaining_potential = 100.0
        
        for measure in sorted(completed_measures, key=lambda m: m.expected_savings, reverse=True):
            effective_savings = min(measure.expected_savings, remaining_potential * 0.9)
            total_savings += effective_savings
            remaining_potential -= effective_savings
        
        return total_savings
    
    def export_to_json(self) -> str:
        """导出 SEEMP 计划为 JSON.
        
        Returns:
            JSON 字符串
        """
        plan = self.get_three_year_plan()
        return json.dumps(plan, indent=2, ensure_ascii=False)
    
    def generate_verification_report(self) -> Dict[str, Any]:
        """生成验证报告.
        
        用于船级社或船旗国验证。
        
        Returns:
            验证报告字典
        """
        return {
            "report_type": "SEEMP Part III Verification",
            "vessel_info": {
                "name": self.vessel.vessel_name,
                "imo": self.vessel.imo_number,
                "type": self.vessel.vessel_type.value,
                "dwt": self.vessel.dwt
            },
            "plan_summary": self.get_three_year_plan(),
            "combined_savings": self.calculate_combined_savings(),
            "verification_date": datetime.now().isoformat(),
            "verifier": "Pending assignment",
            "status": "Ready for verification"
        }


# ============================================================================
# 能效顾问
# ============================================================================

