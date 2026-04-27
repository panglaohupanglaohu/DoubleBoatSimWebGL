# PM分解 — project_manager

任务: 复杂任务测试V3
步骤: pm_decompose
Agent: build_pm

---

📋 任务: a7e34c74-6de
🤖 Agent: PM (project_manager)
📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
🔧 执行方式: DeepSeek API (直连)
⏱️ 超时: 1200s
────────────────────────────────────────────────────────────
📝 提示词:
  你是 PoseidonX 系统的 PM (project_manager)。
  请执行以下开发任务:
  
  你是项目经理 (PM)。请对以下任务进行分解和规划:
  
  ## 任务
  复杂任务测试V3
  在 src/frontend/digital-twin/main.js 给 cargo ship 圆周运动加上一个 wabi-sabi 风格的 HUD，显示当前角度和距离双体船的距离。同时需要新建一个 src/backend/channels/cargo_orbit_telemetry.py channel 继承 MarineChannel，process_event 上报 cargo 当前 lat/lon。
  
  ## 📂 项目上下文 (系统自动预加载)
  
  ### 项目文件结构 (src/ 目录)
  ```
  src/frontend/ARCHIVED_worldmonitor-ar-cas.html
  src/frontend/GLB_20251223141542.glb
  src/frontend/LOADING_FIX.md
  src/frontend/agent-team-config.html
  src/frontend/agent-team-config.html.backup
  src/frontend/agent-team-config.html.bak
  src/frontend/agent-team-config.html.bak2
  src/frontend/agent-team-config.html.bak3
  src/frontend/agent-team-config.html.bk
  src/frontend/agent-team-config.v1.bak.html
  src/frontend/captain-cockpit-new.html
  src/frontend/captain-cockpit-new.v1.bak.html
  src/frontend/captain-cockpit.html
  src/frontend/cms-health.html
  src/frontend/cms-health.html.bak
  src/frontend/cms-health.v1.bak.html
  src/frontend/crew-management.html
  src/frontend/crew-management.v1.bak.html
  src/frontend/datacenter-digital-twin.html
  src/frontend/datacenter-ratchet-evolution.html
  src/frontend/datacenter-ratchet-evolution.v1.bak.html
  src/frontend/datacenter-sensory-mesh.html
  src/frontend/design-demo-deepsea-ink.html
  src/frontend/design-demo-fieldio.html
  src/frontend/design-demo-kenyahara.html
  src/frontend/design-demo-pentagram.html
  src/frontend/design-demo-urushi.html
  src/frontend/design-demo-wabisabi.html
  src/frontend/digital-twin.html
  src/frontend/dp-control.html
  src/frontend/dp-control.html.bak
  src/frontend/dp-control.v1.bak.html
  src/frontend/energy-compliance.html
  src/frontend/energy-compliance.html.bak
  src/frontend/energy-compliance.v1.bak.html
  src/frontend/hmi-console.html
  src/frontend/hmi-console.html.bak
  src/frontend/hmi-console.v1.bak.html
  src/frontend/index.html
  src/frontend/index.html.bak
  src/frontend/index.v1.bak.html
  src/frontend/knowledge-base.html
  src/frontend/knowledge-base.html.bak
  src/frontend/knowledge-base.v1.bak.html
  src/frontend/marine-datacenter.html
  src/frontend/marine-datacenter.html.bak
  src/frontend/navigation-v2.bak.html
  src/frontend/navigation-v2.html
  src/frontend/navigation-v3.html
  src/frontend/navigation-v3.v1.bak.html
  src/frontend/navigation.html
  src/frontend/offshore-ops.html
  src/frontend/offshore-ops.html.bak
  src/frontend/offshore-ops.v1.bak.html
  src/frontend/poseidon-config.html
  src/frontend/poseidon-config.html.bak
  src/frontend/poseidon-config.v1.bak.html
  src/frontend/safety-emergency.html
  src/frontend/safety-emergency.html.bak
  src/frontend/safety-emergency.v1.bak.html
  src/frontend/ship-shore.html
  src/frontend/ship-shore.html.bak
  src/frontend/ship-shore.v1.bak.html
  src/frontend/sim-training.html
  src/frontend/sim-training.html.bak
  src/frontend/sim-training.v1.bak.html
  src/frontend/system-evolution.html
  src/frontend/system-evolution.html.bak
  src/frontend/system-evolution.v1.bak.html
  src/frontend/system-evolution.v2.bak.html
  src/frontend/thruster-control.html
  src/frontend/thruster-control.html.bak
  src/frontend/thruster-control.v1.bak.html
  src/frontend/thruster-control2.html
  src/frontend/thruster-control2.v1.bak.html
  src/frontend/weather-ocean.html
  src/frontend/weather-ocean.v1.bak.html
  src/frontend/worldmonitor-ar-cas-pro.html
  src/frontend/worldmonitor-ar-cas-pro.v1.bak.html
  src/frontend/worldmonitor-map.html
  src/frontend/worldmonitor-map.v1.bak.html
  src/frontend/css/openbridge-theme.css
  src/frontend/css/ws-theme-bridge.css
  src/frontend/js/AIoTMesh.js
  src/frontend/js/darwin-ratchet.js
  src/frontend/js/darwin-ratchet.js.bak
  src/frontend/js/i18n.js
  src/frontend/js/i18n.js.v1.bak
  src/frontend/js/nav-sidebar.js
  src/frontend/digital-twin/DataAggregator.js
  src/frontend/digital-twin/MarineEngineeringChannels.js
  src/frontend/digital-twin/MarineEngineeringModule.js
  src/frontend/digital-twin/NavigationMonitor.js
  src/frontend/digital-twin/PoseidonX.js
  src/frontend/digital-twin/PoseidonXChannels.js
  src/frontend/digital-twin/PoseidonXIntegration.js
  src/frontend/digital-twin/WeatherEffects.js
  src/frontend/digital-twin/WeatherEffects.js.bak
  src/frontend/digital-twin/demo.js
  src/frontend/digital-twin/index.js
  src/frontend/digital-twin/main.js
  src/frontend/digital-twin/main.js.bak
  src/frontend/digital-twin/simple-bridge-chat.js
  src/frontend/digital-twin/waves.js
  src/frontend/digital-twin/weather-controls.js
  src/frontend/digital-twin/layer3-platform/LLMJudge.js
  src/frontend/digital-twin/layer3-platform/SimulationValidator.js
  src/frontend/digital-twin/layer3-platform/VibeGenerator.js
  src/frontend/digital-twin/layer2-agents/AgentBase.js
  src/frontend/digital-twin/layer2-agents/AgentOrchestrator.js
  src/frontend/digital-twin/layer2-agents/BaseAgent.js
  src/frontend/digital-twin/layer2-agents/EngineerAgent.js
  src/frontend/digital-twin/layer2-agents/EnhancedEngineerAgent.js
  src/frontend/digital-twin/layer2-agents/NavigatorAgent.js
  src/frontend/digital-twin/layer2-agents/SafetyAgent.js
  src/frontend/digital-twin/layer2-agents/StewardAgent.js
  src/frontend/digital-twin/layer1-interface/AgentTeamMonitor.js
  src/frontend/digital-twin/layer1-interface/AnchorWatchPanel.js
  src/frontend/digital-twin/layer1-interface/BridgeChat.js
  src/frontend/digital-twin/layer1-interface/BridgeChat.js.bak
  src/frontend/digital-twin/layer1-interface/ContextWindow.js
  src/frontend/digital-twin/layer1-interface/CrewFatiguePanel.js
  src/frontend/digital-twin/layer1-interface/DPStatusPanel.js
  src/frontend/digital-twin/layer1-interface/DigitalTwinMap.js
  src/frontend/digital-twin/layer1-interface/HullStressPanel.js
  src/frontend/digital-twin/layer1-interface/LLMClient.js
  src/frontend/digital-twin/layer1-interface/MarineEngineeringPanel.js
  src/frontend/digital-twin/layer1-interface/PowerManagementPanel.js
  src/frontend/digital-twin/layer1-interface/WeatherRoutingPanel.js
  src/frontend/digital-twin/layer1-interface/panels/AlarmPanel.js
  src/frontend/digital-twin/layer1-interface/panels/AutopilotPanel.js
  src/frontend/digital-twin/layer1-interface/panels/CommsStatusPanel.js
  src/frontend/digital-twin/layer1-interface/panels/MOBPanel.js
  src/frontend/digital-twin/layer1-interface/panels/PropulsionPanel.js
  src/frontend/digital-twin/layer1-interface/panels/RudderPanel.js
  src/frontend/digital-twin/layer1-interface/panels/SafetyPanel.js
  src/frontend/digital-twin/layer1-interface/panels/TankLevelPanel.js
  src/frontend/digital-twin/layer1-interface/panels/VDRStatusPanel.js
  src/frontend/digital-twin/utils/EventEmitter.js
  src/backend/__init__.py
  src/backend/agent_team_api.py
  src/backend/api_extensions.py
  src/backend/api_marine_services.py
  src/backend/config_loader.py
  src/backend/main.py
  src/backend/main.py.bak
  src/backend/marine_channels_integration.py
  src/backend/register_channels.py
  src/backend/token_factory.py
  src/backend/agents/__init__.py
  ... (共 844 个 src/ 文件)
  
  ```
  
  ### 文件: `src/backend/channels/cargo_monitor.py`
  ```py
  # -*- coding: utf-8 -*-
  """
  L2: Cargo Monitor Channel - 货物监控
  
  监测各货舱的货物状态 (重量、温度、湿度)，
  跟踪装卸事件，并进行简化稳性估算。
  
  简化稳性模型:
  - GM = KM - KG
  - KM ≈ KB + BM, 其中 BM ≈ B² / (12 × T)
  - KB ≈ T / 2
  - KG 基于货物重心分布加权平均
  """
  
  from __future__ import annotations
  
  import logging
  from datetime import datetime
  from typing import Any, Dict, List
  
  from .marine_base import MarineChannel, ChannelStatus, ChannelPriority
  
  logger = logging.getLogger(__name__)
  
  
  class CargoMonitorChannel(MarineChannel):
      """货物监控 Channel — 货物状态、装卸事件与简化稳性估算。"""
  
      name = "cargo_monitor"
      description = "货物监控与简化稳性估算"
      version = "1.0.0"
      priority = ChannelPriority.P1
  
      def __init__(self, config=None, **kwargs):
          super().__init__(**(config or {}), **kwargs)
          self._active: bool = False
          # 货舱数据: hold_id -> {cargo_type, weight_tons, temperature, humidity, kg_height}
          self._holds: Dict[str, Dict[str, Any]] = {}
          # 装卸记录
          self._loading_events: List[Dict[str, Any]] = []
          # 船舶参数 (可通过 config 覆盖)
          cfg = config or {}
          self._beam: float = cfg.get("beam", 26.0)
          self._draft: float = cfg.get("draft", 5.5)
          self._lightship_weight: float = cfg.get("lightship_weight", 15000.0)
          self._lightship_kg: float = cfg.get("lightship_kg", 6.0)
  
      def initialize(self) -> bool:
          self._initialized = True
          self._active = True
          self._set_health(ChannelStatus.OK, "Cargo monitor ready")
          return True
  
      def get_status(self) -> Dict[str, Any]:
          total_weight = sum(h.get("weight_tons", 0.0) for h in self._holds.values())
          stability = self.check_stability()
          return {
              "name": self.name,
              "active": self._active,
              "initialized": self._initialized,
              "health": self._health.status.value,
              "holds": list(self._holds.values()),
              "total_weight": total_weight,
              "gm_estimate": stability["gm"],
              "trim": stability["trim"],
              "stability_status": stability["status"],
          }
  
      def shutdown(self) -> bool:
          self._active = False
          self._initialized = False
          self._set_health(ChannelStatus.OFF, "Shutdown")
          return True
  
      async def start(self):
          self._active = True
          self._set_health(ChannelStatus.OK, "Running")
  
      async def stop(self):
          self._active = False
  
      async def process_event(self, event: dict) -> dict:
          event_type = event.get("type", "")
  
          if event_type == "cargo_status":
              return self._handle_cargo_status(event)
          elif event_type == "loading_event":
              return self._handle_loading_event(event)
          elif event_type == "stability_check":
              return self._handle_stability_check(event)
  
          return {"status": "ignored", "reason": f"unknown event type: {event_type}"}
  
      # ---- event handlers ----
  
      def _handle_cargo_status(self, event: dict) -> dict:
          hold_id = event.get("hold_id")
          if hold_id is None:
              return {"status": "error", "reason": "hold_id is required"}
  
          self._holds[hold_id] = {
              "hold_id": hold_id,
              "cargo_type": event.get("cargo_type", "unknown"),
              "weight_tons": event.get("weight_tons", 0.0),
              "temperature": event.get("temperature"),
              "humidity": event.get("humidity"),
              "kg_height": event.get("kg_height", self._draft * 0.6),
              "updated_at": datetime.now().isoformat(),
          }
          return {"status": "updated", "hold_id": hold_id}
  
      def _handle_loading_event(self, event: dict) -> dict:
          hold_id = event.get("hold_id")
          if hold_id is None:
              return {"status": "error", "reason": "hold_id is required"}
  
          operation = event.get("operation", "load")
          weight_change = event.get("weight_change", 0.0)
  
          record = {
              "hold_id": hold_id,
              "operation": operation,
              "weight_change": weight_change,
              "timestamp": datetime.now().isoformat(),
          }
          self._loading_events.append(record)
  
          # 更新货舱重量
          if hold_id in self._holds:
              if operation == "load":
                  self._holds[hold_id]["weight_tons"] += weight_change
              elif operation == "unload":
                  self._holds[hold_id]["weight_tons"] = max(
                      0.0, self._holds[hold_id]["weight_tons"] - weight_change
                  )
              self._holds[hold_id]["updated_at"] = datetime.now().isoformat()
  
          return {"status": "recorded", "operation": operation, "hold_id": hold_id}
  
      def _handle_stability_check(self, event: dict) -> dict:
          stability = self.check_stability()
          return {**stability, "event_status": "checked"}
  
      # ---- core algorithms ----
  
      def check_stability(self) -> Dict[str, Any]:
          """简化稳性估算。
  
          GM = KM - KG
          KM = KB + BM
          KB ≈ T / 2
          BM ≈ B² / (12 × T)
          KG = Σ(wi × kgi) / Σ(wi)  (包含空船)
          """
          T = self._draft
          B = self._beam
  
          if T <= 0:
              return {"gm": 0.0, "km": 0.0, "kg": 0.0, "trim": 0.0, "status": "error"}
  
          KB = T / 2.0
          BM = (B ** 2) / (12.0 * T)
          KM = KB + BM
  
          # 加权 KG
          total_weight = self._lightship_weight
          moment = self._lightship_weight * self._lightship_kg
  
          for hold in self._holds.values():
              w = hold.get("weight_tons", 0.0)
              kg_h = hold.get("kg_height", T * 0.6)
              total_weight += w
              moment += w * kg_h
  
          KG = moment / total_weight if total_weight > 0 else 0.0
          GM = KM - KG
  
          # 简化纵倾估算 (基于货物前后分布不均匀度)
          trim = self._estimate_trim()
  
          if GM < 0.15:
              status = "critical"
          elif GM < 0.5:
              status = "warning"
          else:
              status = "ok"
  
          return {
              "gm": round(GM, 3),
              "km": round(KM, 3),
              "kg": round(KG, 3),
              "trim": round(trim, 3),
              "status": status,
          }
  
      def _estimate_trim(self) -> float:
          """简化纵倾估算 — 基于前后货舱重量差。"""
          forward_weight = 0.0
          aft_weight = 0.0
          for hold in self._holds.values():
              hold_id = hold.get("hold_id", "")
              w = hold.get("weight_tons", 0.0)
              # 简单规则: hold id 含 'F'/'1'/'2' 归前部, 含 'A'/'4'/'5' 归后部
              if any(c in str(hold_id).upper() for c in ("F", "1", "2")):
                  forward_weight += w
              elif any(c in str(hold_id).upper() for c in ("A", "4", "5")):
                  aft_weight += w
              else:
                  forward_weight += w / 2
                  aft_weight += w / 2
  
          total = forward_weight + aft_weight
          if total <= 0:
              return 0.0
          # 归一化差值作为纵倾指标 (正值 = 尾倾)
          return (aft_weight - forward_weight) / total
  
  ```
  
  ### 文件: `src/backend/channels/cargo_ship_orbit.py`
  ```py
  # -*- coding: utf-8 -*-
  """
  Cargo Ship Orbit Channel - 货船绕双体船轨道运动控制
  
  实现货船以双体船为圆心做圆周运动的控制逻辑。
  通过 MarineChannel 架构集成到 PoseidonX 系统中。
  """
  
  from __future__ import annotations
  
  import logging
  import math
  from dataclasses import dataclass, field, asdict
  from datetime import datetime
  from typing import Any, Dict, List, Optional
  
  from channels.marine_base import MarineChannel, ChannelPriority, ChannelStatus
  
  logger = logging.getLogger(__name__)
  
  
  # ---------------------------------------------------------------------------
  # Data Models
  # ---------------------------------------------------------------------------
  
  @dataclass
  class OrbitConfig:
      """轨道运动配置参数。"""
      radius: float = 80.0           # 轨道半径 (场景单位，与前端3D场景匹配)
      speed_deg_per_sec: float = 0.3  # 角速度 (度/秒) — 慢速，约 0.005 rad/帧 @60fps
      initial_angle_deg: float = 0.0  # 初始角度 (度)
      height_offset: float = 0.0      # 高度偏移 (米)
      enabled: bool = True            # 是否启用轨道运动
      auto_start: bool = True         # 是否自动启动
  
      def to_dict(self) -> Dict[str, Any]:
          return asdict(self)
  
  
  @dataclass
  class OrbitState:
      """轨道运动状态。"""
      current_angle_deg: float = 0.0
      elapsed_seconds: float = 0.0
      is_running: bool = False
      last_update: Optional[str] = None
      total_orbits: float = 0.0
  
      def to_dict(self) -> Dict[str, Any]:
          return asdict(self)
  
  
  # ---------------------------------------------------------------------------
  # Cargo Ship Orbit Channel
  # ---------------------------------------------------------------------------
  
  class CargoShipOrbitChannel(MarineChannel):
      """
      货船轨道运动控制 Channel。
      
      控制货船以双体船为圆心做匀速圆周运动。
      通过 tick() 方法计算��船的新位置，供前端3D场景使用。
      """
      
      name = "cargo_ship_orbit"
      description = "货船绕双体船轨道运动控制"
      version = "1.0.0"
      priority = ChannelPriority.P2  # 辅助功能，不影响核心功能
      dependencies: List[str] = [
          "wpc_attitude_control",  # 依赖双体船姿态控制，确保双体船已初始化
      ]
      
      def __init__(self, config: Optional[Dict[str, Any]] = None):
          super().__init__()
          self.config = config or {}
          self._config = self.config
          
          # 轨道配置
          orbit_cfg = self.config.get("orbit", {})
          self.orbit_config = OrbitConfig(
              radius=orbit_cfg.get("radius", 80.0),
              speed_deg_per_sec=orbit_cfg.get("speed_deg_per_sec", 0.3),
              initial_angle_deg=orbit_cfg.get("initial_angle_deg", 0.0),
              height_offset=orbit_cfg.get("height_offset", 0.0),
              enabled=orbit_cfg.get("enabled", True),
              auto_start=orbit_cfg.get("auto_start", True),
          )
          
          # 轨道状态
          self.orbit_state = OrbitState(
              current_angle_deg=self.orbit_config.initial_angle_deg,
              is_running=self.orbit_config.auto_start and self.orbit_config.enabled,
          )
          
          # 双体船位置 (由外部更新)
          self._catamaran_position: Dict[str, float] = {"x": 0.0, "y": 0.0, "z": 0.0}
          
          # 货船当前位置 (计算结果)
          self._cargo_ship_position: Dict[str, float] = {"x": 0.0, "y": 0.0, "z": 0.0}
          
          # 货船朝向角度 (始终朝向运动方向)
          self._cargo_ship_heading: float = 0.0
          
          # 事件日志
          self.event_log: List[Dict[str, Any]] = []
          
          logger.info("🚢 CargoShipOrbitChannel initialized (radius=%.1fm, speed=%.2f°/s)",
                       self.orbit_config.radius, self.orbit_config.speed_deg_per_sec)
      
      # ── MarineChannel 接口 ───────────────────────────────────
      
      def initialize(self) -> bool:
          """初始化轨道控制。"""
          self._initialized = True
          
          if self.orbit_config.enabled:
              self.orbit_state.is_running = self.orbit_config.auto_start
              self._set_health(
                  ChannelStatus.OK,
                  f"货船轨道运动就绪 (半径={self.orbit_config.radius}m, 速度={self.orbit_config.speed_deg_per_sec}°/s)"
              )
              logger.info("🚢 Cargo ship orbit initialized: radius=%.1fm, speed=%.2f°/s",
                           self.orbit_config.radius, self.orbit_config.speed_deg_per_sec)
          else:
              self._set_health(ChannelStatus.OK, "货船轨道运动已禁用")
          
          return True
      
      def shutdown(self) -> bool:
          """关闭轨道控制。"""
          self._initialized = False
          self.orbit_state.is_running = False
          self._set_health(ChannelStatus.OFF, "Shutdown")
          return True
      
      def get_status(self) -> Dict[str, Any]:
          """获取 Channel 当前状态。"""
          return self.to_dict()
      
      def process_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
          """
          处理外部事件。
          
          支持的事件类型:
            - "start_orbit": 启动轨道运动
            - "stop_orbit": 停止轨道运动
            - "set_radius": 设置轨道半径 (需提供 radius 参数)
            - "set_speed": 设置轨道角速度 (需提供 speed_deg_per_sec 参数)
            - "reset_orbit": 重置轨道到初始状态
            - "update_catamaran": 更新双体船位置 (需提供 x, y, z 参数)
            - "tick": 触发一次位置更新
          
          Args:
              event: 事件字典，必须包含 "type" 字段
              
          Returns:
              处理结果字典，或 None 如果事件类型不支持
          """
          event_type = event.get("type", "")
          
          if event_type == "start_orbit":
              ok = self.start_orbit()
              return {"status": "ok" if ok else "error", "action": "start_orbit"}
          
          elif event_type == "stop_orbit":
              ok = self.stop_orbit()
              return {"status": "ok" if ok else "error", "action": "stop_orbit"}
          
          elif event_type == "set_radius":
              radius = event.get("radius", 80.0)
              try:
                  self.set_orbit_radius(radius)
                  return {"status": "ok", "action": "set_radius", "radius": radius}
              except ValueError as e:
                  return {"status": "error", "action": "set_radius", "message": str(e)}
          
          elif event_type == "set_speed":
              speed = event.get("speed_deg_per_sec", 0.3)
              try:
                  self.set_orbit_speed(speed)
                  return {"status": "ok", "action": "set_speed", "speed_deg_per_sec": speed}
              except ValueError as e:
                  return {"status": "error", "action": "set_speed", "message": str(e)}
          
          elif event_type == "reset_orbit":
              self.reset_orbit()
              return {"status": "ok", "action": "reset_orbit"}
          
          elif event_type == "update_catamaran":
              x = event.get("x", 0.0)
              y = event.get("y", 0.0)
              z = event.get("z", 0.0)
              self.update_catamaran_position(x, y, z)
              return {"status": "ok", "action": "update_catamaran", "position": {"x": x, "y": y, "z": z}}
          
          elif event_type == "tick":
              now = event.get("now")
              result = self.tick(now=now)
              return {"status": "ok", "action": "tick", "result": result}
          
          return None
      
      # ── 核心逻辑 ─────────────────────────────────────────────
      
      def tick(self, now: Optional[datetime] = None, channel_registry: Optional[Dict] = None) -> Dict[str, Any]:
          """
          定时更新货船位置。
          
          计算货船在轨道上的新位置，基于双体船位置和当前角度。
          
          Args:
              now: 当前时间
              channel_registry: Channel 注册表 (可选)
              
          Returns:
              包含货船新位置和状态的字典
          """
          now = now or datetime.now()
          
          # 如果未启用或未运行，返回当前位置
          if not self.orbit_config.enabled or not self.orbit_state.is_running:
              return {
                  "running": self.orbit_state.is_running,
                  "enabled": self.orbit_config.enabled,
                  "cargo_position": self._cargo_ship_position,
                  "cargo_heading": self._cargo_ship_heading,
                  "catamaran_position": self._catamaran_position,
              }
          
          # 计算时间增量
          if self.orbit_state.last_update:
              try:
                  last = datetime.fromisoformat(self.orbit_state.last_update)
                  delta_seconds = (now - last).total_seconds()
              except (ValueError, TypeError):
                  delta_seconds = 1.0
          else:
              delta_seconds = 1.0
          
          # 限制最大时间步长 (防止跳帧)
          delta_seconds = min(delta_seconds, 5.0)
          
          # 更新角度
          angle_change = self.orbit_config.speed_deg_per_sec * delta_seconds
          self.orbit_state.current_angle_deg = (self.orbit_state.current_angle_deg + angle_change) % 360.0
          
          # 更新状态
          self.orbit_state.elapsed_seconds += delta_seconds
          self.orbit_state.last_update = now.isoformat()
          self.orbit_state.total_orbits = self.orbit_state.elapsed_seconds * self.orbit_config.speed_deg_per_sec / 360.0
          
          # 计算货船位置
          angle_rad = math.radians(self.orbit_state.current_angle_deg)
          cx = self._catamaran_position["x"]
          cz = self._catamaran_position["z"]
          cy = self._catamaran_position["y"]
          
          self._cargo_ship_position = {
              "x": cx + self.orbit_config.radius * math.cos(angle_rad),
              "y": cy + self.orbit_config.height_offset,
              "z": cz + self.orbit_config.radius * math.sin(angle_rad),
          }
          
          # 货船朝向 (运动方向切线方向)
          # 切线方向 = 当前角度 + 90°
          heading_deg = (self.orbit_state.current_angle_deg + 90.0) % 360.0
          self._cargo_ship_heading = heading_deg
          
          # 记录事件
          self.event_log.append({
              "time": now.isoformat(),
              "angle_deg": self.orbit_state.current_angle_deg,
              "position": dict(self._cargo_ship_position),
              "heading": heading_deg,
          })
          
          # 限制日志大小
          if len(self.event_log) > 1000:
              self.event_log = self.event_log[-500:]
          
          return {
              "running": True,
              "enabled": True,
              "angle_deg": self.orbit_state.current_angle_deg,
              "cargo_position": self._cargo_ship_position,
              "cargo_heading": self._cargo_ship_heading,
              "catamaran_position": self._catamaran_position,
              "total_orbits": round(self.orbit_state.total_orbits, 2),
              "elapsed_seconds": round(self.orbit_state.elapsed_seconds, 1),
          }
      
      # ── 公共方法 ─────────────────────────────────────────────
      
      def update_catamaran_position(self, x: float, y: float, z: float) -> None:
          """
          更新双体船位置。
          
          由外部 (如 WPC 姿态控制 Channel) 调用，更新双体船当前位置。
          
          Args:
              x: X 坐标
              y: Y 坐标 (高度)
              z: Z 坐标
          """
          self._catamaran_position = {"x": x, "y": y, "z": z}
      
      def get_cargo_position(self) -> Dict[str, float]:
          """获取货船当前位置。"""
          return dict(self._cargo_ship_position)
      
      def get_cargo_heading(self) -> float:
          """获取货船朝向角度 (度)。"""
          return self._cargo_ship_heading
      
      def get_orbit_state(self) -> Dict[str, Any]:
          """获取完整轨道状态。"""
          return {
              "config": self.orbit_config.to_dict(),
              "state": self.orbit_state.to_dict(),
              "cargo_position": self._cargo_ship_position,
              "cargo_heading": self._cargo_ship_heading,
              "catamaran_position": self._catamaran_position,
          }
      
      def start_orbit(self) -> bool:
          """启动轨道运动。"""
          if not self.orbit_config.enabled:
              logger.warning("🚢 Cannot start orbit: orbit is disabled")
              return False
          self.orbit_state.is_running = True
          self._set_health(ChannelStatus.OK, "货船轨道运动已启动")
          logger.info("🚢 Cargo ship orbit started")
          return True
      
      def stop_orbit(self) -> bool:
          """停止轨道运动。"""
          self.orbit_state.is_running = False
          self._set_health(ChannelStatus.OK, "货船轨道运动已停止")
          logger.info("🚢 Cargo ship orbit stopped")
          return True
      
      def set_orbit_radius(self, radius: float) -> None:
          """设置轨道半径。"""
          if radius <= 0:
              raise ValueError("Radius must be positive")
          self.orbit_config.radius = radius
          logger.info("🚢 Orbit radius set to %.1fm", radius)
      
      def set_orbit_speed(self, speed_deg_per_sec: float) -> None:
          """设置轨道角速度。"""
          if speed_deg_per_sec <= 0:
              raise ValueError("Speed must be positive")
          self.orbit_config.speed_deg_per_sec = speed_deg_per_sec
          logger.info("🚢 Orbit speed set to %.2f°/s", speed_deg_per_sec)
      
      def reset_orbit(self) -> None:
          """重置轨道到初始状态。"""
          self.orbit_state.current_angle_deg = self.orbit_config.initial_angle_deg
          self.orbit_state.elapsed_seconds = 0.0
          self.orbit_state.total_orbits = 0.0
          self.orbit_state.last_update = None
          logger.info("🚢 Orbit reset to initial state")
      
      def to_dict(self) -> Dict[str, Any]:
          """序列化 Channel 状态。"""
          return {
              "name": self.name,
              "description": self.description,
              "version": self.version,
              "priority": self.priority.value,
              "initialized": self._initialized,
              "health": self._health.status.value if self._health else "unknown",
              "health_message": self._health.message if self._health else "",
              "orbit_config": self.orbit_config.to_dict(),
              "orbit_state": self.orbit_state.to_dict(),
              "cargo_position": self._cargo_ship_position,
              "cargo_heading": self._cargo_ship_heading,
              "catamaran_position": self._catamaran_position,
          }
  
  
  __all__ = ["CargoShipOrbitChannel", "OrbitConfig", "OrbitState"]
  ```
  
  ### 文件: `src/backend/channels/maintenance_planner.py`
  ```py
  # -*- coding: utf-8 -*-
  """
  L2: Maintenance Planner Channel - 维修计划管理 (PMS)
  
  设备维修计划和状态跟踪，工单管理。
  """
  
  from __future__ import annotations
  
  import logging
  import uuid
  from datetime import datetime
  from typing import Any, Dict, List, Optional
  
  from .marine_base import MarineChannel, ChannelStatus, ChannelPriority
  
  logger = logging.getLogger(__name__)
  
  VALID_CATEGORIES = {"engine", "navigation", "safety", "hull", "electrical"}
  VALID_STATUSES = {"ok", "maintenance_due", "overdue", "out_of_service"}
  VALID_WO_STATUSES = {"open", "in_progress", "completed", "cancelled"}
  
  
  class MaintenancePlannerChannel(MarineChannel):
      """维修计划管理 Channel — PMS 设备跟踪与工单管理。"""
  
      name = "maintenance_planner"
      description = "设备维修计划与工单管理"
      version = "1.0.0"
      priority = ChannelPriority.P1
  
      def __init__(self, config=None, **kwargs):
          super().__init__(**(config or {}), **kwargs)
          self._active: bool = False
          self._equipment: Dict[str, Dict[str, Any]] = {}
          self._work_orders: List[Dict[str, Any]] = []
  
      # ---- lifecycle ----
  
      def initialize(self) -> bool:
          self._initialized = True
          self._active = True
          self._set_health(ChannelStatus.OK, "Maintenance planner ready")
          return True
  
      def shutdown(self) -> bool:
          self._active = False
          self._initialized = False
          self._set_health(ChannelStatus.OFF, "Shutdown")
          return True
  
      async def start(self):
          self._active = True
          self._set_health(ChannelStatus.OK, "Running")
  
      async def stop(self):
          self._active = False
  
      # ---- core methods ----
  
      def register_equipment(self, equip_id: str, name: str, category: str,
                             maintenance_interval_hours: float = 500) -> dict:
          equip = {
              "equip_id": equip_id,
              "name": name,
              "category": category,
              "running_hours": 0.0,
              "last_maintenance_hours": 0.0,
              "maintenance_interval_hours": maintenance_interval_hours,
              "status": "ok",
          }
          self._equipment[equip_id] = equip
          return {"status": "registered", "equipment": equip}
  
      def update_running_hours(self, equip_id: str, hours: float) -> dict:
          equip = self._equipment.get(equip_id)
          if equip is None:
              return {"status": "error", "reason": f"equipment {equip_id} not found"}
          equip["running_hours"] = hours
          self._check_maintenance_status(equip)
          return {"status": "updated", "equipment": equip}
  
      def record_maintenance(self, equip_id: str) -> dict:
          equip = self._equipment.get(equip_id)
          if equip is None:
              return {"status": "error", "reason": f"equipment {equip_id} not found"}
          equip["last_maintenance_hours"] = equip["running_hours"]
          equip["status"] = "ok"
          return {"status": "maintenance_recorded", "equipment": equip}
  
      def create_work_order(self, equip_id: str, description: str, priority: int = 3) -> dict:
          wo = {
              "work_order_id": str(uuid.uuid4())[:8],
              "equip_id": equip_id,
              "description": description,
              "priority": max(1, min(5, priority)),
              "status": "open",
              "created_at": datetime.now().isoformat(),
          }
          self._work_orders.append(wo)
          return {"status": "work_order_created", "work_order": wo}
  
      def get_maintenance_summary(self) -> dict:
          due_count = sum(1 for e in self._equipment.values() if e["status"] == "maintenance_due")
          overdue_count = sum(1 for e in self._equipment.values() if e["status"] == "overdue")
          open_wo = sum(1 for wo in self._work_orders if wo["status"] in ("open", "in_progress"))
  
          # 找最近下一个需要维修的设备
          next_maint: Optional[Dict[str, Any]] = None
          min_remaining = float("inf")
          for equip in self._equipment.values():
              interval = equip["maintenance_interval_hours"]
              since_last = equip["running_hours"] - equip["last_maintenance_hours"]
              remaining = interval - since_last
              if remaining < min_remaining:
                  min_remaining = remaining
                  next_maint = {
                      "equip_id": equip["equip_id"],
                      "name": equip["name"],
                      "remaining_hours": remaining,
                  }
  
          return {
              "total_equipment": len(self._equipment),
              "due_count": due_count,
              "overdue_count": overdue_count,
              "open_work_orders": open_wo,
              "next_maintenance": next_maint,
          }
  
      # ---- event processing ----
  
      async def process_event(self, event: dict) -> dict:
          event_type = event.get("type", "")
  
          if event_type == "equipment_update":
              equip_id = event.get("equip_id")
              hours = event.get("running_hours")
              if equip_id is None or hours is None:
                  return {"status": "error", "reason": "equip_id and running_hours required"}
              return self.update_running_hours(equip_id, hours)
          elif event_type == "maintenance_complete":
              equip_id = event.get("equip_id")
              if equip_id is None:
                  return {"status": "error", "reason": "equip_id required"}
              return self.record_maintenance(equip_id)
          elif event_type == "work_order":
              equip_id = event.get("equip_id", "")
              desc = event.get("description", "")
              prio = event.get("priority", 3)
              return self.create_work_order(equip_id, desc, prio)
  
          return {"status": "ignored", "reason": f"unknown event type: {event_type}"}
  
      def get_status(self) -> Dict[str, Any]:
          summary = self.get_maintenance_summary()
          return {
              "name": self.name,
              "total_equipment": summary["total_equipment"],
              "due_count": summary["due_count"],
              "overdue_count": summary["overdue_count"],
              "open_work_orders": summary["open_work_orders"],
              "initialized": self._initialized,
              "health": self._health.status.value,
          }
  
      # ---- internal ----
  
      @staticmethod
      def _check_maintenance_status(equip: dict) -> None:
          interval = equip["maintenance_interval_hours"]
          since_last = equip["running_hours"] - equip["last_maintenance_hours"]
          if since_last >= interval * 1.1:
              equip["status"] = "overdue"
          elif since_last >= interval:
              equip["status"] = "maintenance_due"
          else:
              equip["status"] = "ok"
  
  ```
  
  ### 文件: `src/backend/channels/ship_shore_link.py`
  ```py
  #!/usr/bin/env python3
  # -*- coding: utf-8 -*-
  """
  Ship-Shore Communication Link Manager - 船岸通信链路管理
  
  参考 SHI SVESSEL BIG (onBoard Integrated Gateway) 架构:
  - 多链路管理 (LTE/5G, VSAT, Inmarsat)
  - 链路质量监测与自动切换
  - 网络延迟预测与补偿
  - 数据传输优先级队列
  
  参考 DFFAS 联合体岸基 FOC 通信系统:
  - 船-岸之间稳定通信
  - 紧急情况下从 FOC 切换到远程操作
  """
  
  from dataclasses import dataclass, field
  from datetime import datetime, timedelta
  from enum import Enum
  from typing import Any, Dict, List, Optional, Tuple
  import random
  import math
  
  from .marine_base import MarineChannel, ChannelStatus, ChannelPriority
  
  
  class LinkType(Enum):
      """通信链路类型."""
      LTE_5G = "lte_5g"
      VSAT = "vsat"
      INMARSAT = "inmarsat"
      WIFI = "wifi"
      VHF_DATA = "vhf_data"
  
  
  class LinkStatus(Enum):
      """链路状态."""
      CONNECTED = "connected"
      DEGRADED = "degraded"
      DISCONNECTED = "disconnected"
      SWITCHING = "switching"
  
  
  @dataclass
  class LinkProfile:
      """链路配置参数."""
      link_type: LinkType
      max_bandwidth_kbps: float
      typical_latency_ms: float
      max_range_km: float
      priority: int  # 1=最高优先
      cost_per_mb: float  # 美元/MB
      encryption: str = "AES-256"
      is_available: bool = True
  
  
  @dataclass
  class LinkMetrics:
      """链路实时测量指标."""
      link_type: LinkType
      status: LinkStatus = LinkStatus.DISCONNECTED
      current_latency_ms: float = 0.0
      packet_loss_pct: float = 0.0
      bandwidth_usage_pct: float = 0.0
      signal_strength_dbm: float = -80.0
      jitter_ms: float = 0.0
      uptime_seconds: float = 0.0
      bytes_sent: int = 0
      bytes_received: int = 0
      last_heartbeat: Optional[datetime] = None
      error_count: int = 0
  
  
  @dataclass
  class LatencyPrediction:
      """网络延迟预测 (参考论文中网络时延预测和补偿技术)."""
      predicted_latency_ms: float
      confidence: float
      trend: str  # "stable", "increasing", "decreasing"
      compensation_strategy: str
      samples_used: int = 0
  
  
  # 默认链路参数 (基于实际海上通信系统)
  def build_default_link_profiles() -> Dict[LinkType, LinkProfile]:
      """Build fresh link profile objects for each channel instance.
  
      This avoids cross-instance state leakage when tests mutate availability.
      """
      return {
          LinkType.LTE_5G: LinkProfile(
              link_type=LinkType.LTE_5G,
              max_bandwidth_kbps=50000,
              typical_latency_ms=30,
              max_range_km=50,
              priority=1,
              cost_per_mb=0.01,
          ),
          LinkType.VSAT: LinkProfile(
              link_type=LinkType.VSAT,
              max_bandwidth_kbps=4096,
              typical_latency_ms=600,
              max_range_km=99999,
              priority=2,
              cost_per_mb=0.10,
          ),
          LinkType.INMARSAT: LinkProfile(
              link_type=LinkType.INMARSAT,
              max_bandwidth_kbps=492,
              typical_latency_ms=800,
              max_range_km=99999,
              priority=3,
              cost_per_mb=1.50,
          ),
      }
  
  
  class ShipShoreLinkChannel(MarineChannel):
      """船岸通信链路管理 Channel.
  
      对标 SVESSEL BIG 网关 + DFFAS FOC 通信系统架构。
      实现多链路管理、自动切换、延迟预测与补偿。
      """
  
      name = "ship_shore_link"
      description = "船岸通信链路管理 - 多链路监测、自动切换与延迟补偿"
      version = "1.0.0"
      priority = ChannelPriority.P0
      dependencies = []
  
      def __init__(self, **kwargs):
          super().__init__(**kwargs)
          self._links: Dict[LinkType, LinkMetrics] = {}
          self._link_profiles: Dict[LinkType, LinkProfile] = build_default_link_profiles()
          self._active_link: Optional[LinkType] = None
          self._latency_history: List[Tuple[datetime, float]] = []
          self._switch_history: List[Dict] = []
          self._shore_connected: bool = False
          self._distance_to_shore_km: float = 0.0
          self._max_latency_samples = 60
  
      def initialize(self) -> bool:
          for link_type, profile in self._link_profiles.items():
              self._links[link_type] = LinkMetrics(link_type=link_type)
          self._initialized = True
          self._set_health(ChannelStatus.OK, "Ship-shore link manager initialized")
          return True
  
      def update_link_status(
          self,
          link_type: LinkType,
          latency_ms: float,
          packet_loss_pct: float = 0.0,
          signal_strength_dbm: float = -70.0,
          bandwidth_usage_pct: float = 30.0,
      ) -> LinkMetrics:
          """更新链路实时指标."""
          metrics = self._links.get(link_type)
          if metrics is None:
              metrics = LinkMetrics(link_type=link_type)
              self._links[link_type] = metrics
  
          metrics.current_latency_ms = latency_ms
          metrics.packet_loss_pct = max(0.0, min(100.0, packet_loss_pct))
          metrics.signal_strength_dbm = signal_strength_dbm
          metrics.bandwidth_usage_pct = max(0.0, min(100.0, bandwidth_usage_pct))
          metrics.last_heartbeat = datetime.now()
  
          # 根据信号判定链路状态
          if signal_strength_dbm > -85 and packet_loss_pct < 5:
              metrics.status = LinkStatus.CONNECTED
          elif signal_strength_dbm > -95 and packet_loss_pct < 15:
              metrics.status = LinkStatus.DEGRADED
          else:
              metrics.status = LinkStatus.DISCONNECTED
  
          # 记录延迟历史
          now = datetime.now()
          self._latency_history.append((now, latency_ms))
          if len(self._latency_history) > self._max_latency_samples:
              self._latency_history = self._latency_history[-self._max_latency_samples:]
  
          return metrics
  
      def get_active_link(self) -> Optional[LinkType]:
          """返回当前活跃链路."""
          return self._active_link
  
      def select_best_link(self) -> Optional[LinkType]:
          """自动选择最佳链路 (基于质量评分)."""
          best_link = None
          best_score = -1.0
  
          for link_type, metrics in self._links.items():
              if metrics.status == LinkStatus.DISCONNECTED:
                  continue
              profile = self._link_profiles.get(link_type)
              if profile is None or not profile.is_available:
                  continue
  
              # 综合评分: 延迟(40%) + 带宽(20%) + 信号(20%) + 丢包(20%)
              latency_score = max(0, 1.0 - metrics.current_latency_ms / 2000)
              bw_score = 1.0 - metrics.bandwidth_usage_pct / 100
              signal_score = max(0, (metrics.signal_strength_dbm + 100) / 50)
              loss_score = 1.0 - metrics.packet_loss_pct / 100
              score = latency_score * 0.4 + bw_score * 0.2 + signal_score * 0.2 + loss_score * 0.2
  
              if score > best_score:
                  best_score = score
                  best_link = link_type
  
          old_link = self._active_link
          if best_link is not None and best_link != old_link:
              self._active_link = best_link
              self._switch_history.append({
                  "timestamp": datetime.now().isoformat(),
                  "from_link": old_link.value if old_link else None,
                  "to_link": best_link.value,
                  "reason": "quality_based_selection",
              })
          elif best_link is None and self._active_link is not None:
              self._active_link = None
  
          return self._active_link
  
      def predict_latency(self) -> LatencyPrediction:
          """网络延迟预测 (滑动窗口 + 加权平均)."""
          if len(self._latency_history) < 3:
              return LatencyPrediction(
                  predicted_latency_ms=500.0,
                  confidence=0.3,
                  trend="unknown",
                  compensation_strategy="fixed_buffer",
                  samples_used=len(self._latency_history),
              )
  
          samples = [lat for _, lat in self._latency_history[-20:]]
          n = len(samples)
  
          # 指数加权平均
          weights = [math.exp(i / n) for i in range(n)]
          total_weight = sum(weights)
          ewa = sum(s * w for s, w in zip(samples, weights)) / total_weight
  
          # 趋势检测: 前半段与后半段均值对比
          mid = n // 2
          first_half = sum(samples[:mid]) / max(mid, 1)
          second_half = sum(samples[mid:]) / max(n - mid, 1)
          diff = second_half - first_half
  
          if diff > 30:
              trend = "increasing"
              compensation = "predictive_extrapolation"
          elif diff < -30:
              trend = "decreasing"
              compensation = "adaptive_reduction"
          else:
              trend = "stable"
              compensation = "ewa_smoothing"
  
          # 置信度: 基于方差
          variance = sum((s - ewa) ** 2 for s in samples) / n
          std_dev = math.sqrt(variance)
          confidence = max(0.3, min(0.99, 1.0 - std_dev / max(ewa, 1)))
  
          return LatencyPrediction(
              predicted_latency_ms=round(ewa, 1),
              confidence=round(confidence, 3),
              trend=trend,
              compensation_strategy=compensation,
              samples_used=n,
          )
  
      def set_distance_to_shore(self, distance_km: float) -> None:
          """更新离岸距离, 影响链路可用性."""
          self._distance_to_shore_km = max(0.0, distance_km)
          for link_type, profile in self._link_profiles.items():
              metrics = self._links.get(link_type)
              if metrics is None:
                  continue
              if self._distance_to_shore_km > profile.max_range_km:
                  metrics.status = LinkStatus.DISCONNECTED
                  profile.is_available = False
              else:
                  profile.is_available = True
  
      def simulate_link_conditions(self) -> Dict[str, Any]:
          """模拟当前海况下的通信状况 (用于仿真和演示)."""
          dist = self._distance_to_shore_km
  
          for link_type, profile in self._link_profiles.items():
              if dist > profile.max_range_km:
                  self.update_link_status(link_type, 9999, 100, -120, 0)
                  continue
  
              range_factor = min(1.0, dist / max(profile.max_range_km, 1))
              base_lat = profile.typical_latency_ms
              jitter = random.uniform(-0.1, 0.15) * base_lat
              latency = base_lat * (1 + range_factor * 0.5) + jitter
              loss = range_factor * 8 + random.uniform(0, 2)
              signal = -60 - range_factor * 35 + random.uniform(-3, 3)
              bw = 20 + range_factor * 40 + random.uniform(-5, 10)
  
              self.update_link_status(link_type, max(5, latency), loss, signal, bw)
  
          self.select_best_link()
          return self.get_link_summary()
  
      def get_link_summary(self) -> Dict[str, Any]:
          """获取所有链路摘要."""
          links = {}
          for link_type, metrics in self._links.items():
              profile = self._link_profiles.get(link_type)
              links[link_type.value] = {
                  "status": metrics.status.value,
                  "latency_ms": round(metrics.current_latency_ms, 1),
                  "packet_loss_pct": round(metrics.packet_loss_pct, 2),
                  "signal_dbm": round(metrics.signal_strength_dbm, 1),
                  "bandwidth_usage_pct": round(metrics.bandwidth_usage_pct, 1),
                  "max_bandwidth_kbps": profile.max_bandwidth_kbps if profile else 0,
                  "last_heartbeat": metrics.last_heartbeat.isoformat() if metrics.last_heartbeat else None,
              }
  
          prediction = self.predict_latency()
          best_link_type = self._active_link.value if self._active_link else None
          best_link_latency = prediction.predicted_latency_ms
          best_link_quality = None
          if self._active_link and self._active_link.value in links:
              active_metrics = links[self._active_link.value]
              loss = float(active_metrics.get("packet_loss_pct", 0.0))
              latency = float(active_metrics.get("latency_ms", best_link_latency or 0.0))
              quality = max(0.0, min(1.0, (100.0 - (loss * 2.0) - (latency / 20.0)) / 100.0))
              best_link_quality = round(quality, 3)
  
          return {
              "active_link": self._active_link.value if self._active_link else None,
              "best_link_type": best_link_type,
              "best_link_latency": best_link_latency,
              "best_link_quality": best_link_quality,
              "distance_to_shore_km": round(self._distance_to_shore_km, 1),
              "shore_connected": self._active_link is not None,
              "links": links,
              "latency_prediction": {
                  "predicted_ms": prediction.predicted_latency_ms,
                  "confidence": prediction.confidence,
                  "trend": prediction.trend,
                  "compensation": prediction.compensation_strategy,
              },
              "switch_count": len(self._switch_history),
              "recent_switches": self._switch_history[-3:] if self._switch_history else [],
          }
  
      def get_status(self) -> Dict[str, Any]:
          summary = self.get_link_summary()
          return {
              "channel": self.name,
              "version": self.version,
              "initialized": self._initialized,
              "health": "ok" if summary["shore_connected"] else "warn",
              "health_message": f"Active: {summary['active_link'] or 'none'}, "
                                f"Distance: {summary['distance_to_shore_km']} km",
              **summary,
          }
  
      def shutdown(self) -> bool:
          self._initialized = False
          self._set_health(ChannelStatus.OFF, "Shut down")
          return True
  
  ```
  
  ### 文件: `src/backend/channels/system_evolution.py`
  ```py
  # -*- coding: utf-8 -*-
  """
  System Self-Evolution Engine — 系统自我演进引擎
  
  执行智能体参考业界标准审查各 Channel，发现不完善之处后
  自动生成演进任务，派发给 Build 团队执行修改，并通过
  模拟人类操作的自动化测试进行验证。
  
  闭环流程:
    Audit (执行智能体审查)
      → Discovery (发现演进项)
        → Dispatch (派发 Build 团队)
          → Build (实施修改)
            → Verify (自动化测试验证)
              → Close / Retry
  
  术语:
    EvolutionItem   — 一条演进需求
    AuditRule       — 审查规则 (对标 IAMSAR / SOLAS / COLREGs / GMDSS 等)
    BuildTask       — 派发给 Build 团队的工作单元
    VerifyResult    — 自动化测试验证结果
  """
  
  from __future__ import annotations
  
  import logging
  import time
  import uuid
  from dataclasses import dataclass, field, asdict
  from datetime import datetime
  from enum import Enum
  from typing import Any, Callable, Dict, List, Optional, Tuple
  
  from .marine_base import (
      MarineChannel,
      ChannelPriority,
      ChannelStatus,
      get_default_registry,
  )
  
  logger = logging.getLogger(__name__)
  
  
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # Data Models
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  
  class EvolutionStatus(str, Enum):
      """演进条目生命周期状态。"""
      DISCOVERED = "discovered"          # 执行智能体发现
      DISPATCHED = "dispatched"          # 已派发 Build 团队
      IN_PROGRESS = "in_progress"        # Build 团队工作中
      VERIFY_PENDING = "verify_pending"  # 等待验证
      VERIFIED = "verified"              # 验证通过
      FAILED = "failed"                  # 验证失败 (需重试)
      CLOSED = "closed"                  # 关闭
  
  
  class Severity(str, Enum):
      CRITICAL = "critical"
      HIGH = "high"
      MEDIUM = "medium"
      LOW = "low"
  
  
  class AuditDomain(str, Enum):
      IAMSAR = "IAMSAR"
      SOLAS = "SOLAS"
      COLREGS = "COLREGs"
      GMDSS = "GMDSS"
      MARPOL = "MARPOL"
      MLC_STCW = "MLC/STCW"
      CII_EEXI = "CII/EEXI"
      DATACENTER = "Datacenter"
      GENERAL = "general"
  
  
  # ── DNV-style A~E Compliance Rating (inspired by DNV CII) ──
  
  class ComplianceRating(str, Enum):
      """DNV CII 风格 A~E 五级合规评级。"""
      A = "A"  # Major superior — 全面优秀
      B = "B"  # Minor superior — 良好，少量待改进
      C = "C"  # Moderate       — 基本合规，需要关注
      D = "D"  # Minor inferior — 不达标，需要纠正计划
      E = "E"  # Inferior       — 严重不合规，需紧急干预
  
      @staticmethod
      def from_score(score: float) -> "ComplianceRating":
          """0~100 分 → A~E 评级 (阈值逐年加严，参考 DNV CII reduction factor)。"""
          if score >= 85:
              return ComplianceRating.A
          if score >= 70:
              return ComplianceRating.B
          if score >= 55:
              return ComplianceRating.C
          if score >= 40:
              return ComplianceRating.D
          return ComplianceRating.E
  
  
  # ── Kongsberg-style Operational Domain (6-domain) ───────────
  
  class OperationalDomain(str, Enum):
      """Kongsberg Maritime 启发的 6 大操作域分类。"""
      TECHNICAL_MGMT = "technical_management"    # 技术管理
      COMPLIANCE_SAFETY = "compliance_safety"    # 合规与安全
      FUEL_EMISSIONS = "fuel_emissions"          # 燃油与排放
      VOYAGE_COMMERCIAL = "voyage_commercial"    # 航次与商业
      DATA_DECISION = "data_decision"            # 数据与决策
      ADVANCED_OPS = "advanced_operations"       # 高级操作 (自主/DP)
  
  
  # ── ClassNK-style Dual-Layer Checklist ──────────────────────
  
  class ChecklistLevel(str, Enum):
      """ClassNK 双层自查清单: 公司级 + 船级。"""
      COMPANY = "company"  # 公司管理体系 (ISM DOC)
      SHIP = "ship"        # 船舶管理体系 (ISM SMC)
      BOTH = "both"        # 两级均需检查
  
  
  # ── Failure Escalation Tiers (DNV SEEMP Part III) ───────────
  
  class EscalationTier(str, Enum):
      """失败升级层级 — 参考 DNV SEEMP Part III 纠正计划机制。"""
      NORMAL = "normal"              # 正常处理
      CORRECTIVE_PLAN = "corrective" # 需要纠正行动计划 (连续2次失败)
      MANAGEMENT_REVIEW = "review"   # 需要管理层审查 (连续3次失败)
      CRITICAL_HOLD = "hold"         # 暂停相关操作 (连续4+次失败)
  
  
  @dataclass
  class EvolutionItem:
      """一条由执行智能体发现的系统演进需求。"""
      id: str = field(default_factory=lambda: f"EVO-{uuid.uuid4().hex[:8]}")
      title: str = ""
      description: str = ""
      target_channel: str = ""
      audit_domain: str = AuditDomain.GENERAL.value
      severity: str = Severity.MEDIUM.value
      status: str = EvolutionStatus.DISCOVERED.value
  
      # 审查依据
      reference_standard: str = ""       # 例如 "IAMSAR Vol III §3.7"
      current_behavior: str = ""         # 当前系统行为描述
      expected_behavior: str = ""        # 业界期望行为
  
      # Build 团队处理
      build_task_id: Optional[str] = None
      assigned_agent: Optional[str] = None
      code_changes: List[str] = field(default_factory=list)  # 变更文件列表
  
      # 验证
      verify_test_name: Optional[str] = None   # 用于验证的测试函数名
      verify_result: Optional[str] = None      # passed / failed
      verify_detail: Optional[str] = None
  
      # 时间线
      discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
      dispatched_at: Optional[str] = None
      completed_at: Optional[str] = None
      closed_at: Optional[str] = None
  
      # 重试
      retry_count: int = 0
      max_retries: int = 3
  
      # ── Phase 3 新增字段 ─────────────────────────────
      escalation_tier: str = EscalationTier.NORMAL.value
      consecutive_failures: int = 0
      compliance_rating: str = ""  # A~E
      operational_domain: str = ""
      checklist_level: str = ChecklistLevel.SHIP.value
  
      def to_dict(self) -> Dict[str, Any]:
          return asdict(self)
  
  
  # ── Compliance Zone (Wärtsilä Zone Management 启发) ─────────
  
  @dataclass
  class ComplianceZone:
      """地理围栏合规区域 — 进入特定水域时自动激活对应合规规则。"""
      id: str
      name: str
      zone_type: str  # ECA / MARPOL_SPECIAL / SECA / PSSA / HIGH_RISK / CUSTOM
      description: str = ""
      # 简化几何: 矩形包围盒 (适合船舶航线粗筛)
      lat_min: float = 0.0
      lat_max: float = 0.0
      lon_min: float = 0.0
      lon_max: float = 0.0
      # 此区域内自动激活的规则 ID 列表
      activated_rule_ids: List[str] = field(default_factory=list)
      # 额外合规要求描述
      extra_requirements: str = ""
      # 生效状态
      active: bool = True
  
      def contains(self, lat: float, lon: float) -> bool:
          """检查坐标是否在区域内。"""
          return (self.lat_min <= lat <= self.lat_max and
                  self.lon_min <= lon <= self.lon_max)
  
      def to_dict(self) -> Dict[str, Any]:
          return asdict(self)
  
  
  # ── Audit Trail Entry (NAPA Logbook 启发) ───────────────────
  
  @dataclass
  class AuditTrailEntry:
      """审计轨迹条目 — 不可变的审计日志记录。"""
      id: str = field(default_factory=lambda: f"ATR-{uuid.uuid4().hex[:8]}")
      timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
      event_type: str = ""  # audit_run / dispatch / verify / escalation / zone_enter / rating_change
      rule_id: str = ""
      item_id: str = ""
      actor: str = ""       # agent name 或 "system"
      old_value: str = ""
      new_value: str = ""
      detail: str = ""
      compliance_rating: str = ""
      zone_id: str = ""
  
      def to_dict(self) -> Dict[str, Any]:
          return asdict(self)
  
  
  @dataclass
  class AuditRule:
      """一条审查规则，用于自动发现演进项。"""
      id: str
      domain: str
      title: str
      description: str
      target_channel: str
      check_fn: Optional[Callable] = None  # (channel) -> (passed: bool, detail: str)
      reference: str = ""
      severity: str = Severity.MEDIUM.value
      # ── Phase 3 新增字段 ─────────────────────────────
      operational_domain: str = OperationalDomain.COMPLIANCE_SAFETY.value
      checklist_level: str = ChecklistLevel.SHIP.value
      rating_weight: float = 1.0  # 评级权重 (用于加权合规分数计算)
  
      def to_dict(self) -> Dict[str, Any]:
          d = asdict(self)
          d.pop("check_fn", None)
          return d
  
  
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # Built-in Audit Rules
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  
  def _check_mob_survival_table(channel) -> Tuple[bool, str]:
      """SOLAS: 5°C 生存时间应 ≤ 1.0h (IMO MSC/Circ.1046)。"""
      from .man_overboard import _SURVIVAL_TABLE
      for temp, hours in _SURVIVAL_TABLE:
          if temp == 5 and hours > 1.05:
              return False, f"5°C 生存时间为 {hours}h，IMO 建议 ≤ 1.0h"
      return True, "生存时间表符合 IMO MSC/Circ.1046"
  
  
  def _check_mob_search_patterns(channel) -> Tuple[bool, str]:
      """IAMSAR: 应包含 Expanding Square 和 Sector Search 搜索模式。"""
      from .man_overboard import VALID_SEARCH_PATTERNS
      required = {"expanding_square", "sector_search"}
      existing = set(VALID_SEARCH_PATTERNS)
      missing = required - existing
      if missing:
          return False, f"缺少 IAMSAR 标准搜索模式: {missing}"
      return True, "搜索模式包含 IAMSAR 标准模式"
  
  
  def _check_mob_message_priority(channel) -> Tuple[bool, str]:
      """GMDSS: MOB PAN-PAN 应使用 URGENCY 优先级，非 DISTRESS。"""
      # 检查 activate_mob 中的消息优先级
      import inspect
      src = inspect.getsource(channel.activate_mob)
      if "MessagePriority.DISTRESS" in src and "URGENCY_PAN_PAN" in src:
          return False, "PAN-PAN 消息使用了 DISTRESS 优先级，应为 URGENCY"
      return True, "PAN-PAN 消息优先级正确"
  
  
  def _check_mob_in_decision_orchestrator(_channel) -> Tuple[bool, str]:
      """L3 决策编排器应集成 MOB 状态感知。"""
      import inspect
      from .decision_orchestrator import DecisionOrchestratorChannel
      src = inspect.getsource(DecisionOrchestratorChannel._build_action_plan)
      if "man_overboard" not in src and "mob" not in src.lower():
          return False, "DecisionOrchestrator._build_action_plan 未集成 MOB 状态"
      return True, "决策编排器已集成 MOB"
  
  
  def _check_mob_drift_formula(channel) -> Tuple[bool, str]:
      """IAMSAR: 搜索半径应考虑 Total Probable Error。"""
      drift = channel.estimate_drift(
          wind_speed_kn=10.0, wind_dir_deg=0.0,
          current_speed_kn=0.5, current_dir_deg=0.0,
          elapsed_min=60.0,
      )
      if "datum_error" not in drift and "total_error" not in drift:
          return False, "漂移模型缺少 datum error / total probable error 字段"
      return True, "漂移模型包含 TPE 估算"
  
  
  def _check_build_exec_feedback_loop(_channel) -> Tuple[bool, str]:
      """Build↔Exec 团队应有闭环反馈。"""
      reg = get_default_registry()
      build = reg.get("build_team_manager")
      exec_team = reg.get("execution_team_manager")
      if not build or not exec_team:
          return False, "Build 或 Exec 团队 Channel 未注册"
      # 检查 build 是否有接收 exec 反馈的机制
      has_accept = hasattr(build, "accept_evolution_feedback")
      if not has_accept:
          return False, "BuildTeamManager 缺少 accept_evolution_feedback 方法"
      return True, "Build↔Exec 反馈闭环已就绪"
  
  
  # ── Additional Audit Rules ──────────────────────────────────
  
  
  def _check_colregs_rule17(channel) -> Tuple[bool, str]:
      """COLREGs Rule 17: Stand-on vessel action handling."""
      reg = get_default_registry()
      colregs = reg.get("colregs_brain")
      if not colregs:
          return False, "COLREGs Brain Channel 未注册"
      import inspect
      src = inspect.getsource(type(colregs))
      if "rule_17" not in src.lower() and "stand_on" not in src.lower():
          return False, "COLREGs Brain 缺少 Rule 17 (stand-on vessel) 处理逻辑"
      return True, "COLREGs Rule 17 已实现"
  
  
  def _check_colregs_overtaking(channel) -> Tuple[bool, str]:
      """COLREGs Rule 13: Overtaking vessel gives way."""
      reg = get_default_registry()
      colregs = reg.get("colregs_brain")
      if not colregs:
          return False, "COLREGs Brain Channel 未注册"
      import inspect
      src = inspect.getsource(type(colregs))
      if "overtaking" not in src.lower() and "rule_13" not in src.lower():
          return False, "COLREGs Brain 缺少 Rule 13 (overtaking) 处理逻辑"
      return True, "COLREGs Rule 13 (Overtaking) 已实现"
  
  
  def _check_eexi_attained_calculation(channel) -> Tuple[bool, str]:
      """CII/EEXI: EEXI attained calculation must exist."""
      reg = get_default_registry()
      eexi = reg.get("energy_efficiency")
      if not eexi:
          return False, "Energy Efficiency Channel 未注册"
      has_calc = hasattr(eexi, "calculate_eexi") or hasattr(eexi, "get_eexi_status")
      if not has_calc:
          return False, "能效 Channel 缺少 EEXI 计算方法"
      return True, "EEXI 计算方法已就绪"
  
  
  def _check_cii_rating_system(channel) -> Tuple[bool, str]:
      """CII/EEXI: CII annual rating (A-E) must be implemented."""
      reg = get_default_registry()
      eexi = reg.get("energy_efficiency")
      if not eexi:
          return False, "Energy Efficiency Channel 未注册"
      has_cii = hasattr(eexi, "calculate_cii") or hasattr(eexi, "get_cii_rating")
      if not has_cii:
          return False, "能效 Channel 缺少 CII 评级方法 (A-E)"
      return True, "CII 评级系统已就绪"
  
  
  def _check_fire_zone_matrix(channel) -> Tuple[bool, str]:
      """SOLAS Ch II-2: Fire zone matrix should cover all zones."""
      reg = get_default_registry()
      fire_ch = reg.get("cargo_fire_suppression") or reg.get("fire_detection")
      if not fire_ch:
          return False, "消防 Channel 未注册"
      has_zones = hasattr(fire_ch, "fire_zones") or hasattr(fire_ch, "get_fire_zones")
      if not has_zones:
          return False, "消防 Channel 缺少分区管理 (fire_zones)"
      return True, "消防分区矩阵已实现"
  
  
  def _check_alarm_priority_system(channel) -> Tuple[bool, str]:
      """IEC 62923: Alarm system priority classification."""
      reg = get_default_registry()
      alarm = reg.get("alarm_management")
      if not alarm:
          return False, "报警管理 Channel 未注册"
      has_priority = hasattr(alarm, "priorities") or hasattr(alarm, "alarm_priorities")
      if not has_priority:
          import inspect
          src = inspect.getsource(type(alarm))
          if "priority" not in src.lower():
              return False, "报警管理缺少优先级分类 (IEC 62923)"
      return True, "报警优先级系统符合 IEC 62923"
  
  
  def _check_wpc_seakeeping(channel) -> Tuple[bool, str]:
      """WPC 穿浪双体船纵摇/横摇限值检查。"""
      reg = get_default_registry()
      wpc = reg.get("wpc_attitude_control")
      if not wpc:
          return False, "WPC 姿态控制 Channel 未注册"
      has_limits = hasattr(wpc, "pitch_limit") or hasattr(wpc, "_pitch_l
  ```
  
  ## 要求
  1. 分析任务需求，拆解为可执行的子步骤
  2. 识别技术风险和依赖关系
  3. 为后续研究人员、架构师、开发者提供清晰的指导
  4. 输出一份结构化的任务分解文档 (Markdown 格式)
  
  ## ⚠️ 重要提示
  系统已自动预加载项目文件结构和相关源文件（见下方 📂 项目上下文）。
  请基于**实际存在的文件**进行分析，不要猜测文件名。
  
  项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  后端: src/backend/ (Python FastAPI)
  前端: src/frontend/ (HTML + JS)
  
  
  项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  后端: src/backend/ (Python FastAPI)
  前端: src/frontend/ (HTML + JS)
  
