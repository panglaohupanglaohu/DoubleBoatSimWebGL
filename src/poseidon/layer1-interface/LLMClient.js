/**
 * LLM Client - 真实的 LLM API 调用客户端
 * 
 * 支持多个提供商：
 * - MiniMax (推荐 - 2.5 模型)
 * - DeepSeek
 * - OpenAI (GPT-4)
 * - Anthropic (Claude)
 * - 本地模型 (Ollama)
 */

export class LLMClient {
  constructor(config = {}) {
    // 每次调用时动态从 localStorage 加载配置，支持热插拔
    this.config = {
      provider: 'minimax',  // 默认值，会被 loadConfig() 覆盖
      apiKey: '',
      apiEndpoint: '',
      model: '',
      temperature: 0.7,
      maxTokens: 4096,
      ...config
    };

    console.log('🧠 LLM Client initialized (configurable):', {
      provider: this.config.provider,
      model: this.config.model
    });
  }

  /**
   * 动态加载配置（从 localStorage，支持热插拔）
   * @private
   */
  _loadConfig() {
    if (typeof localStorage === 'undefined') return null;
    try {
      const saved = localStorage.getItem('poseidon_config');
      if (saved) {
        const config = JSON.parse(saved);
        // 更新配置
        this.config.provider = config.llmProvider || this.config.provider;
        this.config.apiKey = config.apiKey || this.config.apiKey;
        this.config.apiEndpoint = config.apiEndpoint || this._getDefaultEndpoint(this.config.provider);
        this.config.model = config.model || this._getDefaultModel(this.config.provider);
        this.config.temperature = config.temperature || this.config.temperature;
        
        console.log('🔌 LLM Config loaded (hot-swap):', {
          provider: this.config.provider,
          model: this.config.model,
          hasApiKey: !!this.config.apiKey
        });
        return config;
      }
    } catch (error) {
      console.warn('⚠️ 加载配置失败:', error);
    }
    return null;
  }

  /**
   * 获取默认 API 端点
   * @private
   */
  _getDefaultEndpoint(provider) {
    const endpoints = {
      'minimax': 'https://api.minimax.chat/v1',
      'deepseek': 'https://api.deepseek.com/v1',
      'openai': 'https://api.openai.com/v1',
      'anthropic': 'https://api.anthropic.com/v1',
      'local': 'http://localhost:11434/v1'
    };

    return endpoints[provider] || endpoints.minimax;
  }

  /**
   * 获取默认模型
   * @private
   */
  _getDefaultModel(provider) {
    const models = {
      'minimax': 'MiniMax-M2.5',
      'deepseek': 'deepseek-chat',
      'openai': 'gpt-4',
      'anthropic': 'claude-3-opus-20240229',
      'local': 'llama2'
    };

    return models[provider] || models.minimax;
  }

  /**
   * 调用 LLM（OpenAI 兼容格式）
   * @param {Array} messages - 消息数组
   * @param {Object} options - 额外选项
   * @returns {Promise<Object>} - LLM 响应
   */
  async chat(messages, options = {}) {
    // 每次调用前动态加载配置，支持热插拔
    this._loadConfig();

    if (!this.config.apiKey && this.config.provider !== 'local') {
      const errorMsg = `API Key 未配置 (provider: ${this.config.provider})。请访问 poseidon-config.html 配置。`;
      console.error('❌', errorMsg);
      throw new Error(errorMsg);
    }

    console.log('🧠 LLM Chat request:', {
      provider: this.config.provider,
      model: this.config.model,
      endpoint: this.config.apiEndpoint,
      hasApiKey: !!this.config.apiKey,
      apiKeyLength: this.config.apiKey?.length || 0
    });

    // 按厂商规范化 model，避免 "Model Not Exist"
    let model = options.model || this.config.model;
    const endpoint = (this.config.apiEndpoint || '').toLowerCase();
    
    // MiniMax API 处理
    if (this.config.provider === 'minimax' || endpoint.includes('minimax.chat')) {
      return this._callMiniMax(messages, options);
    }
    
    // DeepSeek API 处理
    const isDeepSeekEndpoint = endpoint.includes('deepseek.com');
    if (this.config.provider === 'deepseek' || isDeepSeekEndpoint) {
      const deepseekModels = ['deepseek-chat', 'deepseek-reasoner', 'deepseek-coder'];
      if (!model || !deepseekModels.includes(model)) {
        model = 'deepseek-chat';
        console.warn('🧠 DeepSeek 使用有效模型名: deepseek-chat（原 model 不适用于当前 API）');
      }
    }

    const requestBody = {
      model: model,
      messages: messages,
      temperature: options.temperature || this.config.temperature,
      max_tokens: options.maxTokens || this.config.maxTokens
    };

    // Anthropic API 格式不同
    if (this.config.provider === 'anthropic') {
      return this._callAnthropic(messages, options);
    }

    // OpenAI 兼容格式（DeepSeek, OpenAI, Local）
    try {
      const response = await fetch(this.config.apiEndpoint + '/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API 调用失败 (${response.status}): ${errorText}`);
      }

      const data = await response.json();

      return {
        content: data.choices?.[0]?.message?.content || '',
        role: 'assistant',
        model: data.model,
        usage: data.usage,
        finish_reason: data.choices?.[0]?.finish_reason
      };

    } catch (error) {
      console.error('❌ LLM API 调用失败:', error);
      throw error;
    }
  }

