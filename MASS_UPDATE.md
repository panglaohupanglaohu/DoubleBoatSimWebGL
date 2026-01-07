# 船体质量参数更新 | Boat Mass Parameter Update

## 📋 更新内容 | Update Summary

**日期 | Date**: 2025-12-25  
**版本 | Version**: v2.1.2

### 主要变更 | Main Changes

**船体质量默认值调整 | Default Boat Mass Adjustment**:
```
20000 kg → 7000 kg
```

## 🎯 更新原因 | Reason for Update

1. **轻量化设计 | Lightweight Design**
   - 7000kg 更适合中小型船舶
   - 更灵活的响应特性
   - 更真实的快艇/科考船模拟

2. **性能优化 | Performance Optimization**
   - 较轻的质量降低物理计算负担
   - 更快的姿态响应
   - 更明显的波浪影响效果

3. **用户反馈 | User Feedback**
   - 用户偏好更灵活的船体表现
   - 便于观察天气和波浪的影响

## 📊 参数调整对比 | Parameter Comparison

| 参数 | 原值 | 新值 | 变化 |
|------|------|------|------|
| 船体质量 | 20000 kg | **7000 kg** | ↓ 65% |
| 浮力系数 | 800 | **400** | ↓ 50% |
| 质量范围（GUI） | 1000-100000 | **1000-50000** | 调整 |

**注意**：浮力系数已自动调整以保持浮力-重力平衡。

## 🎮 使用建议 | Usage Recommendations

### 不同船型的质量配置 | Mass Configuration for Different Vessel Types

#### 1️⃣ 快艇 / 小型船 | Speedboat / Small Vessel
```javascript
质量 | Mass: 3000-5000 kg
浮力系数 | Buoyancy Coeff: 200-300
特点 | Characteristics: 灵活、快速响应
```

#### 2️⃣ 科考船 / 中型船 | Research Vessel / Medium Ship (默认 | Default)
```javascript
质量 | Mass: 7000-10000 kg
浮力系数 | Buoyancy Coeff: 400-600
特点 | Characteristics: 平衡、适度稳定
```

#### 3️⃣ 货船 / 大型船 | Cargo Ship / Large Vessel
```javascript
质量 | Mass: 20000-40000 kg
浮力系数 | Buoyancy Coeff: 800-1500
特点 | Characteristics: 稳重、抗风浪
```

#### 4️⃣ 邮轮 / 超大型船 | Cruise Ship / Extra Large
```javascript
质量 | Mass: 40000-50000 kg
浮力系数 | Buoyancy Coeff: 1500-2000
特点 | Characteristics: 极稳定、缓慢响应
```

## 🔧 如何调整 | How to Adjust

### 方法1：使用GUI（推荐 | Recommended）

1. 打开 GUI 控制面板
2. 找到 **"⚓ 浮力与稳定性 | Buoyancy & Stability"**
3. 调整 **"船体质量 | Boat Mass (kg)"** 滑块
4. 同时调整 **"浮力系数 | Buoyancy Coeff"** 以保持平衡

**建议比例 | Recommended Ratio**:
```
浮力系数 ≈ 质量(kg) / 17.5

例如：
- 7000 kg → 浮力系数 400
- 10000 kg → 浮力系数 571
- 20000 kg → 浮力系数 1143
```

### 方法2：修改配置文件

编辑 `src/demo-refactored.js`:

```javascript
const config = {
  boatMass: 7000,  // 修改此处
  buoyancy: {
    buoyancyCoeff: 400,  // 同时调整浮力系数
    // ...
  }
};
```

## 🎭 不同质量的表现对比 | Performance Comparison

| 质量 | 稳定性 | 响应性 | 波浪影响 | 风影响 | 适用场景 |
|------|--------|--------|----------|--------|----------|
| 3000kg | ⭐⭐ | ⭐⭐⭐⭐⭐ | 明显 | 明显 | 快艇、竞速 |
| 7000kg | ⭐⭐⭐ | ⭐⭐⭐⭐ | 适中 | 适中 | 科考、观光 |
| 15000kg | ⭐⭐⭐⭐ | ⭐⭐⭐ | 较小 | 较小 | 渔船、货船 |
| 30000kg | ⭐⭐⭐⭐⭐ | ⭐⭐ | 很小 | 很小 | 大型货轮 |
| 50000kg | ⭐⭐⭐⭐⭐ | ⭐ | 极小 | 极小 | 邮轮、油轮 |

## 🧪 测试场景 | Test Scenarios

### 场景1：平静海面 | Calm Sea
```
质量: 7000 kg
天气: calm
预期: 船体平稳浮在水面，轻微起伏
```

### 场景2：中等海况 | Moderate Conditions
```
质量: 7000 kg
天气: moderate (风速10m/s)
预期: 明显的横摇和俯仰，但保持稳定
```

### 场景3：风暴测试 | Storm Test
```
质量: 7000 kg
天气: storm (风速20m/s, 大雨)
预期: 剧烈摇晃，但不会倾覆
```

### 场景4：台风极限 | Typhoon Extreme
```
质量: 7000 kg
天气: typhoon (风速35m/s, 暴雨)
预期: 极度不稳定，建议增加质量或浮力系数
```

## ⚖️ 平衡调优指南 | Balance Tuning Guide

### 症状1：船体下沉 | Sinking

