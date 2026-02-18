/**
 * Safety Agent 测试用例
 * 测试 Safety Agent 是否能正确调用 LLM 进行分析
 */

// 模拟浏览器 localStorage
global.localStorage = {
  getItem: () => null,
  setItem: () => {},
  removeItem: () => {}
};

import { SafetyAgent } from '../src/poseidon/layer2-agents/SafetyAgent.js';

const API_KEY = 'sk-cp-UaXXGY2aCId_sf_-9WLCbNG6PQ_ziAia8t2QbGVXgFWvSzwugqpkufY8ozB3LWPgcGeTDhKL6QfFXiE49TzA5X6L2s-yIS4HEUoBO_nh1aP_BwKCas67ZVs';

async function testSafetyAgentLLM() {
  console.log('\n========== 测试 Safety Agent LLM 调用 ==========');
  
  // 创建 Safety Agent
  const safetyAgent = new SafetyAgent({
    llmProvider: 'minimax',
    apiKey: API_KEY,
    model: 'MiniMax-M2.5'
  });
  
  console.log('Safety Agent 已创建:', {
    name: safetyAgent.name,
    provider: safetyAgent.llmConfig?.provider,
    model: safetyAgent.llmConfig?.model
  });
  
  // 测试安全态势评估
  console.log('\n测试安全态势评估...');
  try {
    const result = await safetyAgent.execute('安全分析', {});
    
    console.log('\n✅ Safety Agent 执行成功');
    console.log('类型:', result.type);
    console.log('响应:', result.response?.substring(0, 200) + '...');
    
    // 检查是否包含 LLM 分析
    if (result.llmAnalysis && result.llmAnalysis.length > 10) {
      console.log('\n✅ LLM 分析已集成');
      return true;
    } else {
      console.log('\n⚠️ LLM 分析内容较少或为空');
      return false;
    }
  } catch (error) {
    console.error('\n❌ Safety Agent 执行失败:', error.message);
    return false;
  }
}

async function testSafetyAgentTools() {
  console.log('\n========== 测试 Safety Agent 工具 ==========');
  
  const safetyAgent = new SafetyAgent({
    llmProvider: 'minimax',
    apiKey: API_KEY,
    model: 'MiniMax-M2.5'
  });
  
  // 测试工具注册
  const tools = Array.from(safetyAgent.tools.keys());
  console.log('已注册工具:', tools);
  
  const hasRequiredTools = [
    'analyzeVideoFrame',
    'triggerAlert',
    'generateEvacuationRoute',
    'assessSafetySituation'
  ].every(t => tools.includes(t));
  
  if (hasRequiredTools) {
    console.log('✅ 必需工具已注册');
    return true;
  } else {
    console.log('❌ 部分工具缺失');
    return false;
  }
}

async function runAllTests() {
  console.log('🚀 开始运行 Safety Agent 测试...\n');
  
  const results = {
    tools: false,
    llm: false
  };
  
  results.tools = await testSafetyAgentTools();
  results.llm = await testSafetyAgentLLM();
  
  console.log('\n========== 测试结果 ==========');
  console.log('工具注册:', results.tools ? '✅ 通过' : '❌ 失败');
  console.log('LLM 调用:', results.llm ? '✅ 通过' : '❌ 失败');
  
  const allPassed = Object.values(results).every(r => r);
  console.log('\n总体结果:', allPassed ? '✅ 全部通过' : '❌ 存在失败');
  
  return allPassed;
}

// 运行测试
runAllTests().then(success => {
  process.exit(success ? 0 : 1);
}).catch(error => {
  console.error('测试运行失败:', error);
  process.exit(1);
});
