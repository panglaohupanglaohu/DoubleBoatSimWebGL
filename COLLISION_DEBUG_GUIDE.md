# 碰撞检查 Console 无输出问题诊断指南

## 🔍 问题描述

点击"碰撞风险"按钮后，Console 中没有显示预期输出。

## 📋 可能原因

### 1. 系统未完全初始化
- **症状：** 点击按钮后无任何反应
- **检查：** 打开浏览器 Console (F12)，查看是否有 `poseidonSystem 未初始化` 警告
- **解决：** 等待 10-15 秒，待系统完全初始化后再试

### 2. Bridge Chat 未正确配置
- **症状：** 系统已初始化，但调用 LLM 失败
- **检查：** Console 中是否有 `LLM Client initialized` 日志
- **解决：** 检查 `poseidon-config.html` 中的 LLM 配置

### 3. Console 元素问题
- **症状：** 功能正常，但 Console 不显示
- **检查：** Console 区域是否可见，是否有 CSS 问题
- **解决：** 刷新页面或检查 HTML 结构

## 🛠️ 诊断步骤

### 步骤 1：打开浏览器开发者工具
1. 按 `F12` 或右键 → 检查
2. 切换到 **Console** 标签

### 步骤 2：检查系统状态
在 Console 中运行：
```javascript
console.log('poseidonSystem:', window.poseidonSystem);
console.log('initialized:', window.poseidonSystem?.initialized);
console.log('Agents:', Object.keys(window.poseidonSystem?.agents || {}));
```

### 步骤 3：运行诊断脚本
在 Console 中运行：
```javascript
// 加载诊断脚本
const script = document.createElement('script');
script.src = 'debug_collision_check.js';
document.head.appendChild(script);
```

### 步骤 4：手动测试
在 Console 中直接调用：
```javascript
await window.queryCollisionRisk();
```

## 📝 预期输出

正常的 Console 输出应该包含：
```
🚢 正在查询碰撞风险...
🎯 Executing task: 右舷那艘集装箱船有碰撞风险吗？
✅ executeTask 返回：{response: "...", ...}
✅ Navigator Agent 响应:
   [响应内容]
```

## 🔧 修复方案

### 方案 1：等待系统初始化
- 刷新页面
- 等待 10-15 秒
- 查看 Console 中是否有 `✅ Poseidon-X initialized successfully!`
- 然后再点击"碰撞风险"按钮

### 方案 2：检查 LLM 配置
1. 打开 `poseidon-config.html`
2. 确认已配置 LLM API Key
3. 保存并跳转到主页面
4. 重试碰撞检查

### 方案 3：查看详细日志
修改 `queryCollisionRisk` 函数，添加更多调试日志：
```javascript
window.queryCollisionRisk = async function() {
  console.log('🔍 queryCollisionRisk 被调用');
  const sys = window.poseidonSystem;
  console.log('poseidonSystem:', sys);
  console.log('initialized:', sys?.initialized);
  
  if (!sys) {
    console.warn('❌ poseidonSystem 未初始化');
    log('⚠️ 系统正在初始化中，请稍候...', 'warning');
    return;
  }
  if (!sys.initialized) {
    console.warn('❌ sys.initialized = false');
    log('⚠️ 系统未完全初始化，请等待...', 'warning');
    return;
  }
  
  try {
    console.log('📡 调用 executeTask...');
    log('🚢 正在查询碰撞风险...', 'info');
    const result = await sys.executeTask("右舷那艘集装箱船有碰撞风险吗？");
    console.log('✅ executeTask 返回:', result);
    log('✅ Navigator Agent 响应:', 'success');
    const navText = result?.response || result?.result?.response || JSON.stringify(result, null, 2);
    log(`   ${navText}`, 'success');
    updateStatusPanel();
  } catch (error) {
    console.error('❌ 异常:', error);
    log(`❌ 查询失败：${error.message}`, 'error');
  }
};
```

## 📞 如需进一步帮助

请提供以下信息：
1. 浏览器 Console 完整输出
2. `poseidonSystem` 状态截图
3. 问题复现步骤

---

**最后更新：** 2026-03-09 22:45
