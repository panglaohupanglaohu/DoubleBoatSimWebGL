# 架构设计 — architect

任务: 给build团队的PM一个任务将http://localhost:5173/worldmonitor-ar-cas-pro.html的菜单AR-CAS-PRO的功能全部平移到数字孪生页面的AR-CAS...
步骤: architecture
Agent: build_architect

---

📋 任务: 6a2426e3-538
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
  给build团队的PM一个任务将http://localhost:5173/worldmonitor-ar-cas-pro.html的菜单AR-CAS-PRO的功能全部平移到数字孪生页面的AR-CAS...
  给build团队的PM一个任务将http://localhost:5173/worldmonitor-ar-cas-pro.html的菜单AR-CAS-PRO的功能全部平移到数字孪生页面的AR-CAS-PRO菜单中来，根据当前的数字孪生页面赋予现实增强的能力，就是当前的页面是他来做AR的基础
  
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
  ... (共 830 个 src/ 文件)
  
  ```
  
  ### 文件: `src/frontend/datacenter-digital-twin.html`
  ```html
  <!DOCTYPE html>
  <html lang="zh-CN" data-obc-theme="dusk">
  <head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Digital Twin · 物理↔数字一一映射 · xFirst Principle</title>
  <link rel="stylesheet" href="/css/openbridge-theme.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300;400;500;700&family=Noto+Serif:wght@200;300;400;600;900&family=Noto+Serif+SC:wght@200;300;400;600;900&family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap');
    :root {
      /* ── 侘寂橡胶 · Wabi-Sabi Rubber ── */
      --bg-0:oklch(0.96 0.003 110); --bg-1:oklch(0.91 0.004 110); --bg-2:oklch(0.85 0.005 110);
      --grid:oklch(0 0 0 / 0.03); --line:oklch(0.82 0.004 110);
      --accent:oklch(0.18 0.008 110); --accent-2:oklch(0.52 0.04 160); --accent-3:oklch(0.55 0.005 110);
      --warn:oklch(0.56 0.05 70); --danger:oklch(0.48 0.07 22);
      --text:oklch(0.18 0.008 110); --muted:oklch(0.55 0.005 110);
      --rack:oklch(0.18 0.008 110); --pdu:oklch(0.56 0.05 70); --ats:oklch(0.48 0.07 22); --busway:oklch(0.55 0.005 110);
      --cold:oklch(0.52 0.04 160); --hot:oklch(0.48 0.07 22); --pipe:oklch(0.52 0.04 160); --floor:oklch(0.72 0.006 110);
      /* rubber button system */
      --rubber:oklch(0.72 0.006 110); --rubber-hover:oklch(0.68 0.007 110); --rubber-press:oklch(0.64 0.007 110);
      --sumi:oklch(0.18 0.008 110); --koke:oklch(0.52 0.04 160); --shu:oklch(0.48 0.07 22);
      --kitsune:oklch(0.56 0.05 70); --shironeri:oklch(0.96 0.003 110);
      --groove:oklch(0.82 0.004 110); --ridge:oklch(1.00 0 0 / 0.6);
    }
    *{box-sizing:border-box;margin:0;padding:0}
    html,body{margin:0;padding:0;height:100%;font-family:'Noto Sans SC','JetBrains Mono',sans-serif;color:var(--text);-webkit-font-smoothing:antialiased}
    body{
      background:var(--bg-0);
      overflow-x:hidden;
    }
    /* 和紙质感 — 微粒紋理 */
    body::before{
      content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
      background-image:
        radial-gradient(oklch(0 0 0 / 0.012) 1px, transparent 1px),
        radial-gradient(oklch(0 0 0 / 0.008) 1px, transparent 1px);
      background-size:5px 5px, 7px 7px;
      background-position:0 0, 3px 3px;
    }
    .container{position:relative;z-index:1;max-width:100%;margin:0 auto;padding:18px 24px}
  
    .hud{display:flex;align-items:center;justify-content:space-between;
      padding:14px 0;border-bottom:1px solid var(--groove)}
    .hud .brand{display:flex;align-items:center;gap:14px}
    .hud .logo{width:34px;height:34px;
      background:var(--sumi);
      display:flex;align-items:center;justify-content:center;
      font-family:'Noto Serif SC',serif;font-size:18px;font-weight:900;color:var(--shironeri)}
    .hud h1{margin:0;font-family:'Noto Serif SC',serif;font-size:13px;letter-spacing:3px;font-weight:300;color:var(--muted)}
    .hud h1 strong{color:var(--text);font-weight:600}
    .hud .sub{font-size:10px;color:var(--muted);letter-spacing:2px;font-family:'JetBrains Mono',monospace}
    .hud .pills{display:flex;gap:6px;align-items:center;flex-wrap:wrap;justify-content:flex-end}
    /* 橡胶按钮 pill */
    .pill{padding:5px 14px;font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:1.5px;
      border:none;cursor:pointer;user-select:none;text-decoration:none;text-transform:uppercase;
      background:var(--rubber);color:var(--sumi);
      box-shadow:0 2px 5px oklch(0 0 0/0.12),0 1px 2px oklch(0 0 0/0.08),inset 0 1px 0 oklch(1 0 0/0.35),inset 0 -1px 0 oklch(0 0 0/0.08);
      background-image:radial-gradient(oklch(0 0 0/0.02) 1px,transparent 1px);background-size:3px 3px;
      transition:all 0.08s ease-out}
    .pill:hover{background-color:var(--rubber-hover)}
    .pill:active{box-shadow:inset 0 2px 5px oklch(0 0 0/0.15),inset 0 1px 2px oklch(0 0 0/0.10);transform:translateY(1px);background-color:var(--rubber-press)}
    .pill.live{background:var(--sumi);color:var(--shironeri);box-shadow:0 2px 5px oklch(0 0 0/0.15),inset 0 1px 0 oklch(1 0 0/0.08),inset 0 -1px 0 oklch(0 0 0/0.3)}
    .pill.live::before{content:'';display:inline-block;width:5px;height:5px;
      background:var(--koke);margin-right:6px;animation:blink 2.5s infinite}
    .pill.ws{background:var(--sumi);color:var(--shironeri)}
    .pill.ws.off{background:oklch(0.85 0.005 110);color:var(--shu)}
    @keyframes blink{50%{opacity:0.3}}
  
    .fp-banner{margin-top:14px;padding:12px 18px;
      background:oklch(0.93 0.003 110);
      box-shadow:inset 0 1px 4px oklch(0 0 0/0.05),0 1px 0 var(--ridge);
      font-size:12px;color:var(--text);
      display:flex;gap:18px;align-items:center;flex-wrap:wrap}
    .fp-banner .formula{font-family:'JetBrains Mono',monospace;color:var(--sumi);font-weight:700}
  
    .panel{padding:14px 16px;
      background:oklch(0.93 0.003 110);
      box-shadow:inset 0 1px 5px oklch(0 0 0/0.05),0 1px 0 oklch(1 0 0/0.5)}
    .panel h2{margin:0 0 10px;font-family:'Noto Serif SC',serif;font-size:12px;letter-spacing:3px;color:var(--sumi);
      text-transform:uppercase;display:flex;justify-content:space-between;align-items:center}
    .badge{font-family:'JetBrains Mono',monospace;font-size:8px;color:var(--muted);padding:2px 8px;border:1px solid var(--groove);letter-spacing:1.5px}
    .section-title{font-family:'Noto Serif SC',serif;font-size:11px;color:var(--muted);letter-spacing:3px;margin:14px 0 6px;text-transform:uppercase}
  
    .grid-21{display:grid;grid-template-columns:2fr 1fr;gap:14px}
    .grid-12{display:grid;grid-template-columns:1fr 2fr;gap:14px}
  
    /* 3D twin viewport — 石壁观察窗 */
    .twin-viewport{position:relative;width:100%;height:680px;
      overflow:hidden;
      padding:8px;background:oklch(0.85 0.005 110);
      box-shadow:inset 0 1px 0 oklch(1 0 0/0.3),0 1px 0 oklch(0 0 0/0.04)}
    .twin-viewport canvas{display:block}
    .twin-overlay{position:absolute;top:8px;left:8px;right:8px;padding:10px 14px;
      display:flex;justify-content:space-between;pointer-events:none;font-size:11px}
    .twin-overlay .tag{background:oklch(0.93 0.003 110 / 0.85);
      padding:4px 10px;color:var(--sumi);letter-spacing:1.5px;pointer-events:auto;
      font-family:'JetBrains Mono',monospace;font-size:9px}
    .twin-overlay .tag.live{color:var(--koke)}
    .twin-controls{position:absolute;left:16px;top:52px;
      display:flex;flex-direction:column;gap:4px;font-size:10px;
      max-height:calc(100% - 64px);overflow-y:auto;padding-bottom:10px}
    /* 橡胶图层按钮 */
    .twin-controls .layer-btn{
      padding:4px 10px;background:oklch(0.88 0.004 110);
      border:none;color:var(--sumi);cursor:pointer;letter-spacing:1.5px;text-align:left;min-width:160px;
      display:flex;justify-content:space-between;align-items:center;gap:8px;
      font-family:'JetBrains Mono',monospace;font-size:9px;
      box-shadow:0 1px 3px oklch(0 0 0/0.08),inset 0 1px 0 oklch(1 0 0/0.4),inset 0 -1px 0 oklch(0 0 0/0.05);
      background-image:radial-gradient(oklch(0 0 0/0.02) 1px,transparent 1px);background-size:3px 3px;
      transition:all 0.08s ease-out;
    }
    .twin-controls .layer-btn:active{box-shadow:inset 0 2px 4px oklch(0 0 0/0.12);transform:translateY(1px);background-color:oklch(0.82 0.004 110)}
    .twin-controls .layer-btn .swatch{width:8px;height:8px;display:inline-block}
    .twin-controls .layer-btn.off{opacity:0.35;text-decoration:line-through}
    .twin-legend{position:absolute;right:16px;bottom:16px;
      background:oklch(0.93 0.003 110 / 0.9);
      padding:8px 12px;font-size:10px;line-height:1.7;color:var(--muted);font-family:'JetBrains Mono',monospace}
    .twin-legend b{color:var(--text)}
    .twin-readout{position:absolute;right:16px;top:68px;width:240px;
      background:oklch(0.93 0.003 110 / 0.95);
      box-shadow:inset 0 1px 4px oklch(0 0 0/0.06),0 2px 8px oklch(0 0 0/0.1);
      padding:10px 12px;font-size:11px;color:var(--text);display:none}
    .twin-readout.show{display:block}
    .twin-readout h4{margin:0 0 6px;color:var(--sumi);font-family:'Noto Serif SC',serif;font-size:12px;letter-spacing:2px}
    .twin-readout .row{display:flex;justify-content:space-between;padding:2px 0;border-bottom:1px solid oklch(0.90 0.003 110)}
    .twin-readout .row .v{color:var(--koke);font-weight:700;font-family:'JetBrains Mono',monospace}
  
    /* mapping list */
    .map-list{display:flex;flex-direction:column;gap:6px}
    .map-item{padding:8px 10px;
      background:oklch(0.93 0.003 110);box-shadow:inset 0 1px 3px oklch(0 0 0/0.04),0 1px 0 oklch(1 0 0/0.3);
      font-size:11px;cursor:pointer;
      display:grid;grid-template-columns:10px 1fr auto;gap:8px;align-items:center;transition:background 0.15s}
    .map-item:hover{background:oklch(0.90 0.003 110)}
    .map-item .dot{width:8px;height:8px}
    .map-item .name{color:var(--text);font-weight:500;letter-spacing:0.5px;font-size:10px}
    .map-item .phys{font-size:9px;color:var(--muted);margin-top:1px}
    .map-item .v{font-size:12px;color:var(--sumi);font-weight:600;font-family:'JetBrains Mono',monospace;font-feature-settings:'tnum'}
  
    /* KPI strip — 石硯嵌入卡 */
    .kpi-strip{display:grid;grid-template-columns:repeat(7,1fr);gap:10px;margin:14px 0}
    .kpi{padding:12px 14px;
      background:oklch(0.93 0.003 110);
      box-shadow:inset 0 1px 4px oklch(0 0 0/0.05),0 1px 0 oklch(1 0 0/0.4);
      position:relative;overflow:hidden}
    .kpi::after{content:'';position:absolute;bottom:0;left:0;height:1px;width:100%;
      background:var(--groove)}
    .kpi .label{font-size:8px;color:var(--muted);letter-spacing:2.5px;text-transform:uppercase;font-family:'JetBrains Mono',monospace}
    .kpi .value{font-size:22px;font-weight:600;color:var(--sumi);margin:4px 0 2px;font-family:'JetBrains Mono',monospace;font-feature-settings:'tnum'}
    .kpi .unit{font-size:10px;color:var(--muted);margin-left:2px}
    .kpi .delta{font-size:10px;color:var(--koke)}
  
    /* device cards — 石硯卡片 */
    .dev-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:6px;
      max-height:260px;overflow-y:auto;padding-right:4px}
    .dev-card{padding:8px 10px;
      background:oklch(0.93 0.003 110);box-shadow:inset 0 1px 3px oklch(0 0 0/0.04),0 1px 0 oklch(1 0 0/0.3);
      font-size:10px;cursor:pointer;transition:all .12s}
    .dev-card:hover{background:oklch(0.90 0.003 110)}
    .dev-card.hot{border-left:2px solid var(--kitsune)}
    .dev-card.crit{border-left:2px solid var(--shu)}
    .dev-card .id{color:var(--sumi);font-weight:600;font-size:10px;letter-spacing:0.5px;display:flex;justify-content:space-between;font-family:'JetBrains Mono',monospace}
    .dev-card .id .typ{color:var(--muted);font-size:8px;letter-spacing:1px}
    .dev-card .pw{font-size:16px;color:var(--sumi);font-weight:600;font-family:'JetBrains Mono',monospace;font-feature-settings:'tnum';margin:2px 0}
    .dev-card .ln{font-size:9px;color:var(--muted)}
  
    /* energy flow svg */
    svg.flow{width:100%;height:300px}
    .flow .node{fill:oklch(0.93 0.003 110);stroke:var(--sumi);stroke-width:1}
    .flow .label{fill:var(--text);font-size:11px;font-family:'JetBrains Mono',monospace}
    .flow .sublabel{fill:var(--muted);font-size:9px;font-family:'JetBrains Mono',monospace}
  
    /* ratchet steps */
    .ratchet-loop{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:6px}
    .step{padding:10px 12px;
      background:oklch(0.93 0.003 110);box-shadow:inset 0 1px 3px oklch(0 0 0/0.04),0 1px 0 oklch(1 0 0/0.3);
      font-size:11px;position:relative;transition:all 0.2s}
    .step.active{background:oklch(0.90 0.004 110);box-shadow:inset 0 1px 3px oklch(0 0 0/0.06),0 0 0 1px var(--sumi)}
    .step .step-n{position:absolute;top:-10px;left:10px;background:var(--bg-0);
      color:var(--muted);padding:1px 8px;font-size:9px;letter-spacing:1.5px;font-family:'JetBrains Mono',monospace}
    .step.active .step-n{color:var(--sumi)}
    .step h4{margin:0 0 4px;color:var(--sumi);letter-spacing:1.5px;font-size:11px;font-family:'Noto Serif SC',serif}
    .step.active h4{color:var(--sumi);font-weight:700}
  
    /* 橡胶通用按钮 */
    button{padding:5px 12px;font:inherit;font-size:10px;
      background:var(--rubber);color:var(--sumi);
      border:none;cursor:pointer;letter-spacing:1px;
      font-family:'JetBrains Mono',monospace;
      box-shadow:0 2px 5px oklch(0 0 0/0.10),0 1px 2px oklch(0 0 0/0.06),inset 0 1px 0 oklch(1 0 0/0.35),inset 0 -1px 0 oklch(0 0 0/0.06);
      background-image:radial-gradient(oklch(0 0 0/0.02) 1px,transparent 1px);background-size:3px 3px;
      transition:all 0.08s ease-out}
    button:hover{background-color:var(--rubber-hover)}
    button:active{box-shadow:inset 0 2px 5px oklch(0 0 0/0.12),inset 0 1px 2px oklch(0 0 0/0.08);transform:translateY(1px);background-color:var(--rubber-press)}
    button.primary{background:var(--sumi);color:var(--shironeri);box-shadow:0 2px 5px oklch(0 0 0/0.15),inset 0 1px 0 oklch(1 0 0/0.08),inset 0 -1px 0 oklch(0 0 0/0.3)}
  
    ::-webkit-scrollbar{width:4px;height:4px}
    ::-webkit-scrollbar-thumb{background:oklch(0.75 0.005 110);border-radius:0}
    ::-webkit-scrollbar-track{background:oklch(0.93 0.003 110)}
  
    .footer{text-align:center;color:var(--muted);padding:14px 0 6px;font-size:9px;letter-spacing:2px;font-family:'JetBrains Mono',monospace}
  
    /* sensory mesh popup */
    .mesh-popup{display:none;position:absolute;bottom:16px;left:16px;z-index:50;width:280px;padding:14px;
      background:oklch(0.93 0.003 110 / 0.97);box-shadow:inset 0 1px 4px oklch(0 0 0/0.06),0 4px 16px oklch(0 0 0/0.12);
      color:var(--text);font-size:11px}
    .mesh-popup h4{color:var(--sumi);font-family:'Noto Serif SC',serif;font-size:12px;margin:0 0 8px;letter-spacing:2px}
    .mesh-popup .mp-layer{display:inline-block;padding:2px 8px;font-size:9px;font-weight:600;margin-bottom:8px;background:var(--rubber);font-family:'JetBrains Mono',monospace}
    .mesh-popup .mp-analysis{color:var(--text);line-height:1.6}
    .mesh-popup-close{position:absolute;top:6px;right:10px;cursor:pointer;color:var(--muted);font-size:16px}
    /* layer detail HUD */
    .layer-hud{display:none;position:absolute;top:16px;right:16px;z-index:50;width:260px;padding:14px;
      background:oklch(0.93 0.003 110 / 0.97);box-shadow:inset 0 1px 4px oklch(0 0 0/0.06),0 4px 16px oklch(0 0 0/0.12);
      color:var(--text);font-size:11px}
    .layer-hud h4{font-family:'Noto Serif SC',serif;font-size:13px;margin:0 0 6px;letter-spacing:2px}
    .layer-hud .lh-desc{color:var(--muted);margin-bottom:10px;line-height:1.5}
    .layer-hud .lh-tiers{display:flex;flex-direction:column;gap:6px}
    .layer-hud-close{position:absolute;top:6px;right:10px;cursor:pointer;color:var(--muted);font-size:16px}
  
    /* ════ BUILD TEAM CHAT ════ */
    .chat-fab{position:fixed;bottom:24px;right:24px;z-index:2000;width:48px;height:48px;
      border:none;cursor:pointer;
      background:var(--sumi);display:flex;align-items:center;justify-content:center;
      font-size:20px;color:var(--shironeri);
      box-shadow:0 2px 8px oklch(0 0 0/0.15);transition:all 0.15s}
    .chat-fab:hover{background:oklch(0.25 0.008 110)}
    .chat-fab.has-badge::after{content:'';position:absolute;top:2px;right:2px;width:8px;height:8px;
      background:var(--shu)}
    .chat-panel{position:fixed;bottom:80px;right:24px;z-index:2001;width:400px;height:500px;
      display:none;flex-direction:column;
      background:oklch(0.95 0.003 110);
      box-shadow:0 4px 2
  ```
  
  ### 文件: `src/frontend/worldmonitor-ar-cas-pro.html`
  ```html
  <!DOCTYPE html>
  <html lang="zh-CN">
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>WorldMonitor AR-CAS Pro - 船舶避免碰撞增强现实系统（专业版）</title>
      <link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300;400;500;700&family=Noto+Serif:wght@200;300;400;600;900&family=Noto+Serif+SC:wght@200;300;400;600;900&family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap" rel="stylesheet">
      <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>
      <link href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css" rel="stylesheet" />
      <style>
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body {
              font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
              background: oklch(0.96 0.003 110);
              color: oklch(0.18 0.008 110);
              overflow: hidden;
              height: 100vh;
              position: relative;
          }
          /* Wabi-Sabi Rubber tokens */
          :root{--shironeri:oklch(0.96 0.003 110);--ishi:oklch(0.91 0.004 110);--kabe:oklch(0.85 0.005 110);--sumi:oklch(0.18 0.008 110);--sumi-3:oklch(0.55 0.005 110);--koke:oklch(0.52 0.04 160);--shu:oklch(0.48 0.07 22);--kitsune:oklch(0.56 0.05 70);--groove:oklch(0.82 0.004 110);--font-serif:'Noto Serif SC',serif;--font-sans:'Noto Sans SC',sans-serif;--font-mono:'JetBrains Mono',monospace}
          body::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;background-image:radial-gradient(oklch(0 0 0/.012) 1px,transparent 1px),radial-gradient(oklch(0 0 0/.008) 1px,transparent 1px);background-size:5px 5px,7px 7px;background-position:0 0,3px 3px}
          .seal{display:inline-block;font-size:10px;font-weight:900;color:var(--shironeri);background:var(--sumi);padding:1px 5px;line-height:1.3;font-family:var(--font-serif);vertical-align:middle;margin-right:4px}.seal-koke{background:var(--koke)}.seal-shu{background:var(--shu)}.seal-kitsune{background:var(--kitsune)}
          .header{background:var(--ishi) !important;border-bottom:1px solid var(--groove) !important}
          .header h1{background:none !important;-webkit-text-fill-color:var(--koke) !important;color:var(--koke) !important;font-family:var(--font-serif);font-size:16px !important}
          .sidebar{background:var(--ishi) !important;border-color:var(--groove) !important}
          .panel{background:var(--shironeri) !important;border-color:var(--groove) !important}
          .action-button,.action-link{background:oklch(0.52 0.04 160 / 0.06) !important;border-color:oklch(0.52 0.04 160 / 0.15) !important}
          .header {
              position: fixed;
              top: 0; left: 0; right: 0;
              height: 60px;
              background: oklch(0.91 0.004 110);
              border-bottom: 2px solid oklch(0.82 0.004 110);
              display: flex;
              align-items: center;
              justify-content: space-between;
              padding: 0 24px;
              z-index: 1000;
          }
          .header h1 {
              font-size: 20px;
              font-weight: 700;
              background: linear-gradient(90deg, oklch(0.52 0.04 160) 0%, oklch(0.52 0.04 160) 100%);
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
          .status-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: oklch(0.55 0.005 110); }
          .status-dot {
              width: 8px; height: 8px; border-radius: 50%;
              background: oklch(0.52 0.04 160);
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
              border-radius:0;
              border: 1px solid rgba(79,195,247,0.28);
              background: rgba(79,195,247,0.12);
              color: oklch(0.25 0.006 110);
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
              color: oklch(0.18 0.008 110);
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
              border-radius:0;
              padding: 16px;
              margin-bottom: 16px;
          }
          .panel h3 {
              font-size: 14px;
              font-weight: 600;
              color: oklch(0.52 0.04 160);
              margin-bottom: 12px;
              display: flex;
              align-items: center;
              gap: 8px;
          }
          .ais-target {
              background: linear-gradient(135deg, oklch(0 0 0 / 0.4) 0%, oklch(0 0 0 / 0.2) 100%);
              border-radius:0;
              padding: 14px;
              margin-bottom: 10px;
              border-left: 4px solid oklch(0.52 0.04 160);
              cursor: pointer;
              transition: all 0.3s;
          }
          .ais-target:hover {
              background: rgba(79,195,247,0.15);
              transform: translateX(6px);
              box-shadow: 0 4px 12px rgba(79,195,247,0.2);
          }
          .ais-target.high-risk { border-left-color: oklch(0.48 0.07 22); background: linear-gradient(135deg, rgba(245,101,101,0.15) 0%, oklch(0 0 0 / 0.3) 100%); }
          .ais-target.medium-risk { border-left-color: oklch(0.56 0.05 70); }
          .ais-target-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 10px;
          }
          .ais-target-type { font-weight: 700; color: oklch(0.52 0.04 160); font-size: 14px; }
          .ais-target-mmsi { color: oklch(0.55 0.005 110); font-size: 11px; }
          .ais-target-info {
              display: grid;
              grid-template-columns: 1fr 1fr;
              gap: 8px;
              font-size: 11px;
              color: oklch(0.55 0.005 110);
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
          .risk-badge.low { background: rgba(72,187,120,0.25); color: oklch(0.52 0.04 160); }
          .risk-badge.medium { background: rgba(246,173,85,0.25); color: oklch(0.56 0.05 70); }
          .risk-badge.high { background: rgba(245,101,101,0.25); color: oklch(0.48 0.07 22); }
          .colregs-badge { background: rgba(139,92,246,0.25); color: oklch(0.55 0.005 110); }
          .weather-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
          .weather-item {
              background: oklch(0 0 0 / 0.35);
              padding: 14px;
              border-radius:0;
              text-align: center;
          }
          .weather-label { font-size: 11px; color: oklch(0.55 0.005 110); margin-bottom: 6px; }
          .weather-value { font-size: 18px; font-weight: 700; color: oklch(0.52 0.04 160); }
          .port-item {
              display: flex;
              justify-content: space-between;
              align-items: center;
              padding: 12px;
              background: oklch(0 0 0 / 0.3);
              border-radius:0;
              margin-bottom: 8px;
          }
          .port-name { font-weight: 600; color: oklch(0.56 0.05 70); }
          .port-distance { font-size: 11px; color: oklch(0.55 0.005 110); }
          .right-panel {
              width: 360px;
              background: rgba(10,14,26,0.95);
              border-left: 1px solid rgba(79,195,247,0.2);
              overflow-y: auto;
              padding: 16px;
          }
          .camera-feed {
              background: oklch(0 0 0 / 0.6);
              border-radius:0;
              overflow: hidden;
              margin-bottom: 16px;
              position: relative;
          }
          .camera-feed img { width: 100%; height: 200px; object-fit: cover; }
          .ar-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; }
          .ar-target {
              position: absolute;
              width: 28px; height: 28px;
              border: 3px solid oklch(0.52 0.04 160);
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
              background: oklch(0 0 0 / 0.85);
              padding: 4px 8px;
              border-radius: 6px;
              font-size: 10px;
              white-space: nowrap;
              color: oklch(0.18 0.008 110);
              border: 1px solid rgba(79,195,247,0.4);
          }
          .ar-iceberg {
              position: absolute;
              width: 40px; height: 40px;
              background: linear-gradient(180deg, rgba(135,206,250,0.8) 0%, rgba(135,206,250,0.3) 100%);
              border: 2px solid oklch(0.52 0.04 160);
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
              border-left: 3px dashed oklch(0.56 0.05 70);
              border-right: 3px dashed oklch(0.56 0.05 70);
          }
          .ar-canyon-warning {
              position: absolute;
              bottom: 80px; left: 50%;
              transform: translateX(-50%);
              background: linear-gradient(135deg, rgba(245,101,101,0.95) 0%, rgba(245,101,101,0.8) 100%);
              padding: 10px 20px;
              border-radius:0;
              font-size: 13px;
              font-weight: 700;
              color: oklch(0.18 0.008 110);
              white-space: nowrap;
              box-shadow: 0 4px 20px rgba(245,101,101,0.5);
          }
          .ar-iceberg-warning {
              position: absolute;
              top: 80px; left: 50%;
              transform: translateX(-50%);
              background: linear-gradient(135deg, rgba(135,206,250,0.95) 0%, rgba(135,206,250,0.8) 100%);
              padding: 10px 20px;
              border-radius:0;
              font-size: 13px;
              font-weight: 700;
              color: oklch(0.18 0.008 110);
              white-space: nowrap;
              box-shadow: 0 4px 20px rgba(135,206,250,0.5);
          }
          .camera-info { padding: 14px; }
          .camera-name { font-weight: 700; color: oklch(0.18 0.008 110); margin-bottom: 6px; font-size: 13px; }
          .camera-status { font-size: 11px; color: oklch(0.52 0.04 160); }
          .alarm-feed {
              display: flex;
              flex-direction: column;
              gap: 10px;
          }
          .alarm-card {
              background: oklch(0 0 0 / 0.35);
              border-radius:0;
              padding: 12px;
              border-left: 4px solid oklch(0.52 0.04 160);
          }
          .alarm-card.level-WARNING {
              border-left-color: oklch(0.56 0.05 70);
          }
          .alarm-card.level-CRITICAL,
          .alarm-card.level-EMERGENCY {
              border-left-color: oklch(0.48 0.07 22);
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
              border-radius:0;
              font-size: 10px;
              font-weight: 700;
              background: rgba(72,187,120,0.2);
              color: oklch(0.52 0.04 160);
          }
          .alarm-card-level.WARNING {
              background: rgba(246,173,85,0.2);
              color: oklch(0.56 0.05 70);
          }
          .alarm-card-level.CRITICAL,
          .alarm-card-level.EMERGENCY {
              background: rgba(245,101,101,0.2);
              color: oklch(0.48 0.07 22);
          }
          .alarm-card-time {
              font-size: 11px;
              color: oklch(0.55 0.005 110);
          }
          .alarm-card-message {
              font-size: 12px;
              color: oklch(0.18 0.008 110);
              line-height: 1.5;
          }
          .alarm-card-source {
              margin-top: 8px;
              font-size: 10px;
              color: oklch(0.52 0.04 160);
              text-transform: uppercase;
              letter-spacing: 0.04em;
          }
          .route-info { background: oklch(0 0 0 / 0.35); border-radius:0; padding: 16px; }
          .route-point {
              display: flex;
              align-items: center;
              gap: 12px;
              padding: 10px 0;
              border-bottom: 1px solid rgba(79,195,247,0.2);
          }
          .route-point:last-child { border-bottom: none; }
          .route-dot { width: 14px; height: 14px; border-radius: 50%; background: oklch(0.52 0.04 160); }
          .route-dot.waypoint { background: oklch(0.56 0.05 70); }
          .route-label { font-size: 12px; color: oklch(0.55 0.005 110); }
          .colregs-alert {
              background: linear-gradient(135deg, rgba(245,101,101,0.15) 0%, oklch(0 0 0 / 0.3) 100%);
              border: 1px solid oklch(0.48 0.07 22);
              border-radius:0;
              padding: 14px;
              margin-bottom: 14px;
          }
          .colregs-alert-title {
              font-weight: 700;
              colo
  ```
  
  ### 文件: `src/frontend/worldmonitor-ar-cas-pro.v1.bak.html`
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
              background: oklch(0.96 0.003 110);
              color: oklch(0.18 0.008 110);
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
              background: linear-gradient(90deg, oklch(0.52 0.04 160) 0%, oklch(0.52 0.04 160) 100%);
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
          .status-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: oklch(0.55 0.005 110); }
          .status-dot {
              width: 8px; height: 8px; border-radius: 50%;
              background: oklch(0.52 0.04 160);
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
              border-radius:0;
              border: 1px solid rgba(79,195,247,0.28);
              background: rgba(79,195,247,0.12);
              color: oklch(0.25 0.006 110);
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
              color: oklch(0.18 0.008 110);
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
              border-radius:0;
              padding: 16px;
              margin-bottom: 16px;
          }
          .panel h3 {
              font-size: 14px;
              font-weight: 600;
              color: oklch(0.52 0.04 160);
              margin-bottom: 12px;
              display: flex;
              align-items: center;
              gap: 8px;
          }
          .ais-target {
              background: linear-gradient(135deg, oklch(0 0 0 / 0.4) 0%, oklch(0 0 0 / 0.2) 100%);
              border-radius:0;
              padding: 14px;
              margin-bottom: 10px;
              border-left: 4px solid oklch(0.52 0.04 160);
              cursor: pointer;
              transition: all 0.3s;
          }
          .ais-target:hover {
              background: rgba(79,195,247,0.15);
              transform: translateX(6px);
              box-shadow: 0 4px 12px rgba(79,195,247,0.2);
          }
          .ais-target.high-risk { border-left-color: oklch(0.48 0.07 22); background: linear-gradient(135deg, rgba(245,101,101,0.15) 0%, oklch(0 0 0 / 0.3) 100%); }
          .ais-target.medium-risk { border-left-color: oklch(0.56 0.05 70); }
          .ais-target-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 10px;
          }
          .ais-target-type { font-weight: 700; color: oklch(0.52 0.04 160); font-size: 14px; }
          .ais-target-mmsi { color: oklch(0.55 0.005 110); font-size: 11px; }
          .ais-target-info {
              display: grid;
              grid-template-columns: 1fr 1fr;
              gap: 8px;
              font-size: 11px;
              color: oklch(0.55 0.005 110);
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
          .risk-badge.low { background: rgba(72,187,120,0.25); color: oklch(0.52 0.04 160); }
          .risk-badge.medium { background: rgba(246,173,85,0.25); color: oklch(0.56 0.05 70); }
          .risk-badge.high { background: rgba(245,101,101,0.25); color: oklch(0.48 0.07 22); }
          .colregs-badge { background: rgba(139,92,246,0.25); color: oklch(0.55 0.005 110); }
          .weather-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
          .weather-item {
              background: oklch(0 0 0 / 0.35);
              padding: 14px;
              border-radius:0;
              text-align: center;
          }
          .weather-label { font-size: 11px; color: oklch(0.55 0.005 110); margin-bottom: 6px; }
          .weather-value { font-size: 18px; font-weight: 700; color: oklch(0.52 0.04 160); }
          .port-item {
              display: flex;
              justify-content: space-between;
              align-items: center;
              padding: 12px;
              background: oklch(0 0 0 / 0.3);
              border-radius:0;
              margin-bottom: 8px;
          }
          .port-name { font-weight: 600; color: oklch(0.56 0.05 70); }
          .port-distance { font-size: 11px; color: oklch(0.55 0.005 110); }
          .right-panel {
              width: 360px;
              background: rgba(10,14,26,0.95);
              border-left: 1px solid rgba(79,195,247,0.2);
              overflow-y: auto;
              padding: 16px;
          }
          .camera-feed {
              background: oklch(0 0 0 / 0.6);
              border-radius:0;
              overflow: hidden;
              margin-bottom: 16px;
              position: relative;
          }
          .camera-feed img { width: 100%; height: 200px; object-fit: cover; }
          .ar-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; }
          .ar-target {
              position: absolute;
              width: 28px; height: 28px;
              border: 3px solid oklch(0.52 0.04 160);
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
              background: oklch(0 0 0 / 0.85);
              padding: 4px 8px;
              border-radius: 6px;
              font-size: 10px;
              white-space: nowrap;
              color: oklch(0.18 0.008 110);
              border: 1px solid rgba(79,195,247,0.4);
          }
          .ar-iceberg {
              position: absolute;
              width: 40px; height: 40px;
              background: linear-gradient(180deg, rgba(135,206,250,0.8) 0%, rgba(135,206,250,0.3) 100%);
              border: 2px solid oklch(0.52 0.04 160);
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
              border-left: 3px dashed oklch(0.56 0.05 70);
              border-right: 3px dashed oklch(0.56 0.05 70);
          }
          .ar-canyon-warning {
              position: absolute;
              bottom: 80px; left: 50%;
              transform: translateX(-50%);
              background: linear-gradient(135deg, rgba(245,101,101,0.95) 0%, rgba(245,101,101,0.8) 100%);
              padding: 10px 20px;
              border-radius:0;
              font-size: 13px;
              font-weight: 700;
              color: oklch(0.18 0.008 110);
              white-space: nowrap;
              box-shadow: 0 4px 20px rgba(245,101,101,0.5);
          }
          .ar-iceberg-warning {
              position: absolute;
              top: 80px; left: 50%;
              transform: translateX(-50%);
              background: linear-gradient(135deg, rgba(135,206,250,0.95) 0%, rgba(135,206,250,0.8) 100%);
              padding: 10px 20px;
              border-radius:0;
              font-size: 13px;
              font-weight: 700;
              color: oklch(0.18 0.008 110);
              white-space: nowrap;
              box-shadow: 0 4px 20px rgba(135,206,250,0.5);
          }
          .camera-info { padding: 14px; }
          .camera-name { font-weight: 700; color: oklch(0.18 0.008 110); margin-bottom: 6px; font-size: 13px; }
          .camera-status { font-size: 11px; color: oklch(0.52 0.04 160); }
          .alarm-feed {
              display: flex;
              flex-direction: column;
              gap: 10px;
          }
          .alarm-card {
              background: oklch(0 0 0 / 0.35);
              border-radius:0;
              padding: 12px;
              border-left: 4px solid oklch(0.52 0.04 160);
          }
          .alarm-card.level-WARNING {
              border-left-color: oklch(0.56 0.05 70);
          }
          .alarm-card.level-CRITICAL,
          .alarm-card.level-EMERGENCY {
              border-left-color: oklch(0.48 0.07 22);
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
              border-radius:0;
              font-size: 10px;
              font-weight: 700;
              background: rgba(72,187,120,0.2);
              color: oklch(0.52 0.04 160);
          }
          .alarm-card-level.WARNING {
              background: rgba(246,173,85,0.2);
              color: oklch(0.56 0.05 70);
          }
          .alarm-card-level.CRITICAL,
          .alarm-card-level.EMERGENCY {
              background: rgba(245,101,101,0.2);
              color: oklch(0.48 0.07 22);
          }
          .alarm-card-time {
              font-size: 11px;
              color: oklch(0.55 0.005 110);
          }
          .alarm-card-message {
              font-size: 12px;
              color: oklch(0.18 0.008 110);
              line-height: 1.5;
          }
          .alarm-card-source {
              margin-top: 8px;
              font-size: 10px;
              color: oklch(0.52 0.04 160);
              text-transform: uppercase;
              letter-spacing: 0.04em;
          }
          .route-info { background: oklch(0 0 0 / 0.35); border-radius:0; padding: 16px; }
          .route-point {
              display: flex;
              align-items: center;
              gap: 12px;
              padding: 10px 0;
              border-bottom: 1px solid rgba(79,195,247,0.2);
          }
          .route-point:last-child { border-bottom: none; }
          .route-dot { width: 14px; height: 14px; border-radius: 50%; background: oklch(0.52 0.04 160); }
          .route-dot.waypoint { background: oklch(0.56 0.05 70); }
          .route-label { font-size: 12px; color: oklch(0.55 0.005 110); }
          .colregs-alert {
              background: linear-gradient(135deg, rgba(245,101,101,0.15) 0%, oklch(0 0 0 / 0.3) 100%);
              border: 1px solid oklch(0.48 0.07 22);
              border-radius:0;
              padding: 14px;
              margin-bottom: 14px;
          }
          .colregs-alert-title {
              font-weight: 700;
              color: oklch(0.48 0.07 22);
              margin-bottom: 10px;
              display: flex;
              align-items: center;
              gap: 8px;
              font-size: 13px;
          }
          .colregs-rule { font-size: 12px; color: oklch(0.48 0.07 22); line-height: 1.6; }
          .cpa-tcpa { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 14px; }
          .cpa-item {
              background: oklch(0 0 0 / 0.4);
              padding: 12px;
              border-radius:0;
              text-align: center;
          }
          .cpa-label { font-size: 10px; color: oklch(0.55 0.005 110); margin-bottom: 6px; text-transform: uppercase; }
          .cpa-value { font-size: 16px; font-weight: 700; color: oklch(0.18 0.008 110); }
          .cpa-value.danger { color: oklch(0.48 0.07 22); }
          .cpa-value.warning { color: oklch(0.56 0.05 70); }
          .cpa-value.safe { color: oklch(0.52 0.04 160); }
          .maplibregl-map { background: oklch(0.96 0.003 110); }
          .maplibregl-ctrl-bottom-left, .maplibregl-ctrl-bottom-right { display: none; }
          .special-alert {
              background: linear-gradient(135deg, rgba(245,101,101,0.2) 0%, oklch(0 0 0 / 0.4) 100%);
              border: 2px solid oklch(0.48 0.07 22);
              border-radius:0;
              padding: 16px;
              margin-bottom: 16px;
          }
          .special-alert-title {
              font-weight: 700;
              color: oklch(0.48 0.07 22);
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
              background: linear-gradient(180deg, rgba(8,16,30,0.96) 0%, 
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
      const hsContainer = docume
  ```
  
  (后续文件因 token 预算已省略)
  
  (后续文件因 token 预算已省略)
  
  (后续文件因 token 预算已省略)
  
  
  ## 前序步骤的产出 (管线共享工作区)
  
  ### 步骤 01: pm_decompose.md
  
  # PM分解 — project_manager
  
  任务: 给build团队的PM一个任务将http://localhost:5173/worldmonitor-ar-cas-pro.html的菜单AR-CAS-PRO的功能全部平移到数字孪生页面的AR-CAS...
  步骤: pm_decompose
  Agent: build_pm
  
  ---
  
  📋 任务: 6a2426e3-538
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
    给build团队的PM一个任务将http://localhost:5173/worldmonitor-ar-cas-pro.html的菜单AR-CAS-PRO的功能全部平移到数字孪生页面的AR-CAS...
    给build团队的PM一个任务将http://localhost:5173/worldmonitor-ar-cas-pro.html的菜单AR-CAS-PRO的功能全部平移到数字孪生页面的AR-CAS-PRO菜单中来，根据当前的数字孪生页面赋予现实增强的能力，就是当前的页面是他来做AR的基础
    
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
    ... (共 830 个 src/ 文件)
    
    ```
    
    ### 文件: `src/frontend/datacenter-digital-twin.html`
    ```html
    <!DOCTYPE html>
    <html lang="zh-CN" data-obc-theme="dusk">
    <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Digital Twin · 物理↔数字一一映射 · xFirst Principle</title>
    <link rel="stylesheet" href="/css/openbridge-theme.css">
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300;400;500;700&family=Noto+Serif:wght@200;300;400;600;900&family=Noto+Serif+SC:wght@200;300;400;600;900&family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap');
      :root {
        /* ── 侘寂橡胶 · Wabi-Sabi Rubber ── */
        --bg-0:oklch(0.96 0.003 110); --bg-1:oklch(0.91 0.004 110); --bg-2:oklch(0.85 0.005 110);
        --grid:oklch(0 0 0 / 0.03); --line:oklch(0.82 0.004 110);
        --accent:oklch(0.18 0.008 110); --accent-2:oklch(0.52 0.04 160); --accent-3:oklch(0.55 0.005 110);
        --warn:oklch(0.56 0.05 70); --danger:oklch(0.48 0.07 22);
        --text:oklch(0.18 0.008 110); --muted:oklch(0.55 0.005 110);
        --rack:oklch(0.18 0.008 110); --pdu:oklch(0.56 0.05 70); --ats:oklch(0.48 0.07 22); --busway:oklch(0.55 0.005 110);
        --cold:oklch(0.52 0.04 160); --hot:oklch(0.48 0.07 22); --pipe:oklch(0.52 0.04 160); --floor:oklch(0.72 0.006 110);
        /* rubber button system */
        --rubber:oklch(0.72 0.006 110); --rubber-hover:oklch(0.68 0.007 110); --rubber-press:oklch(0.64 0.007 110);
        --sumi:oklch(0.18 0.008 110); --koke:oklch(0.52 0.04 160); --shu:oklch(0.48 0.07 22);
        --kitsune:oklch(0.56 0.05 70); --shironeri:oklch(0.96 0.003 110);
        --groove:oklch(0.82 0.004 110); --ridge:oklch(1.00 0 0 / 0.6);
      }
      *{box-sizing:border-box;margin:0;padding:0}
      html,body{margin:0;padding:0;height:100%;font-family:'Noto Sans SC','JetBrains Mono',sans-serif;color:var(--text);-webkit-font-smoothing:antialiased}
      body{
        background:var(--bg-0);
        overflow-x:hidden;
      }
      /* 和紙质感 — 微粒紋理 */
      body::before{
        content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
        background-image:
          radial-gradient(oklch(0 0 0 / 0.012) 1px, transparent 1px),
          radial-gradient(oklch(0 0 0 / 0.008) 1px, transparent 1px);
        background-size:5px 5px, 7px 7px;
        background-position:0 0, 3px 3px;
      }
      .container{position:relative;z-index:1;max-width:100%;margin:0 auto;padding:18px 24px}
    
      .hud{display:flex;align-items:center;justify-content:space-between;
        padding:14px 0;border-bottom:1px solid var(--groove)}
      .hud .brand{display:flex;align-items:center;gap:14px}
      .hud .logo{width:34px;height:34px;
        background:var(--sumi);
        display:flex;align-items:center;justify-content:center;
        font-family:'Noto Serif SC',serif;font-size:18px;font-weight:900;color:var(--shironeri)}
      .hud h1{margin:0;font-family:'Noto Serif SC',serif;font-size:13px;letter-spacing:3px;font-weight:300;color:var(--muted)}
      .hud h1 strong{color:var(--text);font-weight:600}
      .hud .sub{font-size:10px;color:var(--muted);letter-spacing:2px;font-family:'JetBrains Mono',monospace}
      .hud .pills{display:flex;gap:6px;align-items:center;flex-wrap:wrap;justify-content:flex-end}
      /* 橡胶按钮 pill */
      .pill{padding:5px 14px;font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:1.5px;
        border:none;cursor:pointer;user-select:none;text-decoration:none;text-transform:uppercase;
        background:var(--rubber);color:var(--sumi);
        box-shadow:0 2px 5px oklch(0 0 0/0.12),0 1px 2px oklch(0 0 0/0.08),inset 0 1px 0 oklch(1 0 0/0.35),inset 0 -1px 0 oklch(0 0 0/0.08);
        background-image:radial-gradient(oklch(0 0 0/0.02) 1px,transparent 1px);background-size:3px 3px;
        transition:all 0.08s ease-out}
      .pill:hover{background-color:var(--rubber-hover)}
      .pill:active{box-shadow:inset 0 2px 5px oklch(0 0 0/0.15),inset 0 1px 2px oklch(0 0 0/0.10);transform:translateY(1px);background-color:var(--rubber-press)}
      .pill.live{background:var(--sumi);color:var(--shironeri);box-shadow:0 2px 5px oklch(0 0 0/0.15),inset 0 1px 0 oklch(1 0 0/0.08),inset 0 -1px 0 oklch(0 0 0/0.3)}
      .pill.live::before{content:'';display:inline-block;width:5px;height:5px;
        background:var(--koke);margin-right:6px;animation:blink 2.5s infinite}
      .pill.ws{background:var(--sumi);color:var(--shironeri)}
      .pill.ws.off{background:oklch(0.85 0.005 110);color:var(--shu)}
      @keyframes blink{50%{opacity:0.3}}
    
      .fp-banner{margin-top:14px;padding:12px 18px;
        background:oklch(0.93 0.003 110);
        box-shadow:inset 0 1px 4px oklch(0 0 0/0.05),0 1px 0 var(--ridge);
        font-size:12px;color:var(--text);
        display:flex;gap:18px;align-items:center;flex-wrap:wrap}
      .fp-banner .formula{font-family:'JetBrains Mono',monospace;color:var(--sumi);font-weight:700}
    
      .panel{padding:14px 16px;
        background:oklch(0.93 0.003 110);
        box-shadow:inset 0 1px 5px oklch(0 0 0/0.05),0 1px 0 oklch(1 0 0/0.5)}
      .panel h2{margin:0 0 10px;font-family:'Noto Serif SC',serif;font-size:12px;letter-spacing:3px;color:var(--sumi);
        text-transform:uppercase;display:flex;justify-content:space-between;align-items:center}
      .badge{font-family:'JetBrains Mono',monospace;font-size:8px;color:var(--muted);padding:2px 8px;border:1px solid var(--groove);letter-spacing:1.5px}
      .section-title{font-family:'Noto Serif SC',serif;font-size:11px;color:var(--muted);letter-spacing:3px;margin:14px 0 6px;text-transform:uppercase}
    
      .grid-21{display:grid;grid-template-columns:2fr 1fr;gap:14px}
      .grid-12{display:grid;grid-template-columns:1fr 2fr;gap:14px}
    
      /* 3D twin viewport — 石壁观察窗 */
      .twin-viewport{position:relative;width:100%;height:680px;
        overflow:hidden;
        padding:8px;background:oklch(0.85 0.005 110);
        box-shadow:inset 0 1px 0 oklch(1 0 0/0.3),0 1px 0 oklch(0 0 0/0.04)}
      .twin-viewport canvas{display:block}
      .twin-overlay{position:absolute;top:8px;left:8px;right:8px;padding:10px 14px;
        display:flex;justify-content:space-between;pointer-events:none;font-size:11px}
      .twin-overlay .tag{background:oklch(0.93 0.003 110 / 0.85);
        padding:4px 10px;color:var(--sumi);letter-spacing:1.5px;pointer-events:auto;
        font-family:'JetBrains Mono',monospace;font-size:9px}
      .twin-overlay .tag.live{color:var(--koke)}
      .twin-controls{position:absolute;left:16px;top:52px;
        display:flex;flex-direction:column;gap:4px;font-size:10px;
        max-height:calc(100% - 64px);overflow-y:auto;padding-bottom:10px}
      /* 橡胶图层按钮 */
      .twin-controls .layer-btn{
        padding:4px 10px;background:oklch(0.88 0.004 110);
        border:none;color:var(--sumi);cursor:pointer;letter-spacing:1.5px;text-align:left;min-width:160px;
        display:flex;justify-content:space-between;align-items:center;gap:8px;
        font-family:'JetBrains Mono',monospace;font-size:9px;
        box-shadow:0 1px 3px oklch(0 0 0/0.08),inset 0 1px 0 oklch(1 0 0/0.4),inset 0 -1px 0 oklch(0 0 0/0.05);
        background-image:radial-gradient(oklch(0 0 0/0.02) 1px,transparent 1px);background-size:3px 3px;
        transition:all 0.08s ease-out;
      }
      .twin-controls .layer-btn:active{box-shadow:inset 0 2px 4px oklch(0 0 0/0.12);transform:translateY(1px);background-color:oklch(0.82 0.004 110)}
      .twin-controls .layer-btn .swatch{width:8px;height:8px;display:inline-block}
      .twin-controls .layer-btn.off{opacity:0.35;text-decoration:line-through}
      .twin-legend{position:absolute;right:16px;bottom:16px;
        background:oklch(0.93 0.003 110 / 0.9);
        padding:8px 12px;font-size:10px;line-height:1.7;color:var(--muted);font-family:'JetBrains Mono',monospace}
      .twin-legend b{color:var(--text)}
      .twin-readout{position:absolute;right:16px;top:68px;width:240px;
        background:oklch(0.93 0.003 110 / 0.95);
        box-shadow:inset 0 1px 4px oklch(0 0 0/0.06),0 2px 8px oklch(0 0 0/0.1);
        padding:10px 12px;font-size:11px;color:var(--text);display:none}
      .twin-readout.show{display:block}
      .twin-readout h4{margin:0 0 6px;color:var(--sumi);font-family:'Noto Serif SC',serif;font-size:12px;letter-spacing:2px}
      .twin-readout .row{display:flex;justify-content:space-between;padding:2px 0;border-bottom:1px solid oklch(0.90 0.003 110)}
      .twin-readout .row .v{color:var(--koke);font-weight:700;font-family:'JetBrains Mono',monospace}
    
      /* mapping list */
      .map-list{display:flex;flex-direction:column;gap:6px}
      .map-item{padding:8px 10px;
        background:oklch(0.93 0.003 110);box-shadow:inset 0 1px 3px oklch(0 0 0/0.04),0 1px 0 oklch(1 0 0/0.3);
        font-size:11px;cursor:pointer;
        display:grid;grid-template-columns:10px 1fr auto;gap:8px;align-items:center;transition:background 0.15s}
      .map-item:hover{background:oklch(0.90 0.003 110)}
      .map-item .dot{width:8px;height:8px}
      .map-item .name{color:var(--text);font-weight:500;letter-spacing:0.5px;font-size:10px}
      .map-item .phys{font-size:9px;color:var(--muted);margin-top:1px}
      .map-item .v{font-size:12px;color:var(--sumi);font-weight:600;font-family:'JetBrains Mono',monospace;font-feature-settings:'tnum'}
    
      /* KPI strip — 石硯嵌入卡 */
      .kpi-strip{display:grid;grid-template-columns:repeat(7,1fr);gap:10px;margin:14px 0}
      .kpi{padding:12px 14px;
        background:oklch(0.93 0.003 110);
        box-shadow:inset 0 1px 4px oklch(0 0 0/0.05),0 1px 0 oklch(1 0 0/0.4);
        position:relative;overflow:hidden}
      .kpi::after{content:'';position:absolute;bottom:0;left:0;height:1px;width:100%;
        background:var(--groove)}
      .kpi .label{font-size:8px;color:var(--muted);letter-spacing:2.5px;text-transform:uppercase;font-family:'JetBrains Mono',monospace}
      .kpi .value{font-size:22px;font-weight:600;color:var(--sumi);margin:4px 0 2px;font-family:'JetBrains Mono',monospace;font-feature-settings:'tnum'}
      .kpi .unit{font-size:10px;color:var(--muted);margin-left:2px}
      .kpi .delta{font-size:10px;color:var(--koke)}
    
      /* device cards — 石硯卡片 */
      .dev-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:6px;
        max-height:260px;overflow-y:auto;padding-right:4px}
      .dev-card{padding:8px 10px;
        background:oklch(0.93 0.003 110);box-shadow:inset 0 1px 3px oklch(0 0 0/0.04),0 1px 0 oklch(1 0 0/0.3);
        font-size:10px;cursor:pointer;transition:all .12s}
      .dev-card:hover{background:oklch(0.90 0.003 110)}
      .dev-card.hot{border-left:2px solid var(--kitsune)}
      .dev-card.crit{border-left:2px solid var(--shu)}
      .dev-card .id{color:var(--sumi);font-weight:600;font-size:10px;letter-spacing:0.5px;display:flex;justify-content:space-between;font-family:'JetBrains Mono',monospace}
      .dev-card .id .typ{color:var(--muted);font-size:8px;letter-spacing:1px}
      .dev-card .pw{font-size:16px;color:var(--sumi);font-weight:600;font-family:'JetBrains Mono',monospace;font-feature-settings:'tnum';margin:2px 0}
      .dev-card .ln{font-size:9px;color:var(--muted)}
    
      /* energy flow svg */
      svg.flow{width:100%;height:300px}
      .flow .node{fill:oklch(0.93 0.003 110);stroke:var(--sumi);stroke-width:1}
      .flow .label{fill:var(--text);font-size:11px;font-family:'JetBrains Mono',monospace}
      .flow .sublabel{fill:var(--muted);font-size:9px;font-family:'JetBrains Mono',monospace}
    
      /* ratchet steps */
      .ratchet-loop{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:6px}
      .step{padding:10px 12px;
        background:oklch(0.93 0.003 110);box-shadow:inset 0 1px 3px oklch(0 0 0/0.04),0 1px 0 oklch(1 0 0/0.3);
        font-size:11px;position:relative;transition:all 0.2s}
      .step.active{background:oklch(0.90 0.004 110);box-shadow:inset 0 1px 3px oklch(0 0 0/0.06),0 0 0 1px var(--sumi)}
      .step .step-n{position:absolute;top:-10px;left:10px;background:var(--bg-0);
        color:var(--muted);padding:1px 8px;font-size:9px;letter-spacing:1.5px;font-family:'JetBrains Mono',monospace}
      .step.active .step-n{color:var(--sumi)}
      .step h4{margin:0 0 4px;color:var(--sumi);letter-spacing:1.5px;font-size:11px;font-family:'Noto Serif SC',serif}
      .step.active h4{color:var(--sumi);font-weight:700}
    
      /* 橡胶通用按钮 */
      button{padding:5px 12px;font:inherit;font-size:10px;
        background:var(--rubber);color:var(--sumi);
        border:none;cursor:pointer;letter-spacing:1px;
        font-family:'JetBrains Mono',monospace;
        box-shadow:0 2px 5px oklch(0 0 0/0.10),0 1px 2px oklch(0 0 0/0.06),inset 0 1px 0 oklch(1 0 0/0.35),inset 0 -1px 0 oklch(0 0 0/0.06);
        background-image:radial-gradient(oklch(0 0 0/0.02) 1px,transparent 1px);background-size:3px 3px;
        transition:all 0.08s ease-out}
      button:hover{background-color:var(--rubber-hover)}
      button:active{box-shadow:inset 0 2px 5px oklch(0 0 0/0.12),inset 0 1px 2px oklch(0 0 0/0.08);transform:translateY(1px);background-color:var(--rubber-press)}
      button.primary{background:var(--sumi);color:var(--shironeri);box-shadow:0 2px 5px oklch(0 0 0/0.15),inset 0 1px 0 oklch(1 0 0/0.08),inset 0 -1px 0 oklch(0 0 0/0.3)}
    
      ::-webkit-scrollbar{width:4px;height:4px}
      ::-webkit-scrollbar-thumb{background:oklch(0.75 0.005 110);border-radius:0}
      ::-webkit-scrollbar-track{background:oklch(0.93 0.003 110)}
    
      .footer{text-align:center;color:var(--muted);padding:14px 0 6px;font-size:9px;letter-spacing:2px;font-family:'JetBrains Mono',monospace}
    
      /* sensory mesh popup */
      .mesh-popup{display:none;position:absolute;bottom:16px;left:16px;z-index:50;width:280px;padding:14px;
        background:oklch(0.93 0.003 110 / 0.97);box-shadow:inset 0 1px 4px oklch(0 0 0/0.06),0 4px 16px oklch(0 0 0/0.12);
        color:var(--text);font-size:11px}
      .mesh-popup h4{color:var(--sumi);font-family:'Noto Serif SC',serif;font-size:12px;margin:0 0 8px;letter-spacing:2px}
      .mesh-popup .mp-layer{display:inline-block;padding:2px 8px;font-size:9px;font-weight:600;margin-bottom:8px;background:var(--rubber);font-family:'JetBrains Mono',monospace}
      .mesh-popup .mp-analysis{color:var(--text);line-height:1.6}
      .mesh-popup-close{position:absolute;top:6px;right:10px;cursor:pointer;color:var(--muted);font-size:16px}
      /* layer detail HUD */
      .layer-hud{display:none;position:absolute;top:16px;right:16px;z-index:50;width:260px;padding:14px;
        background:oklch(0.93 0.003 110 / 0.97);box-shadow:inset 0 1px 4px oklch(0 0 0/0.06),0 4px 16px oklch(0 0 0/0.12);
        color:var(--text);font-size:11px}
      .layer-hud h4{font-family:'Noto Serif SC',serif;font-size:13px;margin:0 0 6px;letter-spacing:2px}
      .layer-hud .lh-desc{color:var(--muted);margin-bottom:10px;line-height:1.5}
      .layer-hud .lh-tiers{display:flex;flex-direction:column;gap:6px}
      .layer-hud-close{position:absolute;top:6px;right:10px;cursor:pointer;color:var(--muted);font-size:16px}
    
      /* ════ BUILD TEAM CHAT ════ */
      .chat-fab{position:fixed;bottom:24px;right:24px;z-index:2000;width:48px;height:48px;
        border:none;cursor:pointer;
        background:var(--sumi);display:flex;align-items:center;justify-content:center;
        font-size:20px;color:var(--shironeri);
        box-shadow:0 2px 8px oklch(0 0 0/0.15);transition:all 0.15s}
      .chat-fab:hover{background:oklch(0.25 0.008 110)}
      .chat-fab.has-badge::after{content:'';position:absolute;top:2px;right:2px;width:8px;height:8px;
        background:var(--shu)}
      .chat-panel{position:fixed;bottom:80px;right:24px;z-index:2001;width:400px;height:500px;
        display:none;flex-direction:column;
        background:oklch(0.95 0.003 110);
        box-shadow:0 4px 2
    ```
    
    ### 文件: `src/frontend/worldmonitor-ar-cas-pro.html`
    ```html
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WorldMonitor AR-CAS Pro - 船舶避免碰撞增强现实系统（专业版）</title>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300;400;500;700&family=Noto+Serif:wght@200;300;400;600;900&family=Noto+Serif+SC:wght@200;300;400;600;900&family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap" rel="stylesheet">
        <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>
        <link href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css" rel="stylesheet" />
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
                background: oklch(0.96 0.003 110);
                color: oklch(0.18 0.008 110);
                overflow: hidden;
                height: 100vh;
                position: relative;
            }
            /* Wabi-Sabi Rubber tokens */
            :root{--shironeri:oklch(0.96 0.003 110);--ishi:oklch(0.91 0.004 110);--kabe:oklch(0.85 0.005 110);--sumi:oklch(0.18 0.008 110);--sumi-3:oklch(0.55 0.005 110);--koke:oklch(0.52 0.04 160);--shu:oklch(0.48 0.07 22);--kitsune:oklch(0.56 0.05 70);--groove:oklch(0.82 0.004 110);--font-serif:'Noto Serif SC',serif;--font-sans:'Noto Sans SC',sans-serif;--font-mono:'JetBrains Mono',monospace}
            body::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;background-image:radial-gradient(oklch(0 0 0/.012) 1px,transparent 1px),radial-gradient(oklch(0 0 0/.008) 1px,transparent 1px);background-size:5px 5px,7px 7px;background-position:0 0,3px 3px}
            .seal{display:inline-block;font-size:10px;font-weight:900;color:var(--shironeri);background:var(--sumi);padding:1px 5px;line-height:1.3;font-family:var(--font-serif);vertical-align:middle;margin-right:4px}.seal-koke{background:var(--koke)}.seal-shu{background:var(--shu)}.seal-kitsune{background:var(--kitsune)}
            .header{background:var(--ishi) !important;border-bottom:1px solid var(--groove) !important}
            .header h1{background:none !important;-webkit-text-fill-color:var(--koke) !important;color:var(--koke) !important;font-family:var(--font-serif);font-size:16px !important}
            .sidebar{background:var(--ishi) !important;border-color:var(--groove) !important}
            .panel{background:var(--shironeri) !important;border-color:var(--groove) !important}
            .action-button,.action-link{background:oklch(0.52 0.04 160 / 0.06) !important;border-color:oklch(0.52 0.04 160 / 0.15) !important}
            .header {
                position: fixed;
                top: 0; left: 0; right: 0;
                height: 60px;
                background: oklch(0.91 0.004 110);
                border-bottom: 2px solid oklch(0.82 0.004 110);
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 24px;
                z-index: 1000;
            }
            .header h1 {
                font-size: 20px;
                font-weight: 700;
                background: linear-gradient(90deg, oklch(0.52 0.04 160) 0%, oklch(0.52 0.04 160) 100%);
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
            .status-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: oklch(0.55 0.005 110); }
            .status-dot {
                width: 8px; height: 8px; border-radius: 50%;
                background: oklch(0.52 0.04 160);
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
                border-radius:0;
                border: 1px solid rgba(79,195,247,0.28);
                background: rgba(79,195,247,0.12);
                color: oklch(0.25 0.006 110);
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
                color: oklch(0.18 0.008 110);
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
                border-radius:0;
                padding: 16px;
                margin-bottom: 16px;
            }
            .panel h3 {
                font-size: 14px;
                font-weight: 600;
                color: oklch(0.52 0.04 160);
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .ais-target {
                background: linear-gradient(135deg, oklch(0 0 0 / 0.4) 0%, oklch(0 0 0 / 0.2) 100%);
                border-radius:0;
                padding: 14px;
                margin-bottom: 10px;
                border-left: 4px solid oklch(0.52 0.04 160);
                cursor: pointer;
                transition: all 0.3s;
            }
            .ais-target:hover {
                background: rgba(79,195,247,0.15);
                transform: translateX(6px);
                box-shadow: 0 4px 12px rgba(79,195,247,0.2);
            }
            .ais-target.high-risk { border-left-color: oklch(0.48 0.07 22); background: linear-gradient(135deg, rgba(245,101,101,0.15) 0%, oklch(0 0 0 / 0.3) 100%); }
            .ais-target.medium-risk { border-left-color: oklch(0.56 0.05 70); }
            .ais-target-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .ais-target-type { font-weight: 700; color: oklch(0.52 0.04 160); font-size: 14px; }
            .ais-target-mmsi { color: oklch(0.55 0.005 110); font-size: 11px; }
            .ais-target-info {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                font-size: 11px;
                color: oklch(0.55 0.005 110);
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
            .risk-badge.low { background: rgba(72,187,120,0.25); color: oklch(0.52 0.04 160); }
            .risk-badge.medium { background: rgba(246,173,85,0.25); color: oklch(0.56 0.05 70); }
            .risk-badge.high { background: rgba(245,101,101,0.25); color: oklch(0.48 0.07 22); }
            .colregs-badge { background: rgba(139,92,246,0.25); color: oklch(0.55 0.005 110); }
            .weather-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
            .weather-item {
                background: oklch(0 0 0 / 0.35);
                padding: 14px;
                border-radius:0;
                text-align: center;
            }
            .weather-label { font-size: 11px; color: oklch(0.55 0.005 110); margin-bottom: 6px; }
            .weather-value { font-size: 18px; font-weight: 700; color: oklch(0.52 0.04 160); }
            .port-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px;
                background: oklch(0 0 0 / 0.3);
                border-radius:0;
                margin-bottom: 8px;
            }
            .port-name { font-weight: 600; color: oklch(0.56 0.05 70); }
            .port-distance { font-size: 11px; color: oklch(0.55 0.005 110); }
            .right-panel {
                width: 360px;
                background: rgba(10,14,26,0.95);
                border-left: 1px solid rgba(79,195,247,0.2);
                overflow-y: auto;
                padding: 16px;
            }
            .camera-feed {
                background: oklch(0 0 0 / 0.6);
                border-radius:0;
                overflow: hidden;
                margin-bottom: 16px;
                position: relative;
            }
            .camera-feed img { width: 100%; height: 200px; object-fit: cover; }
            .ar-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; }
            .ar-target {
                position: absolute;
                width: 28px; height: 28px;
                border: 3px solid oklch(0.52 0.04 160);
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
                background: oklch(0 0 0 / 0.85);
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 10px;
                white-space: nowrap;
                color: oklch(0.18 0.008 110);
                border: 1px solid rgba(79,195,247,0.4);
            }
            .ar-iceberg {
                position: absolute;
                width: 40px; height: 40px;
                background: linear-gradient(180deg, rgba(135,206,250,0.8) 0%, rgba(135,206,250,0.3) 100%);
                border: 2px solid oklch(0.52 0.04 160);
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
                border-left: 3px dashed oklch(0.56 0.05 70);
                border-right: 3px dashed oklch(0.56 0.05 70);
            }
            .ar-canyon-warning {
                position: absolute;
                bottom: 80px; left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, rgba(245,101,101,0.95) 0%, rgba(245,101,101,0.8) 100%);
                padding: 10px 20px;
                border-radius:0;
                font-size: 13px;
                font-weight: 700;
                color: oklch(0.18 0.008 110);
                white-space: nowrap;
                box-shadow: 0 4px 20px rgba(245,101,101,0.5);
            }
            .ar-iceberg-warning {
                position: absolute;
                top: 80px; left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, rgba(135,206,250,0.95) 0%, rgba(135,206,250,0.8) 100%);
                padding: 10px 20px;
                border-radius:0;
                font-size: 13px;
                font-weight: 700;
                color: oklch(0.18 0.008 110);
                white-space: nowrap;
                box-shadow: 0 4px 20px rgba(135,206,250,0.5);
            }
            .camera-info { padding: 14px; }
            .camera-name { font-weight: 700; color: oklch(0.18 0.008 110); margin-bottom: 6px; font-size: 13px; }
            .camera-status { font-size: 11px; color: oklch(0.52 0.04 160); }
            .alarm-feed {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .alarm-card {
                background: oklch(0 0 0 / 0.35);
                border-radius:0;
                padding: 12px;
                border-left: 4px solid oklch(0.52 0.04 160);
            }
            .alarm-card.level-WARNING {
                border-left-color: oklch(0.56 0.05 70);
            }
            .alarm-card.level-CRITICAL,
            .alarm-card.level-EMERGENCY {
                border-left-color: oklch(0.48 0.07 22);
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
                border-radius:0;
                font-size: 10px;
                font-weight: 700;
                background: rgba(72,187,120,0.2);
                color: oklch(0.52 0.04 160);
            }
            .alarm-card-level.WARNING {
                background: rgba(246,173,85,0.2);
                color: oklch(0.56 0.05 70);
            }
            .alarm-card-level.CRITICAL,
            .alarm-card-level.EMERGENCY {
                background: rgba(245,101,101,0.2);
                color: oklch(0.48 0.07 22);
            }
            .alarm-card-time {
                font-size: 11px;
                color: oklch(0.55 0.005 110);
            }
            .alarm-card-message {
                font-size: 12px;
                color: oklch(0.18 0.008 110);
                line-height: 1.5;
            }
            .alarm-card-source {
                margin-top: 8px;
                font-size: 10px;
                color: oklch(0.52 0.04 160);
                text-transform: uppercase;
                letter-spacing: 0.04em;
            }
            .route-info { background: oklch(0 0 0 / 0.35); border-radius:0; padding: 16px; }
            .route-point {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 10px 0;
                border-bottom: 1px solid rgba(79,195,247,0.2);
            }
            .route-point:last-child { border-bottom: none; }
            .route-dot { width: 14px; height: 14px; border-radius: 50%; background: oklch(0.52 0.04 160); }
            .route-dot.waypoint { background: oklch(0.56 0.05 70); }
            .route-label { font-size: 12px; color: oklch(0.55 0.005 110); }
            .colregs-alert {
                background: linear-gradient(135deg, rgba(245,101,101,0.15) 0%, oklch(0 0 0 / 0.3) 100%);
                border: 1px solid oklch(0.48 0.07 22);
                border-radius:0;
                padding: 14px;
                margin-bottom: 14px;
            }
            .colregs-alert-title {
                font-weight: 700;
                colo
    ```
    
    ### 文件: `src/frontend/worldmonitor-ar-cas-pro.v1.bak.html`
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
                background: oklch(0.96 0.003 110);
                color: oklch(0.18 0.008 110);
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
                background: linear-gradient(90deg, oklch(0.52 0.04 160) 0%, oklch(0.52 0.04 160) 100%);
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
            .status-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: oklch(0.55 0.005 110); }
            .status-dot {
                width: 8px; height: 8px; border-radius: 50%;
                background: oklch(0.52 0.04 160);
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
                border-radius:0;
                border: 1px solid rgba(79,195,247,0.28);
                background: rgba(79,195,247,0.12);
                color: oklch(0.25 0.006 110);
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
                color: oklch(0.18 0.008 110);
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
                border-radius:0;
                padding: 16px;
                margin-bottom: 16px;
            }
            .panel h3 {
                font-size: 14px;
                font-weight: 600;
                color: oklch(0.52 0.04 160);
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .ais-target {
                background: linear-gradient(135deg, oklch(0 0 0 / 0.4) 0%, oklch(0 0 0 / 0.2) 100%);
                border-radius:0;
                padding: 14px;
                margin-bottom: 10px;
                border-left: 4px solid oklch(0.52 0.04 160);
                cursor: pointer;
                transition: all 0.3s;
            }
            .ais-target:hover {
                background: rgba(79,195,247,0.15);
                transform: translateX(6px);
                box-shadow: 0 4px 12px rgba(79,195,247,0.2);
            }
            .ais-target.high-risk { border-left-color: oklch(0.48 0.07 22); background: linear-gradient(135deg, rgba(245,101,101,0.15) 0%, oklch(0 0 0 / 0.3) 100%); }
            .ais-target.medium-risk { border-left-color: oklch(0.56 0.05 70); }
            .ais-target-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .ais-target-type { font-weight: 700; color: oklch(0.52 0.04 160); font-size: 14px; }
            .ais-target-mmsi { color: oklch(0.55 0.005 110); font-size: 11px; }
            .ais-target-info {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                font-size: 11px;
                color: oklch(0.55 0.005 110);
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
            .risk-badge.low { background: rgba(72,187,120,0.25); color: oklch(0.52 0.04 160); }
            .risk-badge.medium { background: rgba(246,173,85,0.25); color: oklch(0.56 0.05 70); }
            .risk-badge.high { background: rgba(245,101,101,0.25); color: oklch(0.48 0.07 22); }
            .colregs-badge { background: rgba(139,92,246,0.25); color: oklch(0.55 0.005 110); }
            .weather-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
            .weather-item {
                background: oklch(0 0 0 / 0.35);
                padding: 14px;
                border-radius:0;
                text-align: center;
            }
            .weather-label { font-size: 11px; color: oklch(0.55 0.005 110); margin-bottom: 6px; }
            .weather-value { font-size: 18px; font-weight: 700; color: oklch(0.52 0.04 160); }
            .port-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px;
                background: oklch(0 0 0 / 0.3);
                border-radius:0;
                margin-bottom: 8px;
            }
            .port-name { font-weight: 600; color: oklch(0.56 0.05 70); }
            .port-distance { font-size: 11px; color: oklch(0.55 0.005 110); }
            .right-panel {
                width: 360px;
                background: rgba(10,14,26,0.95);
                border-left: 1px solid rgba(79,195,247,0.2);
                overflow-y: auto;
                padding: 16px;
            }
            .camera-feed {
                background: oklch(0 0 0 / 0.6);
                border-radius:0;
                overflow: hidden;
                margin-bottom: 16px;
                position: relative;
            }
            .camera-feed img { width: 100%; height: 200px; object-fit: cover; }
            .ar-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; }
            .ar-target {
                position: absolute;
                width: 28px; height: 28px;
                border: 3px solid oklch(0.52 0.04 160);
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
                background: oklch(0 0 0 / 0.85);
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 10px;
                white-space: nowrap;
                color: oklch(0.18 0.008 110);
                border: 1px solid rgba(79,195,247,0.4);
            }
            .ar-iceberg {
                position: absolute;
                width: 40px; height: 40px;
                background: linear-gradient(180deg, rgba(135,206,250,0.8) 0%, rgba(135,206,250,0.3) 100%);
                border: 2px solid oklch(0.52 0.04 160);
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
                border-left: 3px dashed oklch(0.56 0.05 70);
                border-right: 3px dashed oklch(0.56 0.05 70);
            }
            .ar-canyon-warning {
                position: absolute;
                bottom: 80px; left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, rgba(245,101,101,0.95) 0%, rgba(245,101,101,0.8) 100%);
                padding: 10px 20px;
                border-radius:0;
                font-size: 13px;
                font-weight: 700;
                color: oklch(0.18 0.008 110);
                white-space: nowrap;
                box-shadow: 0 4px 20px rgba(245,101,101,0.5);
            }
            .ar-iceberg-warning {
                position: absolute;
                top: 80px; left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, rgba(135,206,250,0.95) 0%, rgba(135,206,250,0.8) 100%);
                padding: 10px 20px;
                border-radius:0;
                font-size: 13px;
                font-weight: 700;
                color: oklch(0.18 0.008 110);
                white-space: nowrap;
                box-shadow: 0 4px 20px rgba(135,206,250,0.5);
            }
            .camera-info { padding: 14px; }
            .camera-name { font-weight: 700; color: oklch(0.18 0.008 110); margin-bottom: 6px; font-size: 13px; }
            .camera-status { font-size: 11px; color: oklch(0.52 0.04 160); }
            .alarm-feed {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .alarm-card {
                background: oklch(0 0 0 / 0.35);
                border-radius:0;
                padding: 12px;
                border-left: 4px solid oklch(
  ### 步骤 02: research.md
  
  # 研究分析 — researcher
  
  任务: 给build团队的PM一个任务将http://localhost:5173/worldmonitor-ar-cas-pro.html的菜单AR-CAS-PRO的功能全部平移到数字孪生页面的AR-CAS...
  步骤: research
  Agent: build_researcher
  
  ---
  
  📋 任务: 6a2426e3-538
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
    给build团队的PM一个任务将http://localhost:5173/worldmonitor-ar-cas-pro.html的菜单AR-CAS-PRO的功能全部平移到数字孪生页面的AR-CAS...
    给build团队的PM一个任务将http://localhost:5173/worldmonitor-ar-cas-pro.html的菜单AR-CAS-PRO的功能全部平移到数字孪生页面的AR-CAS-PRO菜单中来，根据当前的数字孪生页面赋予现实增强的能力，就是当前的页面是他来做AR的基础
    
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
    ... (共 830 个 src/ 文件)
    
    ```
    
    ### 文件: `src/frontend/datacenter-digital-twin.html`
    ```html
    <!DOCTYPE html>
    <html lang="zh-CN" data-obc-theme="dusk">
    <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Digital Twin · 物理↔数字一一映射 · xFirst Principle</title>
    <link rel="stylesheet" href="/css/openbridge-theme.css">
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300;400;500;700&family=Noto+Serif:wght@200;300;400;600;900&family=Noto+Serif+SC:wght@200;300;400;600;900&family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap');
      :root {
        /* ── 侘寂橡胶 · Wabi-Sabi Rubber ── */
        --bg-0:oklch(0.96 0.003 110); --bg-1:oklch(0.91 0.004 110); --bg-2:oklch(0.85 0.005 110);
        --grid:oklch(0 0 0 / 0.03); --line:oklch(0.82 0.004 110);
        --accent:oklch(0.18 0.008 110); --accent-2:oklch(0.52 0.04 160); --accent-3:oklch(0.55 0.005 110);
        --warn:oklch(0.56 0.05 70); --danger:oklch(0.48 0.07 22);
        --text:oklch(0.18 0.008 110); --muted:oklch(0.55 0.005 110);
        --rack:oklch(0.18 0.008 110); --pdu:oklch(0.56 0.05 70); --ats:oklch(0.48 0.07 22); --busway:oklch(0.55 0.005 110);
        --cold:oklch(0.52 0.04 160); --hot:oklch(0.48 0.07 22); --pipe:oklch(0.52 0.04 160); --floor:oklch(0.72 0.006 110);
        /* rubber button system */
        --rubber:oklch(0.72 0.006 110); --rubber-hover:oklch(0.68 0.007 110); --rubber-press:oklch(0.64 0.007 110);
        --sumi:oklch(0.18 0.008 110); --koke:oklch(0.52 0.04 160); --shu:oklch(0.48 0.07 22);
        --kitsune:oklch(0.56 0.05 70); --shironeri:oklch(0.96 0.003 110);
        --groove:oklch(0.82 0.004 110); --ridge:oklch(1.00 0 0 / 0.6);
      }
      *{box-sizing:border-box;margin:0;padding:0}
      html,body{margin:0;padding:0;height:100%;font-family:'Noto Sans SC','JetBrains Mono',sans-serif;color:var(--text);-webkit-font-smoothing:antialiased}
      body{
        background:var(--bg-0);
        overflow-x:hidden;
      }
      /* 和紙质感 — 微粒紋理 */
      body::before{
        content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
        background-image:
          radial-gradient(oklch(0 0 0 / 0.012) 1px, transparent 1px),
          radial-gradient(oklch(0 0 0 / 0.008) 1px, transparent 1px);
        background-size:5px 5px, 7px 7px;
        background-position:0 0, 3px 3px;
      }
      .container{position:relative;z-index:1;max-width:100%;margin:0 auto;padding:18px 24px}
    
      .hud{display:flex;align-items:center;justify-content:space-between;
        padding:14px 0;border-bottom:1px solid var(--groove)}
      .hud .brand{display:flex;align-items:center;gap:14px}
      .hud .logo{width:34px;height:34px;
        background:var(--sumi);
        display:flex;align-items:center;justify-content:center;
        font-family:'Noto Serif SC',serif;font-size:18px;font-weight:900;color:var(--shironeri)}
      .hud h1{margin:0;font-family:'Noto Serif SC',serif;font-size:13px;letter-spacing:3px;font-weight:300;color:var(--muted)}
      .hud h1 strong{color:var(--text);font-weight:600}
      .hud .sub{font-size:10px;color:var(--muted);letter-spacing:2px;font-family:'JetBrains Mono',monospace}
      .hud .pills{display:flex;gap:6px;align-items:center;flex-wrap:wrap;justify-content:flex-end}
      /* 橡胶按钮 pill */
      .pill{padding:5px 14px;font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:1.5px;
        border:none;cursor:pointer;user-select:none;text-decoration:none;text-transform:uppercase;
        background:var(--rubber);color:var(--sumi);
        box-shadow:0 2px 5px oklch(0 0 0/0.12),0 1px 2px oklch(0 0 0/0.08),inset 0 1px 0 oklch(1 0 0/0.35),inset 0 -1px 0 oklch(0 0 0/0.08);
        background-image:radial-gradient(oklch(0 0 0/0.02) 1px,transparent 1px);background-size:3px 3px;
        transition:all 0.08s ease-out}
      .pill:hover{background-color:var(--rubber-hover)}
      .pill:active{box-shadow:inset 0 2px 5px oklch(0 0 0/0.15),inset 0 1px 2px oklch(0 0 0/0.10);transform:translateY(1px);background-color:var(--rubber-press)}
      .pill.live{background:var(--sumi);color:var(--shironeri);box-shadow:0 2px 5px oklch(0 0 0/0.15),inset 0 1px 0 oklch(1 0 0/0.08),inset 0 -1px 0 oklch(0 0 0/0.3)}
      .pill.live::before{content:'';display:inline-block;width:5px;height:5px;
        background:var(--koke);margin-right:6px;animation:blink 2.5s infinite}
      .pill.ws{background:var(--sumi);color:var(--shironeri)}
      .pill.ws.off{background:oklch(0.85 0.005 110);color:var(--shu)}
      @keyframes blink{50%{opacity:0.3}}
    
      .fp-banner{margin-top:14px;padding:12px 18px;
        background:oklch(0.93 0.003 110);
        box-shadow:inset 0 1px 4px oklch(0 0 0/0.05),0 1px 0 var(--ridge);
        font-size:12px;color:var(--text);
        display:flex;gap:18px;align-items:center;flex-wrap:wrap}
      .fp-banner .formula{font-family:'JetBrains Mono',monospace;color:var(--sumi);font-weight:700}
    
      .panel{padding:14px 16px;
        background:oklch(0.93 0.003 110);
        box-shadow:inset 0 1px 5px oklch(0 0 0/0.05),0 1px 0 oklch(1 0 0/0.5)}
      .panel h2{margin:0 0 10px;font-family:'Noto Serif SC',serif;font-size:12px;letter-spacing:3px;color:var(--sumi);
        text-transform:uppercase;display:flex;justify-content:space-between;align-items:center}
      .badge{font-family:'JetBrains Mono',monospace;font-size:8px;color:var(--muted);padding:2px 8px;border:1px solid var(--groove);letter-spacing:1.5px}
      .section-title{font-family:'Noto Serif SC',serif;font-size:11px;color:var(--muted);letter-spacing:3px;margin:14px 0 6px;text-transform:uppercase}
    
      .grid-21{display:grid;grid-template-columns:2fr 1fr;gap:14px}
      .grid-12{display:grid;grid-template-columns:1fr 2fr;gap:14px}
    
      /* 3D twin viewport — 石壁观察窗 */
      .twin-viewport{position:relative;width:100%;height:680px;
        overflow:hidden;
        padding:8px;background:oklch(0.85 0.005 110);
        box-shadow:inset 0 1px 0 oklch(1 0 0/0.3),0 1px 0 oklch(0 0 0/0.04)}
      .twin-viewport canvas{display:block}
      .twin-overlay{position:absolute;top:8px;left:8px;right:8px;padding:10px 14px;
        display:flex;justify-content:space-between;pointer-events:none;font-size:11px}
      .twin-overlay .tag{background:oklch(0.93 0.003 110 / 0.85);
        padding:4px 10px;color:var(--sumi);letter-spacing:1.5px;pointer-events:auto;
        font-family:'JetBrains Mono',monospace;font-size:9px}
      .twin-overlay .tag.live{color:var(--koke)}
      .twin-controls{position:absolute;left:16px;top:52px;
        display:flex;flex-direction:column;gap:4px;font-size:10px;
        max-height:calc(100% - 64px);overflow-y:auto;padding-bottom:10px}
      /* 橡胶图层按钮 */
      .twin-controls .layer-btn{
        padding:4px 10px;background:oklch(0.88 0.004 110);
        border:none;color:var(--sumi);cursor:pointer;letter-spacing:1.5px;text-align:left;min-width:160px;
        display:flex;justify-content:space-between;align-items:center;gap:8px;
        font-family:'JetBrains Mono',monospace;font-size:9px;
        box-shadow:0 1px 3px oklch(0 0 0/0.08),inset 0 1px 0 oklch(1 0 0/0.4),inset 0 -1px 0 oklch(0 0 0/0.05);
        background-image:radial-gradient(oklch(0 0 0/0.02) 1px,transparent 1px);background-size:3px 3px;
        transition:all 0.08s ease-out;
      }
      .twin-controls .layer-btn:active{box-shadow:inset 0 2px 4px oklch(0 0 0/0.12);transform:translateY(1px);background-color:oklch(0.82 0.004 110)}
      .twin-controls .layer-btn .swatch{width:8px;height:8px;display:inline-block}
      .twin-controls .layer-btn.off{opacity:0.35;text-decoration:line-through}
      .twin-legend{position:absolute;right:16px;bottom:16px;
        background:oklch(0.93 0.003 110 / 0.9);
        padding:8px 12px;font-size:10px;line-height:1.7;color:var(--muted);font-family:'JetBrains Mono',monospace}
      .twin-legend b{color:var(--text)}
      .twin-readout{position:absolute;right:16px;top:68px;width:240px;
        background:oklch(0.93 0.003 110 / 0.95);
        box-shadow:inset 0 1px 4px oklch(0 0 0/0.06),0 2px 8px oklch(0 0 0/0.1);
        padding:10px 12px;font-size:11px;color:var(--text);display:none}
      .twin-readout.show{display:block}
      .twin-readout h4{margin:0 0 6px;color:var(--sumi);font-family:'Noto Serif SC',serif;font-size:12px;letter-spacing:2px}
      .twin-readout .row{display:flex;justify-content:space-between;padding:2px 0;border-bottom:1px solid oklch(0.90 0.003 110)}
      .twin-readout .row .v{color:var(--koke);font-weight:700;font-family:'JetBrains Mono',monospace}
    
      /* mapping list */
      .map-list{display:flex;flex-direction:column;gap:6px}
      .map-item{padding:8px 10px;
        background:oklch(0.93 0.003 110);box-shadow:inset 0 1px 3px oklch(0 0 0/0.04),0 1px 0 oklch(1 0 0/0.3);
        font-size:11px;cursor:pointer;
        display:grid;grid-template-columns:10px 1fr auto;gap:8px;align-items:center;transition:background 0.15s}
      .map-item:hover{background:oklch(0.90 0.003 110)}
      .map-item .dot{width:8px;height:8px}
      .map-item .name{color:var(--text);font-weight:500;letter-spacing:0.5px;font-size:10px}
      .map-item .phys{font-size:9px;color:var(--muted);margin-top:1px}
      .map-item .v{font-size:12px;color:var(--sumi);font-weight:600;font-family:'JetBrains Mono',monospace;font-feature-settings:'tnum'}
    
      /* KPI strip — 石硯嵌入卡 */
      .kpi-strip{display:grid;grid-template-columns:repeat(7,1fr);gap:10px;margin:14px 0}
      .kpi{padding:12px 14px;
        background:oklch(0.93 0.003 110);
        box-shadow:inset 0 1px 4px oklch(0 0 0/0.05),0 1px 0 oklch(1 0 0/0.4);
        position:relative;overflow:hidden}
      .kpi::after{content:'';position:absolute;bottom:0;left:0;height:1px;width:100%;
        background:var(--groove)}
      .kpi .label{font-size:8px;color:var(--muted);letter-spacing:2.5px;text-transform:uppercase;font-family:'JetBrains Mono',monospace}
      .kpi .value{font-size:22px;font-weight:600;color:var(--sumi);margin:4px 0 2px;font-family:'JetBrains Mono',monospace;font-feature-settings:'tnum'}
      .kpi .unit{font-size:10px;color:var(--muted);margin-left:2px}
      .kpi .delta{font-size:10px;color:var(--koke)}
    
      /* device cards — 石硯卡片 */
      .dev-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:6px;
        max-height:260px;overflow-y:auto;padding-right:4px}
      .dev-card{padding:8px 10px;
        background:oklch(0.93 0.003 110);box-shadow:inset 0 1px 3px oklch(0 0 0/0.04),0 1px 0 oklch(1 0 0/0.3);
        font-size:10px;cursor:pointer;transition:all .12s}
      .dev-card:hover{background:oklch(0.90 0.003 110)}
      .dev-card.hot{border-left:2px solid var(--kitsune)}
      .dev-card.crit{border-left:2px solid var(--shu)}
      .dev-card .id{color:var(--sumi);font-weight:600;font-size:10px;letter-spacing:0.5px;display:flex;justify-content:space-between;font-family:'JetBrains Mono',monospace}
      .dev-card .id .typ{color:var(--muted);font-size:8px;letter-spacing:1px}
      .dev-card .pw{font-size:16px;color:var(--sumi);font-weight:600;font-family:'JetBrains Mono',monospace;font-feature-settings:'tnum';margin:2px 0}
      .dev-card .ln{font-size:9px;color:var(--muted)}
    
      /* energy flow svg */
      svg.flow{width:100%;height:300px}
      .flow .node{fill:oklch(0.93 0.003 110);stroke:var(--sumi);stroke-width:1}
      .flow .label{fill:var(--text);font-size:11px;font-family:'JetBrains Mono',monospace}
      .flow .sublabel{fill:var(--muted);font-size:9px;font-family:'JetBrains Mono',monospace}
    
      /* ratchet steps */
      .ratchet-loop{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:6px}
      .step{padding:10px 12px;
        background:oklch(0.93 0.003 110);box-shadow:inset 0 1px 3px oklch(0 0 0/0.04),0 1px 0 oklch(1 0 0/0.3);
        font-size:11px;position:relative;transition:all 0.2s}
      .step.active{background:oklch(0.90 0.004 110);box-shadow:inset 0 1px 3px oklch(0 0 0/0.06),0 0 0 1px var(--sumi)}
      .step .step-n{position:absolute;top:-10px;left:10px;background:var(--bg-0);
        color:var(--muted);padding:1px 8px;font-size:9px;letter-spacing:1.5px;font-family:'JetBrains Mono',monospace}
      .step.active .step-n{color:var(--sumi)}
      .step h4{margin:0 0 4px;color:var(--sumi);letter-spacing:1.5px;font-size:11px;font-family:'Noto Serif SC',serif}
      .step.active h4{color:var(--sumi);font-weight:700}
    
      /* 橡胶通用按钮 */
      button{padding:5px 12px;font:inherit;font-size:10px;
        background:var(--rubber);color:var(--sumi);
        border:none;cursor:pointer;letter-spacing:1px;
        font-family:'JetBrains Mono',monospace;
        box-shadow:0 2px 5px oklch(0 0 0/0.10),0 1px 2px oklch(0 0 0/0.06),inset 0 1px 0 oklch(1 0 0/0.35),inset 0 -1px 0 oklch(0 0 0/0.06);
        background-image:radial-gradient(oklch(0 0 0/0.02) 1px,transparent 1px);background-size:3px 3px;
        transition:all 0.08s ease-out}
      button:hover{background-color:var(--rubber-hover)}
      button:active{box-shadow:inset 0 2px 5px oklch(0 0 0/0.12),inset 0 1px 2px oklch(0 0 0/0.08);transform:translateY(1px);background-color:var(--rubber-press)}
      button.primary{background:var(--sumi);color:var(--shironeri);box-shadow:0 2px 5px oklch(0 0 0/0.15),inset 0 1px 0 oklch(1 0 0/0.08),inset 0 -1px 0 oklch(0 0 0/0.3)}
    
      ::-webkit-scrollbar{width:4px;height:4px}
      ::-webkit-scrollbar-thumb{background:oklch(0.75 0.005 110);border-radius:0}
      ::-webkit-scrollbar-track{background:oklch(0.93 0.003 110)}
    
      .footer{text-align:center;color:var(--muted);padding:14px 0 6px;font-size:9px;letter-spacing:2px;font-family:'JetBrains Mono',monospace}
    
      /* sensory mesh popup */
      .mesh-popup{display:none;position:absolute;bottom:16px;left:16px;z-index:50;width:280px;padding:14px;
        background:oklch(0.93 0.003 110 / 0.97);box-shadow:inset 0 1px 4px oklch(0 0 0/0.06),0 4px 16px oklch(0 0 0/0.12);
        color:var(--text);font-size:11px}
      .mesh-popup h4{color:var(--sumi);font-family:'Noto Serif SC',serif;font-size:12px;margin:0 0 8px;letter-spacing:2px}
      .mesh-popup .mp-layer{display:inline-block;padding:2px 8px;font-size:9px;font-weight:600;margin-bottom:8px;background:var(--rubber);font-family:'JetBrains Mono',monospace}
      .mesh-popup .mp-analysis{color:var(--text);line-height:1.6}
      .mesh-popup-close{position:absolute;top:6px;right:10px;cursor:pointer;color:var(--muted);font-size:16px}
      /* layer detail HUD */
      .layer-hud{display:none;position:absolute;top:16px;right:16px;z-index:50;width:260px;padding:14px;
        background:oklch(0.93 0.003 110 / 0.97);box-shadow:inset 0 1px 4px oklch(0 0 0/0.06),0 4px 16px oklch(0 0 0/0.12);
        color:var(--text);font-size:11px}
      .layer-hud h4{font-family:'Noto Serif SC',serif;font-size:13px;margin:0 0 6px;letter-spacing:2px}
      .layer-hud .lh-desc{color:var(--muted);margin-bottom:10px;line-height:1.5}
      .layer-hud .lh-tiers{display:flex;flex-direction:column;gap:6px}
      .layer-hud-close{position:absolute;top:6px;right:10px;cursor:pointer;color:var(--muted);font-size:16px}
    
      /* ════ BUILD TEAM CHAT ════ */
      .chat-fab{position:fixed;bottom:24px;right:24px;z-index:2000;width:48px;height:48px;
        border:none;cursor:pointer;
        background:var(--sumi);display:flex;align-items:center;justify-content:center;
        font-size:20px;color:var(--shironeri);
        box-shadow:0 2px 8px oklch(0 0 0/0.15);transition:all 0.15s}
      .chat-fab:hover{background:oklch(0.25 0.008 110)}
      .chat-fab.has-badge::after{content:'';position:absolute;top:2px;right:2px;width:8px;height:8px;
        background:var(--shu)}
      .chat-panel{position:fixed;bottom:80px;right:24px;z-index:2001;width:400px;height:500px;
        display:none;flex-direction:column;
        background:oklch(0.95 0.003 110);
        box-shadow:0 4px 2
    ```
    
    ### 文件: `src/frontend/worldmonitor-ar-cas-pro.html`
    ```html
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WorldMonitor AR-CAS Pro - 船舶避免碰撞增强现实系统（专业版）</title>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300;400;500;700&family=Noto+Serif:wght@200;300;400;600;900&family=Noto+Serif+SC:wght@200;300;400;600;900&family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap" rel="stylesheet">
        <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>
        <link href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css" rel="stylesheet" />
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
                background: oklch(0.96 0.003 110);
                color: oklch(0.18 0.008 110);
                overflow: hidden;
                height: 100vh;
                position: relative;
            }
            /* Wabi-Sabi Rubber tokens */
            :root{--shironeri:oklch(0.96 0.003 110);--ishi:oklch(0.91 0.004 110);--kabe:oklch(0.85 0.005 110);--sumi:oklch(0.18 0.008 110);--sumi-3:oklch(0.55 0.005 110);--koke:oklch(0.52 0.04 160);--shu:oklch(0.48 0.07 22);--kitsune:oklch(0.56 0.05 70);--groove:oklch(0.82 0.004 110);--font-serif:'Noto Serif SC',serif;--font-sans:'Noto Sans SC',sans-serif;--font-mono:'JetBrains Mono',monospace}
            body::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;background-image:radial-gradient(oklch(0 0 0/.012) 1px,transparent 1px),radial-gradient(oklch(0 0 0/.008) 1px,transparent 1px);background-size:5px 5px,7px 7px;background-position:0 0,3px 3px}
            .seal{display:inline-block;font-size:10px;font-weight:900;color:var(--shironeri);background:var(--sumi);padding:1px 5px;line-height:1.3;font-family:var(--font-serif);vertical-align:middle;margin-right:4px}.seal-koke{background:var(--koke)}.seal-shu{background:var(--shu)}.seal-kitsune{background:var(--kitsune)}
            .header{background:var(--ishi) !important;border-bottom:1px solid var(--groove) !important}
            .header h1{background:none !important;-webkit-text-fill-color:var(--koke) !important;color:var(--koke) !important;font-family:var(--font-serif);font-size:16px !important}
            .sidebar{background:var(--ishi) !important;border-color:var(--groove) !important}
            .panel{background:var(--shironeri) !important;border-color:var(--groove) !important}
            .action-button,.action-link{background:oklch(0.52 0.04 160 / 0.06) !important;border-color:oklch(0.52 0.04 160 / 0.15) !important}
            .header {
                position: fixed;
                top: 0; left: 0; right: 0;
                height: 60px;
                background: oklch(0.91 0.004 110);
                border-bottom: 2px solid oklch(0.82 0.004 110);
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 24px;
                z-index: 1000;
            }
            .header h1 {
                font-size: 20px;
                font-weight: 700;
                background: linear-gradient(90deg, oklch(0.52 0.04 160) 0%, oklch(0.52 0.04 160) 100%);
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
            .status-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: oklch(0.55 0.005 110); }
            .status-dot {
                width: 8px; height: 8px; border-radius: 50%;
                background: oklch(0.52 0.04 160);
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
                border-radius:0;
                border: 1px solid rgba(79,195,247,0.28);
                background: rgba(79,195,247,0.12);
                color: oklch(0.25 0.006 110);
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
                color: oklch(0.18 0.008 110);
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
                border-radius:0;
                padding: 16px;
                margin-bottom: 16px;
            }
            .panel h3 {
                font-size: 14px;
                font-weight: 600;
                color: oklch(0.52 0.04 160);
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .ais-target {
                background: linear-gradient(135deg, oklch(0 0 0 / 0.4) 0%, oklch(0 0 0 / 0.2) 100%);
                border-radius:0;
                padding: 14px;
                margin-bottom: 10px;
                border-left: 4px solid oklch(0.52 0.04 160);
                cursor: pointer;
                transition: all 0.3s;
            }
            .ais-target:hover {
                background: rgba(79,195,247,0.15);
                transform: translateX(6px);
                box-shadow: 0 4px 12px rgba(79,195,247,0.2);
            }
            .ais-target.high-risk { border-left-color: oklch(0.48 0.07 22); background: linear-gradient(135deg, rgba(245,101,101,0.15) 0%, oklch(0 0 0 / 0.3) 100%); }
            .ais-target.medium-risk { border-left-color: oklch(0.56 0.05 70); }
            .ais-target-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .ais-target-type { font-weight: 700; color: oklch(0.52 0.04 160); font-size: 14px; }
            .ais-target-mmsi { color: oklch(0.55 0.005 110); font-size: 11px; }
            .ais-target-info {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                font-size: 11px;
                color: oklch(0.55 0.005 110);
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
            .risk-badge.low { background: rgba(72,187,120,0.25); color: oklch(0.52 0.04 160); }
            .risk-badge.medium { background: rgba(246,173,85,0.25); color: oklch(0.56 0.05 70); }
            .risk-badge.high { background: rgba(245,101,101,0.25); color: oklch(0.48 0.07 22); }
            .colregs-badge { background: rgba(139,92,246,0.25); color: oklch(0.55 0.005 110); }
            .weather-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
            .weather-item {
                background: oklch(0 0 0 / 0.35);
                padding: 14px;
                border-radius:0;
                text-align: center;
            }
            .weather-label { font-size: 11px; color: oklch(0.55 0.005 110); margin-bottom: 6px; }
            .weather-value { font-size: 18px; font-weight: 700; color: oklch(0.52 0.04 160); }
            .port-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px;
                background: oklch(0 0 0 / 0.3);
                border-radius:0;
                margin-bottom: 8px;
            }
            .port-name { font-weight: 600; color: oklch(0.56 0.05 70); }
            .port-distance { font-size: 11px; color: oklch(0.55 0.005 110); }
            .right-panel {
                width: 360px;
                background: rgba(10,14,26,0.95);
                border-left: 1px solid rgba(79,195,247,0.2);
                overflow-y: auto;
                padding: 16px;
            }
            .camera-feed {
                background: oklch(0 0 0 / 0.6);
                border-radius:0;
                overflow: hidden;
                margin-bottom: 16px;
                position: relative;
            }
            .camera-feed img { width: 100%; height: 200px; object-fit: cover; }
            .ar-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; }
            .ar-target {
                position: absolute;
                width: 28px; height: 28px;
                border: 3px solid oklch(0.52 0.04 160);
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
                background: oklch(0 0 0 / 0.85);
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 10px;
                white-space: nowrap;
                color: oklch(0.18 0.008 110);
                border: 1px solid rgba(79,195,247,0.4);
            }
            .ar-iceberg {
                position: absolute;
                width: 40px; height: 40px;
                background: linear-gradient(180deg, rgba(135,206,250,0.8) 0%, rgba(135,206,250,0.3) 100%);
                border: 2px solid oklch(0.52 0.04 160);
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
                border-left: 3px dashed oklch(0.56 0.05 70);
                border-right: 3px dashed oklch(0.56 0.05 70);
            }
            .ar-canyon-warning {
                position: absolute;
                bottom: 80px; left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, rgba(245,101,101,0.95) 0%, rgba(245,101,101,0.8) 100%);
                padding: 10px 20px;
                border-radius:0;
                font-size: 13px;
                font-weight: 700;
                color: oklch(0.18 0.008 110);
                white-space: nowrap;
                box-shadow: 0 4px 20px rgba(245,101,101,0.5);
            }
            .ar-iceberg-warning {
                position: absolute;
                top: 80px; left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, rgba(135,206,250,0.95) 0%, rgba(135,206,250,0.8) 100%);
                padding: 10px 20px;
                border-radius:0;
                font-size: 13px;
                font-weight: 700;
                color: oklch(0.18 0.008 110);
                white-space: nowrap;
                box-shadow: 0 4px 20px rgba(135,206,250,0.5);
            }
            .camera-info { padding: 14px; }
            .camera-name { font-weight: 700; color: oklch(0.18 0.008 110); margin-bottom: 6px; font-size: 13px; }
            .camera-status { font-size: 11px; color: oklch(0.52 0.04 160); }
            .alarm-feed {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .alarm-card {
                background: oklch(0 0 0 / 0.35);
                border-radius:0;
                padding: 12px;
                border-left: 4px solid oklch(0.52 0.04 160);
            }
            .alarm-card.level-WARNING {
                border-left-color: oklch(0.56 0.05 70);
            }
            .alarm-card.level-CRITICAL,
            .alarm-card.level-EMERGENCY {
                border-left-color: oklch(0.48 0.07 22);
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
                border-radius:0;
                font-size: 10px;
                font-weight: 700;
                background: rgba(72,187,120,0.2);
                color: oklch(0.52 0.04 160);
            }
            .alarm-card-level.WARNING {
                background: rgba(246,173,85,0.2);
                color: oklch(0.56 0.05 70);
            }
            .alarm-card-level.CRITICAL,
            .alarm-card-level.EMERGENCY {
                background: rgba(245,101,101,0.2);
                color: oklch(0.48 0.07 22);
            }
            .alarm-card-time {
                font-size: 11px;
                color: oklch(0.55 0.005 110);
            }
            .alarm-card-message {
                font-size: 12px;
                color: oklch(0.18 0.008 110);
                line-height: 1.5;
            }
            .alarm-card-source {
                margin-top: 8px;
                font-size: 10px;
                color: oklch(0.52 0.04 160);
                text-transform: uppercase;
                letter-spacing: 0.04em;
            }
            .route-info { background: oklch(0 0 0 / 0.35); border-radius:0; padding: 16px; }
            .route-point {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 10px 0;
                border-bottom: 1px solid rgba(79,195,247,0.2);
            }
            .route-point:last-child { border-bottom: none; }
            .route-dot { width: 14px; height: 14px; border-radius: 50%; background: oklch(0.52 0.04 160); }
            .route-dot.waypoint { background: oklch(0.56 0.05 70); }
            .route-label { font-size: 12px; color: oklch(0.55 0.005 110); }
            .colregs-alert {
                background: linear-gradient(135deg, rgba(245,101,101,0.15) 0%, oklch(0 0 0 / 0.3) 100%);
                border: 1px solid oklch(0.48 0.07 22);
                border-radius:0;
                padding: 14px;
                margin-bottom: 14px;
            }
            .colregs-alert-title {
                font-weight: 700;
                colo
    ```
    
    ### 文件: `src/frontend/worldmonitor-ar-cas-pro.v1.bak.html`
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
                background: oklch(0.96 0.003 110);
                color: oklch(0.18 0.008 110);
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
                background: linear-gradient(90deg, oklch(0.52 0.04 160) 0%, oklch(0.52 0.04 160) 100%);
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
            .status-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: oklch(0.55 0.005 110); }
            .status-dot {
                width: 8px; height: 8px; border-radius: 50%;
                background: oklch(0.52 0.04 160);
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
                border-radius:0;
                border: 1px solid rgba(79,195,247,0.28);
                background: rgba(79,195,247,0.12);
                color: oklch(0.25 0.006 110);
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
                color: oklch(0.18 0.008 110);
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
                border-radius:0;
                padding: 16px;
                margin-bottom: 16px;
            }
            .panel h3 {
                font-size: 14px;
                font-weight: 600;
                color: oklch(0.52 0.04 160);
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .ais-target {
                background: linear-gradient(135deg, oklch(0 0 0 / 0.4) 0%, oklch(0 0 0 / 0.2) 100%);
                border-radius:0;
                padding: 14px;
                margin-bottom: 10px;
                border-left: 4px solid oklch(0.52 0.04 160);
                cursor: pointer;
                transition: all 0.3s;
            }
            .ais-target:hover {
                background: rgba(79,195,247,0.15);
                transform: translateX(6px);
                box-shadow: 0 4px 12px rgba(79,195,247,0.2);
            }
            .ais-target.high-risk { border-left-color: oklch(0.48 0.07 22); background: linear-gradient(135deg, rgba(245,101,101,0.15) 0%, oklch(0 0 0 / 0.3) 100%); }
            .ais-target.medium-risk { border-left-color: oklch(0.56 0.05 70); }
            .ais-target-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .ais-target-type { font-weight: 700; color: oklch(0.52 0.04 160); font-size: 14px; }
            .ais-target-mmsi { color: oklch(0.55 0.005 110); font-size: 11px; }
            .ais-target-info {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                font-size: 11px;
                color: oklch(0.55 0.005 110);
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
            .risk-badge.low { background: rgba(72,187,120,0.25); color: oklch(0.52 0.04 160); }
            .risk-badge.medium { background: rgba(246,173,85,0.25); color: oklch(0.56 0.05 70); }
            .risk-badge.high { background: rgba(245,101,101,0.25); color: oklch(0.48 0.07 22); }
            .colregs-badge { background: rgba(139,92,246,0.25); color: oklch(0.55 0.005 110); }
            .weather-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
            .weather-item {
                background: oklch(0 0 0 / 0.35);
                padding: 14px;
                border-radius:0;
                text-align: center;
            }
            .weather-label { font-size: 11px; color: oklch(0.55 0.005 110); margin-bottom: 6px; }
            .weather-value { font-size: 18px; font-weight: 700; color: oklch(0.52 0.04 160); }
            .port-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px;
                background: oklch(0 0 0 / 0.3);
                border-radius:0;
                margin-bottom: 8px;
            }
            .port-name { font-weight: 600; color: oklch(0.56 0.05 70); }
            .port-distance { font-size: 11px; color: oklch(0.55 0.005 110); }
            .right-panel {
                width: 360px;
                background: rgba(10,14,26,0.95);
                border-left: 1px solid rgba(79,195,247,0.2);
                overflow-y: auto;
                padding: 16px;
            }
            .camera-feed {
                background: oklch(0 0 0 / 0.6);
                border-radius:0;
                overflow: hidden;
                margin-bottom: 16px;
                position: relative;
            }
            .camera-feed img { width: 100%; height: 200px; object-fit: cover; }
            .ar-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; }
            .ar-target {
                position: absolute;
                width: 28px; height: 28px;
                border: 3px solid oklch(0.52 0.04 160);
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
                background: oklch(0 0 0 / 0.85);
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 10px;
                white-space: nowrap;
                color: oklch(0.18 0.008 110);
                border: 1px solid rgba(79,195,247,0.4);
            }
            .ar-iceberg {
                position: absolute;
                width: 40px; height: 40px;
                background: linear-gradient(180deg, rgba(135,206,250,0.8) 0%, rgba(135,206,250,0.3) 100%);
                border: 2px solid oklch(0.52 0.04 160);
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
                border-left: 3px dashed oklch(0.56 0.05 70);
                border-right: 3px dashed oklch(0.56 0.05 70);
            }
            .ar-canyon-warning {
                position: absolute;
                bottom: 80px; left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, rgba(245,101,101,0.95) 0%, rgba(245,101,101,0.8) 100%);
                padding: 10px 20px;
                border-radius:0;
                font-size: 13px;
                font-weight: 700;
                color: oklch(0.18 0.008 110);
                white-space: nowrap;
                box-shadow: 0 4px 20px rgba(245,101,101,0.5);
            }
            .ar-iceberg-warning {
                position: absolute;
                top: 80px; left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, rgba(135,206,250,0.95) 0%, rgba(135,206,250,0.8) 100%);
                padding: 10px 20px;
                border-radius:0;
                font-size: 13px;
                font-weight: 700;
                color: oklch(0.18 0.008 110);
                white-space: nowrap;
                box-shadow: 0 4px 20px rgba(135,206,250,0.5);
            }
            .camera-info { padding: 14px; }
            .camera-name { font-weight: 700; color: oklch(0.18 0.008 110); margin-bottom: 6px; font-size: 13px; }
            .camera-status { font-size: 11px; color: oklch(0.52 0.04 160); }
            .alarm-feed {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .alarm-card {
                background: oklch(0 0 0 / 0.35);
                border-radius:0;
                padding: 12px;
                border-left: 4px solid oklch(
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

# 技术方案：AR-CAS Pro 功能平移到数字孪生页面

## 1. 概述

### 1.1 任务目标
将 `worldmonitor-ar-cas-pro.html` 中 AR-CAS-PRO 菜单的所有功能完整平移到数字孪生页面（`datacenter-digital-twin.html`），使数字孪生页面具备增强现实（AR）能力。

### 1.2 核心原则
- **功能完整迁移**：不丢失任何现有功能
- **风格统一**：适配数字孪生页面的 Wabi-Sabi Rubber 设计语言
- **架构整合**：利用现有的 PoseidonX 系统架构
- **AR 增强**：以数字孪生 3D 场景为 AR 基础

---

## 2. 源系统功能分析

### 2.1 worldmonitor-ar-cas-pro.html 功能清单

| 模块 | 功能 | 技术实现 |
|------|------|----------|
| **Header** | 系统标题、状态指示、操作按钮 | CSS + HTML |
| **Map (Maplibre)** | 海图显示、AIS 目标、航线、风险区域 | Maplibre GL JS |
| **Sidebar** | AIS 目标列表、天气信息、港口信息 | HTML + CSS |
| **Right Panel** | 摄像头 AR 叠加、告警列表、COLREGS 规则 | HTML + CSS + JS |
| **AR Overlay** | 目标标记、冰山警告、峡谷警告 | CSS 动画 + 定位 |
| **CPA/TCPA** | 最近会遇点计算 | JS 计算 |
| **Alarm Feed** | 告警卡片（WARNING/CRITICAL/EMERGENCY） | HTML + CSS |
| **Route Info** | 航线点列表 | HTML + CSS |
| **COLREGS Alert** | 碰撞规则警告 | HTML + CSS |

### 2.2 数字孪生页面现有能力

| 模块 | 功能 | 技术实现 |
|------|------|----------|
| **3D Viewport** | Three.js 3D 场景 | Canvas + Three.js |
| **Layer Controls** | 图层切换按钮 | CSS + JS |
| **KPI Strip** | 关键指标展示 | HTML + CSS |
| **Device Cards** | 设备状态卡片 | HTML + CSS |
| **Energy Flow** | 能量流 SVG | SVG |
| **Mapping List** | 物理↔数字映射 | HTML + CSS |
| **Chat System** | 团队聊天 | HTML + JS |

---

## 3. 技术方案设计

### 3.1 架构设计

```
┌───────────────────────────────────────��─────────────────────┐
│                   数字孪生页面 (datacenter-digital-twin.html) │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 3D Viewport  │  │ AR Overlay   │  │ Control Panel    │  │
│  │ (Three.js)   │  │ (CSS+Canvas) │  │ (Layer + KPI)    │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                    │            │
│  ┌──────┴─────────────────┴────────────────────┴─────────┐  │
│  │              PoseidonX Core (PoseidonX.js)            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │  │
│  │  │ Navigator │  │ Engineer │  │ Safety Agent     │    │  │
│  │  │ Agent     │  │ Agent    │  │ (COLREGS + AR)   │    │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 新增/修改文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/frontend/datacenter-digital-twin.html` | **修改** | 添加 AR-CAS-PRO 菜单和功能 |
| `src/frontend/digital-twin/ARCASProModule.js` | **新建** | AR-CAS Pro 核心模块 |
| `src/frontend/digital-twin/layer1-interface/AROverlay.js` | **新建** | AR 叠加层渲染 |
| `src/frontend/digital-twin/layer1-interface/AISTargetPanel.js` | **新建** | AIS 目标面板 |
| `src/frontend/digital-twin/layer1-interface/COLREGSPanel.js` | **新建** | COLREGS 规则面板 |
| `src/frontend/digital-twin/layer1-interface/AlarmFeedPanel.js` | **新建** | 告警面板 |
| `src/frontend/digital-twin/layer2-agents/SafetyAgent.js` | **修改** | 增强 COLREGS 和碰撞避免逻辑 |
| `src/frontend/digital-twin/PoseidonX.js` | **修改** | 注册 AR-CAS Pro 模块 |

---

## 4. 详细设计

### 4.1 ARCASProModule.js 核心模块

```javascript
// src/frontend/digital-twin/ARCASProModule.js

export class ARCASProModule {
  constructor(scene, camera, config = {}) {
    this.scene = scene;
    this.camera = camera;
    this.config = {
      enableAIS: true,
      enableAR: true,
      enableCOLREGS: true,
      enableAlarms: true,
      ...config
    };
    
    // 状态
    this.aisTargets = new Map();
    this.alarms = [];
    this.colregsAlerts = [];
    this.route = [];
    this.weather = null;
    this.ports = [];
    
    // 子模块
    this.arOverlay = null;
    this.aisPanel = null;
    this.colregsPanel = null;
    this.alarmPanel = null;
  }
  
  async initialize(container) {
    // 1. 初始化 AR 叠加层
    this.arOverlay = new AROverlay(this.scene, this.camera);
    await this.arOverlay.initialize();
    
    // 2. 初始化 AIS 目标面板
    this.aisPanel = new AISTargetPanel(container);
    await this.aisPanel.initialize();
    
    // 3. 初始化 COLREGS 面板
    this.colregsPanel = new COLREGSPanel(container);
    await this.colregsPanel.initialize();
    
    // 4. 初始化告警面板
    this.alarmPanel = new AlarmFeedPanel(container);
    await this.alarmPanel.initialize();
    
    // 5. 启动数据模拟
    this._startSimulation();
  }
  
  _startSimulation() {
    // 模拟 AIS 目标
    setInterval(() => this._updateAISTargets(), 5000);
    // 模拟告警
    setInterval(() => this._generateAlarm(), 15000);
    // 模拟天气
    setInterval(() => this._updateWeather(), 30000);
  }
  
  _updateAISTargets() {
    // 生成模拟 AIS 目标
    const targets = this._generateMockAISTargets();
    this.aisTargets.clear();
    targets.forEach(t => this.aisTargets.set(t.mmsi, t));
    
    // 更新 AR 叠加层
    this.arOverlay.updateTargets(targets);
    
    // 更新面板
    this.aisPanel.update(targets);
    
    // 计算 CPA/TCPA
    this._calculateCPA(targets);
  }
  
  _calculateCPA(targets) {
    // 最近会遇点计算
    targets.forEach(target => {
      const cpa = this._computeCPA(
        { lat: 25.0, lon: 121.5, speed: 12, heading: 45 },
        { lat: target.lat, lon: target.lon, speed: target.speed, heading: target.heading }
      );
      target.cpa = cpa.cpa;
      target.tcpa = cpa.tcpa;
      target.risk = this._assessRisk(cpa);
    });
  }
  
  _computeCPA(ownShip, target) {
    // CPA 计算算法
    const R = 6371000; // 地球半径
    const dLat = (target.lat - ownShip.lat) * Math.PI / 180;
    const dLon = (target.lon - ownShip.lon) * Math.PI / 180;
    const lat1 = ownShip.lat * Math.PI / 180;
    const lat2 = target.lat * Math.PI / 180;
    
    const a = Math.sin(dLat/2)**2 + Math.cos(lat1)*Math.cos(lat2)*Math.sin(dLon/2)**2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const distance = R * c; // 米
    
    // 相对速度计算
    const vx = target.speed * Math.sin(target.heading * Math.PI / 180) - 
               ownShip.speed * Math.sin(ownShip.heading * Math.PI / 180);
    const vy = target.speed * Math.cos(target.heading * Math.PI / 180) - 
               ownShip.speed * Math.cos(ownShip.heading * Math.PI / 180);
    const relSpeed = Math.sqrt(vx**2 + vy**2);
    
    // CPA 距离
    const cpaDistance = distance * Math.sin(Math.atan2(relSpeed, 0));
    const tcpa = distance / (relSpeed || 1);
    
    return { cpa: cpaDistance, tcpa };
  }
  
  _assessRisk(cpa) {
    if (cpa.cpa < 500) return 'HIGH';
    if (cpa.cpa < 2000) return 'MEDIUM';
    return 'LOW';
  }
  
  _generateAlarm() {
    const alarmTypes = [
      { level: 'WARNING', message: 'CPA 小于 1 海里', source: 'AR-CAS' },
      { level: 'CRITICAL', message: '碰撞风险 - 目标 MMSI: 412345678', source: 'COLREGS' },
      { level: 'EMERGENCY', message: '立即避让 - 目标距离 0.5 海里', source: 'AR-CAS' }
    ];
    
    const alarm = alarmTypes[Math.floor(Math.random() * alarmTypes.length)];
    alarm.time = new Date().toISOString();
    this.alarms.unshift(alarm);
    
    // 限制告警数量
    if (this.alarms.length > 50) this.alarms.pop();
    
    this.alarmPanel.update(this.alarms);
  }
  
  _updateWeather() {
    this.weather = {
      windSpeed: 15 + Math.random() * 20,
      windDirection: Math.floor(Math.random() * 360),
      waveHeight: 1.5 + Math.random() * 3,
      visibility: 5 + Math.random() * 10,
      current: 1 + Math.random() * 2
    };
  }
  
  _generateMockAISTargets() {
    return [
      {
        mmsi: '412345678',
        type: 'Cargo',
        lat: 25.1 + Math.random() * 0.1,
        lon: 121.6 + Math.random() * 0.1,
        speed: 10 + Math.random() * 5,
        heading: Math.floor(Math.random() * 360),
        course: Math.floor(Math.random() * 360),
        destination: 'Shanghai',
        eta: '2024-01-15 08:00',
        risk: 'HIGH'
      },
      {
        mmsi: '412345679',
        type: 'Tanker',
        lat: 24.9 + Math.random() * 0.1,
        lon: 121.4 + Math.random() * 0.1,
        speed: 8 + Math.random() * 3,
        heading: Math.floor(Math.random() * 360),
        course: Math.floor(Math.random() * 360),
        destination: 'Kaohsiung',
        eta: '2024-01-16 14:00',
        risk: 'MEDIUM'
      },
      {
        mmsi: '412345680',
        type: 'Fishing',
        lat: 25.05 + Math.random() * 0.05,
        lon: 121.55 + Math.random() * 0.05,
        speed: 3 + Math.random() * 2,
        heading: Math.floor(Math.random() * 360),
        course: Math.floor(Math.random() * 360),
        destination: 'Keelung',
        eta: '2024-01-15 18:00',
        risk: 'LOW'
      }
    ];
  }
}
```

### 4.2 AROverlay.js - AR 叠加层

```javascript
// src/frontend/digital-twin/layer1-interface/AROverlay.js

export class AROverlay {
  constructor(scene, camera) {
    this.scene = scene;
    this.camera = camera;
    this.targets = [];
    this.icebergs = [];
    this.canyons = [];
    this.arElements = [];
  }
  
  async initialize() {
    // 创建 AR 标记材质
    this._createARMaterials();
    
    // 启动渲染循环
    this._startRenderLoop();
  }
  
  _createARMaterials() {
    // 目标标记材质
    this.targetMaterial = new THREE.MeshBasicMaterial({
      color: 0x4fc3f7,
      transparent: true,
      opacity: 0.8,
      side: THREE.DoubleSide
    });
    
    // 危险标记材质
    this.dangerMaterial = new THREE.MeshBasicMaterial({
      color: 0xf56565,
      transparent: true,
      opacity: 0.9,
      side: THREE.DoubleSide
    });
    
    // 警告标记材质
    this.warningMaterial = new THREE.MeshBasicMaterial({
      color: 0xf6ad55,
      transparent: true,
      opacity: 0.8,
      side: THREE.DoubleSide
    });
  }
  
  updateTargets(targets) {
    // 清除旧标记
    this._clearARElements();
    
    // 创建新标记
    targets.forEach(target => {
      const position = this._latLonToWorld(target.lat, target.lon);
      const marker = this._createTargetMarker(target, position);
      this.arElements.push(marker);
      this.scene.add(marker);
      
      // 添加标签
      const label = this._createLabel(target, position);
      this.arElements.push(label);
      this.scene.add(label);
    });
  }
  
  _latLonToWorld(lat, lon) {
    // 经纬度转世界坐标
    const R = 100; // 场景半径
    const phi = (90 - lat) * Math.PI / 180;
    const theta = lon * Math.PI / 180;
    
    return new THREE.Vector3(
      R * Math.sin(phi) * Math.cos(theta),
      R * Math.cos(phi),
      R * Math.sin(phi) * Math.sin(theta)
    );
  }
  
  _createTargetMarker(target, position) {
    const geometry = new THREE.RingGeometry(0.5, 1, 32);
    const material = target.risk === 'HIGH' ? this.dangerMaterial :
                     target.risk === 'MEDIUM' ? this.warningMaterial :
                     this.targetMaterial;
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(position);
    mesh.lookAt(0, 0, 0); // 面向场景中心
    
    return mesh;
  }
  
  _createLabel(target, position) {
    // 使用 Sprite 创建文本标签
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 64;
    const ctx = canvas.getContext('2d');
    
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(0, 0, 256, 64);
    ctx.strokeStyle = '#4fc3f7';
    ctx.lineWidth = 2;
    ctx.strokeRect(0, 0, 256, 64);
    
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 16px JetBrains Mono';
    ctx.fillText(`${target.type} | ${target.speed}kn`, 10, 25);
    ctx.fillStyle = '#4fc3f7';
    ctx.font = '12px JetBrains Mono';
    ctx.fillText(`CPA: ${target.cpa?.toFixed(1)}nm`, 10, 50);
    
    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(material);
    sprite.position.copy(position);
    sprite.position.y += 2;
    sprite.scale.set(4, 1, 1);
    
    return sprite;
  }
  
  _clearARElements() {
    this.arElements.forEach(element => {
      this.scene.remove(element);
      if (element.geometry) element.geometry.dispose();
      if (element.material) element.material.dispose();
    });
    this.arElements = [];
  }
  
  _startRenderLoop() {
    // 动画循环 - 标记脉冲效果
    setInterval(() => {
      this.arElements.forEach(element => {
        if (element.isMesh && element.material.opacity) {
          element.material.opacity = 0.5 + Math.sin(Date.now() / 500) * 0.3;
        }
      });
    }, 50);
  }
}
```

### 4.3 AISTargetPanel.js - AIS 目标面板

```javascript
// src/frontend/digital-twin/layer1-interface/AISTargetPanel.js

export class AISTargetPanel {
  constructor(container) {
    this.container = container;
    this.targets = [];
    this.selectedTarget = null;
  }
  
  async initialize() {
    this._createPanel();
  }
  
  _createPanel() {
    this.panel = document.createElement('div');
    this.panel.className = 'panel';
    this.panel.innerHTML = `
      <h2>
        AIS 目标
        <span class="badge">AR-CAS</span>
      </h2>
      <div class="ais-target-list" id="ais-target-list"></div>
      <div class="cpa-tcpa" id="cpa-tcpa">
        <div class="cpa-item">
          <div class="cpa-label">CPA</div>
          <div class="cpa-value safe" id="cpa-value">--</div>
        </div>
        <div class="cpa-item">
          <div class="cpa-label">TCPA</div>
          <div class="cpa-value safe" id="tcpa-value">--</div>
        </div>
        <div class="cpa-item">
          <div class="cpa-label">风险</div>
          <div class="cpa-value safe" id="risk-value">--</div>
        </div>
      </div>
    `;
    
    this.container.appendChild(this.panel);
  }
  
  update(targets) {
    this.targets = targets;
    const list = document.getElementById('ais-target-list');
    list.innerHTML = '';
    
    targets.forEach(target => {
      const item = document.createElement('div');
      item.className = `ais-target ${target.risk === 'HIGH' ? 'high-risk' : target.risk === 'MEDIUM' ? 'medium-risk' : ''}`;
      item.innerHTML = `
        <div class="ais-target-header">
          <span class="ais-target-type">${target.type}</span>
          <span class="ais-target-mmsi">MMSI: ${target.mmsi}</span>
        </div>
        <div class="ais-target-info">
          <span>航速: ${target.speed.toFixed(1)} kn</span>
          <span>航向: ${target.heading}°</span>
          <span>CPA: ${target.cpa?.toFixed(2) || '--'} nm</span>
          <span>TCPA: ${target.tcpa?.toFixed(1) || '--'} min</span>
        </div>
        <span class="risk-badge ${target.risk?.toLowerCase()}">${target.risk || 'UNKNOWN'}</span>
      `;
      
      item.addEventListener('click', () => this._selectTarget(target));
      list.appendChild(item);
    });
    
    // 更新 CPA/TCPA 显示
    this._updateCPAInfo(targets);
  }
  
  _selectTarget(target) {
    this.selectedTarget = target;
    this.emit('target:selected', target);
  }
  
  _updateCPAInfo(targets) {
    const cpaValue = document.getElementById('cpa-value');
    const tcpaValue = document.getElementById('tcpa-value');
    const riskValue = document.getElementById('risk-value');
    
    if (targets.length > 0) {
      const minCPA = Math.min(...targets.map(t => t.cpa || Infinity));
      const minTCPA = Math.min(...targets.map(t => t.tcpa || Infinity));
      const maxRisk = Math.max(...targets.map(t => 
        t.risk === 'HIGH' ? 3 : t.risk === 'MEDIUM' ? 2 : 1
      ));
      
      cpaValue.textContent = minCPA.toFixed(2) + ' nm';
      cpaValue.className = `cpa-value ${minCPA < 0.5 ? 'danger' : minCPA < 2 ? 'warning' : 'safe'}`;
      
      tcpaValue.textContent = minTCPA.toFixed(1) + ' min';
      tcpaValue.className = `cpa-value ${minTCPA < 10 ? 'danger' : minTCPA < 30 ? 'warning' : 'safe'}`;
      
      const riskLabels = { 1: 'LOW', 2: 'MEDIUM', 3: 'HIGH' };
      riskValue.textContent = riskLabels[maxRisk];
      riskValue.className = `cpa-value ${maxRisk === 3 ? 'danger' : maxRisk === 2 ? 'warning' : 'safe'}`;
    }
  }
}
```

### 4.4 COLREGSPanel.js - COLREGS 规则面板

```javascript
// src/frontend/digital-twin/layer1-interface/COLREGSPanel.js

export class COLREGSPanel {
  constructor(container) {
    this.container = container;
    this.alerts = [];
  }
  
  async initialize() {
    this._createPanel();
  }
  
  _createPanel() {
    this.panel = document.createElement('div');
    this.panel.className = 'panel';
    this.panel.innerHTML = `
      <h2>
        COLREGS 规则
        <span class="badge">碰撞避免</span>
      </h2>
      <div id="colregs-alerts"></div>
      <div class="section-title">适用规则</div>
      <div class="route-info" id="colregs-rules">
        <div class="route-point">
          <div class="route-dot"></div>
          <span class="route-label">规则 13 - 追越</span>
        </div>
        <div class="route-point">
          <div class="route-dot"></div>
          <span class="route-label">规则 14 - 对遇</span>
        </div>
        <div class="route-point">
          <div class="route-dot"></div>
          <span class="route-label">规则 15 - 交叉</span>
        </div>
        <div class="route-point">
          <div class="route-dot"></div>
          <span class="route-label">规则 16 - 让路船</span>
        </div>
      </div>
    `;
    
    this.container.appendChild(this.panel);
  }
  
  update(alerts) {
    this.alerts = alerts;
    const container = document.getElementById('colregs-alerts');
    container.innerHTML = '';
    
    alerts.forEach(alert => {
      const div = document.createElement('div');
      div.className = 'colregs-alert';
      div.innerHTML = `
        <div class="colregs-alert-title">
          ⚠️ ${alert.rule || 'COLREGS 警告'}
        </div>
        <div class="colregs-rule">${alert.message}</div>
      `;
      container.appendChild(div);
    });
  }
}
```

### 4.5 AlarmFeedPanel.js - 告警面板

```javascript
// src/frontend/digital-twin/layer1-interface/AlarmFeedPanel.js

export class AlarmFeedPanel {
  constructor(container) {
    this.container = container;
    this.alarms = [];
  }
  
  async initialize() {
    this._createPanel();
  }
  
  _createPanel() {
    this.panel = document.createElement('div');
    this.panel.className = 'panel';
    this.panel.innerHTML = `
      <h2>
        告警列表
        <span class="badge">实时</span>
      </h2>
      <div class="alarm-feed" id="alarm-feed"></div>
    `;
    
    this.container.appendChild(this.panel);
  }
  
  update(alarms) {
    this.alarms = alarms;
    const feed = document.getElementById('alarm-feed');
    feed.innerHTML = '';
    
    alarms.slice(0, 10).forEach(alarm => {
      const card = document.createElement('div');
      card.className = `alarm-card level-${alarm.level}`;
      card.innerHTML = `
        <div class="alarm-card-header">
          <span class="alarm-card-level ${alarm.level}">${alarm.level}</span>
          <span class="alarm-card-time">${new Date(alarm.time).toLocaleTimeString()}</span>
        </div>
        <div class="alarm-card-message">${alarm.message}</div>
        <div class="alarm-card-source">${alarm.source}</div>
      `;
      feed.appendChild(card);
    });
  }
}
```

---

## 5. HTML 页面修改

### 5.1 datacenter-digital-twin.html 新增 AR-CAS-PRO 菜单

在现有 HTML 结构中添加 AR-CAS-PRO 菜单按钮和面板容器：

```html
<!-- 在 HUD 的 pills 区域添加 AR-CAS-PRO 按钮 -->
<div class="pills">
  <button class="pill" onclick="toggleARCASPro()">AR-CAS PRO</button>
  <button class="pill live">LIVE</button>
  <button class="pill ws">WS</button>
</div>

<!-- 在 twin-viewport 中添加 AR 叠加层 -->
<div class="twin-viewport" id="twin-viewport">
  <canvas id="three-canvas"></canvas>
  
  <!-- AR 叠加层 -->
  <div class="ar-overlay" id="ar-overlay" style="display:none;">
    <div class="ar-target" id="ar-target-1"></div>
    <div class="ar-target-label" id="ar-target-label-1">Cargo | 12kn</div>
    <div class="ar-iceberg" id="ar-iceberg-1"></div>
    <div class="ar-iceberg-warning">⚠️ 冰山警告 - 距离 2.5 海里</div>
    <div class="ar-canyon" id="ar-canyon-1"></div>
    <div class="ar-canyon-warning">⚠️ 海底峡谷 - 水深 15m</div>
  </div>
  
  <!-- 原有 twin-overlay -->
  <div class="twin-overlay">
    <span class="tag live">● LIVE</span>
    <span class="tag">AR-CAS PRO</span>
  </div>
  
  <!-- 原有 twin-controls -->
  <div class="twin-controls" id="twin-controls">
    <!-- ... 原有图层按钮 ... -->
  </div>
</div>

<!-- 在 grid-21 布局中添加 AR-CAS-PRO 面板 -->
<div class="grid-21" id="main-grid">
  <div>
    <!-- 原有 twin-viewport -->
  </div>
  <div id="right-panels">
    <!-- 原有面板 -->
    <div class="panel">
      <h2>物理↔数字映射</h2>
      <!-- ... -->
    </div>
    
    <!-- AR-CAS-PRO 面板容器 -->
    <div id="ar-cas-pro-panels" style="display:none;">
      <!-- AIS 目标面板 -->
      <div id="ais-target-panel"></div>
      <!-- COLREGS 面板 -->
      <div id="colregs-panel"></div>
      <!-- 告警面板 -->
      <div id="alarm-feed-panel"></div>
      <!-- 天气面板 -->
      <div class="panel">
        <h2>天气信息 <span class="badge">AR-CAS</span></h2>
        <div class="weather-grid">
          <div class="weather-item">
            <div class="weather-label">风速</div>
            <div class="weather-value" id="wind-speed">--</div>
          </div>
          <div class="weather-item">
            <div class="weather-label">风向</div>
            <div class="weather-value" id="wind-direction">--</div>
          </div>
          <div class="weather-item">
            <div class="weather-label">浪高</div>
            <div class="weather-value" id="wave-height">--</div>
          </div>
          <div class="weather-item">
            <div class="weather-label">能见度</div>
            <div class="weather-value" id="visibility">--</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

### 5.2 CSS 样式添加

在 `datacenter-digital-twin.html` 的 `<style>` 中添加 AR-CAS-PRO 相关样式：

```css
/* AR-CAS-PRO 样式 */
.ar-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  pointer-events: none;
  z-index: 10;
}

.ar-target {
  position: absolute;
  width: 28px; height: 28px;
  border: 3px solid var(--koke);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 20px rgba(79,195,247,0.6);
  animation: ar-pulse 2s infinite;
}

@keyframes ar-pulse {
  0%, 100% { box-shadow: 0 0 20px rgba(79,195,247,0.6); }
  50% { box-shadow: 0 0 30px rgba(79,195,247,0.9); }
}

.ar-target-label {
  position: absolute;
  top: -24px; left: 50%;
  transform: translateX(-50%);
  background: var(--sumi);
  padding: 4px 8px;
  font-size: 10px;
  white-space: nowrap;
  color: var(--shironeri);
  border: 1px solid var(--koke);
  font-family: var(--font-mono);
}

.ar-iceberg {
  position: absolute;
  width: 40px; height: 40px;
  background: linear-gradient(180deg, rgba(135,206,250,0.8) 0%, rgba(135,206,250,0.3) 100%);
  border: 2px solid var(--koke);
  clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
  transform: translate(-50%, -50%);
  animation: iceberg-pulse 3s infinite;
}

@keyframes iceberg-pulse {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

.ar-canyon {
  position: absolute;
  height: 100%;
  width: 80px;
  background: linear-gradient(90deg, rgba(139,69,19,0.5) 0%, rgba(139,69,19,0.2) 50%, rgba(139,69,19,0.5) 100%);
  border-left: 3px dashed var(--kitsune);
  border-right: 3px dashed var(--kitsune);
}

.ar-canyon-warning {
  position: absolute;
  bottom: 80px; left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, rgba(245,101,101,0.95) 0%, rgba(245,101,101,0.8) 100%);
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 700;
  color: var(--shironeri);
  white-space: nowrap;
  box-shadow: 0 4px 20px rgba(245,101,101,0.5);
}

.ar-iceberg-warning {
  position: absolute;
  top: 80px; left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, rgba(135,206,250,0.95) 0%, rgba(135,206,250,0.8) 100%);
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 700;
  color: var(--shironeri);
  white-space: nowrap;
  box-shadow: 0 4px 20px rgba(135,206,250,0.5);
}

/* AIS 目标样式 */
.ais-target {
  background: var(--bg-1);
  padding: 14px;
  margin-bottom: 10px;
  border-left: 4px solid var(--koke);
  cursor: pointer;
  transition: all 0.3s;
}

.ais-target:hover {
  background: var(--bg-2);
  transform: translateX(6px);
  box-shadow: 0 4px 12px rgba(79,195,247,0.2);
}

.ais-target.high-risk {
  border-left-color: var(--shu);
  background: linear-gradient(135deg, rgba(245,101,101,0.15) 0%, var(--bg-1) 100%);
}

.ais-target.medium-risk {
  border-left-color: var(--kitsune);
}

.ais-target-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.ais-target-type {
  font-weight: 700;
  color: var(--koke);
  font-size: 14px;
}

.ais-target-mmsi {
  color: var(--muted);
  font-size: 11px;
}

.ais-target-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  font-size: 11px;
  color: var(--muted);
}

