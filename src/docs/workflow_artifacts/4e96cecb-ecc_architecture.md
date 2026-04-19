# 架构设计 — architect

任务: 数字孪生的AR-CAS Pro菜单是空白的，需要他来实现
步骤: architecture
Agent: build_architect

---

📋 任务: 4e96cecb-ecc
🤖 Agent: Architect (architect)
📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
🔧 执行方式: DeepSeek API (直连)
⏱️ 超时: 300s
────────────────────────────────────────────────────────────
📝 提示词:
  你是 PoseidonX 系统的 Architect (architect)。
  请执行以下开发任务:
  
  你是系统架构师。请为以下任务设计技术方案:
  
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
  ... (共 674 个 src/ 文件)
  
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
  
  
  ## 前序步骤的产出 (管线共享工作区)
  
  ### 步骤 01: pm_decompose.md
  
  # PM分解 — project_manager
  
  任务: 数字孪生的AR-CAS Pro菜单是空白的，需要他来实现
  步骤: pm_decompose
  Agent: build_pm
  
  ---
  
  📋 任务: 4e96cecb-ecc
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
    ... (共 674 个 src/ 文件)
    
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
          model: this.co
  ### 步骤 02: research.md
  
  # 研究分析 — researcher
  
  任务: 数字孪生的AR-CAS Pro菜单是空白的，需要他来实现
  步骤: research
  Agent: build_researcher
  
  ---
  
  📋 任务: 4e96cecb-ecc
  🤖 Agent: Researcher (researcher)
  📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  🔧 执行方式: DeepSeek API (直连)
  ⏱️ 超时: 300s
  ────────────────────────────────────────────────────────────
  📝 提示词:
    你是 PoseidonX 系统的 Researcher (researcher)。
    请执行以下开发任务:
    
    你是技术研究员。请对以下任务进行技术调研:
    
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
    ... (共 674 个 src/ 文件)
    
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
          model: this.co
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
⚡ 使用 DeepSeek API 直连 (快速模式)...

🔗 API: api.deepseek.com | 模型: deepseek-chat
────────────────────────────────────────────────────────────

# AR-CAS Pro 菜单实现技术方案

## 1. 现状分析

### 1.1 当前问题
- `worldmonitor-ar-cas-pro.html` 文件中的 VR 菜单部分代码不完整（在 `vr-toolbar` 处截断）
- 数字孪生系统中缺少 AR-CAS Pro 菜单的完整实现
- 需要为数字孪生系统添加专业的 AR 碰撞避免系统菜单

### 1.2 现有资源
- 已有完整的 HTML 结构和 CSS 样式
- 已有 DataAggregator 用于数据聚合
- 已有 PoseidonX 系统框架
- 已有 MarineEngineeringModule 用于船舶工程计算

## 2. 技术方案设计

### 2.1 架构设计

```
AR-CAS Pro 系统架构
├── 前端层 (HTML/CSS/JS)
│   ├── worldmonitor-ar-cas-pro.html (主界面)
│   ├── ARCASMenu.js (菜单核心逻辑)
│   └── ARVisualization.js (AR 可视化)
├── 业务逻辑层
│   ├── CollisionAvoidanceEngine.js (碰撞避免引擎)
│   ├── ARTargetManager.js (AR 目标管理)
│   └── RiskAssessment.js (风险评估)
└── 数据层
    ├── DataAggregator.js (数据聚合)
    └── PoseidonXIntegration.js (系统集成)
```

### 2.2 核心功能模块

#### 2.2.1 AR-CAS 菜单系统
- **VR 菜单控制面板**：可折叠/展开的浮动菜单
- **AR 目标管理**：船舶、冰山、峡谷等 AR 目标
- **风险可视化**：不同风险级别的视觉反馈
- **实时数据监控**：CPA/TCPA、COLREGS 规则等

#### 2.2.2 碰撞避免引擎
- **CPA/TCPA 计算**：最近会遇点/时间计算
- **COLREGS 规则引擎**：国际海上避碰规则
- **风险评估算法**：基于距离、速度、航向的风险评估
- **避碰建议生成**：智能避碰建议

