/**
 * Safety Agent - 安全官智能体
 * 
 * Vibe: "永不眨眼的守望者，安全是最高指令。"
 * 
 * 职责：
 * - 视觉监控（CCTV 视频流分析）
 * - 应急响应（MOB 人员落水、火灾、烟雾）
 * - 安全巡检（自动检测违规行为）
 * - 应急预案执行
 * 
 * 能力：
 * - 实时分析 CCTV 视频流（计算机视觉）
 * - 检测异常事件（人员落水、烟雾、火焰、闯入）
 * - 自动触发警报和应急程序
 * - 生成逃生/救援方案
 */

import { AgentBase } from './AgentBase.js';

export class SafetyAgent extends AgentBase {
  constructor(config = {}) {
    super({
      ...config,
      id: 'safety-agent',
      name: 'Safety Agent',
      role: 'safety',
      vibe: `你是 Poseidon-X 的安全官智能体。
你是一位永不眨眼的守望者，安全是你的最高指令。

核心职责：
1. 视觉监控：实时分析全船 CCTV 视频流
2. 异常检测：识别人员落水（MOB）、火灾、烟雾、闯入等
3. 应急响应：自动触发警报，切断危险源，引导疏散
4. 安全巡检：检测违规行为（未穿救生衣、吸烟、违章操作）

你的能力：
- 计算机视觉（目标检测、行为识别）
- 多传感器融合（视觉 + 烟雾探测器 + 温度传感器）
- 应急预案数据库（火灾、落水、碰撞等场景）
- 实时定位和路径规划（逃生路线）

决策原则：
- 安全永远第一，不惜代价
- 快速反应，争分夺秒
- 预防为主，防患未然
- 清晰指挥，避免混乱

你的语气坚定、冷静、权威，在紧急情况下直接下达指令。`,
      deploymentLocation: 'edge' // 需要实时响应
    });
    
    // 安全官专属状态
    this.safetyState = {
      cameras: new Map(), // CCTV 摄像头状态
      events: [], // 安全事件历史
      activeAlerts: [], // 当前活跃警报
      drillHistory: [], // 演习历史
      coverage: 0.98, // 监控覆盖率
      emergencyMode: false
    };
    
    this._registerTools();
    this._loadEmergencyProcedures();
    
    console.log('🛡️ Safety Agent ready');
  }
  
