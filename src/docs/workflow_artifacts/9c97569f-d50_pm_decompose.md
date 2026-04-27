# PM分解 — project_manager

任务: 让货船以双体船为圆心动起来 (V2)
步骤: pm_decompose
Agent: build_pm

---

📋 任务: 9c97569f-d50
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
  让货船以双体船为圆心动起来 (V2)
  在 src/frontend/digital-twin/main.js 里让 cargo ship 围绕双体船做圆周轨道运动，半径 80m，角速度 0.015 rad/帧。验证：刷新前端页面后货船能可见地以圆周轨迹移动。
  
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
  ... (共 800 个 src/ 文件)
  
  ```
  
  ### 文件: `src/frontend/ship-shore.html`
  ```html
  <!DOCTYPE html>
  <html lang="zh-CN">
  <head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>船岸协同 — PoseidonX</title>
  <link rel="stylesheet" href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css">
  <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300;400;500;700&family=Noto+Serif:wght@200;300;400;600;900&family=Noto+Serif+SC:wght@200;300;400;600;900&family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap">
  <style>
  :root{
    --shironeri:oklch(0.96 0.003 110);--ishi:oklch(0.91 0.004 110);--kabe:oklch(0.85 0.005 110);
    --hai:oklch(0.78 0.005 110);--nezumi:oklch(0.68 0.006 110);
    --sumi:oklch(0.18 0.008 110);--sumi-2:oklch(0.38 0.006 110);--sumi-3:oklch(0.55 0.005 110);
    --koke:oklch(0.52 0.04 160);--shu:oklch(0.48 0.07 22);--kitsune:oklch(0.56 0.05 70);
    --groove:oklch(0.82 0.004 110);--ridge:oklch(1.00 0 0 / 0.6);
  }
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Noto Sans SC',sans-serif;background:var(--shironeri);color:var(--sumi);overflow:hidden;padding:48px 0 0 64px}
  body::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
    background-image:radial-gradient(oklch(0 0 0/.012) 1px,transparent 1px),radial-gradient(oklch(0 0 0/.008) 1px,transparent 1px);
    background-size:5px 5px,7px 7px;background-position:0 0,3px 3px}
  .shore-layout{display:grid;grid-template-columns:1fr 380px;gap:0;height:calc(100vh - 48px);position:relative;z-index:1}
  #fleetMap{width:100%;height:100%;min-height:400px}
  .shore-sidebar{display:flex;flex-direction:column;gap:12px;padding:14px;overflow-y:auto;background:var(--ishi);border-left:1px solid var(--groove)}
  .sh-card{background:var(--shironeri);border:1px solid var(--groove);padding:16px}
  .sh-card h5{margin:0 0 12px;font-family:'Noto Serif SC',serif;font-size:12px;font-weight:600;display:flex;align-items:center;gap:8px}
  .sh-card h5 .seal{font-size:10px;font-weight:900;color:var(--shironeri);background:var(--sumi);padding:1px 5px;line-height:1.3;font-family:'Noto Serif SC',serif}
  .comm-link{display:flex;align-items:center;gap:12px;padding:10px;background:var(--kabe);border:1px solid var(--groove);margin-bottom:8px;transition:all .15s}
  .comm-link:last-child{margin-bottom:0}
  .comm-link:hover{border-color:var(--hai)}
  .comm-seal{font-family:'Noto Serif SC',serif;font-size:14px;font-weight:900;width:36px;height:36px;display:flex;align-items:center;justify-content:center;background:var(--ishi);border:1px solid var(--groove)}
  .comm-info{flex:1}
  .comm-info .name{font-size:12px;font-weight:600}
  .comm-info .signal{font-size:10px;color:var(--sumi-3);margin-top:2px;font-family:'JetBrains Mono',monospace}
  .comm-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
  .comm-dot.online{background:var(--koke)}.comm-dot.degraded{background:var(--kitsune)}.comm-dot.offline{background:var(--shu)}
  .flow-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
  .flow-item{text-align:center;padding:12px;background:var(--kabe);border:1px solid var(--groove)}
  .flow-item .v{font-size:20px;font-weight:700;color:var(--sumi);font-family:'JetBrains Mono',monospace}
  .flow-item .l{font-size:10px;color:var(--sumi-3);margin-top:2px}
  .bw-canvas{width:100%;height:60px;display:block;margin-top:8px}
  .sync-items{display:flex;flex-direction:column;gap:8px}
  .sync-item{display:flex;align-items:center;gap:10px;padding:8px 10px;background:var(--kabe);font-size:12px}
  .sync-item .v{margin-left:auto;font-weight:600;font-size:11px;font-family:'JetBrains Mono',monospace}
  .cmd-table{width:100%;border-collapse:collapse;font-size:11px}
  .cmd-table th{text-align:left;padding:6px 8px;color:var(--sumi-3);font-weight:600;font-size:10px;text-transform:uppercase;border-bottom:1px solid var(--groove);font-family:'JetBrains Mono',monospace}
  .cmd-table td{padding:6px 8px;border-bottom:1px solid var(--kabe)}
  .cmd-table tr:hover td{background:var(--kabe)}
  .badge-s{display:inline-flex;padding:2px 8px;font-size:9px;font-weight:600;font-family:'JetBrains Mono',monospace}
  .badge-ok{background:oklch(0.52 0.04 160/.1);color:var(--koke);border:1px solid oklch(0.52 0.04 160/.2)}
  .badge-warn{background:oklch(0.56 0.05 70/.1);color:var(--kitsune);border:1px solid oklch(0.56 0.05 70/.2)}
  .live-dot{display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--koke);margin-left:auto;animation:pulse 2s infinite}
  @keyframes pulse{0%,100%{opacity:.5}50%{opacity:1}}
  </style>
  <link rel="stylesheet" href="/css/openbridge-theme.css">
  <link rel="stylesheet" href="/css/ws-theme-bridge.css">
  </head>
  <body>
  <div class="shore-layout">
  <div id="fleetMap"></div>
  <div class="shore-sidebar">
      <div class="sh-card">
          <h5><span class="seal">链</span> 通信链路 <span class="live-dot"></span></h5>
          <div class="comm-link"><div class="comm-seal">衛</div><div class="comm-info"><div class="name">VSAT Ku-Band</div><div class="signal">-62 dBm | 12 Mbps</div></div><div class="comm-dot online"></div></div>
          <div class="comm-link"><div class="comm-seal">蜂</div><div class="comm-info"><div class="name">4G/LTE (沿海)</div><div class="signal">-78 dBm | 50 Mbps</div></div><div class="comm-dot online"></div></div>
          <div class="comm-link"><div class="comm-seal">銥</div><div class="comm-info"><div class="name">Iridium NEXT</div><div class="signal">-94 dBm | 704 kbps</div></div><div class="comm-dot degraded"></div></div>
          <div class="comm-link"><div class="comm-seal">舶</div><div class="comm-info"><div class="name">AIS 雙频</div><div class="signal">正常 | 2 × VHF</div></div><div class="comm-dot online"></div></div>
          <div class="comm-link"><div class="comm-seal">遇</div><div class="comm-info"><div class="name">GMDSS / DSC</div><div class="signal">VHF Ch70 | MF/HF</div></div><div class="comm-dot online"></div></div>
      </div>
      <div class="sh-card">
          <h5><span class="seal">流</span> 远程数据流</h5>
          <div class="flow-grid">
              <div class="flow-item"><div class="v" id="flowUp">1.2</div><div class="l">上行 Mbps</div></div>
              <div class="flow-item"><div class="v" id="flowDown">4.5</div><div class="l">下行 Mbps</div></div>
              <div class="flow-item"><div class="v" id="flowLat">280</div><div class="l">延遲 ms</div></div>
              <div class="flow-item"><div class="v" style="color:var(--koke)" id="flowSync">OK</div><div class="l">数据同步</div></div>
          </div>
          <canvas id="bwChart" class="bw-canvas" height="60"></canvas>
      </div>
      <div class="sh-card">
          <h5><span class="seal">同</span> 数据同步</h5>
          <div class="sync-items">
              <div class="sync-item"><span class="comm-dot online" style="width:8px;height:8px"></span>航行数据 → 岸基<div class="v" style="color:var(--koke)">实时</div></div>
              <div class="sync-item"><span class="comm-dot online" style="width:8px;height:8px"></span>CMS 传感器 → 云存儲<div class="v" style="color:var(--koke)">5s</div></div>
              <div class="sync-item"><span class="comm-dot degraded" style="width:8px;height:8px"></span>視频监控 → S3<div class="v" style="color:var(--kitsune)">30s</div></div>
              <div class="sync-item"><span class="comm-dot online" style="width:8px;height:8px"></span>岸基指令 → 船端<div class="v" style="color:var(--koke)">实时</div></div>
          </div>
      </div>
      <div class="sh-card">
          <h5><span class="seal">令</span> 岸基指令历史</h5>
          <table class="cmd-table">
              <thead><tr><th>时間</th><th>來源</th><th>指令</th><th>狀态</th></tr></thead>
              <tbody id="cmdBody">
                  <tr><td>14:30</td><td>SCC 上海</td><td>航速调整至 12kn</td><td><span class="badge-s badge-ok">已执行</span></td></tr>
                  <tr><td>12:15</td><td>VTS 寧波</td><td>进港航道确认</td><td><span class="badge-s badge-ok">已确认</span></td></tr>
                  <tr><td>09:40</td><td>SCC 上海</td><td>台風预警转发</td><td><span class="badge-s badge-warn">待确认</span></td></tr>
                  <tr><td>08:00</td><td>总部</td><td>CII 优化建议下发</td><td><span class="badge-s badge-ok">已接收</span></td></tr>
              </tbody>
          </table>
      </div>
  </div>
  </div>
  <script>
  const map=new maplibregl.Map({container:'fleetMap',style:{version:8,sources:{'osm':{type:'raster',tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,attribution:'OpenStreetMap'}},layers:[{id:'osm',type:'raster',source:'osm'}]},center:[122,30],zoom:5});
  map.on('load',()=>{
      fetch('/api/v1/fleet/positions').then(r=>r.json()).then(geojson=>{
          map.addSource('fleet',{type:'geojson',data:geojson});
          map.addLayer({id:'fleet-dots',type:'circle',source:'fleet',paint:{'circle-radius':8,'circle-color':['case',['get','is_own'],'oklch(0.48 0.07 22)','oklch(0.52 0.04 160)'],'circle-stroke-width':2,'circle-stroke-color':'oklch(0.96 0.003 110)','circle-opacity':0.9}});
          map.addLayer({id:'fleet-labels',type:'symbol',source:'fleet',layout:{'text-field':['get','name'],'text-offset':[0,1.8],'text-size':12},paint:{'text-color':'oklch(0.18 0.008 110)','text-halo-color':'oklch(0.96 0.003 110)','text-halo-width':1}});
      }).catch(()=>{
          map.addSource('fleet',{type:'geojson',data:{type:'FeatureCollection',features:[
              {type:'Feature',geometry:{type:'Point',coordinates:[122.1,30.6]},properties:{name:'PoseidonX-01',is_own:true}},
              {type:'Feature',geometry:{type:'Point',coordinates:[121.5,31.2]},properties:{name:'PoseidonX-02'}},
              {type:'Feature',geometry:{type:'Point',coordinates:[120.8,29.8]},properties:{name:'PoseidonX-03'}}
          ]}});
          map.addLayer({id:'fleet-dots',type:'circle',source:'fleet',paint:{'circle-radius':8,'circle-color':['case',['get','is_own'],'oklch(0.48 0.07 22)','oklch(0.52 0.04 160)'],'circle-stroke-width':2,'circle-stroke-color':'oklch(0.96 0.003 110)'}});
          map.addLayer({id:'fleet-labels',type:'symbol',source:'fleet',layout:{'text-field':['get','name'],'text-offset':[0,1.8],'text-size':12},paint:{'text-color':'oklch(0.18 0.008 110)','text-halo-color':'oklch(0.96 0.003 110)','text-halo-width':1}});
      });
      setInterval(()=>{fetch('/api/v1/fleet/positions').then(r=>r.json()).then(geojson=>{const src=map.getSource('fleet');if(src)src.setData(geojson);}).catch(()=>{});},15000);
  });
  const bwHistory=[];
  function drawBwChart(){
      const cv=document.getElementById('bwChart'),ctx=cv.getContext('2d');
      const W=cv.width=cv.offsetWidth,H=60;
      ctx.clearRect(0,0,W,H);
      if(bwHistory.length<2)return;
      const max=Math.max(...bwHistory.map(b=>b.up+b.down))*1.3||10;
      ctx.beginPath();bwHistory.forEach((b,i)=>{const x=i/(bwHistory.length-1)*W,y=H-(b.up/max)*H;i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});
      ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.closePath();ctx.fillStyle='oklch(0.52 0.04 160/.08)';ctx.fill();
      ctx.beginPath();bwHistory.forEach((b,i)=>{const x=i/(bwHistory.length-1)*W,y=H-(b.up/max)*H;i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});
      ctx.strokeStyle='oklch(0.52 0.04 160/.5)';ctx.lineWidth=1.5;ctx.stroke();
      ctx.beginPath();bwHistory.forEach((b,i)=>{const x=i/(bwHistory.length-1)*W,y=H-(b.down/max)*H;i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});
      ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.closePath();ctx.fillStyle='oklch(0.38 0.006 110/.08)';ctx.fill();
      ctx.beginPath();bwHistory.forEach((b,i)=>{const x=i/(bwHistory.length-1)*W,y=H-(b.down/max)*H;i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});
      ctx.strokeStyle='oklch(0.38 0.006 110/.5)';ctx.lineWidth=1.5;ctx.stroke();
  }
  setInterval(()=>{
      bwHistory.push({up:1.2+(Math.random()-.5)*.6,down:4.5+(Math.random()-.5)*1.5});
      if(bwHistory.length>60)bwHistory.shift();drawBwChart();
      if(bwHistory.length>0){const last=bwHistory[bwHistory.length-1];document.getElementById('flowUp').textContent=last.up.toFixed(1);document.getElementById('flowDown').textContent=last.down.toFixed(1);}
  },2000);
  function fetchComms(){fetch('/api/v1/comms/link-status').then(r=>r.json()).then(d=>{const links=d.links||[];const commLinks=document.querySelectorAll('.comm-link');links.forEach((l,i)=>{if(commLinks[i]){const dot=commLinks[i].querySelector('.comm-dot');if(dot)dot.className='comm-dot '+(l.status==='online'?'online':l.status==='degraded'?'degraded':'offline');}});}).catch(()=>{});}
  function fetchCmds(){fetch('/api/v1/fleet/command-history').then(r=>r.json()).then(d=>{const tbody=document.getElementById('cmdBody');if(!tbody||!d.commands)return;tbody.innerHTML='';d.commands.slice(0,6).forEach(c=>{const time=c.time?new Date(c.time).toLocaleTimeString('zh-CN',{hour:'2-digit',minute:'2-digit'}):'';tbody.innerHTML+=`<tr><td>${time}</td><td>${(c.from||'').replace(/</g,'&lt;')}</td><td>${(c.command||'').replace(/</g,'&lt;')}</td><td><span class="badge-s badge-ok">已执行</span></td></tr>`;});}).catch(()=>{});}
  fetchComms();fetchCmds();setInterval(fetchComms,10000);setInterval(fetchCmds,30000);
  (function(){let ws;function cn(){try{ws=new WebSocket('ws://'+location.host+'/ws/shore');ws.onclose=()=>setTimeout(cn,5000);ws.onerror=()=>ws.close();}catch(e){setTimeout(cn,5000);}}cn();})();
  </script>
  <script src="/js/i18n.js"></script>
  <script src="/js/nav-sidebar.js" data-active="shore"></script>
  </body>
  </html>
  
  ```
  
  ### 文件: `src/frontend/ship-shore.v1.bak.html`
  ```html
  <!DOCTYPE html>
  <html lang="zh-CN" data-obc-theme="dusk">
  <head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <meta name="ob-title" content="船岸协同">
  <meta name="ob-subtitle" content="K-Fleet SCC — 船岸一体化通信">
  <title>船岸协同 — PoseidonX</title>
  <link rel="stylesheet" href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css">
  <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>
  <link rel="stylesheet" href="/css/openbridge-theme.css">
  <style>
  :root{--sh-glass:rgba(24,28,36,.72);--sh-border:oklch(1 0 0 / .08);--sh-cyan:oklch(0.52 0.04 160);--sh-ok:oklch(0.52 0.04 160);--sh-warn:oklch(0.56 0.05 70);--sh-alarm:oklch(0.48 0.07 22);--sh-blue:oklch(0.52 0.04 160);}
  *{box-sizing:border-box}
  body{margin:0;padding:var(--ob-topbar-height,48px) 0 0 64px;background:var(--ob-bg-global);color:var(--ob-text-primary);font-family:var(--ob-font,system-ui,sans-serif);overflow:hidden}
  .shore-layout{display:grid;grid-template-columns:1fr 380px;gap:0;height:calc(100vh - var(--ob-topbar-height,48px))}
  #fleetMap{width:100%;height:100%;min-height:400px}
  .shore-sidebar{display:flex;flex-direction:column;gap:12px;padding:14px;overflow-y:auto;background:rgba(0,0,0,.2)}
  .sh-card{background:var(--sh-glass);backdrop-filter:blur(14px);border:1px solid var(--sh-border);border-radius:0;padding:16px}
  .sh-card h5{margin:0 0 12px;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;display:flex;align-items:center;gap:8px}
  .sh-card h5::before{content:'';width:3px;height:12px;border-radius:2px;background:var(--sh-cyan)}
  /* Comm Links */
  .comm-link{display:flex;align-items:center;gap:12px;padding:10px;border-radius:0;background:rgba(0,0,0,.1);border:1px solid var(--sh-border);margin-bottom:8px;transition:all .15s}
  .comm-link:last-child{margin-bottom:0}
  .comm-link:hover{border-color:rgba(34,211,238,.2)}
  .comm-icon{font-size:20px;width:36px;height:36px;display:flex;align-items:center;justify-content:center;border-radius:0;background:oklch(1 0 0 / .04)}
  .comm-info{flex:1}
  .comm-info .name{font-size:12px;font-weight:600}
  .comm-info .signal{font-size:10px;color:var(--ob-text-tertiary);margin-top:2px}
  .comm-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
  .comm-dot.online{background:var(--sh-ok);box-shadow:0 0 6px rgba(74,222,128,.4)}
  .comm-dot.degraded{background:var(--sh-warn);box-shadow:0 0 6px oklch(0.56 0.05 70 / .3)}
  .comm-dot.offline{background:var(--sh-alarm)}
  /* Data Flow */
  .flow-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
  .flow-item{text-align:center;padding:12px;background:rgba(0,0,0,.1);border-radius:0;border:1px solid var(--sh-border)}
  .flow-item .v{font-size:20px;font-weight:700;color:var(--sh-cyan)}
  .flow-item .l{font-size:10px;color:var(--ob-text-tertiary);margin-top:2px}
  /* Bandwidth Canvas */
  .bw-canvas{width:100%;height:60px;display:block;margin-top:8px}
  /* Command History */
  .cmd-table{width:100%;border-collapse:collapse;font-size:11px}
  .cmd-table th{text-align:left;padding:6px 8px;color:var(--ob-text-tertiary);font-weight:600;font-size:10px;text-transform:uppercase;border-bottom:1px solid var(--sh-border)}
  .cmd-table td{padding:6px 8px;border-bottom:1px solid oklch(1 0 0 / .03)}
  .cmd-table tr:hover td{background:oklch(1 0 0 / .03)}
  .badge{display:inline-flex;padding:2px 8px;border-radius:0;font-size:9px;font-weight:600}
  .badge-ok{background:rgba(74,222,128,.12);color:var(--sh-ok);border:1px solid rgba(74,222,128,.2)}
  .badge-warn{background:oklch(0.56 0.05 70 / .12);color:var(--sh-warn);border:1px solid oklch(0.56 0.05 70 / .2)}
  /* Sync Status */
  .sync-items{display:flex;flex-direction:column;gap:8px}
  .sync-item{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:0;background:rgba(0,0,0,.08);font-size:12px}
  .sync-item .v{margin-left:auto;font-weight:600;font-size:11px}
  @keyframes pulse{0%,100%{opacity:.6}50%{opacity:1}}.pulse{animation:pulse 2s infinite}
  </style>
  </head>
  <body>
  <div class="shore-layout">
  <div id="fleetMap"></div>
  <div class="shore-sidebar">
      <!-- Comm Status -->
      <div class="sh-card">
          <h5>📡 通信链路 <span class="pulse" style="font-size:10px;color:var(--sh-cyan);margin-left:auto">● 在线</span></h5>
          <div class="comm-link"><div class="comm-icon">🛰️</div><div class="comm-info"><div class="name">VSAT Ku-Band</div><div class="signal">-62 dBm | 12 Mbps</div></div><div class="comm-dot online"></div></div>
          <div class="comm-link"><div class="comm-icon">📶</div><div class="comm-info"><div class="name">4G/LTE (沿海)</div><div class="signal">-78 dBm | 50 Mbps</div></div><div class="comm-dot online"></div></div>
          <div class="comm-link"><div class="comm-icon">🌐</div><div class="comm-info"><div class="name">Iridium NEXT</div><div class="signal">-94 dBm | 704 kbps</div></div><div class="comm-dot degraded"></div></div>
          <div class="comm-link"><div class="comm-icon">🚢</div><div class="comm-info"><div class="name">AIS 双频</div><div class="signal">正常 | 2 × VHF</div></div><div class="comm-dot online"></div></div>
          <div class="comm-link"><div class="comm-icon">📻</div><div class="comm-info"><div class="name">GMDSS / DSC</div><div class="signal">VHF Ch70 | MF/HF</div></div><div class="comm-dot online"></div></div>
      </div>
      <!-- Data Flow -->
      <div class="sh-card">
          <h5>📊 远程数据流</h5>
          <div class="flow-grid">
              <div class="flow-item"><div class="v" id="flowUp">1.2</div><div class="l">上行 Mbps</div></div>
              <div class="flow-item"><div class="v" id="flowDown">4.5</div><div class="l">下行 Mbps</div></div>
              <div class="flow-item"><div class="v" id="flowLat">280</div><div class="l">延迟 ms</div></div>
              <div class="flow-item"><div class="v" style="color:var(--sh-ok)" id="flowSync">OK</div><div class="l">数据同步</div></div>
          </div>
          <canvas id="bwChart" class="bw-canvas" height="60"></canvas>
      </div>
      <!-- Data Sync -->
      <div class="sh-card">
          <h5>🔄 数据同步</h5>
          <div class="sync-items">
              <div class="sync-item"><span class="comm-dot online" style="width:8px;height:8px"></span>航行数据 → 岸基<div class="v" style="color:var(--sh-ok)">实时</div></div>
              <div class="sync-item"><span class="comm-dot online" style="width:8px;height:8px"></span>CMS 传感器 → 云存储<div class="v" style="color:var(--sh-ok)">5s</div></div>
              <div class="sync-item"><span class="comm-dot degraded" style="width:8px;height:8px"></span>视频监控 → S3<div class="v" style="color:var(--sh-warn)">30s</div></div>
              <div class="sync-item"><span class="comm-dot online" style="width:8px;height:8px"></span>岸基指令 → 船端<div class="v" style="color:var(--sh-ok)">实时</div></div>
          </div>
      </div>
      <!-- Command History -->
      <div class="sh-card">
          <h5>📋 岸基指令历史</h5>
          <table class="cmd-table">
              <thead><tr><th>时间</th><th>来源</th><th>指令</th><th>状态</th></tr></thead>
              <tbody id="cmdBody">
                  <tr><td>14:30</td><td>SCC 上海</td><td>航速调整至 12kn</td><td><span class="badge badge-ok">已执行</span></td></tr>
                  <tr><td>12:15</td><td>VTS 宁波</td><td>进港航道确认</td><td><span class="badge badge-ok">已确认</span></td></tr>
                  <tr><td>09:40</td><td>SCC 上海</td><td>台风预警转发</td><td><span class="badge badge-warn">待确认</span></td></tr>
                  <tr><td>08:00</td><td>总部</td><td>CII 优化建议下发</td><td><span class="badge badge-ok">已接收</span></td></tr>
              </tbody>
          </table>
      </div>
  </div>
  </div>
  <script>
  // ═══════════════════════════════════════════════
  //  PoseidonX Ship-Shore — Enhanced
  // ═══════════════════════════════════════════════
  
  // ── Map ──
  const map=new maplibregl.Map({container:'fleetMap',style:{version:8,sources:{'osm':{type:'raster',tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,attribution:'OpenStreetMap'}},layers:[{id:'osm',type:'raster',source:'osm'}]},center:[122,30],zoom:5});
  map.on('load',()=>{
      fetch('/api/v1/fleet/positions').then(r=>r.json()).then(geojson=>{
          map.addSource('fleet',{type:'geojson',data:geojson});
          map.addLayer({id:'fleet-dots',type:'circle',source:'fleet',paint:{'circle-radius':8,'circle-color':['case',['get','is_own'],'oklch(0.48 0.07 22)','oklch(0.52 0.04 160)'],'circle-stroke-width':2,'circle-stroke-color':'oklch(0.96 0.003 110)','circle-opacity':0.9}});
          map.addLayer({id:'fleet-labels',type:'symbol',source:'fleet',layout:{'text-field':['get','name'],'text-offset':[0,1.8],'text-size':12},paint:{'text-color':'oklch(0.96 0.003 110)','text-halo-color':'oklch(0.18 0.008 110)','text-halo-width':1}});
      }).catch(()=>{
          map.addSource('fleet',{type:'geojson',data:{type:'FeatureCollection',features:[
              {type:'Feature',geometry:{type:'Point',coordinates:[122.1,30.6]},properties:{name:'PoseidonX-01',is_own:true}},
              {type:'Feature',geometry:{type:'Point',coordinates:[121.5,31.2]},properties:{name:'PoseidonX-02'}},
              {type:'Feature',geometry:{type:'Point',coordinates:[120.8,29.8]},properties:{name:'PoseidonX-03'}}
          ]}});
          map.addLayer({id:'fleet-dots',type:'circle',source:'fleet',paint:{'circle-radius':8,'circle-color':['case',['get','is_own'],'oklch(0.48 0.07 22)','oklch(0.52 0.04 160)'],'circle-stroke-width':2,'circle-stroke-color':'oklch(0.96 0.003 110)'}});
          map.addLayer({id:'fleet-labels',type:'symbol',source:'fleet',layout:{'text-field':['get','name'],'text-offset':[0,1.8],'text-size':12},paint:{'text-color':'oklch(0.96 0.003 110)','text-halo-color':'oklch(0.18 0.008 110)','text-halo-width':1}});
      });
      setInterval(()=>{fetch('/api/v1/fleet/positions').then(r=>r.json()).then(geojson=>{const src=map.getSource('fleet');if(src)src.setData(geojson);}).catch(()=>{});},15000);
  });
  
  // ── Bandwidth History Chart ──
  const bwHistory=[];
  function drawBwChart(){
      const cv=document.getElementById('bwChart'),ctx=cv.getContext('2d');
      const W=cv.width=cv.offsetWidth,H=60;
      ctx.clearRect(0,0,W,H);
      if(bwHistory.length<2)return;
      const max=Math.max(...bwHistory.map(b=>b.up+b.down))*1.3||10;
      // Up area
      ctx.beginPath();bwHistory.forEach((b,i)=>{const x=i/(bwHistory.length-1)*W,y=H-(b.up/max)*H;i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});
      ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.closePath();ctx.fillStyle='rgba(34,211,238,.1)';ctx.fill();
      ctx.beginPath();bwHistory.forEach((b,i)=>{const x=i/(bwHistory.length-1)*W,y=H-(b.up/max)*H;i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});
      ctx.strokeStyle='rgba(34,211,238,.6)';ctx.lineWidth=1.5;ctx.stroke();
      // Down area
      ctx.beginPath();bwHistory.forEach((b,i)=>{const x=i/(bwHistory.length-1)*W,y=H-(b.down/max)*H;i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});
      ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.closePath();ctx.fillStyle='rgba(96,165,250,.08)';ctx.fill();
      ctx.beginPath();bwHistory.forEach((b,i)=>{const x=i/(bwHistory.length-1)*W,y=H-(b.down/max)*H;i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});
      ctx.strokeStyle='rgba(96,165,250,.5)';ctx.lineWidth=1.5;ctx.stroke();
  }
  // Simulated bandwidth data
  setInterval(()=>{
      bwHistory.push({up:1.2+(Math.random()-.5)*.6,down:4.5+(Math.random()-.5)*1.5});
      if(bwHistory.length>60)bwHistory.shift();
      drawBwChart();
      if(bwHistory.length>0){const last=bwHistory[bwHistory.length-1];document.getElementById('flowUp').textContent=last.up.toFixed(1);document.getElementById('flowDown').textContent=last.down.toFixed(1);}
  },2000);
  
  // ── Fetch APIs ──
  function fetchComms(){fetch('/api/v1/comms/link-status').then(r=>r.json()).then(d=>{const links=d.links||[];const commLinks=document.querySelectorAll('.comm-link');links.forEach((l,i)=>{if(commLinks[i]){const dot=commLinks[i].querySelector('.comm-dot');if(dot)dot.className='comm-dot '+(l.status==='online'?'online':l.status==='degraded'?'degraded':'offline');}});}).catch(()=>{});}
  function fetchCmds(){fetch('/api/v1/fleet/command-history').then(r=>r.json()).then(d=>{const tbody=document.getElementById('cmdBody');if(!tbody||!d.commands)return;tbody.innerHTML='';d.commands.slice(0,6).forEach(c=>{const time=c.time?new Date(c.time).toLocaleTimeString('zh-CN',{hour:'2-digit',minute:'2-digit'}):'';tbody.innerHTML+=`<tr><td>${time}</td><td>${c.from||''}</td><td>${c.command||''}</td><td><span class="badge badge-ok">已执行</span></td></tr>`;});}).catch(()=>{});}
  fetchComms();fetchCmds();
  setInterval(fetchComms,10000);setInterval(fetchCmds,30000);
  
  // ── WebSocket ──
  (function(){let ws;function cn(){try{ws=new WebSocket('ws://'+location.host+'/ws/shore');ws.onclose=()=>setTimeout(cn,5000);ws.onerror=()=>ws.close();}catch(e){setTimeout(cn,5000);}}cn();})();
  </script>
  <script src="/js/nav-sidebar.js" data-active="shore"></script>
  </body>
  </html>
  
  ```
  
  ### 文件: `src/frontend/js/i18n.js`
  ```js
  /**
   * PoseidonX — i18n Internationalization Module v2
   * DOM text-walker approach: walks all text nodes and replaces Chinese↔English.
   * Usage: <script src="/js/i18n.js"></script>
   * Pages can extend via: PX_I18N.addTexts({ '中文': 'English', ... })
   */
  (function () {
    'use strict';
  
    const LANGS = ['zh', 'en'];
    const STORAGE_KEY = 'px-lang';
  
    /* ── Shared text map: zh → en ── */
    const TEXT_MAP = new Map([
      // ─── Index / Home page ───
      ['深海远洋双体船舶智能综合信息系统', 'Deep-Sea Ocean-Going Catamaran Intelligent Information System'],
      ['船长中控台', 'Captain Cockpit'],
      ['智能导航', 'Smart Navigation'],
      ['数据中心孪生', 'DC Digital Twin'],
      ['态势感知', 'Situation Awareness'],
      ['船岸通信', 'Ship-Shore Link'],
      ['气象海况', 'Weather & Sea'],
      ['海上作业', 'Offshore Operations'],
      ['进入系统', 'Enter System'],
  
      // ─── Page titles ───
      ['船长智能中控台', 'Captain Cockpit'],
      ['船长驾驶舱', 'Captain Cockpit'],
      ['导航与操纵', 'Navigation & Maneuvering'],
      ['动力定位', 'DP Control'],
      ['推进控制', 'Thruster Control'],
      ['全船监控', 'Full Ship Monitor'],
      ['设备健康', 'CMS Health'],
      ['控制台', 'HMI Console'],
      ['海工特种作业', 'Offshore Operations'],
      ['海工特種作业', 'Offshore Operations'],
      ['气象海洋', 'Weather & Ocean'],
      ['船员管理', 'Crew Management'],
      ['仿真训练', 'Simulation & Training'],
      ['能效合规', 'Energy Compliance'],
      ['船载数据中心', 'Marine Datacenter'],
      ['安全应急', 'Safety & Emergency'],
      ['船岸协同', 'Ship-Shore Sync'],
      ['数字孪生', 'Digital Twin'],
      ['智能体', 'AI Agents'],
      ['系统自我演进', 'System Self-Evolution'],
      ['系统演进', 'System Evolution'],
      ['知识库', 'Knowledge Base'],
      ['系统配置', 'System Configuration'],
      ['全球船舶监控平台', 'Global Ship Monitoring'],
      ['船舶避免碰撞增强现实系统', 'Ship Collision Avoidance AR System'],
  
      // ─── Nav sidebar ───
      ['船长总览', 'Captain'],
      ['导航', 'Navigation'],
      ['全船监控', 'Monitor'],
      ['海工作业', 'Offshore Ops'],
      ['船员管理', 'Crew Mgmt'],
  
      // ─── Common status / UI ───
      ['正常', 'Normal'],
      ['报警', 'Alarm'],
      ['警告', 'Warning'],
      ['离线', 'Offline'],
      ['在线', 'Online'],
      ['已连接', 'Connected'],
      ['待命', 'Standby'],
      ['就绪', 'Ready'],
      ['待确认', 'Pending'],
      ['已执行', 'Executed'],
      ['已确认', 'Confirmed'],
      ['已接收', 'Received'],
      ['已批准', 'Approved'],
      ['已提交', 'Submitted'],
      ['有效', 'Valid'],
      ['即将到期', 'Expiring Soon'],
      ['检修中', 'Under Maintenance'],
      ['加载中', 'Loading'],
      ['初始化中', 'Initializing'],
      ['搜索', 'Search'],
      ['保存', 'Save'],
      ['取消', 'Cancel'],
      ['确认', 'Confirm'],
      ['关闭', 'Close'],
      ['刷新', 'Refresh'],
      ['导出', 'Export'],
      ['状态', 'Status'],
      ['设置', 'Settings'],
      ['提交', 'Submit'],
      ['返回', 'Back'],
      ['折叠', 'Collapse'],
      ['全屏', 'Fullscreen'],
      ['隐藏', 'Hide'],
      ['开始', 'Start'],
      ['暂停', 'Pause'],
      ['重置', 'Reset'],
      ['清空', 'Clear'],
      ['添加', 'Add'],
      ['保存配置', 'Save Config'],
      ['刷新全部', 'Refresh All'],
  
      // ─── Captain cockpit ───
      ['快捷指令', 'Quick Commands'],
      ['拋錨', 'Drop Anchor'],
      ['抛锚', 'Drop Anchor'],
      ['响笛', 'Sound Horn'],
      ['紧急停车', 'Emergency Stop'],
      ['信号灯', 'Signal Light'],
      ['信号燈', 'Signal Light'],
      ['航行日志', 'Navigation Log'],
      ['航行日誌', 'Navigation Log'],
      ['系统设置', 'System Settings'],
      ['性能报告', 'Performance Report'],
      ['气象更新', 'Weather Update'],
      ['操作日志', 'Operation Log'],
      ['操作日誌', 'Operation Log'],
      ['操作人', 'Operator'],
      ['事件', 'Event'],
      ['结果', 'Result'],
      ['完成', 'Complete'],
      ['大副', 'Chief Officer'],
      ['轮机长', 'Chief Engineer'],
      ['船长', 'Captain'],
      ['调整航向', 'Adjust Heading'],
      ['主机转速', 'M/E RPM'],
      ['确认航线', 'Confirm Route'],
      ['您好', 'Hello'],
      ['当前航行状态如何', 'Current navigation status?'],
      ['当前航速', 'Current Speed'],
      ['航向', 'Heading'],
      ['主机功率', 'M/E Power'],
      ['子系统全部在线', 'All subsystems online'],
      ['抵达下一航路点', 'ETA next waypoint'],
      ['首页', 'Home'],
      ['中控台', 'Control Center'],
      ['广播', 'Broadcast'],
  
      // ─── Safety & Emergency ───
      ['消防区域矩阵', 'Fire Zone Matrix'],
      ['救生设备清单', 'Life Saving Equipment'],
      ['应急预案', 'Emergency Plans'],
      ['集合站点', 'Muster Stations'],
      ['正常区域', 'Normal Zones'],
      ['注意区域', 'Caution Zones'],
      ['报警区域', 'Alarm Zones'],
      ['救生设备', 'Life Saving Equip.'],
      ['预案就绪', 'Plans Ready'],
      ['设备', 'Equipment'],
      ['数量', 'Qty'],
      ['容量', 'Capacity'],
      ['检验日期', 'Inspection Date'],
      ['救生艇', 'Lifeboat'],
      ['救生筏', 'Life Raft'],
      ['救生圈', 'Life Buoy'],
      ['救生衣', 'Life Jacket'],
      ['发光', 'Illuminated'],
      ['烟雾', 'Smoke Signal'],
      ['火灾', 'Fire'],
      ['弃船', 'Abandon Ship'],
      ['人落水', 'Man Overboard'],
      ['碰撞', 'Collision'],
      ['搁浅', 'Grounding'],
      ['进水', 'Flooding'],
      ['污染', 'Pollution'],
      ['医疗', 'Medical'],
      ['机舱', 'Engine Room'],
      ['货舱', 'Cargo Hold'],
      ['住舱', 'Accommodation'],
      ['驾驶', 'Bridge'],
      ['甲板', 'Deck'],
      ['左舷甲板', 'Port Deck'],
      ['右舷甲板', 'Starboard Deck'],
      ['驾驶台', 'Bridge'],
      ['机舱控制室', 'Engine Control Room'],
      ['人已到', 'Arrived'],
  
      // ─── Ship-Shore ───
      ['通信链路', 'Communication Links'],
      ['数据同步', 'Data Sync'],
      ['岸基指令历史', 'Shore Command History'],
      ['远程数据流', 'Remote Data Flow'],
      ['上行', 'Uplink'],
      ['下行', 'Downlink'],
      ['延迟', 'Latency'],
      ['航行数据', 'Navigation Data'],
      ['实时', 'Real-time'],
      ['岸基', 'Shore'],
      ['云存储', 'Cloud Storage'],
      ['云存儲', 'Cloud Storage'],
      ['视频监控', 'Video Monitor'],
      ['視频监控', 'Video Monitor'],
      ['岸基指令', 'Shore Command'],
      ['船端', 'Ship-side'],
      ['时间', 'Time'],
      ['来源', 'Source'],
      ['指令', 'Command'],
      ['航速调整', 'Speed Adjustment'],
      ['进港航道确认', 'Port Channel Confirm'],
      ['台风预警转发', 'Typhoon Alert Forward'],
      ['优化建议下发', 'Optimization Advice'],
      ['沿海', 'Coastal'],
      ['双频', 'Dual Freq'],
  
      // ─── Simulation & Training ───
      ['综合评分', 'Overall Score'],
      ['綜合評分', 'Overall Score'],
      ['训练次数', 'Training Count'],
      ['本月', 'This Month'],
      ['累计时长', 'Total Duration'],
      ['船员排名', 'Crew Ranking'],
      ['场景配置', 'Scenario Config'],
      ['训练场景', 'Training Scenario'],
      ['故障注入', 'Fault Injection'],
      ['训练日志', 'Training Log'],
      ['训练日誌', 'Training Log'],
      ['能力评估雷达图', 'Competency Radar'],
      ['能力評估雷达图', 'Competency Radar'],
      ['成绩详情', 'Score Details'],
      ['成績详情', 'Score Details'],
      ['评分趋势', 'Score Trend'],
      ['評分趨勢', 'Score Trend'],
      ['避碰判断', 'Collision Avoidance'],
      ['导航精度', 'Navigation Accuracy'],
      ['通信规范', 'Communication Standards'],
      ['应急反应', 'Emergency Response'],
      ['操纵技能', 'Maneuvering Skills'],
      ['团队协作', 'Teamwork'],
      ['平均反应时间', 'Avg. Response Time'],
      ['天气', 'Weather'],
      ['海况', 'Sea State'],
      ['交通密度', 'Traffic Density'],
      ['能见度', 'Visibility'],
      ['模拟时间', 'Simulation Time'],
      ['主机故障', 'M/E Failure'],
      ['舵机故障', 'Rudder Lock'],
      ['雷达故障', 'Radar Fail'],
      ['通信中断', 'Comms Down'],
      ['电力丧失', 'Blackout'],
      ['优秀', 'Excellent'],
      ['合格', 'Pass'],
      ['失败', 'Fail'],
      ['晴朗', 'Clear'],
      ['多云', 'Cloudy'],
      ['暴雨', 'Storm'],
      ['台风', 'Typhoon'],
      ['轻浪', 'Slight'],
      ['大浪', 'Rough'],
      ['狂浪', 'Very Rough'],
      ['狂涛', 'High'],
      ['蒲氏风级', 'Beaufort Scale'],
      ['评价', 'Grade'],
      ['右舷让路避让', 'Starboard Give-way'],
      ['雷达标绘', 'Radar Plotting'],
      ['联络确认', 'Communication Confirm'],
      ['狭水道右舷通行', 'Narrow Channel Starboard'],
      ['应急舵切换', 'Emergency Steering Switch'],
      ['追越船避让', 'Overtaking Avoidance'],
      ['避碰', 'COLREG Avoidance'],
      ['分道通航', 'TSS'],
      ['港口进出', 'Port Entry/Exit'],
      ['应急操纵', 'Emergency Maneuvering'],
      ['锚泊作业', 'Anchoring Ops'],
  
      // ─── System Evolution ───
      ['达尔文棘轮', 'Darwin Ratchet'],
      ['自然选择', 'Natural Selection'],
      ['棘轮机制', 'Ratchet Mechanism'],
      ['演进时间线', 'Evolution Timeline'],
      ['初始化棘轮引擎中', 'Initializing Ratchet Engine'],
      ['演进流水线', 'Evolution Pipeline'],
      ['演进操作', 'Evolution Ops'],
      ['演进趋势', 'Evolution Trend'],
      ['域覆盖雷达', 'Domain Radar'],
      ['审查热力图', 'Audit Heatmap'],
      ['合规评级', 'Compliance Rating'],
      ['合规区域', 'Compliance Zones'],
      ['升级仪表板', 'Upgrade Dashboard'],
      ['双重检查单', 'Double Checklist'],
      ['公司级', 'Company Level'],
      ['船舶级', 'Vessel Level'],
      ['审计轨迹', 'Audit Trail'],
      ['审查规则库', 'Audit Rules'],
      ['演进条目', 'Evolution Entries'],
      ['审查历史', 'Audit History'],
      ['运行审查', 'Runtime Audit'],
      ['派发', 'Dispatch'],
      ['验证', 'Verify'],
      ['完整周期', 'Full Cycle'],
      ['已锁定的演化特性只增不减', 'Locked traits only grow, never regress'],
      ['永不回退', 'Never Rollback'],
      ['系统自我演进引擎就绪', 'Self-Evolution Engine Ready'],
      ['正在加载演进数据', 'Loading evolution data'],
      ['活跃', 'Active'],
  
      // ─── Thruster Control ───
      ['机舱综合状态', 'Engine Room Overview'],
      ['机舱綜合狀态', 'Engine Room Overview'],
      ['功率趋势', 'Power Trend'],
      ['功率趨勢', 'Power Trend'],
      ['振动频谱', 'Vibration Spectrum'],
      ['振动频譜', 'Vibration Spectrum'],
      ['缸温分布', 'Cylinder Temp Distribution'],
      ['缸溫分布', 'Cylinder Temp Distribution'],
      ['燃油流量', 'Fuel Flow'],
      ['能效指标', 'Efficiency Indicators'],
      ['额定', 'Rated'],
      ['负荷', 'Load'],
      ['燃油压力', 'Fuel Pressure'],
      ['排气温度', 'Exhaust Temp'],
      ['振动水平', 'Vibration Level'],
      ['舱底水位', 'Bilge Water Level'],
      ['推进效率', 'Propulsion Efficiency'],
      ['总运行时', 'Total Runtime'],
      ['下次保养', 'Next Maintenance'],
      ['高级控制', 'Advanced Control'],
      ['限值', 'Limit'],
      ['滑油温度', 'Lube Oil Temp'],
      ['冷却水温', 'Cooling Water Temp'],
      ['车钟', 'Telegraph'],
      ['车鐘', 'Telegraph'],
  
      // ─── Weather & Ocean ───
      ['风场', 'Wind Field'],
      ['風场', 'Wind Field'],
      ['海浪谱', 'Wave Spectrum'],
      ['海浪譜', 'Wave Spectrum'],
      ['海况综合', 'Sea Conditions'],
      ['海況綜合', 'Sea Conditions'],
      ['道格拉斯海况', 'Douglas Sea State'],
      ['蒲福风级', 'Beaufort Scale'],
      ['气温', 'Air Temp'],
      ['水温', 'Water Temp'],
      ['气压', 'Pressure'],
      ['湿度', 'Humidity'],
      ['洋流', 'Current'],
      ['涌浪', 'Swell'],
      ['表面流速', 'Surface Current Speed'],
      ['流向', 'Current Direction'],
      ['涌浪评估', 'Swell Assessment'],
      ['适航', 'Seaworthy'],
      ['潮汐', 'Tide'],
      ['当前潮高', 'Current Tide Height'],
      ['气象预警', 'Weather Warning'],
      ['大风蓝色预警', 'Blue Gale Warning'],
      ['天气窗口', 'Weather Window'],
      ['可作业', 'Operable'],
      ['航线天气评估', 'Route Weather Assessment'],
      ['良好', 'Good'],
      ['预报', 'Forecast'],
      ['方向', 'Direction'],
      ['风速', 'Wind Speed'],
      ['风向', 'Wind Dir'],
      ['浪高', 'Wave Height'],
  
      // ─── Offshore Operations ───
      ['作业状态', 'Operation Status'],
      ['作业狀态', 'Operation Status'],
      ['作业类型', 'Operation Type'],
      ['起重吊装', 'Crane Lifting'],
      ['许可状态', 'Permit Status'],
      ['許可狀态', 'Permit Status'],
      ['作业区域', 'Work Zone'],
      ['客户', 'Client'],
      ['起重机状态', 'Crane Status'],
      ['起重机狀态', 'Crane Status'],
      ['臂仰角', 'Boom Angle'],
      ['回转角', 'Slew Angle'],
      ['吃钩高度', 'Hook Height'],
      ['吃鉤高度', 'Hook Height'],
      ['环境条件', 'Environment Conditions'],
      ['环境條件', 'Environment Conditions'],
      ['作业限制', 'Op. Limits'],
      ['未超限', 'Within Limits'],
      ['安全检查单', 'Safety Checklist'],
      ['安全检查單', 'Safety Checklist'],
      ['系统状态确认', 'System Status Confirmed'],
      ['系统狀态确认', 'System Status Confirmed'],
      ['通信链路测试', 'Comms Link Test'],
      ['通信链路测試', 'Comms Link Test'],
      ['人员就位确认', 'Personnel Positioned'],
      ['气象窗口核实', 'Weather Window Verified'],
      ['应急预案就绪', 'Emergency Plan Ready'],
      ['应急预案就緒', 'Emergency Plan Ready'],
      ['吊具检验合格', 'Rigging Inspection Pass'],
      ['吊具检驗合格', 'Rigging Inspection Pass'],
      ['安全区域清场', 'Safety Zone Cleared'],
      ['平台东南侧', 'Platform SE Side'],
      ['平台東南側', 'Platform SE Side'],
  
      // ─── Crew Management ───
      ['总船员', 'Total Crew'],
      ['当值', 'On Watch'],
      ['休息', 'Off Watch'],
      ['疲劳预警', 'Fatigue Alert'],
      ['疲勞预警', 'Fatigue Alert'],
      ['证书到期', 'Certificate Expiring'],
      ['证書到期', 'Certificate Expiring'],
      ['船员花名册', 'Crew Roster'],
      ['船员花名冊', 'Crew Roster'],
      ['休息时间合规', 'Work/Rest Compliance'],
      ['休息时間合规', 'Work/Rest Compliance'],
      ['疲劳风险', 'Fatigue Risk'],
      ['疲勞風险', 'Fatigue Risk'],
      ['船舶评分', 'Vessel Score'],
      ['高风险人员', 'High Risk Personnel'],
      ['达标', 'Compliant'],
      ['证书监控', 'Certificate Monitor'],
      ['证書监控', 'Certificate Monitor'],
      ['应急演练记录', 'Emergency Drill Records'],
      ['值班安排', 'Watch Schedule'],
      ['当前班次', 'Current Watch'],
      ['甲班', 'Watch A'],
      ['下次换班', 'Next Changeover'],
      ['大管轮', 'Second Engineer'],
      ['水手长', 'Bosun'],
      ['机工', 'Motorman'],
  
      // ─── Energy Compliance ───
      ['当前', 'Current'],
      ['年度评级', 'Annual Rating'],
      ['年度轨迹', 'Annual Trajectory'],
      ['实时追踪', 'Real-time Tracking'],
      ['月度燃油消耗', 'Monthly Fuel Consumption'],
      ['排放监测', 'Emissions Monitoring'],
      ['二氧化碳', 'CO₂'],
      ['年度申报', 'Annual Declaration'],
      ['硫氧化物', 'SOx'],
      ['氮氧化物', 'NOx'],
      ['颗粒物', 'Particulate Matter'],
      ['合规文档', 'Compliance Documents'],
      ['文档名称', 'Document Name'],
      ['编号', 'Number'],
      ['有效期', 'Validity'],
      ['更新日期', 'Update Date'],
      ['审核机构', 'Audit Authority'],
      ['技术档案', 'Technical File'],
      ['改善方案', 'Improvement Plan'],
      ['国际能效证书', 'International Energy Cert.'],
      ['排放合规声明', 'Emission Compliance Decl.'],
      ['年报', 'Annual Report'],
      ['合规', 'Compliant'],
  
      // ─── Navigation ───
      ['电子海图', 'ECDIS'],
      ['航线路径点', 'Route Waypoints'],
      ['气象数据', 'Weather Data'],
      ['叠加层', 'Overlays'],
      ['目标', 'Targets'],
      ['雷达回波', 'Radar Echo'],
      ['安全等深线', 'Safety Contour'],
      ['追踪', 'Tracking'],
      ['航线进度', 'Route Progress'],
      ['航速', 'Speed'],
  
      // ─── Knowledge Base ───
      ['文档', 'Documents'],
      ['向量', 'Vectors'],
      ['领域', 'Domains'],
      ['領域', 'Domains'],
      ['全部', 'All'],
      ['法规', 'Regulations'],
      ['程序', 'Procedures'],
      ['技术', 'Technical'],
      ['培训', 'Training'],
      ['清单', 'Checklist'],
      ['清單', 'Checklist'],
      ['添加知识文档', 'Add Knowledge Document'],
      ['标题', 'Title'],
      ['标題', 'Title'],
      ['类别', 'Category'],
      ['类別', 'Category'],
      ['标签', 'Tags'],
      ['标籤', 'Tags'],
      ['逗号分隔', 'Comma separated'],
      ['内容', 'Content'],
      ['內容', 'Content'],
  
      // ─── Config page ───
      ['船舶信息', 'Ship Info'],
      ['船名', 'Ship Name'],
      ['船型', 'Ship Type'],
      ['穿浪双体船', 'Wave-Piercing Catamaran'],
      ['集装箱船', 'Container Ship'],
      ['散货船', 'Bulk Carrier'],
      ['油轮', 'Tanker'],
      ['总吨', 'Gross Tonnage'],
      ['功能开关', 'Feature Toggles'],
      ['决策辅助', 'Decision Aid'],
      ['決策輔助', 'Decision Aid'],
      ['启用', 'Enable'],
      ['自动避碰', 'Auto COLREG'],
      ['气象航线优化', 'Weather Route Optimization'],
      ['船员疲劳监控', 'Crew Fatigue Monitor'],
      ['船员疲勞监控', 'Crew Fatigue Monitor'],
      ['闭环审查', 'Closed-loop Audit'],
      ['构建', 'Build'],
      ['数据存储', 'Data Storage'],
      ['数据存儲', 'Data Storage'],
      ['访问控制', 'Access Control'],
      ['认证', 'Authentication'],
      ['端口控制', 'Port Control'],
      ['未授权', 'Unauthorized'],
      ['审查日志', 'Audit Log'],
      ['審查日誌', 'Audit Log'],
      ['记录所有系统配置变更', 'Log all config changes'],
      ['系统运行状态', 'System Runtime Status'],
      ['系统运行狀态', 'System Runtime Status'],
      ['运行时间', 'Uptime'],
      ['使用率', 'Usage'],
      ['内存使用', 'Memory Usage'],
      ['健康', 'Health'],
   
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
            this.components.simulatorEngine,
            this.components.shipController
          );
          
          return {
            success: true,
            message: result.stable ? '船体已稳定' : '稳定化完成，有建议',
            result,
            agent: 'system'
          };
        }
      }
      
      // 其他命令：通过 Poseidon Orchestrator 处理
      const result = await this.poseidonSystem.executeTask(command);
      
      return result;
    }
    
    /**
     * 获取系统状态
     */
    getIntegratedStatus() {
      const poseidonStatus = this.poseidonSystem.getSystemStatus();
      
      return {
        poseidon: poseidonStatus,
        ship: {
          loaded: this.components.shipController?.loaded || false,
          position: this.components.shipController?.body?.position,
          mass: this.components.shipController?.config?.mass
        },
        weather: this.components.weatherSystem?.getWeatherState(),
        physics: {
          algorithms: this.components.simulatorEngine?.getActiveAlgorithms?.() || []
        }
      };
    }
  }
  
  /**
   * 便捷函数：创建完整集成
   */
  export async function createIntegratedPoseidonX(systemComponents) {
    const integration = new PoseidonXIntegration(systemComponents);
    await integration.initialize();
    return integration;
  }
  
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

