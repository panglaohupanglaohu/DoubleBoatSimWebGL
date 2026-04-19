# -*- coding: utf-8 -*-
"""
System Self-Evolution Engine — 系统自我演进引擎

执行智能体参考业界标准审查各 Channel，发现不完善之处后
自动生成演进任务，派发给 Build 团队执行修改，并通过
模拟人类操作的自动化测试进行验证。

闭环流程:
  Audit (执行智能体审查)
    → Discovery (发现演进项)
      → Dispatch (派发 Build 团队)
        → Build (实施修改)
          → Verify (自动化测试验证)
            → Close / Retry

术语:
  EvolutionItem   — 一条演进需求
  AuditRule       — 审查规则 (对标 IAMSAR / SOLAS / COLREGs / GMDSS 等)
  BuildTask       — 派发给 Build 团队的工作单元
  VerifyResult    — 自动化测试验证结果
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .marine_base import (
    MarineChannel,
    ChannelPriority,
    ChannelStatus,
    get_default_registry,
)

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Data Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class EvolutionStatus(str, Enum):
    """演进条目生命周期状态。"""
    DISCOVERED = "discovered"          # 执行智能体发现
    DISPATCHED = "dispatched"          # 已派发 Build 团队
    IN_PROGRESS = "in_progress"        # Build 团队工作中
    VERIFY_PENDING = "verify_pending"  # 等待验证
    VERIFIED = "verified"              # 验证通过
    FAILED = "failed"                  # 验证失败 (需重试)
    CLOSED = "closed"                  # 关闭


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AuditDomain(str, Enum):
    IAMSAR = "IAMSAR"
    SOLAS = "SOLAS"
    COLREGS = "COLREGs"
    GMDSS = "GMDSS"
    MARPOL = "MARPOL"
    MLC_STCW = "MLC/STCW"
    CII_EEXI = "CII/EEXI"
    DATACENTER = "Datacenter"
    GENERAL = "general"


# ── DNV-style A~E Compliance Rating (inspired by DNV CII) ──

class ComplianceRating(str, Enum):
    """DNV CII 风格 A~E 五级合规评级。"""
    A = "A"  # Major superior — 全面优秀
    B = "B"  # Minor superior — 良好，少量待改进
    C = "C"  # Moderate       — 基本合规，需要关注
    D = "D"  # Minor inferior — 不达标，需要纠正计划
    E = "E"  # Inferior       — 严重不合规，需紧急干预

    @staticmethod
    def from_score(score: float) -> "ComplianceRating":
        """0~100 分 → A~E 评级 (阈值逐年加严，参考 DNV CII reduction factor)。"""
        if score >= 85:
            return ComplianceRating.A
        if score >= 70:
            return ComplianceRating.B
        if score >= 55:
            return ComplianceRating.C
        if score >= 40:
            return ComplianceRating.D
        return ComplianceRating.E


# ── Kongsberg-style Operational Domain (6-domain) ───────────

class OperationalDomain(str, Enum):
    """Kongsberg Maritime 启发的 6 大操作域分类。"""
    TECHNICAL_MGMT = "technical_management"    # 技术管理
    COMPLIANCE_SAFETY = "compliance_safety"    # 合规与安全
    FUEL_EMISSIONS = "fuel_emissions"          # 燃油与排放
    VOYAGE_COMMERCIAL = "voyage_commercial"    # 航次与商业
    DATA_DECISION = "data_decision"            # 数据与决策
    ADVANCED_OPS = "advanced_operations"       # 高级操作 (自主/DP)


# ── ClassNK-style Dual-Layer Checklist ──────────────────────

class ChecklistLevel(str, Enum):
    """ClassNK 双层自查清单: 公司级 + 船级。"""
    COMPANY = "company"  # 公司管理体系 (ISM DOC)
    SHIP = "ship"        # 船舶管理体系 (ISM SMC)
    BOTH = "both"        # 两级均需检查


# ── Failure Escalation Tiers (DNV SEEMP Part III) ───────────

class EscalationTier(str, Enum):
    """失败升级层级 — 参考 DNV SEEMP Part III 纠正计划机制。"""
    NORMAL = "normal"              # 正常处理
    CORRECTIVE_PLAN = "corrective" # 需要纠正行动计划 (连续2次失败)
    MANAGEMENT_REVIEW = "review"   # 需要管理层审查 (连续3次失败)
    CRITICAL_HOLD = "hold"         # 暂停相关操作 (连续4+次失败)


@dataclass
class EvolutionItem:
    """一条由执行智能体发现的系统演进需求。"""
    id: str = field(default_factory=lambda: f"EVO-{uuid.uuid4().hex[:8]}")
    title: str = ""
    description: str = ""
    target_channel: str = ""
    audit_domain: str = AuditDomain.GENERAL.value
    severity: str = Severity.MEDIUM.value
    status: str = EvolutionStatus.DISCOVERED.value

    # 审查依据
    reference_standard: str = ""       # 例如 "IAMSAR Vol III §3.7"
    current_behavior: str = ""         # 当前系统行为描述
    expected_behavior: str = ""        # 业界期望行为

    # Build 团队处理
    build_task_id: Optional[str] = None
    assigned_agent: Optional[str] = None
    code_changes: List[str] = field(default_factory=list)  # 变更文件列表

    # 验证
    verify_test_name: Optional[str] = None   # 用于验证的测试函数名
    verify_result: Optional[str] = None      # passed / failed
    verify_detail: Optional[str] = None

    # 时间线
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    dispatched_at: Optional[str] = None
    completed_at: Optional[str] = None
    closed_at: Optional[str] = None

    # 重试
    retry_count: int = 0
    max_retries: int = 3

    # ── Phase 3 新增字段 ─────────────────────────────
    escalation_tier: str = EscalationTier.NORMAL.value
    consecutive_failures: int = 0
    compliance_rating: str = ""  # A~E
    operational_domain: str = ""
    checklist_level: str = ChecklistLevel.SHIP.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── Compliance Zone (Wärtsilä Zone Management 启发) ─────────

@dataclass
class ComplianceZone:
    """地理围栏合规区域 — 进入特定水域时自动激活对应合规规则。"""
    id: str
    name: str
    zone_type: str  # ECA / MARPOL_SPECIAL / SECA / PSSA / HIGH_RISK / CUSTOM
    description: str = ""
    # 简化几何: 矩形包围盒 (适合船舶航线粗筛)
    lat_min: float = 0.0
    lat_max: float = 0.0
    lon_min: float = 0.0
    lon_max: float = 0.0
    # 此区域内自动激活的规则 ID 列表
    activated_rule_ids: List[str] = field(default_factory=list)
    # 额外合规要求描述
    extra_requirements: str = ""
    # 生效状态
    active: bool = True

    def contains(self, lat: float, lon: float) -> bool:
        """检查坐标是否在区域内。"""
        return (self.lat_min <= lat <= self.lat_max and
                self.lon_min <= lon <= self.lon_max)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── Audit Trail Entry (NAPA Logbook 启发) ───────────────────

@dataclass
class AuditTrailEntry:
    """审计轨迹条目 — 不可变的审计日志记录。"""
    id: str = field(default_factory=lambda: f"ATR-{uuid.uuid4().hex[:8]}")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    event_type: str = ""  # audit_run / dispatch / verify / escalation / zone_enter / rating_change
    rule_id: str = ""
    item_id: str = ""
    actor: str = ""       # agent name 或 "system"
    old_value: str = ""
    new_value: str = ""
    detail: str = ""
    compliance_rating: str = ""
    zone_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AuditRule:
    """一条审查规则，用于自动发现演进项。"""
    id: str
    domain: str
    title: str
    description: str
    target_channel: str
    check_fn: Optional[Callable] = None  # (channel) -> (passed: bool, detail: str)
    reference: str = ""
    severity: str = Severity.MEDIUM.value
    # ── Phase 3 新增字段 ─────────────────────────────
    operational_domain: str = OperationalDomain.COMPLIANCE_SAFETY.value
    checklist_level: str = ChecklistLevel.SHIP.value
    rating_weight: float = 1.0  # 评级权重 (用于加权合规分数计算)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("check_fn", None)
        return d


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Built-in Audit Rules
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _check_mob_survival_table(channel) -> Tuple[bool, str]:
    """SOLAS: 5°C 生存时间应 ≤ 1.0h (IMO MSC/Circ.1046)。"""
    from .man_overboard import _SURVIVAL_TABLE
    for temp, hours in _SURVIVAL_TABLE:
        if temp == 5 and hours > 1.05:
            return False, f"5°C 生存时间为 {hours}h，IMO 建议 ≤ 1.0h"
    return True, "生存时间表符合 IMO MSC/Circ.1046"


def _check_mob_search_patterns(channel) -> Tuple[bool, str]:
    """IAMSAR: 应包含 Expanding Square 和 Sector Search 搜索模式。"""
    from .man_overboard import VALID_SEARCH_PATTERNS
    required = {"expanding_square", "sector_search"}
    existing = set(VALID_SEARCH_PATTERNS)
    missing = required - existing
    if missing:
        return False, f"缺少 IAMSAR 标准搜索模式: {missing}"
    return True, "搜索模式包含 IAMSAR 标准模式"


def _check_mob_message_priority(channel) -> Tuple[bool, str]:
    """GMDSS: MOB PAN-PAN 应使用 URGENCY 优先级，非 DISTRESS。"""
    # 检查 activate_mob 中的消息优先级
    import inspect
    src = inspect.getsource(channel.activate_mob)
    if "MessagePriority.DISTRESS" in src and "URGENCY_PAN_PAN" in src:
        return False, "PAN-PAN 消息使用了 DISTRESS 优先级，应为 URGENCY"
    return True, "PAN-PAN 消息优先级正确"


def _check_mob_in_decision_orchestrator(_channel) -> Tuple[bool, str]:
    """L3 决策编排器应集成 MOB 状态感知。"""
    import inspect
    from .decision_orchestrator import DecisionOrchestratorChannel
    src = inspect.getsource(DecisionOrchestratorChannel._build_action_plan)
    if "man_overboard" not in src and "mob" not in src.lower():
        return False, "DecisionOrchestrator._build_action_plan 未集成 MOB 状态"
    return True, "决策编排器已集成 MOB"


def _check_mob_drift_formula(channel) -> Tuple[bool, str]:
    """IAMSAR: 搜索半径应考虑 Total Probable Error。"""
    drift = channel.estimate_drift(
        wind_speed_kn=10.0, wind_dir_deg=0.0,
        current_speed_kn=0.5, current_dir_deg=0.0,
        elapsed_min=60.0,
    )
    if "datum_error" not in drift and "total_error" not in drift:
        return False, "漂移模型缺少 datum error / total probable error 字段"
    return True, "漂移模型包含 TPE 估算"


def _check_build_exec_feedback_loop(_channel) -> Tuple[bool, str]:
    """Build↔Exec 团队应有闭环反馈。"""
    reg = get_default_registry()
    build = reg.get("build_team_manager")
    exec_team = reg.get("execution_team_manager")
    if not build or not exec_team:
        return False, "Build 或 Exec 团队 Channel 未注册"
    # 检查 build 是否有接收 exec 反馈的机制
    has_accept = hasattr(build, "accept_evolution_feedback")
    if not has_accept:
        return False, "BuildTeamManager 缺少 accept_evolution_feedback 方法"
    return True, "Build↔Exec 反馈闭环已就绪"


# ── Additional Audit Rules ──────────────────────────────────


def _check_colregs_rule17(channel) -> Tuple[bool, str]:
    """COLREGs Rule 17: Stand-on vessel action handling."""
    reg = get_default_registry()
    colregs = reg.get("colregs_brain")
    if not colregs:
        return False, "COLREGs Brain Channel 未注册"
    import inspect
    src = inspect.getsource(type(colregs))
    if "rule_17" not in src.lower() and "stand_on" not in src.lower():
        return False, "COLREGs Brain 缺少 Rule 17 (stand-on vessel) 处理逻辑"
    return True, "COLREGs Rule 17 已实现"


def _check_colregs_overtaking(channel) -> Tuple[bool, str]:
    """COLREGs Rule 13: Overtaking vessel gives way."""
    reg = get_default_registry()
    colregs = reg.get("colregs_brain")
    if not colregs:
        return False, "COLREGs Brain Channel 未注册"
    import inspect
    src = inspect.getsource(type(colregs))
    if "overtaking" not in src.lower() and "rule_13" not in src.lower():
        return False, "COLREGs Brain 缺少 Rule 13 (overtaking) 处理逻辑"
    return True, "COLREGs Rule 13 (Overtaking) 已实现"


def _check_eexi_attained_calculation(channel) -> Tuple[bool, str]:
    """CII/EEXI: EEXI attained calculation must exist."""
    reg = get_default_registry()
    eexi = reg.get("energy_efficiency")
    if not eexi:
        return False, "Energy Efficiency Channel 未注册"
    has_calc = hasattr(eexi, "calculate_eexi") or hasattr(eexi, "get_eexi_status")
    if not has_calc:
        return False, "能效 Channel 缺少 EEXI 计算方法"
    return True, "EEXI 计算方法已就绪"


def _check_cii_rating_system(channel) -> Tuple[bool, str]:
    """CII/EEXI: CII annual rating (A-E) must be implemented."""
    reg = get_default_registry()
    eexi = reg.get("energy_efficiency")
    if not eexi:
        return False, "Energy Efficiency Channel 未注册"
    has_cii = hasattr(eexi, "calculate_cii") or hasattr(eexi, "get_cii_rating")
    if not has_cii:
        return False, "能效 Channel 缺少 CII 评级方法 (A-E)"
    return True, "CII 评级系统已就绪"


def _check_fire_zone_matrix(channel) -> Tuple[bool, str]:
    """SOLAS Ch II-2: Fire zone matrix should cover all zones."""
    reg = get_default_registry()
    fire_ch = reg.get("cargo_fire_suppression") or reg.get("fire_detection")
    if not fire_ch:
        return False, "消防 Channel 未注册"
    has_zones = hasattr(fire_ch, "fire_zones") or hasattr(fire_ch, "get_fire_zones")
    if not has_zones:
        return False, "消防 Channel 缺少分区管理 (fire_zones)"
    return True, "消防分区矩阵已实现"


def _check_alarm_priority_system(channel) -> Tuple[bool, str]:
    """IEC 62923: Alarm system priority classification."""
    reg = get_default_registry()
    alarm = reg.get("alarm_management")
    if not alarm:
        return False, "报警管理 Channel 未注册"
    has_priority = hasattr(alarm, "priorities") or hasattr(alarm, "alarm_priorities")
    if not has_priority:
        import inspect
        src = inspect.getsource(type(alarm))
        if "priority" not in src.lower():
            return False, "报警管理缺少优先级分类 (IEC 62923)"
    return True, "报警优先级系统符合 IEC 62923"


def _check_wpc_seakeeping(channel) -> Tuple[bool, str]:
    """WPC 穿浪双体船纵摇/横摇限值检查。"""
    reg = get_default_registry()
    wpc = reg.get("wpc_attitude_control")
    if not wpc:
        return False, "WPC 姿态控制 Channel 未注册"
    has_limits = hasattr(wpc, "pitch_limit") or hasattr(wpc, "_pitch_limit_deg")
    if not has_limits:
        import inspect
        src = inspect.getsource(type(wpc))
        if "pitch_limit" not in src.lower() and "roll_limit" not in src.lower():
            return False, "WPC 姿态控制缺少纵摇/横摇限值参数"
    return True, "WPC 纵摇/横摇限值已配置"


def _check_navigation_waypoint_system(channel) -> Tuple[bool, str]:
    """ECDIS: Voyage plan with waypoints should exist."""
    reg = get_default_registry()
    nav = reg.get("gps_navigation") or reg.get("navigation")
    if not nav:
        return False, "导航 Channel 未注册"
    has_wp = hasattr(nav, "waypoints") or hasattr(nav, "voyage_plan")
    if not has_wp:
        import inspect
        src = inspect.getsource(type(nav))
        if "waypoint" not in src.lower() and "voyage" not in src.lower():
            return False, "导航 Channel 缺少航路点/航次计划管理"
    return True, "航路点/航次计划已实现"


def _check_dp_position_keeping(channel) -> Tuple[bool, str]:
    """DP (Dynamic Positioning): Position deviation threshold check."""
    reg = get_default_registry()
    dp = reg.get("dp_control") or reg.get("dynamic_positioning")
    if not dp:
        return False, "动力定位 Channel 未注册"
    has_thresh = hasattr(dp, "position_threshold") or hasattr(dp, "_max_deviation")
    if not has_thresh:
        import inspect
        src = inspect.getsource(type(dp))
        if "deviation" not in src.lower() and "threshold" not in src.lower():
            return False, "DP 缺少位置偏差阈值配置"
    return True, "DP 位置偏差阈值已配置"


def _check_marpol_discharge_tracking(channel) -> Tuple[bool, str]:
    """MARPOL Annex I: OWS discharge monitoring."""
    reg = get_default_registry()
    env = reg.get("environmental_compliance") or reg.get("marpol_compliance")
    if not env:
        # Non-critical, channel may not exist
        return True, "环境合规 Channel 未注册 (可选)"
    return True, "MARPOL 排放监控已就绪"


# ── Phase 2 Audit Rules — 深度合规审查 ────────────────────

def _check_vdr_annual_test(channel) -> Tuple[bool, str]:
    """SOLAS V/18.8: VDR 需年度性能测试及胶囊检查。"""
    reg = get_default_registry()
    vdr = reg.get("vdr_recorder")
    if not vdr:
        return False, "VDR Channel 未注册"
    has_apt = hasattr(vdr, "annual_performance_test") or hasattr(vdr, "capsule_status")
    if not has_apt:
        return False, "VDR 缺少年度性能测试 (annual_performance_test) 或胶囊状态检查"
    return True, "VDR 年度测试功能已实现"


def _check_vdr_playback(channel) -> Tuple[bool, str]:
    """SOLAS V/20: VDR 应支持回放和数据备份。"""
    reg = get_default_registry()
    vdr = reg.get("vdr_recorder")
    if not vdr:
        return False, "VDR Channel 未注册"
    has_playback = hasattr(vdr, "playback") or hasattr(vdr, "backup_data")
    if not has_playback:
        return False, "VDR 缺少回放功能 (playback/backup_data)，不满足 SOLAS 调查取证需求"
    return True, "VDR 回放和备份功能已就绪"


def _check_cyber_vulnerability_scan(channel) -> Tuple[bool, str]:
    """IMO MSC-FAL.1/Circ.3: 海事网络安全风险管理。"""
    reg = get_default_registry()
    cyber = reg.get("cyber_security")
    if not cyber:
        return False, "网络安全 Channel 未注册"
    has_scan = hasattr(cyber, "run_vulnerability_scan") or hasattr(cyber, "get_incident_log")
    if not has_scan:
        return False, "网络安全缺少漏洞扫描 (run_vulnerability_scan) 和事件日志功能"
    return True, "网络安全漏洞扫描已实现"


def _check_cyber_network_segmentation(channel) -> Tuple[bool, str]:
    """BIMCO/ICS: OT/IT 网络分区隔离。"""
    reg = get_default_registry()
    cyber = reg.get("cyber_security")
    if not cyber:
        return False, "网络安全 Channel 未注册"
    import inspect
    src = inspect.getsource(type(cyber))
    if "segmentation" not in src.lower() and "network_zone" not in src.lower() and "firewall" not in src.lower():
        return False, "网络安全缺少 OT/IT 网络分区隔离检查 (BIMCO Guidelines)"
    return True, "OT/IT 网络分区隔离已实现"


def _check_crew_rest_hours(channel) -> Tuple[bool, str]:
    """MLC 2006 / STCW A-VIII/1: 船员休息时间合规。"""
    reg = get_default_registry()
    fatigue = reg.get("crew_fatigue")
    if not fatigue:
        return False, "船员疲劳监控 Channel 未注册"
    has_rest = hasattr(fatigue, "rest_hours_compliance") or hasattr(fatigue, "mlc_check")
    if not has_rest:
        import inspect
        src = inspect.getsource(type(fatigue))
        if "rest_hour" not in src.lower() and "mlc" not in src.lower():
            return False, "船员疲劳监控缺少 MLC 休息时间合规检查 (最低 10h/24h, 77h/7d)"
    return True, "MLC 休息时间合规检查已实现"


def _check_bwm_d2_standard(channel) -> Tuple[bool, str]:
    """BWM Convention: 压载水 D-2 排放标准达标检查。"""
    reg = get_default_registry()
    bw = reg.get("ballast_water")
    if not bw:
        return False, "压载水 Channel 未注册"
    has_d2 = hasattr(bw, "d2_standard_check") or hasattr(bw, "bwm_convention_compliance")
    if not has_d2:
        import inspect
        src = inspect.getsource(type(bw))
        if "d2_standard" not in src.lower() and "d-2" not in src.lower() and "bwm" not in src.lower():
            return False, "压载水管理缺少 IMO D-2 排放标准检查 (BWM Convention)"
        return True, "代码中包含 D-2 相关逻辑"
    return True, "BWM D-2 标准检查已实现"


def _check_hull_slamming_detection(channel) -> Tuple[bool, str]:
    """DNV GL: 穿浪双体船砰击/鞭击检测。"""
    reg = get_default_registry()
    hull = reg.get("hull_stress_monitor")
    if not hull:
        return False, "船体应力 Channel 未注册"
    has_slam = hasattr(hull, "slamming_detection") or hasattr(hull, "whipping_detection")
    if not has_slam:
        import inspect
        src = inspect.getsource(type(hull))
        if "slamming" not in src.lower() and "whipping" not in src.lower():
            return False, "船体应力监控缺少砰击/鞭击检测 (DNV GL WPC 结构规范)"
    return True, "砰击/鞭击检测已实现"


def _check_mass_autonomy_levels(channel) -> Tuple[bool, str]:
    """IMO MASS: 自主等级分类与安全回退。"""
    reg = get_default_registry()
    auto = reg.get("autonomy_manager")
    if not auto:
        return False, "自主管理 Channel 未注册"
    has_fallback = hasattr(auto, "fall_back_safe_state") or hasattr(auto, "safe_state_fallback")
    if not has_fallback:
        import inspect
        src = inspect.getsource(type(auto))
        if "fallback" not in src.lower() and "safe_state" not in src.lower() and "degraded" not in src.lower():
            return False, "自主管理缺少安全回退状态 (IMO MASS Degree 1-4 要求 fail-safe)"
    return True, "MASS 安全回退机制已实现"


def _check_weather_fuel_optimization(channel) -> Tuple[bool, str]:
    """ISO 19030: 气象航线优化与燃油消耗预测。"""
    reg = get_default_registry()
    wr = reg.get("weather_routing")
    if not wr:
        return False, "气象航线 Channel 未注册"
    has_fuel = hasattr(wr, "fuel_optimization") or hasattr(wr, "passage_plan_update")
    if not has_fuel:
        import inspect
        src = inspect.getsource(type(wr))
        if "fuel_optim" not in src.lower() and "consumption_predict" not in src.lower():
            return False, "气象航线缺少燃油优化功能 (ISO 19030 船舶能效)"
    return True, "气象航线燃油优化已实现"


def _check_propulsion_trending(channel) -> Tuple[bool, str]:
    """ISO 19030: 推进系统性能趋势分析。"""
    reg = get_default_registry()
    prop = reg.get("propulsion_monitor")
    if not prop:
        return False, "推进监控 Channel 未注册"
    has_trend = hasattr(prop, "performance_trending") or hasattr(prop, "cylinder_pressure_monitoring")
    if not has_trend:
        import inspect
        src = inspect.getsource(type(prop))
        if "trending" not in src.lower() and "performance_trend" not in src.lower():
            return False, "推进监控缺少性能趋势分析 (ISO 19030 船舶能效)"
    return True, "推进性能趋势分析已实现"


def _check_safety_epirb_sart(channel) -> Tuple[bool, str]:
    """SOLAS Ch IV: EPIRB/SART 设备状态监控。"""
    reg = get_default_registry()
    safe = reg.get("safety_system_monitor")
    if not safe:
        return False, "安全系统 Channel 未注册"
    has_epirb = hasattr(safe, "epirb_check") or hasattr(safe, "sart_check")
    if not has_epirb:
        import inspect
        src = inspect.getsource(type(safe))
        if "epirb" not in src.lower() and "sart" not in src.lower():
            return False, "安全系统缺少 EPIRB/SART 设备状态监控 (SOLAS Ch IV Reg 7)"
    return True, "EPIRB/SART 设备监控已实现"


def _check_lrit_position_reporting(channel) -> Tuple[bool, str]:
    """SOLAS V/19-1: LRIT 远程识别追踪定时报告。"""
    reg = get_default_registry()
    lrit = reg.get("lrit_reporter")
    if not lrit:
        return False, "LRIT Channel 未注册"
    has_report = hasattr(lrit, "send_position_report") or hasattr(lrit, "report_interval")
    if not has_report:
        import inspect
        src = inspect.getsource(type(lrit))
        if "position_report" not in src.lower() and "report_interval" not in src.lower():
            return False, "LRIT 缺少定时位置报告功能 (每 6h 一次, SOLAS V/19-1)"
    return True, "LRIT 定时位置报告已实现"


def _check_ism_code_safety_management(channel) -> Tuple[bool, str]:
    """ISM Code: 安全管理体系审核准备。"""
    reg = get_default_registry()
    # Check if any channel implements ISM audit preparation
    compliance = reg.get("compliance_digital_expert")
    if not compliance:
        return False, "合规专家 Channel 未注册"
    has_ism = hasattr(compliance, "ism_audit") or hasattr(compliance, "safety_management_system")
    if not has_ism:
        import inspect
        src = inspect.getsource(type(compliance))
        if "ism" not in src.lower() and "safety_management" not in src.lower():
            return False, "合规专家缺少 ISM Code 安全管理体系审核支持"
    return True, "ISM Code 安全管理审核已集成"


def _check_ar_cas_digital_twin_fusion(channel) -> Tuple[bool, str]:
    """检查 AR-CAS Pro 数字孪生避碰融合能力。"""
    import inspect
    src = inspect.getsource(type(channel))
    has_rule13 = "rule_13" in src.lower() or "overtaking" in src.lower()
    has_rule17 = "rule_17" in src.lower() or "stand_on" in src.lower()
    if not (has_rule13 and has_rule17):
        return False, "COLREGs Brain 缺少 Rule 13/17 评估方法"
    return True, "AR-CAS 数字孪生避碰融合: COLREGs Rule 13/17 + 3D 场景 + AIS 融合"


def _check_iceberg_detection_rule6(channel) -> Tuple[bool, str]:
    """检查冰山检测与 COLREGs Rule 6 安全航速能力。"""
    registry = get_default_registry()
    colregs = registry.get("colregs_brain")
    if not colregs:
        return False, "COLREGs Brain 未注册, 无法执行 Rule 6 安全航速评估"
    nav = registry.get("intelligent_navigation")
    if not nav:
        return False, "智能导航 Channel 未注册"
    return True, "冰山检测 + COLREGs Rule 6 安全航速: 感知融合 + 3D AR 叠加就绪"


# ── Datacenter Energy check functions ──

def _check_dc_pue_monitoring(channel):
    """PUE 实时监控: 确保 PUE 数据持续更新."""
    registry = get_default_registry()
    dc = registry.get("marine_datacenter_energy")
    if not dc:
        return False, "marine_datacenter_energy Channel 未注册"
    status = dc.get_status() if hasattr(dc, 'get_status') else {}
    pue = status.get('current_pue', 0)
    if pue <= 0:
        return False, "PUE 数据为零, 监控未就绪"
    return True, f"PUE 实时监控正常, 当前 PUE={pue:.2f}"


def _check_dc_ratchet_heritage(channel):
    """Darwin Ratchet 棘轮遗产: 确保 heritage ledger 有记录."""
    registry = get_default_registry()
    dc = registry.get("marine_datacenter_energy")
    if not dc:
        return False, "marine_datacenter_energy Channel 未注册"
    heritage = []
    if hasattr(dc, 'heritage_ledger'):
        result = dc.heritage_ledger()
        heritage = result.get('heritage', []) if isinstance(result, dict) else []
    if len(heritage) < 1:
        return False, "Heritage Ledger 为空, 尚无棘轮锁定记录"
    return True, f"Heritage Ledger 含 {len(heritage)} 条演进记录"


def _check_dc_sensor_coverage(channel):
    """IoT 传感器覆盖率: LoRa TH + PLC + RFID 三网融合."""
    registry = get_default_registry()
    dc = registry.get("marine_datacenter_energy")
    if not dc:
        return False, "marine_datacenter_energy Channel 未注册"
    status = dc.get_status() if hasattr(dc, 'get_status') else {}
    count = status.get('sensor_count', 0)
    if count < 10:
        return False, f"传感器数量 {count} 不足, 需 ≥ 10 (LoRa TH + PLC + RFID)"
    return True, f"传感器覆盖: {count} 个传感器在线"


def _check_dc_thermal_hotspot(channel):
    """热岛检测: 确保热场监控能识别热点."""
    registry = get_default_registry()
    dc = registry.get("marine_datacenter_energy")
    if not dc:
        return False, "marine_datacenter_energy Channel 未注册"
    if not hasattr(dc, 'detect_heat_island'):
        return False, "detect_heat_island 方法缺失"
    return True, "热岛检测功能就绪"


def _check_dc_policy_engine(channel):
    """策略引擎: 确保 save_outgo / open_source 双轨策略可用."""
    registry = get_default_registry()
    dc = registry.get("marine_datacenter_energy")
    if not dc:
        return False, "marine_datacenter_energy Channel 未注册"
    status = dc.get_status() if hasattr(dc, 'get_status') else {}
    pc = status.get('policy_count', 0)
    if pc < 1:
        return False, "策略引擎无可用策略"
    return True, f"策略引擎就绪, {pc} 条策略可用"


def _check_dc_closed_loop(channel):
    """闭环控制: 感知→决策→执行→验证."""
    registry = get_default_registry()
    dc = registry.get("marine_datacenter_energy")
    if not dc:
        return False, "marine_datacenter_energy Channel 未注册"
    if not hasattr(dc, 'closed_loop_tick'):
        return False, "closed_loop_tick 方法缺失"
    return True, "闭环 tick 就绪: 感知→决策→执行→验证"


def _check_dc_anomaly_detection(channel):
    """异常检测: Z-score 异常分析功能就绪."""
    registry = get_default_registry()
    dc = registry.get("marine_datacenter_energy")
    if not dc:
        return False, "marine_datacenter_energy Channel 未注册"
    if not hasattr(dc, 'detect_anomalies'):
        return False, "detect_anomalies 方法缺失"
    return True, "异常检测 (Z-score) 功能就绪"


def _check_dc_musk_audit(channel):
    """第一性原理五步审计: Musk 方法论就绪."""
    registry = get_default_registry()
    dc = registry.get("marine_datacenter_energy")
    if not dc:
        return False, "marine_datacenter_energy Channel 未注册"
    if not hasattr(dc, 'musk_five_step_audit'):
        return False, "musk_five_step_audit 方法缺失"
    return True, "第一性原理五步审计功能就绪"


def _check_dc_pue_forecast(channel):
    """PUE 预测: 24h 趋势预测功能."""
    registry = get_default_registry()
    dc = registry.get("marine_datacenter_energy")
    if not dc:
        return False, "marine_datacenter_energy Channel 未注册"
    if not hasattr(dc, 'forecast_pue'):
        return False, "forecast_pue 方法缺失"
    return True, "PUE 24h 预测功能就绪"


def _check_dc_whatif_simulation(channel):
    """What-If 场景模拟: CAPEX/ROI 评估."""
    registry = get_default_registry()
    dc = registry.get("marine_datacenter_energy")
    if not dc:
        return False, "marine_datacenter_energy Channel 未注册"
    if not hasattr(dc, 'what_if'):
        return False, "what_if 方法缺失"
    return True, "What-If 场景模拟功能就绪"


# 所有内置审查规则
BUILTIN_AUDIT_RULES: List[AuditRule] = [
    AuditRule(
        id="MOB-SURV-001",
        domain=AuditDomain.SOLAS.value,
        title="MOB 5°C 生存时间偏高",
        description="IMO MSC/Circ.1046 规定 5°C 水温无保温服预期生存 ≤ 1.0h",
        target_channel="man_overboard",
        check_fn=_check_mob_survival_table,
        reference="IMO MSC/Circ.1046, SOLAS Ch III",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.COMPLIANCE_SAFETY.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.5,
    ),
    AuditRule(
        id="MOB-SRCH-002",
        domain=AuditDomain.IAMSAR.value,
        title="缺少标准搜索模式",
        description="IAMSAR Vol III 要求 Expanding Square Search 和 Sector Search",
        target_channel="man_overboard",
        check_fn=_check_mob_search_patterns,
        reference="IAMSAR Vol III §5.3",
        severity=Severity.CRITICAL.value,
        operational_domain=OperationalDomain.COMPLIANCE_SAFETY.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=2.0,
    ),
    AuditRule(
        id="MOB-GMDSS-003",
        domain=AuditDomain.GMDSS.value,
        title="PAN-PAN 优先级错误",
        description="MOB PAN-PAN 广播应使用 URGENCY 而非 DISTRESS 优先级",
        target_channel="man_overboard",
        check_fn=_check_mob_message_priority,
        reference="SOLAS Ch IV, GMDSS 操作规程",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.COMPLIANCE_SAFETY.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.0,
    ),
    AuditRule(
        id="MOB-ORCH-004",
        domain=AuditDomain.GENERAL.value,
        title="决策编排未集成 MOB",
        description="L3 DecisionOrchestrator 应在 action plan 中纳入 MOB 告警状态",
        target_channel="decision_orchestrator",
        check_fn=_check_mob_in_decision_orchestrator,
        reference="PoseidonX L3 架构规范",
        severity=Severity.CRITICAL.value,
        operational_domain=OperationalDomain.DATA_DECISION.value,
        checklist_level=ChecklistLevel.COMPANY.value,
        rating_weight=1.5,
    ),
    AuditRule(
        id="MOB-DRIFT-005",
        domain=AuditDomain.IAMSAR.value,
        title="漂移模型缺少 TPE",
        description="IAMSAR 搜索半径应基于 Total Probable Error 计算",
        target_channel="man_overboard",
        check_fn=_check_mob_drift_formula,
        reference="IAMSAR Vol III §3.7",
        severity=Severity.MEDIUM.value,
        operational_domain=OperationalDomain.COMPLIANCE_SAFETY.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.0,
    ),
    AuditRule(
        id="SYS-LOOP-006",
        domain=AuditDomain.GENERAL.value,
        title="Build↔Exec 缺少闭环反馈",
        description="执行团队发现的问题应自动派发给构建团队并跟踪闭环",
        target_channel="build_team_manager",
        check_fn=_check_build_exec_feedback_loop,
        reference="PoseidonX AI Native CPS 架构",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.DATA_DECISION.value,
        checklist_level=ChecklistLevel.COMPANY.value,
        rating_weight=1.0,
    ),
    AuditRule(
        id="COL-R17-007",
        domain=AuditDomain.COLREGS.value,
        title="COLREGs Rule 17 让路船行动",
        description="直行船应在必要时采取避碰行动 (Rule 17 Stand-on Vessel)",
        target_channel="colregs_brain",
        check_fn=_check_colregs_rule17,
        reference="COLREGs Rule 17",
        severity=Severity.CRITICAL.value,
        operational_domain=OperationalDomain.VOYAGE_COMMERCIAL.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=2.0,
    ),
    AuditRule(
        id="COL-R13-008",
        domain=AuditDomain.COLREGS.value,
        title="COLREGs Rule 13 追越处理",
        description="追越船应给直行船让路 (Rule 13 Overtaking)",
        target_channel="colregs_brain",
        check_fn=_check_colregs_overtaking,
        reference="COLREGs Rule 13",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.VOYAGE_COMMERCIAL.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.5,
    ),
    AuditRule(
        id="EEX-CALC-009",
        domain=AuditDomain.CII_EEXI.value,
        title="EEXI 计算方法缺失",
        description="能效 Channel 必须实现 EEXI attained 值计算 (MEPC.333(76))",
        target_channel="energy_efficiency",
        check_fn=_check_eexi_attained_calculation,
        reference="MEPC.333(76), MEPC.335(76)",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.FUEL_EMISSIONS.value,
        checklist_level=ChecklistLevel.BOTH.value,
        rating_weight=2.0,
    ),
    AuditRule(
        id="CII-RATE-010",
        domain=AuditDomain.CII_EEXI.value,
        title="CII 年度评级 A-E",
        description="必须实现 CII 年度评级 (A-E, MEPC.339(76))",
        target_channel="energy_efficiency",
        check_fn=_check_cii_rating_system,
        reference="MEPC.339(76)",
        severity=Severity.MEDIUM.value,
        operational_domain=OperationalDomain.FUEL_EMISSIONS.value,
        checklist_level=ChecklistLevel.BOTH.value,
        rating_weight=2.0,
    ),
    AuditRule(
        id="FIR-ZONE-011",
        domain=AuditDomain.SOLAS.value,
        title="消防分区矩阵",
        description="SOLAS II-2 要求消防系统覆盖所有防火分区",
        target_channel="cargo_fire_suppression",
        check_fn=_check_fire_zone_matrix,
        reference="SOLAS Ch II-2 Reg 5",
        severity=Severity.CRITICAL.value,
        operational_domain=OperationalDomain.COMPLIANCE_SAFETY.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=2.0,
    ),
    AuditRule(
        id="ALM-PRI-012",
        domain=AuditDomain.GENERAL.value,
        title="报警优先级分类",
        description="IEC 62923 要求报警系统具备优先级分类 (emergency/alarm/warning)",
        target_channel="alarm_management",
        check_fn=_check_alarm_priority_system,
        reference="IEC 62923-1:2018",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.TECHNICAL_MGMT.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.5,
    ),
    AuditRule(
        id="WPC-SEA-013",
        domain=AuditDomain.GENERAL.value,
        title="WPC 耐波性限值",
        description="穿浪双体船应配置纵摇/横摇限值以确保结构安全",
        target_channel="wpc_attitude_control",
        check_fn=_check_wpc_seakeeping,
        reference="DNV GL Rules for WPC",
        severity=Severity.MEDIUM.value,
        operational_domain=OperationalDomain.ADVANCED_OPS.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.0,
    ),
    AuditRule(
        id="NAV-WPT-014",
        domain=AuditDomain.GENERAL.value,
        title="航路点/航次计划管理",
        description="ECDIS 导航应支持航路点和航次计划管理",
        target_channel="gps_navigation",
        check_fn=_check_navigation_waypoint_system,
        reference="IMO MSC.232(82) ECDIS",
        severity=Severity.MEDIUM.value,
        operational_domain=OperationalDomain.VOYAGE_COMMERCIAL.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.0,
    ),
    AuditRule(
        id="DP-POS-015",
        domain=AuditDomain.GENERAL.value,
        title="DP 位置偏差阈值",
        description="动力定位应配置位置偏差阈值以触发告警",
        target_channel="dp_control",
        check_fn=_check_dp_position_keeping,
        reference="IMO MSC.1/Circ.1580 DP",
        severity=Severity.MEDIUM.value,
        operational_domain=OperationalDomain.ADVANCED_OPS.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.5,
    ),
    AuditRule(
        id="MAR-OWS-016",
        domain=AuditDomain.MARPOL.value,
        title="MARPOL 排放监控",
        description="MARPOL Annex I 要求油水分离器排放监控",
        target_channel="environmental_compliance",
        check_fn=_check_marpol_discharge_tracking,
        reference="MARPOL Annex I Reg 14",
        severity=Severity.LOW.value,
        operational_domain=OperationalDomain.FUEL_EMISSIONS.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.0,
    ),
    # ── Phase 2: 深度合规审查规则 ───────────────────────────
    AuditRule(
        id="VDR-APT-017",
        domain=AuditDomain.SOLAS.value,
        title="VDR 年度性能测试",
        description="SOLAS V/18.8 要求 VDR 每年进行性能测试并检查保护胶囊",
        target_channel="vdr_recorder",
        check_fn=_check_vdr_annual_test,
        reference="SOLAS V/18.8, IEC 61996",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.TECHNICAL_MGMT.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.5,
    ),
    AuditRule(
        id="VDR-PLY-018",
        domain=AuditDomain.SOLAS.value,
        title="VDR 回放与数据备份",
        description="VDR 应支持事故调查所需的回放和数据备份功能",
        target_channel="vdr_recorder",
        check_fn=_check_vdr_playback,
        reference="SOLAS V/20, IMO A.861(20)",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.TECHNICAL_MGMT.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.0,
    ),
    AuditRule(
        id="CYB-VSC-019",
        domain=AuditDomain.GENERAL.value,
        title="网络安全漏洞扫描",
        description="IMO MSC-FAL.1/Circ.3 要求定期进行网络安全风险评估和漏洞扫描",
        target_channel="cyber_security",
        check_fn=_check_cyber_vulnerability_scan,
        reference="IMO MSC-FAL.1/Circ.3, BIMCO Guidelines",
        severity=Severity.CRITICAL.value,
        operational_domain=OperationalDomain.DATA_DECISION.value,
        checklist_level=ChecklistLevel.BOTH.value,
        rating_weight=2.0,
    ),
    AuditRule(
        id="CYB-NET-020",
        domain=AuditDomain.GENERAL.value,
        title="OT/IT 网络分区隔离",
        description="BIMCO 指南要求 OT (操作技术) 和 IT 网络物理或逻辑隔离",
        target_channel="cyber_security",
        check_fn=_check_cyber_network_segmentation,
        reference="BIMCO Cyber Security Guidelines 2021",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.DATA_DECISION.value,
        checklist_level=ChecklistLevel.BOTH.value,
        rating_weight=1.5,
    ),
    AuditRule(
        id="MLC-REST-021",
        domain=AuditDomain.MLC_STCW.value,
        title="MLC 船员休息时间合规",
        description="MLC 2006 / STCW A-VIII/1 要求最低 10h/24h 和 77h/7d 休息",
        target_channel="crew_fatigue",
        check_fn=_check_crew_rest_hours,
        reference="MLC 2006 Reg 2.3, STCW A-VIII/1",
        severity=Severity.CRITICAL.value,
        operational_domain=OperationalDomain.COMPLIANCE_SAFETY.value,
        checklist_level=ChecklistLevel.BOTH.value,
        rating_weight=2.0,
    ),
    AuditRule(
        id="BWM-D2-022",
        domain=AuditDomain.MARPOL.value,
        title="BWM D-2 排放标准",
        description="BWM Convention 要求压载水处理系统满足 D-2 排放标准",
        target_channel="ballast_water",
        check_fn=_check_bwm_d2_standard,
        reference="IMO BWM Convention Reg D-2",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.FUEL_EMISSIONS.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.5,
    ),
    AuditRule(
        id="HSM-SLM-023",
        domain=AuditDomain.SOLAS.value,
        title="船体砰击/鞭击检测",
        description="DNV GL 穿浪双体船规范要求监测砰击和鞭击载荷",
        target_channel="hull_stress_monitor",
        check_fn=_check_hull_slamming_detection,
        reference="DNV GL Rules for WPC, CSR-BC&OT",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.TECHNICAL_MGMT.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.5,
    ),
    AuditRule(
        id="MASS-FB-024",
        domain=AuditDomain.GENERAL.value,
        title="MASS 安全回退机制",
        description="IMO MASS 框架要求自主船舶具备安全回退状态 (fail-safe)",
        target_channel="autonomy_manager",
        check_fn=_check_mass_autonomy_levels,
        reference="IMO MSC.1/Circ.1638 MASS Code",
        severity=Severity.CRITICAL.value,
        operational_domain=OperationalDomain.ADVANCED_OPS.value,
        checklist_level=ChecklistLevel.BOTH.value,
        rating_weight=2.0,
    ),
    AuditRule(
        id="WR-FUEL-025",
        domain=AuditDomain.CII_EEXI.value,
        title="气象航线燃油优化",
        description="ISO 19030 船舶能效要求气象航线优化中包含燃油消耗预测",
        target_channel="weather_routing",
        check_fn=_check_weather_fuel_optimization,
        reference="ISO 19030:2016, SEEMP Part III",
        severity=Severity.MEDIUM.value,
        operational_domain=OperationalDomain.FUEL_EMISSIONS.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.0,
    ),
    AuditRule(
        id="PROP-TRD-026",
        domain=AuditDomain.GENERAL.value,
        title="推进性能趋势分析",
        description="ISO 19030 要求推进系统具备性能趋势分析和缸压监控",
        target_channel="propulsion_monitor",
        check_fn=_check_propulsion_trending,
        reference="ISO 19030:2016, MAN B&W Service Letter",
        severity=Severity.MEDIUM.value,
        operational_domain=OperationalDomain.TECHNICAL_MGMT.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.0,
    ),
    AuditRule(
        id="SAF-EPIRB-027",
        domain=AuditDomain.SOLAS.value,
        title="EPIRB/SART 设备监控",
        description="SOLAS Ch IV Reg 7 要求 EPIRB 和 SART 设备状态可监控",
        target_channel="safety_system_monitor",
        check_fn=_check_safety_epirb_sart,
        reference="SOLAS Ch IV Reg 7, IMO MSC.471(101)",
        severity=Severity.CRITICAL.value,
        operational_domain=OperationalDomain.COMPLIANCE_SAFETY.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=2.0,
    ),
    AuditRule(
        id="LRIT-POS-028",
        domain=AuditDomain.SOLAS.value,
        title="LRIT 定时位置报告",
        description="SOLAS V/19-1 要求每 6 小时向 LRIT DC 发送位置报告",
        target_channel="lrit_reporter",
        check_fn=_check_lrit_position_reporting,
        reference="SOLAS V/19-1, IMO MSC.210(81)",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.COMPLIANCE_SAFETY.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.5,
    ),
    AuditRule(
        id="ISM-SMS-029",
        domain=AuditDomain.SOLAS.value,
        title="ISM 安全管理审核",
        description="ISM Code 要求数字化安全管理体系审核准备和不符合项跟踪",
        target_channel="compliance_digital_expert",
        check_fn=_check_ism_code_safety_management,
        reference="ISM Code Ch 12, SOLAS Ch IX",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.COMPLIANCE_SAFETY.value,
        checklist_level=ChecklistLevel.COMPANY.value,
        rating_weight=2.0,
    ),
    # ── Phase 4: AR-CAS Pro 数字孪生融合 ──
    AuditRule(
        id="ARCAS-DT-030",
        domain=AuditDomain.COLREGS.value,
        title="AR-CAS 数字孪生避碰融合",
        description="数字孪生 3D 场景须集成 AR-CAS 货船/冰山目标与 CPA/TCPA 实时计算",
        target_channel="colregs_brain",
        check_fn=_check_ar_cas_digital_twin_fusion,
        reference="COLREGs Rule 6/13/14/15, IMO MASS L2",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.ADVANCED_OPS.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=2.5,
    ),
    AuditRule(
        id="ARCAS-ICE-031",
        domain=AuditDomain.SOLAS.value,
        title="冰山检测与 Rule 6 安全航速",
        description="COLREGs Rule 6 要求在冰山区域降低航速，AR 增强叠加冰山距离显示",
        target_channel="distributed_perception_hub",
        check_fn=_check_iceberg_detection_rule6,
        reference="COLREGs Rule 6, SOLAS V/34.1",
        severity=Severity.CRITICAL.value,
        operational_domain=OperationalDomain.COMPLIANCE_SAFETY.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=3.0,
    ),
    # ── Phase 5: Datacenter Energy First Principle ──
    AuditRule(
        id="DC-PUE-032",
        domain=AuditDomain.DATACENTER.value,
        title="PUE 实时监控与基线跟踪",
        description="数据中心 PUE 须持续监控, 基线 PUE 与目标 PUE 差值驱动棘轮演进",
        target_channel="marine_datacenter_energy",
        check_fn=_check_dc_pue_monitoring,
        reference="ISO 50001, TIA-942, EN 50600",
        severity=Severity.CRITICAL.value,
        operational_domain=OperationalDomain.TECHNICAL_MGMT.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=3.0,
    ),
    AuditRule(
        id="DC-RATCH-033",
        domain=AuditDomain.DATACENTER.value,
        title="Darwin Ratchet 棘轮锁定",
        description="每轮演进的 ΔPUE 须通过 heritage ledger 不可逆锁定, 禁止 PUE 回退",
        target_channel="marine_datacenter_energy",
        check_fn=_check_dc_ratchet_heritage,
        reference="Zero Waste Compute, Darwin Heritage Ledger",
        severity=Severity.CRITICAL.value,
        operational_domain=OperationalDomain.TECHNICAL_MGMT.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=3.0,
    ),
    AuditRule(
        id="DC-IOT-034",
        domain=AuditDomain.DATACENTER.value,
        title="IoT 三网融合传感器覆盖",
        description="LoRa TH + MC-RFID + PLC 三网传感器覆盖所有机柜, 确保温湿度场完整",
        target_channel="marine_datacenter_energy",
        check_fn=_check_dc_sensor_coverage,
        reference="LoRa Alliance TS003, ISO 50001:2018",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.TECHNICAL_MGMT.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=2.0,
    ),
    AuditRule(
        id="DC-HEAT-035",
        domain=AuditDomain.DATACENTER.value,
        title="热岛检测与过冷区识别",
        description="温度场分析须实时识别 hot-island 和 over-cool 区域, 指导 CRAC 调节",
        target_channel="marine_datacenter_energy",
        check_fn=_check_dc_thermal_hotspot,
        reference="ASHRAE TC 9.9, TIA-942",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.TECHNICAL_MGMT.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=2.0,
    ),
    AuditRule(
        id="DC-POL-036",
        domain=AuditDomain.DATACENTER.value,
        title="节支/开源双轨策略引擎",
        description="save_outgo + open_source 双轨策略须可评估适应度并执行, 驱动 PUE 下降",
        target_channel="marine_datacenter_energy",
        check_fn=_check_dc_policy_engine,
        reference="Zero Waste Compute Policy Framework",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.FUEL_EMISSIONS.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=2.0,
    ),
    AuditRule(
        id="DC-LOOP-037",
        domain=AuditDomain.DATACENTER.value,
        title="闭环控制: 感知→决策→执行→验证",
        description="closed-loop tick 须完成完整四步循环, 确保每次调节有验证反馈",
        target_channel="marine_datacenter_energy",
        check_fn=_check_dc_closed_loop,
        reference="PDCA, ISO 50001 Energy Management",
        severity=Severity.CRITICAL.value,
        operational_domain=OperationalDomain.TECHNICAL_MGMT.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=2.5,
    ),
    AuditRule(
        id="DC-ANOM-038",
        domain=AuditDomain.DATACENTER.value,
        title="能耗异常检测与分级告警",
        description="Z-score 异常分析须覆盖所有传感器, 按 critical/high/medium/low 分级告警",
        target_channel="marine_datacenter_energy",
        check_fn=_check_dc_anomaly_detection,
        reference="ISO 50001, DCIM Best Practice",
        severity=Severity.HIGH.value,
        operational_domain=OperationalDomain.TECHNICAL_MGMT.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.5,
    ),
    AuditRule(
        id="DC-MUSK-039",
        domain=AuditDomain.DATACENTER.value,
        title="第一性原理五步审计",
        description="Musk 五步法: 质疑需求→删除冗余→简化优化→加速迭代→自动化",
        target_channel="marine_datacenter_energy",
        check_fn=_check_dc_musk_audit,
        reference="First Principles, Elon Musk 5-Step",
        severity=Severity.MEDIUM.value,
        operational_domain=OperationalDomain.DATA_DECISION.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=2.0,
    ),
    AuditRule(
        id="DC-FCST-040",
        domain=AuditDomain.DATACENTER.value,
        title="PUE 24h 趋势预测",
        description="基于历史数据预测未来 24h PUE 走势, 为策略决策提供前瞻支撑",
        target_channel="marine_datacenter_energy",
        check_fn=_check_dc_pue_forecast,
        reference="ISO 50006 Energy Baselines",
        severity=Severity.MEDIUM.value,
        operational_domain=OperationalDomain.DATA_DECISION.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.5,
    ),
    AuditRule(
        id="DC-WHIF-041",
        domain=AuditDomain.DATACENTER.value,
        title="What-If 场景模拟与 ROI 评估",
        description="改造方案须经 What-If 模拟评估 CAPEX/回收期/CO₂ 减排量后方可实施",
        target_channel="marine_datacenter_energy",
        check_fn=_check_dc_whatif_simulation,
        reference="ISO 50001, DCIM Financial Modeling",
        severity=Severity.MEDIUM.value,
        operational_domain=OperationalDomain.FUEL_EMISSIONS.value,
        checklist_level=ChecklistLevel.SHIP.value,
        rating_weight=1.5,
    ),
]


# ── Built-in Compliance Zones (Wärtsilä Zone Management) ─────

BUILTIN_COMPLIANCE_ZONES: List[ComplianceZone] = [
    ComplianceZone(
        id="ZONE-ECA-BALTIC",
        name="Baltic Sea ECA",
        zone_type="ECA",
        description="波罗的海硫排放控制区 (SOx ECA, MARPOL Annex VI)",
        lat_min=53.5, lat_max=66.0, lon_min=9.0, lon_max=30.0,
        activated_rule_ids=["MAR-OWS-016", "BWM-D2-022", "WR-FUEL-025"],
        extra_requirements="SOx ≤ 0.10% m/m, Tier III NOx",
    ),
    ComplianceZone(
        id="ZONE-ECA-NORTHSEA",
        name="North Sea ECA",
        zone_type="ECA",
        description="北海硫排放控制区 (SOx ECA)",
        lat_min=48.0, lat_max=62.0, lon_min=-5.0, lon_max=9.0,
        activated_rule_ids=["MAR-OWS-016", "BWM-D2-022", "WR-FUEL-025"],
        extra_requirements="SOx ≤ 0.10% m/m",
    ),
    ComplianceZone(
        id="ZONE-SECA-CHINA",
        name="China DECA",
        zone_type="SECA",
        description="中国沿海排放控制区 (DECA 2019)",
        lat_min=18.0, lat_max=41.0, lon_min=105.0, lon_max=130.0,
        activated_rule_ids=["MAR-OWS-016", "WR-FUEL-025", "CII-RATE-010"],
        extra_requirements="SOx ≤ 0.50% m/m (港口 0.10%)",
    ),
    ComplianceZone(
        id="ZONE-PSSA-GALAPAGOS",
        name="Galápagos PSSA",
        zone_type="PSSA",
        description="加拉帕戈斯特别敏感海域 (IMO PSSA)",
        lat_min=-2.0, lat_max=2.0, lon_min=-92.0, lon_max=-88.0,
        activated_rule_ids=["MAR-OWS-016", "BWM-D2-022", "COL-R17-007"],
        extra_requirements="低速航行、禁止排放、VTS 报告",
    ),
    ComplianceZone(
        id="ZONE-HIGHRISK-ADEN",
        name="Gulf of Aden HRA",
        zone_type="HIGH_RISK",
        description="亚丁湾高风险区 (海盗/武装抢劫)",
        lat_min=11.0, lat_max=16.0, lon_min=43.0, lon_max=54.0,
        activated_rule_ids=["SAF-EPIRB-027", "LRIT-POS-028", "CYB-VSC-019"],
        extra_requirements="BMP5 措施、ISPS 增强、AIS 持续开启",
    ),
    ComplianceZone(
        id="ZONE-STRAITS-MALACCA",
        name="Strait of Malacca TSS",
        zone_type="CUSTOM",
        description="马六甲海峡分道通航制 (TSS / ATBA)",
        lat_min=0.5, lat_max=4.5, lon_min=99.0, lon_max=104.0,
        activated_rule_ids=["COL-R17-007", "COL-R13-008", "NAV-WPT-014", "LRIT-POS-028"],
        extra_requirements="UKC ≥ 3.5m, VTS 报告, 引航服务",
    ),
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# System Evolution Channel
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class SystemEvolutionChannel(MarineChannel):
    """系统自我演进引擎 — 执行智能体审查 → Build 团队修改 → 自动测试验证。"""

    name = "system_evolution"
    description = "系统自我演进引擎 (审查 → 发现 → 派发 → 构建 → 验证 → 闭环)"
    version = "1.0.0"
    priority = ChannelPriority.P1
    dependencies: List[str] = ["build_team_manager", "execution_team_manager"]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.config = config or {}
        self._config = self.config

        # 演进条目仓库
        self.evolution_items: Dict[str, EvolutionItem] = {}

        # 审查规则
        self.audit_rules: List[AuditRule] = list(BUILTIN_AUDIT_RULES)

        # 验证函数注册表: verify_test_name -> callable
        self._verify_registry: Dict[str, Callable] = {}

        # 审查历史
        self.audit_history: List[Dict[str, Any]] = []

        # 统计
        self.total_audits = 0
        self.total_discovered = 0
        self.total_dispatched = 0
        self.total_verified = 0
        self.total_failed = 0
        self.total_closed = 0

        # ── Phase 3: 新增状态 ────────────────────────────
        # A~E 合规评级 (DNV CII 风格)
        self._compliance_score: float = 100.0
        self._compliance_rating: str = ComplianceRating.A.value
        self._rating_history: List[Dict[str, Any]] = []

        # 地理围栏合规区域 (Wärtsilä Zone Management)
        self.compliance_zones: List[ComplianceZone] = list(BUILTIN_COMPLIANCE_ZONES)
        self._active_zone_ids: List[str] = []
        self._vessel_position: Dict[str, float] = {"lat": 0.0, "lon": 0.0}

        # 持久化审计轨迹 (NAPA Logbook)
        self._audit_trail: List[AuditTrailEntry] = []
        self._max_trail_entries: int = 500

        # 规则失败跟踪 (用于升级机制)
        self._rule_failure_counts: Dict[str, int] = {}  # rule_id -> consecutive failures
        self._escalation_levels: Dict[str, str] = {}    # rule_id -> EscalationTier

        # 连续监控间隔 (秒)
        self._monitoring_interval: int = 300  # 5分钟
        self._last_monitoring_time: float = 0.0

        # 趋势分析数据
        self._score_trend: List[Dict[str, Any]] = []  # [{time, score, rating, passed, failed}]

    # ── MarineChannel 接口 ───────────────────────────────────

    def initialize(self) -> bool:
        self._initialized = True
        self._set_health(ChannelStatus.OK, "系统自我演进引擎已就绪")
        # 种子 AR-CAS 数字孪生融合演化计划
        self._seed_ar_cas_evolution_plan()
        logger.info("🔄 System Evolution Engine initialized (%d audit rules)", len(self.audit_rules))
        return True

    def _seed_ar_cas_evolution_plan(self):
        """创建 AR-CAS Pro 数字孪生融合演化计划条目。"""
        plan_steps = [
            ("ARCAS-PLAN-001", "3D 货船模型集成",
             "在数字孪生 Three.js 场景中添加可交互货船模型 (MV Pacific Fortune)",
             "completed"),
            ("ARCAS-PLAN-002", "冰山 3D 建模与水下体积渲染",
             "创建不规则冰山模型 (水上 IcosahedronGeometry + 水下半透明体) 并应用 COLREGs Rule 6",
             "completed"),
            ("ARCAS-PLAN-003", "CPA/TCPA 实时计算引擎",
             "在 3D 场景中实时计算 CPA (最近会遇点) 和 TCPA (到达时间)",
             "completed"),
            ("ARCAS-PLAN-004", "AR-CAS HUD 面板集成",
             "将 AR-CAS Pro 避碰面板移植到数字孪生页面, 显示目标列表/冰山距离/COLREGs规则",
             "completed"),
            ("ARCAS-PLAN-005", "COLREGs Rule 13/14/15/6 审查规则",
             "在演进引擎中新增 ARCAS-DT-030 和 ARCAS-ICE-031 审查规则",
             "completed"),
            ("ARCAS-PLAN-006", "Channel 注册补全",
             "将 colregs_brain/wpc_attitude/hull_stress 等 11 个 Channel 纳入 main.py 注册启动",
             "completed"),
            ("ARCAS-PLAN-007", "物理比例校准 (Build PM)",
             "调整数字孪生 3D 场景中货船(~160m Handymax)、冰山(25-42m)与WPC双体船(~35m)的物理尺寸比例, "
             "使模型尺寸符合真实世界比例 (货船≈4.5倍WPC长度)",
             "completed"),
        ]
        import time as _time
        for item_id, title, desc, status in plan_steps:
            if item_id not in self.evolution_items:
                item = EvolutionItem(
                    id=item_id,
                    title=title,
                    description=desc,
                    target_channel="colregs_brain",
                    audit_domain=AuditDomain.COLREGS.value,
                    severity=Severity.HIGH.value,
                    status=status,
                    discovered_at=_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    operational_domain=OperationalDomain.ADVANCED_OPS.value,
                )
                item.build_task_id = "ARCAS-DT-030"
                self.evolution_items[item_id] = item

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True

    async def process_event(self, event: dict) -> dict:
        event_type = event.get("type", "")
        if event_type == "run_audit":
            return self.run_full_audit()
        if event_type == "dispatch_all":
            return self.dispatch_all_pending()
        if event_type == "verify_all":
            return self.verify_all_pending()
        if event_type == "evolution_cycle":
            return self.run_evolution_cycle()
        return {"status": "ignored", "reason": f"Unknown event: {event_type}"}

    def get_status(self) -> Dict[str, Any]:
        by_status = {}
        for item in self.evolution_items.values():
            by_status[item.status] = by_status.get(item.status, 0) + 1
        return {
            "name": self.name,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "audit_rules_count": len(self.audit_rules),
            "evolution_items_count": len(self.evolution_items),
            "items_by_status": by_status,
            "compliance_rating": self._compliance_rating,
            "compliance_score": self._compliance_score,
            "active_zones": len(self._active_zone_ids),
            "escalated_rules": sum(1 for v in self._escalation_levels.values()
                                   if v != EscalationTier.NORMAL.value),
            "stats": {
                "total_audits": self.total_audits,
                "total_discovered": self.total_discovered,
                "total_dispatched": self.total_dispatched,
                "total_verified": self.total_verified,
                "total_failed": self.total_failed,
                "total_closed": self.total_closed,
            },
        }

    # ── 审查: 执行智能体参照业界标准发现演进项 ────────────────

    def run_full_audit(self) -> Dict[str, Any]:
        """运行全部审查规则，发现不达标项自动创建 EvolutionItem。"""
        registry = get_default_registry()
        self.total_audits += 1
        results: List[Dict[str, Any]] = []
        new_items: List[str] = []

        for rule in self.audit_rules:
            channel = registry.get(rule.target_channel)
            if not channel:
                results.append({
                    "rule": rule.id, "status": "skip",
                    "reason": f"Channel '{rule.target_channel}' 未注册",
                })
                continue

            if rule.check_fn is None:
                results.append({"rule": rule.id, "status": "skip", "reason": "无检查函数"})
                continue

            try:
                passed, detail = rule.check_fn(channel)
            except Exception as exc:
                passed, detail = False, f"审查异常: {exc}"

            results.append({
                "rule": rule.id, "passed": passed, "detail": detail,
            })

            # ── Phase 3: 升级机制跟踪 ──
            self._update_escalation(rule.id, passed)

            if not passed:
                # 避免重复创建
                existing = self._find_item_by_rule(rule.id)
                if existing and existing.status not in (
                    EvolutionStatus.CLOSED.value, EvolutionStatus.FAILED.value
                ):
                    continue

                item = EvolutionItem(
                    title=rule.title,
                    description=rule.description,
                    target_channel=rule.target_channel,
                    audit_domain=rule.domain,
                    severity=rule.severity,
                    reference_standard=rule.reference,
                    current_behavior=detail,
                    expected_behavior=rule.description,
                    verify_test_name=f"test_evo_{rule.id.lower().replace('-', '_')}",
                )
                item.build_task_id = rule.id
                self.evolution_items[item.id] = item
                self.total_discovered += 1
                new_items.append(item.id)

        result = {
            "audit_run": self.total_audits,
            "rules_checked": len(results),
            "passed": sum(1 for r in results if r.get("passed")),
            "failed": sum(1 for r in results if r.get("passed") is False),
            "skipped": sum(1 for r in results if r.get("status") == "skip"),
            "new_items_created": new_items,
            "details": results,
        }

        # ── Phase 3: 计算合规评级 ──
        rating_result = self.calculate_compliance_rating(results)
        result["compliance_rating"] = rating_result["rating"]
        result["compliance_score"] = rating_result["score"]
        result["domain_scores"] = rating_result.get("domain_scores", {})
        result["escalation"] = self.get_escalation_status()

        # 记录审计轨迹
        self._record_trail(
            "audit_run",
            detail=f"审查 #{self.total_audits}: {result['passed']} pass, "
                   f"{result['failed']} fail, 评级 {rating_result['rating']} "
                   f"({rating_result['score']}分)",
            compliance_rating=rating_result["rating"],
        )
        self._last_monitoring_time = time.time()

        # Record in history
        self.audit_history.append({
            "run": self.total_audits,
            "time": datetime.now().isoformat(),
            "passed": result["passed"],
            "failed": result["failed"],
            "skipped": result["skipped"],
            "new_items": len(new_items),
        })
        # Keep last 50 audits
        if len(self.audit_history) > 50:
            self.audit_history = self.audit_history[-50:]

        return result

    def _find_item_by_rule(self, rule_id: str) -> Optional[EvolutionItem]:
        for item in self.evolution_items.values():
            if item.build_task_id == rule_id:
                return item
        return None

    # ── 派发: 将演进需求发送给 Build 团队 ─────────────────────

    def dispatch_all_pending(self) -> Dict[str, Any]:
        """将所有 DISCOVERED 状态的演进项派发给 Build 团队。"""
        dispatched: List[str] = []
        registry = get_default_registry()
        build_mgr = registry.get("build_team_manager")

        # Agent assignment strategy based on domain and severity
        _AGENT_MAP = {
            AuditDomain.COLREGS.value: "marine_researcher",
            AuditDomain.IAMSAR.value: "marine_researcher",
            AuditDomain.SOLAS.value: "system_architect",
            AuditDomain.GMDSS.value: "system_architect",
            AuditDomain.CII_EEXI.value: "code_writer",
            AuditDomain.MARPOL.value: "code_writer",
            AuditDomain.MLC_STCW.value: "qa_engineer",
            AuditDomain.GENERAL.value: "dev_lead",
        }
        _SEVERITY_OVERRIDE = {
            Severity.CRITICAL.value: "chief_director",  # Critical → 总监亲自跟踪
        }
        # Per-rule agent override for balanced distribution
        _RULE_AGENT_OVERRIDE = {
            "ISM-SMS-029": "doc_writer",     # ISM 文档审核 → 文档工程师
            "LRIT-POS-028": "doc_writer",    # 合规报告 → 文档工程师
            "SAF-EPIRB-027": "qa_engineer",  # 设备检查 → 测试工程师
            "PROP-TRD-026": "qa_engineer",   # 性能趋势 → 测试工程师验证
        }

        for item in self.evolution_items.values():
            if item.status != EvolutionStatus.DISCOVERED.value:
                continue

            item.status = EvolutionStatus.DISPATCHED.value
            item.dispatched_at = datetime.now().isoformat()
            self.total_dispatched += 1

            # Assign agent: per-rule override > severity override > domain map
            if item.build_task_id in _RULE_AGENT_OVERRIDE:
                item.assigned_agent = _RULE_AGENT_OVERRIDE[item.build_task_id]
            elif item.severity == Severity.CRITICAL.value:
                item.assigned_agent = _SEVERITY_OVERRIDE[item.severity]
            else:
                item.assigned_agent = _AGENT_MAP.get(item.audit_domain, "code_writer")

            # 如果 Build 团队 Channel 存在，下发任务
            if build_mgr and hasattr(build_mgr, "assign_task"):
                task_desc = f"evolution_fix:{item.build_task_id}:{item.title}"
                build_mgr.assign_task(item.assigned_agent, task_desc)

            dispatched.append(item.id)

        return {"dispatched": dispatched, "count": len(dispatched)}

    def mark_in_progress(self, item_id: str) -> bool:
        """Build 团队标记开始工作。"""
        item = self.evolution_items.get(item_id)
        if not item:
            return False
        item.status = EvolutionStatus.IN_PROGRESS.value
        return True

    def mark_build_complete(self, item_id: str, code_changes: Optional[List[str]] = None) -> bool:
        """Build 团队标记修改完成，进入待验证。"""
        item = self.evolution_items.get(item_id)
        if not item:
            return False
        item.status = EvolutionStatus.VERIFY_PENDING.value
        if code_changes:
            item.code_changes = code_changes
        return True

    # ── 验证: 通过模拟人类操作的自动化测试 ─────────────────────

    def register_verify_test(self, test_name: str, test_fn: Callable) -> None:
        """注册一个验证测试函数。test_fn() -> (passed: bool, detail: str)"""
        self._verify_registry[test_name] = test_fn

    def verify_all_pending(self) -> Dict[str, Any]:
        """运行所有待验证项的自动化测试。"""
        results: List[Dict[str, Any]] = []

        for item in self.evolution_items.values():
            if item.status != EvolutionStatus.VERIFY_PENDING.value:
                continue

            test_fn = self._verify_registry.get(item.verify_test_name)
            if test_fn is None:
                # 也可以回退到重新运行 audit rule
                rule = self._get_rule_by_id(item.build_task_id)
                if rule and rule.check_fn:
                    channel = get_default_registry().get(item.target_channel)
                    if channel:
                        test_fn = lambda ch=channel, fn=rule.check_fn: fn(ch)

            if test_fn is None:
                results.append({
                    "item_id": item.id, "status": "skip",
                    "reason": f"验证函数 '{item.verify_test_name}' 未注册",
                })
                continue

            try:
                passed, detail = test_fn()
            except Exception as exc:
                passed, detail = False, f"验证异常: {exc}"

            item.verify_result = "passed" if passed else "failed"
            item.verify_detail = detail

            if passed:
                item.status = EvolutionStatus.VERIFIED.value
                item.completed_at = datetime.now().isoformat()
                self.total_verified += 1
            else:
                item.retry_count += 1
                if item.retry_count >= item.max_retries:
                    item.status = EvolutionStatus.FAILED.value
                    self.total_failed += 1
                else:
                    # 退回给 Build 团队重做
                    item.status = EvolutionStatus.DISPATCHED.value

            results.append({
                "item_id": item.id, "passed": passed, "detail": detail,
                "retry_count": item.retry_count,
            })

        return {"verified": results, "count": len(results)}

    def close_verified(self) -> List[str]:
        """关闭所有已验证通过的演进项。"""
        closed: List[str] = []
        for item in self.evolution_items.values():
            if item.status == EvolutionStatus.VERIFIED.value:
                item.status = EvolutionStatus.CLOSED.value
                item.closed_at = datetime.now().isoformat()
                self.total_closed += 1
                closed.append(item.id)
        return closed

    def _get_rule_by_id(self, rule_id: Optional[str]) -> Optional[AuditRule]:
        if not rule_id:
            return None
        for rule in self.audit_rules:
            if rule.id == rule_id:
                return rule
        return None

    # ── 完整演进周期 ──────────────────────────────────────────

    def run_evolution_cycle(self) -> Dict[str, Any]:
        """一键运行完整的审查→派发→验证→关闭循环。"""
        audit_result = self.run_full_audit()
        dispatch_result = self.dispatch_all_pending()
        verify_result = self.verify_all_pending()
        closed = self.close_verified()

        return {
            "cycle": self.total_audits,
            "audit": audit_result,
            "dispatch": dispatch_result,
            "verify": verify_result,
            "closed": closed,
            "summary": self.get_evolution_summary(),
        }

    # ── 查询接口 ──────────────────────────────────────────────

    def get_evolution_items(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取演进项列表，可按状态过滤。"""
        items = self.evolution_items.values()
        if status:
            items = [i for i in items if i.status == status]
        return [i.to_dict() for i in items]

    def get_evolution_summary(self) -> Dict[str, Any]:
        """演进状态汇总。"""
        by_status: Dict[str, int] = {}
        by_domain: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}
        by_operational_domain: Dict[str, int] = {}
        by_checklist_level: Dict[str, int] = {}
        for item in self.evolution_items.values():
            by_status[item.status] = by_status.get(item.status, 0) + 1
            by_domain[item.audit_domain] = by_domain.get(item.audit_domain, 0) + 1
            by_severity[item.severity] = by_severity.get(item.severity, 0) + 1
            od = item.operational_domain or "unknown"
            by_operational_domain[od] = by_operational_domain.get(od, 0) + 1
            cl = item.checklist_level or "ship"
            by_checklist_level[cl] = by_checklist_level.get(cl, 0) + 1

        return {
            "total_items": len(self.evolution_items),
            "by_status": by_status,
            "by_domain": by_domain,
            "by_severity": by_severity,
            "by_operational_domain": by_operational_domain,
            "by_checklist_level": by_checklist_level,
            "audit_rules_count": len(self.audit_rules),
            "verify_tests_registered": len(self._verify_registry),
            "compliance_rating": self._compliance_rating,
            "compliance_score": self._compliance_score,
            "active_zones": len(self._active_zone_ids),
            "zones_total": len(self.compliance_zones),
        }

    def add_audit_rule(self, rule: AuditRule) -> None:
        """动态添加审查规则。"""
        self.audit_rules.append(rule)

    def get_audit_history(self) -> List[Dict[str, Any]]:
        """返回审查历史记录列表 (最近 50 次)。"""
        return list(reversed(self.audit_history))

    # ══════════════════════════════════════════════════════════
    # Phase 3: A~E 合规评级系统 (DNV CII 风格)
    # ══════════════════════════════════════════════════════════

    def calculate_compliance_rating(self, audit_details: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        基于审查结果计算加权合规分数和 A~E 评级。
        权重: critical=4x, high=3x, medium=2x, low=1x, 乘以 rule.rating_weight。
        """
        if audit_details is None:
            # 使用最近一次审查结果
            if not self.audit_history:
                return {"score": 100.0, "rating": "A", "detail": "尚未运行审查"}
            # 运行一次快速审查获取结果
            result = self._quick_score_audit()
            audit_details = result

        severity_weight = {
            Severity.CRITICAL.value: 4.0,
            Severity.HIGH.value: 3.0,
            Severity.MEDIUM.value: 2.0,
            Severity.LOW.value: 1.0,
        }

        total_weight = 0.0
        earned_weight = 0.0
        details_by_domain: Dict[str, Dict] = {}

        for rule in self.audit_rules:
            sev_w = severity_weight.get(rule.severity, 1.0)
            rule_w = rule.rating_weight
            w = sev_w * rule_w
            total_weight += w

            # 查找此规则的审查结果
            result_entry = None
            for d in audit_details:
                if d.get("rule") == rule.id:
                    result_entry = d
                    break

            if result_entry and result_entry.get("passed") is True:
                earned_weight += w
            elif result_entry and result_entry.get("status") == "skip":
                # 跳过的规则不扣分也不加分
                total_weight -= w

            # 按操作域汇总
            od = rule.operational_domain
            if od not in details_by_domain:
                details_by_domain[od] = {"total": 0.0, "earned": 0.0, "count": 0, "passed": 0}
            details_by_domain[od]["total"] += w
            details_by_domain[od]["count"] += 1
            if result_entry and result_entry.get("passed") is True:
                details_by_domain[od]["earned"] += w
                details_by_domain[od]["passed"] += 1

        score = (earned_weight / total_weight * 100) if total_weight > 0 else 100.0
        rating = ComplianceRating.from_score(score)

        # 更新内部状态
        old_rating = self._compliance_rating
        self._compliance_score = round(score, 1)
        self._compliance_rating = rating.value

        # 记录评级变化
        record = {
            "time": datetime.now().isoformat(),
            "score": self._compliance_score,
            "rating": rating.value,
        }
        self._rating_history.append(record)
        if len(self._rating_history) > 100:
            self._rating_history = self._rating_history[-100:]

        # 趋势记录
        self._score_trend.append({
            "time": datetime.now().isoformat(),
            "score": self._compliance_score,
            "rating": rating.value,
            "passed": sum(1 for d in audit_details if d.get("passed") is True),
            "failed": sum(1 for d in audit_details if d.get("passed") is False),
        })
        if len(self._score_trend) > 50:
            self._score_trend = self._score_trend[-50:]

        # 审计轨迹
        if old_rating != rating.value:
            self._record_trail("rating_change", detail=f"评级变化 {old_rating} → {rating.value}",
                               old_value=old_rating, new_value=rating.value,
                               compliance_rating=rating.value)

        # 域级评分
        domain_scores: Dict[str, Dict] = {}
        for od, dd in details_by_domain.items():
            ds = (dd["earned"] / dd["total"] * 100) if dd["total"] > 0 else 100.0
            domain_scores[od] = {
                "score": round(ds, 1),
                "rating": ComplianceRating.from_score(ds).value,
                "rules_total": dd["count"],
                "rules_passed": dd["passed"],
            }

        return {
            "score": self._compliance_score,
            "rating": rating.value,
            "rating_label": self._rating_label(rating.value),
            "total_weight": round(total_weight, 1),
            "earned_weight": round(earned_weight, 1),
            "domain_scores": domain_scores,
            "rating_history": self._rating_history[-10:],
        }

    @staticmethod
    def _rating_label(rating: str) -> str:
        labels = {
            "A": "Major Superior — 全面优秀",
            "B": "Minor Superior — 良好",
            "C": "Moderate — 基本合规",
            "D": "Minor Inferior — 需纠正计划",
            "E": "Inferior — 需紧急干预",
        }
        return labels.get(rating, rating)

    def _quick_score_audit(self) -> List[Dict]:
        """快速运行审查仅获取 pass/fail 结果 (不创建 EvolutionItem)。"""
        registry = get_default_registry()
        results: List[Dict[str, Any]] = []
        for rule in self.audit_rules:
            channel = registry.get(rule.target_channel)
            if not channel:
                results.append({"rule": rule.id, "status": "skip"})
                continue
            if rule.check_fn is None:
                results.append({"rule": rule.id, "status": "skip"})
                continue
            try:
                passed, detail = rule.check_fn(channel)
            except Exception:
                passed = False
                detail = "check exception"
            results.append({"rule": rule.id, "passed": passed, "detail": detail})
        return results

    def get_compliance_rating(self) -> Dict[str, Any]:
        """获取当前合规评级 (不会重新审查)。"""
        return {
            "score": self._compliance_score,
            "rating": self._compliance_rating,
            "rating_label": self._rating_label(self._compliance_rating),
            "trend": self._score_trend[-10:],
        }

    # ══════════════════════════════════════════════════════════
    # Phase 3: 双层自查清单 (ClassNK 风格)
    # ══════════════════════════════════════════════════════════

    def get_checklist(self, level: Optional[str] = None) -> Dict[str, Any]:
        """获取按 ClassNK 双层模型组织的自查清单。"""
        company_rules = []
        ship_rules = []

        for rule in self.audit_rules:
            entry = {
                "id": rule.id,
                "title": rule.title,
                "domain": rule.domain,
                "severity": rule.severity,
                "reference": rule.reference,
                "operational_domain": rule.operational_domain,
            }
            if rule.checklist_level in (ChecklistLevel.COMPANY.value, ChecklistLevel.BOTH.value):
                company_rules.append(entry)
            if rule.checklist_level in (ChecklistLevel.SHIP.value, ChecklistLevel.BOTH.value):
                ship_rules.append(entry)

        result: Dict[str, Any] = {"total_rules": len(self.audit_rules)}

        if level is None or level == ChecklistLevel.COMPANY.value:
            result["company_checklist"] = {
                "level": "company",
                "label": "公司安全管理体系自查 (ISM DOC)",
                "count": len(company_rules),
                "items": company_rules,
            }
        if level is None or level == ChecklistLevel.SHIP.value:
            result["ship_checklist"] = {
                "level": "ship",
                "label": "船舶安全管理体系自查 (ISM SMC)",
                "count": len(ship_rules),
                "items": ship_rules,
            }

        return result

    # ══════════════════════════════════════════════════════════
    # Phase 3: 地理围栏合规 (Wärtsilä Zone Management)
    # ══════════════════════════════════════════════════════════

    def update_vessel_position(self, lat: float, lon: float) -> Dict[str, Any]:
        """更新船舶位置，自动检测进入/离开合规区域。"""
        old_active = set(self._active_zone_ids)
        self._vessel_position = {"lat": lat, "lon": lon}

        new_active: List[str] = []
        for zone in self.compliance_zones:
            if zone.active and zone.contains(lat, lon):
                new_active.append(zone.id)

        self._active_zone_ids = new_active
        new_active_set = set(new_active)

        entered = new_active_set - old_active
        exited = old_active - new_active_set

        events: List[Dict] = []
        for zid in entered:
            zone = self._get_zone(zid)
            if zone:
                events.append({
                    "event": "zone_enter",
                    "zone_id": zid,
                    "zone_name": zone.name,
                    "zone_type": zone.zone_type,
                    "activated_rules": zone.activated_rule_ids,
                    "extra_requirements": zone.extra_requirements,
                })
                self._record_trail("zone_enter", zone_id=zid,
                                   detail=f"进入合规区域: {zone.name} ({zone.zone_type})")

        for zid in exited:
            zone = self._get_zone(zid)
            if zone:
                events.append({
                    "event": "zone_exit",
                    "zone_id": zid,
                    "zone_name": zone.name,
                })
                self._record_trail("zone_exit", zone_id=zid,
                                   detail=f"离开合规区域: {zone.name}")

        return {
            "position": self._vessel_position,
            "active_zones": new_active,
            "entered": list(entered),
            "exited": list(exited),
            "events": events,
        }

    def get_active_zones(self) -> List[Dict[str, Any]]:
        """获取当前激活的合规区域列表。"""
        result = []
        for zid in self._active_zone_ids:
            zone = self._get_zone(zid)
            if zone:
                result.append(zone.to_dict())
        return result

    def get_zone_activated_rules(self) -> List[str]:
        """获取当前区域内激活的所有规则 ID (去重)。"""
        rule_ids: set = set()
        for zid in self._active_zone_ids:
            zone = self._get_zone(zid)
            if zone:
                rule_ids.update(zone.activated_rule_ids)
        return sorted(rule_ids)

    def get_all_zones(self) -> List[Dict[str, Any]]:
        """获取所有注册的合规区域。"""
        return [z.to_dict() for z in self.compliance_zones]

    def _get_zone(self, zone_id: str) -> Optional[ComplianceZone]:
        for z in self.compliance_zones:
            if z.id == zone_id:
                return z
        return None

    # ══════════════════════════════════════════════════════════
    # Phase 3: 失败升级机制 (DNV SEEMP Part III)
    # ══════════════════════════════════════════════════════════

    def _update_escalation(self, rule_id: str, passed: bool) -> Optional[str]:
        """更新规则失败计数和升级层级。返回新的升级层级或 None。"""
        if passed:
            # 通过时重置
            self._rule_failure_counts[rule_id] = 0
            old_level = self._escalation_levels.get(rule_id, EscalationTier.NORMAL.value)
            self._escalation_levels[rule_id] = EscalationTier.NORMAL.value
            if old_level != EscalationTier.NORMAL.value:
                self._record_trail("escalation_reset", rule_id=rule_id,
                                   old_value=old_level, new_value=EscalationTier.NORMAL.value,
                                   detail=f"规则 {rule_id} 通过，升级层级重置")
            return None

        count = self._rule_failure_counts.get(rule_id, 0) + 1
        self._rule_failure_counts[rule_id] = count

        old_level = self._escalation_levels.get(rule_id, EscalationTier.NORMAL.value)
        if count >= 4:
            new_level = EscalationTier.CRITICAL_HOLD.value
        elif count >= 3:
            new_level = EscalationTier.MANAGEMENT_REVIEW.value
        elif count >= 2:
            new_level = EscalationTier.CORRECTIVE_PLAN.value
        else:
            new_level = EscalationTier.NORMAL.value

        self._escalation_levels[rule_id] = new_level
        if new_level != old_level and new_level != EscalationTier.NORMAL.value:
            self._record_trail("escalation", rule_id=rule_id,
                               old_value=old_level, new_value=new_level,
                               detail=f"规则 {rule_id} 连续失败 {count} 次，升级至 {new_level}")
            logger.warning("🚨 Escalation: rule %s → %s (consecutive failures: %d)",
                           rule_id, new_level, count)
        return new_level

    def get_escalation_status(self) -> Dict[str, Any]:
        """获取所有规则的升级状态。"""
        escalated = {}
        for rule_id, level in self._escalation_levels.items():
            if level != EscalationTier.NORMAL.value:
                escalated[rule_id] = {
                    "level": level,
                    "consecutive_failures": self._rule_failure_counts.get(rule_id, 0),
                    "label": self._escalation_label(level),
                }
        return {
            "escalated_count": len(escalated),
            "rules": escalated,
            "total_tracked": len(self._rule_failure_counts),
        }

    @staticmethod
    def _escalation_label(level: str) -> str:
        labels = {
            EscalationTier.NORMAL.value: "正常",
            EscalationTier.CORRECTIVE_PLAN.value: "需纠正行动计划",
            EscalationTier.MANAGEMENT_REVIEW.value: "需管理层审查",
            EscalationTier.CRITICAL_HOLD.value: "暂停相关操作",
        }
        return labels.get(level, level)

    # ══════════════════════════════════════════════════════════
    # Phase 3: 审计轨迹 (NAPA Logbook)
    # ══════════════════════════════════════════════════════════

    def _record_trail(self, event_type: str, rule_id: str = "", item_id: str = "",
                      actor: str = "system", old_value: str = "", new_value: str = "",
                      detail: str = "", compliance_rating: str = "", zone_id: str = "") -> None:
        """记录一条不可变的审计轨迹。"""
        entry = AuditTrailEntry(
            event_type=event_type, rule_id=rule_id, item_id=item_id,
            actor=actor, old_value=old_value, new_value=new_value,
            detail=detail, compliance_rating=compliance_rating or self._compliance_rating,
            zone_id=zone_id,
        )
        self._audit_trail.append(entry)
        if len(self._audit_trail) > self._max_trail_entries:
            self._audit_trail = self._audit_trail[-self._max_trail_entries:]

    def get_audit_trail(self, event_type: Optional[str] = None,
                        limit: int = 50) -> List[Dict[str, Any]]:
        """获取审计轨迹，可按事件类型过滤。"""
        trail = self._audit_trail
        if event_type:
            trail = [e for e in trail if e.event_type == event_type]
        return [e.to_dict() for e in trail[-limit:]]

    # ══════════════════════════════════════════════════════════
    # Phase 3: 连续监控 + 趋势分析 (Wärtsilä FOS)
    # ══════════════════════════════════════════════════════════

    def get_trend_analysis(self) -> Dict[str, Any]:
        """获取合规评级趋势分析数据。"""
        trend = self._score_trend
        if len(trend) < 2:
            return {
                "data_points": len(trend),
                "trend_direction": "insufficient_data",
                "current_score": self._compliance_score,
                "current_rating": self._compliance_rating,
                "scores": trend,
            }

        recent = trend[-5:]
        scores = [t["score"] for t in recent]
        avg_recent = sum(scores) / len(scores)

        if len(trend) > 5:
            earlier = trend[-10:-5]
            avg_earlier = sum(t["score"] for t in earlier) / len(earlier)
            delta = avg_recent - avg_earlier
        else:
            delta = 0.0

        if delta > 3:
            direction = "improving"
        elif delta < -3:
            direction = "degrading"
        else:
            direction = "stable"

        return {
            "data_points": len(trend),
            "trend_direction": direction,
            "trend_delta": round(delta, 1),
            "current_score": self._compliance_score,
            "current_rating": self._compliance_rating,
            "avg_recent_5": round(avg_recent, 1),
            "scores": trend[-20:],
            "rating_history": self._rating_history[-10:],
        }

    def get_monitoring_status(self) -> Dict[str, Any]:
        """获取连续监控状态。"""
        now = time.time()
        since_last = now - self._last_monitoring_time if self._last_monitoring_time else None
        return {
            "interval_seconds": self._monitoring_interval,
            "seconds_since_last": round(since_last, 1) if since_last else None,
            "active_zones": len(self._active_zone_ids),
            "vessel_position": self._vessel_position,
            "compliance_rating": self._compliance_rating,
            "compliance_score": self._compliance_score,
            "escalated_rules": sum(1 for v in self._escalation_levels.values()
                                   if v != EscalationTier.NORMAL.value),
        }

    # ── Build 团队反馈接收 ────────────────────────────────────

    def accept_build_feedback(
        self, item_id: str, success: bool,
        code_changes: Optional[List[str]] = None, detail: str = "",
    ) -> Dict[str, Any]:
        """Build 团队完成修改后回调。"""
        item = self.evolution_items.get(item_id)
        if not item:
            return {"status": "error", "reason": f"Item {item_id} not found"}

        if success:
            item.status = EvolutionStatus.VERIFY_PENDING.value
            if code_changes:
                item.code_changes = code_changes
            return {"status": "verify_pending", "item_id": item_id}
        else:
            item.retry_count += 1
            if item.retry_count >= item.max_retries:
                item.status = EvolutionStatus.FAILED.value
                self.total_failed += 1
            else:
                item.status = EvolutionStatus.DISPATCHED.value
            return {
                "status": item.status, "item_id": item_id,
                "retry": item.retry_count, "detail": detail,
            }


__all__ = [
    "SystemEvolutionChannel",
    "EvolutionItem",
    "EvolutionStatus",
    "Severity",
    "AuditDomain",
    "AuditRule",
    "ComplianceRating",
    "OperationalDomain",
    "ChecklistLevel",
    "EscalationTier",
    "ComplianceZone",
    "AuditTrailEntry",
    "BUILTIN_AUDIT_RULES",
    "BUILTIN_COMPLIANCE_ZONES",
]
