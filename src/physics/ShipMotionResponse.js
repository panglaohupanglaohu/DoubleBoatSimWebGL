/**
 * 船舶运动响应模块
 * Ship Motion Response Module
 * 
 * 基于船舶理论计算船舶运动响应
 * 包含规则波和不规则波中的运动计算
 */

export class ShipMotionResponse {
  constructor(config = {}) {
    this.config = {
      length: config.length || 138,      // 船长 (m)
      beam: config.beam || 26,          // 船宽 (m)
      draft: config.draft || 5.5,       // 吃水 (m)
      displacement: config.displacement || 37000, // 排水量 (吨)
      GMt: config.GMt || 15,            // 初稳性高度 (m)
      GMl: config.GMl || 120,           // 纵稳性高度 (m)
      ω0: config.ω0 || 0.5,             // 固有频率
    };
    
    this.motionData = [];
    this.timeHistory = [];
  }

  /**
   * 计算横摇固有周期
   * Tr = 2π * B / √(GMt * g)
   */
  calculateRollPeriod() {
    const { beam, GMt } = this.config;
    const g = 9.81;
    
    if (GMt <= 0) return Infinity;
    
    return 2 * Math.PI * beam / Math.sqrt(GMt * g);
  }

  /**
   * 计算纵摇固有周期
   * Tp = 2π * L / √(GMl * g)
   */
  calculatePitchPeriod() {
    const { length, GMl } = this.config;
    const g = 9.81;
    
    if (GMl <= 0) return Infinity;
    
    return 2 * Math.PI * length / Math.sqrt(GMl * g);
  }

  /**
   * 计算垂荡固有周期
   * Tv = 2π * √(d / g)
   */
  calculateHeavePeriod() {
    const { draft } = this.config;
    const g = 9.81;
    
    return 2 * Math.PI * Math.sqrt(draft / g);
  }

  /**
   * 计算规则波中的运动幅值响应算子 (RAO)
   * @param {string} motionType - 运动类型: 'roll', 'pitch', 'heave', 'yaw', 'surge', 'sway'
   * @param {number} wavePeriod - 波浪周期 (s)
   * @param {number} waveHeading - 波浪来向 (度, 0=正横, 90=顺浪)
   */
  calculateRAO(motionType, wavePeriod, waveHeading) {
    const ω = 2 * Math.PI / wavePeriod; // 波浪频率
    const ω0 = this.getNaturalFrequency(motionType);
    const ζ = this.getDampingRatio(motionType);
    
    // 频率比
    const ratio = ω / ω0;
    
    // 放大因子 (DAF)
    let DAF;
    if (ratio < 0.3) {
      DAF = 1;
    } else {
      DAF = 1 / Math.sqrt(Math.pow(1 - ratio * ratio, 2) + Math.pow(2 * ζ * ratio, 2));
    }
    
    // 波浪幅值
    const waveAmplitude = 1; // 假设单位波高
    
    // 运动幅值
    const motionAmplitude = DAF * waveAmplitude * this.getMotionGain(motionType, waveHeading);
    
    return {
      motionType,
      wavePeriod,
      waveHeading,
      frequency: ω,
      naturalFrequency: ω0,
      dampingRatio: ζ,
      frequencyRatio: ratio,
      DAF: DAF,
      motionAmplitude: motionAmplitude
    };
  }

  /**
   * 获取固有频率
   */
  getNaturalFrequency(motionType) {
    switch(motionType) {
      case 'roll': return 2 * Math.PI / this.calculateRollPeriod();
      case 'pitch': return 2 * Math.PI / this.calculatePitchPeriod();
      case 'heave': return 2 * Math.PI / this.calculateHeavePeriod();
      default: return 0.5;
    }
  }

  /**
   * 获取阻尼比
   */
  getDampingRatio(motionType) {
    switch(motionType) {
      case 'roll': return 0.05;    // 横摇阻尼比
      case 'pitch': return 0.03;   // 纵摇阻尼比
      case 'heave': return 0.02;   // 垂荡阻尼比
      default: return 0.05;
    }
  }

  /**
   * 获取运动增益（与航向角相关）
   */
  getMotionGain(motionType, heading) {
    const h = heading * Math.PI / 180;
    
    switch(motionType) {
      case 'roll':
        // 横摇在正横浪(0°)最大，顺浪(90°)最小
        return Math.abs(Math.cos(h));
      case 'pitch':
        // 纵摇在首尾浪(90°)最大
        return Math.abs(Math.sin(h));
      case 'heave':
        // 垂荡各航向相近
        return 0.8 + 0.2 * Math.abs(Math.cos(h));
      default:
        return 1;
    }
  }