.risk-badge {
  display: inline-block;
  padding: 3px 10px;
  font-size: 10px;
  font-weight: 700;
  margin-left: 8px;
  text-transform: uppercase;
}

.risk-badge.low {
  background: rgba(72,187,120,0.25);
  color: var(--koke);
}

.risk-badge.medium {
  background: rgba(246,173,85,0.25);
  color: var(--kitsune);
}

.risk-badge.high {
  background: rgba(245,101,101,0.25);
  color: var(--shu);
}

/* CPA/TCPA 样式 */
.cpa-tcpa {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  margin-top: 14px;
}

.cpa-item {
  background: var(--bg-2);
  padding: 12px;
  text-align: center;
}

.cpa-label {
  font-size: 10px;
  color: var(--muted);
  margin-bottom: 6px;
  text-transform: uppercase;
}

.cpa-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
}

.cpa-value.danger {
  color: var(--shu);
}

.cpa-value.warning {
  color: var(--kitsune);
}

.cpa-value.safe {
  color: var(--koke);
}

/* COLREGS 样式 */
.colregs-alert {
  background: linear-gradient(135deg, rgba(245,101,101,0.15) 0%, var(--bg-1) 100%);
  border: 1px solid var(--shu);
  padding: 14px;
  margin-bottom: 14px;
}

