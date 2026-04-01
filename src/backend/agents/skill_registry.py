# -*- coding: utf-8 -*-
"""PoseidonX Agent Team Framework — Skill Registry.

Provides default skill definitions across general, digital-twin, and maritime
categories, plus a registry class for runtime skill management.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import SkillCategory, SkillDefinition


def get_default_skills() -> List[SkillDefinition]:
    """Return the default catalog of skill definitions."""

    SC = SkillCategory
    SD = SkillDefinition
    return [
        # ── General skills ─────────────────────────────────────────────
        SD(
            name="competitive_analysis",
            description="Analyze competitors and market positioning",
            category=SC.GENERAL,
            required_tools=['web_search', 'extract_content']),
        SD(
            name="complex_task_executor",
            description="Break down and execute complex multi-step tasks",
            category=SC.GENERAL,
            required=True,
            required_tools=['run_python', 'run_shell', 'send_message']),
        SD(
            name="content_research_writer",
            description="Research topics and produce written content",
            category=SC.GENERAL,
            required_tools=['web_search', 'extract_content', 'write_file']),
        SD(
            name="content_writing",
            description="Write and edit documentation and reports",
            category=SC.GENERAL,
            required_tools=['write_file', 'read_file']),
        SD(
            name="data_analysis",
            description="Analyze datasets and produce insights",
            category=SC.GENERAL,
            required_tools=['run_python', 'read_file']),
        SD(
            name="mcp_installer",
            description="Install and configure MCP server integrations",
            category=SC.GENERAL,
            required=True,
            required_tools=['run_shell', 'write_file', 'read_file']),
        SD(
            name="meeting_notes",
            description="Capture and summarize meeting notes",
            category=SC.GENERAL,
            required_tools=['write_file']),
        SD(
            name="skill_creator",
            description="Create new custom skills from descriptions",
            category=SC.GENERAL,
            required=True,
            required_tools=['write_file', 'read_file']),
        SD(
            name="web_research",
            description="Conduct web research and summarize findings",
            category=SC.GENERAL,
            required_tools=['web_search', 'navigate_url', 'extract_content']),
        # ── Digital Twin skills ────────────────────────────────────────
        SD(
            name="dt_camera_control",
            description="Control digital twin camera views and animations",
            category=SC.DIGITAL_TWIN,
            required_tools=['dt_camera_move']),
        SD(
            name="dt_coordinate_system",
            description="Manage coordinate system transformations",
            category=SC.DIGITAL_TWIN,
            required_tools=['dt_model_transform']),
        SD(
            name="dt_model_layout",
            description="Arrange and layout 3D models in the scene",
            category=SC.DIGITAL_TWIN,
            required_tools=['dt_model_load', 'dt_model_transform']),
        SD(
            name="dt_model_import",
            description="Import 3D models from various formats",
            category=SC.DIGITAL_TWIN,
            required_tools=['dt_model_load']),
        SD(
            name="dt_interaction_actions",
            description="Define interactive inspection paths and actions",
            category=SC.DIGITAL_TWIN,
            required_tools=['dt_inspection_path', 'dt_camera_move']),
        SD(
            name="dt_material_change",
            description="Change materials and textures on models",
            category=SC.DIGITAL_TWIN,
            required_tools=['dt_material_set']),
        SD(
            name="dt_physics_simulation",
            description="Configure and run physics simulations",
            category=SC.DIGITAL_TWIN,
            required_tools=['dt_physics_toggle']),
        SD(
            name="dt_lighting_control",
            description="Control scene lighting and shadows",
            category=SC.DIGITAL_TWIN,
            required_tools=['dt_light_adjust']),
        SD(
            name="dt_rendering_control",
            description="Control rendering pipeline and effects",
            category=SC.DIGITAL_TWIN,
            required_tools=['dt_render_mode']),
        # ── Maritime skills ────────────────────────────────────────────
        SD(
            name="navigation_assessment",
            description="Assess navigation conditions and risks",
            category=SC.MARITIME,
            required_tools=['ais_query', 'weather_fetch', 'route_calculate']),
        SD(
            name="colregs_compliance",
            description="Evaluate COLREGs rule compliance",
            category=SC.MARITIME,
            required_tools=['colregs_check', 'ais_query']),
        SD(
            name="engine_diagnostics",
            description="Diagnose engine health and performance",
            category=SC.MARITIME,
            required_tools=['engine_status']),
        SD(
            name="weather_analysis",
            description="Analyze marine weather patterns and forecasts",
            category=SC.MARITIME,
            required_tools=['weather_fetch']),
        SD(
            name="route_optimization",
            description="Optimize maritime routes for efficiency and safety",
            category=SC.MARITIME,
            required_tools=['route_calculate', 'weather_fetch']),
        SD(
            name="cargo_management",
            description="Manage cargo loading, stability, and tracking",
            category=SC.MARITIME,
            required_tools=['cargo_status']),
        # Maritime subcategory skills
        SD(
            name="celestial_navigation",
            description="Celestial and inertial navigation techniques",
            category=SC.NAVIGATION,
            required_tools=['chart_ecdis_query']),
        SD(
            name="colregs_compliance",
            description="COLREGs collision avoidance rule compliance",
            category=SC.COLLISION_AVOIDANCE,
            required_tools=['colregs_check', 'ais_vessel_track']),
        SD(
            name="propulsion_management",
            description="Main engine and propulsion system management",
            category=SC.PROPULSION,
            required_tools=['engine_diagnostic_scan']),
        SD(
            name="weather_routing",
            description="Weather-based route optimization",
            category=SC.WEATHER_ANALYSIS,
            required_tools=['weather_marine_forecast']),
        SD(
            name="cargo_ops",
            description="Cargo loading plans and stability calculation",
            category=SC.CARGO_MANAGEMENT,
            required_tools=['cargo_status']),
        SD(
            name="vhf_dsc_communication",
            description="VHF/DSC maritime communication protocols",
            category=SC.SHIP_COMMUNICATION,
            required_tools=[]),
        # ── Automation skills ──────────────────────────────────────────
        SD(
            name="auto_report",
            description="定时生成工作报告",
            category=SC.AUTOMATION,
            icon="📊",
            required_tools=['write_file']),
        SD(
            name="auto_monitor",
            description="监控系统状态并报警",
            category=SC.AUTOMATION,
            icon="🔔",
            required_tools=['schedule_task', 'send_message']),
        SD(
            name="workflow_runner",
            description="运行预定义工作流",
            category=SC.AUTOMATION,
            icon="▶️",
            required_tools=['run_python', 'run_shell']),
        # ── Hermes Research skills (自改进研究技能) ─────────────────────
        SD(
            name="imo_regulation_lookup",
            description="IMO/CCS/DNV 法规标准查询与引用 — 自动检索并引用海事法规",
            category=SC.RESEARCH,
            icon="📜",
            required_tools=['web_search', 'extract_content', 'memory_save']),
        SD(
            name="cpa_tcpa_calculator",
            description="CPA/TCPA 碰撞风险计算 — 验证避碰算法的最近会遇距离和时间",
            category=SC.RESEARCH,
            icon="📐",
            required_tools=['run_python', 'read_file', 'memory_save']),
        SD(
            name="eexi_verification",
            description="EEXI 能效指标验证工作流 — IMO MEPC.364(79) 合规审查",
            category=SC.RESEARCH,
            icon="⚡",
            required_tools=['run_python', 'read_file', 'web_search']),
        SD(
            name="wpc_motion_model_review",
            description="穿浪双体船运动模型审查 — pitch/roll/bow-slam 物理模型验证",
            category=SC.RESEARCH,
            icon="🚢",
            required_tools=['read_file', 'run_python', 'memory_save']),
        SD(
            name="maritime_paper_analysis",
            description="海事学术论文检索与分析 — 文献综述和前沿跟踪",
            category=SC.RESEARCH,
            icon="📄",
            required_tools=['web_search', 'navigate_url', 'extract_content']),
        SD(
            name="cross_session_recall",
            description="跨会话研究回溯 — 从历史研究中提取相关发现",
            category=SC.RESEARCH,
            icon="🔍",
            required_tools=['session_search', 'memory_read']),
        # ── Domain Knowledge skills (领域知识技能) ─────────────────────
        SD(
            name="colregs_rule_matrix",
            description="COLREGs 规则矩阵 — Rules 5-19 适用场景速查和冲突分析",
            category=SC.DOMAIN_KNOWLEDGE,
            icon="⚓",
            required_tools=['read_file']),
        SD(
            name="mass_autonomy_assessment",
            description="MASS 自主等级评估 — AL0-AL6 权限矩阵和人机协作分析",
            category=SC.DOMAIN_KNOWLEDGE,
            icon="🤖",
            required_tools=['read_file', 'web_search']),
        SD(
            name="link_budget_modeling",
            description="船岸通信链路预算 — VSAT/LTE/HF/Starlink 性能建模",
            category=SC.DOMAIN_KNOWLEDGE,
            icon="📡",
            required_tools=['run_python', 'read_file']),
    ]


class SkillRegistry:
    """Runtime registry for managing skills."""

    def __init__(self) -> None:
        self._skills: Dict[str, SkillDefinition] = {}

    def load_defaults(self) -> None:
        """Load all default skills into the registry."""
        for skill in get_default_skills():
            self._skills[skill.skill_id] = skill

    def register(self, skill: SkillDefinition) -> None:
        """Register a single skill."""
        self._skills[skill.skill_id] = skill

    def get(self, skill_id: str) -> Optional[SkillDefinition]:
        """Get a skill by ID."""
        return self._skills.get(skill_id)

    def list_all(self) -> List[SkillDefinition]:
        """Return all registered skills."""
        return list(self._skills.values())

    def list_by_category(self, category: SkillCategory) -> List[SkillDefinition]:
        """Return skills filtered by category."""
        return [s for s in self._skills.values() if s.category == category]

    def list_required(self) -> List[SkillDefinition]:
        """Return only required skills."""
        return [s for s in self._skills.values() if s.required]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize registry to dict."""
        return {sid: s.to_dict() for sid, s in self._skills.items()}
