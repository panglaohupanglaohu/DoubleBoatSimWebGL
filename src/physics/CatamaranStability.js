/**
 * 双体船稳定性分析增强模块
 * Catamaran Stability Analysis Enhancement
 * 
 * 基于船舶工程理论增强双体船稳定性计算
 * 添加GM值、稳性曲线、摇摆周期等关键参数
 */

import * as CANNON from '../../public/lib/cannon-es.js';

// 双体船稳定性参数
export const CatamaranStabilityConfig = {
  // 默认双体船参数 (138米双体客船)
  defaultHullLength: 138,        //船长(m)
  defaultHullBeam: 26,           //单个船体宽度(m)
  defaultHullDepth: 7.5,         //船体深度(m)
  defaultDraft: 5.5,             //吃水(m)
  defaultDisplacement: 37000,    //排水量(吨)
  defaultHullSpacing: 80,        //两船体间距(m)
  defaultGMt: 15,                //初稳性高度GMt (m) - 双体船典型值
};

/**
 * 双体船稳定性计算器
 */
export class CatamaranStabilityCalculator {
  constructor(config = {}) {
    this.config = { ...CatamaranStabilityConfig, ...config };
    this.stabilityCurve = []; // GZ曲线数据
    this.rollHistory = [];
    this.pitchHistory = [];
  }

  /**
   * 计算双体船初稳性高度 GMt
   * GMt = KMt - KG
   * KMt = KB + BMt
   * 
   * @param {number} displacement - 排水量 (吨)
   * @param {number} hullSpacing - 两船体中心距 (m)
   * @param {number} beam - 单船体宽度 (m)
   * @returns {object} 稳性参数
   */
  calculateGMt(displacement, hullSpacing, beam) {
    const ρ = 1.025; // 海水密度 (吨/m³)
    const V = displacement / ρ; // 排水体积 (m³)
    
    // 浮心高度 KB (简化估算)
    const KB = this.config.defaultDraft * 0.55;
    
    // 横稳心半径 BMt (双体船简化公式)
    // BMt = (B² - a²) / (2T) * (V / ΣAi)
    // 简化：BMt ≈ (hullSpacing² - beam²) / (12 * draft)
    const BMt = (hullSpacing * hullSpacing - beam * beam) / (12 * this.config.defaultDraft);
    
    // 重心高度 KG (估算)
    const KG = this.config.defaultDraft * 0.7;
    
    // 初稳性高度
    const GMt = KB + BMt - KG;
    
    return {
      GMt: GMt,           // 初稳性高度 (m)
      KB: KB,             // 浮心高 (m)
      BMt: BMt,           // 横稳心半径 (m)
      KG: KG,             // 重心高 (m)
      displacement: displacement, // 排水量
      hullSpacing: hullSpacing,   // 船体间距
      beam: beam          // 船体宽度
    };
  }

  /**
   * 计算横摇周期 Tr
   * Tr = 2π * B / √(GMt * g)
   * 
   * @param {number} GMt - 初稳性高度 (m)
   * @param {number} beam - 船宽 (m)
   * @returns {number} 横摇周期 (秒)
   */
  calculateRollPeriod(GMt, beam) {
    const g = 9.81; // 重力加速度
    const B = beam; // 船宽
    
    if (GMt <= 0) return Infinity;
    
    const Tr = 2 * Math.PI * B / Math.sqrt(GMt * g);
    return Tr;
  }

  /**
   * 计算纵摇周期 Tp
   * Tp = 2π * L / √(GMt * g)
   * 
   * @param {number} GMl - 纵稳性高度 (m)
   * @param {number} length - 船长 (m)
   * @returns {number} 纵摇周期 (秒)
   */
  calculatePitchPeriod(GMl, length) {
    const g = 9.81;
    
    if (GMl <= 0) return Infinity;
    
    const Tp = 2 * Math.PI * length / Math.sqrt(GMl * g);
    return Tp;
  }

  /**
   * 计算稳性曲线 GZ
   * @param {number} GMt - 初稳性高度
   * @param {number} maxAngle - 最大横倾角 (度)
   * @returns {Array} GZ曲线数据
   */
  calculateStabilityCurve(GMt, maxAngle = 60) {
    const curve = [];
    const g = 9.81;
    const Δ = this.config.defaultDisplacement * 1000 * g; // 重量(N)
    
    for (let angle = 0; angle <= maxAngle; angle += 5) {
      const φ = angle * Math.PI / 180; // 弧度
      
      let GZ;
      if (angle <= 30) {
        // 小角度：GZ ≈ GMt * sin(φ)
        GZ = GMt * Math.sin(φ);
      } else {
        // 大角度：简化公式
        // 实际需要从船舶静水力曲线获取
        const factor = Math.max(0, 1 - (angle - 30) / 60);
        GZ = GMt * Math.sin(φ) * factor;
      }
      
      curve.push({
        angle: angle,
        GZ: GZ,
        GZ_radians: GZ,
        rightingMoment: GZ * Δ / 1000 // kN·m
      });
    }
    
    this.stabilityCurve = curve;
    return curve;
  }

