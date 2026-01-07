/**
 * 自动稳定系统
 * Auto Stabilization System
 * 
 * 自动检测船体不稳定状态并启动稳定调整
 * 记录所有稳定调整过程
 */

import * as CANNON from '../../public/lib/cannon-es.js';

export class AutoStabilizationSystem {
  constructor(stabilityAnalyzer, simulatorEngine, shipController) {
    this.stabilityAnalyzer = stabilityAnalyzer;
    this.simulatorEngine = simulatorEngine;
    this.shipController = shipController;
    
    this.enabled = true;
    this.checkInterval = 2.0; // 每2秒检查一次
    this.lastCheckTime = 0;
    this.isStabilizing = false;
    
    // 稳定调整记录
    this.stabilizationLog = [];
    this.maxLogEntries = 100;
    
    // 不稳定阈值
    this.thresholds = {
      maxTilt: 15,        // 最大倾斜角度（度）
      maxSink: 5,         // 最大下沉深度（米）
      maxAngularSpeed: 2, // 最大角速度（rad/s）
      maxDrift: 50        // 最大漂移距离（米）
    };
    
    // 自动调整参数
    this.autoAdjust = {
      enabled: true,
      maxAdjustments: 5,  // 最大调整次数
      adjustmentInterval: 3.0 // 调整间隔（秒）
    };
    
    this.currentAdjustments = 0;
    this.lastAdjustmentTime = 0;
  }

  /**
   * 更新自动稳定系统
   */
  update(deltaTime, clock) {
    if (!this.enabled || !this.shipController || !this.shipController.body) {
      return;
    }
    
    const currentTime = clock.elapsedTime;
    
    // 定期检查稳定性
    if (currentTime - this.lastCheckTime >= this.checkInterval) {
      this.lastCheckTime = currentTime;
      this._checkAndStabilize(currentTime);
    }
  }

  /**
   * 检查并稳定船体
   * @private
   */
  _checkAndStabilize(time) {
    if (this.isStabilizing) {
      return; // 正在稳定中，跳过
    }
    
    const body = this.shipController.body;
    const config = this.shipController.config || {};
    
    // 分析船体状态
    const analysis = this.stabilityAnalyzer.analyze(body, time, config);
    
    // 检查是否需要稳定
    const needsStabilization = this._needsStabilization(analysis);
    
    if (needsStabilization) {
      console.warn('⚠️ 检测到船体不稳定，启动自动稳定系统 | Ship instability detected, starting auto-stabilization');
      this._startStabilization(analysis, time);
    }
  }

  /**
   * 判断是否需要稳定
   * @private
   */
  _needsStabilization(analysis) {
    if (!analysis.metrics) return false;
    
    const metrics = analysis.metrics;
    
    // 检查各项指标
    if (Math.abs(metrics.tilt) > this.thresholds.maxTilt) {
      return true;
    }
    
    if (metrics.sink > this.thresholds.maxSink) {
      return true;
    }
    
    if (metrics.angularSpeed > this.thresholds.maxAngularSpeed) {
      return true;
    }
    
    if (metrics.drift > this.thresholds.maxDrift) {
      return true;
    }
    
    return false;
  }

  /**
   * 启动稳定过程
   * @private
   */
  _startStabilization(analysis, time) {
    if (!this.autoAdjust.enabled) {
      console.warn('⚠️ 自动调整已禁用 | Auto-adjustment disabled');
      return;
    }
    
    // 检查调整限制
    if (this.currentAdjustments >= this.autoAdjust.maxAdjustments) {
      console.warn('⚠️ 已达到最大调整次数 | Maximum adjustments reached');
      return;
    }
    
    // 检查调整间隔
    if (time - this.lastAdjustmentTime < this.autoAdjust.adjustmentInterval) {
      return; // 间隔太短，跳过
    }
    
    this.isStabilizing = true;
    this.lastAdjustmentTime = time;
    this.currentAdjustments++;
    
    // 记录稳定开始
    const logEntry = {
      timestamp: Date.now(),
      time: time,
      trigger: 'auto',
      initialAnalysis: analysis,
      adjustments: []
    };
    
    // 执行稳定调整
    const result = this._performStabilization(analysis, logEntry);
    
    // 记录稳定结果
    logEntry.result = result;
    logEntry.duration = Date.now() - logEntry.timestamp;
    this._addLogEntry(logEntry);
    
    this.isStabilizing = false;
    
    console.log(`✅ 自动稳定完成 | Auto-stabilization completed:`, result);
  }

