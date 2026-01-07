# 舱室高亮标注功能 | Cabin Highlight Feature

## ✨ 新功能 | New Features

### 1. 高亮标注 | Highlight Indicators

在船体上为每个舱室添加了**明显的高亮标注**，包括：

#### 🟢 高亮平面
- **位置**：覆盖在舱室入口区域（船体表面）
- **颜色**：绿色半透明
- **大小**：舱室尺寸的1.2倍
- **动画**：呼吸效果（透明度变化）
- **功能**：可点击区域，双击进入

#### ⬜ 发光边框
- **位置**：围绕舱室边界
- **颜色**：绿色线框
- **大小**：舱室尺寸的1.15倍
- **动画**：持续旋转 + 呼吸效果

#### 🔵 发光标记点
- **位置**：舱室上方
- **颜色**：绿色发光球体
- **大小**：0.8米半径
- **动画**：呼吸效果（大小和透明度变化）

#### 📝 文字标签
- **位置**：舱室上方
- **内容**：舱室名称 + "双击进入 | Double-click to enter"
- **样式**：绿色文字，黑色背景，绿色边框
- **大小**：10x2.5米

#### 💫 脉冲光环
- **位置**：标记点下方
- **颜色**：绿色圆环
- **动画**：脉冲效果（大小和透明度变化）

### 2. 双击进入 | Double-Click to Enter

#### 操作方式
- **双击**高亮标注区域进入舱室
- 支持双击以下对象：
  - ✅ 高亮平面
  - ✅ 发光边框
  - ✅ 发光标记点
  - ✅ 文字标签
  - ✅ 脉冲光环

#### 交互反馈
- 双击后控制台输出确认消息
- 相机平滑过渡到舱室内部
- 第一人称视角

## 🎯 使用方法 | Usage

### 步骤 1：查找高亮标注
在船体上查找：
- 🟢 **绿色高亮平面**（最明显）
- 📝 **文字标签**（显示舱室名称）
- 🔵 **发光球体**（闪烁）

### 步骤 2：双击进入
1. 将鼠标移到高亮标注区域
2. **双击**（快速点击两次）
3. 相机自动飞入舱室内部

### 步骤 3：退出舱室
- 按 **ESC** 键
- 或使用GUI菜单的"退出舱室"按钮

## 📍 舱室位置 | Cabin Locations

### 零部件仓库 | Parts Warehouse
- **位置**：船体左侧
- **标识**：绿色高亮标注
- **标签**："零部件仓库 | Parts Warehouse"

### 数据中心 | Data Center
- **位置**：船体右侧
- **标识**：绿色高亮标注
- **标签**："数据中心 | Data Center"

## 🎨 视觉效果 | Visual Effects

### 动画效果
1. **呼吸效果**：所有高亮元素都有透明度和大小的呼吸动画
2. **旋转效果**：发光边框持续旋转
3. **脉冲效果**：光环有脉冲动画

### 颜色方案
- **主色**：绿色 (#00ff00)
- **高亮**：半透明绿色
- **发光**：高亮度绿色（emissive）

## 🔧 技术实现 | Technical Implementation

### 高亮平面创建
```javascript
const highlightPlane = new THREE.Mesh(
  new THREE.PlaneGeometry(size.x * 1.2, size.y * 1.2),
  new THREE.MeshBasicMaterial({
    color: 0x00ff00,
    transparent: true,
    opacity: 0.3,
    side: THREE.DoubleSide
  })
);
highlightPlane.userData = { cabinId: cabin.id, isCabinIndicator: true };
```

### 双击检测
```javascript
renderer.domElement.addEventListener('dblclick', onMouseDoubleClick, false);

function onMouseDoubleClick(event) {
  const clicked = cabinManager.checkCabinClick(raycaster, mouse);
  if (clicked) {
    console.log('✅ 双击进入舱室');
  }
}
```

### 点击检测优化
- 优先检测高亮标注对象（`userData.isCabinIndicator`）
- 如果命中高亮标注，直接进入舱室
- 备用方案：检测舱室模型本身

## 📊 对比 | Comparison

| 功能 | 之前 | 现在 |
|------|------|------|
| 视觉提示 | 小标记点 | 多重视觉元素 |
| 进入方式 | 单击 | 双击 |
| 高亮效果 | 简单边框 | 平面+边框+标记+标签+光环 |
| 动画效果 | 基础呼吸 | 多种动画组合 |
| 可点击区域 | 小 | 大（高亮平面） |

## 🧪 测试方法 | Testing

### 1. 刷新页面
```
Ctrl + Shift + R
```

### 2. 查找高亮标注
- 应该能看到船体左右两侧的**绿色高亮区域**
- 应该能看到**文字标签**（"零部件仓库"、"数据中心"）
- 应该能看到**发光球体**（闪烁）

### 3. 测试双击
- 将鼠标移到高亮区域
- **双击**（快速点击两次）
- 应该进入舱室内部

### 4. 测试退出
- 在舱室内按 **ESC**
- 应该返回船外视角

## 🐛 故障排查 | Troubleshooting

### Q: 看不到高亮标注？
**A**: 
1. 等待2-3秒初始化完成
2. 旋转相机，从不同角度查看船体
3. 检查控制台是否有错误

### Q: 双击没反应？
**A**:
1. 确保双击速度足够快（两次点击间隔<300ms）
2. 确保鼠标在高亮区域内
3. 检查控制台是否有错误消息

### Q: 高亮标注位置不对？
**A**:
- 高亮标注会跟随船体移动和旋转
- 如果船体模型尺寸变化，可能需要调整bounds

## 📝 相关文件 | Related Files

- **`src/ship/cabins/CabinManager.js`**
  - `_createCabinIndicator()` - 创建高亮标注
  - `checkCabinClick()` - 检测双击
  - `update()` - 更新动画

- **`src/demo-refactored.js`**
  - `onMouseDoubleClick()` - 双击事件处理

---

**更新时间**: 2025-12-25  
**版本**: v2.4.0-cabin-highlight  
**状态**: ✅ 完成 | Completed



