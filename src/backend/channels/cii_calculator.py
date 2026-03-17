# -*- coding: utf-8 -*-
"""
CII Calculator - 船舶 CII 指数计算器
"""

from .efficiency_models import VesselInfo, CIIResult, CIIRating, FuelType
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import math


class CIICalculator:
    """CII (Carbon Intensity Indicator) 计算器.
    
    CII 是船舶运营能效指标，基于年度燃油消耗和运输功计算。
    公式：CII = (Total CO2 emissions) / (Total transport work)
         = (Σ Fuel × CF) / (DWT × Total distance)
    
    评级阈值 (attained CII / required CII):
    - A: ≤0.67 (显著优于要求)
    - B: ≤0.83 (优于要求)
    - C: ≤1.07 (满足要求)
    - D: ≤1.27 (接近不合规)
    - E: >1.27 (不合规)
    
    参考：IMO MEPC.346(78) Annex 6
    """
    
    # CII 年度减排因子 (2023-2030)
    # 来源：IMO MEPC.385(81)
    ANNUAL_REDUCTION_FACTORS = {
        2023: 0.05,
        2024: 0.07,
        2025: 0.09,
        2026: 0.13625,  # 13.625%
        2027: 0.16250,  # 16.250%
        2028: 0.18875,  # 18.875%
        2029: 0.21500,  # 21.500%
        2030: 0.21500,  # 保持 2029 水平
    }
    
    # 评级阈值 (attained/required 比值)
    RATING_THRESHOLDS = {
        CIIRating.A: 0.67,
        CIIRating.B: 0.83,
        CIIRating.C: 1.07,
        CIIRating.D: 1.27,
    }
    
    def __init__(self, vessel: VesselInfo):
        """初始化 CII 计算器.
        
        Args:
            vessel: 船舶基本信息
        """
        self.vessel = vessel
    
    def get_reference_line(self) -> float:
        """获取 CII 参考线.
        
        使用与 EEXI 相同的参考线公式。
        
        Returns:
            参考线值 (g CO2 / dwt-mile)
        """
        eexi_calc = EEXICalculator(self.vessel)
        return eexi_calc.calculate_reference_line(self.vessel.dwt)
    
    def get_required_cii(self, year: int) -> float:
        """获取年度要求 CII 值.
        
        要求 CII = 参考线 × (1 - 年度减排因子)
        
        Args:
            year: 计算年份
            
        Returns:
            要求 CII 值 (g CO2 / dwt-mile)
        """
        reference_line = self.get_reference_line()
        reduction_factor = self.ANNUAL_REDUCTION_FACTORS.get(year, 0.05)
        return reference_line * (1.0 - reduction_factor)
    
    def calculate_cii_from_voyages(
        self,
        voyages: List[VoyageData],
        year: int
    ) -> CIIResult:
        """基于航次数据计算年度 CII.
        
        Args:
            voyages: 航次数据列表
            year: 计算年份
            
        Returns:
            CIIResult: CII 计算结果
        """
        # 汇总年度数据
        total_fuel = 0.0  # kg
        total_distance = 0.0  # nm
        total_co2 = 0.0  # kg
        
        for voyage in voyages:
            total_fuel += voyage.fuel_consumed
            total_distance += voyage.distance_nm
            
            # CO2 = Fuel × CF
            cf = voyage.fuel_type.emission_factor / 1000.0  # kg CO2 / kg fuel
            total_co2 += voyage.fuel_consumed * cf
        
        return self.calculate_cii(
            total_fuel=total_fuel,
            total_distance=total_distance,
            total_co2=total_co2,
            year=year
        )
    
    def calculate_cii(
        self,
        total_fuel: float,
        total_distance: float,
        total_co2: Optional[float] = None,
        year: int = 2026
    ) -> CIIResult:
        """计算 CII.
        
        Args:
            total_fuel: 总燃油消耗 (kg)
            total_distance: 总航行距离 (海里)
            total_co2: 总 CO2 排放 (kg), 如为 None 则从燃油计算
            year: 计算年份
            
        Returns:
            CIIResult: CII 计算结果
        """
        # 计算 CO2 (如未提供)
        if total_co2 is None:
            cf = self.vessel.fuel_type.emission_factor / 1000.0
            total_co2 = total_fuel * cf
        
        # 运输功 = DWT × 距离 (dwt-mile)
        transport_work = self.vessel.dwt * total_distance
        
        # CII = CO2 / transport work (g CO2 / dwt-mile)
        # 转换：kg → g (×1000)
        attained_cii = (total_co2 * 1000) / transport_work if transport_work > 0 else float('inf')
        
        # 要求 CII
        required_cii = self.get_required_cii(year)
        
        # CII 比值
        cii_ratio = attained_cii / required_cii if required_cii > 0 else float('inf')
        
        # 确定评级
        rating, rating_threshold = self._determine_rating(cii_ratio)
        
        # 合规状态 (C 级或以上为合规)
        compliance_status = rating in [CIIRating.A, CIIRating.B, CIIRating.C]
        
        return CIIResult(
            attained_cii=attained_cii,
            required_cii=required_cii,
            cii_ratio=cii_ratio,
            rating=rating,
            rating_threshold=rating_threshold,
            compliance_status=compliance_status,
            calculation_period=str(year),
            total_fuel=total_fuel,
            total_distance=total_distance,
            total_co2=total_co2,
            transport_work=transport_work,
            calculation_date=datetime.now()
        )
    
    def _determine_rating(self, cii_ratio: float) -> Tuple[CIIRating, float]:
        """根据 CII 比值确定评级.
        
        Args:
            cii_ratio: attained CII / required CII 比值
            
        Returns:
            (评级，评级阈值)
        """
        if cii_ratio <= self.RATING_THRESHOLDS[CIIRating.A]:
            return CIIRating.A, self.RATING_THRESHOLDS[CIIRating.A]
        elif cii_ratio <= self.RATING_THRESHOLDS[CIIRating.B]:
            return CIIRating.B, self.RATING_THRESHOLDS[CIIRating.B]
        elif cii_ratio <= self.RATING_THRESHOLDS[CIIRating.C]:
            return CIIRating.C, self.RATING_THRESHOLDS[CIIRating.C]
        elif cii_ratio <= self.RATING_THRESHOLDS[CIIRating.D]:
            return CIIRating.D, self.RATING_THRESHOLDS[CIIRating.D]
        else:
            return CIIRating.E, self.RATING_THRESHOLDS[CIIRating.D]
    
    def predict_year_end_cii(
        self,
        current_fuel: float,
        current_distance: float,
        current_co2: Optional[float] = None,
        year: int = 2026
    ) -> CIIResult:
        """预测年度结束时的 CII.
        
        基于当前数据和剩余航程预测全年 CII。
        
        Args:
            current_fuel: 当前累计燃油消耗 (kg)
            current_distance: 当前累计航行距离 (海里)
            current_co2: 当前累计 CO2 排放 (kg)
            year: 计算年份
            
        Returns:
            CIIResult: 预测 CII 结果
        """
        # 估算全年数据 (简单线性外推)
        day_of_year = datetime.now().timetuple().tm_yday
        days_remaining = 365 - day_of_year
        
        if day_of_year > 0:
            projected_fuel = current_fuel * (365 / day_of_year)
            projected_distance = current_distance * (365 / day_of_year)
            projected_co2 = (current_co2 or current_fuel * 0.003114) * (365 / day_of_year)
        else:
            projected_fuel = current_fuel
            projected_distance = current_distance
            projected_co2 = current_co2 or current_fuel * 0.003114
        
        return self.calculate_cii(
            total_fuel=projected_fuel,
            total_distance=projected_distance,
            total_co2=projected_co2,
            year=year
        )
    
    def calculate_corrective_action_target(
        self,
        current_cii: CIIResult,
        target_rating: CIIRating = CIIRating.C
    ) -> Dict[str, Any]:
        """计算纠正措施目标.
        
        针对 D/E 级船舶，计算达到目标评级所需的改进。
        
        Args:
            current_cii: 当前 CII 结果
            target_rating: 目标评级 (默认 C 级)
            
        Returns:
            纠正措施目标字典
        """
        target_threshold = self.RATING_THRESHOLDS[target_rating]
        target_cii = current_cii.required_cii * target_threshold
        
        # 需要的 CO2 减排量
        current_co2_g = current_cii.attained_cii * current_cii.transport_work
        target_co2_g = target_cii * current_cii.transport_work
        co2_reduction_g = current_co2_g - target_co2_g
        co2_reduction_kg = co2_reduction_g / 1000
        
        # 需要的燃油减排量
        cf = self.vessel.fuel_type.emission_factor / 1000
        fuel_reduction_kg = co2_reduction_kg / cf if cf > 0 else 0
        
        # 减排百分比
        reduction_percentage = (co2_reduction_g / current_co2_g * 100) if current_co2_g > 0 else 0
        
        return {
            "target_rating": target_rating.value,
            "target_cii": target_cii,
            "co2_reduction_kg": co2_reduction_kg,
            "fuel_reduction_kg": fuel_reduction_kg,
            "reduction_percentage": reduction_percentage,
            "measures_needed": self._suggest_measures_for_reduction(reduction_percentage)
        }
    
    def _suggest_measures_for_reduction(self, reduction_percentage: float) -> List[str]:
        """根据需要的减排百分比建议措施.
        
        Args:
            reduction_percentage: 需要的减排百分比
            
        Returns:
            建议措施列表
        """
        measures = []
        
        if reduction_percentage <= 5:
            measures.extend([
                "优化航速 (慢速航行)",
                "改进航线规划 (气象定线)",
                "加强船体清洁"
            ])
        elif reduction_percentage <= 10:
            measures.extend([
                "优化航速 (慢速航行 10-15%)",
                "螺旋桨抛光或优化",
                "船体防污涂层升级",
                "改进纵倾优化"
            ])
        elif reduction_percentage <= 20:
            measures.extend([
                "显著降低航速 (15-25%)",
                "安装节能装置 (ESD)",
                "考虑轴带发电机",
                "实施废热回收系统"
            ])
        else:
            measures.extend([
                "重大运营调整",
                "考虑替代燃料",
                "船舶改造或更换",
                "评估风力助推系统"
            ])
        
        return measures


# ============================================================================
# SEEMP 管理器
# ============================================================================

