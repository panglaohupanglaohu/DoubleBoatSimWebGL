/**
 * Engineer Agent - 轮机长智能体
 * 
 * Vibe: "经验丰富的老轨，能听懂机器的呻吟。"
 * 
 * 职责：
 * - 设备健康管理（PHM - Prognostics and Health Management）
 * - 能效监控与优化
 * - 预测性维护
 * - 故障诊断
 * 
 * 能力：
 * - 监听全船 2000+ 个传感器（温度、压力、振动）
 * - 结合设备说明书和历史维修记录进行故障推理
 * - 生成维护建议和备件需求
 */

import { AgentBase } from './AgentBase.js';

export class EngineerAgent extends AgentBase {
  constructor(config = {}) {
    super({
      ...config,
      id: 'engineer-agent',
      name: 'Engineer Agent',
      role: 'engineering',
      vibe: `你是 Poseidon-X 的轮机长智能体。
你是一位经验丰富的老轨，精通船舶机械和电气系统。

核心职责：
1. 设备健康管理：监控主机、辅机、泵、发电机等 2000+ 个设备
2. 预测性维护：提前发现潜在故障，避免停机
3. 能效优化：分析燃油消耗，提供节能建议
4. 故障诊断：根据症状推理根因，提供维修方案

你的能力：
- 能"听懂"机器的异常声音（振动频谱分析）
- 能"看见"设备的疲劳（趋势预测）
- 能"预知"故障（基于历史数据和物理模型）

决策原则：
- 安全可靠是第一位
- 预防胜于治疗
- 数据驱动，不凭经验主义
- 清晰沟通，便于船员执行

你擅长用"老轨"的语气说话，专业但不晦涩。`,
      deploymentLocation: 'edge' // 部署在船端
    });
    
    // 轮机长专属状态
    this.engineeringState = {
      sensors: new Map(), // 传感器实时数据
      equipment: new Map(), // 设备状态
      alerts: [], // 告警列表
      maintenancePlan: [], // 维护计划
      fuelConsumption: {
        hourly: 0,
        daily: 0,
        trend: []
      },
      healthScores: new Map() // 设备健康评分
    };
    
    // 注册工具
    this._registerTools();
    
    // 加载设备知识库
    this._loadEquipmentKnowledge();
    
    console.log('⚙️ Engineer Agent ready');
  }
  
