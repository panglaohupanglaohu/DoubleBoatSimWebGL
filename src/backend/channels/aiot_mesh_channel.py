#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AIoT Mesh Channel — BIOS + LoRA + MC-RFID + 带外通信 关联学习.

对齐需求：
    1) MC-RFID ↔ LoRA      资产位置 × 环境参数(温湿度/气体) 余弦相似度匹配 + 阈值判断
    2) MC-RFID ↔ OOB(带外)  指令特征 × 资产标签 精准定位故障资产 → 处置辅助
    3) LoRA   ↔ OOB(带外)  异常检测(孤立森林式) → 通道优先级调度 → 自动调控指令

Mesh 自学习：每一次关联写入 `association_rules`，成功/失败强化置信度(贝叶斯平滑)。
"""

from __future__ import annotations

import math
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .marine_base import ChannelPriority, ChannelStatus, MarineChannel


# ───────────────────────── 数据模型 ─────────────────────────

@dataclass
class BIOSRecord:
    """板卡 BIOS / 自检 / 固件 数据."""
    device_id: str
    board_model: str
    firmware_version: str
    post_ok: bool = True
    boot_count: int = 0
    cpu_temp_c: float = 45.0
    mem_ecc_errors: int = 0
    watchdog_resets: int = 0
    asset_tag: str = ""          # 关联 MC-RFID 标签
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    last_seen: float = field(default_factory=time.time)


@dataclass
class LoRaSample:
    """LoRa 环境样本."""
    sensor_id: str
    position: Tuple[float, float, float]
    temperature_c: float = 22.0
    humidity_pct: float = 50.0
    gas_ppm: float = 0.0          # 可燃气体/有害气体浓度 (ppm)
    gas_species: str = "CH4"
    rssi: int = -80
    battery_pct: float = 95.0
    zone: str = "zone-A"
    ts: float = field(default_factory=time.time)


@dataclass
class RFIDAsset:
    """MC-RFID 资产."""
    tag_id: str
    asset_id: str
    asset_type: str               # 精密设备 / 服务器 / 泵 / 阀 / 电池
    model: str = ""
    material: str = ""
    service_years: float = 0.0
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    zone: str = "zone-A"
    # 存储/工作环境阈值
    temp_min_c: float = 20.0
    temp_max_c: float = 25.0
    rh_min_pct: float = 40.0
    rh_max_pct: float = 60.0
    gas_max_ppm: float = 100.0
    last_seen: float = field(default_factory=time.time)


@dataclass
class OOBCommand:
    """带外通信高优指令."""
    cmd_id: str
    kind: str                     # fault_alert / env_alert / maintenance / control
    priority: int                 # 0=最高
    payload: Dict[str, Any]
    target_hint: Dict[str, Any] = field(default_factory=dict)   # {asset_type, model, tag_id?, zone?}
    ts: float = field(default_factory=time.time)
    routed_channel: Optional[str] = None


@dataclass
class AssociationRule:
    """Mesh 学到的关联规则，持续优化置信度."""
    rule_id: str
    kind: str                     # rfid_lora / rfid_oob / lora_oob
    left_ref: str                 # e.g. asset_id / cmd_id / sensor_id
    right_ref: str
    features: Dict[str, float]    # 相似度 / 距离 / 分数
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    success: int = 0
    fail: int = 0
    confidence: float = 0.5       # Bayesian smoothed

    def reinforce(self, ok: bool) -> None:
        if ok:
            self.success += 1
        else:
            self.fail += 1
        n = self.success + self.fail
        self.confidence = (self.success + 1) / (n + 2)
        self.updated_at = time.time()


# ───────────────────────── 工具函数 ─────────────────────────

def _euclid(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _cosine(a: Tuple[float, ...], b: Tuple[float, ...]) -> float:
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na <= 1e-12 or nb <= 1e-12:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    return max(-1.0, min(1.0, dot / (na * nb)))


def _robust_zscore(values: List[float], v: float) -> float:
    """孤立森林式轻量异常分数：基于中位数/MAD 的 Z-score."""
    if not values:
        return 0.0
    s = sorted(values)
    med = s[len(s) // 2]
    mad = sorted(abs(x - med) for x in values)[len(values) // 2] or 1e-6
    return abs(v - med) / (1.4826 * mad)


# ───────────────────────── Channel ─────────────────────────

class AIoTMeshChannel(MarineChannel):
    """AIoT Mesh — 三域(BIOS/LoRA/MC-RFID) + 带外通信 的关联挖掘 Channel."""

    name = "aiot_mesh"
    description = "AIoT Mesh: BIOS/LoRA/MC-RFID/带外通信关联学习 (特征匹配+关联规则挖掘)"
    version = "1.0.0"
    priority = ChannelPriority.P1

    # 关联阈值（可配置）
    DIST_MATCH_M = 6.0              # 资产-传感器匹配最大欧氏距离(m)
    COSINE_MIN = 0.85               # 空间特征余弦相似度下限
    ANOMALY_Z = 3.0                 # 异常 Z-score 阈值

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bios: Dict[str, BIOSRecord] = {}
        self.lora: Dict[str, LoRaSample] = {}
        self.rfid: Dict[str, RFIDAsset] = {}
        self.oob_queue: List[OOBCommand] = []
        self.association_rules: Dict[str, AssociationRule] = {}
        self.event_log: List[Dict[str, Any]] = []
        self._cap_log = 400

    # ── lifecycle ──
    def initialize(self) -> bool:
        self._seed()
        self._initialized = True
        self._set_health(ChannelStatus.OK, "aiot_mesh ready")
        return True

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "shutdown")
        return True

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "health": self._health.status.value,
            "health_message": self._health.message,
            "initialized": self._initialized,
            "counts": {
                "bios": len(self.bios),
                "lora": len(self.lora),
                "rfid": len(self.rfid),
                "oob_queue": len(self.oob_queue),
                "rules": len(self.association_rules),
            },
            "thresholds": {
                "dist_match_m": self.DIST_MATCH_M,
                "cosine_min": self.COSINE_MIN,
                "anomaly_z": self.ANOMALY_Z,
            },
        }

    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """接收外部事件 (BIOS/LoRA/RFID/OOB) 并触发关联学习."""
        kind = (event or {}).get("type", "")
        if kind == "bios":
            return self.ingest_bios(event)
        if kind == "lora":
            return self.ingest_lora(event)
        if kind == "rfid":
            return self.ingest_rfid(event)
        if kind == "oob":
            return self.ingest_oob_command(event)
        return {"ok": False, "reason": f"unknown event type: {kind}"}

    # ── seed (演示数据) ──
    def _seed(self) -> None:
        # 9 块板卡 (3x3 网格)
        for i, (x, y) in enumerate([(r, c) for r in range(3) for c in range(3)]):
            dev = f"board-{i+1:02d}"
            tag = f"RFID-{1000+i}"
            self.bios[dev] = BIOSRecord(
                device_id=dev,
                board_model="Edge-X86-IPMI" if i % 2 == 0 else "ARM-IPMI-A78",
                firmware_version="2.5.1" if i % 2 == 0 else "1.8.3",
                post_ok=(i != 4),  # 一个 POST 失败示例
                boot_count=120 + i * 3,
                cpu_temp_c=round(42 + i * 1.3, 1),
                mem_ecc_errors=1 if i == 4 else 0,
                watchdog_resets=0,
                asset_tag=tag,
                position=(float(x * 3), 1.8, float(y * 3)),
            )
            self.rfid[tag] = RFIDAsset(
                tag_id=tag,
                asset_id=dev,
                asset_type="精密服务器" if i % 3 != 0 else "GPU 推理节点",
                model="Dell R760" if i % 2 else "HPE DL380",
                material="铝/钢/环氧树脂",
                service_years=round(1 + i * 0.4, 1),
                position=(float(x * 3), 1.8, float(y * 3)),
                zone=f"zone-{chr(65 + (i // 3))}",
                temp_min_c=18.0, temp_max_c=27.0,
                rh_min_pct=35.0, rh_max_pct=65.0,
                gas_max_ppm=80.0,
            )
        # 再加 2 个精密设备 (更严格阈值)
        for j, tag in enumerate(["RFID-2001", "RFID-2002"]):
            self.rfid[tag] = RFIDAsset(
                tag_id=tag,
                asset_id=f"instr-{j+1:02d}",
                asset_type="精密设备",
                model="CalLab-DAQ-2k",
                material="精密光学/电子",
                service_years=0.5 + j,
                position=(float(6 + j * 2), 1.2, 6.0),
                zone="zone-C",
                temp_min_c=20.0, temp_max_c=25.0,
                rh_min_pct=40.0, rh_max_pct=60.0,
                gas_max_ppm=30.0,
            )

        # LoRa 传感器网格 (与 board 对齐一部分, 其余偏移)
        grid = [
            ("lora-th-01", (0.0, 1.8, 0.0), 23.4, 52.0, 18.0, "zone-A"),
            ("lora-th-02", (3.0, 1.8, 0.0), 24.1, 55.0, 22.0, "zone-A"),
            ("lora-th-03", (6.0, 1.8, 0.0), 28.7, 58.0, 40.0, "zone-A"),
            ("lora-th-04", (0.0, 1.8, 3.0), 23.0, 49.0, 12.0, "zone-B"),
            ("lora-th-05", (3.0, 1.8, 3.0), 30.2, 64.0, 55.0, "zone-B"),  # 热+湿偏高
            ("lora-th-06", (6.0, 1.8, 3.0), 24.8, 57.0, 26.0, "zone-B"),
            ("lora-th-07", (0.0, 1.8, 6.0), 22.5, 48.0, 10.0, "zone-C"),
            ("lora-th-08", (3.0, 1.8, 6.0), 23.3, 51.0, 14.0, "zone-C"),
            ("lora-th-09", (6.0, 1.2, 6.0), 26.9, 68.0, 120.0, "zone-C"),  # 异常: 气体超标
        ]
        for sid, pos, t, rh, gas, zone in grid:
            self.lora[sid] = LoRaSample(
                sensor_id=sid, position=pos,
                temperature_c=t, humidity_pct=rh,
                gas_ppm=gas, gas_species="CH4" if gas < 80 else "H2S",
                zone=zone,
            )

        # 两条典型 OOB 指令 (故障告警 / 环境告警)
        self.oob_queue.append(OOBCommand(
            cmd_id=f"oob-{uuid.uuid4().hex[:8]}",
            kind="fault_alert",
            priority=1,
            payload={"fault": "memory ECC burst", "severity": "high"},
            target_hint={"asset_type": "精密服务器", "model": "HPE DL380"},
        ))
        self.oob_queue.append(OOBCommand(
            cmd_id=f"oob-{uuid.uuid4().hex[:8]}",
            kind="env_alert",
            priority=0,
            payload={"hazard": "H2S exceedance"},
            target_hint={"zone": "zone-C"},
        ))

    # ── ingest ──
    def ingest_bios(self, ev: Dict[str, Any]) -> Dict[str, Any]:
        dev = ev.get("device_id")
        if not dev:
            return {"ok": False, "reason": "device_id required"}
        rec = self.bios.get(dev) or BIOSRecord(
            device_id=dev, board_model=ev.get("board_model", "generic"),
            firmware_version=ev.get("firmware_version", "0.0.0"),
        )
        for k in ("firmware_version", "post_ok", "boot_count", "cpu_temp_c",
                  "mem_ecc_errors", "watchdog_resets", "asset_tag"):
            if k in ev:
                setattr(rec, k, ev[k])
        if "position" in ev:
            rec.position = tuple(ev["position"])  # type: ignore[assignment]
        rec.last_seen = time.time()
        self.bios[dev] = rec
        return {"ok": True, "device_id": dev}

    def ingest_lora(self, ev: Dict[str, Any]) -> Dict[str, Any]:
        sid = ev.get("sensor_id")
        if not sid:
            return {"ok": False, "reason": "sensor_id required"}
        s = self.lora.get(sid) or LoRaSample(sensor_id=sid, position=(0.0, 0.0, 0.0))
        for k in ("temperature_c", "humidity_pct", "gas_ppm", "gas_species",
                  "rssi", "battery_pct", "zone"):
            if k in ev:
                setattr(s, k, ev[k])
        if "position" in ev:
            s.position = tuple(ev["position"])  # type: ignore[assignment]
        s.ts = time.time()
        self.lora[sid] = s
        # 自动触发 LoRa↔OOB 异常检测关联
        triggered = self.associate_lora_oob(single_sensor=sid)
        return {"ok": True, "sensor_id": sid, "triggered_oob": len(triggered)}

    def ingest_rfid(self, ev: Dict[str, Any]) -> Dict[str, Any]:
        tag = ev.get("tag_id")
        if not tag:
            return {"ok": False, "reason": "tag_id required"}
        a = self.rfid.get(tag) or RFIDAsset(tag_id=tag, asset_id=ev.get("asset_id", tag),
                                             asset_type=ev.get("asset_type", "unknown"))
        for k in ("asset_id", "asset_type", "model", "material", "service_years",
                  "zone", "temp_min_c", "temp_max_c", "rh_min_pct", "rh_max_pct",
                  "gas_max_ppm"):
            if k in ev:
                setattr(a, k, ev[k])
        if "position" in ev:
            a.position = tuple(ev["position"])  # type: ignore[assignment]
        a.last_seen = time.time()
        self.rfid[tag] = a
        return {"ok": True, "tag_id": tag}

    def ingest_oob_command(self, ev: Dict[str, Any]) -> Dict[str, Any]:
        cmd = OOBCommand(
            cmd_id=ev.get("cmd_id") or f"oob-{uuid.uuid4().hex[:8]}",
            kind=ev.get("kind", "control"),
            priority=int(ev.get("priority", 3)),
            payload=ev.get("payload", {}) or {},
            target_hint=ev.get("target_hint", {}) or {},
        )
        self.oob_queue.append(cmd)
        # 立即尝试 RFID↔OOB 匹配
        match = self.associate_rfid_oob(cmd_id=cmd.cmd_id)
        return {"ok": True, "cmd_id": cmd.cmd_id, "matches": len(match)}

    # ── 关联算法 1: MC-RFID ↔ LoRA ──
    def associate_rfid_lora(self) -> List[Dict[str, Any]]:
        """资产 ↔ 环境 关联: 欧氏距离 + 位置余弦 + 环境阈值判断 + 影响量化."""
        results: List[Dict[str, Any]] = []
        for asset in self.rfid.values():
            best: Optional[Tuple[LoRaSample, float, float]] = None
            for s in self.lora.values():
                d = _euclid(asset.position, s.position)
                cos = _cosine(asset.position, s.position)
                if d <= self.DIST_MATCH_M and cos >= self.COSINE_MIN:
                    score = (1.0 / (1.0 + d)) * cos
                    if best is None or score > best[2]:
                        best = (s, d, score)
            if not best:
                continue
            s, d, score = best
            breaches: List[str] = []
            if not (asset.temp_min_c <= s.temperature_c <= asset.temp_max_c):
                breaches.append(f"temp={s.temperature_c}°C∉[{asset.temp_min_c},{asset.temp_max_c}]")
            if not (asset.rh_min_pct <= s.humidity_pct <= asset.rh_max_pct):
                breaches.append(f"rh={s.humidity_pct}%∉[{asset.rh_min_pct},{asset.rh_max_pct}]")
            if s.gas_ppm > asset.gas_max_ppm:
                breaches.append(f"gas={s.gas_ppm}ppm>{asset.gas_max_ppm}")
            # 影响量化：材质/服役年限加权
            age_factor = min(1.0, asset.service_years / 10.0)
            impact = round(min(1.0, 0.25 * len(breaches) + 0.4 * age_factor), 3)
            rule = self._upsert_rule(
                kind="rfid_lora",
                left_ref=asset.tag_id,
                right_ref=s.sensor_id,
                features={"distance_m": round(d, 3), "cosine": round(_cosine(asset.position, s.position), 3),
                          "match_score": round(score, 4), "breach_count": len(breaches), "impact": impact},
                ok=(len(breaches) == 0),
            )
            results.append({
                "asset_id": asset.asset_id, "tag_id": asset.tag_id, "asset_type": asset.asset_type,
                "sensor_id": s.sensor_id, "zone": asset.zone,
                "distance_m": round(d, 3),
                "environment": {"temp_c": s.temperature_c, "rh_pct": s.humidity_pct,
                                "gas_ppm": s.gas_ppm, "gas_species": s.gas_species},
                "breaches": breaches,
                "impact": impact,
                "rule_id": rule.rule_id,
                "confidence": round(rule.confidence, 3),
            })
        self._log({"type": "associate_rfid_lora", "count": len(results)})
        return results

    # ── 关联算法 2: MC-RFID ↔ OOB ──
    def associate_rfid_oob(self, cmd_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """指令 ↔ 资产 标签匹配, 锁定故障资产坐标 + 生成处置辅助信息."""
        out: List[Dict[str, Any]] = []
        queue = [c for c in self.oob_queue if (cmd_id is None or c.cmd_id == cmd_id)]
        for cmd in queue:
            hint = cmd.target_hint or {}
            matches: List[Tuple[RFIDAsset, float]] = []
            for a in self.rfid.values():
                score = 0.0
                if hint.get("tag_id") and hint["tag_id"] == a.tag_id:
                    score += 1.0
                if hint.get("asset_type") and hint["asset_type"] == a.asset_type:
                    score += 0.5
                if hint.get("model") and hint["model"].lower() in a.model.lower():
                    score += 0.3
                if hint.get("zone") and hint["zone"] == a.zone:
                    score += 0.25
                if score > 0:
                    matches.append((a, score))
            matches.sort(key=lambda t: t[1], reverse=True)
            top = matches[:5]
            for a, s in top:
                rule = self._upsert_rule(
                    kind="rfid_oob", left_ref=cmd.cmd_id, right_ref=a.tag_id,
                    features={"label_score": round(s, 3), "priority": cmd.priority},
                    ok=(s >= 0.5),
                )
                out.append({
                    "cmd_id": cmd.cmd_id, "cmd_kind": cmd.kind, "priority": cmd.priority,
                    "tag_id": a.tag_id, "asset_id": a.asset_id, "asset_type": a.asset_type,
                    "model": a.model, "service_years": a.service_years,
                    "position": list(a.position), "zone": a.zone,
                    "label_score": round(s, 3),
                    "handling_hint": self._build_handling_hint(cmd, a),
                    "rule_id": rule.rule_id,
                    "confidence": round(rule.confidence, 3),
                })
        self._log({"type": "associate_rfid_oob", "count": len(out)})
        return out

    def _build_handling_hint(self, cmd: OOBCommand, a: RFIDAsset) -> str:
        if cmd.kind == "fault_alert":
            age = f"服役{a.service_years}年" if a.service_years else ""
            return f"前往 {a.zone} 定位 {a.model} {age} (位置{a.position}), 携带备件/日志采集工具"
        if cmd.kind == "env_alert":
            return f"隔离 {a.zone} 区域, 启动新风与保护性关机 {a.asset_id}"
        return f"按 {cmd.kind} SOP 处置 {a.asset_id} @ {a.zone}"

    # ── 关联算法 3: LoRA ↔ OOB ──
    def associate_lora_oob(self, single_sensor: Optional[str] = None) -> List[Dict[str, Any]]:
        """环境异常 → 生成紧急 OOB 指令 (设为最高优先级) + 自动调控指令."""
        out: List[Dict[str, Any]] = []
        gas_values = [s.gas_ppm for s in self.lora.values()]
        sensors = [self.lora[single_sensor]] if single_sensor and single_sensor in self.lora \
                  else list(self.lora.values())
        for s in sensors:
            z = _robust_zscore(gas_values, s.gas_ppm)
            gas_sev = (
                "critical" if s.gas_ppm > 100 or z >= self.ANOMALY_Z + 1 else
                "high"     if s.gas_ppm > 50  or z >= self.ANOMALY_Z     else
                "normal"
            )
            t_breach = s.temperature_c > 32.0
            if gas_sev == "normal" and not t_breach:
                continue
            prio = 0 if gas_sev == "critical" else 1
            actions = []
            if gas_sev != "normal":
                actions += ["启动新风系统最大档", "就近停用非必要电源"]
            if s.gas_ppm > 100:
                actions.append("切断受影响配电回路")
            if t_breach:
                actions.append("CRAC 降温送风 -2°C")
            cmd = OOBCommand(
                cmd_id=f"oob-auto-{uuid.uuid4().hex[:6]}",
                kind="env_alert",
                priority=prio,
                payload={"gas_ppm": s.gas_ppm, "gas_species": s.gas_species,
                         "temperature_c": s.temperature_c, "severity": gas_sev,
                         "anomaly_z": round(z, 2), "actions": actions},
                target_hint={"zone": s.zone},
                routed_channel="OOB-priority-0" if prio == 0 else "OOB-priority-1",
            )
            self.oob_queue.append(cmd)
            rule = self._upsert_rule(
                kind="lora_oob", left_ref=s.sensor_id, right_ref=cmd.cmd_id,
                features={"anomaly_z": round(z, 3), "gas_ppm": s.gas_ppm,
                          "temp_c": s.temperature_c, "priority": prio},
                ok=True,
            )
            out.append({
                "sensor_id": s.sensor_id, "zone": s.zone,
                "anomaly_z": round(z, 3), "severity": gas_sev,
                "gas_ppm": s.gas_ppm, "gas_species": s.gas_species,
                "temperature_c": s.temperature_c,
                "emit_cmd": cmd.cmd_id, "priority": prio,
                "routed_channel": cmd.routed_channel,
                "actions": actions,
                "rule_id": rule.rule_id,
                "confidence": round(rule.confidence, 3),
            })
        self._log({"type": "associate_lora_oob", "count": len(out)})
        return out

    # ── 综合 mesh 视图 ──
    def mesh_overview(self) -> Dict[str, Any]:
        rfid_lora = self.associate_rfid_lora()
        rfid_oob = self.associate_rfid_oob()
        lora_oob = self.associate_lora_oob()
        # Mesh 图: 节点 = 三域实体 + OOB 指令, 边 = 关联
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []
        for dev, b in self.bios.items():
            nodes.append({"id": f"bios:{dev}", "kind": "bios", "label": dev,
                          "pos": list(b.position),
                          "meta": {"post_ok": b.post_ok, "fw": b.firmware_version,
                                   "cpu_temp_c": b.cpu_temp_c, "ecc": b.mem_ecc_errors}})
        for tag, a in self.rfid.items():
            nodes.append({"id": f"rfid:{tag}", "kind": "rfid", "label": tag,
                          "pos": list(a.position),
                          "meta": {"asset_type": a.asset_type, "model": a.model,
                                   "zone": a.zone, "service_years": a.service_years}})
        for sid, s in self.lora.items():
            nodes.append({"id": f"lora:{sid}", "kind": "lora", "label": sid,
                          "pos": list(s.position),
                          "meta": {"t": s.temperature_c, "rh": s.humidity_pct,
                                   "gas": s.gas_ppm, "species": s.gas_species, "zone": s.zone}})
        for c in self.oob_queue[-20:]:
            nodes.append({"id": f"oob:{c.cmd_id}", "kind": "oob", "label": c.cmd_id,
                          "pos": [0.0, 4.0, 0.0],
                          "meta": {"kind": c.kind, "priority": c.priority,
                                   "payload": c.payload, "routed": c.routed_channel}})
        # BIOS 天然关联 RFID 资产标签
        for b in self.bios.values():
            if b.asset_tag and b.asset_tag in self.rfid:
                edges.append({"source": f"bios:{b.device_id}", "target": f"rfid:{b.asset_tag}",
                              "kind": "bios_rfid", "weight": 1.0})
        for r in rfid_lora:
            edges.append({"source": f"rfid:{r['tag_id']}", "target": f"lora:{r['sensor_id']}",
                          "kind": "rfid_lora", "weight": r["confidence"],
                          "breach": len(r["breaches"]) > 0, "impact": r["impact"]})
        for r in rfid_oob:
            edges.append({"source": f"oob:{r['cmd_id']}", "target": f"rfid:{r['tag_id']}",
                          "kind": "rfid_oob", "weight": r["confidence"],
                          "label_score": r["label_score"]})
        for r in lora_oob:
            edges.append({"source": f"lora:{r['sensor_id']}", "target": f"oob:{r['emit_cmd']}",
                          "kind": "lora_oob", "weight": r["confidence"],
                          "severity": r["severity"]})
        return {
            "generated_at": time.time(),
            "summary": {
                "bios": len(self.bios), "lora": len(self.lora), "rfid": len(self.rfid),
                "oob_queue": len(self.oob_queue),
                "edges_rfid_lora": len(rfid_lora),
                "edges_rfid_oob": len(rfid_oob),
                "edges_lora_oob": len(lora_oob),
                "rules_learned": len(self.association_rules),
                "avg_confidence": round(
                    sum(r.confidence for r in self.association_rules.values())
                    / max(len(self.association_rules), 1), 3),
            },
            "rfid_lora": rfid_lora,
            "rfid_oob": rfid_oob,
            "lora_oob": lora_oob,
            "graph": {"nodes": nodes, "edges": edges},
        }

    def list_rules(self) -> List[Dict[str, Any]]:
        rules = sorted(self.association_rules.values(), key=lambda r: -r.confidence)
        return [{
            "rule_id": r.rule_id, "kind": r.kind,
            "left": r.left_ref, "right": r.right_ref,
            "features": r.features, "success": r.success, "fail": r.fail,
            "confidence": round(r.confidence, 3),
            "updated_at": r.updated_at,
        } for r in rules]

    def reinforce_rule(self, rule_id: str, ok: bool) -> Dict[str, Any]:
        r = self.association_rules.get(rule_id)
        if not r:
            return {"ok": False, "reason": "rule not found"}
        r.reinforce(ok)
        return {"ok": True, "rule_id": rule_id, "confidence": round(r.confidence, 3),
                "success": r.success, "fail": r.fail}

    # ── internals ──
    def _upsert_rule(self, *, kind: str, left_ref: str, right_ref: str,
                     features: Dict[str, float], ok: bool) -> AssociationRule:
        key = f"{kind}::{left_ref}::{right_ref}"
        r = self.association_rules.get(key)
        if r is None:
            r = AssociationRule(rule_id=key, kind=kind, left_ref=left_ref,
                                right_ref=right_ref, features=features)
            self.association_rules[key] = r
        else:
            r.features.update(features)
        r.reinforce(ok)
        return r

    def _log(self, event: Dict[str, Any]) -> None:
        event.setdefault("ts", time.time())
        self.event_log.append(event)
        if len(self.event_log) > self._cap_log:
            self.event_log = self.event_log[-self._cap_log:]