好的，项目经理。收到任务。

根据您提供的任务描述和项目上下文，我将对“让货船以双体船为圆心动起来 (V2)”这一开发任务进行详细分解和规划。

---

## 任务分解与规划文档

**项目名称:** PoseidonX 数字孪生系统
**任务ID:** TASK-DT-CARGO-ORBIT-V2
**任务名称:** 让货船以双体船为圆心动起来 (V2)
**负责人:** 项目经理 (PM)
**版本:** 1.0
**日期:** 2024-05-24

### 1. 任务概述

**目标:** 在 `src/frontend/digital-twin/main.js` 文件中，实现货船（Cargo Ship）围绕双体船（Catamaran）进行圆周轨道运动的动画逻辑。具体要求为：轨道半径 80 米，角速度 0.015 弧度/帧。最终效果需在刷新前端页面后，货船能够以可见的、连续的圆周轨迹移动。

**核心文件:**
- `src/frontend/digital-twin/main.js` (主要修改文件)
- `src/frontend/digital-twin/PoseidonXIntegration.js` (可能涉及集成逻辑)
- `src/frontend/digital-twin/layer1-interface/DigitalTwinMap.js` (可能涉及3D场景对象管理)

### 2. 任务分解 (WBS)

#### 阶段 1: 需求分析与技术预研 (预估工时: 0.5 小时)

