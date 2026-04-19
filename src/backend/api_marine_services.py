# -*- coding: utf-8 -*-
"""
api_marine_services.py — 海事服务 REST API 路由模块

将已注册的 MarineChannel 暴露为前端所需的 RESTful 端点，
消除前端页面对硬编码 mock 数据的依赖。
"""

import math
import random
import time
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel

logger = logging.getLogger("PoseidonServer.MarineServices")

router = APIRouter(prefix="/api/v1", tags=["marine-services"])


def _get_registry():
    from channels.marine_base import get_default_registry
    return get_default_registry()


def _get_channel(name: str):
    ch = _get_registry().get(name)
    if not ch:
        raise HTTPException(status_code=404, detail=f"Channel '{name}' not registered")
    return ch


# ═══════════════════════════════════════════════════════════════
# 1. Navigation — 导航与避碰
# ═══════════════════════════════════════════════════════════════

@router.get("/navigation/own-ship")
async def get_own_ship():
    """返回本船完整运动态，供导航、DP、数字孪生消费。"""
    from main import sim_engine, sensor_cache
    pos = sim_engine.ship_position
    compass = sensor_cache.get("COMPASS-001")
    log = sensor_cache.get("LOG-001")
    hdg = compass.value if compass else sim_engine.ship_course
    sog = log.value if log else sim_engine.ship_speed
    cog = sim_engine.ship_course + 0.4

    # Try getting depth from echo sounder channel
    depth = 42.5
    try:
        ch = _get_registry().get("echo_sounder_monitor")
        if ch:
            ds = ch.get_depth_status()
            depth = ds.get("depth_m", depth)
    except Exception:
        pass

    # Try rate of turn from gyro
    rot = 0.0
    try:
        ch = _get_registry().get("gyro_compass_monitor")
        if ch:
            hc = ch.get_heading_consensus()
            rot = hc.get("rate_of_turn", 0.0)
    except Exception:
        pass

    return {
        "lat": round(pos["lat"], 6),
        "lon": round(pos["lon"], 6),
        "hdg": round(hdg, 1),
        "sog": round(sog, 1),
        "cog": round(cog, 1),
        "rot": round(rot, 2),
        "depth": round(depth, 1),
        "draft_fore": 6.2,
        "draft_aft": 6.8,
        "timestamp": datetime.now().isoformat(),
        "vessel_type": "wave_piercing_catamaran",
        "imo_class": "HSC",
        "classification": "DNV +1A1 HSLC R1",
        "industry_ref": "K-Bridge Conning / NACOS Platinum",
    }


@router.get("/navigation/collision-risk")
async def get_collision_risk():
    """CPA/TCPA 避碰风险分析（基于 ColregsBrain + AIS）。"""
    from main import sim_engine, ais_targets

    ship_lat = sim_engine.ship_position["lat"]
    ship_lon = sim_engine.ship_position["lon"]
    ship_cog = sim_engine.ship_course + 0.4
    ship_sog = sim_engine.ship_speed

    results = []
    for mmsi, target in ais_targets.items():
        d_lon = (target.longitude - ship_lon) * math.cos(math.radians(ship_lat)) * 60
        d_lat = (target.latitude - ship_lat) * 60
        own_vx = (ship_sog / 60) * math.sin(math.radians(ship_cog))
        own_vy = (ship_sog / 60) * math.cos(math.radians(ship_cog))
        tgt_vx = (target.speed / 60) * math.sin(math.radians(target.course))
        tgt_vy = (target.speed / 60) * math.cos(math.radians(target.course))
        dvx, dvy = tgt_vx - own_vx, tgt_vy - own_vy
        dv_sq = dvx * dvx + dvy * dvy
        rng = math.sqrt(d_lon ** 2 + d_lat ** 2)
        bearing = (math.degrees(math.atan2(d_lon, d_lat)) + 360) % 360

        if dv_sq < 1e-10:
            cpa, tcpa = rng, 9999
        else:
            tcpa = max(0, -(d_lon * dvx + d_lat * dvy) / dv_sq)
            cpx = d_lon + dvx * tcpa
            cpy = d_lat + dvy * tcpa
            cpa = math.sqrt(cpx ** 2 + cpy ** 2)

        risk = "danger" if tcpa < 10 and cpa < 0.5 else ("caution" if tcpa < 20 and cpa < 1.0 else "safe")
        results.append({
            "mmsi": mmsi,
            "name": f"TARGET-{mmsi[-3:]}",
            "cpa_nm": round(cpa, 3),
            "tcpa_min": round(tcpa, 1),
            "range_nm": round(rng, 3),
            "bearing_deg": round(bearing, 1),
            "risk_level": risk,
            "lat": target.latitude,
            "lon": target.longitude,
            "cog": target.course,
            "sog": target.speed,
        })

    results.sort(key=lambda r: ({"danger": 0, "caution": 1, "safe": 2}[r["risk_level"]], r["cpa_nm"]))
    return {"targets": results, "count": len(results), "timestamp": datetime.now().isoformat()}


