# -*- coding: utf-8 -*-
"""
OpenBridge command router - 驾驶台语义命令轻量路由
"""

from __future__ import annotations

from typing import Any, Dict


def classify_openbridge_intent(command: str) -> Dict[str, Any]:
    """将驾驶台自然语言命令映射为轻量意图。"""
    lower = (command or "").strip().lower()
    intents = [
        {
            "intent": "show_task_graph",
            "keywords": ["task", "任务", "graph", "行动", "mission", "brief", "计划"],
            "domain": "decision",
            "mode": "monitor",
            "operator_action": "Review current task graph and execution order.",
        },
        {
            "intent": "show_collision_risk",
            "keywords": ["碰撞", "风险", "ais", "导航", "colregs", "避碰"],
            "domain": "navigation",
            "mode": "manual_ack_required",
            "operator_action": "Review active COLREGs constraints and confirm the next manoeuvre.",
        },
        {
            "intent": "set_comfort_mode",
            "keywords": ["舒适", "rcs", "平稳", "减摇", "foil", "trim", "姿态"],
            "domain": "rcs",
            "mode": "supervised_adjustment",
            "operator_action": "Bias T-Foil and trim tab settings toward comfort-preserving stabilization.",
        },
        {
            "intent": "show_structural_health",
            "keywords": ["结构", "shm", "疲劳", "应变", "寿命", "弯矩", "torsion"],
            "domain": "shm",
            "mode": "monitor",
            "operator_action": "Inspect structural hotspot loads and remaining life margins.",
        },
        {
            "intent": "show_engine_health",
            "keywords": ["主机", "机舱", "engine", "维护", "健康"],
            "domain": "engine",
            "mode": "monitor",
            "operator_action": "Review engine alerts and maintenance advice.",
        },
    ]

    for item in intents:
        if any(keyword in lower for keyword in item["keywords"]):
            return item

    return {
        "intent": "general_assist",
        "domain": "general",
        "mode": "advisory",
        "operator_action": "Provide high-level situational assistance.",
    }


def build_openbridge_command_result(command: str, dashboard: Dict[str, Any], mission: Dict[str, Any]) -> Dict[str, Any]:
    """构造 OpenBridge 语义命令结果。"""
    intent = classify_openbridge_intent(command)
    task_graph = mission.get("task_graph") or dashboard.get("decision", {}).get("task_graph", {})
    nav_report = dashboard.get("navigation", {}).get("report", {})
    rcs = dashboard.get("rcs", {})
    shm = dashboard.get("shm", {})
    engine = dashboard.get("engine", {})

    summaries = {
        "show_task_graph": f"当前任务图共有 {len(task_graph.get('nodes', []))} 个节点，执行模式为 {mission.get('autonomy_mode', 'unknown')}。",
        "show_collision_risk": f"当前导航总体状态为 {nav_report.get('overall_status', 'unknown')}，活动风险数 {len(nav_report.get('collision_risks', []))}。",
        "set_comfort_mode": f"RCS 当前建议 T-Foil {rcs.get('foil_angle_deg', '--')}°，Trim Tabs {rcs.get('trim_tab_angle_deg', '--')}°，MSDV 目标 {rcs.get('comfort_target_msdv', '--')}。",
        "show_structural_health": f"SHM 当前疲劳损伤 {shm.get('fatigue_damage_index', '--')}，寿命余度 {shm.get('life_remaining_pct', '--')}%。",
        "show_engine_health": f"主机健康分 {engine.get('health_score', '--')}，当前告警 {len(engine.get('alerts', []))} 条。",
        "general_assist": "已进入桥楼综合辅助模式，可查询任务图、避碰、姿态控制、结构健康和主机状态。",
    }

    domain_focus = {
        "decision": task_graph.get("nodes", [])[:5],
        "navigation": nav_report.get("colregs_assessments", [])[:3],
        "rcs": [
            {"label": "foil_angle_deg", "value": rcs.get("foil_angle_deg")},
            {"label": "trim_tab_angle_deg", "value": rcs.get("trim_tab_angle_deg")},
            {"label": "comfort_target_msdv", "value": rcs.get("comfort_target_msdv")},
        ],
        "shm": shm.get("strain_hotspots", [])[:3],
        "engine": engine.get("maintenance_advice", [])[:3],
        "general": [],
    }

    return {
        "command": command,
        "recognized_intent": intent["intent"],
        "domain": intent["domain"],
        "execution_mode": intent["mode"],
        "operator_action": intent["operator_action"],
        "summary": summaries[intent["intent"]],
        "task_graph": {
            "node_count": len(task_graph.get("nodes", [])),
            "execution_order": task_graph.get("execution_order", [])[:5],
        },
        "control_state": {
            "rcs": {
                "foil_angle_deg": rcs.get("foil_angle_deg"),
                "trim_tab_angle_deg": rcs.get("trim_tab_angle_deg"),
                "comfort_target_msdv": rcs.get("comfort_target_msdv"),
            },
            "shm": {
                "fatigue_damage_index": shm.get("fatigue_damage_index"),
                "life_remaining_pct": shm.get("life_remaining_pct"),
            },
        },
        "focus_items": domain_focus[intent["domain"]],
    }


__all__ = ["classify_openbridge_intent", "build_openbridge_command_result"]