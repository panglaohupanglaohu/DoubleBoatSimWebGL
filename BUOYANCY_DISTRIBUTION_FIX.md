# 浮力分布修复 | Buoyancy Distribution Fix

## 🐛 问题根本原因 | Root Cause

**现象 | Symptom**: 船体一头下沉、一头上翘（船头下沉、船尾上翘）  
**根本原因 | Root Cause**: **浮力采样点分布不均匀，无法准确反映100米长船体的浮力分布**

### 问题分析 | Problem Analysis

1. **采样点过少 | Too Few Sampling Points**
   - 原版只有5个采样点
   - 对于100米长的船体，5个点无法准确反映浮力分布
   - 船头和船尾的浮力差异无法被检测和平衡

2. **浮力分布不均匀 | Uneven Buoyancy Distribution**
   - 船头下沉 → 船头部分浮力不足
   - 船尾上翘 → 船尾部分浮力过大
   - 没有动态调整机制

3. **缺少姿态感知 | No Attitude Awareness**
   - 浮力计算没有考虑船体的俯仰角度
   - 无法根据船体姿态动态调整浮力分布

## 🔧 修复方案 | Fix Solution

### 1. ✅ 大幅增加浮力采样点 | Significantly Increase Sampling Points

**修复前 | Before**: 5个点（四角+中心）  
**修复后 | After**: 约20-30个点（沿长度方向均匀分布）

**分布策略 | Distribution Strategy**:
- 沿船体长度方向（Z轴）分成9段（10个位置）
- 每个位置横向分布3个点（左、中、右）
- 船头和船尾强制保留中心采样点
- 船中区域适当减少边缘点，保持中心线

**采样点分布图 | Distribution**:
```
船头区域（密集采样）:
  * - * - * - * - *
  | | | | | | | | |
  *   *   *   *   *

船中区域（适度采样）:
  *   *   *   *   *
    |   |   |   |
    *   *   *   *

船尾区域（密集采样）:
  * - * - * - * - *
  | | | | | | | | |
  *   *   *   *   *
```

### 2. ✅ 动态浮力调整机制 | Dynamic Buoyancy Adjustment

**检测船体俯仰角度 | Detect Pitch Angle**:
```javascript
const bodyForward = body.quaternion.vmult(new CANNON.Vec3(0, 0, 1));
const pitchAngle = Math.asin(bodyForward.y);
```

**根据俯仰角度调整浮力权重 | Adjust Buoyancy Weight by Pitch**:
- **船头下沉** (pitch < 0): 增加船头浮力权重（+30%）
- **船尾下沉** (pitch > 0): 增加船尾浮力权重（+30%）
- **船头上翘**: 减少船头浮力权重
- **船尾上翘**: 减少船尾浮力权重

**权重计算公式 | Weight Formula**:
```javascript
if (isBow && pitchAngle < 0) {
  positionWeight = 1.0 - pitchAdjustment; // 增加船头浮力
} else if (isStern && pitchAngle > 0) {
  positionWeight = 1.0 + pitchAdjustment; // 增加船尾浮力
}
```

### 3. ✅ 浮力分布统计 | Buoyancy Distribution Statistics

**实时监控 | Real-time Monitoring**:
- 船头浮力总和
- 船尾浮力总和
- 浮力分布比例
- 俯仰角度

**调试输出 | Debug Output**:
```
🔍 Buoyancy Distribution:
  pitch: -5.23° (船头下沉)
  bowForce: 15,234N (45.2%)
  sternForce: 18,456N (54.8%)
  adjustment: +5.2% (船头浮力增强)
```

## 📊 修复对比 | Fix Comparison

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| 采样点数量 | 5个 | 20-30个 |
| 长度方向分布 | 2段 | 9段 |
| 横向分布 | 不均匀 | 左中右均匀 |
| 姿态感知 | ❌ | ✅ |
| 动态调整 | ❌ | ✅ |
| 船头采样点 | 2个 | 8-10个 |
| 船尾采样点 | 2个 | 8-10个 |

## 🎯 工作原理 | How It Works

### 浮力平衡机制 | Buoyancy Balance Mechanism

1. **检测姿态 | Detect Attitude**
   ```
   计算船体俯仰角度 → 判断船头/船尾下沉
   ```

2. **调整权重 | Adjust Weights**
   ```
   船头下沉 → 增加船头浮力权重
   船尾上翘 → 减少船尾浮力权重
   ```

3. **应用浮力 | Apply Buoyancy**
   ```
   每个采样点根据深度和权重计算浮力
   直接施加到船体，产生恢复力矩
   ```

