# -*- coding: utf-8 -*-
"""PoseidonX Agent Team Framework — Tool Registry.

Provides a default catalog of ~36 tools across 8 categories and a registry
class for runtime tool management.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import ToolCategory, ToolDefinition


def get_default_tools() -> List[ToolDefinition]:
    """Return the default catalog of tool definitions."""

    TC = ToolCategory
    TD = ToolDefinition
    return [
        # Browser (6)
        TD(name="web_search", description="Search the web for information", category=TC.BROWSER,
           parameters={"query": {"type": "string", "required": True, "description": "搜索关键词"}, "max_results": {"type": "integer", "required": False, "default": 10, "description": "最大结果数"}, "language": {"type": "string", "required": False, "default": "zh", "description": "语言"}}),
        TD(name="navigate_url", description="Navigate to a specific URL", category=TC.BROWSER,
           parameters={"url": {"type": "string", "required": True, "description": "目标URL"}, "wait_for": {"type": "string", "required": False, "default": "load", "description": "等待事件"}}),
        TD(name="screenshot", description="Take a screenshot of current page", category=TC.BROWSER,
           parameters={"selector": {"type": "string", "required": False, "default": "", "description": "CSS选择器"}, "full_page": {"type": "boolean", "required": False, "default": False, "description": "是否全页截图"}}),
        TD(name="click_element", description="Click an element on the page", category=TC.BROWSER,
           parameters={"selector": {"type": "string", "required": True, "description": "CSS选择器"}, "wait_after": {"type": "integer", "required": False, "default": 500, "description": "点击后等待ms"}}),
        TD(name="fill_form", description="Fill in a form field", category=TC.BROWSER,
           parameters={"selector": {"type": "string", "required": True, "description": "输入框选择器"}, "value": {"type": "string", "required": True, "description": "填入值"}}),
        TD(name="extract_content", description="Extract text content from page", category=TC.BROWSER,
           parameters={"selector": {"type": "string", "required": False, "default": "body", "description": "CSS选择器"}, "format": {"type": "string", "required": False, "default": "text", "description": "输出格式: text/html/markdown"}}),
        # Code Execution (3)
        TD(name="run_python", description="Execute Python code in sandbox", category=TC.CODE_EXECUTION,
           parameters={"code": {"type": "string", "required": True, "description": "Python代码"}, "timeout": {"type": "integer", "required": False, "default": 30, "description": "超时秒数"}}),
        TD(name="run_shell", description="Execute shell commands", category=TC.CODE_EXECUTION, requires_approval=True,
           parameters={"command": {"type": "string", "required": True, "description": "Shell命令"}, "cwd": {"type": "string", "required": False, "default": "", "description": "工作目录"}, "timeout": {"type": "integer", "required": False, "default": 30, "description": "超时秒数"}}),
        TD(name="run_javascript", description="Execute JavaScript code", category=TC.CODE_EXECUTION,
           parameters={"code": {"type": "string", "required": True, "description": "JavaScript代码"}, "context": {"type": "string", "required": False, "default": "browser", "description": "执行环境: browser/node"}}),
        # Communication (4)
        TD(name="send_message", description="Send a message to another agent", category=TC.COMMUNICATION,
           parameters={"target_agent_id": {"type": "string", "required": True, "description": "目标Agent ID"}, "content": {"type": "string", "required": True, "description": "消息内容"}, "priority": {"type": "integer", "required": False, "default": 0, "description": "优先级 0-10"}}),
        TD(name="broadcast", description="Broadcast message to all agents", category=TC.COMMUNICATION,
           parameters={"content": {"type": "string", "required": True, "description": "广播内容"}, "channel": {"type": "string", "required": False, "default": "default", "description": "频道名"}}),
        TD(name="subscribe_channel", description="Subscribe to a message channel", category=TC.COMMUNICATION,
           parameters={"channel_name": {"type": "string", "required": True, "description": "频道名称"}, "filter_pattern": {"type": "string", "required": False, "default": "", "description": "过滤模式"}}),
        TD(name="publish_event", description="Publish an event to the message bus", category=TC.COMMUNICATION,
           parameters={"event_type": {"type": "string", "required": True, "description": "事件类型"}, "payload": {"type": "object", "required": False, "default": {}, "description": "事件数据"}}),
        # File Operation (4)
        TD(name="read_file", description="Read contents of a file", category=TC.FILE_OPERATION,
           parameters={"path": {"type": "string", "required": True, "description": "文件路径"}, "encoding": {"type": "string", "required": False, "default": "utf-8", "description": "字符编码"}}),
        TD(name="write_file", description="Write contents to a file", category=TC.FILE_OPERATION, requires_approval=True,
           parameters={"path": {"type": "string", "required": True, "description": "文件路径"}, "content": {"type": "string", "required": True, "description": "文件内容"}, "mode": {"type": "string", "required": False, "default": "w", "description": "写入模式: w/a"}}),
        TD(name="list_directory", description="List files in a directory", category=TC.FILE_OPERATION,
           parameters={"path": {"type": "string", "required": True, "description": "目录路径"}, "recursive": {"type": "boolean", "required": False, "default": False, "description": "是否递归"}, "pattern": {"type": "string", "required": False, "default": "*", "description": "匹配模式"}}),
        TD(name="search_files", description="Search for files by pattern", category=TC.FILE_OPERATION,
           parameters={"pattern": {"type": "string", "required": True, "description": "搜索模式"}, "directory": {"type": "string", "required": False, "default": ".", "description": "搜索目录"}, "max_depth": {"type": "integer", "required": False, "default": 5, "description": "最大深度"}}),
        # Triggers (4)
        TD(name="schedule_task", description="Schedule a task for later execution", category=TC.TRIGGERS,
           parameters={"task_id": {"type": "string", "required": True, "description": "任务ID"}, "cron_expr": {"type": "string", "required": False, "default": "", "description": "Cron表达式"}, "delay_seconds": {"type": "integer", "required": False, "default": 0, "description": "延迟秒数"}}),
        TD(name="set_alarm", description="Set an alarm/reminder", category=TC.TRIGGERS,
           parameters={"name": {"type": "string", "required": True, "description": "闹钟名称"}, "trigger_at": {"type": "string", "required": True, "description": "触发时间 ISO8601"}, "callback": {"type": "string", "required": False, "default": "", "description": "回调函数名"}}),
        TD(name="watch_file", description="Watch a file for changes", category=TC.TRIGGERS,
           parameters={"path": {"type": "string", "required": True, "description": "监听文件路径"}, "events": {"type": "array", "required": False, "default": ["modify"], "description": "监听事件类型"}}),
        TD(name="cron_trigger", description="Set up a cron-based trigger", category=TC.TRIGGERS,
           parameters={"expression": {"type": "string", "required": True, "description": "Cron表达式"}, "task_name": {"type": "string", "required": True, "description": "任务名称"}, "enabled": {"type": "boolean", "required": False, "default": True, "description": "是否启用"}}),
        # Discovery (2)
        TD(name="list_agents", description="List all available agents", category=TC.DISCOVERY,
           parameters={"team_id": {"type": "string", "required": False, "default": "", "description": "团队ID过滤"}, "state_filter": {"type": "string", "required": False, "default": "", "description": "状态过滤"}}),
        TD(name="list_capabilities", description="List capabilities of an agent", category=TC.DISCOVERY,
           parameters={"agent_id": {"type": "string", "required": True, "description": "Agent ID"}}),
        # Digital Twin (8)
        TD(name="dt_camera_move", description="Move digital twin camera to specified position or preset view", category=TC.DIGITAL_TWIN,
           parameters={"position": {"type": "object", "required": False, "description": "相机位置 {x,y,z}"}, "target": {"type": "object", "required": False, "default": {"x": 0, "y": 0, "z": 0}, "description": "注视目标 {x,y,z}"}, "duration": {"type": "number", "required": False, "default": 1.0, "description": "过渡时间秒"}, "view_preset": {"type": "string", "required": False, "default": "", "description": "预设视角: top/front/side/back/iso"}}),
        TD(name="dt_model_load", description="Load a 3D model into scene", category=TC.DIGITAL_TWIN,
           parameters={"model_url": {"type": "string", "required": True, "description": "模型文件URL"}, "format": {"type": "string", "required": False, "default": "glb", "description": "格式: glb/gltf/obj/fbx"}, "position": {"type": "object", "required": False, "default": {"x": 0, "y": 0, "z": 0}, "description": "初始位置"}}),
        TD(name="dt_model_transform", description="Transform model position/rotation/scale", category=TC.DIGITAL_TWIN,
           parameters={"model_id": {"type": "string", "required": True, "description": "模型ID"}, "position": {"type": "object", "required": False, "description": "位置 {x,y,z}"}, "rotation": {"type": "object", "required": False, "description": "旋转 {x,y,z} 弧度"}, "scale": {"type": "object", "required": False, "description": "缩放 {x,y,z}"}}),
        TD(name="dt_material_set", description="Set material properties on model", category=TC.DIGITAL_TWIN,
           parameters={"model_id": {"type": "string", "required": True, "description": "模型ID"}, "material_name": {"type": "string", "required": False, "default": "", "description": "材质名称"}, "color": {"type": "string", "required": False, "default": "#ffffff", "description": "颜色HEX"}, "metalness": {"type": "number", "required": False, "default": 0.5, "description": "金属度 0-1"}, "roughness": {"type": "number", "required": False, "default": 0.5, "description": "粗糙度 0-1"}}),
        TD(name="dt_physics_toggle", description="Toggle physics simulation", category=TC.DIGITAL_TWIN,
           parameters={"enabled": {"type": "boolean", "required": True, "description": "是否启用物理"}, "gravity": {"type": "number", "required": False, "default": -9.81, "description": "重力加速度"}}),
        TD(name="dt_light_adjust", description="Adjust scene lighting", category=TC.DIGITAL_TWIN,
           parameters={"light_type": {"type": "string", "required": False, "default": "directional", "description": "灯光类型: directional/point/spot/ambient"}, "intensity": {"type": "number", "required": False, "default": 1.0, "description": "强度 0-10"}, "color": {"type": "string", "required": False, "default": "#ffffff", "description": "颜色HEX"}, "position": {"type": "object", "required": False, "description": "位置 {x,y,z}"}}),
        TD(name="dt_render_mode", description="Switch rendering mode", category=TC.DIGITAL_TWIN,
           parameters={"mode": {"type": "string", "required": True, "description": "渲染模式: solid/wireframe/xray/heatmap"}}),
        TD(name="dt_inspection_path", description="Create inspection path for camera fly-through", category=TC.DIGITAL_TWIN,
           parameters={"waypoints": {"type": "array", "required": True, "description": "路径点列表 [{x,y,z},...]"}, "speed": {"type": "number", "required": False, "default": 1.0, "description": "飞行速度"}, "loop": {"type": "boolean", "required": False, "default": False, "description": "是否循环"}}),
        # Maritime (6)
        TD(name="ais_query", description="Query AIS vessel tracking data", category=TC.MARITIME,
           parameters={"mmsi": {"type": "string", "required": False, "default": "", "description": "MMSI号码"}, "area": {"type": "object", "required": False, "description": "区域 {lat_min,lat_max,lon_min,lon_max}"}, "vessel_type": {"type": "string", "required": False, "default": "", "description": "船舶类型"}}),
        TD(name="weather_fetch", description="Fetch marine weather data", category=TC.MARITIME,
           parameters={"lat": {"type": "number", "required": True, "description": "纬度"}, "lon": {"type": "number", "required": True, "description": "经度"}, "hours": {"type": "integer", "required": False, "default": 24, "description": "预报时长"}}),
        TD(name="route_calculate", description="Calculate maritime route", category=TC.MARITIME,
           parameters={"origin": {"type": "object", "required": True, "description": "起点 {lat,lon}"}, "destination": {"type": "object", "required": True, "description": "终点 {lat,lon}"}, "avoid_areas": {"type": "array", "required": False, "default": [], "description": "避开区域列表"}}),
        TD(name="colregs_check", description="Check COLREGs compliance", category=TC.MARITIME,
           parameters={"own_vessel": {"type": "object", "required": True, "description": "本船信息 {position,course,speed}"}, "target_vessel": {"type": "object", "required": True, "description": "目标船信息"}, "rule": {"type": "string", "required": False, "default": "", "description": "特定规则编号"}}),
        TD(name="engine_status", description="Get engine diagnostic status", category=TC.MARITIME,
           parameters={"engine_id": {"type": "string", "required": False, "default": "main", "description": "发动机ID"}, "include_history": {"type": "boolean", "required": False, "default": False, "description": "是否含历史数据"}}),
        TD(name="cargo_status", description="Get cargo hold status", category=TC.MARITIME,
           parameters={"hold_id": {"type": "string", "required": False, "default": "all", "description": "货舱ID"}, "include_stability": {"type": "boolean", "required": False, "default": True, "description": "是否含稳性数据"}}),
        # Maritime subcategory tools
        TD(name="chart_ecdis_query", description="Query ECDIS electronic chart data", category=TC.CHART_TOOLS,
           parameters={"area": {"type": "object", "required": True, "description": "区域 {lat_min,lat_max,lon_min,lon_max}"}, "chart_type": {"type": "string", "required": False, "default": "ENC", "description": "海图类型: ENC/RNC"}}),
        TD(name="ais_vessel_track", description="Track vessel via AIS transponder", category=TC.AIS_TOOLS,
           parameters={"mmsi": {"type": "string", "required": True, "description": "MMSI号码"}, "duration_hours": {"type": "number", "required": False, "default": 6, "description": "追踪时长"}}),
        TD(name="weather_marine_forecast", description="Marine weather & sea state forecast", category=TC.WEATHER_TOOLS,
           parameters={"lat": {"type": "number", "required": True, "description": "纬度"}, "lon": {"type": "number", "required": True, "description": "经度"}, "forecast_hours": {"type": "integer", "required": False, "default": 48, "description": "预报时长"}}),
        TD(name="engine_diagnostic_scan", description="Full engine diagnostic scan", category=TC.ENGINE_TOOLS,
           parameters={"engine_id": {"type": "string", "required": False, "default": "main", "description": "发动机ID"}, "deep_scan": {"type": "boolean", "required": False, "default": False, "description": "深度扫描"}}),
        # ── Hermes-style tools (Web, Vision, Memory, Skills, Delegation) ──
        TD(name="web_extract", description="Extract structured content from a URL (Hermes web_extract)", category=TC.WEB, icon="🌐",
           parameters={"url": {"type": "string", "required": True, "description": "URL to extract from"}, "format": {"type": "string", "required": False, "default": "markdown", "description": "输出格式: text/markdown/json"}}),
        TD(name="vision_analyze", description="Analyze an image — charts, diagrams, technical drawings (Hermes vision_analyze)", category=TC.VISION, icon="👁",
           parameters={"image_path": {"type": "string", "required": True, "description": "图片路径或URL"}, "question": {"type": "string", "required": False, "default": "", "description": "分析问题"}}),
        TD(name="memory_save", description="Save a durable fact to persistent memory (Hermes memory)", category=TC.MEMORY, icon="🧠",
           parameters={"key": {"type": "string", "required": True, "description": "记忆键名"}, "content": {"type": "string", "required": True, "description": "记忆内容"}, "category": {"type": "string", "required": False, "default": "research", "description": "分类: research/regulation/formula/convention"}}),
        TD(name="memory_read", description="Read from persistent memory (Hermes memory)", category=TC.MEMORY, icon="🧠",
           parameters={"key": {"type": "string", "required": False, "default": "", "description": "记忆键名 (空=列出全部)"}, "category": {"type": "string", "required": False, "default": "", "description": "分类过滤"}}),
        TD(name="session_search", description="Search past conversation sessions for relevant context (Hermes session_search)", category=TC.MEMORY, icon="🔍",
           parameters={"query": {"type": "string", "required": True, "description": "搜索查询"}, "max_results": {"type": "integer", "required": False, "default": 5, "description": "最大结果数"}}),
        TD(name="skill_list", description="List available skills (Hermes skills_list)", category=TC.SKILLS, icon="📚",
           parameters={"category": {"type": "string", "required": False, "default": "", "description": "分类过滤"}}),
        TD(name="skill_view", description="View a skill's instructions (Hermes skill_view)", category=TC.SKILLS, icon="📖",
           parameters={"name": {"type": "string", "required": True, "description": "技能名称"}}),
        TD(name="skill_manage", description="Create/patch/delete skills (Hermes skill_manage)", category=TC.SKILLS, icon="✏️",
           parameters={"action": {"type": "string", "required": True, "description": "操作: create/patch/delete"}, "name": {"type": "string", "required": True, "description": "技能名称"}, "content": {"type": "string", "required": False, "default": "", "description": "技能内容 (create/patch 时需要)"}}),
        TD(name="delegate_task", description="Spawn a subagent for parallel research (Hermes delegate_task)", category=TC.DELEGATION, icon="🤖",
           parameters={"task_description": {"type": "string", "required": True, "description": "任务描述"}, "target_agent": {"type": "string", "required": False, "default": "", "description": "目标Agent (空=自动选择)"}, "timeout": {"type": "integer", "required": False, "default": 300, "description": "超时秒数"}}),
        TD(name="mixture_of_agents", description="Multi-agent reasoning — consult multiple models (Hermes MoA)", category=TC.DELEGATION, icon="🧪",
           parameters={"question": {"type": "string", "required": True, "description": "需要多角度分析的问题"}, "agent_count": {"type": "integer", "required": False, "default": 3, "description": "参与Agent数"}}),
        TD(name="engine_monitor", description="Real-time engine monitoring (Hermes maritime)", category=TC.MARITIME, icon="⚙️",
           parameters={"engine_id": {"type": "string", "required": False, "default": "all", "description": "发动机ID"}, "metrics": {"type": "array", "required": False, "default": ["rpm", "temp", "fuel_rate"], "description": "监控指标"}}),
        TD(name="chart_lookup", description="Lookup nautical chart information", category=TC.MARITIME, icon="🗺",
           parameters={"area": {"type": "object", "required": True, "description": "区域 {lat,lon,radius_nm}"}, "chart_type": {"type": "string", "required": False, "default": "ENC", "description": "海图类型"}}),
    ]

class ToolRegistry:
    """Runtime registry for managing tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolDefinition] = {}

    def load_defaults(self) -> None:
        """Load all default tools into the registry."""
        for tool in get_default_tools():
            self._tools[tool.tool_id] = tool

    def register(self, tool: ToolDefinition) -> None:
        """Register a single tool."""
        self._tools[tool.tool_id] = tool

    def get(self, tool_id: str) -> Optional[ToolDefinition]:
        """Get a tool by ID."""
        return self._tools.get(tool_id)

    def list_all(self) -> List[ToolDefinition]:
        """Return all registered tools."""
        return list(self._tools.values())

    def list_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """Return tools filtered by category."""
        return [t for t in self._tools.values() if t.category == category]

    def list_enabled(self) -> List[ToolDefinition]:
        """Return only enabled tools."""
        return [t for t in self._tools.values() if t.enabled]

    def enable(self, tool_id: str) -> bool:
        """Enable a tool. Returns True if found."""
        tool = self._tools.get(tool_id)
        if tool is not None:
            tool.enabled = True
            return True
        return False

    def disable(self, tool_id: str) -> bool:
        """Disable a tool. Returns True if found."""
        tool = self._tools.get(tool_id)
        if tool is not None:
            tool.enabled = False
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize registry to dict."""
        return {tid: t.to_dict() for tid, t in self._tools.items()}
