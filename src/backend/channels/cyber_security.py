#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cyber Security Manager - 船舶网络安全管理模块 (SCM)

参考 SVESSEL BIG (onBoard Integrated Gateway):
- 网络安全与访问控制
- 审计日志
- 异常检测
- 数据完整性校验

参考 AUTOSHIP KET:
- Cybersecurity risk assessment
- 安全通信保障
"""

import hashlib
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority


class ThreatLevel(Enum):
    """威胁等级."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AccessRole(Enum):
    """访问角色 (BIG 多级权限)."""
    VIEWER = "viewer"          # 只读
    OPERATOR = "operator"      # 操作员
    OFFICER = "officer"        # 驾驶员
    MASTER = "master"          # 船长
    SHORE_ADMIN = "shore_admin"  # 岸基管理
    SYSTEM = "system"          # 系统内部


class AuditAction(Enum):
    """审计操作类型."""
    LOGIN = "login"
    LOGOUT = "logout"
    COMMAND = "command"
    CONFIG_CHANGE = "config_change"
    DATA_ACCESS = "data_access"
    ALARM_ACK = "alarm_ack"
    AUTONOMY_CHANGE = "autonomy_change"
    LINK_SWITCH = "link_switch"
    THREAT_DETECTED = "threat_detected"
    ACCESS_DENIED = "access_denied"


# 角色权限映射: 角色 -> 允许的操作集合
ROLE_PERMISSIONS: Dict[AccessRole, set] = {
    AccessRole.VIEWER: {"read_status", "read_logs"},
    AccessRole.OPERATOR: {"read_status", "read_logs", "ack_alarm", "send_report"},
    AccessRole.OFFICER: {
        "read_status", "read_logs", "ack_alarm", "send_report",
        "change_route", "change_speed", "manual_override",
    },
    AccessRole.MASTER: {
        "read_status", "read_logs", "ack_alarm", "send_report",
        "change_route", "change_speed", "manual_override",
        "change_autonomy", "emergency_override", "config_change",
    },
    AccessRole.SHORE_ADMIN: {
        "read_status", "read_logs", "ack_alarm", "send_report",
        "change_route", "change_speed", "config_change",
        "change_autonomy", "user_management", "firmware_update",
    },
    AccessRole.SYSTEM: {
        "read_status", "read_logs", "change_route", "change_speed",
        "change_autonomy", "internal_sync",
    },
}


@dataclass
class AuditRecord:
    """审计日志记录."""
    timestamp: str
    action: AuditAction
    user_id: str
    role: AccessRole
    resource: str
    detail: str
    success: bool
    source_ip: str = ""
    session_token_hash: str = ""


@dataclass
class ThreatEvent:
    """威胁事件."""
    timestamp: str
    level: ThreatLevel
    category: str       # "brute_force", "anomaly", "integrity", "spoofing", "port_scan"
    description: str
    source: str
    mitigated: bool = False
    mitigation_action: str = ""


@dataclass
class SessionInfo:
    """用户会话."""
    user_id: str
    role: AccessRole
    token_hash: str
    created_at: float
    last_activity: float
    source_ip: str = ""


