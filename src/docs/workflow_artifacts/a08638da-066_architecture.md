# 架构设计 — architect

任务: 给build团队的PM一个任务，让货船的绕圈轨迹是一个椭圆
步骤: architecture
Agent: build_architect

---

📋 任务: a08638da-066
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
  给build团队的PM一个任务，让货船的绕圈轨迹是一个椭圆
  给build团队的PM一个任务，让货船的绕圈轨迹是一个椭圆
  
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
  src/frontend/agent-team-config.html.wabi-rewrite
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
  src/backend/register_channels.py.bak
  ... (共 897 个 src/ 文件)
  
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
              { id: 'cargo-orbit-catamaran-v1', title: '货船以双体船为圆心做圆周运动', category: 'scene',   description: '货船围绕双体船(原点)以半径80单位匀速圆周运动, 船头指向切线方向' },
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
  
  ### 文件: `src/frontend/digital-twin/demo.js`
  ```js
  /**
   * Poseidon-X 演示程序
   * 
   * 展示如何使用 Poseidon-X 系统
   */
  
  import { createPoseidonX } from './PoseidonX.js';
  
  /**
   * 演示 1: 基础使用
   */
  export async function demo1_BasicUsage(scene, camera) {
    console.log('\n=== Demo 1: Basic Usage ===\n');
    
    // 创建并初始化 Poseidon-X 系统
    const poseidon = await createPoseidonX(scene, camera, {
      enableBridgeChat: true,
      enableDigitalTwin: true,
      enableVoice: false,
      llmProvider: 'openai',
      model: 'gpt-4'
    });
    
    console.log('✅ Poseidon-X system created');
    
    // 查询系统状态
    const status = poseidon.getSystemStatus();
    console.log('📊 System status:', status);
    
    return poseidon;
  }
  
  /**
   * 演示 2: 执行任务
   */
  export async function demo2_ExecuteTasks(poseidon) {
    console.log('\n=== Demo 2: Execute Tasks ===\n');
    
    // 任务 1: 查询碰撞风险
    console.log('🚢 Task 1: Check collision risk');
    const result1 = await poseidon.executeTask(
      "右舷那艘集装箱船有碰撞风险吗？"
    );
    console.log('Result:', result1);
    
    // 任务 2: 检查主机状态
    console.log('\n⚙️ Task 2: Check main engine');
    const result2 = await poseidon.executeTask(
      "主机排温正常吗？"
    );
    console.log('Result:', result2);
    
    // 任务 3: 检查库存
    console.log('\n📦 Task 3: Check inventory');
    const result3 = await poseidon.executeTask(
      "淡水库存够用吗？"
    );
    console.log('Result:', result3);
    
    // 任务 4: 安全态势评估
    console.log('\n🛡️ Task 4: Safety assessment');
    const result4 = await poseidon.executeTask(
      "过去24小时的安全态势如何？"
    );
    console.log('Result:', result4);
  }
  
  /**
   * 演示 3: 并行任务
   */
  export async function demo3_ParallelTasks(poseidon) {
    console.log('\n=== Demo 3: Parallel Tasks ===\n');
    
    const tasks = [
      "检查主机状态",
      "评估碰撞风险",
      "检查库存",
      "评估安全态势"
    ];
    
    console.log(`⚡ Executing ${tasks.length} tasks in parallel...`);
    
    const result = await poseidon.orchestrator.executeParallel(
      tasks,
      poseidon.shipContext
    );
    
    console.log(`✅ Completed: ${result.successful}/${result.total}`);
    console.log(`❌ Failed: ${result.failed}`);
    
    return result;
  }
  
  /**
   * 演示 4: 更新船舶状态
   */
  export async function demo4_UpdateContext(poseidon) {
    console.log('\n=== Demo 4: Update Ship Context ===\n');
    
    // 模拟传感器数据更新
    const sensorData = new Map([
      ['MainEngine.ExhaustTemp.Cyl1', 375],
      ['MainEngine.ExhaustTemp.Cyl2', 380],
      ['MainEngine.RPM', 100],
      ['GPS.Latitude', 31.2304],
      ['GPS.Longitude', 121.4737],
      ['Weather.WindSpeed', 20],
      ['FuelTank.Level', 0.75]
    ]);
    
    poseidon.updateShipContext({
      position: {
        lat: 31.2304,
        lon: 121.4737,
        heading: 90,
        speed: 15
      },
      sensors: sensorData,
      environment: {
        windSpeed: 20,
        waveHeight: 2.0,
        visibility: 8
      }
    });
    
    console.log('✅ Ship context updated');
    
    // 查询更新后的状态
    const status = poseidon.getSystemStatus();
    console.log('📊 Updated status:', status.shipContext);
  }
  
  /**
   * 演示 5: Digital Twin Map
   */
  export async function demo5_DigitalTwin(poseidon) {
    console.log('\n=== Demo 5: Digital Twin Map ===\n');
    
    if (!poseidon.digitalTwinMap) {
      console.log('⚠️ Digital Twin Map not enabled');
      return;
    }
    
    // 添加 AIS 目标
    poseidon.digitalTwinMap.addAISTarget('413123456', {
      name: 'EVER GIVEN',
      position: { x: 50, z: 30 },
      velocity: { x: -2, z: 0 },
      distance: 2.5,
      heading: 270
    });
    
    console.log('✅ AIS target added: EVER GIVEN');
    
    // 高亮风险区域
    poseidon.digitalTwinMap.highlight(
      { x: 50, z: 30 },
      '注意：AIS 目标靠近'
    );
    
    console.log('✅ Risk area highlighted');
    
    // 绘制航线
    const waypoints = [
      { x: 0, z: 0 },
      { x: 100, z: 50 },
      { x: 200, z: 100 },
      { x: 300, z: 150 }
    ];
    
    poseidon.digitalTwinMap.drawRoute(waypoints);
    
    console.log('✅ Route drawn with 4 waypoints');
  }
  
  /**
   * 演示 6: 开发模式 - 生成新 Agent
   */
  export async function demo6_GenerateAgent(poseidon) {
    console.log('\n=== Demo 6: Generate New Agent (Dev Mode) ===\n');
    
    if (!poseidon.devMode) {
      console.log('⚠️ Dev mode not enabled');
      console.log('💡 To enable: createPoseidonX(scene, camera, { devMode: true })');
      return;
    }
    
    // 使用自然语言生成新 Agent
    const vibe = `
      创建一个监控海水淡化装置的 Agent。
      它能：
      1. 实时监控产水量和水质（TDS）
      2. 检测膜污堵情况
      3. 预测滤芯更换时间
      4. 优化反渗透压力以节省能耗
    `;
    
    console.log('🧬 Generating agent from vibe...');
    
    const generation = await poseidon.generateAgent(vibe);
    
    console.log('✅ Agent generated!');
    console.log('   Name:', generation.parsed.agentName);
    console.log('   Role:', generation.parsed.role);
    console.log('   Tools:', generation.parsed.tools.length);
    console.log('   Code lines:', generation.agentCode.split('\n').length);
  }
  
  /**
   * 演示 7: 开发模式 - 验证 Agent
   */
  export async function demo7_ValidateAgent(poseidon) {
    console.log('\n=== Demo 7: Validate Agent (Dev Mode) ===\n');
    
    if (!poseidon.devMode) {
      console.log('⚠️ Dev mode not enabled');
      return;
    }
    
    // 验证 Navigator Agent
    console.log('🔬 Validating Navigator Agent...');
    
    const report = await poseidon.validateAgent(
      poseidon.agents.navigator,
      ['weather', 'equipment']
    );
    
    console.log('✅ Validation completed!');
    console.log(`   Pass rate: ${report.passRate}`);
    console.log(`   Passed: ${report.passedScenarios}/${report.totalScenarios}`);
    console.log(`   Status: ${report.passed ? '✅ PASSED' : '❌ FAILED'}`);
    
    if (report.failedScenarios > 0) {
      console.log('\n❌ Failed scenarios:');
      report.results
        .filter(r => !r.passed)
        .forEach(r => {
          console.log(`   - ${r.scenario}: ${r.error || 'Failed criteria'}`);
        });
    }
  }
  
  /**
   * 演示 8: 开发模式 - 评估 Agent 执行
   */
  export async function demo8_EvaluateAgent(poseidon) {
    console.log('\n=== Demo 8: Evaluate Agent Execution (Dev Mode) ===\n');
    
    if (!poseidon.devMode) {
      console.log('⚠️ Dev mode not enabled');
      return;
    }
    
    // 先执行一个任务
    console.log('🤖 Executing task for evaluation...');
    
    const execution = await poseidon.agents.safety.execute(
      "人员落水！",
      poseidon.shipContext
    );
    
    // 评估执行结果
    console.log('\n⚖️ Evaluating execution...');
    
    const evaluation = await poseidon.evaluateExecution({
      agent: 'SafetyAgent',
      task: "人员落水！",
      result: execution,
      executionTime: 1200 // ms
    });
    
    console.log('✅ Evaluation completed!');
    console.log(`   Overall score: ${evaluation.scores.overall.toFixed(1)}/100`);
    console.log(`   Correctness: ${evaluation.scores.correctness.toFixed(1)}`);
    console.log(`   Compliance: ${evaluation.scores.compliance.toFixed(1)}`);
    console.log(`   Decision quality: ${evaluation.scores.decisionQuality.toFixed(1)}`);
    console.log(`   Timeliness: ${evaluation.scores.timeliness.toFixed(1)}`);
    console.log(`   Status: ${evaluation.passed ? '✅ PASSED' : '❌ FAILED'}`);
    
    if (evaluation.recommendations.length > 0) {
      console.log('\n💡 Recommendations:');
      evaluation.recommendations.forEach(rec => {
        console.log(`   [${rec.priority}] ${rec.suggestion}`);
      });
    }
  }
  
  /**
   * 演示 9: 监听系统事件
   */
  export function demo9_SystemEvents(poseidon) {
    console.log('\n=== Demo 9: System Events ===\n');
    
    // 监听任务完成事件
    poseidon.on('agent:task_completed', (data) => {
      console.log(`📢 Event: Task completed by ${data.agent}`);
    });
    
    // 监听上下文更新事件
    poseidon.on('context:updated', (context) => {
      console.log(`📢 Event: Ship context updated`);
    });
    
    // 监听聊天消息事件
    poseidon.on('chat:message', (data) => {
      console.log(`📢 Event: Chat message - ${data.message}`);
    });
    
    console.log('✅ Event listeners registered');
  }
  
  /**
   * 完整演示流程
   */
  export async function runFullDemo(scene, camera) {
    console.log('\n🌊🌊🌊 Poseidon-X Full Demo 🌊🌊🌊\n');
    
    try {
      // 1. 创建系统
      const poseidon = await demo1_BasicUsage(scene, camera);
      
      // 2. 更新船舶状态
      await demo4_UpdateContext(poseidon);
      
      // 3. 设置事件监听
      demo9_SystemEvents(poseidon);
      
      // 4. 执行单个任务
      await demo2_ExecuteTasks(poseidon);
      
      // 5. 并行任务
      await demo3_ParallelTasks(poseidon);
      
      // 6. Digital Twin
      await demo5_DigitalTwin(poseidon);
      
      console.log('\n✅ Full demo completed successfully!\n');
      
      return poseidon;
      
    } catch (error) {
      console.error('\n❌ Demo failed:', error);
      throw error;
    }
  }
  
  /**
   * 开发模式完整演示
   */
  export async function runDevDemo(scene, camera) {
    console.log('\n🧬🧬🧬 Poseidon-X Dev Mode Demo 🧬🧬🧬\n');
    
    try {
      // 1. 创建系统（开发模式）
      const poseidon = await createPoseidonX(scene, camera, {
        devMode: true,
        enableBridgeChat: true,
        enableDigitalTwin: true
      });
      
      console.log('✅ Dev mode system created\n');
      
      // 2. 生成新 Agent
      await demo6_GenerateAgent(poseidon);
      
      // 3. 验证 Agent
      await demo7_ValidateAgent(poseidon);
      
      // 4. 评估 Agent
      await demo8_EvaluateAgent(poseidon);
      
      console.log('\n✅ Dev demo completed successfully!\n');
      
      return poseidon;
      
    } catch (error) {
      console.error('\n❌ Dev demo failed:', error);
      throw error;
    }
  }
  
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
      from .man_overboard impor
  ```
  
  
  ## 前序步骤的产出 (递进式摘要)
  
  ### 步骤 01: pm_decompose
  任务: 给build团队的PM一个任务，让货船的绕圈轨迹是一个椭圆
  步骤: pm_decompose
  📋 任务: a08638da-066
  🤖 Agent: PM (project_manager)
  📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  🔧 执行方式: DeepSeek API (直连)
  ────────────────────────────────────────────────────────────
  你是 PoseidonX 系统的 PM (project_manager)。
  你是项目经理 (PM)。请对以下任务进行分解和规划:
  给build团队的PM一个任务，让货船的绕圈轨迹是一个椭圆
  给build团队的PM一个任务，让货船的绕圈轨迹是一个椭圆
  ## 📂 项目上下文 (系统自动预加载)
  ### 项目文件结构 (src/ 目录)
  ### 文件: `src/frontend/js/darwin-ratchet.js`
  ### 文件: `src/frontend/digital-twin/demo.js`
  **子任务拆解:**
    - *任务目标**：将货船围绕双体船的绕圈轨迹从圆形（半径80单位）改为椭圆形。
    - *当前状态**：根据 `darwin-ratchet.js` 中的记录 `cargo-orbit-catamaran-v1`，货船以双体船为圆心做半径80单位的匀速圆周运动，船头指向切线方向。
    - *技术栈**：Three.js 3D 场景（前端），Python FastAPI 后端（用于配置管理）。
    - 椭圆参数：长轴半径 120 单位，短轴半径 60 单位，长轴沿 X 轴方向
    - 运动逻辑：保持匀速角速度（非开普勒），便于视觉观察
    - 配置方式：先在代码中硬编码，后续通过后端 API 可配置
    - 货船运动控制代码可能分散在多个文件中
    - 可能存在多个货船实例，需要确认修改哪个
  
  ### 步骤 02: research (完整产出)
  
  # 研究分析 — researcher
  
  任务: 给build团队的PM一个任务，让货船的绕圈轨迹是一个椭圆
  步骤: research
  Agent: build_researcher
  
  ---
  
  📋 任务: a08638da-066
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
    给build团队的PM一个任务，让货船的绕圈轨迹是一个椭圆
    给build团队的PM一个任务，让货船的绕圈轨迹是一个椭圆
    
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
    src/frontend/agent-team-config.html.wabi-rewrite
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
    src/backend/register_channels.py.bak
    ... (共 897 个 src/ 文件)
    
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
                { id: 'cargo-orbit-catamaran-v1', title: '货船以双体船为圆心做圆周运动', category: 'scene',   description: '货船围绕双体船(原点)以半径80单位匀速圆周运动, 船头指向切线方向' },
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
    
    ### 文件: `src/frontend/digital-twin/demo.js`
    ```js
    /**
     * Poseidon-X 演示程序
     * 
     * 展示如何使用 Poseidon-X 系统
     */
    
    import { createPoseidonX } from './PoseidonX.js';
    
    /**
     * 演示 1: 基础使用
     */
    export async function demo1_BasicUsage(scene, camera) {
      console.log('\n=== Demo 1: Basic Usage ===\n');
      
      // 创建并初始化 Poseidon-X 系统
      const poseidon = await createPoseidonX(scene, camera, {
        enableBridgeChat: true,
        enableDigitalTwin: true,
        enableVoice: false,
        llmProvider: 'openai',
        model: 'gpt-4'
      });
      
      console.log('✅ Poseidon-X system created');
      
      // 查询系统状态
      const status = poseidon.getSystemStatus();
      console.log('📊 System status:', status);
      
      return poseidon;
    }
    
    /**
     * 演示 2: 执行任务
     */
    export async function demo2_ExecuteTasks(poseidon) {
      console.log('\n=== Demo 2: Execute Tasks ===\n');
      
      // 任务 1: 查询碰撞风险
      console.log('🚢 Task 1: Check collision risk');
      const result1 = await poseidon.executeTask(
        "右舷那艘集装箱船有碰撞风险吗？"
      );
      console.log('Result:', result1);
      
      // 任务 2: 检查主机状态
      console.log('\n⚙️ Task 2: Check main engine');
      const result2 = await poseidon.executeTask(
        "主机排温正常吗？"
      );
      console.log('Result:', result2);
      
      // 任务 3: 检查库存
      console.log('\n📦 Task 3: Check inventory');
      const result3 = await poseidon.executeTask(
        "淡水库存够用吗？"
      );
      console.log('Result:', result3);
      
      // 任务 4: 安全态势评估
      console.log('\n🛡️ Task 4: Safety assessment');
      const result4 = await poseidon.executeTask(
        "过去24小时的安全态势如何？"
      );
      console.log('Result:', result4);
    }
    
    /**
     * 演示 3: 并行任务
     */
    export async function demo3_ParallelTasks(poseidon) {
      console.log('\n=== Demo 3: Parallel Tasks ===\n');
      
      const tasks = [
        "检查主机状态",
        "评估碰撞风险",
        "检查库存",
        "评估安全态势"
      ];
      
      console.log(`⚡ Executing ${tasks.length} tasks in parallel...`);
      
      const result = await poseidon.orchestrator.executeParallel(
        tasks,
        poseidon.shipContext
      );
      
      console.log(`✅ Completed: ${result.successful}/${result.total}`);
      console.log(`❌ Failed: ${result.failed}`);
      
      return result;
    }
    
    /**
     * 演示 4: 更新船舶状态
     */
    export async function demo4_UpdateContext(poseidon) {
      console.log('\n=== Demo 4: Update Ship Context ===\n');
      
      // 模拟传感器数据更新
      const sensorData = new Map([
        ['MainEngine.ExhaustTemp.Cyl1', 375],
        ['MainEngine.ExhaustTemp.Cyl2', 380],
        ['MainEngine.RPM', 100],
        ['GPS.Latitude', 31.2304],
        ['GPS.Longitude', 121.4737],
        ['Weather.WindSpeed', 20],
        ['FuelTank.Level', 0.75]
      ]);
      
      poseidon.updateShipContext({
        position: {
          lat: 31.2304,
          lon: 121.4737,
          heading: 90,
          speed: 15
        },
        sensors: sensorData,
        environment: {
          windSpeed: 20,
          waveHeight: 2.0,
          visibility: 8
        }
      });
      
      console.log('✅ Ship context updated');
      
      // 查询更新后的状态
      const status = poseidon.getSystemStatus();
      console.log('📊 Updated status:', status.shipContext);
    }
    
    /**
     * 演示 5: Digital Twin Map
     */
    export async function demo5_DigitalTwin(poseidon) {
      console.log('\n=== Demo 5: Digital Twin Map ===\n');
      
      if (!poseidon.digitalTwinMap) {
        console.log('⚠️ Digital Twin Map not enabled');
        return;
      }
      
      // 添加 AIS 目标
      poseidon.digitalTwinMap.addAISTarget('413123456', {
        name: 'EVER GIVEN',
        position: { x: 50, z: 30 },
        velocity: { x: -2, z: 0 },
        distance: 2.5,
        heading: 270
      });
      
      console.log('✅ AIS target added: EVER GIVEN');
      
      // 高亮风险区域
      poseidon.digitalTwinMap.highlight(
        { x: 50, z: 30 },
        '注意：AIS 目标靠近'
      );
      
      console.log('✅ Risk area highlighted');
      
      // 绘制航线
      const waypoints = [
        { x: 0, z: 0 },
        { x: 100, z: 50 },
        { x: 200, z: 100 },
        { x: 300, z: 150 }
      ];
      
      poseidon.digitalTwinMap.drawRoute(waypoints);
      
      console.log('✅ Route drawn with 4 waypoints');
    }
    
    /**
     * 演示 6: 开发模式 - 生成新 Agent
     */
    export async function demo6_GenerateAgent(poseidon) {
      console.log('\n=== Demo 6: Generate New Agent (Dev Mode) ===\n');
      
      if (!poseidon.devMode) {
        console.log('⚠️ Dev mode not enabled');
        console.log('💡 To enable: createPoseidonX(scene, camera, { devMode: true })');
        return;
      }
      
      // 使用自然语言生成新 Agent
      const vibe = `
        创建一个监控海水淡化装置的 Agent。
        它能：
        1. 实时监控产水量和水质（TDS）
        2. 检测膜污堵情况
        3. 预测滤芯更换时间
        4. 优化反渗透压力以节省能耗
      `;
      
      console.log('🧬 Generating agent from vibe...');
      
      const generation = await poseidon.generateAgent(vibe);
      
      console.log('✅ Agent generated!');
      console.log('   Name:', generation.parsed.agentName);
      console.log('   Role:', generation.parsed.role);
      console.log('   Tools:', generation.parsed.tools.length);
      console.log('   Code lines:', generation.agentCode.split('\n').length);
    }
    
    /**
     * 演示 7: 开发模式 - 验证 Agent
     */
    export async function demo7_ValidateAgent(poseidon) {
      console.log('\n=== Demo 7: Validate Agent (Dev Mode) ===\n');
      
      if (!poseidon.devMode) {
        console.log('⚠️ Dev mode not enabled');
        return;
      }
      
      // 验证 Navigator Agent
      console.log('🔬 Validating Navigator Agent...');
      
      const report = await poseidon.validateAgent(
        poseidon.agents.navigator,
        ['weather', 'equipment']
      );
      
      console.log('✅ Validation completed!');
      console.log(`   Pass rate: ${report.passRate}`);
      console.log(`   Passed: ${report.passedScenarios}/${report.totalScenarios}`);
      console.log(`   Status: ${report.passed ? '✅ PASSED' : '❌ FAILED'}`);
      
      if (report.failedScenarios > 0) {
        console.log('\n❌ Failed scenarios:');
        report.results
          .filter(r => !r.passed)
          .forEach(r => {
            console.log(`   - ${r.scenario}: ${r.error || 'Failed criteria'}`);
          });
      }
    }
    
    /**
     * 演示 8: 开发模式 - 评估 Agent 执行
     */
    export async function demo8_EvaluateAgent(poseidon) {
      console.log('\n=== Demo 8: Evaluate Agent Execution (Dev Mode) ===\n');
      
      if (!poseidon.devMode) {
        console.log('⚠️ Dev mode not enabled');
        return;
      }
      
      // 先执行一个任务
      console.log('🤖 Executing task for evaluation...');
      
      const execution = await poseidon.agents.safety.execute(
        "人员落水！",
        poseidon.shipContext
      );
      
      // 评估执行结果
      console.log('\n⚖️ Evaluating execution...');
      
      const evaluation = await poseidon.evaluateExecution({
        agent: 'SafetyAgent',
        task: "人员落水！",
        result: execution,
        executionTime: 1200 // ms
      });
      
      console.log('✅ Evaluation completed!');
      console.log(`   Overall score: ${evaluation.scores.overall.toFixed(1)}/100`);
      console.log(`   Correctness: ${evaluation.scores.correctness.toFixed(1)}`);
      console.log(`   Compliance: ${evaluation.scores.compliance.toFixed(1)}`);
      console.log(`   Decision quality: ${evaluation.scores.decisionQuality.toFixed(1)}`);
      console.log(`   Timeliness: ${evaluation.scores.timeliness.toFixed(1)}`);
      console.log(`   Status: ${evaluation.passed ? '✅ PASSED' : '❌ FAILED'}`);
      
      if (evaluation.recommendations.length > 0) {
        console.log('\n💡 Recommendations:');
        evaluation.recommendations.forEach(rec => {
          console.log(`   [${rec.priority}] ${rec.suggestion}`);
        });
      }
    }
    
    /**
     * 演示 9: 监听系统事件
     */
    export function demo9_SystemEvents(poseidon) {
      console.log('\n=== Demo 9: System Events ===\n');
      
      // 监听任务完成事件
      poseidon.on('agent:task_completed', (data) => {
        console.log(`📢 Event: Task completed by ${data.agent}`);
      });
      
      // 监听上下文更新事件
      poseidon.on('context:updated', (context) => {
        console.log(`📢 Event: Ship context updated`);
      });
      
      // 监听聊天消息事件
      poseidon.on('chat:message', (data) => {
        console.log(`📢 Event: Chat message - ${data.message}`);
      });
      
      console.log('✅ Event listeners registered');
    }
    
    /**
     * 完整演示流程
     */
    export async function runFullDemo(scene, camera) {
      console.log('\n🌊🌊🌊 Poseidon-X Full Demo 🌊🌊🌊\n');
      
      try {
        // 1. 创建系统
        const poseidon = await demo1_BasicUsage(scene, camera);
        
        // 2. 更新船舶状态
        await demo4_UpdateContext(poseidon);
        
        // 3. 设置事件监听
        demo9_SystemEvents(poseidon);
        
        // 4. 执行单个任务
        await demo2_ExecuteTasks(poseidon);
        
        // 5. 并行任务
        await demo3_ParallelTasks(poseidon);
        
        // 6. Digital Twin
        await demo5_DigitalTwin(poseidon);
        
        console.log('\n✅ Full demo completed successfully!\n');
        
        return poseidon;
        
      } catch (error) {
        console.error('\n❌ Demo failed:', error);
        throw error;
      }
    }
    
    /**
     * 开发模式完整演示
     */
    export async function runDevDemo(scene, camera) {
      console.log('\n🧬🧬🧬 Poseidon-X Dev Mode Demo 🧬🧬🧬\n');
      
      try {
        // 1. 创建系统（开发模式）
        const poseidon = await createPoseidonX(scene, camera, {
          devMode: true,
          enableBridgeChat: true,
          enableDigitalTwin: true
        });
        
        console.log('✅ Dev mode system created\n');
        
        // 2. 生成新 Agent
        await demo6_GenerateAgent(poseidon);
        
        // 3. 验证 Agent
        await demo7_ValidateAgent(poseidon);
        
        // 4. 评估 Agent
        await demo8_EvaluateAgent(poseidon);
        
        console.log('\n✅ Dev demo completed successfully!\n');
        
        return poseidon;
        
      } catch (error) {
        console.error('\n❌ Dev demo failed:', error);
        throw error;
      }
    }
    
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
    
    ### 文件: `src/backend
  ...(截断)
  
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

