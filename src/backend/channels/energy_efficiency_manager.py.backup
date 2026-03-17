# -*- coding: utf-8 -*-
"""
Energy Efficiency Manager Channel — 船舶能效管理与合规监控.

实现 IMO 船舶能效法规 (EEXI/CII/SEEMP) 的计算、监控和报告功能。
支持 NMEA 2000 数据集成、实时 CII 计算、能效优化建议和合规报告生成。

参考标准:
- IMO MARPOL Annex VI (Chapter 4: Energy Efficiency)
- MEPC.346(78) - 2022 SEEMP Guidelines
- MEPC.347(78) - SEEMP Verification Guidelines
- MEPC.385(81) - 2026 CII Reduction Factors
- ISO 19030:2016 - Hull and Propeller Performance Monitoring

核心组件:
- EEXICalculator: EEXI 技术指数计算与合规验证
- CIICalculator: CII 运营碳强度计算与评级
- SEEMPManager: SEEMP Part III 计划管理与实施跟踪
- EfficiencyAdvisor: 能效优化建议与措施推荐
- ComplianceReporter: 合规报告生成与数据导出

作者：CaptainCatamaran (marine_engineer_agent) 🐱⛵
版本：Round 13 - 2026-03-14
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
from .marine_base import MarineChannel, ChannelStatus, ChannelPriority
import math
import json


# ============================================================================
# 枚举类型定义
# ============================================================================

class CIIRating(Enum):
    """CII 能效评级 (IMO MARPOL Annex VI Regulation 28).
    
    评级基于 attained CII 与 required CII 的比值:
    - A: 优秀 (≤0.67 × required CII)
    - B: 良好 (≤0.83 × required CII)
    - C: 中等 (≤1.07 × required CII)
    - D: 较差 (≤1.27 × required CII)
    - E: 差 (>1.27 × required CII)
    
    连续 3 年 D 级或任何 E 级需要 SEEMP 纠正措施计划。
    """
    A = "A"  # 优秀 - 显著优于要求
    B = "B"  # 良好 - 优于要求
    C = "C"  # 中等 - 满足要求
    D = "D"  # 较差 - 接近不合规
    E = "E"  # 差 - 不合规，需要纠正措施


class VesselType(Enum):
    """适用船舶类型 (MARPOL Annex VI Regulation 2.2).
    
    定义 EEXI 和 CII 适用的船舶类型。
    """
    BULK_CARRIER = "Bulk Carrier"  # 散货船
    OIL_TANKER = "Oil Tanker"  # 油轮
    CHEMICAL_TANKER = "Chemical Tanker"  # 化学品船
    CONTAINER_SHIP = "Container Ship"  # 集装箱船
    LNG_CARRIER = "LNG Carrier"  # LNG 运输船
    LPG_CARRIER = "LPG Carrier"  # LPG 运输船
    RO_RO_CARGO = "Ro-Ro Cargo Ship"  # 滚装货船
    RO_RO_PASSENGER = "Ro-Ro Passenger Ship"  # 滚装客船
    PASSENGER_SHIP = "Passenger Ship"  # 客船
    CRUISE_SHIP = "Cruise Ship"  # 邮轮
    GENERAL_CARGO = "General Cargo Ship"  # 杂货船
    REFRIGERATED_CARGO = "Refrigerated Cargo Ship"  # 冷藏船
    COMBINATION_CARRIER = "Combination Carrier"  # 多用途船
    FISHING_VESSEL = "Fishing Vessel"  # 渔船 (可选)
    OFFSHORE_VESSEL = "Offshore Vessel"  # 海工船 (可选)
    OTHER = "Other"  # 其他类型


class FuelType(Enum):
    """燃油类型与 CO2 排放因子 (IMO 2026 Guidelines).
    
    排放因子 (CF) 单位：g CO2 / g fuel
    来源：IMO MEPC.385(81) Annex 7
    """
    HFO = ("Heavy Fuel Oil", 3.114)  # 重油
    MDO = ("Marine Diesel Oil", 3.206)  # 船用柴油
    MGO = ("Marine Gas Oil", 3.206)  # 船用瓦斯油
    LNG = ("Liquefied Natural Gas", 2.751)  # 液化天然气
    LPG = ("Liquefied Petroleum Gas", 3.000)  # 液化石油气
    METHANOL = ("Methanol", 1.375)  # 甲醇
    ETHANOL = ("Ethanol", 1.913)  # 乙醇
    BIODIESEL = ("Biodiesel", 0.0)  # 生物柴油 (视为碳中和)
    HYDROGEN = ("Hydrogen", 0.0)  # 氢气 (零排放)
    AMMONIA = ("Ammonia", 0.0)  # 氨 (零排放)
    ELECTRICITY = ("Electricity", 0.0)  # 电力 (船上零排放)
    
    def __init__(self, display_name: str, emission_factor: float):
        self.display_name = display_name
        self.emission_factor = emission_factor  # g CO2 / g fuel


class EnergySavingMeasureType(Enum):
    """节能措施类型分类."""
    HULL_CLEANING = "Hull Cleaning"  # 船体清洁
    PROPELLER_OPTIMIZATION = "Propeller Optimization"  # 螺旋桨优化
    SPEED_OPTIMIZATION = "Speed Optimization"  # 航速优化
    WEATHER_ROUTING = "Weather Routing"  # 气象定线
    TRIM_OPTIMIZATION = "Trim Optimization"  # 纵倾优化
    AIR_LUBRICATION = "Air Lubrication System"  # 空气润滑系统
    WIND_ASSIST = "Wind-Assisted Propulsion"  # 风力助推
    WASTE_HEAT_RECOVERY = "Waste Heat Recovery"  # 废热回收
    SHAFT_GENERATOR = "Shaft Generator"  # 轴带发电机
    BATTERY_HYBRID = "Battery Hybrid System"  # 电池混合动力
    SOLAR_PANEL = "Solar Panel System"  # 太阳能板
    LED_LIGHTING = "LED Lighting Upgrade"  # LED 照明升级
    HVAC_OPTIMIZATION = "HVAC Optimization"  # 暖通空调优化
    ENGINE_DERATING = "Engine Derating"  # 发动机降功率
    VFD_INSTALLATION = "Variable Frequency Drive"  # 变频驱动


class AlarmLevel(Enum):
    """能效报警级别."""
    INFO = "INFO"  # 信息 - 记录备案
    WARNING = "WARNING"  # 警告 - 需要注意
    ALERT = "ALERT"  # 警报 - 需要行动
    CRITICAL = "CRITICAL"  # 严重 - 立即行动


# ============================================================================
# 数据类定义
# ============================================================================

@dataclass
class VesselInfo:
    """船舶基本信息.
    
    Attributes:
        imo_number: IMO 编号 (7 位数字)
        vessel_name: 船舶名称
        vessel_type: 船舶类型
        dwt: 载重吨 (Deadweight Tonnage)
        gross_tonnage: 总吨位
        length: 船长 (m)
        beam: 船宽 (m)
        draft: 吃水 (m)
        main_engine_power: 主机功率 (kW)
        fuel_type: 主要燃油类型
        built_year: 建造年份
        ice_class: 冰级 (可选)
    """
    imo_number: int
    vessel_name: str
    vessel_type: VesselType
    dwt: float  # 载重吨
    gross_tonnage: float  # 总吨位
    length: float  # 船长 (m)
    beam: float  # 船宽 (m)
    draft: float  # 吃水 (m)
    main_engine_power: float  # 主机功率 (kW)
    fuel_type: FuelType = FuelType.HFO
    built_year: int = 2010
    ice_class: Optional[str] = None


@dataclass
class VoyageData:
    """航次数据.
    
    Attributes:
        voyage_id: 航次编号
        departure_port: 离港
        arrival_port: 到港
        departure_time: 离港时间
        arrival_time: 到港时间
        distance_nm: 航行距离 (海里)
        fuel_consumed: 燃油消耗 (kg)
        fuel_type: 燃油类型
        cargo_weight: 货物重量 (吨)
        average_speed: 平均航速 (knots)
        sea_conditions: 海况描述
    """
    voyage_id: str
    departure_port: str
    arrival_port: str
    departure_time: datetime
    arrival_time: datetime
    distance_nm: float  # 海里
    fuel_consumed: float  # kg
    fuel_type: FuelType = FuelType.HFO
    cargo_weight: Optional[float] = None
    average_speed: Optional[float] = None
    sea_conditions: Optional[str] = None


@dataclass
class EngineData:
    """主机工况数据 (来自 NMEA 2000 PGN).
    
    Attributes:
        timestamp: 数据时间戳
        engine_rpm: 发动机转速 (rpm)
        engine_load: 发动机负载 (%)
        fuel_rate: 燃油消耗率 (kg/h)
        engine_power: 发动机功率 (kW)
        exhaust_temp: 排气温度 (°C)
        cooling_water_temp: 冷却水温度 (°C)
        lube_oil_pressure: 滑油压力 (bar)
        boost_pressure: 增压压力 (bar)
        specific_fuel_consumption: 燃油消耗率 (g/kWh)
    """
    timestamp: datetime
    engine_rpm: float
    engine_load: float  # %
    fuel_rate: float  # kg/h
    engine_power: Optional[float] = None  # kW
    exhaust_temp: Optional[float] = None  # °C
    cooling_water_temp: Optional[float] = None  # °C
    lube_oil_pressure: Optional[float] = None  # bar
    boost_pressure: Optional[float] = None  # bar
    specific_fuel_consumption: Optional[float] = None  # g/kWh


@dataclass
class EEXIResult:
    """EEXI 计算结果.
    
    Attributes:
        attained_eexi: 实际 EEXI 值 (g CO2 / tonne-mile)
        required_eexi: 要求 EEXI 值
        compliance_status: 合规状态 (True/False)
        margin: 合规裕度 (%)
        reference_line: 参考线值
        reduction_factor: 减排因子
        calculation_date: 计算日期
        notes: 备注说明
    """
    attained_eexi: float
    required_eexi: float
    compliance_status: bool
    margin: float  # %
    reference_line: float
    reduction_factor: float
    calculation_date: datetime = field(default_factory=datetime.now)
    notes: Optional[str] = None


@dataclass
class CIIResult:
    """CII 计算结果.
    
    Attributes:
        attained_cii: 实际 CII 值 (g CO2 / dwt-mile)
        required_cii: 要求 CII 值
        cii_ratio: attained/required 比值
        rating: CII 评级 (A-E)
        rating_threshold: 评级阈值
        compliance_status: 合规状态
        calculation_period: 计算周期
        total_fuel: 总燃油消耗 (kg)
        total_distance: 总航行距离 (海里)
        total_co2: 总 CO2 排放 (kg)
        transport_work: 运输功 (dwt-mile)
        calculation_date: 计算日期
    """
    attained_cii: float
    required_cii: float
    cii_ratio: float
    rating: CIIRating
    rating_threshold: float
    compliance_status: bool
    calculation_period: str  # e.g., "2026"
    total_fuel: float  # kg
    total_distance: float  # nm
    total_co2: float  # kg
    transport_work: float  # dwt-mile
    calculation_date: datetime = field(default_factory=datetime.now)


@dataclass
class SEEMPMeasure:
    """SEEMP 能效措施.
    
    Attributes:
        measure_id: 措施编号
        measure_type: 措施类型
        description: 措施描述
        expected_savings: 预期节能 (%)
        implementation_cost: 实施成本 (USD)
        payback_period: 投资回收期 (月)
        implementation_status: 实施状态
        planned_date: 计划实施日期
        actual_date: 实际实施日期
        responsible_person: 负责人
        verification_method: 验证方法
    """
    measure_id: str
    measure_type: EnergySavingMeasureType
    description: str
    expected_savings: float  # %
    implementation_cost: float  # USD
    payback_period: int  # months
    implementation_status: str = "planned"  # planned, in_progress, completed, cancelled
    planned_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    responsible_person: Optional[str] = None
    verification_method: Optional[str] = None


@dataclass
class EfficiencyRecommendation:
    """能效优化建议.
    
    Attributes:
        recommendation_id: 建议编号
        category: 建议类别
        title: 建议标题
        description: 详细描述
        expected_improvement: 预期改善 (%)
        implementation_difficulty: 实施难度 (easy/medium/hard)
        estimated_cost: 估算成本 (USD)
        priority: 优先级 (high/medium/low)
        references: 参考资料
    """
    recommendation_id: str
    category: str
    title: str
    description: str
    expected_improvement: float  # %
    implementation_difficulty: str
    estimated_cost: float  # USD
    priority: str
    references: List[str] = field(default_factory=list)


@dataclass
class ComplianceReport:
    """合规报告.
    
    Attributes:
        report_id: 报告编号
        report_type: 报告类型
        vessel_info: 船舶信息
        reporting_period: 报告周期
        generation_date: 生成日期
        eexi_result: EEXI 结果
        cii_result: CII 结果
        seemp_measures: SEEMP 措施列表
        recommendations: 优化建议
        data_quality: 数据质量评估
        verifier_notes: 验证机构备注
        compliance_status: 整体合规状态
    """
    report_id: str
    report_type: str
    vessel_info: VesselInfo
    reporting_period: str
    generation_date: datetime
    eexi_result: Optional[EEXIResult]
    cii_result: Optional[CIIResult]
    seemp_measures: List[SEEMPMeasure]
    recommendations: List[EfficiencyRecommendation]
    data_quality: str
    verifier_notes: Optional[str]
    compliance_status: bool


# ============================================================================
# EEXI 计算器
# ============================================================================

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

class ComplianceReporter:
    """合规报告生成器.
    
    生成 IMO DCS、EU MRV 等合规报告。
    """
    
    def __init__(self, vessel: VesselInfo):
        """初始化报告生成器.
        
        Args:
            vessel: 船舶基本信息
        """
        self.vessel = vessel
        self.eexi_calculator = EEXICalculator(vessel)
        self.cii_calculator = CIICalculator(vessel)
        self.seemp_manager = SEEMPManager(vessel)
    
    def generate_imodcs_report(
        self,
        voyages: List[VoyageData],
        year: int
    ) -> Dict[str, Any]:
        """生成 IMO DCS (Data Collection System) 报告.
        
        Args:
            voyages: 航次数据
            year: 报告年份
            
        Returns:
            IMO DCS 报告字典
        """
        # 汇总数据
        total_fuel_by_type: Dict[FuelType, float] = {}
        total_distance = 0.0
        total_time_at_sea = 0.0
        
        for voyage in voyages:
            if voyage.departure_time.year != year:
                continue
            
            # 按燃油类型汇总
            if voyage.fuel_type not in total_fuel_by_type:
                total_fuel_by_type[voyage.fuel_type] = 0.0
            total_fuel_by_type[voyage.fuel_type] += voyage.fuel_consumed
            
            total_distance += voyage.distance_nm
            
            # 计算海上时间
            time_at_sea = (voyage.arrival_time - voyage.departure_time).total_seconds() / 3600
            total_time_at_sea += time_at_sea
        
        # 计算 CO2 排放
        total_co2 = sum(
            fuel_kg * ft.emission_factor / 1000
            for ft, fuel_kg in total_fuel_by_type.items()
        )
        
        # 计算运输功和 CII
        cii_result = self.cii_calculator.calculate_cii_from_voyages(voyages, year)
        
        return {
            "report_type": "IMO DCS",
            "version": "2026",
            "vessel_info": {
                "imo_number": self.vessel.imo_number,
                "vessel_name": self.vessel.vessel_name,
                "vessel_type": self.vessel.vessel_type.value,
                "gross_tonnage": self.vessel.gross_tonnage,
                "dwt": self.vessel.dwt
            },
            "reporting_period": str(year),
            "fuel_consumption": {
                ft.display_name: {
                    "mass_kg": fuel_kg,
                    "co2_tonnes": fuel_kg * ft.emission_factor / 1000000
                }
                for ft, fuel_kg in total_fuel_by_type.items()
            },
            "total_co2_emissions_tonnes": total_co2 / 1000,
            "total_distance_nm": total_distance,
            "total_time_at_sea_hours": total_time_at_sea,
            "transport_work_dwt_nm": self.vessel.dwt * total_distance,
            "cii_result": {
                "attained_cii": cii_result.attained_cii,
                "required_cii": cii_result.required_cii,
                "rating": cii_result.rating.value,
                "compliance_status": "Compliant" if cii_result.compliance_status else "Non-compliant"
            },
            "verification_status": "Pending verification",
            "submission_date": datetime.now().isoformat()
        }
    
    def generate_eumrv_report(
        self,
        voyages: List[VoyageData],
        year: int
    ) -> Dict[str, Any]:
        """生成 EU MRV (Monitoring, Reporting, Verification) 报告.
        
        Args:
            voyages: 航次数据
            year: 报告年份
            
        Returns:
            EU MRV 报告字典
        """
        # 筛选 EU 相关航次 (简化：假设所有航次都相关)
        eu_voyages = [v for v in voyages if v.departure_time.year == year]
        
        total_fuel = sum(v.fuel_consumed for v in eu_voyages)
        total_co2 = total_fuel * self.vessel.fuel_type.emission_factor / 1000
        total_distance = sum(v.distance_nm for v in eu_voyages)
        
        return {
            "report_type": "EU MRV",
            "version": "2026",
            "vessel_info": {
                "imo_number": self.vessel.imo_number,
                "vessel_name": self.vessel.vessel_name,
                "company": "TBD"
            },
            "reporting_period": str(year),
            "total_fuel_consumed_tonnes": total_fuel / 1000,
            "total_co2_emissions_tonnes": total_co2 / 1000,
            "total_distance_nm": total_distance,
            "number_of_voyages": len(eu_voyages),
            "verification_status": "Pending verification",
            "submission_deadline": f"{year + 1}-04-30"
        }
    
    def generate_annual_compliance_report(
        self,
        year: int,
        voyages: List[VoyageData],
        eexi_result: Optional[EEXIResult] = None,
        seemp_measures: Optional[List[SEEMPMeasure]] = None
    ) -> ComplianceReport:
        """生成年度合规报告.
        
        Args:
            year: 报告年份
            voyages: 航次数据
            eexi_result: EEXI 结果
            seemp_measures: SEEMP 措施列表
            
        Returns:
            ComplianceReport: 合规报告
        """
        # 计算 CII
        cii_result = self.cii_calculator.calculate_cii_from_voyages(voyages, year)
        
        # 生成建议
        advisor = EfficiencyAdvisor(self.vessel)
        recommendations = advisor.generate_recommendations(cii_result, eexi_result)
        
        # 数据质量评估
        data_quality = "Good" if len(voyages) > 0 else "Insufficient data"
        
        # 整体合规状态
        eexi_compliant = eexi_result.compliance_status if eexi_result else True
        cii_compliant = cii_result.compliance_status
        overall_compliant = eexi_compliant and cii_compliant
        
        return ComplianceReport(
            report_id=f"ACR-{self.vessel.imo_number}-{year}",
            report_type="Annual Compliance Report",
            vessel_info=self.vessel,
            reporting_period=str(year),
            generation_date=datetime.now(),
            eexi_result=eexi_result,
            cii_result=cii_result,
            seemp_measures=seemp_measures or [],
            recommendations=recommendations,
            data_quality=data_quality,
            verifier_notes=None,
            compliance_status=overall_compliant
        )
    
    def export_report_to_json(self, report: ComplianceReport) -> str:
        """导出合规报告为 JSON.
        
        Args:
            report: 合规报告
            
        Returns:
            JSON 字符串
        """
        report_dict = {
            "report_id": report.report_id,
            "report_type": report.report_type,
            "vessel_info": {
                "imo_number": report.vessel_info.imo_number,
                "vessel_name": report.vessel_info.vessel_name,
                "vessel_type": report.vessel_info.vessel_type.value,
                "dwt": report.vessel_info.dwt
            },
            "reporting_period": report.reporting_period,
            "generation_date": report.generation_date.isoformat(),
            "eexi_result": {
                "attained_eexi": report.eexi_result.attained_eexi if report.eexi_result else None,
                "required_eexi": report.eexi_result.required_eexi if report.eexi_result else None,
                "compliance_status": report.eexi_result.compliance_status if report.eexi_result else None,
                "margin": report.eexi_result.margin if report.eexi_result else None
            } if report.eexi_result else None,
            "cii_result": {
                "attained_cii": report.cii_result.attained_cii if report.cii_result else None,
                "required_cii": report.cii_result.required_cii if report.cii_result else None,
                "rating": report.cii_result.rating.value if report.cii_result else None,
                "compliance_status": report.cii_result.compliance_status if report.cii_result else None
            } if report.cii_result else None,
            "seemp_measures_count": len(report.seemp_measures),
            "recommendations_count": len(report.recommendations),
            "data_quality": report.data_quality,
            "compliance_status": report.compliance_status
        }
        
        return json.dumps(report_dict, indent=2, ensure_ascii=False)


# ============================================================================
# Channel 实现
# ============================================================================

class EnergyEfficiencyChannel(MarineChannel):
    """能效管理 Channel - 主入口类.
    
    提供完整的船舶能效管理功能，包括:
    - EEXI 计算与合规验证
    - CII 计算与评级
    - SEEMP 计划管理
    - 能效优化建议
    - 合规报告生成
    
    支持 NMEA 2000 数据集成，实现实时能效监控。
    """
    
    name = "energy_efficiency"
    description = "船舶能效管理 (EEXI/CII/SEEMP)"
    version = "1.0.0"
    priority = ChannelPriority.P0
    dependencies: List[str] = []
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化能效管理器.
        
        Args:
            config: 配置字典，包括船舶信息等
        """
        # 显式调用父类初始化
        MarineChannel.__init__(self)
        self.config = config or {}
        self._config = config or {}  # 同步到父类属性
        self.vessel: Optional[VesselInfo] = None
        self.eexi_calculator: Optional[EEXICalculator] = None
        self.cii_calculator: Optional[CIICalculator] = None
        self.seemp_manager: Optional[SEEMPManager] = None
        self.advisor: Optional[EfficiencyAdvisor] = None
        self.reporter: Optional[ComplianceReporter] = None
        
        if config and "vessel" in config:
            self.set_vessel(config["vessel"])
    
    def set_vessel(self, vessel: VesselInfo):
        """设置船舶信息并初始化计算器.
        
        Args:
            vessel: 船舶基本信息
        """
        self.vessel = vessel
        self.eexi_calculator = EEXICalculator(vessel)
        self.cii_calculator = CIICalculator(vessel)
        self.seemp_manager = SEEMPManager(vessel)
        self.advisor = EfficiencyAdvisor(vessel)
        self.reporter = ComplianceReporter(vessel)
    
    def initialize(self) -> bool:
        """初始化 Channel.
        
        Returns:
            True 如果初始化成功
        """
        try:
            # 验证配置
            is_valid, errors = self.validate_config()
            if not is_valid:
                self._set_health(ChannelStatus.ERROR, f"配置验证失败：{errors}")
                return False
            
            # 检查船舶配置
            if self.vessel is None:
                if self.config and "vessel" in self.config:
                    self.set_vessel(self.config["vessel"])
            
            if self.vessel:
                self._set_health(ChannelStatus.OK, f"已配置：{self.vessel.vessel_name}")
            else:
                self._set_health(ChannelStatus.WARN, "等待船舶配置")
            
            self._initialized = True
            return True
        except Exception as e:
            self._set_health(ChannelStatus.ERROR, str(e))
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取 Channel 当前状态.
        
        Returns:
            状态字典
        """
        status = {
            "name": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "health_message": self._health.message,
            "metrics": {
                "calls_total": self._metrics.calls_total,
                "calls_success": self._metrics.calls_success,
                "calls_failed": self._metrics.calls_failed,
            },
        }
        
        if self.vessel:
            status["vessel"] = {
                "name": self.vessel.vessel_name,
                "imo": self.vessel.imo_number,
                "type": self.vessel.vessel_type.value,
            }
        
        return status
    
    def shutdown(self) -> bool:
        """关闭 Channel，释放资源.
        
        Returns:
            True 如果关闭成功
        """
        try:
            self._initialized = False
            self._set_health(ChannelStatus.OFF, "Shutdown")
            return True
        except Exception:
            return False
    
    def check(self) -> Tuple[str, str]:
        """检查 Channel 是否可用 (MarineChannel 方法).
        
        Returns:
            (状态，消息)
        """
        if not self._initialized:
            return ("off", "Channel not initialized")
        
        if self.vessel is None:
            return ("warn", "需要配置船舶信息")
        
        if self.vessel.dwt <= 0:
            return ("error", "DWT 必须大于 0")
        
        return (self._health.status.value, self._health.message)
    
    # ========== 快捷方法 ==========
    
    def calculate_eexi(
        self,
        installed_power: float,
        sfc: float = 180.0
    ) -> EEXIResult:
        """计算 EEXI.
        
        Args:
            installed_power: 安装功率 (kW)
            sfc: 特定燃油消耗 (g/kWh)
            
        Returns:
            EEXI 结果
        """
        if not self.eexi_calculator:
            raise ValueError("Vessel not configured")
        return self.eexi_calculator.calculate_attained_eexi(installed_power, sfc)
    
    def calculate_cii(
        self,
        total_fuel: float,
        total_distance: float,
        year: int = 2026
    ) -> CIIResult:
        """计算 CII.
        
        Args:
            total_fuel: 总燃油消耗 (kg)
            total_distance: 总航行距离 (海里)
            year: 年份
            
        Returns:
            CII 结果
        """
        if not self.cii_calculator:
            raise ValueError("Vessel not configured")
        return self.cii_calculator.calculate_cii(total_fuel, total_distance, year=year)
    
    def add_seemp_measure(
        self,
        measure_type: EnergySavingMeasureType,
        planned_date: Optional[datetime] = None
    ) -> SEEMPMeasure:
        """添加 SEEMP 措施.
        
        Args:
            measure_type: 措施类型
            planned_date: 计划日期
            
        Returns:
            创建的措施
        """
        if not self.seemp_manager:
            raise ValueError("Vessel not configured")
        return self.seemp_manager.create_measure(measure_type, planned_date=planned_date)
    
    def get_recommendations(self) -> List[EfficiencyRecommendation]:
        """获取能效建议.
        
        Returns:
            建议列表
        """
        if not self.advisor:
            raise ValueError("Vessel not configured")
        return self.advisor.generate_recommendations()
    
    def generate_compliance_report(
        self,
        year: int,
        voyages: List[VoyageData]
    ) -> ComplianceReport:
        """生成合规报告.
        
        Args:
            year: 年份
            voyages: 航次数据
            
        Returns:
            合规报告
        """
        if not self.reporter:
            raise ValueError("Vessel not configured")
        return self.reporter.generate_annual_compliance_report(year, voyages)
    
    def export_seemp_json(self) -> str:
        """导出 SEEMP 为 JSON.
        
        Returns:
            JSON 字符串
        """
        if not self.seemp_manager:
            raise ValueError("Vessel not configured")
        return self.seemp_manager.export_to_json()
    
    def export_imodcs_json(
        self,
        voyages: List[VoyageData],
        year: int
    ) -> str:
        """导出 IMO DCS 报告为 JSON.
        
        Args:
            voyages: 航次数据
            year: 年份
            
        Returns:
            JSON 字符串
        """
        if not self.reporter:
            raise ValueError("Vessel not configured")
        report = self.reporter.generate_imodcs_report(voyages, year)
        return json.dumps(report, indent=2, ensure_ascii=False)


# ============================================================================
# 主函数 (测试用)
# ============================================================================

def main():
    """主函数 - 演示能效管理器功能."""
    print("=" * 60)
    print("船舶能效管理系统 - Round 13 演示")
    print("=" * 60)
    
    # 创建示例船舶
    vessel = VesselInfo(
        imo_number=9876543,
        vessel_name="Ocean Pioneer",
        vessel_type=VesselType.BULK_CARRIER,
        dwt=82000,
        gross_tonnage=43500,
        length=229,
        beam=32,
        draft=14.5,
        main_engine_power=14280,
        fuel_type=FuelType.HFO,
        built_year=2015
    )
    
    print(f"\n🚢 船舶：{vessel.vessel_name}")
    print(f"   IMO: {vessel.imo_number}")
    print(f"   类型：{vessel.vessel_type.value}")
    print(f"   DWT: {vessel.dwt:,} t")
    print(f"   建造：{vessel.built_year}")
    
    # 初始化能效管理器
    manager = EnergyEfficiencyManager({"vessel": vessel})
    
    # 计算 EEXI
    print("\n" + "=" * 60)
    print("📊 EEXI 计算")
    print("=" * 60)
    
    eexi_result = manager.calculate_eexi(installed_power=12000, sfc=175)
    print(f"实际 EEXI: {eexi_result.attained_eexi:.3f} g CO₂/t-nm")
    print(f"要求 EEXI: {eexi_result.required_eexi:.3f} g CO₂/t-nm")
    print(f"合规状态：{'✅ 合规' if eexi_result.compliance_status else '❌ 不合规'}")
    print(f"裕度：{eexi_result.margin:.1f}%")
    if eexi_result.notes:
        print(f"备注：{eexi_result.notes}")
    
    # 计算 CII
    print("\n" + "=" * 60)
    print("📈 CII 计算")
    print("=" * 60)
    
    # 模拟年度数据
    total_fuel = 15000000  # kg
    total_distance = 45000  # nm
    
    cii_result = manager.calculate_cii(total_fuel, total_distance, year=2026)
    print(f"实际 CII: {cii_result.attained_cii:.3f} g CO₂/dwt-nm")
    print(f"要求 CII: {cii_result.required_cii:.3f} g CO₂/dwt-nm")
    print(f"CII 比值：{cii_result.cii_ratio:.3f}")
    print(f"评级：{cii_result.rating.value} ({'合规' if cii_result.compliance_status else '不合规'})")
    print(f"总燃油：{cii_result.total_fuel / 1000:.0f} t")
    print(f"总距离：{cii_result.total_distance:,.0f} nm")
    print(f"总 CO₂: {cii_result.total_co2 / 1000:.0f} t")
    
    # 添加 SEEMP 措施
    print("\n" + "=" * 60)
    print("📋 SEEMP 措施")
    print("=" * 60)
    
    manager.add_seemp_measure(EnergySavingMeasureType.HULL_CLEANING)
    manager.add_seemp_measure(EnergySavingMeasureType.SPEED_OPTIMIZATION)
    manager.add_seemp_measure(EnergySavingMeasureType.WEATHER_ROUTING)
    
    seemp_plan = manager.seemp_manager.get_three_year_plan(2026)
    print(f"三年计划：{seemp_plan['plan_period']}")
    print(f"措施数量：{len(seemp_plan['measures'])}")
    print(f"总投资：${seemp_plan['total_investment']:,.0f}")
    print(f"预期节能：{seemp_plan['total_expected_savings']:.1f}%")
    
    # 获取建议
    print("\n" + "=" * 60)
    print("💡 能效建议")
    print("=" * 60)
    
    recommendations = manager.get_recommendations()
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"{i}. {rec.title}")
        print(f"   预期改善：{rec.expected_improvement:.1f}%")
        print(f"   优先级：{rec.priority}")
    
    # 生成合规报告
    print("\n" + "=" * 60)
    print("📄 合规报告")
    print("=" * 60)
    
    # 创建模拟航次
    voyages = [
        VoyageData(
            voyage_id="V001",
            departure_port="Shanghai",
            arrival_port="Singapore",
            departure_time=datetime(2026, 1, 5),
            arrival_time=datetime(2026, 1, 12),
            distance_nm=2400,
            fuel_consumed=350000,
            fuel_type=FuelType.HFO
        ),
        VoyageData(
            voyage_id="V002",
            departure_port="Singapore",
            arrival_port="Rotterdam",
            departure_time=datetime(2026, 1, 15),
            arrival_time=datetime(2026, 2, 10),
            distance_nm=8500,
            fuel_consumed=1200000,
            fuel_type=FuelType.HFO
        )
    ]
    
    report = manager.generate_compliance_report(2026, voyages)
    print(f"报告 ID: {report.report_id}")
    print(f"数据质量：{report.data_quality}")
    print(f"整体合规：{'✅ 是' if report.compliance_status else '❌ 否'}")
    
    print("\n" + "=" * 60)
    print("✅ Round 13 能效管理 Channel 实现完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
