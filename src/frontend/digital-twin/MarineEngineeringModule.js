/**
 * MarineEngineeringModule - 船舶工程增强模块
 * 
 * 为 Poseidon-X 系统添加专业船舶工程计算能力
 * 基于真实船舶理论和 IMO 规范
 */

import { CatamaranStabilityCalculator } from '../physics/CatamaranStability.js';
import { ShipMotionResponse } from '../physics/ShipMotionResponse.js';

/**
 * 船舶工程计算引擎
 */
export class MarineEngineeringModule {
  constructor(config = {}) {
    this.config = {
      // 默认双体船参数 (138 米双体客船)
      shipType: config.shipType || 'catamaran',
      length: config.length || 138,
      beam: config.beam || 26,
      draft: config.draft || 5.5,
      displacement: config.displacement || 37000,
      hullSpacing: config.hullSpacing || 80, // 两片体中心距 (m)
      GMt: config.GMt || 15,
      GMl: config.GMl || 120,
      
      // IMO 稳性衡准参数
      imoCriteria: {
        minGMt: 0.15,           // 最小初稳性高度 (m)
        maxGZ: 0.2,             // 最大 GZ 值 (m)
        maxRollAngle: 30,       // 最大横倾角 (度)
        weatherCriterion: 1.0   // 天气衡准
      }
    };
    
    // 初始化计算器
    this.stabilityCalc = new CatamaranStabilityCalculator(this.config);
    this.motionResponse = new ShipMotionResponse(this.config);
    
    // 实时状态
    this.realtimeState = {
      stability: null,
      motion: null,
      alerts: [],
      recommendations: []
    };
    
    console.log('⚓ Marine Engineering Module initialized');
  }
  
  /**
   * 实时稳定性监控
   * @param {object} sensorData - 传感器实时数据
   * @returns {object} 稳定性分析结果
   */
  monitorStability(sensorData) {
    const { roll, pitch, heave, speed, heading } = sensorData;
    
    // 计算当前 GMt（参数顺序：displacement, hullSpacing, beam）
    const gmData = this.stabilityCalc.calculateGMt(
      this.config.displacement,
      this.config.hullSpacing,
      this.config.beam
    );
    
    // 计算摇摆周期
    const rollPeriod = this.stabilityCalc.calculateRollPeriod(gmData.GMt, this.config.beam);
    const pitchPeriod = this.stabilityCalc.calculatePitchPeriod(gmData.GMt * 0.8, this.config.length);
    
    // 评估稳定性
    const assessment = this.stabilityCalc.assessStability(roll, pitch, gmData.GMt);
    
    // 检查 IMO 稳性衡准
    const imoCompliance = this.checkIMOCriteria(gmData.GMt, roll);
    
    // 生成告警
    const alerts = this.generateStabilityAlerts(assessment, imoCompliance);
    
    this.realtimeState.stability = {
      timestamp: Date.now(),
      GMt: gmData.GMt.toFixed(2),
      rollPeriod: rollPeriod.toFixed(2),
      pitchPeriod: pitchPeriod.toFixed(2),
      rollAngle: roll.toFixed(2),
      pitchAngle: pitch.toFixed(2),
      assessment,
      imoCompliance,
      alerts
    };
    
    return this.realtimeState.stability;
  }
  
  /**
   * 检查 IMO 稳性衡准
   */
  checkIMOCriteria(GMt, rollAngle) {
    const criteria = this.config.imoCriteria;
    const compliance = {
      passed: true,
      violations: [],
      warnings: []
    };
    
    // 1. 最小 GMt 检查
    if (GMt < criteria.minGMt) {
      compliance.passed = false;
      compliance.violations.push(`GMt (${GMt.toFixed(2)}m) < 最小要求 (${criteria.minGMt}m)`);
    } else if (GMt < criteria.minGMt * 1.5) {
      compliance.warnings.push(`GMt 偏低 (${GMt.toFixed(2)}m)`);
    }
    
    // 2. 横倾角检查
    if (Math.abs(rollAngle) > criteria.maxRollAngle) {
      compliance.passed = false;
      compliance.violations.push(`横倾角 (${Math.abs(rollAngle).toFixed(1)}°) > 最大允许 (${criteria.maxRollAngle}°)`);
    }
    
    // 3. GZ 曲线检查（简化）
    const gzCurve = this.stabilityCalc.calculateStabilityCurve(GMt);
    const maxGZ = Math.max(...gzCurve.map(p => p.GZ));
    
    if (maxGZ < criteria.maxGZ) {
      compliance.warnings.push(`最大 GZ (${maxGZ.toFixed(3)}m) 偏小`);
    }
    
    return compliance;
  }
  