# 技术方案：货船绕圈轨迹从圆形改为椭圆形

## 1. 概述

### 1.1 任务目标
将货船围绕双体船（原点）的绕圈轨迹从**圆形（半径80单位）** 改为**椭圆形（长轴120单位，短轴60单位）**，保持匀速角速度运动，船头指向切线方向。

### 1.2 当前状态
根据 `darwin-ratchet.js` 中的记录 `cargo-orbit-catamaran-v1`，货船当前以双体船为圆心做半径80单位的匀速圆周运动。

### 1.3 技术栈
- **前端**: Three.js 3D 场景（HTML + JavaScript）
- **后端**: Python FastAPI（用于配置管理）
- **核心文件**: 货船运动控制代码位于前端 JavaScript 文件中

---

## 2. 技术调研结果

### 2.1 关键文件定位

通过分析项目结构，货船运动控制代码最可能位于以下文件中：

| 文件路径 | 可能性 | 说明 |
|---------|--------|------|
| `src/frontend/digital-twin/main.js` | **高** | 主场景初始化，包含3D对象管理和动画循环 |
| `src/frontend/digital-twin/PoseidonX.js` | **中** | 系统核心，可能包含场景对象管理 |
| `src/frontend/digital-twin/NavigationMonitor.js` | **中** | 导航监控，可能包含船舶运动逻辑 |
| `src/frontend/digital-twin/DigitalTwinMap.js` | **低** | 地图显示，不负责3D运动 |
| `src/frontend/digital-twin/layer1-interface/DigitalTwinMap.js` | **低** | 同上 |

