/**
 * Poseidon-X - 主系统入口
 * 
 * Software 3.0 Edition
 * 
 * 这是整个 Poseidon-X 系统的统一入口，
 * 集成了 Layer 1、Layer 2 和 Layer 3 的所有组件。
 */

// Layer 1: 交互界面
import { BridgeChat } from './layer1-interface/BridgeChat.js';
import { DigitalTwinMap } from './layer1-interface/DigitalTwinMap.js';
import { ContextWindow } from './layer1-interface/ContextWindow.js';

// Layer 2: 智能体
import { NavigatorAgent } from './layer2-agents/NavigatorAgent.js';
import { EngineerAgent } from './layer2-agents/EngineerAgent.js';
import { StewardAgent } from './layer2-agents/StewardAgent.js';
import { SafetyAgent } from './layer2-agents/SafetyAgent.js';
import { AgentOrchestrator } from './layer2-agents/AgentOrchestrator.js';

// Layer 3: 开发平台
import { VibeGenerator } from './layer3-platform/VibeGenerator.js';
import { SimulationValidator } from './layer3-platform/SimulationValidator.js';
import { LLMJudge } from './layer3-platform/LLMJudge.js';

import { EventEmitter } from '../utils/EventEmitter.js';

/**
 * Poseidon-X 主系统类
 */
export class PoseidonX extends EventEmitter {
  constructor(scene, camera, config = {}) {
    super();
    
    this.scene = scene;
    this.camera = camera;
    
    this.config = {
      enableBridgeChat: config.enableBridgeChat !== false,
      enableDigitalTwin: config.enableDigitalTwin !== false,
      enableVoice: config.enableVoice || false,
      llmProvider: config.llmProvider || 'openai',
      model: config.model || 'gpt-4',
      ...config
    };
    
    // 系统状态
    this.status = 'initializing';
    this.initialized = false;
    
    // Layer 1 组件
    this.bridgeChat = null;
    this.digitalTwinMap = null;
    this.contextWindow = null;
    
    // Layer 2 组件
    this.agents = {
      navigator: null,
      engineer: null,
      steward: null,
      safety: null
    };
    this.orchestrator = null;
    
    // Layer 3 组件（开发模式）
    this.devMode = config.devMode || false;
    this.vibeGenerator = null;
    this.simulationValidator = null;
    this.llmJudge = null;
    
    // 船舶上下文（全局状态）
    this.shipContext = {
      position: { lat: 0, lon: 0, heading: 0, speed: 0 },
      sensors: new Map(),
      environment: {},
      equipment: {},
      crew: {},
      alerts: []
    };
    
    console.log('🌊 Poseidon-X System initializing...');
  }
  
  /**
   * 初始化系统
   */
  async initialize() {
    console.log('🚀 Starting Poseidon-X initialization...');
    
    try {
      // 1. 初始化 Layer 1（交互界面）
      await this._initializeLayer1();
      
      // 2. 初始化 Layer 2（智能体）
      await this._initializeLayer2();
      
      // 3. 初始化 Layer 3（开发平台，仅开发模式）
      if (this.devMode) {
        await this._initializeLayer3();
      }
      
      // 4. 连接各层
      this._connectLayers();
      
      this.status = 'ready';
      this.initialized = true;
      
      console.log('✅ Poseidon-X initialized successfully!');
      console.log(`   Mode: ${this.devMode ? 'Development' : 'Production'}`);
      console.log(`   Agents: ${Object.keys(this.agents).length}`);
      
      // 触发事件
      this.emit('system:ready', {
        agents: Object.keys(this.agents),
        devMode: this.devMode
      });
      
      // 显示欢迎消息
      if (this.bridgeChat) {
        this.bridgeChat._addMessage('system', 
          '🌊 Poseidon-X 智能船舶系统已就绪。\n' +
          `✅ ${Object.keys(this.agents).length} 个智能体已激活\n` +
          `📡 全船传感器数据实时监控中\n\n` +
          '您可以通过自然语言与我对话，我会协调各个专业智能体为您服务。'
        );
      }
      
      return this;
      
    } catch (error) {
      this.status = 'error';
      console.error('❌ Poseidon-X initialization failed:', error);
      throw error;
    }
  }
  