1.  **确认“双体船”与“货船”的3D对象引用:**
    - **目标:** 在 `main.js` 中找到或确认代表“双体船”和“货船”的 Three.js 对象（`Object3D` 或 `Mesh`）。
    - **行动:**
        - 审查 `main.js` 中关于模型加载、场景构建的代码。
        - 搜索 `main.js` 中可能存在的变量名，如 `catamaran`, `cargoShip`, `ship`, `vessel` 等。
        - 检查 `PoseidonXIntegration.js` 中 `shipController` 对象是如何被创建和引用的。
        - 确认 `DigitalTwinMap.js` 中是否管理了这些对象。
    - **风险:** 如果对象引用不明确或未导出，需要先进行代码重构以暴露必要的对象。

2.  **理解现有动画循环:**
    - **目标:** 确定 `main.js` 中负责每帧更新的主循环（通常是 `requestAnimationFrame` 回调函数）。
    - **行动:** 在 `main.js` 中搜索 `animate`, `update`, `render`, `requestAnimationFrame` 等关键词，找到核心的更新逻辑入口。

#### 阶段 2: 核心逻辑开发 (预估工时: 2 小时)

1.  **定义轨道参数:**
    - **目标:** 在 `main.js` 的合适位置（如全局变量区域或动画循环开始前）定义圆周运动的参数。
    - **代码示例:**
        ```javascript
        // 轨道参数
        const ORBIT_RADIUS = 80; // 单位：米
        const ANGULAR_VELOCITY = 0.015; // 单位：弧度/帧
        let currentAngle = 0; // 初始角度
        ```

