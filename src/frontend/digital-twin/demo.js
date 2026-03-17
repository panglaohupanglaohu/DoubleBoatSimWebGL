/**
 * Poseidon-X 演示程序
 * 
 * 展示如何使用 Poseidon-X 系统
 */

import { createPoseidonX } from './PoseidonX.js';

/**
 * 演示 1: 基础使用
 */
export async function demo1_BasicUsage(scene, camera) {
  console.log('\n=== Demo 1: Basic Usage ===\n');
  
  // 创建并初始化 Poseidon-X 系统
  const poseidon = await createPoseidonX(scene, camera, {
    enableBridgeChat: true,
    enableDigitalTwin: true,
    enableVoice: false,
    llmProvider: 'openai',
    model: 'gpt-4'
  });
  
  console.log('✅ Poseidon-X system created');
  
  // 查询系统状态
  const status = poseidon.getSystemStatus();
  console.log('📊 System status:', status);
  
  return poseidon;
}

/**
 * 演示 2: 执行任务
 */
export async function demo2_ExecuteTasks(poseidon) {
  console.log('\n=== Demo 2: Execute Tasks ===\n');
  
  // 任务 1: 查询碰撞风险
  console.log('🚢 Task 1: Check collision risk');
  const result1 = await poseidon.executeTask(
    "右舷那艘集装箱船有碰撞风险吗？"
  );
  console.log('Result:', result1);
  
  // 任务 2: 检查主机状态
  console.log('\n⚙️ Task 2: Check main engine');
  const result2 = await poseidon.executeTask(
    "主机排温正常吗？"
  );
  console.log('Result:', result2);
  
  // 任务 3: 检查库存
  console.log('\n📦 Task 3: Check inventory');
  const result3 = await poseidon.executeTask(
    "淡水库存够用吗？"
  );
  console.log('Result:', result3);
  
  // 任务 4: 安全态势评估
  console.log('\n🛡️ Task 4: Safety assessment');
  const result4 = await poseidon.executeTask(
    "过去24小时的安全态势如何？"
  );
  console.log('Result:', result4);
}

/**
 * 演示 3: 并行任务
 */
export async function demo3_ParallelTasks(poseidon) {
  console.log('\n=== Demo 3: Parallel Tasks ===\n');
  
  const tasks = [
    "检查主机状态",
    "评估碰撞风险",
    "检查库存",
    "评估安全态势"
  ];
  
  console.log(`⚡ Executing ${tasks.length} tasks in parallel...`);
  
  const result = await poseidon.orchestrator.executeParallel(
    tasks,
    poseidon.shipContext
  );
  
  console.log(`✅ Completed: ${result.successful}/${result.total}`);
  console.log(`❌ Failed: ${result.failed}`);
  
  return result;
}

/**
 * 演示 4: 更新船舶状态
 */
export async function demo4_UpdateContext(poseidon) {
  console.log('\n=== Demo 4: Update Ship Context ===\n');
  
  // 模拟传感器数据更新
  const sensorData = new Map([
    ['MainEngine.ExhaustTemp.Cyl1', 375],
    ['MainEngine.ExhaustTemp.Cyl2', 380],
    ['MainEngine.RPM', 100],
    ['GPS.Latitude', 31.2304],
    ['GPS.Longitude', 121.4737],
    ['Weather.WindSpeed', 20],
    ['FuelTank.Level', 0.75]
  ]);
  
  poseidon.updateShipContext({
    position: {
      lat: 31.2304,
      lon: 121.4737,
      heading: 90,
      speed: 15
    },
    sensors: sensorData,
    environment: {
      windSpeed: 20,
      waveHeight: 2.0,
      visibility: 8
    }
  });
  
  console.log('✅ Ship context updated');
  
  // 查询更新后的状态
  const status = poseidon.getSystemStatus();
  console.log('📊 Updated status:', status.shipContext);
}