  /**
   * 分析当前稳定性状态
   * @param {CANNON.Body} body - 船体物理体
   * @param {number} time - 当前时间
   * @returns {object} 稳定性分析结果
   */
  analyzeStability(body, time) {
    if (!body) {
      return { error: 'No body provided' };
    }
    
    const quat = body.quaternion;
    const angVel = body.angularVelocity;
    
    // 从四元数获取横倾角和纵倾角
    const euler = new CANNON.Vec3();
    quat.toEuler(euler);
    
    const roll = euler.x * 180 / Math.PI;  // 横倾角 (度)
    const pitch = euler.y * 180 / Math.PI; // 纵倾角 (度)
    
    // 记录历史数据
    this.rollHistory.push({ time, roll, angVelX: angVel.x });
    this.pitchHistory.push({ time, pitch, angVelY: angVel.y });
    
    // 保持历史数据在合理范围
    if (this.rollHistory.length > 1000) {
      this.rollHistory = this.rollHistory.slice(-500);
    }
    if (this.pitchHistory.length > 1000) {
      this.pitchHistory = this.pitchHistory.slice(-500);
    }
    
    // 计算当前GMt
    const GMt = this.calculateGMt(
      this.config.defaultDisplacement,
      this.config.defaultHullSpacing,
      this.config.defaultHullBeam
    );
    
    // 计算摇摆周期
    const rollPeriod = this.calculateRollPeriod(GMt.GMt, this.config.defaultHullBeam);
    const pitchPeriod = this.calculatePitchPeriod(GMt.GMt * 0.8, this.config.defaultHullLength);
    
    // 评估稳定性
    const assessment = this.assessStability(roll, pitch, GMt.GMt);
    
    return {
      GMt: GMt.GMt.toFixed(2),
      rollAngle: roll.toFixed(2),
      pitchAngle: pitch.toFixed(2),
      rollPeriod: rollPeriod.toFixed(2),
      pitchPeriod: pitchPeriod.toFixed(2),
      assessment: assessment,
      metrics: {
        displacement: this.config.defaultDisplacement,
        hullSpacing: this.config.defaultHullSpacing,
        beam: this.config.defaultHullBeam
      }
    };
  }

  /**
   * 评估稳定性状态
   */
  assessStability(roll, pitch, GMt) {
    const issues = [];
    const warnings = [];
    
    // 横倾评估
    if (Math.abs(roll) > 45) {
      issues.push('横倾角过大，有倾覆风险');
    } else if (Math.abs(roll) > 30) {
      warnings.push('横倾角较大');
    }
    
    // 纵倾评估
    if (Math.abs(pitch) > 25) {
      warnings.push('纵倾角较大');
    }
    
    // GMt评估
    if (GMt < 0) {
      issues.push('GMt为负，稳性不足');
    } else if (GMt < 5) {
      warnings.push('GMt较小，稳性偏低');
    } else if (GMt > 30) {
      warnings.push('GMt过大，摇摆周期短，舒适性差');
    }
    
    return {
      stable: issues.length === 0,
      issues,
      warnings
    };
  }
}

/**
 * 增强的浮力算法 - 考虑双体船特性
 */
export class EnhancedBuoyancyAlgorithm {
  constructor(config = {}) {
    this.config = {
      buoyancyCoeff: config.buoyancyCoeff || 40000000,
      dragCoeff: config.dragCoeff || 6,
      density: config.density || 1.025, // 海水密度
      catamaranMode: config.catamaranMode !== false,
      hullSpacing: config.hullSpacing || 80,
    };
    
    this.buoyancyPoints = [];
    this.stabilityCalc = new CatamaranStabilityCalculator();
  }

  /**
   * 初始化双体船浮力点
   */
  initializeCatamaranBuoyancy(shipSize) {
    const { x: width, y: height, z: length } = shipSize;
    const spacing = this.config.hullSpacing;
    
    // 双体船两侧各一列浮力点
    const pointsPerSide = Math.ceil(length / 2);
    const pointsPerWidth = Math.ceil(width / 1.5);
    
    this.buoyancyPoints = [];
    
    // 左船体
    for (let z = -length/2; z <= length/2; z += 2) {
      for (let x = -width/2; x <= width/2; x += 1.5) {
        this.buoyancyPoints.push({
          x: x - spacing/2,
          y: 0, // 底部
          z: z,
          area: 3, // 面积权重
          hull: 'left'
        });
      }
    }
    
    // 右船体
    for (let z = -length/2; z <= length/2; z += 2) {
      for (let x = -width/2; x <= width/2; x += 1.5) {
        this.buoyancyPoints.push({
          x: x + spacing/2,
          y: 0,
          z: z,
          area: 3,
          hull: 'right'
        });
      }
    }
    
    // 连接桥区（横撑）- 减少浮力
    const bridgeWidth = spacing - width;
    for (let z = -length/4; z <= length/4; z += 2) {
      for (let x = -bridgeWidth/2; x <= bridgeWidth/2; x += 1.5) {
        if (Math.abs(x) > width/2) { // 只在船体外部
          this.buoyancyPoints.push({
            x: x,
            y: 0,
            z: z,
            area: 1, // 连接区浮力较小
            hull: 'bridge'
          });
        }
      }
    }
    
    console.log(`双体船浮力点: ${this.buoyancyPoints.length}个`);
    return this.buoyancyPoints;
  }
}

export default {
  CatamaranStabilityCalculator,
  EnhancedBuoyancyAlgorithm,
  CatamaranStabilityConfig
};
