/**
 * EngineerAgent 增强模块
 * 
 * 集成真实船舶工程计算能力
 * 添加轮机长专业功能
 */

import { MarineEngineeringModule } from '../MarineEngineeringModule.js';

/**
 * 增强 EngineerAgent 的功能
 */
export class EnhancedEngineerAgent {
  constructor(baseAgent) {
    this.baseAgent = baseAgent;
    this.id = 'enhanced-engineer-agent';
    this.name = 'Enhanced Engineer Agent';
    
    // 集成船舶工程模块
    this.engineeringModule = new MarineEngineeringModule({
      shipType: 'catamaran',
      length: 138,
      beam: 26,
      draft: 5.5,
      displacement: 37000,
      GMt: 15
    });
    
    // 增强状态
    this.enhancedState = {
      stabilityMonitoring: true,
      motionAnalysis: true,
      efficiencyOptimization: true,
      predictiveMaintenance: true
    };
    
    // 注册增强工具
    this._registerEnhancedTools();
    
    console.log('⚙️ Enhanced Engineer Agent ready');
  }
  
  /**
   * 注册增强工具
   * @private
   */
  _registerEnhancedTools() {
    // 工具 1: 实时稳定性监控
    this.baseAgent?.registerTool?.('monitorStability', async (sensorData) => {
      const result = this.engineeringModule.monitorStability(sensorData);
      return {
        success: true,
        data: result,
        summary: this._formatStabilitySummary(result)
      };
    });
    
    // 工具 2: 运动响应分析
    this.baseAgent?.registerTool?.('analyzeShipMotion', async (waveData) => {
      const result = this.engineeringModule.analyzeMotion(waveData);
      return {
        success: true,
        data: result,
        summary: this._formatMotionSummary(result)
      };
    });
    
    // 工具 3: 能效分析
    this.baseAgent?.registerTool?.('analyzeEfficiency', async (engineData, resistanceData) => {
      const result = this.engineeringModule.analyzeEfficiency(engineData, resistanceData);
      return {
        success: true,
        data: result,
        summary: this._formatEfficiencySummary(result)
      };
    });
    
    // 工具 4: IMO 稳性检查
    this.baseAgent?.registerTool?.('checkIMOStability', async (GMt, rollAngle) => {
      const compliance = this.engineeringModule.stabilityCalc.assessStability(rollAngle, 0, GMt);
      const imoCheck = this.engineeringModule.checkIMOCriteria(GMt, rollAngle);
      
      return {
        success: true,
        compliant: imoCheck.passed,
        violations: imoCheck.violations,
        warnings: imoCheck.warnings,
        recommendations: this._getIMORecommendations(imoCheck)
      };
    });
    
    // 工具 5: 故障诊断增强
    this.baseAgent?.registerTool?.('diagnoseEngineFault', async (symptoms) => {
      const diagnosis = this._performFaultDiagnosis(symptoms);
      return {
        success: true,
        diagnosis,
        confidence: diagnosis.confidence,
        actions: diagnosis.recommendedActions
      };
    });
  }
  
  /**
   * 格式化稳定性摘要
   * @private
   */
  _formatStabilitySummary(result) {
    const lines = [
      `📊 稳定性状态：${result.assessment.stable ? '✅ 稳定' : '⚠️ 不稳定'}`,
      `GMt: ${result.GMt}m`,
      `横摇周期：${result.rollPeriod}s`,
      `纵摇周期：${result.pitchPeriod}s`,
      `横倾角：${result.rollAngle}°`,
      `IMO 合规：${result.imoCompliance.passed ? '✅' : '❌'}`
    ];
    
    if (result.alerts.length > 0) {
      lines.push('\\n⚠️ 告警:');
      result.alerts.forEach(alert => {
        lines.push(`  - [${alert.level}] ${alert.message}`);
      });
    }
    
    return lines.join('\\n');
  }
  
