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
    this.recognition = null;
    this.isListening = false;
    
    this.init();
    this.initializeShipContext();
    this.initVoice();
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
      width: 420px;
      max-height: calc(100vh - 80px);
      background: rgba(11, 21, 37, 0.95);
      border: 2px solid #4caf50;
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
      border-bottom: 1px solid #4caf50;
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
        <a href="/agent-team-config.html" target="_blank" style="padding: 4px 8px; border-radius: 999px; background: rgba(79,195,247,0.16); color: #b3e5fc; text-decoration: none; font-size: 11px;" title="LLM 来自智能体团队配置">🤖 智能体 LLM</a>
        <span style="color: #888; font-size: 10px;">💡 拖动</span>
        <span id="bridge-llm-status" style="color: #81c784; font-size: 11px;">● AI Ready (Agent)</span>
      </div>
    `;
    
    // 消息区域
    const messagesContainer = document.createElement('div');
    messagesContainer.id = 'bridge-messages';
    messagesContainer.style.cssText = `
      flex: 1 1 auto;
      min-height: 60px;
      max-height: 280px;
      overflow-y: scroll;
      padding: 16px 10px 16px 16px;
      transition: max-height 0.3s ease;
      scrollbar-width: thin;
      scrollbar-color: rgba(79,195,247,0.5) rgba(255,255,255,0.06);
    `;
    
    // 输入区域
    const quickBar = document.createElement('div');
    quickBar.style.cssText = `padding: 8px 12px; display:flex; gap:6px; flex-wrap:wrap; border-top: 1px solid rgba(255,255,255,0.08);`;
    ['任务图','碰撞风险','自由视角','Bridge视角','顶视图','全景','跟踪高风险目标','停止跟踪'].forEach(text => {
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
    input.placeholder = '输入桥楼指令或自然语言问题 (LLM 来自智能体团队)';
    input.disabled = false;
    input.style.cssText = `flex: 1; padding: 8px 12px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; color: #fff; font-size: 13px;`;
    
    const sendBtn = document.createElement('button');
    sendBtn.id = 'bridge-send';
    sendBtn.textContent = '发送';
    sendBtn.style.cssText = 'padding: 8px 16px; background: linear-gradient(135deg, #4fc3f7 0%, #2196f3 100%); border: none; border-radius: 6px; color: #fff; cursor: pointer; font-size: 13px;';
    
    // 语音按钮
    const voiceBtn = document.createElement('button');
    voiceBtn.id = 'bridge-voice';
    voiceBtn.innerHTML = '🎤';
    voiceBtn.title = '按住说话 / 点击切换语音输入';
    voiceBtn.style.cssText = 'width: 36px; height: 36px; background: rgba(79,195,247,0.2); border: 1px solid rgba(79,195,247,0.4); border-radius: 6px; color: #fff; font-size: 18px; cursor: pointer; transition: all 0.3s; flex-shrink: 0; display: flex; align-items: center; justify-content: center;';
    voiceBtn.addEventListener('click', () => this.toggleVoice());
    
    inputArea.appendChild(input);
    inputArea.appendChild(voiceBtn);
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
      this.addMessage('system', '✅ 桥楼就绪 — LLM 来自<a href="/agent-team-config.html" target="_blank" style="color:#4fc3f7">智能体团队</a>默认模型。可输入：自由视角、Bridge视角、跟踪高风险目标、给 build 团队 PM 分配任务…');
    }, 500);
    
    console.log('🌊 Simple Bridge Chat initialized');

    // Inject scrollbar styles for WebKit browsers
    if (!document.getElementById('bridge-chat-scrollbar-style')) {
      const style = document.createElement('style');
      style.id = 'bridge-chat-scrollbar-style';
      style.textContent = `
        #bridge-messages { overflow-y: scroll !important; }
        #bridge-messages::-webkit-scrollbar { width: 8px !important; display: block !important; }
        #bridge-messages::-webkit-scrollbar-track { background: rgba(255,255,255,0.06); border-radius: 4px; }
        #bridge-messages::-webkit-scrollbar-thumb { background: rgba(79,195,247,0.5); border-radius: 4px; min-height: 30px; }
        #bridge-messages::-webkit-scrollbar-thumb:hover { background: rgba(79,195,247,0.7); }
      `;
      document.head.appendChild(style);
    }
  }
  
  toggle() {
    this.isExpanded = !this.isExpanded;
    const messagesContainer = document.getElementById('bridge-messages');
    const inputArea = messagesContainer.nextElementSibling;
    const input = document.getElementById('bridge-input');
    
    if (this.isExpanded) {
      messagesContainer.style.maxHeight = '280px';
      messagesContainer.style.minHeight = '60px';
      messagesContainer.style.padding = '16px 10px 16px 16px';
      inputArea.style.display = 'flex';
      input.disabled = false;
    } else {
      messagesContainer.style.maxHeight = '0';
      messagesContainer.style.minHeight = '0';
      messagesContainer.style.padding = '0 16px';
      inputArea.style.display = 'none';
    }
  }
  
  /**
   * 初始化 Web Speech API 语音识别
   */
  initVoice() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn('⚠️ Web Speech API not supported in this browser');
      return;
    }
    
    this.recognition = new SpeechRecognition();
    this.recognition.lang = 'zh-CN';
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    
    this.recognition.onresult = (event) => {
      const input = document.getElementById('bridge-input');
      if (!input) return;
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      input.value = transcript;
      // 如果是最终结果，自动发送
      if (event.results[event.results.length - 1].isFinal) {
        setTimeout(() => {
          if (input.value.trim()) {
            this.sendMessage();
          }
        }, 300);
      }
    };
    
    this.recognition.onerror = (event) => {
      console.error('🎤 Voice error:', event.error);
      if (event.error === 'not-allowed') {
        this.addMessage('system', '⚠️ 麦克风权限被拒绝。请在浏览器设置中允许麦克风访问。');
      }
      this.stopListening();
    };
    
    this.recognition.onend = () => {
      this.stopListening();
    };
    
    console.log('🎤 Voice input ready');
  }
  
  /**
   * 切换语音输入
   */
  toggleVoice() {
    if (!this.recognition) {
      this.addMessage('system', '⚠️ 当前浏览器不支持语音识别 (Web Speech API)。请使用 Chrome 或 Edge。');
      return;
    }
    
    if (this.isListening) {
      this.recognition.stop();
    } else {
      try {
        this.recognition.start();
        this.startListening();
      } catch (e) {
        // 可能已经在监听
        console.warn('Voice start error:', e);
      }
    }
  }
  
  /**
   * 开始监听 UI 状态
   */
  startListening() {
    this.isListening = true;
    const btn = document.getElementById('bridge-voice');
    if (btn) {
      btn.style.background = 'rgba(244, 67, 54, 0.5)';
      btn.style.borderColor = '#f44336';
      btn.style.animation = 'bridge-pulse 1.5s infinite';
      btn.innerHTML = '🔴';
      btn.title = '正在录音... 点击停止';
    }
    const input = document.getElementById('bridge-input');
    if (input) {
      input.placeholder = '🎤 正在聆听...';
      input.value = '';
    }
    // 添加脉冲动画
    if (!document.getElementById('bridge-pulse-style')) {
      const style = document.createElement('style');
      style.id = 'bridge-pulse-style';
      style.textContent = '@keyframes bridge-pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.15)} }';
      document.head.appendChild(style);
    }
  }
  
  /**
   * 停止监听 UI 状态
   */
  stopListening() {
    this.isListening = false;
    const btn = document.getElementById('bridge-voice');
    if (btn) {
      btn.style.background = 'rgba(79,195,247,0.2)';
      btn.style.borderColor = 'rgba(79,195,247,0.4)';
      btn.style.animation = 'none';
      btn.innerHTML = '🎤';
      btn.title = '按住说话 / 点击切换语音输入';
    }
    const input = document.getElementById('bridge-input');
    if (input && input.placeholder.includes('聆听')) {
      input.placeholder = '输入桥楼指令或自然语言问题 (LLM 来自智能体团队)';
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
    
      if (!text) return;
    
    this.addMessage('user', text);
    input.value = '';
    this.addMessage('assistant', '🤔 正在思考...');
    
    try {
        // ── 🧬 任务派发意图识别 (Darwin Rule: bridge-task-dispatch-v1) ──
        const taskIntent = this.parseTaskIntent(text);
        if (taskIntent) {
          const messagesContainer = document.getElementById('bridge-messages');
          messagesContainer.lastChild.remove();
          const taskResult = await this.dispatchTask(taskIntent);
          this.addMessage('assistant', taskResult);
          return;
        }

        const commandResult = await this.executeOpenBridgeCommand(text);
        // 仅当识别到明确相机/本地控制意图才走模板; 其他一律走后端 LLM (智能体配置)
        if (commandResult?.result?.recognized_intent && commandResult.result.recognized_intent !== 'general_assist') {
          const messagesContainer = document.getElementById('bridge-messages');
          messagesContainer.lastChild.remove();
          this.addMessage('assistant', this.formatCommandResponse(commandResult.result));
          return;
        }

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
  
  // ── 🧬 Darwin Rule: bridge-task-dispatch-v1 (locked, irreversible) ──
  // 桥楼聊天必须能识别"给X团队的Y设置/分配任务"指令并派发到智能体团队
  // POST /api/v1/agent-config/teams/{team_id}/tasks
  parseTaskIntent(text) {
    if (!text) return null;
    // 触发词: 任务/task/设置一个任务/分配/派发/给XX设置
    const taskTrigger = /(任务|task|设置.*任务|分配|派发|给.*?(?:团队|agent|PM|开发|测试|架构))/i;
    if (!taskTrigger.test(text)) return null;
    
    // 团队识别
    let teamId = 'build_system';  // 默认
    if (/build|构建|开发团队/i.test(text)) teamId = 'build_system';
    else if (/exec|运行|执行/i.test(text)) teamId = 'execution_system';
    
    // Agent 识别 (按 build_team.py 中定义)
    let agentId = '';
    if (/PM|项目经理|产品经理|product\s*manager/i.test(text)) agentId = 'build_pm';
    else if (/researcher|研究员|调研/i.test(text)) agentId = 'build_researcher';
    else if (/architect|架构师|架构/i.test(text)) agentId = 'build_architect';
    else if (/developer|开发者|程序员|码农/i.test(text)) agentId = 'build_developer';
    else if (/tester|qa|测试/i.test(text)) agentId = 'build_tester';
    else if (/deployer|devops|部署/i.test(text)) agentId = 'build_deployer';
    else if (/doc|文档/i.test(text)) agentId = 'build_doc_writer';
    
    // 优先级
    let priority = 2;
    if (/紧急|urgent|asap|立即/i.test(text)) priority = 0;
    else if (/高|重要|high/i.test(text)) priority = 1;
    
    // 标题: 取触发词后的内容, 或者整句压缩
    let title = text.replace(/^.*?(?:设置|分配|派发|创建).*?(?:任务|task)[，:：,]?\s*/i, '').trim();
    if (!title || title.length < 5) title = text.slice(0, 80);
    if (title.length > 100) title = title.slice(0, 100) + '...';
    
    return {
      teamId,
      agentId,
      title,
      description: text,  // 原始指令作为描述
      priority,
    };
  }
  
  async dispatchTask(intent) {
    try {
      const url = `/api/v1/agent-config/teams/${intent.teamId}/tasks`;
      const body = {
        title: intent.title,
        description: intent.description,
        agent_id: intent.agentId || '',
        priority: intent.priority,
        dependencies: [],
        metadata: { source: 'bridge_chat', issued_at: new Date().toISOString() },
      };
      const r = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!r.ok) {
        const err = await r.text();
        // 即使后端不可达, 也记录到 Darwin 作为本地任务
        this.recordLocalTask(intent, 'pending-backend');
        return `⚠️ 任务已本地登记 (后端 ${r.status})\n📋 标题: ${intent.title}\n👤 团队: ${intent.teamId} / ${intent.agentId || '自动分配'}\n💡 请前往 <a href="/agent-team-config.html" target="_blank" style="color:#4fc3f7">智能体配置页</a> 查看`;
      }
      const data = await r.json();
      this.recordLocalTask(intent, 'submitted', data.task_id);
      return `✅ 任务已提交至 <b>${intent.teamId}</b>\n👤 执行者: <b>${intent.agentId || '自动分配'}</b>\n📋 ID: <code>${data.task_id}</code>\n🔥 优先级: ${['紧急','高','普通','低'][intent.priority]}\n\n👉 <a href="/agent-team-config.html?view=tasks" target="_blank" style="color:#4fc3f7">查看任务进度</a>`;
    } catch (e) {
      this.recordLocalTask(intent, 'error');
      return `❌ 任务派发失败: ${e.message}\n（已记录到本地 Darwin 队列）`;
    }
  }
  
  recordLocalTask(intent, status, backendId = null) {
    try {
      const KEY = 'poseidonx.bridge.dispatched_tasks';
      const list = JSON.parse(localStorage.getItem(KEY) || '[]');
      list.push({
        ts: new Date().toISOString(),
        teamId: intent.teamId,
        agentId: intent.agentId,
        title: intent.title,
        priority: intent.priority,
        status,
        backendId,
      });
      localStorage.setItem(KEY, JSON.stringify(list.slice(-50)));
      // 写入 Darwin 演化日志
      if (window.Darwin && window.Darwin.record) {
        window.Darwin.record({
          id: `bridge-task-${Date.now()}`,
          title: `桥楼派发: ${intent.title.slice(0, 40)}`,
          category: 'ai',
          description: `Team=${intent.teamId} Agent=${intent.agentId || 'auto'} | ${status}`,
          fitness: status === 'submitted' ? 'pass' : 'pending',
        });
      }
    } catch (e) {}
  }
  
  async callLLM(userMessage, channelContext = '') {
    // 🧬 Darwin rule: bridge-uses-agent-llm-v1
    // 优先走后端 /api/v1/bridge-chat/send (使用智能体页配置的 LLM: default model of build/execution team)
    // 只有当后端不可达时才回退到 localStorage 的 poseidon_config
    try {
      const sessionId = this._sessionId || (this._sessionId = 'twin-' + Date.now().toString(36));
      const agentId = this.config.bridgeAgentId || 'ship_navigator';
      const message = channelContext ? `${userMessage}\n\n[上下文]\n${channelContext}` : userMessage;
      const r = await fetch('/api/v1/bridge-chat/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, session_id: sessionId, agent_id: agentId }),
      });
      if (r.ok) {
        const data = await r.json();
        if (data && data.reply) {
          const src = data.source || 'agent-llm';
          const tag = data.task_id ? ` · 任务 <code>${data.task_id}</code>` : '';
          return `${data.reply}\n\n<span style="font-size:10px;color:#78909c">⚙️ ${src}${tag}</span>`;
        }
      } else {
        console.warn('[BridgeChat] backend /bridge-chat/send returned', r.status);
      }
    } catch (e) {
      console.warn('[BridgeChat] backend /bridge-chat/send unreachable, falling back to direct API:', e.message);
    }
    
    // ── Fallback: 直接调用 localStorage 配置的外部 LLM ──
    if (!this.config.apiKey) {
      throw new Error('智能体后端不可达, 且本地未配置 LLM API Key. 请在智能体页 → LLM 配置或 poseidon-config.html 中配置。');
    }
    const endpoint = this.config.apiEndpoint || 'https://api.minimax.chat/v1';
    const model = this.config.model || 'MiniMax-M2.5';
    
    const systemContext = `${this.config.systemPrompt || '你是 Poseidon-X 船舶智能助手。'}\n\n当前系统上下文：${JSON.stringify(this.shipContext)}${channelContext}`;
    const messages = [
      { role: 'system', content: systemContext },
      { role: 'user', content: userMessage }
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
    return data.choices[0].message.content + '\n\n<span style="font-size:10px;color:#ffb74d">⚙️ fallback: local API</span>';
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

  async persistBridgeActionFeedback(action, outcome) {
    try {
      await fetch('/api/v1/ai-native/decision/feedback/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action,
          outcome,
          confirmed_by: 'bridge_chat',
        }),
      });
    } catch (error) {
      console.warn('Failed to persist bridge action feedback:', error);
    }
  }

  findPriorityAisTarget() {
    const targets = Array.isArray(window.__digitalTwinAisTargets) ? window.__digitalTwinAisTargets : [];
    return targets.find((target) => ['high', 'medium'].includes(String(target.risk_level || '').toLowerCase())) || targets[0] || null;
  }

  async executeLocalBridgeCommand(command) {
    const text = String(command || '').trim().toLowerCase();
    const twin = window.DigitalTwin;
    if (!text || !twin) {
      return null;
    }

    const refreshUi = async () => {
      if (typeof window.refreshDigitalTwinBridgeUi === 'function') {
        await window.refreshDigitalTwinBridgeUi();
      }
    };

    if ((text.includes('自由视角') || text.includes('free view') || text.includes('free camera')) && twin.setCameraMode) {
      twin.setCameraMode('free');
      await this.persistBridgeActionFeedback('camera:free', 'bridge_chat_local_control');
      await refreshUi();
      return {
        result: {
          recognized_intent: 'camera_control',
          execution_mode: 'local_bridge_control',
          summary: '已切换到自由视角，相机不会被桥楼逻辑自动接管。',
          operator_action: '可手动拖拽观察，如需回到舰桥输入“Bridge视角”。',
          focus_items: [{ label: 'Camera Mode', value: 'FREE' }],
        },
      };
    }

    if ((text.includes('bridge视角') || text.includes('舰桥视角') || text.includes('桥楼视角')) && twin.setCameraMode) {
      twin.setCameraMode('bridge');
      await this.persistBridgeActionFeedback('camera:bridge', 'bridge_chat_local_control');
      await refreshUi();
      return {
        result: {
          recognized_intent: 'camera_control',
          execution_mode: 'local_bridge_control',
          summary: '已切换到 Bridge 视角。',
          operator_action: '继续监控目标列表，必要时可输入“跟踪高风险目标”。',
          focus_items: [{ label: 'Camera Mode', value: 'BRIDGE' }],
        },
      };
    }


    // Extended camera view commands (top, bow, stern, port, starboard, overview)
    const viewMap = {
      'top view': 'top', '顶视图': 'top', '俯视图': 'top', '鸟瞰': 'top',
      'bow view': 'bow', '船首视角': 'bow', '前视图': 'bow',
      'stern view': 'stern', '船尾视角': 'stern', '后视图': 'stern',
      'port view': 'port', '左舷视角': 'port', '左视图': 'port',
      'starboard view': 'starboard', '右舷视角': 'starboard', '右视图': 'starboard',
      'overview': 'overview', '全局视图': 'overview', '总览': 'overview', '全景': 'overview',
    };
    const viewLabels = {
      top: 'TOP (俯视)', bow: 'BOW (船首)', stern: 'STERN (船尾)',
      port: 'PORT (左舷)', starboard: 'STARBOARD (右舷)', overview: 'OVERVIEW (全景)',
    };
    for (const [keyword, mode] of Object.entries(viewMap)) {
      if (text.includes(keyword) && twin.setCameraMode) {
        twin.setCameraMode(mode);
        await this.persistBridgeActionFeedback('camera:' + mode, 'bridge_chat_local_control');
        await refreshUi();
        return {
          result: {
            recognized_intent: 'camera_control',
            execution_mode: 'local_bridge_control',
            summary: '已切换到 ' + (viewLabels[mode] || mode) + ' 视角。',
            operator_action: '可输入其他视角名称切换: top view / bow view / stern view / port view / starboard view / overview / Bridge视角。',
            focus_items: [{ label: 'Camera Mode', value: viewLabels[mode] || mode.toUpperCase() }],
          },
        };
      }
    }
    if ((text.includes('停止跟踪') || text.includes('stop tracking') || text.includes('取消跟踪')) && twin.stopTrackingTarget) {
      twin.stopTrackingTarget();
      await this.persistBridgeActionFeedback('camera:stop_track', 'bridge_chat_local_control');
      await refreshUi();
      return {
        result: {
          recognized_intent: 'camera_control',
          execution_mode: 'local_bridge_control',
          summary: '已停止目标跟踪并返回 Bridge 视角。',
          operator_action: '如需重新锁定目标，可点击 AIS 列表或输入“跟踪高风险目标”。',
          focus_items: [{ label: 'Camera Mode', value: 'BRIDGE' }],
        },
      };
    }

    if ((text.includes('跟踪') || text.includes('track')) && twin.setSelectedTarget) {
      const target = this.findPriorityAisTarget();
      if (!target) {
        return {
          result: {
            recognized_intent: 'camera_control',
            execution_mode: 'local_bridge_control',
            summary: '当前没有可跟踪的 AIS 目标。',
            operator_action: '等待 AIS 数据刷新后再尝试跟踪。',
            focus_items: [],
          },
        };
      }

      twin.setSelectedTarget(target, { cameraMode: 'target-track', source: 'bridge-chat' });
      await this.persistBridgeActionFeedback(`camera:track:${target.mmsi || target.id || 'target'}`, 'bridge_chat_local_control');
      await refreshUi();
      return {
        result: {
          recognized_intent: 'camera_control',
          execution_mode: 'local_bridge_control',
          summary: `已开始跟踪目标 ${target.vessel_type || target.name || target.mmsi || 'UNKNOWN'}。`,
          operator_action: '继续观察风险变化，必要时输入“停止跟踪”回到 Bridge 视角。',
          focus_items: [
            { label: 'Camera Mode', value: 'TRACK' },
            { label: 'Target', value: target.vessel_type || target.name || target.mmsi || 'UNKNOWN' },
            { label: 'Risk', value: String(target.risk_level || '--').toUpperCase() },
          ],
        },
      };
    }

    return null;
  }

    async executeOpenBridgeCommand(command) {
      const localResult = await this.executeLocalBridgeCommand(command);
      if (localResult) {
        return localResult;
      }

      const response = await fetch('/api/v1/ai-native/openbridge/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command, source: 'bridge_chat' })
      });
      if (!response.ok) {
        throw new Error(`OpenBridge command failed: ${response.status}`);
      }
      return await response.json();
    }

    formatCommandResponse(result) {
      const focus = Array.isArray(result.focus_items) ? result.focus_items.slice(0, 3) : [];
      const focusLines = focus.map((item) => {
        if (item.zone) {
          return `- ${item.zone}: ${item.microstrain} µε`;
        }
        if (item.label && Object.prototype.hasOwnProperty.call(item, 'value')) {
          return `- ${item.label}: ${item.value ?? '--'}`;
        }
        if (item.title) {
          return `- ${item.title}`;
        }
        if (item.label && item.status) {
          return `- ${item.label}: ${item.status}`;
        }
        if (item.id) {
          return `- ${item.id}`;
        }
        return `- ${JSON.stringify(item)}`;
      }).join('\n');

      return [
        `意图: ${result.recognized_intent}`,
        `模式: ${result.execution_mode}`,
        `摘要: ${result.summary}`,
        `操作建议: ${result.operator_action}`,
        focusLines ? `重点:\n${focusLines}` : ''
      ].filter(Boolean).join('\n');
    }
  
  updateShipContext(context) {
    this.shipContext = { ...this.shipContext, ...context };
  }

  async initializeShipContext() {
    await this.updateShipContextFromAPI();
  }

  async updateShipContextFromAPI() {
    try {
      const [sensorsResp, channelsResp, engineResp, dashboardResp, missionResp, rcsResp, shmResp] = await Promise.all([
        fetch('/api/v1/sensors'),
        fetch('/api/v1/channels'),
        fetch('/api/v1/engine/status'),
        fetch('/api/v1/dashboard'),
        fetch('/api/v1/ai-native/cps/mission-brief'),
        fetch('/api/v1/ai-native/rcs/status'),
        fetch('/api/v1/ai-native/shm/status')
      ]);
      const sensors = await sensorsResp.json();
      const channels = await channelsResp.json();
      const engine = await engineResp.json();
      const dashboard = await dashboardResp.json();
      const missionBrief = await missionResp.json();
      const rcs = await rcsResp.json();
      const shm = await shmResp.json();
      this.updateShipContext({
        sensors: sensors.sensors || [],
        channels: channels.channels || [],
        engine,
        dashboard,
        missionBrief,
        rcs: rcs.result || {},
        shm: shm.result || {},
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
    // CCTV 监控模式下不创建桥楼聊天面板
    if (new URLSearchParams(window.location.search).has('cam')) {
      console.log('🚫 Bridge Chat skipped (cam-mode)');
      return;
    }
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