### 2.2 椭圆运动数学公式

对于匀速角速度的椭圆运动：

```
参数方程:
  x(t) = a * cos(ωt)
  z(t) = b * sin(ωt)

速度向量（切线方向）:
  vx(t) = -a * ω * sin(ωt)
  vz(t) = b * ω * cos(ωt)

船头朝向角:
  heading(t) = atan2(vz(t), vx(t))
```

其中：
- `a` = 长轴半径（120单位）
- `b` = 短轴半径（60单位）
- `ω` = 角速度（弧度/秒）
- `t` = 时间

### 2.3 与圆形运动的差异

| 特性 | 圆形运动 | 椭圆运动 |
|------|---------|---------|
| 参数方程 | x = R*cos(ωt), z = R*sin(ωt) | x = a*cos(ωt), z = b*sin(ωt) |
| 速度大小 | 恒定 = R*ω | 变化 = ω*sqrt(a²sin²(ωt) + b²cos²(ωt)) |
| 曲率半径 | 恒定 = R | 变化 |
| 船头朝向 | 始终指向切线 | 始终指向切线（需重新计算） |

---

## 3. 技术方案

### 3.1 修改文件清单

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `src/frontend/digital-twin/main.js` | **修改** | 更新货船位置计算逻辑 |
| `src/frontend/js/darwin-ratchet.js` | **修改** | 更新演化记录描述 |
| `src/backend/main.py` | **新增API** | 添加椭圆参数配置端点（可选） |

