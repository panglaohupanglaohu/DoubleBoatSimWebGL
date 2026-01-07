# GUI 使用说明 | GUI Usage Guide

## 🎯 新功能 | New Features

### 精确数值调整 | Precise Value Adjustment

所有数字参数现在都支持三种调整方式：

#### 1. 滑块调整 | Slider Adjustment
- 拖动滑块快速调整数值
- 适合大范围快速调整

#### 2. 精确输入 | Precise Input ✨ **新增**
- **点击数值**直接输入精确值
- 支持键盘输入
- 按 Enter 确认，按 Esc 取消

#### 3. 步进按钮 | Stepper Buttons ✨ **新增**
- 点击 `+` 按钮：增加步进值
- 点击 `−` 按钮：减少步进值
- 精确控制数值变化

## 🎨 视觉增强 | Visual Enhancements

### 下拉箭头提示 | Dropdown Arrow Indicator
- 所有数字参数右侧显示 **▼** 符号
- 鼠标悬停时箭头变色并放大
- 提示可以点击进行精确输入

### 交互反馈 | Interactive Feedback
- 鼠标悬停：背景变亮，边框高亮
- 聚焦输入：背景更亮，蓝色边框，外发光效果
- 步进按钮：悬停放大，点击缩小

### 工具提示 | Tooltip
- 鼠标悬停在数字参数上时显示提示
- 提示内容："点击输入精确值 | Click to input exact value"

## 📝 使用示例 | Usage Examples

### 示例 1：调整浮力系数 | Example 1: Adjust Buoyancy Coefficient

**方式 1 - 滑块：**
1. 拖动 "浮力系数" 滑块
2. 观察船体反应

**方式 2 - 精确输入：**
1. 点击 "浮力系数" 数值（例如：800）
2. 输入精确值（例如：820）
3. 按 Enter 确认

**方式 3 - 步进按钮：**
1. 点击 `+` 按钮：浮力系数增加 10
2. 点击 `−` 按钮：浮力系数减少 10
3. 每次点击精确调整 10 个单位

### 示例 2：微调船体吃水深度 | Example 2: Fine-tune Draft Depth

**精确调整（步进 0.1）：**
1. 找到 "吃水深度 | Draft Depth" 参数
2. 点击 `+` 按钮：增加 0.1m
3. 点击 `−` 按钮：减少 0.1m
4. 或直接点击数值输入精确值

### 示例 3：设置风速 | Example 3: Set Wind Speed

**快速设置为 15 m/s：**
1. 点击 "风速 | Wind Speed" 数值
2. 输入 `15`
3. 按 Enter
4. 风速立即设置为 15 m/s

## 🎛️ 所有支持精确调整的参数 | All Parameters with Precise Adjustment

### 波浪参数 | Wave Parameters
- **振幅** (步进: 0.1) - 范围: 0.1 ~ 5
- **波长** (步进: 1) - 范围: 4 ~ 40
- **速度** (步进: 0.1) - 范围: 0.2 ~ 4
- **陡度** (步进: 0.02) - 范围: 0.2 ~ 1.2

### 天气控制 | Weather Control
- **风速** (步进: 0.5 m/s) - 范围: 0 ~ 40
- **风向** (步进: 5°) - 范围: 0 ~ 360
- **降雨强度** (步进: 1 mm/h) - 范围: 0 ~ 100
- **海况等级** (步进: 1) - 范围: 0 ~ 9

### 浮力参数 | Buoyancy Parameters
- **浮力系数** (步进: 10) - 范围: 200 ~ 1200
- **阻尼系数** (步进: 0.5) - 范围: 0 ~ 20
- **密度** (步进: 0.05) - 范围: 0.5 ~ 2.0
- **船体质量** (步进: 500 kg) - 范围: 1000 ~ 50000
- **吃水深度** (步进: 0.1 m) - 范围: -5 ~ 25

### 自稳系统 | Stabilizer System
- **自稳刚度** (步进: 0.1) - 范围: 0 ~ 15
- **自稳阻尼** (步进: 0.1) - 范围: 0 ~ 10
- **摇晃系数** (步进: 0.1) - 范围: 0.2 ~ 5.0

## 💡 使用技巧 | Tips

### 1. 快速调整
- 使用滑块进行快速调整
- 观察效果后再精确调整

### 2. 精确设置
- 需要精确数值时，直接点击输入
- 避免多次尝试滑块位置

### 3. 微调参数
- 使用步进按钮进行微调
- 每次调整固定步长，结果可预测

### 4. 批量调整
- 按 Tab 键在参数间切换
- 快速连续输入多个精确值

### 5. 恢复默认
- 点击 "重置船体" 按钮恢复默认参数
- 或使用 "船身稳定" 按钮自动优化

## 🎨 自定义样式 | Custom Styles

如果需要修改样式，编辑 `public/gui-enhancements.css`：

```css
/* 修改箭头颜色 */
.lil-gui .controller.number::after {
  color: rgba(255, 255, 255, 0.4); /* 默认颜色 */
}

/* 修改悬停效果 */
.lil-gui .controller.number:hover {
  background: rgba(255, 255, 255, 0.15); /* 悬停背景 */
  border-color: #4a9eff; /* 边框颜色 */
}

/* 修改步进按钮大小 */
.number-stepper button {
  width: 16px;  /* 按钮宽度 */
  height: 16px; /* 按钮高度 */
}
```

## 🔧 技术实现 | Technical Implementation

### 增强函数 | Enhancement Function

```javascript
function enhanceNumberController(controller, step = null) {
  // 1. 添加工具提示
  // 2. 创建步进按钮
  // 3. 绑定事件处理
  return controller;
}
```

### 使用示例 | Usage Example

```javascript
enhanceNumberController(
  gui.add(config, 'value', 0, 100, 1)
    .name('参数名称')
    .onChange(callback),
  1 // 步进值
);
```

## 🐛 常见问题 | Troubleshooting

### Q: 点击数值无反应？
**A**: 确保已加载 `gui-enhancements.css` 文件

### Q: 步进按钮不可见？
**A**: 检查浏览器控制台是否有CSS加载错误

### Q: 输入值不生效？
**A**: 确保输入值在参数范围内，按 Enter 确认

### Q: 样式显示异常？
**A**: 清除浏览器缓存（Ctrl+Shift+R）后重试

## 📚 相关文档 | Related Documentation

- [项目 README](./README.md)
- [架构文档](./ARCHITECTURE.md)
- [开发指南](./DEVELOPMENT_GUIDE.md)

---

**更新时间 | Last Updated**: 2025-12-25  
**版本 | Version**: v2.2.0-gui-enhanced