  /**
   * 注册工具
   * @private
   */
  _registerTools() {
    // 工具 1: 分析排温异常
    this.registerTool('analyzeExhaustTemp', async (params) => {
      const { cylinderNo, temperature, normalRange } = params;
      
      const deviation = temperature - normalRange.avg;
      const deviationPercent = (deviation / normalRange.avg * 100).toFixed(1);
      
      let diagnosis = '';
      let severity = 'normal';
      let action = '';
      
      if (Math.abs(deviation) < 10) {
        diagnosis = '排温正常';
        severity = 'normal';
        action = '无需操作';
      } else if (deviation > 10 && deviation < 30) {
        diagnosis = `${cylinderNo} 号缸排温偏高 ${deviationPercent}%`;
        severity = 'warning';
        action = '建议下次停泊时检查喷油嘴';
      } else if (deviation > 30) {
        diagnosis = `${cylinderNo} 号缸排温严重偏高 ${deviationPercent}%！`;
        severity = 'critical';
        action = '立即降低负荷，检查是否有喷油嘴堵塞或气门泄漏';
      } else if (deviation < -20) {
        diagnosis = `${cylinderNo} 号缸排温过低`;
        severity = 'warning';
        action = '可能喷油不足，检查燃油系统';
      }
      
      return {
        diagnosis,
        severity,
        action,
        deviation,
        deviationPercent
      };
    }, 'Analyze exhaust temperature anomaly');
    
    // 工具 2: 计算设备健康评分
    this.registerTool('calculateHealthScore', async (params) => {
      const { equipmentId, sensorData, historicalData } = params;
      
      // 简化的健康评分算法
      // 实际应该使用机器学习模型（例如 Isolation Forest 检测异常）
      
      let score = 100;
      const issues = [];
      
      // 检查温度
      if (sensorData.temperature) {
        if (sensorData.temperature > sensorData.temperatureLimit * 0.9) {
          score -= 15;
          issues.push('温度接近上限');
        }
      }
      
      // 检查振动
      if (sensorData.vibration) {
        if (sensorData.vibration > sensorData.vibrationLimit * 0.8) {
          score -= 20;
          issues.push('振动异常');
        }
      }
      
      // 检查运行时长
      if (sensorData.runningHours) {
        const maintenanceInterval = 8000; // 8000 小时保养周期
        const hoursUntilMaintenance = maintenanceInterval - (sensorData.runningHours % maintenanceInterval);
        
        if (hoursUntilMaintenance < 500) {
          score -= 10;
          issues.push(`距离保养剩余 ${hoursUntilMaintenance} 小时`);
        }
      }
      
      return {
        equipmentId,
        healthScore: Math.max(0, score),
        status: score > 80 ? 'healthy' : score > 60 ? 'warning' : 'critical',
        issues,
        nextMaintenanceDue: sensorData.runningHours ? `${8000 - (sensorData.runningHours % 8000)} 小时后` : '未知'
      };
    }, 'Calculate equipment health score');
    
    // 工具 3: 生成维护建议
    this.registerTool('generateMaintenancePlan', async (params) => {
      const { equipmentList, currentDate } = params;
      
      const plan = equipmentList.map((eq, index) => {
        return {
          equipmentId: eq.id,
          equipmentName: eq.name,
          priority: eq.healthScore < 70 ? 'high' : 'normal',
          scheduledDate: new Date(Date.now() + (index + 1) * 86400000).toISOString().split('T')[0],
          tasks: [
            '检查主要部件磨损情况',
            '更换润滑油和滤芯',
            '测量关键参数',
            '记录保养数据'
          ],
          estimatedDuration: '4 小时',
          requiredParts: eq.healthScore < 70 ? ['密封圈', '轴承'] : []
        };
      });
      
      return {
        plan,
        totalTasks: plan.length,
        highPriorityCount: plan.filter(p => p.priority === 'high').length
      };
    }, 'Generate predictive maintenance plan');
    
    // 工具 4: 燃油消耗分析
    this.registerTool('analyzeFuelConsumption', async (params) => {
      const { period, data } = params;
      
      // 分析燃油消耗趋势
      const average = data.reduce((sum, val) => sum + val, 0) / data.length;
      const trend = data[data.length - 1] > average ? 'increasing' : 'decreasing';
      
      const efficiency = 100 - ((data[data.length - 1] - average) / average * 100);
      
      return {
        period,
        averageConsumption: average.toFixed(2),
        currentConsumption: data[data.length - 1].toFixed(2),
        trend,
        efficiency: efficiency.toFixed(1) + '%',
        recommendation: trend === 'increasing' ? 
          '油耗上升。建议：1) 清洁主机；2) 检查螺旋桨是否有海生物附着；3) 优化航速。' :
          '油耗控制良好，继续保持。'
      };
    }, 'Analyze fuel consumption trends');
  }
  
  /**
   * 加载设备知识库
   * @private
   */
  _loadEquipmentKnowledge() {
    // 设备正常运行参数范围
    const equipmentSpecs = {
      'MainEngine': {
        exhaustTemp: { min: 320, max: 420, avg: 370, unit: '°C' },
        rpm: { min: 80, max: 120, avg: 100, unit: 'RPM' },
        lubOilPress: { min: 2.5, max: 4.5, avg: 3.5, unit: 'bar' }
      },
      'Generator1': {
        loadPercent: { min: 30, max: 85, avg: 60, unit: '%' },
        frequency: { min: 59.5, max: 60.5, avg: 60, unit: 'Hz' }
      },
      'AirCompressor': {
        pressure: { min: 25, max: 30, avg: 27, unit: 'bar' },
        temperature: { min: 80, max: 120, avg: 95, unit: '°C' }
      }
    };
    
    Object.entries(equipmentSpecs).forEach(([equipment, specs]) => {
      this.learn(`Equipment.${equipment}.Specs`, specs);
    });
    
    // 常见故障模式
    const faultPatterns = {
      '排温偏高': ['喷油嘴堵塞', '气门泄漏', '冷却水不足', '增压器效率下降'],
      '振动异常': ['轴系不对中', '螺旋桨损伤', '轴承磨损', '平衡重失调'],
      '油压下降': ['滤芯堵塞', '油泵磨损', '管路泄漏', '润滑油粘度下降']
    };
    
    Object.entries(faultPatterns).forEach(([symptom, causes]) => {
      this.learn(`FaultPattern.${symptom}`, causes);
    });
    
    console.log('📚 Equipment knowledge loaded into long-term memory');
  }
  
