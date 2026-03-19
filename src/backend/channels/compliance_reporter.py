# -*- coding: utf-8 -*-
"""
Compliance Reporter - 合规报告生成
"""

from .efficiency_models import ComplianceReport, VesselInfo, VoyageData, CIIResult, EEXIResult, CIIRating, FuelType, SEEMPMeasure
from .cii_calculator import CIICalculator
from .eexi_calculator import EEXICalculator
from .seemp_manager import SEEMPManager
from .efficiency_advisor import EfficiencyAdvisor
from typing import Optional, Dict, Any, List
from datetime import datetime
import json


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