#### 2.2.3 AR 可视化系统
- **3D 目标标注**：船舶、障碍物的 AR 标注
- **风险热力图**：基于风险级别的颜色编码
- **导航路径显示**：安全路径规划
- **预警系统**：视觉和听觉预警

## 3. 详细实现方案

### 3.1 文件修改清单

#### 3.1.1 需要修改的文件
1. `src/frontend/worldmonitor-ar-cas-pro.html` - 补全 VR 菜单代码
2. `src/frontend/digital-twin/` - 新增 AR-CAS 相关模块

#### 3.1.2 需要新增的文件
1. `src/frontend/digital-twin/arcas/ARCASMenu.js` - AR-CAS 菜单核心
2. `src/frontend/digital-twin/arcas/CollisionAvoidanceEngine.js` - 碰撞避免引擎
3. `src/frontend/digital-twin/arcas/ARTargetManager.js` - AR 目标管理
4. `src/frontend/digital-twin/arcas/RiskAssessment.js` - 风险评估
5. `src/frontend/digital-twin/arcas/ARVisualization.js` - AR 可视化
6. `src/frontend/digital-town/arcas/COLREGSEngine.js` - COLREGS 规则引擎

### 3.2 接口规范

#### 3.2.1 数据接口
```javascript
// AR-CAS 数据接口
interface ARCASEvents {
  onTargetDetected: (target: AISTarget) => void;
  onRiskUpdated: (riskLevel: string, details: RiskDetails) => void;
  onCollisionWarning: (warning: CollisionWarning) => void;
  onARVisualizationReady: () => void;
}

// AISTarget 数据结构
interface AISTarget {
  mmsi: string;
  type: string;
  position: { lat: number; lon: number };
  course: number;
  speed: number;
  cpa: number;
  tcpa: number;
  riskLevel: 'low' | 'medium' | 'high';
  colregsRule: string;
}
```

#### 3.2.2 API 接口
```python
# 后端 API 接口 (Python FastAPI)
@app.get("/api/v1/arcas/targets")
async def get_arcas_targets():
    """获取 AR-CAS 目标列表"""
    pass

@app.post("/api/v1/arcas/risk-assessment")
async def assess_risk(target_data: dict):
    """风险评估"""
    pass

@app.get("/api/v1/arcas/colregs-advice")
async def get_colregs_advice():
    """获取 COLREGS 避碰建议"""
    pass
```

### 3.3 具体实现步骤

#### 步骤 1: 补全 HTML 文件
```html
<!-- 在 worldmonitor-ar-cas-pro.html 中补全 VR 菜单 -->
<div class="vr-menu" id="arcas-vr-menu">
    <div class="vr-toolbar">
        <div class="vr-title">
            <h3>AR-CAS Pro 控制面板</h3>
            <span class="vr-status">在线</span>
        </div>
        <div class="vr-actions">
            <button class="vr-btn collapse-btn" id="collapse-menu">
                <i class="icon-collapse"></i>
            </button>
            <button class="vr-btn settings-btn" id="arcas-settings">
                <i class="icon-settings"></i>
            </button>
        </div>
    </div>
    
    <div class="vr-content" id="arcas-content">
        <!-- AR 控制区域 -->
        <div class="ar-controls">
            <div class="control-group">
                <label>AR 模式</label>
                <select id="ar-mode">
                    <option value="basic">基础模式</option>
                    <option value="advanced">高级模式</option>
                    <option value="expert">专家模式</option>
                </select>
            </div>
            
            <div class="control-group">
                <label>目标过滤</label>
                <div class="filter-options">
                    <label><input type="checkbox" checked> 船舶</label>
                    <label><input type="checkbox" checked> 冰山</label>
                    <label><input type="checkbox" checked> 浅滩</label>
                </div>
            </div>
        </div>
        
        <!-- 风险监控区域 -->
        <div class="risk-monitor">
            <h4>实时风险监控</h4>
            <div class="risk-meters">
                <div class="risk-meter" id="collision-risk">
                    <div class="meter-label">碰撞风险</div>
                    <div class="meter-value low">低</div>
                </div>
                <div class="risk-meter" id="grounding-risk">
                    <div class="meter-label">搁浅风险</div>
                    <div class="meter-value low">低</div>
                </div>
            </div>
        </div>
        
        <!-- 目标列表区域 -->
        <div class="target-list">
            <h4>AR 目标列表</h4>
            <div class="target-items" id="ar-target-items">
                <!-- 动态加载目标 -->
            </div>
        </div>
    </div>
</div>
```