  /**
   * 执行稳定调整
   * @private
   */
  _performStabilization(analysis, logEntry) {
    const adjustments = [];
    const metrics = analysis.metrics;
    
    // 获取算法
    const buoyancyAlg = this.simulatorEngine?.getAlgorithm('Buoyancy');
    const stabilizerAlg = this.simulatorEngine?.getAlgorithm('Stabilizer');
    
    // 1. 调整浮力系数（如果下沉）
    if (metrics.sink > this.thresholds.maxSink && buoyancyAlg) {
      const currentCoeff = buoyancyAlg.buoyancyCoeff || 800000;
      const sinkExcess = metrics.sink - this.thresholds.maxSink;
      const increase = sinkExcess * 50000; // 每米下沉增加50000
      const newCoeff = Math.min(currentCoeff + increase, 2000000);
      
      if (newCoeff !== currentCoeff) {
        buoyancyAlg.buoyancyCoeff = newCoeff;
        adjustments.push({
          type: 'buoyancy',
          parameter: 'buoyancyCoeff',
          oldValue: currentCoeff,
          newValue: newCoeff,
          reason: `下沉深度 ${metrics.sink.toFixed(2)}m 超过阈值 ${this.thresholds.maxSink}m`
        });
        
        // 更新配置
        if (this.shipController.config && this.shipController.config.buoyancy) {
          this.shipController.config.buoyancy.buoyancyCoeff = newCoeff;
        }
      }
    }
    
    // 2. 调整自稳系统（如果倾斜）
    if (Math.abs(metrics.tilt) > this.thresholds.maxTilt && stabilizerAlg) {
      const currentStiffness = stabilizerAlg.uprightStiffness || 12.0;
      const tiltExcess = Math.abs(metrics.tilt) - this.thresholds.maxTilt;
      const increase = tiltExcess * 0.5; // 每度倾斜增加0.5
      const newStiffness = Math.min(currentStiffness + increase, 20.0);
      
      if (newStiffness !== currentStiffness) {
        stabilizerAlg.setStiffness(newStiffness);
        adjustments.push({
          type: 'stabilizer',
          parameter: 'uprightStiffness',
          oldValue: currentStiffness,
          newValue: newStiffness,
          reason: `倾斜角度 ${metrics.tilt.toFixed(2)}° 超过阈值 ${this.thresholds.maxTilt}°`
        });
        
        // 更新配置
        if (this.shipController.config && this.shipController.config.stabilizer) {
          this.shipController.config.stabilizer.uprightStiffness = newStiffness;
        }
      }
    }
    
    // 3. 调整阻尼（如果角速度过大）
    if (metrics.angularSpeed > this.thresholds.maxAngularSpeed && buoyancyAlg) {
      const currentDrag = buoyancyAlg.dragCoeff || 6;
      const speedExcess = metrics.angularSpeed - this.thresholds.maxAngularSpeed;
      const increase = speedExcess * 0.5; // 增加阻尼
      const newDrag = Math.min(currentDrag + increase, 20);
      
      if (newDrag !== currentDrag) {
        buoyancyAlg.dragCoeff = newDrag;
        adjustments.push({
          type: 'buoyancy',
          parameter: 'dragCoeff',
          oldValue: currentDrag,
          newValue: newDrag,
          reason: `角速度 ${metrics.angularSpeed.toFixed(2)} rad/s 超过阈值 ${this.thresholds.maxAngularSpeed} rad/s`
        });
      }
    }
    
    // 4. 如果漂移过大，重置位置
    if (metrics.drift > this.thresholds.maxDrift && this.shipController) {
      // 重置船体位置和速度
      this.shipController.reset();
      adjustments.push({
        type: 'position',
        parameter: 'reset',
        reason: `漂移距离 ${metrics.drift.toFixed(2)}m 超过阈值 ${this.thresholds.maxDrift}m`
      });
    }
    
    logEntry.adjustments = adjustments;
    
    return {
      success: adjustments.length > 0,
      adjustmentsCount: adjustments.length,
      adjustments: adjustments,
      metricsAfter: metrics // 将在下次检查时更新
    };
  }

  /**
   * 添加日志条目
   * @private
   */
  _addLogEntry(entry) {
    this.stabilizationLog.push(entry);
    
    // 限制日志大小
    if (this.stabilizationLog.length > this.maxLogEntries) {
      this.stabilizationLog.shift();
    }
    
    // 触发日志事件
    if (this.onLogEntry) {
      this.onLogEntry(entry);
    }
  }

  /**
   * 获取稳定日志
   */
  getLog() {
    return [...this.stabilizationLog];
  }

  /**
   * 获取最近的稳定记录
   */
  getRecentLog(count = 10) {
    return this.stabilizationLog.slice(-count);
  }

  /**
   * 清除日志
   */
  clearLog() {
    this.stabilizationLog = [];
  }

  /**
   * 重置调整计数
   */
  resetAdjustmentCount() {
    this.currentAdjustments = 0;
    this.lastAdjustmentTime = 0;
  }

  /**
   * 启用/禁用自动稳定
   */
  setEnabled(enabled) {
    this.enabled = enabled;
    if (!enabled) {
      this.isStabilizing = false;
    }
  }

  /**
   * 设置阈值
   */
  setThresholds(thresholds) {
    this.thresholds = { ...this.thresholds, ...thresholds };
  }
}