────────────────────────────────────────────────────────────
⚡ 使用 DeepSeek V4 直连 (64K 输出, 流式)...

🔗 API: api.deepseek.com | 模型: deepseek-chat
────────────────────────────────────────────────────────────

好的，作为 PoseidonX 系统的项目经理 (PM)，我已经分析了“复杂任务测试V3”的需求。以下是针对该任务的详细分解和规划。

---

## 任务分解与规划: 货船轨道运动 HUD 与遥测 Channel

**任务 ID:** TASK-COMPLEX-V3
**任务名称:** 复杂任务测试V3
**项目经理:** PoseidonX PM
**创建日期:** 2024-05-24

### 1. 任务概述

本任务旨在为 PoseidonX 数字孪生系统增加两项核心功能：
1.  **前端 (Frontend):** 在 `src/frontend/digital-twin/main.js` 中，为正在进行的货船圆周运动添加一个 **wabi-sabi 风格**的 HUD (Heads-Up Display)。该 HUD 需要实时显示货船的当前角度以及其与双体船之间的距离。
2.  **后端 (Backend):** 新建一个 `src/backend/channels/cargo_orbit_telemetry.py` 文件，其中包含一个继承自 `MarineChannel` 的 `CargoOrbitTelemetryChannel`。该 Channel 需要处理 `process_event` 事件，并上报货船的当前经纬度 (`lat/lon`)。