class CyberSecurityChannel(MarineChannel):
    """船舶网络安全管理 Channel.

    对标 SVESSEL BIG 安全网关:
    - RBAC 访问控制
    - 完整审计日志
    - 异常行为检测
    - 数据完整性校验
    - 会话管理
    """

    name = "cyber_security"
    description = "船舶网络安全管理 - 访问控制、审计日志与异常检测"
    version = "1.0.0"
    priority = ChannelPriority.P0
    dependencies = []

    SESSION_TIMEOUT_S = 3600  # 1 小时超时

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._audit_log: List[AuditRecord] = []
        self._threat_events: List[ThreatEvent] = []
        self._sessions: Dict[str, SessionInfo] = {}
        self._failed_login_tracker: Dict[str, List[float]] = {}
        self._current_threat_level = ThreatLevel.NONE
        self._data_checksums: Dict[str, str] = {}

    def initialize(self) -> bool:
        self._initialized = True
        self._set_health(ChannelStatus.OK, "Cyber security module active")
        self._record_audit(
            AuditAction.LOGIN, "system", AccessRole.SYSTEM,
            "cyber_security", "模块初始化", True,
        )
        return True

    # ── RBAC ──────────────────────────────────────────────────

    def check_permission(self, user_id: str, role: AccessRole, operation: str) -> bool:
        """检查用户是否有权执行操作."""
        allowed = ROLE_PERMISSIONS.get(role, set())
        granted = operation in allowed
        if not granted:
            self._record_audit(
                AuditAction.ACCESS_DENIED, user_id, role,
                operation, f"权限不足: {role.value} 无法执行 {operation}", False,
            )
        return granted

    def create_session(self, user_id: str, role: AccessRole, source_ip: str = "") -> Optional[str]:
        """创建用户会话，返回 session token (明文，只返回一次)."""
        # 暴力破解检测
        if self._is_brute_force(user_id):
            self._add_threat(
                ThreatLevel.HIGH, "brute_force",
                f"多次登录失败: {user_id}", source_ip,
            )
            return None

        token = secrets.token_hex(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        now = time.time()

        self._sessions[token_hash] = SessionInfo(
            user_id=user_id,
            role=role,
            token_hash=token_hash,
            created_at=now,
            last_activity=now,
            source_ip=source_ip,
        )
        self._record_audit(
            AuditAction.LOGIN, user_id, role,
            "session", f"登录成功 from {source_ip}", True, source_ip, token_hash,
        )
        return token

    def validate_session(self, token: str) -> Optional[SessionInfo]:
        """验证会话 token."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        session = self._sessions.get(token_hash)
        if session is None:
            return None

        now = time.time()
        if now - session.last_activity > self.SESSION_TIMEOUT_S:
            self._sessions.pop(token_hash, None)
            self._record_audit(
                AuditAction.LOGOUT, session.user_id, session.role,
                "session", "会话超时", True,
            )
            return None

        session.last_activity = now
        return session

    def end_session(self, token: str) -> bool:
        """结束会话."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        session = self._sessions.pop(token_hash, None)
        if session:
            self._record_audit(
                AuditAction.LOGOUT, session.user_id, session.role,
                "session", "主动登出", True,
            )
            return True
        return False

    def record_failed_login(self, user_id: str, source_ip: str = "") -> None:
        """记录登录失败 (用于暴力破解检测)."""
        now = time.time()
        if user_id not in self._failed_login_tracker:
            self._failed_login_tracker[user_id] = []
        self._failed_login_tracker[user_id].append(now)
        # 只保留最近 10 分钟
        cutoff = now - 600
        self._failed_login_tracker[user_id] = [
            t for t in self._failed_login_tracker[user_id] if t > cutoff
        ]
        self._record_audit(
            AuditAction.LOGIN, user_id, AccessRole.VIEWER,
            "session", f"登录失败 from {source_ip}", False, source_ip,
        )

    def _is_brute_force(self, user_id: str) -> bool:
        """5 次/10分钟 判定为暴力破解."""
        attempts = self._failed_login_tracker.get(user_id, [])
        now = time.time()
        recent = [t for t in attempts if now - t < 600]
        return len(recent) >= 5

    # ── 审计日志 ──────────────────────────────────────────────

    def _record_audit(
        self,
        action: AuditAction,
        user_id: str,
        role: AccessRole,
        resource: str,
        detail: str,
        success: bool,
        source_ip: str = "",
        token_hash: str = "",
    ) -> None:
        record = AuditRecord(
            timestamp=datetime.now().isoformat(),
            action=action,
            user_id=user_id,
            role=role,
            resource=resource,
            detail=detail,
            success=success,
            source_ip=source_ip,
            session_token_hash=token_hash,
        )
        self._audit_log.append(record)
        if len(self._audit_log) > 5000:
            self._audit_log = self._audit_log[-5000:]

    def record_action(
        self, action: AuditAction, user_id: str, role: AccessRole,
        resource: str, detail: str, success: bool = True,
    ) -> None:
        """外部模块记录审计事件."""
        self._record_audit(action, user_id, role, resource, detail, success)

    def get_audit_log(self, limit: int = 50) -> List[Dict]:
        """获取审计日志."""
        records = self._audit_log[-limit:]
        return [
            {
                "timestamp": r.timestamp,
                "action": r.action.value,
                "user": r.user_id,
                "role": r.role.value,
                "resource": r.resource,
                "detail": r.detail,
                "success": r.success,
            }
            for r in records
        ]

    # ── 威胁检测 ──────────────────────────────────────────────

    def _add_threat(
        self, level: ThreatLevel, category: str,
        description: str, source: str,
    ) -> ThreatEvent:
        event = ThreatEvent(
            timestamp=datetime.now().isoformat(),
            level=level,
            category=category,
            description=description,
            source=source,
        )
        self._threat_events.append(event)
        if len(self._threat_events) > 2000:
            self._threat_events = self._threat_events[-2000:]

        self._record_audit(
            AuditAction.THREAT_DETECTED, "system", AccessRole.SYSTEM,
            "threat_detection", f"[{level.value}] {category}: {description}", True,
        )

        # 更新全局威胁等级
        if level.value in ("high", "critical"):
            self._current_threat_level = level
            self._set_health(ChannelStatus.WARN, f"Threat: {level.value}")

        return event

    def detect_anomaly(self, subsystem: str, metric: str, value: float, threshold: float) -> Optional[Dict]:
        """通用异常检测 — 当 value 超过 threshold 时报告."""
        if value <= threshold:
            return None
        severity = ThreatLevel.MEDIUM if value < threshold * 1.5 else ThreatLevel.HIGH
        event = self._add_threat(
            severity, "anomaly",
            f"{subsystem}.{metric} = {value:.2f} (threshold {threshold:.2f})",
            subsystem,
        )
        return {
            "level": event.level.value,
            "category": event.category,
            "description": event.description,
        }

    def get_threat_summary(self) -> Dict[str, Any]:
        """威胁态势摘要."""
        recent = self._threat_events[-100:]
        by_level = {}
        for e in recent:
            by_level[e.level.value] = by_level.get(e.level.value, 0) + 1

        unmitigated = [e for e in self._threat_events if not e.mitigated]
        return {
            "current_threat_level": self._current_threat_level.value,
            "recent_events_count": len(recent),
            "by_level": by_level,
            "unmitigated_count": len(unmitigated),
            "active_sessions": len(self._sessions),
        }

    # ── 数据完整性 (BIG 数据校验) ────────────────────────────

    def register_checksum(self, data_id: str, data: bytes) -> str:
        """注册数据校验和."""
        digest = hashlib.sha256(data).hexdigest()
        self._data_checksums[data_id] = digest
        return digest

    def verify_checksum(self, data_id: str, data: bytes) -> bool:
        """验证数据完整性."""
        expected = self._data_checksums.get(data_id)
        if expected is None:
            return True  # 未注册不做校验
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            self._add_threat(
                ThreatLevel.HIGH, "integrity",
                f"数据完整性校验失败: {data_id}", data_id,
            )
            return False
        return True

    # ── Channel interface ─────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        return {
            "channel": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": "ok" if self._initialized else "off",
            "threat_level": self._current_threat_level.value,
            "active_sessions": len(self._sessions),
            "audit_entries": len(self._audit_log),
            "threat_events": len(self._threat_events),
            "data_checksums_tracked": len(self._data_checksums),
        }

    def shutdown(self) -> bool:
        # 清理所有会话
        self._sessions.clear()
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shut down")
        return True