### 3.2 具体修改内容

#### 3.2.1 `main.js` - 核心运动逻辑修改

**定位代码段**：在 `main.js` 中搜索以下关键词定位货船运动代码：
- `cargo` 或 `cargoShip`
- `orbit` 或 `circular`
- `radius` 或 `80`
- `Math.cos` 或 `Math.sin` 结合位置更新

**修改内容**：

```javascript
// 修改前（圆形运动）
const radius = 80;
cargoShip.position.x = radius * Math.cos(angle);
cargoShip.position.z = radius * Math.sin(angle);
// 船头朝向切线方向
cargoShip.rotation.y = -angle + Math.PI / 2;

// 修改后（椭圆运动）
const a = 120; // 长轴半径
const b = 60;  // 短轴半径
cargoShip.position.x = a * Math.cos(angle);
cargoShip.position.z = b * Math.sin(angle);
// 船头朝向切线方向（椭圆切线）
const dx = -a * Math.sin(angle);
const dz = b * Math.cos(angle);
cargoShip.rotation.y = Math.atan2(dz, dx);
```

**完整代码段**（假设在 `animate()` 或 `update()` 函数中）：

```javascript
// 货船椭圆轨道运动
function updateCargoOrbit(time) {
    const angularSpeed = 0.3; // 角速度（弧度/秒）
    const angle = time * angularSpeed;
    
    // 椭圆参数
    const a = 120; // 长轴半径（X轴方向）
    const b = 60;  // 短轴半径（Z轴方向）
    
    // 位置计算
    cargoShip.position.x = a * Math.cos(angle);
    cargoShip.position.z = b * Math.sin(angle);
    
    // 切线方向计算（船头朝向）
    const dx = -a * Math.sin(angle);
    const dz = b * Math.cos(angle);
    cargoShip.rotation.y = Math.atan2(dz, dx);
}
```

