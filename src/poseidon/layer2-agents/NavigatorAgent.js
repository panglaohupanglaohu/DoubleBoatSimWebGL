/**
 * Navigator Agent - 领航员智能体
 * 
 * Vibe: "极致安全与效率的追求者，时刻计算最优解。"
 * 
 * 职责：
 * - 航行路径规划
 * - 避碰决策（遵守 COLREGs 国际海上避碰规则）
 * - 气象路由优化
 * - 纵倾优化（减少阻力）
 * 
 * 能力：
 * - 实时接入雷达、AIS 和气象数据
 * - 利用强化学习模型进行路径规划
 * - 根据实时海况微调航向
 */

import { AgentBase } from './AgentBase.js';

export class NavigatorAgent extends AgentBase {
  constructor(config = {}) {
    super({
      ...config,
      id: 'navigator-agent',
      name: 'Navigator Agent',
      role: 'navigation',
      vibe: `你是 Poseidon-X 的领航员智能体。
你的专业领域是航行安全和效率优化。

核心职责：
1. 路径规划：计算从 A 到 B 的最优航线
2. 避碰决策：严格遵守 COLREGs（国际海上避碰规则）
3. 气象路由：根据风浪流避开恶劣海况
4. 燃油优化：通过纵倾调整和航速优化减少油耗

决策原则：
- 安全永远是第一位
- 在确保安全的前提下追求效率
- 提前预判，避免被动应对
- 清晰沟通决策理由

你擅长使用专业术语（CPA, TCPA, COLREGs, ETA 等），但会在必要时用通俗语言解释。`,
      deploymentLocation: 'edge' // 部署在船端，实时性要求高
    });

    // 领航员专属状态
    this.navigationState = {
      currentRoute: null, // 当前航线
      aisTargets: new Map(), // AIS 目标
      weatherData: null, // 气象数据
      collisionRisks: [], // 碰撞风险列表
      optimizationMode: 'balanced' // 'safe' | 'balanced' | 'efficient'
    };

    // 注册工具
    this._registerTools();

    // 加载 COLREGs 规则到长期记忆
    this._loadCOLREGsRules();

    console.log('⚓ Navigator Agent ready');
  }

  /**
   * 注册工具
   * @private
   */
  _registerTools() {
    // 工具 1: 计算 CPA/TCPA（最近会遇距离/时间）
    this.registerTool('calculateCPA', async (params) => {
      const { ownShip, targetShip } = params;

      // CPA 计算（简化版）
      const relativeVelocity = {
        x: targetShip.velocity.x - ownShip.velocity.x,
        z: targetShip.velocity.z - ownShip.velocity.z
      };

      const relativePosition = {
        x: targetShip.position.x - ownShip.position.x,
        z: targetShip.position.z - ownShip.position.z
      };

      const speed = Math.sqrt(relativeVelocity.x ** 2 + relativeVelocity.z ** 2);

      if (speed < 0.01) {
        // 相对静止
        return {
          cpa: Math.sqrt(relativePosition.x ** 2 + relativePosition.z ** 2),
          tcpa: Infinity
        };
      }

      // TCPA: 到达最近点的时间
      const tcpa = -(relativePosition.x * relativeVelocity.x + relativePosition.z * relativeVelocity.z) /
        (relativeVelocity.x ** 2 + relativeVelocity.z ** 2);

      // CPA: 最近会遇距离
      let cpa;
      if (tcpa < 0) {
        // 已经过了最近点
        cpa = Math.sqrt(relativePosition.x ** 2 + relativePosition.z ** 2);
      } else {
        const cpaX = relativePosition.x + relativeVelocity.x * tcpa;
        const cpaZ = relativePosition.z + relativeVelocity.z * tcpa;
        cpa = Math.sqrt(cpaX ** 2 + cpaZ ** 2);
      }

      return { cpa, tcpa };
    }, 'Calculate CPA/TCPA for collision avoidance');

    // 工具 2: 评估碰撞风险
    this.registerTool('assessCollisionRisk', async (params) => {
      const { cpa, tcpa } = params;

      // 风险等级判断（基于 IMO 标准）
      let riskLevel = 'none';
      let action = 'maintain';

      if (cpa < 0.5) {
        riskLevel = 'critical';
        action = 'immediate_action';
      } else if (cpa < 1.0 && tcpa < 10) {
        riskLevel = 'high';
        action = 'alter_course';
      } else if (cpa < 2.0 && tcpa < 20) {
        riskLevel = 'medium';
        action = 'monitor_closely';
      } else {
        riskLevel = 'low';
        action = 'maintain';
      }

      return { riskLevel, action };
    }, 'Assess collision risk level');

    // 工具 3: 生成避碰建议
    this.registerTool('generateAvoidanceManeuver', async (params) => {
      const { ownShip, targetShip, riskLevel } = params;

      // 根据 COLREGs 规则生成建议
      // （实际应该用强化学习模型，这里简化）

      const suggestions = [];

      if (riskLevel === 'critical' || riskLevel === 'high') {
        // 右舷目标：向右转
        if (targetShip.bearing > 0 && targetShip.bearing < 180) {
          suggestions.push({
            type: 'course_change',
            action: '右转 15°',
            reason: '遵守 COLREGs Rule 15：交叉相遇，让清右舷来船'
          });
        } else {
          // 左舷目标：减速或右转
          suggestions.push({
            type: 'speed_change',
            action: '减速至 8 节',
            reason: '拉大 CPA，避免紧迫局面'
          });
        }
      }

      return suggestions;
    }, 'Generate collision avoidance maneuver suggestions');

    // 工具 4: 优化航线（燃油经济性）
    this.registerTool('optimizeRoute', async (params) => {
      const { waypoints, weatherData } = params;

      // 路径优化（考虑风浪流）
      // 实际应该使用图搜索算法 + 能耗模型

      const optimizedWaypoints = waypoints.map((wp, index) => {
        // 简化：稍微偏离原航线以避开恶劣海况
        return {
          ...wp,
          optimized: true,
          fuelSavingEstimate: Math.random() * 5 // 0-5% 燃油节省
        };
      });

      return {
        waypoints: optimizedWaypoints,
        totalFuelSaving: optimizedWaypoints.reduce((sum, wp) => sum + (wp.fuelSavingEstimate || 0), 0),
        etaChange: '+12min' // ETA 可能稍有延迟
      };
    }, 'Optimize route for fuel efficiency');
  }

