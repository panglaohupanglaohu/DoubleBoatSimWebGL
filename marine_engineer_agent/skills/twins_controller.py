"""
数字孪生控制技能模块

为 DoubleBoatSimWebGL 数字孪生系统提供智能控制能力。
支持场景配置、船只控制、传感器数据模拟、故障注入等功能。

:author: marine_engineer_agent
:version: 1.0.0
:since: 2026-03-10
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import random
import math

# 导入配置类
from marine_config import MarineEngineerConfig

# 配置模块日志
logger = logging.getLogger(__name__)


# ============== 场景预设配置 ==============

SCENE_PRESETS = {
    "calm": {
        "name": "平静海面",
        "weather": {
            "waveHeight": 0.5,
            "waveSpeed": 0.3,
            "windSpeed": 5,
            "windDirection": 90,
            "waterColor": "#1E90FF"
        },
        "physics": {
            "gravity": -9.8,
            "waterDensity": 1025,
            "linearDamping": 0.1
        },
        "lighting": {
            "ambientIntensity": 0.6,
            "directionalIntensity": 1.0,
            "skyColor": "#87CEEB"
        }
    },
    "stormy": {
        "name": "暴风雨",
        "weather": {
            "waveHeight": 3.5,
            "waveSpeed": 0.8,
            "windSpeed": 25,
            "windDirection": 180,
            "waterColor": "#2F4F4F"
        },
        "physics": {
            "gravity": -9.8,
            "waterDensity": 1025,
            "linearDamping": 0.3
        },
        "lighting": {
            "ambientIntensity": 0.3,
            "directionalIntensity": 0.5,
            "skyColor": "#4A4A4A"
        }
    },
    "sunset": {
        "name": "日落",
        "weather": {
            "waveHeight": 1.0,
            "waveSpeed": 0.4,
            "windSpeed": 8,
            "windDirection": 270,
            "waterColor": "#FF6347"
        },
        "physics": {
            "gravity": -9.8,
            "waterDensity": 1025,
            "linearDamping": 0.15
        },
        "lighting": {
            "ambientIntensity": 0.4,
            "directionalIntensity": 0.7,
            "skyColor": "#FF4500"
        }
    },
    "night": {
        "name": "夜晚",
        "weather": {
            "waveHeight": 0.8,
            "waveSpeed": 0.35,
            "windSpeed": 6,
            "windDirection": 45,
            "waterColor": "#000033"
        },
        "physics": {
            "gravity": -9.8,
            "waterDensity": 1025,
            "linearDamping": 0.12
        },
        "lighting": {
            "ambientIntensity": 0.15,
            "directionalIntensity": 0.2,
            "skyColor": "#000022"
        }
    }
}


# ============== 传感器数据模拟 ==============

def generate_sensor_data(sensor_type: str, timestamp: Optional[str] = None) -> Dict[str, Any]:
    """
    生成模拟传感器数据
    
    :param sensor_type: 传感器类型 (gps/imu/weather/engine/fuel/rudder)
    :param timestamp: 时间戳 (ISO 格式)，默认当前时间
    :return: 传感器数据字典
    """
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    if sensor_type == "gps":
        return {
            "timestamp": timestamp,
            "sensor_id": "GPS-001",
            "sensor_type": "GPS",
            "data": {
                "latitude": 31.2304 + random.uniform(-0.001, 0.001),
                "longitude": 121.4737 + random.uniform(-0.001, 0.001),
                "altitude": 10.5 + random.uniform(-0.5, 0.5),
                "speed": 12.3 + random.uniform(-0.5, 0.5),
                "heading": 135.0 + random.uniform(-2, 2)
            },
            "quality": {
                "signal_strength": random.randint(85, 100),
                "accuracy": "high"
            }
        }
    
    elif sensor_type == "imu":
        return {
            "timestamp": timestamp,
            "sensor_id": "IMU-001",
            "sensor_type": "IMU",
            "data": {
                "roll": random.uniform(-5, 5),
                "pitch": random.uniform(-3, 3),
                "yaw": random.uniform(0, 360),
                "accel_x": random.uniform(-0.5, 0.5),
                "accel_y": random.uniform(-0.5, 0.5),
                "accel_z": random.uniform(-0.2, 0.2)
            },
            "quality": {
                "signal_strength": random.randint(90, 100),
                "accuracy": "high"
            }
        }
    
    elif sensor_type == "weather":
        return {
            "timestamp": timestamp,
            "sensor_id": "WTH-001",
            "sensor_type": "Weather",
            "data": {
                "temperature": 22.5 + random.uniform(-2, 2),
                "humidity": 65 + random.uniform(-5, 5),
                "pressure": 1013.25 + random.uniform(-5, 5),
                "wind_speed": 8 + random.uniform(-2, 2),
                "wind_direction": random.uniform(0, 360)
            },
            "quality": {
                "signal_strength": random.randint(85, 100),
                "accuracy": "medium"
            }
        }
    
    elif sensor_type == "engine":
        return {
            "timestamp": timestamp,
            "sensor_id": "ENG-001",
            "sensor_type": "Engine",
            "data": {
                "rpm": 1800 + random.randint(-50, 50),
                "power": 450 + random.randint(-20, 20),
                "temperature": 85 + random.randint(-5, 5),
                "oil_pressure": 4.5 + random.uniform(-0.3, 0.3)
            },
            "quality": {
                "signal_strength": random.randint(95, 100),
                "accuracy": "high"
            }
        }
    
    elif sensor_type == "fuel":
        return {
            "timestamp": timestamp,
            "sensor_id": "FUL-001",
            "sensor_type": "Fuel",
            "data": {
                "level": 75 + random.uniform(-2, 2),
                "flow_rate": 12.5 + random.uniform(-0.5, 0.5),
                "temperature": 35 + random.uniform(-2, 2),
                "pressure": 2.8 + random.uniform(-0.2, 0.2)
            },
            "quality": {
                "signal_strength": random.randint(90, 100),
                "accuracy": "high"
            }
        }
    
    elif sensor_type == "rudder":
        return {
            "timestamp": timestamp,
            "sensor_id": "RUD-001",
            "sensor_type": "Rudder",
            "data": {
                "angle": random.uniform(-35, 35),
                "hydraulic_pressure": 150 + random.uniform(-10, 10),
                "motor_current": 8.5 + random.uniform(-0.5, 0.5)
            },
            "quality": {
                "signal_strength": random.randint(95, 100),
                "accuracy": "high"
            }
        }
    
    else:
        logger.warning(f"未知传感器类型：{sensor_type}")
        return {"error": f"Unknown sensor type: {sensor_type}"}


# ============== 数字孪生控制技能 ==============

def twins_scene_control(
    action: str,
    params: Optional[Dict[str, Any]] = None,
    config: Optional[MarineEngineerConfig] = None
) -> Dict[str, Any]:
    """
    数字孪生场景控制技能
    
    :param action: 控制动作 (apply_preset/adjust_weather/adjust_physics/adjust_lighting/reset)
    :param params: 动作参数
    :param config: 配置对象
    :return: 控制结果
    """
    logger.info(f"场景控制请求：action={action}, params={params}")
    
    result = {
        "success": False,
        "action": action,
        "timestamp": datetime.now().isoformat(),
        "message": "",
        "data": {}
    }
    
    try:
        if action == "apply_preset":
            preset_name = params.get("preset", "calm") if params else "calm"
            if preset_name not in SCENE_PRESETS:
                result["message"] = f"未知预设：{preset_name}，可用预设：{list(SCENE_PRESETS.keys())}"
                return result
            
            preset = SCENE_PRESETS[preset_name]
            result["success"] = True
            result["message"] = f"已应用场景预设：{preset['name']}"
            result["data"] = preset
            logger.info(f"应用场景预设：{preset_name}")
        
        elif action == "adjust_weather":
            if not params:
                result["message"] = "缺少天气参数"
                return result
            
            result["success"] = True
            result["message"] = "天气参数已调整"
            result["data"] = {"weather": params}
            logger.info(f"调整天气参数：{params}")
        
        elif action == "adjust_physics":
            if not params:
                result["message"] = "缺少物理参数"
                return result
            
            result["success"] = True
            result["message"] = "物理参数已调整"
            result["data"] = {"physics": params}
            logger.info(f"调整物理参数：{params}")
        
        elif action == "adjust_lighting":
            if not params:
                result["message"] = "缺少灯光参数"
                return result
            
            result["success"] = True
            result["message"] = "灯光参数已调整"
            result["data"] = {"lighting": params}
            logger.info(f"调整灯光参数：{params}")
        
        elif action == "reset":
            result["success"] = True
            result["message"] = "场景已重置为默认状态"
            result["data"] = SCENE_PRESETS["calm"]
            logger.info("场景重置")
        
        else:
            result["message"] = f"未知控制动作：{action}"
            return result
    
    except Exception as e:
        logger.error(f"场景控制失败：{e}")
        result["message"] = f"控制失败：{str(e)}"
    
    return result


def twins_boat_control(
    boat_id: str,
    action: str,
    params: Optional[Dict[str, Any]] = None,
    config: Optional[MarineEngineerConfig] = None
) -> Dict[str, Any]:
    """
    船只控制技能
    
    :param boat_id: 船只 ID (boat1/boat2)
    :param action: 控制动作 (move/stop/rotate/set_speed/set_heading)
    :param params: 控制参数
    :param config: 配置对象
    :return: 控制结果
    """
    logger.info(f"船只控制请求：boat_id={boat_id}, action={action}, params={params}")
    
    result = {
        "success": False,
        "boat_id": boat_id,
        "action": action,
        "timestamp": datetime.now().isoformat(),
        "message": "",
        "data": {}
    }
    
    if boat_id not in ["boat1", "boat2"]:
        result["message"] = f"无效的船只 ID：{boat_id}，可用：boat1, boat2"
        return result
    
    try:
        if action == "move":
            result["success"] = True
            result["message"] = f"{boat_id} 开始移动"
            result["data"] = {"status": "moving", **params}
        
        elif action == "stop":
            result["success"] = True
            result["message"] = f"{boat_id} 已停止"
            result["data"] = {"status": "stopped"}
        
        elif action == "rotate":
            angle = params.get("angle", 0) if params else 0
            result["success"] = True
            result["message"] = f"{boat_id} 旋转 {angle}°"
            result["data"] = {"rotation": angle}
        
        elif action == "set_speed":
            speed = params.get("speed", 0) if params else 0
            result["success"] = True
            result["message"] = f"{boat_id} 速度设置为 {speed}"
            result["data"] = {"speed": speed}
        
        elif action == "set_heading":
            heading = params.get("heading", 0) if params else 0
            result["success"] = True
            result["message"] = f"{boat_id} 航向设置为 {heading}°"
            result["data"] = {"heading": heading}
        
        else:
            result["message"] = f"未知控制动作：{action}"
            return result
    
    except Exception as e:
        logger.error(f"船只控制失败：{e}")
        result["message"] = f"控制失败：{str(e)}"
    
    return result


def twins_sensor_query(
    sensor_type: str,
    count: int = 1,
    config: Optional[MarineEngineerConfig] = None
) -> Dict[str, Any]:
    """
    传感器数据查询技能
    
    :param sensor_type: 传感器类型 (all/gps/imu/weather/engine/fuel/rudder)
    :param count: 数据点数量
    :param config: 配置对象
    :return: 传感器数据
    """
    logger.info(f"传感器数据查询：sensor_type={sensor_type}, count={count}")
    
    result = {
        "success": False,
        "sensor_type": sensor_type,
        "count": count,
        "timestamp": datetime.now().isoformat(),
        "message": "",
        "data": []
    }
    
    try:
        if sensor_type == "all":
            sensor_types = ["gps", "imu", "weather", "engine", "fuel", "rudder"]
        else:
            sensor_types = [sensor_type]
        
        for _ in range(count):
            for st in sensor_types:
                data = generate_sensor_data(st)
                result["data"].append(data)
        
        result["success"] = True
        result["message"] = f"已获取 {len(result['data'])} 个传感器数据"
    
    except Exception as e:
        logger.error(f"传感器数据查询失败：{e}")
        result["message"] = f"查询失败：{str(e)}"
    
    return result


def twins_diagnosis(
    symptom: str,
    sensor_data: Optional[Dict[str, Any]] = None,
    config: Optional[MarineEngineerConfig] = None
) -> Dict[str, Any]:
    """
    数字孪生故障诊断技能
    
    :param symptom: 故障现象描述
    :param sensor_data: 传感器数据
    :param config: 配置对象
    :return: 诊断报告
    """
    logger.info(f"故障诊断请求：symptom={symptom}")
    
    result = {
        "success": False,
        "symptom": symptom,
        "timestamp": datetime.now().isoformat(),
        "message": "",
        "diagnosis": {
            "possible_causes": [],
            "confidence": 0,
            "recommendations": [],
            "severity": "unknown"
        }
    }
    
    try:
        # 简单规则诊断（实际应调用 fault_diagnosis_skill）
        symptom_lower = symptom.lower()
        
        if "转速" in symptom or "rpm" in symptom_lower:
            result["diagnosis"]["possible_causes"] = [
                "燃油供应不足",
                "进气系统阻塞",
                "调速器故障",
                "负载突变"
            ]
            result["diagnosis"]["confidence"] = 0.75
            result["diagnosis"]["recommendations"] = [
                "检查燃油油位和流量",
                "检查空气滤清器",
                "检查调速器设置",
                "监控负载变化"
            ]
            result["diagnosis"]["severity"] = "medium"
            result["success"] = True
            result["message"] = "诊断完成，发现 4 个可能原因"
        
        elif "温度" in symptom or "过热" in symptom:
            result["diagnosis"]["possible_causes"] = [
                "冷却系统故障",
                "散热器阻塞",
                "冷却液不足",
                "温度传感器故障"
            ]
            result["diagnosis"]["confidence"] = 0.80
            result["diagnosis"]["recommendations"] = [
                "检查冷却液液位",
                "检查散热器",
                "检查冷却水泵",
                "验证温度传感器读数"
            ]
            result["diagnosis"]["severity"] = "high"
            result["success"] = True
            result["message"] = "诊断完成，发现 4 个可能原因（高优先级）"
        
        elif "压力" in symptom:
            result["diagnosis"]["possible_causes"] = [
                "泵故障",
                "管路泄漏",
                "压力传感器故障",
                "阀门位置异常"
            ]
            result["diagnosis"]["confidence"] = 0.70
            result["diagnosis"]["recommendations"] = [
                "检查管路密封性",
                "检查泵运行状态",
                "验证压力传感器",
                "检查阀门位置"
            ]
            result["diagnosis"]["severity"] = "medium"
            result["success"] = True
            result["message"] = "诊断完成，发现 4 个可能原因"
        
        else:
            result["message"] = "无法识别故障现象，请提供更多细节"
            result["diagnosis"]["severity"] = "unknown"
    
    except Exception as e:
        logger.error(f"故障诊断失败：{e}")
        result["message"] = f"诊断失败：{str(e)}"
    
    return result


def twins_decision_support(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    config: Optional[MarineEngineerConfig] = None
) -> Dict[str, Any]:
    """
    智能决策支持技能
    
    :param query: 决策问题
    :param context: 上下文信息（海况、设备状态等）
    :param config: 配置对象
    :return: 决策建议
    """
    logger.info(f"决策支持请求：query={query}")
    
    result = {
        "success": False,
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "message": "",
        "decision": {
            "recommendation": "",
            "confidence": 0,
            "reasoning": [],
            "risks": [],
            "alternatives": []
        }
    }
    
    try:
        query_lower = query.lower()
        
        if "航行" in query or "适合" in query:
            result["decision"]["recommendation"] = "建议继续航行，保持当前航向和速度"
            result["decision"]["confidence"] = 0.75
            result["decision"]["reasoning"] = [
                "当前海况良好",
                "设备状态正常",
                "天气条件适宜"
            ]
            result["decision"]["risks"] = [
                "注意监控天气变化",
                "保持常规瞭望"
            ]
            result["decision"]["alternatives"] = [
                "减速航行以增加安全性",
                "改变航向避开潜在风险区域"
            ]
            result["success"] = True
            result["message"] = "决策分析完成"
        
        elif "停泊" in query or "锚泊" in query:
            result["decision"]["recommendation"] = "建议选择遮蔽良好的锚地，水深 15-25 米"
            result["decision"]["confidence"] = 0.80
            result["decision"]["reasoning"] = [
                "当前水域适合锚泊",
                "底质为泥沙，抓力良好"
            ]
            result["decision"]["risks"] = [
                "注意与其他船只保持安全距离",
                "监控锚位防止走锚"
            ]
            result["decision"]["alternatives"] = [
                "等待引航员引导至指定锚地",
                "使用双锚增加安全性"
            ]
            result["success"] = True
            result["message"] = "决策分析完成"
        
        else:
            result["message"] = "请提供更具体的决策问题"
    
    except Exception as e:
        logger.error(f"决策支持失败：{e}")
        result["message"] = f"分析失败：{str(e)}"
    
    return result


# ============== 技能注册表 ==============

TWINS_SKILLS = {
    "scene_control": twins_scene_control,
    "boat_control": twins_boat_control,
    "sensor_query": twins_sensor_query,
    "diagnosis": twins_diagnosis,
    "decision_support": twins_decision_support
}


def get_twins_skill(skill_name: str):
    """
    获取数字孪生技能函数
    
    :param skill_name: 技能名称
    :return: 技能函数
    """
    return TWINS_SKILLS.get(skill_name)


def list_twins_skills() -> List[str]:
    """
    列出所有可用的数字孪生技能
    
    :return: 技能名称列表
    """
    return list(TWINS_SKILLS.keys())
