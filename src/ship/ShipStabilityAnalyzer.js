/**
 * 船身稳定分析器
 * Ship Stability Analyzer
 * 
 * 分析船体状态并自动调整参数使其稳定
 */

import * as CANNON from '../../public/lib/cannon-es.js';
import { getWaveHeight } from '../waves.js';

export class ShipStabilityAnalyzer {
  constructor() {
    this.analysisHistory = [];
  }

  /**
   * 分析船体当前状态
   * @param {CANNON.Body} body - 船体物理体
   * @param {number} time - 当前时间
   * @param {object} config - 当前配置
   * @returns {object} 分析结果和建议
   */
  analyze(body, time, config) {
    if (!body) {
      return {
        stable: false,
        issues: ['船体未加载 | Ship not loaded'],
        suggestions: []
      };
    }

    const analysis = {
      timestamp: Date.now(),
      stable: true,
      issues: [],
      warnings: [],
      suggestions: [],
      metrics: {},
      adjustments: {}
    };

    // 计算当前指标
    const metrics = this.calculateMetrics(body, time);
    analysis.metrics = metrics;

    // 检查稳定性问题
    this.checkStabilityIssues(metrics, analysis);
    
    // 生成调整建议
    this.generateSuggestions(metrics, config, analysis);

    // 判断是否稳定
    analysis.stable = analysis.issues.length === 0 && analysis.warnings.length === 0;

    this.analysisHistory.push(analysis);
    return analysis;
  }

  /**
   * 计算船体指标
   * @private
   */
  calculateMetrics(body, time) {
    const pos = body.position;
    const quat = body.quaternion;
    const vel = body.velocity;
    const angVel = body.angularVelocity;

    // 计算倾斜角度
    const bodyUp = quat.vmult(new CANNON.Vec3(0, 1, 0));
    const worldUp = new CANNON.Vec3(0, 1, 0);
    const dot = Math.max(-1, Math.min(1, bodyUp.dot(worldUp)));
    const tilt = Math.acos(dot) * (180 / Math.PI);

    // 计算水面高度
    const waterH = getWaveHeight(pos.x, -pos.z, time) * -1;
    const sink = waterH - pos.y;

    // 计算速度
    const speed = Math.sqrt(vel.x * vel.x + vel.y * vel.y + vel.z * vel.z);
    const angularSpeed = Math.sqrt(
      angVel.x * angVel.x + angVel.y * angVel.y + angVel.z * angVel.z
    );

    // 计算漂移
    const drift = Math.sqrt(pos.x * pos.x + pos.z * pos.z);

    return {
      tilt,              // 倾斜角度（度）
      sink,              // 下沉深度（米）
      speed,             // 线速度（m/s）
      angularSpeed,      // 角速度（rad/s）
      drift,             // 漂移距离（米）
      waterHeight: waterH,
      position: { x: pos.x, y: pos.y, z: pos.z }
    };
  }

  /**
   * 检查稳定性问题
   * @private
   */
  checkStabilityIssues(metrics, analysis) {
    // 检查倾覆风险
    if (metrics.tilt > 60) {
      analysis.stable = false;
      analysis.issues.push('严重倾斜，有倾覆风险 | Severe tilt, risk of capsizing');
    } else if (metrics.tilt > 30) {
      analysis.warnings.push('倾斜角度较大 | Large tilt angle');
    }

    // 检查下沉
    if (metrics.sink > 10) {
      analysis.stable = false;
      analysis.issues.push('过度下沉 | Excessive sinking');
    } else if (metrics.sink > 7) {
      analysis.warnings.push('下沉较深 | Deep sinking');
    }

    // 检查振荡
    if (metrics.angularSpeed > 2.0) {
      analysis.warnings.push('角速度过大，船体振荡 | High angular velocity, ship oscillating');
    }

    if (metrics.speed > 5.0) {
      analysis.warnings.push('线速度过大 | High linear velocity');
    }

    // 检查漂移
    if (metrics.drift > 100) {
      analysis.warnings.push('漂移距离过大 | Large drift distance');
    }
  }