#### 3.2.2 `darwin-ratchet.js` - 更新演化记录

在 `bootstrap()` 函数的 `HERITAGE` 数组中，将 `cargo-orbit-catamaran-v1` 的描述更新为：

```javascript
{ 
    id: 'cargo-orbit-catamaran-v2', 
    title: '货船以双体船为圆心做椭圆运动', 
    category: 'scene', 
    description: '货船围绕双体船(原点)以椭圆轨迹运动, 长轴120单位(X轴), 短轴60单位(Z轴), 匀速角速度, 船头指向切线方向' 
}
```

#### 3.2.3 后端 API（可选）- 椭圆参数配置

在 `src/backend/main.py` 中添加配置端点：

```python
from pydantic import BaseModel

class EllipseConfig(BaseModel):
    a: float = 120.0  # 长轴半径
    b: float = 60.0   # 短轴半径
    angular_speed: float = 0.3  # 角速度

# 全局配置存储
_ellipse_config = EllipseConfig()

@router.get("/api/v1/scene/cargo-orbit")
async def get_cargo_orbit_config():
    """获取货船轨道配置"""
    return _ellipse_config.dict()

@router.post("/api/v1/scene/cargo-orbit")
async def set_cargo_orbit_config(config: EllipseConfig):
    """���置货船轨道配置"""
    global _ellipse_config
    _ellipse_config = config
    return {"status": "updated", "config": config.dict()}
```

