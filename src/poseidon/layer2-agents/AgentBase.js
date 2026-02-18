/**
 * Agent Base - 智能体基类
 * 
 * Software 3.0 理念：所有智能体的通用能力框架
 * - 每个 Agent 都有自己的 Vibe（角色定义）
 * - 每个 Agent 都有记忆（Memory）
 * - 每个 Agent 都有工具使用能力（Tool Use）
 * - 每个 Agent 都可以与其他 Agent 协作
 */

import { EventEmitter } from '../../utils/EventEmitter.js';
import { LLMClient } from '../layer1-interface/LLMClient.js';

export class AgentBase extends EventEmitter {
  constructor(config = {}) {
    super();

    this.id = config.id || `agent-${Date.now()}`;
    this.name = config.name || 'Unnamed Agent';
    this.role = config.role || 'generic';

    // Vibe 定义（Agent 的"人格"和行为准则）
    this.vibe = config.vibe || '你是一个通用智能助手。';

    // 尝试从 localStorage 加载配置
    const savedConfig = this._loadConfig();

    // LLM 配置
    this.llmConfig = {
      provider: savedConfig?.llmProvider || config.llmProvider || 'minimax',
      apiKey: savedConfig?.apiKey || config.apiKey || '',
      apiEndpoint: savedConfig?.apiEndpoint || config.apiEndpoint || 'https://api.minimax.chat/v1',
      model: savedConfig?.model || config.model || 'MiniMax-M2.5',
      temperature: config.temperature || 0.7,
      maxTokens: config.maxTokens || 4096
    };

    // 创建 LLM Client
    this.llmClient = new LLMClient(this.llmConfig);

    // 记忆系统（短期 + 长期）
    this.memory = {
      shortTerm: [], // 最近的对话和操作（会话级）
      longTerm: new Map(), // 知识库（持久化）
      working: {} // 工作记忆（当前任务的临时状态）
    };

    // 工具箱（Tool Use）
    this.tools = new Map();

    // 执行状态
    this.status = 'idle'; // 'idle' | 'thinking' | 'executing' | 'error'
    this.currentTask = null;

    // 性能指标
    this.metrics = {
      tasksExecuted: 0,
      successRate: 0,
      averageResponseTime: 0,
      totalResponseTime: 0
    };

    // 部署位置
    this.deploymentLocation = config.deploymentLocation || 'edge'; // 'edge' | 'cloud'

    console.log(`🤖 Agent initialized: ${this.name} (${this.role})`);
  }

  /**
   * 注册工具
   * @param {string} toolName - 工具名称
   * @param {Function} toolFunction - 工具函数
   * @param {string} description - 工具描述
   */
  registerTool(toolName, toolFunction, description = '') {
    this.tools.set(toolName, {
      name: toolName,
      function: toolFunction,
      description: description,
      usageCount: 0
    });

    console.log(`🔧 Tool registered for ${this.name}: ${toolName}`);
  }

  /**
   * 使用工具
   * @param {string} toolName - 工具名称
   * @param {*} params - 工具参数
   */
  async useTool(toolName, params = {}) {
    const tool = this.tools.get(toolName);

    if (!tool) {
      throw new Error(`Tool "${toolName}" not found in ${this.name}'s toolbox`);
    }

    console.log(`🔧 ${this.name} using tool: ${toolName}`, params);

    try {
      const result = await tool.function(params);
      tool.usageCount++;

      // 记录到短期记忆
      this.memory.shortTerm.push({
        type: 'tool_use',
        tool: toolName,
        params,
        result,
        timestamp: new Date().toISOString()
      });

      return result;
    } catch (error) {
      console.error(`❌ Tool "${toolName}" execution failed:`, error);
      throw error;
    }
  }

  /**
   * 执行任务（核心方法，子类必须实现）
   * @param {string} task - 任务描述
   * @param {Object} context - 船舶上下文
   */
  async execute(task, context = {}) {
    throw new Error('execute() must be implemented by subclass');
  }