  /**
   * 注册工具
   * @private
   */
  _registerTools() {
    // 工具 1: 分析视频帧（计算机视觉）
    this.registerTool('analyzeVideoFrame', async (params) => {
      const { cameraId, frame, timestamp } = params;
      
      // 模拟计算机视觉检测（实际应该调用 YOLO/Faster R-CNN 等模型）
      const detections = [];
      
      // 随机生成检测结果（模拟）
      const anomalyChance = Math.random();
      
      if (anomalyChance < 0.05) {
        // 5% 概率检测到异常
        const anomalies = [
          { type: 'person_overboard', confidence: 0.95, location: { x: 0.3, y: 0.7 } },
          { type: 'smoke', confidence: 0.87, location: { x: 0.5, y: 0.4 } },
          { type: 'fire', confidence: 0.92, location: { x: 0.6, y: 0.5 } },
          { type: 'unauthorized_access', confidence: 0.78, location: { x: 0.2, y: 0.3 } }
        ];
        
        detections.push(anomalies[Math.floor(Math.random() * anomalies.length)]);
      }
      
      return {
        cameraId,
        timestamp,
        detections,
        normalActivity: detections.length === 0
      };
    }, 'Analyze video frame for anomalies (MOB, fire, smoke, etc.)');
    
    // 工具 2: 触发警报
    this.registerTool('triggerAlert', async (params) => {
      const { alertType, severity, location, autoActions } = params;
      
      console.log(`🚨 ALERT TRIGGERED: ${alertType} (Severity: ${severity})`);
      
      // 自动执行的动作
      const executedActions = [];
      
      if (autoActions) {
        if (autoActions.includes('sound_alarm')) {
          console.log('🔊 General alarm activated');
          executedActions.push('全船警报已启动');
        }
        
        if (autoActions.includes('cut_ventilation')) {
          console.log('💨 Ventilation system shut down');
          executedActions.push('通风系统已切断');
        }
        
        if (autoActions.includes('activate_sprinklers')) {
          console.log('💧 Fire suppression system activated');
          executedActions.push('消防喷淋系统已启动');
        }
        
        if (autoActions.includes('notify_captain')) {
          console.log('📞 Captain notified');
          executedActions.push('已通知船长');
        }
      }
      
      return {
        alertType,
        severity,
        location,
        executedActions,
        timestamp: new Date().toISOString()
      };
    }, 'Trigger emergency alert and auto-actions');
    
    // 工具 3: 生成逃生路线
    this.registerTool('generateEvacuationRoute', async (params) => {
      const { fromLocation, emergencyType } = params;
      
      // 简化的路径规划（实际应该用 A* 算法 + 动态避障）
      const routes = {
        'fire': [
          { step: 1, action: '前往最近的防火门' },
          { step: 2, action: '沿着应急照明标志向集合点移动' },
          { step: 3, action: '到达甲板集合点 Muster Station A' },
          { step: 4, action: '等待船长指令' }
        ],
        'flooding': [
          { step: 1, action: '立即向上层甲板移动' },
          { step: 2, action: '关闭水密门' },
          { step: 3, action: '到达甲板集合点' },
          { step: 4, action: '准备弃船（如需要）' }
        ],
        'collision': [
          { step: 1, action: '穿戴救生衣' },
          { step: 2, action: '到达集合点' },
          { step: 3, action: '等待弃船指令' }
        ]
      };
      
      const route = routes[emergencyType] || routes['fire'];
      
      return {
        fromLocation,
        emergencyType,
        route,
        estimatedTime: '3-5 分钟',
        safetyLevel: 'high'
      };
    }, 'Generate evacuation route based on emergency type');
    
    // 工具 4: 评估安全态势
    this.registerTool('assessSafetySituation', async (params) => {
      const { period } = params;
      
      // 统计过去 N 小时的安全事件
      const now = Date.now();
      const periodMs = period * 3600000;
      
      const recentEvents = this.safetyState.events.filter(e => {
        return (now - new Date(e.timestamp).getTime()) < periodMs;
      });
      
      const eventTypes = {
        critical: recentEvents.filter(e => e.severity === 'critical').length,
        warning: recentEvents.filter(e => e.severity === 'warning').length,
        info: recentEvents.filter(e => e.severity === 'info').length
      };
      
      const overallStatus = eventTypes.critical > 0 ? 'critical' :
                           eventTypes.warning > 3 ? 'warning' : 'good';
      
      return {
        period: `${period} 小时`,
        totalEvents: recentEvents.length,
        eventTypes,
        overallStatus,
        coverage: this.safetyState.coverage,
        recommendation: overallStatus === 'good' ? 
          '安全态势良好，继续保持警惕。' :
          `发现 ${eventTypes.critical} 个严重事件，${eventTypes.warning} 个警告。建议加强巡查。`
      };
    }, 'Assess overall safety situation');
  }
  
  /**
   * 加载应急程序
   * @private
   */
  _loadEmergencyProcedures() {
    const procedures = {
      'MOB': {
        name: '人员落水应急程序',
        steps: [
          '立即喊叫 "Man Overboard!" 并指明方向',
          '投放救生圈和烟雾信号',
          '记录落水位置（GPS）',
          '启动 MOB 按钮（自动记录位置和时间）',
          '通知驾驶台，执行 Williamson Turn',
          '准备救生艇'
        ],
        responseTime: '< 2 秒（检测）+ 30 秒（投放救生圈）'
      },
      'Fire': {
        name: '火灾应急程序',
        steps: [
          '启动火灾警报',
          '切断火源区域的电源和通风',
          '组织灭火小组',
          '使用适当的灭火器材（CO2/泡沫/水）',
          '如失控，准备弃船'
        ],
        responseTime: '< 5 秒（检测）+ 1 分钟（启动消防系统）'
      },
      'Flooding': {
        name: '进水应急程序',
        steps: [
          '定位进水点',
          '关闭相关水密门',
          '启动应急泵',
          '评估稳性影响',
          '必要时进行反压载'
        ],
        responseTime: '< 3 分钟'
      }
    };
    
    Object.entries(procedures).forEach(([type, procedure]) => {
      this.learn(`Emergency.${type}`, procedure);
    });
    
    console.log('📚 Emergency procedures loaded');
  }
  