### 2. 任务分解 (WBS)

#### 阶段 1: 分析与准备 (PM & 架构师)

| 步骤 | 描述 | 负责人 | 产出物 |
| :--- | :--- | :--- | :--- |
| **1.1** | **审查现有代码:** 分析 `src/frontend/digital-twin/main.js` 中货船圆周运动的实现逻辑，特别是如何获取货船位置 (`x, y, z`) 和角度。 | 架构师 | 理解现有数据流和接口 |
| **1.2** | **审查后端架构:** 分析 `src/backend/channels/marine_base.py` 中 `MarineChannel` 的基类定义，以及 `src/backend/channels/cargo_ship_orbit.py` 中 `CargoShipOrbitChannel` 的实现，理解如何创建新的 Channel 和上报事件。 | 架构师 | 理解 Channel 生命周期和事件处理模式 |
| **1.3** | **定义 wabi-sabi 风格:** 与设计师或产品负责人确认“wabi-sabi 风格”的具体视觉元素（如：不完美的线条、自然纹理、不对称、侘寂色调、手写字体等），并确定 HUD 的布局和交互方式。 | PM / 设计师 | wabi-sabi HUD 设计规范 |
| **1.4** | **定义遥测数据格式:** 明确 `CargoOrbitTelemetryChannel` 上报的 `lat/lon` 数据格式（例如：WGS84 标准），以及 `process_event` 应接受的事件类型和参数。 | 架构师 | 数据接口定义文档 |

