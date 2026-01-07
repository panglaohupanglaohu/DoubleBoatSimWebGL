# 船体稳定性测试系统 | Ship Stability Test System

## 📋 概述 | Overview

这是一个完整的船体稳定性自动化测试系统，用于验证船体在各种条件下的稳定性表现。

**功能 | Features**:
- ✅ 7种不同的稳定性测试场景
- ✅ 自动化的物理模拟
- ✅ 详细的指标收集和分析
- ✅ 可视化的测试报告
- ✅ 双语界面支持

## 🚀 快速开始 | Quick Start

### 1. 启动测试页面

```bash
# 确保服务器正在运行
npm start

# 访问测试页面
http://localhost:3000/test-stability.html
```

### 2. 运行测试

**运行所有测试 | Run All Tests**:
- 点击 "运行所有测试 | Run All Tests" 按钮
- 等待所有测试完成（约 1-2 分钟）
- 查看测试报告和详细结果

**快速测试 | Quick Test**:
- 点击 "快速测试 | Quick Test" 按钮
- 只运行基础稳定性测试（约 10 秒）
- 快速验证船体基本稳定性

## 🧪 测试场景 | Test Scenarios

### 1. 基础稳定性测试 | Basic Stability Test

**测试内容 | Test Content**:
- 船体在平静海面上的稳定性
- 无风无雨条件下的表现
- 基本浮力和自稳系统验证

**通过标准 | Pass Criteria**:
- 最大倾斜角度 < 45°
- 最大下沉深度 < 15m
- 最终倾斜角度 < 5°

### 2. 波浪响应测试 | Wave Response Test

**测试内容 | Test Content**:
- 船体对波浪的响应
- 大波浪条件下的稳定性
- 振荡幅度控制

**通过标准 | Pass Criteria**:
- 最大倾斜角度 < 30°
- 振荡幅度 < 2.0m
- 不倾覆

### 3. 风力影响测试 | Wind Effect Test

**测试内容 | Test Content**:
- 15 m/s 风速下的表现
- 侧向漂移控制
- 横摇稳定性

**通过标准 | Pass Criteria**:
- 最大倾斜角度 < 25°
- 最大漂移距离 < 50m
- 不倾覆

### 4. 降雨影响测试 | Rain Effect Test

**测试内容 | Test Content**:
- 50 mm/h 降雨强度下的表现
- 积水对船体的影响
- 重量增加导致的吃水变化

**通过标准 | Pass Criteria**:
- 最大下沉深度 < 8m
- 最终下沉深度 < 3m
- 不倾覆

### 5. 极端天气测试 | Extreme Weather Test

**测试内容 | Test Content**:
- 30 m/s 风速 + 80 mm/h 降雨
- 3.0m 大波浪
- 综合极端条件下的稳定性

**通过标准 | Pass Criteria**:
- 不倾覆
- 最大倾斜角度 < 60°
- 恢复时间 < 10秒

### 6. 参数变化测试 | Parameter Changes Test

**测试内容 | Test Content**:
- 不同质量配置（5000kg, 7000kg, 10000kg）
- 不同浮力系数
- 参数组合的稳定性

**通过标准 | Pass Criteria**:
- 所有配置都通过测试
- 最大倾斜角度 < 30°
- 不倾覆

### 7. 扰动恢复测试 | Disturbance Recovery Test

**测试内容 | Test Content**:
- 施加突然的角速度和线速度扰动
- 测试自稳系统的恢复能力
- 恢复时间测量

**通过标准 | Pass Criteria**:
- 恢复时间 < 5秒
- 最终倾斜角度 < 5°

## 📊 测试指标 | Test Metrics

### 收集的指标 | Collected Metrics

| 指标 | 说明 | 单位 |
|------|------|------|
| maxTilt | 最大倾斜角度 | 度 (°) |
| maxSink | 最大下沉深度 | 米 (m) |
| maxDrift | 最大漂移距离 | 米 (m) |
| oscillationAmplitude | 振荡幅度 | 米 (m) |
| finalTilt | 最终倾斜角度 | 度 (°) |
| finalSink | 最终下沉深度 | 米 (m) |
| capsized | 是否倾覆 | 布尔值 |
| recoveryTime | 恢复时间 | 秒 (s) |

### 稳定性阈值 | Stability Thresholds

```javascript
{
  maxTilt: 45°,        // 最大倾斜角度
  maxSink: 15m,        // 最大下沉深度
  maxOscillation: 0.5m, // 最大振荡幅度
  recoveryTime: 5s     // 恢复时间
}
```

## 🎯 测试结果解读 | Interpreting Results

### 通过率 | Pass Rate

- **≥ 80%**: 🎉 船体稳定性良好
- **60-79%**: ⚠️ 船体稳定性需要改进
- **< 60%**: ❌ 船体稳定性不足

### 常见问题诊断 | Common Issues

#### 问题1: 基础稳定性测试失败

**可能原因 | Possible Causes**:
- 浮力系数不足
- 自稳系统参数不当
- 采样点分布不合理

**解决方案 | Solutions**:
```javascript
// 增加浮力系数
buoyancyCoeff: 400 → 600

// 增强自稳系统
uprightStiffness: 12 → 15
uprightDamping: 6 → 8
```

