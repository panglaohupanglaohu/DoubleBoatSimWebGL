#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marine DataCenter Energy Channel — 船载数据中心 AI 能耗管理 Channel.

第一性原理 (First Principles, Musk-style):
  能耗 = 物理负载 × 转换损耗 × 散热代价 × 时间利用率
  破除"按机房传统建设"思维：船舶摇晃/盐雾/有限电网/极端散热环境
  → 必须从 设备 / 设施 / 环境 / 流程 4 个视角并行优化
  → 必须形成 监控 → 决策 → 调整 → 验证 的闭环
  → 必须自我演进 (Darwin Ratchet 棘轮：只增不减)

四视角:
  - device:      单机功耗 / 利用率 / PUE 贡献 / 服务密度
  - facility:    机柜 / 配电 / UPS / CRAC / 冷热通道
  - environment: 温度/湿度/盐雾/振动/船摇姿态 (来自 LoRa 传感网)
  - process:     工作负载调度 / 任务编排 / 运维 SOP / 节能策略

IoT 接入:
  - LoRa 温湿度传感器 (低功耗广域)
  - MC-RFID (Multi-Channel RFID 资产盘点)
  - PLC 端 Agent (单板机 + 边缘 LLM 推理)
  - Hub Channel 信息汇总

闭环 + 自演进:
  - SkillLibrary: O&M 经验沉淀 (Lobster-style)
  - PolicyEngine: 开源/节流策略
  - DarwinLedger: 演进遗产 (持久化)
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .marine_base import ChannelPriority, ChannelStatus, MarineChannel


# ───────────────────────────── Enums ─────────────────────────────

class DCPerspective(str, Enum):
    DEVICE = "device"
    FACILITY = "facility"
    ENVIRONMENT = "environment"
    PROCESS = "process"


class IoTKind(str, Enum):
    LORA_TH = "lora_temp_humidity"
    MC_RFID = "mc_rfid"
    PLC_AGENT = "plc_agent"
    POWER_METER = "power_meter"
    FLOW_METER = "flow_meter"


class PolicyKind(str, Enum):
    OPEN_SOURCE = "open_source"   # 开源: 余热回收/光伏/船摇能量
    SAVE_OUTGO = "save_outgo"     # 节流: 调度/休眠/温度松弛


# ───────────────────────────── Dataclasses ─────────────────────────────

@dataclass
class DCDevice:
    device_id: str
    name: str
    rated_power_kw: float
    cpu_util: float = 0.3        # 0..1
    mem_util: float = 0.4
    intake_temp_c: float = 22.0
    healthy: bool = True
    location: str = "rack-A1"
    last_seen: float = field(default_factory=time.time)
    device_type: str = "IT"
    slot_u: int = 1
    power_cap_kw: float = 6.0
    _actual_power_override: float = -1.0   # <0 means use formula

    @property
    def actual_power_kw(self) -> float:
        if self._actual_power_override >= 0:
            return self._actual_power_override
        return self.rated_power_kw * (0.4 + 0.6 * self.cpu_util)

    @actual_power_kw.setter
    def actual_power_kw(self, v: float):
        self._actual_power_override = v


@dataclass
class IoTSensor:
    sensor_id: str
    kind: IoTKind
    location: str
    value: float = 0.0
    unit: str = ""
    battery_pct: float = 95.0
    rssi: int = -78
    last_seen: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OpsSkill:
    """运维技能沉淀 (Lobster-skill 风格)。"""
    skill_id: str
    title: str
    trigger: str          # 触发条件 (自然语言)
    action: str           # 处置动作
    author: str = "ops_team"
    success_count: int = 0
    fail_count: int = 0
    confidence: float = 0.5
    created_at: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)

    def reinforce(self, success: bool):
        if success:
            self.success_count += 1
        else:
            self.fail_count += 1
        n = self.success_count + self.fail_count
        # Bayesian-ish smoothed
        self.confidence = (self.success_count + 1) / (n + 2)


@dataclass
class EnergyPolicy:
    policy_id: str
    kind: PolicyKind
    title: str
    rationale: str
    estimated_saving_kwh_day: float = 0.0
    applied: bool = False
    applied_at: Optional[float] = None
    fitness: float = 0.0   # 实测节能率 0..1


@dataclass
class DarwinHeritage:
    """棘轮遗产 — 只增不减。"""
    heritage_id: str
    title: str
    category: str
    delta_pue: float       # 对 PUE 的累积改进 (负值=改善)
    delta_kwh_day: float
    locked_at: float = field(default_factory=time.time)


# ───────────────────────────── Channel ─────────────────────────────

