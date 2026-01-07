/**
 * 船体稳定性测试系统
 * Ship Stability Test System
 * 
 * 测试船体在各种条件下的稳定性表现
 */

import * as CANNON from '../../public/lib/cannon-es.js';
import { SimulatorEngine } from '../physics/SimulatorEngine.js';
import { BuoyancyAlgorithm } from '../physics/algorithms/BuoyancyAlgorithm.js';
import { StabilizerAlgorithm } from '../physics/algorithms/StabilizerAlgorithm.js';
import { WindAlgorithm } from '../physics/algorithms/WindAlgorithm.js';
import { RainAlgorithm } from '../physics/algorithms/RainAlgorithm.js';
import { getWaveHeight, waveParams } from '../waves.js';

export class ShipStabilityTest {
  constructor() {
    this.results = [];
    this.testConfig = {
      duration: 10,        // 测试持续时间（秒）
      timeStep: 1 / 60,     // 物理时间步长
      sampleRate: 10,      // 采样频率（每N帧采样一次）
      stabilityThreshold: {
        maxTilt: 45,       // 最大倾斜角度（度）
        maxSink: 15,       // 最大下沉深度（米）
        maxOscillation: 0.5, // 最大振荡幅度（米）
        recoveryTime: 5     // 恢复时间（秒）
      }
    };
  }

  /**
   * 运行所有测试
   */
  async runAllTests() {
    console.log('🧪 开始船体稳定性测试 | Starting Ship Stability Tests...\n');

    const tests = [
      { name: '基础稳定性测试', func: this.testBasicStability.bind(this) },
      { name: '波浪响应测试', func: this.testWaveResponse.bind(this) },
      { name: '风力影响测试', func: this.testWindEffect.bind(this) },
      { name: '降雨影响测试', func: this.testRainEffect.bind(this) },
      { name: '极端天气测试', func: this.testExtremeWeather.bind(this) },
      { name: '参数变化测试', func: this.testParameterChanges.bind(this) },
      { name: '扰动恢复测试', func: this.testDisturbanceRecovery.bind(this) }
    ];

    for (const test of tests) {
      try {
        console.log(`\n📋 运行测试: ${test.name} | Running: ${test.name}`);
        const result = await test.func();
        this.results.push({ name: test.name, ...result });
        this.printTestResult(test.name, result);
      } catch (error) {
        console.error(`❌ 测试失败 | Test failed: ${test.name}`, error);
        this.results.push({ name: test.name, passed: false, error: error.message });
      }
    }

    this.printSummary();
    return this.results;
  }

  /**
   * 测试1: 基础稳定性
   */
  async testBasicStability() {
    const { world, simulator, shipBody } = this.setupTestEnvironment({
      mass: 7000,
      buoyancyCoeff: 400,
      enableStabilizer: true
    });

    const metrics = this.runSimulation(world, simulator, shipBody, {
      duration: 5,
      environment: { time: 0, weather: { windSpeed: 0, rainIntensity: 0 } }
    });

    const passed = 
      metrics.maxTilt < this.testConfig.stabilityThreshold.maxTilt &&
      metrics.maxSink < this.testConfig.stabilityThreshold.maxSink &&
      metrics.finalTilt < 5;

    return {
      passed,
      metrics,
      message: passed 
        ? '✅ 基础稳定性良好 | Basic stability good'
        : '❌ 基础稳定性不足 | Basic stability insufficient'
    };
  }

  /**
   * 测试2: 波浪响应
   */
  async testWaveResponse() {
    // 临时设置波浪参数
    const originalAmplitude = waveParams.amplitude;
    const originalSpeed = waveParams.speed;
    waveParams.amplitude = 2.0;
    waveParams.speed = 2.0;

    const { world, simulator, shipBody } = this.setupTestEnvironment({
      mass: 7000,
      buoyancyCoeff: 400
    });

    const metrics = this.runSimulation(world, simulator, shipBody, {
      duration: 10,
      environment: { time: 0, weather: { windSpeed: 0, rainIntensity: 0 } }
    });

    // 恢复原始波浪参数
    waveParams.amplitude = originalAmplitude;
    waveParams.speed = originalSpeed;

    const passed = 
      metrics.maxTilt < 30 &&
      metrics.oscillationAmplitude < 2.0 &&
      !metrics.capsized;

    return {
      passed,
      metrics,
      message: passed
        ? '✅ 波浪响应正常 | Wave response normal'
        : '❌ 波浪响应异常 | Wave response abnormal'
    };
  }

