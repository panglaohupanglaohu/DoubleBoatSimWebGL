# 架构设计 — architect

任务: 让货船以双体船为圆心做圆周运动 V2
步骤: architecture
Agent: build_architect

---

📋 任务: a7813b18-c3b
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
  
  
  ## 前序步骤的产出 (管线共享工作区)
  
  ### 步骤 01: pm_decompose.md
  
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
    
      /*
  ### 步骤 02: research.md
  
  # 研究分析 — researcher
  
  任务: 让货船以双体船为圆心做圆周运动 V2
  步骤: research
  Agent: build_researcher
  
  ---
  
  📋 任务: a7813b18-c3b
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
    
      /*
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

# 技术方案设计

## 1. 任务概述

创建货船围绕双体船做圆周运动的独立模块，包含前端3D可视化和后端数据上报通道。

## 2. 技术方案

### 2.1 前端模块 `cargo_orbit.js`

**文件路径**: `src/frontend/digital-twin/cargo_orbit.js`

**核心功能**:
- 创建货船 Mesh（使用 Three.js BoxGeometry 或加载 GLB 模型）
- 实现圆周运动算法（半径500米，角速度0.5°/秒）
- 导出 `setupCargoOrbit(scene, catamaranObject, options)` 函数

**技术要点**:
1. 使用 Three.js 创建货船模型（简化版用 BoxGeometry + 颜色材质）
2. 圆周运动参数：
   - 半径: 500 米（场景单位）
   - 角速度: 0.5°/秒 = 0.00872665 rad/s
   - 周期: 720秒（12分钟）
3. 每帧更新位置：`x = center.x + radius * cos(angle)`, `z = center.z + radius * sin(angle)`
4. 货船朝向始终指向运动方向（切线方向）

### 2.2 后端通道 `cargo_orbit_channel.py`

**文件路径**: `src/backend/channels/cargo_orbit_channel.py`

**核心功能**:
- 继承 `MarineChannel` 基类
- 定期上报货船位置数据 (lat, lon, course, speed)
- 数据格式符合 PoseidonX 通道规范

## 3. 接口设计

### 3.1 `setupCargoOrbit` 函数接口

```javascript
/**
 * 设置货船围绕双体船做圆周运动
 * @param {THREE.Scene} scene - Three.js 场景
 * @param {THREE.Object3D} catamaranObject - 双体船对象
 * @param {Object} options - 配置选项
 * @param {number} options.radius - 圆周半径（默认500）
 * @param {number} options.angularSpeed - 角速度 度/秒（默认0.5）
 * @param {string} options.cargoColor - 货船颜色（默认0x888888）
 * @param {number} options.cargoSize - 货船尺寸比例（默认1.0）
 * @param {Function} options.onPositionUpdate - 位置更新回调
 * @returns {Object} 控制对象 { start, stop, getPosition, dispose }
 */
export function setupCargoOrbit(scene, catamaranObject, options = {})
```

### 3.2 `CargoOrbitChannel` 类接口

```python
class CargoOrbitChannel(MarineChannel):
    """
    货船轨道数据通道
    定期上报货船位置 (lat, lon, course, speed)
    """
    
    def __init__(self, update_interval=1.0):
        """
        @param update_interval: 更新间隔（秒）
        """
    
    async def get_current_position(self) -> dict:
        """
        获取当前货船位置
        @return: {lat, lon, course, speed, timestamp}
        """
    
    async def run(self):
        """通道主循环"""
```

## 4. 实施步骤

### 步骤1: 创建前端模块 `cargo_orbit.js`

```javascript
// src/frontend/digital-twin/cargo_orbit.js
import * as THREE from 'three';

/**
 * 设置货船围绕双体船做圆周运动
 */