class MarineDataCenterEnergyChannel(MarineChannel):
    """船载数据中心 AI 能耗管理 Channel."""

    name = "marine_datacenter_energy"
    description = "船载数据中心四视角 AI 能耗管理 + IoT 闭环 + Darwin 自演进"
    version = "1.0.0"
    priority = ChannelPriority.P1

    # 工厂默认值 (避免可变默认共享)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.devices: Dict[str, DCDevice] = {}
        self.sensors: Dict[str, IoTSensor] = {}
        self.skills: Dict[str, OpsSkill] = {}
        self.policies: Dict[str, EnergyPolicy] = {}
        self.heritage: List[DarwinHeritage] = []
        self.events: List[Dict[str, Any]] = []   # 闭环事件记录 (capped)
        self.baseline_pue: float = 1.85
        self.current_pue: float = 1.85
        self.target_pue: float = 1.25
        self._evolution_round: int = 0
        # PUE history (time series)
        self.pue_history: List[Dict[str, float]] = []
        # Cost / benchmark constants
        self.elec_price_cny_per_kwh: float = 0.85   # 工商业大工业电价
        self.benchmark_pue_industry: float = 1.58   # 全球数据中心平均
        self.benchmark_pue_marine: float = 1.95     # 船舶机房平均
        # Auto closed-loop control
        self.auto_loop_enabled: bool = False
        self.auto_loop_interval_s: int = 45

    # ── lifecycle ──
    def initialize(self) -> bool:
        self._seed_devices()
        self._seed_sensors()
        self._seed_skills()
        self._seed_policies()
        self._seed_heritage()
        self._initialized = True
        self._set_health(ChannelStatus.OK, "marine_datacenter_energy ready")
        return True

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "shutdown")
        return True

    # ── seed ──
    def _seed_devices(self):
        import random as _rng
        _rng.seed(42)  # reproducible layout
        # ── Real datacenter layout matching CAD floor plan ──
        # 9 columns (1-8 + B row in center), 8-12 racks each (A-L)
        # AC units around perimeter, PDUs per row pair
        ROWS = list(range(1, 9))         # 1..8
        COLS = list("ABCDEFGH")          # A..H
        device_types = [
            ("Dell R760",     "2U Server",  0.8,  2.5),
            ("HPE DL380",     "2U Server",  0.9,  2.8),
            ("Supermicro 1U", "1U Server",  0.3,  0.9),
            ("GPU A100x2",    "4U AI Node", 1.6,  4.2),
            ("NAS 144TB",     "4U Storage", 0.5,  1.5),
            ("Core Switch",   "1U Network", 0.15, 0.45),
        ]
        # Rack layout: each rack gets 3-6 devices
        for row in ROWS:
            for col in COLS:
                rack_id = f"rack-{row}{col}"
                # pick 3-6 random devices for this rack
                n_dev = _rng.randint(3, 6)
                rack_budget_kw = 6.0
                for slot in range(n_dev):
                    dt = _rng.choice(device_types)
                    did = f"svr-{row}{col}-U{slot*2+1:02d}"
                    pw_rated = dt[2] + _rng.uniform(-0.05, 0.1)
                    d = DCDevice(
                        device_id=did, name=f"{dt[0]} ({row}{col}:U{slot*2+1})",
                        rated_power_kw=round(pw_rated, 2),
                        location=rack_id,
                    )
                    d.actual_power_kw = round(pw_rated * _rng.uniform(0.3, 0.95), 3)
                    d.cpu_util = round(_rng.uniform(0.05, 0.92), 3)
                    d.intake_temp_c = round(20 + _rng.uniform(0, 12), 1)
                    d.power_cap_kw = rack_budget_kw
                    d.device_type = dt[1]
                    d.slot_u = slot * 2 + 1
                    self.devices[did] = d
        # AC units (perimeter)
        for i in range(1, 9):
            did = f"ac-{i}"
            d = DCDevice(device_id=did, name=f"CRAC AC-{i}", rated_power_kw=3.5, location="perimeter")
            d.actual_power_kw = round(3.5 * _rng.uniform(0.5, 0.85), 2)
            d.intake_temp_c = round(18 + _rng.uniform(0, 3), 1)
            d.device_type = "CRAC"
            self.devices[did] = d
        # PDUs (one per row pair)
        for i in range(1, 5):
            did = f"pdu-{i}"
            d = DCDevice(device_id=did, name=f"PDU-{i} (Row {i*2-1}-{i*2})", rated_power_kw=80.0, location=f"pdu-row-{i}")
            d.actual_power_kw = round(80.0 * _rng.uniform(0.3, 0.6), 1)
            d.device_type = "PDU"
            self.devices[did] = d
        # UPS
        for i in range(1, 3):
            did = f"ups-{i}"
            d = DCDevice(device_id=did, name=f"UPS-{i} 40kVA", rated_power_kw=2.0, location="facility")
            d.actual_power_kw = round(2.0 * _rng.uniform(0.3, 0.5), 2)
            d.device_type = "UPS"
            self.devices[did] = d

    def _seed_sensors(self):
        import random as _rng
        _rng.seed(99)
        # LoRA T/H sensors: front+back of every 4th rack (sampling grid)
        ROWS = list(range(1, 9))
        COLS = list("ABCDEFGH")
        for row in ROWS:
            for col in COLS[::2]:  # every other column → 32 sensors
                rack_id = f"rack-{row}{col}"
                for face in ("front", "back"):
                    sid = f"lora-th-{row}{col}-{face[0]}"
                    base_t = 22 + _rng.uniform(0, 10) + (2 if face == "back" else 0)
                    self.sensors[sid] = IoTSensor(
                        sensor_id=sid, kind=IoTKind.LORA_TH,
                        location=f"{rack_id}-{face}",
                        value=round(base_t, 1), unit="°C")
        # humidity sensors in cold aisles
        for row in ROWS[::2]:
            sid = f"lora-rh-aisle-{row}"
            self.sensors[sid] = IoTSensor(
                sensor_id=sid, kind=IoTKind.LORA_TH,
                location=f"cold-aisle-row-{row}",
                value=round(40 + _rng.uniform(0, 15), 1), unit="%RH")
        # RFID + PLC + power meters
        self.sensors["rfid-mc-01"] = IoTSensor(sensor_id="rfid-mc-01", kind=IoTKind.MC_RFID,
                                                location="rack-row-all", value=0.0, unit="tags")
        self.sensors["plc-001"] = IoTSensor(sensor_id="plc-001", kind=IoTKind.PLC_AGENT,
                                             location="facility-pdu-01", value=14.2, unit="kW")
        self.sensors["pmeter-01"] = IoTSensor(sensor_id="pmeter-01", kind=IoTKind.POWER_METER,
                                               location="main-bus", value=18.6, unit="kW")

    def _seed_skills(self):
        seeds = [
            ("skl-th-1", "热点冷却", "rack 后端温度 > 35°C", "提高对应 CRAC 风量 10% + 任务向冷柜迁移", ["thermal","auto"]),
            ("skl-pue-1", "夜间松弛", "00:00-05:00 业务低峰", "送风温度 +1.5°C, AI 推理批合并", ["schedule","ai"]),
            ("skl-rfid-1", "资产闪盘", "运维进入机房刷工牌", "MC-RFID 自动盘点 + 异常资产告警", ["asset","rfid"]),
            ("skl-plc-1",  "PLC 端推理",  "电力波动检测", "PLC-Agent 本地推理 + 边缘自治", ["plc","edge"]),
        ]
        for sid, title, trig, act, tags in seeds:
            sk = OpsSkill(skill_id=sid, title=title, trigger=trig, action=act, tags=tags)
            sk.success_count = 8
            sk.fail_count = 1
            sk.reinforce(True)  # recompute confidence
            self.skills[sid] = sk

    def _seed_policies(self):
        seeds = [
            ("pol-save-01", PolicyKind.SAVE_OUTGO, "AI 推理 DVFS 调频",
             "按 SLA 与温度联动调节 GPU 频率, 利用率<30% 进入低功耗", 4.8),
            ("pol-save-02", PolicyKind.SAVE_OUTGO, "冷热通道封闭复检",
             "夏航/赤道航段强化封闭, 减少 CRAC 短循环", 6.2),
            ("pol-save-03", PolicyKind.SAVE_OUTGO, "夜间任务批合并",
             "把可延迟训练/同步任务排到电网低峰段", 3.4),
            ("pol-open-01", PolicyKind.OPEN_SOURCE, "余热回收预热生活水",
             "CRAC 排热接入生活舱热水预热环路", 5.1),
            ("pol-open-02", PolicyKind.OPEN_SOURCE, "上层甲板光伏补能",
             "300m² 单晶硅, 日均发电 35kWh, 直供 UPS 母线", 35.0),
            ("pol-open-03", PolicyKind.OPEN_SOURCE, "船摇能量回收",
             "压电+液压回收船摇/振动 0.8kW 平均", 19.2),
        ]
        for pid, k, t, r, kwh in seeds:
            self.policies[pid] = EnergyPolicy(policy_id=pid, kind=k, title=t, rationale=r,
                                              estimated_saving_kwh_day=kwh)

    def _seed_heritage(self):
        # 初始遗产: 演进起点
        self.heritage = [
            DarwinHeritage("dh-fp-1", "第一性原理重构", "principle", -0.0, 0.0),
            DarwinHeritage("dh-iot-1", "LoRa+MC-RFID+PLC 三网融合", "iot", -0.05, 8.0),
            DarwinHeritage("dh-loop-1", "监控-决策-调整-验证 闭环", "loop", -0.10, 12.0),
        ]

    # ── 4-perspective analytics ──
    def analyze_perspective(self, perspective: DCPerspective) -> Dict[str, Any]:
        """从指定视角分析能耗结构."""
        if perspective == DCPerspective.DEVICE:
            rows = []
            for d in self.devices.values():
                rows.append({
                    "device_id": d.device_id, "name": d.name, "location": d.location,
                    "rated_kw": d.rated_power_kw, "actual_kw": round(d.actual_power_kw, 3),
                    "cpu_util": d.cpu_util, "intake_temp_c": d.intake_temp_c,
                    "efficiency_score": round((d.cpu_util / max(d.actual_power_kw, 0.01)) * 10, 2),
                })
            total = sum(r["actual_kw"] for r in rows)
            return {"perspective": "device", "total_kw": round(total, 2),
                    "device_count": len(rows), "devices": rows,
                    "insight": "设备视角 — 推理节点功耗占比最高, DVFS 节能潜力 8-15%"}

        if perspective == DCPerspective.FACILITY:
            crac = sum(d.actual_power_kw for d in self.devices.values() if "crac" in d.device_id)
            ups = sum(d.actual_power_kw for d in self.devices.values() if "ups" in d.device_id)
            it = sum(d.actual_power_kw for d in self.devices.values()
                     if not any(k in d.device_id for k in ["crac", "ups"]))
            total = crac + ups + it
            pue = (total / it) if it > 0 else 0
            return {"perspective": "facility",
                    "it_kw": round(it, 2), "crac_kw": round(crac, 2), "ups_kw": round(ups, 2),
                    "total_kw": round(total, 2), "pue": round(pue, 3),
                    "insight": "设施视角 — CRAC 占非IT负载 80%, 冷热通道封闭可降 PUE 0.10-0.15"}

        if perspective == DCPerspective.ENVIRONMENT:
            temps = [s.value for s in self.sensors.values() if s.kind == IoTKind.LORA_TH and s.unit == "°C"]
            rh = [s.value for s in self.sensors.values() if s.unit == "%RH"]
            hotspots = [s.sensor_id for s in self.sensors.values()
                        if s.kind == IoTKind.LORA_TH and s.unit == "°C" and s.value > 32.0]
            return {"perspective": "environment",
                    "temp_avg_c": round(sum(temps) / max(len(temps), 1), 2),
                    "temp_max_c": max(temps) if temps else 0,
                    "rh_avg_pct": round(sum(rh) / max(len(rh), 1), 1) if rh else 0,
                    "hotspot_count": len(hotspots),
                    "hotspot_sensors": hotspots,
                    "ship_motion_factor": 1.08,
                    "salt_fog_alert": False,
                    "insight": "环境视角 — 检测到热点 + 船摇影响, 建议触发 skl-th-1 技能"}

        if perspective == DCPerspective.PROCESS:
            avg_util = sum(d.cpu_util for d in self.devices.values()) / max(len(self.devices), 1)
            applied_pol = [p for p in self.policies.values() if p.applied]
            return {"perspective": "process",
                    "avg_utilization": round(avg_util, 3),
                    "active_policies": len(applied_pol),
                    "skill_library_size": len(self.skills),
                    "process_maturity_pct": round(min(100, len(self.skills) * 8 + len(applied_pol) * 12), 1),
                    "insight": "流程视角 — 调度+SOP 沉淀提升 0.18 PUE, 推荐 pol-save-03 夜间批合并"}

        raise ValueError(f"unknown perspective: {perspective}")

    def four_view_overview(self) -> Dict[str, Any]:
        return {p.value: self.analyze_perspective(p) for p in DCPerspective}

    # ── IoT hub ──
    def ingest_sensor(self, sensor_id: str, value: float, **meta) -> Dict[str, Any]:
        s = self.sensors.get(sensor_id)
        if not s:
            return {"ok": False, "reason": "sensor not found"}
        s.value = value
        s.last_seen = time.time()
        if meta:
            s.metadata.update(meta)
        return {"ok": True, "sensor": sensor_id, "value": value}

    def hub_summary(self) -> Dict[str, Any]:
        kinds: Dict[str, int] = {}
        for s in self.sensors.values():
            kinds[s.kind.value] = kinds.get(s.kind.value, 0) + 1
        return {"total_sensors": len(self.sensors), "by_kind": kinds,
                "uplink_health": "green", "lora_avg_rssi_dbm": -78,
                "rfid_inventory_complete_pct": 98.6,
                "plc_agents_online": sum(1 for s in self.sensors.values()
                                         if s.kind == IoTKind.PLC_AGENT)}

    # ── O&M Skill (Lobster-style) ──
    def add_skill(self, skill_id: str, title: str, trigger: str, action: str,
                  author: str = "ops_team", tags: Optional[List[str]] = None) -> Dict[str, Any]:
        if skill_id in self.skills:
            return {"ok": False, "reason": "exists"}
        self.skills[skill_id] = OpsSkill(skill_id=skill_id, title=title, trigger=trigger,
                                         action=action, author=author, tags=list(tags or []))
        return {"ok": True, "skill_id": skill_id, "library_size": len(self.skills)}

    def reinforce_skill(self, skill_id: str, success: bool) -> Dict[str, Any]:
        sk = self.skills.get(skill_id)
        if not sk:
            return {"ok": False, "reason": "not found"}
        sk.reinforce(success)
        return {"ok": True, "confidence": round(sk.confidence, 3),
                "success": sk.success_count, "fail": sk.fail_count}

    # ── Policies (open source / save outgo) ──
    def apply_policy(self, policy_id: str, fitness: float = 0.85) -> Dict[str, Any]:
        p = self.policies.get(policy_id)
        if not p:
            return {"ok": False, "reason": "not found"}
        p.applied = True
        p.applied_at = time.time()
        p.fitness = max(0.0, min(1.0, fitness))
        # 闭环事件
        self._record_event("policy_applied", {"policy_id": policy_id, "fitness": fitness})
        # 反映到 PUE
        delta = -0.02 * p.fitness if p.kind == PolicyKind.SAVE_OUTGO else -0.015 * p.fitness
        self.current_pue = max(1.05, round(self.current_pue + delta, 3))
        return {"ok": True, "current_pue": self.current_pue,
                "estimated_saving_kwh_day": p.estimated_saving_kwh_day * p.fitness}

    # ── Closed Loop ──
    def closed_loop_tick(self) -> Dict[str, Any]:
        """监控 → 决策 → 调整 → 验证 一次闭环."""
        # 1. 监控: 4 视角快照
        snap = self.four_view_overview()
        # 2. 决策: 选择置信度最高且未应用的策略
        candidates = [p for p in self.policies.values() if not p.applied]
        decided = None
        if candidates:
            decided = max(candidates, key=lambda p: p.estimated_saving_kwh_day)
        # 3. 调整: 应用决策
        adjust_result = None
        if decided:
            adjust_result = self.apply_policy(decided.policy_id, fitness=0.88)
        # 4. 验证: 比对 PUE 变化
        verified = self.current_pue < self.baseline_pue
        self._record_event("closed_loop_tick", {
            "decided_policy": decided.policy_id if decided else None,
            "current_pue": self.current_pue, "verified": verified,
        })
        return {"ok": True, "snapshot": {k: v.get("insight") for k, v in snap.items()},
                "decided_policy": decided.policy_id if decided else None,
                "adjustment": adjust_result, "current_pue": self.current_pue,
                "baseline_pue": self.baseline_pue, "verified": verified}

    # ── Darwin Ratchet ──
    def evolve(self, title: str, category: str, delta_pue: float, delta_kwh_day: float) -> Dict[str, Any]:
        """棘轮: 只增不减. 新增遗产, 永不删除."""
        self._evolution_round += 1
        h = DarwinHeritage(heritage_id=f"dh-{int(time.time())}-{self._evolution_round}",
                           title=title, category=category,
                           delta_pue=delta_pue, delta_kwh_day=delta_kwh_day)
        self.heritage.append(h)
        # 累积应用到当前 PUE
        self.current_pue = max(1.05, round(self.current_pue + delta_pue, 3))
        self._record_event("darwin_evolve", {"heritage_id": h.heritage_id,
                                             "delta_pue": delta_pue})
        return {"ok": True, "heritage_id": h.heritage_id,
                "evolution_round": self._evolution_round,
                "total_heritage": len(self.heritage),
                "cumulative_kwh_day": round(sum(x.delta_kwh_day for x in self.heritage), 2),
                "current_pue": self.current_pue}

    def heritage_ledger(self) -> List[Dict[str, Any]]:
        return [{"heritage_id": h.heritage_id, "title": h.title, "category": h.category,
                 "delta_pue": h.delta_pue, "delta_kwh_day": h.delta_kwh_day,
                 "locked_at": h.locked_at} for h in self.heritage]

    # ── helpers ──
    def _record_event(self, kind: str, data: Dict[str, Any]):
        self.events.append({"ts": time.time(), "kind": kind, "data": data})
        if len(self.events) > 500:
            self.events = self.events[-500:]
        # PUE history snapshot
        self.pue_history.append({"ts": time.time(), "pue": self.current_pue})
        if len(self.pue_history) > 720:   # keep ~6h at 30s resolution
            self.pue_history = self.pue_history[-720:]

    # ── Time-series ──
    def get_pue_history(self, limit: int = 240) -> List[Dict[str, float]]:
        if not self.pue_history:
            # seed with baseline if empty
            now = time.time()
            self.pue_history = [{"ts": now - (10 - i) * 30, "pue": self.baseline_pue}
                                for i in range(10)]
        return self.pue_history[-limit:]

    # ── Energy Sankey (flow data) ──
    def energy_sankey(self) -> Dict[str, Any]:
        """Sankey 流图: 输入电网 → IT/CRAC/UPS-loss → 工作/排热/光伏回流."""
        devices = list(self.devices.values())
        crac_kw = sum(d.actual_power_kw for d in devices if "crac" in d.device_id)
        ups_kw = sum(d.actual_power_kw for d in devices if "ups" in d.device_id)
        it_kw = sum(d.actual_power_kw for d in devices
                    if not any(k in d.device_id for k in ["crac", "ups"]))
        total_in = round(it_kw + crac_kw + ups_kw, 2)
        # Heat output ≈ 95% of IT consumed becomes heat that needs to be removed
        heat_out = round(it_kw * 0.95, 2)
        # Recovered through open-source policies if applied
        recovered = 0.0
        for p in self.policies.values():
            if p.applied and p.kind == PolicyKind.OPEN_SOURCE:
                recovered += p.estimated_saving_kwh_day * p.fitness / 24.0  # avg power kW
        recovered = round(recovered, 2)
        nodes = [
            {"id": "grid",     "label": "船电网/光伏",  "side": "input"},
            {"id": "ups",      "label": "UPS",          "side": "transform"},
            {"id": "it",       "label": "IT 负载",       "side": "transform"},
            {"id": "crac",     "label": "CRAC 制冷",     "side": "transform"},
            {"id": "compute",  "label": "有效算力",      "side": "output"},
            {"id": "heat",     "label": "排热",          "side": "output"},
            {"id": "recover",  "label": "余热/光伏回流", "side": "output"},
        ]
        links = [
            {"source": "grid", "target": "ups",  "value": round(ups_kw, 2)},
            {"source": "grid", "target": "it",   "value": round(it_kw, 2)},
            {"source": "grid", "target": "crac", "value": round(crac_kw, 2)},
            {"source": "it",   "target": "compute", "value": round(it_kw - heat_out * 0.05, 2)},
            {"source": "it",   "target": "heat",    "value": round(heat_out, 2)},
            {"source": "crac", "target": "heat",    "value": round(crac_kw * 0.05, 2)},
        ]
        if recovered > 0:
            links.append({"source": "heat", "target": "recover", "value": recovered})
        return {"total_in_kw": total_in, "heat_out_kw": heat_out,
                "recovered_kw": recovered, "nodes": nodes, "links": links}

    # ── Recommendation engine ──
    def recommend_actions(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """根据当前状态打分排序未应用策略, 给出 top-N AI 建议."""
        recs: List[Dict[str, Any]] = []
        env = self.analyze_perspective(DCPerspective.ENVIRONMENT)
        process = self.analyze_perspective(DCPerspective.PROCESS)
        for p in self.policies.values():
            if p.applied:
                continue
            score = p.estimated_saving_kwh_day * 1.0
            # Boost SAVE_OUTGO when hotspots exist
            if p.kind == PolicyKind.SAVE_OUTGO and env.get("hotspot_count", 0) > 0:
                score *= 1.4
            # Boost OPEN_SOURCE when process maturity is low (need more upside)
            if p.kind == PolicyKind.OPEN_SOURCE and process.get("process_maturity_pct", 0) < 60:
                score *= 1.25
            cost_save_year = p.estimated_saving_kwh_day * 365 * self.elec_price_cny_per_kwh
            recs.append({
                "policy_id": p.policy_id, "title": p.title, "kind": p.kind.value,
                "rationale": p.rationale, "score": round(score, 2),
                "expected_saving_kwh_day": p.estimated_saving_kwh_day,
                "expected_saving_cny_year": round(cost_save_year, 0),
                "expected_co2_saving_ton_year": round(p.estimated_saving_kwh_day * 365 * 0.785 / 1000, 2),
            })
        recs.sort(key=lambda x: x["score"], reverse=True)
        return recs[:top_n]

    # ── Benchmark + Cost ──
    def benchmark(self) -> Dict[str, Any]:
        """与行业基准对比."""
        return {
            "current_pue": self.current_pue,
            "target_pue": self.target_pue,
            "industry_avg_pue": self.benchmark_pue_industry,
            "marine_industry_avg_pue": self.benchmark_pue_marine,
            "world_class_pue": 1.10,
            "vs_industry_pct": round(
                (self.benchmark_pue_industry - self.current_pue) / self.benchmark_pue_industry * 100, 1),
            "vs_marine_pct": round(
                (self.benchmark_pue_marine - self.current_pue) / self.benchmark_pue_marine * 100, 1),
            "to_world_class_gap": round(self.current_pue - 1.10, 3),
        }

    def cost_summary(self) -> Dict[str, Any]:
        """节能 → 钱 / CO₂ 折算."""
        applied = [p for p in self.policies.values() if p.applied]
        kwh_day = sum(p.estimated_saving_kwh_day * p.fitness for p in applied)
        cny_year = kwh_day * 365 * self.elec_price_cny_per_kwh
        co2_ton_year = kwh_day * 365 * 0.785 / 1000
        # Equivalent: trees planted (1 mature tree absorbs ~22kg CO2/yr)
        trees_eq = (co2_ton_year * 1000) / 22.0
        return {
            "saving_kwh_day": round(kwh_day, 2),
            "saving_kwh_year": round(kwh_day * 365, 0),
            "saving_cny_year": round(cny_year, 0),
            "saving_cny_year_per_man": round(cny_year / max(len(applied), 1), 0),
            "co2_ton_year": round(co2_ton_year, 2),
            "tree_equivalent": round(trees_eq, 0),
            "elec_price_cny_per_kwh": self.elec_price_cny_per_kwh,
        }

    # ── Single device drill-down ──
    def get_device_detail(self, device_id: str) -> Optional[Dict[str, Any]]:
        d = self.devices.get(device_id)
        if not d:
            return None
        # nearby sensors at same location prefix (rack-X)
        loc_prefix = d.location.split("-")[0] + "-" + d.location.split("-")[1] if "-" in d.location else d.location
        nearby = [{"sensor_id": s.sensor_id, "kind": s.kind.value, "value": s.value, "unit": s.unit}
                  for s in self.sensors.values() if loc_prefix in s.location]
        return {
            "device_id": d.device_id, "name": d.name, "location": d.location,
            "rated_power_kw": d.rated_power_kw, "actual_power_kw": round(d.actual_power_kw, 3),
            "cpu_util": d.cpu_util, "mem_util": d.mem_util,
            "intake_temp_c": d.intake_temp_c, "healthy": d.healthy,
            "last_seen_ts": d.last_seen, "nearby_sensors": nearby,
        }

    def list_devices(self) -> List[Dict[str, Any]]:
        return [
            {"device_id": d.device_id, "name": d.name, "location": d.location,
             "device_type": getattr(d, 'device_type', 'IT'),
             "slot_u": getattr(d, 'slot_u', 1),
             "power_cap_kw": getattr(d, 'power_cap_kw', 6.0),
             "rated_power_kw": d.rated_power_kw,
             "actual_power_kw": round(d.actual_power_kw, 3),
             "cpu_util": d.cpu_util, "intake_temp_c": d.intake_temp_c,
             "healthy": d.healthy}
            for d in self.devices.values()
        ]

    # ── Auto closed-loop control ──
    def set_auto_loop(self, enabled: bool, interval_s: int = 45) -> Dict[str, Any]:
        self.auto_loop_enabled = bool(enabled)
        self.auto_loop_interval_s = max(10, int(interval_s))
        self._record_event("auto_loop_config", {"enabled": self.auto_loop_enabled,
                                                 "interval_s": self.auto_loop_interval_s})
        return {"ok": True, "enabled": self.auto_loop_enabled,
                "interval_s": self.auto_loop_interval_s}

    # ── AI Insight (template-based, optional LLM via bridge-chat upstream) ──
    def ai_insight(self, focus: str = "") -> Dict[str, Any]:
        st = self.get_status()
        env = self.analyze_perspective(DCPerspective.ENVIRONMENT)
        recs = self.recommend_actions(top_n=3)
        bench = self.benchmark()
        bullets = [
            f"当前 PUE {st['current_pue']} (基线 {st['baseline_pue']} → 目标 {st['target_pue']}), 已达成 {st['pue_progress_pct']}% 路径",
            f"环境: 温度均值 {env['temp_avg_c']}°C, 热点 {env['hotspot_count']} 处, 船摇影响系数 {env.get('ship_motion_factor', 1.0)}",
            f"对比行业平均 PUE={bench['industry_avg_pue']}, 当前 优于 {bench['vs_industry_pct']}%",
            f"已沉淀 {st['skill_count']} 条运维 Skill, 演进 {st['evolution_round']} 轮, 锁定遗产 {st['heritage_count']} 项",
        ]
        if recs:
            r = recs[0]
            bullets.append(f"AI 建议优先执行: 「{r['title']}」, 预期年节省 {r['expected_saving_cny_year']:.0f} CNY / "
                           f"{r['expected_co2_saving_ton_year']:.2f} t CO₂")
        if focus:
            bullets.append(f"用户关注: {focus}")
        return {"ok": True, "summary": " · ".join(bullets[:2]),
                "bullets": bullets, "top_recommendations": recs[:3],
                "generated_at": time.time()}

    # ── Forecast (24h PUE projection) ──
    def forecast_pue(self, hours: int = 24, sample_step_min: int = 30) -> Dict[str, Any]:
        """简单 24 小时 PUE 预测 (基于负载日变化 + 已应用策略).

        模型: pue(t) = current_pue + util_factor * sin(2π*(t-14)/24) * 0.04
              - util_factor 反映白天高峰
              - 已应用 SAVE_OUTGO 策略每条 -0.005
              - 已应用 OPEN_SOURCE 策略每条 -0.003
        """
        import math
        steps = max(1, int((hours * 60) / max(sample_step_min, 5)))
        applied_save = sum(1 for p in self.policies.values()
                           if p.applied and p.kind == PolicyKind.SAVE_OUTGO)
        applied_open = sum(1 for p in self.policies.values()
                           if p.applied and p.kind == PolicyKind.OPEN_SOURCE)
        baseline = self.current_pue - applied_save * 0.005 - applied_open * 0.003
        baseline = max(self.target_pue, baseline)
        now = time.time()
        points: List[Dict[str, float]] = []
        for i in range(steps + 1):
            t_offset_h = i * sample_step_min / 60.0
            hour_of_day = (datetime.fromtimestamp(now + t_offset_h * 3600).hour
                           + t_offset_h % 1)
            util = 0.5 + 0.4 * math.sin(2 * math.pi * (hour_of_day - 6) / 24)
            pue_pred = round(baseline + 0.04 * util, 3)
            points.append({
                "ts": round(now + t_offset_h * 3600, 1),
                "pue": pue_pred,
                "load_factor": round(util, 3),
            })
        peak = max(points, key=lambda p: p["pue"])
        valley = min(points, key=lambda p: p["pue"])
        return {
            "horizon_hours": hours,
            "step_min": sample_step_min,
            "points": points,
            "peak": peak,
            "valley": valley,
            "expected_avg_pue": round(sum(p["pue"] for p in points) / len(points), 3),
            "applied_save_policies": applied_save,
            "applied_open_policies": applied_open,
        }

    # ── Anomaly Detection (z-score on env sensors + device temp/util) ──
    def detect_anomalies(self, z_threshold: float = 2.0) -> Dict[str, Any]:
        """检测温度热点、设备过载、传感器离线异常.

        使用简单 z-score (无依赖 numpy/scipy).
        """
        anomalies: List[Dict[str, Any]] = []
        # 1. 温度传感器热点
        temps = [(s.sensor_id, s.value, s.location)
                 for s in self.sensors.values()
                 if s.kind == IoTKind.LORA_TH and s.unit == "°C"]
        if len(temps) >= 2:
            vals = [t[1] for t in temps]
            mean = sum(vals) / len(vals)
            var = sum((v - mean) ** 2 for v in vals) / len(vals)
            std = var ** 0.5 or 0.001
            for sid, v, loc in temps:
                z = (v - mean) / std
                if z >= z_threshold or v > 35.0:
                    anomalies.append({
                        "kind": "thermal_hotspot",
                        "sensor_id": sid, "location": loc,
                        "value": round(v, 2), "z_score": round(z, 2),
                        "severity": "high" if v > 38.0 else "medium",
                        "suggested_action": "提高对应 CRAC 风量 + 任务向冷柜迁移 (skl-th-1)",
                    })
        # 2. 设备过载
        for d in self.devices.values():
            if d.actual_power_kw > d.rated_power_kw * 0.9:
                anomalies.append({
                    "kind": "device_overload",
                    "device_id": d.device_id, "name": d.name,
                    "actual_kw": round(d.actual_power_kw, 3),
                    "rated_kw": d.rated_power_kw,
                    "utilization_pct": round(100 * d.actual_power_kw / d.rated_power_kw, 1),
                    "severity": "high",
                    "suggested_action": "DVFS 降频 / 任务迁移 (pol-save-01)",
                })
        # 3. 设备健康
        for d in self.devices.values():
            if not d.healthy:
                anomalies.append({
                    "kind": "device_unhealthy",
                    "device_id": d.device_id, "name": d.name,
                    "severity": "critical",
                    "suggested_action": "立即派发运维, 切换备机",
                })
        # 4. 传感器离线 (last_seen > 600s)
        now = time.time()
        for s in self.sensors.values():
            if (now - s.last_seen) > 600:
                anomalies.append({
                    "kind": "sensor_offline",
                    "sensor_id": s.sensor_id, "kind_name": s.kind.value,
                    "last_seen_ago_s": round(now - s.last_seen, 1),
                    "severity": "low",
                    "suggested_action": "检查 LoRa 链路 / 电池",
                })
        # 5. PUE 漂移
        if self.current_pue > self.baseline_pue + 0.05:
            anomalies.append({
                "kind": "pue_drift",
                "current_pue": self.current_pue,
                "baseline_pue": self.baseline_pue,
                "delta": round(self.current_pue - self.baseline_pue, 3),
                "severity": "medium",
                "suggested_action": "触发闭环 tick + 检查策略执行情况",
            })
        return {
            "ok": True,
            "total": len(anomalies),
            "by_severity": {
                "critical": sum(1 for a in anomalies if a["severity"] == "critical"),
                "high": sum(1 for a in anomalies if a["severity"] == "high"),
                "medium": sum(1 for a in anomalies if a["severity"] == "medium"),
                "low": sum(1 for a in anomalies if a["severity"] == "low"),
            },
            "anomalies": anomalies,
            "scanned_at": time.time(),
        }

    # ── What-If Simulation ──
    def what_if(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """对一组假设策略进行模拟 (不修改真实状态), 返回预期 PUE / 节能 / 投资回收期.

        scenarios = [{"policy_id": "pol-save-01", "fitness": 0.9}, ...]
                  或 [{"delta_pue": -0.05, "delta_kwh_day": 5.0, "capex_cny": 50000, "title": "..."}]
        """
        sim_pue = self.current_pue
        total_kwh_day = 0.0
        total_capex = 0.0
        results: List[Dict[str, Any]] = []
        for sc in scenarios or []:
            pid = sc.get("policy_id")
            if pid and pid in self.policies:
                p = self.policies[pid]
                fit = float(sc.get("fitness", 0.85))
                kwh = p.estimated_saving_kwh_day * fit
                d_pue = -0.01 * fit
                title = p.title
                capex = float(sc.get("capex_cny", 0.0))
            else:
                d_pue = float(sc.get("delta_pue", 0.0))
                kwh = float(sc.get("delta_kwh_day", 0.0))
                title = sc.get("title", "custom")
                capex = float(sc.get("capex_cny", 0.0))
            sim_pue = max(self.target_pue * 0.95, round(sim_pue + d_pue, 3))
            total_kwh_day += kwh
            total_capex += capex
            results.append({
                "title": title,
                "delta_pue": round(d_pue, 4),
                "saving_kwh_day": round(kwh, 2),
                "capex_cny": capex,
            })
        annual_save_cny = total_kwh_day * 365 * self.elec_price_cny_per_kwh
        payback_years = (total_capex / annual_save_cny) if annual_save_cny > 0 else None
        return {
            "ok": True,
            "scenario_count": len(results),
            "scenarios": results,
            "current_pue": self.current_pue,
            "projected_pue": sim_pue,
            "delta_pue_total": round(sim_pue - self.current_pue, 3),
            "saving_kwh_day_total": round(total_kwh_day, 2),
            "saving_kwh_year_total": round(total_kwh_day * 365, 0),
            "saving_cny_year_total": round(annual_save_cny, 0),
            "co2_ton_year_total": round(total_kwh_day * 365 * 0.785 / 1000, 2),
            "total_capex_cny": total_capex,
            "payback_years": round(payback_years, 2) if payback_years is not None else None,
        }

    # ── Sensing Layer (Page 2): LoRA 热场 + AI 热岛检测 + PLC 闭环 ──
    def _sensor_coords(self, sensor_id: str, location: str) -> Dict[str, float]:
        """从 sensor_id/location 派生物理坐标 (X,Y,Z in meters).

        机房布局: 8 行 × 8 列 rack (rows 1-8, cols A-H).
        Scene: ROOM_W=80, ROOM_D=50, rackPos(row,col):
          x = -32 + (row-1)*8.5
          z = -14 + colIdx*3.2 + (colIdx>=4 ? 4.5 : 0)
        """
        col_map = {c: i for i, c in enumerate("ABCDEFGH")}
        AISLE_W = 4.5
        loc = (location or "")
        # default center
        x, y, z = 0.0, 1.5, 0.0
        import re
        # parse "rack-1A-front" / "rack-8H-back"  (row=digit, col=letter)
        m = re.search(r"rack-(\d+)([A-Ha-h])-(front|back)", loc)
        if m:
            row, col, face = int(m.group(1)), m.group(2).upper(), m.group(3)
            col_idx = col_map.get(col, 0)
            x = -32.0 + (row - 1) * 8.5
            z = -14.0 + col_idx * 3.2 + (AISLE_W if col_idx >= 4 else 0.0)
            if face == "front":
                z -= 1.2
            else:
                z += 1.2
            y = 2.0 + (hash(sensor_id) % 3) * 0.9
            return {"x": round(x, 2), "y": round(y, 2), "z": round(z, 2)}
        # parse "cold-aisle-row-3" (new format)
        m = re.search(r"(cold|hot)-aisle-row-(\d+)", loc)
        if m:
            face, row = m.group(1), int(m.group(2))
            x = -32.0 + (row - 1) * 8.5
            z = -14.0 + 3 * 3.2 + (-2.0 if face == "cold" else AISLE_W + 2.0)
            y = 1.2
            return {"x": round(x, 2), "y": round(y, 2), "z": round(z, 2)}
        # legacy: "cold-aisle-A" / "hot-aisle-B"
        m = re.search(r"(cold|hot)-aisle-([A-Ha-h])", loc)
        if m:
            face, col = m.group(1), m.group(2).upper()
            col_idx = col_map.get(col, 0)
            z = -14.0 + col_idx * 3.2 + (AISLE_W if col_idx >= 4 else 0.0)
            z += (-2.0 if face == "cold" else 2.0)
            x = 0.0
            y = 1.2
            return {"x": round(x, 2), "y": round(y, 2), "z": round(z, 2)}
        # facility sensors → corners
        if "pdu" in loc.lower() or "facility" in loc.lower():
            return {"x": -22.0, "y": 1.4, "z": -14.0}
        if "main-bus" in loc.lower() or "bus" in loc.lower():
            return {"x": 22.0, "y": 1.4, "z": -14.0}
        if "row" in loc.lower():
            m = re.search(r"row-(\d+)", loc)
            if m:
                row = int(m.group(1))
                x = -32.0 + (row - 1) * 8.5
                return {"x": round(x, 2), "y": 0.8, "z": 0.0}
        return {"x": x, "y": y, "z": z}

    def sensor_field(self) -> Dict[str, Any]:
        """返回所有 LoRA 传感器 + X/Y/Z + 热场分类.

        用于前端 GPU Shader 插值渲染 (Page 2 极智感知层).
        """
        import re
        sensors = []
        for s in self.sensors.values():
            coord = self._sensor_coords(s.sensor_id, s.location)
            kind_label = s.kind.value
            cls = "normal"
            if s.kind == IoTKind.LORA_TH and s.unit == "°C":
                if s.value >= 33.0:
                    cls = "hotspot"
                elif s.value >= 29.0:
                    cls = "warm"
                elif s.value < 20.5:
                    cls = "overcool"
                else:
                    cls = "normal"
            # bind to nearest MC-RFID asset (same rack prefix)
            bound_asset = None
            m = re.search(r"rack-([a-d]\d)", s.location.lower())
            if m:
                rack = m.group(1).upper()
                for d in self.devices.values():
                    if d.location.upper().endswith(rack):
                        bound_asset = d.device_id
                        break
            sensors.append({
                "sensor_id": s.sensor_id,
                "kind": kind_label,
                "location": s.location,
                "coord": coord,
                "value": round(s.value, 2),
                "unit": s.unit,
                "battery_pct": s.battery_pct,
                "rssi": s.rssi,
                "classification": cls,
                "bound_asset": bound_asset,
                "last_seen": s.last_seen,
            })
        temps = [s["value"] for s in sensors if s["unit"] == "°C"]
        return {
            "sensors": sensors,
            "stats": {
                "count": len(sensors),
                "th_count": sum(1 for s in sensors if s["unit"] == "°C"),
                "temp_min": round(min(temps), 2) if temps else 0,
                "temp_max": round(max(temps), 2) if temps else 0,
                "temp_avg": round(sum(temps) / len(temps), 2) if temps else 0,
                "hotspot_count": sum(1 for s in sensors if s["classification"] == "hotspot"),
                "overcool_count": sum(1 for s in sensors if s["classification"] == "overcool"),
            },
            "layout": {
                "room_x": 44.0,  # 2×22
                "room_z": 32.0,
                "room_y": 4.5,
                "rack_rows": [-10.0, -2.0, 2.0, 10.0],
            },
            "ts": time.time(),
        }

    def detect_heat_island(self) -> Dict[str, Any]:
        """AI 热岛检测: 识别气流阻挡 / 制冷效率下降 / 资产拓扑变化的热聚集.

        第一性原理: 热岛 = 局部温度 - 同排其他点平均温 > 阈值.
        """
        import re
        th = [s for s in self.sensors.values()
              if s.kind == IoTKind.LORA_TH and s.unit == "°C"]
        # group by rack row
        row_temps: Dict[str, List[float]] = {}
        for s in th:
            m = re.search(r"rack-([a-d])", s.location.lower())
            row = m.group(1).upper() if m else "?"
            row_temps.setdefault(row, []).append(s.value)
        islands = []
        for s in th:
            m = re.search(r"rack-([a-d])(\d+)-(front|back)", s.location.lower())
            if not m:
                continue
            row = m.group(1).upper()
            others = [v for v in row_temps.get(row, []) if v != s.value]
            if not others:
                continue
            peer_avg = sum(others) / len(others)
            delta = s.value - peer_avg
            # heat-island if sensor ≥ 3°C hotter than same-row peers AND absolute > 31°C
            if delta >= 3.0 and s.value > 31.0:
                # classify cause
                face = m.group(3)
                cause = ("气流阻挡 (资产拓扑变化)" if face == "back"
                         else "制冷分布不均 (CRAC 效率下降)")
                islands.append({
                    "sensor_id": s.sensor_id,
                    "location": s.location,
                    "temp_c": round(s.value, 2),
                    "peer_avg_c": round(peer_avg, 2),
                    "delta_c": round(delta, 2),
                    "probable_cause": cause,
                    "coord": self._sensor_coords(s.sensor_id, s.location),
                })
        # overcool zones (第一性原理: 冷量过剩 → 可松弛冷却)
        overcool = []
        for s in th:
            if s.value < 20.5:
                overcool.append({
                    "sensor_id": s.sensor_id,
                    "location": s.location,
                    "temp_c": round(s.value, 2),
                    "suggestion": "送风温度上调 0.5°C (CRAC-01 frequency -5Hz)",
                })
        return {
            "ok": True,
            "ts": time.time(),
            "heat_islands": islands,
            "overcool_zones": overcool,
            "alert_level": "red" if islands else ("yellow" if overcool else "green"),
            "principle": "热岛 Δ≥3°C & T>31°C; 冷量过剩 T<20.5°C (First Principles)",
        }

    def plc_adjust_fan(self, device_hint: str, delta_hz: float) -> Dict[str, Any]:
        """PLC 端 Agent 调整 CRAC/风机频率 (毫秒级).

        更新本地传感器的风速/功率镜像, 并记录事件.
        """
        # 记录为 event + 在对应 CRAC 设备上模拟功率变化
        target = None
        for d in self.devices.values():
            if device_hint.lower() in d.device_id.lower() or device_hint.lower() in d.name.lower():
                target = d
                break
        if target is None:
            return {"ok": False, "reason": f"no device matches {device_hint}"}
        # fan Δ → 功率 Δ (经验: 每 Hz ≈ 4% 额定)
        ratio = 1.0 + 0.04 * (delta_hz / 1.0)
        target.cpu_util = max(0.05, min(0.99, target.cpu_util * ratio))
        # 小幅反映到附近 LoRA 传感器: 风量↑ → 温度↓
        import re
        for s in self.sensors.values():
            if s.kind == IoTKind.LORA_TH and s.unit == "°C":
                # 同 facility 的所有温度传感器都受益
                s.value = round(max(18.0, s.value - 0.25 * (delta_hz / 2.0)), 2)
        self._record_event("plc_fan_adjust",
                           {"device": target.device_id, "delta_hz": delta_hz,
                            "new_util": round(target.cpu_util, 3)})
        return {"ok": True, "device": target.device_id,
                "delta_hz": delta_hz, "new_cpu_util": round(target.cpu_util, 3)}

    def ratchet_lock_cooling(self, note: str = "cooling optimum captured") -> Dict[str, Any]:
        """棘轮锁定: 把本轮热场优化转为不可逆遗产.

        依据当前 min/avg 温度, 计算 PUE 下降量, 写入 DarwinHeritage.
        """
        th = [s.value for s in self.sensors.values()
              if s.kind == IoTKind.LORA_TH and s.unit == "°C"]
        if not th:
            return {"ok": False, "reason": "no TH sensors"}
        avg_t = sum(th) / len(th)
        # 每低于基线 25°C 一度, 锁定 0.008 PUE / 1.4 kWh·day
        baseline_t = 25.0
        delta_t = max(0.0, baseline_t - avg_t)
        if delta_t <= 0.01:
            return {"ok": False, "reason": f"no cooling gain (avg={avg_t:.2f})"}
        delta_pue = -min(0.05, 0.008 * delta_t)
        delta_kwh = min(20.0, 1.4 * delta_t)
        res = self.evolve(
            title=f"Heat-Field Lock Δ{delta_t:.2f}°C · {note}",
            category="thermal_ratchet",
            delta_pue=delta_pue,
            delta_kwh_day=delta_kwh,
        )
        res["avg_temp_c"] = round(avg_t, 2)
        return res


        """模拟一次时序更新: 设备负载/温度小波动, 把当前 PUE 写入历史.

        非破坏性: 不修改 baseline / target / heritage.
        """
        import random
        # 设备负载随机抖动: 调 cpu_util (actual_power_kw 是派生属性)
        for d in self.devices.values():
            d.cpu_util = round(min(0.98, max(0.05, d.cpu_util + (random.random() - 0.5) * 0.06)), 3)
            d.intake_temp_c = round(min(38.0, max(20.0,
                                          d.intake_temp_c + (random.random() - 0.5) * 0.4)), 2)
        # 传感器温湿度抖动
        for s in self.sensors.values():
            if s.kind == IoTKind.LORA_TH and s.unit == "°C":
                s.value = round(min(40.0, max(20.0, s.value + (random.random() - 0.5) * 0.5)), 2)
                s.last_seen = time.time()
        # PUE 在 baseline 附近做 ±0.01 抖动 (除非已应用策略已下调)
        drift = (random.random() - 0.5) * 0.02
        self.current_pue = round(max(self.target_pue * 0.95,
                                     min(self.baseline_pue + 0.05, self.current_pue + drift)), 3)
        # 写入历史
        self.pue_history.append({"ts": time.time(), "pue": self.current_pue})
        if len(self.pue_history) > 720:
            self.pue_history = self.pue_history[-720:]
        return {"ok": True, "current_pue": self.current_pue,
                "history_size": len(self.pue_history)}

    # ── Musk's Five-Step Algorithm Reasoning ──
    def musk_five_step_audit(self) -> Dict[str, Any]:
        """对当前数据中心配置应用马斯克五步工作法, 输出第一性原理推演结果.

        Steps: (1) 质疑需求 (2) 删除环节 (3) 简化优化 (4) 加速循环 (5) 自动化
        """
        st_skills = len(self.skills)
        st_policies_total = len(self.policies)
        st_policies_applied = sum(1 for p in self.policies.values() if p.applied)
        st_offline_sensors = sum(1 for s in self.sensors.values()
                                 if (time.time() - s.last_seen) > 600)
        st_overload = sum(1 for d in self.devices.values()
                          if d.actual_power_kw > d.rated_power_kw * 0.9)
        st_overcool = sum(1 for s in self.sensors.values()
                          if s.kind == IoTKind.LORA_TH and s.unit == "°C" and s.value < 20.0)

        question = [
            f"质疑: 当前 PUE 基线 {self.baseline_pue} — 是否仍合理? 全球平均 {self.benchmark_pue_industry}, 目标 {self.target_pue}",
            f"质疑: {st_offline_sensors} 个传感器 >10min 无心跳 — 它们的物理价值是否仍存在?",
            f"质疑: 已沉淀 {st_skills} 条 Skill — 是否每条都至少触发过一次?",
        ]
        delete = [
            f"删除: {st_offline_sensors} 个离线传感器(可能是僵尸节点) — 建议从拓扑剪枝",
            f"删除: {st_policies_total - st_policies_applied} 条未应用策略 — 若长期未触发, 可降权或移除",
            f"删除: {st_overcool} 个过冷区域(<20°C) — 第一性原理: 芯片可承受更高入口温度, 删除冗余冷量",
        ]
        simplify = [
            f"简化: 设备过载 {st_overload} 台 — DVFS 调频 + 负载迁移到低利用率节点",
            "简化: 把 4 个视角合并到 single AI 推理调用, 减少前端往返",
        ]
        accelerate = [
            "加速: 闭环 tick 由 45s → 10s (模拟单板机 Agent 毫秒级响应)",
            f"加速: PUE 历史采样 {len(self.pue_history)} 点, 已支持滑窗预测",
        ]
        automate = [
            f"自动化: auto_loop_enabled={self.auto_loop_enabled}, 已应用 {st_policies_applied}/{st_policies_total} 策略",
            f"自动化: 棘轮锁定 {len(self.heritage)} 项遗产, 演进 {self._evolution_round} 轮",
        ]
        return {
            "ok": True,
            "principle": "Musk's Algorithm — Make Requirements Less Dumb · Delete · Simplify · Accelerate · Automate",
            "steps": {
                "1_question_requirements": question,
                "2_delete": delete,
                "3_simplify_optimize": simplify,
                "4_accelerate_cycle": accelerate,
                "5_automate": automate,
            },
            "ratchet_locked_items": len(self.heritage),
            "current_pue": self.current_pue,
            "evolution_round": self._evolution_round,
            "generated_at": time.time(),
        }

    # ── Status ──
    def get_status(self) -> Dict[str, Any]:
        applied = sum(1 for p in self.policies.values() if p.applied)
        total_save = sum(p.estimated_saving_kwh_day * p.fitness
                         for p in self.policies.values() if p.applied)
        return {
            "name": self.name,
            "health": self._health.status.value,
            "health_message": self._health.message,
            "current_pue": self.current_pue,
            "baseline_pue": self.baseline_pue,
            "target_pue": self.target_pue,
            "pue_progress_pct": round(
                100 * (self.baseline_pue - self.current_pue) /
                max(self.baseline_pue - self.target_pue, 0.01), 1),
            "device_count": len(self.devices),
            "sensor_count": len(self.sensors),
            "skill_count": len(self.skills),
            "policy_count": len(self.policies),
            "policies_applied": applied,
            "saving_kwh_day": round(total_save, 2),
            "saving_kwh_year": round(total_save * 365, 0),
            "co2_saved_ton_year": round(total_save * 365 * 0.785 / 1000, 2),
            "heritage_count": len(self.heritage),
            "evolution_round": self._evolution_round,
        }

    # ── Event handler (Channel 通用入口) ──
    async def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        et = event.get("type", "")
        if et == "perspective_query":
            p = DCPerspective(event.get("perspective", "device"))
            return {"ok": True, "result": self.analyze_perspective(p)}
        if et == "four_view":
            return {"ok": True, "result": self.four_view_overview()}
        if et == "ingest_sensor":
            return {"ok": True, "result": self.ingest_sensor(event["sensor_id"],
                                                              float(event["value"]))}
        if et == "hub_summary":
            return {"ok": True, "result": self.hub_summary()}
        if et == "apply_policy":
            return {"ok": True, "result": self.apply_policy(event["policy_id"],
                                                             float(event.get("fitness", 0.85)))}
        if et == "closed_loop_tick":
            return {"ok": True, "result": self.closed_loop_tick()}
        if et == "evolve":
            return {"ok": True, "result": self.evolve(
                event.get("title", "演进"),
                event.get("category", "general"),
                float(event.get("delta_pue", -0.005)),
                float(event.get("delta_kwh_day", 1.0)))}
        if et == "heritage":
            return {"ok": True, "result": self.heritage_ledger()}
        if et == "status":
            return {"ok": True, "result": self.get_status()}
        if et == "pue_history":
            return {"ok": True, "result": self.get_pue_history(int(event.get("limit", 240)))}
        if et == "sankey":
            return {"ok": True, "result": self.energy_sankey()}
        if et == "recommend":
            return {"ok": True, "result": self.recommend_actions(int(event.get("top_n", 5)))}
        if et == "benchmark":
            return {"ok": True, "result": self.benchmark()}
        if et == "cost":
            return {"ok": True, "result": self.cost_summary()}
        if et == "device_detail":
            d = self.get_device_detail(event.get("device_id", ""))
            return {"ok": d is not None, "result": d}
        if et == "list_devices":
            return {"ok": True, "result": self.list_devices()}
        if et == "auto_loop":
            return {"ok": True, "result": self.set_auto_loop(
                bool(event.get("enabled", False)), int(event.get("interval_s", 45)))}
        if et == "ai_insight":
            return {"ok": True, "result": self.ai_insight(event.get("focus", ""))}
        if et == "forecast":
            return {"ok": True, "result": self.forecast_pue(
                int(event.get("hours", 24)), int(event.get("step_min", 30)))}
        if et == "anomalies":
            return {"ok": True, "result": self.detect_anomalies(
                float(event.get("z_threshold", 2.0)))}
        if et == "what_if":
            return {"ok": True, "result": self.what_if(event.get("scenarios", []))}
        if et == "simulate_tick":
            return {"ok": True, "result": self.simulate_tick()}
        if et == "musk_audit":
            return {"ok": True, "result": self.musk_five_step_audit()}
        return {"ok": False, "reason": f"unknown event type: {et}"}
