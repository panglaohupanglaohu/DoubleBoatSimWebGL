# -*- coding: utf-8 -*-
"""
Intelligent Engine Channel - 智能机舱模块

实现主机健康度评估、趋势分析、故障预警、维护建议。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from .marine_base import MarineChannel, ChannelStatus, ChannelPriority


@dataclass
class EngineSnapshot:
    rpm: float
    load: float
    coolant_temp: float
    oil_pressure: float
    fuel_rate: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rpm": round(self.rpm, 1),
            "load": round(self.load, 1),
            "coolant_temp": round(self.coolant_temp, 1),
            "oil_pressure": round(self.oil_pressure, 2),
            "fuel_rate": round(self.fuel_rate, 1),
            "timestamp": self.timestamp.isoformat(),
        }


class IntelligentEngineChannel(MarineChannel):
    name = "intelligent_engine"
    description = "智能机舱 (健康评估 + 趋势分析 + 故障预警)"
    version = "1.0.0"
    priority = ChannelPriority.P0
    dependencies: List[str] = ["engine_monitor"]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.config = config or {}
        self._config = config or {}
        self.snapshots: List[EngineSnapshot] = []
        self.max_snapshots = self.config.get("max_snapshots", 120)
        self.engine_instance = self.config.get("engine_instance", 0)
        self.thresholds = {
            "rpm_high": 900,
            "load_high": 90,
            "coolant_temp_warn": 85,
            "coolant_temp_alarm": 95,
            "oil_pressure_warn": 2.5,
            "oil_pressure_alarm": 1.8,
            "fuel_rate_high": 600,
        }
        self._pending_nmea: Dict[int, Dict[str, Any]] = {}
        # seeded demo data
        self.update_snapshot(720, 68, 78.5, 3.4, 465)

    def initialize(self) -> bool:
        try:
            valid, errors = self.validate_config()
            if not valid:
                self._set_health(ChannelStatus.ERROR, f"配置验证失败：{errors}")
                return False
            self._initialized = True
            self._set_health(ChannelStatus.OK, "智能机舱系统就绪")
            return True
        except Exception as e:
            self._set_health(ChannelStatus.ERROR, str(e))
            return False

    def get_status(self) -> Dict[str, Any]:
        latest = self.get_latest_snapshot()
        return {
            "name": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "health_message": self._health.message,
            "engine_health_score": self.calculate_health_score(),
            "alerts": self.get_alerts(),
            "latest_snapshot": latest.to_dict() if latest else None,
            "trend": self.get_trend_summary(),
        }

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shutdown")
        return True

    def update_snapshot(self, rpm: float, load: float, coolant_temp: float, oil_pressure: float, fuel_rate: float):
        snap = EngineSnapshot(rpm, load, coolant_temp, oil_pressure, fuel_rate)
        self.snapshots.append(snap)
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots = self.snapshots[-self.max_snapshots :]
        score = self.calculate_health_score()
        if score >= 85:
            self._set_health(ChannelStatus.OK, f"主机健康良好 ({score})")
        elif score >= 65:
            self._set_health(ChannelStatus.WARN, f"主机存在关注项 ({score})")
        else:
            self._set_health(ChannelStatus.ERROR, f"主机健康较差 ({score})")

    def get_latest_snapshot(self) -> Optional[EngineSnapshot]:
        return self.snapshots[-1] if self.snapshots else None

    def calculate_health_score(self) -> int:
        snap = self.get_latest_snapshot()
        if not snap:
            return 0
        score = 100.0
        if snap.coolant_temp > self.thresholds["coolant_temp_warn"]:
            score -= min(25, (snap.coolant_temp - self.thresholds["coolant_temp_warn"]) * 1.5)
        if snap.oil_pressure < self.thresholds["oil_pressure_warn"]:
            score -= min(30, (self.thresholds["oil_pressure_warn"] - snap.oil_pressure) * 15)
        if snap.load > self.thresholds["load_high"]:
            score -= min(15, (snap.load - self.thresholds["load_high"]) * 1.5)
        if snap.fuel_rate > self.thresholds["fuel_rate_high"]:
            score -= min(10, (snap.fuel_rate - self.thresholds["fuel_rate_high"]) / 20)
        return max(0, int(round(score)))

    def get_alerts(self) -> List[Dict[str, Any]]:
        snap = self.get_latest_snapshot()
        if not snap:
            return []
        alerts: List[Dict[str, Any]] = []
        if snap.coolant_temp >= self.thresholds["coolant_temp_alarm"]:
            alerts.append({"level": "critical", "message": f"冷却水温度过高 {snap.coolant_temp:.1f}°C"})
        elif snap.coolant_temp >= self.thresholds["coolant_temp_warn"]:
            alerts.append({"level": "warning", "message": f"冷却水温度偏高 {snap.coolant_temp:.1f}°C"})
        if snap.oil_pressure <= self.thresholds["oil_pressure_alarm"]:
            alerts.append({"level": "critical", "message": f"滑油压力过低 {snap.oil_pressure:.2f} bar"})
        elif snap.oil_pressure <= self.thresholds["oil_pressure_warn"]:
            alerts.append({"level": "warning", "message": f"滑油压力偏低 {snap.oil_pressure:.2f} bar"})
        if snap.load >= self.thresholds["load_high"]:
            alerts.append({"level": "warning", "message": f"主机高负载 {snap.load:.1f}%"})
        return alerts

    def get_trend_summary(self) -> Dict[str, Any]:
        if len(self.snapshots) < 2:
            return {"rpm": "stable", "temp": "stable", "pressure": "stable"}
        recent = self.snapshots[-5:]
        first = recent[0]
        last = recent[-1]
        return {
            "rpm": self._trend_label(last.rpm - first.rpm, 15),
            "temp": self._trend_label(last.coolant_temp - first.coolant_temp, 1.5),
            "pressure": self._trend_label(last.oil_pressure - first.oil_pressure, 0.15, invert=True),
        }

    def _trend_label(self, delta: float, threshold: float, invert: bool = False) -> str:
        if abs(delta) < threshold:
            return "stable"
        if invert:
            return "worsening" if delta < 0 else "improving"
        return "rising" if delta > 0 else "falling"

    def get_maintenance_advice(self) -> List[str]:
        snap = self.get_latest_snapshot()
        if not snap:
            return ["暂无可用数据"]
        advice: List[str] = []
        if snap.coolant_temp >= self.thresholds["coolant_temp_warn"]:
            advice.append("检查冷却水回路、海水滤器和换热器状态")
        if snap.oil_pressure <= self.thresholds["oil_pressure_warn"]:
            advice.append("检查滑油液位、滤器和滑油泵工况")
        if snap.load >= self.thresholds["load_high"]:
            advice.append("评估螺旋桨/船体阻力，必要时适当降载运行")
        if snap.fuel_rate >= self.thresholds["fuel_rate_high"]:
            advice.append("复核喷油、燃烧和进气效率，排查燃油消耗异常")
        if not advice:
            advice.append("主机工况平稳，维持当前监测频率即可")
        return advice

    def ingest_nmea2000_message(self, message: Any) -> bool:
        """接收 NMEA 2000 消息并在关键字段齐备时生成机舱快照。"""
        pgn = getattr(message, "pgn", None)
        fields = getattr(message, "fields", {}) or {}
        if pgn not in {127488, 127489, 127493}:
            return False

        engine_instance = int(fields.get("engine_instance", self.engine_instance) or 0)
        if engine_instance != self.engine_instance:
            return False

        pending = self._pending_nmea.setdefault(engine_instance, {})
        timestamp = getattr(message, "timestamp", datetime.now())
        pending["timestamp"] = timestamp

        if pgn == 127488:
            speed = fields.get("speed")
            if speed is not None:
                pending["rpm"] = float(speed)
        elif pgn == 127489:
            load = fields.get("engine_load")
            fuel_rate = fields.get("fuel_rate")
            oil_pressure = fields.get("oil_pressure")
            coolant_temp = fields.get("coolant_temp")
            
            if load is not None:
                pending["load"] = float(load)
            if fuel_rate is not None:
                pending["fuel_rate"] = float(fuel_rate)
            if oil_pressure is not None:
                pending["oil_pressure"] = self._normalize_pressure_to_bar(float(oil_pressure))
            if coolant_temp is not None:
                pending["coolant_temp"] = self._normalize_temperature_to_celsius(float(coolant_temp))
        elif pgn == 127493:
            # Fallback to transmission parameters if 127489 didn't provide them
            trans_oil_pressure = fields.get("oil_pressure")
            trans_oil_temp = fields.get("oil_temp")
            if trans_oil_pressure is not None and "oil_pressure" not in pending:
                pending["oil_pressure"] = self._normalize_pressure_to_bar(float(trans_oil_pressure))
            if trans_oil_temp is not None and "coolant_temp" not in pending:
                pending["coolant_temp"] = self._normalize_temperature_to_celsius(float(trans_oil_temp))

        required = {"rpm", "load", "coolant_temp", "oil_pressure", "fuel_rate"}
        if required.issubset(pending):
            snap = EngineSnapshot(
                rpm=pending["rpm"],
                load=pending["load"],
                coolant_temp=pending["coolant_temp"],
                oil_pressure=pending["oil_pressure"],
                fuel_rate=pending["fuel_rate"],
                timestamp=pending.get("timestamp", datetime.now()),
            )
            self.snapshots.append(snap)
            if len(self.snapshots) > self.max_snapshots:
                self.snapshots = self.snapshots[-self.max_snapshots :]
            score = self.calculate_health_score()
            if score >= 85:
                self._set_health(ChannelStatus.OK, f"主机健康良好 ({score})")
            elif score >= 65:
                self._set_health(ChannelStatus.WARN, f"主机存在关注项 ({score})")
            else:
                self._set_health(ChannelStatus.ERROR, f"主机健康较差 ({score})")
            self._pending_nmea[engine_instance] = {}
            return True
        return False

    def _normalize_pressure_to_bar(self, value: float) -> float:
        if value > 50:
            return value / 100000.0
        return value

    def _normalize_temperature_to_celsius(self, value: float) -> float:
        if value > 200:
            return value - 273.15
        return value

    def diagnose_faults(self) -> List[Dict[str, Any]]:
        snap = self.get_latest_snapshot()
        if not snap:
            return []

        trend = self.get_trend_summary()
        current_time = datetime.now().isoformat()
        findings: List[Dict[str, Any]] = []
        if snap.coolant_temp >= self.thresholds["coolant_temp_warn"]:
            findings.append({
                "fault_type": "cooling_system_abnormal",
                "confidence": 0.82 if snap.coolant_temp >= self.thresholds["coolant_temp_alarm"] else 0.67,
                "risk_level": "critical" if snap.coolant_temp >= self.thresholds["coolant_temp_alarm"] else "warning",
                "recommended_action": "检查海水滤器、淡水回路和换热器堵塞情况",
                "supporting_features": {"coolant_temp": snap.coolant_temp, "trend": trend.get("temp")},
                "timestamp": current_time
            })
        if snap.oil_pressure <= self.thresholds["oil_pressure_warn"]:
            findings.append({
                "fault_type": "lubrication_system_abnormal",
                "confidence": 0.86 if snap.oil_pressure <= self.thresholds["oil_pressure_alarm"] else 0.71,
                "risk_level": "critical" if snap.oil_pressure <= self.thresholds["oil_pressure_alarm"] else "warning",
                "recommended_action": "检查滑油液位、滤器压差和油泵输出",
                "supporting_features": {"oil_pressure": snap.oil_pressure, "trend": trend.get("pressure")},
                "timestamp": current_time
            })
        if snap.load >= self.thresholds["load_high"] and snap.fuel_rate >= self.thresholds["fuel_rate_high"]:
            findings.append({
                "fault_type": "overload_or_combustion_inefficiency",
                "confidence": 0.74,
                "risk_level": "warning",
                "recommended_action": "核查推进阻力、喷油状态和空燃比，必要时降载",
                "supporting_features": {"load": snap.load, "fuel_rate": snap.fuel_rate},
                "timestamp": current_time
            })
        if trend.get("pressure") == "worsening" and trend.get("temp") == "rising":
            findings.append({
                "fault_type": "degradation_trend_detected",
                "confidence": 0.69,
                "risk_level": "warning",
                "recommended_action": "将监测频率提升到 5 分钟级，并安排点检确认趋势",
                "supporting_features": {"pressure_trend": "worsening", "temp_trend": "rising"},
                "timestamp": current_time
            })
        return findings

    def query_engine_status(self, query: str) -> str:
        snap = self.get_latest_snapshot()
        if not snap:
            return "当前没有机舱数据。"
        score = self.calculate_health_score()
        alerts = self.get_alerts()
        q = query.lower()
        if "健康" in q or "状态" in q or "主机" in q:
            base = (
                f"当前主机健康度 {score}/100。\n"
                f"转速 {snap.rpm:.0f} RPM，负载 {snap.load:.1f}% 。\n"
                f"冷却水温度 {snap.coolant_temp:.1f}°C，滑油压力 {snap.oil_pressure:.2f} bar，燃油消耗 {snap.fuel_rate:.1f} kg/h。"
            )
            if alerts:
                base += "\n当前告警：" + "；".join(a["message"] for a in alerts)
            else:
                base += "\n当前无机舱告警。"
            return base
        if "维护" in q or "建议" in q:
            return "维护建议：\n- " + "\n- ".join(self.get_maintenance_advice())
        if "趋势" in q:
            trend = self.get_trend_summary()
            return f"趋势分析：RPM {trend['rpm']}，冷却水温度 {trend['temp']}，滑油压力 {trend['pressure']}。"
        if "故障" in q or "诊断" in q:
            findings = self.diagnose_faults()
            if not findings:
                return "当前未识别出明确故障模式，建议继续监测。"
            lines = [
                f"- {item['fault_type']} | 风险 {item['risk_level']} | 置信度 {item['confidence']:.0%} | {item['recommended_action']}"
                for item in findings
            ]
            return "故障诊断：\n" + "\n".join(lines)
        return "我可以回答主机健康度、机舱告警、趋势分析、故障诊断和维护建议。"


__all__ = ["IntelligentEngineChannel", "EngineSnapshot"]