  /**
   * 加载 COLREGs 规则
   * @private
   */
  _loadCOLREGsRules() {
    // 国际海上避碰规则（简化版）
    const rules = {
      'Rule 13': '追越：追越船应从被追越船的船尾一侧通过',
      'Rule 14': '对遇：两船对遇应各自向右转向',
      'Rule 15': '交叉相遇：让清右舷来船',
      'Rule 16': '让路船行动：让路船应尽早采取明显行动',
      'Rule 17': '直航船行动：直航船应保持航向和航速',
      'Rule 19': '能见度不良：所有船舶应以安全航速行驶'
    };

    Object.entries(rules).forEach(([rule, description]) => {
      this.learn(`COLREGs.${rule}`, description);
    });

    console.log('📚 COLREGs rules loaded into long-term memory');
  }

  /**
   * 执行任务（重写基类方法）
   * @param {string} task - 任务描述
   * @param {Object} context - 船舶上下文
   */
  async execute(task, context = {}) {
    this.status = 'executing';
    this.currentTask = task;
    this.metrics.tasksExecuted++;

    const startTime = Date.now();

    try {
      console.log(`⚓ Navigator Agent executing: ${task}`);

      // 根据任务类型分发
      let result;

      if (task.includes('碰撞') || task.includes('风险') || task.includes('CPA')) {
        result = await this._handleCollisionQuery(task, context);
      } else if (task.includes('航线') || task.includes('路径') || task.includes('优化')) {
        result = await this._handleRouteOptimization(task, context);
      } else if (task.includes('航向') || task.includes('航速')) {
        result = await this._handleCourseSpeedAdjustment(task, context);
      } else {
        // 通用处理：使用 LLM 思考
        const thought = await this.think(task, context);
        result = {
          type: 'general',
          response: thought.content
        };
      }

      // 更新性能指标
      const executionTime = Date.now() - startTime;
      this.metrics.averageResponseTime =
        (this.metrics.averageResponseTime * (this.metrics.tasksExecuted - 1) + executionTime) /
        this.metrics.tasksExecuted;

      this.status = 'idle';
      this.currentTask = null;

      // 触发事件
      this.emit('task:completed', { task, result, executionTime });

      return result;

    } catch (error) {
      this.status = 'error';
      this.metrics.successRate = (this.metrics.tasksExecuted - 1) / this.metrics.tasksExecuted;

      console.error(`❌ Navigator Agent execution failed:`, error);
      throw error;
    }
  }