#### 步骤 2: 实现 ARCASMenu.js
```javascript
/**
 * ARCASMenu - AR-CAS Pro 菜单系统
 */
export class ARCASMenu {
    constructor(config = {}) {
        this.config = {
            menuId: 'arcas-vr-menu',
            collapseBtnId: 'collapse-menu',
            settingsBtnId: 'arcas-settings',
            arModeId: 'ar-mode',
            ...config
        };
        
        this.isCollapsed = false;
        this.arMode = 'basic';
        this.targets = [];
        
        this.initialize();
    }
    
    initialize() {
        this.bindEvents();
        this.loadSettings();
        this.startDataPolling();
    }
    
    bindEvents() {
        // 折叠/展开菜单
        document.getElementById(this.config.collapseBtnId)?.addEventListener('click', () => {
            this.toggleCollapse();
        });
        
        // AR 模式切换
        document.getElementById(this.config.arModeId)?.addEventListener('change', (e) => {
            this.setARMode(e.target.value);
        });
        
        // 设置按钮
        document.getElementById(this.config.settingsBtnId)?.addEventListener('click', () => {
            this.openSettings();
        });
    }
    
    toggleCollapse() {
        const menu = document.getElementById(this.config.menuId);
        if (!menu) return;
        
        this.isCollapsed = !this.isCollapsed;
        menu.classList.toggle('collapsed', this.isCollapsed);
        
        // 保存状态到 localStorage
        localStorage.setItem('arcas_menu_collapsed', this.isCollapsed);
    }
    
    setARMode(mode) {
        this.arMode = mode;
        console.log(`AR 模式已切换至: ${mode}`);
        
        // 触发模式切换事件
        this.dispatchEvent('arModeChanged', { mode });
        
        // 保存设置
        this.saveSettings();
    }
    
    openSettings() {
        // 打开设置对话框
        console.log('打开 AR-CAS 设置');
        // 这里可以打开模态框或跳转到设置页面
    }
    
    updateTargets(targets) {
        this.targets = targets;
        this.renderTargetList();
    }
    
    renderTargetList() {
        const container = document.getElementById('ar-target-items');
        if (!container) return;
        
        container.innerHTML = this.targets.map(target => `
            <div class="target-item ${target.riskLevel}">
                <div class="target-header">
                    <span class="target-type">${target.type}</span>
                    <span class="target-mmsi">${target.mmsi}</span>
                </div>
                <div class="target-info">
                    <div>距离: ${target.distance.toFixed(2)} nm</div>
                    <div>航向: ${target.course}°</div>
                    <div>CPA: ${target.cpa.toFixed(2)} nm</div>
                    <div>TCPA: ${target.tcpa.toFixed(1)} min</div>
                </div>
                <div class="target-risk">
                    <span class="risk-badge ${target.riskLevel}">${target.riskLevel}</span>
                </div>
            </div>
        `).join('');
    }
    
    startDataPolling() {
        // 每 5 秒更新一次数据
        setInterval(() => {
            this.fetchTargetData();
        }, 5000);
    }
    
    async fetchTargetData() {
        try {
            const response = await fetch('/api/v1/arcas/targets');
            const data = await response.json();
            this.updateTargets(data.targets);
        } catch (error) {
            console.error('获取目标数据失败:', error);
        }
    }
    
    saveSettings() {
        const settings = {
            arMode: this.arMode,
            isCollapsed: this.isCollapsed
        };
        localStorage.setItem('arcas_settings', JSON.stringify(settings));
    }
    
    loadSettings() {
        const saved = localStorage.getItem('arcas_settings');
        if (saved) {
            try {
                const settings = JSON.parse(saved);
                this.arMode = settings.arMode || 'basic';
                this.isCollapsed = settings.isCollapsed || false;
                
                // 应用设置
                const menu = document.getElementById(this.config.menuId);
                if (menu) {
                    menu.classList.toggle('collapsed', this.isCollapsed);
                }
                
                const modeSelect = document.getElementById(this.config.arModeId);
                if (modeSelect) {
                    modeSelect.value = this.arMode;
                }
            } catch (error) {
                console.warn('加载 AR-CAS 设置失败:', error);
            }
        }
    }
    
    dispatchEvent(eventName, data) {
        const event = new CustomEvent(`arcas:${eventName}`, { detail: data });
        window.dispatchEvent(event);
    }
}
```

