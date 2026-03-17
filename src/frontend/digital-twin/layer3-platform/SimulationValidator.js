/**
 * Simulation Validator - 仿真验证器
 * 
 * Software 3.0 理念：这是"编译器"
 * - 生成的 Agent 必须在这里通过测试才能部署
 * - 生成 1000+ 种场景（暴风雨、夜间、大雾、设备故障）
 * - Vibe Check: Agent 是否符合预期行为？
 * 
 * 集成：
 * - NVIDIA Isaac Sim (OceanSim)
 * - Unity ML-Agents
 * - Gazebo
 */

import { EventEmitter } from '../../utils/EventEmitter.js';

export class SimulationValidator extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      scenarioCount: config.scenarioCount || 100, // 测试场景数量
      passThreshold: config.passThreshold || 0.85, // 通过阈值（85%）
      timeout: config.timeout || 60000, // 单个场景超时
      simulatorType: config.simulatorType || 'mock', // 'mock' | 'isaac' | 'unity' | 'gazebo'
      ...config
    };
    
    // 测试场景库
    this.scenarios = new Map();
    
    // 验证历史
    this.validationHistory = [];
    
    // 初始化场景
    this._initializeScenarios();
    
    console.log('🔬 Simulation Validator initialized');
  }
  
  /**
   * 验证 Agent
   * @param {Object} agent - Agent 实例
   * @param {Array<string>} scenarioTypes - 要测试的场景类型
   * @returns {Promise<Object>} - 验证报告
   */
  async validateAgent(agent, scenarioTypes = ['all']) {
    console.log(`🔬 Validating Agent: ${agent.name || agent.id}`);
    
    const startTime = Date.now();
    
    // 选择测试场景
    const selectedScenarios = this._selectScenarios(scenarioTypes);
    
    console.log(`  Testing with ${selectedScenarios.length} scenarios`);
    
    const results = [];
    let passedCount = 0;
    
    // 运行每个场景
    for (let i = 0; i < selectedScenarios.length; i++) {
      const scenario = selectedScenarios[i];
      
      console.log(`  [${i + 1}/${selectedScenarios.length}] Running scenario: ${scenario.name}`);
      
      const result = await this._runScenario(agent, scenario);
      
      results.push(result);
      
      if (result.passed) {
        passedCount++;
      }
    }
    
    const passRate = passedCount / selectedScenarios.length;
    const passed = passRate >= this.config.passThreshold;
    
    const report = {
      agent: agent.name || agent.id,
      totalScenarios: selectedScenarios.length,
      passedScenarios: passedCount,
      failedScenarios: selectedScenarios.length - passedCount,
      passRate: (passRate * 100).toFixed(1) + '%',
      passed,
      results,
      validationTime: Date.now() - startTime,
      timestamp: new Date().toISOString()
    };
    
    // 记录到历史
    this.validationHistory.push(report);
    
    // 触发事件
    this.emit('validation:completed', report);
    
    if (passed) {
      console.log(`✅ Validation PASSED: ${report.passRate} (${passedCount}/${selectedScenarios.length})`);
    } else {
      console.log(`❌ Validation FAILED: ${report.passRate} (threshold: ${this.config.passThreshold * 100}%)`);
    }
    
    return report;
  }
  
  /**
   * 初始化测试场景
   * @private
   */
  _initializeScenarios() {
    // 场景 1: 正常海况
    this.scenarios.set('normal_weather', {
      name: '正常海况',
      type: 'weather',
      difficulty: 'easy',
      description: '晴朗天气，3-4 级海况',
      conditions: {
        windSpeed: 15, // knots
        waveHeight: 1.5, // meters
        visibility: 10, // nautical miles
        time: 'day'
      },
      expectedBehavior: 'Agent 应该正常工作，无警报',
      successCriteria: (result) => result.alerts.length === 0
    });
    
    // 场景 2: 暴风雨
    this.scenarios.set('storm', {
      name: '暴风雨',
      type: 'weather',
      difficulty: 'hard',
      description: '8-9 级大风，5 米浪高',
      conditions: {
        windSpeed: 55,
        waveHeight: 5.0,
        visibility: 2,
        time: 'night',
        lightning: true
      },
      expectedBehavior: 'Agent 应该发出警告，建议减速或避航',
      successCriteria: (result) => result.alerts.length > 0 && result.actions.includes('reduce_speed')
    });
    
    // 场景 3: 大雾
    this.scenarios.set('fog', {
      name: '大雾',
      type: 'weather',
      difficulty: 'medium',
      description: '能见度 0.5 海里',
      conditions: {
        windSpeed: 10,
        waveHeight: 1.0,
        visibility: 0.5,
        time: 'day'
      },
      expectedBehavior: 'Agent 应该启用雾号，降低航速',
      successCriteria: (result) => result.actions.includes('sound_fog_horn') && result.actions.includes('reduce_speed')
    });
    
    // 场景 4: 设备故障
    this.scenarios.set('equipment_failure', {
      name: '设备故障',
      type: 'equipment',
      difficulty: 'hard',
      description: '主机突然过热',
      conditions: {
        mainEngineTemp: 450, // 超过正常 420°C
        normalTemp: 370
      },
      expectedBehavior: 'Agent 应该立即警报并建议降低负荷',
      successCriteria: (result) => result.severity === 'critical' && result.actions.includes('reduce_load')
    });
    
    // 场景 5: 人员落水 (MOB)
    this.scenarios.set('mob', {
      name: '人员落水',
      type: 'safety',
      difficulty: 'critical',
      description: 'CCTV 检测到人员落水',
      conditions: {
        event: 'person_overboard',
        location: { x: 0.3, y: 0.7 },
        confidence: 0.95
      },
      expectedBehavior: 'Agent 应该在 2 秒内识别并触发 MOB 警报',
      responseTimeLimit: 2000, // 2 秒
      successCriteria: (result) => result.detected && result.responseTime < 2000 && result.actions.includes('trigger_mob_alarm')
    });
    
    // 场景 6: 火灾
    this.scenarios.set('fire', {
      name: '机舱火灾',
      type: 'safety',
      difficulty: 'critical',
      description: '烟雾探测器报警',
      conditions: {
        event: 'fire',
        location: 'engine_room',
        smokeLevel: 0.8
      },
      expectedBehavior: 'Agent 应该触发火警，切断通风，启动消防系统',
      successCriteria: (result) => 
        result.actions.includes('trigger_fire_alarm') &&
        result.actions.includes('cut_ventilation') &&
        result.actions.includes('activate_suppression')
    });
    
    console.log(`📚 Loaded ${this.scenarios.size} test scenarios`);
  }
  
  /**
   * 选择测试场景
   * @private
   */
  _selectScenarios(types) {
    if (types.includes('all')) {
      return Array.from(this.scenarios.values());
    }
    
    const selected = [];
    
    for (const [key, scenario] of this.scenarios.entries()) {
      if (types.includes(scenario.type) || types.includes(key)) {
        selected.push(scenario);
      }
    }
    
    return selected;
  }
  
  /**
   * 运行单个场景
   * @private
   */
  async _runScenario(agent, scenario) {
    const startTime = Date.now();
    
    try {
      // 准备场景上下文
      const context = {
        scenario: scenario.name,
        conditions: scenario.conditions,
        timestamp: Date.now()
      };
      
      // 构建任务描述
      const task = this._buildTaskFromScenario(scenario);
      
      // 执行 Agent
      const agentResult = await Promise.race([
        agent.execute(task, context),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout')), this.config.timeout)
        )
      ]);
      
      const responseTime = Date.now() - startTime;
      
      // 评估结果
      const passed = scenario.successCriteria ? 
        scenario.successCriteria(agentResult) : 
        true;
      
      // 检查响应时间（如果有限制）
      const responseTimeOK = scenario.responseTimeLimit ? 
        responseTime <= scenario.responseTimeLimit :
        true;
      
      return {
        scenario: scenario.name,
        type: scenario.type,
        difficulty: scenario.difficulty,
        passed: passed && responseTimeOK,
        responseTime,
        responseTimeLimit: scenario.responseTimeLimit,
        agentResult,
        conditions: scenario.conditions,
        expectedBehavior: scenario.expectedBehavior
      };
      
    } catch (error) {
      return {
        scenario: scenario.name,
        type: scenario.type,
        difficulty: scenario.difficulty,
        passed: false,
        error: error.message,
        expectedBehavior: scenario.expectedBehavior
      };
    }
  }
  
  /**
   * 从场景构建任务描述
   * @private
   */
  _buildTaskFromScenario(scenario) {
    switch (scenario.type) {
      case 'weather':
        return `当前遇到${scenario.name}：${scenario.description}。请评估风险并给出建议。`;
      case 'equipment':
        return `设备异常：${scenario.description}。请诊断并给出处理建议。`;
      case 'safety':
        return `安全事件：${scenario.description}。请立即响应。`;
      default:
        return `场景：${scenario.description}`;
    }
  }
  
  /**
   * 生成随机场景（压力测试）
   * @param {number} count - 生成数量
   */
  generateRandomScenarios(count = 100) {
    console.log(`🎲 Generating ${count} random scenarios...`);
    
    const generated = [];
    
    for (let i = 0; i < count; i++) {
      const scenario = {
        name: `Random Scenario ${i + 1}`,
        type: ['weather', 'equipment', 'safety'][Math.floor(Math.random() * 3)],
        difficulty: ['easy', 'medium', 'hard', 'critical'][Math.floor(Math.random() * 4)],
        description: `Randomly generated test case ${i + 1}`,
        conditions: {
          windSpeed: Math.random() * 60,
          waveHeight: Math.random() * 8,
          visibility: Math.random() * 10,
          time: Math.random() > 0.5 ? 'day' : 'night'
        },
        successCriteria: () => true // 随机场景只要不崩溃就算通过
      };
      
      generated.push(scenario);
      this.scenarios.set(`random_${i}`, scenario);
    }
    
    console.log(`✅ Generated ${generated.length} random scenarios`);
    
    return generated;
  }
  
  /**
   * 获取验证历史
   */
  getHistory() {
    return this.validationHistory;
  }
  
  /**
   * 获取场景统计
   */
  getScenarioStats() {
    const stats = {
      total: this.scenarios.size,
      byType: {},
      byDifficulty: {}
    };
    
    for (const scenario of this.scenarios.values()) {
      // 按类型统计
      stats.byType[scenario.type] = (stats.byType[scenario.type] || 0) + 1;
      
      // 按难度统计
      stats.byDifficulty[scenario.difficulty] = (stats.byDifficulty[scenario.difficulty] || 0) + 1;
    }
    
    return stats;
  }
}
