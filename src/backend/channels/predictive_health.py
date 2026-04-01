#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Predictive Health Management (PHM) - 预测性健康管理

参考 SVESSEL Onboard CBM (Condition Based Maintenance) 模块:
- 基于状态的维护 (而非定期维护)
- 趋势外推与故障预测
- 剩余使用寿命 (RUL) 估算
- 维护窗口建议

参考 AUTOSHIP KET (关键核心技术):
- 新型智能资产管理
- 高级仿真和数据分析
- 数字孪生 AI 轮机长
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import math

from .marine_base import MarineChannel, ChannelStatus, ChannelPriority


class ComponentType(Enum):
    """设备/部件类型."""
    MAIN_ENGINE = "main_engine"
    AUX_ENGINE = "aux_engine"
    TURBOCHARGER = "turbocharger"
    COOLING_PUMP = "cooling_pump"
    LUBE_OIL_PUMP = "lube_oil_pump"
    FUEL_PUMP = "fuel_pump"
    SEPARATOR = "separator"
    COMPRESSOR = "compressor"
    STEERING_GEAR = "steering_gear"
    BOW_THRUSTER = "bow_thruster"
    GENERATOR = "generator"
    PROPELLER_SHAFT = "propeller_shaft"
    HULL_STRUCTURE = "hull_structure"


class HealthTrend(Enum):
    """健康趋势."""
    STABLE = "stable"
    DEGRADING_SLOW = "degrading_slow"
    DEGRADING_FAST = "degrading_fast"
    IMPROVING = "improving"
    CRITICAL = "critical"


class MaintenancePriority(Enum):
    """维护优先级."""
    IMMEDIATE = "immediate"     # 立即维护
    NEXT_PORT = "next_port"     # 下个港口维护
    SCHEDULED = "scheduled"     # 按计划维护
    MONITOR = "monitor"         # 持续监测
    OK = "ok"                   # 无需维护


@dataclass
class ComponentHealth:
    """部件健康状态."""
    component_id: str
    component_type: ComponentType
    health_score: float          # 0-100
    trend: HealthTrend
    rul_hours: float             # 剩余使用寿命 (小时)
    confidence: float            # 预测置信度 0-1
    last_maintenance: Optional[str] = None
    operating_hours: float = 0.0
    failure_probability_30d: float = 0.0  # 30天内故障概率


@dataclass
class HealthSample:
    """健康指标采样."""
    timestamp: datetime
    component_id: str
    parameter: str
    value: float
    unit: str


@dataclass
class MaintenanceRecommendation:
    """维护建议."""
    component_id: str
    component_type: str
    priority: MaintenancePriority
    action: str
    reason: str
    estimated_hours: float       # 预计维护耗时
    spare_parts: List[str]
    deadline: Optional[str] = None


# 设备正常参数范围与退化模型 (基于典型船用中速柴油机)
COMPONENT_MODELS = {
    ComponentType.MAIN_ENGINE: {
        "mtbf_hours": 8000,       # 平均故障间隔
        "ideal_score": 95,
        "degradation_rate_per_1000h": 2.5,  # 每1000小时退化分数
        "critical_threshold": 55,
        "parameters": {
            "coolant_temp": {"normal": (75, 85), "warn": (85, 92), "alarm": (92, 120), "unit": "°C"},
            "oil_pressure": {"normal": (2.5, 5.0), "warn": (2.0, 2.5), "alarm": (0, 2.0), "unit": "bar"},
            "vibration": {"normal": (0, 4.5), "warn": (4.5, 7.0), "alarm": (7.0, 20), "unit": "mm/s"},
            "exhaust_temp": {"normal": (300, 420), "warn": (420, 480), "alarm": (480, 600), "unit": "°C"},
        },
    },
    ComponentType.TURBOCHARGER: {
        "mtbf_hours": 12000,
        "ideal_score": 95,
        "degradation_rate_per_1000h": 1.8,
        "critical_threshold": 50,
        "parameters": {
            "bearing_temp": {"normal": (40, 70), "warn": (70, 85), "alarm": (85, 120), "unit": "°C"},
            "vibration": {"normal": (0, 5.0), "warn": (5.0, 8.0), "alarm": (8.0, 20), "unit": "mm/s"},
            "speed_deviation": {"normal": (0, 3), "warn": (3, 8), "alarm": (8, 20), "unit": "%"},
        },
    },
    ComponentType.STEERING_GEAR: {
        "mtbf_hours": 15000,
        "ideal_score": 98,
        "degradation_rate_per_1000h": 1.2,
        "critical_threshold": 60,
        "parameters": {
            "hydraulic_pressure": {"normal": (120, 180), "warn": (100, 120), "alarm": (0, 100), "unit": "bar"},
            "response_time": {"normal": (0, 5), "warn": (5, 8), "alarm": (8, 20), "unit": "s"},
        },
    },
    ComponentType.PROPELLER_SHAFT: {
        "mtbf_hours": 20000,
        "ideal_score": 97,
        "degradation_rate_per_1000h": 0.8,
        "critical_threshold": 65,
        "parameters": {
            "vibration": {"normal": (0, 3.0), "warn": (3.0, 5.0), "alarm": (5.0, 15), "unit": "mm/s"},
            "bearing_temp": {"normal": (35, 55), "warn": (55, 70), "alarm": (70, 100), "unit": "°C"},
        },
    },
}


