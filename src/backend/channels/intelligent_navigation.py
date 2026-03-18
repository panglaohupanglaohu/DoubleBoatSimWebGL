# -*- coding: utf-8 -*-
"""
Intelligent Navigation Channel - 智能导航模块

实现三星 S.VESSEL i-Navigation 核心功能:
- CPA/TCPA 计算 (碰撞风险评估)
- 避碰预警
- 航线优化建议
- 航行安全监控

作者：CaptainCatamaran 🐱⛵
版本：Phase 2 - 2026-03-14
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from .marine_base import MarineChannel, ChannelStatus, ChannelPriority
from .maritime_scene_model import MaritimeSceneModel
import math


COLREGS_GUIDANCE = {
    "head_on": {
        "rule": "Rule 14",
        "summary": "两船对遇时，应各自向右转向并安全通过。",
        "default_action": "立即向右转向，拉开 CPA，并广播避让意图。",
    },
    "crossing_starboard": {
        "rule": "Rule 15/16",
        "summary": "目标位于本船右舷前方，本船为让路船。",
        "default_action": "优先减速或向右转向，避免抢越船首。",
    },
    "crossing_port": {
        "rule": "Rule 17",
        "summary": "目标位于本船左舷前方，本船通常为直航船。",
        "default_action": "保持态势监视，必要时执行最后时刻避险动作。",
    },
    "overtaking": {
        "rule": "Rule 13",
        "summary": "追越船应始终让清被追越船。",
        "default_action": "避免贴近追越，预留横向安全间距并明确改向。",
    },
}


@dataclass
class AISTarget:
    """AIS 目标数据."""
    mmsi: int
    latitude: float
    longitude: float
    course: float  # 航向 (度)
    speed: float   # 航速 (节)
    heading: float # 船首向 (度)
    vessel_type: str = "Unknown"
    nav_status: str = "normal"
    length: float = 0.0
    width: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CollisionRisk:
    """碰撞风险评估结果."""
    target_mmsi: int
    cpa: float          # 最近会遇距离 (海里)
    tcpa: float         # 最近会遇时间 (分钟)
    risk_level: str     # safe/caution/warning/danger
    bearing: float      # 目标方位 (度)
    range: float        # 目标距离 (海里)
    dcpa_limit: float   # CPA 限制 (海里)
    tcpa_limit: float   # TCPA 限制 (分钟)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mmsi": self.target_mmsi,
            "cpa": round(self.cpa, 3),
            "tcpa": round(self.tcpa, 2),
            "risk_level": self.risk_level,
            "bearing": round(self.bearing, 1),
            "range": round(self.range, 3),
            "dcpa_limit": self.dcpa_limit,
            "tcpa_limit": self.tcpa_limit
        }


class IntelligentNavigationChannel(MarineChannel):
    """智能导航 Channel.
    
    实现功能:
    - CPA/TCPA 计算
    - 碰撞风险分级
    - 避碰预警
    - 航线优化建议
    """
    
    name = "intelligent_navigation"
    description = "智能导航 (航线优化 + 避碰预警)"
    version = "1.0.0"
    priority = ChannelPriority.P0
    dependencies: List[str] = ["navigation_data", "vessel_ais"]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.config = config or {}
        self._config = config or {}
        
        # 本船数据
        self.own_ship = {
            "latitude": 0.0,
            "longitude": 0.0,
            "course": 0.0,
            "speed": 0.0
        }
        
        # AIS 目标列表
        self.ais_targets: List[AISTarget] = []
        
        # 碰撞风险阈值
        self.dcpa_limit = self.config.get("dcpa_limit", 0.5)  # 海里
        self.tcpa_limit = self.config.get("tcpa_limit", 30.0)  # 分钟
        
        # 风险记录
        self.risk_history: List[CollisionRisk] = []
        self.scene_model = MaritimeSceneModel()
    
    def initialize(self) -> bool:
        """初始化 Channel."""
        try:
            is_valid, errors = self.validate_config()
            if not is_valid:
                self._set_health(ChannelStatus.ERROR, f"配置验证失败：{errors}")
                return False
            
            self._set_health(ChannelStatus.OK, "智能导航系统就绪")
            self._initialized = True
            return True
        except Exception as e:
            self._set_health(ChannelStatus.ERROR, str(e))
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取 Channel 状态."""
        report = self.generate_navigation_report() if self._initialized else None
        return {
            "name": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "health": self._health.status.value,
            "health_message": self._health.message,
            "own_ship": self.own_ship,
            "ais_targets_count": len(self.ais_targets),
            "risk_thresholds": {
                "dcpa_limit": self.dcpa_limit,
                "tcpa_limit": self.tcpa_limit
            },
            "active_risks": len(report["collision_risks"]) if report else 0,
            "highest_risk": report["risk_index"]["highest_risk"] if report else "safe",
            "colregs_cases": len(report["colregs_assessments"]) if report else 0,
        }
    
    def shutdown(self) -> bool:
        """关闭 Channel."""
        try:
            self._initialized = False
            self._set_health(ChannelStatus.OFF, "Shutdown")
            return True
        except Exception:
            return False
    
    def update_own_ship(self, latitude: float, longitude: float, 
                       course: float, speed: float):
        """更新本船数据."""
        self.own_ship = {
            "latitude": latitude,
            "longitude": longitude,
            "course": course,
            "speed": speed
        }
    
    def add_ais_target(self, target: AISTarget):
        """添加 AIS 目标."""
        self.ais_targets.append(target)
        # 限制目标数量
        if len(self.ais_targets) > 100:
            self.ais_targets = self.ais_targets[-100:]
    
    def calculate_cpa_tcpa(self, target: AISTarget) -> CollisionRisk:
        """
        计算 CPA (最近会遇距离) 和 TCPA (最近会遇时间)
        
        使用相对运动法计算两船的 CPA 和 TCPA
        
        Returns:
            CollisionRisk 对象
        """
        # 本船数据
        lat1 = math.radians(self.own_ship["latitude"])
        lon1 = math.radians(self.own_ship["longitude"])
        cog1 = math.radians(self.own_ship["course"])
        sog1 = self.own_ship["speed"] * 0.514444  # 节 → m/s
        
        # 目标船数据
        lat2 = math.radians(target.latitude)
        lon2 = math.radians(target.longitude)
        cog2 = math.radians(target.course)
        sog2 = target.speed * 0.514444  # 节 → m/s
        
        # 计算距离和方位
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        range_m = 6371000 * c  # 地球半径 × 角距离 (米)
        range_nm = range_m / 1852.0  # 米 → 海里
        
        # 计算方位
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dlon)
        bearing = math.degrees(math.atan2(y, x))
        bearing = (bearing + 360) % 360
        
        # 计算相对速度和相对方位
        v1x = sog1 * math.sin(cog1)
        v1y = sog1 * math.cos(cog1)
        v2x = sog2 * math.sin(cog2)
        v2y = sog2 * math.cos(cog2)
        
        # 相对速度
        vrx = v2x - v1x
        vry = v2y - v1y
        vr = math.sqrt(vrx**2 + vry**2)  # 相对速度 (m/s)
        
        # 相对运动方位
        if vr > 0.01:  # 避免除零
            relative_bearing = math.degrees(math.atan2(vrx, vry))
        else:
            relative_bearing = 0
        
        # 计算 CPA 和 TCPA
        if vr > 0.01:
            # CPA = 距离 × sin(相对方位差)
            angle_diff = math.radians(bearing) - math.atan2(vrx, vry)
            cpa_m = range_m * abs(math.sin(angle_diff))
            cpa_nm = cpa_m / 1852.0
            
            # TCPA = 距离 × cos(相对方位差) / 相对速度
            tcpa_s = range_m * math.cos(angle_diff) / vr
            tcpa_min = tcpa_s / 60.0
        else:
            cpa_nm = range_nm
            tcpa_min = 9999.0
        
        # 风险评估
        risk_level = self._assess_risk(cpa_nm, tcpa_min)
        
        return CollisionRisk(
            target_mmsi=target.mmsi,
            cpa=cpa_nm,
            tcpa=tcpa_min,
            risk_level=risk_level,
            bearing=bearing,
            range=range_nm,
            dcpa_limit=self.dcpa_limit,
            tcpa_limit=self.tcpa_limit
        )
    
    def _assess_risk(self, cpa: float, tcpa: float) -> str:
        """
        评估碰撞风险等级
        
        Returns:
            safe/caution/warning/danger
        """
        # TCPA 为负表示已经通过
        if tcpa < 0:
            return "safe"
        
        # 危险：CPA < 0.1 海里 且 TCPA < 6 分钟
        if cpa < 0.1 and tcpa < 6:
            return "danger"
        
        # 警告：CPA < 0.3 海里 且 TCPA < 15 分钟
        if cpa < 0.3 and tcpa < 15:
            return "warning"
        
        # 注意：CPA < 0.5 海里 且 TCPA < 30 分钟
        if cpa < 0.5 and tcpa < 30:
            return "caution"
        
        return "safe"

    def _build_scene_context(self) -> Dict[str, Any]:
        return self.scene_model.evaluate(self.own_ship, self.ais_targets)

    def _resolve_contextual_rule(self, target: AISTarget, scene_context: Dict[str, Any]) -> Dict[str, str]:
        vessel_type = (target.vessel_type or "").lower()
        if target.nav_status == "restricted_manoeuvrability" or vessel_type in {"tug", "dredger", "offshore support vessel"}:
            return {
                "contextual_rule": "Rule 18",
                "priority_basis": "Target treated as restricted in ability to manoeuvre.",
            }

        scene_type = scene_context.get("scene_type")
        if scene_type == "narrow_channel":
            return {
                "contextual_rule": "Rule 9",
                "priority_basis": "Channel geometry constrains both vessels.",
            }
        if scene_type == "port_approach":
            return {
                "contextual_rule": "Rule 9/10",
                "priority_basis": "Port traffic lanes and entry constraints are active.",
            }
        if scene_type == "ice_navigation":
            return {
                "contextual_rule": "Rule 19",
                "priority_basis": "Restricted visibility / ice-navigation safeguards applied.",
            }

        return {
            "contextual_rule": "Rule 5/7/8",
            "priority_basis": "Standard watchkeeping and early action basis.",
        }

    def classify_colregs_encounter(self, target: AISTarget, risk: Optional[CollisionRisk] = None) -> Dict[str, Any]:
        """基于目标相对方位和运动趋势给出简化 COLREGs 遭遇分类。"""
        risk = risk or self.calculate_cpa_tcpa(target)
        scene_context = self._build_scene_context()
        bearing = risk.bearing
        relative_heading = abs((self.own_ship["course"] - target.course + 180) % 360 - 180)
        speed_delta = max(0.0, self.own_ship["speed"] - target.speed)

        if (bearing <= 15 or bearing >= 345) and relative_heading >= 150:
            encounter = "head_on"
            role = "both_give_way"
        elif 112.5 <= bearing <= 247.5 and speed_delta > 1.5:
            encounter = "overtaking"
            role = "give_way"
        elif 0 < bearing < 112.5:
            encounter = "crossing_starboard"
            role = "give_way"
        else:
            encounter = "crossing_port"
            role = "stand_on"

        guidance = COLREGS_GUIDANCE[encounter]
        urgency = "immediate" if risk.risk_level in {"danger", "warning"} else "monitor"
        contextual_rule = self._resolve_contextual_rule(target, scene_context)
        return {
            "target_mmsi": target.mmsi,
            "target_type": target.vessel_type,
            "encounter_type": encounter,
            "role": role,
            "rule": guidance["rule"],
            "contextual_rule": contextual_rule["contextual_rule"],
            "priority_basis": contextual_rule["priority_basis"],
            "summary": guidance["summary"],
            "recommended_action": f"{guidance['default_action']} 场景约束：{scene_context['scene_type']}。",
            "urgency": urgency,
            "bearing": round(bearing, 1),
            "range_nm": round(risk.range, 3),
            "risk_level": risk.risk_level,
            "scene_type": scene_context["scene_type"],
        }

    def generate_colregs_assessment(self) -> List[Dict[str, Any]]:
        """生成面向控制层的 COLREGs 规则评估列表。"""
        assessments: List[Dict[str, Any]] = []
        for target in self.ais_targets:
            risk = self.calculate_cpa_tcpa(target)
            if risk.risk_level == "safe":
                continue
            assessments.append(self.classify_colregs_encounter(target, risk))

        risk_rank = {"danger": 0, "warning": 1, "caution": 2, "safe": 3}
        assessments.sort(key=lambda item: (risk_rank.get(item["risk_level"], 4), item["range_nm"]))
        return assessments
    
    def get_collision_risks(self) -> List[CollisionRisk]:
        """获取所有 AIS 目标的碰撞风险."""
        risks = []
        for target in self.ais_targets:
            risk = self.calculate_cpa_tcpa(target)
            if risk.risk_level != "safe":  # 只返回有风险的目标
                risks.append(risk)
        
        # 按风险等级排序
        risk_order = {"danger": 0, "warning": 1, "caution": 2, "safe": 3}
        risks.sort(key=lambda r: (risk_order.get(r.risk_level, 4), r.tcpa))
        
        self.risk_history = risks
        return risks
    
    def get_avoidance_advice(self, risk: CollisionRisk) -> str:
        """
        生成避碰建议
        
        Returns:
            避碰建议文本
        """
        if risk.risk_level == "safe":
            return "无碰撞风险，保持当前航向航速"

        target = next((item for item in self.ais_targets if item.mmsi == risk.target_mmsi), None)
        if target is not None:
            assessment = self.classify_colregs_encounter(target, risk)
            return (
                f"{assessment['summary']} 当前风险等级 {risk.risk_level}，"
                f"CPA {risk.cpa:.2f} 海里，TCPA {risk.tcpa:.1f} 分钟。"
                f"建议：{assessment['recommended_action']}"
            )
        
        advice = []
        
        # 根据目标方位和 CPA 生成建议
        bearing = risk.bearing
        
        if 0 <= bearing < 90:  # 右前方
            advice.append("目标位于右前方")
            advice.append("建议向右转向或减速")
        elif 90 <= bearing < 180:  # 右后方
            advice.append("目标位于右后方")
            advice.append("保持航向，注意观察")
        elif 180 <= bearing < 270:  # 左后方
            advice.append("目标位于左后方")
            advice.append("保持航向航速")
        else:  # 左前方
            advice.append("目标位于左前方")
            advice.append("建议向右转向 (COLREGs 规则)")
        
        # 根据 TCPA 紧急程度
        if risk.tcpa < 3:
            advice.append("⚠️ 紧急！立即采取行动")
        elif risk.tcpa < 10:
            advice.append("建议尽快采取避让行动")
        
        return "。".join(advice) + "。"
    
    def generate_navigation_report(self) -> Dict[str, Any]:
        """生成航行安全报告."""
        risks = self.get_collision_risks()
        colregs = self.generate_colregs_assessment()
        scene_context = self._build_scene_context()
        highest_risk = risks[0].risk_level if risks else "safe"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "own_ship": self.own_ship,
            "ais_targets_total": len(self.ais_targets),
            "collision_risks": [r.to_dict() for r in risks],
            "scene_context": scene_context,
            "colregs_assessments": colregs,
            "recommended_manoeuvres": [item["recommended_action"] for item in colregs[:3]],
            "risk_summary": {
                "danger": sum(1 for r in risks if r.risk_level == "danger"),
                "warning": sum(1 for r in risks if r.risk_level == "warning"),
                "caution": sum(1 for r in risks if r.risk_level == "caution"),
                "safe": len(self.ais_targets) - len(risks)
            },
            "risk_index": {
                "value": min(
                    100,
                    len(risks) * 20
                    + (35 if highest_risk == "danger" else 20 if highest_risk == "warning" else 8 if highest_risk == "caution" else 0),
                ),
                "highest_risk": highest_risk,
            },
            "overall_status": "danger" if any(r.risk_level == "danger" for r in risks)
                           else "warning" if any(r.risk_level == "warning" for r in risks)
                           else "caution" if any(r.risk_level == "caution" for r in risks)
                           else "safe"
        }
        
        return report
    
    def query_navigation_status(self, query: str) -> str:
        """
        自然语言查询航行状态 (供 Bridge Chat 调用)
        
        Args:
            query: 用户问题
        
        Returns:
            回答文本
        """
        query = query.lower()
        
        if "碰撞" in query or "风险" in query or "危险" in query:
            risks = self.get_collision_risks()
            if not risks:
                return "当前无碰撞风险，所有 AIS 目标安全。"
            
            danger_count = sum(1 for r in risks if r.risk_level == "danger")
            warning_count = sum(1 for r in risks if r.risk_level == "warning")
            
            response = f"发现 {len(risks)} 个潜在碰撞目标。\n"
            if danger_count > 0:
                response += f"⚠️ {danger_count} 个危险目标！\n"
            if warning_count > 0:
                response += f"⚠️ {warning_count} 个警告目标。\n"
            
            # 返回最危险的目标
            if risks:
                worst = risks[0]
                response += f"\n最危险目标 MMSI {worst.target_mmsi}:\n"
                response += f"- CPA: {worst.cpa:.2f} 海里\n"
                response += f"- TCPA: {worst.tcpa:.1f} 分钟\n"
                response += f"- 方位：{worst.bearing:.0f}°\n"
                response += f"- 距离：{worst.range:.2f} 海里\n"
                response += f"\n建议：{self.get_avoidance_advice(worst)}"
            
            return response
        
        elif "位置" in query or "在哪" in query:
            return f"当前船位：{self.own_ship['latitude']:.4f}°N, {self.own_ship['longitude']:.4f}°E\n" \
                   f"航向：{self.own_ship['course']:.1f}°\n" \
                   f"航速：{self.own_ship['speed']:.1f} 节"
        
        elif "ais" in query.lower() or "目标" in query:
            return f"当前追踪 {len(self.ais_targets)} 个 AIS 目标。\n" \
                   f"其中 {len(self.get_collision_risks())} 个存在碰撞风险。"
        
        else:
            return "我可以帮您查询：\n" \
                   "- 碰撞风险\n" \
                   "- 当前船位\n" \
                   "- AIS 目标信息\n\n" \
                   "请问具体想了解什么？"


# 导出
__all__ = [
    "IntelligentNavigationChannel",
    "AISTarget",
    "CollisionRisk"
]