#### 步骤 3: 实现碰撞避免引擎
```javascript
/**
 * CollisionAvoidanceEngine - 碰撞避免引擎
 */
export class CollisionAvoidanceEngine {
    constructor(config = {}) {
        this.config = {
            safeDistance: 0.5, // 海里
            warningDistance: 1.0,
            cpaThreshold: 0.3,
            tcpaThreshold: 10, // 分钟
            ...config
        };
        
        this.colregsEngine = new COLREGSEngine();
        this.riskAssessor = new RiskAssessment();
    }
    
    calculateCPA(ownShip, targetShip) {
        // 计算最近会遇点
        const dx = targetShip.position.lon - ownShip.position.lon;
        const dy = targetShip.position.lat - ownShip.position.lat;
        
        const vx = targetShip.speed * Math.sin(targetShip.course * Math.PI / 180) -
                  ownShip.speed * Math.sin(ownShip.course * Math.PI / 180);
        const vy = targetShip.speed * Math.cos(targetShip.course * Math.PI / 180) -
                  ownShip.speed * Math.cos(ownShip.course * Math.PI / 180);
        
        const t = -(dx * vx + dy * vy) / (vx * vx + vy * vy);
        
        const cpa = Math.sqrt(
            Math.pow(dx + vx * t, 2) + 
            Math.pow(dy + vy * t, 2)
        );
        
        return {
            cpa: cpa,
            tcpa: t > 0 ? t * 60 : 0, // 转换为分钟
            timeToCPA: t
        };
    }
    
    assessCollisionRisk(ownShip, targets) {
        const risks = [];
        
        for (const target of targets) {
            const cpaData = this.calculateCPA(ownShip, target);
            const colregsRule = this.colregsEngine.determineRule(ownShip, target);
            const riskLevel = this.riskAssessor.assessRisk(cpaData, colregsRule);
            
            risks.push({
                target,
                cpa: cpaData.cpa,
                tcpa: cpaData.tcpa,
                colregsRule,
                riskLevel,
                suggestion: this.generateSuggestion(riskLevel, colregsRule)
            });
        }
        
        return risks.sort((a, b) => a.tcpa - b.tcpa); // 按 TCPA 排序
    }
    
    generateSuggestion(riskLevel, colregsRule) {
        const suggestions = {
            high: '立即采取避碰行动！',
            medium: '密切监控，准备采取行动',
            low: '保持监控'
        };
        
        return `${suggestions[riskLevel]} (适用规则: ${colregsRule})`;
    }
}
```

#### 步骤 4: 集成到 PoseidonX 系统
```javascript
// 在 PoseidonX.js 中添加 AR-CAS 集成
import { ARCASMenu } from './arcas/ARCASMenu.js';
import { CollisionAvoidanceEngine } from './arcas/CollisionAvoidanceEngine.js';

// 在 PoseidonX 类中添加
class PoseidonX extends EventEmitter {
    // ... 现有代码 ...
    
    async _initializeARCAS() {
        console.log('🚀 Initializing AR-CAS Pro System...');
        
        // 初始化 AR-CAS 菜单
        this.arcasMenu = new ARCASMenu();
        
        // 初始化碰撞避免引擎
        this.collisionEngine = new CollisionAvoidanceEngine();
        
        // 监听 AR-CAS 事件
        window.addEventListener('arcas:arModeChanged', (e) => {
            console.log('AR 模式已更改:', e.detail.mode);
        });
        
        // 启动碰撞避免监控
        this.startCollisionMonitoring();
        
        console.log('✅ AR-CAS Pro System initialized');
    }
    
    startCollisionMonitoring() {
        setInterval(() => {
            if (this.shipContext.position) {
                const risks = this.collisionEngine.assessCollisionRisk(
                    this.shipContext,
                    this.getAISTargets()
                );
                
                // 更新 AR-CAS 菜单
                this.arcasMenu.updateTargets(risks);
                
                // 触发高风险警报
                const highRisks = risks.filter(r => r.riskLevel === 'high');
                if (highRisks.length > 0) {
                    this.triggerCollisionAlert(highRisks);
                }
            }
        }, 3000); // 每 3 秒检查一次
    }
    
    getAISTargets() {
        // 从 DataAggregator 获取 AIS 目标
        // 这里需要实现实际的数据获取逻辑
        return [];
    }
    
    triggerCollisionAlert(highRisks) {
        console.warn('🚨 碰撞风险警报！', highRisks);
        
        // 在界面上显示警报
        if (this.bridgeChat) {
            this.bridgeChat._addMessage('safety', 
                `🚨 检测到 ${highRisks.length} 个高风险目标！\n` +
                `请立即采取避碰行动。`
            );
        }
    }
}
```