2.  **实现位置更新逻辑:**
    - **目标:** 在动画循环中，根据当前角度计算货船的新位置，并更新其 `position` 属性。
    - **行动:**
        - 在动画循环中，增加 `currentAngle += ANGULAR_VELOCITY;`。
        - 计算新坐标：
            ```javascript
            const newX = catamaran.position.x + ORBIT_RADIUS * Math.cos(currentAngle);
            const newZ = catamaran.position.z + ORBIT_RADIUS * Math.sin(currentAngle);
            ```
        - 将计算出的坐标赋值给货船对象：
            ```javascript
            cargoShip.position.set(newX, cargoShip.position.y, newZ);
            ```
    - **技术细节:**
        - **坐标系确认:** 需要确认 Three.js 场景的坐标系。通常 Y 轴向上，X 和 Z 轴构成水平面。上述代码假设在 XZ 平面上运动。
        - **对象引用:** 确保 `catamaran` 和 `cargoShip` 变量在当前作用域内是可访问的。
        - **初始位置:** 确保货船在动画开始前被放置在轨道上的一个初始点，例如 `(catamaran.position.x + ORBIT_RADIUS, y, catamaran.position.z)`。

3.  **处理货船朝向:**
    - **目标:** 让货船在运动过程中始终朝向其运动方向（即切线方向），使其看起来更真实。
    - **行动:**
        - 计算货船当前的运动方向向量（切线方向）。
        - 使用 `cargoShip.lookAt()` 方法让货船朝向该方向上的一个点。
        - **代码示例:**
            ```javascript
            // 计算切线方向上的一个点
            const lookAtX = catamaran.position.x + ORBIT_RADIUS * Math.cos(currentAngle + Math.PI / 2);
            const lookAtZ = catamaran.position.z + ORBIT_RADIUS * Math.sin(currentAngle + Math.PI / 2);
            cargoShip.lookAt(lookAtX, cargoShip.position.y, lookAtZ);
            ```

