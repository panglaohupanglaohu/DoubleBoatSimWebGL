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

