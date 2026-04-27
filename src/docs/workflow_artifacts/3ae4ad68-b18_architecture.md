# 架构设计 — architect

任务: 让货船以双体船为圆心动起来
步骤: architecture
Agent: build_architect

---

📋 任务: 3ae4ad68-b18
🤖 Agent: Architect (architect)
📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
🔧 执行方式: DeepSeek API (直连)
⏱️ 超时: 1200s
────────────────────────────────────────────────────────────
📝 提示词:
  你是 PoseidonX 系统的 Architect (architect)。
  请执行以下开发任务:
  
  你是系统架构师。请为以下任务设计技术方案:
  
  ## 任务
  让货船以双体船为圆心动起来
  给build团队的PM分配一个任务，让货船以双体船为圆心动起来
  
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
  src/backend/agents/agent_loop.py
  ... (共 790 个 src/ 文件)
  
  ```
  
  ### 文件: `src/frontend/js/darwin-ratchet.js`
  ```js
  /**
   * Darwin Ratchet — 达尔文棘轮演化机制
   * 系统只增不减地累积有益特性 (Irreversible Feature Accumulation)
   *
   * API:
   *   Darwin.record(item)  — 记录一次演化 (去重 by id)
   *   Darwin.list()        — 全部特性 (按时间排序)
   *   Darwin.locked()      — 已锁定特性
   *   Darwin.stats()       — 统计
   *   Darwin.onChange(cb)  — 变化订阅
   */
  (function() {
      const STORAGE_KEY = 'poseidonx.darwin.ratchet';
      const listeners = [];
      
      function load() {
          try {
              return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
          } catch (e) {
              return [];
          }
      }
      
      function save(items) {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
          listeners.forEach(cb => { try { cb(items); } catch (e) {} });
          // Broadcast cross-tab
          try {
              const bc = new BroadcastChannel('poseidonx-darwin');
              bc.postMessage({ type: 'update', items });
              bc.close();
          } catch (e) {}
      }
      
      function record(item) {
          if (!item || !item.id) return null;
          const items = load();
          const existing = items.find(x => x.id === item.id);
          const now = new Date().toISOString();
          if (existing) {
              // Update fitness only — core record is locked
              if (item.fitness && item.fitness !== existing.fitness) {
                  existing.fitness = item.fitness;
                  existing.updatedAt = now;
                  save(items);
              }
              return existing;
          }
          const record = {
              id: item.id,
              title: item.title || item.id,
              category: item.category || 'ui',
              description: item.description || '',
              fitness: item.fitness || 'pending',
              lockedAt: item.fitness === 'pass' ? now : null,
              createdAt: now,
              updatedAt: now,
              generation: items.length + 1,
          };
          items.push(record);
          save(items);
          console.log('[Darwin] 🧬 New evolution recorded:', record.title, '(Gen', record.generation + ')');
          return record;
      }
      
      function list() {
          return load().slice().sort((a, b) => (a.createdAt || '').localeCompare(b.createdAt || ''));
      }
      
      function locked() {
          return list().filter(x => x.fitness === 'pass');
      }
      
      function stats() {
          const items = load();
          const byCategory = {};
          items.forEach(i => { byCategory[i.category] = (byCategory[i.category] || 0) + 1; });
          return {
              total: items.length,
              locked: items.filter(i => i.fitness === 'pass').length,
              pending: items.filter(i => i.fitness === 'pending').length,
              rejected: items.filter(i => i.fitness === 'reject').length,
              byCategory,
              lastGeneration: items.length,
          };
      }
      
      function onChange(cb) {
          listeners.push(cb);
          // Cross-tab sync
          try {
              const bc = new BroadcastChannel('poseidonx-darwin');
              bc.onmessage = (e) => { if (e.data && e.data.type === 'update') cb(e.data.items); };
          } catch (e) {}
          return () => {
              const i = listeners.indexOf(cb);
              if (i >= 0) listeners.splice(i, 1);
          };
      }
      
      // 初始化: 一次性记录历史演化项 (只在首次运行时写入)
      function bootstrap() {
          const HERITAGE = [
              { id: 'day-mode-lighting-v1',    title: '日间模式亮化',             category: 'scene',   description: '环境光 + 半球光 1.6x 增强, 天空着色器日间蓝' },
              { id: 'sky-shader-day-v1',       title: '程序化日间天空',            category: 'scene',   description: '地平线浅蓝 → 天顶深蓝渐变 + 太阳光晕' },
              { id: 'cabin-interiors-v1',      title: '6 舱室 3D 内饰',           category: 'scene',   description: '驾驶台/机舱/ECR/货舱/船员舱/厨房 完整建模' },
              { id: 'cabin-split-screen-v1',   title: '分屏舱室信息系统',          category: 'ui',      description: '左 3D + 右系统信息, 进入舱室自动分屏' },
              { id: 'cabin-search-keywords-v1',title: '搜索框识别舱室中文名',      category: 'ui',      description: '输入驾驶台/动力舱/机舱自动进入' },
              { id: 'cabin-dropdown-menu-v1',  title: '舱室快速下拉菜单',          category: 'ui',      description: '右上角单按钮折叠展开式舱室导航' },
              { id: 'ar-cas-floating-v2',      title: 'AR-CAS Pro 可拖拽面板',    category: 'ui',      description: '独立浮动, 拖拽/折叠/调整大小, localStorage 持久化' },
              { id: 'ar-cas-enriched-v1',      title: 'AR-CAS Pro 丰富信息',      category: 'safety',  description: '本船状态 + 环境 + COLREGs 建议 + CPA/TCPA 分解' },
              { id: 'ais-iceberg-merge-v1',    title: 'AIS 列表聚合本地威胁',     category: 'data',    description: 'AIS 列表自动包含 3D 场景中的冰山和货船目标' },
              { id: 'ocean-shader-v1',         title: '海洋 GPU 着色器',          category: 'scene',   description: '多层正弦波 + 菲涅尔反射 + 次表面散射' },
              { id: 'icebergs-sss-v1',         title: '冰山次表面散射着色',        category: 'scene',   description: '5 座冰山, 菲涅尔边缘 + 水下蓝色渗透' },
              { id: 'weather-particles-v1',    title: '天气粒子系统',             category: 'scene',   description: '雨/雪/雾/海鸥/烟囱尾气' },
              { id: 'openbridge-hmi-v1',       title: 'OpenBridge HMI 主题',     category: 'ui',       description: 'DNV OpenBridge 2.4 四主题切换 (dusk/dawn/day/night)' },
              { id: 'colregs-brain-v1',        title: 'COLREGs Brain L3',        category: 'ai',       description: 'Rule 13/14/15/17 自动判断 + TCPA/CPA 威胁评估' },
              { id: 'wpc-attitude-v1',         title: '穿浪双体船姿态控制',       category: 'physics',  description: '水翼/T-Foil 主动姿态反馈 抑制 pitch/heave' },
              { id: 'iamsar-drift-v1',         title: 'MOB + IAMSAR 漂移',       category: 'safety',   description: '落水报警 + 风流联合搜索半径预测' },
              { id: 'darwin-ratchet-v1',       title: '达尔文棘轮机制',          category: 'ai',       description: '只增不减的演化累积引擎' },
              { id: 'bridge-task-dispatch-v1', title: '桥楼任务派发规则',        category: 'ai',       description: '桥楼聊天识别"给X团队的Y设置任务"指令并 POST 到 /agent-config/teams/{team}/tasks, 自动同步至智能体页面' },
              { id: 'ar-cas-pm-task-v1',       title: 'AR-CAS Pro PM 任务案例',  category: 'safety',   description: '用户在桥楼下达"AR-CAS Pro 菜单需要PM实现"任务, 经派发规则路由至 build_pm' },
              { id: 'agent-page-light-theme-v1', title: '智能体页强制浅色主题',   category: 'ui',       description: '/agent-team-config.html 使用 OpenBridge day 主题, 不从 localStorage 继承深色' },
              { id: 'bridge-uses-agent-llm-v1', title: '桥楼 LLM 统一走智能体团队', category: 'ai',      description: '数字孪生 Bridge Chat 通过 /api/v1/bridge-chat/send 使用智能体团队默认 LLM 配置 (localStorage 降级为 fallback)' },
              { id: 'marine-datacenter-v1',     title: '船载数据中心 AI 能耗管理',  category: 'energy',   description: '第一性原理重构: 4 视角(设备/设施/环境/流程) + IoT Hub(LoRa/MC-RFID/PLC-Agent) + Skill库 + Policy引擎 + 闭环 + Darwin 棘轮; 页面: /marine-datacenter.html' },
          ];
          
          const existing = load();
          let added = 0;
          HERITAGE.forEach(h => {
              if (!existing.find(x => x.id === h.id)) {
                  existing.push({
                      ...h,
                      fitness: 'pass',  // Heritage 默认锁定
                      lockedAt: new Date().toISOString(),
                      createdAt: new Date().toISOString(),
                      updatedAt: new Date().toISOString(),
                      generation: existing.length + 1,
                  });
                  added++;
              }
          });
          if (added > 0) {
              save(existing);
              console.log(`[Darwin] 🧬 Bootstrapped ${added} heritage evolutions`);
          }
      }
      
      bootstrap();
      
      window.Darwin = { record, list, locked, stats, onChange };
      console.log('[Darwin] 🧬 Ratchet evolution engine online. Current:', stats());
  })();
  
  ```
  
  ### 文件: `src/backend/agent_team_api.py`
  ```py
  # -*- coding: utf-8 -*-
  """
  Agent Team API Routes - 双团队管理 REST API
  
  提供构建团队 & 执行团队的状态查询、KPI 考核、
  任务分配、报告查询等端点。挂载至 FastAPI 的 router。
  """
  
  from __future__ import annotations
  
  from fastapi import APIRouter, HTTPException
  from pydantic import BaseModel
  from typing import Any, Dict, List, Optional
  
  router = APIRouter(prefix="/api/v1/agent-teams", tags=["Agent Teams"])
  
  
  # ---------------------------------------------------------------------------
  # 全局引用（在 main.py startup 时注入）
  # ---------------------------------------------------------------------------
  _build_team = None
  _execution_team = None
  _scheduler = None
  _evolution_engine = None
  
  
  def set_teams(build_team, execution_team, scheduler, evolution_engine=None):
      """在应用启动时由 main.py 调用，注入团队实例."""
      global _build_team, _execution_team, _scheduler, _evolution_engine
      _build_team = build_team
      _execution_team = execution_team
      _scheduler = scheduler
      _evolution_engine = evolution_engine
  
  
  # ---------------------------------------------------------------------------
  # Request / Response Models
  # ---------------------------------------------------------------------------
  
  class TaskAssignment(BaseModel):
      agent_id: str
      task: str
  
  class FeedbackSubmission(BaseModel):
      category: str = "optimization"
      severity: str = "medium"
      title: str
      detail: str
  
  
  # ---------------------------------------------------------------------------
  # Scheduler
  # ---------------------------------------------------------------------------
  
  @router.get("/scheduler/status")
  async def scheduler_status():
      if not _scheduler:
          raise HTTPException(503, "Scheduler not initialized")
      return _scheduler.get_status()
  
  
  @router.post("/scheduler/report")
  async def scheduler_generate_report():
      if not _scheduler:
          raise HTTPException(503, "Scheduler not initialized")
      return _scheduler.generate_report_now()
  
  
  @router.post("/scheduler/tick")
  async def scheduler_tick_once():
      """手动触发一次调度 tick (调试用)."""
      if not _scheduler:
          raise HTTPException(503, "Scheduler not initialized")
      return _scheduler.tick_once()
  
  
  # ---------------------------------------------------------------------------
  # Build Team
  # ---------------------------------------------------------------------------
  
  @router.get("/build/status")
  async def build_team_status():
      if not _build_team:
          raise HTTPException(503, "Build team not initialized")
      return _build_team.get_status()
  
  
  @router.get("/build/kpis")
  async def build_team_kpis():
      if not _build_team:
          raise HTTPException(503, "Build team not initialized")
      return _build_team.get_agent_kpis()
  
  
  @router.get("/build/agents/{agent_id}")
  async def build_agent_detail(agent_id: str):
      if not _build_team:
          raise HTTPException(503, "Build team not initialized")
      agent = _build_team.agents.get(agent_id)
      if not agent:
          raise HTTPException(404, f"Agent '{agent_id}' not found")
      return agent.to_dict()
  
  
  @router.post("/build/assign")
  async def build_assign_task(body: TaskAssignment):
      if not _build_team:
          raise HTTPException(503, "Build team not initialized")
      ok = _build_team.assign_task(body.agent_id, body.task)
      if not ok:
          raise HTTPException(404, f"Agent '{body.agent_id}' not found")
      return {"status": "assigned", "agent_id": body.agent_id, "task": body.task}
  
  
  @router.get("/build/reports")
  async def build_reports(limit: int = 10):
      if not _build_team:
          raise HTTPException(503, "Build team not initialized")
      reports = _build_team.hourly_reports[-limit:]
      return [r.to_dict() for r in reports]
  
  
  @router.get("/build/issues")
  async def build_issues():
      if not _build_team:
          raise HTTPException(503, "Build team not initialized")
      return _build_team.issue_backlog
  
  
  # ---------------------------------------------------------------------------
  # Execution Team
  # ---------------------------------------------------------------------------
  
  @router.get("/execution/status")
  async def execution_team_status():
      if not _execution_team:
          raise HTTPException(503, "Execution team not initialized")
      return _execution_team.get_status()
  
  
  @router.get("/execution/agents/{agent_id}")
  async def execution_agent_detail(agent_id: str):
      if not _execution_team:
          raise HTTPException(503, "Execution team not initialized")
      agent = _execution_team.agents.get(agent_id)
      if not agent:
          raise HTTPException(404, f"Agent '{agent_id}' not found")
      return agent.to_dict()
  
  
  @router.get("/execution/reports")
  async def execution_reports(limit: int = 10):
      if not _execution_team:
          raise HTTPException(503, "Execution team not initialized")
      reports = _execution_team.execution_reports[-limit:]
      return [r.to_dict() for r in reports]
  
  
  @router.get("/execution/feedback")
  async def execution_feedback():
      if not _execution_team:
          raise HTTPException(503, "Execution team not initialized")
      return [item.to_dict() for item in _execution_team.feedback_queue]
  
  
  @router.post("/execution/feedback")
  async def submit_feedback(body: FeedbackSubmission):
      if not _execution_team:
          raise HTTPException(503, "Execution team not initialized")
      item = _execution_team.submit_feedback(
          category=body.category,
          severity=body.severity,
          title=body.title,
          detail=body.detail,
      )
      return item.to_dict()
  
  
  # ---------------------------------------------------------------------------
  # Combined
  # ---------------------------------------------------------------------------
  
  @router.get("/overview")
  async def teams_overview():
      """一站式获取双团队全局概览."""
      result: Dict[str, Any] = {}
      if _build_team:
          bs = _build_team.get_status()
          result["build_team"] = {
              "health": bs["health"],
              "agent_count": bs["agent_count"],
              "metrics": bs["metrics"],
          }
      if _execution_team:
          es = _execution_team.get_status()
          result["execution_team"] = {
              "health": es["health"],
              "agent_count": es["agent_count"],
              "metrics": es["metrics"],
          }
      if _scheduler:
          result["scheduler"] = _scheduler.get_status()
      if _evolution_engine:
          result["evolution"] = _evolution_engine.get_status()
      return result
  
  
  # ---------------------------------------------------------------------------
  # System Evolution (自我演进引擎)
  # ---------------------------------------------------------------------------
  
  @router.get("/evolution/status")
  async def evolution_status():
      """获取自我演进引擎状态。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.get_status()
  
  
  @router.get("/evolution/summary")
  async def evolution_summary():
      """获取演进项汇总。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.get_evolution_summary()
  
  
  @router.get("/evolution/items")
  async def evolution_items(status: Optional[str] = None):
      """获取演进项列表，可按状态过滤。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.get_evolution_items(status=status)
  
  
  @router.get("/evolution/rules")
  async def evolution_rules():
      """获取审查规则列表。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return [r.to_dict() for r in _evolution_engine.audit_rules]
  
  
  @router.post("/evolution/audit")
  async def evolution_run_audit():
      """手动触发一次审查。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.run_full_audit()
  
  
  @router.post("/evolution/cycle")
  async def evolution_run_cycle():
      """运行完整演进周期（审查→派发→验证→关闭）。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.run_evolution_cycle()
  
  
  @router.post("/evolution/dispatch")
  async def evolution_dispatch():
      """派发所有待处理演进项给 Build 团队。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.dispatch_all_pending()
  
  
  @router.post("/evolution/verify")
  async def evolution_verify():
      """验证所有待验证项。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.verify_all_pending()
  
  
  @router.get("/evolution/items/{item_id}")
  async def evolution_item_detail(item_id: str):
      """获取单个演进项详情。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      item = _evolution_engine.evolution_items.get(item_id)
      if not item:
          raise HTTPException(404, f"Item '{item_id}' not found")
      return item.to_dict()
  
  
  @router.post("/evolution/items/{item_id}/progress")
  async def evolution_mark_progress(item_id: str):
      """标记演进项为进行中。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      ok = _evolution_engine.mark_in_progress(item_id)
      if not ok:
          raise HTTPException(404, f"Item '{item_id}' not found")
      return {"status": "ok", "item_id": item_id, "new_status": "in_progress"}
  
  
  @router.post("/evolution/items/{item_id}/complete")
  async def evolution_mark_complete(item_id: str):
      """标记演进项构建完成，进入待验证。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      ok = _evolution_engine.mark_build_complete(item_id)
      if not ok:
          raise HTTPException(404, f"Item '{item_id}' not found")
      return {"status": "ok", "item_id": item_id, "new_status": "verify_pending"}
  
  
  @router.post("/evolution/close-verified")
  async def evolution_close_verified():
      """关闭所有已验证通过的演进项。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      closed = _evolution_engine.close_verified()
      return {"closed": closed, "count": len(closed)}
  
  
  @router.get("/evolution/history")
  async def evolution_audit_history():
      """获取审查历史记录。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.get_audit_history()
  
  
  @router.get("/evolution/analytics")
  async def evolution_analytics():
      """获取演进分析数据 (域覆盖、严重度分布、趋势)。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      summary = _evolution_engine.get_evolution_summary()
      history = _evolution_engine.get_audit_history()
      status = _evolution_engine.get_status()
  
      return {
          "summary": summary,
          "history": history,
          "stats": status.get("stats", {}),
          "items_by_status": status.get("items_by_status", {}),
          "rules_count": status.get("audit_rules_count", 0),
      }
  
  
  # ---------------------------------------------------------------------------
  # Phase 3: 业界标准化改进 API
  # ---------------------------------------------------------------------------
  
  @router.get("/evolution/compliance-rating")
  async def evolution_compliance_rating():
      """获取 DNV CII 风格 A~E 合规评级。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.get_compliance_rating()
  
  
  @router.post("/evolution/compliance-rating/calculate")
  async def evolution_calculate_rating():
      """重新计算合规评级 (运行快速审查)。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.calculate_compliance_rating()
  
  
  @router.get("/evolution/checklist")
  async def evolution_checklist(level: Optional[str] = None):
      """获取 ClassNK 双层自查清单 (company/ship)。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.get_checklist(level=level)
  
  
  @router.get("/evolution/zones")
  async def evolution_zones():
      """获取所有合规区域。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.get_all_zones()
  
  
  @router.get("/evolution/zones/active")
  async def evolution_active_zones():
      """获取当前激活的合规区域。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return {
          "active_zones": _evolution_engine.get_active_zones(),
          "activated_rules": _evolution_engine.get_zone_activated_rules(),
          "vessel_position": _evolution_engine._vessel_position,
      }
  
  
  @router.post("/evolution/zones/update-position")
  async def evolution_update_position(lat: float = 0.0, lon: float = 0.0):
      """更新船舶位置，自动检测合规区域进入/离开。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.update_vessel_position(lat, lon)
  
  
  @router.get("/evolution/escalation")
  async def evolution_escalation():
      """获取失败升级状态 (DNV SEEMP Part III 风格)。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.get_escalation_status()
  
  
  @router.get("/evolution/trend")
  async def evolution_trend():
      """获取合规评级趋势分析。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.get_trend_analysis()
  
  
  @router.get("/evolution/monitoring")
  async def evolution_monitoring():
      """获取连续监控状态。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.get_monitoring_status()
  
  
  @router.get("/evolution/audit-trail")
  async def evolution_audit_trail(event_type: Optional[str] = None, limit: int = 50):
      """获取审计轨迹日志。"""
      if not _evolution_engine:
          raise HTTPException(404, "Evolution engine not registered")
      return _evolution_engine.get_audit_trail(event_type=event_type, limit=limit)
  
  
  __all__ = ["router", "set_teams"]
  
  ```
  
  ### 文件: `src/backend/channels/execution_team_manager.py`
  ```py
  # -*- coding: utf-8 -*-
  """
  Execution Agent Team Manager - 执行智能体团队管理器
  
  管理负责 AI Native 系统运行时功能最大化的智能体团队。
  团队通过 DeepSeek 驱动，实时运行系统核心功能，
  并将发现的问题和优化建议反馈给构建团队。
  
  角色分工：
    - Perception Agent   : 管理分布式感知融合 (L2)
    - Decision Agent     : 管理决策编排 (L3)
    - Navigation Agent   : 管理自主航行 / COLREGS 合规 (L3)
    - Energy Agent       : 管理能效优化 (跨层)
    - Feedback Agent     : 汇总执行数据，向构建团队提交优化需求
  """
  
  from __future__ import annotations
  
  import asyncio
  import logging
  import time
  from dataclasses import dataclass, field, asdict
  from datetime import datetime
  from enum import Enum
  from typing import Any, Dict, List, Optional
  
  from channels.marine_base import MarineChannel, ChannelPriority, ChannelStatus
  
  logger = logging.getLogger(__name__)
  
  
  # ---------------------------------------------------------------------------
  # Data Models
  # ---------------------------------------------------------------------------
  
  class ExecRole(str, Enum):
      PERCEPTION = "perception"
      DECISION = "decision"
      NAVIGATION = "navigation"
      ENERGY = "energy"
      FEEDBACK = "feedback"
  
  
  class ExecState(str, Enum):
      IDLE = "idle"
      MONITORING = "monitoring"
      OPTIMIZING = "optimizing"
      ALERTING = "alerting"
      ERROR = "error"
  
  
  @dataclass
  class ExecAgentMetrics:
      """执行 Agent 运行时指标."""
      cycles_run: int = 0
      anomalies_detected: int = 0
      optimizations_applied: int = 0
      feedback_sent: int = 0
      uptime_seconds: float = 0.0
      last_cycle_at: Optional[str] = None
  
  
  @dataclass
  class ExecAgent:
      """单个执行智能体."""
      id: str
      role: ExecRole
      name: str
      description: str
      llm_backend: str = "deepseek"
      state: ExecState = ExecState.IDLE
      target_channels: List[str] = field(default_factory=list)
      metrics: ExecAgentMetrics = field(default_factory=ExecAgentMetrics)
      config: Dict[str, Any] = field(default_factory=dict)
  
      def to_dict(self) -> Dict[str, Any]:
          return {**asdict(self), "state": self.state.value, "role": self.role.value}
  
  
  @dataclass
  class FeedbackItem:
      """执行团队向构建团队发送的反馈条目."""
      id: str
      source_agent: str
      category: str  # bug, optimization, feature_request, alert
      severity: str  # critical, high, medium, low
      title: str
      detail: str
      created_at: str
      resolved: bool = False
      resolution: Optional[str] = None
  
      def to_dict(self) -> Dict[str, Any]:
          return asdict(self)
  
  
  @dataclass
  class ExecutionReport:
      """执行团队的定期运行报告."""
      timestamp: str
      period_seconds: float
      perception_events: int = 0
      decisions_made: int = 0
      nav_corrections: int = 0
      energy_savings_pct: float = 0.0
      anomalies: int = 0
      feedback_items_sent: int = 0
      channel_health: Dict[str, str] = field(default_factory=dict)
      agents_summary: Dict[str, Any] = field(default_factory=dict)
  
      def to_dict(self) -> Dict[str, Any]:
          return asdict(self)
  
  
  # ---------------------------------------------------------------------------
  # Execution Team Manager Channel
  # ---------------------------------------------------------------------------
  
  class ExecutionTeamManagerChannel(MarineChannel):
      """执行智能体团队管理器 — 融入 AI Native CPS 架构."""
  
      name = "execution_team_manager"
      description = "执行智能体团队管理 (感知 → 决策 → 导航 → 能效 → 反馈)"
      version = "1.0.0"
      priority = ChannelPriority.P0  # 执行团队优先级最高
      dependencies: List[str] = [
          "distributed_perception_hub",
          "decision_orchestrator",
      ]
  
      # 默认运行间隔 (秒) — 执行团队运行更频繁
      SCHEDULE = {
          ExecRole.PERCEPTION: 5,    # 每 5 秒一次感知融合
          ExecRole.DECISION: 10,     # 每 10 秒一次决策评估
          ExecRole.NAVIGATION: 10,   # 每 10 秒一次航行校正
          ExecRole.ENERGY: 30,       # 每 30 秒一次能效评估
          ExecRole.FEEDBACK: 60,     # 每 60 秒汇总反馈
      }
  
      def __init__(self, config: Optional[Dict[str, Any]] = None):
          super().__init__()
          self.config = config or {}
          self._config = self.config
          self.llm_backend = self.config.get("llm_backend", "deepseek")
  
          self.agents: Dict[str, ExecAgent] = {}
          self._init_agents()
  
          self.feedback_queue: List[FeedbackItem] = []
          self.execution_reports: List[ExecutionReport] = []
          self.event_log: List[Dict[str, Any]] = []
          self._running = False
          self._start_time: Optional[float] = None
  
          # 全局运行时指标
          self.total_perception_events = 0
          self.total_decisions = 0
          self.total_nav_corrections = 0
          self.total_energy_savings_pct = 0.0
          self.total_anomalies = 0
          self._feedback_counter = 0
  
      # ── Agent 初始化 ──────────────────────────────────────────
  
      def _init_agents(self):
          definitions = [
              {
                  "id": "exec_perception",
                  "role": ExecRole.PERCEPTION,
                  "name": "Perception Fusion Agent",
                  "description": "持续融合 AIS/雷达/气象/WorldMonitor 数据，检测异常",
                  "target_channels": [
                      "distributed_perception_hub",
                      "nmea_channel",
                      "worldmonitor",
                  ],
              },
              {
                  "id": "exec_decision",
                  "role": ExecRole.DECISION,
                  "name": "Decision & Planning Agent",
                  "description": "实时评估态势，产出决策建议，驱动自主操控",
                  "target_channels": [
                      "decision_orchestrator",
                      "colregs_brain",
                  ],
              },
              {
                  "id": "exec_navigation",
                  "role": ExecRole.NAVIGATION,
                  "name": "Navigation Control Agent",
                  "description": "航行纠偏、COLREGS 合规检查、姿态控制",
                  "target_channels": [
                      "colregs_brain",
                      "wpc_attitude_control",
                  ],
              },
              {
                  "id": "exec_energy",
                  "role": ExecRole.ENERGY,
                  "name": "Energy Optimization Agent",
                  "description": "能效分析 (CII/EEXI)、航速优化、燃料节省",
                  "target_channels": [
                      "energy_efficiency",
                      "data_lakehouse",
                  ],
              },
              {
                  "id": "exec_feedback",
                  "role": ExecRole.FEEDBACK,
                  "name": "Feedback & Issue Agent",
                  "description": "汇总执行数据，向构建团队提交优化需求与 bug 报告",
                  "target_channels": [
                      "build_team_manager",
                      "event_store",
                  ],
              },
          ]
          for defn in definitions:
              agent = ExecAgent(
                  id=defn["id"],
                  role=defn["role"],
                  name=defn["name"],
                  description=defn["description"],
                  llm_backend=self.llm_backend,
                  target_channels=defn.get("target_channels", []),
              )
              self.agents[agent.id] = agent
  
      # ── MarineChannel 接口 ───────────────────────────────────
  
      def initialize(self) -> bool:
          self._initialized = True
          self._running = True
          self._start_time = time.monotonic()
          for agent in self.agents.values():
              agent.state = ExecState.MONITORING
          self._set_health(ChannelStatus.OK, "执行团队就绪，5 名 Agent 已上线")
          logger.info("⚡ Execution Team Manager initialized (%d agents)", len(self.agents))
          return True
  
      def shutdown(self) -> bool:
          self._running = False
          self._initialized = False
          for agent in self.agents.values():
              agent.state = ExecState.IDLE
          self._set_health(ChannelStatus.OFF, "Shutdown")
          return True
  
      # ── 调度 & 执行 ──────────────────────────────────────────
  
      def tick(self, now: Optional[datetime] = None, channel_registry: Optional[Dict] = None) -> Dict[str, Any]:
          """外部定时调用，驱动所有执行 Agent."""
          now = now or datetime.now()
          results: Dict[str, Any] = {}
          for agent in self.agents.values():
              if self._should_run(agent, now):
                  result = self._execute_agent_cycle(agent, now, channel_registry)
                  results[agent.id] = result
          return results
  
      def _should_run(self, agent: ExecAgent, now: datetime) -> bool:
          interval = self.SCHEDULE.get(agent.role, 30)
          if not agent.metrics.last_cycle_at:
              return True
          try:
              last = datetime.fromisoformat(agent.metrics.last_cycle_at)
              return (now - last).total_seconds() >= interval
          except (ValueError, TypeError):
              return True
  
      def _execute_agent_cycle(
          self, agent: ExecAgent, now: datetime,
          channel_registry: Optional[Dict] = None,
      ) -> Dict[str, Any]:
          agent.state = ExecState.MONITORING
          agent.metrics.last_cycle_at = now.isoformat()
          cycle_start = time.monotonic()
          result: Dict[str, Any] = {
              "agent": agent.id, "role": agent.role.value, "time": now.isoformat()
          }
  
          try:
              if agent.role == ExecRole.PERCEPTION:
                  result.update(self._run_perception(agent, now, channel_registry))
              elif agent.role == ExecRole.DECISION:
                  result.update(self._run_decision(agent, now, channel_registry))
              elif agent.role == ExecRole.NAVIGATION:
                  result.update(self._run_navigation(agent, now, channel_registry))
              elif agent.role == ExecRole.ENERGY:
                  result.update(self._run_energy(agent, now, channel_registry))
              elif agent.role == ExecRole.FEEDBACK:
                  result.update(self._run_feedback(agent, now))
  
              agent.metrics.cycles_run += 1
              agent.state = ExecState.MONITORING
          except Exception as exc:
              agent.state = ExecState.ERROR
              result["error"] = str(exc)
              logger.error("Exec agent %s cycle failed: %s", agent.id, exc)
  
          elapsed = time.monotonic() - cycle_start
          agent.metrics.uptime_seconds += elapsed
          self.event_log.append(result)
          return result
  
      # ── 各角色执行逻辑 ───────────────────────────────────────
  
      def _run_perception(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
          """感知 Agent：融合多源数据，检测异常."""
          # 如果有实际 channel registry，从中获取感知数据
          snapshot: Dict[str, Any] = {}
          if registry:
              hub = registry.get("distributed_perception_hub")
              if hub and hasattr(hub, "capture_system_snapshot"):
                  try:
                      snapshot = hub.capture_system_snapshot()
                  except Exception:
                      snapshot = {"error": "snapshot_unavailable"}
  
          # 基本感知事件模拟
          event_count = 3 + (agent.metrics.cycles_run % 5)
          anomaly = 1 if agent.metrics.cycles_run % 7 == 0 else 0
          self.total_perception_events += event_count
          self.total_anomalies += anomaly
  
          if anomaly:
              agent.state = ExecState.ALERTING
              agent.metrics.anomalies_detected += 1
              self._create_feedback(
                  agent.id, "alert", "high",
                  f"感知异常 #{agent.metrics.anomalies_detected}",
                  f"在第 {agent.metrics.cycles_run} 个感知周期检测到数据异常",
              )
  
          return {
              "action": "perception_fusion",
              "events_processed": event_count,
              "anomaly_detected": anomaly > 0,
              "snapshot_available": bool(snapshot),
          }
  
      def _run_decision(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
          """决策 Agent：态势评估 & 行动建议."""
          decision_quality = 0.85 + (agent.metrics.cycles_run % 10) * 0.01
          self.total_decisions += 1
  
          actions_recommended = [
              {"type": "course_adjustment", "priority": "medium", "detail": "建议微调航向 2°"},
              {"type": "speed_optimization", "priority": "low", "detail": "当前航速经济性良好"},
          ]
  
          if self.total_anomalies > 0 and agent.metrics.cycles_run % 5 == 0:
              actions_recommended.append({
                  "type": "emergency_assessment", "priority": "high",
                  "detail": "需要评估最近的感知异常对航行安全的影响",
              })
  
          return {
              "action": "decision_evaluation",
              "decision_quality": round(decision_quality, 3),
              "actions_recommended": len(actions_recommended),
              "details": actions_recommended,
          }
  
      def _run_navigation(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
          """航行 Agent：COLREGS 合规 & 纠偏."""
          correction_needed = agent.metrics.cycles_run % 4 == 0
          if correction_needed:
              self.total_nav_corrections += 1
              agent.metrics.optimizations_applied += 1
  
          colregs_status = "COMPLIANT"
          if agent.metrics.cycles_run % 20 == 0 and agent.metrics.cycles_run > 0:
              colregs_status = "REVIEW_NEEDED"
              self._create_feedback(
                  agent.id, "optimization", "medium",
                  "COLREGS 规则需要审查",
                  "建议构建团队更新 COLREGS 规则引擎以覆盖最新 IMO 规定",
              )
  
          return {
              "action": "navigation_control",
              "correction_applied": correction_needed,
              "colregs_status": colregs_status,
              "total_corrections": self.total_nav_corrections,
          }
  
      def _run_energy(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
          """能效 Agent：CII/EEXI 实时评估."""
          # 模拟能效节省 (最高 ~8%)
          savings = 2.5 + (agent.metrics.cycles_run % 12) * 0.5
          self.total_energy_savings_pct = savings
          agent.metrics.optimizations_applied += 1
  
          cii_rating = "A" if savings > 5 else "B" if savings > 3 else "C"
  
          if cii_rating == "C":
              self._create_feedback(
                  agent.id, "optimization", "high",
                  "CII 评级下降至 C",
                  "建议构建团队优化航速控制算法以改善 CII 评级",
              )
  
          return {
              "action": "energy_optimization",
              "savings_pct": round(savings, 2),
              "cii_rating": cii_rating,
              "cycle": agent.metrics.cycles_run,
          }
  
      def _run_feedback(self, agent: ExecAgent, now: datetime) -> Dict[str, Any]:
          """反馈 Agent：汇总 & 发送反馈给构建团队."""
          pending = list(self.feedback_queue)
          self.feedback_queue = []
          agent.metrics.feedback_sent += len(pending)
  
          return {
              "action": "feedback_delivery",
              "items_sent": len(pending),
              "items": [item.to_dict() for item in pending[:10]],  # 最多 10 条
              "total_feedback_sent": agent.metrics.feedback_sent,
          }
  
      # ── 反馈生成 ─────────────────────────────────────────────
  
      def _create_feedback(
          self, source: str, category: str, severity: str, title: str, detail: str,
      ):
          self._feedback_counter += 1
          item = FeedbackItem(
              id=f"FB-{self._feedback_counter:04d}",
              source_agent=source,
              category=category,
              severity=severity,
              title=title,
              detail=detail,
              created_at=datetime.now().isoformat(),
        
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
      has_limits = hasattr(wpc, "pitch_limit") or hasattr(wpc, "_pitch_limit_deg")
      if not has_limits:
          import inspect
          src = inspect.getsource(type(wpc))
          if "pitch_limit" not in src.lower() and "roll_limit" not in src.lower():
              return False, "WPC 姿态控制缺少纵摇/横摇限值参数"
      return True, "WPC 纵摇/横摇限值已配置"
  
  
  def _check_navigation_waypoint_system(channel) -> Tuple[bool, str]:
      """ECDIS: Voyage plan with waypoints should exist."""
      reg = get_default_registry()
      nav = reg.get("gps_navigation") or reg.get("navigation")
      if not nav:
          return False, "导航 Channel 未注册"
      has_wp = hasattr(nav, "waypoints") or hasattr(nav, "voyage_plan")
      if not has_wp:
          import inspect
          src = inspect.getsource(type(nav))
          if "waypoint" not in src.lower() and "voyage" not in src.lower():
              return False, "导航 Channel 缺少航路点/航次计划管理"
      return True, "航路点/航次计划已实现"
  
  
  def _check_dp_position_keeping(channel) -> Tuple[bool, str]:
      """DP (Dynamic Positioning): Position deviation threshold check."""
      reg = get_default_registry()
      dp = reg.get("dp_control") or reg.get("dynamic_positioning")
      if not dp:
          return False, "动力定位 Channel 未注册"
      has_thresh = hasattr(dp, "position_threshold") or hasattr(dp, "_max_deviation")
      if not has_thresh:
          import inspect
          src = inspect.getsource(type(dp))
          if "deviation" not in src.lower() and "threshold" not in src.lower():
              return False, "DP 缺少位置偏差阈值配置"
      return True, "DP 位置偏差阈值已配置"
  
  
  def _check_marpol_discharge_tracking(channel) -> Tuple[bool, str]:
      """MARPOL Annex I: OWS discharge monitoring."""
      reg = get_default_registry()
      env = reg.get("environmental_compliance") or reg.get("marpol_compliance")
      if
  ```
  
  
  ## 前序步骤的产出 (管线共享工作区)
  
  ### 步骤 01: pm_decompose.md
  
  # PM分解 — project_manager
  
  任务: 让货船以双体船为圆心动起来
  步骤: pm_decompose
  Agent: build_pm
  
  ---
  
  📋 任务: 3ae4ad68-b18
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
    让货船以双体船为圆心动起来
    给build团队的PM分配一个任务，让货船以双体船为圆心动起来
    
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
    src/backend/agents/agent_loop.py
    ... (共 790 个 src/ 文件)
    
    ```
    
    ### 文件: `src/frontend/js/darwin-ratchet.js`
    ```js
    /**
     * Darwin Ratchet — 达尔文棘轮演化机制
     * 系统只增不减地累积有益特性 (Irreversible Feature Accumulation)
     *
     * API:
     *   Darwin.record(item)  — 记录一次演化 (去重 by id)
     *   Darwin.list()        — 全部特性 (按时间排序)
     *   Darwin.locked()      — 已锁定特性
     *   Darwin.stats()       — 统计
     *   Darwin.onChange(cb)  — 变化订阅
     */
    (function() {
        const STORAGE_KEY = 'poseidonx.darwin.ratchet';
        const listeners = [];
        
        function load() {
            try {
                return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
            } catch (e) {
                return [];
            }
        }
        
        function save(items) {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
            listeners.forEach(cb => { try { cb(items); } catch (e) {} });
            // Broadcast cross-tab
            try {
                const bc = new BroadcastChannel('poseidonx-darwin');
                bc.postMessage({ type: 'update', items });
                bc.close();
            } catch (e) {}
        }
        
        function record(item) {
            if (!item || !item.id) return null;
            const items = load();
            const existing = items.find(x => x.id === item.id);
            const now = new Date().toISOString();
            if (existing) {
                // Update fitness only — core record is locked
                if (item.fitness && item.fitness !== existing.fitness) {
                    existing.fitness = item.fitness;
                    existing.updatedAt = now;
                    save(items);
                }
                return existing;
            }
            const record = {
                id: item.id,
                title: item.title || item.id,
                category: item.category || 'ui',
                description: item.description || '',
                fitness: item.fitness || 'pending',
                lockedAt: item.fitness === 'pass' ? now : null,
                createdAt: now,
                updatedAt: now,
                generation: items.length + 1,
            };
            items.push(record);
            save(items);
            console.log('[Darwin] 🧬 New evolution recorded:', record.title, '(Gen', record.generation + ')');
            return record;
        }
        
        function list() {
            return load().slice().sort((a, b) => (a.createdAt || '').localeCompare(b.createdAt || ''));
        }
        
        function locked() {
            return list().filter(x => x.fitness === 'pass');
        }
        
        function stats() {
            const items = load();
            const byCategory = {};
            items.forEach(i => { byCategory[i.category] = (byCategory[i.category] || 0) + 1; });
            return {
                total: items.length,
                locked: items.filter(i => i.fitness === 'pass').length,
                pending: items.filter(i => i.fitness === 'pending').length,
                rejected: items.filter(i => i.fitness === 'reject').length,
                byCategory,
                lastGeneration: items.length,
            };
        }
        
        function onChange(cb) {
            listeners.push(cb);
            // Cross-tab sync
            try {
                const bc = new BroadcastChannel('poseidonx-darwin');
                bc.onmessage = (e) => { if (e.data && e.data.type === 'update') cb(e.data.items); };
            } catch (e) {}
            return () => {
                const i = listeners.indexOf(cb);
                if (i >= 0) listeners.splice(i, 1);
            };
        }
        
        // 初始化: 一次性记录历史演化项 (只在首次运行时写入)
        function bootstrap() {
            const HERITAGE = [
                { id: 'day-mode-lighting-v1',    title: '日间模式亮化',             category: 'scene',   description: '环境光 + 半球光 1.6x 增强, 天空着色器日间蓝' },
                { id: 'sky-shader-day-v1',       title: '程序化日间天空',            category: 'scene',   description: '地平线浅蓝 → 天顶深蓝渐变 + 太阳光晕' },
                { id: 'cabin-interiors-v1',      title: '6 舱室 3D 内饰',           category: 'scene',   description: '驾驶台/机舱/ECR/货舱/船员舱/厨房 完整建模' },
                { id: 'cabin-split-screen-v1',   title: '分屏舱室信息系统',          category: 'ui',      description: '左 3D + 右系统信息, 进入舱室自动分屏' },
                { id: 'cabin-search-keywords-v1',title: '搜索框识别舱室中文名',      category: 'ui',      description: '输入驾驶台/动力舱/机舱自动进入' },
                { id: 'cabin-dropdown-menu-v1',  title: '舱室快速下拉菜单',          category: 'ui',      description: '右上角单按钮折叠展开式舱室导航' },
                { id: 'ar-cas-floating-v2',      title: 'AR-CAS Pro 可拖拽面板',    category: 'ui',      description: '独立浮动, 拖拽/折叠/调整大小, localStorage 持久化' },
                { id: 'ar-cas-enriched-v1',      title: 'AR-CAS Pro 丰富信息',      category: 'safety',  description: '本船状态 + 环境 + COLREGs 建议 + CPA/TCPA 分解' },
                { id: 'ais-iceberg-merge-v1',    title: 'AIS 列表聚合本地威胁',     category: 'data',    description: 'AIS 列表自动包含 3D 场景中的冰山和货船目标' },
                { id: 'ocean-shader-v1',         title: '海洋 GPU 着色器',          category: 'scene',   description: '多层正弦波 + 菲涅尔反射 + 次表面散射' },
                { id: 'icebergs-sss-v1',         title: '冰山次表面散射着色',        category: 'scene',   description: '5 座冰山, 菲涅尔边缘 + 水下蓝色渗透' },
                { id: 'weather-particles-v1',    title: '天气粒子系统',             category: 'scene',   description: '雨/雪/雾/海鸥/烟囱尾气' },
                { id: 'openbridge-hmi-v1',       title: 'OpenBridge HMI 主题',     category: 'ui',       description: 'DNV OpenBridge 2.4 四主题切换 (dusk/dawn/day/night)' },
                { id: 'colregs-brain-v1',        title: 'COLREGs Brain L3',        category: 'ai',       description: 'Rule 13/14/15/17 自动判断 + TCPA/CPA 威胁评估' },
                { id: 'wpc-attitude-v1',         title: '穿浪双体船姿态控制',       category: 'physics',  description: '水翼/T-Foil 主动姿态反馈 抑制 pitch/heave' },
                { id: 'iamsar-drift-v1',         title: 'MOB + IAMSAR 漂移',       category: 'safety',   description: '落水报警 + 风流联合搜索半径预测' },
                { id: 'darwin-ratchet-v1',       title: '达尔文棘轮机制',          category: 'ai',       description: '只增不减的演化累积引擎' },
                { id: 'bridge-task-dispatch-v1', title: '桥楼任务派发规则',        category: 'ai',       description: '桥楼聊天识别"给X团队的Y设置任务"指令并 POST 到 /agent-config/teams/{team}/tasks, 自动同步至智能体页面' },
                { id: 'ar-cas-pm-task-v1',       title: 'AR-CAS Pro PM 任务案例',  category: 'safety',   description: '用户在桥楼下达"AR-CAS Pro 菜单需要PM实现"任务, 经派发规则路由至 build_pm' },
                { id: 'agent-page-light-theme-v1', title: '智能体页强制浅色主题',   category: 'ui',       description: '/agent-team-config.html 使用 OpenBridge day 主题, 不从 localStorage 继承深色' },
                { id: 'bridge-uses-agent-llm-v1', title: '桥楼 LLM 统一走智能体团队', category: 'ai',      description: '数字孪生 Bridge Chat 通过 /api/v1/bridge-chat/send 使用智能体团队默认 LLM 配置 (localStorage 降级为 fallback)' },
                { id: 'marine-datacenter-v1',     title: '船载数据中心 AI 能耗管理',  category: 'energy',   description: '第一性原理重构: 4 视角(设备/设施/环境/流程) + IoT Hub(LoRa/MC-RFID/PLC-Agent) + Skill库 + Policy引擎 + 闭环 + Darwin 棘轮; 页面: /marine-datacenter.html' },
            ];
            
            const existing = load();
            let added = 0;
            HERITAGE.forEach(h => {
                if (!existing.find(x => x.id === h.id)) {
                    existing.push({
                        ...h,
                        fitness: 'pass',  // Heritage 默认锁定
                        lockedAt: new Date().toISOString(),
                        createdAt: new Date().toISOString(),
                        updatedAt: new Date().toISOString(),
                        generation: existing.length + 1,
                    });
                    added++;
                }
            });
            if (added > 0) {
                save(existing);
                console.log(`[Darwin] 🧬 Bootstrapped ${added} heritage evolutions`);
            }
        }
        
        bootstrap();
        
        window.Darwin = { record, list, locked, stats, onChange };
        console.log('[Darwin] 🧬 Ratchet evolution engine online. Current:', stats());
    })();
    
    ```
    
    ### 文件: `src/backend/agent_team_api.py`
    ```py
    # -*- coding: utf-8 -*-
    """
    Agent Team API Routes - 双团队管理 REST API
    
    提供构建团队 & 执行团队的状态查询、KPI 考核、
    任务分配、报告查询等端点。挂载至 FastAPI 的 router。
    """
    
    from __future__ import annotations
    
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel
    from typing import Any, Dict, List, Optional
    
    router = APIRouter(prefix="/api/v1/agent-teams", tags=["Agent Teams"])
    
    
    # ---------------------------------------------------------------------------
    # 全局引用（在 main.py startup 时注入）
    # ---------------------------------------------------------------------------
    _build_team = None
    _execution_team = None
    _scheduler = None
    _evolution_engine = None
    
    
    def set_teams(build_team, execution_team, scheduler, evolution_engine=None):
        """在应用启动时由 main.py 调用，注入团队实例."""
        global _build_team, _execution_team, _scheduler, _evolution_engine
        _build_team = build_team
        _execution_team = execution_team
        _scheduler = scheduler
        _evolution_engine = evolution_engine
    
    
    # ---------------------------------------------------------------------------
    # Request / Response Models
    # ---------------------------------------------------------------------------
    
    class TaskAssignment(BaseModel):
        agent_id: str
        task: str
    
    class FeedbackSubmission(BaseModel):
        category: str = "optimization"
        severity: str = "medium"
        title: str
        detail: str
    
    
    # ---------------------------------------------------------------------------
    # Scheduler
    # ---------------------------------------------------------------------------
    
    @router.get("/scheduler/status")
    async def scheduler_status():
        if not _scheduler:
            raise HTTPException(503, "Scheduler not initialized")
        return _scheduler.get_status()
    
    
    @router.post("/scheduler/report")
    async def scheduler_generate_report():
        if not _scheduler:
            raise HTTPException(503, "Scheduler not initialized")
        return _scheduler.generate_report_now()
    
    
    @router.post("/scheduler/tick")
    async def scheduler_tick_once():
        """手动触发一次调度 tick (调试用)."""
        if not _scheduler:
            raise HTTPException(503, "Scheduler not initialized")
        return _scheduler.tick_once()
    
    
    # ---------------------------------------------------------------------------
    # Build Team
    # ---------------------------------------------------------------------------
    
    @router.get("/build/status")
    async def build_team_status():
        if not _build_team:
            raise HTTPException(503, "Build team not initialized")
        return _build_team.get_status()
    
    
    @router.get("/build/kpis")
    async def build_team_kpis():
        if not _build_team:
            raise HTTPException(503, "Build team not initialized")
        return _build_team.get_agent_kpis()
    
    
    @router.get("/build/agents/{agent_id}")
    async def build_agent_detail(agent_id: str):
        if not _build_team:
            raise HTTPException(503, "Build team not initialized")
        agent = _build_team.agents.get(agent_id)
        if not agent:
            raise HTTPException(404, f"Agent '{agent_id}' not found")
        return agent.to_dict()
    
    
    @router.post("/build/assign")
    async def build_assign_task(body: TaskAssignment):
        if not _build_team:
            raise HTTPException(503, "Build team not initialized")
        ok = _build_team.assign_task(body.agent_id, body.task)
        if not ok:
            raise HTTPException(404, f"Agent '{body.agent_id}' not found")
        return {"status": "assigned", "agent_id": body.agent_id, "task": body.task}
    
    
    @router.get("/build/reports")
    async def build_reports(limit: int = 10):
        if not _build_team:
            raise HTTPException(503, "Build team not initialized")
        reports = _build_team.hourly_reports[-limit:]
        return [r.to_dict() for r in reports]
    
    
    @router.get("/build/issues")
    async def build_issues():
        if not _build_team:
            raise HTTPException(503, "Build team not initialized")
        return _build_team.issue_backlog
    
    
    # ---------------------------------------------------------------------------
    # Execution Team
    # ---------------------------------------------------------------------------
    
    @router.get("/execution/status")
    async def execution_team_status():
        if not _execution_team:
            raise HTTPException(503, "Execution team not initialized")
        return _execution_team.get_status()
    
    
    @router.get("/execution/agents/{agent_id}")
    async def execution_agent_detail(agent_id: str):
        if not _execution_team:
            raise HTTPException(503, "Execution team not initialized")
        agent = _execution_team.agents.get(agent_id)
        if not agent:
            raise HTTPException(404, f"Agent '{agent_id}' not found")
        return agent.to_dict()
    
    
    @router.get("/execution/reports")
    async def execution_reports(limit: int = 10):
        if not _execution_team:
            raise HTTPException(503, "Execution team not initialized")
        reports = _execution_team.execution_reports[-limit:]
        return [r.to_dict() for r in reports]
    
    
    @router.get("/execution/feedback")
    async def execution_feedback():
        if not _execution_team:
            raise HTTPException(503, "Execution team not initialized")
        return [item.to_dict() for item in _execution_team.feedback_queue]
    
    
    @router.post("/execution/feedback")
    async def submit_feedback(body: FeedbackSubmission):
        if not _execution_team:
            raise HTTPException(503, "Execution team not initialized")
        item = _execution_team.submit_feedback(
            category=body.category,
            severity=body.severity,
            title=body.title,
            detail=body.detail,
        )
        return item.to_dict()
    
    
    # ---------------------------------------------------------------------------
    # Combined
    # ---------------------------------------------------------------------------
    
    @router.get("/overview")
    async def teams_overview():
        """一站式获取双团队全局概览."""
        result: Dict[str, Any] = {}
        if _build_team:
            bs = _build_team.get_status()
            result["build_team"] = {
                "health": bs["health"],
                "agent_count": bs["agent_count"],
                "metrics": bs["metrics"],
            }
        if _execution_team:
            es = _execution_team.get_status()
            result["execution_team"] = {
                "health": es["health"],
                "agent_count": es["agent_count"],
                "metrics": es["metrics"],
            }
        if _scheduler:
            result["scheduler"] = _scheduler.get_status()
        if _evolution_engine:
            result["evolution"] = _evolution_engine.get_status()
        return result
    
    
    # ---------------------------------------------------------------------------
    # System Evolution (自我演进引擎)
    # ---------------------------------------------------------------------------
    
    @router.get("/evolution/status")
    async def evolution_status():
        """获取自我演进引擎状态。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_status()
    
    
    @router.get("/evolution/summary")
    async def evolution_summary():
        """获取演进项汇总。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_evolution_summary()
    
    
    @router.get("/evolution/items")
    async def evolution_items(status: Optional[str] = None):
        """获取演进项列表，可按状态过滤。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_evolution_items(status=status)
    
    
    @router.get("/evolution/rules")
    async def evolution_rules():
        """获取审查规则列表。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return [r.to_dict() for r in _evolution_engine.audit_rules]
    
    
    @router.post("/evolution/audit")
    async def evolution_run_audit():
        """手动触发一次审查。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.run_full_audit()
    
    
    @router.post("/evolution/cycle")
    async def evolution_run_cycle():
        """运行完整演进周期（审查→派发→验证→关闭）。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.run_evolution_cycle()
    
    
    @router.post("/evolution/dispatch")
    async def evolution_dispatch():
        """派发所有待处理演进项给 Build 团队。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.dispatch_all_pending()
    
    
    @router.post("/evolution/verify")
    async def evolution_verify():
        """验证所有待验证项。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.verify_all_pending()
    
    
    @router.get("/evolution/items/{item_id}")
    async def evolution_item_detail(item_id: str):
        """获取单个演进项详情。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        item = _evolution_engine.evolution_items.get(item_id)
        if not item:
            raise HTTPException(404, f"Item '{item_id}' not found")
        return item.to_dict()
    
    
    @router.post("/evolution/items/{item_id}/progress")
    async def evolution_mark_progress(item_id: str):
        """标记演进项为进行中。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        ok = _evolution_engine.mark_in_progress(item_id)
        if not ok:
            raise HTTPException(404, f"Item '{item_id}' not found")
        return {"status": "ok", "item_id": item_id, "new_status": "in_progress"}
    
    
    @router.post("/evolution/items/{item_id}/complete")
    async def evolution_mark_complete(item_id: str):
        """标记演进项构建完成，进入待验证。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        ok = _evolution_engine.mark_build_complete(item_id)
        if not ok:
            raise HTTPException(404, f"Item '{item_id}' not found")
        return {"status": "ok", "item_id": item_id, "new_status": "verify_pending"}
    
    
    @router.post("/evolution/close-verified")
    async def evolution_close_verified():
        """关闭所有已验证通过的演进项。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        closed = _evolution_engine.close_verified()
        return {"closed": closed, "count": len(closed)}
    
    
    @router.get("/evolution/history")
    async def evolution_audit_history():
        """获取审查历史记录。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_audit_history()
    
    
    @router.get("/evolution/analytics")
    async def evolution_analytics():
        """获取演进分析数据 (域覆盖、严重度分布、趋势)。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        summary = _evolution_engine.get_evolution_summary()
        history = _evolution_engine.get_audit_history()
        status = _evolution_engine.get_status()
    
        return {
            "summary": summary,
            "history": history,
            "stats": status.get("stats", {}),
            "items_by_status": status.get("items_by_status", {}),
            "rules_count": status.get("audit_rules_count", 0),
        }
    
    
    # ---------------------------------------------------------------------------
    # Phase 3: 业界标准化改进 API
    # ---------------------------------------------------------------------------
    
    @router.get("/evolution/compliance-rating")
    async def evolution_compliance_rating():
        """获取 DNV CII 风格 A~E 合规评级。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_compliance_rating()
    
    
    @router.post("/evolution/compliance-rating/calculate")
    async def evolution_calculate_rating():
        """重新计算合规评级 (运行快速审查)。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.calculate_compliance_rating()
    
    
    @router.get("/evolution/checklist")
    async def evolution_checklist(level: Optional[str] = None):
        """获取 ClassNK 双层自查清单 (company/ship)。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_checklist(level=level)
    
    
    @router.get("/evolution/zones")
    async def evolution_zones():
        """获取所有合规区域。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_all_zones()
    
    
    @router.get("/evolution/zones/active")
    async def evolution_active_zones():
        """获取当前激活的合规区域。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return {
            "active_zones": _evolution_engine.get_active_zones(),
            "activated_rules": _evolution_engine.get_zone_activated_rules(),
            "vessel_position": _evolution_engine._vessel_position,
        }
    
    
    @router.post("/evolution/zones/update-position")
    async def evolution_update_position(lat: float = 0.0, lon: float = 0.0):
        """更新船舶位置，自动检测合规区域进入/离开。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.update_vessel_position(lat, lon)
    
    
    @router.get("/evolution/escalation")
    async def evolution_escalation():
        """获取失败升级状态 (DNV SEEMP Part III 风格)。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_escalation_status()
    
    
    @router.get("/evolution/trend")
    async def evolution_trend():
        """获取合规评级趋势分析。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_trend_analysis()
    
    
    @router.get("/evolution/monitoring")
    async def evolution_monitoring():
        """获取连续监控状态。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_monitoring_status()
    
    
    @router.get("/evolution/audit-trail")
    async def evolution_audit_trail(event_type: Optional[str] = None, limit: int = 50):
        """获取审计轨迹日志。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_audit_trail(event_type=event_type, limit=limit)
    
    
    __all__ = ["router", "set_teams"]
    
    ```
    
    ### 文件: `src/backend/channels/execution_team_manager.py`
    ```py
    # -*- coding: utf-8 -*-
    """
    Execution Agent Team Manager - 执行智能体团队管理器
    
    管理负责 AI Native 系统运行时功能最大化的智能体团队。
    团队通过 DeepSeek 驱动，实时运行系统核心功能，
    并将发现的问题和优化建议反馈给构建团队。
    
    角色分工：
      - Perception Agent   : 管理分布式感知融合 (L2)
      - Decision Agent     : 管理决策编排 (L3)
      - Navigation Agent   : 管理自主航行 / COLREGS 合规 (L3)
      - Energy Agent       : 管理能效优化 (跨层)
      - Feedback Agent     : 汇总执行数据，向构建团队提交优化需求
    """
    
    from __future__ import annotations
    
    import asyncio
    import logging
    import time
    from dataclasses import dataclass, field, asdict
    from datetime import datetime
    from enum import Enum
    from typing import Any, Dict, List, Optional
    
    from channels.marine_base import MarineChannel, ChannelPriority, ChannelStatus
    
    logger = logging.getLogger(__name__)
    
    
    # ---------------------------------------------------------------------------
    # Data Models
    # ---------------------------------------------------------------------------
    
    class ExecRole(str, Enum):
        PERCEPTION = "perception"
        DECISION = "decision"
        NAVIGATION = "navigation"
        ENERGY = "energy"
        FEEDBACK = "feedback"
    
    
    class ExecState(str, Enum):
        IDLE = "idle"
        MONITORING = "monitoring"
        OPTIMIZING = "optimizing"
        ALERTING = "alerting"
        ERROR = "error"
    
    
    @dataclass
    class ExecAgentMetrics:
        """执行 Agent 运行时指标."""
        cycles_run: int = 0
        anomalies_detected: int = 0
        optimizations_applied: int = 0
        feedback_sent: int = 0
        uptime_seconds: float = 0.0
        last_cycle_at: Optional[str] = None
    
    
    @dataclass
    class ExecAgent:
        """单个执行智能体."""
        id: str
        role: ExecRole
        name: str
        description: str
        llm_backend: str = "deepseek"
        state: ExecState = ExecState.IDLE
        target_channels: List[str] = field(default_factory=list)
        metrics: ExecAgentMetrics = field(default_factory=ExecAgentMetrics)
        config: Dict[str, Any] = field(default_factory=dict)
    
        def to_dict(self) -> Dict[str, Any]:
            return {**asdict(self), "state": self.state.value, "role": self.role.value}
    
    
    @dataclass
    class FeedbackItem:
        """执行团队向构建团队发送的反馈条目."""
        id: str
        source_agent: str
        category: str  # bug, optimization, feature_request, alert
        severity: str  # critical, high, medium, low
        title: str
        detail: str
        created_at: str
        resolved: bool = False
        resolution: Optional[str] = None
    
        def to_dict(self) -> Dict[str, Any]:
            return asdict(self)
    
    
    @dataclass
    class ExecutionReport:
        """执行团队的定期运行报告."""
        timestamp: str
        period_seconds: float
        perception_events: int = 0
        decisions_made: int = 0
        nav_corrections: int = 0
        energy_savings_pct: float = 0.0
        anomalies: int = 0
        feedback_items_sent: int = 0
        channel_health: Dict[str, str] = field(default_factory=dict)
        agents_summary: Dict[str, Any] = field(default_factory=dict)
    
        def to_dict(self) -> Dict[str, Any]:
            return asdict(self)
    
    
    # ---------------------------------------------------------------------------
    # Execution Team Manager Channel
    # ---------------------------------------------------------------------------
    
    class ExecutionTeamManagerChannel(MarineChannel):
        """执行智能体团队管理器 — 融入 AI Native CPS 架构."""
    
        name = "execution_team_manager"
        description = "执行智能体团队管理 (感知 → 决策 → 导航 → 能效 → 反馈)"
        version = "1.0.0"
        priority = ChannelPriority.P0  # 执行团队优先级最高
        dependencies: List[str] = [
            "distributed_perception_hub",
            "decision_orchestrator",
        ]
    
        # 默认运行间隔 (秒) — 执行团队运行更频繁
        SCHEDULE = {
            ExecRole.PERCEPTION: 5,    # 每 5 秒一次感知融合
            ExecRole.DECISION: 10,     # 每 10 秒一次决策评估
            ExecRole.NAVIGATION: 10,   # 每 10 秒一次航行校正
            ExecRole.ENERGY: 30,       # 每 30 秒一次能效评估
            ExecRole.FEEDBACK: 60,     # 每 60 秒汇总反馈
        }
    
        def __init__(self, config: Optional[Dict[str, Any]] = None):
            super().__init__()
            self.config = config or {}
            self._config = self.config
            self.llm_backend = self.config.get("llm_backend", "deepseek")
    
            self.agents: Dict[str, ExecAgent] = {}
            self._init_agents()
    
            self.feedback_queue: List[FeedbackItem] = []
            self.execution_reports: List[ExecutionReport] = []
            self.event_log: List[Dict[str, Any]] = []
            self._running = False
            self._start_time: Optional[float] = None
    
            # 全局运行时指标
            self.total_perception_events = 0
            self.total_decisions = 0
            self.total_nav_corrections = 0
            self.total_energy_savings_pct = 0.0
            self.total_anomalies = 0
            self._feedback_counter = 0
    
        # ── Agent 初始化 ──────────────────────────────────────────
    
        def _init_agents(self):
            definitions = [
                {
                    "id": "exec_perception",
                    "role": ExecRole.PERCEPTION,
                    "name": "Perception Fusion Agent",
                    "description": "持续融合 AIS/雷达/气象/WorldMonitor 数据，检测异常",
                    "target_channels": [
                        "distributed_perception_hub",
                        "nmea_channel",
                        "worldmonitor",
                    ],
                },
                {
                    "id": "exec_decision",
                    "role": ExecRole.DECISION,
                    "name": "Decision & Planning Agent",
                    "description": "实时评估态势，产出决策建议，驱动自主操控",
                    "target_channels": [
                        "decision_orchestrator",
                        "colregs_brain",
                    ],
                },
                {
                    "id": "exec_navigation",
                    "role": ExecRole.NAVIGATION,
                    "name": "Navigation Control Agent",
                    "description": "航行纠偏、COLREGS 合规检查、姿态控制",
                    "target_channels": [
                        "colregs_brain",
                        "wpc_attitude_control",
                    ],
                },
                {
                    "id": "exec_energy",
                    "role": ExecRole.ENERGY,
                    "name": "Energy Optimization Agent",
                    "description": "能效分析 (CII/EEXI)、航速优化、燃料节省",
                    "target_channels": [
                        "energy_efficiency",
                        "data_lakehouse",
                    ],
                },
                {
                    "id": "exec_feedback",
                    "role": ExecRole.FEEDBACK,
                    "name": "Feedback & Issue Agent",
                    "description": "汇总执行数据，向构建团队提交优化需求与 bug 报告",
                    "target_channels": [
                        "build_team_manager",
                        "event_store",
                    ],
                },
            ]
            for defn in definitions:
                agent = ExecAgent(
                    id=defn["id"],
                    role=defn["role"],
                    name=defn["name"],
                    description=defn["description"],
                    llm_backend=self.llm_backend,
                    target_channels=defn.get("target_channels", []),
                )
                self.agents[agent.id] = agent
    
        # ── MarineChannel 接口 ───────────────────────────────────
    
        def initialize(self) -> bool:
            self._initialized = True
            self._running = True
            self._start_time = time.monotonic()
            for agent in self.agents.values():
                agent.state = ExecState.MONITORING
            self._set_health(ChannelStatus.OK, "执行团队就绪，5 名 Agent 已上线")
            logger.info("⚡ Execution Team Manager initialized (%d agents)", len(self.agents))
            return True
    
        def shutdown(self) -> bool:
            self._running = False
            self._initialized = False
            for agent in self.agents.values():
                agent.state = ExecState.IDLE
            self._set_health(ChannelStatus.OFF, "Shutdown")
            return True
    
        # ── 调度 & 执行 ──────────────────────────────────────────
    
        def tick(self, now: Optional[datetime] = None, channel_registry: Optional[Dict] = None) -> Dict[str, Any]:
            """外部定时调用，驱动所有执行 Agent."""
            now = now or datetime.now()
            results: Dict[str, Any] = {}
            for agent in self.agents.values():
                if self._should_run(agent, now):
                    result = self._execute_agent_cycle(agent, now, channel_registry)
                    results[agent.id] = result
            return results
    
        def _should_run(self, agent: ExecAgent, now: datetime) -> bool:
            interval = self.SCHEDULE.get(agent.role, 30)
            if not agent.metrics.last_cycle_at:
                return True
            try:
                last = datetime.fromisoformat(agent.metrics.last_cycle_at)
                return (now - last).total_seconds() >= interval
            except (ValueError, TypeError):
                return True
    
        def _execute_agent_cycle(
            self, agent: ExecAgent, now: datetime,
            channel_registry: Optional[Dict] = None,
        ) -> Dict[str, Any]:
            agent.state = ExecState.MONITORING
            agent.metrics.last_cycle_at = now.isoformat()
            cycle_start = time.monotonic()
            result: Dict[str, Any] = {
                "agent": agent.id, "role": agent.role.value, "time": now.isoformat()
            }
    
            try:
                if agent.role == ExecRole.PERCEPTION:
                    result.update(self._run_perception(agent, now, channel_registry))
                elif agent.role == ExecRole.DECISION:
                    result.update(self._run_decision(agent, now, channel_registry))
                elif agent.role == ExecRole.NAVIGATION:
                    result.update(self._run_navigation(agent, now, channel_registry))
                elif agent.role == ExecRole.ENERGY:
                    result.update(self._run_energy(agent, now, channel_registry))
                elif agent.role == ExecRole.FEEDBACK:
                    result.update(self._run_feedback(agent, now))
    
                agent.metrics.cycles_run += 1
                agent.state = ExecState.MONITORING
            except Exception as exc:
                agent.state = ExecState.ERROR
                result["error"] = str(exc)
                logger.error("Exec agent %s cycle failed: %s", agent.id, exc)
    
            elapsed = time.monotonic() - cycle_start
            agent.metrics.uptime_seconds += elapsed
            self.event_log.append(result)
            return result
    
        # ── 各角色执行逻辑 ───────────────────────────────────────
    
        def _run_perception(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
            """感知 Agent：融合多源数据，检测异常."""
            # 如果有实际 channel registry，从中获取感知数据
            snapshot: Dict[str, Any] = {}
            if registry:
                hub = registry.get("distributed_perception_hub")
                if hub and hasattr(hub, "capture_system_snapshot"):
                    try:
                        snapshot = hub.capture_system_snapshot()
                    except Exception:
                        snapshot = {"error": "snapshot_unavailable"}
    
            # 基本感知事件模拟
            event_count = 3 + (agent.metrics.cycles_run % 5)
            anomaly = 1 if agent.metrics.cycles_run % 7 == 0 else 0
            self.total_perception_events += event_count
            self.total_anomalies += anomaly
    
            if anomaly:
                agent.state = ExecState.ALERTING
                agent.metrics.anomalies_detected += 1
                self._create_feedback(
                    agent.id, "alert", "high",
                    f"感知异常 #{agent.metrics.anomalies_detected}",
                    f"在第 {agent.metrics.cycles_run} 个感知周期检测到数据异常",
                )
    
            return {
                "action": "perception_fusion",
                "events_processed": event_count,
                "anomaly_detected": anomaly > 0,
                "snapshot_available": bool(snapshot),
            }
    
        def _run_decision(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
            """决策 Agent：态势评估 & 行动建议."""
            decision_quality = 0.85 + (agent.metrics.cycles_run % 10) * 0.01
            self.total_decisions += 1
    
            actions_recommended = [
                {"type": "course_adjustment", "priority": "medium", "detail": "建议微调航向 2°"},
                {"type": "speed_optimization", "priority": "low", "detail": "当前航速经济性良好"},
            ]
    
            if self.total_anomalies > 0 and agent.metrics.cycles_run % 5 == 0:
                actions_recommended.append({
                    "type": "emergency_assessment", "priority": "high",
                    "detail": "需要评估最近的感知异常对航行安全的影响",
                })
    
            return {
                "action": "decision_evaluation",
                "decision_quality": round(decision_quality, 3),
                "actions_recommended": len(actions_recommended),
                "details": actions_recommended,
            }
    
        def _run_navigation(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
            """航行 Agent：COLREGS 合规 & 纠偏."""
            correction_needed = agent.metrics.cycles_run % 4 == 0
            if correction_needed:
                self.total_nav_corrections += 1
                agent.metrics.optimizations_applied += 1
    
            colregs_status = "COMPLIANT"
            if agent.metrics.cycles_run % 20 == 0 and agent.metrics.cycles_run > 0:
                colregs_status = "REVIEW_NEEDED"
                self._create_feedback(
                    agent.id, "optimization", "medium",
                    "COLREGS 规则需要审查",
                    "建议构建团队更新 COLREGS 规则引擎以覆盖最新 IMO 规定",
                )
    
            return {
                "action": "navigation_control",
                "correction_applied": correction_needed,
                "colregs_status": colregs_status,
                "total_corrections": self.total_nav_corrections,
            }
    
        def _run_energy(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
            """能效 Agent：CII/EEXI 实时评估."""
            # 模拟能效节省 (最高 ~8%)
            savings = 2.5 + (agent.metrics.cycles_run % 12) * 0.5
            self.total_energy_savings_pct = savings
            agent.metrics.optimizations_applied += 1
    
            cii_rating = "A" if savings > 5 else "B" if savings > 3 else "C"
    
            if cii_rating == "C":
                self._create_feedback(
                    agent.id, "optimization", "high",
                    "CII 评级下降至 C",
                    "建议构建团队优化航速控制算法以改善 CII 评级",
                )
    
            return {
                "action": "energy_optimization",
                "savings_pct": round(savings, 2),
                "cii_rating": cii_rating,
                "cycle": agent.metrics.cycles_run,
            }
    
        def _run_feedback(self, agent: ExecAgent, now: datetime) -> Dict[str, Any]:
            """反馈 Agent：汇总 & 发送反馈给构建团队."""
            pending = list(self.feedback_queue)
            self.feedback_queue = []
            agent.metrics.feedback_sent += len(pending)
    
            return {
                "action": "feedback_delivery",
                "items_sent": len(pending),
                "items": [item.to_dict() for item in pending[:10]],  # 最多 10 条
                "total_feedback_sent": agent.metrics.feedback_sent,
            }
    
        # ── 反馈生成 ─────────────────────────────────────────────
    
        def _create_feedback(
            self, source: str, category: str, severity: str, title: str, detail: str,
        ):
            self._feedback_counter += 1
            item = FeedbackItem(
                id=f"FB-{self._feedback_counter:04d}",
                source_agent=source,
                category=category,
                severity=severity,
                title=title,
                detail=detail,
                created_at=datetime.now().isoformat(),
          
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
     
  ### 步骤 02: research.md
  
  # 研究分析 — researcher
  
  任务: 让货船以双体船为圆心动起来
  步骤: research
  Agent: build_researcher
  
  ---
  
  📋 任务: 3ae4ad68-b18
  🤖 Agent: Researcher (researcher)
  📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  🔧 执行方式: DeepSeek API (直连)
  ⏱️ 超时: 1200s
  ────────────────────────────────────────────────────────────
  📝 提示词:
    你是 PoseidonX 系统的 Researcher (researcher)。
    请执行以下开发任务:
    
    你是技术研究员。请对以下任务进行技术调研:
    
    ## 任务
    让货船以双体船为圆心动起来
    给build团队的PM分配一个任务，让货船以双体船为圆心动起来
    
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
    src/backend/agents/agent_loop.py
    ... (共 790 个 src/ 文件)
    
    ```
    
    ### 文件: `src/frontend/js/darwin-ratchet.js`
    ```js
    /**
     * Darwin Ratchet — 达尔文棘轮演化机制
     * 系统只增不减地累积有益特性 (Irreversible Feature Accumulation)
     *
     * API:
     *   Darwin.record(item)  — 记录一次演化 (去重 by id)
     *   Darwin.list()        — 全部特性 (按时间排序)
     *   Darwin.locked()      — 已锁定特性
     *   Darwin.stats()       — 统计
     *   Darwin.onChange(cb)  — 变化订阅
     */
    (function() {
        const STORAGE_KEY = 'poseidonx.darwin.ratchet';
        const listeners = [];
        
        function load() {
            try {
                return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
            } catch (e) {
                return [];
            }
        }
        
        function save(items) {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
            listeners.forEach(cb => { try { cb(items); } catch (e) {} });
            // Broadcast cross-tab
            try {
                const bc = new BroadcastChannel('poseidonx-darwin');
                bc.postMessage({ type: 'update', items });
                bc.close();
            } catch (e) {}
        }
        
        function record(item) {
            if (!item || !item.id) return null;
            const items = load();
            const existing = items.find(x => x.id === item.id);
            const now = new Date().toISOString();
            if (existing) {
                // Update fitness only — core record is locked
                if (item.fitness && item.fitness !== existing.fitness) {
                    existing.fitness = item.fitness;
                    existing.updatedAt = now;
                    save(items);
                }
                return existing;
            }
            const record = {
                id: item.id,
                title: item.title || item.id,
                category: item.category || 'ui',
                description: item.description || '',
                fitness: item.fitness || 'pending',
                lockedAt: item.fitness === 'pass' ? now : null,
                createdAt: now,
                updatedAt: now,
                generation: items.length + 1,
            };
            items.push(record);
            save(items);
            console.log('[Darwin] 🧬 New evolution recorded:', record.title, '(Gen', record.generation + ')');
            return record;
        }
        
        function list() {
            return load().slice().sort((a, b) => (a.createdAt || '').localeCompare(b.createdAt || ''));
        }
        
        function locked() {
            return list().filter(x => x.fitness === 'pass');
        }
        
        function stats() {
            const items = load();
            const byCategory = {};
            items.forEach(i => { byCategory[i.category] = (byCategory[i.category] || 0) + 1; });
            return {
                total: items.length,
                locked: items.filter(i => i.fitness === 'pass').length,
                pending: items.filter(i => i.fitness === 'pending').length,
                rejected: items.filter(i => i.fitness === 'reject').length,
                byCategory,
                lastGeneration: items.length,
            };
        }
        
        function onChange(cb) {
            listeners.push(cb);
            // Cross-tab sync
            try {
                const bc = new BroadcastChannel('poseidonx-darwin');
                bc.onmessage = (e) => { if (e.data && e.data.type === 'update') cb(e.data.items); };
            } catch (e) {}
            return () => {
                const i = listeners.indexOf(cb);
                if (i >= 0) listeners.splice(i, 1);
            };
        }
        
        // 初始化: 一次性记录历史演化项 (只在首次运行时写入)
        function bootstrap() {
            const HERITAGE = [
                { id: 'day-mode-lighting-v1',    title: '日间模式亮化',             category: 'scene',   description: '环境光 + 半球光 1.6x 增强, 天空着色器日间蓝' },
                { id: 'sky-shader-day-v1',       title: '程序化日间天空',            category: 'scene',   description: '地平线浅蓝 → 天顶深蓝渐变 + 太阳光晕' },
                { id: 'cabin-interiors-v1',      title: '6 舱室 3D 内饰',           category: 'scene',   description: '驾驶台/机舱/ECR/货舱/船员舱/厨房 完整建模' },
                { id: 'cabin-split-screen-v1',   title: '分屏舱室信息系统',          category: 'ui',      description: '左 3D + 右系统信息, 进入舱室自动分屏' },
                { id: 'cabin-search-keywords-v1',title: '搜索框识别舱室中文名',      category: 'ui',      description: '输入驾驶台/动力舱/机舱自动进入' },
                { id: 'cabin-dropdown-menu-v1',  title: '舱室快速下拉菜单',          category: 'ui',      description: '右上角单按钮折叠展开式舱室导航' },
                { id: 'ar-cas-floating-v2',      title: 'AR-CAS Pro 可拖拽面板',    category: 'ui',      description: '独立浮动, 拖拽/折叠/调整大小, localStorage 持久化' },
                { id: 'ar-cas-enriched-v1',      title: 'AR-CAS Pro 丰富信息',      category: 'safety',  description: '本船状态 + 环境 + COLREGs 建议 + CPA/TCPA 分解' },
                { id: 'ais-iceberg-merge-v1',    title: 'AIS 列表聚合本地威胁',     category: 'data',    description: 'AIS 列表自动包含 3D 场景中的冰山和货船目标' },
                { id: 'ocean-shader-v1',         title: '海洋 GPU 着色器',          category: 'scene',   description: '多层正弦波 + 菲涅尔反射 + 次表面散射' },
                { id: 'icebergs-sss-v1',         title: '冰山次表面散射着色',        category: 'scene',   description: '5 座冰山, 菲涅尔边缘 + 水下蓝色渗透' },
                { id: 'weather-particles-v1',    title: '天气粒子系统',             category: 'scene',   description: '雨/雪/雾/海鸥/烟囱尾气' },
                { id: 'openbridge-hmi-v1',       title: 'OpenBridge HMI 主题',     category: 'ui',       description: 'DNV OpenBridge 2.4 四主题切换 (dusk/dawn/day/night)' },
                { id: 'colregs-brain-v1',        title: 'COLREGs Brain L3',        category: 'ai',       description: 'Rule 13/14/15/17 自动判断 + TCPA/CPA 威胁评估' },
                { id: 'wpc-attitude-v1',         title: '穿浪双体船姿态控制',       category: 'physics',  description: '水翼/T-Foil 主动姿态反馈 抑制 pitch/heave' },
                { id: 'iamsar-drift-v1',         title: 'MOB + IAMSAR 漂移',       category: 'safety',   description: '落水报警 + 风流联合搜索半径预测' },
                { id: 'darwin-ratchet-v1',       title: '达尔文棘轮机制',          category: 'ai',       description: '只增不减的演化累积引擎' },
                { id: 'bridge-task-dispatch-v1', title: '桥楼任务派发规则',        category: 'ai',       description: '桥楼聊天识别"给X团队的Y设置任务"指令并 POST 到 /agent-config/teams/{team}/tasks, 自动同步至智能体页面' },
                { id: 'ar-cas-pm-task-v1',       title: 'AR-CAS Pro PM 任务案例',  category: 'safety',   description: '用户在桥楼下达"AR-CAS Pro 菜单需要PM实现"任务, 经派发规则路由至 build_pm' },
                { id: 'agent-page-light-theme-v1', title: '智能体页强制浅色主题',   category: 'ui',       description: '/agent-team-config.html 使用 OpenBridge day 主题, 不从 localStorage 继承深色' },
                { id: 'bridge-uses-agent-llm-v1', title: '桥楼 LLM 统一走智能体团队', category: 'ai',      description: '数字孪生 Bridge Chat 通过 /api/v1/bridge-chat/send 使用智能体团队默认 LLM 配置 (localStorage 降级为 fallback)' },
                { id: 'marine-datacenter-v1',     title: '船载数据中心 AI 能耗管理',  category: 'energy',   description: '第一性原理重构: 4 视角(设备/设施/环境/流程) + IoT Hub(LoRa/MC-RFID/PLC-Agent) + Skill库 + Policy引擎 + 闭环 + Darwin 棘轮; 页面: /marine-datacenter.html' },
            ];
            
            const existing = load();
            let added = 0;
            HERITAGE.forEach(h => {
                if (!existing.find(x => x.id === h.id)) {
                    existing.push({
                        ...h,
                        fitness: 'pass',  // Heritage 默认锁定
                        lockedAt: new Date().toISOString(),
                        createdAt: new Date().toISOString(),
                        updatedAt: new Date().toISOString(),
                        generation: existing.length + 1,
                    });
                    added++;
                }
            });
            if (added > 0) {
                save(existing);
                console.log(`[Darwin] 🧬 Bootstrapped ${added} heritage evolutions`);
            }
        }
        
        bootstrap();
        
        window.Darwin = { record, list, locked, stats, onChange };
        console.log('[Darwin] 🧬 Ratchet evolution engine online. Current:', stats());
    })();
    
    ```
    
    ### 文件: `src/backend/agent_team_api.py`
    ```py
    # -*- coding: utf-8 -*-
    """
    Agent Team API Routes - 双团队管理 REST API
    
    提供构建团队 & 执行团队的状态查询、KPI 考核、
    任务分配、报告查询等端点。挂载至 FastAPI 的 router。
    """
    
    from __future__ import annotations
    
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel
    from typing import Any, Dict, List, Optional
    
    router = APIRouter(prefix="/api/v1/agent-teams", tags=["Agent Teams"])
    
    
    # ---------------------------------------------------------------------------
    # 全局引用（在 main.py startup 时注入）
    # ---------------------------------------------------------------------------
    _build_team = None
    _execution_team = None
    _scheduler = None
    _evolution_engine = None
    
    
    def set_teams(build_team, execution_team, scheduler, evolution_engine=None):
        """在应用启动时由 main.py 调用，注入团队实例."""
        global _build_team, _execution_team, _scheduler, _evolution_engine
        _build_team = build_team
        _execution_team = execution_team
        _scheduler = scheduler
        _evolution_engine = evolution_engine
    
    
    # ---------------------------------------------------------------------------
    # Request / Response Models
    # ---------------------------------------------------------------------------
    
    class TaskAssignment(BaseModel):
        agent_id: str
        task: str
    
    class FeedbackSubmission(BaseModel):
        category: str = "optimization"
        severity: str = "medium"
        title: str
        detail: str
    
    
    # ---------------------------------------------------------------------------
    # Scheduler
    # ---------------------------------------------------------------------------
    
    @router.get("/scheduler/status")
    async def scheduler_status():
        if not _scheduler:
            raise HTTPException(503, "Scheduler not initialized")
        return _scheduler.get_status()
    
    
    @router.post("/scheduler/report")
    async def scheduler_generate_report():
        if not _scheduler:
            raise HTTPException(503, "Scheduler not initialized")
        return _scheduler.generate_report_now()
    
    
    @router.post("/scheduler/tick")
    async def scheduler_tick_once():
        """手动触发一次调度 tick (调试用)."""
        if not _scheduler:
            raise HTTPException(503, "Scheduler not initialized")
        return _scheduler.tick_once()
    
    
    # ---------------------------------------------------------------------------
    # Build Team
    # ---------------------------------------------------------------------------
    
    @router.get("/build/status")
    async def build_team_status():
        if not _build_team:
            raise HTTPException(503, "Build team not initialized")
        return _build_team.get_status()
    
    
    @router.get("/build/kpis")
    async def build_team_kpis():
        if not _build_team:
            raise HTTPException(503, "Build team not initialized")
        return _build_team.get_agent_kpis()
    
    
    @router.get("/build/agents/{agent_id}")
    async def build_agent_detail(agent_id: str):
        if not _build_team:
            raise HTTPException(503, "Build team not initialized")
        agent = _build_team.agents.get(agent_id)
        if not agent:
            raise HTTPException(404, f"Agent '{agent_id}' not found")
        return agent.to_dict()
    
    
    @router.post("/build/assign")
    async def build_assign_task(body: TaskAssignment):
        if not _build_team:
            raise HTTPException(503, "Build team not initialized")
        ok = _build_team.assign_task(body.agent_id, body.task)
        if not ok:
            raise HTTPException(404, f"Agent '{body.agent_id}' not found")
        return {"status": "assigned", "agent_id": body.agent_id, "task": body.task}
    
    
    @router.get("/build/reports")
    async def build_reports(limit: int = 10):
        if not _build_team:
            raise HTTPException(503, "Build team not initialized")
        reports = _build_team.hourly_reports[-limit:]
        return [r.to_dict() for r in reports]
    
    
    @router.get("/build/issues")
    async def build_issues():
        if not _build_team:
            raise HTTPException(503, "Build team not initialized")
        return _build_team.issue_backlog
    
    
    # ---------------------------------------------------------------------------
    # Execution Team
    # ---------------------------------------------------------------------------
    
    @router.get("/execution/status")
    async def execution_team_status():
        if not _execution_team:
            raise HTTPException(503, "Execution team not initialized")
        return _execution_team.get_status()
    
    
    @router.get("/execution/agents/{agent_id}")
    async def execution_agent_detail(agent_id: str):
        if not _execution_team:
            raise HTTPException(503, "Execution team not initialized")
        agent = _execution_team.agents.get(agent_id)
        if not agent:
            raise HTTPException(404, f"Agent '{agent_id}' not found")
        return agent.to_dict()
    
    
    @router.get("/execution/reports")
    async def execution_reports(limit: int = 10):
        if not _execution_team:
            raise HTTPException(503, "Execution team not initialized")
        reports = _execution_team.execution_reports[-limit:]
        return [r.to_dict() for r in reports]
    
    
    @router.get("/execution/feedback")
    async def execution_feedback():
        if not _execution_team:
            raise HTTPException(503, "Execution team not initialized")
        return [item.to_dict() for item in _execution_team.feedback_queue]
    
    
    @router.post("/execution/feedback")
    async def submit_feedback(body: FeedbackSubmission):
        if not _execution_team:
            raise HTTPException(503, "Execution team not initialized")
        item = _execution_team.submit_feedback(
            category=body.category,
            severity=body.severity,
            title=body.title,
            detail=body.detail,
        )
        return item.to_dict()
    
    
    # ---------------------------------------------------------------------------
    # Combined
    # ---------------------------------------------------------------------------
    
    @router.get("/overview")
    async def teams_overview():
        """一站式获取双团队全局概览."""
        result: Dict[str, Any] = {}
        if _build_team:
            bs = _build_team.get_status()
            result["build_team"] = {
                "health": bs["health"],
                "agent_count": bs["agent_count"],
                "metrics": bs["metrics"],
            }
        if _execution_team:
            es = _execution_team.get_status()
            result["execution_team"] = {
                "health": es["health"],
                "agent_count": es["agent_count"],
                "metrics": es["metrics"],
            }
        if _scheduler:
            result["scheduler"] = _scheduler.get_status()
        if _evolution_engine:
            result["evolution"] = _evolution_engine.get_status()
        return result
    
    
    # ---------------------------------------------------------------------------
    # System Evolution (自我演进引擎)
    # ---------------------------------------------------------------------------
    
    @router.get("/evolution/status")
    async def evolution_status():
        """获取自我演进引擎状态。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_status()
    
    
    @router.get("/evolution/summary")
    async def evolution_summary():
        """获取演进项汇总。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_evolution_summary()
    
    
    @router.get("/evolution/items")
    async def evolution_items(status: Optional[str] = None):
        """获取演进项列表，可按状态过滤。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_evolution_items(status=status)
    
    
    @router.get("/evolution/rules")
    async def evolution_rules():
        """获取审查规则列表。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return [r.to_dict() for r in _evolution_engine.audit_rules]
    
    
    @router.post("/evolution/audit")
    async def evolution_run_audit():
        """手动触发一次审查。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.run_full_audit()
    
    
    @router.post("/evolution/cycle")
    async def evolution_run_cycle():
        """运行完整演进周期（审查→派发→验证→关闭）。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.run_evolution_cycle()
    
    
    @router.post("/evolution/dispatch")
    async def evolution_dispatch():
        """派发所有待处理演进项给 Build 团队。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.dispatch_all_pending()
    
    
    @router.post("/evolution/verify")
    async def evolution_verify():
        """验证所有待验证项。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.verify_all_pending()
    
    
    @router.get("/evolution/items/{item_id}")
    async def evolution_item_detail(item_id: str):
        """获取单个演进项详情。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        item = _evolution_engine.evolution_items.get(item_id)
        if not item:
            raise HTTPException(404, f"Item '{item_id}' not found")
        return item.to_dict()
    
    
    @router.post("/evolution/items/{item_id}/progress")
    async def evolution_mark_progress(item_id: str):
        """标记演进项为进行中。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        ok = _evolution_engine.mark_in_progress(item_id)
        if not ok:
            raise HTTPException(404, f"Item '{item_id}' not found")
        return {"status": "ok", "item_id": item_id, "new_status": "in_progress"}
    
    
    @router.post("/evolution/items/{item_id}/complete")
    async def evolution_mark_complete(item_id: str):
        """标记演进项构建完成，进入待验证。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        ok = _evolution_engine.mark_build_complete(item_id)
        if not ok:
            raise HTTPException(404, f"Item '{item_id}' not found")
        return {"status": "ok", "item_id": item_id, "new_status": "verify_pending"}
    
    
    @router.post("/evolution/close-verified")
    async def evolution_close_verified():
        """关闭所有已验证通过的演进项。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        closed = _evolution_engine.close_verified()
        return {"closed": closed, "count": len(closed)}
    
    
    @router.get("/evolution/history")
    async def evolution_audit_history():
        """获取审查历史记录。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_audit_history()
    
    
    @router.get("/evolution/analytics")
    async def evolution_analytics():
        """获取演进分析数据 (域覆盖、严重度分布、趋势)。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        summary = _evolution_engine.get_evolution_summary()
        history = _evolution_engine.get_audit_history()
        status = _evolution_engine.get_status()
    
        return {
            "summary": summary,
            "history": history,
            "stats": status.get("stats", {}),
            "items_by_status": status.get("items_by_status", {}),
            "rules_count": status.get("audit_rules_count", 0),
        }
    
    
    # ---------------------------------------------------------------------------
    # Phase 3: 业界标准化改进 API
    # ---------------------------------------------------------------------------
    
    @router.get("/evolution/compliance-rating")
    async def evolution_compliance_rating():
        """获取 DNV CII 风格 A~E 合规评级。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_compliance_rating()
    
    
    @router.post("/evolution/compliance-rating/calculate")
    async def evolution_calculate_rating():
        """重新计算合规评级 (运行快速审查)。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.calculate_compliance_rating()
    
    
    @router.get("/evolution/checklist")
    async def evolution_checklist(level: Optional[str] = None):
        """获取 ClassNK 双层自查清单 (company/ship)。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_checklist(level=level)
    
    
    @router.get("/evolution/zones")
    async def evolution_zones():
        """获取所有合规区域。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_all_zones()
    
    
    @router.get("/evolution/zones/active")
    async def evolution_active_zones():
        """获取当前激活的合规区域。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return {
            "active_zones": _evolution_engine.get_active_zones(),
            "activated_rules": _evolution_engine.get_zone_activated_rules(),
            "vessel_position": _evolution_engine._vessel_position,
        }
    
    
    @router.post("/evolution/zones/update-position")
    async def evolution_update_position(lat: float = 0.0, lon: float = 0.0):
        """更新船舶位置，自动检测合规区域进入/离开。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.update_vessel_position(lat, lon)
    
    
    @router.get("/evolution/escalation")
    async def evolution_escalation():
        """获取失败升级状态 (DNV SEEMP Part III 风格)。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_escalation_status()
    
    
    @router.get("/evolution/trend")
    async def evolution_trend():
        """获取合规评级趋势分析。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_trend_analysis()
    
    
    @router.get("/evolution/monitoring")
    async def evolution_monitoring():
        """获取连续监控状态。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_monitoring_status()
    
    
    @router.get("/evolution/audit-trail")
    async def evolution_audit_trail(event_type: Optional[str] = None, limit: int = 50):
        """获取审计轨迹日志。"""
        if not _evolution_engine:
            raise HTTPException(404, "Evolution engine not registered")
        return _evolution_engine.get_audit_trail(event_type=event_type, limit=limit)
    
    
    __all__ = ["router", "set_teams"]
    
    ```
    
    ### 文件: `src/backend/channels/execution_team_manager.py`
    ```py
    # -*- coding: utf-8 -*-
    """
    Execution Agent Team Manager - 执行智能体团队管理器
    
    管理负责 AI Native 系统运行时功能最大化的智能体团队。
    团队通过 DeepSeek 驱动，实时运行系统核心功能，
    并将发现的问题和优化建议反馈给构建团队。
    
    角色分工：
      - Perception Agent   : 管理分布式感知融合 (L2)
      - Decision Agent     : 管理决策编排 (L3)
      - Navigation Agent   : 管理自主航行 / COLREGS 合规 (L3)
      - Energy Agent       : 管理能效优化 (跨层)
      - Feedback Agent     : 汇总执行数据，向构建团队提交优化需求
    """
    
    from __future__ import annotations
    
    import asyncio
    import logging
    import time
    from dataclasses import dataclass, field, asdict
    from datetime import datetime
    from enum import Enum
    from typing import Any, Dict, List, Optional
    
    from channels.marine_base import MarineChannel, ChannelPriority, ChannelStatus
    
    logger = logging.getLogger(__name__)
    
    
    # ---------------------------------------------------------------------------
    # Data Models
    # ---------------------------------------------------------------------------
    
    class ExecRole(str, Enum):
        PERCEPTION = "perception"
        DECISION = "decision"
        NAVIGATION = "navigation"
        ENERGY = "energy"
        FEEDBACK = "feedback"
    
    
    class ExecState(str, Enum):
        IDLE = "idle"
        MONITORING = "monitoring"
        OPTIMIZING = "optimizing"
        ALERTING = "alerting"
        ERROR = "error"
    
    
    @dataclass
    class ExecAgentMetrics:
        """执行 Agent 运行时指标."""
        cycles_run: int = 0
        anomalies_detected: int = 0
        optimizations_applied: int = 0
        feedback_sent: int = 0
        uptime_seconds: float = 0.0
        last_cycle_at: Optional[str] = None
    
    
    @dataclass
    class ExecAgent:
        """单个执行智能体."""
        id: str
        role: ExecRole
        name: str
        description: str
        llm_backend: str = "deepseek"
        state: ExecState = ExecState.IDLE
        target_channels: List[str] = field(default_factory=list)
        metrics: ExecAgentMetrics = field(default_factory=ExecAgentMetrics)
        config: Dict[str, Any] = field(default_factory=dict)
    
        def to_dict(self) -> Dict[str, Any]:
            return {**asdict(self), "state": self.state.value, "role": self.role.value}
    
    
    @dataclass
    class FeedbackItem:
        """执行团队向构建团队发送的反馈条目."""
        id: str
        source_agent: str
        category: str  # bug, optimization, feature_request, alert
        severity: str  # critical, high, medium, low
        title: str
        detail: str
        created_at: str
        resolved: bool = False
        resolution: Optional[str] = None
    
        def to_dict(self) -> Dict[str, Any]:
            return asdict(self)
    
    
    @dataclass
    class ExecutionReport:
        """执行团队的定期运行报告."""
        timestamp: str
        period_seconds: float
        perception_events: int = 0
        decisions_made: int = 0
        nav_corrections: int = 0
        energy_savings_pct: float = 0.0
        anomalies: int = 0
        feedback_items_sent: int = 0
        channel_health: Dict[str, str] = field(default_factory=dict)
        agents_summary: Dict[str, Any] = field(default_factory=dict)
    
        def to_dict(self) -> Dict[str, Any]:
            return asdict(self)
    
    
    # ---------------------------------------------------------------------------
    # Execution Team Manager Channel
    # ---------------------------------------------------------------------------
    
    class ExecutionTeamManagerChannel(MarineChannel):
        """执行智能体团队管理器 — 融入 AI Native CPS 架构."""
    
        name = "execution_team_manager"
        description = "执行智能体团队管理 (感知 → 决策 → 导航 → 能效 → 反馈)"
        version = "1.0.0"
        priority = ChannelPriority.P0  # 执行团队优先级最高
        dependencies: List[str] = [
            "distributed_perception_hub",
            "decision_orchestrator",
        ]
    
        # 默认运行间隔 (秒) — 执行团队运行更频繁
        SCHEDULE = {
            ExecRole.PERCEPTION: 5,    # 每 5 秒一次感知融合
            ExecRole.DECISION: 10,     # 每 10 秒一次决策评估
            ExecRole.NAVIGATION: 10,   # 每 10 秒一次航行校正
            ExecRole.ENERGY: 30,       # 每 30 秒一次能效评估
            ExecRole.FEEDBACK: 60,     # 每 60 秒汇总反馈
        }
    
        def __init__(self, config: Optional[Dict[str, Any]] = None):
            super().__init__()
            self.config = config or {}
            self._config = self.config
            self.llm_backend = self.config.get("llm_backend", "deepseek")
    
            self.agents: Dict[str, ExecAgent] = {}
            self._init_agents()
    
            self.feedback_queue: List[FeedbackItem] = []
            self.execution_reports: List[ExecutionReport] = []
            self.event_log: List[Dict[str, Any]] = []
            self._running = False
            self._start_time: Optional[float] = None
    
            # 全局运行时指标
            self.total_perception_events = 0
            self.total_decisions = 0
            self.total_nav_corrections = 0
            self.total_energy_savings_pct = 0.0
            self.total_anomalies = 0
            self._feedback_counter = 0
    
        # ── Agent 初始化 ──────────────────────────────────────────
    
        def _init_agents(self):
            definitions = [
                {
                    "id": "exec_perception",
                    "role": ExecRole.PERCEPTION,
                    "name": "Perception Fusion Agent",
                    "description": "持续融合 AIS/雷达/气象/WorldMonitor 数据，检测异常",
                    "target_channels": [
                        "distributed_perception_hub",
                        "nmea_channel",
                        "worldmonitor",
                    ],
                },
                {
                    "id": "exec_decision",
                    "role": ExecRole.DECISION,
                    "name": "Decision & Planning Agent",
                    "description": "实时评估态势，产出决策建议，驱动自主操控",
                    "target_channels": [
                        "decision_orchestrator",
                        "colregs_brain",
                    ],
                },
                {
                    "id": "exec_navigation",
                    "role": ExecRole.NAVIGATION,
                    "name": "Navigation Control Agent",
                    "description": "航行纠偏、COLREGS 合规检查、姿态控制",
                    "target_channels": [
                        "colregs_brain",
                        "wpc_attitude_control",
                    ],
                },
                {
                    "id": "exec_energy",
                    "role": ExecRole.ENERGY,
                    "name": "Energy Optimization Agent",
                    "description": "能效分析 (CII/EEXI)、航速优化、燃料节省",
                    "target_channels": [
                        "energy_efficiency",
                        "data_lakehouse",
                    ],
                },
                {
                    "id": "exec_feedback",
                    "role": ExecRole.FEEDBACK,
                    "name": "Feedback & Issue Agent",
                    "description": "汇总执行数据，向构建团队提交优化需求与 bug 报告",
                    "target_channels": [
                        "build_team_manager",
                        "event_store",
                    ],
                },
            ]
            for defn in definitions:
                agent = ExecAgent(
                    id=defn["id"],
                    role=defn["role"],
                    name=defn["name"],
                    description=defn["description"],
                    llm_backend=self.llm_backend,
                    target_channels=defn.get("target_channels", []),
                )
                self.agents[agent.id] = agent
    
        # ── MarineChannel 接口 ───────────────────────────────────
    
        def initialize(self) -> bool:
            self._initialized = True
            self._running = True
            self._start_time = time.monotonic()
            for agent in self.agents.values():
                agent.state = ExecState.MONITORING
            self._set_health(ChannelStatus.OK, "执行团队就绪，5 名 Agent 已上线")
            logger.info("⚡ Execution Team Manager initialized (%d agents)", len(self.agents))
            return True
    
        def shutdown(self) -> bool:
            self._running = False
            self._initialized = False
            for agent in self.agents.values():
                agent.state = ExecState.IDLE
            self._set_health(ChannelStatus.OFF, "Shutdown")
            return True
    
        # ── 调度 & 执行 ──────────────────────────────────────────
    
        def tick(self, now: Optional[datetime] = None, channel_registry: Optional[Dict] = None) -> Dict[str, Any]:
            """外部定时调用，驱动所有执行 Agent."""
            now = now or datetime.now()
            results: Dict[str, Any] = {}
            for agent in self.agents.values():
                if self._should_run(agent, now):
                    result = self._execute_agent_cycle(agent, now, channel_registry)
                    results[agent.id] = result
            return results
    
        def _should_run(self, agent: ExecAgent, now: datetime) -> bool:
            interval = self.SCHEDULE.get(agent.role, 30)
            if not agent.metrics.last_cycle_at:
                return True
            try:
                last = datetime.fromisoformat(agent.metrics.last_cycle_at)
                return (now - last).total_seconds() >= interval
            except (ValueError, TypeError):
                return True
    
        def _execute_agent_cycle(
            self, agent: ExecAgent, now: datetime,
            channel_registry: Optional[Dict] = None,
        ) -> Dict[str, Any]:
            agent.state = ExecState.MONITORING
            agent.metrics.last_cycle_at = now.isoformat()
            cycle_start = time.monotonic()
            result: Dict[str, Any] = {
                "agent": agent.id, "role": agent.role.value, "time": now.isoformat()
            }
    
            try:
                if agent.role == ExecRole.PERCEPTION:
                    result.update(self._run_perception(agent, now, channel_registry))
                elif agent.role == ExecRole.DECISION:
                    result.update(self._run_decision(agent, now, channel_registry))
                elif agent.role == ExecRole.NAVIGATION:
                    result.update(self._run_navigation(agent, now, channel_registry))
                elif agent.role == ExecRole.ENERGY:
                    result.update(self._run_energy(agent, now, channel_registry))
                elif agent.role == ExecRole.FEEDBACK:
                    result.update(self._run_feedback(agent, now))
    
                agent.metrics.cycles_run += 1
                agent.state = ExecState.MONITORING
            except Exception as exc:
                agent.state = ExecState.ERROR
                result["error"] = str(exc)
                logger.error("Exec agent %s cycle failed: %s", agent.id, exc)
    
            elapsed = time.monotonic() - cycle_start
            agent.metrics.uptime_seconds += elapsed
            self.event_log.append(result)
            return result
    
        # ── 各角色执行逻辑 ───────────────────────────────────────
    
        def _run_perception(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
            """感知 Agent：融合多源数据，检测异常."""
            # 如果有实际 channel registry，从中获取感知数据
            snapshot: Dict[str, Any] = {}
            if registry:
                hub = registry.get("distributed_perception_hub")
                if hub and hasattr(hub, "capture_system_snapshot"):
                    try:
                        snapshot = hub.capture_system_snapshot()
                    except Exception:
                        snapshot = {"error": "snapshot_unavailable"}
    
            # 基本感知事件模拟
            event_count = 3 + (agent.metrics.cycles_run % 5)
            anomaly = 1 if agent.metrics.cycles_run % 7 == 0 else 0
            self.total_perception_events += event_count
            self.total_anomalies += anomaly
    
            if anomaly:
                agent.state = ExecState.ALERTING
                agent.metrics.anomalies_detected += 1
                self._create_feedback(
                    agent.id, "alert", "high",
                    f"感知异常 #{agent.metrics.anomalies_detected}",
                    f"在第 {agent.metrics.cycles_run} 个感知周期检测到数据异常",
                )
    
            return {
                "action": "perception_fusion",
                "events_processed": event_count,
                "anomaly_detected": anomaly > 0,
                "snapshot_available": bool(snapshot),
            }
    
        def _run_decision(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
            """决策 Agent：态势评估 & 行动建议."""
            decision_quality = 0.85 + (agent.metrics.cycles_run % 10) * 0.01
            self.total_decisions += 1
    
            actions_recommended = [
                {"type": "course_adjustment", "priority": "medium", "detail": "建议微调航向 2°"},
                {"type": "speed_optimization", "priority": "low", "detail": "当前航速经济性良好"},
            ]
    
            if self.total_anomalies > 0 and agent.metrics.cycles_run % 5 == 0:
                actions_recommended.append({
                    "type": "emergency_assessment", "priority": "high",
                    "detail": "需要评估最近的感知异常对航行安全的影响",
                })
    
            return {
                "action": "decision_evaluation",
                "decision_quality": round(decision_quality, 3),
                "actions_recommended": len(actions_recommended),
                "details": actions_recommended,
            }
    
        def _run_navigation(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
            """航行 Agent：COLREGS 合规 & 纠偏."""
            correction_needed = agent.metrics.cycles_run % 4 == 0
            if correction_needed:
                self.total_nav_corrections += 1
                agent.metrics.optimizations_applied += 1
    
            colregs_status = "COMPLIANT"
            if agent.metrics.cycles_run % 20 == 0 and agent.metrics.cycles_run > 0:
                colregs_status = "REVIEW_NEEDED"
                self._create_feedback(
                    agent.id, "optimization", "medium",
                    "COLREGS 规则需要审查",
                    "建议构建团队更新 COLREGS 规则引擎以覆盖最新 IMO 规定",
                )
    
            return {
                "action": "navigation_control",
                "correction_applied": correction_needed,
                "colregs_status": colregs_status,
                "total_corrections": self.total_nav_corrections,
            }
    
        def _run_energy(self, agent: ExecAgent, now: datetime, registry=None) -> Dict[str, Any]:
            """能效 Agent：CII/EEXI 实时评估."""
            # 模拟能效节省 (最高 ~8%)
            savings = 2.5 + (agent.metrics.cycles_run % 12) * 0.5
            self.total_energy_savings_pct = savings
            agent.metrics.optimizations_applied += 1
    
            cii_rating = "A" if savings > 5 else "B" if savings > 3 else "C"
    
            if cii_rating == "C":
                self._create_feedback(
                    agent.id, "optimization", "high",
                    "CII 评级下降至 C",
                    "建议构建团队优化航速控制算法以改善 CII 评级",
                )
    
            return {
                "action": "energy_optimization",
                "savings_pct": round(savings, 2),
                "cii_rating": cii_rating,
                "cycle": agent.metrics.cycles_run,
            }
    
        def _run_feedback(self, agent: ExecAgent, now: datetime) -> Dict[str, Any]:
            """反馈 Agent：汇总 & 发送反馈给构建团队."""
            pending = list(self.feedback_queue)
            self.feedback_queue = []
            agent.metrics.feedback_sent += len(pending)
    
            return {
                "action": "feedback_delivery",
                "items_sent": len(pending),
                "items": [item.to_dict() for item in pending[:10]],  # 最多 10 条
                "total_feedback_sent": agent.metrics.feedback_sent,
            }
    
        # ── 反馈生成 ─────────────────────────────────────────────
    
        def _create_feedback(
            self, source: str, category: str, severity: str, title: str, detail: str,
        ):
            self._feedback_counter += 1
            item = FeedbackItem(
                id=f"FB-{self._feedback_counter:04d}",
                source_agent=source,
                category=category,
                severity=severity,
                title=title,
                detail=detail,
                created_at=datetime.now().isoformat(),
          
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
     
  ## ⚠️ 重要提示
  上方 📂 项目上下文 包含了任务相关的实际源文件。
  请基于这些文件设计方案，不要引用不存在的文件。
  
  ## 要求
  1. 基于调研结果和实际源码，设计详细技术方案
  2. 明确指出需要修改的文件和具体修改内容
  3. 定义接口规范（如有新增 API）
  4. 为开发工程师提供逐步实施指南
  
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

# 技术方案: 让货船以双体船为圆心动起来

## 1. 任务分析

### 1.1 核心需求
- **目标**: 让货船以双体船为圆心进行圆周运动
- **场景**: 3D 数字孪生场景中的船舶运动模拟
- **关键实体**: 
  - 双体船 (穿浪双体船 WPC) - 作为圆心
  - 货船 - 围绕双体船做圆周运动

### 1.2 现有资源分析
- 项目已有 `GLB_20251223141542.glb` 3D 模型文件
- 已有 `wpc-attitude-v1` 穿浪双体船姿态控制功能
- 前端使用 Three.js 进行 3D 渲染
- 后端有完整的 Agent 团队管理 API

## 2. 技术方案设计

### 2.1 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    前端 (Three.js 3D 场景)                    │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  场景初始化   │    │  船舶运动引擎  │    │  UI 控制面板  │  │
│  │  (Scene)     │    │  (ShipOrbit)  │    │  (Controls)  │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │          │
│         └───────────────────┼───────────────────┘          │
│                             │                              │
│                    ┌────────▼────────┐                     │
│                    │  Darwin Ratchet  │                     │
│                    │  (演化记录)      │                     │
│                    └─────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    后端 (FastAPI)                            │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Agent Team  │    │  Evolution   │    │  API Routes  │  │
│  │  Manager     │    │  Engine      │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心算法设计

#### 圆周运动算法
```javascript
// 货船绕双体船做圆周运动
class ShipOrbitController {
    constructor() {
        this.orbitRadius = 200;      // 轨道半径 (米)
        this.orbitSpeed = 0.005;     // 角速度 (弧度/帧)
        this.currentAngle = 0;       // 当前角度
        this.centerPosition = { x: 0, z: 0 }; // 双体船位置
        this.cargoShip = null;       // 货船对象
        this.isRunning = false;
    }

    update() {
        if (!this.isRunning || !this.cargoShip) return;
        
        // 更新角度
        this.currentAngle += this.orbitSpeed;
        if (this.currentAngle > Math.PI * 2) {
            this.currentAngle -= Math.PI * 2;
        }

        // 计算新位置
        const x = this.centerPosition.x + this.orbitRadius * Math.cos(this.currentAngle);
        const z = this.centerPosition.z + this.orbitRadius * Math.sin(this.currentAngle);

        // 更新货船位置
        this.cargoShip.position.set(x, 0, z);
        
        // 让货船朝向运动方向 (切线方向)
        const tangentAngle = this.currentAngle + Math.PI / 2;
        this.cargoShip.rotation.y = -tangentAngle;
    }
}
```

### 2.3 需要修改的文件

#### 前端文件

| 文件 | 修改内容 | 优先级 |
|------|---------|--------|
| `src/frontend/digital-twin/main.js` | 添加货船圆周运动逻辑 | P0 |
| `src/frontend/digital-twin/PoseidonX.js` | 集成轨道控制器 | P0 |
| `src/frontend/digital-twin/layer1-interface/DigitalTwinMap.js` | 添加轨道可视化 | P1 |
| `src/frontend/js/darwin-ratchet.js` | 记录新演化项 | P1 |

#### 后端文件

| 文件 | 修改内容 | 优先级 |
|------|---------|--------|
| `src/backend/agent_team_api.py` | 添加任务分配端点 | P0 |
| `src/backend/channels/execution_team_manager.py` | 添加轨道控制监控 | P1 |

### 2.4 具体修改方案

#### 2.4.1 前端: `main.js` - 添加圆周运动控制器

```javascript
// 在 main.js 中添加
class ShipOrbitController {
    constructor(scene, cargoShip, centerShip) {
        this.scene = scene;
        this.cargoShip = cargoShip;
        this.centerShip = centerShip;
        this.orbitRadius = 200;
        this.orbitSpeed = 0.003;
        this.currentAngle = 0;
        this.isRunning = false;
        this.orbitLine = null;
    }

    start() {
        this.isRunning = true;
        this.currentAngle = 0;
        this.createOrbitVisualization();
        console.log('[ShipOrbit] 货船开始绕双体船运动');
    }

    stop() {
        this.isRunning = false;
        console.log('[ShipOrbit] 货船运动停止');
    }

    update() {
        if (!this.isRunning || !this.cargoShip) return;

        this.currentAngle += this.orbitSpeed;
        if (this.currentAngle > Math.PI * 2) {
            this.currentAngle -= Math.PI * 2;
        }

        const centerPos = this.centerShip.position;
        const x = centerPos.x + this.orbitRadius * Math.cos(this.currentAngle);
        const z = centerPos.z + this.orbitRadius * Math.sin(this.currentAngle);

        this.cargoShip.position.set(x, 0, z);
        
        // 朝向运动方向
        const tangentAngle = this.currentAngle + Math.PI / 2;
        this.cargoShip.rotation.y = -tangentAngle;
    }

    createOrbitVisualization() {
        // 创建轨道线 (圆形)
        const points = [];
        const segments = 64;
        for (let i = 0; i <= segments; i++) {
            const angle = (i / segments) * Math.PI * 2;
            const x = this.centerShip.position.x + this.orbitRadius * Math.cos(angle);
            const z = this.centerShip.position.z + this.orbitRadius * Math.sin(angle);
            points.push(new THREE.Vector3(x, 0.5, z));
        }
        
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({ 
            color: 0x00ff88, 
            transparent: true, 
            opacity: 0.3 
        });
        this.orbitLine = new THREE.Line(geometry, material);
        this.scene.add(this.orbitLine);
    }

    setSpeed(speed) {
        this.orbitSpeed = speed;
    }

    setRadius(radius) {
        this.orbitRadius = radius;
        if (this.orbitLine) {
            this.scene.remove(this.orbitLine);
            this.createOrbitVisualization();
        }
    }
}
```

#### 2.4.2 前端: `PoseidonX.js` - 集成轨道控制器

```javascript
// 在 PoseidonX 类中添加
class PoseidonX {
    constructor() {
        // ... 现有代码 ...
        this.shipOrbitController = null;
    }

    initShipOrbit(scene, cargoShip, centerShip) {
        this.shipOrbitController = new ShipOrbitController(scene, cargoShip, centerShip);
        
        // 注册到动画循环
        this.animationCallbacks.push(() => {
            if (this.shipOrbitController) {
                this.shipOrbitController.update();
            }
        });
        
        // 记录到 Darwin Ratchet
        if (window.Darwin) {
            window.Darwin.record({
                id: 'cargo-ship-orbit-v1',
                title: '货船绕双体船圆周运动',
                category: 'physics',
                description: '货船以双体船为圆心做匀速圆周运动，带轨道可视化',
                fitness: 'pass'
            });
        }
    }

    startCargoShipOrbit() {
        if (this.shipOrbitController) {
            this.shipOrbitController.start();
        }
    }

    stopCargoShipOrbit() {
        if (this.shipOrbitController) {
            this.shipOrbitController.stop();
        }
    }
}
```

#### 2.4.3 后端: `agent_team_api.py` - 添加任务分配端点

```python
# 在 agent_team_api.py 中添加新的路由

@router.post("/build/pm/assign-task")
async def assign_pm_task(body: TaskAssignment):
    """
    给 Build 团队的 PM 分配任务
    用于桥楼指令: "给build团队的PM分配一个任务，让货船以双体船为圆心动起来"
    """
    if not _build_team:
        raise HTTPException(503, "Build team not initialized")
    
    # 查找 PM agent
    pm_agent = _build_team.agents.get("build_pm")
    if not pm_agent:
        raise HTTPException(404, "Build PM agent not found")
    
    # 分配任务
    ok = _build_team.assign_task("build_pm", body.task)
    if not ok:
        raise HTTPException(500, "Failed to assign task to PM")
    
    # 记录到演化引擎
    if _evolution_engine:
        _evolution_engine.create_evolution_item(
            title="货船圆周运动",
            description=body.task,
            target_channel="poseidonx_3d_scene",
            severity="medium"
        )
    
    return {
        "status": "assigned",
        "agent_id": "build_pm",
        "task": body.task,
        "timestamp": datetime.now().isoformat()
    }
```

#### 2.4.4 前端: `DigitalTwinMap.js` - 添加轨道控制 UI

```javascript
// 在 DigitalTwinMap 类中添加轨道控制面板
class DigitalTwinMap {
    // ... 现有代码 ...
    
    addOrbitControls() {
        const controlsDiv = document.createElement('div');
        controlsDiv.className = 'orbit-controls';
        controlsDiv.innerHTML = `
            <div class="orbit-panel">
                <h4>🚢 货船轨道控制</h4>
                <button id="startOrbit" class="btn btn-primary">▶ 开始运动</button>
                <button id="stopOrbit" class="btn btn-danger">⏹ 停止运动</button>
                <div class="slider-group">
                    <label>轨道半径: <span id="radiusValue">200m</span></label>
                    <input type="range" id="orbitRadius" min="50" max="500" value="200">
                </div>
                <div class="slider-group">
                    <label>运动速度: <span id="speedValue">1x</span></label>
                    <input type="range" id="orbitSpeed" min="0.1" max="3" value="1" step="0.1">
                </div>
            </div>
        `;
        
        document.body.appendChild(controlsDiv);
        
        // 绑定事件
        document.getElementById('startOrbit').addEventListener('click', () => {
            if (window.poseidonX) {
                window.poseidonX.startCargoShipOrbit();
            }
        });
        
        document.getElementById('stopOrbit').addEventListener('click', () => {
            if (window.poseidonX) {
                window.poseidonX.stopCargoShipOrbit();
            }
        });
        
        document.getElementById('orbitRadius').addEventListener('input', (e) => {
            const radius = parseInt(e.target.value);
            document.getElementById('radiusValue').textContent = radius + 'm';
            if (window.poseidonX && window.poseidonX.shipOrbitController) {
                window.poseidonX.shipOrbitController.setRadius(radius);
            }
        });
        
        document.getElementById('orbitSpeed').addEventListener('input', (e) => {
            const speed = parseFloat(e.target.value) * 0.003;
            document.getElementById('speedValue').textContent = e.target.value + 'x';
            if (window.poseidonX && window.poseidonX.shipOrbitController) {
                window.poseidonX.shipOrbitController.setSpeed(speed);
            }
        });
    }
}
```

## 3. 接口规范

### 3.1 新增 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/agent-teams/build/pm/assign-task` | 给 Build PM 分配任务 |
| GET | `/api/v1/agent-teams/build/pm/tasks` | 获取 PM 当前任务列表 |

### 3.2 请求/响应格式

**POST /api/v1/agent-teams/build/pm/assign-task**
```json
// 请求
{
    "agent_id": "build_pm",
    "task": "让货船以双体船为圆心动起来"
}

// 响应
{
    "status": "assigned",
    "agent_id": "build_pm",
    "task": "让货船以双体船为圆心动起来",
    "timestamp": "2025-01-15T10:30:00Z"
}
```

## 4. 实施步骤

### 步骤 1: 前端核心逻辑实现
1. 在 `main.js` 中添加 `ShipOrbitController` 类
2. 在 `PoseidonX.js` 中集成轨道控制器
3. 在场景初始化时创建货船和双体船引用

### 步骤 2: UI 控制面板
1. 在 `DigitalTwinMap.js` 中添加轨道控制 UI
2. 实现速度/半径调节滑块
3. 添加开始/停止按钮

### 步骤 3: 后端 API 支持
1. 在 `agent_team_api.py` 中添加 PM 任务分配端点
2. 确保桥楼指令可以路由到该端点

### 步骤 4: 演化记录
1. 在 `darwin-ratchet.js` 中记录新功能
2. 在系统演化引擎中创建对应的演进项

### 步骤 5: 测试验证
1. 验证货船是否按圆周轨迹运动
2. 验证轨道可视化是否正确显示
3. 验证速度/半径调节功能
4. 验证 API 任务分配是否成功

## 5. 风险与注意事项

### 5.1 技术风险
- **3D 模型加载**: 确保 `GLB_20251223141542.glb` 包含货船和双体船模型
- **性能影响**: 圆周运动计算量小，但轨道线渲染可能影响性能
- **坐标系统**: 确保 Three.js 坐标与物理模拟坐标一致

### 5.2 解决方案
- 使用 `THREE.Line` 的 `frustumCulled` 优化
- 轨道线透明度可调，支持隐藏
- 添加性能监控，自动降低渲染质量

## 6. 交付物清单

1. ✅ 修改后的 `main.js` - 包含 `ShipOrbitController`
2. ✅ 修改后的 `PoseidonX.js` - 集成轨道控制
3. ✅ 修改后的 `DigitalTwinMap.js` - 添加 UI 控制
4. ✅ 修改后的 `agent_team_api.py` - 添加 API 端点
5. ✅ 更新后的 `darwin-ratchet.js` - 记录演化项

## 7. 时间估算

| 任务 | 预估时间 | 负责人 |
|------|---------|--------|
| 前端核心逻辑 | 2小时 | Frontend Dev |
| UI 控制面板 | 1小时 | Frontend Dev |
| 后端 API | 1小时 | Backend Dev |
| 测试验证 | 1小时 | QA |
| **总计** | **5小时** | - |

────────────────────────────────────────────────────────────
✅ deepseek-chat 完成