  /**
   * 执行任务（重写基类方法）
   */
  async execute(task, context = {}) {
    this.status = 'executing';
    this.currentTask = task;
    this.metrics.tasksExecuted++;
    
    const startTime = Date.now();
    
    try {
      console.log(`⚙️ Engineer Agent executing: ${task}`);
      
      let result;
      
      if (task.includes('主机') || task.includes('排温') || task.includes('engine')) {
        result = await this._handleMainEngineQuery(task, context);
      } else if (task.includes('能效') || task.includes('燃油') || task.includes('fuel')) {
        result = await this._handleFuelEfficiencyQuery(task, context);
      } else if (task.includes('维护') || task.includes('保养') || task.includes('maintenance')) {
        result = await this._handleMaintenanceQuery(task, context);
      } else if (task.includes('设备') || task.includes('故障') || task.includes('equipment')) {
        result = await this._handleEquipmentQuery(task, context);
      } else {
        // 通用处理
        const thought = await this.think(task, context);
        result = {
          type: 'general',
          response: thought.content
        };
      }
      
      const executionTime = Date.now() - startTime;
      this.metrics.averageResponseTime = 
        (this.metrics.averageResponseTime * (this.metrics.tasksExecuted - 1) + executionTime) / 
        this.metrics.tasksExecuted;
      
      this.status = 'idle';
      this.currentTask = null;
      
      this.emit('task:completed', { task, result, executionTime });
      
      return result;
      
    } catch (error) {
      this.status = 'error';
      console.error(`❌ Engineer Agent execution failed:`, error);
      throw error;
    }
  }
  
  /**
   * 处理主机查询
   * @private
   */
  async _handleMainEngineQuery(task, context) {
    // 模拟主机传感器数据
    const cylinderTemps = [370, 380, 385, 375, 372, 368]; // 6 个气缸
    const normalRange = { min: 350, max: 400, avg: 370 };
    
    // 分析每个气缸
    const analyses = [];
    for (let i = 0; i < cylinderTemps.length; i++) {
      const analysis = await this.useTool('analyzeExhaustTemp', {
        cylinderNo: i + 1,
        temperature: cylinderTemps[i],
        normalRange
      });
      
      if (analysis.severity !== 'normal') {
        analyses.push(analysis);
      }
    }
    
    // 构建响应
    let response = '主机运行正常。';
    
    if (analyses.length > 0) {
      const warnings = analyses.filter(a => a.severity === 'warning');
      const criticals = analyses.filter(a => a.severity === 'critical');
      
      if (criticals.length > 0) {
        response = `⚠️ 主机异常！${criticals.map(a => a.diagnosis).join('；')}。${criticals[0].action}`;
      } else if (warnings.length > 0) {
        response = `主机运行正常，但有轻微异常。${warnings.map(a => a.diagnosis).join('；')}。${warnings[0].action}`;
      }
    } else {
      response = `主机运行正常。平均排温 ${(cylinderTemps.reduce((a,b) => a+b) / cylinderTemps.length).toFixed(0)}°C，各缸均衡良好。`;
    }
    
    return {
      type: 'main_engine_status',
      cylinderTemps,
      analyses,
      response,
      overallStatus: analyses.some(a => a.severity === 'critical') ? 'critical' : 
                     analyses.length > 0 ? 'warning' : 'healthy'
    };
  }
  