  /**
   * 执行任务
   */
  async execute(task, context = {}) {
    this.status = 'executing';
    this.currentTask = task;
    this.metrics.tasksExecuted++;
    
    const startTime = Date.now();
    
    try {
      console.log(`🛡️ Safety Agent executing: ${task}`);
      
      let result;
      
      if (task.includes('监控') || task.includes('安全') || task.includes('态势')) {
        result = await this._handleSafetyAssessment(task, context);
      } else if (task.includes('落水') || task.includes('MOB')) {
        result = await this._handleMOBScenario(task, context);
      } else if (task.includes('火灾') || task.includes('烟雾')) {
        result = await this._handleFireScenario(task, context);
      } else if (task.includes('演习') || task.includes('drill')) {
        result = await this._handleDrillScenario(task, context);
      } else {
        const thought = await this.think(task, context);
        result = {
          type: 'general',
          response: thought.content
        };
      }
      
      const executionTime = Date.now() - startTime;
      this.status = 'idle';
      this.currentTask = null;
      
      this.emit('task:completed', { task, result, executionTime });
      
      return result;
      
    } catch (error) {
      this.status = 'error';
      console.error(`❌ Safety Agent execution failed:`, error);
      throw error;
    }
  }
  
  /**
   * 处理安全态势评估
   * @private
   */
  async _handleSafetyAssessment(task, context) {
    const assessment = await this.useTool('assessSafetySituation', {
      period: 24 // 过去 24 小时
    });
    
    return {
      type: 'safety_assessment',
      assessment,
      response: `安全态势评估（过去 ${assessment.period}）：\n状态：${assessment.overallStatus.toUpperCase()}\n总事件数：${assessment.totalEvents}\n监控覆盖率：${(assessment.coverage * 100).toFixed(0)}%\n\n${assessment.recommendation}`
    };
  }
  
  /**
   * 处理人员落水场景
   * @private
   */
  async _handleMOBScenario(task, context) {
    console.log('🚨 MOB SCENARIO ACTIVATED');
    
    // 触发警报
    const alert = await this.useTool('triggerAlert', {
      alertType: 'MOB',
      severity: 'critical',
      location: { deck: 'main', side: 'starboard' },
      autoActions: ['sound_alarm', 'notify_captain']
    });
    
    // 获取应急程序
    const procedure = this.recall('Emergency.MOB');
    
    // 生成救援方案
    const response = `🚨 人员落水警报！\n\n执行的自动动作：\n${alert.executedActions.join('\n')}\n\n应急程序：\n${procedure.steps.map((s, i) => `${i + 1}. ${s}`).join('\n')}\n\n响应时间要求：${procedure.responseTime}`;
    
    // 记录事件
    this.safetyState.events.push({
      type: 'MOB',
      severity: 'critical',
      timestamp: new Date().toISOString(),
      actions: alert.executedActions
    });
    
    return {
      type: 'mob_response',
      alert,
      procedure,
      response
    };
  }
  
  /**
   * 处理火灾场景
   * @private
   */
  async _handleFireScenario(task, context) {
    console.log('🔥 FIRE SCENARIO ACTIVATED');
    
    // 触发警报
    const alert = await this.useTool('triggerAlert', {
      alertType: 'Fire',
      severity: 'critical',
      location: { deck: 'engine_room', zone: 'B' },
      autoActions: ['sound_alarm', 'cut_ventilation', 'activate_sprinklers', 'notify_captain']
    });
    
    // 生成逃生路线
    const evacuation = await this.useTool('generateEvacuationRoute', {
      fromLocation: 'engine_room',
      emergencyType: 'fire'
    });
    
    const procedure = this.recall('Emergency.Fire');
    
    const response = `🔥 火灾警报！机舱 B 区检测到火情！\n\n执行的自动动作：\n${alert.executedActions.join('\n')}\n\n逃生路线：\n${evacuation.route.map(r => `步骤 ${r.step}: ${r.action}`).join('\n')}\n\n预计逃生时间：${evacuation.estimatedTime}`;
    
    // 进入应急模式
    this.safetyState.emergencyMode = true;
    
    this.safetyState.events.push({
      type: 'Fire',
      severity: 'critical',
      timestamp: new Date().toISOString(),
      actions: alert.executedActions
    });
    
    return {
      type: 'fire_response',
      alert,
      evacuation,
      response
    };
  }
  