.colregs-alert-title {
  font-weight: 700;
  color: var(--shu);
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.colregs-rule {
  font-size: 12px;
  color: var(--shu);
  line-height: 1.6;
}

/* 告警样式 */
.alarm-feed {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.alarm-card {
  background: var(--bg-2);
  padding: 12px;
  border-left: 4px solid var(--koke);
}

.alarm-card.level-WARNING {
  border-left-color: var(--kitsune);
}

.alarm-card.level-CRITICAL,
.alarm-card.level-EMERGENCY {
  border-left-color: var(--shu);
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
  font-size: 10px;
  font-weight: 700;
  background: rgba(72,187,120,0.2);
  color: var(--koke);
}

.alarm-card-level.WARNING {
  background: rgba(246,173,85,0.2);
  color: var(--kitsune);
}

.alarm-card-level.CRITICAL,
.alarm-card-level.EMERGENCY {
  background: rgba(245,101,101,0.2);
  color: var(--shu);
}

.alarm-card-time {
  font-size: 11px;
  color: var(--muted);
}

.alarm-card-message {
  font-size: 12px;
  color: var(--text);
  line-height: 1.5;
}

.alarm-card-source {
  margin-top: 8px;
  font-size: 10px;
  color: var(--koke);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* 天气样式 */
.weather-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.weather-item {
  background: var(--bg-2);
  padding: 14px;
  text-align: center;
}

.weather-label {
  font-size: 11px;
  color: var(--muted);
  margin-bottom: 6px;
}

.weather-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--koke);
}
```

### 5.3 JavaScript 初始化代码

在 `datacenter-digital-twin.html` 的 `<script>` 中添加：

```javascript
// AR-CAS-PRO 模块
let arCasProModule = null;

function toggleARCASPro() {
  const panels = document.getElementById('ar-cas-pro-panels');
  const arOverlay = document.getElementById('ar-overlay');
  const button = event.target;
  
  if (panels.style.display === 'none') {
    panels.style.display = 'block';
    arOverlay.style.display = 'block';
    button.classList.add('active');
    
    // 初始化 AR-CAS-PRO 模块
    if (!arCasProModule) {
      initARCASPro();
    }
  } else {
    panels.style.display = 'none';
    arOverlay.style.display = 'none';
    button.classList.remove('active');
  }
}

async function initARCASPro() {
  const { ARCASProModule } = await import('/digital-twin/ARCASProModule.js');
  
  arCasProModule = new ARCASProModule(scene, camera, {
    enableAIS: true,
    enableAR: true,
    enableCOLREGS: true,
    enableAlarms: true
  });
  
  await arCasProModule.initialize(document.getElementById('ar-cas-pro-panels'));
  
  // 更新天气信息
  setInterval(() => {
    if (arCasProModule && arCasProModule.weather) {
      document.getElementById('wind-speed').textContent = 
        arCasProModule.weather.windSpeed.toFixed(1) + ' kn';
      document.getElementById('wind-direction').textContent = 
        arCasProModule.weather.windDirection + '°';
      document.getElementById('wave-height').textContent = 
        arCasProModule.weather.waveHeight.toFixed(1) + ' m';
      document.getElementById('visibility').textContent = 
        arCasProModule.weather.visibility.toFixed(1) + ' nm';
    }
  }, 5000);
}
```

---

## 6. PoseidonX.js 修改

在 `PoseidonX.js` 中添加 AR-CAS-PRO 模块注册：

```javascript
// 在 PoseidonX 类的 initialize 方法中添加
async _initializeARCASPro() {
  const { ARCASProModule } = await import('./ARCASProModule.js');
  
  this.arCasPro = new ARCASProModule(this.scene, this.camera, {
    enableAIS: true,
    enableAR: true,
    enableCOLREGS: true,
    enableAlarms: true
  });
  
  // 监听 AR-CAS-PRO 事件
  this.arCasPro.on('target:selected', (target) => {
    this.emit('ar:targetSelected', target);
  });
  
  this.arCasPro.on('alarm:generated', (alarm) => {
    this.emit('ar:alarm', alarm);
  });
  
  console.log('  ✅ AR-CAS-PRO Module initialized');
}
```

---

## 7. 实施步骤

### 步骤 1: 创建新文件
1. 创建 `src/frontend/digital-twin/ARCASProModule.js`
2. 创建 `src/frontend/digital-twin/layer1-interface/AROverlay.js`
3. 创建 `src/frontend/digital-twin/layer1-interface/AISTargetPanel.js`
4. 创建 `src/frontend/digital-twin/layer1-interface/COLREGSPanel.js`
5. 创建 `src/frontend/digital-twin/layer1-interface/AlarmFeedPanel.js`

### 步骤 2: 修改现有文件
1. 修改 `src/frontend/datacenter-digital-twin.html`
   - 添加 AR-CAS-PRO 菜单按钮
   - 添加 AR 叠加层 HTML
   - 添加 AR-CAS-PRO 面板容器
   - 添加 CSS 样式
   - 添加 JavaScript 初始化代码

2. 修改 `src/frontend/digital-twin/PoseidonX.js`
   - 添加 AR-CAS-PRO 模块注册

### 步骤 3: 测试验证
1. 启动开发服务器
2. 打开数字孪生页面
3. 点击 AR-CAS-PRO 按钮
4. 验证：
   - AIS 目标显示
   - AR 叠加层渲染
   - COLREGS 规则显示
   - 告警列表更新
   - 天气信息更新
   - CPA/TCPA 计算

---

## 8. 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Three.js 与 Maplibre 冲突 | AR 渲染异常 | 使用独立渲染层 |
| 性能开销 | 帧率下降 | 限制 AIS 目标数量 (≤20) |
| 数据模拟不真实 | 测试效果差 | 后续接入真实 AIS 数据源 |
| 样式冲突 | 视觉不一致 | 使用 Wabi-Sabi 设计变量 |

---

## 9. 后续优化

1. **真实数据接入**：连接后端 AIS 数据 API
2. **3D 模型增强**：在场景中渲染 3D 船舶模型
3. **手势交互**：支持触摸/手势操作 AR 目标
4. **语音告警**：集成语音播报系统
5. **历史回放**：支持 AR-CAS 事件回放

────────────────────────────────────────────────────────────
✅ deepseek-chat 完成
