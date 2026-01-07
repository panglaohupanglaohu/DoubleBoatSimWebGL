/**
 * 自稳算法
 * 提供船体自动恢复直立的力矩
 */

import * as CANNON from '../../../public/lib/cannon-es.js';
import { SimulationAlgorithm } from '../SimulatorEngine.js';

export class StabilizerAlgorithm extends SimulationAlgorithm {
  constructor(config = {}) {
    super('Stabilizer', 90); // 高优先级（仅次于浮力）
    this.description = 'Ship stabilizer system with upright torque';
    
    // 自稳参数
    this.enableStabilizer = config.enableStabilizer !== false; // 默认启用
    this.uprightStiffness = config.uprightStiffness || 8.0;
    this.uprightDamping = config.uprightDamping || 4.0;
    this.wobbleBoost = config.wobbleBoost || 1.0; // >1 表示更容易摇晃
    
    this.minAngleThreshold = 0.01; // 小于此角度不施加力矩
  }

  setStiffness(value) {
    this.uprightStiffness = Math.max(0, value);
  }

  setDamping(value) {
    this.uprightDamping = Math.max(0, value);
  }

  setWobbleBoost(value) {
    this.wobbleBoost = Math.max(0.2, value);
  }

  update(deltaTime, shipState, environment) {
    const { body } = shipState;
    
    if (!body || !this.enableStabilizer) return null;

    // 世界坐标系的上方向
    const worldUp = new CANNON.Vec3(0, 1, 0);
    
    // 船体坐标系的上方向（转换到世界坐标）
    const bodyUp = body.quaternion.vmult(new CANNON.Vec3(0, 1, 0));

    // 计算两个向量的夹角
    const dot = Math.max(-1, Math.min(1, bodyUp.dot(worldUp)));
    const angle = Math.acos(dot);

    // 如果角度很小，不需要自稳力矩
    if (angle < this.minAngleThreshold) return null;

    // 计算旋转轴（叉乘）
    const axis = bodyUp.cross(worldUp);
    
    // 计算有效刚度和阻尼（wobbleBoost 越大，自稳越弱）
    const wobble = this.wobbleBoost;
    const effStiffness = this.uprightStiffness / wobble;
    const effDamping = this.uprightDamping / wobble;
    
    if (effStiffness < 0.01 && effDamping < 0.01) return null;

    // 自稳力矩 = 恢复力矩 - 阻尼力矩
    // 恢复力矩：axis * angle * stiffness
    // 阻尼力矩：angularVelocity * damping
    const restoreTorque = axis.scale(angle * effStiffness);
    const dampingTorque = body.angularVelocity.scale(effDamping);
    const totalTorque = restoreTorque.vsub(dampingTorque);

    return {
      force: new CANNON.Vec3(0, 0, 0), // 不施加力，只施加力矩
      torque: totalTorque,
      metadata: {
        angle: (angle * 180) / Math.PI,
        effStiffness,
        effDamping,
        wobbleBoost: wobble
      }
    };
  }
}

