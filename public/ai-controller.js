/**
 * 前端 AI 控制面板
 * 集成到 index.html 的脚本
 */

class AIBoatController {
  constructor(apiBaseUrl = 'http://localhost:3001') {
    this.apiBaseUrl = apiBaseUrl;
    this.currentScene = null;
  }

  // 获取场景状态
  async getSceneStatus() {
    const response = await fetch(`${this.apiBaseUrl}/api/scene`);
    this.currentScene = await response.json();
    return this.currentScene;
  }

  // AI 对话
  async chat(message) {
    const response = await fetch(`${this.apiBaseUrl}/api/ai/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return await response.json();
  }

  // MCP 工具调用
  async callTool(tool, parameters) {
    const response = await fetch(`${this.apiBaseUrl}/api/mcp/call`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool, parameters })
    });
    return await response.json();
  }

  // 预设场景
  async applyPreset(preset) {
    const response = await fetch(`${this.apiBaseUrl}/api/scene/preset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preset })
    });
    return await response.json();
  }

  // 重置场景
  async resetScene() {
    const response = await fetch(`${this.apiBaseUrl}/api/scene/reset`, {
      method: 'POST'
    });
    return await response.json();
  }

  // 生成场景
  async generateScene(type) {
    return this.callTool('generate_scene', { type });
  }

  // 调整物理
  async adjustPhysics(params) {
    return this.callTool('adjust_physics', params);
  }

  // 控制船只
  async controlBoat(boatId, params) {
    return this.callTool('control_boat', { boatId, ...params });
  }

  // 调整灯光
  async adjustLighting(params) {
    return this.callTool('adjust_lighting', params);
  }
}

// 创建全局实例
window.aiController = new AIBoatController();

console.log('🤖 AI Controller 已初始化');
console.log('使用 window.aiController 与 AI 服务交互');