### 3.4 CSS 样式补充
```css
/* 在现有 CSS 中添加以下样式 */

/* VR 菜单内容样式 */
.vr-content {
    padding: 16px;
    overflow-y: auto;
    flex: 1;
}

.vr-menu.collapsed .vr-content {
    display: none;
}

/* AR 控制区域 */
.ar-controls {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 16px;
}

.control-group {
    margin-bottom: 12px;
}

.control-group label {
    display: block;
    font-size: 12px;
    color: #a0aec0;
    margin-bottom: 6px;
}

.control-group select {
    width: 100%;
    padding: 8px;
    background: rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(79, 195, 247, 0.3);
    border-radius: 6px;
    color: white;
}

.filter-options {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.filter-options label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #cbd5e0;
}

/* 风险监控 */
.risk-monitor {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 16px;
}

.risk-monitor h4 {
    font-size: 13px;
    color: #4fc3f7;
    margin-bottom: 12px;
}

.risk-meters {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

.risk-meter {
    background: rgba(0, 0, 0, 0.4);
    border-radius: 6px;
    padding: 10px;
    text-align: center;
}

.meter-label {
    font-size: 11px;
    color: #718096;
    margin-bottom: 4px;
}

.meter-value {
    font-size: 14px;
    font-weight: 700;
}

.meter-value.low { color: #48bb78; }
.meter-value.medium { color: #f6ad55; }
.meter-value.high { color: #f56565; }

/* 目标列表 */
.target-list {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    padding: 12px;
}

.target-list h4 {
    font-size: 13px;
    color: #4fc3f7;
    margin-bottom: 12px;
}

.target-items {
    max-height: 200px;
    overflow-y: auto;
}

.target-item {
    background: rgba(0, 0, 0, 0.4);
    border-radius: 6px;
    padding: 10px;
    margin-bottom: 8px;
    border-left: 3px solid #48bb78;
}

.target-item.high {
    border-left-color: #f56565;
    background: rgba(245, 101, 101, 0.1);
}

.target-item.medium {
    border-left-color: #f6ad55;
    background: rgba(246, 173, 85, 0.1);
}

.target-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
}

.target-type {
    font-weight: 600;
    color: #4fc3f7;
    font-size: 12px;
}

.target-mmsi {
    font-size: 10px;
    color: #718096;
}

.target-info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4px;
    font-size: 10px;
    color: #a0aec0;
    margin-bottom: 8px;
}

.target-risk {
    text-align: right;
}

/* VR 工具栏 */
.vr-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid rgba(79, 195, 247, 0.2);
    background: rgba(8, 16, 30, 0.8);
}

.vr-title {
    display: flex;
    align-items: center;
    gap: 10px;
}

.vr-title h3 {
    font-size: 14px;
    font-weight: 600;
    color: #4fc3f7;
    margin: 0;
}

.vr-status {
    font-size: 10px;
    padding: 2px 8px;
    background: rgba(72, 187, 120, 0.2);
    color: #48bb78;
    border-radius: 10px;
}

.vr-actions {
    display: flex;
    gap: 8px;
}

.vr-btn {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: 1px solid rgba(79, 195, 247, 0.3);
    background: rgba(79, 195, 247, 0.1);
    color: #4fc3f7;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.vr-btn:hover {
    background: rgba(79, 195, 247, 0.2);
    transform: scale(1.05);
}
```

