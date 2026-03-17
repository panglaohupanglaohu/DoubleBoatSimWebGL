# -*- coding: utf-8 -*-
"""
EEXI Calculator - 船舶 EEXI 指数计算器
"""

from .efficiency_models import VesselInfo, EEXIResult, VesselType
from typing import Optional, Dict, Any
import math


class EEXICalculator:
    """EEXI (Energy Efficiency Existing Ship Index) 计算器.
    
    EEXI 是船舶设计能效指标，基于船舶的几何参数和主机功率计算。
    公式：EEXI = (CO2 emissions) / (transport work)
         = (Fuel consumption × CF) / (Capacity × Reference speed)
    
    简化公式 (适用于大多数船型):
    EEXI = (P × CF × SFC) / (Capacity × Vref)
    
    其中:
    - P: 主机功率 (kW)
    - CF: CO2 排放因子 (g CO2 / g fuel)
    - SFC: 特定燃油消耗 (g/kWh)
    - Capacity: 船舶容量 (dwt for cargo ships)
    - Vref: 参考航速 (knots)
    
    参考：IMO MEPC.346(78) Annex 4
    """
    
    # 参考线公式系数 (a, b, c) - 基于船型和尺寸
    REFERENCE_LINE_COEFFICIENTS = {
        VesselType.BULK_CARRIER: {"a": 9617.9, "b": -0.479, "c": 0},
        VesselType.OIL_TANKER: {"a": 1219.0, "b": -0.488, "c": 0},
        VesselType.CHEMICAL_TANKER: {"a": 1384.0, "b": -0.488, "c": 0},
        VesselType.CONTAINER_SHIP: {"a": 174.22, "b": -0.201, "c": 0},
        VesselType.LNG_CARRIER: {"a": 3000.0, "b": -0.5, "c": 0},
        VesselType.LPG_CARRIER: {"a": 2500.0, "b": -0.5, "c": 0},
        VesselType.RO_RO_CARGO: {"a": 5000.0, "b": -0.5, "c": 0},
        VesselType.GENERAL_CARGO: {"a": 2000.0, "b": -0.45, "c": 0},
        VesselType.REFRIGERATED_CARGO: {"a": 3500.0, "b": -0.45, "c": 0},
        VesselType.COMBINATION_CARRIER: {"a": 1219.0, "b": -0.488, "c": 0},
    }
    
    # EEXI 减排因子 (2023 生效)
    REDUCTION_FACTORS = {
        (2014, 2019): 0.0,  # 2014-2019 年建造：无减排要求
        (2020, 2022): 0.0,  # 2020-2022 年建造：无减排要求
        (2023, 2024): 0.0,  # 2023 及以后：按 EEDI Phase 3
    }
    
    def __init__(self, vessel: VesselInfo):
        """初始化 EEXI 计算器.
        
        Args:
            vessel: 船舶基本信息
        """
        self.vessel = vessel
    
    def calculate_reference_speed(self, capacity: float) -> float:
        """计算参考航速 Vref.
        
        基于船舶容量和船型计算参考航速。
        对于无法达到参考航速的船舶，可使用 PTO 功率或简化方法。
        
        Args:
            capacity: 船舶容量 (dwt)
            
        Returns:
            参考航速 (knots)
        """
        # 简化计算：基于船型和容量的经验公式
        if self.vessel.vessel_type == VesselType.CONTAINER_SHIP:
            # 集装箱船：较高航速
            return min(24.0, 18.0 + 0.0001 * capacity)
        elif self.vessel.vessel_type in [VesselType.BULK_CARRIER, VesselType.OIL_TANKER]:
            # 散货船/油轮：中等航速
            return min(18.0, 14.0 + 0.00005 * capacity)
        elif self.vessel.vessel_type in [VesselType.GENERAL_CARGO, VesselType.CHEMICAL_TANKER]:
            # 杂货船/化学品船：较低航速
            return min(16.0, 12.0 + 0.00005 * capacity)
        else:
            # 默认参考航速
            return 14.0
    
    def calculate_reference_line(self, capacity: float) -> float:
        """计算 EEXI 参考线.
        
        参考线公式：Reference line = a × Capacity^(-b) + c
        
        Args:
            capacity: 船舶容量 (dwt)
            
        Returns:
            参考线值 (g CO2 / tonne-mile)
        """
        coeffs = self.REFERENCE_LINE_COEFFICIENTS.get(
            self.vessel.vessel_type,
            {"a": 2000.0, "b": -0.5, "c": 0}
        )
        a, b, c = coeffs["a"], coeffs["b"], coeffs["c"]
        return a * (capacity ** b) + c
    
    def get_reduction_factor(self) -> float:
        """获取 EEXI 减排因子.
        
        基于船舶建造年份确定减排因子。
        
        Returns:
            减排因子 (0.0 - 0.5)
        """
        built_year = self.vessel.built_year
        
        for (start, end), factor in self.REDUCTION_FACTORS.items():
            if start <= built_year <= end:
                return factor
        
        # 2023 年及以后：Phase 3 要求 (30% 减排)
        if built_year >= 2023:
            return 0.30
        
        # 2013-2014 年建造：Phase 2 (20% 减排)
        if 2013 <= built_year < 2014:
            return 0.20
        
        # 2010-2012 年建造：Phase 1 (10% 减排)
        if 2010 <= built_year < 2013:
            return 0.10
        
        # 2010 年以前：无 EEDI 要求，但 EEXI 适用
        return 0.0
    
    def calculate_attained_eexi(
        self,
        installed_power: float,
        specific_fuel_consumption: float = 180.0,
        capacity_utilization: float = 1.0
    ) -> EEXIResult:
        """计算实际 EEXI 值.
        
        Args:
            installed_power: 安装功率 (kW) - 考虑功率限制 (EPL)
            specific_fuel_consumption: 特定燃油消耗 (g/kWh), 默认 180
            capacity_utilization: 容量利用率 (0.0-1.0), 默认 1.0
            
        Returns:
            EEXIResult: EEXI 计算结果
        """
        # 计算参数
        capacity = self.vessel.dwt * capacity_utilization
        vref = self.calculate_reference_speed(capacity)
        reference_line = self.calculate_reference_line(capacity)
        reduction_factor = self.get_reduction_factor()
        
        # 要求 EEXI = 参考线 × (1 - 减排因子)
        required_eexi = reference_line * (1.0 - reduction_factor)
        
        # 实际 EEXI = (P × CF × SFC) / (Capacity × Vref)
        # 单位转换：SFC 从 g/kWh 转换为 kg/kWh (÷1000)
        cf = self.vessel.fuel_type.emission_factor  # g CO2 / g fuel
        sfc_kg = specific_fuel_consumption / 1000.0  # kg/kWh
        
        # EEXI 分子：CO2 排放率 (g/h)
        # P (kW) × SFC (kg/kWh) × CF (g/g) × 1000 (g/kg) = g CO2 / h
        co2_emission_rate = installed_power * sfc_kg * cf * 1000
        
        # EEXI 分母：运输功 (tonne-mile/h)
        # Capacity (tonne) × Vref (nm/h) = tonne-mile/h
        transport_work_rate = capacity * vref
        
        # EEXI = CO2 / transport work (g CO2 / tonne-mile)
        attained_eexi = co2_emission_rate / transport_work_rate if transport_work_rate > 0 else float('inf')
        
        # 合规状态和裕度
        compliance_status = attained_eexi <= required_eexi
        margin = ((required_eexi - attained_eexi) / required_eexi) * 100 if required_eexi > 0 else 0
        
        notes = []
        if not compliance_status:
            notes.append(f"⚠️ 不合规：需要降低功率或实施节能措施")
            # 计算需要的功率限制
            required_power = installed_power * (required_eexi / attained_eexi)
            notes.append(f"💡 建议功率限制：{required_power:.1f} kW (当前：{installed_power:.1f} kW)")
        
        return EEXIResult(
            attained_eexi=attained_eexi,
            required_eexi=required_eexi,
            compliance_status=compliance_status,
            margin=margin,
            reference_line=reference_line,
            reduction_factor=reduction_factor,
            calculation_date=datetime.now(),
            notes="; ".join(notes) if notes else None
        )
    
    def calculate_required_power_for_compliance(
        self,
        specific_fuel_consumption: float = 180.0,
        capacity_utilization: float = 1.0
    ) -> float:
        """计算合规所需的最大功率.
        
        Args:
            specific_fuel_consumption: 特定燃油消耗 (g/kWh)
            capacity_utilization: 容量利用率
            
        Returns:
            最大功率 (kW) 以满足 EEXI 要求
        """
        capacity = self.vessel.dwt * capacity_utilization
        vref = self.calculate_reference_speed(capacity)
        reference_line = self.calculate_reference_line(capacity)
        reduction_factor = self.get_reduction_factor()
        required_eexi = reference_line * (1.0 - reduction_factor)
        
        cf = self.vessel.fuel_type.emission_factor
        sfc_kg = specific_fuel_consumption / 1000.0
        
        # 从 EEXI 公式反推功率:
        # required_eexi = (P × CF × SFC) / (Capacity × Vref)
        # P = (required_eexi × Capacity × Vref) / (CF × SFC)
        max_power = (required_eexi * capacity * vref) / (cf * sfc_kg * 1000)
        
        return max_power


# ============================================================================
# CII 计算器
# ============================================================================