  /**
   * 测试3: 风力影响
   */
  async testWindEffect() {
    const { world, simulator, shipBody } = this.setupTestEnvironment({
      mass: 7000,
      buoyancyCoeff: 400,
      windSpeed: 15
    });

    const metrics = this.runSimulation(world, simulator, shipBody, {
      duration: 8,
      environment: { time: 0, weather: { windSpeed: 15, rainIntensity: 0 } }
    });

    const passed = 
      metrics.maxTilt < 25 &&
      metrics.maxDrift < 50 &&
      !metrics.capsized;

    return {
      passed,
      metrics,
      message: passed
        ? '✅ 风力影响可控 | Wind effect controllable'
        : '❌ 风力影响过大 | Wind effect too strong'
    };
  }

  /**
   * 测试4: 降雨影响
   */
  async testRainEffect() {
    const { world, simulator, shipBody } = this.setupTestEnvironment({
      mass: 7000,
      buoyancyCoeff: 400,
      rainIntensity: 50
    });

    const metrics = this.runSimulation(world, simulator, shipBody, {
      duration: 10,
      environment: { time: 0, weather: { windSpeed: 0, rainIntensity: 50 } }
    });

    const passed = 
      metrics.maxSink < 8 &&
      metrics.finalSink < 3 &&
      !metrics.capsized;

    return {
      passed,
      metrics,
      message: passed
        ? '✅ 降雨影响可控 | Rain effect controllable'
        : '❌ 降雨导致过度下沉 | Rain causes excessive sinking'
    };
  }

  /**
   * 测试5: 极端天气
   */
  async testExtremeWeather() {
    // 临时设置波浪参数
    const originalAmplitude = waveParams.amplitude;
    const originalSpeed = waveParams.speed;
    waveParams.amplitude = 3.0;
    waveParams.speed = 3.0;

    const { world, simulator, shipBody } = this.setupTestEnvironment({
      mass: 7000,
      buoyancyCoeff: 400,
      windSpeed: 30,
      rainIntensity: 80
    });

    const metrics = this.runSimulation(world, simulator, shipBody, {
      duration: 15,
      environment: { time: 0, weather: { windSpeed: 30, rainIntensity: 80 } }
    });

    // 恢复原始波浪参数
    waveParams.amplitude = originalAmplitude;
    waveParams.speed = originalSpeed;

    const passed = 
      !metrics.capsized &&
      metrics.maxTilt < 60 &&
      metrics.recoveryTime < 10;

    return {
      passed,
      metrics,
      message: passed
        ? '✅ 极端天气下保持稳定 | Stable in extreme weather'
        : '⚠️ 极端天气下不稳定 | Unstable in extreme weather'
    };
  }

  /**
   * 测试6: 参数变化
   */
  async testParameterChanges() {
    const configs = [
      { mass: 5000, buoyancyCoeff: 300, name: '轻量配置' },
      { mass: 7000, buoyancyCoeff: 400, name: '标准配置' },
      { mass: 10000, buoyancyCoeff: 600, name: '重量配置' }
    ];

    const results = [];
    for (const config of configs) {
      const { world, simulator, shipBody } = this.setupTestEnvironment(config);
      const metrics = this.runSimulation(world, simulator, shipBody, {
        duration: 5,
        environment: { time: 0, weather: { windSpeed: 10, rainIntensity: 10 } }
      });

      results.push({
        config: config.name,
        passed: metrics.maxTilt < 30 && !metrics.capsized,
        metrics
      });
    }

    const allPassed = results.every(r => r.passed);

    return {
      passed: allPassed,
      metrics: { configs: results },
      message: allPassed
        ? '✅ 所有参数配置稳定 | All configurations stable'
        : '❌ 部分配置不稳定 | Some configurations unstable'
    };
  }