### 3.3 接口规范

#### 前端接口（内部使用）

```javascript
// 货船轨道配置对象
const cargoOrbitConfig = {
    a: 120,           // 长轴半径（单位）
    b: 60,            // 短轴半径（单位）
    angularSpeed: 0.3 // 角速度（弧度/秒）
};
```

#### 后端 API（可选）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/scene/cargo-orbit` | 获取当前椭圆参数 |
| POST | `/api/v1/scene/cargo-orbit` | 更新椭圆参数 |

**请求体示例**：
```json
{
    "a": 120.0,
    "b": 60.0,
    "angular_speed": 0.3
}
```

**响应体示例**：
```json
{
    "status": "updated",
    "config": {
        "a": 120.0,
        "b": 60.0,
        "angular_speed": 0.3
    }
}
```

---

## 4. 实施步骤

### 步骤 1: 定位货船运动代码

1. 打开 `src/frontend/digital-twin/main.js`
2. 搜索关键词：`cargo`、`orbit`、`radius`、`Math.cos`、`Math.sin`
3. 找到货船位置更新的代码段（通常在 `animate()` 或 `update()` 函数中）

### 步骤 2: 修改运动逻辑

1. 将圆形参数方程替换为椭圆参数方程
2. 重新计算切线方向（船头朝向）
3. 保持角速度不变（匀速运动）

