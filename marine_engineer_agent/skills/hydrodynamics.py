"""
船舶水动力学技能模块

基于 NArch 502 Ship Design and Construction 第 11 章 (Parametric Design)
实现船舶阻力、推进、稳性等水动力学计算。

:author: marine_engineer_agent
:version: 1.0.0
:since: 2026-03-10
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import math

# 配置模块日志
logger = logging.getLogger(__name__)

# ============== 物理常数 ==============

WATER_DENSITY_SEAWATER = 1025.0  # kg/m³ (海水)
WATER_DENSITY_FRESHWATER = 1000.0  # kg/m³ (淡水)
GRAVITY = 9.81  # m/s²
AIR_DENSITY = 1.225  # kg/m³


# ============== 船型参数 ==============

def calculate_hull_coefficients(
    length: float,      # 垂线间长 Lpp (m)
    beam: float,        # 型宽 B (m)
    draft: float,       # 吃水 T (m)
    displacement: float # 排水体积 ∇ (m³)
) -> Dict[str, float]:
    """
    计算船型系数
    
    :param length: 垂线间长 (m)
    :param beam: 型宽 (m)
    :param draft: 吃水 (m)
    :param displacement: 排水体积 (m³)
    :return: 船型系数字典
    """
    # 方形系数 (Block Coefficient)
    cb = displacement / (length * beam * draft)
    
    # 水线面系数 (Waterplane Area Coefficient) - 估算
    cw = 0.7 + 0.15 * cb
    
    # 棱形系数 (Prismatic Coefficient) - 估算
    cp = cb / cw
    
    # 中横剖面系数 (Midship Section Coefficient) - 估算
    cm = cb / cp
    
    return {
        "cb": round(cb, 4),
        "cw": round(cw, 4),
        "cp": round(cp, 4),
        "cm": round(cm, 4)
    }


# ============== 阻力计算 ==============

def calculate_froude_number(
    speed: float,       # 航速 (knots)
    length: float       # 垂线间长 (m)
) -> float:
    """
    计算傅汝德数 (Froude Number)
    
    Fn = V / sqrt(g * L)
    
    :param speed: 航速 (knots)
    :param length: 垂线间长 (m)
    :return: 傅汝德数
    """
    speed_ms = speed * 0.5144  # knots → m/s
    fn = speed_ms / math.sqrt(GRAVITY * length)
    return round(fn, 4)


def calculate_reynolds_number(
    speed: float,       # 航速 (knots)
    length: float,      # 垂线间长 (m)
    kinematic_viscosity: float = 1.19e-6  # 海水运动粘性系数 (m²/s)
) -> float:
    """
    计算雷诺数 (Reynolds Number)
    
    Rn = V * L / ν
    
    :param speed: 航速 (knots)
    :param length: 垂线间长 (m)
    :param kinematic_viscosity: 运动粘性系数 (m²/s)
    :return: 雷诺数
    """
    speed_ms = speed * 0.5144
    rn = (speed_ms * length) / kinematic_viscosity
    return round(rn, 2)


def calculate_frictional_resistance(
    speed: float,       # 航速 (knots)
    length: float,      # 垂线间长 (m)
    wetted_area: float, # 湿表面积 (m²)
    water_density: float = WATER_DENSITY_SEAWATER
) -> Dict[str, float]:
    """
    计算摩擦阻力 (Frictional Resistance)
    
    使用 ITTC-1957 公式：
    Cf = 0.075 / (log10(Rn) - 2)²
    Rf = 0.5 * ρ * V² * S * Cf
    
    :param speed: 航速 (knots)
    :param length: 垂线间长 (m)
    :param wetted_area: 湿表面积 (m²)
    :param water_density: 水密度 (kg/m³)
    :return: 摩擦阻力计算结果
    """
    speed_ms = speed * 0.5144
    rn = calculate_reynolds_number(speed, length)
    
    # ITTC-1957 摩擦系数
    cf = 0.075 / ((math.log10(rn) - 2) ** 2)
    
    # 摩擦阻力
    rf = 0.5 * water_density * (speed_ms ** 2) * wetted_area * cf
    
    return {
        "reynolds_number": rn,
        "friction_coefficient": round(cf, 6),
        "frictional_resistance_N": round(rf, 2),
        "frictional_resistance_kN": round(rf / 1000, 2)
    }


def estimate_wetted_area(
    displacement: float,  # 排水体积 (m³)
    length: float,        # 垂线间长 (m)
    draft: float          # 吃水 (m)
) -> float:
    """
    估算湿表面积 (Holtrop 公式)
    
    :param displacement: 排水体积 (m³)
    :param length: 垂线间长 (m)
    :param draft: 吃水 (m)
    :return: 湿表面积 (m²)
    """
    # 简化估算公式
    s = displacement * (2.0 / draft + 1.0 / length)
    return round(s, 2)


def calculate_total_resistance(
    speed: float,       # 航速 (knots)
    length: float,      # 垂线间长 (m)
    beam: float,        # 型宽 (m)
    draft: float,       # 吃水 (m)
    displacement: float,# 排水体积 (m³)
    cb: float           # 方形系数
) -> Dict[str, Any]:
    """
    计算总阻力 (使用简化方法)
    
    :param speed: 航速 (knots)
    :param length: 垂线间长 (m)
    :param beam: 型宽 (m)
    :param draft: 吃水 (m)
    :param displacement: 排水体积 (m³)
    :param cb: 方形系数
    :return: 阻力计算结果
    """
    # 湿表面积估算
    wetted_area = estimate_wetted_area(displacement, length, draft)
    
    # 摩擦阻力
    friction = calculate_frictional_resistance(speed, length, wetted_area)
    
    # 傅汝德数
    fn = calculate_froude_number(speed, length)
    
    # 剩余阻力系数 (简化估算，基于 Fn 和 Cb)
    if fn < 0.15:
        cr = 0.0005  # 低速
    elif fn < 0.25:
        cr = 0.0010  # 中速
    elif fn < 0.35:
        cr = 0.0020  # 高速
    else:
        cr = 0.0035  # 非常高速
    
    # 剩余阻力
    speed_ms = speed * 0.5144
    rr = 0.5 * WATER_DENSITY_SEAWATER * (speed_ms ** 2) * wetted_area * cr
    
    # 空气阻力 (简化)
    ra = 0.5 * AIR_DENSITY * (speed_ms ** 2) * (beam * draft * 0.8) * 0.001
    
    # 总阻力
    rt = friction["frictional_resistance_N"] + rr + ra
    
    return {
        "speed_knots": speed,
        "froude_number": fn,
        "wetted_area_m2": wetted_area,
        "frictional_resistance_N": friction["frictional_resistance_N"],
        "residual_resistance_N": round(rr, 2),
        "air_resistance_N": round(ra, 2),
        "total_resistance_N": round(rt, 2),
        "total_resistance_kN": round(rt / 1000, 2),
        "total_resistance_tf": round(rt / 9806.65, 4)  # 吨力
    }


# ============== 推进计算 ==============

def calculate_effective_power(
    total_resistance: float,  # 总阻力 (N)
    speed: float              # 航速 (knots)
) -> Dict[str, float]:
    """
    计算有效功率 (Effective Power, PE)
    
    PE = RT * V
    
    :param total_resistance: 总阻力 (N)
    :param speed: 航速 (knots)
    :return: 有效功率
    """
    speed_ms = speed * 0.5144
    pe = total_resistance * speed_ms
    
    return {
        "effective_power_W": round(pe, 2),
        "effective_power_kW": round(pe / 1000, 2),
        "effective_power_HP": round(pe / 745.7, 2)
    }


def estimate_propulsive_coefficient(
    cb: float = 0.65  # 方形系数
) -> float:
    """
    估算推进系数 (Propulsive Coefficient, PC)
    
    PC = ηH × ηO × ηR × ηS
    
    :param cb: 方形系数
    :return: 推进系数
    """
    # 典型值范围：0.55 - 0.75
    if cb < 0.55:
        pc = 0.65  # 高速船
    elif cb < 0.70:
        pc = 0.62  # 中速船
    else:
        pc = 0.58  # 低速船 (油轮/散货船)
    
    return pc


def calculate_required_power(
    effective_power: float,  # 有效功率 (kW)
    propulsive_coefficient: float = 0.62
) -> Dict[str, float]:
    """
    计算所需主机功率
    
    :param effective_power: 有效功率 (kW)
    :param propulsive_coefficient: 推进系数
    :return: 所需功率
    """
    # 主机功率
    pb = effective_power / propulsive_coefficient
    
    # 考虑服务余量 (15%)
    pb_service = pb * 1.15
    
    return {
        "brake_power_kW": round(pb, 2),
        "brake_power_HP": round(pb / 0.7457, 2),
        "service_power_kW": round(pb_service, 2),
        "service_power_HP": round(pb_service / 0.7457, 2)
    }


# ============== 稳性计算 ==============

def calculate_initial_gm(
    beam: float,        # 型宽 (m)
    draft: float,       # 吃水 (m)
    kg: float,          # 重心高度 (m)
    cb: float = 0.65    # 方形系数
) -> Dict[str, float]:
    """
    计算初稳性高度 (GM)
    
    GM = KB + BM - KG
    
    :param beam: 型宽 (m)
    :param draft: 吃水 (m)
    :param kg: 重心高度 (m)
    :param cb: 方形系数
    :return: 稳性计算结果
    """
    # 浮心高度 KB (简化公式)
    kb = 0.53 * draft
    
    # 横稳心半径 BM
    # BM = I / V, I ≈ (L * B³ * CW) / 12
    # 简化：BM ≈ B² / (12 * T * CM)
    cm = cb / 0.7  # 估算中横剖面系数
    bm = (beam ** 2) / (12 * draft * cm)
    
    # 稳心高度 KM
    km = kb + bm
    
    # 初稳性高度 GM
    gm = km - kg
    
    return {
        "kb_m": round(kb, 3),
        "bm_m": round(bm, 3),
        "km_m": round(km, 3),
        "kg_m": kg,
        "gm_m": round(gm, 3),
        "status": "✅ 稳定" if gm > 0.15 else "⚠️ 临界" if gm > 0 else "❌ 不稳定"
    }


def check_stability_criteria(
    gm: float,        # GM 值 (m)
    displacement: float  # 排水量 (吨)
) -> Dict[str, Any]:
    """
    检查稳性衡准
    
    :param gm: GM 值 (m)
    :param displacement: 排水量 (吨)
    :return: 稳性检查结果
    """
    criteria = {
        "gm_requirement": gm >= 0.15,
        "gm_good": gm >= 0.30,
        "gm_excellent": gm >= 0.50
    }
    
    if gm < 0:
        status = "❌ 不稳定 - 立即整改"
    elif gm < 0.15:
        status = "⚠️ 临界 - 需要改进"
    elif gm < 0.30:
        status = "✅ 合格 - 满足最低要求"
    elif gm < 0.50:
        status = "✅ 良好 - 正常运营"
    else:
        status = "✅ 优秀 - 稳性充裕"
    
    return {
        "gm_m": gm,
        "criteria": criteria,
        "status": status,
        "recommendation": get_stability_recommendation(gm)
    }


def get_stability_recommendation(gm: float) -> str:
    """获取稳性改进建议"""
    if gm < 0:
        return "降低重心或增加船宽"
    elif gm < 0.15:
        return "减少上层建筑重量或增加压载"
    elif gm < 0.30:
        return "考虑优化载荷分布"
    elif gm < 0.50:
        return "稳性良好，保持当前配置"
    else:
        return "稳性充裕，可适当优化"


# ============== 综合技能函数 ==============

def hydrodynamics_analysis(
    length: float,
    beam: float,
    draft: float,
    displacement: float,
    speed: float,
    kg: Optional[float] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    船舶水动力学综合分析
    
    :param length: 垂线间长 (m)
    :param beam: 型宽 (m)
    :param draft: 吃水 (m)
    :param displacement: 排水体积 (m³)
    :param speed: 航速 (knots)
    :param kg: 重心高度 (m)，可选
    :param config: 配置参数
    :return: 综合分析结果
    """
    logger.info(f"水动力分析：L={length}m, B={beam}m, T={draft}m, V={speed}kn")
    
    result = {
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "ship_parameters": {
            "length_pp_m": length,
            "beam_m": beam,
            "draft_m": draft,
            "displacement_m3": displacement,
            "speed_knots": speed
        },
        "hull_coefficients": {},
        "resistance": {},
        "propulsion": {},
        "stability": {},
        "message": ""
    }
    
    try:
        # 1. 船型系数
        result["hull_coefficients"] = calculate_hull_coefficients(
            length, beam, draft, displacement
        )
        cb = result["hull_coefficients"]["cb"]
        
        # 2. 阻力计算
        result["resistance"] = calculate_total_resistance(
            speed, length, beam, draft, displacement, cb
        )
        
        # 3. 推进计算
        ep = calculate_effective_power(
            result["resistance"]["total_resistance_N"],
            speed
        )
        pc = estimate_propulsive_coefficient(cb)
        result["propulsion"] = {
            **ep,
            "propulsive_coefficient": pc,
            **calculate_required_power(ep["effective_power_kW"], pc)
        }
        
        # 4. 稳性计算 (如果提供 KG)
        if kg:
            gm_result = calculate_initial_gm(beam, draft, kg, cb)
            result["stability"] = {
                **gm_result,
                **check_stability_criteria(gm_result["gm_m"], displacement * 1.025)
            }
        else:
            result["stability"] = {"message": "未提供 KG，无法计算稳性"}
        
        result["success"] = True
        result["message"] = "水动力分析完成"
        
    except Exception as e:
        logger.error(f"水动力分析失败：{e}")
        result["message"] = f"分析失败：{str(e)}"
    
    return result


# ============== 技能注册表 ==============

HYDRO_SKILLS = {
    "hull_coefficients": calculate_hull_coefficients,
    "froude_number": calculate_froude_number,
    "reynolds_number": calculate_reynolds_number,
    "frictional_resistance": calculate_frictional_resistance,
    "total_resistance": calculate_total_resistance,
    "effective_power": calculate_effective_power,
    "required_power": calculate_required_power,
    "initial_gm": calculate_initial_gm,
    "stability_check": check_stability_criteria,
    "hydrodynamics_analysis": hydrodynamics_analysis
}


def get_hydro_skill(skill_name: str):
    """获取水动力学技能函数"""
    return HYDRO_SKILLS.get(skill_name)


def list_hydro_skills() -> List[str]:
    """列出所有可用的水动力学技能"""
    return list(HYDRO_SKILLS.keys())
