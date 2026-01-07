/**
 * 自动化测试运行器
 * Auto Test Runner
 * 
 * 监控代码变化，自动运行测试，并根据测试结果调整代码
 */

export class AutoTestRunner {
  constructor() {
    this.testResults = [];
    this.isRunning = false;
    this.checkInterval = 5000; // 每5秒检查一次代码变化
    this.lastCheckTime = Date.now();
    this.fileHashes = new Map();
  }

  /**
   * 启动自动测试
   */
  start() {
    if (this.isRunning) {
      console.warn('⚠️ 自动测试已在运行 | Auto test already running');
      return;
    }
    
    this.isRunning = true;
    console.log('🧪 自动测试系统启动 | Auto test system started');
    this._runTests();
  }

  /**
   * 停止自动测试
   */
  stop() {
    this.isRunning = false;
    console.log('⏹️ 自动测试系统停止 | Auto test system stopped');
  }

  /**
   * 运行测试套件
   * @private
   */
  async _runTests() {
    if (!this.isRunning) return;
    
    try {
      console.log('🧪 开始运行测试 | Running tests...');
      
      // 运行所有测试
      const results = await this._executeTests();
      
      // 分析测试结果
      this._analyzeResults(results);
      
      // 如果测试失败，尝试自动修复
      if (results.failed > 0) {
        await this._attemptAutoFix(results);
      }
      
      // 记录测试结果
      this.testResults.push({
        timestamp: Date.now(),
        results: results
      });
      
      console.log(`✅ 测试完成 | Tests completed: ${results.passed} passed, ${results.failed} failed`);
      
    } catch (error) {
      console.error('❌ 测试运行出错 | Test execution error:', error);
    }
    
    // 定期运行测试
    setTimeout(() => {
      if (this.isRunning) {
        this._runTests();
      }
    }, this.checkInterval);
  }

  /**
   * 执行测试
   * @private
   */
  async _executeTests() {
    const results = {
      total: 0,
      passed: 0,
      failed: 0,
      tests: []
    };
    
    // 测试1: 检查船体控制器
    results.total++;
    try {
      if (typeof window !== 'undefined' && window.shipController) {
        if (window.shipController.loaded) {
          results.passed++;
          results.tests.push({ name: 'Ship Controller Loaded', status: 'passed' });
        } else {
          results.failed++;
          results.tests.push({ name: 'Ship Controller Loaded', status: 'failed', error: 'Ship not loaded' });
        }
      } else {
        results.failed++;
        results.tests.push({ name: 'Ship Controller Loaded', status: 'failed', error: 'ShipController not found' });
      }
    } catch (error) {
      results.failed++;
      results.tests.push({ name: 'Ship Controller Loaded', status: 'failed', error: error.message });
    }
    
    // 测试2: 检查物理引擎
    results.total++;
    try {
      if (typeof window !== 'undefined' && window.simulatorEngine) {
        const algCount = window.simulatorEngine.algorithms?.size || 0;
        if (algCount > 0) {
          results.passed++;
          results.tests.push({ name: 'Simulator Engine', status: 'passed', info: `${algCount} algorithms` });
        } else {
          results.failed++;
          results.tests.push({ name: 'Simulator Engine', status: 'failed', error: 'No algorithms registered' });
        }
      } else {
        results.failed++;
        results.tests.push({ name: 'Simulator Engine', status: 'failed', error: 'SimulatorEngine not found' });
      }
    } catch (error) {
      results.failed++;
      results.tests.push({ name: 'Simulator Engine', status: 'failed', error: error.message });
    }
    
    // 测试3: 检查天气系统
    results.total++;
    try {
      if (typeof window !== 'undefined' && window.weatherSystem) {
        const weather = window.weatherSystem.getWeatherState();
        if (weather !== null && typeof weather === 'object') {
          results.passed++;
          results.tests.push({ name: 'Weather System', status: 'passed' });
        } else {
          results.failed++;
          results.tests.push({ name: 'Weather System', status: 'failed', error: 'Invalid weather state' });
        }
      } else {
        results.failed++;
        results.tests.push({ name: 'Weather System', status: 'failed', error: 'WeatherSystem not found' });
      }
    } catch (error) {
      results.failed++;
      results.tests.push({ name: 'Weather System', status: 'failed', error: error.message });
    }
    
    // 测试4: 检查舱室管理器
    results.total++;
    try {
      if (typeof window !== 'undefined' && window.cabinManager) {
        const cabinCount = window.cabinManager.cabins?.size || 0;
        if (cabinCount > 0) {
          results.passed++;
          results.tests.push({ name: 'Cabin Manager', status: 'passed', info: `${cabinCount} cabins` });
        } else {
          results.failed++;
          results.tests.push({ name: 'Cabin Manager', status: 'failed', error: 'No cabins registered' });
        }
      } else {
        results.failed++;
        results.tests.push({ name: 'Cabin Manager', status: 'failed', error: 'CabinManager not found' });
      }
    } catch (error) {
      results.failed++;
      results.tests.push({ name: 'Cabin Manager', status: 'failed', error: error.message });
    }
    
    // 测试5: 检查自动稳定系统
    results.total++;
    try {
      if (typeof window !== 'undefined' && window.autoStabilizationSystem) {
        const enabled = window.autoStabilizationSystem.enabled;
        results.passed++;
        results.tests.push({ name: 'Auto Stabilization System', status: 'passed', info: `enabled: ${enabled}` });
      } else {
        results.failed++;
        results.tests.push({ name: 'Auto Stabilization System', status: 'failed', error: 'AutoStabilizationSystem not found' });
      }
    } catch (error) {
      results.failed++;
      results.tests.push({ name: 'Auto Stabilization System', status: 'failed', error: error.message });
    }
    
    return results;
  }