  /**
   * 生成调整建议
   * @private
   */
  generateSuggestions(metrics, config, analysis) {
    const adjustments = {};

    // 如果倾斜过大，建议调整自稳系统
    if (metrics.tilt > 20) {
      const currentStiffness = config.stabilizer?.uprightStiffness || 12.0;
      const suggestedStiffness = Math.min(20, currentStiffness + (metrics.tilt - 20) * 0.3);
      
      if (suggestedStiffness > currentStiffness) {
        adjustments.uprightStiffness = suggestedStiffness;
        analysis.suggestions.push({
          param: '自稳刚度 | Stabilizer Stiffness',
          current: currentStiffness.toFixed(1),
          suggested: suggestedStiffness.toFixed(1),
          reason: '倾斜角度过大，需要更强的恢复力 | Tilt too large, need stronger recovery'
        });
      }
    }

    // 如果下沉过深，建议增加浮力
    if (metrics.sink > 5) {
      const currentBuoyancy = config.buoyancy?.buoyancyCoeff || 400;
      const suggestedBuoyancy = Math.min(1000, currentBuoyancy + (metrics.sink - 5) * 50);
      
      if (suggestedBuoyancy > currentBuoyancy) {
        adjustments.buoyancyCoeff = suggestedBuoyancy;
        analysis.suggestions.push({
          param: '浮力系数 | Buoyancy Coeff',
          current: currentBuoyancy.toFixed(0),
          suggested: suggestedBuoyancy.toFixed(0),
          reason: '下沉过深，需要增加浮力 | Sinking too deep, need more buoyancy'
        });
      }
    }

    // 如果振荡过大，建议增加阻尼
    if (metrics.angularSpeed > 1.0) {
      const currentDrag = config.buoyancy?.dragCoeff || 8;
      const suggestedDrag = Math.min(20, currentDrag + (metrics.angularSpeed - 1.0) * 3);
      
      if (suggestedDrag > currentDrag) {
        adjustments.dragCoeff = suggestedDrag;
        analysis.suggestions.push({
          param: '阻尼系数 | Drag Coeff',
          current: currentDrag.toFixed(1),
          suggested: suggestedDrag.toFixed(1),
          reason: '振荡过大，需要增加阻尼 | Oscillation too large, need more damping'
        });
      }
    }

    // 如果质量过轻导致不稳定，建议增加质量
    if (metrics.tilt > 15 && config.boatMass < 10000) {
      const suggestedMass = Math.min(20000, config.boatMass + 2000);
      adjustments.boatMass = suggestedMass;
      analysis.suggestions.push({
        param: '船体质量 | Boat Mass',
        current: config.boatMass.toFixed(0) + ' kg',
        suggested: suggestedMass.toFixed(0) + ' kg',
        reason: '质量过轻，增加质量可提高稳定性 | Mass too light, increase for stability'
      });
    }

    // 如果摇晃增强系数过大，建议减小
    if (metrics.angularSpeed > 0.8 && config.stabilizer?.wobbleBoost > 0.8) {
      const currentWobble = config.stabilizer.wobbleBoost;
      const suggestedWobble = Math.max(0.3, currentWobble - 0.2);
      adjustments.wobbleBoost = suggestedWobble;
      analysis.suggestions.push({
        param: '摇晃增强 | Wobble Boost',
        current: currentWobble.toFixed(1),
        suggested: suggestedWobble.toFixed(1),
        reason: '摇晃过大，减小摇晃增强系数 | Wobbling too much, reduce wobble boost'
      });
    }

    analysis.adjustments = adjustments;
  }