#### 阶段 3: 集成与调试 (预估工时: 1 小时)

1.  **代码集成:**
    - **目标:** 将阶段2开发的代码无缝集成到 `main.js` 的现有结构中。
    - **行动:**
        - 将轨道参数定义放在文件顶部的配置区域。
        - 将位置更新逻辑放在动画循环的合适位置，确保它在渲染之前执行。
        - 注意代码的健壮性，添加对 `catamaran` 和 `cargoShip` 对象是否存在的检查。

2.  **本地验证:**
    - **目标:** 在本地开发环境中运行项目，验证货船是否按预期运动。
    - **行动:**
        - 启动前端开发服务器。
        - 打开浏览器，访问数字孪生页面。
        - 观察货船是否围绕双体船做圆周运动。
        - 检查运动半径和速度是否与参数一致。
        - 检查货船朝向是否正确。

#### 阶段 4: 测试与修复 (预估工时: 0.5 小时)

1.  **边界情况测试:**
    - **目标:** 确保代码在各种情况下都能稳定运行。
    - **测试用例:**
        - 页面刷新后，货船是否立即开始运动。
        - 长时间运行后，角度是否会溢出（`currentAngle` 可以取模 `2 * Math.PI` 来避免）。
        - 如果双体船或货船模型加载失败，代码是否会报错。

