/**
 * Bridge Chat - 舰桥自然语言交互中心
 * 
 * Software 3.0 理念：统一交互入口
 * - 船长不再需要面对 50 个不同的仪表盘和按钮
 * - 界面只有一个简单的对话框和一个沉浸式的 3D 数字孪生海图
 * 
 * 核心能力：
 * - 多模态输入（语音、文本、手势）
 * - 上下文感知（全船状态可见）
 * - 智能体协调（调度 N 个专业 Agent）
 */

import { EventEmitter } from '../utils/EventEmitter.js';
import { LLMClient } from './LLMClient.js';

export class BridgeChat extends EventEmitter {
  constructor(config = {}) {
    super();
    
    // 优先使用 localStorage 的配置（用户从 poseidon-config 保存的），避免被 PoseidonX 默认值覆盖
    const savedConfig = this._loadConfig();
    const finalConfig = { ...config, ...savedConfig };
    
    this.config = {
      llmProvider: finalConfig.llmProvider || 'minimax',
      apiKey: finalConfig.apiKey || '',
      apiEndpoint: finalConfig.apiEndpoint || 'https://api.minimax.chat/v1',
      model: finalConfig.model || 'MiniMax-M2.5',
      temperature: finalConfig.temperature || 0.7,
      voiceEnabled: finalConfig.enableVoice || false,
      language: finalConfig.language || 'zh-CN',
      maxContextLength: finalConfig.maxContextTokens || 128000,
      vibe: config.vibe || `你是 Poseidon-X 船舶智能系统的核心 AI 助手。
你管理着 4 个专业智能体：
1. Navigator Agent（领航员）- 负责航行和避碰
2. Engineer Agent（轮机长）- 负责设备健康和能效
3. Steward Agent（大管家）- 负责仓储和船员福祉
4. Safety Agent（安全官）- 负责安全监控和应急响应

你还可以直接执行以下菜单操作：
- 天气控制：设置降雨强度、风速、风向、温度、降雪强度、天气预设（calm/moderate/storm/typhoon/snow）
- 视图切换：顶视图(top view)、整体视图(overall view)
- 船体标记：设置船体颜色或区域颜色

当用户提问时，你要：
1. 判断应该由哪个Agent处理，或者是否需要执行菜单操作
2. 调用对应的Agent或执行菜单操作
3. 将结果用自然语言呈现给用户

你的语气专业、简洁、可靠。
你是一位经验丰富的领航员，精通海事专业术语。
你的职责：
1. 用简洁清晰的语言回答船长的问题
2. 在数字孪生海图上高亮关键信息
3. 协调船上各个专业智能体（领航员、轮机长、大管家、安全官）
4. 在紧急情况下提供快速决策支持
5. 当用户要求设置天气参数时，直接执行并确认

回答风格：专业、简洁、可执行。`,
      ...config
    };
    
    // 创建 LLM Client（配置由用户通过 poseidon-config.html 热插拔）
    this.llmClient = new LLMClient({});
    
    console.log('🧠 LLM Client initialized (hot-swappable via config page)');
    
    // 对话历史（作为 LLM 的上下文）
    this.conversationHistory = [];
    
    // 当前船舶状态（实时更新，作为 Context Window 的一部分）
    this.shipContext = {
      position: { lat: 0, lon: 0, heading: 0 },
      sensors: {}, // NMEA, Modbus 数据转为文本/Embedding
      environment: {}, // 天气、海况
      equipment: {}, // 设备状态
      crew: {}, // 船员信息
      alerts: [] // 警报列表
    };
    
    // UI 元素
    this.chatContainer = null;
    this.inputBox = null;
    this.messagesContainer = null;
    this.voiceButton = null;
    
    // 语音识别（Web Speech API）
    this.recognition = null;
    this.isListening = false;
    
    // 智能体引用
    this.agents = new Map(); // { 'navigator': NavigatorAgent, ... }
    
    this._initializeUI();
    this._initializeVoice();
    
    console.log('🌊 Bridge Chat initialized (Software 3.0)');
  }
  