## 4. 实施指南

### 4.1 开发步骤

#### 阶段 1: 基础框架搭建 (1-2 天)
1. 补全 `worldmonitor-ar-cas-pro.html` 中的 VR 菜单代码
2. 创建 `src/frontend/digital-twin/arcas/` 目录结构
3. 实现 `ARCASMenu.js` 基础功能
4. 添加必要的 CSS 样式

#### 阶段 2: 核心引擎开发 (2-3 天)
1. 实现 `CollisionAvoidanceEngine.js`
2. 实现 `COLREGSEngine.js`
3. 实现 `RiskAssessment.js`
4. 实现 `ARTargetManager.js`

#### 阶段 3: 可视化集成 (1-2 天)
1. 实现 `ARVisualization.js`
2. 集成到现有地图系统
3. 添加 AR 标注和可视化效果

#### 阶段 4: 系统集成与测试 (1-2 天)
1. 集成到 PoseidonX 系统
2. 添加数据接口
3. 进行功能测试和性能优化

### 4.2 测试要点

#### 功能测试
1. VR 菜单的折叠/展开功能
2. AR 模式切换
3. 目标数据加载和显示
4. 碰撞风险计算和显示
5. COLREGS 规则应用

#### 性能测试
1. 数据更新频率和响应时间
2. 多目标情况下的性能
3. 内存使用情况
4. 浏览器兼容性

#### 集成测试
1. 与 DataAggregator 的集成
2. 与 PoseidonX 系统的集成
3. 与现有地图系统的集成
4. 跨模块数据流测试

### 4.3 部署说明

#### 前端部署
1. 确保所有 JS 文件正确引入
2. 检查 CSS 样式兼容性
3. 配置 API 端点
4. 设置本地存储策略

#### 后端部署
1. 添加 AR-CAS 相关 API 端点
2. 配置数据源连接
3. 设置缓存策略
4. 配置日志和监控

## 5. 风险与缓解措施

### 5.1 技术风险
1. **性能问题**：大量 AR 目标可能导致性能下降
   - 缓解：实现目标过滤和 LOD（细节层次）机制
   
2. **数据延迟**：实时数据可能延迟
   - 缓解：实现数据缓存和预测算法
   
3. **浏览器兼容性**：不同浏览器对 WebGL 支持不同
   - 缓解：提供降级方案和功能检测

### 5.2 业务风险
1. **误报警**：过于敏感的系统可能产生误报
   - 缓解：实现智能过滤和用户可调阈值
   
2. **用户接受度**：复杂的 AR 界面可能难以使用
   - 缓解：提供多种显示模式和详细帮助文档

## 6. 成功标准

### 技术标准
1. VR 菜单响应时间 < 100ms
2. 目标数据更新延迟 < 3s
3. 碰撞计算准确率 > 95%
4. 系统可用性 > 99.5%

### 业务标准
1. 用户能够通过 AR-CAS 系统有效识别碰撞风险
2. 系统提供的避碰建议符合 COLREGS 规则
3. 用户界面直观易用
4. 系统能够处理至少 50 个并发目标

## 7. 后续优化建议

### 短期优化 (1-3 个月)
1. 添加机器学习模型优化风险评估
2. 实现更精细的 AR 可视化效果
3. 添加语音警报和交互功能
4. 优化移动端显示

### 长期规划 (3-12 个月)
1. 集成 AI 避碰决策系统
2. 实现多船协同避碰
3. 添加历史数据分析和学习功能
4. 扩展支持更多类型的海上障碍物

---

**实施优先级**：
1. ✅ 补全 HTML 和基础 CSS
2. ✅ 实现 ARCASMenu 基础功能  
3. ✅ 集成到 PoseidonX 系统
4. 🔄 实现碰撞避免引擎
5. 🔄 添加 AR 可视化
6. 🔄 完整测试和优化

这个技术方案提供了完整的实现路径，开发团队可以按照这个方案逐步实施 AR-CAS Pro 菜单系统。

────────────────────────────────────────────────────────────
✅ deepseek-chat 完成
