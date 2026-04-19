# PM分解 — project_manager

任务: 数字孪生的AR-CAS Pro菜单是空白的，需要他来实现
步骤: pm_decompose
Agent: build_pm

---

📋 任务: a859a3be-e78
🤖 Agent: PM (project_manager)
📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
🔧 执行方式: DeepSeek API (直连)
⏱️ 超时: 300s
────────────────────────────────────────────────────────────
📝 提示词:
  你是 PoseidonX 系统的 PM (project_manager)。
  请执行以下开发任务:
  
  你是项目经理 (PM)。请对以下任务进行分解和规划:
  
  ## 任务
  数字孪生的AR-CAS Pro菜单是空白的，需要他来实现
  给build团队的PM设置一个任务，数字孪生的AR-CAS Pro菜单是空白的，需要他来实现
  
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
  src/frontend/captain-cockpit-new.html
  src/frontend/captain-cockpit.html
  src/frontend/cms-health.html
  src/frontend/cms-health.html.bak
  src/frontend/crew-management.html
  src/frontend/digital-twin.html
  src/frontend/dp-control.html
  src/frontend/dp-control.html.bak
  src/frontend/energy-compliance.html
  src/frontend/energy-compliance.html.bak
  src/frontend/hmi-console.html
  src/frontend/hmi-console.html.bak
  src/frontend/index.html
  src/frontend/index.html.bak
  src/frontend/knowledge-base.html
  src/frontend/knowledge-base.html.bak
  src/frontend/navigation-v2.bak.html
  src/frontend/navigation-v2.html
  src/frontend/navigation-v3.html
  src/frontend/navigation.html
  src/frontend/offshore-ops.html
  src/frontend/offshore-ops.html.bak
  src/frontend/poseidon-config.html
  src/frontend/poseidon-config.html.bak
  src/frontend/safety-emergency.html
  src/frontend/safety-emergency.html.bak
  src/frontend/ship-shore.html
  src/frontend/ship-shore.html.bak
  src/frontend/sim-training.html
  src/frontend/sim-training.html.bak
  src/frontend/system-evolution.html
  src/frontend/system-evolution.html.bak
  src/frontend/thruster-control.html
  src/frontend/thruster-control.html.bak
  src/frontend/thruster-control2.html
  src/frontend/weather-ocean.html
  src/frontend/worldmonitor-ar-cas-pro.html
  src/frontend/worldmonitor-map.html
  src/frontend/css/openbridge-theme.css
  src/frontend/js/darwin-ratchet.js
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
  src/backend/agents/api.py
  src/backend/agents/chat_harness.py
  src/backend/agents/execution_registry.py
  src/backend/agents/hermes_research.py
  src/backend/agents/knowledge_base.py
  src/backend/agents/models.py
  src/backend/agents/session_store.py
  src/backend/agents/skill_registry.py
  src/backend/agents/task_engine.py
  src/backend/agents/team_manager.py
  src/backend/agents/tool_executor.py
  src/backend/agents/tool_registry.py
  src/backend/agents/teams/__init__.py
  src/backend/agents/teams/build_team.py
  src/backend/agents/teams/execution_team.py
  src/backend/agents/skills/__init__.py
  src/backend/storage/__init__.py
  src/backend/storage/cloud_sync.py
  src/backend/storage/data_lakehouse.py
  src/backend/storage/event_store.py
  src/backend/adapters/__init__.py
  src/backend/adapters/worldmonitor_adapter.py
  src/backend/adapters/worldmonitor_adapter_real.py
  src/backend/channels/## GitHub Copilot Chat.litcoffee
  src/backend/channels/__init__.py
  src/backend/channels/agent_set_base.py
  src/backend/channels/agent_set_coordinator.py
  src/backend/channels/agent_set_protocol.py
  src/backend/channels/agent_team_scheduler.py
  src/backend/channels/ais_processor.py
  src/backend/channels/alarm_management.py
  src/backend/channels/anchor_watch_channel.py
  src/backend/channels/autonomy_manager.py
  src/backend/channels/autopilot_monitor.py
  src/backend/channels/ballast_water_monitor.py
  src/backend/channels/bilge_water_monitor.py
  src/backend/channels/bridge_chat.py
  src/backend/channels/build_team_manager.py
  src/backend/channels/cargo_monitor.py
  ... (共 679 个 src/ 文件)
  
  ```
  
  ### 文件: `src/frontend/worldmonitor-ar-cas-pro.html`
  ```html
  <!DOCTYPE html>
  <html lang="zh-CN">
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>WorldMonitor AR-CAS Pro - 船舶避免碰撞增强现实系统（专业版）</title>
      <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>
      <link href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css" rel="stylesheet" />
      <style>
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              background: #0a0e1a;
              color: #ffffff;
              overflow: hidden;
              height: 100vh;
          }
          .header {
              position: fixed;
              top: 0; left: 0; right: 0;
              height: 60px;
              background: linear-gradient(180deg, rgba(10,14,26,0.95) 0%, rgba(10,14,26,0.8) 100%);
              border-bottom: 2px solid rgba(79,195,247,0.4);
              display: flex;
              align-items: center;
              justify-content: space-between;
              padding: 0 24px;
              z-index: 1000;
          }
          .header h1 {
              font-size: 20px;
              font-weight: 700;
              background: linear-gradient(90deg, #4fc3f7 0%, #29b6f6 100%);
              -webkit-background-clip: text;
              -webkit-text-fill-color: transparent;
          }
          .header-title {
              display: flex;
              align-items: center;
              gap: 14px;
          }
          .header-status { display: flex; gap: 20px; align-items: center; }
          .header-actions {
              display: flex;
              align-items: center;
              gap: 10px;
          }
          .status-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #a0aec0; }
          .status-dot {
              width: 8px; height: 8px; border-radius: 50%;
              background: #48bb78;
              animation: pulse 2s infinite;
          }
          .action-button,
          .action-link {
              display: inline-flex;
              align-items: center;
              justify-content: center;
              gap: 6px;
              min-height: 36px;
              padding: 0 14px;
              border-radius: 999px;
              border: 1px solid rgba(79,195,247,0.28);
              background: rgba(79,195,247,0.12);
              color: #d9f6ff;
              font-size: 12px;
              font-weight: 600;
              cursor: pointer;
              text-decoration: none;
              transition: background 0.2s ease, transform 0.2s ease, border-color 0.2s ease;
          }
          .action-button:hover,
          .action-link:hover {
              background: rgba(79,195,247,0.2);
              border-color: rgba(79,195,247,0.45);
              transform: translateY(-1px);
          }
          .action-button.active {
              background: linear-gradient(135deg, rgba(79,195,247,0.34) 0%, rgba(41,182,246,0.16) 100%);
              color: #ffffff;
          }
          @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
          .main-container { display: flex; height: 100vh; padding-top: 60px; }
          #map { flex: 1; height: 100%; }
          .sidebar {
              width: 420px;
              background: rgba(10,14,26,0.95);
              border-right: 1px solid rgba(79,195,247,0.2);
              overflow-y: auto;
              padding: 16px;
          }
          .panel {
              background: rgba(16,24,48,0.8);
              border: 1px solid rgba(79,195,247,0.25);
              border-radius: 12px;
              padding: 16px;
              margin-bottom: 16px;
          }
          .panel h3 {
              font-size: 14px;
              font-weight: 600;
              color: #4fc3f7;
              margin-bottom: 12px;
              display: flex;
              align-items: center;
              gap: 8px;
          }
          .ais-target {
              background: linear-gradient(135deg, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0.2) 100%);
              border-radius: 10px;
              padding: 14px;
              margin-bottom: 10px;
              border-left: 4px solid #48bb78;
              cursor: pointer;
              transition: all 0.3s;
          }
          .ais-target:hover {
              background: rgba(79,195,247,0.15);
              transform: translateX(6px);
              box-shadow: 0 4px 12px rgba(79,195,247,0.2);
          }
          .ais-target.high-risk { border-left-color: #f56565; background: linear-gradient(135deg, rgba(245,101,101,0.15) 0%, rgba(0,0,0,0.3) 100%); }
          .ais-target.medium-risk { border-left-color: #f6ad55; }
          .ais-target-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 10px;
          }
          .ais-target-type { font-weight: 700; color: #4fc3f7; font-size: 14px; }
          .ais-target-mmsi { color: #718096; font-size: 11px; }
          .ais-target-info {
              display: grid;
              grid-template-columns: 1fr 1fr;
              gap: 8px;
              font-size: 11px;
              color: #a0aec0;
          }
          .risk-badge {
              display: inline-block;
              padding: 3px 10px;
              border-radius: 6px;
              font-size: 10px;
              font-weight: 700;
              margin-left: 8px;
              text-transform: uppercase;
          }
          .risk-badge.low { background: rgba(72,187,120,0.25); color: #48bb78; }
          .risk-badge.medium { background: rgba(246,173,85,0.25); color: #f6ad55; }
          .risk-badge.high { background: rgba(245,101,101,0.25); color: #f56565; }
          .colregs-badge { background: rgba(139,92,246,0.25); color: #9f7aea; }
          .weather-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
          .weather-item {
              background: rgba(0,0,0,0.35);
              padding: 14px;
              border-radius: 10px;
              text-align: center;
          }
          .weather-label { font-size: 11px; color: #718096; margin-bottom: 6px; }
          .weather-value { font-size: 18px; font-weight: 700; color: #48bb78; }
          .port-item {
              display: flex;
              justify-content: space-between;
              align-items: center;
              padding: 12px;
              background: rgba(0,0,0,0.3);
              border-radius: 8px;
              margin-bottom: 8px;
          }
          .port-name { font-weight: 600; color: #f6ad55; }
          .port-distance { font-size: 11px; color: #718096; }
          .right-panel {
              width: 360px;
              background: rgba(10,14,26,0.95);
              border-left: 1px solid rgba(79,195,247,0.2);
              overflow-y: auto;
              padding: 16px;
          }
          .camera-feed {
              background: rgba(0,0,0,0.6);
              border-radius: 10px;
              overflow: hidden;
              margin-bottom: 16px;
              position: relative;
          }
          .camera-feed img { width: 100%; height: 200px; object-fit: cover; }
          .ar-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; }
          .ar-target {
              position: absolute;
              width: 28px; height: 28px;
              border: 3px solid #4fc3f7;
              border-radius: 50%;
              transform: translate(-50%, -50%);
              box-shadow: 0 0 20px rgba(79,195,247,0.6);
              animation: ar-pulse 2s infinite;
          }
          @keyframes ar-pulse { 0%, 100% { box-shadow: 0 0 20px rgba(79,195,247,0.6); } 50% { box-shadow: 0 0 30px rgba(79,195,247,0.9); } }
          .ar-target-label {
              position: absolute;
              top: -24px; left: 50%;
              transform: translateX(-50%);
              background: rgba(0,0,0,0.85);
              padding: 4px 8px;
              border-radius: 6px;
              font-size: 10px;
              white-space: nowrap;
              color: #fff;
              border: 1px solid rgba(79,195,247,0.4);
          }
          .ar-iceberg {
              position: absolute;
              width: 40px; height: 40px;
              background: linear-gradient(180deg, rgba(135,206,250,0.8) 0%, rgba(135,206,250,0.3) 100%);
              border: 2px solid #87cefa;
              clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
              transform: translate(-50%, -50%);
              animation: iceberg-pulse 3s infinite;
          }
          @keyframes iceberg-pulse { 0%, 100% { opacity: 0.7; } 50% { opacity: 1; } }
          .ar-canyon {
              position: absolute;
              height: 100%;
              width: 80px;
              background: linear-gradient(90deg, rgba(139,69,19,0.5) 0%, rgba(139,69,19,0.2) 50%, rgba(139,69,19,0.5) 100%);
              border-left: 3px dashed #8b4513;
              border-right: 3px dashed #8b4513;
          }
          .ar-canyon-warning {
              position: absolute;
              bottom: 80px; left: 50%;
              transform: translateX(-50%);
              background: linear-gradient(135deg, rgba(245,101,101,0.95) 0%, rgba(245,101,101,0.8) 100%);
              padding: 10px 20px;
              border-radius: 8px;
              font-size: 13px;
              font-weight: 700;
              color: #fff;
              white-space: nowrap;
              box-shadow: 0 4px 20px rgba(245,101,101,0.5);
          }
          .ar-iceberg-warning {
              position: absolute;
              top: 80px; left: 50%;
              transform: translateX(-50%);
              background: linear-gradient(135deg, rgba(135,206,250,0.95) 0%, rgba(135,206,250,0.8) 100%);
              padding: 10px 20px;
              border-radius: 8px;
              font-size: 13px;
              font-weight: 700;
              color: #fff;
              white-space: nowrap;
              box-shadow: 0 4px 20px rgba(135,206,250,0.5);
          }
          .camera-info { padding: 14px; }
          .camera-name { font-weight: 700; color: #fff; margin-bottom: 6px; font-size: 13px; }
          .camera-status { font-size: 11px; color: #48bb78; }
          .alarm-feed {
              display: flex;
              flex-direction: column;
              gap: 10px;
          }
          .alarm-card {
              background: rgba(0,0,0,0.35);
              border-radius: 10px;
              padding: 12px;
              border-left: 4px solid #48bb78;
          }
          .alarm-card.level-WARNING {
              border-left-color: #f6ad55;
          }
          .alarm-card.level-CRITICAL,
          .alarm-card.level-EMERGENCY {
              border-left-color: #f56565;
          }
          .alarm-card-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              gap: 8px;
              margin-bottom: 8px;
          }
          .alarm-card-level {
              display: inline-flex;
              align-items: center;
              justify-content: center;
              min-width: 72px;
              padding: 4px 8px;
              border-radius: 999px;
              font-size: 10px;
              font-weight: 700;
              background: rgba(72,187,120,0.2);
              color: #9ae6b4;
          }
          .alarm-card-level.WARNING {
              background: rgba(246,173,85,0.2);
              color: #fbd38d;
          }
          .alarm-card-level.CRITICAL,
          .alarm-card-level.EMERGENCY {
              background: rgba(245,101,101,0.2);
              color: #feb2b2;
          }
          .alarm-card-time {
              font-size: 11px;
              color: #718096;
          }
          .alarm-card-message {
              font-size: 12px;
              color: #e2e8f0;
              line-height: 1.5;
          }
          .alarm-card-source {
              margin-top: 8px;
              font-size: 10px;
              color: #90cdf4;
              text-transform: uppercase;
              letter-spacing: 0.04em;
          }
          .route-info { background: rgba(0,0,0,0.35); border-radius: 10px; padding: 16px; }
          .route-point {
              display: flex;
              align-items: center;
              gap: 12px;
              padding: 10px 0;
              border-bottom: 1px solid rgba(79,195,247,0.2);
          }
          .route-point:last-child { border-bottom: none; }
          .route-dot { width: 14px; height: 14px; border-radius: 50%; background: #4fc3f7; }
          .route-dot.waypoint { background: #f6ad55; }
          .route-label { font-size: 12px; color: #a0aec0; }
          .colregs-alert {
              background: linear-gradient(135deg, rgba(245,101,101,0.15) 0%, rgba(0,0,0,0.3) 100%);
              border: 1px solid #f56565;
              border-radius: 10px;
              padding: 14px;
              margin-bottom: 14px;
          }
          .colregs-alert-title {
              font-weight: 700;
              color: #f56565;
              margin-bottom: 10px;
              display: flex;
              align-items: center;
              gap: 8px;
              font-size: 13px;
          }
          .colregs-rule { font-size: 12px; color: #feb2b2; line-height: 1.6; }
          .cpa-tcpa { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 14px; }
          .cpa-item {
              background: rgba(0,0,0,0.4);
              padding: 12px;
              border-radius: 8px;
              text-align: center;
          }
          .cpa-label { font-size: 10px; color: #718096; margin-bottom: 6px; text-transform: uppercase; }
          .cpa-value { font-size: 16px; font-weight: 700; color: #fff; }
          .cpa-value.danger { color: #f56565; }
          .cpa-value.warning { color: #f6ad55; }
          .cpa-value.safe { color: #48bb78; }
          .maplibregl-map { background: #0a0e1a; }
          .maplibregl-ctrl-bottom-left, .maplibregl-ctrl-bottom-right { display: none; }
          .special-alert {
              background: linear-gradient(135deg, rgba(245,101,101,0.2) 0%, rgba(0,0,0,0.4) 100%);
              border: 2px solid #f56565;
              border-radius: 10px;
              padding: 16px;
              margin-bottom: 16px;
          }
          .special-alert-title {
              font-weight: 700;
              color: #f56565;
              margin-bottom: 10px;
              display: flex;
              align-items: center;
              gap: 10px;
              font-size: 14px;
          }
          .vr-menu {
              position: fixed;
              right: 388px;
              bottom: 18px;
              width: min(42vw, 680px);
              height: min(42vh, 360px);
              min-width: 460px;
              min-height: 280px;
              background: linear-gradient(180deg, rgba(8,16,30,0.96) 0%, rgba(6,10,20,0.94) 100%);
              border: 1px solid rgba(79,195,247,0.3);
              border-radius: 16px;
              overflow: hidden;
              z-index: 990;
              box-shadow: 0 20px 60px rgba(0,0,0,0.4);
              display: flex;
              flex-direction: column;
              backdrop-filter: blur(14px);
          }
          .vr-menu.collapsed {
              height: 68px;
              min-height: 68px;
          }
          .vr-menu.hidden {
              display: none;
          }
          .vr-toolbar {
              display: flex;
              align-items: center;
              justify-content: space-between;
              gap: 14px;
              padding: 12px 14px;
              border-bottom: 1px solid rgb
  ```
  
  ### 文件: `src/frontend/digital-twin/DataAggregator.js`
  ```js
  /**
   * DataAggregator - WorldMonitor / 本地船舶数据聚合器
   *
   * 当前阶段：方案层代码 / 结构骨架
   * 目标：统一汇总本地 API 与未来 WorldMonitor 数据源
   */
  
  export class DataAggregator {
    constructor(config = {}) {
      this.config = {
        dashboardUrl: '/api/v1/dashboard',
        coordinationUrl: '/api/v1/ai-native/coordination/status',
        missionBriefUrl: '/api/v1/ai-native/cps/mission-brief',
        fusionStateUrl: '/api/v1/ai-native/perception/fusion-state',
        worldmonitorAisUrl: '/api/v1/worldmonitor/ais',
        worldmonitorWeatherUrl: '/api/v1/worldmonitor/weather',
        refreshIntervalMs: 15000,
        cacheTtlMs: 3000,
        ...config,
      };
      this.cache = new Map();
      this._inflight = new Map();
    }
  
    async fetchJson(url) {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`fetch failed: ${url} (${response.status})`);
      }
      return response.json();
    }
  
    /**
     * TTL-aware fetch with in-flight dedup.
     * Returns cached data if fresh; coalesces concurrent requests to same URL.
     */
    async _cachedFetch(key, url) {
      const cached = this.cache.get(key);
      if (cached && (Date.now() - cached.ts) < this.config.cacheTtlMs) {
        return cached.data;
      }
      if (this._inflight.has(key)) {
        return this._inflight.get(key);
      }
      const promise = this.fetchJson(url).then(data => {
        this.cache.set(key, { ts: Date.now(), data });
        this._inflight.delete(key);
        return data;
      }).catch(err => {
        this._inflight.delete(key);
        throw err;
      });
      this._inflight.set(key, promise);
      return promise;
    }
  
    async getLocalDashboard() {
      return this._cachedFetch('dashboard', this.config.dashboardUrl);
    }
  
    async getCoordinationStatus() {
      return this._cachedFetch('ai-native:coordination', this.config.coordinationUrl);
    }
  
    async getMissionBrief() {
      return this._cachedFetch('ai-native:mission-brief', this.config.missionBriefUrl);
    }
  
    async getFusionState() {
      return this._cachedFetch('ai-native:fusion-state', this.config.fusionStateUrl);
    }
  
    async getWorldMonitorAis() {
      return this._cachedFetch('worldmonitor:ais', this.config.worldmonitorAisUrl);
    }
  
    async getWorldMonitorWeather(lat, lng) {
      const params = new URLSearchParams({ lat: String(lat), lng: String(lng) });
      return this._cachedFetch('worldmonitor:weather', `${this.config.worldmonitorWeatherUrl}?${params.toString()}`);
    }
  
    async buildUnifiedView() {
      const [dashboardResult, coordinationResult, missionResult, fusionResult] = await Promise.allSettled([
        this.getLocalDashboard(),
        this.getCoordinationStatus(),
        this.getMissionBrief(),
        this.getFusionState(),
      ]);
      const dashboard = dashboardResult.status === 'fulfilled' ? dashboardResult.value : null;
      const coordination = coordinationResult.status === 'fulfilled' ? coordinationResult.value : null;
      const missionBrief = missionResult.status === 'fulfilled' ? missionResult.value : null;
      const fusionState = fusionResult.status === 'fulfilled' ? fusionResult.value : null;
      
      // Try to get real WorldMonitor data
      let wmAis = null;
      let wmWeather = null;
      let wmStatus = 'placeholder';
      
      try {
        wmAis = await this.getWorldMonitorAis();
        if (wmAis && wmAis.source === 'real') {
          wmStatus = 'connected';
        }
      } catch (e) {
        console.warn('Failed to get WorldMonitor AIS:', e);
      }
      
      try {
        wmWeather = await this.getWorldMonitorWeather(31.2304, 121.4737);
        if (wmWeather && wmWeather.source === 'real') {
          wmStatus = 'connected';
        }
      } catch (e) {
        console.warn('Failed to get WorldMonitor weather:', e);
      }
      
      return {
        generatedAt: new Date().toISOString(),
        source: wmStatus === 'connected' ? 'real' : 'hybrid',
        local: dashboard,
        aiNative: {
          coordination,
          missionBrief,
          fusionState,
        },
        worldmonitor: {
          ais: wmAis,
          weather: wmWeather,
          status: wmStatus,
        },
      };
    }
  }
  
  export default DataAggregator;
  
  ```
  
  ### 文件: `src/frontend/digital-twin/MarineEngineeringModule.js`
  ```js
  /**
   * MarineEngineeringModule - 船舶工程增强模块
   * 
   * 为 Poseidon-X 系统添加专业船舶工程计算能力
   * 基于真实船舶理论和 IMO 规范
   */
  
  import { CatamaranStabilityCalculator } from '../physics/CatamaranStability.js';
  import { ShipMotionResponse } from '../physics/ShipMotionResponse.js';
  
  /**
   * 船舶工程计算引擎
   */
  export class MarineEngineeringModule {
    constructor(config = {}) {
      this.config = {
        // 默认双体船参数 (138 米双体客船)
        shipType: config.shipType || 'catamaran',
        length: config.length || 138,
        beam: config.beam || 26,
        draft: config.draft || 5.5,
        displacement: config.displacement || 37000,
        hullSpacing: config.hullSpacing || 80, // 两片体中心距 (m)
        GMt: config.GMt || 15,
        GMl: config.GMl || 120,
        
        // IMO 稳性衡准参数
        imoCriteria: {
          minGMt: 0.15,           // 最小初稳性高度 (m)
          maxGZ: 0.2,             // 最大 GZ 值 (m)
          maxRollAngle: 30,       // 最大横倾角 (度)
          weatherCriterion: 1.0   // 天气衡准
        }
      };
      
      // 初始化计算器
      this.stabilityCalc = new CatamaranStabilityCalculator(this.config);
      this.motionResponse = new ShipMotionResponse(this.config);
      
      // 实时状态
      this.realtimeState = {
        stability: null,
        motion: null,
        alerts: [],
        recommendations: []
      };
      
      console.log('⚓ Marine Engineering Module initialized');
    }
    
    /**
     * 实时稳定性监控
     * @param {object} sensorData - 传感器实时数据
     * @returns {object} 稳定性分析结果
     */
    monitorStability(sensorData) {
      const { roll, pitch, heave, speed, heading } = sensorData;
      
      // 计算当前 GMt（参数顺序：displacement, hullSpacing, beam）
      const gmData = this.stabilityCalc.calculateGMt(
        this.config.displacement,
        this.config.hullSpacing,
        this.config.beam
      );
      
      // 计算摇摆周期
      const rollPeriod = this.stabilityCalc.calculateRollPeriod(gmData.GMt, this.config.beam);
      const pitchPeriod = this.stabilityCalc.calculatePitchPeriod(gmData.GMt * 0.8, this.config.length);
      
      // 评估稳定性
      const assessment = this.stabilityCalc.assessStability(roll, pitch, gmData.GMt);
      
      // 检查 IMO 稳性衡准
      const imoCompliance = this.checkIMOCriteria(gmData.GMt, roll);
      
      // 生成告警
      const alerts = this.generateStabilityAlerts(assessment, imoCompliance);
      
      this.realtimeState.stability = {
        timestamp: Date.now(),
        GMt: gmData.GMt.toFixed(2),
        rollPeriod: rollPeriod.toFixed(2),
        pitchPeriod: pitchPeriod.toFixed(2),
        rollAngle: roll.toFixed(2),
        pitchAngle: pitch.toFixed(2),
        assessment,
        imoCompliance,
        alerts
      };
      
      return this.realtimeState.stability;
    }
    
    /**
     * 检查 IMO 稳性衡准
     */
    checkIMOCriteria(GMt, rollAngle) {
      const criteria = this.config.imoCriteria;
      const compliance = {
        passed: true,
        violations: [],
        warnings: []
      };
      
      // 1. 最小 GMt 检查
      if (GMt < criteria.minGMt) {
        compliance.passed = false;
        compliance.violations.push(`GMt (${GMt.toFixed(2)}m) < 最小要求 (${criteria.minGMt}m)`);
      } else if (GMt < criteria.minGMt * 1.5) {
        compliance.warnings.push(`GMt 偏低 (${GMt.toFixed(2)}m)`);
      }
      
      // 2. 横倾角检查
      if (Math.abs(rollAngle) > criteria.maxRollAngle) {
        compliance.passed = false;
        compliance.violations.push(`横倾角 (${Math.abs(rollAngle).toFixed(1)}°) > 最大允许 (${criteria.maxRollAngle}°)`);
      }
      
      // 3. GZ 曲线检查（简化）
      const gzCurve = this.stabilityCalc.calculateStabilityCurve(GMt);
      const maxGZ = Math.max(...gzCurve.map(p => p.GZ));
      
      if (maxGZ < criteria.maxGZ) {
        compliance.warnings.push(`最大 GZ (${maxGZ.toFixed(3)}m) 偏小`);
      }
      
      return compliance;
    }
    
    /**
     * 生成稳定性告警
     */
    generateStabilityAlerts(assessment, imoCompliance) {
      const alerts = [];
      
      // IMO 违规告警
      imoCompliance.violations.forEach(violation => {
        alerts.push({
          level: 'critical',
          type: 'IMO_VIOLATION',
          message: `IMO 稳性违规：${violation}`,
          action: '立即减速并调整航向'
        });
      });
      
      // 稳定性警告
      assessment.warnings.forEach(warning => {
        alerts.push({
          level: 'warning',
          type: 'STABILITY_WARNING',
          message: warning,
          action: '密切监控船舶状态'
        });
      });
      
      // 稳定性问题
      assessment.issues.forEach(issue => {
        alerts.push({
          level: 'critical',
          type: 'STABILITY_ISSUE',
          message: issue,
          action: '立即采取纠正措施'
        });
      });
      
      return alerts;
    }
    
    /**
     * 运动响应分析
     * @param {object} waveData - 波浪数据
     * @returns {object} 运动分析结果
     */
    analyzeMotion(waveData) {
      const { significantWaveHeight, meanWavePeriod, waveDirection } = waveData;
      
      // 模拟不规则波中的运动
      const motionData = this.motionResponse.simulateIrregularMotion(
        significantWaveHeight,
        meanWavePeriod,
        60, // 60 秒模拟
        0.5 // 0.5 秒步长
      );
      
      // 计算统计参数
      const stats = this.motionResponse.calculateMotionStatistics();
      
      // 晕船风险评估
      const comfort = this.motionResponse.assessMotionComfort();
      
      // 计算 RAO
      const rao = {
        roll: this.motionResponse.calculateRAO('roll', meanWavePeriod, waveDirection),
        pitch: this.motionResponse.calculateRAO('pitch', meanWavePeriod, waveDirection),
        heave: this.motionResponse.calculateRAO('heave', meanWavePeriod, waveDirection)
      };
      
      this.realtimeState.motion = {
        timestamp: Date.now(),
        waveConditions: waveData,
        statistics: stats,
        comfort,
        rao,
        motionData
      };
      
      return this.realtimeState.motion;
    }
    
    /**
     * 能效分析
     * @param {object} engineData - 主机数据
     * @param {object} resistanceData - 阻力数据
     * @returns {object} 能效分析结果
     */
    analyzeEfficiency(engineData, resistanceData) {
      const { rpm, torque, fuelRate } = engineData;
      const { totalResistance, speed } = resistanceData;
      
      // 计算有效功率
      const effectivePower = totalResistance * speed / 1000; // kW
      
      // 计算轴功率
      const shaftPower = 2 * Math.PI * rpm * torque / 60000; // kW
      
      // 计算推进效率
      const propulsiveEfficiency = effectivePower / shaftPower;
      
      // 计算燃油消耗率
      const sfc = fuelRate / shaftPower; // g/kWh
      
      // 能效评估
      const efficiencyScore = this.calculateEfficiencyScore(propulsiveEfficiency, sfc);
      
      return {
        timestamp: Date.now(),
        effectivePower: effectivePower.toFixed(1),
        shaftPower: shaftPower.toFixed(1),
        propulsiveEfficiency: (propulsiveEfficiency * 100).toFixed(1) + '%',
        sfc: sfc.toFixed(1),
        efficiencyScore,
        recommendations: this.getEfficiencyRecommendations(efficiencyScore)
      };
    }
    
    /**
     * 计算能效评分
     */
    calculateEfficiencyScore(propulsiveEfficiency, sfc) {
      let score = 100;
      
      // 推进效率评分 (理想值 0.6-0.7)
      if (propulsiveEfficiency < 0.5) {
        score -= 30;
      } else if (propulsiveEfficiency < 0.6) {
        score -= 15;
      }
      
      // 燃油消耗率评分 (理想值 < 180 g/kWh)
      if (sfc > 220) {
        score -= 30;
      } else if (sfc > 200) {
        score -= 15;
      }
      
      return {
        score: Math.max(0, score),
        level: score >= 80 ? '优秀' : score >= 60 ? '良好' : score >= 40 ? '一般' : '需改进'
      };
    }
    
    /**
     * 获取能效优化建议
     */
    getEfficiencyRecommendations(efficiencyScore) {
      const recommendations = [];
      
      if (efficiencyScore.score < 60) {
        recommendations.push('建议清理船底海生物，减少摩擦阻力');
        recommendations.push('检查螺旋桨状态，优化螺距比');
      }
      
      if (efficiencyScore.score < 80) {
        recommendations.push('优化航速，避免主机超负荷运行');
        recommendations.push('考虑安装节能装置（如预旋导轮）');
      }
      
      return recommendations;
    }
    
    /**
     * 获取实时状态摘要
     */
    getStatusSummary() {
      return {
        stability: this.realtimeState.stability ? {
          GMt: this.realtimeState.stability.GMt,
          rollAngle: this.realtimeState.stability.rollAngle,
          status: this.realtimeState.stability.assessment.stable ? '✅ 稳定' : '⚠️ 不稳定'
        } : null,
        motion: this.realtimeState.motion ? {
          comfortLevel: this.realtimeState.motion.comfort?.comfortLevel || '未知',
          motionSicknessIndex: this.realtimeState.motion.comfort?.motionSicknessIndex?.toFixed(2) || 'N/A'
        } : null,
        alerts: this.realtimeState.alerts.length
      };
    }
  }
  
  export default MarineEngineeringModule;
  
  ```
  
  ### 文件: `src/frontend/digital-twin/PoseidonX.js`
  ```js
  /**
   * Poseidon-X - 主系统入口
   * 
   * Software 3.0 Edition
   * 
   * 这是整个 Poseidon-X 系统的统一入口，
   * 集成了 Layer 1、Layer 2 和 Layer 3 的所有组件。
   */
  
  // Layer 1: 交互界面
  import { BridgeChat } from './layer1-interface/BridgeChat.js';
  import { DigitalTwinMap } from './layer1-interface/DigitalTwinMap.js';
  import { ContextWindow } from './layer1-interface/ContextWindow.js';
  import { MarineEngineeringPanel } from './layer1-interface/MarineEngineeringPanel.js';
  import { WeatherRoutingPanel } from './layer1-interface/WeatherRoutingPanel.js';
  import { CrewFatiguePanel } from './layer1-interface/CrewFatiguePanel.js';
  import { AnchorWatchPanel } from './layer1-interface/AnchorWatchPanel.js';
  import { HullStressPanel } from './layer1-interface/HullStressPanel.js';
  import { PowerManagementPanel } from './layer1-interface/PowerManagementPanel.js';
  import { DPStatusPanel } from './layer1-interface/DPStatusPanel.js';
  import { VDRStatusPanel } from './layer1-interface/panels/VDRStatusPanel.js';
  import { AlarmPanel } from './layer1-interface/panels/AlarmPanel.js';
  import { TankLevelPanel } from './layer1-interface/panels/TankLevelPanel.js';
  import { CommsStatusPanel } from './layer1-interface/panels/CommsStatusPanel.js';
  import { MOBPanel } from './layer1-interface/panels/MOBPanel.js';
  import { PropulsionPanel } from './layer1-interface/panels/PropulsionPanel.js';
  import { SafetyPanel } from './layer1-interface/panels/SafetyPanel.js';
  import { AutopilotPanel } from './layer1-interface/panels/AutopilotPanel.js';
  import { RudderPanel } from './layer1-interface/panels/RudderPanel.js';
  
  // Layer 2: 智能体
  import { NavigatorAgent } from './layer2-agents/NavigatorAgent.js';
  import { EngineerAgent } from './layer2-agents/EngineerAgent.js';
  import { StewardAgent } from './layer2-agents/StewardAgent.js';
  import { SafetyAgent } from './layer2-agents/SafetyAgent.js';
  import { AgentOrchestrator } from './layer2-agents/AgentOrchestrator.js';
  
  // Layer 3: 开发平台
  import { VibeGenerator } from './layer3-platform/VibeGenerator.js';
  import { SimulationValidator } from './layer3-platform/SimulationValidator.js';
  import { LLMJudge } from './layer3-platform/LLMJudge.js';
  
  import { EventEmitter } from '../utils/EventEmitter.js';
  
  /**
   * Poseidon-X 主系统类
   */
  export class PoseidonX extends EventEmitter {
    /**
     * 从 localStorage 加载配置
     * @private
     */
    _loadConfigFromStorage() {
      if (typeof localStorage === 'undefined') return {};
      try {
        const saved = localStorage.getItem('poseidon_config');
        if (saved) {
          return JSON.parse(saved);
        }
      } catch (error) {
        console.warn('⚠️ 加载配置失败:', error);
      }
      return {};
    }
    constructor(scene, camera, config = {}) {
      super();
      
      this.scene = scene;
      this.camera = camera;
      
      // 优先从 localStorage 加载用户配置（避免被默认值覆盖）
      const savedConfig = this._loadConfigFromStorage();
      
      this.config = {
        enableBridgeChat: config.enableBridgeChat !== false,
        enableDigitalTwin: config.enableDigitalTwin !== false,
        enableVoice: config.enableVoice || false,
        llmProvider: savedConfig.llmProvider || config.llmProvider || 'deepseek',
        model: savedConfig.model || config.model || 'deepseek-chat',
        apiKey: savedConfig.apiKey || config.apiKey || '',
        apiEndpoint: savedConfig.apiEndpoint || config.apiEndpoint || 'https://api.deepseek.com/v1',
        temperature: savedConfig.temperature || config.temperature || 0.7,
        ...config
      };
      
      // 系统状态
      this.status = 'initializing';
      this.initialized = false;
      
      // Layer 1 组件
      this.bridgeChat = null;
      this.digitalTwinMap = null;
      this.contextWindow = null;
      
      // Layer 2 组件
      this.agents = {
        navigator: null,
        engineer: null,
        steward: null,
        safety: null
      };
      this.orchestrator = null;
      
      // Layer 3 组件（开发模式）
      this.devMode = config.devMode || false;
      this.vibeGenerator = null;
      this.simulationValidator = null;
      this.llmJudge = null;
      
      // 船舶上下文（全局状态）
      this.shipContext = {
        position: { lat: 0, lon: 0, heading: 0, speed: 0 },
        sensors: new Map(),
        environment: {},
        equipment: {},
        crew: {},
        alerts: []
      };
      
      console.log('🌊 Poseidon-X System initializing...');
    }
    
    /**
     * 初始化系统
     */
    async initialize() {
      console.log('🚀 Starting Poseidon-X initialization...');
      
      try {
        // 1. 初始化 Layer 1（交互界面）
        await this._initializeLayer1();
        
        // 2. 初始化 Layer 2（智能体）
        await this._initializeLayer2();
        
        // 3. 初始化 Layer 3（开发平台，仅开发模式）
        if (this.devMode) {
          await this._initializeLayer3();
        }
        
        // 4. 连接各层
        this._connectLayers();
        
        this.status = 'ready';
        this.initialized = true;
        
        console.log('✅ Poseidon-X initialized successfully!');
        console.log(`   Mode: ${this.devMode ? 'Development' : 'Production'}`);
        console.log(`   Agents: ${Object.keys(this.agents).length}`);
        
        // 触发事件
        this.emit('system:ready', {
          agents: Object.keys(this.agents),
          devMode: this.devMode
        });
        
        // 显示欢迎消息
        if (this.bridgeChat) {
          this.bridgeChat._addMessage('system', 
            '🌊 Poseidon-X 智能船舶系统已就绪。\n' +
            `✅ ${Object.keys(this.agents).length} 个智能体已激活\n` +
            `📡 全船传感器数据实时监控中\n\n` +
            '您可以通过自然语言与我对话，我会协调各个专业智能体为您服务。'
          );
        }
        
        return this;
        
      } catch (error) {
        this.status = 'error';
        console.error('❌ Poseidon-X initialization failed:', error);
        throw error;
      }
    }
    
    /**
     * 初始化 Layer 1
     * @private
     */
    async _initializeLayer1() {
      console.log('📱 Initializing Layer 1: User Interface...');
      
      // Context Window（上下文窗口）
      this.contextWindow = new ContextWindow({
        maxTokens: 128000,
        compressionThreshold: 0.8
      });
      
      // 设置系统 Vibe
      this.contextWindow.setSystemVibe(`你是 Poseidon-X 智能船舶系统的核心 AI。
  你的职责是协调船上的各个专业智能体，为船长和船员提供智能决策支持。`);
      
      // Digital Twin Map（数字孪生海图）
      if (this.config.enableDigitalTwin) {
        this.digitalTwinMap = new DigitalTwinMap(this.scene, this.camera, {
          showAIS: true,
          showRoute: true
        });
        
        console.log('  ✅ Digital Twin Map initialized');
      }
      
      // Bridge Chat（舰桥对话中心）- 配置由 BridgeChat 自己从 localStorage 加载
      if (this.config.enableBridgeChat) {
        this.bridgeChat = new BridgeChat({
          vibe: `你是 Poseidon-X 的核心 AI 助手，协调全船的智能体团队。`
        });
        
        // 监听消息事件
        this.bridgeChat.on('message:sent', (data) => {
          this.emit('chat:message', data);
        });
        
        console.log('  ✅ Bridge Chat initialized');
      }
      
      // Marine Engineering Panel（船舶工程监控面板）
      this.marinePanel = new MarineEngineeringPanel({
        shipType: 'catamaran',
        length: 138,
        beam: 26,
        draft: 5.5,
        displacement: 37000,
        hullSpacing: 80
      });
      
      // 在页面中查找或创建容器
      const marineContainer = document.getElementById('marine-engineering-panel');
      if (marineContainer) {
        this.marinePanel.initialize(marineContainer);
        console.log('  ✅ Marine Engineering Panel initialized');
      }
  
      // Weather Routing Panel（天气航线面板）
      const wrContainer = document.getElementById('weather-routing-panel');
      if (wrContainer) {
        this.weatherRoutingPanel = new WeatherRoutingPanel(wrContainer);
        await this.weatherRoutingPanel.initialize();
        console.log('  ✅ Weather Routing Panel initialized');
      }
  
      // Crew Fatigue Panel（船员疲劳面板）
      const cfContainer = document.getElementById('crew-fatigue-panel');
      if (cfContainer) {
        this.crewFatiguePanel = new CrewFatiguePanel(cfContainer);
        await this.crewFatiguePanel.initialize();
        console.log('  ✅ Crew Fatigue Panel initialized');
      }
  
      // Anchor Watch Panel（锚泊监控面板）
      const awContainer = document.getElementById('anchor-watch-panel');
      if (awContainer) {
        this.anchorWatchPanel = new AnchorWatchPanel(awContainer);
        await this.anchorWatchPanel.initialize();
        console.log('  ✅ Anchor Watch Panel initialized');
      }
  
      // Hull Stress Panel（船体应力监测面板）
      const hsContainer = document.getElementById('hull-stress-panel');
      if (hsContainer) {
        this.hullStressPanel = new HullStressPanel(hsContainer);
        await this.hullStressPanel.initialize();
        console.log('  ✅ Hull Stress Panel initialized');
      }
  
      // Power Management Panel（电力管理面板）
      const pmContainer = document.getElementById('power-management-panel');
      if (pmContainer) {
        this.powerManagementPanel = new PowerManagementPanel(pmContainer);
        await this.powerManagementPanel.initialize();
        console.log('  ✅ Power Management Panel initialized');
      }
  
      // DP Status Panel（动态定位面板）
      const dpContainer = document.getElementById('dp-status-panel');
      if (dpContainer) {
        this.dpStatusPanel = new DPStatusPanel(dpContainer);
        await this.dpStatusPanel.initialize();
        console.log('  ✅ DP Status Panel initialized');
      }
  
      // VDR Status Panel（VDR 状态面板）
      const vdrContainer = document.getElementById('vdr-status-panel');
      if (vdrContainer) {
        this.vdrStatusPanel = new VDRStatusPanel(vdrContainer);
        await this.vdrStatusPanel.initialize();
        console.log('  ✅ VDR Status Panel initialized');
      }
  
      // Alarm Panel（告警中心面板）
      const alarmContainer = document.getElementById('alarm-panel');
      if (alarmContainer) {
        this.alarmPanel = new AlarmPanel(alarmContainer);
        await this.alarmPanel.initialize();
        console.log('  ✅ Alarm Panel initialized');
      }
  
      // Tank Level Panel（液舱水位面板）
      const tankContainer = document.getElementById('tank-level-panel');
      if (tankContainer) {
        this.tankLevelPanel = new TankLevelPanel(tankContainer);
        await this.tankLevelPanel.initialize();
        console.log('  ✅ Tank Level Panel initialized');
      }
  
      // Comms Status Panel（通信状态面板）
      const commsContainer = document.getElementById('comms-status-panel');
      if (commsContainer) {
        this.commsStatusPanel = new CommsStatusPanel(commsContainer);
        await this.commsStatusPanel.initialize();
        console.log('  ✅ Comms Status Panel initialized');
      }
  
      // MOB Panel（落水告警面板）
      const mobContainer = document.getElementById('mob-panel');
      if (mobContainer) {
        this.mobPanel = new MOBPanel(mobContainer);
        await this.mobPanel.initialize();
        console.log('  ✅ MOB Panel initialized');
      }
  
      // Propulsion Panel（推进系统面板）
      const propContainer = document.getElementById('propulsion-panel');
      if (propContainer) {
        this.propulsionPanel = new PropulsionPanel(propContainer);
        await this.propulsionPanel.initialize();
        console.log('  ✅ Propulsion Panel initialized');
      }
  
      // Safety Panel（安全系统面板）
      const safetyContainer = document.getElementById('safety-panel');
      if (safetyContainer) {
        this.safetyPanel = new SafetyPanel(safetyContainer);
        await this.safetyPanel.initialize();
        console.log('  ✅ Safety Panel initialized');
      }
  
      // Autopilot Panel（自动舵面板）
      const apContainer = document.getElementById('autopilot-panel');
      if (apContainer) {
        this.autopilotPanel = new AutopilotPanel(apContainer);
        await this.autopilotPanel.initialize();
        console.log('  ✅ Autopilot Panel initialized');
      }
  
      // Rudder Panel（舵机面板）
      const rudderContainer = document.getElementById('rudder-panel');
      if (rudderContainer) {
        this.rudderPanel = new RudderPanel(rudderContainer);
        await this.rudderPanel.initialize();
        console.log('  ✅ Rudder Panel initialized');
      }
  
      console.log('✅ Layer 1 initialized');
    }
    
    /**
     * 初始化 Layer 2
     * @private
     */
    async _initializeLayer2() {
      console.log('🤖 Initializing Layer 2: AI Crew...');
      
      // 创建 Agent Orchestrator
      this.orchestrator = new AgentOrchestrator({
        maxParallelAgents: 4,
        timeout: 30000
      });
      
      // 创建各个专业智能体（使用从 localStorage 加载的配置）
      this.agents.navigator = new NavigatorAgent({
        llmProvider: this.config.llmProvider,
        model: this.config.model,
        apiKey: this.config.apiKey,
        apiEndpoint: this.config.apiEndpoint
      });
      
      this.agents.engineer = new EngineerAgent({
        llmProvider: this.config.llmProvider,
        model: this.config.model,
        apiKey: this.config.apiKey,
        apiEndpoint: this.config.apiEndpoint
      });
      
      this.agents.steward = new StewardAgent({
        llmProvider: this.config.llmProvider,
        model: this.config.model,
        apiKey: this.config.apiKey,
        apiEndpoint: this.config.apiEndpoint
      });
      
      this.agents.safety = new SafetyAgent({
        llmProvider: this.config.llmProvider,
        model: this.config.model,
        apiKey: this.config.apiKey,
        apiEndpoint: this.config.apiEndpoint
      });
      
      // 注册到 Orchestrator
      this.orchestrator.registerAgent('navigator', this.agents.navigator);
      this.orchestrator.registerAgent('engineer', this.agents.engineer);
      this.orchestrator.registerAgent('steward', this.agents.steward);
      this.orchestrator.registerAgent('safety', this.agents.safety);
      
      // 监听 Agent 事件
      this.orchestrator.on('task:completed', (data) => {
        console.log(`✅ Task completed by ${data.agent}: ${data.task}`);
        this.emit('agent:task_completed', data);
      });
      
      console.log('✅ Layer 2 initialized');
      console.log(`  ⚓ Navigator Agent ready`);
      console.log(`  ⚙️ Engineer Agent ready`);
      console.log(`  🏠 Steward Agent ready`);
      console.log(`  🛡️ Safety Agent ready`);
    }
    
    /**
     * 初始化 Layer 3（开发模式）
     * @private
     */
    async _initializeLayer3() {
      console.log('🧬 Initializing Layer 3: Intelligence Foundry (Dev Mode)...');
      
      // Vibe Generator
      this.vibeGenerator = new VibeGenerator({
        llmProvider: this.config.llmProvider,
        model: this.config.model,
        outputLanguage: 'javascript'
      });
      
      // Simulation Validator
      this.simulationValidator = new SimulationValidator({
        scenarioCount: 100,
        passThreshold: 0.85
      });
      
      // LLM Judge
      this.llmJudge = new LLMJudge({
        llmProvider: this.config.llmProvider,
        model: this.config.model,
        strictness: 0.8
      });
      
      console.log('✅ Layer 3 initialized (Development Platform)');
    }
    
    /**
     * 连接各层
     * @private
     */
    _connectLayers() {
      // 连接 Bridge Chat 和 Orchestrator
      if (this.bridgeChat && this.orchestrator) {
        // 注册 Agents 到 Bridge Chat
        Object.entries(this.agents).forEach(([name, agent]) => {
          this.bridgeChat.registerAgent(name, agent);
        });
      }
      
      // 连接 Digital Twin Map 和 Agents
      if (this.digitalTwinMap) {
        // Navigator Agent 可以在地图上高亮目标
        this.agents.navigator.on('collision:risk', (data) => {
          this.digitalTwinMap.highlight(data.target, '碰撞风险');
        });
      }
      
      // 连接 Context Window 和 Bridge Chat
      if (this.contextWindow && this.bridgeChat) {
        // Context Window 更新时通知 Bridge Chat
        this.contextWi
  ```
  
  ### 文件: `src/frontend/digital-twin/PoseidonXIntegration.js`
  ```js
  /**
   * Poseidon-X Integration Module
   * 
   * 将 Poseidon-X AI 系统与现有的数字孪生系统深度集成
   * - AI Agent 可以控制真实的船舶模型
   * - AI Agent 可以读取真实的传感器数据
   * - AI Agent 可以在 3D 场景中进行操作
   * - Bridge Chat 可以通过自然语言控制整个系统
   */
  
  import { createPoseidonX } from './PoseidonX.js';
  
  export class PoseidonXIntegration {
    constructor(systemComponents) {
      this.components = systemComponents;
      this.poseidonSystem = null;
      this.initialized = false;
      
      // 必需的组件
      this.requiredComponents = [
        'scene', 'camera', 'shipController', 'simulatorEngine', 
        'weatherSystem', 'virtualDataSource'
      ];
    }
    
    /**
     * 初始化集成
     */
    async initialize() {
      console.log('🌊 ========== Poseidon-X Integration Starting ==========');
      
      // 验证必需组件
      for (const component of this.requiredComponents) {
        if (!this.components[component]) {
          throw new Error(`Required component missing: ${component}`);
        }
      }
      
      // 创建 Poseidon-X 系统
      this.poseidonSystem = await createPoseidonX(
        this.components.scene,
        this.components.camera,
        {
          enableBridgeChat: true,
          enableDigitalTwin: true,
          enableVoice: false
        }
      );
      
      // 注入现有组件
      this._injectComponents();
      
      // 注册真实工具
      this._registerRealTools();
      
      // 启动数据同步
      this._startDataSync();
      
      // 监听 Bridge Chat 事件
      this._setupEventListeners();
      
      this.initialized = true;
      
      console.log('✅ ========== Poseidon-X Integration Complete ==========');
      
      return this.poseidonSystem;
    }
    
    /**
     * 注入现有组件
     * @private
     */
    _injectComponents() {
      // 将现有系统组件绑定到 Poseidon
      this.poseidonSystem.shipController = this.components.shipController;
      this.poseidonSystem.simulatorEngine = this.components.simulatorEngine;
      this.poseidonSystem.weatherSystem = this.components.weatherSystem;
      this.poseidonSystem.virtualDataSource = this.components.virtualDataSource;
      this.poseidonSystem.world = this.components.world;
      this.poseidonSystem.cabinManager = this.components.cabinManager;
      
      console.log('✅ System components injected to Poseidon-X');
    }
    
    /**
     * 注册真实工具
     * @private
     */
    _registerRealTools() {
      this._registerNavigatorTools();
      this._registerEngineerTools();
      this._registerStewardTools();
      this._registerSafetyTools();
      
      console.log('✅ Real-world tools registered for all Agents');
    }
    
    /**
     * Navigator Agent 真实工具
     * @private
     */
    _registerNavigatorTools() {
      const navigator = this.poseidonSystem.agents.navigator;
      
      // 设置航向
      navigator.registerTool('setShipHeading', async (params) => {
        const { heading } = params;
        
        if (this.components.shipController && this.components.shipController.body) {
          const radians = (heading * Math.PI) / 180;
          const quaternion = new CANNON.Quaternion();
          quaternion.setFromAxisAngle(new CANNON.Vec3(0, 1, 0), radians);
          this.components.shipController.body.quaternion.copy(quaternion);
          
          console.log(`⚓ Navigator: 航向已设置到 ${heading}°`);
          
          return { success: true, newHeading: heading };
        }
        
        return { success: false, error: 'Ship controller not available' };
      }, 'Set ship heading in 3D scene');
      
      // 在地图上添加航路点
      navigator.registerTool('addWaypointToMap', async (params) => {
        const { waypoint } = params;
        
        if (this.poseidonSystem.digitalTwinMap) {
          // 在 3D 场景中绘制航路点
          const waypoints = [
            { x: 0, z: 0 },
            { x: waypoint.x, z: waypoint.z }
          ];
          
          this.poseidonSystem.digitalTwinMap.drawRoute(waypoints);
          
          console.log(`⚓ Navigator: 航路点已添加到地图`);
          
          return { success: true };
        }
        
        return { success: false };
      }, 'Add waypoint to 3D map');
    }
    
    /**
     * Engineer Agent 真实工具
     * @private
     */
    _registerEngineerTools() {
      const engineer = this.poseidonSystem.agents.engineer;
      
      // 读取真实的传感器数据
      engineer.registerTool('readRealSensor', async (params) => {
        const { sensorId } = params;
        
        if (this.components.virtualDataSource) {
          const allData = this.components.virtualDataSource.getAllData();
          
          let value = null;
          
          // 解析传感器路径，例如 "MainEngine.ExhaustTemp"
          if (sensorId.includes('MainEngine.ExhaustTemp')) {
            value = allData.ship?.mainEngine?.exhaustTemp;
          } else if (sensorId.includes('MainEngine.RPM')) {
            value = allData.ship?.mainEngine?.rpm;
          } else if (sensorId.includes('FuelTank.Level')) {
            value = allData.ship?.fuel?.level;
          }
          
          console.log(`⚙️ Engineer: 读取传感器 ${sensorId} = ${value}`);
          
          return { sensorId, value, timestamp: Date.now() };
        }
        
        return { sensorId, value: null };
      }, 'Read real-time sensor data from ship');
      
      // 调整主机转速
      engineer.registerTool('adjustEngineRPM', async (params) => {
        const { rpm } = params;
        
        if (this.components.virtualDataSource) {
          const allData = this.components.virtualDataSource.getAllData();
          if (allData.ship && allData.ship.mainEngine) {
            allData.ship.mainEngine.rpm = rpm;
            
            console.log(`⚙️ Engineer: 主机转速已调整到 ${rpm} RPM`);
            
            return { success: true, newRPM: rpm };
          }
        }
        
        return { success: false };
      }, 'Adjust main engine RPM');
    }
    
    /**
     * Steward Agent 真实工具
     * @private
     */
    _registerStewardTools() {
      const steward = this.poseidonSystem.agents.steward;
      
      // 查询真实舱室状态
      steward.registerTool('queryCabinStatus', async (params) => {
        const { cabinId } = params;
        
        if (this.components.cabinManager) {
          const cabin = this.components.cabinManager.getCabin(cabinId);
          
          if (cabin) {
            console.log(`🏠 Steward: 查询舱室 ${cabin.name}`);
            
            return {
              cabinId,
              name: cabin.name,
              position: cabin.position,
              temperature: 24 + Math.random() * 2,
              humidity: 50 + Math.random() * 10,
              co2: 600 + Math.random() * 200
            };
          }
        }
        
        return { cabinId, status: 'not_found' };
      }, 'Query real cabin status');
    }
    
    /**
     * Safety Agent 真实工具
     * @private
     */
    _registerSafetyTools() {
      const safety = this.poseidonSystem.agents.safety;
      
      // 在 3D 场景中触发可视化警报
      safety.registerTool('trigger3DAlert', async (params) => {
        const { alertType, location } = params;
        
        if (this.poseidonSystem.digitalTwinMap) {
          // 高亮警报位置
          this.poseidonSystem.digitalTwinMap.highlight(
            location || { x: 0, z: 0 },
            `🚨 ${alertType}`
          );
          
          console.log(`🛡️ Safety: 3D 警报已触发 - ${alertType}`);
          
          return { success: true };
        }
        
        return { success: false };
      }, 'Trigger visual alert in 3D scene');
    }
    
    /**
     * 启动数据同步
     * @private
     */
    _startDataSync() {
      // 每秒同步一次数据
      setInterval(() => {
        if (!this.components.shipController || !this.components.virtualDataSource) return;
        
        const body = this.components.shipController.body;
        if (!body) return;
        
        // 收集传感器数据
        const sensorData = new Map();
        const allData = this.components.virtualDataSource.getAllData();
        
        if (allData && allData.ship) {
          // 主机数据
          if (allData.ship.mainEngine) {
            sensorData.set('MainEngine.RPM', allData.ship.mainEngine.rpm);
            sensorData.set('MainEngine.ExhaustTemp', allData.ship.mainEngine.exhaustTemp);
            sensorData.set('MainEngine.Load', allData.ship.mainEngine.load);
          }
          
          // 燃油数据
          if (allData.ship.fuel) {
            sensorData.set('FuelTank.Level', allData.ship.fuel.level);
            sensorData.set('FuelTank.FlowRate', allData.ship.fuel.flowRate);
            sensorData.set('FuelTank.Remaining', allData.ship.fuel.remaining);
          }
          
          // 舵机数据
          if (allData.ship.rudder) {
            sensorData.set('Rudder.Angle', allData.ship.rudder.angle);
          }
          
          // 推进系统
          if (allData.ship.propulsion) {
            sensorData.set('Propulsion.Efficiency', allData.ship.propulsion.efficiency * 100);
          }
        }
        
        // 天气数据
        const weather = this.components.weatherSystem ? 
          this.components.weatherSystem.getWeatherState() : {};
        
        // 更新 Poseidon 上下文
        this.poseidonSystem.updateShipContext({
          position: {
            x: body.position.x,
            y: body.position.y,
            z: body.position.z,
            heading: 0,
            speed: Math.sqrt(
              body.velocity.x ** 2 + 
              body.velocity.z ** 2
            )
          },
          sensors: sensorData,
          environment: {
            windSpeed: weather.windSpeed || 0,
            windDirection: weather.windDirection || 0,
            rainIntensity: weather.rainIntensity || 0,
            visibility: weather.visibility || 1.0,
            seaState: weather.seaState || 'calm'
          },
          equipment: {
            mainEngine: allData?.ship?.mainEngine,
            fuel: allData?.ship?.fuel,
            rudder: allData?.ship?.rudder
          }
        });
      }, 1000);
      
      console.log('✅ Data sync started (1Hz)');
    }
    
    /**
     * 设置事件监听
     * @private
     */
    _setupEventListeners() {
      // 监听 Agent 任务完成事件
      this.poseidonSystem.on('agent:task_completed', (data) => {
        console.log(`✅ Agent task completed: ${data.agent} - ${data.task}`);
        
        // 如果是 Navigator 调整了航向，在 3D 场景中显示
        if (data.agent === 'NavigatorAgent' && data.result.type === 'course_speed_adjustment') {
          // 可以在这里添加视觉反馈
        }
      });
      
      // 监听上下文更新事件
      this.poseidonSystem.on('context:updated', (context) => {
        // Context 已更新，可以触发其他系统的响应
      });
    }
    
    /**
     * 执行自然语言命令（与现有系统交互）
     */
    async executeNaturalLanguageCommand(command) {
      if (!this.initialized) {
        throw new Error('Poseidon-X not initialized');
      }
      
      console.log(`🌊 Executing command: "${command}"`);
      
      // 特殊命令：直接控制现有系统
      if (command.includes('台风') || command.includes('typhoon')) {
        const level = parseInt(command.match(/\d+/)?.[0]) || 12;
        if (this.components.weatherSystem) {
          this.components.weatherSystem.setTyphoonLevel(level);
          return {
            success: true,
            message: `已设置 ${level} 级台风`,
            agent: 'system'
          };
        }
      }
      
      if (command.includes('稳定') || command.includes('stabilize')) {
        if (this.components.shipController && this.components.stabilityAnalyzer) {
          const result = this.components.stabilityAnalyzer.stabilize(
            this.components.shipController.body,
            this.components.clock.elapsedTime,
            this.components.config,
            this.c
  ```
  
  (后续文件因 token 预算已省略)
  
  (后续文件因 token 预算已省略)
  
  (后续文件因 token 预算已省略)
  
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
⚡ 使用 DeepSeek API 直连 (快速模式)...

🔗 API: api.deepseek.com | 模型: deepseek-chat
────────────────────────────────────────────────────────────

# 任务分解：数字孪生AR-CAS Pro菜单实现

## 📋 任务概述
**目标**：实现数字孪生系统中AR-CAS Pro（增强现实碰撞避免系统专业版）的功能菜单，当前菜单为空白状态。

**当前状态**：`src/frontend/worldmonitor-ar-cas-pro.html` 文件已存在基本框架，但菜单功能未实现。

## 🔍 现状分析

### 现有文件结构
1. **AR-CAS Pro主页面**：`src/frontend/worldmonitor-ar-cas-pro.html`
   - 已有完整的UI框架和样式
   - 包含地图、侧边栏、摄像头视图等组件
   - VR菜单部分（`.vr-menu`）已定义但功能未实现

2. **相关依赖系统**：
   - Poseidon-X AI系统：`src/frontend/digital-twin/PoseidonX.js`
   - 数据聚合器：`src/frontend/digital-twin/DataAggregator.js`
   - 船舶工程模块：`src/frontend/digital-twin/MarineEngineeringModule.js`
   - 集成模块：`src/frontend/digital-twin/PoseidonXIntegration.js`

3. **后端支持**：
   - 多个通道（channels）支持AIS、天气、警报等数据
   - 智能体系统支持AI决策

## 🎯 任务分解

### 阶段1：需求分析与设计（1-2天）

#### 1.1 功能需求分析
- [ ] **确定AR-CAS Pro核心功能**：
  - AIS目标实时显示与风险评估
  - COLREGS（国际海上避碰规则）合规性检查
  - CPA/TCPA（最近会遇点/时间）计算
  - 增强现实叠加显示（摄像头视图）
  - 天气与海况影响分析
  - 航线规划与避碰建议

#### 1.2 技术架构设计
- [ ] **前端架构**：
  - 确定与现有Poseidon-X系统的集成方式
  - 设计数据流：DataAggregator → AR-CAS Pro → 可视化
  - 定义组件通信协议

- [ ] **后端接口**：
  - 分析现有API端点可用性
  - 设计AR-CAS专用API（如需）
  - 确定实时数据推送机制

#### 1.3 UI/UX设计细化
- [ ] **菜单结构设计**：
  - 主菜单项定义（文件、视图、工具、设置等）
  - 子菜单层级规划
  - 快捷键映射

### 阶段2：基础框架实现（2-3天）

#### 2.1 VR菜单组件开发
- [ ] **创建VR菜单JavaScript模块**：
  - 位置：`src/frontend/digital-twin/ar-cas-pro/VRMenu.js`
  - 功能：菜单显示/隐藏、折叠/展开、动态内容加载

- [ ] **菜单状态管理**：
  - 实现`collapsed`和`hidden`状态切换
  - 添加动画效果
  - 响应式布局适配

#### 2.2 菜单内容实现
- [ ] **主菜单栏**：
  - 文件菜单（导入/导出航线、保存配置）
  - 视图菜单（图层控制、显示选项）
  - 工具菜单（CPA计算器、COLREGS助手）
  - 设置菜单（系统配置、警报阈值）

- [ ] **工具栏**：
  - 快速操作按钮（目标锁定、航线绘制、AR模式切换）
  - 状态指示器（连接状态、数据质量）

#### 2.3 数据绑定框架
- [ ] **与DataAggregator集成**：
  - 创建AR-CAS专用数据适配器
  - 实现实时数据更新机制
  - 错误处理和降级策略

### 阶段3：核心功能实现（3-4天）

#### 3.1 AIS目标管理
- [ ] **目标列表组件**：
  - 实时显示AIS目标
  - 风险评估可视化（低/中/高风险）
  - 目标筛选和排序

- [ ] **目标详情面板**：
  - 显示MMSI、船型、航向、航速
  - CPA/TCPA实时计算
  - COLREGS规则应用状态

#### 3.2 增强现实叠加
- [ ] **摄像头视图增强**：
  - 实现`.ar-target`、`.ar-iceberg`等叠加元素
  - 目标位置计算和映射
  - 警告标签动态显示

- [ ] **AR控制面板**：
  - 叠加元素开关控制
  - 透明度调节
  - 标签样式配置

#### 3.3 避碰算法集成
- [ ] **CPA/TCPA计算器**：
  - 集成现有导航智能体算法
  - 实时计算和显示
  - 阈值警报触发

- [ ] **COLREGS合规检查**：
  - 规则库集成
  - 情景分析
  - 建议行动生成

### 阶段4：系统集成与测试（2-3天）

#### 4.1 Poseidon-X系统集成
- [ ] **智能体协调**：
  - 与NavigatorAgent通信获取避碰建议
  - 与SafetyAgent协调警报处理
  - 通过Orchestrator管理多智能体任务

- [ ] **上下文共享**：
  - 集成ContextWindow获取系统状态
  - 共享船舶上下文数据
  - 统一警报管理

#### 4.2 后端API集成
- [ ] **数据通道连接**：
  - 连接`ais_processor.py`获取AIS数据
  - 连接`weather_ocean_channel.py`获取天气数据
  - 连接`alarm_management.py`处理警报

- [ ] **实时数据流**：
  - WebSocket连接建立
  - 数据订阅/发布机制
  - ���接状态监控

#### 4.3 测试与验证
- [ ] **单元测试**：
  - 菜单组件测试
  - 计算算法测试
  - 数据流测试

- [ ] **集成测试**：
  - 端到端功能测试
  - 性能测试（大数据量场景）
  - 兼容性测试（不同浏览器）

### 阶段5：优化与部署（1-2天）

#### 5.1 性能优化
- [ ] **渲染优化**：
  - 虚拟滚动（大量AIS目标时）
  - 图层渲染性能优化
  - 内存泄漏检查

- [ ] **数据优化**：
  - 数据缓存策略
  - 增量更新机制
  - 网络请求合并

#### 5.2 用户体验优化
- [ ] **交互优化**：
  - 快捷键支持
  - 拖拽操作
  - 上下文菜单

- [ ] **可访问性**：
  - 键盘导航支持
  - 屏幕阅读器兼容
  - 高对比度模式

#### 5.3 文档与部署
- [ ] **用户文档**：
  - 功能说明文档
  - 操作指南
  - 故障排除

- [ ] **部署配置**：
  - 构建脚本更新
  - 依赖管理
  - 环境配置

## ⚠️ 技术风险与依赖

### 高风险项
1. **实时数据性能**：大量AIS目标同时显示可能导致性能问题
   - 缓解：实现虚拟化渲染，分批加载

2. **浏览器兼容性**：WebGL和WebSocket在不同浏览器表现可能不同
   - 缓解：渐进增强，提供降级方案

3. **后端数据延迟**：实时避碰决策对延迟敏感
   - 缓解：前端缓存+预测算法，后端优化数据通道

### 关键依赖
1. **Poseidon-X系统**：需要AI智能体提供决策支持
2. **DataAggregator**：统一数据源访问
3. **MapLibre GL JS**：地图渲染基础
4. **后端数据通道**：AIS、天气、警报等实时数据

## 📁 建议文件结构

```
src/frontend/digital-twin/ar-cas-pro/
├── VRMenu.js                    # VR菜单主组件
├── AISManager.js               # AIS目标管理
├── ARRenderer.js               # 增强现实渲染
├── CollisionAvoidance.js       # 避碰算法
├── COLREGSChecker.js          # 规则检查
├── DataAdapter.js              # 数据适配器
├── MenuController.js           # 菜单控制器
├── styles/
│   └── ar-cas-pro.css          # 专用样式
└── utils/
    ├── CPAcalculator.js        # CPA计算工具
    └── CoordinateMapper.js     # 坐标映射工具
```

## 🚀 实施建议

### 开发优先级
1. **先实现基础框架**：VR菜单显示、基本交互
2. **集成现有数据**：连接DataAggregator显示AIS目标
3. **实现核心算法**：CPA/TCPA计算、COLREGS检查
4. **增强现实功能**：摄像头叠加显示
5. **系统集成**：与Poseidon-X深度集成
6. **优化完善**：性能、用户体验、文档

### 团队协作建议
- **前端开发**：负责UI组件、交互逻辑、数据可视化
- **算法开发**：负责避碰算法、COLREGS规则实现
- **后端开发**：负责数据通道优化、实时API支持
- **测试团队**：负责功能验证、性能测试

### 里程碑计划
- **M1**（3天）：基础菜单框架 + AIS数据显示
- **M2**（5天）：核心避碰功能 + AR叠加显示
- **M3**（7天）：系统集成 + 基础测试
- **M4**（9天）：优化完善 + 用户文档

## 📞 沟通要点

1. **与Poseidon-X团队协调**：确保AR-CAS Pro能充分利用现有AI智能体
2. **与数据团队协调**：确认实时数据接口的稳定性和性能
3. **与设计团队协调**：确保UI/UX符合系统整体设计语言
4. **与测试团队协调**：制定详细的测试计划和验收标准

---

**预计总工时**：9-14人日（取决于团队规模和并行开发能力）

**关键成功因素**：
1. 充分利用现有Poseidon-X基础设施
2. 保持与数字孪生系统其他组件的设计一致性
3. 确保实时性能满足航海安全要求
4. 提供清晰的操作界面和决策支持信息

────────────────────────────────────────────────────────────
✅ deepseek-chat 完成