  /**
   * 生成稳定性告警
   */
  generateStabilityAlerts(assessment, imoCompliance) {
    const alerts = [];
    
    // IMO 违规告警
    imoCompliance.violations.forEach(violation => {
      alerts.push({
        level: 'critical',
        type: 'IMO_VIOLATION',
        message: `IMO 稳性违规：${violation}`,
        action: '立即减速并调整航向'
      });
    });
    
    // 稳定性警告
    assessment.warnings.forEach(warning => {
      alerts.push({
        level: 'warning',
        type: 'STABILITY_WARNING',
        message: warning,
        action: '密切监控船舶状态'
      });
    });
    
    // 稳定性问题
    assessment.issues.forEach(issue => {
      alerts.push({
        level: 'critical',
        type: 'STABILITY_ISSUE',
        message: issue,
        action: '立即采取纠正措施'
      });
    });
    
    return alerts;
  }
  
  /**
   * 运动响应分析
   * @param {object} waveData - 波浪数据
   * @returns {object} 运动分析结果
   */
  analyzeMotion(waveData) {
    const { significantWaveHeight, meanWavePeriod, waveDirection } = waveData;
    
    // 模拟不规则波中的运动
    const motionData = this.motionResponse.simulateIrregularMotion(
      significantWaveHeight,
      meanWavePeriod,
      60, // 60 秒模拟
      0.5 // 0.5 秒步长
    );
    
    // 计算统计参数
    const stats = this.motionResponse.calculateMotionStatistics();
    
    // 晕船风险评估
    const comfort = this.motionResponse.assessMotionComfort();
    
    // 计算 RAO
    const rao = {
      roll: this.motionResponse.calculateRAO('roll', meanWavePeriod, waveDirection),
      pitch: this.motionResponse.calculateRAO('pitch', meanWavePeriod, waveDirection),
      heave: this.motionResponse.calculateRAO('heave', meanWavePeriod, waveDirection)
    };
    
    this.realtimeState.motion = {
      timestamp: Date.now(),
      waveConditions: waveData,
      statistics: stats,
      comfort,
      rao,
      motionData
    };
    
    return this.realtimeState.motion;
  }
  
  /**
   * 能效分析
   * @param {object} engineData - 主机数据
   * @param {object} resistanceData - 阻力数据
   * @returns {object} 能效分析结果
   */
  analyzeEfficiency(engineData, resistanceData) {
    const { rpm, torque, fuelRate } = engineData;
    const { totalResistance, speed } = resistanceData;
    
    // 计算有效功率
    const effectivePower = totalResistance * speed / 1000; // kW
    
    // 计算轴功率
    const shaftPower = 2 * Math.PI * rpm * torque / 60000; // kW
    
    // 计算推进效率
    const propulsiveEfficiency = effectivePower / shaftPower;
    
    // 计算燃油消耗率
    const sfc = fuelRate / shaftPower; // g/kWh
    
    // 能效评估
    const efficiencyScore = this.calculateEfficiencyScore(propulsiveEfficiency, sfc);
    
    return {
      timestamp: Date.now(),
      effectivePower: effectivePower.toFixed(1),
      shaftPower: shaftPower.toFixed(1),
      propulsiveEfficiency: (propulsiveEfficiency * 100).toFixed(1) + '%',
      sfc: sfc.toFixed(1),
      efficiencyScore,
      recommendations: this.getEfficiencyRecommendations(efficiencyScore)
    };
  }
  
  /**
   * 计算能效评分
   */
  calculateEfficiencyScore(propulsiveEfficiency, sfc) {
    let score = 100;
    
    // 推进效率评分 (理想值 0.6-0.7)
    if (propulsiveEfficiency < 0.5) {
      score -= 30;
    } else if (propulsiveEfficiency < 0.6) {
      score -= 15;
    }
    
    // 燃油消耗率评分 (理想值 < 180 g/kWh)
    if (sfc > 220) {
      score -= 30;
    } else if (sfc > 200) {
      score -= 15;
    }
    
    return {
      score: Math.max(0, score),
      level: score >= 80 ? '优秀' : score >= 60 ? '良好' : score >= 40 ? '一般' : '需改进'
    };
  }
  
  /**
   * 获取能效优化建议
   */
  getEfficiencyRecommendations(efficiencyScore) {
    const recommendations = [];
    
    if (efficiencyScore.score < 60) {
      recommendations.push('建议清理船底海生物，减少摩擦阻力');
      recommendations.push('检查螺旋桨状态，优化螺距比');
    }
    
    if (efficiencyScore.score < 80) {
      recommendations.push('优化航速，避免主机超负荷运行');
      recommendations.push('考虑安装节能装置（如预旋导轮）');
    }
    
    return recommendations;
  }
  
  /**
   * 获取实时状态摘要
   */
  getStatusSummary() {
    return {
      stability: this.realtimeState.stability ? {
        GMt: this.realtimeState.stability.GMt,
        rollAngle: this.realtimeState.stability.rollAngle,
        status: this.realtimeState.stability.assessment.stable ? '✅ 稳定' : '⚠️ 不稳定'
      } : null,
      motion: this.realtimeState.motion ? {
        comfortLevel: this.realtimeState.motion.comfort?.comfortLevel || '未知',
        motionSicknessIndex: this.realtimeState.motion.comfort?.motionSicknessIndex?.toFixed(2) || 'N/A'
      } : null,
      alerts: this.realtimeState.alerts.length
    };
  }
}

export default MarineEngineeringModule;