  /**
   * 初始化 Layer 1
   * @private
   */
  async _initializeLayer1() {
    console.log('📱 Initializing Layer 1: User Interface...');
    
    // Context Window（上下文窗口）
    this.contextWindow = new ContextWindow({
      maxTokens: 128000,
      compressionThreshold: 0.8
    });
    
    // 设置系统 Vibe
    this.contextWindow.setSystemVibe(`你是 Poseidon-X 智能船舶系统的核心 AI。
你的职责是协调船上的各个专业智能体，为船长和船员提供智能决策支持。`);
    
    // Digital Twin Map（数字孪生海图）
    if (this.config.enableDigitalTwin) {
      this.digitalTwinMap = new DigitalTwinMap(this.scene, this.camera, {
        showAIS: true,
        showRoute: true
      });
      
      console.log('  ✅ Digital Twin Map initialized');
    }
    
    // Bridge Chat（舰桥对话中心）
    if (this.config.enableBridgeChat) {
      this.bridgeChat = new BridgeChat({
        llmProvider: this.config.llmProvider,
        model: this.config.model,
        voiceEnabled: this.config.enableVoice,
        vibe: `你是 Poseidon-X 的核心 AI 助手，协调全船的智能体团队。`
      });
      
      // 监听消息事件
      this.bridgeChat.on('message:sent', (data) => {
        this.emit('chat:message', data);
      });
      
      console.log('  ✅ Bridge Chat initialized');
    }
    
    console.log('✅ Layer 1 initialized');
  }
  
  /**
   * 初始化 Layer 2
   * @private
   */
  async _initializeLayer2() {
    console.log('🤖 Initializing Layer 2: AI Crew...');
    
    // 创建 Agent Orchestrator
    this.orchestrator = new AgentOrchestrator({
      maxParallelAgents: 4,
      timeout: 30000
    });
    
    // 创建各个专业智能体
    this.agents.navigator = new NavigatorAgent({
      llmProvider: this.config.llmProvider,
      model: this.config.model
    });
    
    this.agents.engineer = new EngineerAgent({
      llmProvider: this.config.llmProvider,
      model: this.config.model
    });
    
    this.agents.steward = new StewardAgent({
      llmProvider: this.config.llmProvider,
      model: this.config.model
    });
    
    this.agents.safety = new SafetyAgent({
      llmProvider: this.config.llmProvider,
      model: this.config.model
    });
    
    // 注册到 Orchestrator
    this.orchestrator.registerAgent('navigator', this.agents.navigator);
    this.orchestrator.registerAgent('engineer', this.agents.engineer);
    this.orchestrator.registerAgent('steward', this.agents.steward);
    this.orchestrator.registerAgent('safety', this.agents.safety);
    
    // 监听 Agent 事件
    this.orchestrator.on('task:completed', (data) => {
      console.log(`✅ Task completed by ${data.agent}: ${data.task}`);
      this.emit('agent:task_completed', data);
    });
    
    console.log('✅ Layer 2 initialized');
    console.log(`  ⚓ Navigator Agent ready`);
    console.log(`  ⚙️ Engineer Agent ready`);
    console.log(`  🏠 Steward Agent ready`);
    console.log(`  🛡️ Safety Agent ready`);
  }
  
  /**
   * 初始化 Layer 3（开发模式）
   * @private
   */
  async _initializeLayer3() {
    console.log('🧬 Initializing Layer 3: Intelligence Foundry (Dev Mode)...');
    
    // Vibe Generator
    this.vibeGenerator = new VibeGenerator({
      llmProvider: this.config.llmProvider,
      model: this.config.model,
      outputLanguage: 'javascript'
    });
    
    // Simulation Validator
    this.simulationValidator = new SimulationValidator({
      scenarioCount: 100,
      passThreshold: 0.85
    });
    
    // LLM Judge
    this.llmJudge = new LLMJudge({
      llmProvider: this.config.llmProvider,
      model: this.config.model,
      strictness: 0.8
    });
    
    console.log('✅ Layer 3 initialized (Development Platform)');
  }
  
  /**
   * 连接各层
   * @private
   */
  _connectLayers() {
    // 连接 Bridge Chat 和 Orchestrator
    if (this.bridgeChat && this.orchestrator) {
      // 注册 Agents 到 Bridge Chat
      Object.entries(this.agents).forEach(([name, agent]) => {
        this.bridgeChat.registerAgent(name, agent);
      });
    }
    
    // 连接 Digital Twin Map 和 Agents
    if (this.digitalTwinMap) {
      // Navigator Agent 可以在地图上高亮目标
      this.agents.navigator.on('collision:risk', (data) => {
        this.digitalTwinMap.highlight(data.target, '碰撞风险');
      });
    }
    
    // 连接 Context Window 和 Bridge Chat
    if (this.contextWindow && this.bridgeChat) {
      // Context Window 更新时通知 Bridge Chat
      this.contextWindow.on('tokens:updated', (data) => {
        // 可以在 UI 上显示 token 使用情况
      });
    }
  }
  