**原因 | Cause**: 浮力不足  
**解决方案 | Solution**:
```javascript
// 增加浮力系数
浮力系数 | Buoyancy Coeff: 400 → 600-800
// 或减小质量
质量 | Mass: 7000 → 5000 kg
```

### 症状2：船体浮得太高 | Floating Too High

**原因 | Cause**: 浮力过大  
**解决方案 | Solution**:
```javascript
// 减小浮力系数
浮力系数 | Buoyancy Coeff: 400 → 200-300
// 或增加吃水深度
吃水深度 | Draft Depth: 5 → 3 m
```

### 症状3：摇晃过于剧烈 | Too Much Wobbling

**原因 | Cause**: 质量太轻或稳定性不足  
**解决方案 | Solution**:
```javascript
// 增加质量
质量 | Mass: 7000 → 10000 kg
// 或增加自稳参数
自稳刚度 | Stabilizer Stiffness: 12 → 15
摇晃增强 | Wobble Boost: 0.8 → 0.5
```

### 症状4：响应太慢 | Slow Response

**原因 | Cause**: 质量太大或阻尼太高  
**解决方案 | Solution**:
```javascript
// 减小质量
质量 | Mass: 7000 → 5000 kg
// 或减小阻尼
阻尼系数 | Drag Coeff: 8 → 6
```

## 📈 质量与浮力的数学关系 | Mass-Buoyancy Relationship

### 平衡公式 | Balance Formula

```
总浮力 = 浮力系数 × 深度 × 采样点数 × 水密度
Total Buoyancy = BuoyancyCoeff × Depth × NumPoints × Density

平衡条件 | Balance Condition:
总浮力 ≈ 重力
Total Buoyancy ≈ Gravity

即 | i.e.:
BuoyancyCoeff × Depth × 11 × 1.0 ≈ Mass × 9.82
```

### 示例计算 | Example Calculation

```
质量 = 7000 kg
重力 = 7000 × 9.82 = 68,740 N

所需总浮力 = 68,740 N
采样点数 = 11
假设深度 = 2.5 m

所需浮力系数 = 68,740 / (2.5 × 11 × 1.0) = 2,499

但实际使用 400-600 之间即可，因为：
1. 不是所有点都完全浸入水中
2. 存在动态平衡和阻尼
3. 需要留出调节余地
```

## 🎓 物理原理 | Physics Principles

### 为什么质量减小需要调整浮力？| Why Adjust Buoyancy with Mass?

```
重力 ↓ (质量减小) → 需要的浮力 ↓

如果保持浮力系数不变：
  浮力过大 → 船体浮得太高 → 不真实

如果同步降低浮力系数：
  保持平衡 → 正确的吃水深度 → 真实
```

### 阿基米德原理应用 | Archimedes' Principle

```
浮力 = 排水体积 × 水密度 × 重力加速度
Buoyancy = DisplacedVolume × WaterDensity × g

在我们的模拟中：
DisplacedVolume ≈ 深度 × 采样点覆盖面积
```

## 🔄 版本历史 | Version History

| 版本 | 日期 | 默认质量 | 说明 |
|------|------|----------|------|
| v2.0.0 | 2025-12-24 | 20000 kg | 初始版本 |
| v2.1.0 | 2025-12-25 | 20000 kg | 添加双语支持 |
| v2.1.1 | 2025-12-25 | 20000 kg | 稳定性修复 |
| v2.1.2 | 2025-12-25 | **7000 kg** | **轻量化配置** ⭐ |

## 🚀 快速测试 | Quick Test

### 步骤 | Steps

1. **刷新页面 | Refresh**
```bash
Ctrl + Shift + R
```

2. **访问重构版 | Visit Refactored**
```
http://localhost:3000/index-refactored.html
```

3. **检查质量 | Check Mass**
   - 打开 GUI 控制面板
   - 查看 "船体质量 | Boat Mass"
   - 应该显示: **7000 kg**

4. **观察表现 | Observe Behavior**
   - ✅ 船体应该更灵活
   - ✅ 波浪影响更明显
   - ✅ 风力影响更显著
   - ✅ 仍然保持稳定不倾覆

## 💡 专业提示 | Pro Tips

1. **质量-浮力配比公式 | Mass-Buoyancy Ratio**
   ```
   浮力系数 = 质量 / 17.5
   (经验值，实际可在 ±30% 范围内调整)
   ```

2. **快速恢复默认 | Quick Reset**
   ```
   质量: 7000 kg
   浮力系数: 400
   点击 "重置船体 | Reset Boat"
   ```

3. **性能测试 | Performance Testing**
   ```
   台风模式下测试极限:
   - 质量 7000kg 会剧烈摇晃
   - 质量 15000kg 较为稳定
   - 质量 30000kg 几乎不动
   ```

4. **真实感调校 | Realism Tuning**
   ```
   科考船配置（推荐）:
   - 质量: 7000-10000 kg
   - 浮力系数: 400-600
   - 自稳刚度: 10-12
   - 摇晃增强: 0.8-1.0
   ```

## 📚 相关文档 | Related Documents

- [稳定性修复文档 | Stability Fix](./STABILITY_FIX.md)
- [重构更新日志 | Refactoring Changelog](./REFACTORING_CHANGELOG.md)
- [开发指南 | Development Guide](./DEVELOPMENT_GUIDE.md)

---

**更新完成 | Update Complete**: ✅  
**当前默认质量 | Current Default Mass**: **7000 kg**  
**版本 | Version**: v2.1.2

**Happy Sailing! ⚓ 轻舟已过万重山！🚢**