export function setupCargoOrbit(scene, catamaranObject, options = {}) {
    const {
        radius = 500,
        angularSpeed = 0.5, // 度/秒
        cargoColor = 0x888888,
        cargoSize = 1.0,
        onPositionUpdate = null
    } = options;

    // 1. 创建货船 Mesh
    const cargoGroup = new THREE.Group();
    
    // 船体
    const hullGeometry = new THREE.BoxGeometry(80 * cargoSize, 20 * cargoSize, 15 * cargoSize);
    const hullMaterial = new THREE.MeshPhongMaterial({ color: cargoColor });
    const hull = new THREE.Mesh(hullGeometry, hullMaterial);
    hull.position.y = 5 * cargoSize;
    cargoGroup.add(hull);

    // 上层建筑
    const superstructureGeometry = new THREE.BoxGeometry(30 * cargoSize, 10 * cargoSize, 10 * cargoSize);
    const superstructureMaterial = new THREE.MeshPhongMaterial({ color: 0xcccccc });
    const superstructure = new THREE.Mesh(superstructureGeometry, superstructureMaterial);
    superstructure.position.set(0, 15 * cargoSize, 0);
    cargoGroup.add(superstructure);

    // 烟囱
    const funnelGeometry = new THREE.CylinderGeometry(3 * cargoSize, 4 * cargoSize, 8 * cargoSize);
    const funnelMaterial = new THREE.MeshPhongMaterial({ color: 0xff4444 });
    const funnel = new THREE.Mesh(funnelGeometry, funnelMaterial);
    funnel.position.set(-15 * cargoSize, 20 * cargoSize, 0);
    cargoGroup.add(funnel);

    scene.add(cargoGroup);

    // 2. 状态变量
    let angle = 0; // 当前角度（弧度）
    let isRunning = true;
    let lastTimestamp = performance.now();

    // 3. 动画循环
    function animate() {
        if (!isRunning) return;

        const now = performance.now();
        const deltaTime = (now - lastTimestamp) / 1000; // 秒
        lastTimestamp = now;

        // 更新角度
        const angularSpeedRad = THREE.MathUtils.degToRad(angularSpeed);
        angle += angularSpeedRad * deltaTime;

        // 计算位置
        const x = catamaranObject.position.x + radius * Math.cos(angle);
        const z = catamaranObject.position.z + radius * Math.sin(angle);
        
        cargoGroup.position.set(x, catamaranObject.position.y, z);

        // 计算朝向（切线方向）
        const tangentAngle = angle + Math.PI / 2;
        cargoGroup.rotation.y = -tangentAngle;

        // 回调通知
        if (onPositionUpdate) {
            onPositionUpdate({
                x: x,
                z: z,
                angle: THREE.MathUtils.radToDeg(angle),
                speed: radius * angularSpeedRad // 线速度
            });
        }

        requestAnimationFrame(animate);
    }

    // 启动动画
    animate();

    // 4. 返回控制接口
    return {
        start() {
            if (!isRunning) {
                isRunning = true;
                lastTimestamp = performance.now();
                animate();
            }
        },
        stop() {
            isRunning = false;
        },
        getPosition() {
            return {
                x: cargoGroup.position.x,
                z: cargoGroup.position.z,
                angle: THREE.MathUtils.radToDeg(angle)
            };
        },
        dispose() {
            isRunning = false;
            scene.remove(cargoGroup);
            // 清理几何体和材质
            [hullGeometry, superstructureGeometry, funnelGeometry].forEach(g => g.dispose());
            [hullMaterial, superstructureMaterial, funnelMaterial].forEach(m => m.dispose());
        }
    };
}
```

### 步骤2: 创建后端通道 `cargo_orbit_channel.py`

```python
# src/backend/channels/cargo_orbit_channel.py
import asyncio
import math
import time
from typing import Optional

from src.backend.marine_channels_integration import MarineChannel


