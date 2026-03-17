/**
 * Simple Bridge Chat - 轻量级舰桥聊天组件
 * 直接集成到数字孪生页面
 */

export class SimpleBridgeChat {
  constructor() {
    this.config = this.loadConfig();
    this.container = null;
    this.messages = [];
    this.isExpanded = true; // 默认展开
    this.dragState = null;
    this.shipContext = {};
    
    this.init();
    this.initializeShipContext();
    setInterval(() => this.updateShipContextFromAPI(), 5000);
  }
  
  loadConfig() {
    try {
      return JSON.parse(localStorage.getItem('poseidon_config') || '{}');
    } catch {
      return {};
    }
  }
  
  init() {
    // 创建聊天容器
    this.container = document.createElement('div');
    this.container.id = 'simple-bridge-chat';
    this.container.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 320px;
      background: rgba(11, 21, 37, 0.95);
      border: 2px solid ${this.config.apiKey ? '#4caf50' : '#ffb74d'};
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
      backdrop-filter: blur(10px);
      z-index: 999;
      transition: all 0.3s ease;
    `;
    
    // 标题栏
    const header = document.createElement('div');
    header.id = 'bridge-header';
    header.style.cssText = `
      padding: 12px 16px;
      background: linear-gradient(135deg, #1e3a5f 0%, #0b1525 100%);
      border-bottom: 1px solid ${this.config.apiKey ? '#4caf50' : '#ffb74d'};
      border-radius: 10px 10px 0 0;
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: move;
      user-select: none;
    `;
    header.innerHTML = `
      <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 20px;">🌊</span>
        <span style="color: #4fc3f7; font-weight: bold; font-size: 14px;">Poseidon-X Bridge</span>
      </div>
      <div style="display: flex; align-items: center; gap: 8px;">
        <span style="color: #888; font-size: 10px;">💡 拖动</span>
        <span style="color: ${this.config.apiKey ? '#81c784' : '#ffb74d'}; font-size: 11px;">
          ${this.config.apiKey ? '● AI Ready' : '○ 配置 API'}
        </span>
      </div>
    `;
    
    // 消息区域
    const messagesContainer = document.createElement('div');
    messagesContainer.id = 'bridge-messages';
    messagesContainer.style.cssText = `
      max-height: 300px;
      overflow-y: auto;
      padding: 16px;
      transition: max-height 0.3s ease;
    `;
    
    // 输入区域
    const quickBar = document.createElement('div');
    quickBar.style.cssText = `padding: 8px 12px; display:flex; gap:6px; flex-wrap:wrap; border-top: 1px solid rgba(255,255,255,0.08);`;
    ['主机状态','碰撞风险','能效状态'].forEach(text => {
      const btn = document.createElement('button');
      btn.textContent = text;
      btn.style.cssText = 'padding:4px 8px; border:none; border-radius:999px; background:rgba(79,195,247,0.16); color:#b3e5fc; cursor:pointer; font-size:11px;';
      btn.addEventListener('click', () => {
        const inputEl = document.getElementById('bridge-input');
        if (inputEl) inputEl.value = text;
      });
      quickBar.appendChild(btn);
    });

    const inputArea = document.createElement('div');
    inputArea.style.cssText = `
      padding: 12px;
      border-top: 1px solid rgba(255,255,255,0.1);
      display: flex;
      gap: 8px;
    `;
    
    const input = document.createElement('input');
    input.type = 'text';
    input.id = 'bridge-input';
    input.placeholder = this.config.apiKey ? '询问船舶状态...' : '请先配置 LLM';
    input.disabled = !this.config.apiKey;
    input.style.cssText = `flex: 1; padding: 8px 12px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; color: #fff; font-size: 13px;`;
    
    const sendBtn = document.createElement('button');
    sendBtn.id = 'bridge-send';
    sendBtn.textContent = '发送';
    sendBtn.style.cssText = `padding: 8px 16px; background: linear-gradient(135deg, #4fc3f7 0%, #2196f3 100%); border: none; border-radius: 6px; color: #fff; cursor: ${this.config.apiKey ? 'pointer' : 'not-allowed'}; font-size: 13px;`;
    
    inputArea.appendChild(input);
    inputArea.appendChild(sendBtn);
    
    this.container.appendChild(header);
    this.container.appendChild(messagesContainer);
    this.container.appendChild(quickBar);
    this.container.appendChild(inputArea);
    document.body.appendChild(this.container);
    
    // 绑定事件
    header.addEventListener('mousedown', (e) => this.startDrag(e));
    document.addEventListener('mousemove', (e) => this.onDrag(e));
    document.addEventListener('mouseup', () => this.endDrag());
    
    // 双击展开/收起
    header.addEventListener('dblclick', () => this.toggle());
    
    // 使用已创建的 input 和 sendBtn
    sendBtn.addEventListener('click', () => this.sendMessage());
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.sendMessage();
    });
    
