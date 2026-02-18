/**
 * LLMClient 测试用例
 * 测试不同 LLM 提供商的配置和调用
 */

import { LLMClient } from '../src/poseidon/layer1-interface/LLMClient.js';

const API_KEY = 'sk-cp-UaXXGY2aCId_sf_-9WLCbNG6PQ_ziAia8t2QbGVXgFWvSzwugqpkufY8ozB3LWPgcGeTDhKL6QfFXiE49TzA5X6L2s-yIS4HEUoBO_nh1aP_BwKCas67ZVs';

async function testMiniMaxProvider() {
  console.log('\n========== 测试 MiniMax Provider ==========');
  
  const client = new LLMClient({
    provider: 'minimax',
    apiKey: API_KEY,
    model: 'MiniMax-M2.5'
  });
  
  console.log('配置:', {
    provider: client.config.provider,
    endpoint: client.config.apiEndpoint,
    model: client.config.model
  });
  
  // 测试聊天
  const messages = [
    { role: 'user', content: '你好，请用一句话介绍自己' }
  ];
  
  try {
    const response = await client.chat(messages);
    console.log('✅ MiniMax 聊天成功:', response.content?.substring(0, 100) + '...');
    return true;
  } catch (error) {
    console.error('❌ MiniMax 聊天失败:', error.message);
    return false;
  }
}

async function testDeepSeekProvider() {
  console.log('\n========== 测试 DeepSeek Provider ==========');
  
  // DeepSeek 需要有效的 API Key，这里只测试配置
  const client = new LLMClient({
    provider: 'deepseek',
    apiKey: 'test-key',
    model: 'deepseek-chat'
  });
  
  console.log('配置:', {
    provider: client.config.provider,
    endpoint: client.config.apiEndpoint,
    model: client.config.model
  });
  
  // 验证端点
  const expectedEndpoint = 'https://api.deepseek.com/v1';
  if (client.config.apiEndpoint === expectedEndpoint) {
    console.log('✅ DeepSeek 端点配置正确');
    return true;
  } else {
    console.error('❌ DeepSeek 端点配置错误:', client.config.apiEndpoint);
    return false;
  }
}

async function testOpenAIProvider() {
  console.log('\n========== 测试 OpenAI Provider ==========');
  
  const client = new LLMClient({
    provider: 'openai',
    apiKey: 'test-key',
    model: 'gpt-4'
  });
  
  console.log('配置:', {
    provider: client.config.provider,
    endpoint: client.config.apiEndpoint,
    model: client.config.model
  });
  
  const expectedEndpoint = 'https://api.openai.com/v1';
  if (client.config.apiEndpoint === expectedEndpoint) {
    console.log('✅ OpenAI 端点配置正确');
    return true;
  } else {
    console.error('❌ OpenAI 端点配置错误:', client.config.apiEndpoint);
    return false;
  }
}

async function testDefaultModel() {
  console.log('\n========== 测试默认模型 ==========');
  
  // MiniMax 默认模型
  const minimaxClient = new LLMClient({
    provider: 'minimax',
    apiKey: API_KEY
  });
  
  console.log('MiniMax 默认模型:', minimaxClient.config.model);
  
  if (minimaxClient.config.model === 'MiniMax-M2.5') {
    console.log('✅ MiniMax 默认模型正确');
  } else {
    console.error('❌ MiniMax 默认模型错误:', minimaxClient.config.model);
    return false;
  }
  
  return true;
}

async function runAllTests() {
  console.log('🚀 开始运行 LLMClient 测试...\n');
  
  const results = {
    minimax: false,
    deepseek: false,
    openai: false,
    defaultModel: false
  };
  
  results.minimax = await testMiniMaxProvider();
  results.deepseek = await testDeepSeekProvider();
  results.openai = await testOpenAIProvider();
  results.defaultModel = await testDefaultModel();
  
  console.log('\n========== 测试结果 ==========');
  console.log('MiniMax:', results.minimax ? '✅ 通过' : '❌ 失败');
  console.log('DeepSeek:', results.deepseek ? '✅ 通过' : '❌ 失败');
  console.log('OpenAI:', results.openai ? '✅ 通过' : '❌ 失败');
  console.log('默认模型:', results.defaultModel ? '✅ 通过' : '❌ 失败');
  
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
