/**
 * 前端 AI 控制面板 - 集成 marine_engineer_agent 智能体
 * 
 * 连接到 Poseidon 服务，使用智能体技能进行数字孪生控制
 * 
 * @version 2.0.0
 * @since 2026-03-10
 */

class AITwinsController {
  constructor(apiBaseUrl = 'http://127.0.0.1:8080') {
    this.apiBaseUrl = apiBaseUrl;
    this.currentScene = null;
    this.serviceStatus = 'unknown';
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

  // 获取可用技能列表
  async getSkills() {
    const response = await fetch(`${this.apiBaseUrl}/api/v1/skills`);
    return await response.json();
  }

  // ===== 场景控制 =====

  // 获取场景状态
  async getSceneStatus() {
    // 从本地存储或模拟器获取当前场景状态
    const scene = localStorage.getItem('twins_scene');
    if (scene) {
      this.currentScene = JSON.parse(scene);
      return this.currentScene;
    }
    
    // 默认场景
    this.currentScene = {
      ocean: {
        waveHeight: 0.5,
        waveSpeed: 0.3,
        waterColor: '#1E90FF'
      },
      physics: {
        gravity: -9.8,
        waterDensity: 1025,
        linearDamping: 0.1
      },
      boats: {
        boat1: { position: { x: 0, y: 0, z: 0 } },
        boat2: { position: { x: 10, y: 0, z: 0 } }
      }
    };
    return this.currentScene;
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
      // 保存到本地存储
      localStorage.setItem('twins_scene', JSON.stringify(result.data));
      this.currentScene = result.data;
      
      // 通知主场景更新（通过 postMessage）
      this.notifySceneUpdate(result.data);
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
      this.notifySceneUpdate({ weather: params });
    }
    
    return result;
  }

  // 调整物理参数
  async adjustPhysics(params) {
    const response = await fetch(`${this.apiBaseUrl}/api/v1/twins/scene/control`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'adjust_physics',
        params
      })
    });
    const result = await response.json();
    
    if (result.success) {
      this.notifySceneUpdate({ physics: params });
    }
    
    return result;
  }

  // 调整灯光
  async adjustLighting(params) {
    const response = await fetch(`${this.apiBaseUrl}/api/v1/twins/scene/control`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'adjust_lighting',
        params
      })
    });
    const result = await response.json();
    
    if (result.success) {
      this.notifySceneUpdate({ lighting: params });
    }
    
    return result;
  }

  // 重置场景
  async resetScene() {
    const response = await fetch(`${this.apiBaseUrl}/api/v1/twins/scene/control`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'reset' })
    });
    const result = await response.json();
    
    if (result.success) {
      localStorage.setItem('twins_scene', JSON.stringify(result.data));
      this.currentScene = result.data;
      this.notifySceneUpdate(result.data);
    }
    
    return result;
  }

  // ===== 船只控制 =====

  // 控制船只
  async controlBoat(boatId, action, params = {}) {
    const response = await fetch(`${this.apiBaseUrl}/api/v1/twins/boat/control`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        boat_id: boatId,
        action,
        params
      })
    });
    return await response.json();
  }

  // 移动船只
  async moveBoat(boatId, params) {
    return this.controlBoat(boatId, 'move', params);
  }

  // 停止船只
  async stopBoat(boatId) {
    return this.controlBoat(boatId, 'stop');
  }

  // 设置航向
  async setBoatHeading(boatId, heading) {
    return this.controlBoat(boatId, 'set_heading', { heading });
  }

  // 设置速度
  async setBoatSpeed(boatId, speed) {
    return this.controlBoat(boatId, 'set_speed', { speed });
  }

  // ===== 传感器数据 =====

  // 查询传感器数据
  async querySensors(sensorType = 'all', count = 1) {
    const response = await fetch(`${this.apiBaseUrl}/api/v1/twins/sensor/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sensor_type: sensorType,
        count
      })
    });
    return await response.json();
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
      body: JSON.stringify({
        query,
        context
      })
    });
    return await response.json();
  }

  // ===== AI 对话 =====

  // 智能对话（解析自然语言并执行相应操作）
  async chat(message) {
    // 简单意图识别
    const msgLower = message.toLowerCase();
    
    // 场景控制意图
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
    
    // 故障诊断
    if (msgLower.includes('故障') || msgLower.includes('问题') || msgLower.includes('异常')) {
      return await this.diagnose(message);
    }
    
    // 决策支持
    if (msgLower.includes('建议') || msgLower.includes('应该') || msgLower.includes('适合')) {
      return await this.getDecision(message);
    }
    
    // 默认：尝试作为决策问题处理
    return await this.getDecision(message);
  }

  // ===== 辅助方法 =====

  // 通知场景更新（发送给主场景）
  notifySceneUpdate(data) {
    // 向主窗口发送消息（如果存在）
    if (window.opener || window.parent !== window) {
      window.postMessage({
        type: 'TWINS_SCENE_UPDATE',
        data
      }, '*');
    }
    
    // 触发自定义事件
    const event = new CustomEvent('twinsSceneUpdate', { detail: data });
    window.dispatchEvent(event);
    
    console.log('🌊 场景已更新:', data);
  }
}

// 创建全局实例
window.aiController = new AITwinsController();

// 自动检查服务状态
(async function init() {
  try {
    await window.aiController.checkHealth();
    console.log('✅ Poseidon 服务在线');
  } catch (e) {
    console.warn('⚠️  Poseidon 服务离线，部分功能可能不可用');
  }
  
  console.log('🤖 AI Twins Controller v2.0 已初始化');
  console.log('使用 window.aiController 与智能体交互');
  console.log('API 端点:', window.aiController.apiBaseUrl);
})();
