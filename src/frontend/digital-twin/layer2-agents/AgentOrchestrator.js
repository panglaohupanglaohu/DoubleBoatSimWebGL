/**
 * Agent Orchestrator - 智能体编排系统
 * 
 * Software 3.0 理念：LangGraph 编排
 * - 协调多个智能体协作
 * - 管理智能体间的通信和数据流
 * - 智能路由任务到最合适的 Agent
 * - 处理复杂的多步骤工作流
 * 
 * 架构模式：类似 LangGraph 的状态图
 * - Nodes: 各个 Agent
 * - Edges: Agent 之间的协作关系
 * - State: 共享的船舶状态
 */

import { EventEmitter } from '../../utils/EventEmitter.js';

export class AgentOrchestrator extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      maxParallelAgents: config.maxParallelAgents || 4, // 最多同时运行的 Agent 数
      timeout: config.timeout || 30000, // 单个 Agent 超时时间
      retryAttempts: config.retryAttempts || 2,
      ...config
    };
    
    // 注册的智能体
    this.agents = new Map();
    
    // 工作流定义（类似 LangGraph 的图结构）
    this.workflows = new Map();
    
    // 执行队列
    this.taskQueue = [];
    this.runningTasks = new Map();
    
    // 统计
    this.stats = {
      totalTasks: 0,
      completedTasks: 0,
      failedTasks: 0,
      averageExecutionTime: 0
    };
    
    console.log('🎭 Agent Orchestrator initialized');
  }
  
  /**
   * 注册智能体
   * @param {string} name - Agent 名称
   * @param {Object} agent - Agent 实例
   */
  registerAgent(name, agent) {
    this.agents.set(name, agent);
    
    // 监听 Agent 事件
    agent.on('task:completed', (data) => {
      this.emit('agent:task_completed', { agentName: name, ...data });
    });
    
    agent.on('task:failed', (data) => {
      this.emit('agent:task_failed', { agentName: name, ...data });
    });
    
    console.log(`✅ Agent registered in orchestrator: ${name}`);
  }
  
  /**
   * 定义工作流
   * @param {string} workflowName - 工作流名称
   * @param {Object} workflow - 工作流定义
   */
  defineWorkflow(workflowName, workflow) {
    this.workflows.set(workflowName, workflow);
    console.log(`📋 Workflow defined: ${workflowName}`);
  }
  
  /**
   * 执行任务（自动路由到合适的 Agent）
   * @param {string} task - 任务描述
   * @param {Object} context - 上下文
   */
  async executeTask(task, context = {}) {
    this.stats.totalTasks++;
    
    const taskId = `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    console.log(`🎯 Orchestrator executing task [${taskId}]: ${task}`);
    
    const startTime = Date.now();
    
    try {
      // 1. 智能路由：选择最合适的 Agent
      const selectedAgent = this._routeTask(task);
      
      if (!selectedAgent) {
        throw new Error('No suitable agent found for this task');
      }
      
      console.log(`🤖 Routed to: ${selectedAgent.name}`);
      
      // 2. 执行任务
      this.runningTasks.set(taskId, {
        agent: selectedAgent,
        task,
        startTime
      });
      
      const result = await selectedAgent.execute(task, context);
      
      // 3. 记录完成
      this.runningTasks.delete(taskId);
      this.stats.completedTasks++;
      
      const executionTime = Date.now() - startTime;
      this.stats.averageExecutionTime = 
        (this.stats.averageExecutionTime * (this.stats.completedTasks - 1) + executionTime) / 
        this.stats.completedTasks;
      
      this.emit('task:completed', {
        taskId,
        task,
        agent: selectedAgent.name,
        result,
        executionTime
      });
      
      return {
        success: true,
        taskId,
        agent: selectedAgent.name,
        result,
        executionTime
      };
      
    } catch (error) {
      this.stats.failedTasks++;
      this.runningTasks.delete(taskId);
      
      console.error(`❌ Task execution failed [${taskId}]:`, error);
      
      this.emit('task:failed', {
        taskId,
        task,
        error: error.message
      });
      
      return {
        success: false,
        taskId,
        error: error.message
      };
    }
  }
  
  /**
   * 路由任务到合适的 Agent
   * @private
   */
  _routeTask(task) {
    // 简单的关键词匹配（实际应该用 LLM 做语义理解）
    const routingRules = [
      {
        keywords: ['航行', '避碰', '航向', '碰撞', 'CPA', 'TCPA', '航线', '路径'],
        agent: 'navigator'
      },
      {
        keywords: ['主机', '设备', '排温', '能效', '燃油', '维护', '保养', '故障'],
        agent: 'engineer'
      },
      {
        keywords: ['库存', '伙食', '菜单', '舱室', '环境', '温度', '湿度'],
        agent: 'steward'
      },
      {
        keywords: ['安全', '监控', '警报', '落水', 'MOB', '火灾', '烟雾', '演习'],
        agent: 'safety'
      }
    ];
    
    const taskLower = task.toLowerCase();
    
    for (const rule of routingRules) {
      if (rule.keywords.some(kw => taskLower.includes(kw))) {
        const agent = this.agents.get(rule.agent);
        if (agent) {
          return agent;
        }
      }
    }
    
    // 如果没有匹配，默认使用第一个可用的 Agent
    const firstAgent = Array.from(this.agents.values())[0];
    console.warn(`⚠️ No specific agent matched, using default: ${firstAgent?.name || 'None'}`);
    
    return firstAgent;
  }
  
  /**
   * 执行工作流
   * @param {string} workflowName - 工作流名称
   * @param {Object} input - 输入数据
   */
  async executeWorkflow(workflowName, input = {}) {
    const workflow = this.workflows.get(workflowName);
    
    if (!workflow) {
      throw new Error(`Workflow "${workflowName}" not found`);
    }
    
    console.log(`🔄 Executing workflow: ${workflowName}`);
    
    let state = { ...input };
    
    try {
      // 按照工作流定义的步骤顺序执行
      for (const step of workflow.steps) {
        const agent = this.agents.get(step.agent);
        
        if (!agent) {
          console.warn(`⚠️ Agent "${step.agent}" not found, skipping step`);
          continue;
        }
        
        console.log(`  Step: ${step.name} (Agent: ${step.agent})`);
        
        // 执行步骤
        const result = await agent.execute(step.task, state);
        
        // 更新状态
        state = {
          ...state,
          [step.outputKey || step.agent]: result
        };
        
        // 如果有条件跳转
        if (step.condition && !step.condition(state)) {
          console.log(`  ⏭️ Condition not met, skipping to next`);
          continue;
        }
      }
      
      console.log(`✅ Workflow completed: ${workflowName}`);
      
      return {
        success: true,
        workflow: workflowName,
        state
      };
      
    } catch (error) {
      console.error(`❌ Workflow execution failed: ${workflowName}`, error);
      
      return {
        success: false,
        workflow: workflowName,
        error: error.message,
        state
      };
    }
  }
  
  /**
   * 并行执行多个任务
   * @param {Array<string>} tasks - 任务数组
   * @param {Object} context - 共享上下文
   */
  async executeParallel(tasks, context = {}) {
    console.log(`⚡ Executing ${tasks.length} tasks in parallel`);
    
    const promises = tasks.map(task => this.executeTask(task, context));
    
    const results = await Promise.allSettled(promises);
    
    const successful = results.filter(r => r.status === 'fulfilled' && r.value.success);
    const failed = results.filter(r => r.status === 'rejected' || !r.value?.success);
    
    console.log(`✅ Parallel execution: ${successful.length} succeeded, ${failed.length} failed`);
    
    return {
      total: tasks.length,
      successful: successful.length,
      failed: failed.length,
      results: results.map(r => r.status === 'fulfilled' ? r.value : { success: false, error: r.reason })
    };
  }
  
  /**
   * 获取所有 Agent 的状态
   */
  getAgentStatuses() {
    const statuses = [];
    
    for (const [name, agent] of this.agents.entries()) {
      if (agent.getPerformanceReport) {
        statuses.push(agent.getPerformanceReport());
      } else if (agent.getStatus) {
        statuses.push(agent.getStatus());
      }
    }
    
    return statuses;
  }
  
  /**
   * 获取编排器统计
   */
  getStats() {
    return {
      ...this.stats,
      registeredAgents: this.agents.size,
      runningTasks: this.runningTasks.size,
      queuedTasks: this.taskQueue.length,
      successRate: this.stats.totalTasks > 0 ? 
        (this.stats.completedTasks / this.stats.totalTasks * 100).toFixed(1) + '%' : '0%'
    };
  }
  
  /**
   * 销毁
   */
  dispose() {
    // 停止所有运行中的任务
    this.runningTasks.clear();
    this.taskQueue = [];
    
    // 销毁所有 Agent
    for (const agent of this.agents.values()) {
      if (agent.dispose) {
        agent.dispose();
      }
    }
    
    this.agents.clear();
    this.workflows.clear();
    this.removeAllListeners();
    
    console.log('🗑️ Agent Orchestrator disposed');
  }
}