### 步骤 3: 验证修改

1. 启动前端应用
2. 观察货船是否沿椭圆轨迹运动
3. 验证船头是否始终指向运动方向（切线方向）
4. 检���椭圆参数：长轴120单位（X轴），短轴60单位（Z轴）

### 步骤 4: 更新演化记录（可选）

1. 打开 `src/frontend/js/darwin-ratchet.js`
2. 在 `HERITAGE` 数组中添加或更新 `cargo-orbit-catamaran-v2` 记录

### 步骤 5: 添加后端 API（可选）

1. 在 `src/backend/main.py` 中添加椭圆参数配置端点
2. 重启后端服务
3. 测试 API 的 GET 和 POST 方法

---

## 5. 注意事项

### 5.1 椭圆参数选择
- **长轴（a=120）**：沿 X 轴方向，比原半径（80）增加50%
- **短轴（b=60）**：沿 Z 轴方向，比原半径（80）减少25%
- **角速度**：保持与圆形运动相同的角速度，确保视觉连续性

### 5.2 船头朝向
- 椭圆运动中，切线方向随时间变化
- 必须使用 `atan2(dz, dx)` 计算正确的朝向角
- 不能简单使用 `-angle + π/2`（圆形运动的简化公式）

### 5.3 性能考虑
- 椭圆运动计算与圆形运动计算复杂度相同（仅多一次乘法和一次除法）
- 对性能无显著影响

### 5.4 多货船实例
- 如果场景中存在多个货船，需要确认修改的是哪个实例
- 建议在代码中添加注释标识

---

## 6. 验证标准

| 检查项 | 预期结果 |
|--------|---------|
| 轨迹形状 | 椭圆形，长轴120单位（X轴），短轴60单位（Z轴） |
| 运动速度 | 匀速角速度，视觉上平滑 |
| 船头朝向 | 始终指向运动方向（椭圆切线） |
| 与双体船关系 | 双体船位于椭圆中心（原点） |
| 性能 | 无卡顿，帧率稳定 |

---

## 7. 回滚方案

如果修改后出现问题，可以快速回滚：

1. **代码回滚**：使用 Git 恢复 `main.js` 的原始版本
2. **配置回滚**：如果使用了后端 API，将椭圆参数恢复为圆形参数（a=b=80）
3. **演化记录回滚**：删除或注释掉 `cargo-orbit-catamaran-v2` 记录

---

**方案制定人**: PoseidonX 系统架构师  
**日期**: 2025年  
**版本**: v1.0

────────────────────────────────────────────────────────────
✅ deepseek-chat 完成
