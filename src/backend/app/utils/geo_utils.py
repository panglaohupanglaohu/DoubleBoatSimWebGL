# -*- coding: utf-8 -*-
"""
geo_utils.py — 地理计算工具函数

提供方位角、距离计算等地理空间计算功能。
"""

from __future__ import annotations

import math
from typing import Tuple


def calculate_bearing_and_range(
    origin: Tuple[float, float],
    destination: Tuple[float, float],
) -> Tuple[float, float]:
    """
    计算从 origin 到 destination 的方位角和距离。

    Args:
        origin: (latitude, longitude) 本船位置，单位度
        destination: (latitude, longitude) 目标位置，单位度

    Returns:
        (bearing_deg, range_nm): 方位角（度，正北为0，顺时针）和距离（海里）
    """
    lat1, lon1 = math.radians(origin[0]), math.radians(origin[1])
    lat2, lon2 = math.radians(destination[0]), math.radians(destination[1])

    dlon = lon2 - lon1

    # 计算方位角
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360

    # 使用 Haversine 公式计算距离
    a = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_km = 6371 * c  # 地球半径 6371 km
    distance_nm = distance_km / 1.852  # 转换为海里

    return bearing, distance_nm


def calculate_cpa_tcpa(
    own_pos: Tuple[float, float],
    own_course: float,
    own_speed: float,
    target_pos: Tuple[float, float],
    target_course: float,
    target_speed: float,
) -> Tuple[float, float]:
    """
    计算 CPA (最近会遇距离) 和 TCPA (到达最近会遇点时间)。

    Args:
        own_pos: (lat, lon) 本船位置
        own_course: 本船航向（度）
        own_speed: 本船航速（节）
        target_pos: (lat, lon) 目标位置
        target_course: 目标航向（度）
        target_speed: 目标航速（节）

    Returns:
        (cpa_nm, tcpa_min): CPA（海里）和 TCPA（分钟）
    """
    # 将经纬度差转换为海里
    d_lon = (target_pos[1] - own_pos[1]) * math.cos(math.radians(own_pos[0])) * 60
    d_lat = (target_pos[0] - own_pos[0]) * 60

    # 计算相对速度分量（海里/分钟）
    own_vx = (own_speed / 60) * math.sin(math.radians(own_course))
    own_vy = (own_speed / 60) * math.cos(math.radians(own_course))
    tgt_vx = (target_speed / 60) * math.sin(math.radians(target_course))
    tgt_vy = (target_speed / 60) * math.cos(math.radians(target_course))

    dvx = tgt_vx - own_vx
    dvy = tgt_vy - own_vy
    dv_sq = dvx * dvx + dvy * dvy

    if dv_sq < 1e-10:
        # 相对速度为零，两船同向同速
        cpa = math.sqrt(d_lon ** 2 + d_lat ** 2)
        tcpa = 9999.0
    else:
        tcpa = max(0, -(d_lon * dvx + d_lat * dvy) / dv_sq)
        cpx = d_lon + dvx * tcpa
        cpy = d_lat + dvy * tcpa
        cpa = math.sqrt(cpx ** 2 + cpy ** 2)

    return cpa, tcpa


def calculate_risk_level(cpa_nm: float, tcpa_min: float) -> str:
    """
    根据 CPA 和 TCPA 计算碰撞风险等级。

    Args:
        cpa_nm: 最近会遇距离（海里）
        tcpa_min: 到达最近会遇点时间（分钟）

    Returns:
        'high', 'medium', 'low' 之一
    """
    if cpa_nm < 0.5 and tcpa_min < 8:
        return 'high'
    elif cpa_nm < 1.0 and tcpa_min < 15:
        return 'medium'
    elif cpa_nm < 2.0 and tcpa_min < 30:
        return 'medium'
    return 'low'