  /**
   * 格式化运动摘要
   * @private
   */
  _formatMotionSummary(result) {
    const lines = [
      `🌊 海况：有义波高 ${result.waveConditions.significantWaveHeight}m`,
      `舒适度：${result.comfort?.comfortLevel || '未知'}`,
      `晕船指数：${result.comfort?.motionSicknessIndex?.toFixed(2) || 'N/A'}`
    ];
    
    if (result.statistics) {
      lines.push('\\n运动统计:');
      lines.push(`  横摇 RMS: ${(result.statistics.roll.RMS * 180 / Math.PI).toFixed(1)}°`);
      lines.push(`  纵摇 RMS: ${(result.statistics.pitch.RMS * 180 / Math.PI).toFixed(1)}°`);
      lines.push(`  垂荡 RMS: ${result.statistics.heave.RMS.toFixed(2)}m`);
    }
    
    if (result.comfort?.recommendations?.length > 0) {
      lines.push('\\n建议:');
      result.comfort.recommendations.forEach(rec => lines.push(`  - ${rec}`));
    }
    
    return lines.join('\\n');
  }
  
  /**
   * 格式化能效摘要
   * @private
   */
  _formatEfficiencySummary(result) {
    const lines = [
      `⚡ 能效评分：${result.efficiencyScore.score}/100 (${result.efficiencyScore.level})`,
      `有效功率：${result.effectivePower} kW`,
      `轴功率：${result.shaftPower} kW`,
      `推进效率：${result.propulsiveEfficiency}`,
      `燃油消耗率：${result.sfc} g/kWh`
    ];
    
    if (result.recommendations.length > 0) {
      lines.push('\\n优化建议:');
      result.recommendations.forEach(rec => lines.push(`  - ${rec}`));
    }
    
    return lines.join('\\n');
  }
  
  /**
   * 获取 IMO 建议
   * @private
   */
  _getIMORecommendations(imoCheck) {
    const recommendations = [];
    
    if (!imoCheck.passed) {
      recommendations.push('立即减速航行');
      recommendations.push('调整航向避开迎浪');
      recommendations.push('检查压载水分布');
      recommendations.push('通知船长和轮机长');
    }
    
    imoCheck.warnings.forEach(warning => {
      if (warning.includes('GMt')) {
        recommendations.push('考虑调整压载水降低重心');
      }
    });
    
    return recommendations;
  }
  
  /**
   * 执行故障诊断
   * @private
   */
  _performFaultDiagnosis(symptoms) {
    const { exhaustTemp, vibration, pressure, rpm, fuelConsumption } = symptoms;
    
    const diagnosis = {
      possibleCauses: [],
      confidence: 0,
      recommendedActions: [],
      urgency: 'normal'
    };
    
    // 排温异常诊断
    if (exhaustTemp && exhaustTemp.deviation > 20) {
      diagnosis.possibleCauses.push('喷油嘴堵塞或磨损');
      diagnosis.possibleCauses.push('气缸压缩压力不足');
      diagnosis.confidence = 0.7;
      diagnosis.recommendedActions.push('检查喷油嘴雾化质量');
      diagnosis.recommendedActions.push('测量气缸压缩压力');
    }
    
    // 振动异常诊断
    if (vibration && vibration.level > 'normal') {
      diagnosis.possibleCauses.push('螺旋桨不平衡或损坏');
      diagnosis.possibleCauses.push('轴系对中不良');
      diagnosis.confidence = Math.max(diagnosis.confidence, 0.6);
      diagnosis.recommendedActions.push('检查螺旋桨叶片');
      diagnosis.recommendedActions.push('进行轴系对中检查');
    }
    
    // 滑油压力异常
    if (pressure && pressure.oil < pressure.normal) {
      diagnosis.possibleCauses.push('滑油泵故障');
      diagnosis.possibleCauses.push('滑油滤器堵塞');
      diagnosis.possibleCauses.push('轴承间隙过大');
      diagnosis.confidence = Math.max(diagnosis.confidence, 0.8);
      diagnosis.urgency = 'high';
      diagnosis.recommendedActions.push('立即检查滑油系统');
      diagnosis.recommendedActions.push('准备备用泵');
    }
    
    return diagnosis;
  }
  
  /**
   * 获取增强状态
   */
  getEnhancedStatus() {
    return {
      agentId: this.id,
      moduleName: 'Enhanced Engineer Agent',
      features: this.enhancedState,
      engineeringModule: this.engineeringModule.getStatusSummary(),
      availableTools: [
        'monitorStability',
        'analyzeShipMotion',
        'analyzeEfficiency',
        'checkIMOStability',
        'diagnoseEngineFault'
      ]
    };
  }
}

export default EnhancedEngineerAgent;