#### 阶段 2: 后端开发 (Backend Developer)

| 步骤 | 描述 | 负责人 | 产出物 |
| :--- | :--- | :--- | :--- |
| **2.1** | **创建 Channel 文件:** 在 `src/backend/channels/` 目录下新建 `cargo_orbit_telemetry.py` 文件。 | 后端开发 | `cargo_orbit_telemetry.py` 文件 |
| **2.2** | **实现 `CargoOrbitTelemetryChannel` 类:** 继承 `MarineChannel`，实现 `__init__`, `initialize`, `process_event`, `get_status`, `shutdown` 等必要方法。 | 后端开发 | 完整的 Channel 类 |
| **2.3** | **实现 `process_event` 逻辑:** 处理 `report_position` 类型的事件。该事件应包含 `lat` 和 `lon` 参数。Channel 需要将这些数据存储或转发到���统总线（例如，通过 `self.publish_event` 或写入内部状态）。 | 后端开发 | 事件处理逻辑 |
| **2.4** | **集成坐标转换 (可选):** 如果 `CargoShipOrbitChannel` 使用的是笛卡尔坐标系 (`x, y, z`)，`CargoOrbitTelemetryChannel` 需要实现一个简单的坐标转换函数，将 `x, z` 转换为 `lat, lon`（基于��体船位置和地球曲率简化模型）。 | 后端开发 | 坐标转换逻辑 |
| **2.5** | **注册 Channel:** 在 `src/backend/register_channels.py` 或相关配置文件中注册新的 `CargoOrbitTelemetryChannel`，确保系统启动时能加载它。 | 后端开发 | 更新后的注册文件 |
| **2.6** | **单元测试:** 为 `CargoOrbitTelemetryChannel` 编写单元测试，验证 `process_event` 的正确性和数据上报流程。 | 后端开发 | 单元测试代码 |