  /**
   * 执行任务（用户输入）
   * @param {string} task - 任务描述
   * @returns {Promise<Object>} - 执行结果
   */
  async executeTask(task) {
    if (!this.initialized) {
      throw new Error('System not initialized. Call initialize() first.');
    }
    
    console.log(`🎯 Executing task: ${task}`);
    
    // 使用 Orchestrator 智能路由
    const result = await this.orchestrator.executeTask(task, this.shipContext);
    
    return result;
  }
  
  /**
   * 更新船舶状态
   * @param {Object} update - 状态更新
   */
  updateShipContext(update) {
    this.shipContext = {
      ...this.shipContext,
      ...update
    };
    
    // 更新 Context Window
    if (this.contextWindow) {
      Object.entries(update).forEach(([key, value]) => {
        if (key === 'sensors' && value instanceof Map) {
          // 更新传感器数据
          for (const [sensorId, sensorValue] of value.entries()) {
            this.contextWindow.addSensorData(sensorId, sensorValue, 'medium');
          }
        }
      });
    }
    
    // 通知 Bridge Chat
    if (this.bridgeChat) {
      this.bridgeChat.updateShipContext(update);
    }
    
    // 触发事件
    this.emit('context:updated', this.shipContext);
  }
  
  /**
   * 生成新的 Agent（开发模式）
   * @param {string} vibe - Agent 需求描述
   */
  async generateAgent(vibe) {
    if (!this.devMode || !this.vibeGenerator) {
      throw new Error('Agent generation only available in dev mode');
    }
    
    const generation = await this.vibeGenerator.generateAgent(vibe);
    
    console.log(`🧬 Generated new agent from vibe:`, generation.parsed.agentName);
    
    return generation;
  }
  
  /**
   * 验证 Agent（开发模式）
   * @param {Object} agent - Agent 实例
   * @param {Array} scenarioTypes - 测试场景类型
   */
  async validateAgent(agent, scenarioTypes = ['all']) {
    if (!this.devMode || !this.simulationValidator) {
      throw new Error('Agent validation only available in dev mode');
    }
    
    const report = await this.simulationValidator.validateAgent(agent, scenarioTypes);
    
    console.log(`🔬 Validation report:`, report);
    
    return report;
  }
  
  /**
   * 评估 Agent 执行（开发模式）
   * @param {Object} execution - Agent 执行记录
   */
  async evaluateExecution(execution) {
    if (!this.devMode || !this.llmJudge) {
      throw new Error('Agent evaluation only available in dev mode');
    }
    
    const evaluation = await this.llmJudge.evaluate(execution, this.shipContext);
    
    console.log(`⚖️ Evaluation:`, evaluation);
    
    return evaluation;
  }
  
  /**
   * 获取系统状态
   */
  getSystemStatus() {
    return {
      status: this.status,
      initialized: this.initialized,
      devMode: this.devMode,
      layer1: {
        bridgeChat: !!this.bridgeChat,
        digitalTwinMap: !!this.digitalTwinMap,
        contextWindow: this.contextWindow?.getStats()
      },
      layer2: {
        agents: Object.keys(this.agents),
        orchestrator: this.orchestrator?.getStats()
      },
      layer3: this.devMode ? {
        vibeGenerator: !!this.vibeGenerator,
        simulationValidator: !!this.simulationValidator,
        llmJudge: this.llmJudge?.getStats()
      } : null,
      shipContext: {
        position: this.shipContext.position,
        sensors: this.shipContext.sensors.size,
        alerts: this.shipContext.alerts.length
      }
    };
  }
  
  /**
   * 销毁系统
   */
  dispose() {
    console.log('🗑️ Disposing Poseidon-X system...');
    
    // 销毁 Layer 1
    if (this.bridgeChat) this.bridgeChat.dispose();
    if (this.digitalTwinMap) this.digitalTwinMap.dispose();
    if (this.contextWindow) this.contextWindow.dispose();
    
    // 销毁 Layer 2
    Object.values(this.agents).forEach(agent => {
      if (agent && agent.dispose) agent.dispose();
    });
    
    if (this.orchestrator) this.orchestrator.dispose();
    
    this.removeAllListeners();
    
    console.log('✅ Poseidon-X system disposed');
  }
}

/**
 * 快速启动函数（便捷方法）
 */
export async function createPoseidonX(scene, camera, config = {}) {
  const system = new PoseidonX(scene, camera, config);
  await system.initialize();
  return system;
}
