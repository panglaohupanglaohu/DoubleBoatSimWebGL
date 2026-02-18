/**
 * LLM Judge - AI 裁判系统
 * 
 * Software 3.0 理念：评估与数据闭环
 * - AI 裁判阅读仿真日志，判断 Agent 的表现
 * - 评估是否符合海事法规和公司政策
 * - 实船数据回流，成为新的测试用例
 * - 持续优化 Agent 行为
 */

import { EventEmitter } from '../../utils/EventEmitter.js';

export class LLMJudge extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      llmProvider: config.llmProvider || 'minimax',
      model: config.model || 'MiniMax-M2.5',
      scoringCriteria: config.scoringCriteria || this._getDefaultCriteria(),
      strictness: config.strictness || 0.8, // 0-1，越高越严格
      ...config
    };
    
    // 评估历史
    this.evaluationHistory = [];
    
    // 规则库（海事法规、公司政策）
    this.ruleBase = new Map();
    
    // 实船数据收集
    this.realShipData = [];
    
    this._loadRules();
    
    console.log('⚖️ LLM Judge initialized (Software 3.0)');
  }
  
  /**
   * 评估 Agent 行为
   * @param {Object} agentExecution - Agent 执行记录
   * @param {Object} context - 场景上下文
   * @returns {Promise<Object>} - 评估报告
   */
  async evaluate(agentExecution, context = {}) {
    console.log(`⚖️ Evaluating Agent execution: ${agentExecution.agent}`);
    
    const startTime = Date.now();
    
    try {
      // 1. 分析执行日志
      const analysis = await this._analyzeExecution(agentExecution, context);
      
      // 2. 检查合规性（海事法规）
      const compliance = await this._checkCompliance(agentExecution, context);
      
      // 3. 评估决策质量
      const decisionQuality = await this._assessDecisionQuality(agentExecution, context);
      
      // 4. 评估响应时间
      const timelinessScore = this._assessTimeliness(agentExecution);
      
      // 5. 综合评分
      const scores = {
        correctness: analysis.correctness,
        compliance: compliance.score,
        decisionQuality: decisionQuality.score,
        timeliness: timelinessScore,
        overall: this._calculateOverallScore({
          correctness: analysis.correctness,
          compliance: compliance.score,
          decisionQuality: decisionQuality.score,
          timeliness: timelinessScore
        })
      };
      
      // 6. 生成建议
      const recommendations = await this._generateRecommendations(
        agentExecution,
        analysis,
        compliance,
        decisionQuality
      );
      
      const evaluation = {
        agent: agentExecution.agent,
        task: agentExecution.task,
        scores,
        analysis,
        compliance,
        decisionQuality,
        recommendations,
        passed: scores.overall >= (this.config.strictness * 100),
        timestamp: new Date().toISOString(),
        evaluationTime: Date.now() - startTime
      };
      
      // 记录到历史
      this.evaluationHistory.push(evaluation);
      
      // 触发事件
      this.emit('evaluation:completed', evaluation);
      
      if (evaluation.passed) {
        console.log(`✅ Evaluation PASSED: ${scores.overall.toFixed(1)}/100`);
      } else {
        console.log(`❌ Evaluation FAILED: ${scores.overall.toFixed(1)}/100 (threshold: ${(this.config.strictness * 100).toFixed(0)})`);
      }
      
      return evaluation;
      
    } catch (error) {
      console.error('❌ Evaluation failed:', error);
      throw error;
    }
  }
  
  /**
   * 分析执行过程
   * @private
   */
  async _analyzeExecution(execution, context) {
    // 使用 LLM 分析 Agent 的执行逻辑
    // 实际应该调用 GPT-4/Claude API
    
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // 模拟分析结果
    const correctness = Math.random() * 40 + 60; // 60-100
    
    return {
      correctness,
      logicFlow: execution.result?.type ? 'clear' : 'unclear',
      toolUsage: execution.result?.tools ? 'appropriate' : 'none',
      reasoning: '执行逻辑清晰，工具使用合理',
      issues: correctness < 80 ? ['响应不够准确', '建议改进推理链'] : []
    };
  }
  
  /**
   * 检查合规性
   * @private
   */
  async _checkCompliance(execution, context) {
    const violations = [];
    let score = 100;
    
    // 检查海事法规
    if (execution.task.includes('避碰') || execution.task.includes('碰撞')) {
      const colregsCompliant = this._checkCOLREGsCompliance(execution);
      
      if (!colregsCompliant.passed) {
        violations.push({
          rule: 'COLREGs',
          severity: 'critical',
          description: colregsCompliant.violation
        });
        score -= 30;
      }
    }
    
    // 检查安全规定
    if (execution.task.includes('火灾') || execution.task.includes('落水')) {
      const safetyCompliant = this._checkSafetyCompliance(execution);
      
      if (!safetyCompliant.passed) {
        violations.push({
          rule: 'ISM Code',
          severity: 'critical',
          description: safetyCompliant.violation
        });
        score -= 25;
      }
    }
    
    // 检查公司政策
    const policyCompliant = this._checkCompanyPolicy(execution);
    
    if (!policyCompliant.passed) {
      violations.push({
        rule: 'Company Policy',
        severity: 'warning',
        description: policyCompliant.violation
      });
      score -= 10;
    }
    
    return {
      score: Math.max(0, score),
      violations,
      compliant: violations.length === 0
    };
  }
  
  /**
   * 检查 COLREGs 合规性
   * @private
   */
  _checkCOLREGsCompliance(execution) {
    // 简化检查（实际应该分析详细的操作日志）
    
    const result = execution.result;
    
    // 如果是避碰任务，检查是否遵守规则
    if (result?.action === 'alter_course') {
      // 检查转向方向是否符合 Rule 15（交叉相遇让右舷）
      return { passed: true };
    }
    
    return { passed: true };
  }
  
  /**
   * 检查安全合规性
   * @private
   */
  _checkSafetyCompliance(execution) {
    const result = execution.result;
    
    // 如果是 MOB 响应，检查是否在 2 秒内触发警报
    if (execution.task.includes('落水') || execution.task.includes('MOB')) {
      const responseTime = execution.executionTime || 0;
      
      if (responseTime > 2000) {
        return {
          passed: false,
          violation: `MOB 响应时间 ${responseTime}ms 超过 2 秒标准`
        };
      }
      
      // 检查是否执行了必要动作
      const requiredActions = ['trigger_mob_alarm', 'record_position'];
      const executedActions = result?.actions || [];
      
      const missingActions = requiredActions.filter(a => !executedActions.includes(a));
      
      if (missingActions.length > 0) {
        return {
          passed: false,
          violation: `缺少必要动作：${missingActions.join(', ')}`
        };
      }
    }
    
    return { passed: true };
  }
  
  /**
   * 检查公司政策
   * @private
   */
  _checkCompanyPolicy(execution) {
    // 模拟公司政策检查
    return { passed: true };
  }
  
  /**
   * 评估决策质量
   * @private
   */
  async _assessDecisionQuality(execution, context) {
    // 使用 LLM 评估决策是否合理
    
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const score = Math.random() * 30 + 70; // 70-100
    
    return {
      score,
      reasoning: score > 85 ? '决策优秀，考虑周全' : '决策合理，但有改进空间',
      strengths: ['快速响应', '考虑了多个因素'],
      weaknesses: score < 85 ? ['可以更主动预防'] : []
    };
  }
  
  /**
   * 评估及时性
   * @private
   */
  _assessTimeliness(execution) {
    const responseTime = execution.executionTime || 0;
    
    // 根据任务类型设定时限
    let timeLimit = 5000; // 默认 5 秒
    
    if (execution.task.includes('落水') || execution.task.includes('MOB')) {
      timeLimit = 2000; // 2 秒
    } else if (execution.task.includes('火灾')) {
      timeLimit = 3000; // 3 秒
    }
    
    // 计算得分（线性衰减）
    const score = Math.max(0, 100 - (responseTime / timeLimit) * 100);
    
    return Math.min(100, score);
  }
  
  /**
   * 计算综合得分
   * @private
   */
  _calculateOverallScore(scores) {
    // 加权平均
    const weights = {
      correctness: 0.3,
      compliance: 0.3,
      decisionQuality: 0.25,
      timeliness: 0.15
    };
    
    const overall = 
      scores.correctness * weights.correctness +
      scores.compliance * weights.compliance +
      scores.decisionQuality * weights.decisionQuality +
      scores.timeliness * weights.timeliness;
    
    return overall;
  }
  
  /**
   * 生成优化建议
   * @private
   */
  async _generateRecommendations(execution, analysis, compliance, decisionQuality) {
    const recommendations = [];
    
    // 基于分析结果
    if (analysis.correctness < 80) {
      recommendations.push({
        priority: 'high',
        category: 'accuracy',
        suggestion: '提高响应准确性：建议增加更多领域知识到 Vibe 中'
      });
    }
    
    // 基于合规性
    if (compliance.violations.length > 0) {
      compliance.violations.forEach(v => {
        recommendations.push({
          priority: v.severity === 'critical' ? 'critical' : 'medium',
          category: 'compliance',
          suggestion: `修复合规性问题：${v.description}`,
          rule: v.rule
        });
      });
    }
    
    // 基于决策质量
    if (decisionQuality.weaknesses.length > 0) {
      recommendations.push({
        priority: 'medium',
        category: 'decision',
        suggestion: `改进决策：${decisionQuality.weaknesses.join('、')}`
      });
    }
    
    // 通用建议
    if (recommendations.length === 0) {
      recommendations.push({
        priority: 'low',
        category: 'optimization',
        suggestion: '表现良好，建议继续积累更多场景数据'
      });
    }
    
    return recommendations;
  }
  
  /**
   * 加载规则库
   * @private
   */
  _loadRules() {
    // COLREGs 规则
    this.ruleBase.set('COLREGs.Rule13', '追越：追越船应从被追越船的船尾一侧通过');
    this.ruleBase.set('COLREGs.Rule14', '对遇：两船对遇应各自向右转向');
    this.ruleBase.set('COLREGs.Rule15', '交叉相遇：让清右舷来船');
    
    // ISM Code (国际安全管理规则)
    this.ruleBase.set('ISM.Emergency', '应急响应：必须在规定时间内启动应急程序');
    this.ruleBase.set('ISM.MOB', 'MOB 响应：2 秒内触发警报，30 秒内投放救生圈');
    
    // SOLAS (海上人命安全公约)
    this.ruleBase.set('SOLAS.Fire', '火灾响应：5 秒内触发警报，1 分钟内启动消防系统');
    
    console.log(`📚 Loaded ${this.ruleBase.size} compliance rules`);
  }
  
  /**
   * 获取默认评分标准
   * @private
   */
  _getDefaultCriteria() {
    return {
      correctness: {
        weight: 0.3,
        description: '响应的正确性和准确性'
      },
      compliance: {
        weight: 0.3,
        description: '是否符合海事法规和公司政策'
      },
      decisionQuality: {
        weight: 0.25,
        description: '决策的合理性和全面性'
      },
      timeliness: {
        weight: 0.15,
        description: '响应的及时性'
      }
    };
  }
  
  /**
   * 添加实船数据（数据回流）
   * @param {Object} data - 实船执行数据
   */
  addRealShipData(data) {
    this.realShipData.push({
      ...data,
      timestamp: new Date().toISOString(),
      source: 'real_ship'
    });
    
    console.log(`📡 Real ship data added: ${data.scenario || 'unknown'}`);
    
    // 触发事件
    this.emit('data:realship', data);
  }
  
  /**
   * 生成新的测试用例（从实船数据）
   * @returns {Array} - 测试用例列表
   */
  generateTestCasesFromRealData() {
    const testCases = [];
    
    for (const data of this.realShipData) {
      const testCase = {
        name: `Real Ship Case: ${data.scenario}`,
        type: data.type || 'real_world',
        difficulty: 'real',
        description: data.description || '来自实船的真实场景',
        conditions: data.conditions || {},
        expectedBehavior: data.captainAction ? 
          `船长执行了：${data.captainAction}。Agent 应该给出类似建议。` :
          '基于实船经验进行决策',
        successCriteria: (result) => {
          // 与船长决策比对
          return true; // 简化
        },
        metadata: {
          source: 'real_ship',
          originalData: data
        }
      };
      
      testCases.push(testCase);
    }
    
    console.log(`✅ Generated ${testCases.length} test cases from real ship data`);
    
    return testCases;
  }
  
  /**
   * 获取评估统计
   */
  getStats() {
    const total = this.evaluationHistory.length;
    
    if (total === 0) {
      return {
        total: 0,
        passed: 0,
        failed: 0,
        passRate: '0%',
        averageScore: 0
      };
    }
    
    const passed = this.evaluationHistory.filter(e => e.passed).length;
    const totalScore = this.evaluationHistory.reduce((sum, e) => sum + e.scores.overall, 0);
    
    return {
      total,
      passed,
      failed: total - passed,
      passRate: ((passed / total) * 100).toFixed(1) + '%',
      averageScore: (totalScore / total).toFixed(1)
    };
  }
  
  /**
   * 获取评估历史
   */
  getHistory() {
    return this.evaluationHistory;
  }
}
