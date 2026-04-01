import os
BASE = '/Users/pangloahu/Downloads/DoubleBoatClawSystem'

# Step 2: tool_registry.py - add icons/is_default to existing tools
p = os.path.join(BASE, 'src/backend/agents/tool_registry.py')
with open(p) as f:
    c = f.read()

c = c.replace('~36 tools across 8 categories', '~52 tools across 12 categories (Clawith-aligned)')

pairs = [
    ('TD(name="web_search",', 'TD(name="web_search", icon="\u1f50d", is_default=True,'),
    ('TD(name="navigate_url",', 'TD(name="navigate_url", icon="\u1f310", is_default=True,'),
    ('TD(name="screenshot",', 'TD(name="screenshot", icon="\u1f4f8", is_default=True,'),
    ('TD(name="click_element",', 'TD(name="click_element", icon="\u1f446", is_default=True,'),
    ('TD(name="fill_form",', 'TD(name="fill_form", icon="\u1f4dd", is_default=True,'),
    ('TD(name="extract_content",', 'TD(name="extract_content", icon="\u1f4c4", is_default=True,'),
    ('TD(name="run_python",', 'TD(name="run_python", icon="\u1f40d", is_default=True,'),
    ('TD(name="run_shell",', 'TD(name="run_shell", icon="\u1f5a5", is_default=True,'),
    ('TD(name="run_javascript",', 'TD(name="run_javascript", icon="\u1f4dc", is_default=True,'),
    ('TD(name="send_message",', 'TD(name="send_message", icon="\u1f4ac", is_default=True,'),
    ('TD(name="broadcast",', 'TD(name="broadcast", icon="\u1f4e2", is_default=True,'),
    ('TD(name="subscribe_channel",', 'TD(name="subscribe_channel", icon="\u1f4e1", is_default=True,'),
    ('TD(name="publish_event",', 'TD(name="publish_event", icon="\u1f4e8", is_default=True,'),
    ('TD(name="read_file",', 'TD(name="read_file", icon="\u1f4d6", is_default=True,'),
    ('TD(name="write_file",', 'TD(name="write_file", icon="\u270f", is_default=True,'),
    ('TD(name="list_directory",', 'TD(name="list_directory", icon="\u1f4c1", is_default=True,'),
    ('TD(name="search_files",', 'TD(name="search_files", icon="\u1f50e", is_default=True,'),
    ('TD(name="schedule_task",', 'TD(name="schedule_task", icon="\u1f4c5", is_default=True,'),
    ('TD(name="set_alarm",', 'TD(name="set_alarm", icon="\u23f0", is_default=True,'),
    ('TD(name="watch_file",', 'TD(name="watch_file", icon="\u1f441", is_default=True,'),
    ('TD(name="cron_trigger",', 'TD(name="cron_trigger", icon="\u1f550", is_default=True,'),
    ('TD(name="list_agents",', 'TD(name="list_agents", icon="\u1f465", is_default=True,'),
    ('TD(name="list_capabilities",', 'TD(name="list_capabilities", icon="\u1f4cb", is_default=True,'),
    ('TD(name="dt_camera_move",', 'TD(name="dt_camera_move", icon="\u1f3a5", is_default=True,'),
    ('TD(name="dt_model_load",', 'TD(name="dt_model_load", icon="\u1f4e6", is_default=True,'),
    ('TD(name="dt_model_transform",', 'TD(name="dt_model_transform", icon="\u1f504", is_default=True,'),
    ('TD(name="dt_material_set",', 'TD(name="dt_material_set", icon="\u1f3a8", is_default=True,'),
    ('TD(name="dt_physics_toggle",', 'TD(name="dt_physics_toggle", icon="\u2699", is_default=True,'),
    ('TD(name="dt_light_adjust",', 'TD(name="dt_light_adjust", icon="\u1f4a1", is_default=True,'),
    ('TD(name="dt_render_mode",', 'TD(name="dt_render_mode", icon="\u1f5bc", is_default=True,'),
    ('TD(name="dt_inspection_path",', 'TD(name="dt_inspection_path", icon="\u1f6e4", is_default=True,'),
    ('TD(name="ais_query",', 'TD(name="ais_query", icon="\u1f6a2", is_default=True,'),
    ('TD(name="weather_fetch",', 'TD(name="weather_fetch", icon="\u1f30a", is_default=True,'),
    ('TD(name="route_calculate",', 'TD(name="route_calculate", icon="\u1f5fa", is_default=True,'),
    ('TD(name="colregs_check",', 'TD(name="colregs_check", icon="\u2693", is_default=True,'),
    ('TD(name="engine_status",', 'TD(name="engine_status", icon="\u1f527", is_default=True,'),
    ('TD(name="cargo_status",', 'TD(name="cargo_status", icon="\u1f4e6", is_default=True,'),
    ('TD(name="chart_ecdis_query",', 'TD(name="chart_ecdis_query", icon="\u1f5fa", is_default=True,'),
    ('TD(name="ais_vessel_track",', 'TD(name="ais_vessel_track", icon="\u1f4cd", is_default=True,'),
    ('TD(name="weather_marine_forecast",', 'TD(name="weather_marine_forecast", icon="\u26c5", is_default=True,'),
    ('TD(name="engine_diagnostic_scan",', 'TD(name="engine_diagnostic_scan", icon="\u1f529", is_default=True,'),
]
for old, new in pairs:
    c = c.replace(old, new, 1)

# Add new Clawith tools
new_tools = """        # \u2500\u2500 Clawith Platform Built-in Tools \u2500\u2500
        # Triggers (Clawith)
        TD(name="create_trigger", description="\u8bbe\u7f6e\u89e6\u53d1\u5668\u5728\u7279\u5b9a\u65f6\u95f4\u6216\u6761\u4ef6\u5524\u9192 Agent", category=TC.TRIGGERS, icon="\u23f0", is_default=True,
           parameters={"trigger_type": {"type": "string", "required": True, "description": "\u89e6\u53d1\u7c7b\u578b: time/condition/event"}, "schedule": {"type": "string", "required": False, "default": "", "description": "\u65f6\u95f4\u8868\u8fbe\u5f0f"}, "condition": {"type": "string", "required": False, "default": "", "description": "\u6761\u4ef6\u8868\u8fbe\u5f0f"}, "reason": {"type": "string", "required": False, "default": "", "description": "\u89e6\u53d1\u539f\u56e0"}}),
        TD(name="update_trigger", description="\u66f4\u65b0\u5df2\u6709\u89e6\u53d1\u5668\u7684\u914d\u7f6e\u6216\u539f\u56e0", category=TC,´RIA†ERS, icon="\u1f504", is_default=True,
           parameters={"trigger_id": {"type": "string", "required": True, "description": "\u89e6\u53d1\u5668ID"}, "schedule": {"type": "string", "required": False, "default": "", "description": "\u65b0\u65f6\u95f4\u8868\u8fbe\u5f0f"}, "condition": {"type": "string", "required": False, "default": "", "description": "\u65b0\u6761\u4ef6"}, "reason": {"type": "string", "required": False, "default": "", "description": "\u66f4\u65b0\u539f\u56e0"}, "enabled": {"type": "boolean", "required": False, "default": True, "description": "\u662f\u5426\u542f\u7528"}}),
"""

# Print success
print('Icons added, new tools partial')
with open(p, 'w') as f:
    f.write(c)
print('tool_registry.py icons DONE')