#### 阶段 3: 前端开发 (Frontend Developer)

| 步骤 | 描述 | 负责人 | 产出物 |
| :--- | :--- | :--- | :--- |
| **3.1** | **创建 HUD 组件:** 在 `src/frontend/digital-twin/` 目录下（或 `main.js` 内部）创建一个新的 HUD 组件。该组件负责渲染和管理 wabi-sabi 风格的 UI 元素。 | 前端开发 | HUD 组件代码 |
| **3.2** | **实现 wabi-sabi 样式:** 使用 CSS 或 Canvas 绘制 wabi-sabi 风格的 HUD。这可能包括：<br> - 使用 `@font-face` 加载手写风格字体。<br> - 绘制不完美的圆形或弧形来显示角度。<br> - 使用自然、低饱和度的颜色（如米色、墨色、赭石）。<br> - 添加轻微的纹理或噪点效果。 | 前端开发 | wabi-sabi 样式代码 |
| **3.3** | **集成数据源:** 在 `main.js` 中，找到货船位置更新的代码段。将货船的当前角度和与双体船的距离数据传递给新创建的 HUD 组件。 | 前端开发 | 数据绑定逻辑 |
| **3.4** | **HUD 数据更新:** 在 HUD 组件内部，实现一个更新方法（如 `updateData(angle, distance)`），用于实时刷新显示内容。 | 前端开发 | HUD 数据更新逻辑 |
| **3.5** | **触发后端事件:** 在 `main.js` 的货船位置更新循环中，添加代码以调用后端 API 或通过 WebSocket 发送 `report_position` 事件，触发 `CargoOrbitTelemetryChannel` 的 `process_event`。 | 前端开发 | 前后端事件触发逻辑 |