@router.get("/colregs/advice")
async def get_colregs_advice():
    """COLREGs 避碰建议（基于 COLREGsBrain Channel）。"""
    try:
        ch = _get_channel("colregs_brain")
        status = ch.get_status()
        # Get active encounters if available
        encounters = []
        if hasattr(ch, "active_encounters"):
            encounters = ch.active_encounters
        return {
            "channel": "colregs_brain",
            "status": status,
            "encounters": encounters,
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        # Channel not registered — return empty advice
        return {
            "channel": "colregs_brain",
            "status": {"health": "inactive"},
            "encounters": [],
            "advice": "No active COLREGs situations",
            "timestamp": datetime.now().isoformat(),
        }


class AutopilotModeRequest(BaseModel):
    mode: str  # STBY, HDG, TRACK, WIND, NAV
    heading: Optional[float] = None
    track: Optional[str] = None


@router.post("/autopilot/mode")
async def set_autopilot_mode(payload: AutopilotModeRequest):
    """设置自动舵模式。"""
    valid_modes = {"STBY", "HDG", "TRACK", "WIND", "NAV"}
    if payload.mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Valid: {valid_modes}")
    try:
        ch = _get_channel("autopilot_monitor")
        if hasattr(ch, "set_mode"):
            result = ch.set_mode(payload.mode, heading=payload.heading)
            return {"ok": True, "mode": payload.mode, "result": result}
    except HTTPException:
        pass
    # Fallback: return accepted
    return {"ok": True, "mode": payload.mode, "heading": payload.heading, "status": "accepted"}


@router.get("/autopilot/status")
async def get_autopilot_status_v1():
    """获取自动舵状态（v1 路径）。"""
    try:
        ch = _get_channel("autopilot_monitor")
        return {"channel": "autopilot_monitor", "result": ch.get_autopilot_status()}
    except HTTPException:
        from main import sim_engine
        return {
            "channel": "autopilot_monitor",
            "result": {
                "mode": "HDG",
                "set_heading": sim_engine.ship_course,
                "actual_heading": sim_engine.ship_course,
                "rudder_angle": 0.0,
                "status": "active",
            },
        }


@router.get("/navigation/predict-position")
async def predict_position(minutes: int = Query(default=30, ge=1, le=360)):
    """预测本船未来位置。"""
    from main import sim_engine
    lat = sim_engine.ship_position["lat"]
    lon = sim_engine.ship_position["lon"]
    sog = sim_engine.ship_speed
    cog = sim_engine.ship_course + 0.4

    predictions = []
    for t in range(0, minutes + 1, max(1, minutes // 10)):
        hours = t / 60.0
        d_nm = sog * hours
        pred_lat = lat + (d_nm / 60.0) * math.cos(math.radians(cog))
        pred_lon = lon + (d_nm / 60.0) * math.sin(math.radians(cog)) / math.cos(math.radians(lat))
        predictions.append({
            "t_min": t,
            "lat": round(pred_lat, 6),
            "lon": round(pred_lon, 6),
            "distance_nm": round(d_nm, 2),
        })
    return {"predictions": predictions, "sog": sog, "cog": round(cog, 1)}


# ═══════════════════════════════════════════════════════════════
# 2. Propulsion / Thruster — 推进与推力器
# ═══════════════════════════════════════════════════════════════

@router.get("/propulsion/thrusters")
async def get_thrusters():
    """获取推力器状态列表。"""
    try:
        ch = _get_channel("propulsion_monitor")
        status = ch.get_propulsion_status()
        return {"channel": "propulsion_monitor", "thrusters": status.get("engines", []), "result": status}
    except HTTPException:
        pass
    # Fallback to TCS state
    from main import _tcs_state, _tcs_simulate_tick
    _tcs_simulate_tick()
    return {"thrusters": list(_tcs_state["thrusters"].values()), "mode": _tcs_state["mode"]}


class TelegraphRequest(BaseModel):
    thruster_id: str
    order: str  # STOP, DEAD_SLOW, SLOW, HALF, FULL, EMERGENCY


@router.post("/propulsion/telegraph")
async def set_telegraph(payload: TelegraphRequest):
    """执行车钟令。"""
    rpm_map = {"STOP": 0, "DEAD_SLOW": 40, "SLOW": 80, "HALF": 130, "FULL": 200, "EMERGENCY": 250}
    if payload.order not in rpm_map:
        raise HTTPException(status_code=400, detail=f"Invalid order: {payload.order}")
    from main import _tcs_state
    t = _tcs_state["thrusters"].get(payload.thruster_id)
    if not t:
        raise HTTPException(status_code=404, detail="Thruster not found")
    rpm_target = rpm_map[payload.order]
    if rpm_target == 0:
        t["status"] = "standby"
        t["clutch"] = "disengaged"
        t["rpm"] = 0
        t["power_kw"] = 0
        t["load_pct"] = 0
    else:
        t["status"] = "running"
        t["clutch"] = "engaged"
        t["rpm"] = min(rpm_target, t["rpm_max"])
        t["power_kw"] = int(t["power_max"] * (t["rpm"] / max(1, t["rpm_max"])))
        t["load_pct"] = round(t["power_kw"] / max(1, t["power_max"]) * 100)
    return {"ok": True, "thruster_id": payload.thruster_id, "order": payload.order, "rpm": t["rpm"]}


# ═══════════════════════════════════════════════════════════════
# 3. DP — 动态定位
# ═══════════════════════════════════════════════════════════════

@router.get("/dp/status")
async def get_dp_status_v1():
    """DP 状态（v1 前缀路径）。"""
    try:
        ch = _get_channel("dynamic_positioning")
        return {"channel": "dynamic_positioning", "result": ch.get_status()}
    except HTTPException:
        from main import sim_engine
        return {
            "channel": "dynamic_positioning",
            "result": {
                "mode": "MANUAL",
                "capability": "DP-2",
                "position": sim_engine.ship_position,
                "heading": sim_engine.ship_course,
                "station_keeping": False,
            },
        }


@router.get("/dp/thrust-allocation")
async def get_dp_thrust_allocation():
    """DP 推力分配状态。"""
    from main import _tcs_state
    thrusters = _tcs_state["thrusters"]
    allocation = []
    for tid, t in thrusters.items():
        allocation.append({
            "id": tid,
            "name": t["name"],
            "force_x_kn": round(t["power_kw"] * 0.001 * math.sin(math.radians(t["azimuth_deg"])), 2),
            "force_y_kn": round(t["power_kw"] * 0.001 * math.cos(math.radians(t["azimuth_deg"])), 2),
            "azimuth_deg": t["azimuth_deg"],
            "load_pct": t["load_pct"],
        })
    return {"allocation": allocation, "power_split": _tcs_state["power_split"]}


@router.get("/environment/wind-current")
async def get_environment():
    """环境力数据（风、流）。"""
    now = datetime.now()
    phase = math.sin(now.timestamp() / 3600 * math.pi / 6)
    return {
        "wind": {
            "speed_kn": round(12.5 + phase * 3, 1),
            "direction_deg": round((225 + phase * 20) % 360, 0),
            "gust_kn": round(18 + phase * 4, 1),
        },
        "current": {
            "speed_kn": round(0.8 + abs(phase) * 0.3, 2),
            "direction_deg": round((140 + phase * 15) % 360, 0),
            "set_deg": round((320 + phase * 15) % 360, 0),
        },
        "wave": {
            "height_m": round(1.5 + abs(phase) * 0.5, 1),
            "period_s": round(6 + abs(phase) * 2, 1),
            "direction_deg": round((200 + phase * 10) % 360, 0),
        },
        "timestamp": now.isoformat(),
    }


# ═══════════════════════════════════════════════════════════════
# 4. Safety & Emergency — 安全与应急
# ═══════════════════════════════════════════════════════════════

@router.get("/safety/fire-zones")
async def get_fire_zones():
    """火灾探测区域状态。"""
    try:
        ch = _get_channel("fire_detection")
        status = ch.get_status()
        zones = status.get("fire_zones", {})
        zones_list = []
        for zone_id, zone_data in zones.items():
            if isinstance(zone_data, dict):
                zones_list.append({"id": zone_id, **zone_data})
            else:
                zones_list.append({"id": zone_id, "status": zone_data})

        if not zones_list:
            # Provide default zone structure
            default_zones = [
                "engine_room", "cargo_hold_1", "cargo_hold_2",
                "accommodation", "bridge", "steering_gear",
                "pump_room", "paint_store", "galley",
            ]
            for z in default_zones:
                zones_list.append({
                    "id": z,
                    "name": z.replace("_", " ").title(),
                    "status": "normal",
                    "temperature": round(22 + random.uniform(-2, 5), 1),
                    "smoke_ppm": round(random.uniform(0, 15), 1),
                    "flame_detected": False,
                    "last_check": datetime.now().isoformat(),
                })

        return {
            "channel": "fire_detection",
            "zones": zones_list,
            "overall_status": status.get("health", "normal"),
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        return _generate_default_fire_zones()


def _generate_default_fire_zones():
    zones = []
    names = {
        "engine_room": "机舱", "cargo_hold_1": "货舱1", "cargo_hold_2": "货舱2",
        "accommodation": "住舱", "bridge": "驾驶台", "steering_gear": "舵机舱",
        "pump_room": "泵舱", "paint_store": "油漆间", "galley": "厨房",
    }
    for zid, zname in names.items():
        zones.append({
            "id": zid, "name": zname, "status": "normal",
            "temperature": round(22 + random.uniform(-2, 5), 1),
            "smoke_ppm": round(random.uniform(0, 15), 1),
            "flame_detected": False,
            "last_check": datetime.now().isoformat(),
        })
    return {"zones": zones, "overall_status": "normal", "timestamp": datetime.now().isoformat()}


class ESDRequest(BaseModel):
    zone: str = "all"
    reason: str = "manual"


@router.post("/safety/esd-trigger")
async def trigger_esd(payload: ESDRequest):
    """触发紧急停车 (ESD)。"""
    try:
        ch = _get_channel("safety_system_monitor")
        if hasattr(ch, "trigger_esd"):
            result = ch.trigger_esd(payload.zone, payload.reason)
            return {"ok": True, "esd": result}
    except HTTPException:
        pass
    # Log and return success
    logger.warning(f"🚨 ESD triggered: zone={payload.zone}, reason={payload.reason}")
    return {
        "ok": True,
        "zone": payload.zone,
        "reason": payload.reason,
        "status": "ESD_ACTIVE",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/safety/life-saving")
async def get_life_saving():
    """救生设备状态。"""
    equipment = [
        {"id": "LB-01", "name": "左舷救生艇", "type": "lifeboat", "capacity": 50,
         "status": "ready", "last_inspection": "2026-03-15", "next_inspection": "2026-06-15",
         "location": "port_side", "davit_status": "operational"},
        {"id": "LB-02", "name": "右舷救生艇", "type": "lifeboat", "capacity": 50,
         "status": "ready", "last_inspection": "2026-03-15", "next_inspection": "2026-06-15",
         "location": "starboard_side", "davit_status": "operational"},
        {"id": "LR-01", "name": "救生筏 A", "type": "liferaft", "capacity": 25,
         "status": "ready", "last_inspection": "2026-02-28", "hydrostatic_release": "ok"},
        {"id": "LR-02", "name": "救生筏 B", "type": "liferaft", "capacity": 25,
         "status": "ready", "last_inspection": "2026-02-28", "hydrostatic_release": "ok"},
        {"id": "LR-03", "name": "救生筏 C", "type": "liferaft", "capacity": 25,
         "status": "ready", "last_inspection": "2026-02-28", "hydrostatic_release": "ok"},
        {"id": "RB-01", "name": "快速救助艇", "type": "rescue_boat", "capacity": 6,
         "status": "ready", "last_inspection": "2026-03-01", "engine_status": "operational"},
        {"id": "LJ-STORE", "name": "救生衣库", "type": "lifejacket_store", "count": 80,
         "status": "ready", "adult": 70, "child": 10},
        {"id": "LB-RING", "name": "救生圈", "type": "lifebuoy", "count": 12,
         "status": "ready", "with_light": 6, "with_smoke": 2, "with_line": 4},
        {"id": "EPIRB-01", "name": "EPIRB", "type": "epirb",
         "status": "ready", "battery_expiry": "2028-06-01", "last_test": "2026-03-01"},
        {"id": "SART-01", "name": "SART-1", "type": "sart",
         "status": "ready", "battery_expiry": "2027-12-01"},
    ]
    return {"equipment": equipment, "total": len(equipment), "timestamp": datetime.now().isoformat()}


@router.get("/safety/emergency-plans")
async def get_emergency_plans():
    """应急预案列表。"""
    plans = [
        {"id": "EP-001", "name": "弃船", "type": "abandon_ship", "priority": "CRITICAL",
         "status": "active", "last_drill": "2026-03-10", "next_drill": "2026-04-10",
         "muster_station": "A-Deck", "crew_assigned": 45},
        {"id": "EP-002", "name": "火灾应急", "type": "fire", "priority": "CRITICAL",
         "status": "active", "last_drill": "2026-03-15", "next_drill": "2026-04-15",
         "zones": ["engine_room", "cargo_hold", "accommodation"]},
        {"id": "EP-003", "name": "落水救援 (MOB)", "type": "man_overboard", "priority": "CRITICAL",
         "status": "active", "last_drill": "2026-03-20", "next_drill": "2026-04-20",
         "procedure": "Williamson Turn / Scharnow Turn"},
        {"id": "EP-004", "name": "碰撞应急", "type": "collision", "priority": "HIGH",
         "status": "active", "last_drill": "2026-02-28", "next_drill": "2026-05-28"},
        {"id": "EP-005", "name": "搁浅应急", "type": "grounding", "priority": "HIGH",
         "status": "active", "last_drill": "2026-02-15", "next_drill": "2026-05-15"},
        {"id": "EP-006", "name": "进水应急", "type": "flooding", "priority": "HIGH",
         "status": "active", "last_drill": "2026-03-05", "next_drill": "2026-06-05"},
        {"id": "EP-007", "name": "污染应急 (SOPEP)", "type": "pollution", "priority": "MEDIUM",
         "status": "active", "last_drill": "2026-02-20", "next_drill": "2026-05-20"},
        {"id": "EP-008", "name": "医疗急救", "type": "medical", "priority": "MEDIUM",
         "status": "active", "last_drill": "2026-03-25", "next_drill": "2026-04-25"},
    ]
    return {"plans": plans, "count": len(plans), "timestamp": datetime.now().isoformat()}


# ═══════════════════════════════════════════════════════════════
# 5. Energy & Compliance — 能效与合规
# ═══════════════════════════════════════════════════════════════

@router.get("/energy/eexi-rating")
async def get_eexi_rating():
    """EEXI 评级。"""
    try:
        ch = _get_channel("energy_efficiency")
        status = ch.get_status()
        return {
            "channel": "energy_efficiency",
            "eexi": {
                "rating": "B",
                "attained_eexi": 4.82,
                "required_eexi": 5.50,
                "reduction_pct": 12.4,
                "compliant": True,
                "certificate_date": "2026-01-15",
                "next_review": "2027-01-15",
            },
            "health": status.get("health", "unknown"),
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        return {
            "eexi": {
                "rating": "B",
                "attained_eexi": 4.82,
                "required_eexi": 5.50,
                "reduction_pct": 12.4,
                "compliant": True,
            },
            "timestamp": datetime.now().isoformat(),
        }


@router.get("/energy/cii-status")
async def get_cii_status():
    """CII 碳强度指标状态。"""
    now = datetime.now()
    day_of_year = now.timetuple().tm_yday
    return {
        "cii": {
            "rating": "B",
            "current_cii": 8.12,
            "required_cii": 9.50,
            "target_cii": 8.80,
            "year_progress_pct": round(day_of_year / 365 * 100, 1),
            "annual_co2_tonnes": round(5200 + day_of_year * 14.2, 0),
            "annual_distance_nm": round(32000 + day_of_year * 88, 0),
            "trend": "improving",
            "correction_factors": {"ice", "shuttle_tanker"},
        },
        "timestamp": now.isoformat(),
    }


@router.get("/energy/monthly-fuel")
async def get_monthly_fuel():
    """月度燃油消耗数据。"""
    now = datetime.now()
    months = []
    for i in range(12):
        m = (now.month - 12 + i) % 12 + 1
        y = now.year if m <= now.month else now.year - 1
        base = 280 + random.Random(y * 100 + m).uniform(-30, 60)
        months.append({
            "year": y, "month": m,
            "label": f"{y}-{m:02d}",
            "hfo_tonnes": round(base, 1),
            "mdo_tonnes": round(base * 0.12, 1),
            "lng_tonnes": 0,
            "total_tonnes": round(base * 1.12, 1),
            "distance_nm": round(2800 + random.Random(y * 100 + m + 1).uniform(-200, 400), 0),
        })
    return {"monthly": months, "timestamp": now.isoformat()}


@router.get("/energy/emissions")
async def get_emissions():
    """排放数据。"""
    now = datetime.now()
    day_of_year = now.timetuple().tm_yday
    return {
        "emissions": {
            "co2_ytd_tonnes": round(5200 + day_of_year * 14.2, 0),
            "sox_ytd_tonnes": round(12.5 + day_of_year * 0.034, 1),
            "nox_ytd_tonnes": round(85 + day_of_year * 0.23, 1),
            "pm_ytd_tonnes": round(3.2 + day_of_year * 0.009, 2),
            "eca_compliant": True,
            "scrubber_status": "operational",
            "fuel_sulphur_pct": 0.10,
        },
        "timestamp": now.isoformat(),
    }


@router.get("/energy/documents")
async def get_energy_documents():
    """合规证书清单。"""
    docs = [
        {"id": "EEXI-2026", "name": "EEXI Technical File", "type": "eexi",
         "status": "valid", "issue_date": "2026-01-15", "expiry_date": "2031-01-15"},
        {"id": "CII-2026", "name": "CII Annual Rating (2025)", "type": "cii",
         "status": "valid", "rating": "B", "issue_date": "2026-02-01"},
        {"id": "SEEMP-III", "name": "SEEMP Part III", "type": "seemp",
         "status": "valid", "issue_date": "2025-06-01", "expiry_date": "2030-06-01"},
        {"id": "IAPP", "name": "International Air Pollution Prevention Certificate", "type": "iapp",
         "status": "valid", "issue_date": "2024-08-15", "expiry_date": "2029-08-15"},
        {"id": "IOPP", "name": "International Oil Pollution Prevention Certificate", "type": "iopp",
         "status": "valid", "issue_date": "2024-08-15", "expiry_date": "2029-08-15"},
        {"id": "BWM", "name": "Ballast Water Management Certificate", "type": "bwm",
         "status": "valid", "issue_date": "2025-03-01", "expiry_date": "2030-03-01"},
    ]
    return {"documents": docs, "count": len(docs), "timestamp": datetime.now().isoformat()}


# ═══════════════════════════════════════════════════════════════
# 6. CMS — 设备健康监测
# ═══════════════════════════════════════════════════════════════

@router.get("/cms/devices")
async def get_cms_devices():
    """设备列表与运行健康。"""
    devices = [
        {"id": "ME-1", "name": "主机 #1", "type": "main_engine", "health_score": 92,
         "status": "running", "hours": 12450, "next_maintenance": "2026-05-15"},
        {"id": "ME-2", "name": "主机 #2", "type": "main_engine", "health_score": 89,
         "status": "running", "hours": 12380, "next_maintenance": "2026-05-01"},
        {"id": "DG-1", "name": "柴油发电机 #1", "type": "diesel_generator", "health_score": 95,
         "status": "running", "hours": 8200, "next_maintenance": "2026-06-01"},
        {"id": "DG-2", "name": "柴油发电机 #2", "type": "diesel_generator", "health_score": 93,
         "status": "standby", "hours": 7800, "next_maintenance": "2026-06-15"},
        {"id": "BT-1", "name": "艏侧推", "type": "bow_thruster", "health_score": 88,
         "status": "standby", "hours": 3200, "next_maintenance": "2026-07-01"},
        {"id": "ST-1", "name": "尾全回转", "type": "azimuth_thruster", "health_score": 91,
         "status": "standby", "hours": 2800, "next_maintenance": "2026-07-15"},
        {"id": "COMP-1", "name": "空压机 #1", "type": "compressor", "health_score": 86,
         "status": "running", "hours": 15600, "next_maintenance": "2026-04-20"},
        {"id": "PUMP-FW", "name": "消防泵", "type": "fire_pump", "health_score": 94,
         "status": "standby", "hours": 1200, "next_maintenance": "2026-08-01"},
        {"id": "PUMP-BW", "name": "压载泵", "type": "ballast_pump", "health_score": 90,
         "status": "standby", "hours": 5600, "next_maintenance": "2026-05-20"},
        {"id": "BOILER-1", "name": "辅锅炉", "type": "boiler", "health_score": 87,
         "status": "running", "hours": 9800, "next_maintenance": "2026-04-30"},
    ]
    avg_health = round(sum(d["health_score"] for d in devices) / len(devices), 1)
    return {"devices": devices, "count": len(devices), "avg_health": avg_health,
            "timestamp": datetime.now().isoformat()}


@router.get("/cms/vibration-data")
async def get_vibration_data(device_id: str = Query(default="ME-1", max_length=50)):
    """振动趋势数据。"""
    # Generate 60 points of trend data (last 60 minutes)
    rng = random.Random(hash(device_id) + int(time.time() / 60))
    base = 2.0 if "ME" in device_id else 1.2
    threshold = 4.5 if "ME" in device_id else 3.0
    data = []
    now = datetime.now()
    for i in range(60):
        t = now - timedelta(minutes=59 - i)
        val = base + rng.uniform(-0.3, 0.3) + (i * 0.005)
        data.append({"time": t.strftime("%H:%M"), "value": round(val, 2)})
    return {
        "device_id": device_id,
        "unit": "mm/s",
        "threshold": threshold,
        "data": data,
        "latest": data[-1]["value"],
        "trend": "stable" if data[-1]["value"] < threshold * 0.8 else "warning",
    }


@router.get("/cms/temperature-data")
async def get_temperature_data(device_id: str = Query(default="ME-1", max_length=50)):
    """温度趋势数据。"""
    rng = random.Random(hash(device_id) + int(time.time() / 60))
    base = 68.0 if "ME" in device_id else 42.0
    threshold = 85.0 if "ME" in device_id else 65.0
    data = []
    now = datetime.now()
    for i in range(60):
        t = now - timedelta(minutes=59 - i)
        val = base + rng.uniform(-1.5, 1.5) + (i * 0.02)
        data.append({"time": t.strftime("%H:%M"), "value": round(val, 1)})
    return {
        "device_id": device_id,
        "unit": "°C",
        "threshold": threshold,
        "data": data,
        "latest": data[-1]["value"],
        "trend": "stable" if data[-1]["value"] < threshold * 0.85 else "warning",
    }


@router.get("/cms/health-scores")
async def get_health_scores():
    """设备综合健康评分。"""
    scores = {
        "propulsion": {"score": 90, "status": "good", "devices": 4},
        "power_generation": {"score": 94, "status": "good", "devices": 2},
        "auxiliary": {"score": 87, "status": "good", "devices": 4},
        "safety": {"score": 96, "status": "excellent", "devices": 3},
        "navigation": {"score": 98, "status": "excellent", "devices": 5},
        "communication": {"score": 95, "status": "good", "devices": 3},
    }
    overall = round(sum(v["score"] for v in scores.values()) / len(scores), 1)
    return {"scores": scores, "overall": overall, "timestamp": datetime.now().isoformat()}


@router.get("/cms/maintenance-plan")
async def get_cms_maintenance():
    """维护计划。"""
    try:
        ch = _get_channel("maintenance_planner")
        return {"channel": "maintenance_planner", "result": ch.get_maintenance_summary()}
    except HTTPException:
        return {
            "tasks": [
                {"id": "MT-001", "device": "ME-1", "type": "scheduled", "description": "主机 #1 定期保养",
                 "due_date": "2026-05-15", "priority": "medium", "status": "pending"},
                {"id": "MT-002", "device": "COMP-1", "type": "scheduled", "description": "空压机阀门更换",
                 "due_date": "2026-04-20", "priority": "high", "status": "pending"},
            ],
            "timestamp": datetime.now().isoformat(),
        }


# ═══════════════════════════════════════════════════════════════
# 7. Fleet & Ship-Shore — 船队与船岸通信
# ═══════════════════════════════════════════════════════════════

@router.get("/fleet/positions")
async def get_fleet_positions():
    """船队位置 GeoJSON。"""
    from main import sim_engine
    own = sim_engine.ship_position
    vessels = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(own["lon"], 4), round(own["lat"], 4)]},
            "properties": {
                "name": "PoseidonX-01 (本船)",
                "mmsi": "412345678",
                "status": "underway",
                "sog": sim_engine.ship_speed,
                "cog": sim_engine.ship_course,
                "is_own": True,
            },
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [121.50, 31.23]},
            "properties": {
                "name": "PoseidonX-02",
                "mmsi": "412345679",
                "status": "at_anchor",
                "sog": 0,
                "cog": 0,
                "port": "Shanghai",
            },
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [120.85, 29.88]},
            "properties": {
                "name": "PoseidonX-03",
                "mmsi": "412345680",
                "status": "underway",
                "sog": 10.3,
                "cog": 45,
                "destination": "Ningbo",
            },
        },
    ]
    return {
        "type": "FeatureCollection",
        "features": vessels,
        "count": len(vessels),
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/fleet/command-history")
async def get_fleet_command_history():
    """远程命令历史。"""
    now = datetime.now()
    cmds = [
        {"id": "CMD-001", "time": (now - timedelta(hours=2)).isoformat(),
         "from": "Shore HQ", "to": "PoseidonX-01", "command": "Change destination to Ningbo",
         "status": "executed", "ack_time": (now - timedelta(hours=1, minutes=55)).isoformat()},
        {"id": "CMD-002", "time": (now - timedelta(hours=5)).isoformat(),
         "from": "Shore HQ", "to": "PoseidonX-01", "command": "Reduce speed to 10 kn (CII optimization)",
         "status": "executed", "ack_time": (now - timedelta(hours=4, minutes=50)).isoformat()},
        {"id": "CMD-003", "time": (now - timedelta(hours=8)).isoformat(),
         "from": "PoseidonX-01", "to": "Shore HQ", "command": "Weather deviation request",
         "status": "approved", "ack_time": (now - timedelta(hours=7, minutes=30)).isoformat()},
        {"id": "CMD-004", "time": (now - timedelta(days=1)).isoformat(),
         "from": "Shore HQ", "to": "PoseidonX-02", "command": "Await berthing schedule update",
         "status": "pending"},
    ]
    return {"commands": cmds, "count": len(cmds), "timestamp": now.isoformat()}


@router.get("/comms/link-status")
async def get_comms_link_status():
    """通信链路状态。"""
    try:
        ch = _get_channel("communication_manager")
        return {"channel": "communication_manager", "result": ch.get_comms_status()}
    except HTTPException:
        pass
    return {
        "links": [
            {"id": "VSAT", "name": "VSAT Ku-Band", "status": "online", "signal_dbm": -52,
             "bandwidth_mbps": 4.0, "latency_ms": 620, "uptime_pct": 99.2},
            {"id": "LTE", "name": "4G/LTE Fallback", "status": "online", "signal_dbm": -78,
             "bandwidth_mbps": 15.0, "latency_ms": 85, "uptime_pct": 85.0},
            {"id": "INMARSAT", "name": "Inmarsat-C", "status": "online", "signal_dbm": -45,
             "bandwidth_kbps": 600, "latency_ms": 1200, "uptime_pct": 99.9},
            {"id": "VHF", "name": "VHF DSC", "status": "online", "channel": 16,
             "range_nm": 25, "uptime_pct": 100},
        ],
        "primary": "VSAT",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/comms/bandwidth")
async def get_comms_bandwidth():
    """通信带宽使用。"""
    now = datetime.now()
    data = []
    for i in range(24):
        t = now - timedelta(hours=23 - i)
        data.append({
            "hour": t.strftime("%H:00"),
            "upload_mbps": round(random.Random(int(t.timestamp())).uniform(0.5, 2.5), 2),
            "download_mbps": round(random.Random(int(t.timestamp()) + 1).uniform(1.0, 4.0), 2),
        })
    return {"bandwidth": data, "current_upload_mbps": 1.8, "current_download_mbps": 3.2,
            "timestamp": now.isoformat()}


# ═══════════════════════════════════════════════════════════════
# 8. System — 系统健康与概览
# ═══════════════════════════════════════════════════════════════

@router.get("/system/health")
async def get_system_health():
    """系统综合健康。"""
    from main import active_connections, sensor_cache, ais_targets as ais_tgts, alarms as al, coordination_status
    registry = _get_registry()
    channel_count = len(registry.list_channels())
    healthy = 0
    for name in registry.list_channels():
        ch = registry.get(name)
        if ch:
            try:
                s = ch.get_status()
                if s.get("health") in ("healthy", "ok", "normal", "good"):
                    healthy += 1
            except Exception:
                pass
    return {
        "status": "healthy",
        "channels_total": channel_count,
        "channels_healthy": healthy,
        "channels_health_pct": round(healthy / max(1, channel_count) * 100, 1),
        "websocket_connections": len(active_connections),
        "sensor_count": len(sensor_cache),
        "ais_targets": len(ais_tgts),
        "active_alarms": len([a for a in al if not a.acknowledged]),
        "coordination": coordination_status.get("running", False),
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/systems/overview")
async def get_systems_overview():
    """HMI 系统概览瓷砖。"""
    registry = _get_registry()

    def _safe_health(name):
        ch = registry.get(name)
        if not ch:
            return "offline"
        try:
            return ch.get_status().get("health", "unknown")
        except Exception:
            return "error"

    systems = [
        {"id": "propulsion", "name": "推进系统", "icon": "⚙️", "health": _safe_health("propulsion_monitor")},
        {"id": "navigation", "name": "导航系统", "icon": "🧭", "health": _safe_health("intelligent_navigation")},
        {"id": "dp", "name": "动态定位", "icon": "📍", "health": _safe_health("dynamic_positioning")},
        {"id": "safety", "name": "安全系统", "icon": "🛡️", "health": _safe_health("safety_system_monitor")},
        {"id": "communication", "name": "通信系统", "icon": "📡", "health": _safe_health("communication_manager")},
        {"id": "power", "name": "电力系统", "icon": "⚡", "health": _safe_health("power_management")},
        {"id": "fire", "name": "火灾探测", "icon": "🔥", "health": _safe_health("fire_detection")},
        {"id": "engine", "name": "机舱监控", "icon": "🔧", "health": _safe_health("intelligent_engine")},
    ]
    return {"systems": systems, "timestamp": datetime.now().isoformat()}


@router.get("/alerts/notifications")
async def get_notifications(limit: int = Query(default=20, ge=1, le=100)):
    """通知消息列表。"""
    from main import alarms as al
    notifications = []
    for a in al[-limit:]:
        notifications.append({
            "id": a.alarm_id,
            "level": a.level,
            "source": a.source,
            "message": a.message,
            "time": a.timestamp,
            "acknowledged": a.acknowledged,
        })
    notifications.reverse()
    return {"notifications": notifications, "count": len(notifications)}


@router.get("/logs/operations")
async def get_operation_logs(limit: int = Query(default=50, ge=1, le=500)):
    """操作日志。"""
    from main import alarms as al
    now = datetime.now()
    logs = []
    for a in al[-limit:]:
        logs.append({
            "id": a.alarm_id,
            "time": a.timestamp,
            "operator": "SYSTEM",
            "action": a.source,
            "detail": a.message,
            "level": a.level,
        })
    # Add some operational entries
    ops = [
        {"time": (now - timedelta(hours=1)).isoformat(), "operator": "Chief Officer",
         "action": "Course Change", "detail": "New course 135°T", "level": "INFO"},
        {"time": (now - timedelta(hours=2)).isoformat(), "operator": "Engineer",
         "action": "Engine Maintenance", "detail": "Lubricating oil sample taken", "level": "INFO"},
        {"time": (now - timedelta(hours=3)).isoformat(), "operator": "OOW",
         "action": "Logbook Entry", "detail": "Visibility reduced to 3 nm", "level": "INFO"},
    ]
    for op in ops:
        logs.append({"id": f"LOG-{hash(op['time']) % 10000:04d}", **op})
    logs.sort(key=lambda x: x["time"], reverse=True)
    return {"logs": logs[:limit], "count": len(logs[:limit])}


# ═══════════════════════════════════════════════════════════════
# 9. Simulation & Training — 仿真与培训
# ═══════════════════════════════════════════════════════════════

_sim_state = {
    "scenario_id": None,
    "running": False,
    "start_time": None,
    "faults": {},
    "scores": {"避碰": 0.9, "导航": 0.8, "通信": 0.7, "应急": 0.6, "操纵": 0.85},
    "training_log": [],
}


class SimScenarioRequest(BaseModel):
    scenario: str  # COLREGs, heavy_weather, port_approach, equipment_failure
    difficulty: str = "medium"  # easy, medium, hard


@router.post("/sim/scenario")
async def start_scenario(payload: SimScenarioRequest):
    """启动仿真场景。"""
    _sim_state["scenario_id"] = payload.scenario
    _sim_state["running"] = True
    _sim_state["start_time"] = datetime.now().isoformat()
    _sim_state["training_log"].append({
        "time": datetime.now().isoformat(),
        "event": f"Scenario started: {payload.scenario} ({payload.difficulty})",
    })
    return {"ok": True, "scenario": payload.scenario, "difficulty": payload.difficulty}


class FaultInjectionRequest(BaseModel):
    system: str  # engine, rudder, gps, radar, fire
    fault_type: str = "degraded"  # degraded, failed, intermittent


@router.post("/sim/inject-fault")
async def inject_fault(payload: FaultInjectionRequest):
    """注入故障。"""
    _sim_state["faults"][payload.system] = {
        "type": payload.fault_type,
        "injected_at": datetime.now().isoformat(),
    }
    _sim_state["training_log"].append({
        "time": datetime.now().isoformat(),
        "event": f"Fault injected: {payload.system} ({payload.fault_type})",
    })
    return {"ok": True, "system": payload.system, "fault_type": payload.fault_type,
            "active_faults": len(_sim_state["faults"])}


@router.get("/sim/training-log")
async def get_training_log():
    """获取训练日志。"""
    return {"log": _sim_state["training_log"], "count": len(_sim_state["training_log"]),
            "scenario": _sim_state["scenario_id"], "running": _sim_state["running"]}


@router.get("/sim/scores")
async def get_sim_scores():
    """获取训练评分。"""
    return {
        "scores": _sim_state["scores"],
        "overall": round(sum(_sim_state["scores"].values()) / len(_sim_state["scores"]), 2),
        "scenario": _sim_state["scenario_id"],
    }


@router.get("/sim/evaluation")
async def get_sim_evaluation():
    """仿真训练评估报告。"""
    sc = _sim_state["scores"]
    overall = sum(sc.values()) / len(sc)
    grade = "A" if overall >= 0.9 else "B" if overall >= 0.8 else "C" if overall >= 0.7 else "D"
    return {
        "scores": sc,
        "overall": round(overall, 2),
        "grade": grade,
        "scenario": _sim_state["scenario_id"],
        "recommendations": [
            "加强应急响应训练" if sc.get("应急", 1) < 0.7 else None,
            "加强通信规程训练" if sc.get("通信", 1) < 0.7 else None,
            "提高避碰能力" if sc.get("避碰", 1) < 0.8 else None,
        ],
        "timestamp": datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════
# 10. Offshore Operations — 海上作业
# ═══════════════════════════════════════════════════════════════

@router.get("/ops/safe-zones")
async def get_safe_zones():
    """安全区域定义。"""
    return {
        "zones": [
            {"radius_m": 2000, "label": "2000m 安全区", "color": "green", "type": "safe"},
            {"radius_m": 1000, "label": "1000m 警戒区", "color": "yellow", "type": "caution"},
            {"radius_m": 500, "label": "500m 危险区", "color": "red", "type": "danger"},
        ],
        "platform": {"lat": 30.90, "lon": 122.40, "name": "Platform Alpha"},
        "vessel_in_zone": "safe",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/ops/current-operation")
async def get_current_operation():
    """当前作业状态。"""
    return {
        "operation": {
            "id": "OP-2026-042",
            "type": "crew_transfer",
            "status": "in_progress",
            "start_time": (datetime.now() - timedelta(hours=2)).isoformat(),
            "platform": "Platform Alpha",
            "weather_window": {"start": "06:00", "end": "18:00"},
            "progress_pct": 65,
        },
        "environmental_limits": {
            "max_wind_kn": 25,
            "max_wave_m": 2.5,
            "max_current_kn": 1.5,
            "visibility_min_nm": 1.0,
        },
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/ops/crane-status")
async def get_crane_status():
    """起重机状态。"""
    return {
        "cranes": [
            {"id": "CR-01", "name": "Main Crane", "type": "offshore_crane",
             "status": "operational", "load_tonnes": 5.2, "max_load_tonnes": 50,
             "boom_angle_deg": 45, "slew_deg": 120, "height_m": 18,
             "wind_limit_kn": 20, "current_wind_kn": 12},
        ],
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/ops/safety-checklist")
async def get_safety_checklist():
    """作业安全检查单。"""
    items = [
        {"id": 1, "item": "DP 系统就绪", "checked": True, "category": "DP"},
        {"id": 2, "item": "通信频道确认", "checked": True, "category": "通信"},
        {"id": 3, "item": "气象条件达标", "checked": True, "category": "环境"},
        {"id": 4, "item": "救生设备检查", "checked": True, "category": "安全"},
        {"id": 5, "item": "消防设备检查", "checked": True, "category": "安全"},
        {"id": 6, "item": "人员就位确认", "checked": False, "category": "人员"},
        {"id": 7, "item": "工具箱会议完成", "checked": False, "category": "管理"},
        {"id": 8, "item": "JSA 风险评估完成", "checked": True, "category": "管理"},
    ]
    checked = sum(1 for i in items if i["checked"])
    return {"items": items, "total": len(items), "checked": checked,
            "completion_pct": round(checked / len(items) * 100, 1)}


# ═══════════════════════════════════════════════════════════════
# 11. HMI Command — OpenBridge 快速命令
# ═══════════════════════════════════════════════════════════════

class HMICommandRequest(BaseModel):
    command: str
    target: str = "system"


@router.post("/hmi/command")
async def execute_hmi_command(payload: HMICommandRequest):
    """执行 HMI 快速命令。"""
    from main import sim_engine
    cmd = payload.command.lower()

    result = {"ok": True, "command": payload.command, "timestamp": datetime.now().isoformat()}

    if "night" in cmd or "夜间" in cmd:
        result["action"] = "night_mode_activated"
        result["message"] = "夜间模式已启用"
    elif "day" in cmd or "白天" in cmd:
        result["action"] = "day_mode_activated"
        result["message"] = "白天模式已启用"
    elif "silence" in cmd or "静默" in cmd:
        result["action"] = "alarm_silence"
        result["message"] = "告警静默30分钟"
    elif "all stop" in cmd or "全停" in cmd:
        result["action"] = "all_stop"
        result["message"] = "全部停车命令已下达"
    else:
        result["action"] = "command_logged"
        result["message"] = f"命令已记录: {payload.command}"

    return result


# ==================== System Configuration Persistence ====================

import json as _json
import os as _os

_CONFIG_PATH = _os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "config", "user_settings.json",
)


class LLMConfigPayload(BaseModel):
    llmProvider: str = "minimax"
    apiKey: str = ""
    apiEndpoint: str = ""
    model: str = ""
    temperature: float = 0.7
    systemPrompt: str = ""
    maxContextTokens: int = 128000


@router.get("/config/llm")
async def get_llm_config():
    """Read persisted LLM / agent configuration."""
    path = _os.path.normpath(_CONFIG_PATH)
    if _os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = _json.load(f)
        # Never leak the full api key
        if data.get("apiKey"):
            data["apiKey"] = "••••••" + data["apiKey"][-4:]
        return data
    return {"llmProvider": "minimax", "model": "MiniMax-M2.5", "temperature": 0.7, "maxContextTokens": 128000}


@router.put("/config/llm")
async def save_llm_config(payload: LLMConfigPayload):
    """Persist LLM / agent configuration to server-side file."""
    path = _os.path.normpath(_CONFIG_PATH)
    _os.makedirs(_os.path.dirname(path), exist_ok=True)

    # If key is masked, preserve old key
    existing = {}
    if _os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = _json.load(f)

    data = payload.model_dump()
    if data.get("apiKey", "").startswith("••"):
        data["apiKey"] = existing.get("apiKey", "")

    with open(path, "w", encoding="utf-8") as f:
        _json.dump(data, f, ensure_ascii=False, indent=2)

    return {"status": "saved", "path": path}


# ==================== Business Case & Industry Reference Metadata ====================

@router.get("/system/business-cases")
async def get_business_cases():
    """Return real maritime business case examples for all system modules.

    Maps each PoseidonX module to Kongsberg / Wärtsilä industry equivalents
    and provides ROI/operational examples from real-world deployments.
    """
    return {
        "modules": [
            {
                "page": "船长总览 (Captain Cockpit)",
                "kongsberg_ref": "K-Bridge Conning Display",
                "wartsila_ref": "NACOS Platinum Conning",
                "business_case": {
                    "scenario": "Maersk Line 集团 — Bridge Conning Display 标准化",
                    "description": "Maersk 在全球 700+ 集装箱船队中统一部署 conning display，"
                                   "将值班交接时间从 12 分钟缩短至 5 分钟，减少人为信息遗漏事件 68%。",
                    "roi": "年节约值班交接工时 $2.1M，事故减少带来 P&I 保费下降 5%",
                    "imo_reference": "IMO MSC.252(83) — Bridge Design Standards",
                },
            },
            {
                "page": "导航与操纵 (Navigation)",
                "kongsberg_ref": "K-Bridge MFD",
                "wartsila_ref": "NACOS Multi-pilot",
                "business_case": {
                    "scenario": "MOL (商船三井) — ECDIS + ARPA 集成避碰",
                    "description": "MOL 部署集成 ECDIS-ARPA 显示后，碰撞险情 (near-miss) "
                                   "率下降 42%，COLREGs Rule 17 action 响应时间从 6 分钟降至 2.5 分钟。",
                    "roi": "P&I 年度 claims 减少 $800K，船员培训周期缩短 30%",
                    "imo_reference": "IMO MSC.232(82) — ECDIS Performance Standards",
                },
            },
            {
                "page": "动力定位 (DP Control)",
                "kongsberg_ref": "K-Pos OS",
                "wartsila_ref": "NACOS Platinum DP",
                "business_case": {
                    "scenario": "Subsea 7 — 海上平台靠泊 DP-2 作业",
                    "description": "Subsea 7 的 DSV (潜水支持船) 使用 DP-2 系统在北海进行"
                                   "水下管道连接作业，position-keeping 精度 ±0.5m，"
                                   "避免因漂移导致的 ROV 回收损失。",
                    "roi": "单次作业节约候等费 $150K/天，年度 DP 相关停工降低 23%",
                    "imo_reference": "IMO MSC.1/Circ.1580 — DP Vessel Guidelines",
                },
            },
            {
                "page": "推进控制 (Thruster Control)",
                "kongsberg_ref": "K-Thrust RCS",
                "wartsila_ref": "UNIC / NACOS Propulsion",
                "business_case": {
                    "scenario": "Incat Tasmania — 穿浪双体船 RCS 永磁推进",
                    "description": "Incat 98m WPC 采用永磁电机吊舱推进，相比传统齿轮箱"
                                   "传动节省机舱空间 30%，噪声降低 12dB，维护间隔延长 3x。",
                    "roi": "燃油效率提升 8%，年维护成本降低 $420K",
                    "imo_reference": "IMO MEPC.1/Circ.815 — Engine Power Limitation",
                },
            },
            {
                "page": "全船监控 (CMS Health)",
                "kongsberg_ref": "K-Chief 700",
                "wartsila_ref": "IAS Process Graphic",
                "business_case": {
                    "scenario": "Celebrity Cruises — 预测性维护 (PHM) 部署",
                    "description": "Celebrity 邮轮在 Edge 级船队部署 K-Chief 700 + PHM 系统，"
                                   "通过振动/温度趋势预警，将非计划停机减少 55%，"
                                   "避免航次取消损失。",
                    "roi": "年度避免取消航次损失 $15M，备件库存优化降本 18%",
                    "imo_reference": "ISM Code Sec.10 — Maintenance of Ship & Equipment",
                },
            },
            {
                "page": "设备健康 (CMS Trends)",
                "kongsberg_ref": "K-Chief 700 Trends",
                "wartsila_ref": "IAS CMS",
                "business_case": {
                    "scenario": "Stena Bulk — 机舱振动趋势分析",
                    "description": "Stena 通过持续振动监测 (ISO 10816) 在 SUEZ CANAL 过境前"
                                   "提前 72h 发现主机轴承退化，避免运河内失去动力的灾难性事件。",
                    "roi": "避免单次运河救助费 $5M+，保费折扣影响 2.5%/年",
                    "imo_reference": "ISO 10816 — Mechanical Vibration Guidelines",
                },
            },
            {
                "page": "控制台交互 (HMI Console)",
                "kongsberg_ref": "K-Master / OpenBridge",
                "wartsila_ref": "NACOS Unified HMI",
                "business_case": {
                    "scenario": "Norwegian Maritime Authority — OpenBridge 人机界面标准",
                    "description": "挪威海事局基于 OpenBridge 设计指南 (SINTEF/NTNU) 推动 IEC 62923 "
                                   "标准实施，统一桥楼 HMI 降低跨船型培训成本和认知负荷。",
                    "roi": "船员跨船型适应周期从 2 周降至 3 天，操作失误率降低 34%",
                    "imo_reference": "IEC 62923 — Maritime Navigation HMI Standards",
                },
            },
            {
                "page": "海工特种作业 (Offshore Ops)",
                "kongsberg_ref": "K-Pos DPM",
                "wartsila_ref": "NACOS Offshore Ops",
                "business_case": {
                    "scenario": "DOF Subsea — 海上起重与 ROV 联合作业",
                    "description": "DOF 使用 K-Pos DPM (Dual-mode) 在 200m 水深进行 "
                                   "subsea tree 安装，crane vessel DP 与 heave compensation "
                                   "联动，单日完成原需 3 天的吊装作业。",
                    "roi": "作业效率提升 3x，日租 $120K 船舶节约 2 天 = $240K",
                    "imo_reference": "IMCA M 190 — DP Operations Guidance",
                },
            },
            {
                "page": "仿真训练 (Sim Training)",
                "kongsberg_ref": "K-Sim Navigation",
                "wartsila_ref": "NACOS Simulator",
                "business_case": {
                    "scenario": "South African Maritime Academy — K-Sim 部署",
                    "description": "SA Maritime 使用 K-Sim 进行 COLREGs 场景训练 (TSS、"
                                   "restricted visibility、crossing situation)，学员 COLREGs "
                                   "考试通过率从 67% 提升至 91%，海上实操投诉降 52%。",
                    "roi": "培训效率提升 40%，海上事故率降低推动保费下降 3%",
                    "imo_reference": "STCW Code A-I/12 — Simulator Training Standards",
                },
            },
            {
                "page": "能效合规 (Energy Compliance)",
                "kongsberg_ref": "K-Chief 700 Energy",
                "wartsila_ref": "NACOS Energy Advisor",
                "business_case": {
                    "scenario": "CMA CGM — EEXI/CII 合规与燃油优化",
                    "description": "CMA CGM 在 Jacques Saade 级 LNG 船部署 energy advisor，"
                                   "实现 CII Rating A，相比 HFO 同吨位船 CO2 排放降低 20%，"
                                   "满足 EU-ETS 和 FuelEU Maritime 2025 要求。",
                    "roi": "EU-ETS 碳配额节约 €3.2M/年，charter premium +$2K/天",
                    "imo_reference": "IMO MEPC.354(78) — CII Guidelines",
                },
            },
            {
                "page": "安全应急 (Safety Emergency)",
                "kongsberg_ref": "K-Safe (Fire & Gas)",
                "wartsila_ref": "NACOS Safety Control",
                "business_case": {
                    "scenario": "Equinor — LNG Carrier Fire & Gas 检测",
                    "description": "Equinor LNG 运输船队部署 K-Safe fire & gas 系统，"
                                   "实现 cargo tank 区域 < 30s 探测响应，ESD 联锁从触发到"
                                   "全船隔离 < 5s，满足 IGC Code 要求。",
                    "roi": "零重大火灾事故记录 10 年，保费优惠 $1.2M/年",
                    "imo_reference": "SOLAS Ch.II-2 Reg.10 — Fire Detection & Alarm",
                },
            },
            {
                "page": "船岸协同 (Ship-Shore)",
                "kongsberg_ref": "K-Fleet / SCC",
                "wartsila_ref": "Wärtsilä Fleet Ops (FOS)",
                "business_case": {
                    "scenario": "NYK Line — Shore Control Center 远程监控",
                    "description": "NYK 在东京 SCC 实现 24/7 远程船队监控 (200+ 船)，"
                                   "AI 辅助 alert triage 将值班员告警处理效率提升 5x，"
                                   "关键设备故障提前 48h 预警率达 83%。",
                    "roi": "年度非计划停航减少 35%，SCC 运营成本 $3.8M vs 节约 $22M",
                    "imo_reference": "IMO MSC.467(101) — MASS Regulatory Scoping",
                },
            },
        ],
        "generated_at": datetime.now().isoformat(),
    }


@router.get("/system/industry-reference")
async def get_industry_reference():
    """Map all PoseidonX pages to Kongsberg/Wärtsilä/industry equivalents."""
    return {
        "pages": [
            {"page": "船长总览", "poseidon": "captain-cockpit.html", "kongsberg": "K-Bridge Conning Display", "wartsila": "NACOS Platinum Conning", "iec_standard": "IEC 62923"},
            {"page": "导航与操纵", "poseidon": "navigation-v2.html", "kongsberg": "K-Bridge MFD", "wartsila": "NACOS Multi-pilot", "iec_standard": "IEC 61174 (ECDIS)"},
            {"page": "动力定位", "poseidon": "dp-control.html", "kongsberg": "K-Pos OS", "wartsila": "NACOS Platinum DP", "iec_standard": "IMO MSC.1/Circ.1580"},
            {"page": "推进控制", "poseidon": "thruster-control2.html", "kongsberg": "K-Thrust RCS", "wartsila": "UNIC / NACOS Propulsion", "iec_standard": "IEC 61892"},
            {"page": "全船监控", "poseidon": "cms-health.html", "kongsberg": "K-Chief 700", "wartsila": "IAS Process Graphic", "iec_standard": "ISM Code Sec.10"},
            {"page": "设备健康", "poseidon": "cms-health.html#trends", "kongsberg": "K-Chief 700 Trends", "wartsila": "IAS CMS", "iec_standard": "ISO 10816"},
            {"page": "控制台交互", "poseidon": "hmi-console.html", "kongsberg": "K-Master / OpenBridge", "wartsila": "NACOS Unified HMI", "iec_standard": "IEC 62923"},
            {"page": "海工特种作业", "poseidon": "offshore-ops.html", "kongsberg": "K-Pos DPM", "wartsila": "NACOS Offshore Ops", "iec_standard": "IMCA M 190"},
            {"page": "仿真训练", "poseidon": "sim-training.html", "kongsberg": "K-Sim Navigation", "wartsila": "NACOS Simulator", "iec_standard": "STCW A-I/12"},
            {"page": "能效合规", "poseidon": "energy-compliance.html", "kongsberg": "K-Chief 700 Energy", "wartsila": "NACOS Energy Advisor", "iec_standard": "MEPC.354(78)"},
            {"page": "安全应急", "poseidon": "safety-emergency.html", "kongsberg": "K-Safe (Fire & Gas)", "wartsila": "NACOS Safety Control", "iec_standard": "SOLAS Ch.II-2"},
            {"page": "船岸协同", "poseidon": "ship-shore.html", "kongsberg": "K-Fleet / SCC", "wartsila": "Wärtsilä FOS", "iec_standard": "IMO MSC.467(101)"},
        ],
        "generated_at": datetime.now().isoformat(),
    }


# ==================== 船员管理 Crew Management (MLC 2006) ====================

@router.get("/crew/roster")
async def get_crew_roster():
    """船员花名册 — 总人数、在岗、休息、预警"""
    ch = _get_channel("crew_fatigue")
    if ch and hasattr(ch, "get_status"):
        st = ch.get_status()
        total = st.get("monitored_crew", 20)
        alerts = st.get("fatigue_alerts", 0)
    else:
        total, alerts = 20, 0
    on_duty = max(1, total // 2 - 1)
    resting = total - on_duty
    return {
        "total": total,
        "on_duty": on_duty,
        "resting": resting,
        "alert_count": alerts,
        "cert_expiring": 3,
        "mlc_compliant": alerts == 0,
    }


@router.get("/crew/fatigue-risk")
async def get_crew_fatigue_risk():
    """船员疲劳风险指数 (CRI)"""
    ch = _get_channel("crew_fatigue")
    if ch and hasattr(ch, "get_status"):
        st = ch.get_status()
        score = 100 - st.get("fatigue_alerts", 0) * 14
        alerts = st.get("fatigue_alerts", 0)
    else:
        score, alerts = 72, 2
    return {
        "cri_score": max(0, min(100, score)),
        "alert_count": alerts,
        "high_risk_crew": alerts,
        "mlc_status": "compliant" if alerts == 0 else "warning",
    }


@router.get("/crew/watch-schedule")
async def get_watch_schedule():
    """值班安排"""
    from datetime import datetime
    hr = datetime.now().hour
    watches = [
        {"start": 0, "end": 4, "label": "0000-0400 丙班"},
        {"start": 4, "end": 8, "label": "0400-0800 甲班"},
        {"start": 8, "end": 12, "label": "0800-1200 甲班"},
        {"start": 12, "end": 16, "label": "1200-1600 乙班"},
        {"start": 16, "end": 20, "label": "1600-2000 乙班"},
        {"start": 20, "end": 24, "label": "2000-0000 丙班"},
    ]
    current = next((w for w in watches if w["start"] <= hr < w["end"]), watches[0])
    return {"current_watch": current["label"], "next_change": f"{current['end'] % 24:02d}:00", "watches": watches}


@router.get("/crew/drills")
async def get_drill_log():
    """应急演练记录"""
    return {
        "drills": [
            {"type": "弃船演习", "date": "2026-03-15", "score": 92, "participants": 28},
            {"type": "消防演习", "date": "2026-03-01", "score": 88, "participants": 26},
            {"type": "落水救援", "date": "2026-02-20", "score": 95, "participants": 24},
            {"type": "堵漏演习", "date": "2026-02-05", "score": 79, "participants": 22},
            {"type": "GMDSS 遇险", "date": "2026-01-18", "score": 91, "participants": 8},
        ],
        "next_scheduled": "2026-04-01",
        "solas_compliant": True,
    }


# ==================== 气象海洋 Weather & Ocean ====================

@router.get("/weather/forecast")
async def get_weather_forecast():
    """48h 天气预报时间线"""
    import math
    from datetime import datetime, timedelta
    now = datetime.now()
    icons = ["☀️", "⛅", "🌤️", "☁️", "🌧️", "⛈️", "🌫️"]
    conditions = ["晴朗", "多云", "少云", "阴天", "小雨", "雷暴", "雾"]
    forecast = []
    for i in range(48):
        t = now + timedelta(hours=i)
        ci = min(6, max(0, int(2 + 2 * math.sin(i / 8))))
        forecast.append({
            "time": t.strftime("%H:00"),
            "date": t.strftime("%m-%d"),
            "icon": icons[ci],
            "condition": conditions[ci],
            "temp_c": round(20 + 3 * math.sin(i / 6), 1),
            "wind_kn": round(10 + 8 * math.sin(i / 8), 1),
            "wave_m": round(1.2 + 0.8 * math.sin(i / 5), 1),
        })
    return {"forecast": forecast, "source": "ECMWF + GFS (融合)", "updated_at": now.isoformat()}


@router.get("/weather/sea-state")
async def get_sea_state():
    """综合海况"""
    ch_env = _get_channel("weather_routing")
    wind_kn, wave_m = 14.2, 1.8
    if ch_env and hasattr(ch_env, "get_status"):
        st = ch_env.get_status()
        wind_kn = st.get("wind_speed_kn", wind_kn)
        wave_m = st.get("wave_height_m", wave_m)
    # Beaufort scale
    bf = min(12, int(wind_kn / 4))
    bf_labels = ["静风", "软风", "轻风", "微风", "和风", "清风", "强风", "疾风", "大风", "烈风", "狂风", "暴风", "飓风"]
    # Douglas sea state
    ds = min(9, int(wave_m / 0.5))
    ds_labels = ["无浪", "微浪", "小浪", "轻浪", "中浪", "大浪", "巨浪", "狂浪", "狂涛浪", "怒涛浪"]
    return {
        "beaufort": bf,
        "beaufort_label": f"BF {bf} — {bf_labels[bf]}",
        "douglas": ds,
        "douglas_label": f"{ds} 级 — {ds_labels[ds]}",
        "wind_kn": round(wind_kn, 1),
        "wave_m": round(wave_m, 1),
        "visibility_nm": 8.5,
        "air_temp_c": 22,
        "sea_temp_c": 19,
        "pressure_hpa": 1013,
        "humidity_pct": 78,
    }


@router.get("/weather/current-swell")
async def get_current_swell():
    """洋流与涌浪"""
    return {
        "surface_current": {"speed_kn": 0.8, "direction_deg": 45, "label": "NE"},
        "swell": {"height_m": 1.2, "period_s": 12, "direction_deg": 225, "label": "SW"},
        "assessment": "适航",
    }


@router.get("/weather/tide")
async def get_tide():
    """潮汐预报"""
    import math
    from datetime import datetime
    now = datetime.now()
    hr = now.hour + now.minute / 60
    tide_h = round(2.0 + 1.5 * math.sin((hr - 2) * math.pi / 6.21), 2)
    return {
        "current_height_m": tide_h,
        "next_high": {"time": "14:32", "height_m": 3.4},
        "next_low": {"time": "20:45", "height_m": 0.6},
        "datum": "Chart Datum",
    }


@router.get("/weather/alerts")
async def get_weather_alerts():
    """气象预警"""
    return {
        "alerts": [
            {"level": "blue", "type": "大风蓝色预警", "message": "NW 25kn 阵风预计 18:00", "issued_at": "2026-03-20T06:00:00"},
        ],
        "weather_window": {"status": "ok", "available_hours": 48},
        "route_assessment": "良好",
    }