  /**
   * 模拟不规则波中的运动响应
   * @param {number} significantWaveHeight - 有义波高 (m)
   * @param {number} meanWavePeriod - 平均波浪周期 (s)
   * @param {number} duration - 模拟时长 (s)
   * @param {number} dt - 时间步长 (s)
   */
  simulateIrregularMotion(significantWaveHeight, meanWavePeriod, duration, dt = 0.1) {
    const results = [];
    const steps = Math.ceil(duration / dt);
    
    // 使用JONSWAP谱
    const γ = 3.3; // 峰化系数
    
    for (let t = 0; t < duration; t += dt) {
      // 生成波面
      const waveElevation = this.generateWaveElevation(t, significantWaveHeight, meanWavePeriod, γ);
      
      // 计算各运动分量
      const roll = this.calculateMotionComponent('roll', waveElevation, t);
      const pitch = this.calculateMotionComponent('pitch', waveElevation, t);
      const heave = this.calculateMotionComponent('heave', waveElevation, t);
      
      results.push({
        time: t,
        waveElevation,
        roll,
        pitch,
        heave
      });
    }
    
    this.motionData = results;
    return results;
  }

  /**
   * 生成波面高程（JONSWAP谱）
   */
  generateWaveElevation(t, Hs, Tp, γ) {
    // 简化：使用多个正弦波叠加
    let elevation = 0;
    const components = 5;
    
    for (let i = 1; i <= components; i++) {
      const fi = i / components;
      const omega = 2 * Math.PI / (Tp * fi);
      const amplitude = Hs / 4 * Math.sqrt(2) * fi * Math.exp(-fi * fi / 2);
      const phase = Math.random() * 2 * Math.PI;
      
      elevation += amplitude * Math.sin(omega * t + phase);
    }
    
    return elevation;
  }

  /**
   * 计算运动分量
   */
  calculateMotionComponent(motionType, waveElevation, t) {
    const RAO = this.calculateRAO(motionType, 6, 45); // 假设典型波浪
    return RAO.motionAmplitude * waveElevation * Math.sin(t);
  }

  /**
   * 计算运动统计参数
   */
  calculateMotionStatistics() {
    if (this.motionData.length === 0) {
      return null;
    }
    
    const rolls = this.motionData.map(d => d.roll);
    const pitches = this.motionData.map(d => d.pitch);
    const heaves = this.motionData.map(d => d.heave);
    
    return {
      roll: {
        max: Math.max(...rolls),
        min: Math.min(...rolls),
        RMS: this.calculateRMS(rolls),
        significant: this.calculateSignificant(rolls)
      },
      pitch: {
        max: Math.max(...pitches),
        min: Math.min(...pitches),
        RMS: this.calculateRMS(pitches),
        significant: this.calculateSignificant(pitches)
      },
      heave: {
        max: Math.max(...heaves),
        min: Math.min(...heaves),
        RMS: this.calculateRMS(heaves),
        significant: this.calculateSignificant(heaves)
      }
    };
  }

  calculateRMS(values) {
    const sum = values.reduce((a, b) => a + b * b, 0);
    return Math.sqrt(sum / values.length);
  }

  calculateSignificant(values) {
    const sorted = [...values].sort((a, b) => Math.abs(b) - Math.abs(a));
    const n = Math.ceil(sorted.length / 3);
    return sorted.slice(0, n).reduce((a, b) => a + Math.abs(b), 0) / n;
  }

  /**
   * 晕船风险评估
   * 基于ISO 2631和IMIT标准
   */
  assessMotionComfort() {
    const stats = this.calculateMotionStatistics();
    if (!stats) return null;
    
    // 计算晕船指数 (MSK)
    const msk = this.calculateMotionSicknessIndex(stats);
    
    // 评估舒适度
    let comfortLevel;
    if (msk < 0.5) {
      comfortLevel = '舒适 | Comfortable';
    } else if (msk < 1.0) {
      comfortLevel = '较舒适 | Moderate';
    } else if (msk < 2.0) {
      comfortLevel = '不舒适 | Uncomfortable';
    } else {
      comfortLevel = '非常不舒适 | Very Uncomfortable';
    }
    
    return {
      motionSicknessIndex: msk,
      comfortLevel,
      recommendations: this.getComfortRecommendations(msk)
    };
  }

  calculateMotionSicknessIndex(stats) {
    // 简化的晕船指数计算
    // 考虑横摇和纵摇的RMS值
    const rollRMS = stats.roll.RMS * 180 / Math.PI; // 转换为度
    const pitchRMS = stats.pitch.RMS * 180 / Math.PI;
    
    // 经验公式
    const msk = 0.5 * rollRMS + 0.3 * pitchRMS;
    return msk;
  }

  getComfortRecommendations(msk) {
    const recommendations = [];
    
    if (msk > 1.0) {
      recommendations.push('建议减速航行 | Recommend reducing speed');
      recommendations.push('建议改变航向避开迎浪 | Consider changing course');
    }
    
    if (msk > 0.5) {
      recommendations.push('建议使用防晕船药物 | Consider motion sickness medication');
    }
    
    return recommendations;
  }
}

export default ShipMotionResponse;
