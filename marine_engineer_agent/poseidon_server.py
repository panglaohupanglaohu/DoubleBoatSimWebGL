#!/usr/bin/env python3
"""
Poseidon Service - 智能船舶工程服务 API (轻量版)

基于 Python 内置 http.server 模块，无需外部依赖。
支持故障诊断、知识查询等功能。

:author: marine_engineer_agent
:version: 1.0.0
:since: 2026-03-10
"""

import sys
import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# 添加 skills 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills'))

# 导入技能模块
try:
    from fault_diagnosis import fault_diagnosis_skill
    from query_answer import query_answer_skill
    from marine_config import MarineEngineerConfig
    from twins_controller import (
        twins_scene_control,
        twins_boat_control,
        twins_sensor_query,
        twins_diagnosis,
        twins_decision_support,
        list_twins_skills
    )
    from hydrodynamics import (
        hydrodynamics_analysis,
        calculate_hull_coefficients,
        calculate_total_resistance,
        calculate_required_power,
        calculate_initial_gm,
        list_hydro_skills
    )
    SKILLS_AVAILABLE = True
    TWINS_AVAILABLE = True
    HYDRO_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  技能模块导入失败：{e}")
    SKILLS_AVAILABLE = False
    TWINS_AVAILABLE = False
    HYDRO_AVAILABLE = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("poseidon_server")


class PoseidonHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    def _set_headers(self, status_code=200, content_type="application/json"):
        """设置响应头"""
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def _send_json(self, data, status_code=200):
        """发送 JSON 响应"""
        self._set_headers(status_code)
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode("utf-8"))
    
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self._set_headers(204)
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/":
            self._send_json({
                "success": True,
                "data": {
                    "name": "Poseidon Service",
                    "version": "1.0.0",
                    "description": "智能船舶工程服务 API"
                },
                "timestamp": datetime.now().isoformat(),
                "message": "欢迎使用 Poseidon 服务"
            })
        
        elif path == "/health":
            self._send_json({
                "status": "healthy",
                "service": "poseidon",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "skills": ["fault_diagnosis", "query_answer"] if SKILLS_AVAILABLE else [],
                "skills_available": SKILLS_AVAILABLE
            })
        
        elif path == "/api/v1/config":
            if SKILLS_AVAILABLE:
                config = MarineEngineerConfig()
                self._send_json({
                    "success": True,
                    "data": config.to_dict(),
                    "timestamp": datetime.now().isoformat()
                })
            else:
                self._send_json({"error": "Skills not available"}, 503)
        
        elif path == "/api/v1/skills":
            skills_list = [
                {
                    "name": "fault_diagnosis",
                    "endpoint": "/api/v1/fault_diagnosis",
                    "method": "POST"
                },
                {
                    "name": "query_answer",
                    "endpoint": "/api/v1/query_answer",
                    "method": "POST"
                }
            ]
            if TWINS_AVAILABLE:
                skills_list.extend([
                    {
                        "name": "twins_scene_control",
                        "endpoint": "/api/v1/twins/scene/control",
                        "method": "POST"
                    },
                    {
                        "name": "twins_boat_control",
                        "endpoint": "/api/v1/twins/boat/control",
                        "method": "POST"
                    },
                    {
                        "name": "twins_sensor_query",
                        "endpoint": "/api/v1/twins/sensor/query",
                        "method": "POST"
                    },
                    {
                        "name": "twins_diagnosis",
                        "endpoint": "/api/v1/twins/diagnosis",
                        "method": "POST"
                    },
                    {
                        "name": "twins_decision_support",
                        "endpoint": "/api/v1/twins/decision",
                        "method": "POST"
                    }
                ])
            self._send_json({
                "success": True,
                "data": {
                    "available": SKILLS_AVAILABLE,
                    "twins_available": TWINS_AVAILABLE,
                    "skills": skills_list
                },
                "timestamp": datetime.now().isoformat()
            })
        
        elif path == "/api/v1/twins/skills":
            if TWINS_AVAILABLE:
                self._send_json({
                    "success": True,
                    "data": {
                        "available": TWINS_AVAILABLE,
                        "skills": list_twins_skills()
                    },
                    "timestamp": datetime.now().isoformat()
                })
            else:
                self._send_json({"error": "Twins skills not available"}, 503)
        
        else:
            self._send_json({"error": "Not Found", "path": path}, 404)
    
    def do_POST(self):
        """处理 POST 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # 读取请求体
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
            return
        
        if path == "/api/v1/fault_diagnosis":
            if not SKILLS_AVAILABLE:
                self._send_json({"error": "Skills not available"}, 503)
                return
            
            user_input = data.get("user_input", "")
            relevant_docs = data.get("relevant_docs", [])
            config = data.get("config", None)
            
            if not user_input:
                self._send_json({"error": "user_input is required"}, 400)
                return
            
            try:
                logger.info(f"故障诊断请求：{user_input}")
                result = fault_diagnosis_skill(
                    user_input=user_input,
                    relevant_docs=relevant_docs,
                    config=config
                )
                self._send_json({
                    "success": True,
                    "data": {"diagnosis": result},
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"故障诊断失败：{e}")
                self._send_json({"error": str(e)}, 500)
        
        elif path == "/api/v1/query_answer":
            if not SKILLS_AVAILABLE:
                self._send_json({"error": "Skills not available"}, 503)
                return
            
            question = data.get("question", "")
            context = data.get("context", "")
            config = data.get("config", None)
            
            if not question:
                self._send_json({"error": "question is required"}, 400)
                return
            
            try:
                logger.info(f"知识查询请求：{question}")
                result = query_answer_skill(
                    question=question,
                    context=context,
                    config=config
                )
                self._send_json({
                    "success": True,
                    "data": {"answer": result},
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"知识查询失败：{e}")
                self._send_json({"error": str(e)}, 500)
        
        # ===== 数字孪生 API 端点 =====
        
        elif path == "/api/v1/twins/scene/control":
            if not TWINS_AVAILABLE:
                self._send_json({"error": "Twins skills not available"}, 503)
                return
            
            action = data.get("action", "")
            params = data.get("params", {})
            config = data.get("config", None)
            
            if not action:
                self._send_json({"error": "action is required"}, 400)
                return
            
            try:
                logger.info(f"场景控制请求：{action}")
                result = twins_scene_control(
                    action=action,
                    params=params,
                    config=config
                )
                self._send_json(result)
            except Exception as e:
                logger.error(f"场景控制失败：{e}")
                self._send_json({"error": str(e)}, 500)
        
        elif path == "/api/v1/twins/boat/control":
            if not TWINS_AVAILABLE:
                self._send_json({"error": "Twins skills not available"}, 503)
                return
            
            boat_id = data.get("boat_id", "")
            action = data.get("action", "")
            params = data.get("params", {})
            
            if not boat_id or not action:
                self._send_json({"error": "boat_id and action are required"}, 400)
                return
            
            try:
                logger.info(f"船只控制请求：boat={boat_id}, action={action}")
                result = twins_boat_control(
                    boat_id=boat_id,
                    action=action,
                    params=params
                )
                self._send_json(result)
            except Exception as e:
                logger.error(f"船只控制失败：{e}")
                self._send_json({"error": str(e)}, 500)
        
        elif path == "/api/v1/twins/sensor/query":
            if not TWINS_AVAILABLE:
                self._send_json({"error": "Twins skills not available"}, 503)
                return
            
            sensor_type = data.get("sensor_type", "all")
            count = data.get("count", 1)
            
            try:
                logger.info(f"传感器查询：{sensor_type}, count={count}")
                result = twins_sensor_query(
                    sensor_type=sensor_type,
                    count=count
                )
                self._send_json(result)
            except Exception as e:
                logger.error(f"传感器查询失败：{e}")
                self._send_json({"error": str(e)}, 500)
        
        elif path == "/api/v1/twins/diagnosis":
            if not TWINS_AVAILABLE:
                self._send_json({"error": "Twins skills not available"}, 503)
                return
            
            symptom = data.get("symptom", "")
            sensor_data = data.get("sensor_data", {})
            
            if not symptom:
                self._send_json({"error": "symptom is required"}, 400)
                return
            
            try:
                logger.info(f"故障诊断请求：{symptom}")
                result = twins_diagnosis(
                    symptom=symptom,
                    sensor_data=sensor_data
                )
                self._send_json(result)
            except Exception as e:
                logger.error(f"故障诊断失败：{e}")
                self._send_json({"error": str(e)}, 500)
        
        elif path == "/api/v1/twins/decision":
            if not TWINS_AVAILABLE:
                self._send_json({"error": "Twins skills not available"}, 503)
                return
            
            query = data.get("query", "")
            context = data.get("context", {})
            
            if not query:
                self._send_json({"error": "query is required"}, 400)
                return
            
            try:
                logger.info(f"决策支持请求：{query}")
                result = twins_decision_support(
                    query=query,
                    context=context
                )
                self._send_json(result)
            except Exception as e:
                logger.error(f"决策支持失败：{e}")
                self._send_json({"error": str(e)}, 500)
        
        # ===== 水动力学 API 端点 =====
        
        elif path == "/api/v1/hydro/analysis":
            if not HYDRO_AVAILABLE:
                self._send_json({"error": "Hydrodynamics skills not available"}, 503)
                return
            
            length = data.get("length", 0)
            beam = data.get("beam", 0)
            draft = data.get("draft", 0)
            displacement = data.get("displacement", 0)
            speed = data.get("speed", 0)
            kg = data.get("kg", None)
            
            if not all([length, beam, draft, displacement, speed]):
                self._send_json({"error": "Missing required parameters"}, 400)
                return
            
            try:
                logger.info(f"水动力分析请求：L={length}m, B={beam}m, T={draft}m, V={speed}kn")
                result = hydrodynamics_analysis(
                    length=length,
                    beam=beam,
                    draft=draft,
                    displacement=displacement,
                    speed=speed,
                    kg=kg
                )
                self._send_json(result)
            except Exception as e:
                logger.error(f"水动力分析失败：{e}")
                self._send_json({"error": str(e)}, 500)
        
        else:
            self._send_json({"error": "Not Found", "path": path}, 404)
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        logger.info(f"{self.address_string()} - {format % args}")


def run_server(host="127.0.0.1", port=8080):
    """启动服务器"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, PoseidonHandler)
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║           🌊 Poseidon Service 已启动                     ║
╠══════════════════════════════════════════════════════════╣
║  地址：http://{host}:{port}
║  文档：http://{host}:{port}/api/v1/skills
║  健康：http://{host}:{port}/health
║  技能：{ '✅ 已加载' if SKILLS_AVAILABLE else '⚠️  未加载' }
║  数字孪生：{ '✅ 已启用' if TWINS_AVAILABLE else '⚠️  未启用' }
║  水动力学：{ '✅ 已启用' if HYDRO_AVAILABLE else '⚠️  未启用' }
╚══════════════════════════════════════════════════════════╝
    """)
    
    logger.info(f"Poseidon 服务运行在 http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    HOST = os.getenv("POSEIDON_HOST", "127.0.0.1")
    PORT = int(os.getenv("POSEIDON_PORT", "8080"))
    
    try:
        run_server(HOST, PORT)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 服务启动失败：{e}")
        sys.exit(1)