  /**
   * 思考（调用 LLM 进行推理）
   * @param {string} query - 查询
   * @param {Object} context - 上下文
   */
  async think(query, context = {}) {
    this.status = 'thinking';

    const startTime = Date.now();

    try {
      // 构建 prompt
      const prompt = this._buildPrompt(query, context);

      // 调用 LLM（这里先模拟）
      const response = await this._callLLM(prompt);

      // 记录到短期记忆
      this.memory.shortTerm.push({
        type: 'thought',
        query,
        response,
        timestamp: new Date().toISOString()
      });

      // 更新性能指标
      const responseTime = Date.now() - startTime;
      this.metrics.totalResponseTime += responseTime;
      this.metrics.averageResponseTime = this.metrics.totalResponseTime / (this.metrics.tasksExecuted + 1);

      this.status = 'idle';

      return response;

    } catch (error) {
      this.status = 'error';
      console.error(`❌ ${this.name} thinking error:`, error);
      throw error;
    }
  }

  /**
   * 构建 Prompt
   * @private
   */
  _buildPrompt(query, context) {
    const parts = [];

    // 1. Agent Vibe（角色定义）
    parts.push(`# 角色定义\n${this.vibe}\n`);

    // 2. 当前上下文
    parts.push(`# 当前状态\n${JSON.stringify(context, null, 2)}\n`);

    // 3. 短期记忆（最近的对话）
    if (this.memory.shortTerm.length > 0) {
      const recentMemory = this.memory.shortTerm.slice(-5);
      parts.push(`# 最近记忆\n${JSON.stringify(recentMemory, null, 2)}\n`);
    }

    // 4. 可用工具
    if (this.tools.size > 0) {
      const toolsList = Array.from(this.tools.entries())
        .map(([name, tool]) => `- ${name}: ${tool.description}`)
        .join('\n');
      parts.push(`# 可用工具\n${toolsList}\n`);
    }

    // 5. 用户查询
    parts.push(`# 任务\n${query}\n`);

    return parts.join('\n');
  }

  /**
   * 调用 LLM（真实 API）
   * @private
   */
  async _callLLM(prompt) {
    try {
      // 构建消息数组
      const messages = [
        {
          role: 'system',
          content: this.vibe
        },
        {
          role: 'user',
          content: prompt
        }
      ];

      // 调用真实的 LLM
      const response = await this.llmClient.chat(messages);

      return {
        content: response.content,
        metadata: {
          model: response.model,
          provider: this.llmConfig.provider,
          usage: response.usage
        }
      };

    } catch (error) {
      console.error(`❌ ${this.name} LLM 调用失败:`, error);

      // 返回友好的错误提示
      return {
        content: `抱歉，LLM 服务暂时不可用。错误：${error.message}\n\n提示：请访问 /poseidon-config.html 配置 API Key。`,
        metadata: {
          error: error.message
        }
      };
    }
  }

  /**
   * 从 localStorage 加载配置
   * @private
   */
  _loadConfig() {
    if (typeof localStorage === 'undefined') return {};
    const saved = localStorage.getItem('poseidon_config');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (error) {
        return {};
      }
    }
    return {};
  }

  /**
   * 学习（将新知识添加到长期记忆）
   * @param {string} key - 知识键
   * @param {*} value - 知识值
   */
  learn(key, value) {
    this.memory.longTerm.set(key, {
      value,
      timestamp: new Date().toISOString(),
      accessCount: 0
    });

    console.log(`🧠 ${this.name} learned: ${key}`);
  }

  /**
   * 回忆（从长期记忆中检索）
   * @param {string} key - 知识键
   */
  recall(key) {
    const knowledge = this.memory.longTerm.get(key);

    if (knowledge) {
      knowledge.accessCount++;
      return knowledge.value;
    }

    return null;
  }

  /**
   * 清空短期记忆
   */
  clearShortTermMemory() {
    this.memory.shortTerm = [];
    console.log(`🧹 ${this.name} short-term memory cleared`);
  }

  /**
   * 获取性能报告
   */
  getPerformanceReport() {
    return {
      agent: this.name,
      role: this.role,
      status: this.status,
      metrics: this.metrics,
      memory: {
        shortTerm: this.memory.shortTerm.length,
        longTerm: this.memory.longTerm.size
      },
      tools: Array.from(this.tools.entries()).map(([name, tool]) => ({
        name,
        usageCount: tool.usageCount
      }))
    };
  }

  /**
   * 销毁
   */
  dispose() {
    this.tools.clear();
    this.memory.shortTerm = [];
    this.memory.longTerm.clear();
    this.removeAllListeners();

    console.log(`🗑️ Agent disposed: ${this.name}`);
  }
}