2.  **代码审查与提交:**
    - **目标:** 确保代码质量，并提交最终版本。
    - **行动:**
        - 代码格式化，添加必要的注释。
        - 提交 Pull Request 或直接合并到开发分支。

### 3. 技术风险与依赖关系

| 风险/依赖项 | 描述 | 缓解措施 |
| :--- | :--- | :--- |
| **对象引用不明确** | `main.js` 中可能没有直接暴露 `catamaran` 和 `cargoShip` 对象，或者它们被封装在复杂的类结构中。 | 1. 深入阅读 `main.js` 和 `PoseidonXIntegration.js` 的代码。 <br> 2. 如果对象在 `PoseidonXIntegration` 内部，考虑通过 `window` 对象暴露，或修改 `PoseidonXIntegration` 以提供 getter 方法。 <br> 3. 如果对象在 `DigitalTwinMap` 中，需要调用其提供的 API 来获取。 |
| **坐标系不匹配** | Three.js 场景的坐标系可能与预期不同（例如，Y轴为水平轴）。 | 1. 在 Three.js 场景中添加一个辅助的 `AxesHelper` 来可视化坐标系。 <br> 2. 在开发阶段，先让货船沿 X 轴移动，确认方向正确后再改为圆周运动。 |
| **动画循环冲突** | 新的动画逻辑可能与现有的物理引擎或动画系统产生冲突，导致运动卡顿或不自然。 | 1. 将新逻辑放在现有动画循环的末尾，确保它不会干扰物理计算。 <br> 2. 使用 `requestAnimationFrame` 的时间戳 `deltaTime` 来计算角度增量，而不是使用固定的“每帧”增量，使运动速度与帧率无关。 |
| **模型加载异步** | 货船和双体船的 3D 模型可能是异步加载的，在动画开始时可能尚未就绪。 | 1. 在动画循环中添加 `if (catamaran && cargoShip) { ... }` 的条件判断。 <br> 2. 或者，在模型加载完成的回调函数中启动动画。 |

