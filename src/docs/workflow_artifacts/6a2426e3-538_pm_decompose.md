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

好的，项目经理。我已经分析了任务需求和项目上下文，以下是结构化的任务分解文档。

---

## 任务分解与规划: AR-CAS-PRO 功能迁移至数字孪生页面

**项目名称:** PoseidonX 系统 - AR-CAS-PRO 功能集成
**项目经理:** PoseidonX PM
**目标受众:** Build 团队 PM、架构师、前端/后端开发者
**优先级:** 高
**预计工期:** 3-5 个工作日 (取决于资源投入和复杂度)

---

### 1. 任务概述

将独立页面 `worldmonitor-ar-cas-pro.html` 中的“AR-CAS-PRO”菜单及其全部功能，完整、无缝地迁移并集成到现有的数字孪生页面 `datacenter-digital-twin.html` 中。迁移后的 AR-CAS-PRO 功能应利用数字孪生页面的 3D 场景作为增强现实 (AR) 的基础，实现物理世界与数字模型的融合。

### 2. 核心目标

1.  **功能完整性:** 确保 `worldmonitor-ar-cas-pro.html` 中的所有核心功能（AIS 目标追踪、碰撞风险评估、AR 叠加、告警系统、天气信息、航线规划等）在数字孪生页面中均可正常工作。
2.  **技术融合:** 将 AR-CAS-PRO 的 2D 地图和 AR 叠加逻辑，与数字孪生页面的 3D 场景 (`Three.js` / `WebGL`) 进行深度整合。AR 元素（如目标标记、危险警告）应作为 3D 场景中的覆盖层或对象呈现。
3.  **用户体验一致性:** 保持 AR-CAS-PRO 的核心交互逻辑和视觉风格，同时适配数字孪生页面的整体 UI/UX 设计语言（Wabi-Sabi Rubber 主题）。
4.  **代码可维护性:** 迁移后的代码应模块化，与现有数字孪生系统的架构 (`PoseidonX.js`, `DigitalTwinMap.js` 等) 良好集成，避免产生大量重复或难以维护的代码。

### 3. 任务分解与子步骤

#### 阶段 1: 分析与规划 (1天)

| 子步骤 | 描述 | 负责人 | 交付物 |
| :--- | :--- | :--- | :--- |
| **1.1 功能清单梳理** | 详细分析 `worldmonitor-ar-cas-pro.html`，列出所有功能模块、UI 组件、交互逻辑、数据流和依赖的外部库（如 MapLibre GL JS）。 | 架构师 / 高级前端 | `AR-CAS-PRO_Function_List.md` |
| **1.2 数字孪生架构评估** | 分析 `datacenter-digital-twin.html` 的现有架构，特别是 `PoseidonX.js` 及其子模块（`DigitalTwinMap.js`, `BridgeChat.js` 等），确定集成点。 | 架构师 | `Integration_Points_Report.md` |
| **1.3 技术方案设计** | 确定核心集成方案：<br> - **AR 渲染层:** 在 3D 场景中创建一个独立的 `AR Overlay` 层或使用 `CSS3DRenderer` 叠加 HTML 元素。<br> - **数据源:** 确定 AIS、天气、告警等数据的来源（模拟数据 vs. 后端 API）。<br> - **交互模式:** 定义用户如何与 AR 对象交互（点击、悬停等）。 | 架构师 / 技术负责人 | `Technical_Design_Doc.md` |
| **1.4 风险评估** | 识别潜在风险：<br> - **性能风险:** 在 3D 场景中叠加大量 AR 元素可能导致帧率下降。<br> - **数据依赖:** 后端 API 可能尚未提供 AR-CAS-PRO 所需的所有数据。<br> - **UI 冲突:** AR-CAS-PRO 的 UI 可能与数字孪生页面现有 UI 冲突。 | 项目经理 / 技术负责人 | `Risk_Register.md` |

#### 阶段 2: 核心功能迁移与集成 (2-3天)

| 子步骤 | 描述 | 负责人 | 交付物 |
| :--- | :--- | :--- | :--- |
| **2.1 创建 AR-CAS-PRO 核心模块** | 在 `src/frontend/digital-twin/` 下创建新的模块，例如 `ARCASProModule.js`。该模块将封装所有 AR-CAS-PRO 相关的逻辑，包括数据获取、碰撞计算、AR 对象管理等。 | 高级前端 | `ARCASProModule.js` |
| **2.2 集成数据层** | 将 AIS 目标数据、天气数据、告警数据等接入 `ARCASProModule`。优先使用后端 API (`src/backend/`)，若不可用则使用模拟数据。 | 后端 / 前端 | 数据接口代码 |
| **2.3 实现 3D AR 叠加层** | - 在 `DigitalTwinMap.js` 或 `PoseidonX.js` 中集成 `ARCASProModule`。<br>- 实现 AR 对象的 3D 渲染：<br>  - **AIS 目标:** 使用 `Sprite` 或 `Mesh` 在对应经纬度位置显示船只图标、名称、航向、速度等信息。<br>  - **碰撞风险:** 高亮显示高风险目标，绘制 CPA/TCPA 预测线。<br>  - **危险区域:** 使用半透明几何体或粒子系统表示冰山、峡谷等。<br>  - **告警标记:** 在 3D 场景中弹出告警气泡或标记。 | 高级前端 | 3D AR 渲染代码 |
| **2.4 迁移 UI 组件** | - 将 `worldmonitor-ar-cas-pro.html` 中的侧边栏（AIS 目标列表、天气、航线等）和右侧面板（告警、AR 视图）的 HTML/CSS 代码迁移到 `datacenter-digital-twin.html` 中。<br>- 适配 Wabi-Sabi Rubber 主题样式。<br>- 将 UI 组件与 `ARCASProModule` 的数据和事件绑定。 | 前端 | 迁移后的 UI 代码 |
| **2.5 实现交互逻辑** | - 实现点击 3D AR 目标弹出详情信息的功能。<br>- 实现侧边栏 AIS 目标列表与 3D 场景中目标的联动高亮。<br>- 实现告警卡片与 3D 场景中告警位置的联动。 | 前端 | 交互逻辑代码 |

