/**
 * Base Agent - 智能体基类
 * 
 * Software 3.0 理念：我们不写固定功能，我们培育智能体
 * 
 * 每个智能体都具有：
 * - 角色（Role）：定义职责范围
 * - Vibe：行为风格和决策偏好
 * - 工具（Tools）：可以调用的函数/API
 * - 记忆（Memory）：短期和长期记忆
 * - 感知（Perception）：可以访问的传感器和数据源
 */

import { EventEmitter } from '../../utils/EventEmitter.js';

export class BaseAgent extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      name: config.name || 'UnnamedAgent',
      role: config.role || 'general',
      vibe: config.vibe || '一个通用的智能助手',
      llmProvider: config.llmProvider || 'openai',
      model: config.model || 'gpt-4',
      temperature: config.temperature || 0.7,
      maxTokens: config.maxTokens || 4096,
      tools: config.tools || [], // 可用工具列表
      ...config
    };
    
    // 记忆系统
    this.memory = {
      shortTerm: [], // 短期记忆（当前会话）
      longTerm: [], // 长期记忆（持久化）
      working: [] // 工作记忆（正在处理的任务）
    };
    
    // 工具注册表
    this.tools = new Map();
    this._registerDefaultTools();
    
    // 状态
    this.status = 'idle'; // 'idle' | 'thinking' | 'executing' | 'error'
    this.currentTask = null;
    
    console.log(`🤖 Agent "${this.config.name}" initialized (Role: ${this.config.role})`);
  }
  
  /**
   * 注册默认工具
   * @private
   */
  _registerDefaultTools() {
    // 每个 Agent 都有的基础工具
    
    // 工具 1: 查询传感器
    this.registerTool('query_sensor', {
      description: '查询指定传感器的当前值',
      parameters: {
        sensorId: 'string'
      },
      execute: async (params) => {
        return {
          sensorId: params.sensorId,
          value: Math.random() * 100, // 模拟数据
          timestamp: new Date().toISOString()
        };
      }
    });
    
    // 工具 2: 记录日志
    this.registerTool('log_event', {
      description: '记录事件到日志',
      parameters: {
        event: 'string',
        level: 'string' // 'info' | 'warning' | 'error'
      },
      execute: async (params) => {
        console.log(`📝 [${this.config.name}] ${params.level.toUpperCase()}: ${params.event}`);
        return { success: true };
      }
    });
  }
  
  /**
   * 注册工具
   * @param {string} name - 工具名称
   * @param {Object} tool - 工具定义
   */
  registerTool(name, tool) {
    this.tools.set(name, tool);
    console.log(`🔧 Tool registered: ${name} (for ${this.config.name})`);
  }
  
  /**
   * 执行任务
   * @param {string} task - 任务描述
   * @param {Object} context - 上下文信息（船舶状态等）
   * @returns {Promise<Object>} - 执行结果
   */
  async execute(task, context = {}) {
    console.log(`🤖 [${this.config.name}] Executing task: ${task}`);
    
    this.status = 'thinking';
    this.currentTask = task;
    
    // 添加到工作记忆
    this.memory.working.push({
      task,
      context,
      startTime: Date.now()
    });
    
    try {
      // 1. 感知（Perception）：收集相关传感器数据
      const perception = await this._perceive(context);
      
      // 2. 思考（Reasoning）：调用 LLM 推理
      const reasoning = await this._reason(task, perception, context);
      
      // 3. 执行（Action）：调用工具完成任务
      const action = await this._act(reasoning);
      
      // 4. 记录到记忆
      this._memorize({
        task,
        perception,
        reasoning,
        action,
        timestamp: new Date().toISOString()
      });
      
      this.status = 'idle';
      this.currentTask = null;
      
      // 触发事件
      this.emit('task:completed', { task, result: action });
      
      return {
        success: true,
        result: action,
        agent: this.config.name
      };
      
    } catch (error) {
      this.status = 'error';
      console.error(`❌ [${this.config.name}] Task execution failed:`, error);
      
      this.emit('task:failed', { task, error });
      
      return {
        success: false,
        error: error.message,
        agent: this.config.name
      };
    }
  }
  
  /**
   * 感知阶段：收集相关数据
   * @private
   */
  async _perceive(context) {
    // 子类可以重写这个方法，定义自己需要的传感器
    return {
      context,
      timestamp: Date.now()
    };
  }
  
  /**
   * 推理阶段：调用 LLM 分析
   * @private
   */
  async _reason(task, perception, context) {
    // 构建 prompt
    const prompt = this._buildPrompt(task, perception, context);
    
    // 在实际实现中，这里应该调用真实的 LLM API
    // 现在我们模拟响应
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return {
      thought: `分析任务: ${task}`,
      plan: ['步骤1: 收集数据', '步骤2: 分析数据', '步骤3: 生成建议'],
      toolCalls: [] // LLM 决定需要调用哪些工具
    };
  }
  
  /**
   * 执行阶段：调用工具
   * @private
   */
  async _act(reasoning) {
    const results = [];
    
    // 执行 LLM 建议的工具调用
    for (const toolCall of reasoning.toolCalls) {
      const tool = this.tools.get(toolCall.name);
      
      if (tool) {
        const result = await tool.execute(toolCall.parameters);
        results.push({ tool: toolCall.name, result });
      } else {
        console.warn(`⚠️ Tool not found: ${toolCall.name}`);
      }
    }
    
    return {
      thought: reasoning.thought,
      plan: reasoning.plan,
      results
    };
  }
  
  /**
   * 构建 LLM Prompt
   * @private
   */
  _buildPrompt(task, perception, context) {
    return `
你是 ${this.config.name}。
角色：${this.config.role}
行为风格：${this.config.vibe}

当前任务：${task}

感知数据：
${JSON.stringify(perception, null, 2)}

船舶上下文：
${JSON.stringify(context, null, 2)}

可用工具：
${Array.from(this.tools.keys()).map(name => {
  const tool = this.tools.get(name);
  return `- ${name}: ${tool.description}`;
}).join('\n')}

请分析任务并决定需要调用哪些工具。
    `.trim();
  }
  
  /**
   * 记忆
   * @private
   */
  _memorize(experience) {
    // 添加到短期记忆
    this.memory.shortTerm.push(experience);
    
    // 如果短期记忆超过 50 条，转移到长期记忆
    if (this.memory.shortTerm.length > 50) {
      const toArchive = this.memory.shortTerm.splice(0, 25);
      this.memory.longTerm.push(...toArchive);
    }
    
    // 清空工作记忆
    this.memory.working = [];
  }
  
  /**
   * 获取状态
   */
  getStatus() {
    return {
      name: this.config.name,
      role: this.config.role,
      status: this.status,
      currentTask: this.currentTask,
      memory: {
        shortTerm: this.memory.shortTerm.length,
        longTerm: this.memory.longTerm.length,
        working: this.memory.working.length
      },
      tools: Array.from(this.tools.keys())
    };
  }
  
  /**
   * 销毁
   */
  dispose() {
    this.memory.shortTerm = [];
    this.memory.longTerm = [];
    this.memory.working = [];
    this.tools.clear();
    this.removeAllListeners();
    
    console.log(`🗑️ Agent "${this.config.name}" disposed`);
  }
}