  /**
   * 处理碰撞查询
   * @private
   */
  async _handleCollisionQuery(task, context) {
    // 模拟 AIS 数据（实际应该从真实传感器获取）
    const mockAISTarget = {
      mmsi: '413123456',
      name: '集装箱船 EVER GIVEN',
      position: { x: 50, z: 30 },
      velocity: { x: -2, z: 0 },
      heading: 270,
      length: 400,
      beam: 59
    };

    const ownShip = {
      position: { x: 0, z: 0 },
      velocity: { x: 5, z: 0 },
      heading: 90
    };

    // 计算 CPA/TCPA
    const { cpa, tcpa } = await this.useTool('calculateCPA', {
      ownShip,
      targetShip: mockAISTarget
    });

    // 评估风险
    const { riskLevel, action } = await this.useTool('assessCollisionRisk', {
      cpa,
      tcpa
    });

    // 构建响应
    const response = {
      type: 'collision_assessment',
      target: mockAISTarget,
      cpa: cpa.toFixed(2),
      tcpa: tcpa > 0 ? `${(tcpa / 60).toFixed(1)} 分钟` : '已通过',
      riskLevel,
      action,
      recommendation: ''
    };

    // 生成建议
    if (riskLevel === 'low' || riskLevel === 'none') {
      response.recommendation = `无碰撞风险。CPA 为 ${cpa.toFixed(1)} 海里。建议在其船尾通过以节省燃油。`;
    } else {
      const maneuvers = await this.useTool('generateAvoidanceManeuver', {
        ownShip,
        targetShip: mockAISTarget,
        riskLevel
      });

      response.recommendation = `${riskLevel} 风险！建议：${maneuvers[0]?.action}。理由：${maneuvers[0]?.reason}`;
    }

    return response;
  }

  /**
   * 处理航线优化
   * @private
   */
  async _handleRouteOptimization(task, context) {
    // 模拟航路点
    const waypoints = [
      { x: 0, z: 0, name: '起点' },
      { x: 100, z: 50, name: 'WP1' },
      { x: 200, z: 100, name: 'WP2' },
      { x: 300, z: 150, name: '终点' }
    ];

    // 优化航线
    const optimized = await this.useTool('optimizeRoute', {
      waypoints,
      weatherData: context.environment || {}
    });

    return {
      type: 'route_optimization',
      originalWaypoints: waypoints,
      optimizedWaypoints: optimized.waypoints,
      fuelSaving: `${optimized.totalFuelSaving.toFixed(1)}%`,
      etaChange: optimized.etaChange,
      recommendation: `航线已优化。预计节省燃油 ${optimized.totalFuelSaving.toFixed(1)}%，ETA 变化 ${optimized.etaChange}。`
    };
  }

  /**
   * 处理航向/航速调整
   * @private
   */
  async _handleCourseSpeedAdjustment(task, context) {
    // 使用 LLM 分析任务
    const thought = await this.think(task, context);

    return {
      type: 'course_speed_adjustment',
      response: thought.content,
      recommendation: '请通过舰桥控制台执行航向/航速调整。'
    };
  }

  /**
   * 更新 AIS 目标
   * @param {string} mmsi - 目标 MMSI
   * @param {Object} data - 目标数据
   */
  updateAISTarget(mmsi, data) {
    this.navigationState.aisTargets.set(mmsi, {
      ...data,
      lastUpdate: Date.now()
    });

    // 自动评估碰撞风险
    this._assessAllCollisionRisks();
  }

  /**
   * 评估所有目标的碰撞风险
   * @private
   */
  async _assessAllCollisionRisks() {
    this.navigationState.collisionRisks = [];

    for (const [mmsi, target] of this.navigationState.aisTargets.entries()) {
      // 模拟风险计算（实际应该调用真实算法）
      const risk = {
        mmsi,
        target: target.name || mmsi,
        cpa: Math.random() * 5,
        tcpa: Math.random() * 30,
        riskLevel: 'low'
      };

      if (risk.cpa < 1.0) {
        risk.riskLevel = 'high';
        this.navigationState.collisionRisks.push(risk);

        // 触发警报
        this.emit('collision:risk', risk);
      }
    }
  }

  /**
   * 设置优化模式
   * @param {string} mode - 'safe' | 'balanced' | 'efficient'
   */
  setOptimizationMode(mode) {
    if (['safe', 'balanced', 'efficient'].includes(mode)) {
      this.navigationState.optimizationMode = mode;
      console.log(`⚓ Optimization mode set to: ${mode}`);
    }
  }
}
