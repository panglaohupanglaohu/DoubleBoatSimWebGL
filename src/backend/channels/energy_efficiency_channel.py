# -*- coding: utf-8 -*-
"""
Energy Efficiency Channel - 船舶能效管理与合规监控
"""

from .efficiency_models import (
    CIIRating, VesselType, FuelType, EnergySavingMeasureType, AlarmLevel,
    VesselInfo, VoyageData, EngineData, EEXIResult, CIIResult,
    SEEMPMeasure, EfficiencyRecommendation, ComplianceReport
)
from .eexi_calculator import EEXICalculator
from .cii_calculator import CIICalculator
from .seemp_manager import SEEMPManager
from .efficiency_advisor import EfficiencyAdvisor
from .compliance_reporter import ComplianceReporter
from .marine_base import MarineChannel, ChannelStatus, ChannelPriority
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

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
