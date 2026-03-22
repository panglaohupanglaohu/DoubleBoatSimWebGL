"""
船舶推进系统仿真模块
Ship Propulsion System Simulation Module

基于 ITTC 推荐方法和船 - 桨 - 机耦合理论
实现推进效率计算、螺旋桨 - 主机匹配分析

参考：
- ITTC Recommended Procedures 7.5-02-03-01.4
- Marine Propellers and Propulsion (Carlton, 2019)
- 船舶阻力与推进 (2025)
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class PropellerType(Enum):
    """螺旋桨类型"""
    FIXED_PITCH = "fixed_pitch"  # 定距桨
    CONTROLLABLE_PITCH = "controllable_pitch"  # 调距桨
    AZIPOD = "azipod"  # 电力推进
    WATERJET = "waterjet"  # 喷水推进


@dataclass
class ShipMainParticulars:
    """船舶主尺度"""
    length_pp: float  # 垂线间长 (m)
    beam: float  # 型宽 (m)
    draft: float  # 吃水 (m)
    displacement: float  # 排水量 (吨)
    block_coefficient: float  # 方形系数 Cb
    wetted_surface: Optional[float] = None  # 湿表面积 (m²)


@dataclass
class PropellerData:
    """螺旋桨参数"""
    diameter: float  # 直径 (m)
    pitch_ratio: float  # 螺距比 P/D
    blade_count: int  # 叶数
    expanded_area_ratio: float  # 展开面积比 EAR
    propeller_type: PropellerType = PropellerType.FIXED_PITCH
    kq_open_water: Optional[float] = None  # 扭矩系数 (敞水)
    kt_open_water: Optional[float] = None  # 推力系数 (敞水)


@dataclass
class PropulsionAnalysisResult:
    """推进分析结果"""
    # 效率组成
    wake_fraction: float = 0.0  # 伴流分数 w
    thrust_deduction: float = 0.0  # 推力减额 t
    hull_efficiency: float = 1.0  # 船身效率 ηH
    open_water_efficiency: float = 0.0  # 敞水效率 ηO
    relative_rotative_efficiency: float = 1.0  # 相对旋转效率 ηR
    shaft_efficiency: float = 0.98  # 轴系效率 ηS
    propulsive_efficiency: float = 0.0  # 推进效率 ηD
    
    # 功率计算
    effective_power: float = 0.0  # 有效功率 PE (kW)
    thrust_power: float = 0.0  # 推力功率 PT (kW)
    delivered_power: float = 0.0  # 收到功率 PD (kW)
    brake_power: float = 0.0  # 制动功率 PB (kW)
    
    # 性能指标
    advance_coefficient: float = 0.0  # 进速系数 J
    thrust_coefficient: float = 0.0  # 推力系数 KT
    torque_coefficient: float = 0.0  # 扭矩系数 KQ
    cavitation_number: float = 0.0  # 空泡数 σ
    
    # 评估
    propulsive_coefficient: float = 0.0  # 推进系数 PC
    quasi_propulsive_coefficient: float = 0.0  # 准推进系数 QPC
    assessment: str = ""
    recommendations: List[str] = field(default_factory=list)


class PropulsionSystem:
    """
    船舶推进系统仿真类
    
    实现船 - 桨 - 机耦合计算，包括：
    1. 伴流分数计算 (基于船型)
    2. 推力减额计算
    3. 敞水效率估算
    4. 推进效率综合分析
    5. 螺旋桨 - 主机匹配检查
    """
    
    def __init__(self, ship: ShipMainParticulars, propeller: PropellerData):
        """
        初始化推进系统
        
        Args:
            ship: 船舶主尺度
            propeller: 螺旋桨参数
        """
        self.ship = ship
        self.propeller = propeller
        
        # 默认参数
        self.water_density = 1025.0  # 海水密度 (kg/m³)
        self.gravity = 9.81  # 重力加速度 (m/s²)
        self.vapor_pressure = 2337.0  # 水蒸气压力 (Pa)
        
    def calculate_wake_fraction(self, speed_kn: float) -> float:
        """
        计算伴流分数 (Wake Fraction)
        
        基于 Taylor 方法，考虑船型和傅汝德数
        
        Args:
            speed_kn: 航速 (节)
            
        Returns:
            伴流分数 w
        """
        # 航速转换 (节 → m/s)
        speed_ms = speed_kn * 0.5144
        
        # 傅汝德数
        fn = speed_ms / math.sqrt(self.gravity * self.ship.length_pp)
        
        # 基于船型的伴流分数估算 (Taylor 方法)
        cb = self.ship.block_coefficient
        
        # 单桨船经验公式
        if cb < 0.6:
            w = 0.3 * cb + 0.1
        elif cb < 0.75:
            w = 0.25 * cb + 0.14
        else:
            w = 0.2 * cb + 0.2
        
        # 傅汝德数修正
        if fn > 0.3:
            w *= (1.0 - 0.2 * (fn - 0.3))
        
        # 双体船修正 (伴流分数通常较小)
        # 如果是双体船，减少伴流分数
        if hasattr(self.ship, 'hull_spacing') and self.ship.hull_spacing:
            w *= 0.8  # 双体船伴流分数约为单体船的 80%
        
        return max(0.05, min(0.4, w))
    
    def calculate_thrust_deduction(self, speed_kn: float) -> float:
        """
        计算推力减额 (Thrust Deduction Factor)
        
        基于船型和螺旋桨位置
        
        Args:
            speed_kn: 航速 (节)
            
        Returns:
            推力减额 t
        """
        cb = self.ship.block_coefficient
        
        # 经验公式 (基于 Cb)
        if cb < 0.6:
            t = 0.2 * cb + 0.05
        elif cb < 0.75:
            t = 0.18 * cb + 0.07
        else:
            t = 0.15 * cb + 0.1
        
        # 考虑螺旋桨位置 (艉部流动影响)
        # 通常 t ≈ w (伴流分数 ≈ 推力减额)
        w = self.calculate_wake_fraction(speed_kn)
        t = 0.9 * t + 0.1 * w  # 加权平均
        
        return max(0.05, min(0.35, t))
    
    def calculate_hull_efficiency(self, w: float, t: float) -> float:
        """
        计算船身效率 (Hull Efficiency)
        
        ηH = (1 - t) / (1 - w)
        
        Args:
            w: 伴流分数
            t: 推力减额
            
        Returns:
            船身效率 ηH
        """
        if w >= 1.0:
            return 1.0
        
        eta_h = (1.0 - t) / (1.0 - w)
        return max(0.8, min(1.3, eta_h))
    
    def calculate_open_water_efficiency(
        self, 
        advance_coefficient: float,
        kt: float,
        kq: float
    ) -> float:
        """
        计算敞水效率 (Open Water Efficiency)
        
        ηO = (J / 2π) × (KT / KQ)
        
        Args:
            advance_coefficient: 进速系数 J
            kt: 推力系数 KT
            kq: 扭矩系数 KQ
            
        Returns:
            敞水效率 ηO
        """
        if kq <= 0:
            return 0.0
        
        eta_o = (advance_coefficient / (2 * math.pi)) * (kt / kq)
        return max(0.3, min(0.8, eta_o))
    
    def estimate_propeller_coefficients(
        self,
        advance_coefficient: float
    ) -> Tuple[float, float]:
        """
        估算螺旋桨推力系数和扭矩系数
        
        基于 Wageningen B 系列螺旋桨图谱的简化公式
        
        Args:
            advance_coefficient: 进速系数 J
            
        Returns:
            (KT, KQ) 推力和扭矩系数
        """
        # 简化模型：基于典型螺旋桨特性
        # 实际应使用螺旋桨图谱数据
        
        p_d = self.propeller.pitch_ratio
        ear = self.propeller.expanded_area_ratio
        z = self.propeller.blade_count
        
        # 推力系数估算
        kt = 0.5 - 0.4 * advance_coefficient + 0.1 * p_d
        
        # 扭矩系数估算
        kq = 0.08 - 0.05 * advance_coefficient + 0.02 * p_d
        
        # 确保正值
        kt = max(0.1, kt)
        kq = max(0.01, kq)
        
        return kt, kq
    
    def calculate_cavitation_number(
        self,
        speed_kn: float,
        depth: float = 5.0
    ) -> float:
        """
        计算空泡数 (Cavitation Number)
        
        σ = (p - pv) / (0.5 × ρ × V²)
        
        Args:
            speed_kn: 航速 (节)
            depth: 螺旋桨浸深 (m)
            
        Returns:
            空泡数 σ
        """
        speed_ms = speed_kn * 0.5144
        
        # 静水压力 (大气压 + 水压)
        atmospheric_pressure = 101325.0  # Pa
        hydrostatic_pressure = self.water_density * self.gravity * depth
        total_pressure = atmospheric_pressure + hydrostatic_pressure
        
        # 动压
        dynamic_pressure = 0.5 * self.water_density * speed_ms ** 2
        
        if dynamic_pressure <= 0:
            return 10.0  # 静止状态，高空泡数
        
        sigma = (total_pressure - self.vapor_pressure) / dynamic_pressure
        return max(0.1, sigma)
    
    def analyze(
        self,
        speed_kn: float,
        rpm: float,
        effective_power_kw: float
    ) -> PropulsionAnalysisResult:
        """
        推进系统综合分析
        
        Args:
            speed_kn: 航速 (节)
            rpm: 螺旋桨转速 (转/分)
            effective_power_kw: 有效功率 (kW)
            
        Returns:
            推进分析结果
        """
        result = PropulsionAnalysisResult()
        
        # 1. 计算伴流分数和推力减额
        result.wake_fraction = self.calculate_wake_fraction(speed_kn)
        result.thrust_deduction = self.calculate_thrust_deduction(speed_kn)
        
        # 2. 计算船身效率
        result.hull_efficiency = self.calculate_hull_efficiency(
            result.wake_fraction,
            result.thrust_deduction
        )
        
        # 3. 计算进速系数
        speed_ms = speed_kn * 0.5144
        advance_speed = speed_ms * (1.0 - result.wake_fraction)
        n_rps = rpm / 60.0
        
        if n_rps > 0 and self.propeller.diameter > 0:
            result.advance_coefficient = advance_speed / (n_rps * self.propeller.diameter)
        else:
            result.advance_coefficient = 0.0
        
        # 4. 估算螺旋桨系数
        kt, kq = self.estimate_propeller_coefficients(result.advance_coefficient)
        result.thrust_coefficient = kt
        result.torque_coefficient = kq
        
        # 5. 计算敞水效率
        result.open_water_efficiency = self.calculate_open_water_efficiency(
            result.advance_coefficient,
            kt,
            kq
        )
        
        # 6. 相对旋转效率 (通常 0.98-1.02)
        result.relative_rotative_efficiency = 1.0
        
        # 7. 轴系效率 (通常 0.97-0.99)
        result.shaft_efficiency = 0.98
        
        # 8. 推进效率 (准推进系数)
        result.propulsive_efficiency = (
            result.hull_efficiency *
            result.open_water_efficiency *
            result.relative_rotative_efficiency
        )
        
        # 9. 功率计算
        result.effective_power = effective_power_kw
        
        # 推力功率
        result.thrust_power = result.effective_power / (1.0 - result.thrust_deduction)
        
        # 收到功率
        if result.propulsive_efficiency > 0:
            result.delivered_power = result.effective_power / result.propulsive_efficiency
        else:
            result.delivered_power = 0.0
        
        # 制动功率 (考虑轴系效率)
        result.brake_power = result.delivered_power / result.shaft_efficiency
        
        # 10. 空泡数检查
        result.cavitation_number = self.calculate_cavitation_number(speed_kn)
        
        # 11. 推进系数估算
        result.propulsive_coefficient = result.propulsive_efficiency
        result.quasi_propulsive_coefficient = (
            result.open_water_efficiency *
            result.hull_efficiency *
            result.relative_rotative_efficiency
        )
        
        # 12. 评估与建议
        self._assess_performance(result, speed_kn, rpm)
        
        return result
    
    def _assess_performance(
        self,
        result: PropulsionAnalysisResult,
        speed_kn: float,
        rpm: float
    ):
        """评估推进性能并生成建议"""
        assessments = []
        recommendations = []
        
        # 推进效率评估
        if result.propulsive_efficiency >= 0.65:
            assessments.append("推进效率优秀")
        elif result.propulsive_efficiency >= 0.55:
            assessments.append("推进效率良好")
        elif result.propulsive_efficiency >= 0.45:
            assessments.append("推进效率一般")
        else:
            assessments.append("推进效率偏低")
            recommendations.append("考虑优化螺旋桨设计或船型")
        
        # 敞水效率评估
        if result.open_water_efficiency >= 0.65:
            assessments.append("螺旋桨效率高")
        elif result.open_water_efficiency >= 0.55:
            assessments.append("螺旋桨效率正常")
        else:
            assessments.append("螺旋桨效率偏低")
            recommendations.append("检查螺旋桨螺距比或考虑更换高效螺旋桨")
        
        # 空泡风险评估
        if result.cavitation_number < 1.5:
            assessments.append("空泡风险高")
            recommendations.append("降低转速或增加螺旋桨浸深")
        elif result.cavitation_number < 3.0:
            assessments.append("空泡风险中等")
            recommendations.append("监控螺旋桨空泡腐蚀")
        else:
            assessments.append("空泡风险低")
        
        # 伴流分数评估
        if result.wake_fraction > 0.35:
            assessments.append("伴流分数偏高")
            recommendations.append("优化艉部线型以减少伴流不均匀性")
        
        result.assessment = " | ".join(assessments)
        result.recommendations = recommendations
    
    def get_propulsion_map(
        self,
        speed_range: Tuple[float, float, float],
        rpm_max: float = 200
    ) -> List[Dict]:
        """
        生成推进特性图谱
        
        Args:
            speed_range: (min_speed, max_speed, step) 节
            rpm_max: 最大转速
            
        Returns:
            推进特性数据列表
        """
        min_spd, max_spd, step = speed_range
        results = []
        
        for speed in [min_spd + i * step for i in range(int((max_spd - min_spd) / step) + 1)]:
            # 估算所需功率 (立方关系)
            pe_kw = 100 * (speed / 10) ** 3  # 简化模型
            
            # 估算转速 (线性关系)
            rpm = rpm_max * (speed / max_spd) * 0.9
            
            analysis = self.analyze(speed, rpm, pe_kw)
            
            results.append({
                "speed_kn": speed,
                "rpm": rpm,
                "effective_power_kw": pe_kw,
                "brake_power_kw": analysis.brake_power,
                "propulsive_efficiency": analysis.propulsive_efficiency,
                "wake_fraction": analysis.wake_fraction,
                "thrust_deduction": analysis.thrust_deduction,
                "hull_efficiency": analysis.hull_efficiency,
                "open_water_efficiency": analysis.open_water_efficiency,
                "assessment": analysis.assessment
            })
        
        return results
    
    def get_status_summary(self) -> Dict:
        """获取推进系统状态摘要"""
        return {
            "module": "PropulsionSystem",
            "ship_length": self.ship.length_pp,
            "propeller_diameter": self.propeller.diameter,
            "propeller_type": self.propeller.propeller_type.value,
            "calculations_available": [
                "wake_fraction",
                "thrust_deduction",
                "hull_efficiency",
                "open_water_efficiency",
                "propulsive_efficiency",
                "power_breakdown",
                "cavitation_check",
                "propulsion_map"
            ]
        }


# ============================================================================
# API 端点辅助函数
# ============================================================================

def analyze_propulsion(
    ship_data: Dict,
    propeller_data: Dict,
    operating_condition: Dict
) -> Dict:
    """
    推进系统分析 API 辅助函数
    
    Args:
        ship_data: 船舶主尺度数据
        propeller_data: 螺旋桨参数
        operating_condition: 运行工况 (speed_kn, rpm, effective_power_kw)
        
    Returns:
        分析结果字典
    """
    # 创建船舶对象
    ship = ShipMainParticulars(
        length_pp=ship_data.get("length_pp", 100.0),
        beam=ship_data.get("beam", 15.0),
        draft=ship_data.get("draft", 5.0),
        displacement=ship_data.get("displacement", 5000.0),
        block_coefficient=ship_data.get("block_coefficient", 0.65)
    )
    
    # 创建螺旋桨对象
    prop_type = PropellerType(propeller_data.get("type", "fixed_pitch"))
    propeller = PropellerData(
        diameter=propeller_data.get("diameter", 3.0),
        pitch_ratio=propeller_data.get("pitch_ratio", 1.0),
        blade_count=propeller_data.get("blade_count", 4),
        expanded_area_ratio=propeller_data.get("ear", 0.55),
        propeller_type=prop_type
    )
    
    # 创建推进系统
    propulsion = PropulsionSystem(ship, propeller)
    
    # 执行分析
    result = propulsion.analyze(
        speed_kn=operating_condition.get("speed_kn", 15.0),
        rpm=operating_condition.get("rpm", 120.0),
        effective_power_kw=operating_condition.get("effective_power_kw", 1000.0)
    )
    
    # 返回字典格式结果
    return {
        "efficiency_breakdown": {
            "wake_fraction": round(result.wake_fraction, 4),
            "thrust_deduction": round(result.thrust_deduction, 4),
            "hull_efficiency": round(result.hull_efficiency, 4),
            "open_water_efficiency": round(result.open_water_efficiency, 4),
            "relative_rotative_efficiency": round(result.relative_rotative_efficiency, 4),
            "shaft_efficiency": round(result.shaft_efficiency, 4),
            "propulsive_efficiency": round(result.propulsive_efficiency, 4)
        },
        "power_breakdown": {
            "effective_power_kw": round(result.effective_power, 2),
            "thrust_power_kw": round(result.thrust_power, 2),
            "delivered_power_kw": round(result.delivered_power, 2),
            "brake_power_kw": round(result.brake_power, 2)
        },
        "performance_coefficients": {
            "advance_coefficient": round(result.advance_coefficient, 4),
            "thrust_coefficient": round(result.thrust_coefficient, 4),
            "torque_coefficient": round(result.torque_coefficient, 4),
            "cavitation_number": round(result.cavitation_number, 4)
        },
        "assessment": result.assessment,
        "recommendations": result.recommendations
    }


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    # 测试用例：典型货船
    ship = ShipMainParticulars(
        length_pp=150.0,
        beam=25.0,
        draft=8.0,
        displacement=15000.0,
        block_coefficient=0.68
    )
    
    propeller = PropellerData(
        diameter=5.5,
        pitch_ratio=1.0,
        blade_count=5,
        expanded_area_ratio=0.55,
        propeller_type=PropellerType.FIXED_PITCH
    )
    
    propulsion = PropulsionSystem(ship, propeller)
    
    # 设计工况分析
    result = propulsion.analyze(
        speed_kn=15.0,
        rpm=120.0,
        effective_power_kw=3000.0
    )
    
    print("=" * 60)
    print("船舶推进系统分析报告")
    print("=" * 60)
    print(f"\n航速：15.0 节 | 转速：120 RPM | 有效功率：3000 kW")
    print(f"\n【效率分解】")
    print(f"  伴流分数 w:     {result.wake_fraction:.4f}")
    print(f"  推力减额 t:     {result.thrust_deduction:.4f}")
    print(f"  船身效率 ηH:    {result.hull_efficiency:.4f}")
    print(f"  敞水效率 ηO:    {result.open_water_efficiency:.4f}")
    print(f"  推进效率 ηD:    {result.propulsive_efficiency:.4f}")
    print(f"\n【功率分解】")
    print(f"  有效功率 PE:    {result.effective_power:.2f} kW")
    print(f"  收到功率 PD:    {result.delivered_power:.2f} kW")
    print(f"  制动功率 PB:    {result.brake_power:.2f} kW")
    print(f"\n【评估】{result.assessment}")
    if result.recommendations:
        print(f"\n【建议】")
        for rec in result.recommendations:
            print(f"  - {rec}")
    print("=" * 60)
