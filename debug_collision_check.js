// Poseidon-X 碰撞检查诊断脚本
// 在浏览器 Console 中运行此脚本进行诊断

console.log('🔍 开始诊断碰撞检查功能...');

// 1. 检查 poseidonSystem 是否初始化
if (!window.poseidonSystem) {
    console.error('❌ poseidonSystem 未初始化！');
    console.log('👉 请等待系统初始化完成（约 10-15 秒）后再试');
} else {
    console.log('✅ poseidonSystem 已初始化');
    console.log('   状态:', window.poseidonSystem.status);
    console.log('   Agents:', Object.keys(window.poseidonSystem.agents || {}));
}

// 2. 检查 log 函数
if (typeof log !== 'function') {
    console.error('❌ log 函数未定义！');
} else {
    console.log('✅ log 函数可用');
    log('🧪 测试消息', 'info');
}

// 3. 检查 console-content 元素
const consoleEl = document.getElementById('console-content');
if (!consoleEl) {
    console.error('❌ console-content 元素未找到！');
} else {
    console.log('✅ console-content 元素存在');
    console.log('   子元素数量:', consoleEl.children.length);
}

// 4. 手动执行碰撞检查
async function debugCollisionCheck() {
    console.log('🚢 开始手动碰撞检查...');
    
    if (!window.poseidonSystem) {
        console.error('❌ poseidonSystem 未初始化');
        return;
    }
    
    try {
        console.log('📡 调用 executeTask...');
        const result = await window.poseidonSystem.executeTask("右舷那艘集装箱船有碰撞风险吗？");
        console.log('✅ 收到响应:', result);
        console.log('   response:', result?.response);
        console.log('   result.response:', result?.result?.response);
        
        // 在 console 中显示
        log('🚢 碰撞风险检查结果:', 'info');
        const navText = result?.response || result?.result?.response || JSON.stringify(result, null, 2);
        log(`   ${navText}`, 'success');
        
    } catch (error) {
        console.error('❌ 碰撞检查失败:', error);
        log(`❌ 查询失败：${error.message}`, 'error');
    }
}

// 运行诊断
console.log('📋 运行诊断...');
debugCollisionCheck();

console.log('🔍 诊断完成！请查看上方输出。');
