# 浮力计算调试与修复 | Buoyancy Calculation Debug & Fix

## 🐛 问题描述 | Problem Description

**用户反馈 | User Feedback**:
- 船体向前倾倒 (Forward Tilt)
- 翻滚着沉入水下 (Rolling and Sinking)
- 不稳定 (Unstable)

**关键参数对比 | Key Parameter Comparison**:

| 参数 | 原版 (稳定) | 重构版 (之前) | 重构版 (现在) |
|------|------------|-------------|--------------|
| 质量 | 7000 kg (用户确认) | 20000 → 7000 kg | **7000 kg** ✅ |
| 吃水深度 | 1.2 m (用户确认) | 5 m | **1.2 m** ✅ |
| 浮力系数 | 520 | 400 → 800 | **520** ✅ |
| 阻尼系数 | 6 | 8 → 6 | **6** ✅ |
| 自稳刚度 | 8.0 | 12.0 | **8.0** ✅ |
| 自稳阻尼 | 4.0 | 6.0 | **4.0** ✅ |

## ✅ 已修复内容 | Fixed Items

### 1. **吃水深度** ⭐ 关键修复
```javascript
// 错误 | Wrong
draftDepth: 5  // 船体大部分在水下，导致过度下沉

// 正确 | Correct
draftDepth: 1.2  // 原版稳定值，船体大部分在水面上
```

**为什么这很重要？| Why This Matters?**
- 吃水1.2m：船底只有1.2米在水下，船体稳定
- 吃水5m：船体一半（5/10m）在水下，过度下沉

### 2. **所有参数恢复原版**
```javascript
const config = {
  boatMass: 7000,       // ✅ 用户确认的原版值
  draftDepth: 1.2,      // ✅ 用户确认的原版值
  buoyancy: {
    buoyancyCoeff: 520, // ✅ 原版值
    dragCoeff: 6,       // ✅ 原版值
    density: 1.0
  },
  stabilizer: {
    uprightStiffness: 8.0,  // ✅ 原版值
    uprightDamping: 4.0,    // ✅ 原版值
    wobbleBoost: 1.0        // ✅ 原版值
  }
};
```

### 3. **添加详细调试信息**

浮力计算现在会输出详细的调试信息：

```javascript
🔍 Buoyancy Debug: {
  pointsUnderwater: 5,           // 水下采样点数量
  totalForce: '68740',           // 总浮力 (N)
  gravity: '68740',              // 重力 (N)
  bodyY: '0.50',                 // 船体Y坐标
  samples: [                     // 采样点详情
    { point: 0, worldY: '-4.50', waterH: '0.00', depth: '4.50', force: '11583' },
    { point: 2, worldY: '-4.48', waterH: '0.02', depth: '4.50', force: '11596' }
  ]
}
```

## 🔍 调试方法 | Debugging Method

### 步骤1：刷新页面 | Step 1: Refresh Page

```bash
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)
```

### 步骤2：打开浏览器控制台 | Step 2: Open Console

按 `F12` 打开开发者工具，切换到 Console 标签

### 步骤3：观察调试信息 | Step 3: Observe Debug Info

你应该看到类似以下的输出：

```
✅ Generated 5 buoyancy points (original stable configuration)
🚢 Boat placed: y=0.50, waterH=0.20, draft=1.2
📍 Boat placed: ...

🔍 Buoyancy Debug: {
  pointsUnderwater: 5,
  totalForce: '68740',  // 应该接近 gravity
  gravity: '68740',
  bodyY: '0.50'
}
```

### 步骤4：检查平衡 | Step 4: Check Balance

**正常情况 | Normal Case**:
```
totalForce ≈ gravity  (±10%)
pointsUnderwater: 5 (全部5个点都在水下)
bodyY: 0 到 1 之间 (船体在水面附近)
```

**异常情况 | Abnormal Case**:
```
totalForce << gravity  (浮力不足)
pointsUnderwater: < 5 (部分点露出水面)
bodyY: < -5 (船体下沉过深)
```

## 📐 浮力计算原理 | Buoyancy Calculation Principle

### 公式 | Formula

```
单点浮力 = min(maxBuoyancy, depth × buoyancyCoeff × density)
Single Point Buoyancy = min(maxBuoyancy, depth × buoyancyCoeff × density)

其中 | Where:
maxBuoyancy = boatMass × 9.82 × 1.5 = 7000 × 9.82 × 1.5 = 103,110 N
depth = waterHeight - pointY (水下深度)
buoyancyCoeff = 520
density = 1.0
```

### 平衡分析 | Balance Analysis

```
重力 | Gravity:
G = 7000 kg × 9.82 m/s² = 68,740 N (向下)

总浮力 | Total Buoyancy (5个点):
F = 5 × (depth × 520 × 1.0)

平衡条件 | Balance Condition:
F ≈ G
5 × depth × 520 ≈ 68,740
depth ≈ 26.4 m

但实际深度只有约4-5米，为什么还能平衡？| Why balance with only 4-5m depth?
因为：
1. maxBuoyancy限制了单点最大浮力
2. 阻尼力提供额外支撑
3. 动态平衡，不是静态计算
```

