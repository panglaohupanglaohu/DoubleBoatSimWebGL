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
    this.alarmListeners.forEach(listener => {
      try {
        listener(alarm);
      } catch (error) {
        this.logger.error('报警监听器错误:', error);
      }
    });

    this.logger.warn(`[报警] ${system}: ${issue.message} [${issue.severity}]`);
  }

  /**
   * 注册报警监听器
   * @param {Function} listener - 监听器回调
   * @returns {Function} 取消注册函数
   */
  onAlarm(listener) {
    this.alarmListeners.push(listener);

    return () => {
      const index = this.alarmListeners.indexOf(listener);
      if (index > -1) {
        this.alarmListeners.splice(index, 1);
      }
    };
  }

  /**
   * 获取当前报警
   * @param {Object} options - 过滤选项
   * @param {string} options.system - 系统过滤
   * @param {string} options.severity - 严重程度过滤
   * @param {boolean} options.acknowledged - 是否包含已确认的报警
   * @returns {Array} 报警列表
   */
  getAlarms(options = {}) {
    let filtered = [...this.alarms];

    if (options.system) {
      filtered = filtered.filter(a => a.system === options.system);
    }

    if (options.severity) {
      filtered = filtered.filter(a => a.severity === options.severity);
    }

    if (options.acknowledged === false) {
      filtered = filtered.filter(a => !a.acknowledged);
    }

    return filtered;
  }

  /**
   * 确认报警
   * @param {string} alarmId - 报警 ID
   */
  acknowledgeAlarm(alarmId) {
    const alarm = this.alarms.find(a => a.id === alarmId);
    if (alarm) {
      alarm.acknowledged = true;
      this.logger.info(`报警已确认：${alarmId}`);
    }
  }

  /**
   * 注册 HITL 回调
   * @param {string} action - 动作名称
   * @param {Function} callback - 回调函数
   */
  registerHITLCallback(action, callback) {
    this.hitlCallbacks.set(action, callback);
    this.logger.info(`HITL 回调已注册：${action}`);
  }

  /**
   * 执行 HITL 动作
   * @param {string} action - 动作名称
   * @param {Object} context - 上下文
   * @returns {Promise<Object>} 动作结果
   */
  async executeHITL(action, context = {}) {
    const callback = this.hitlCallbacks.get(action);
    if (!callback) {
      throw new Error(`未注册的 HITL 动作：${action}`);
    }

    try {
      const result = await callback(context, this);
      this.logger.info(`HITL 动作执行完成：${action}`);
      return result;
    } catch (error) {
      this.logger.error(`HITL 动作执行失败：${action}`, error);
      throw error;
    }
  }

  /**
   * 获取所有工程数据
   * @returns {Object} 工程数据
   */
  getAllData() {
    return {
      navigation: this.navigation,
      engine: this.engine,
      cargo: this.cargo,
      weather: this.weather,
      diagnostics: this.diagnostics,
      alarms: this.getAlarms({ acknowledged: false }),
      timestamp: Date.now(),
    };
  }

  /**
   * 获取系统健康状态
   * @returns {Object} 健康状态
   */
  getHealthStatus() {
    const criticalCount = this.alarms.filter(a => a.severity === 'critical' && !a.acknowledged).length;
    const warningCount = this.alarms.filter(a => a.severity === 'warning' && !a.acknowledged).length;

    let overallStatus = 'ok';
    if (criticalCount > 0) {
      overallStatus = 'critical';
    } else if (warningCount > 0) {
      overallStatus = 'warning';
    }

    return {
      overall: overallStatus,
      navigation: this.diagnostics.navigation.status,
      engine: this.diagnostics.engine.status,
      cargo: this.diagnostics.cargo.status,
      weather: this.diagnostics.weather.status,
      alarms: {
        critical: criticalCount,
        warning: warningCount,
      },
      timestamp: Date.now(),
    };
  }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { MarineEngineeringChannels };
} else {
  window.MarineEngineeringChannels = MarineEngineeringChannels;
}