/**
 * 演示 5: Digital Twin Map
 */
export async function demo5_DigitalTwin(poseidon) {
  console.log('\n=== Demo 5: Digital Twin Map ===\n');
  
  if (!poseidon.digitalTwinMap) {
    console.log('⚠️ Digital Twin Map not enabled');
    return;
  }
  
  // 添加 AIS 目标
  poseidon.digitalTwinMap.addAISTarget('413123456', {
    name: 'EVER GIVEN',
    position: { x: 50, z: 30 },
    velocity: { x: -2, z: 0 },
    distance: 2.5,
    heading: 270
  });
  
  console.log('✅ AIS target added: EVER GIVEN');
  
  // 高亮风险区域
  poseidon.digitalTwinMap.highlight(
    { x: 50, z: 30 },
    '注意：AIS 目标靠近'
  );
  
  console.log('✅ Risk area highlighted');
  
  // 绘制航线
  const waypoints = [
    { x: 0, z: 0 },
    { x: 100, z: 50 },
    { x: 200, z: 100 },
    { x: 300, z: 150 }
  ];
  
  poseidon.digitalTwinMap.drawRoute(waypoints);
  
  console.log('✅ Route drawn with 4 waypoints');
}

/**
 * 演示 6: 开发模式 - 生成新 Agent
 */
export async function demo6_GenerateAgent(poseidon) {
  console.log('\n=== Demo 6: Generate New Agent (Dev Mode) ===\n');
  
  if (!poseidon.devMode) {
    console.log('⚠️ Dev mode not enabled');
    console.log('💡 To enable: createPoseidonX(scene, camera, { devMode: true })');
    return;
  }
  
  // 使用自然语言生成新 Agent
  const vibe = `
    创建一个监控海水淡化装置的 Agent。
    它能：
    1. 实时监控产水量和水质（TDS）
    2. 检测膜污堵情况
    3. 预测滤芯更换时间
    4. 优化反渗透压力以节省能耗
  `;
  
  console.log('🧬 Generating agent from vibe...');
  
  const generation = await poseidon.generateAgent(vibe);
  
  console.log('✅ Agent generated!');
  console.log('   Name:', generation.parsed.agentName);
  console.log('   Role:', generation.parsed.role);
  console.log('   Tools:', generation.parsed.tools.length);
  console.log('   Code lines:', generation.agentCode.split('\n').length);
}

/**
 * 演示 7: 开发模式 - 验证 Agent
 */
export async function demo7_ValidateAgent(poseidon) {
  console.log('\n=== Demo 7: Validate Agent (Dev Mode) ===\n');
  
  if (!poseidon.devMode) {
    console.log('⚠️ Dev mode not enabled');
    return;
  }
  
  // 验证 Navigator Agent
  console.log('🔬 Validating Navigator Agent...');
  
  const report = await poseidon.validateAgent(
    poseidon.agents.navigator,
    ['weather', 'equipment']
  );
  
  console.log('✅ Validation completed!');
  console.log(`   Pass rate: ${report.passRate}`);
  console.log(`   Passed: ${report.passedScenarios}/${report.totalScenarios}`);
  console.log(`   Status: ${report.passed ? '✅ PASSED' : '❌ FAILED'}`);
  
  if (report.failedScenarios > 0) {
    console.log('\n❌ Failed scenarios:');
    report.results
      .filter(r => !r.passed)
      .forEach(r => {
        console.log(`   - ${r.scenario}: ${r.error || 'Failed criteria'}`);
      });
  }
}

/**
 * 演示 8: 开发模式 - 评估 Agent 执行
 */