#### 问题2: 波浪响应测试失败

**可能原因 | Possible Causes**:
- 阻尼系数不足
- 船体质量过轻
- 波浪参数过大

**解决方案 | Solutions**:
```javascript
// 增加阻尼
dragCoeff: 8 → 12

// 增加质量
mass: 7000 → 10000
```

#### 问题3: 极端天气测试失败

**可能原因 | Possible Causes**:
- 船体质量过轻
- 自稳系统不够强
- 浮力不足

**解决方案 | Solutions**:
```javascript
// 增加质量
mass: 7000 → 15000

// 增强自稳
uprightStiffness: 12 → 18
wobbleBoost: 0.8 → 0.5
```

## 📈 性能优化建议 | Performance Optimization

### 测试速度优化 | Speed Optimization

```javascript
// 减少测试持续时间
duration: 10 → 5  // 秒

// 降低采样频率
sampleRate: 10 → 20  // 每N帧采样一次

// 减少物理迭代次数
solver.iterations: 14 → 10
```

### 精度优化 | Accuracy Optimization

```javascript
// 增加测试持续时间
duration: 10 → 20  // 秒

// 提高采样频率
sampleRate: 10 → 5  // 每N帧采样一次

// 增加物理迭代次数
solver.iterations: 14 → 20
```

## 🔧 自定义测试 | Custom Tests

### 添加新测试 | Adding New Tests

在 `ShipStabilityTest.js` 中添加：

```javascript
async testCustomScenario() {
  const { world, simulator, shipBody } = this.setupTestEnvironment({
    mass: 7000,
    buoyancyCoeff: 400,
    // 自定义参数
  });

  const metrics = this.runSimulation(world, simulator, shipBody, {
    duration: 10,
    environment: { time: 0, weather: { windSpeed: 0, rainIntensity: 0 } }
  });

  const passed = /* 自定义判断条件 */;

  return {
    passed,
    metrics,
    message: passed ? '✅ 通过' : '❌ 失败'
  };
}
```

然后在 `runAllTests()` 中添加：

```javascript
const tests = [
  // ... 现有测试
  { name: '自定义测试', func: this.testCustomScenario.bind(this) }
];
```

## 📄 导出报告 | Export Report

### JSON 报告格式 | JSON Report Format

```json
{
  "timestamp": "2025-12-25T10:00:00.000Z",
  "config": {
    "duration": 10,
    "timeStep": 0.0167,
    "sampleRate": 10,
    "stabilityThreshold": { ... }
  },
  "results": [
    {
      "name": "基础稳定性测试",
      "passed": true,
      "metrics": { ... },
      "message": "✅ 基础稳定性良好"
    }
  ],
  "summary": {
    "total": 7,
    "passed": 6,
    "failed": 1
  }
}
```

### 使用报告 | Using Reports

1. 点击 "导出报告 | Export Report" 按钮
2. 保存 JSON 文件
3. 用于：
   - 性能分析
   - 参数调优
   - 版本对比
   - 问题诊断

## 🐛 故障排除 | Troubleshooting

### 问题1: 测试页面无法加载

**检查 | Check**:
- 服务器是否运行
- 文件路径是否正确
- 浏览器控制台错误信息

**解决 | Solution**:
```bash
# 重启服务器
npm start

# 检查文件是否存在
ls test-stability.html
ls src/tests/ShipStabilityTest.js
```

### 问题2: 测试运行很慢

**原因 | Reason**:
- 测试持续时间过长
- 采样频率过高
- 物理迭代次数过多

**解决 | Solution**:
```javascript
// 在 ShipStabilityTest.js 中调整
this.testConfig = {
  duration: 5,      // 减少到5秒
  sampleRate: 20,   // 降低采样频率
};
```

### 问题3: 测试结果不准确

**原因 | Reason**:
- 测试时间太短
- 采样频率太低
- 物理精度不足

**解决 | Solution**:
```javascript
// 增加测试时间
duration: 10 → 20

// 提高采样频率
sampleRate: 10 → 5

// 增加物理迭代
solver.iterations: 14 → 20
```

## 📚 相关文档 | Related Documents

- [稳定性修复文档 | Stability Fix](./STABILITY_FIX.md)
- [质量更新文档 | Mass Update](./MASS_UPDATE.md)
- [开发指南 | Development Guide](./DEVELOPMENT_GUIDE.md)

## 🎓 最佳实践 | Best Practices

1. **定期运行测试 | Regular Testing**
   - 每次参数调整后运行测试
   - 代码修改后验证稳定性
   - 发布前完整测试

2. **保存测试报告 | Save Reports**
   - 导出并保存测试报告
   - 对比不同版本的测试结果
   - 追踪稳定性变化趋势

3. **参数调优 | Parameter Tuning**
   - 根据测试结果调整参数
   - 逐步优化，不要大幅改动
   - 记录每次调整的效果

4. **性能平衡 | Performance Balance**
   - 测试精度 vs 运行速度
   - 稳定性 vs 响应性
   - 真实感 vs 可控性

---

**版本 | Version**: v1.0.0  
**最后更新 | Last Updated**: 2025-12-25

**Happy Testing! 🧪 测试愉快！⚓**