  /**
   * 分析测试结果
   * @private
   */
  _analyzeResults(results) {
    const passRate = (results.passed / results.total) * 100;
    console.log(`📊 测试通过率 | Test pass rate: ${passRate.toFixed(1)}%`);
    
    if (results.failed > 0) {
      console.warn('⚠️ 测试失败详情 | Failed tests:');
      results.tests.filter(t => t.status === 'failed').forEach(test => {
        console.warn(`  - ${test.name}: ${test.error}`);
      });
    }
  }

  /**
   * 尝试自动修复
   * @private
   */
  async _attemptAutoFix(results) {
    console.log('🔧 尝试自动修复 | Attempting auto-fix...');
    
    // 根据失败的测试尝试修复
    for (const test of results.tests) {
      if (test.status === 'failed') {
        // 这里可以添加自动修复逻辑
        // 例如：如果船体未加载，尝试重新加载
        if (test.name === 'Ship Controller Loaded' && test.error === 'Ship not loaded') {
          console.log('🔧 尝试重新加载船体 | Attempting to reload ship...');
          // 可以触发重新加载逻辑
        }
      }
    }
  }

  /**
   * 获取测试报告
   */
  getReport() {
    return {
      totalTests: this.testResults.length,
      recentResults: this.testResults.slice(-10),
      summary: this._calculateSummary()
    };
  }

  /**
   * 计算摘要
   * @private
   */
  _calculateSummary() {
    if (this.testResults.length === 0) return null;
    
    const recent = this.testResults.slice(-10);
    let totalPassed = 0;
    let totalFailed = 0;
    let totalTests = 0;
    
    recent.forEach(result => {
      totalPassed += result.results.passed;
      totalFailed += result.results.failed;
      totalTests += result.results.total;
    });
    
    return {
      totalTests,
      totalPassed,
      totalFailed,
      passRate: totalTests > 0 ? (totalPassed / totalTests) * 100 : 0
    };
  }
}

// 如果在浏览器环境中，将测试运行器暴露到全局
if (typeof window !== 'undefined') {
  window.AutoTestRunner = AutoTestRunner;
}