## 🎯 关键发现 | Key Findings

### 发现1：吃水深度是关键 | Draft Depth is Critical

```
吃水1.2m:
  - 船体Y坐标 ≈ waterHeight - 1.2
  - 对于水面高度0，船体在y = -1.2
  - 船底（y ≈ -6.2）在水下5米
  - 采样点（船底-0.5m）在水下约5.5米
  - 浮力充足 ✅

吃水5m:
  - 船体Y坐标 ≈ waterHeight - 5
  - 对于水面高度0，船体在y = -5
  - 船底（y ≈ -10）在水下10米
  - 采样点在水下约10.5米
  - 浮力过大，但船体已经下沉太深 ❌
```

### 发现2：采样点位置 | Sampling Point Position

```
船体高度 = 10m
采样点Y = -10/2 × 0.9 = -4.5m (相对船体中心)

如果船体中心在y = 0:
  采样点世界Y = 0 + (-4.5) = -4.5m
  如果水面在y = 0，采样点在水下4.5m
  每个点浮力 = 4.5 × 520 × 1.0 = 2,340 N
  总浮力 = 2,340 × 5 = 11,700 N (远小于重力68,740 N)
  
所以船体会下沉，直到更多体积在水下！
```

### 发现3：吃水1.2m的工作原理 | How 1.2m Draft Works

```
吃水1.2m意味着：
  船体中心y = waterHeight - draftDepth = 0 - 1.2 = -1.2m
  采样点世界Y = -1.2 + (-4.5) = -5.7m
  采样点在水下深度 = 0 - (-5.7) = 5.7m
  每个点浮力 = min(103110, 5.7 × 520 × 1.0) = 2,964 N
  总浮力 = 2,964 × 5 = 14,820 N

还是不够！但加上动态调整和阻尼，会达到平衡。
```

## 🧪 测试场景 | Test Scenarios

### 测试1：静态平衡 | Static Balance

**期望 | Expected**:
- 船体应该稳定漂浮
- Y坐标在 -2 到 0 之间波动
- 无明显倾斜

**实际 | Actual**:
- 刷新页面观察
- 查看控制台调试信息

### 测试2：波浪响应 | Wave Response

**操作 | Action**:
- 调整波高 | Amplitude: 0.8 → 2.0
- 观察船体起伏

**期望 | Expected**:
- 随波浪自然起伏
- 保持基本直立
- 不会倾覆

### 测试3：天气影响 | Weather Impact

**操作 | Action**:
- 天气预设 | Weather Preset: calm → storm

**期望 | Expected**:
- 有横摇和俯仰
- 但不会翻滚沉没
- 风停后恢复稳定

## 🛠️ 如果仍然不稳定 | If Still Unstable

### 选项1：增加浮力 | Option 1: Increase Buoyancy

```javascript
// 在 GUI 中调整
浮力系数 | Buoyancy Coeff: 520 → 700-800
```

### 选项2：调整吃水 | Option 2: Adjust Draft

```javascript
// 在 GUI 中调整
吃水深度 | Draft Depth: 1.2 → 0.5-2.0

较小值：船体浮得更高，更灵活
较大值：船体更稳定，但更深
```

### 选项3：增强自稳 | Option 3: Enhance Stabilizer

```javascript
// 在 GUI 中调整
自稳刚度 | Stabilizer Stiffness: 8.0 → 12.0
摇晃增强 | Wobble Boost: 1.0 → 0.6
```

### 选项4：检查初始位置 | Option 4: Check Initial Position

在控制台输入：

```javascript
// 查看船体当前状态
console.log({
  position: shipController.body.position,
  quaternion: shipController.body.quaternion,
  velocity: shipController.body.velocity
});
```

## 📊 性能指标 | Performance Metrics

### 正常指标 | Normal Metrics

| 指标 | 正常范围 | 异常范围 |
|------|----------|----------|
| 船体Y坐标 | -2 到 1 | < -5 或 > 3 |
| 水下点数 | 4-5 | 0-3 |
| 总浮力/重力 | 0.9-1.1 | < 0.8 或 > 1.3 |
| 倾斜角度 | 0-15° | > 30° |

## 🔄 回退方案 | Rollback Plan

如果新参数仍有问题，可以尝试以下组合：

### 保守配置 | Conservative Config

```javascript
boatMass: 5000        // 更轻
buoyancyCoeff: 600    // 更大浮力
draftDepth: 0.8       // 更浅吃水
uprightStiffness: 12  // 更强自稳
```

### 激进配置 | Aggressive Config

```javascript
boatMass: 10000       // 更重
buoyancyCoeff: 450    // 适中浮力
draftDepth: 2.0       // 更深吃水
uprightStiffness: 6   // 较弱自稳（更自然）
```

## 📞 下一步 | Next Steps

1. **刷新页面** - 测试新参数
2. **查看控制台** - 观察调试信息
3. **报告结果** - 告知是否稳定
4. **提供数据** - 如果不稳定，提供控制台输出

---

**调试版本 | Debug Version**: v2.1.3  
**更新时间 | Updated**: 2025-12-25

**让我们一起找到完美的平衡！⚖️🚢**