### 4. 开发指导

1.  **入口文件:** 所有修改应集中在 `src/frontend/digital-twin/main.js`。
2.  **代码位置:**
    - **配置区:** 在文件顶部，找到类似 `// Configuration` 或 `// Constants` 的区域，添加轨道参数。
    - **动画循环:** 找到 `function animate()` 或类似的函数，在函数体内，`renderer.render()` 调用之前，添加位置更新逻辑。
3.  **调试技巧:**
    - 使用 `console.log` 输出 `currentAngle` 和货船的位置，以验证计算是否正确。
    - 在浏览器控制台中，可以手动修改 `currentAngle` 或 `ORBIT_RADIUS` 来实时测试效果。
4.  **代码示例 (集成到 `main.js` 的伪代码):**

    ```javascript
    // 在 main.js 的���置区域
    const ORBIT_CONFIG = {
        radius: 80,
        angularVelocity: 0.015,
        currentAngle: 0
    };

    // 在动画循环中
    function animate() {
        requestAnimationFrame(animate);

        // ... 其他更新逻辑（物理、天气等） ...

        // --- 货船轨道运动逻辑 ---
        if (catamaran && cargoShip) {
            // 更新角度
            ORBIT_CONFIG.currentAngle += ORBIT_CONFIG.angularVelocity;
            // 防止角度无限增长
            ORBIT_CONFIG.currentAngle %= (2 * Math.PI);

            // 计算新位置
            const newX = catamaran.position.x + ORBIT_CONFIG.radius * Math.cos(ORBIT_CONFIG.currentAngle);
            const newZ = catamaran.position.z + ORBIT_CONFIG.radius * Math.sin(ORBIT_CONFIG.currentAngle);
            cargoShip.position.set(newX, cargoShip.position.y, newZ);

            // 更新朝向 (朝向运动方向)
            const lookAtX = catamaran.position.x + ORBIT_CONFIG.radius * Math.cos(ORBIT_CONFIG.currentAngle + Math.PI / 2);
            const lookAtZ = catamaran.position.z + ORBIT_CONFIG.radius * Math.sin(ORBIT_CONFIG.currentAngle + Math.PI / 2);
            cargoShip.lookAt(lookAtX, cargoShip.position.y, lookAtZ);
        }
        // --- 结束 ---

        renderer.render(scene, camera);
    }
    ```

### 5. 验收标准

1.  **功能正确:** 刷新页面后，货船围绕双体船做可见的、连续的圆周运动。
2.  **参数准确:** 运动半径约为 80 米，角速度约为 0.015 弧度/帧。
3.  **视觉合理:** 货船在运动过程中，其船头方向应大致指向其运动方向。
4.  **代码健壮:** 代码不会因模型加载延迟或对象不存在而抛出异常。
5.  **性能良好:** 新增逻辑不会对页面帧率造成明显影响。

---

**下一步行动:** 请开发人员根据此文档，从 **阶段1** 开始，对 `main.js` 进行代码审查，确认对象引用和动画循环入口。完成后，进入 **阶段2** 进行核心逻辑开发。

────────────────────────────────────────────────────────────
✅ deepseek-chat 完成
