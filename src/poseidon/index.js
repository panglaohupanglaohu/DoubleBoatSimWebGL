/**
 * Poseidon-X 系统导出文件
 * 
 * 统一导出所有组件，方便使用
 */

// ============================================
// Layer 1: 统一交互界面
// ============================================
export { BridgeChat } from './layer1-interface/BridgeChat.js';
export { DigitalTwinMap } from './layer1-interface/DigitalTwinMap.js';
export { ContextWindow } from './layer1-interface/ContextWindow.js';

// ============================================
// Layer 2: AI Crew 智能体
// ============================================
export { AgentBase } from './layer2-agents/AgentBase.js';
export { NavigatorAgent } from './layer2-agents/NavigatorAgent.js';
export { EngineerAgent } from './layer2-agents/EngineerAgent.js';
export { StewardAgent } from './layer2-agents/StewardAgent.js';
export { SafetyAgent } from './layer2-agents/SafetyAgent.js';
export { AgentOrchestrator } from './layer2-agents/AgentOrchestrator.js';

// ============================================
// Layer 3: Intelligence Foundry 开发平台
// ============================================
export { VibeGenerator } from './layer3-platform/VibeGenerator.js';
export { SimulationValidator } from './layer3-platform/SimulationValidator.js';
export { LLMJudge } from './layer3-platform/LLMJudge.js';

// ============================================
// 主系统
// ============================================
export { PoseidonX, createPoseidonX } from './PoseidonX.js';

// ============================================
// 演示程序
// ============================================
export {
  demo1_BasicUsage,
  demo2_ExecuteTasks,
  demo3_ParallelTasks,
  demo4_UpdateContext,
  demo5_DigitalTwin,
  demo6_GenerateAgent,
  demo7_ValidateAgent,
  demo8_EvaluateAgent,
  demo9_SystemEvents,
  runFullDemo,
  runDevDemo
} from './demo.js';
