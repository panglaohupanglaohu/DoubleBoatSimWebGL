#!/usr/bin/env python3
"""
Poseidon Server 启动脚本 - AI Native 数字孪生服务

功能:
- REST API (HTTP 8080)
- WebSocket 实时推送 (8765)
- Channel 数据管理
- 报警引擎
- 数据可视化

启动命令:
    python3 start_poseidon_server.py

访问:
- API: http://localhost:8080/api
- WebSocket: ws://localhost:8765
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_dir = Path(__file__).parent
skills_dir = project_dir / 'skills'
sys.path.insert(0, str(skills_dir))

print("🐱⛵ Poseidon Server 启动中...")
print(f"工作目录：{project_dir}")

# 检查必要文件
required_files = [
    'skills/channels_integration.py',
    'skills/realtime_data_bridge.py',
    'skills/alarm_engine.py',
    'skills/visualization_api.py',
    'skills/marine_channels_integration.py',
]

for file in required_files:
    if not (project_dir / file).exists():
        print(f"❌ 缺少文件：{file}")
        sys.exit(1)
    print(f"✅ {file}")

print("\n导入模块中...")

try:
    # 使用绝对导入
    from channels_integration import ChannelsIntegration, ChannelData, Event, DataType
    from realtime_data_bridge import RealtimeDataBridge
    from alarm_engine import AlarmEngine, AlarmLevel, AlarmRule
    from visualization_api import VisualizationAPI
    from marine_channels_integration import MarineChannelsIntegration
    print("✅ 所有模块导入成功")
except ImportError as e:
    print(f"❌ 模块导入失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n初始化服务...")

# 初始化组件
channels = ChannelsIntegration()
alarm = AlarmEngine(channels)
viz = VisualizationAPI(channels, alarm)
marine_integration = MarineChannelsIntegration(channels, alarm)
bridge = RealtimeDataBridge(channels, port=8765)

print("✅ 服务初始化完成")

# 设置报警规则
print("\n设置报警规则...")
marine_integration.setup_alarm_rules()
print("✅ 报警规则已设置")

# 启动 WebSocket 服务器
print("\n🚀 启动 WebSocket 服务器 (ws://localhost:8765)...")
bridge.start()

print("\n🚀 启动 HTTP 服务器 (http://localhost:8080)...")
print("\n" + "="*60)
print("🐱⛵ Poseidon Server 已启动!")
print("="*60)
print("\nAPI 端点:")
print("  GET  http://localhost:8080/api/health          - 健康检查")
print("  GET  http://localhost:8080/api/channels        - 获取所有 Channel")
print("  GET  http://localhost:8080/api/data/{channel}  - 获取 Channel 数据")
print("  POST http://localhost:8080/api/data/{channel}  - 更新 Channel 数据")
print("  GET  http://localhost:8080/api/viz/stats       - 统计数据")
print("  GET  http://localhost:8080/api/viz/alarms      - 活动报警")
print("  GET  http://localhost:8080/api/events          - 事件列表")
print("\nWebSocket:")
print("  ws://localhost:8765")
print("\n按 Ctrl+C 停止服务")
print("="*60 + "\n")

# 启动 HTTP 服务器
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs

class PoseidonHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers(200)
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        if path == '/api/health':
            self._set_headers()
            self.wfile.write(json.dumps({"status": "ok", "message": "Poseidon Server is running"}).encode())
        
        elif path == '/api/channels':
            self._set_headers()
            channel_list = list(channels.channels.keys())
            self.wfile.write(json.dumps({"channels": channel_list}).encode())
        
        elif path.startswith('/api/data/'):
            channel_name = path.split('/api/data/')[-1]
            data = channels.get_channel_data(channel_name)
            self._set_headers()
            self.wfile.write(json.dumps({"channel": channel_name, "data": data}).encode())
        
        elif path == '/api/viz/stats':
            self._set_headers()
            stats = viz.get_aggregated_stats('engine_monitor', '1h')
            self.wfile.write(json.dumps(stats).encode())
        
        elif path == '/api/viz/alarms':
            self._set_headers()
            active_alarms = alarm.get_active_alarms()
            self.wfile.write(json.dumps({"alarms": active_alarms}).encode())
        
        elif path == '/api/events':
            self._set_headers()
            events = channels.get_events(limit=50)
            self.wfile.write(json.dumps({"events": events}).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path.startswith('/api/data/'):
            channel_name = path.split('/api/data/')[-1]
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body)
                channels.update_channel_data(channel_name, data)
                self._set_headers()
                self.wfile.write(json.dumps({"status": "ok", "message": f"Updated {channel_name}"}).encode())
            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def log_message(self, format, *args):
        print(f"[HTTP] {args[0]}")

server = HTTPServer(('localhost', 8080), PoseidonHandler)
server.serve_forever()
