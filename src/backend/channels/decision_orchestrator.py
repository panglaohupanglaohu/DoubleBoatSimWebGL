# -*- coding: utf-8 -*-
"""
Decision Orchestrator Channel - 全场景决策与运维生成骨架
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelPriority, ChannelStatus, get_default_registry

logger = logging.getLogger(f"{__name__}.decision_orchestrator")


PRIORITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


class DecisionOrchestratorChannel(MarineChannel):
    name = "decision_orchestrator"
    description = "全场景决策与运维编排 (风险摘要 + 运维动作 + 反馈闭环)"
    version = "0.1.0"
    priority = ChannelPriority.P0
    dependencies: List[str] = [
        "compliance_digital_expert",
        "distributed_perception_hub",
        "intelligent_navigation",
        "intelligent_engine",
        "energy_efficiency",
        "autonomy_manager",
        "ship_shore_link",
        "predictive_health",
        "route_optimizer",
        "cyber_security",
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.config = config or {}
        self._config = self.config
        self.feedback_records: List[Dict[str, Any]] = []
        self.latest_package: Dict[str, Any] = {}
        self.last_coordination_at: Optional[str] = None
        self.coordination_runs = 0
        self.event_sink = self.config.get("event_sink")

    def set_event_sink(self, event_sink: Any) -> None:
        """设置协调层事件持久化目标。"""
        self.event_sink = event_sink

    def initialize(self) -> bool:
        self._initialized = True
        self._set_health(ChannelStatus.OK, "全场景决策编排器已就绪")
        logger.info("✅ Decision Orchestrator initialized")
        return True

    def _build_action_plan(
        self,
        snapshot: Optional[Dict[str, Any]] = None,
        nav_report: Optional[Dict[str, Any]] = None,
        engine_status: Optional[Dict[str, Any]] = None,
        weather_risk: Optional[Dict[str, Any]] = None,
        crew_fatigue: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:


        snapshot = snapshot or {}
        nav_report = nav_report or {}
        engine_status = engine_status or {}
        weather_risk = weather_risk or {}
        crew_fatigue = crew_fatigue or {}

        action_plan: List[Dict[str, Any]] = []
        generated_at = datetime.now().isoformat()

        for item in nav_report.get("colregs_assessments", [])[:3]:
            action_plan.append(
                {
                    "id": f"nav-{item['target_mmsi']}",
                    "domain": "navigation",
                    "priority": "critical" if item["risk_level"] == "danger" else "high",
                    "title": f"{item['encounter_type']} risk with target {item['target_mmsi']}",
                    "rationale": item["summary"],
                    "rule": item["rule"],
                    "recommended_action": item["recommended_action"],
                    "execute_before": generated_at,
                }
            )

        for alert in engine_status.get("alerts", [])[:2]:
            action_plan.append(
                {
                    "id": f"eng-{abs(hash(alert.get('message', 'engine'))) % 100000}",
                    "domain": "engine",
                    "priority": "critical" if alert.get("level") == "critical" else "high",
                    "title": alert.get("message", "Engine alert"),
                    "rationale": "Engine subsystem health requires operator confirmation.",
                    "rule": "Machinery Safety",
                    "recommended_action": "Dispatch engine room verification and reduce propulsion stress if required.",
                    "execute_before": generated_at,
                }
            )

        energy_rec = snapshot.get("engineering_parameters", {}).get("energy", {}).get("recommendations", [])
        for rec in energy_rec[:2]:
            action_plan.append(
                {
                    "id": f"ene-{abs(hash(rec['title'])) % 100000}",
                    "domain": "energy",
                    "priority": rec.get("priority", "medium"),
                    "title": rec["title"],
                    "rationale": "Improve compliance and voyage efficiency margins.",
                    "rule": "CII/EEXI/SEEMP",
                    "recommended_action": rec["title"],
                    "expected_improvement": rec.get("expected_improvement"),
                    "execute_before": generated_at,
                }
            )


        # Weather risk actions
        wr_score = weather_risk.get("risk_score", 0) or 0
        if wr_score > 60:
            action_plan.append({
                "id": "weather-review",
                "domain": "navigation",
                "priority": "critical" if wr_score >= 70 else "high",
                "title": weather_risk.get("recommendation", "Weather risk detected"),
                "rationale": f"Weather risk score {wr_score} exceeds threshold.",
                "rule": "Weather Routing Safety",
                "recommended_action": "review_route",
                "execute_before": generated_at,
            })

        # Crew fatigue actions
        fatigue_scores = crew_fatigue.get("fatigue_scores", {}) or {}
        for crew_name, score in fatigue_scores.items():
            if score is not None and score < 50:
                action_plan.append({
                    "id": f"fatigue-{crew_name}",
                    "domain": "crew",
                    "priority": "critical" if score < 30 else "high",
                    "title": f"Crew fatigue alert: {crew_name} ({score})",
                    "rationale": f"Fatigue score {score} below safety threshold.",
                    "rule": "MLC/STCW Rest Hours",
                    "recommended_action": "recommend_watch_change",
                    "execute_before": generated_at,
                })

        # ── Registry-based subsystem integration ──
        _reg = get_default_registry()

        # Hull stress monitor
        _hull = _reg.get("hull_stress_monitor")
        if _hull and hasattr(_hull, "get_structural_health"):
            _hs = (_hull.get_structural_health() or {})
            _sr = _hs.get("stress_ratio", 0) or 0
            if _sr > 0.8:
                if _hs.get("alarm_active"):
                    action_plan.append({"id": "hull-alarm", "domain": "structure", "priority": "critical", "title": "Hull stress alarm", "rationale": f"Stress ratio {_sr:.2f}", "rule": "Hull Integrity", "recommended_action": "emergency_hull_stress", "execute_before": generated_at})
                action_plan.append({"id": "hull-reduce", "domain": "structure", "priority": "critical" if _sr > 0.9 else "high", "title": f"Hull stress {_sr:.0%}", "rationale": f"Stress ratio {_sr:.2f} > 0.8", "rule": "Hull Integrity", "recommended_action": "reduce_speed_hull_stress", "execute_before": generated_at})

        # Power management
        _pwr = _reg.get("power_management")
        if _pwr and hasattr(_pwr, "get_power_balance"):
            _ps = (_pwr.get_power_balance() or {})
            if _ps.get("load_shedding_needed"):
                action_plan.append({"id": "power-shed", "domain": "power", "priority": "high", "title": "Load shedding required", "rationale": "Power reserve below threshold", "rule": "Power Management", "recommended_action": "load_shedding_required", "execute_before": generated_at})

        # Echo sounder
        _echo = _reg.get("echo_sounder_monitor")
        if _echo and hasattr(_echo, "get_depth_status"):
            _ds = (_echo.get_depth_status() or {})
            if _ds.get("grounding_risk"):
                action_plan.append({"id": "echo-ground", "domain": "navigation", "priority": "critical", "title": "Grounding risk", "rationale": "Echo sounder grounding detection", "rule": "SOLAS Ch V", "recommended_action": "grounding_risk_alert", "execute_before": generated_at})
            if _ds.get("shallow_alarm"):
                action_plan.append({"id": "echo-shallow", "domain": "navigation", "priority": "high", "title": "Shallow water warning", "rationale": "Echo sounder shallow alarm", "rule": "SOLAS Ch V", "recommended_action": "shallow_water_warning", "execute_before": generated_at})

        # Propulsion monitor
        _prop = _reg.get("propulsion_monitor")
        if _prop and hasattr(_prop, "get_propulsion_status"):
            _pp = (_prop.get_propulsion_status() or {})
            if _pp.get("any_alarm"):
                action_plan.append({"id": "prop-alarm", "domain": "propulsion", "priority": "critical", "title": "Propulsion alarm", "rationale": "Propulsion system alarm", "rule": "Machinery Safety", "recommended_action": "propulsion_alarm", "execute_before": generated_at})
            _eff = _pp.get("efficiency_percent", 100)
            if _eff is not None and _eff < 50:
                action_plan.append({"id": "prop-eff", "domain": "propulsion", "priority": "high", "title": f"Low propulsion efficiency {_eff}%", "rationale": "Propulsion efficiency degraded", "rule": "Engine Performance", "recommended_action": "low_propulsion_efficiency", "execute_before": generated_at})

        # Gyro compass
        _gyro = _reg.get("gyro_compass_monitor")
        if _gyro and hasattr(_gyro, "get_heading_consensus"):
            _gc = (_gyro.get_heading_consensus() or {})
            if not _gc.get("agreement", True):
                action_plan.append({"id": "gyro-disagree", "domain": "navigation", "priority": "high", "title": "Heading disagreement", "rationale": "Gyro compasses disagree", "rule": "SOLAS Ch V", "recommended_action": "heading_disagreement", "execute_before": generated_at})

        # Autopilot
        _ap = _reg.get("autopilot_monitor")
        if _ap and hasattr(_ap, "get_autopilot_status"):
            _as = (_ap.get_autopilot_status() or {})
            if not _as.get("on_course", True):
                action_plan.append({"id": "ap-offcourse", "domain": "navigation", "priority": "high", "title": "Off course warning", "rationale": "Autopilot reports off course", "rule": "Navigation Safety", "recommended_action": "off_course_warning", "execute_before": generated_at})

        # Mooring
        _moor = _reg.get("mooring_monitor")
        if _moor and hasattr(_moor, "get_mooring_status"):
            _ms = (_moor.get_mooring_status() or {})
            if _ms.get("any_parted"):
                action_plan.append({"id": "moor-parted", "domain": "mooring", "priority": "critical", "title": "Mooring line parted", "rationale": "Mooring system reports parted line", "rule": "Mooring Safety", "recommended_action": "mooring_line_parted", "execute_before": generated_at})


        # Bilge water monitor - MARPOL compliance
        _bilge = _reg.get('bilge_water_monitor')
        if _bilge and hasattr(_bilge, 'get_status'):
            _bs = (_bilge.get_status() or {})
            if not _bs.get('marpol_compliant', True):
                action_plan.append({'id': 'bilge-marpol', 'domain': 'compliance', 'priority': 'critical', 'title': 'MARPOL bilge water violation', 'rationale': 'Bilge water system non-compliant with MARPOL Annex I', 'rule': 'MARPOL Annex I', 'recommended_action': 'marpol_violation_bilge', 'execute_before': generated_at})

        # Communication manager - GMDSS and distress
        _comms = _reg.get('communication_manager')
        if _comms and hasattr(_comms, 'get_status'):
            _cs = (_comms.get_status() or {})
            if _cs.get('distress_active'):
                action_plan.append({'id': 'comms-distress', 'domain': 'communication', 'priority': 'critical', 'title': 'Distress signal active', 'rationale': 'Vessel distress signal activated', 'rule': 'SOLAS Ch IV', 'recommended_action': 'distress_active', 'execute_before': generated_at})
            if not _cs.get('gmdss_compliant', True):
                action_plan.append({'id': 'comms-gmdss', 'domain': 'communication', 'priority': 'high', 'title': 'GMDSS non-compliant', 'rationale': 'GMDSS equipment requirements not met', 'rule': 'SOLAS Ch IV', 'recommended_action': 'gmdss_non_compliant', 'execute_before': generated_at})

        # Rudder control - SOLAS steering compliance
        _rudder = _reg.get('rudder_control_monitor')
        if _rudder and hasattr(_rudder, 'get_status'):
            _rs = (_rudder.get_status() or {})
            if not _rs.get('solas_compliant', True):
                action_plan.append({'id': 'rudder-fault', 'domain': 'steering', 'priority': 'critical', 'title': 'Steering system fault', 'rationale': 'Rudder control non-compliant with SOLAS requirements', 'rule': 'SOLAS Ch II-1/Reg.29', 'recommended_action': 'steering_fault', 'execute_before': generated_at})

        # Tank level monitor - fuel level
        _tank = _reg.get('tank_level_monitor')
        if _tank and hasattr(_tank, 'get_tank_summary'):
            _ts2 = (_tank.get_tank_summary() or {})
            if len(_ts2.get('low_level_alarms', []) or []) > 0:
                action_plan.append({'id': 'tank-fuel', 'domain': 'fuel', 'priority': 'high', 'title': 'Low fuel level warning', 'rationale': 'Tank level below safe threshold', 'rule': 'Fuel Management', 'recommended_action': 'low_fuel_warning', 'execute_before': generated_at})

        # Alarm management - emergency alarms
        _alarm = _reg.get('alarm_management')
        if _alarm and hasattr(_alarm, 'get_alarm_summary'):
            _als = (_alarm.get_alarm_summary() or {})
            if (_als.get('emergency_count', 0) or 0) > 0:
                action_plan.append({'id': 'alarm-emergency', 'domain': 'alarm', 'priority': 'critical', 'title': 'Emergency alarm active', 'rationale': 'One or more emergency alarms active', 'rule': 'IMO A.1021(26)', 'recommended_action': 'emergency_alarm_active', 'execute_before': generated_at})

        # Man Overboard (MOB) — SOLAS / IAMSAR
        _mob = _reg.get('man_overboard')
        if _mob and hasattr(_mob, 'get_mob_status'):
            _ms2 = (_mob.get_mob_status() or {})
            if _ms2.get('mob_active'):
                _pos = _ms2.get('mob_position') or {}
                _elapsed = _ms2.get('elapsed_minutes', 0) or 0
                _surv = (_ms2.get('survival_estimate') or {}).get('estimated_hours', 0)
                action_plan.append({
                    'id': 'mob-active',
                    'domain': 'safety',
                    'priority': 'critical',
                    'title': f'MOB active — person in water at ({_pos.get("lat")}, {_pos.get("lon")})',
                    'rationale': f'MOB alert for {_elapsed:.0f} min, est. survival {_surv:.1f}h. Search pattern: {_ms2.get("search_pattern", "none")}',
                    'rule': 'SOLAS Ch III / IAMSAR Vol III',
                    'recommended_action': 'mob_search_and_rescue',
                    'execute_before': generated_at,
                })
                # Escalation: if elapsed > 50% survival, recommend MAYDAY
                if _surv > 0 and (_elapsed / 60.0) > (_surv * 0.5):
                    action_plan.append({
                        'id': 'mob-escalate',
                        'domain': 'safety',
                        'priority': 'critical',
                        'title': 'MOB escalation — upgrade to MAYDAY',
                        'rationale': f'Elapsed {_elapsed:.0f} min exceeds 50% of survival estimate ({_surv:.1f}h)',
                        'rule': 'GMDSS Distress Protocol',
                        'recommended_action': 'mob_escalate_mayday',
                        'execute_before': generated_at,
                    })

        if not action_plan:
            action_plan.append(
                {
                    "id": "ops-monitor",
                    "domain": "operations",
                    "priority": "low",
                    "title": "Maintain supervised monitoring",
                    "rationale": "No high-priority anomaly has been detected in the current cycle.",
                    "rule": "Baseline supervision",
                    "recommended_action": "Continue watchkeeping and preserve current control setpoints.",
                    "execute_before": generated_at,
                }
            )

        action_plan.sort(key=lambda item: PRIORITY_RANK.get(item["priority"], 9))
        return action_plan

    def _build_task_graph(
        self,
        action_plan: List[Dict[str, Any]],
        autonomy_mode: str,
        snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        generated_at = datetime.now().isoformat()
        nodes: List[Dict[str, Any]] = [
            {
                "id": "mission",
                "type": "mission",
                "label": "CPS mission brief",
                "status": snapshot.get("compliance_status", "unknown"),
                "priority": snapshot.get("risk_level", "unknown"),
            }
        ]
        edges: List[Dict[str, str]] = []
        execution_order: List[str] = []

        seen_domains = set()
        for item in action_plan:
            domain_id = f"domain:{item['domain']}"
            if domain_id not in seen_domains:
                nodes.append(
                    {
                        "id": domain_id,
                        "type": "domain",
                        "label": item["domain"],
                        "status": "ready",
                        "priority": item["priority"],
                    }
                )
                edges.append({"from": "mission", "to": domain_id, "relation": "dispatches"})
                seen_domains.add(domain_id)

            task_id = f"task:{item['id']}"
            nodes.append(
                {
                    "id": task_id,
                    "type": "task",
                    "label": item["title"],
                    "status": "ready",
                    "priority": item["priority"],
                    "execute_before": item.get("execute_before", generated_at),
                }
            )
            edges.append({"from": domain_id, "to": task_id, "relation": "contains"})
            execution_order.append(task_id)

        return {
            "generated_at": generated_at,
            "autonomy_mode": autonomy_mode,
            "nodes": nodes,
            "edges": edges,
            "execution_order": execution_order,
            "feedback_channel": "decision_feedback_event",
        }

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        logger.info("🛑 Decision Orchestrator shutdown")
        return True

    def build_decision_package(self) -> Dict[str, Any]:
        registry = get_default_registry()
        compliance = registry.get("compliance_digital_expert")
        perception = registry.get("distributed_perception_hub")
        navigation = registry.get("intelligent_navigation")
        engine = registry.get("intelligent_engine")

        # 新增模块引用
        autonomy_mgr = registry.get("autonomy_manager")
        ship_shore = registry.get("ship_shore_link")
        phm = registry.get("predictive_health")
        route_opt = registry.get("route_optimizer")
        cyber_sec = registry.get("cyber_security")
        weather_routing = registry.get("weather_routing")
        crew_fatigue_ch = registry.get("crew_fatigue")

        logger.debug("📦 Building decision package...")
        snapshot = (compliance.query_compliance_status("overall") if compliance and hasattr(compliance, "query_compliance_status") else {}) or {}
        latest_events = perception.get_latest_events(10) if perception and hasattr(perception, "get_latest_events") else []
        nav_report = (navigation.generate_navigation_report() if navigation and hasattr(navigation, "generate_navigation_report") else {}) or {}
        engine_status = (engine.get_status() if engine else {}) or {}

        # 新模块数据采集
        autonomy_status = autonomy_mgr.get_status() if autonomy_mgr else {}
        link_status = ship_shore.get_status() if ship_shore else {}
        phm_status = phm.get_status() if phm else {}
        route_status = route_opt.get_status() if route_opt else {}
        cyber_status = cyber_sec.get_status() if cyber_sec else {}

        weather_risk_data = {}
        if weather_routing and hasattr(weather_routing, "get_status"):
            wr_status = weather_routing.get_status() or {}
            weather_risk_data = wr_status.get("weather_risk", wr_status)
        crew_fatigue_data = {}
        if crew_fatigue_ch and hasattr(crew_fatigue_ch, "get_status"):
            cf_status = crew_fatigue_ch.get_status() or {}
            crew_fatigue_data = cf_status.get("fatigue", cf_status)

        action_plan = self._build_action_plan(snapshot, nav_report, engine_status, weather_risk_data, crew_fatigue_data)

        # PHM 高优先级维护动作
        if phm and hasattr(phm, "generate_maintenance_plan"):
            maint_list = phm.generate_maintenance_plan()
            # Returns a list of MaintenanceRecommendation dataclasses
            if isinstance(maint_list, list):
                for rec in maint_list[:3]:
                    priority_raw = getattr(rec, "priority", "monitor")
                    priority_val = getattr(priority_raw, "value", priority_raw)
                    component_val = getattr(rec, "component_id", "unknown")
                    action_val = getattr(rec, "action", "检查设备")
                    if str(priority_val).lower() in ("immediate", "next_port"):
                        action_plan.append({
                            "id": f"phm-{component_val}",
                            "domain": "maintenance",
                            "priority": "critical" if "immediate" in str(priority_val).lower() else "high",
                            "title": f"PHM: {component_val} - {action_val}",
                            "rationale": f"Predictive health alert",
                            "rule": "Predictive Health Management",
                            "recommended_action": action_val,
                            "execute_before": datetime.now().isoformat(),
                        })

        # 通信链路降级动作
        if ship_shore and hasattr(ship_shore, "select_best_link"):
            best_link = ship_shore.select_best_link()
            # select_best_link returns a LinkType enum or None
            link_health = link_status.get("health", "ok")
            if best_link is None or link_health in ("error", "warn"):
                action_plan.append({
                    "id": "link-degraded",
                    "domain": "communication",
                    "priority": "high",
                    "title": f"Ship-shore link degraded: {best_link.value if best_link else 'none'}",
                    "rationale": f"Link health: {link_health}",
                    "rule": "Communication Safety",
                    "recommended_action": "切换备用通信链路或降低自主等级",
                    "execute_before": datetime.now().isoformat(),
                })

        action_plan.sort(key=lambda item: PRIORITY_RANK.get(item["priority"], 9))

        # 自主等级决定执行模式
        mass_level_raw = autonomy_status.get("mass_code") or autonomy_status.get("mass_level", "M")
        mass_level_map = {
            "m": "M",
            "manual": "M",
            "r": "R",
            "remote_crewed": "R",
            "ru": "RU",
            "remote_uncrewed": "RU",
            "a": "A",
            "autonomous": "A",
        }
        mass_level = mass_level_map.get(str(mass_level_raw).strip().lower(), "M")
        if mass_level in ("RU", "A"):
            autonomy_mode = "autonomous"
        elif mass_level == "R":
            autonomy_mode = "remote_supervised"
        elif snapshot.get("risk_level") in {"medium", "high"}:
            autonomy_mode = "supervised_autonomy"
        else:
            autonomy_mode = "advisory"

        task_graph = self._build_task_graph(action_plan, autonomy_mode, snapshot)
        package = {
            "generated_at": datetime.now().isoformat(),
            "risk_level": snapshot.get("risk_level", "unknown"),
            "compliance_status": snapshot.get("compliance_status", "unknown"),
            "summary": f"航行风险 {snapshot.get('risk_level', 'unknown')}，MASS={mass_level}，需执行 {len(action_plan)} 个跨域动作。",
            "autonomy_mode": autonomy_mode,
            "mass_level": mass_level,
            "recommended_actions": snapshot.get("recommended_actions", []),
            "action_plan": action_plan,
            "task_graph": task_graph,
            "mission_brief": {
                "operational_picture": {
                    "overall_status": nav_report.get("overall_status", "unknown"),
                    "active_risks": len(nav_report.get("collision_risks", [])),
                    "engine_alerts": len(engine_status.get("alerts", [])),
                    "recent_events": len(latest_events),
                    "threat_level": cyber_status.get("threat_level", "none"),
                    "link_quality": link_status.get(
                        "best_link_quality",
                        link_status.get("latency_prediction", {}).get("confidence", "N/A"),
                    ),
                },
                "control_objectives": [
                    "Preserve safe CPA/TCPA margins under COLREGs constraints.",
                    "Protect propulsion and cooling subsystem availability.",
                    "Maintain efficiency and compliance within voyage limits.",
                    "Ensure ship-shore communication continuity.",
                    "Enforce cybersecurity posture per SVESSEL BIG policy.",
                ],
                "execution_style": autonomy_mode,
                "watchstanding_note": snapshot.get("recommended_actions", ["Maintain normal watch."])[0],
                "weather_summary": {
                    "risk_level": weather_risk_data.get("risk_level", "unknown") if weather_risk_data else "unknown",
                    "risk_score": weather_risk_data.get("risk_score", 0) if weather_risk_data else 0,
                    "recommendation": weather_risk_data.get("recommendation", "No data"),
                },
                "crew_fatigue_warning": {
                    "alerts": [
                        {"crew": k, "score": v}
                        for k, v in (crew_fatigue_data.get("fatigue_scores", {}) or {}).items()
                        if v is not None and v < 50
                    ],
                    "total_crew": len(crew_fatigue_data.get("fatigue_scores", {}) or {}),
                },
            },
            "maintenance_report": snapshot.get("maintenance_report", {}),
            "phm_summary": phm_status,
            "communication": link_status,
            "cybersecurity": cyber_status,
            "route_optimization": route_status,
            "weather_risk": weather_risk_data,
            "crew_fatigue_alert": crew_fatigue_data,
            "supporting_evidence": snapshot.get("evidence", []),
            "latest_events": latest_events,
            "feedback_records": self.feedback_records[-10:],
            "component_status": {
                "navigation": nav_report.get("risk_index", {}),
                "engine": {
                    "health": engine_status.get("health"),
                    "health_score": engine_status.get("engine_health_score"),
                },
                "autonomy": autonomy_status,
                "ship_shore_link": link_status,
                "predictive_health": phm_status,
                "route_optimizer": route_status,
                "cyber_security": cyber_status,
            },
            "kpi_targets": {
                "minimum_dcpa_nm": getattr(navigation, "dcpa_limit", None),
                "maximum_tcpa_min": getattr(navigation, "tcpa_limit", None),
                "engine_health_score_floor": 85,
                "decision_latency_target_ms": 200,
                "link_quality_floor": 0.6,
                "phm_rul_warning_hours": 200,
            },
        }
        self.latest_package = package
        return package

    def coordinate_agents(self, event_sink: Optional[Any] = None) -> Dict[str, Any]:
        """执行一次跨智能体协调循环。"""
        registry = get_default_registry()
        perception = registry.get("distributed_perception_hub")

        captured_events: List[Dict[str, Any]] = []
        if perception and hasattr(perception, "capture_system_snapshot"):
            try:
                snapshot_events = perception.capture_system_snapshot()
                captured_events = [event.to_dict() for event in snapshot_events]
                perception_sink = getattr(perception, "event_sink", None)
                if event_sink and captured_events and perception_sink is not event_sink:
                    event_sink.save_batch(captured_events)
            except Exception as exc:
                logger.warning(f"Perception snapshot during coordination failed: {exc}")

        package = self.build_decision_package()
        decision_event = {
            "timestamp": package["generated_at"],
            "event_type": "decision_package_event",
            "source": self.name,
            "payload": package,
            "confidence": 1.0,
        }
        if event_sink:
            event_sink.save_event(decision_event)

        self.coordination_runs += 1
        self.last_coordination_at = package["generated_at"]

        return {
            "timestamp": self.last_coordination_at,
            "captured_events": len(captured_events),
            "decision_risk_level": package.get("risk_level", "unknown"),
            "recommended_actions_count": len(package.get("recommended_actions", [])),
            "coordination_runs": self.coordination_runs,
        }

    def record_feedback(self, action: str, outcome: str, confirmed_by: str = "system") -> Dict[str, Any]:
        record = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "outcome": outcome,
            "confirmed_by": confirmed_by,
        }
        self.feedback_records.append(record)
        if self.event_sink:
            try:
                self.event_sink.save_event(
                    {
                        "timestamp": record["timestamp"],
                        "event_type": "decision_feedback_event",
                        "source": self.name,
                        "payload": {
                            **record,
                            "coordination_runs": self.coordination_runs,
                            "decision_generated_at": self.latest_package.get("generated_at"),
                        },
                        "confidence": 1.0,
                    }
                )
            except Exception as exc:
                logger.warning(f"Failed to persist decision feedback: {exc}")
        return record

    def get_status(self) -> Dict[str, Any]:
        package = self.build_decision_package()
        return {
            "name": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "health_message": self._health.message,
            "risk_level": package["risk_level"],
            "compliance_status": package["compliance_status"],
            "recommended_actions_count": len(package["recommended_actions"]),
            "action_plan_count": len(package.get("action_plan", [])),
            "task_graph_nodes": len(package.get("task_graph", {}).get("nodes", [])),
            "feedback_records_count": len(self.feedback_records),
            "coordination_runs": self.coordination_runs,
            "last_coordination_at": self.last_coordination_at,
            "autonomy_mode": package.get("autonomy_mode"),
        }

    async def build_decision_package_async(self) -> Dict[str, Any]:
        """异步构建决策包."""
        return await asyncio.get_event_loop().run_in_executor(None, self.build_decision_package)

    async def record_feedback_async(self, action: str, outcome: str, confirmed_by: str = "system") -> Dict[str, Any]:
        """异步记录反馈."""
        return await asyncio.get_event_loop().run_in_executor(None, self.record_feedback, action, outcome, confirmed_by)


__all__ = ["DecisionOrchestratorChannel"]
