/**
 * Poseidon Bridge - AI 对话模块
 * 
 * 连接到 marine_engineer_agent 的 Poseidon API
 * 用户无需配置大模型，所有 AI 逻辑在后端处理
 * 
 * @version 2.0.0
 * @since 2026-03-10
 */

class PoseidonBridge {
  constructor(apiBaseUrl = 'http://127.0.0.1:8080') {
    this.apiBaseUrl = apiBaseUrl;
    this.serviceStatus = 'unknown';
    this.messageHistory = [];
  }

  // ===== 服务状态 =====

  // 检查服务健康状态
  async checkHealth() {
    try {
      const response = await fetch(`${this.apiBaseUrl}/health`);
      const health = await response.json();
      this.serviceStatus = health.status === 'healthy' ? 'online' : 'offline';
      return health;
    } catch (e) {
      this.serviceStatus = 'offline';
      throw e;
    }
  }

  // 获取可用技能
  async getSkills() {
    const response = await fetch(`${this.apiBaseUrl}/api/v1/skills`);
    return await response.json();
  }

  // ===== AI 对话 =====

  // 发送消息到 Agent（后端处理 AI 逻辑）
  async chat(message, context = {}) {
    console.log('🤖 Bridge 发送消息:', message);
    
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/v1/twins/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: message,
          context: {
            ...context,
            timestamp: new Date().toISOString(),
            history: this.messageHistory.slice(-5) // 最近 5 条消息
          }
        })
      });

      const result = await response.json();
      
      // 保存消息历史
      this.messageHistory.push({
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      });
      
      if (result.success) {
        this.messageHistory.push({
          role: 'assistant',
          content: result.decision?.recommendation || result.message,
          timestamp: new Date().toISOString()
        });
      }

      console.log('🤖 Bridge 收到响应:', result);
      return result;

    } catch (e) {
      console.error('❌ Bridge 对话失败:', e);
      return {
        success: false,
        message: `服务不可用：${e.message}`,
        error: e.message
      };
    }
  }

  // ===== 场景控制（通过自然语言） =====

  // 智能场景控制（解析自然语言）
  async controlScene(message) {
    console.log('🌊 Bridge 场景控制:', message);

    // 简单意图识别（本地快速响应）
    const msgLower = message.toLowerCase();
    
    // 场景预设
    if (msgLower.includes('平静') || msgLower.includes('calm')) {
      return await this.applyPreset('calm');
    }
    if (msgLower.includes('风暴') || msgLower.includes('storm') || msgLower.includes('暴风雨')) {
      return await this.applyPreset('stormy');
    }
    if (msgLower.includes('日落') || msgLower.includes('sunset')) {
      return await this.applyPreset('sunset');
    }
    if (msgLower.includes('夜晚') || msgLower.includes('night')) {
      return await this.applyPreset('night');
    }

    // 波浪控制
    if (msgLower.includes('波浪') && (msgLower.includes('大') || msgLower.includes('高'))) {
      return await this.adjustWeather({ waveHeight: 3.0 });
    }
    if (msgLower.includes('波浪') && (msgLower.includes('小') || msgLower.includes('低'))) {
      return await this.adjustWeather({ waveHeight: 0.5 });
    }

    // 其他请求交给 Agent 处理
    return await this.chat(message);
  }

  // 应用场景预设
  async applyPreset(preset) {
    const response = await fetch(`${this.apiBaseUrl}/api/v1/twins/scene/control`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'apply_preset',
        params: { preset }
      })
    });
    const result = await response.json();
    
    if (result.success) {
      // 触发自定义事件通知 3D 场景更新
      window.dispatchEvent(new CustomEvent('poseidon:sceneUpdate', { detail: result.data }));
    }
    
    return result;
  }

  // 调整天气
  async adjustWeather(params) {
    const response = await fetch(`${this.apiBaseUrl}/api/v1/twins/scene/control`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'adjust_weather',
        params
      })
    });
    const result = await response.json();
    
    if (result.success) {
      window.dispatchEvent(new CustomEvent('poseidon:sceneUpdate', { detail: { weather: params } }));
    }
    
    return result;
  }

  // ===== 故障诊断 =====

  // 故障诊断
  async diagnose(symptom, sensorData = {}) {
    const response = await fetch(`${this.apiBaseUrl}/api/v1/twins/diagnosis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symptom,
        sensor_data: sensorData
      })
    });
    return await response.json();
  }

  // ===== 决策支持 =====

  // 获取决策建议
  async getDecision(query, context = {}) {
    const response = await fetch(`${this.apiBaseUrl}/api/v1/twins/decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, context })
    });
    return await response.json();
  }

  // ===== 水动力分析 =====

  // 水动力分析
  async hydroAnalysis(params) {
    const response = await fetch(`${this.apiBaseUrl}/api/v1/hydro/analysis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    return await response.json();
  }

  // ===== 稳性分析 =====

  // 稳性与摇摆分析
  async stabilityAnalysis(params) {
    const response = await fetch(`${this.apiBaseUrl}/api/v1/stability/analysis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    return await response.json();
  }

  // ===== 辅助方法 =====

  // 清空消息历史
  clearHistory() {
    this.messageHistory = [];
    console.log('🧹 消息历史已清空');
  }

  // 获取消息历史
  getHistory(limit = 10) {
    return this.messageHistory.slice(-limit);
  }
}

// 创建全局实例
window.poseidonBridge = new PoseidonBridge();

// 自动检查服务状态
(async function init() {
  try {
    await window.poseidonBridge.checkHealth();
    console.log('✅ Poseidon Bridge 已连接');
  } catch (e) {
    console.warn('⚠️ Poseidon Bridge 未连接，部分功能可能不可用');
  }
  
  console.log('🌉 Poseidon Bridge v2.0 已初始化');
  console.log('使用 window.poseidonBridge 与 Agent 交互');
  console.log('API 端点:', window.poseidonBridge.apiBaseUrl);
})();
