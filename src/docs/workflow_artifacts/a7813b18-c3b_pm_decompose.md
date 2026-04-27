# PM分解 — project_manager

任务: 让货船以双体船为圆心做圆周运动 V2
步骤: pm_decompose
Agent: build_pm

---

📋 任务: a7813b18-c3b
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
  让货船以双体船为圆心做圆周运动 V2
  在 src/frontend/digital-twin/cargo_orbit.js 新建一个独立模块, 导出 setupCargoOrbit(scene, catamaranObject, options) 函数, 创建一个货船 Mesh 并让它围绕双体船以500米半径、每秒0.5度角速度做圆周运动。不要修改 main.js 或 PoseidonX.js 主文件，只新增一个独立 JS 模块即可。同时新建 src/backend/channels/cargo_orbit_channel.py 提供 CargoOrbitChannel(MarineChannel) 上报当前货船位置 (lat, lon, course, speed)。
  
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
  src/backend/agents/api.py
  ... (共 772 个 src/ 文件)
  
  ```
  
  ### 文件: `src/frontend/digital-twin/MarineEngineeringChannels.js`
  ```js
  /**
   * MarineEngineeringChannels.js - 船舶工程模块 Channel 数据集成
   * 
   * 集成实时 Channel 数据输入（Navigation, Engine, Cargo, Weather），
   * 实现故障诊断与报警联动，添加稳性/浮力参数实时更新，支持人在回路 (HITL) 接口。
   * 
   * @version 1.0.0
   * @date 2026-03-12
   */
  
  class MarineEngineeringChannels {
    /**
     * 创建 MarineEngineeringChannels 实例
     * @param {Object} options - 配置选项
     * @param {PoseidonXChannels} options.poseidonX - PoseidonXChannels 实例
     */
    constructor(options = {}) {
      this.poseidonX = options.poseidonX || null;
  
      // 工程模块数据
      this.navigation = {
        position: null,
        speed: null,
        heading: null,
        depth: null,
        route: null,
      };
  
      this.engine = {
        rpm: null,
        temperature: null,
        oilPressure: null,
        fuelLevel: null,
        load: null,
        status: 'unknown',
      };
  
      this.cargo = {
        tanks: [],
        containers: [],
        stability: null,
        buoyancy: null,
      };
  
      this.weather = {
        windSpeed: null,
        windDirection: null,
        waveHeight: null,
        visibility: null,
        temperature: null,
        pressure: null,
      };
  
      // 报警状态
      this.alarms = [];
      this.alarmListeners = [];
  
      // 故障诊断
      this.diagnostics = {
        engine: { status: 'ok', issues: [] },
        navigation: { status: 'ok', issues: [] },
        cargo: { status: 'ok', issues: [] },
        weather: { status: 'ok', issues: [] },
      };
  
      // 人在回路 (HITL) 回调
      this.hitlCallbacks = new Map();
  
      // 日志
      this.logger = this._createLogger();
  
      // 初始化订阅
      if (this.poseidonX) {
        this._initializeSubscriptions();
      }
    }
  
    /**
     * 创建日志记录器
     * @private
     */
    _createLogger() {
      const prefix = '[MarineEngineeringChannels]';
      return {
        info: (...args) => console.log(prefix, '[INFO]', ...args),
        warn: (...args) => console.warn(prefix, '[WARN]', ...args),
        error: (...args) => console.error(prefix, '[ERROR]', ...args),
        debug: (...args) => console.debug(prefix, '[DEBUG]', ...args),
      };
    }
  
    /**
     * 设置 PoseidonXChannels 实例
     * @param {PoseidonXChannels} poseidonX - PoseidonXChannels 实例
     */
    setPoseidonX(poseidonX) {
      this.poseidonX = poseidonX;
      this._initializeSubscriptions();
      this.logger.info('PoseidonXChannels 已设置');
    }
  
    /**
     * 初始化数据订阅
     * @private
     */
    _initializeSubscriptions() {
      if (!this.poseidonX) {
        return;
      }
  
      // 订阅导航数据
      this.poseidonX.subscribe('navigation_data', (data) => {
        this._updateNavigationData(data);
      });
  
      // 订阅发动机数据
      this.poseidonX.subscribe('engine_monitor', (data) => {
        this._updateEngineData(data);
      });
  
      // 订阅货物数据
      this.poseidonX.subscribe('cargo_monitor', (data) => {
        this._updateCargoData(data);
      });
  
      // 订阅气象数据
      this.poseidonX.subscribe('weather_routing', (data) => {
        this._updateWeatherData(data);
      });
  
      // 订阅 AIS 数据
      this.poseidonX.subscribe('vessel_ais', (data) => {
        this._updateAISData(data);
      });
  
      this.logger.info('Channel 订阅已初始化');
    }
  
    /**
     * 更新导航数据
     * @private
     * @param {Object} data - 导航数据
     */
    _updateNavigationData(data) {
      if (!data) return;
  
      this.navigation = {
        position: data.position || this.navigation.position,
        speed: data.speed_over_ground || data.speed || this.navigation.speed,
        heading: data.heading || this.navigation.heading,
        depth: data.depth || this.navigation.depth,
        route: data.route || this.navigation.route,
        timestamp: data.timestamp || Date.now(),
      };
  
      // 更新稳性/浮力参数
      this._updateStabilityAndBuoyancy();
  
      // 故障诊断
      this._diagnoseNavigation();
    }
  
    /**
     * 更新发动机数据
     * @private
     * @param {Object} data - 发动机数据
     */
    _updateEngineData(data) {
      if (!data) return;
  
      this.engine = {
        rpm: data.rpm || this.engine.rpm,
        temperature: data.temperature || this.engine.temperature,
        oilPressure: data.oil_pressure || this.engine.oilPressure,
        fuelLevel: data.fuel_level || this.engine.fuelLevel,
        load: data.load || this.engine.load,
        status: this._determineEngineStatus(data),
        timestamp: data.timestamp || Date.now(),
      };
  
      // 故障诊断
      this._diagnoseEngine();
    }
  
    /**
     * 确定发动机状态
     * @private
     * @param {Object} data - 发动机数据
     * @returns {string} 发动机状态
     */
    _determineEngineStatus(data) {
      if (data.rpm === 0) return 'stopped';
      if (data.temperature > 95) return 'overheated';
      if (data.oil_pressure < 2) return 'low_oil_pressure';
      if (data.load > 90) return 'high_load';
      return 'running';
    }
  
    /**
     * 更新货物数据
     * @private
     * @param {Object} data - 货物数据
     */
    _updateCargoData(data) {
      if (!data) return;
  
      this.cargo = {
        tanks: data.tanks || this.cargo.tanks,
        containers: data.containers || this.cargo.containers,
        stability: data.stability || this.cargo.stability,
        buoyancy: data.buoyancy || this.cargo.buoyancy,
        timestamp: data.timestamp || Date.now(),
      };
  
      // 更新稳性/浮力参数
      this._updateStabilityAndBuoyancy();
  
      // 故障诊断
      this._diagnoseCargo();
    }
  
    /**
     * 更新气象数据
     * @private
     * @param {Object} data - 气象数据
     */
    _updateWeatherData(data) {
      if (!data) return;
  
      this.weather = {
        windSpeed: data.wind_speed || this.weather.windSpeed,
        windDirection: data.wind_direction || this.weather.windDirection,
        waveHeight: data.wave_height || this.weather.waveHeight,
        visibility: data.visibility || this.weather.visibility,
        temperature: data.temperature || this.weather.temperature,
        pressure: data.pressure || this.weather.pressure,
        timestamp: data.timestamp || Date.now(),
      };
  
      // 故障诊断
      this._diagnoseWeather();
    }
  
    /**
     * 更新 AIS 数据
     * @private
     * @param {Object} data - AIS 数据
     */
    _updateAISData(data) {
      if (!data) return;
  
      // AIS 数据主要用于导航和避碰
      this.navigation.aisTargets = data.targets || [];
      this.navigation.cpa = data.cpa || null;
      this.navigation.tcpa = data.tcpa || null;
  
      // 检查碰撞风险
      this._checkCollisionRisk(data);
    }
  
    /**
     * 更新稳性和浮力参数
     * @private
     */
    _updateStabilityAndBuoyancy() {
      // 计算稳性参数
      const gm = this._calculateGM();
      const kg = this._calculateKG();
      const kb = this._calculateKB();
      const bm = this._calculateBM();
  
      this.cargo.stability = {
        GM: gm, // 初稳性高度
        KG: kg, // 重心高度
        KB: kb, // 浮心高度
        BM: bm, // 稳心半径
        status: this._assessStabilityStatus(gm),
        timestamp: Date.now(),
      };
  
      // 计算浮力参数
      const displacement = this._calculateDisplacement();
      const draft = this._calculateDraft();
      const trim = this._calculateTrim();
  
      this.cargo.buoyancy = {
        displacement, // 排水量
        draft, // 吃水
        trim, // 纵倾
        status: this._assessBuoyancyStatus(draft, trim),
        timestamp: Date.now(),
      };
    }
  
    /**
     * 计算初稳性高度 GM
     * @private
     * @returns {number} GM 值 (米)
     */
    _calculateGM() {
      // 简化计算：GM = KB + BM - KG
      const kb = this._calculateKB();
      const bm = this._calculateBM();
      const kg = this._calculateKG();
      return kb + bm - kg;
    }
  
    /**
     * 计算重心高度 KG
     * @private
     * @returns {number} KG 值 (米)
     */
    _calculateKG() {
      // 基于货物分布计算重心
      if (!this.cargo.tanks || this.cargo.tanks.length === 0) {
        return 5.0; // 默认值
      }
  
      let totalWeight = 0;
      let totalMoment = 0;
  
      this.cargo.tanks.forEach(tank => {
        const weight = tank.volume * (tank.density || 1.0);
        const kg = tank.vcg || 5.0; // 垂直重心
        totalWeight += weight;
        totalMoment += weight * kg;
      });
  
      return totalWeight > 0 ? totalMoment / totalWeight : 5.0;
    }
  
    /**
     * 计算浮心高度 KB
     * @private
     * @returns {number} KB 值 (米)
     */
    _calculateKB() {
      // 简化计算：KB ≈ 0.53 * draft
      const draft = this.navigation.depth || 6.0;
      return 0.53 * draft;
    }
  
    /**
     * 计算稳心半径 BM
     * @private
     * @returns {number} BM 值 (米)
     */
    _calculateBM() {
      // 简化计算：BM = I / V
      // I = 水线面惯性矩，V = 排水体积
      const beam = 20.0; // 船宽 (米)
      const draft = this.navigation.depth || 6.0;
      const I = (beam ** 3) / 12;
      const V = beam * draft * 50.0; // 简化排水体积
      return I / V;
    }
  
    /**
     * 计算排水量
     * @private
     * @returns {number} 排水量 (吨)
     */
    _calculateDisplacement() {
      const length = 100.0; // 船长 (米)
      const beam = 20.0; // 船宽 (米)
      const draft = this.navigation.depth || 6.0;
      const blockCoefficient = 0.7; // 方形系数
  
      return length * beam * draft * blockCoefficient * 1.025; // 海水密度
    }
  
    /**
     * 计算吃水
     * @private
     * @returns {number} 吃水 (米)
     */
    _calculateDraft() {
      return this.navigation.depth || 6.0;
    }
  
    /**
     * 计算纵倾
     * @private
     * @returns {number} 纵倾 (米)
     */
    _calculateTrim() {
      // 基于前后吃水差计算
      const aftDraft = this.navigation.depth || 6.0;
      const forwardDraft = aftDraft * 0.95; // 简化假设
      return aftDraft - forwardDraft;
    }
  
    /**
     * 评估稳性状态
     * @private
     * @param {number} gm - GM 值
     * @returns {string} 稳性状态
     */
    _assessStabilityStatus(gm) {
      if (gm < 0) return 'unstable';
      if (gm < 0.5) return 'marginal';
      if (gm > 2.0) return 'stiff';
      return 'stable';
    }
  
    /**
     * 评估浮力状态
     * @private
     * @param {number} draft - 吃水
     * @param {number} trim - 纵倾
     * @returns {string} 浮力状态
     */
    _assessBuoyancyStatus(draft, trim) {
      if (draft > 10.0) return 'deep_draft';
      if (Math.abs(trim) > 2.0) return 'excessive_trim';
      return 'normal';
    }
  
    /**
     * 导航系统故障诊断
     * @private
     */
    _diagnoseNavigation() {
      const issues = [];
  
      // 检查 GPS 信号
      if (!this.navigation.position) {
        issues.push({ code: 'NAV_001', message: 'GPS 信号丢失', severity: 'critical' });
      }
  
      // 检查速度异常
      if (this.navigation.speed !== null) {
        if (this.navigation.speed > 30) {
          issues.push({ code: 'NAV_002', message: '速度异常高', severity: 'warning' });
        }
        if (this.navigation.speed < 0) {
          issues.push({ code: 'NAV_003', message: '速度为负值', severity: 'critical' });
        }
      }
  
      // 检查水深
      if (this.navigation.depth !== null && this.navigation.depth < 5.0) {
        issues.push({ code: 'NAV_004', message: '浅水警告', severity: 'warning' });
      }
  
      this.diagnostics.navigation = {
        status: issues.length > 0 ? 'warning' : 'ok',
        issues,
        timestamp: Date.now(),
      };
  
      // 触发报警
      issues.forEach(issue => {
        this._triggerAlarm('navigation', issue);
      });
    }
  
    /**
     * 发动机故障诊断
     * @private
     */
    _diagnoseEngine() {
      const issues = [];
  
      // 检查温度
      if (this.engine.temperature !== null) {
        if (this.engine.temperature > 95) {
          issues.push({ code: 'ENG_001', message: '发动机温度过高', severity: 'critical' });
        } else if (this.engine.temperature > 85) {
          issues.push({ code: 'ENG_002', message: '发动机温度偏高', severity: 'warning' });
        }
      }
  
      // 检查油压
      if (this.engine.oilPressure !== null) {
        if (this.engine.oilPressure < 2.0) {
          issues.push({ code: 'ENG_003', message: '机油压力过低', severity: 'critical' });
        }
      }
  
      // 检查转速
      if (this.engine.rpm !== null) {
        if (this.engine.rpm > 2500) {
          issues.push({ code: 'ENG_004', message: '发动机超速', severity: 'warning' });
        }
      }
  
      // 检查燃油
      if (this.engine.fuelLevel !== null && this.engine.fuelLevel < 20) {
        issues.push({ code: 'ENG_005', message: '燃油不足', severity: 'warning' });
      }
  
      this.diagnostics.engine = {
        status: issues.some(i => i.severity === 'critical') ? 'critical' : (issues.length > 0 ? 'warning' : 'ok'),
        issues,
        timestamp: Date.now(),
      };
  
      // 触发报警
      issues.forEach(issue => {
        this._triggerAlarm('engine', issue);
      });
    }
  
    /**
     * 货物系统故障诊断
     * @private
     */
    _diagnoseCargo() {
      const issues = [];
  
      // 检查稳性
      if (this.cargo.stability) {
        if (this.cargo.stability.status === 'unstable') {
          issues.push({ code: 'CRG_001', message: '船舶稳性不足', severity: 'critical' });
        } else if (this.cargo.stability.status === 'marginal') {
          issues.push({ code: 'CRG_002', message: '船舶稳性临界', severity: 'warning' });
        }
      }
  
      // 检查浮力
      if (this.cargo.buoyancy) {
        if (this.cargo.buoyancy.status === 'deep_draft') {
          issues.push({ code: 'CRG_003', message: '吃水过深', severity: 'warning' });
        } else if (this.cargo.buoyancy.status === 'excessive_trim') {
          issues.push({ code: 'CRG_004', message: '纵倾过大', severity: 'warning' });
        }
      }
  
      this.diagnostics.cargo = {
        status: issues.some(i => i.severity === 'critical') ? 'critical' : (issues.length > 0 ? 'warning' : 'ok'),
        issues,
        timestamp: Date.now(),
      };
  
      // 触发报警
      issues.forEach(issue => {
        this._triggerAlarm('cargo', issue);
      });
    }
  
    /**
     * 气象系统故障诊断
     * @private
     */
    _diagnoseWeather() {
      const issues = [];
  
      // 检查风速
      if (this.weather.windSpeed !== null) {
        if (this.weather.windSpeed > 20) {
          issues.push({ code: 'WTH_001', message: '强风警告', severity: 'warning' });
        }
        if (this.weather.windSpeed > 30) {
          issues.push({ code: 'WTH_002', message: '大风警告', severity: 'critical' });
        }
      }
  
      // 检查浪高
      if (this.weather.waveHeight !== null) {
        if (this.weather.waveHeight > 3.0) {
          issues.push({ code: 'WTH_003', message: '大浪警告', severity: 'warning' });
        }
        if (this.weather.waveHeight > 5.0) {
          issues.push({ code: 'WTH_004', message: '巨浪警告', severity: 'critical' });
        }
      }
  
      // 检查能见度
      if (this.weather.visibility !== null && this.weather.visibility < 1000) {
        issues.push({ code: 'WTH_005', message: '低能见度', severity: 'warning' });
      }
  
      this.diagnostics.weather = {
        status: issues.some(i => i.severity === 'critical') ? 'critical' : (issues.length > 0 ? 'warning' : 'ok'),
        issues,
        timestamp: Date.now(),
      };
  
      // 触发报警
      issues.forEach(issue => {
        this._triggerAlarm('weather', issue);
      });
    }
  
    /**
     * 检查碰撞风险
     * @private
     * @param {Object} aisData - AIS 数据
     */
    _checkCollisionRisk(aisData) {
      const cpa = aisData.cpa;
      const tcpa = aisData.tcpa;
  
      if (cpa !== null && tcpa !== null) {
        if (cpa < 0.5 && tcpa > 0 && tcpa < 300) { // CPA < 500m, TCPA < 5min
          this._triggerAlarm('navigation', {
            code: 'COL_001',
            message: '碰撞风险！',
            severity: 'critical',
            data: { cpa, tcpa },
          });
        } else if (cpa < 1.0 && tcpa > 0 && tcpa < 600) {
          this._triggerAlarm('navigation', {
            code: 'COL_002',
            message: '潜在碰撞风险',
            severity: 'warning',
            data: { cpa, tcpa },
          });
        }
      }
    }
  
    /**
     * 触发报警
     * @private
     * @param {string} system - 系统名称
     * @param {Object} issue - 问题信息
     */
    _triggerAlarm(system, issue) {
      const alarm = {
        id: `${system}_${issue.code}_${Date.now()}`,
        system,
        ...issue,
        timestamp: Date.now(),
        acknowledged: false,
      };
  
      // 添加到报警列表
      this.alarms.push(alarm);
  
      // 限制报警列表大小
      if (this.alarms.length > 100) {
        this.alarms.shift();
      }
  
      // 通知监听器
      this
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
  
  ### 文件: `src/frontend/digital-twin/PoseidonXChannels.js`
  ```js
  /**
   * PoseidonXChannels.js - PoseidonX 数字孪生体 Channel 数据集成
   * 
   * 扩展 PoseidonX 类支持 Channel 数据输入，实现 WebSocket 客户端连接 Python 后端，
   * 添加 Channel 数据缓存与更新机制，实现 AI 决策与 Channel 数据联动。
   * 
   * @version 1.0.0
   * @date 2026-03-12
   */
  
  class PoseidonXChannels {
    /**
     * 创建 PoseidonXChannels 实例
     * @param {Object} options - 配置选项
     * @param {string} options.wsUrl - WebSocket 服务器地址 (默认：ws://localhost:8765)
     * @param {string} options.apiUrl - REST API 基础地址 (默认：http://localhost:8080)
     * @param {number} options.reconnectInterval - 重连间隔 (毫秒，默认：3000)
     * @param {number} options.cacheMaxSize - 缓存最大条目数 (默认：1000)
     * @param {number} options.cacheTTL - 缓存 TTL (毫秒，默认：300000)
     */
    constructor(options = {}) {
      this.wsUrl = options.wsUrl || 'ws://localhost:8765';
      this.apiUrl = options.apiUrl || 'http://localhost:8080';
      this.reconnectInterval = options.reconnectInterval || 3000;
      this.cacheMaxSize = options.cacheMaxSize || 1000;
      this.cacheTTL = options.cacheTTL || 300000;
  
      // WebSocket 连接
      this.ws = null;
      this.wsConnected = false;
  
      // 数据缓存 (LRU Cache)
      this.cache = new Map();
      this.cacheTimestamps = new Map();
  
      // 数据订阅回调
      this.subscribers = new Map(); // channel -> [callbacks]
  
      // 通道数据状态
      this.channels = {};
      this.channelMetadata = {};
  
      // AI 决策引擎引用
      this.aiDecisionEngine = null;
  
      // 日志
      this.logger = this._createLogger();
  
      // 自动重连标志
      this.autoReconnect = true;
      this.reconnectTimer = null;
    }
  
    /**
     * 创建日志记录器
     * @private
     */
    _createLogger() {
      const prefix = '[PoseidonXChannels]';
      return {
        info: (...args) => console.log(prefix, '[INFO]', ...args),
        warn: (...args) => console.warn(prefix, '[WARN]', ...args),
        error: (...args) => console.error(prefix, '[ERROR]', ...args),
        debug: (...args) => console.debug(prefix, '[DEBUG]', ...args),
      };
    }
  
    /**
     * 初始化连接
     * @returns {Promise<void>}
     */
    async connect() {
      this.logger.info('正在连接到 Poseidon Server...', this.wsUrl);
  
      try {
        // 获取 Channel 元数据
        await this._fetchChannelMetadata();
  
        // 建立 WebSocket 连接
        await this._connectWebSocket();
  
        this.logger.info('连接成功');
      } catch (error) {
        this.logger.error('连接失败:', error);
        throw error;
      }
    }
  
    /**
     * 获取 Channel 元数据
     * @private
     */
    async _fetchChannelMetadata() {
      try {
        const response = await fetch(`${this.apiUrl}/api/channels`);
        const data = await response.json();
        
        this.channelMetadata = {
          channels: data.channels || [],
          timestamp: Date.now(),
        };
  
        // 初始化通道数据结构
        this.channelMetadata.channels.forEach(channel => {
          this.channels[channel] = {
            data: null,
            timestamp: null,
            status: 'pending',
          };
        });
  
        this.logger.info(`获取到 ${this.channelMetadata.channels.length} 个 Channel`);
      } catch (error) {
        this.logger.warn('获取 Channel 元数据失败，使用默认配置:', error);
        // 使用默认 Channel 列表
        this.channelMetadata = {
          channels: [
            'nmea_parser', 'vessel_ais', 'engine_monitor', 'power_management',
            'navigation_data', 'cargo_monitor', 'weather_routing', 'web',
          ],
          timestamp: Date.now(),
        };
      }
    }
  
    /**
     * 连接 WebSocket
     * @private
     */
    _connectWebSocket() {
      return new Promise((resolve, reject) => {
        try {
          this.ws = new WebSocket(this.wsUrl);
  
          this.ws.onopen = () => {
            this.wsConnected = true;
            this.logger.info('WebSocket 连接已建立');
            
            // 清除重连定时器
            if (this.reconnectTimer) {
              clearTimeout(this.reconnectTimer);
              this.reconnectTimer = null;
            }
  
            // 发送订阅请求
            this._subscribeToAllChannels();
  
            resolve();
          };
  
          this.ws.onmessage = (event) => {
            this._handleWebSocketMessage(event);
          };
  
          this.ws.onclose = () => {
            this.wsConnected = false;
            this.logger.warn('WebSocket 连接已关闭');
            
            // 自动重连
            if (this.autoReconnect) {
              this._scheduleReconnect();
            }
          };
  
          this.ws.onerror = (error) => {
            this.logger.error('WebSocket 错误:', error);
            reject(error);
          };
  
          // 连接超时
          setTimeout(() => {
            if (!this.wsConnected) {
              reject(new Error('WebSocket 连接超时'));
            }
          }, 10000);
        } catch (error) {
          reject(error);
        }
      });
    }
  
    /**
     * 安排重连
     * @private
     */
    _scheduleReconnect() {
      if (this.reconnectTimer) {
        return;
      }
  
      this.logger.info(`将在 ${this.reconnectInterval}ms 后重连...`);
      this.reconnectTimer = setTimeout(async () => {
        this.reconnectTimer = null;
        try {
          await this._connectWebSocket();
        } catch (error) {
          this.logger.error('重连失败:', error);
          this._scheduleReconnect();
        }
      }, this.reconnectInterval);
    }
  
    /**
     * 订阅所有 Channel
     * @private
     */
    _subscribeToAllChannels() {
      if (!this.ws || !this.wsConnected) {
        return;
      }
  
      const subscribeMessage = {
        type: 'subscribe',
        channels: this.channelMetadata.channels,
      };
  
      this.ws.send(JSON.stringify(subscribeMessage));
      this.logger.info('已订阅所有 Channel');
    }
  
    /**
     * 处理 WebSocket 消息
     * @private
     * @param {MessageEvent} event - WebSocket 消息事件
     */
    _handleWebSocketMessage(event) {
      try {
        const message = JSON.parse(event.data);
  
        switch (message.type) {
          case 'data_update':
            this._handleDataUpdate(message);
            break;
          case 'alarm':
            this._handleAlarm(message);
            break;
          case 'channel_status':
            this._handleChannelStatus(message);
            break;
          default:
            this.logger.debug('未知消息类型:', message.type);
        }
      } catch (error) {
        this.logger.error('解析 WebSocket 消息失败:', error);
      }
    }
  
    /**
     * 处理数据更新
     * @private
     * @param {Object} message - 消息内容
     */
    _handleDataUpdate(message) {
      const { channel, data, timestamp } = message;
  
      // 更新缓存
      this._setCache(channel, data);
  
      // 更新通道状态
      if (this.channels[channel]) {
        this.channels[channel].data = data;
        this.channels[channel].timestamp = timestamp || Date.now();
        this.channels[channel].status = 'active';
      }
  
      // 通知订阅者
      this._notifySubscribers(channel, data);
  
      // 触发 AI 决策引擎
      if (this.aiDecisionEngine) {
        this.aiDecisionEngine.onChannelDataUpdate(channel, data);
      }
    }
  
    /**
     * 处理报警
     * @private
     * @param {Object} message - 报警消息
     */
    _handleAlarm(message) {
      const { channel, level, rule, value, threshold, timestamp } = message;
  
      this.logger.warn(`[${channel}] 报警 [${level}]: ${rule}, 当前值=${value}, 阈值=${threshold}`);
  
      // 通知订阅者
      this._notifySubscribers(channel, {
        type: 'alarm',
        level,
        rule,
        value,
        threshold,
        timestamp,
      });
    }
  
    /**
     * 处理 Channel 状态
     * @private
     * @param {Object} message - 状态消息
     */
    _handleChannelStatus(message) {
      const { channel, status, message: statusMessage } = message;
  
      if (this.channels[channel]) {
        this.channels[channel].status = status;
      }
  
      this.logger.info(`[${channel}] 状态更新: ${status} - ${statusMessage}`);
    }
  
    /**
     * 设置缓存
     * @private
     * @param {string} key - 缓存键
     * @param {any} value - 缓存值
     */
    _setCache(key, value) {
      // LRU 缓存管理
      if (this.cache.size >= this.cacheMaxSize) {
        const firstKey = this.cache.keys().next().value;
        this.cache.delete(firstKey);
        this.cacheTimestamps.delete(firstKey);
      }
  
      this.cache.set(key, value);
      this.cacheTimestamps.set(key, Date.now());
    }
  
    /**
     * 获取缓存
     * @private
     * @param {string} key - 缓存键
     * @returns {any|null} 缓存值，如果过期或不存在则返回 null
     */
    _getCache(key) {
      const timestamp = this.cacheTimestamps.get(key);
      if (!timestamp || Date.now() - timestamp > this.cacheTTL) {
        this.cache.delete(key);
        this.cacheTimestamps.delete(key);
        return null;
      }
      return this.cache.get(key);
    }
  
    /**
     * 订阅 Channel 数据
     * @param {string} channel - Channel 名称
     * @param {Function} callback - 回调函数 (data) => void
     * @returns {Function} 取消订阅函数
     */
    subscribe(channel, callback) {
      if (!this.subscribers.has(channel)) {
        this.subscribers.set(channel, []);
      }
  
      this.subscribers.get(channel).push(callback);
  
      // 如果已有缓存数据，立即回调
      const cachedData = this._getCache(channel);
      if (cachedData) {
        callback(cachedData);
      }
  
      // 返回取消订阅函数
      return () => {
        const callbacks = this.subscribers.get(channel);
        if (callbacks) {
          const index = callbacks.indexOf(callback);
          if (index > -1) {
            callbacks.splice(index, 1);
          }
        }
      };
    }
  
    /**
     * 通知订阅者
     * @private
     * @param {string} channel - Channel 名称
     * @param {any} data - 数据
     */
    _notifySubscribers(channel, data) {
      const callbacks = this.subscribers.get(channel);
      if (callbacks) {
        callbacks.forEach(callback => {
          try {
            callback(data);
          } catch (error) {
            this.logger.error(`订阅者回调失败 [${channel}]:`, error);
          }
        });
      }
    }
  
    /**
     * 获取 Channel 数据
     * @param {string} channel - Channel 名称
     * @returns {Object|null} Channel 数据
     */
    getChannelData(channel) {
      // 优先返回缓存数据
      const cached = this._getCache(channel);
      if (cached) {
        return cached;
      }
  
      // 返回最新数据
      return this.channels[channel]?.data || null;
    }
  
    /**
     * 获取所有 Channel 数据
     * @returns {Object} 所有 Channel 数据
     */
    getAllChannelData() {
      const result = {};
      this.channelMetadata.channels.forEach(channel => {
        result[channel] = this.getChannelData(channel);
      });
      return result;
    }
  
    /**
     * 通过 REST API 获取历史数据
     * @param {string} channel - Channel 名称
     * @param {Object} options - 查询选项
     * @param {string} options.startTime - 开始时间 (ISO 8601)
     * @param {string} options.endTime - 结束时间 (ISO 8601)
     * @param {number} options.limit - 最大返回条数
     * @returns {Promise<Array>} 历史数据数组
     */
    async getHistoricalData(channel, options = {}) {
      const params = new URLSearchParams();
      if (options.startTime) params.append('start_time', options.startTime);
      if (options.endTime) params.append('end_time', options.endTime);
      if (options.limit) params.append('limit', options.limit);
  
      const response = await fetch(
        `${this.apiUrl}/api/timeseries?channel=${channel}&${params.toString()}`
      );
  
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
  
      const data = await response.json();
      return data.data || [];
    }
  
    /**
     * 设置 AI 决策引擎
     * @param {Object} engine - AI 决策引擎实例
     */
    setAIDecisionEngine(engine) {
      this.aiDecisionEngine = engine;
      this.logger.info('AI 决策引擎已设置');
    }
  
    /**
     * 发送数据到后端
     * @param {string} channel - Channel 名称
     * @param {Object} data - 数据
     * @returns {Promise<Object>} 服务器响应
     */
    async sendData(channel, data) {
      const response = await fetch(`${this.apiUrl}/api/data/${channel}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
  
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
  
      return await response.json();
    }
  
    /**
     * 断开连接
     */
    disconnect() {
      this.autoReconnect = false;
  
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
  
      if (this.ws) {
        this.ws.close();
        this.ws = null;
      }
  
      this.wsConnected = false;
      this.logger.info('连接已断开');
    }
  
    /**
     * 获取连接状态
     * @returns {Object} 连接状态
     */
    getStatus() {
      return {
        connected: this.wsConnected,
        channels: Object.keys(this.channels),
        cacheSize: this.cache.size,
        subscribersCount: Array.from(this.subscribers.values()).reduce(
          (sum, arr) => sum + arr.length,
          0
        ),
      };
    }
  }
  
  /**
   * AI 决策引擎基类
   * 可扩展实现自定义 AI 决策逻辑
   */
  class AIDecisionEngine {
    /**
     * 处理 Channel 数据更新
     * @param {string} channel - Channel 名称
     * @param {Object} data - 数据
     */
    onChannelDataUpdate(channel, data) {
      // 默认实现：子类应重写此方法
      console.debug('[AIDecisionEngine] 数据更新:', channel, data);
    }
  
    /**
     * 做出决策
     * @param {Object} context - 决策上下文
     * @returns {Object} 决策结果
     */
    makeDecision(context) {
      throw new Error('子类必须实现 makeDecision 方法');
    }
  }
  
  // 导出
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PoseidonXChannels, AIDecisionEngine };
  } else {
    window.PoseidonXChannels = PoseidonXChannels;
    window.AIDecisionEngine = AIDecisionEngine;
  }
  
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
          return 
  ```
  
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

好的，作为 PoseidonX 系统的项目经理 (PM)，我已经分析了您提出的“让货船以双体船为圆心做圆周运动 V2”任务。根据项目上下文和任务要求，我将此任务分解为以下可执行的子步骤，并识别了其中的技术风险和依赖关系。

---

### **任务分解与规划文档**

**项目名称:** PoseidonX 数字孪生系统 - 货船圆周运动 V2
**任务负责人:** [待分配]
**版本:** 1.0
**日期:** 2024-05-24

#### **1. 任务概述**

**目标:** 创建一个独立的货船运动模块，使其在3D场景中围绕双体船（`catamaranObject`）做半径为500米、角速度为0.5度/秒的圆周运动。同时，创建一个后端Channel，用于实时上报该货船的位置、航向和速度信息。

**核心交付物:**
1.  **前端模块:** `src/frontend/digital-twin/cargo_orbit.js`
2.  **后端Channel:** `src/backend/channels/cargo_orbit_channel.py`

**约束条件:**
*   不得修改 `main.js` 或 `PoseidonX.js` 主文件。
*   必须是一个独立、可复用的模块。

#### **2. 任务分解与子步骤**

| 步骤 ID | 任务名称 | 详细描述 | 负责人 | 预估工时 | 前置依赖 | 风险/备注 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **S1** | **前端模块设计与实现** | 创建 `src/frontend/digital-twin/cargo_orbit.js` 文件，实现核心逻辑。 | 前端开发者 | 4h | 无 | 需要理解Three.js和项目现有的3D场景结构。 |
| **S1.1** | 模块接口定义 | 定义并导出 `setupCargoOrbit(scene, catamaranObject, options)` 函数。明确参数类型和返回值。 | 前端开发者 | 0.5h | 无 | 确保接口清晰，易于集成。 |
| **S1.2** | 货船Mesh创建 | 在函数内部创建一个代表货船的 `Mesh` 对象。可以使用简单的几何体（如 `BoxGeometry`）或加载外部模型。 | 前端开发者 | 1h | S1.1 | 如果使用外部模型，需考虑模型路径和加载时间。 |
| **S1.3** | 圆周运动逻辑实现 | 实现货船围绕 `catamaranObject` 做圆周运动的逻辑。使用 `requestAnimationFrame` 或 `setInterval` 更新货船位置。 | 前端开发者 | 2h | S1.2 | 需要计算圆周上的点，并更新货船的 `position` 和 `rotation`。 |
| **S1.4** | 参数化配置 | 将半径（500米）和角速度（0.5度/秒）作为 `options` 参数，使其可配置。 | 前端开发者 | 0.5h | S1.3 | 提高模块的灵活性。 |
| **S2** | **后端Channel设计与实现** | 创建 `src/backend/channels/cargo_orbit_channel.py` 文件，实现数据上报功能。 | 后端开发者 | 3h | 无 | 需要理解项目现有的 `MarineChannel` 基类和WebSocket通信机制。 |
| **S2.1** | Channel类创建 | 创建 `CargoOrbitChannel(MarineChannel)` 类，并实现必要的方法（如 `__init__`, `start`, `stop`）。 | 后端开发者 | 1h | 无 | 参考 `src/backend/register_channels.py` 或其他现有Channel的实现。 |
| **S2.2** | 数据上报逻辑 | 实现一个定时任务（如每1秒），模拟或接收前端传来的货船位置数据，并通过WebSocket广播。 | 后端开发者 | 1.5h | S2.1 | 需要定义数据格式：`{lat, lon, course, speed}`。 |
| **S2.3** | Channel注册 | 将 `CargoOrbitChannel` 注册到系统的Channel管理器中，确保其能被启动和停止。 | 后端开发者 | 0.5h | S2.2 | 可能需要修改 `src/backend/register_channels.py` 或类似文件。 |
| **S3** | **前后端集成与测试** | 将前端模块和后端Channel集成到现有系统中，并进行端到端测试。 | 全栈开发者 | 3h | S1, S2 | 需要搭建测试环境，模拟双体船对象。 |
| **S3.1** | 前端集成 | 在 `digital-twin.html` 或其他入口文件中引入 `cargo_orbit.js` 模块，并调用 `setupCargoOrbit` 函数。 | 前端开发者 | 1h | S1 | 需要找到 `catamaranObject` 的引用方式。 |
| **S3.2** | 后端集成 | 确保 `CargoOrbitChannel` 在系统启动时被正确加载和运行。 | 后端开发者 | 1h | S2 | 可能需要修改 `main.py` 或 `marine_channels_integration.py`。 |
| **S3.3** | 端到端测试 | 启动前后端，验证货船是否在3D场景中做圆周运动，并检查后端是否收到并广播了正确的数据。 | 测试工程师 | 1h | S3.1, S3.2 | 重点测试数据的一致性和实时性。 |

#### **3. 技术风险与依赖关系**

*   **技术风险:**
    1.  **`catamaranObject` 引用:** 前端模块需要获取到双体船的3D对象 (`catamaranObject`) 作为圆心。如果该对象在 `main.js` 或 `PoseidonX.js` 内部创建且未暴露，则无法直接引用。**解决方案:** 需要与架构师确认 `catamaranObject` 是否已挂载到 `window` 对象或通过其他全局方式暴露。如果未暴露，可能需要修改 `main.js` 或 `PoseidonX.js` 来导出它，但这违反了任务约束。**备选方案:** 在 `digital-twin.html` 中，在 `main.js` 执行后，通过场景图遍历 (`scene.getObjectByName`) 来查找该对象。
    2.  **坐标系统不一致:** 前端3D场景的坐标系统（通常是笛卡尔坐标系）与后端上报的经纬度坐标系统不同。**解决方案:** 前端模块需要实现一个坐标转换函数，将货船在3D空间中的位置（x, y, z）转换为经纬度（lat, lon）。这需要知道场景中一个参考点的经纬度。
    3.  **`MarineChannel` 基类未知:** 后端开发者需要了解 `MarineChannel` 基类的具体接口和实现方式。**解决方案:** 仔细阅读 `src/backend/marine_channels_integration.py` 和 `src/backend/register_channels.py` 文件，理解其工作原理。

*   **依赖关系:**
    *   **S1 (前端模块):** 依赖于对Three.js API和项目3D场景结构的理解。
    *   **S2 (后端Channel):** 依赖于对 `MarineChannel` 基类和项目WebSocket通信机制的理解。
    *   **S3 (集成测试):** 依赖于S1和S2的完成，以及一个可运行的测试环境。

#### **4. 对后续团队的指导**

*   **前端开发者:**
    *   请首先阅读 `src/frontend/digital-twin/main.js` 和 `PoseidonX.js`，了解 `catamaranObject` 是如何创建和管理的。
    *   在 `cargo_orbit.js` 中，使用 `THREE.Group` 或 `THREE.Mesh` 创建货船对象，并添加到 `scene` 中。
    *   圆周运动的核心逻辑是：在每一帧，根据当前角度计算货船在圆周上的位置，并更新其 `position`。同时，需要计算货船的朝向（`rotation`），使其始终指向运动方向（即圆的切线方向）。
    *   为了向后端上报数据，您需要在模块内部实现一个定时器，定期计算货船的“虚拟”经纬度（基于一个已知的参考点）和航向，并通过WebSocket或REST API发送到后端。**注意:** 任务要求后端Channel上报，但前端需要将数据发送给后端。您可以使用现有的 `PoseidonXChannels` 实例（如果可用）或直接使用WebSocket。

*   **后端开发者:**
    *   请仔细阅读 `src/backend/marine_channels_integration.py` 和 `src/backend/register_channels.py`，理解 `MarineChannel` 的接口。
    *   `CargoOrbitChannel` 的核心功能是接收来自前端的数据（或自己模拟数据），并将其广播给所有订��了该Channel的客户端。
    *   数据格式必须严格遵循 `{lat: float, lon: float, course: float, speed: float}`。
    *   请确保在 `register_channels.py` 或类似配置文件中注册您的Channel，以便系统在启动时自动加载。

*   **架构师/技术负责人:**
    *   请确认 `catamaranObject` 的全局可访问性。如果不可访问，请提供获取该对象的替代方案（如通过场景图查找）。
    *   请提供一个3D场景中已知点的经纬度坐标，以便前端开发者进行坐标转换。
    *   请明确前端数据应通过何种方式发送到后端（例如，通过现有的WebSocket连接，还是创建一个新的REST端点）。

────────────────────────────────────────────────────────────
✅ deepseek-chat 完成