  /**
   * 调用 MiniMax API
   * @private
   */
  async _callMiniMax(messages, options = {}) {
    const model = options.model || this.config.model;
    
    const requestBody = {
      model: model,
      messages: messages,
      temperature: options.temperature || this.config.temperature,
      max_tokens: options.maxTokens || this.config.maxTokens
    };

    try {
      // MiniMax 使用 text/chatcompletion_v2 端点
      const response = await fetch(this.config.apiEndpoint + '/text/chatcompletion_v2', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`MiniMax API 调用失败 (${response.status}): ${errorText}`);
      }

      const data = await response.json();

      return {
        content: data.choices?.[0]?.message?.content || '',
        role: data.choices?.[0]?.message?.role || 'assistant',
        model: data.model,
        usage: data.usage,
        finish_reason: data.choices?.[0]?.finish_reason
      };

    } catch (error) {
      console.error('❌ MiniMax API 调用失败:', error);
      throw error;
    }
  }

  /**
   * 调用 Anthropic API
   * @private
   */
  async _callAnthropic(messages, options = {}) {
    // Anthropic API 使用不同的格式
    const requestBody = {
      model: options.model || this.config.model,
      messages: messages,
      temperature: options.temperature || this.config.temperature,
      max_tokens: options.maxTokens || this.config.maxTokens
    };

    try {
      const response = await fetch(this.config.apiEndpoint + '/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': this.config.apiKey,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Anthropic API 调用失败 (${response.status}): ${errorText}`);
      }

      const data = await response.json();

      return {
        content: data.content?.[0]?.text || '',
        role: 'assistant',
        model: data.model,
        usage: data.usage,
        stop_reason: data.stop_reason
      };

    } catch (error) {
      console.error('❌ Anthropic API 调用失败:', error);
      throw error;
    }
  }

  /**
   * 测试连接
   */
  async testConnection() {
    const messages = [
      { role: 'user', content: '你好，请回复"测试成功"' }
    ];

    try {
      const response = await this.chat(messages, { maxTokens: 50 });
      console.log('✅ LLM 连接测试成功:', response.content);
      return { success: true, response: response.content };
    } catch (error) {
      console.error('❌ LLM 连接测试失败:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * 从 localStorage 加载配置
   */
  static loadFromStorage() {
    if (typeof localStorage === 'undefined') return null;
    const saved = localStorage.getItem('poseidon_config');

    if (saved) {
      try {
        const config = JSON.parse(saved);
        return new LLMClient({
          provider: config.llmProvider,
          apiKey: config.apiKey,
          apiEndpoint: config.apiEndpoint,
          model: config.model,
          temperature: config.temperature,
          maxTokens: config.maxContextTokens
        });
      } catch (error) {
        console.error('加载配置失败:', error);
      }
    }

    return null;
  }
}