#### 阶段 4: 集成与测试 (QA & 架构师)

| 步骤 | 描述 | 负责人 | 产出物 |
| :--- | :--- | :--- | :--- |
| **4.1** | **集成测试:** 启动整个 PoseidonX 系统，验证前端 HUD 能否正确显示货船的角度和距离，并随着货船运动实时更新。 | QA | 集成测试报告 |
| **4.2** | **端到端测试:** 验证前端发送的 `report_position` 事件能否被后端 `CargoOrbitTelemetryChannel` 正确接收和处理。 | QA | 端到端测试报告 |
| **4.3** | **视觉审查:** 检查 wabi-sabi HUD 的视觉效果是否符合设计规范。 | PM / 设计师 | 视觉审查反馈 |
| **4.4** | **性能测试:** 确保 HUD 的渲染和事件上报不会对前端帧率或后端性能造成显著影响。 | QA | 性能测试报告 |

### 3. 技术风险与依赖关系

| 风险/依赖 | 描述 | 缓解措施 |
| :--- | :--- | :--- |
| **R1: wabi-sabi 风格定义不明确** | “wabi-sabi” 是一个抽象概念，不同人对它的理解可能不同，导致前端实现与预期不符。 | 在 **步骤 1.3** 中，必须输出一份具体的、可视化的设计规范（如 Figma 设计稿或截图参考），并得到所有相关方确认。 |
| **R2: 坐标转换精度** | 从笛卡尔坐标到经纬度的转换如果过于简化，可能导致货船位置在地图上显示不准确。 | 在 **步骤 2.4** 中，评估精度需求。如果要求不高，可以使用简化的等距投影。如果要求高，则需要引入更精确的 GIS 库（如 `pyproj`）。 |
| **R3: 前后端数据流中断** | 如果前端通过 WebSocket 发送事件，连接不稳定可能导致数据丢失。 | 在 **步骤 3.5** 中，实现重连机制。后端 Channel 应设计为幂等的，能够处理重复或丢失的数据包。 |
| **D1: 依赖 `CargoShipOrbitChannel`** | 前端 HUD 和后端遥测 Channel 都依赖于 `CargoShipOrbitChannel` 提供的货船位置数据。 | 确保 `CargoShipOrbitChannel` 已经稳定运行，并定义了清晰的公共 API（如 `get_cargo_position()` 和 `get_cargo_heading()`）。 |
| **D2: 依赖 `MarineChannel` 基类** | 新的后端 Channel 必须严格遵循 `MarineChannel` 的接口规范。 | 在 **步骤 1.2** 中，架构师需要提供一份清晰的 `MarineChannel` 接口文档或代码示例，供后端开发者参考。 |

### 4. 执行计划与建议

1.  **并行开发:** 阶段 2 (后端) 和阶段 3 (前端) 可以并行进行，因为它们相对独立。但前提是阶段 1 的分析和设计工作已经完成。
2.  **迭代交付:**
    - **迭代 1 (核心功能):** 先实现一个功能完整的 HUD（不追求完美 wabi-sabi 风格）和基本的后端 Channel，确保数据流畅通。
    - **迭代 2 (风格打磨):** 在核心功能验证通过后，再投入精力打磨 wabi-sabi 的视觉效果。
3.  **代码审查:** 所有代码变更（特别是 `main.js` 和新的 Channel 文件）都需要经过架构师或高级开发者的代码审查，以确保代码质量和系统架构的一致性。
4.  **文档更新:** 任务完成后，需要更新相关文档，说明新增的 HUD 功能和遥测 Channel 的使用方法。

### 5. 总结

本任务是一个典型的前后端协同开发任务，涉及 UI 设计、前端渲染、后端服务开发和系统集成。通过清晰的任务分解、风险识别和并行开发策略，我们有信心在保证质量的前提下高效完成此任务。请各团队负责人根据此规划进行资源分配和任务认领。

────────────────────────────────────────────────────────────
✅ deepseek-chat 完成