  /**
   * 测试7: 扰动恢复
   */
  async testDisturbanceRecovery() {
    const { world, simulator, shipBody } = this.setupTestEnvironment({
      mass: 7000,
      buoyancyCoeff: 400
    });

    // 初始稳定
    this.runSimulation(world, simulator, shipBody, {
      duration: 2,
      environment: { time: 0, weather: { windSpeed: 0, rainIntensity: 0 } }
    });

    // 施加扰动（模拟碰撞或突然转向）
    shipBody.angularVelocity.set(
      (Math.random() - 0.5) * 2,
      (Math.random() - 0.5) * 2,
      (Math.random() - 0.5) * 2
    );
    shipBody.velocity.set(
      (Math.random() - 0.5) * 5,
      (Math.random() - 0.5) * 2,
      (Math.random() - 0.5) * 5
    );

    // 测试恢复
    const metrics = this.runSimulation(world, simulator, shipBody, {
      duration: 8,
      environment: { time: 2, weather: { windSpeed: 0, rainIntensity: 0 } },
      trackRecovery: true
    });

    const passed = 
      metrics.recoveryTime < this.testConfig.stabilityThreshold.recoveryTime &&
      metrics.finalTilt < 5;

    return {
      passed,
      metrics,
      message: passed
        ? '✅ 扰动后快速恢复 | Quick recovery after disturbance'
        : '❌ 扰动后恢复缓慢 | Slow recovery after disturbance'
    };
  }

  /**
   * 设置测试环境
   */
  setupTestEnvironment(config = {}) {
    // 创建物理世界
    const world = new CANNON.World({
      gravity: new CANNON.Vec3(0, -9.82, 0)
    });
    world.broadphase = new CANNON.SAPBroadphase(world);
    world.solver.iterations = 14;

    // 创建模拟器
    const simulator = new SimulatorEngine(world);

    // 注册算法
    const buoyancyAlg = new BuoyancyAlgorithm({
      buoyancyCoeff: config.buoyancyCoeff || 400,
      dragCoeff: 8,
      density: 1.0,
      yFlip: -1
    });
    buoyancyAlg.generateBuoyancyPoints({ x: 100, y: 10, z: 20 });
    simulator.registerAlgorithm(buoyancyAlg);

    const stabilizerAlg = new StabilizerAlgorithm({
      enableStabilizer: config.enableStabilizer !== false,
      uprightStiffness: 12.0,
      uprightDamping: 6.0,
      wobbleBoost: 0.8
    });
    simulator.registerAlgorithm(stabilizerAlg);

    if (config.windSpeed > 0) {
      const windAlg = new WindAlgorithm({
        windSpeed: config.windSpeed,
        windDirection: 180
      });
      simulator.registerAlgorithm(windAlg);
    }

    if (config.rainIntensity > 0) {
      const rainAlg = new RainAlgorithm({
        rainIntensity: config.rainIntensity
      });
      simulator.registerAlgorithm(rainAlg);
    }

    // 创建船体
    const halfExtents = new CANNON.Vec3(50, 5, 10);
    const shape = new CANNON.Box(halfExtents);
    const shipBody = new CANNON.Body({
      mass: config.mass || 7000,
      shape,
      position: new CANNON.Vec3(0, 2, 0),
      linearDamping: 0.15,
      angularDamping: 0.6
    });
    world.addBody(shipBody);

    return { world, simulator, shipBody };
  }