#### 阶段 3: 测试、优化与集成 (1-2天)

| 子步骤 | 描述 | 负责人 | 交付物 |
| :--- | :--- | :--- | :--- |
| **3.1 功能测试** | 对照功能清单，逐一测试所有迁移后的功能是否正常工作。 | QA / 开发者 | `Test_Report.md` |
| **3.2 性能测试与优化** | - 在目标设备上测试页面加载和运行时的性能。<br>- 优化 3D 场景中的 AR 对象数量、LOD（细节层次）和渲染方式。<br>- 优化数据更新频率，避免不必要的重绘。 | 高级前端 | `Performance_Report.md` |
| **3.3 UI/UX 审查** | 确保迁移后的 UI 与数字孪生页面整体风格一致，交互流畅，无视觉冲突。 | UI/UX 设计师 | `UI_Review_Report.md` |
| **3.4 代码审查与合并** | 对 `ARCASProModule.js` 及相关修改进行代码审查，确保代码质量、可读性和与现有架构的兼容性。合并到主分支。 | 技术负责人 / 全体 | 合并后的代码库 |
| **3.5 文档更新** | 更新 `PoseidonX.js` 或相关文档，说明如何启用和配置 AR-CAS-PRO 功能。 | 开发者 | 更新后的文档 |

### 4. 技术依赖与风险

| 依赖/风险 | 描述 | 缓解措施 |
| :--- | :--- | :--- |
| **依赖: 后端 API** | AR-CAS-PRO 的实时 AIS、天气、告警数据需要后端 API 支持。 | 1. 确认 `src/backend/` 中是否有相关 API。2. 若无，则先使用模拟数据，并创建 API 接口需求文档。 |
| **依赖: 3D 场景引擎** | 数字孪生页面使用 `Three.js` (通过 `DigitalTwinMap.js` 等)。AR 叠加需要与 Three.js 场景深度集成。 | 确保开发团队有 Three.js 经验。利用 `CSS2DRenderer` 或 `CSS3DRenderer` 作为备选方案。 |
| **风险: 性能瓶颈** | 在 3D 场景中渲染大量动态 AR 对象（如 AIS 目标）可能导致性能下降。 | 1. 使用 `InstancedMesh` 渲染大量相同几何体。2. 实现视锥体裁剪，只渲染视野内的对象。3. 限制 AR 对象的更新频率。 |
| **风险: 代码冲突** | 新模块 `ARCASProModule.js` 可能与现有模块（如 `DigitalTwinMap.js`）存在功能重叠或命名冲突。 | 在代码审查阶段严格检查。遵循现有模块的设计模式（如 `EventEmitter`）。 |
| **风险: UI 复杂度** | 将 AR-CAS-PRO 的复杂 UI 嵌入数字孪生页面可能导致布局混乱。 | 设计阶段就考虑 UI 布局。使用 `position: absolute` 或 `fixed` 将 AR-CAS-PRO 面板作为独立层叠加在 3D 场景之上。 |

### 5. 交付物清单

1.  **`AR-CAS-PRO_Function_List.md`**: 详细的功能清单。
2.  **`Integration_Points_Report.md`**: 集成点分析报告。
3.  **`Technical_Design_Doc.md`**: 技术方案设计文档。
4.  **`Risk_Register.md`**: 风险登记册。
5.  **`ARCASProModule.js`**: 核心功能模块代码。
6.  **修改后的 `datacenter-digital-twin.html`**: 集成新功能的页面。
7.  **修改后的 `PoseidonX.js`**: 集成新模块的系统入口。
8.  **`Test_Report.md`**: 功能测试报告。
9.  **`Performance_Report.md`**: 性能测试报告。
10. **`UI_Review_Report.md`**: UI/UX 审查报告。

### 6. 后续行动

1.  **立即:** 由架构师主导，开始 **阶段 1** 的分析工作，并在 **1 天内** 输出 `Technical_Design_Doc.md`。
2.  **同步:** 后端团队需确认 AIS、天气等实时数据 API 的可用性，并准备模拟数据方案。
3.  **资源分配:** 请 Build 团队 PM 根据此计划，分配至少 1 名高级前端工程师和 1 名后端工程师全职投入此任务。

请 Build 团队 PM 确认此计划，并开始执行。如有任何疑问，请随时与我沟通。

────────────────────────────────────────────────────────────
✅ deepseek-chat 完成