class PredictiveHealthChannel(MarineChannel):
    """预测性健康管理 Channel.

    对标 SVESSEL Onboard CBM + AUTOSHIP 数字孪生 AI 轮机长。
    实现设备退化建模、RUL估算、智能维护建议。
    """

    name = "predictive_health"
    description = "预测性健康管理 (PHM) - CBM状态监测、RUL预测与智能维护建议"
    version = "1.0.0"
    priority = ChannelPriority.P0
    dependencies = ["intelligent_engine", "engine_monitor"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._components: Dict[str, ComponentHealth] = {}
        self._samples: Dict[str, List[HealthSample]] = {}
        self._recommendations: List[MaintenanceRecommendation] = []
        self._max_samples_per_component = 200

    def initialize(self) -> bool:
        # 初始化默认关键设备
        defaults = [
            ("ME-1", ComponentType.MAIN_ENGINE, 2500),
            ("TC-1", ComponentType.TURBOCHARGER, 2500),
            ("SG-1", ComponentType.STEERING_GEAR, 3000),
            ("PS-1", ComponentType.PROPELLER_SHAFT, 4000),
        ]
        for comp_id, comp_type, hours in defaults:
            self._register_component(comp_id, comp_type, hours)

        self._initialized = True
        self._set_health(ChannelStatus.OK, "PHM initialized with default components")
        return True

    def _register_component(
        self, component_id: str, component_type: ComponentType, operating_hours: float = 0
    ) -> ComponentHealth:
        """注册待监测部件."""
        model = COMPONENT_MODELS.get(component_type, {})
        mtbf = model.get("mtbf_hours", 10000)
        ideal = model.get("ideal_score", 95)
        deg_rate = model.get("degradation_rate_per_1000h", 2.0)

        # 根据运行小时数计算当前健康分
        degraded = deg_rate * operating_hours / 1000
        health_score = max(0, ideal - degraded)
        rul = max(0, (health_score - model.get("critical_threshold", 50)) / deg_rate * 1000)

        comp = ComponentHealth(
            component_id=component_id,
            component_type=component_type,
            health_score=round(health_score, 1),
            trend=HealthTrend.STABLE,
            rul_hours=round(rul, 0),
            confidence=0.75,
            operating_hours=operating_hours,
            failure_probability_30d=self._calc_failure_prob(health_score, rul),
        )
        self._components[component_id] = comp
        self._samples[component_id] = []
        return comp

    @staticmethod
    def _calc_failure_prob(health_score: float, rul_hours: float) -> float:
        """计算30天内故障概率 (韦伯尔分布简化)."""
        hours_30d = 30 * 24
        if rul_hours <= 0:
            return 0.95
        ratio = hours_30d / max(rul_hours, 1)
        prob = 1 - math.exp(-(ratio ** 2.5))
        return round(min(0.99, max(0.01, prob)), 3)

    def ingest_parameter(
        self, component_id: str, parameter: str, value: float, unit: str = ""
    ) -> Optional[Dict]:
        """采集设备参数并更新健康状态."""
        comp = self._components.get(component_id)
        if comp is None:
            return None

        sample = HealthSample(
            timestamp=datetime.now(),
            component_id=component_id,
            parameter=parameter,
            value=value,
            unit=unit,
        )
        samples = self._samples.setdefault(component_id, [])
        samples.append(sample)
        if len(samples) > self._max_samples_per_component:
            self._samples[component_id] = samples[-self._max_samples_per_component:]

        # 评估该参数对健康分的影响
        deviation = self._evaluate_parameter(comp.component_type, parameter, value)
        if deviation is not None:
            comp.health_score = max(0, min(100, comp.health_score + deviation))
            comp.trend = self._detect_trend(component_id)
            comp.rul_hours = self._estimate_rul(component_id)
            comp.failure_probability_30d = self._calc_failure_prob(comp.health_score, comp.rul_hours)

        return {
            "component_id": component_id,
            "parameter": parameter,
            "value": value,
            "health_score": comp.health_score,
            "trend": comp.trend.value,
        }

    def _evaluate_parameter(
        self, comp_type: ComponentType, parameter: str, value: float
    ) -> Optional[float]:
        """评估参数对健康分的影响."""
        model = COMPONENT_MODELS.get(comp_type)
        if model is None:
            return None
        param_spec = model.get("parameters", {}).get(parameter)
        if param_spec is None:
            return None

        lo_normal, hi_normal = param_spec["normal"]
        lo_warn, hi_warn = param_spec["warn"]

        if lo_normal <= value <= hi_normal:
            return 0.05  # 正常范围, 微小增益
        elif lo_warn <= value <= hi_warn or lo_normal > value >= lo_warn:
            return -0.3  # 警告范围, 轻微扣分
        else:
            return -1.5  # 告警范围, 显著扣分

    def _detect_trend(self, component_id: str) -> HealthTrend:
        """趋势检测 (基于最近N个采样)."""
        samples = self._samples.get(component_id, [])
        if len(samples) < 5:
            return HealthTrend.STABLE

        recent = samples[-20:]
        # 提取该部件最频繁的参数
        param_counts: Dict[str, List[float]] = {}
        for s in recent:
            param_counts.setdefault(s.parameter, []).append(s.value)

        # 选择采样最多的参数做趋势分析
        best_param = max(param_counts, key=lambda k: len(param_counts[k]))
        values = param_counts[best_param]
        if len(values) < 3:
            return HealthTrend.STABLE

        mid = len(values) // 2
        first_avg = sum(values[:mid]) / mid
        second_avg = sum(values[mid:]) / max(len(values) - mid, 1)
        diff_pct = (second_avg - first_avg) / max(abs(first_avg), 0.01) * 100

        comp = self._components.get(component_id)
        if comp and comp.health_score < COMPONENT_MODELS.get(
            comp.component_type, {}
        ).get("critical_threshold", 50):
            return HealthTrend.CRITICAL

        if diff_pct > 10:
            return HealthTrend.DEGRADING_FAST
        elif diff_pct > 3:
            return HealthTrend.DEGRADING_SLOW
        elif diff_pct < -3:
            return HealthTrend.IMPROVING
        return HealthTrend.STABLE

    def _estimate_rul(self, component_id: str) -> float:
        """剩余使用寿命估算 (线性外推 + 退化模型)."""
        comp = self._components.get(component_id)
        if comp is None:
            return 0

        model = COMPONENT_MODELS.get(comp.component_type, {})
        threshold = model.get("critical_threshold", 50)
        deg_rate = model.get("degradation_rate_per_1000h", 2.0)

        remaining_score = comp.health_score - threshold
        if remaining_score <= 0:
            return 0

        # 基于趋势调整退化率
        trend_factor = {
            HealthTrend.STABLE: 1.0,
            HealthTrend.DEGRADING_SLOW: 1.5,
            HealthTrend.DEGRADING_FAST: 3.0,
            HealthTrend.IMPROVING: 0.5,
            HealthTrend.CRITICAL: 5.0,
        }.get(comp.trend, 1.0)

        effective_rate = deg_rate * trend_factor
        if effective_rate <= 0:
            return 99999

        rul = remaining_score / effective_rate * 1000
        comp.confidence = min(0.95, 0.6 + len(self._samples.get(component_id, [])) * 0.002)
        return round(max(0, rul), 0)

    def generate_maintenance_plan(self) -> List[MaintenanceRecommendation]:
        """生成维护计划."""
        recs = []
        for comp_id, comp in self._components.items():
            priority = self._determine_priority(comp)
            if priority == MaintenancePriority.OK:
                continue

            action, parts = self._maintenance_action(comp)
            deadline = None
            if priority == MaintenancePriority.IMMEDIATE:
                deadline = datetime.now().isoformat()
            elif priority == MaintenancePriority.NEXT_PORT:
                deadline = (datetime.now() + timedelta(days=7)).isoformat()
            elif priority == MaintenancePriority.SCHEDULED:
                deadline = (datetime.now() + timedelta(days=30)).isoformat()

            recs.append(MaintenanceRecommendation(
                component_id=comp_id,
                component_type=comp.component_type.value,
                priority=priority,
                action=action,
                reason=f"健康分 {comp.health_score}, 趋势 {comp.trend.value}, "
                       f"RUL {comp.rul_hours}h, 30天故障概率 {comp.failure_probability_30d*100:.1f}%",
                estimated_hours=self._estimate_maintenance_hours(comp),
                spare_parts=parts,
                deadline=deadline,
            ))

        self._recommendations = sorted(recs, key=lambda r: {
            MaintenancePriority.IMMEDIATE: 0,
            MaintenancePriority.NEXT_PORT: 1,
            MaintenancePriority.SCHEDULED: 2,
            MaintenancePriority.MONITOR: 3,
        }.get(r.priority, 4))

        return self._recommendations

    def _determine_priority(self, comp: ComponentHealth) -> MaintenancePriority:
        if comp.health_score < 40 or comp.trend == HealthTrend.CRITICAL:
            return MaintenancePriority.IMMEDIATE
        elif comp.health_score < 60 or comp.trend == HealthTrend.DEGRADING_FAST:
            return MaintenancePriority.NEXT_PORT
        elif comp.health_score < 75 or comp.trend == HealthTrend.DEGRADING_SLOW:
            return MaintenancePriority.SCHEDULED
        elif comp.health_score < 85:
            return MaintenancePriority.MONITOR
        return MaintenancePriority.OK

    @staticmethod
    def _maintenance_action(comp: ComponentHealth) -> Tuple[str, List[str]]:
        actions = {
            ComponentType.MAIN_ENGINE: (
                "主机全面检修: 检查气缸套、活塞环、喷油器、冷却系统",
                ["气缸套密封圈", "活塞环组", "喷油器总成", "冷却水泵密封"],
            ),
            ComponentType.TURBOCHARGER: (
                "涡轮增压器检修: 检查轴承、叶轮、密封件",
                ["涡轮轴承", "压气机叶轮", "密封环"],
            ),
            ComponentType.STEERING_GEAR: (
                "舵机检修: 检查液压系统、密封件、响应时间",
                ["液压油", "密封件套装", "电磁阀"],
            ),
            ComponentType.PROPELLER_SHAFT: (
                "推进轴系检修: 检查轴承温度、振动、密封",
                ["尾轴密封", "中间轴承", "润滑脂"],
            ),
        }
        return actions.get(comp.component_type, ("常规检修", []))

    @staticmethod
    def _estimate_maintenance_hours(comp: ComponentHealth) -> float:
        base_hours = {
            ComponentType.MAIN_ENGINE: 48,
            ComponentType.TURBOCHARGER: 16,
            ComponentType.STEERING_GEAR: 8,
            ComponentType.PROPELLER_SHAFT: 24,
        }
        return base_hours.get(comp.component_type, 12)

    def get_fleet_health_summary(self) -> Dict[str, Any]:
        """获取所有部件健康摘要."""
        components = {}
        total_score = 0
        count = 0
        critical_count = 0

        for comp_id, comp in self._components.items():
            components[comp_id] = {
                "type": comp.component_type.value,
                "health_score": comp.health_score,
                "trend": comp.trend.value,
                "rul_hours": comp.rul_hours,
                "confidence": round(comp.confidence, 2),
                "operating_hours": comp.operating_hours,
                "failure_prob_30d": comp.failure_probability_30d,
            }
            total_score += comp.health_score
            count += 1
            if comp.health_score < 60:
                critical_count += 1

        avg_score = round(total_score / max(count, 1), 1)
        self.generate_maintenance_plan()

        return {
            "overall_health_score": avg_score,
            "overall_status": "critical" if critical_count > 0 else (
                "attention" if avg_score < 80 else "good"
            ),
            "components": components,
            "critical_components": critical_count,
            "total_components": count,
            "maintenance_recommendations": [
                {
                    "component": r.component_id,
                    "priority": r.priority.value,
                    "action": r.action,
                    "reason": r.reason,
                    "estimated_hours": r.estimated_hours,
                    "deadline": r.deadline,
                }
                for r in self._recommendations[:5]
            ],
            "next_maintenance_window": self._recommendations[0].deadline
            if self._recommendations else None,
        }

    def get_status(self) -> Dict[str, Any]:
        summary = self.get_fleet_health_summary()
        return {
            "channel": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": "ok" if summary["overall_status"] == "good" else "warn",
            "health_message": f"PHM {summary['overall_status']}: "
                              f"avg={summary['overall_health_score']}, "
                              f"critical={summary['critical_components']}",
            **summary,
        }

    def shutdown(self) -> bool:
        self._initialized = False
        self._set_health(ChannelStatus.OFF, "Shut down")
        return True
