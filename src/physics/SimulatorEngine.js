/**
 * 模拟器引擎 - 可插拔算法架构
 * 支持动态添加/移除模拟算法，统一管理物理计算
 */

import { EventEmitter } from '../utils/EventEmitter.js';

export class SimulatorEngine extends EventEmitter {
  constructor(physicsWorld) {
    super();
    this.physicsWorld = physicsWorld;
    this.algorithms = new Map(); // algorithm name -> algorithm instance
    this.sortedAlgorithms = []; // sorted by priority
    this.enabled = true;
    this.debugMode = false;
  }

  /**
   * 注册模拟算法
   * @param {ISimulationAlgorithm} algorithm 
   */
  registerAlgorithm(algorithm) {
    if (!algorithm || !algorithm.name) {
      console.error('Invalid algorithm:', algorithm);
      return false;
    }

    if (this.algorithms.has(algorithm.name)) {
      console.warn(`Algorithm "${algorithm.name}" already registered, replacing...`);
      this.unregisterAlgorithm(algorithm.name);
    }

    this.algorithms.set(algorithm.name, algorithm);
    this._sortAlgorithms();
    
    // 初始化算法（如果算法需要scene参数，需要在注册后手动调用initialize）
    // 注意：这里只传入physicsWorld，scene参数需要在外部手动设置
    if (algorithm.initialize && algorithm.initialize.length <= 1) {
      algorithm.initialize(this.physicsWorld);
    }

    this.emit('algorithm:registered', algorithm.name);
    console.log(`✅ Algorithm registered: ${algorithm.name} (priority: ${algorithm.priority || 0})`);
    return true;
  }

  /**
   * 注销模拟算法
   * @param {string} name 
   */
  unregisterAlgorithm(name) {
    const algorithm = this.algorithms.get(name);
    if (!algorithm) {
      console.warn(`Algorithm "${name}" not found`);
      return false;
    }

    // 清理算法
    if (algorithm.dispose) {
      algorithm.dispose();
    }

    this.algorithms.delete(name);
    this._sortAlgorithms();
    this.emit('algorithm:unregistered', name);
    console.log(`❌ Algorithm unregistered: ${name}`);
    return true;
  }

  /**
   * 获取算法实例
   * @param {string} name 
   */
  getAlgorithm(name) {
    return this.algorithms.get(name);
  }

  /**
   * 启用/禁用算法
   * @param {string} name 
   * @param {boolean} enabled 
   */
  setAlgorithmEnabled(name, enabled) {
    const algorithm = this.algorithms.get(name);
    if (algorithm) {
      algorithm.enabled = enabled;
      this.emit('algorithm:toggled', { name, enabled });
      console.log(`${enabled ? '✅' : '⏸️'} Algorithm ${name}: ${enabled ? 'enabled' : 'disabled'}`);
    }
  }

  /**
   * 更新所有算法
   * @param {number} deltaTime - 时间增量（秒）
   * @param {object} shipState - 船体状态
   * @param {object} environment - 环境状态
   */
  update(deltaTime, shipState, environment) {
    if (!this.enabled || !shipState.body) return;

    const results = [];

    // 按优先级执行所有启用的算法
    for (const algorithm of this.sortedAlgorithms) {
      if (algorithm.enabled === false) continue;

      try {
        const result = algorithm.update(deltaTime, shipState, environment);
        if (result) {
          results.push({
            name: algorithm.name,
            result
          });

          // 应用力和力矩到刚体（如果算法没有直接施加）
          // 注意：如果算法返回 null，表示已经直接施加，不需要再次施加
          if (result.force !== null && result.force !== undefined) {
            const forceLen = result.force.length();
            if (forceLen > 0.001) {  // 避免施加极小的力
              shipState.body.applyForce(
                result.force,
                result.point || shipState.body.position
              );
            }
          }

          if (result.torque !== null && result.torque !== undefined) {
            const torqueLen = result.torque.length();
            if (torqueLen > 0.001) {  // 避免施加极小的力矩
              shipState.body.torque.vadd(result.torque, shipState.body.torque);
            }
          }
        }
      } catch (error) {
        console.error(`Error in algorithm "${algorithm.name}":`, error);
        this.emit('algorithm:error', { name: algorithm.name, error });
      }
    }

    if (this.debugMode) {
      this.emit('update:complete', { results });
    }

    return results;
  }

  /**
   * 按优先级排序算法（优先级高的先执行）
   * @private
   */
  _sortAlgorithms() {
    this.sortedAlgorithms = Array.from(this.algorithms.values())
      .sort((a, b) => (b.priority || 0) - (a.priority || 0));
  }

  /**
   * 获取所有算法信息
   */
  getAlgorithmInfo() {
    return this.sortedAlgorithms.map(alg => ({
      name: alg.name,
      priority: alg.priority || 0,
      enabled: alg.enabled !== false,
      description: alg.description || ''
    }));
  }

  /**
   * 清理所有算法
   */
  dispose() {
    for (const algorithm of this.algorithms.values()) {
      if (algorithm.dispose) {
        algorithm.dispose();
      }
    }
    this.algorithms.clear();
    this.sortedAlgorithms = [];
    this.emit('disposed');
  }
}

/**
 * 模拟算法基类
 */
export class SimulationAlgorithm {
  constructor(name, priority = 0) {
    this.name = name;
    this.priority = priority;
    this.enabled = true;
    this.description = '';
  }

  /**
   * 初始化算法
   * @param {object} physicsWorld 
   */
  initialize(physicsWorld) {
    // Override in subclass
  }

  /**
   * 更新算法，计算力和力矩
   * @param {number} deltaTime 
   * @param {object} shipState 
   * @param {object} environment 
   * @returns {ForceResult}
   */
  update(deltaTime, shipState, environment) {
    // Override in subclass
    return null;
  }

  /**
   * 清理资源
   */
  dispose() {
    // Override in subclass
  }
}