  /**
   * 应用调整建议
   * @param {object} adjustments - 调整参数
   * @param {object} config - 配置对象
   * @param {object} simulatorEngine - 模拟器引擎
   * @param {object} shipController - 船体控制器
   */
  applyAdjustments(adjustments, config, simulatorEngine, shipController) {
    const applied = [];

    // 调整浮力系数
    if (adjustments.buoyancyCoeff !== undefined) {
      const alg = simulatorEngine?.getAlgorithm('Buoyancy');
      if (alg) {
        alg.buoyancyCoeff = adjustments.buoyancyCoeff;
        config.buoyancy.buoyancyCoeff = adjustments.buoyancyCoeff;
        applied.push(`浮力系数 → ${adjustments.buoyancyCoeff.toFixed(0)}`);
      }
    }

    // 调整阻尼系数
    if (adjustments.dragCoeff !== undefined) {
      const alg = simulatorEngine?.getAlgorithm('Buoyancy');
      if (alg) {
        alg.dragCoeff = adjustments.dragCoeff;
        config.buoyancy.dragCoeff = adjustments.dragCoeff;
        applied.push(`阻尼系数 → ${adjustments.dragCoeff.toFixed(1)}`);
      }
    }

    // 调整自稳刚度
    if (adjustments.uprightStiffness !== undefined) {
      const alg = simulatorEngine?.getAlgorithm('Stabilizer');
      if (alg) {
        alg.setStiffness(adjustments.uprightStiffness);
        config.stabilizer.uprightStiffness = adjustments.uprightStiffness;
        applied.push(`自稳刚度 → ${adjustments.uprightStiffness.toFixed(1)}`);
      }
    }

    // 调整摇晃增强
    if (adjustments.wobbleBoost !== undefined) {
      const alg = simulatorEngine?.getAlgorithm('Stabilizer');
      if (alg) {
        alg.setWobbleBoost(adjustments.wobbleBoost);
        config.stabilizer.wobbleBoost = adjustments.wobbleBoost;
        applied.push(`摇晃增强 → ${adjustments.wobbleBoost.toFixed(1)}`);
      }
    }

    // 调整质量
    if (adjustments.boatMass !== undefined) {
      if (shipController) {
        shipController.setMass(adjustments.boatMass);
        config.boatMass = adjustments.boatMass;
        applied.push(`船体质量 → ${adjustments.boatMass.toFixed(0)} kg`);
      }
    }

    return applied;
  }

  /**
   * 稳定化船体（综合调整）
   * @param {object} body - 船体物理体
   * @param {number} time - 当前时间
   * @param {object} config - 配置对象
   * @param {object} simulatorEngine - 模拟器引擎
   * @param {object} shipController - 船体控制器
   * @returns {object} 稳定化结果
   */
  stabilize(body, time, config, simulatorEngine, shipController) {
    // 分析当前状态
    const analysis = this.analyze(body, time, config);

    // 如果有调整建议，应用它们
    let applied = [];
    if (Object.keys(analysis.adjustments).length > 0) {
      applied = this.applyAdjustments(
        analysis.adjustments,
        config,
        simulatorEngine,
        shipController
      );
    }

    // 重置船体姿态和速度
    if (body) {
      const waterH = getWaveHeight(body.position.x, -body.position.z, time) * -1;
      body.position.y = waterH - (config.draftDepth || 5);
      body.velocity.setZero();
      body.angularVelocity.setZero();
      body.quaternion.set(0, 0, 0, 1);
      body.force.setZero();
      body.torque.setZero();
      body.wakeUp();
    }

    return {
      stable: analysis.stable,
      issues: analysis.issues,
      warnings: analysis.warnings,
      suggestions: analysis.suggestions,
      applied,
      metrics: analysis.metrics
    };
  }

  /**
   * 获取状态摘要
   */
  getStatusSummary(analysis) {
    if (!analysis) return '未分析 | Not analyzed';

    if (analysis.stable) {
      return '✅ 船体稳定 | Ship stable';
    }

    if (analysis.issues.length > 0) {
      return `❌ ${analysis.issues[0]}`;
    }

    if (analysis.warnings.length > 0) {
      return `⚠️ ${analysis.warnings[0]}`;
    }

    return '状态未知 | Status unknown';
  }
}

