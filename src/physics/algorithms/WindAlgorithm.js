/**
 * 风力算法
 * 计算风对船体的侧向力和力矩
 */

import * as CANNON from '../../../public/lib/cannon-es.js';
import { SimulationAlgorithm } from '../SimulatorEngine.js';

export class WindAlgorithm extends SimulationAlgorithm {
  constructor(config = {}) {
    super('Wind', 80); // 高优先级
    this.description = 'Wind force simulation on ship structure';
    
    // 风力参数
    this.windSpeed = config.windSpeed || 0; // m/s
    this.windDirection = config.windDirection || 0; // 角度（0-360）
    this.gustIntensity = config.gustIntensity || 0.2; // 阵风强度
    this.dragCoefficient = config.dragCoefficient || 0.8;
    
    // 船体风阻参数
    this.frontalArea = config.frontalArea || 50; // m²（正面投影面积）
    this.lateralArea = config.lateralArea || 200; // m²（侧面投影面积）
    this.centerOfPressure = config.centerOfPressure || { x: 0, y: 5, z: 0 }; // 风压中心
    
    this.timeAccumulator = 0;
  }

  setWindSpeed(speed) {
    this.windSpeed = Math.max(0, speed);
  }

  setWindDirection(angle) {
    this.windDirection = angle % 360;
  }

  update(deltaTime, shipState, environment) {
    const { body } = shipState;
    
    if (!body || this.windSpeed === 0) return null;

    this.timeAccumulator += deltaTime;

    // 计算阵风（正弦波叠加）
    const gustFactor = 1.0 + this.gustIntensity * (
      Math.sin(this.timeAccumulator * 0.5) * 0.6 +
      Math.sin(this.timeAccumulator * 1.3) * 0.3 +
      Math.sin(this.timeAccumulator * 2.1) * 0.1
    );

    const effectiveWindSpeed = this.windSpeed * gustFactor;

    // 风向向量（世界坐标系）
    const windDirRad = (this.windDirection * Math.PI) / 180;
    const windDirWorld = new CANNON.Vec3(
      Math.sin(windDirRad),
      0,
      Math.cos(windDirRad)
    );

    // 船体朝向向量
    const shipForward = body.quaternion.vmult(new CANNON.Vec3(1, 0, 0));
    shipForward.y = 0;
    shipForward.normalize();

    // 计算风向与船体的夹角
    const dotProduct = windDirWorld.dot(shipForward);
    const angle = Math.acos(Math.max(-1, Math.min(1, dotProduct)));

    // 根据角度选择投影面积（0°=正面，90°=侧面）
    const angleNorm = Math.abs(angle) / (Math.PI / 2); // 0-1
    const effectiveArea = this.frontalArea + 
      (this.lateralArea - this.frontalArea) * angleNorm;

    // 风压计算：F = 0.5 * ρ * v² * Cd * A
    // ρ(空气密度) ≈ 1.225 kg/m³
    const airDensity = 1.225;
    const dynamicPressure = 0.5 * airDensity * effectiveWindSpeed * effectiveWindSpeed;
    const forceMagnitude = dynamicPressure * this.dragCoefficient * effectiveArea;

    // 风力方向
    const windForce = windDirWorld.scale(forceMagnitude);

    // 风压中心（世界坐标）
    const pressureCenter = body.pointToWorldFrame(
      new CANNON.Vec3(
        this.centerOfPressure.x,
        this.centerOfPressure.y,
        this.centerOfPressure.z
      )
    );

    // 计算力矩
    const r = pressureCenter.vsub(body.position);
    const torque = r.cross(windForce);

    return {
      force: windForce,
      torque: torque,
      point: pressureCenter,
      metadata: {
        windSpeed: effectiveWindSpeed,
        windDirection: this.windDirection,
        angle: (angle * 180) / Math.PI,
        effectiveArea,
        forceMagnitude
      }
    };
  }

  /**
   * 设置风力等级（蒲福风级 0-12）
   */
  setBeaufortScale(scale) {
    // 蒲福风级对应的风速（m/s）
    const beaufortToWindSpeed = {
      0: 0,    // 无风
      1: 1,    // 软风
      2: 2.5,  // 轻风
      3: 4.5,  // 微风
      4: 7,    // 和风
      5: 10,   // 清劲风
      6: 13,   // 强风
      7: 16,   // 疾风
      8: 19,   // 大风
      9: 23,   // 烈风
      10: 27,  // 狂风
      11: 31,  // 暴风
      12: 35   // 飓风
    };

    this.windSpeed = beaufortToWindSpeed[Math.min(12, Math.max(0, scale))] || 0;
  }
}