export async function demo8_EvaluateAgent(poseidon) {
  console.log('\n=== Demo 8: Evaluate Agent Execution (Dev Mode) ===\n');
  
  if (!poseidon.devMode) {
    console.log('⚠️ Dev mode not enabled');
    return;
  }
  
  // 先执行一个任务
  console.log('🤖 Executing task for evaluation...');
  
  const execution = await poseidon.agents.safety.execute(
    "人员落水！",
    poseidon.shipContext
  );
  
  // 评估执行结果
  console.log('\n⚖️ Evaluating execution...');
  
  const evaluation = await poseidon.evaluateExecution({
    agent: 'SafetyAgent',
    task: "人员落水！",
    result: execution,
    executionTime: 1200 // ms
  });
  
  console.log('✅ Evaluation completed!');
  console.log(`   Overall score: ${evaluation.scores.overall.toFixed(1)}/100`);
  console.log(`   Correctness: ${evaluation.scores.correctness.toFixed(1)}`);
  console.log(`   Compliance: ${evaluation.scores.compliance.toFixed(1)}`);
  console.log(`   Decision quality: ${evaluation.scores.decisionQuality.toFixed(1)}`);
  console.log(`   Timeliness: ${evaluation.scores.timeliness.toFixed(1)}`);
  console.log(`   Status: ${evaluation.passed ? '✅ PASSED' : '❌ FAILED'}`);
  
  if (evaluation.recommendations.length > 0) {
    console.log('\n💡 Recommendations:');
    evaluation.recommendations.forEach(rec => {
      console.log(`   [${rec.priority}] ${rec.suggestion}`);
    });
  }
}

/**
 * 演示 9: 监听系统事件
 */
export function demo9_SystemEvents(poseidon) {
  console.log('\n=== Demo 9: System Events ===\n');
  
  // 监听任务完成事件
  poseidon.on('agent:task_completed', (data) => {
    console.log(`📢 Event: Task completed by ${data.agent}`);
  });
  
  // 监听上下文更新事件
  poseidon.on('context:updated', (context) => {
    console.log(`📢 Event: Ship context updated`);
  });
  
  // 监听聊天消息事件
  poseidon.on('chat:message', (data) => {
    console.log(`📢 Event: Chat message - ${data.message}`);
  });
  
  console.log('✅ Event listeners registered');
}

/**
 * 完整演示流程
 */
export async function runFullDemo(scene, camera) {
  console.log('\n🌊🌊🌊 Poseidon-X Full Demo 🌊🌊🌊\n');
  
  try {
    // 1. 创建系统
    const poseidon = await demo1_BasicUsage(scene, camera);
    
    // 2. 更新船舶状态
    await demo4_UpdateContext(poseidon);
    
    // 3. 设置事件监听
    demo9_SystemEvents(poseidon);
    
    // 4. 执行单个任务
    await demo2_ExecuteTasks(poseidon);
    
    // 5. 并行任务
    await demo3_ParallelTasks(poseidon);
    
    // 6. Digital Twin
    await demo5_DigitalTwin(poseidon);
    
    console.log('\n✅ Full demo completed successfully!\n');
    
    return poseidon;
    
  } catch (error) {
    console.error('\n❌ Demo failed:', error);
    throw error;
  }
}

/**
 * 开发模式完整演示
 */
export async function runDevDemo(scene, camera) {
  console.log('\n🧬🧬🧬 Poseidon-X Dev Mode Demo 🧬🧬🧬\n');
  
  try {
    // 1. 创建系统（开发模式）
    const poseidon = await createPoseidonX(scene, camera, {
      devMode: true,
      enableBridgeChat: true,
      enableDigitalTwin: true
    });
    
    console.log('✅ Dev mode system created\n');
    
    // 2. 生成新 Agent
    await demo6_GenerateAgent(poseidon);
    
    // 3. 验证 Agent
    await demo7_ValidateAgent(poseidon);
    
    // 4. 评估 Agent
    await demo8_EvaluateAgent(poseidon);
    
    console.log('\n✅ Dev demo completed successfully!\n');
    
    return poseidon;
    
  } catch (error) {
    console.error('\n❌ Dev demo failed:', error);
    throw error;
  }
}