4. **自动平衡 | Auto Balance**
   ```
   船头浮力↑ → 船头浮起 → 俯仰角度减小
   最终达到平衡状态
   ```

### 浮力分布示例 | Buoyancy Distribution Example

**正常状态 | Normal State**:
```
船头浮力: 15,000N (45%)
船尾浮力: 18,000N (55%)
俯仰角度: 0°
```

**船头下沉时 | When Bow Sinks**:
```
检测到俯仰角度: -8°
调整权重: 船头 +8%, 船尾 -4%
船头浮力: 16,200N (48%) ↑
船尾浮力: 17,280N (52%) ↓
结果: 船头浮起，恢复平衡
```

## 🧪 验证方法 | Verification

### 1. 刷新页面 | Refresh Page
```bash
Ctrl + Shift + R
```

### 2. 观察船体姿态 | Observe Ship Attitude

**应该看到 | Should See**:
- ✅ 船体基本水平（俯仰角度 < 5°）
- ✅ 船头和船尾都在水面附近
- ✅ 不会一头下沉一头上翘
- ✅ 保持稳定姿态

### 3. 查看控制台日志 | Check Console Logs

**采样点信息 | Sampling Points**:
```
✅ Generated 25 buoyancy points for 100m ship
   沿长度方向 | Length segments: 10, 横向分布 | Width points: 3
   船头采样点 | Bow: 10, 船中 | Midship: 8, 船尾 | Stern: 10
```

**浮力分布信息 | Distribution Info**:
```
🔍 Buoyancy Distribution:
  pitch: -2.15° (轻微船头下沉)
  bowForce: 16,234N (48.5%)
  sternForce: 17,234N (51.5%)
  adjustment: +2.2% (船头浮力增强中)
```

### 4. 使用稳定化功能 | Use Stabilization

如果仍有轻微不平衡：
- 点击 "⚖️ 船身稳定" 按钮
- 系统会分析并给出建议

## 🔍 技术细节 | Technical Details

### 采样点生成算法 | Sampling Point Generation

```javascript
// 1. 沿长度方向分成9段
lengthSegments = 9 → 10个位置

// 2. 每个位置横向3个点
widthPositions = [-hx, 0, hx] → 左、中、右

// 3. 船中区域适当减少边缘点
if (zRatio < 0.6 && x !== 0 && zi % 2 === 1) {
  continue; // 跳过部分边缘点
}

// 4. 强制保留船头船尾中心点
points.push(0, hy, -hz); // 船头中心
points.push(0, hy, hz);  // 船尾中心
```

### 动态权重计算 | Dynamic Weight Calculation

```javascript
// 1. 计算俯仰角度
pitchAngle = asin(bodyForward.y)

// 2. 计算调整量（限制在±30%）
pitchAdjustment = clamp(pitchDegrees * 0.01, -0.3, 0.3)

// 3. 根据位置和姿态调整权重
if (isBow && pitchAngle < 0) {
  weight = 1.0 - pitchAdjustment  // 增加船头浮力
}
```

## 💡 关键改进点 | Key Improvements

1. **采样点数量**: 5 → 25+ （+400%）
2. **长度方向分布**: 2段 → 9段 （+350%）
3. **姿态感知**: ❌ → ✅ （新增）
4. **动态调整**: ❌ → ✅ （新增）
5. **浮力统计**: ❌ → ✅ （新增）

## 🎓 经验总结 | Lessons Learned

1. **长船体需要更多采样点**
   - 100米长的船，5个点远远不够
   - 需要沿长度方向均匀分布

2. **浮力分布是关键**
   - 不是总浮力的问题，而是分布的问题
   - 船头和船尾的浮力必须平衡

3. **动态调整很重要**
   - 静态的浮力分布无法应对所有情况
   - 需要根据姿态实时调整

4. **姿态感知是基础**
   - 必须先检测船体姿态
   - 才能有针对性地调整浮力

## 🔗 相关文档 | Related Documents

- [稳定性恢复 | Stability Restoration](./STABILITY_RESTORATION.md)
- [浮力修复 | Buoyancy Fix](./BUOYANCY_FIX_7000KG.md)

---

**修复完成时间 | Fix Completion Time**: 2025-12-25  
**版本 | Version**: v2.1.6-buoyancy-distribution

**现在浮力分布已经优化，船体应该能够保持水平平衡了！** ✅  
**Buoyancy distribution optimized, ship should now maintain horizontal balance!** 🚢⚓

