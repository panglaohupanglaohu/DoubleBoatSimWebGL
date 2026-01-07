/**
 * 降雨算法
 * 模拟降雨对船体的影响（重量、能见度等）
 */

import * as CANNON from '../../../public/lib/cannon-es.js';
import { SimulationAlgorithm } from '../SimulatorEngine.js';

export class RainAlgorithm extends SimulationAlgorithm {
  constructor(config = {}) {
    super('Rain', 70); // 中高优先级
    this.description = 'Rain accumulation and weight simulation';
    
    // 降雨参数
    this.rainIntensity = config.rainIntensity || 0; // mm/h (0-200)
    this.deckArea = config.deckArea || 500; // m² 甲板面积
    this.drainageRate = config.drainageRate || 50; // mm/h 排水速度
    
    // 累积水量（立方米）
    this.accumulatedWater = 0;
    this.maxAccumulation = 10; // m³ 最大积水量
  }

  setRainIntensity(intensity) {
    this.rainIntensity = Math.max(0, Math.min(200, intensity));
  }

  /**
   * 根据降雨等级设置（0-4）
   * 0: 无雨
   * 1: 小雨 (2.5 mm/h)
   * 2: 中雨 (8 mm/h)
   * 3: 大雨 (16 mm/h)
   * 4: 暴雨 (50 mm/h)
   */
  setRainLevel(level) {
    const levels = [0, 2.5, 8, 16, 50, 100];
    this.rainIntensity = levels[Math.min(5, Math.max(0, level))];
  }

  update(deltaTime, shipState, environment) {
    const { body } = shipState;
    
    if (!body) return null;

    // 计算降雨累积（转换为 m³/s）
    const rainAccumulation = (this.rainIntensity / 1000 / 3600) * this.deckArea * deltaTime;
    
    // 计算排水（转换为 m³/s）
    const drainage = (this.drainageRate / 1000 / 3600) * this.deckArea * deltaTime;

    // 更新累积水量
    this.accumulatedWater += rainAccumulation - drainage;
    this.accumulatedWater = Math.max(0, Math.min(this.maxAccumulation, this.accumulatedWater));

    // 水的质量（1m³ = 1000kg）
    const waterMass = this.accumulatedWater * 1000;

    // 额外重力（向下的力）
    const additionalWeight = new CANNON.Vec3(0, -waterMass * 9.82, 0);

    // 积水导致的阻尼增加（船体运动变慢）
    const dampingFactor = 1 + (this.accumulatedWater / this.maxAccumulation) * 0.5;
    const velocityDamping = body.velocity.scale(-dampingFactor);

    // 总力
    const totalForce = additionalWeight.vadd(velocityDamping);

    // 能见度降低（元数据，用于渲染）
    const visibilityFactor = Math.max(0.3, 1 - this.rainIntensity / 200);

    return {
      force: totalForce,
      torque: new CANNON.Vec3(0, 0, 0),
      metadata: {
        rainIntensity: this.rainIntensity,
        accumulatedWater: this.accumulatedWater,
        waterMass,
        visibilityFactor,
        drainageRate: this.drainageRate,
        rainLevel: this._getRainLevelName()
      }
    };
  }

  _getRainLevelName() {
    if (this.rainIntensity === 0) return 'None';
    if (this.rainIntensity < 5) return 'Light';
    if (this.rainIntensity < 12) return 'Moderate';
    if (this.rainIntensity < 25) return 'Heavy';
    return 'Storm';
  }

  /**
   * 重置积水
   */
  reset() {
    this.accumulatedWater = 0;
  }

  dispose() {
    this.reset();
  }
}