  /**
   * 处理演习场景
   * @private
   */
  async _handleDrillScenario(task, context) {
    const drillType = task.includes('火灾') ? 'Fire' : 
                     task.includes('落水') ? 'MOB' : 'General';
    
    console.log(`🎯 Drill scenario: ${drillType}`);
    
    const drill = {
      type: drillType,
      startTime: new Date().toISOString(),
      participants: context.crewCount || 20,
      scenario: `模拟 ${drillType} 应急场景`,
      objectives: [
        '测试警报系统响应',
        '检验船员应急反应时间',
        '评估应急设备状态',
        '优化应急流程'
      ],
      status: 'in_progress'
    };
    
    this.safetyState.drillHistory.push(drill);
    
    return {
      type: 'drill',
      drill,
      response: `${drillType} 演习已启动。\n\n演习目标：\n${drill.objectives.map((o, i) => `${i + 1}. ${o}`).join('\n')}\n\n请全体船员按照应急程序执行。演习数据将用于后续分析和优化。`
    };
  }
  
  /**
   * 监控摄像头（持续运行）
   * @param {string} cameraId 
   * @param {Object} frameData 
   */
  async monitorCamera(cameraId, frameData) {
    const analysis = await this.useTool('analyzeVideoFrame', {
      cameraId,
      frame: frameData,
      timestamp: Date.now()
    });
    
    // 如果检测到异常
    if (analysis.detections.length > 0) {
      for (const detection of analysis.detections) {
        // 自动触发应急响应
        await this._handleDetection(detection, cameraId);
      }
    }
    
    // 更新摄像头状态
    this.safetyState.cameras.set(cameraId, {
      lastFrame: Date.now(),
      status: 'active',
      detections: analysis.detections
    });
  }
  
  /**
   * 处理检测结果
   * @private
   */
  async _handleDetection(detection, cameraId) {
    console.log(`🚨 Anomaly detected on camera ${cameraId}:`, detection.type);
    
    let autoActions = [];
    let severity = 'warning';
    
    switch (detection.type) {
      case 'person_overboard':
        autoActions = ['sound_alarm', 'notify_captain'];
        severity = 'critical';
        break;
      case 'fire':
        autoActions = ['sound_alarm', 'cut_ventilation', 'activate_sprinklers', 'notify_captain'];
        severity = 'critical';
        break;
      case 'smoke':
        autoActions = ['sound_alarm', 'notify_captain'];
        severity = 'critical';
        break;
      case 'unauthorized_access':
        autoActions = ['notify_captain'];
        severity = 'warning';
        break;
    }
    
    // 如果置信度足够高，触发警报
    if (detection.confidence > 0.8) {
      await this.useTool('triggerAlert', {
        alertType: detection.type,
        severity,
        location: { camera: cameraId, position: detection.location },
        autoActions
      });
    }
    
    // 触发事件
    this.emit('detection:confirmed', { detection, cameraId });
  }
  
  /**
   * 获取安全仪表盘
   */
  getSafetyDashboard() {
    return {
      emergencyMode: this.safetyState.emergencyMode,
      activeAlerts: this.safetyState.activeAlerts,
      cameras: Array.from(this.safetyState.cameras.entries()).map(([id, data]) => ({
        id,
        status: data.status,
        lastUpdate: Date.now() - data.lastFrame
      })),
      recentEvents: this.safetyState.events.slice(-10),
      coverage: this.safetyState.coverage
    };
  }
  
  /**
   * 解除应急模式
   */
  clearEmergencyMode() {
    this.safetyState.emergencyMode = false;
    this.safetyState.activeAlerts = [];
    console.log('✅ Emergency mode cleared');
  }
}