    // 添加欢迎消息
    setTimeout(() => {
      if (!this.config.apiKey) {
        this.addMessage('system', '⚠️ 请先访问 LLM 配置页面配置 API Key');
      } else {
        this.addMessage('system', `✅ LLM 已配置 (${this.config.llmProvider || 'minimax'})。有什么可以帮您？`);
      }
    }, 500);
    
    console.log('🌊 Simple Bridge Chat initialized');
  }
  
  toggle() {
    this.isExpanded = !this.isExpanded;
    const messagesContainer = document.getElementById('bridge-messages');
    const inputArea = messagesContainer.nextElementSibling;
    const input = document.getElementById('bridge-input');
    
    if (this.isExpanded) {
      messagesContainer.style.maxHeight = '300px';
      messagesContainer.style.padding = '16px';
      inputArea.style.display = 'flex';
      input.disabled = !this.config.apiKey;
    } else {
      messagesContainer.style.maxHeight = '0';
      messagesContainer.style.padding = '0 16px';
      inputArea.style.display = 'none';
    }
  }
  
  startDrag(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON') return;
    this.dragState = {
      startX: e.clientX,
      startY: e.clientY,
      startLeft: this.container.offsetLeft,
      startTop: this.container.offsetTop
    };
    this.container.style.transition = 'none';
  }
  
  onDrag(e) {
    if (!this.dragState) return;
    const dx = e.clientX - this.dragState.startX;
    const dy = e.clientY - this.dragState.startY;
    const newLeft = this.dragState.startLeft + dx;
    const newTop = this.dragState.startTop + dy;
    
    // 限制在视口内
    const maxX = window.innerWidth - this.container.offsetWidth;
    const maxY = window.innerHeight - this.container.offsetHeight;
    
    this.container.style.left = Math.max(0, Math.min(newLeft, maxX)) + 'px';
    this.container.style.top = Math.max(0, Math.min(newTop, maxY)) + 'px';
    this.container.style.right = 'auto';
    this.container.style.bottom = 'auto';
  }
  
  endDrag() {
    this.dragState = null;
    this.container.style.transition = 'all 0.3s ease';
  }
  
  addMessage(role, text) {
    const messagesContainer = document.getElementById('bridge-messages');
    const messageDiv = document.createElement('div');
    messageDiv.style.cssText = `
      padding: 10px;
      margin-bottom: 8px;
      border-radius: 6px;
      font-size: 13px;
      background: ${role === 'user' ? 'rgba(79,195,247,0.2)' : role === 'system' ? 'rgba(255,183,77,0.2)' : 'rgba(76,175,80,0.2)'};
      color: ${role === 'user' ? '#81d4fa' : role === 'system' ? '#ffe082' : '#a5d6a7'};
    `;
    messageDiv.textContent = text;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
  
  async sendMessage() {
    const input = document.getElementById('bridge-input');
    const text = input.value.trim();
    
    if (!text || !this.config.apiKey) return;
    
    this.addMessage('user', text);
    input.value = '';
    this.addMessage('assistant', '🤔 正在思考...');
    
    try {
      let channelContext = '';
      const lower = text.toLowerCase();
      if (lower.includes('碰撞') || lower.includes('风险') || lower.includes('ais') || lower.includes('导航')) {
        const nav = await this.queryChannelData('intelligent_navigation', text);
        channelContext += `\n\n[智能导航]: ${typeof nav.result === 'string' ? nav.result : JSON.stringify(nav.result)}`;
      }
      if (lower.includes('主机') || lower.includes('机舱') || lower.includes('健康') || lower.includes('维护')) {
        const eng = await this.queryChannelData('intelligent_engine', text);
        channelContext += `\n\n[智能机舱]: ${typeof eng.result === 'string' ? eng.result : JSON.stringify(eng.result)}`;
      }
      if (lower.includes('能效') || lower.includes('cii') || lower.includes('eexi')) {
        const eff = await this.queryChannelData('energy_efficiency', text);
        channelContext += `\n\n[能效管理]: ${typeof eff.result === 'string' ? eff.result : JSON.stringify(eff.result)}`;
      }

      const response = await this.callLLM(text, channelContext);
      const messagesContainer = document.getElementById('bridge-messages');
      messagesContainer.lastChild.remove();
      this.addMessage('assistant', response);
    } catch (error) {
      console.error('LLM call failed:', error);
      const messagesContainer = document.getElementById('bridge-messages');
      messagesContainer.lastChild.remove();
      this.addMessage('system', `❌ 调用失败：${error.message}`);
    }
  }
  
  async callLLM(userMessage, channelContext = '') {
    const endpoint = this.config.apiEndpoint || 'https://api.minimax.chat/v1';
    const model = this.config.model || 'MiniMax-M2.5';
    
    const systemContext = `${this.config.systemPrompt || '你是 Poseidon-X 船舶智能助手。'}\n\n当前系统上下文：${JSON.stringify(this.shipContext)}${channelContext}`;
    const messages = [
      {
        role: 'system',
        content: systemContext
      },
      {
        role: 'user',
        content: userMessage
      }
    ];
    
    const response = await fetch(endpoint + '/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config.apiKey}`
      },
      body: JSON.stringify({
        model: model,
        messages: messages,
        temperature: this.config.temperature || 0.7,
        max_tokens: 2048
      })
    });
    
    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error: ${response.status} - ${error}`);
    }
    
    const data = await response.json();
    return data.choices[0].message.content;
  }

  async queryChannelData(channelName, query) {
    const response = await fetch(`/api/v1/channels/${channelName}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    if (!response.ok) {
      throw new Error(`Channel query failed: ${channelName}`);
    }
    return await response.json();
  }
  
  updateShipContext(context) {
    this.shipContext = { ...this.shipContext, ...context };
  }

  async initializeShipContext() {
    await this.updateShipContextFromAPI();
  }

  async updateShipContextFromAPI() {
    try {
      const [sensorsResp, channelsResp, engineResp] = await Promise.all([
        fetch('/api/v1/sensors'),
        fetch('/api/v1/channels'),
        fetch('/api/v1/engine/status')
      ]);
      const sensors = await sensorsResp.json();
      const channels = await channelsResp.json();
      const engine = await engineResp.json();
      this.updateShipContext({
        sensors: sensors.sensors || [],
        channels: channels.channels || [],
        engine,
        updatedAt: new Date().toISOString()
      });
    } catch (error) {
      console.warn('Failed to refresh ship context:', error);
    }
  }
}

// 自动初始化
if (typeof window !== 'undefined') {
  console.log('🌊 Bridge Chat script loaded, initializing...');
  window.addEventListener('DOMContentLoaded', () => {
    console.log('🌊 DOM ready, creating Bridge Chat...');
    setTimeout(() => {
      try {
        new SimpleBridgeChat();
        console.log('✅ Bridge Chat created successfully');
      } catch (error) {
        console.error('❌ Bridge Chat initialization failed:', error);
      }
    }, 1000);
  });
}