  /**
   * 初始化 UI 界面
   * @private
   */
  _initializeUI() {
    // 创建聊天容器（左下角浮动，避免遮挡右侧数字孪生控制面板）
    this.chatContainer = document.createElement('div');
    this.chatContainer.id = 'bridge-chat-container';
    this.chatContainer.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 360px;
      height: 280px;
      background: rgba(11, 21, 37, 0.95);
      border: 2px solid #4fc3f7;
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
      backdrop-filter: blur(10px);
      z-index: 1000;
    `;
    
    // 标题栏
    const header = document.createElement('div');
    header.style.cssText = `
      padding: 12px 16px;
      background: linear-gradient(135deg, #1e3a5f 0%, #0b1525 100%);
      border-bottom: 1px solid #4fc3f7;
      border-radius: 10px 10px 0 0;
      display: flex;
      justify-content: space-between;
      align-items: center;
    `;
    header.innerHTML = `
      <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 20px;">🌊</span>
        <span style="color: #4fc3f7; font-weight: bold; font-size: 16px;">Poseidon-X Bridge</span>
      </div>
      <div style="color: #81c784; font-size: 12px;">AI Crew Ready</div>
    `;
    header.setAttribute('title', '拖动移动窗口');
    header.style.cursor = 'move';
    header.style.userSelect = 'none';
    // 标题栏拖动移动整个窗口
    this._bridgeDragState = null;
    this._boundBridgeDragMove = (e) => this._onBridgeDragMove(e);
    this._boundBridgeDragEnd = () => this._onBridgeDragEnd();
    header.addEventListener('mousedown', (e) => {
      if (e.button !== 0) return;
      const rect = this.chatContainer.getBoundingClientRect();
      this._bridgeDragState = {
        startX: e.clientX,
        startY: e.clientY,
        startLeft: rect.left,
        startTop: rect.top
      };
      this.chatContainer.style.bottom = 'auto';
      this.chatContainer.style.left = rect.left + 'px';
      this.chatContainer.style.top = rect.top + 'px';
      document.addEventListener('mousemove', this._boundBridgeDragMove);
      document.addEventListener('mouseup', this._boundBridgeDragEnd);
      e.preventDefault();
    });
    
    // 消息容器
    this.messagesContainer = document.createElement('div');
    this.messagesContainer.id = 'bridge-chat-messages';
    this.messagesContainer.style.cssText = `
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    `;
    
    // 添加欢迎消息（明确说明配置逻辑）
    const savedConfig = this._loadConfig();
    const providerName = savedConfig.llmProvider || 'LLM';
    const hasApiKey = !!savedConfig.apiKey;
    
    const welcomeText = hasApiKey
      ? `✅ 已配置 ${providerName} API Key。我是您的 AI 领航员，已接入大模型。\n\n📌 功能说明：\n• 语音/文字问答：使用 ${providerName} 大模型\n• 菜单功能：无需 LLM，直接执行\n• 切换模型：在 poseidon-config.html 随时更换提供商`
      : '欢迎登上 Poseidon-X 智能舰桥。\n\n📌 功能说明：\n• 菜单功能：✅ 可用（无需 LLM）\n• 语音/文字问答：需配置 API Key\n• 配置入口：打开 poseidon-config.html 选择 LLM 提供商（DeepSeek/OpenAI/MiniMax 等）';
    
    this._addMessage('system', welcomeText);
    
    // 输入区域
    const inputContainer = document.createElement('div');
    inputContainer.style.cssText = `
      padding: 12px;
      border-top: 1px solid #2a4a6a;
      display: flex;
      gap: 8px;
    `;
    
    this.inputBox = document.createElement('input');
    this.inputBox.type = 'text';
    this.inputBox.placeholder = hasApiKey
      ? '输入指令或问题... (例如: 右舷那艘船有碰撞风险吗？)'
      : '输入菜单指令或先配置 API Key → poseidon-config.html';
    this.inputBox.style.cssText = `
      flex: 1;
      padding: 10px 12px;
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid #4fc3f7;
      border-radius: 6px;
      color: #fff;
      font-size: 14px;
      outline: none;
    `;
    
    this.inputBox.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && this.inputBox.value.trim()) {
        this.sendMessage(this.inputBox.value);
        this.inputBox.value = '';
      }
    });
    
    // 语音按钮
    this.voiceButton = document.createElement('button');
    this.voiceButton.innerHTML = '🎤';
    this.voiceButton.style.cssText = `
      width: 44px;
      height: 44px;
      background: rgba(79, 195, 247, 0.2);
      border: 1px solid #4fc3f7;
      border-radius: 6px;
      color: #fff;
      font-size: 20px;
      cursor: pointer;
      transition: all 0.3s;
    `;
    
    this.voiceButton.addEventListener('click', () => {
      this.toggleVoiceInput();
    });
    
    inputContainer.appendChild(this.inputBox);
    inputContainer.appendChild(this.voiceButton);
    
    this.chatContainer.appendChild(header);
    this.chatContainer.appendChild(this.messagesContainer);
    this.chatContainer.appendChild(inputContainer);
    
    document.body.appendChild(this.chatContainer);
  }
  
  /**
   * Bridge 窗口拖动中
   * @private
   */
  _onBridgeDragMove(e) {
    if (!this._bridgeDragState) return;
    const dx = e.clientX - this._bridgeDragState.startX;
    const dy = e.clientY - this._bridgeDragState.startY;
    const left = Math.max(0, this._bridgeDragState.startLeft + dx);
    const top = Math.max(0, this._bridgeDragState.startTop + dy);
    this.chatContainer.style.left = left + 'px';
    this.chatContainer.style.top = top + 'px';
  }
  
  /**
   * Bridge 窗口拖动结束
   * @private
   */
  _onBridgeDragEnd() {
    this._bridgeDragState = null;
    document.removeEventListener('mousemove', this._boundBridgeDragMove);
    document.removeEventListener('mouseup', this._boundBridgeDragEnd);
  }
  
  /**
   * 初始化语音识别
   * @private
   */
  _initializeVoice() {
    if (!this.config.voiceEnabled) return;
    
    // Web Speech API
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      this.recognition.lang = this.config.language;
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
      
      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        this.inputBox.value = transcript;
        this.sendMessage(transcript);
      };
      
      this.recognition.onerror = (event) => {
        console.error('🎤 Voice recognition error:', event.error);
        this._stopListening();
      };
      
      this.recognition.onend = () => {
        this._stopListening();
      };
      
      console.log('🎤 Voice input initialized');
    } else {
      console.warn('⚠️ Web Speech API not supported');
    }
  }
  
  /**
   * 切换语音输入
   */
  toggleVoiceInput() {
    if (!this.recognition) {
      alert('语音识别不可用。请在支持 Web Speech API 的浏览器中使用。');
      return;
    }
    
    if (this.isListening) {
      this.recognition.stop();
    } else {
      this.recognition.start();
      this._startListening();
    }
  }
  
  /**
   * 开始监听
   * @private
   */
  _startListening() {
    this.isListening = true;
    this.voiceButton.style.background = 'rgba(244, 67, 54, 0.5)';
    this.voiceButton.style.animation = 'pulse 1.5s infinite';
    
    // 添加脉冲动画
    const style = document.createElement('style');
    style.textContent = `
      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
      }
    `;
    document.head.appendChild(style);
  }
  
  /**
   * 停止监听
   * @private
   */
  _stopListening() {
    this.isListening = false;
    this.voiceButton.style.background = 'rgba(79, 195, 247, 0.2)';
    this.voiceButton.style.animation = 'none';
  }
  
  /**
   * 发送消息
   * @param {string} message 
   */
  async sendMessage(message) {
    if (!message || !message.trim()) return;
    
    // 每次发送消息前重新加载配置，支持热插拔
    const savedConfig = this._loadConfig();
    const providerName = savedConfig.llmProvider || 'LLM';
    
    // 添加用户消息到 UI
    this._addMessage('user', message);
    
    // 添加到对话历史
    this.conversationHistory.push({
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    });
    
    // 显示"思考中"状态（显示当前使用的模型）
    const thinkingId = this._addMessage('assistant', `正在分析 [${providerName}]...`, true);
    
    try {
      // 1. 先识别是否为菜单操作并执行（与 GUI 一致），再走 LLM；若已执行菜单则让 LLM 只做简短确认
      const menuResult = this._executeMenuActionIfMatch(message);
      const response = await this._callLLM(message, menuResult.executed ? menuResult.label : null);
      let displayContent = response.content;
      if (menuResult.executed) {
        displayContent = response.content + '\n\n已执行菜单操作：' + menuResult.label;
      }
      
      // 移除"思考中"消息，添加回复
      this._removeMessage(thinkingId);
      this._addMessage('assistant', displayContent);
      
      // 如果需要调用智能体
      if (response.agentCalls) {
        for (const call of response.agentCalls) {
          await this._invokeAgent(call.agentName, call.task);
        }
      }
      
      // 添加到对话历史（存完整展示内容）
      this.conversationHistory.push({
        role: 'assistant',
        content: displayContent,
        timestamp: new Date().toISOString()
      });
      
      this.emit('message:sent', { message, response: { ...response, content: displayContent } });
      
    } catch (error) {
      this._removeMessage(thinkingId);
      this._addMessage('error', `错误：${error.message}`);
      console.error('❌ Bridge Chat error:', error);
    }
  }
  
  /**
   * 识别用户输入是否为菜单操作，若是则执行（与 GUI 菜单项一一对应）
   * 顺序：先走 LLM，识别是菜单操作后再调用本方法执行菜单。
   * @param {string} message - 用户输入
   * @returns {{ executed: boolean, label?: string }}
   */
  _executeMenuActionIfMatch(message) {
    const text = (message || '').trim();
    const lower = text.toLowerCase();
    
    // 视图切换优先：输入 "top view" / "overall view" 等等同于点击对应按钮
    if (typeof window.poseidonSwitchView === 'function') {
      const viewTrim = lower.replace(/\s+/g, ' ').trim();
      if (viewTrim === 'top view' || viewTrim === 'topview' || viewTrim === '顶视图' || viewTrim === '俯视图') {
        if (window.poseidonSwitchView('top')) return { executed: true, label: '⬇️ Top View' };
      }
      if (viewTrim === 'overall view' || viewTrim === 'overallview' || viewTrim === '整体视图' || viewTrim === '全局视图') {
        if (window.poseidonSwitchView('overall')) return { executed: true, label: '🌐 Overall View' };
      }
      // 短句包含视图关键词也触发（如 "switch to top view"）
      if (/\b(top\s*view|topview|顶视图|俯视图)\b/.test(lower) && window.poseidonSwitchView('top')) {
        return { executed: true, label: '⬇️ Top View' };
      }
      if (/\b(overall\s*view|overallview|整体视图|全局视图)\b/.test(lower) && window.poseidonSwitchView('overall')) {
        return { executed: true, label: '🌐 Overall View' };
      }
    }
    
    // 船体颜色标记：区域+颜色 或 整船颜色
    if (typeof window.poseidonSetHullColor === 'function' && typeof window.poseidonSetHullRegionColor === 'function') {
      const regionNames = {
        bow: ['船首', 'bow', '船头'], stern: ['船尾', 'stern'], midship: ['船舯', 'midship', '舯'],
        waterline: ['水线', 'waterline'], keel: ['龙骨', 'keel'], propulsion: ['推进器', 'propulsion', '推进'],
        lifesaving: ['救生', 'lifesaving'], fire: ['消防', 'fire'], danger: ['危险', 'danger'],
        cargo: ['装卸', 'cargo'], mooring: ['系泊', 'mooring'], boarding: ['登船', 'boarding'],
        inspection: ['检查', 'inspection'], radar: ['雷达', 'radar'], gps: ['gps'],
        communication: ['通信', 'communication'], camera: ['摄像头', 'camera']
      };
      const colorWords = ['蓝色', '红色', '绿色', '黄色', '紫色', '橙色', '白色', '黑色', '棕色', '深蓝', '荧光绿', '荧光红', '荧光黄',
        'blue', 'red', 'green', 'yellow', 'purple', 'orange', 'white', 'black', 'brown'];
      // 整船：船体蓝色 / hull blue / 整船红色
      const hullWhole = text.match(/(?:船体|整船|hull)\s*(设为?|设置为?|为|to)?\s*(\S+)/i) || lower.match(/(?:船体|整船|hull)\s*(?:设为?|设置为?|为|to)?\s*(\w+)/);
      if (hullWhole) {
        const colorPart = (hullWhole[2] || hullWhole[1] || '').trim();
        if (colorWords.some(c => colorPart.includes(c)) && window.poseidonSetHullColor(colorPart)) {
          return { executed: true, label: '🎨 Hull Color ' + colorPart };
        }
      }
      // 区域+颜色：船首蓝色 / 船首 蓝色 / bow blue / set stern to red（支持无空格）
      for (const [regionKey, names] of Object.entries(regionNames)) {
        for (const name of names) {
          const escaped = name.replace(/\s/g, '\\s*');
          const re = new RegExp(escaped + '(?:\\s*(?:设为?|设置为?|为|to)?\\s*)?(' + colorWords.join('|') + ')', 'i');
          const m = text.match(re) || lower.match(re);
          if (m && m[1]) {
            const colorPart = m[1].trim();
            if (window.poseidonSetHullRegionColor(regionKey, colorPart)) {
              return { executed: true, label: '🎨 ' + name + ' → ' + colorPart };
            }
          }
        }
      }
    }

    // 带参数的菜单操作：风向/风速，设置后需与 GUI「🌤️ Weather System」联动
    if (typeof window.poseidonSetWindDirection === 'function') {
      const windDirMatch = text.match(/(?:风向|wind\s*direction)\s*(\d+)\s*(?:度|°|度)?/i) || lower.match(/(?:风向|wind\s*direction)\s*(\d+)/);
      if (windDirMatch) {
        const deg = parseInt(windDirMatch[1], 10);
        if (!isNaN(deg) && window.poseidonSetWindDirection(deg)) {
          return { executed: true, label: '🌬️ Wind Direction ' + deg + '°' };
        }
      }
    }
    if (typeof window.poseidonSetWindSpeed === 'function') {
      const windSpeedMatch = text.match(/(?:风速|wind\s*speed)\s*(\d+(?:\.\d+)?)\s*(?:节|m\/s|米)?/i) || lower.match(/(?:风速|wind\s*speed)\s*(\d+(?:\.\d+)?)/);
      if (windSpeedMatch) {
        const speed = parseFloat(windSpeedMatch[1]);
        if (!isNaN(speed) && window.poseidonSetWindSpeed(speed)) {
          return { executed: true, label: '🌬️ Wind Speed ' + speed + ' m/s' };
        }
      }
    }
    // 降雨强度：设置降雨强度为15、降雨强度15、雨量15、rain 15 等
    if (typeof window.poseidonSetRainIntensity === 'function') {
      const rainPatterns = [
        /设置\s*降雨\s*强度\s*[为为]?\s*(\d+(?:\.\d+)?)/i,
        /降雨\s*强度\s*[为]?\s*(\d+(?:\.\d+)?)/i,
        /雨\s*强度\s*[为]?\s*(\d+(?:\.\d+)?)/i,
        /雨量\s*[为]?\s*(\d+(?:\.\d+)?)/i,
        /rain\s*intensity\s*(\d+(?:\.\d+)?)/i,
        /雨\s*(\d+(?:\.\d+)?)\s*mm/i,
        /降雨\s*(\d+(?:\.\d+)?)/i
      ];
      for (const pattern of rainPatterns) {
        const match = text.match(pattern) || lower.match(pattern);
        if (match) {
          const val = parseFloat(match[1]);
          if (!isNaN(val) && window.poseidonSetRainIntensity(val)) {
            return { executed: true, label: `🌧️ Rain Intensity ${val} mm/h` };
          }
        }
      }
    }
    
    // 风速：设置风速为20、风速20、wind speed 20 等
    if (typeof window.poseidonSetWindSpeed === 'function') {
      const windSpeedPatterns = [
        /设置\s*风速\s*[为]?\s*(\d+(?:\.\d+)?)/i,
        /风速\s*[为]?\s*(\d+(?:\.\d+)?)/i,
        /wind\s*speed\s*(\d+(?:\.\d+)?)/i,
        /风\s*(\d+(?:\.\d+)?)\s*m\/s/i
      ];
      for (const pattern of windSpeedPatterns) {
        const match = text.match(pattern) || lower.match(pattern);
        if (match) {
          const val = parseFloat(match[1]);
          if (!isNaN(val) && window.poseidonSetWindSpeed(val)) {
            return { executed: true, label: `🌬️ Wind Speed ${val} m/s` };
          }
        }
      }
    }
    
    // 风向：设置风向为180、风向180、wind direction 180 等
    if (typeof window.poseidonSetWindDirection === 'function') {
      const windDirPatterns = [
        /设置\s*风向\s*[为]?\s*(\d+(?:\.\d+)?)/i,
        /风向\s*[为]?\s*(\d+(?:\.\d+)?)/i,
        /wind\s*direction\s*(\d+(?:\.\d+)?)/i
      ];
      for (const pattern of windDirPatterns) {
        const match = text.match(pattern) || lower.match(pattern);
        if (match) {
          const val = parseFloat(match[1]);
          if (!isNaN(val) && window.poseidonSetWindDirection(val)) {
            return { executed: true, label: `🧭 Wind Direction ${val}°` };
          }
        }
      }
    }
    
    // 温度：设置温度为20、温度20、temperature 20 等
    if (typeof window.poseidonSetTemperature === 'function') {
      const tempPatterns = [
        /设置\s*温度\s*[为]?\s*(-?\d+(?:\.\d+)?)/i,
        /温度\s*[为]?\s*(-?\d+(?:\.\d+)?)/i,
        /temperature\s*(-?\d+(?:\.\d+)?)/i
      ];
      for (const pattern of tempPatterns) {
        const match = text.match(pattern) || lower.match(pattern);
        if (match) {
          const val = parseFloat(match[1]);
          if (!isNaN(val) && window.poseidonSetTemperature(val)) {
            return { executed: true, label: `🌡️ Temperature ${val}°C` };
          }
        }
      }
    }
    
    // 降雪强度：设置降雪强度为10、雪量10 等
    if (typeof window.poseidonSetSnowIntensity === 'function') {
      const snowPatterns = [
        /设置\s*降雪\s*强度\s*[为]?\s*(\d+(?:\.\d+)?)/i,
        /降雪\s*强度\s*[为]?\s*(\d+(?:\.\d+)?)/i,
        /雪量\s*[为]?\s*(\d+(?:\.\d+)?)/i,
        /snow\s*intensity\s*(\d+(?:\.\d+)?)/i
      ];
      for (const pattern of snowPatterns) {
        const match = text.match(pattern) || lower.match(pattern);
        if (match) {
          const val = parseFloat(match[1]);
          if (!isNaN(val) && window.poseidonSetSnowIntensity(val)) {
            return { executed: true, label: `❄️ Snow Intensity ${val} mm/h` };
          }
        }
      }
    }
    
    // 天气预设：晴天、小雨、暴风雨、台风、snow 等
    if (typeof window.poseidonSetWeatherPreset === 'function') {
      const presetPatterns = [
        { keys: ['晴天', '晴朗', 'calm', '好天气'], preset: 'calm' },
        { keys: ['多云', '阴天', 'cloudy'], preset: 'moderate' },
        { keys: ['暴风雨', 'storm', '风暴'], preset: 'storm' },
        { keys: ['台风', '飓风', 'typhoon'], preset: 'typhoon' },
        { keys: ['雪', '下雪', 'snow'], preset: 'snow' }
      ];
      for (const { keys, preset } of presetPatterns) {
        if (keys.some(k => lower.includes(k) || text.includes(k))) {
          if (window.poseidonSetWeatherPreset(preset)) {
            return { executed: true, label: `⛈️ Weather Preset: ${preset}` };
          }
        }
      }
    }
    
    if (typeof window.poseidonMenuAction !== 'function') return { executed: false };
    // 与 GUI 菜单顺序一致：Poseidon-X AI → Ship Control → Weather → Camera Views → Display
    const menuMap = [
      { keys: ['碰撞风险', '碰撞', 'check collision', 'collision risk'], actionId: 'check_collision', label: '🚢 Check Collision Risk' },
      { keys: ['主机', '排温', '检查主机', 'check engine', 'engine'], actionId: 'check_engine', label: '⚙️ Check Engine' },
      { keys: ['台风', '17级', 'set typhoon', 'typhoon'], actionId: 'set_typhoon', label: '🌀 Set Typhoon (17)' },
      { keys: ['稳定船体', '稳定', 'stabilize', 'stabilize ship'], actionId: 'stabilize_ship', label: '⚖️ Stabilize Ship' },
      { keys: ['重置船', '重置', 'reset ship', 'reset'], actionId: 'reset_ship', label: '🔄 Reset Ship' },
      { keys: ['顶视图', '俯视图', 'top view', 'topview', '从上往下'], actionId: 'view_top', label: '⬇️ Top View' },
      { keys: ['整体视图', 'overall view', 'overallview', '全局视图'], actionId: 'view_overall', label: '🌐 Overall View' },
      { keys: ['坐标轴', 'show axes', 'axes', '显示坐标轴', '隐藏坐标轴'], actionId: 'show_axes', label: '👁️ Show Axes' },
      { keys: ['尺寸线', '尺寸', 'show dimensions', 'dimensions', '显示尺寸'], actionId: 'show_dimensions', label: '👁️ Show Dimensions' },
      // 应急场景
      { keys: ['火灾', '火情', '机舱火灾', '模拟火灾', 'fire', 'simulate fire'], actionId: 'simulate_fire', label: '🔥 Simulate Fire' },
      { keys: ['落水', 'MOB', '人员落水', '模拟落水', 'man overboard', 'simulate mob'], actionId: 'simulate_mob', label: '🚨 Simulate MOB' },
      // 查询功能
      { keys: ['查询碰撞风险', '碰撞风险', 'collision risk'], actionId: 'check_collision', label: '🚢 Check Collision Risk' },
      { keys: ['检查主机', '主机状态', 'engine status', 'check engine'], actionId: 'check_engine', label: '⚙️ Check Engine' },
      { keys: ['检查库存', '库存', 'inventory'], actionId: 'check_inventory', label: '📦 Check Inventory' },
      { keys: ['安全态势', '安全评估', 'safety assessment'], actionId: 'check_safety', label: '🛡️ Safety Assessment' },
      { keys: ['并行任务', '并行执行', 'parallel'], actionId: 'parallel_tasks', label: '⚡ Parallel Tasks' },
      { keys: ['数字孪生', 'digital twin', '数字孪生演示'], actionId: 'digital_twin', label: '🗺️ Digital Twin Demo' }
    ];
    for (const { keys, actionId, label } of menuMap) {
      if (keys.some(k => lower.includes(k) || text.includes(k))) {
        if (window.poseidonMenuAction(actionId)) {
          return { executed: true, label };
        }
      }
    }
    return { executed: false };
  }
  
  /**
   * 调用 LLM（真实 API）
   * @param {string} userMessage - 用户输入
   * @param {string|null} executedMenuLabel - 若用户指令已触发菜单操作，则为该操作的显示标签，用于让 LLM 仅做简短确认
   * @private
   */
  async _callLLM(userMessage, executedMenuLabel = null) {
    // 构建完整的上下文
    const context = this._buildContextWindow();
    
    // 构建消息数组（OpenAI 格式）：历史不含当前条，避免重复
    const historyWithoutCurrent = this.conversationHistory.slice(0, -1);
    const messages = [
      {
        role: 'system',
        content: this.config.vibe
      },
      {
        role: 'system',
        content: `当前船舶状态：\n${JSON.stringify(this.shipContext, null, 2)}`
      },
      ...(executedMenuLabel
        ? [{
            role: 'system',
            content: `用户已通过指令直接执行了「${executedMenuLabel}」操作，请用一句简短中文确认此操作已执行，不要展开情景分析或冗长解释。`
          }]
        : []),
      ...historyWithoutCurrent.slice(-5).map(h => ({
        role: h.role,
        content: h.content
      })),
      {
        role: 'user',
        content: userMessage
      }
    ];
    
    try {
      // 调用真实的 LLM API
      const response = await this.llmClient.chat(messages);
      
      // 智能路由
      const agentCalls = this._routeToAgents(userMessage);
      
      return {
        content: response.content,
        agentCalls: agentCalls,
        metadata: {
          model: response.model,
          provider: this.config.llmProvider,
          usage: response.usage,
          timestamp: new Date().toISOString()
        }
      };
      
    } catch (error) {
      console.error('❌ LLM 调用失败:', error);
      
      // 如果 API 调用失败，返回友好提示
      return {
        content: `抱歉，LLM 服务暂时不可用。错误：${error.message}\n\n提示：请访问 /poseidon-config.html 配置 API Key。`,
        agentCalls: [],
        metadata: {
          error: error.message,
          timestamp: new Date().toISOString()
        }
      };
    }
  }
  
  /**
   * 从 localStorage 加载配置
   * @private
   */
  _loadConfig() {
    const saved = localStorage.getItem('poseidon_config');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (error) {
        console.warn('加载配置失败:', error);
      }
    }
    return {};
  }
  
  /**
   * 构建上下文窗口（Context Window = RAM）
   * 将全船状态转化为文本，喂给 LLM
   * @private
   */
  _buildContextWindow() {
    const contextParts = [];
    
    // 1. 系统 Vibe（角色定义）
    contextParts.push({
      type: 'system',
      content: this.config.vibe
    });
    
    // 2. 当前船舶状态（Sensor Data → Text）
    contextParts.push({
      type: 'ship_status',
      content: `
当前船舶状态：
- 位置：${this.shipContext.position.lat}°N, ${this.shipContext.position.lon}°E
- 航向：${this.shipContext.position.heading}°
- 传感器状态：${Object.keys(this.shipContext.sensors).length} 个传感器在线
- 环境：${JSON.stringify(this.shipContext.environment)}
- 警报：${this.shipContext.alerts.length} 条
      `.trim()
    });
    
    // 3. 对话历史（最近 N 条）
    const recentHistory = this.conversationHistory.slice(-10); // 保留最近 10 条
    contextParts.push(...recentHistory);
    
    return contextParts;
  }
  
  /**
   * 路由到智能体
   * 根据用户问题的关键词，决定需要调用哪些 Agent
   * @private
   */
  _routeToAgents(message) {
    const calls = [];
    
    // 简单的关键词匹配（实际应该用 LLM 做更智能的路由）
    if (message.includes('航行') || message.includes('避碰') || message.includes('航向') || message.includes('碰撞')) {
      calls.push({ agentName: 'navigator', task: message });
    }
    
    if (message.includes('主机') || message.includes('设备') || message.includes('能效') || message.includes('维护')) {
      calls.push({ agentName: 'engineer', task: message });
    }
    
    if (message.includes('库存') || message.includes('伙食') || message.includes('舱室') || message.includes('环境')) {
      calls.push({ agentName: 'steward', task: message });
    }
    
    if (message.includes('安全') || message.includes('监控') || message.includes('警报') || message.includes('应急')) {
      calls.push({ agentName: 'safety', task: message });
    }
    
    return calls;
  }
  
  /**
   * 调用智能体
   * @private
   */
  async _invokeAgent(agentName, task) {
    const agent = this.agents.get(agentName);
    
    if (!agent) {
      console.warn(`⚠️ Agent "${agentName}" not registered`);
      return null;
    }
    
    console.log(`🤖 Invoking ${agentName} agent with task:`, task);
    
    try {
      const result = await agent.execute(task, this.shipContext);
      
      // 触发事件
      this.emit('agent:executed', { agentName, task, result });
      
      return result;
    } catch (error) {
      console.error(`❌ Agent "${agentName}" execution failed:`, error);
      return null;
    }
  }
  
  /**
   * 注册智能体
   * @param {string} name - Agent 名称
   * @param {Object} agent - Agent 实例
   */
  registerAgent(name, agent) {
    this.agents.set(name, agent);
    console.log(`✅ Agent registered: ${name}`);
  }
  
  /**
   * 更新船舶上下文
   * @param {Object} contextUpdate - 上下文更新
   */
  updateShipContext(contextUpdate) {
    this.shipContext = {
      ...this.shipContext,
      ...contextUpdate
    };
    
    // 触发事件
    this.emit('context:updated', this.shipContext);
  }
  
  /**
   * 添加消息到 UI
   * @private
   */
  _addMessage(type, content, isTemporary = false) {
    const messageDiv = document.createElement('div');
    const messageId = `msg-${Date.now()}-${Math.random()}`;
    messageDiv.id = messageId;
    messageDiv.dataset.temporary = isTemporary;
    
    let bgColor, textColor, label;
    
    switch (type) {
      case 'user':
        bgColor = 'rgba(79, 195, 247, 0.2)';
        textColor = '#e8f0ff';
        label = '船长';
        break;
      case 'assistant':
        bgColor = 'rgba(129, 199, 132, 0.2)';
        textColor = '#e8f0ff';
        label = 'Poseidon-X';
        break;
      case 'system':
        bgColor = 'rgba(255, 193, 7, 0.2)';
        textColor = '#ffd54f';
        label = '系统';
        break;
      case 'error':
        bgColor = 'rgba(244, 67, 54, 0.2)';
        textColor = '#ff8a80';
        label = '错误';
        break;
      default:
        bgColor = 'rgba(255, 255, 255, 0.1)';
        textColor = '#fff';
        label = 'Unknown';
    }
    
    messageDiv.style.cssText = `
      padding: 12px;
      background: ${bgColor};
      border-left: 3px solid ${textColor};
      border-radius: 6px;
      color: ${textColor};
      font-size: 14px;
      line-height: 1.5;
      animation: slideIn 0.3s ease-out;
    `;
    
    messageDiv.innerHTML = `
      <div style="font-size: 11px; opacity: 0.7; margin-bottom: 4px;">${label}</div>
      <div>${content}</div>
    `;
    
    this.messagesContainer.appendChild(messageDiv);
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    
    // 添加滑入动画
    if (!document.querySelector('#bridge-chat-animations')) {
      const style = document.createElement('style');
      style.id = 'bridge-chat-animations';
      style.textContent = `
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `;
      document.head.appendChild(style);
    }
    
    return messageId;
  }
  
  /**
   * 移除消息
   * @private
   */
  _removeMessage(messageId) {
    const msgEl = document.getElementById(messageId);
    if (msgEl) {
      msgEl.remove();
    }
  }
  
  /**
   * 清空对话
   */
  clearConversation() {
    this.conversationHistory = [];
    this.messagesContainer.innerHTML = '';
    this._addMessage('system', '对话已清空。');
  }

  /**
   * 重新加载配置（热插拔）
   * 用户在配置页面更改后调用此方法
   */
  reloadConfig() {
    const savedConfig = this._loadConfig();
    const providerName = savedConfig.llmProvider || 'LLM';
    const hasApiKey = !!savedConfig.apiKey;
    
    // 更新输入框 placeholder
    this.inputBox.placeholder = hasApiKey
      ? `输入指令... (例如：右舷那艘船有碰撞风险吗？) [${providerName}]`
      : '输入菜单指令或先配置 API Key → poseidon-config.html';
    
    // 通知用户
    this._addMessage('system', `✅ 配置已更新 | 当前使用：${providerName}`);
    
    console.log('🔌 BridgeChat config reloaded:', {
      provider: savedConfig.llmProvider,
      model: savedConfig.model,
      hasApiKey
    });
  }
  
  /**
   * 销毁
   */
  dispose() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
    }
    this._onBridgeDragEnd();
    if (this.chatContainer && this.chatContainer.parentNode) {
      this.chatContainer.parentNode.removeChild(this.chatContainer);
    }
    
    this.removeAllListeners();
    console.log('🗑️ Bridge Chat disposed');
  }
}