class CargoOrbitChannel(MarineChannel):
    """
    货船轨道数据通道
    模拟货船围绕双体船做圆周运动，上报位置数据
    """
    
    def __init__(self, update_interval: float = 1.0):
        super().__init__()
        self.update_interval = update_interval
        self.channel_name = "cargo_orbit"
        
        # 轨道参数
        self.center_lat = 22.5  # 双体船纬度
        self.center_lon = 114.0  # 双体船经度
        self.radius_km = 0.5  # 半径（公里）
        self.angular_speed = 0.5  # 度/秒
        
        # 状态
        self.current_angle = 0.0  # 当前角度（度）
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        
    async def get_current_position(self) -> dict:
        """
        获取当前货船位置
        @return: {lat, lon, course, speed, timestamp}
        """
        # 角度转弧度
        angle_rad = math.radians(self.current_angle)
        
        # 计算经纬度偏移（简化计算）
        # 1度纬度 ≈ 111km, 1度经度 ≈ 111*cos(lat) km
        lat_offset = (self.radius_km * math.cos(angle_rad)) / 111.0
        lon_offset = (self.radius_km * math.sin(angle_rad)) / (111.0 * math.cos(math.radians(self.center_lat)))
        
        # 航向（切线方向 = 当前角度 + 90度）
        course = (self.current_angle + 90) % 360
        
        # 速度（线速度 = 角速度 * 半径）
        speed = self.angular_speed * self.radius_km * (math.pi / 180) * 3600  # km/h
        
        return {
            "lat": self.center_lat + lat_offset,
            "lon": self.center_lon + lon_offset,
            "course": course,
            "speed": round(speed, 2),
            "timestamp": time.time()
        }
    
    async def run(self):
        """通道主循环"""
        self.is_running = True
        self.logger.info(f"CargoOrbitChannel started (interval={self.update_interval}s)")
        
        while self.is_running:
            try:
                # 更新角度
                self.current_angle = (self.current_angle + self.angular_speed * self.update_interval) % 360
                
                # 获取位置
                position = await self.get_current_position()
                
                # 发布数据
                await self.publish_data(self.channel_name, position)
                
                # 等待下一次更新
                await asyncio.sleep(self.update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in CargoOrbitChannel: {e}")
                await asyncio.sleep(1)
        
        self.is_running = False
        self.logger.info("CargoOrbitChannel stopped")
    
    async def start(self):
        """启动通道"""
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self.run())
    
    async def stop(self):
        """停止通道"""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
```

### 步骤3: 注册后端通道

在 `src/backend/register_channels.py` 中添加：

```python
from src.backend.channels.cargo_orbit_channel import CargoOrbitChannel

# 在通道注册函数中添加
def register_channels(app):
    # ... 现有代码 ...
    
    # 注册货船轨道通道
    cargo_orbit_channel = CargoOrbitChannel(update_interval=1.0)
    app.add_channel(cargo_orbit_channel)
```

## 5. 使用示例

### 在 main.js 中集成（不修改主文件，通过独立加载）

```javascript
// 在 HTML 中或通过模块加载
import { setupCargoOrbit } from './cargo_orbit.js';

// 在场景初始化后调用
const cargoOrbit = setupCargoOrbit(scene, catamaranObject, {
    radius: 500,
    angularSpeed: 0.5,
    cargoColor: 0x666666,
    cargoSize: 0.8,
    onPositionUpdate: (pos) => {
        // 可选：更新 UI 或发送到后端
        console.log('Cargo position:', pos);
    }
});
```

## 6. 注意事项

1. **单位���致性**: Three.js 场景中 1 单位 = 1 米，确保半径 500 单位对应 500 米
2. **性能优化**: 使用 `requestAnimationFrame` 实现平滑动画，避免使用 `setInterval`
3. **资源清理**: 提供 `dispose()` 方法清理 Three.js 资源
4. **坐标转换**: 后端经纬度计算使用简化公式，如需高精度请使用 `geopy` 等库
5. **通道注册**: 确保后端通道在应用启动时自动注册并启动

────────────────────────────────────────────────────────────
✅ deepseek-chat 完成