  /**
   * 处理燃油效率查询
   * @private
   */
  async _handleFuelEfficiencyQuery(task, context) {
    // 模拟燃油消耗数据（过去 7 天，单位：升/小时）
    const fuelData = [
      220, 218, 225, 230, 228, 235, 240
    ];
    
    const analysis = await this.useTool('analyzeFuelConsumption', {
      period: 'last_7_days',
      data: fuelData
    });
    
    return {
      type: 'fuel_efficiency',
      data: fuelData,
      analysis,
      response: `燃油消耗分析（过去7天）：\n平均 ${analysis.averageConsumption} L/h，当前 ${analysis.currentConsumption} L/h。\n趋势：${analysis.trend === 'increasing' ? '上升 ⬆️' : '下降 ⬇️'}。\n能效评分：${analysis.efficiency}。\n\n${analysis.recommendation}`
    };
  }
  
  /**
   * 处理维护查询
   * @private
   */
  async _handleMaintenanceQuery(task, context) {
    // 模拟设备列表
    const equipmentList = [
      { id: 'ME-01', name: '主机', healthScore: 85 },
      { id: 'GE-01', name: '1号发电机', healthScore: 72 },
      { id: 'GE-02', name: '2号发电机', healthScore: 88 },
      { id: 'AC-01', name: '空压机', healthScore: 65 }
    ];
    
    const maintenancePlan = await this.useTool('generateMaintenancePlan', {
      equipmentList,
      currentDate: new Date().toISOString()
    });
    
    return {
      type: 'maintenance_plan',
      plan: maintenancePlan.plan,
      response: `已生成维护计划，共 ${maintenancePlan.totalTasks} 项任务，其中 ${maintenancePlan.highPriorityCount} 项高优先级。\n\n重点关注：${maintenancePlan.plan.filter(p => p.priority === 'high').map(p => p.equipmentName).join('、')}。`
    };
  }
  
  /**
   * 处理设备查询
   * @private
   */
  async _handleEquipmentQuery(task, context) {
    // 模拟设备传感器数据
    const mockSensorData = {
      temperature: 95,
      temperatureLimit: 120,
      vibration: 4.5,
      vibrationLimit: 8.0,
      runningHours: 7600
    };
    
    const healthReport = await this.useTool('calculateHealthScore', {
      equipmentId: 'ME-01',
      sensorData: mockSensorData,
      historicalData: []
    });
    
    return {
      type: 'equipment_health',
      healthReport,
      response: `设备健康评分：${healthReport.healthScore} 分 (${healthReport.status})。\n问题：${healthReport.issues.join('、') || '无'}。\n下次保养：${healthReport.nextMaintenanceDue}。`
    };
  }
  
  /**
   * 监控传感器（持续运行）
   * @param {string} sensorId - 传感器 ID
   * @param {*} value - 传感器值
   */
  updateSensor(sensorId, value) {
    this.engineeringState.sensors.set(sensorId, {
      value,
      timestamp: Date.now()
    });
    
    // 自动检测异常
    this._detectAnomalies(sensorId, value);
  }
  
  /**
   * 检测异常
   * @private
   */
  _detectAnomalies(sensorId, value) {
    // 简单的阈值检测（实际应该用时序异常检测算法）
    const thresholds = {
      'MainEngine.ExhaustTemp.Cyl1': { min: 350, max: 400 },
      'MainEngine.ExhaustTemp.Cyl2': { min: 350, max: 400 },
      'MainEngine.LubOilPress': { min: 2.5, max: 4.5 }
    };
    
    const threshold = thresholds[sensorId];
    
    if (threshold && (value < threshold.min || value > threshold.max)) {
      const alert = {
        sensorId,
        value,
        threshold,
        severity: value < threshold.min * 0.8 || value > threshold.max * 1.2 ? 'critical' : 'warning',
        timestamp: new Date().toISOString()
      };
      
      this.engineeringState.alerts.push(alert);
      
      // 触发事件
      this.emit('anomaly:detected', alert);
      
      console.warn(`⚠️ Anomaly detected: ${sensorId} = ${value}`);
    }
  }
  
  /**
   * 获取设备健康仪表盘
   */
  getHealthDashboard() {
    return {
      sensors: Array.from(this.engineeringState.sensors.entries()).map(([id, data]) => ({
        id,
        value: data.value,
        age: Date.now() - data.timestamp
      })),
      alerts: this.engineeringState.alerts,
      healthScores: Array.from(this.engineeringState.healthScores.entries()),
      fuelConsumption: this.engineeringState.fuelConsumption
    };
  }
}