  /**
   * 运行模拟并收集指标
   */
  runSimulation(world, simulator, shipBody, options = {}) {
    const {
      duration = this.testConfig.duration,
      timeStep = this.testConfig.timeStep,
      environment = { time: 0, weather: {} },
      trackRecovery = false
    } = options;

    const metrics = {
      maxTilt: 0,
      maxSink: 0,
      maxDrift: 0,
      oscillationAmplitude: 0,
      finalTilt: 0,
      finalSink: 0,
      capsized: false,
      recoveryTime: trackRecovery ? duration : null,
      positions: [],
      tilts: []
    };

    let elapsed = 0;
    let sampleCount = 0;
    let initialTilt = null;
    let recoveryStartTime = null;

    while (elapsed < duration) {
      // 更新环境时间
      environment.time = elapsed;

      // 更新模拟器
      const shipState = { body: shipBody, mesh: null };
      simulator.update(timeStep, shipState, environment);

      // 物理步进
      world.step(timeStep, timeStep, 3);

      // 采样数据
      if (sampleCount % this.testConfig.sampleRate === 0) {
        const pos = shipBody.position;
        const quat = shipBody.quaternion;

        // 计算倾斜角度
        const bodyUp = quat.vmult(new CANNON.Vec3(0, 1, 0));
        const worldUp = new CANNON.Vec3(0, 1, 0);
        const dot = Math.max(-1, Math.min(1, bodyUp.dot(worldUp)));
        const tilt = Math.acos(dot) * (180 / Math.PI);

        // 计算水面高度
        const waterH = getWaveHeight(pos.x, -pos.z, elapsed) * -1;
        const sink = waterH - pos.y;

        // 计算漂移距离
        const drift = Math.sqrt(pos.x * pos.x + pos.z * pos.z);

        // 更新指标
        metrics.maxTilt = Math.max(metrics.maxTilt, tilt);
        metrics.maxSink = Math.max(metrics.maxSink, sink);
        metrics.maxDrift = Math.max(metrics.maxDrift, drift);
        metrics.capsized = metrics.capsized || tilt > 80;

        metrics.positions.push({ x: pos.x, y: pos.y, z: pos.z, time: elapsed });
        metrics.tilts.push({ tilt, time: elapsed });

        // 跟踪恢复
        if (trackRecovery) {
          if (initialTilt === null && tilt > 10) {
            initialTilt = tilt;
            recoveryStartTime = elapsed;
          }
          if (recoveryStartTime !== null && tilt < 5 && metrics.recoveryTime === duration) {
            metrics.recoveryTime = elapsed - recoveryStartTime;
          }
        }
      }

      elapsed += timeStep;
      sampleCount++;
    }

    // 计算最终值
    if (metrics.tilts.length > 0) {
      metrics.finalTilt = metrics.tilts[metrics.tilts.length - 1].tilt;
    }
    if (metrics.positions.length > 0) {
      const lastPos = metrics.positions[metrics.positions.length - 1];
      const waterH = getWaveHeight(lastPos.x, -lastPos.z, elapsed) * -1;
      metrics.finalSink = waterH - lastPos.y;
    }

    // 计算振荡幅度
    if (metrics.positions.length > 10) {
      const yValues = metrics.positions.map(p => p.y);
      const maxY = Math.max(...yValues);
      const minY = Math.min(...yValues);
      metrics.oscillationAmplitude = maxY - minY;
    }

    return metrics;
  }

  /**
   * 打印测试结果
   */
  printTestResult(name, result) {
    console.log(`\n${result.passed ? '✅' : '❌'} ${name} | ${name}`);
    console.log(`   结果 | Result: ${result.message}`);
    if (result.metrics) {
      console.log(`   最大倾斜 | Max Tilt: ${result.metrics.maxTilt?.toFixed(2) || 'N/A'}°`);
      console.log(`   最大下沉 | Max Sink: ${result.metrics.maxSink?.toFixed(2) || 'N/A'} m`);
      if (result.metrics.recoveryTime !== null) {
        console.log(`   恢复时间 | Recovery Time: ${result.metrics.recoveryTime?.toFixed(2) || 'N/A'} s`);
      }
    }
  }

  /**
   * 打印测试总结
   */
  printSummary() {
    const passed = this.results.filter(r => r.passed).length;
    const total = this.results.length;
    const passRate = ((passed / total) * 100).toFixed(1);

    console.log('\n' + '='.repeat(60));
    console.log('📊 测试总结 | Test Summary');
    console.log('='.repeat(60));
    console.log(`总测试数 | Total Tests: ${total}`);
    console.log(`通过 | Passed: ${passed}`);
    console.log(`失败 | Failed: ${total - passed}`);
    console.log(`通过率 | Pass Rate: ${passRate}%`);
    console.log('='.repeat(60));

    if (passRate >= 80) {
      console.log('🎉 船体稳定性良好 | Ship stability is good!');
    } else if (passRate >= 60) {
      console.log('⚠️ 船体稳定性需要改进 | Ship stability needs improvement');
    } else {
      console.log('❌ 船体稳定性不足 | Ship stability is insufficient');
    }
  }

  /**
   * 导出测试报告
   */
  exportReport() {
    return {
      timestamp: new Date().toISOString(),
      config: this.testConfig,
      results: this.results,
      summary: {
        total: this.results.length,
        passed: this.results.filter(r => r.passed).length,
        failed: this.results.filter(r => !r.passed).length
      }
    };
  }
}

