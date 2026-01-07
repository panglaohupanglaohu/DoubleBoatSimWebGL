# 功能使用指南 | Features Guide

## 🚪 舱室系统 | Cabin System

### 如何进入舱室 | How to Enter Cabins

#### 方式 1：点击船体上的舱室区域 ✨
1. **查找舱室标记**：
   - 🟢 绿色发光标记点
   - 📦 带有舱室名称的标签（悬浮显示）
   - ⬜ 绿色线框边界

2. **点击进入**：
   - 将鼠标移到标记区域
   - 点击进入舱室
   - 相机会平滑过渡到舱室内部视角

3. **当前可用舱室**：
   - **零部件仓库 | Parts Warehouse**：位于船体左侧
   - **数据中心 | Data Center**：位于船体右侧

#### 方式 2：通过GUI菜单切换 🎛️
1. 打开右上角 GUI 菜单
2. 找到 **"舱室系统 | Cabin System"** 面板
3. 在下拉菜单中选择舱室：
   - `none`：船外视角
   - `parts-warehouse`：零部件仓库
   - `data-center`：数据中心
4. 或点击 **"退出舱室 | Exit Cabin"** 按钮返回

#### 方式 3：按ESC键退出 ⌨️
- 在舱室内时按 **ESC** 键
- 相机会平滑返回船外视角

### 舱室功能 | Cabin Features

#### 零部件仓库 | Parts Warehouse
- 📦 货架系统
- 📦 零部件箱
- 🎨 可视化库存展示

#### 数据中心 | Data Center
- 🖥️ 服务器机架
- 🖥️ 监控屏幕
- 💡 闪烁的LED指示灯（动画）

---

## 📊 实时数据显示 | Realtime Data Display

### 船内数据 | Onboard Data

#### 1. 燃油显示 ⛽
- **位置**：船体左前方，舱室内
- **显示内容**：
  - 燃油表盘（3D仪表）
  - 指针指示燃油量
  - 数值百分比显示
- **数据更新频率**：实时（100ms）

#### 2. 吊机状态 🏗️
- **位置**：船体右中部，甲板上
- **显示内容**：
  - 状态指示灯（绿色=正常，黄色=警告，红色=故障）
  - 加速度数值
  - 状态文字
- **数据包括**：
  - 运行状态
  - 加速度（m/s²）
  - 负载（kg）

#### 3. 人员位置 👥
- **位置**：船体中部，甲板层
- **显示内容**：
  - 3个人员标记点
  - 每个标记显示人员信息
- **数据包括**：
  - 人员ID
  - 当前区域
  - 状态（在岗/离岗）

#### 4. 实验任务状态 🧪
- **位置**：船体左后方，实验室区域
- **显示内容**：
  - 进度条
  - 完成百分比
  - 任务名称
- **数据包括**：
  - 任务进度
  - 数据采集量
  - 实验类型

#### 5. 仓储物资 📦
- **位置**：船体右后方，货仓区域
- **显示内容**：
  - 库存指示器
  - 物资状态
  - 数量级别
- **数据包括**：
  - 食品、水、燃料、备件状态
  - 库存充足度

### 船外数据 | Offboard Data

#### 1. 风向风速 🌬️
- **位置**：船体上方
- **显示内容**：
  - 风向箭头（指向风吹向的方向）
  - 风速数值（m/s）
- **特点**：
  - 箭头大小与风速成正比
  - 实时跟随天气系统变化

#### 2. 海上目标物 🚢
- **位置**：周围海域（随机分布）
- **显示内容**：
  - 目标标记（锥形）
  - 目标标签
  - 距离和方位
- **数据包括**：
  - 目标类型（船只、浮标、障碍物）
  - 距离（米）
  - 方位角（度）
  - 速度（节）

### 数据显示特点 | Display Features

- **3D可视化**：所有数据都有3D对象表示
- **实时更新**：数据每100ms更新一次
- **虚拟数据源**：使用模拟数据（可替换为真实数据源）
- **可视化连线**：未来可支持GraphQL等方式对接真实系统

---

## 🎛️ GUI控制面板 | GUI Control Panel

### 舱室系统面板 | Cabin System Panel

位置：右上角GUI → "舱室系统 | Cabin System"

#### 控件 | Controls

1. **当前舱室 | Current Cabin**
   - 下拉菜单：选择要进入的舱室
   - 选项：`none`, `parts-warehouse`, `data-center`

2. **退出舱室 | Exit Cabin**
   - 按钮：点击返回船外视角

3. **舱室列表 | Cabin List**
   - 展开查看所有可用舱室
   - 显示舱室ID和类型
   - 显示是否激活状态

### 其他面板 | Other Panels

详见 [GUI 使用说明](./GUI_USAGE.md)

---

## 🔍 故障排查 | Troubleshooting

### Q: 看不到舱室标记？
**A**: 可能的原因：
1. 舱室系统还在初始化（等待2-3秒）
2. 相机距离太远（缩放拉近）
3. 标记被船体遮挡（调整视角）

**解决方法**：
- 打开浏览器控制台（F12）
- 查看是否有 `✅ Cabin system initialized` 消息
- 如果没有，等待或刷新页面

### Q: 点击舱室没反应？
**A**: 可能的原因：
1. 点击位置不准确（点击绿色标记点或标签）
2. 相机正在过渡中（等待过渡完成）

**解决方法**：
- 使用GUI菜单进入舱室
- 或在浏览器控制台输入：
  ```javascript
  cabinManager.enterCabin('parts-warehouse') // 进入零部件仓库
  cabinManager.enterCabin('data-center') // 进入数据中心
  cabinManager.exitCabin() // 退出舱室
  ```

### Q: 看不到实时数据显示？
**A**: 可能的原因：
1. 显示对象还在初始化
2. 显示对象在船体背面
3. 距离太远看不清

**解决方法**：
1. 打开浏览器控制台（F12）
2. 查看是否有 `✅ Realtime display system initialized` 消息
3. 旋转相机环绕船体，查找数据显示对象
4. 或在控制台输入以下命令查看数据对象位置：
   ```javascript
   realtimeDisplaySystem.displayObjects.forEach((display, key) => {
     console.log(key, display.group.position);
   });
   ```

### Q: ESC键不能退出舱室？
**A**: 
- 确保键盘焦点在页面上（点击页面任意位置）
- 或使用GUI菜单的"退出舱室"按钮
- 或在控制台输入：`cabinManager.exitCabin()`

### Q: GUI中没有"舱室系统"面板？
**A**: 可能的原因：
1. 舱室系统初始化失败
2. GUI面板初始化延迟

**解决方法**：
1. 等待3-5秒（GUI面板延迟初始化）
2. 刷新页面（Ctrl+Shift+R）
3. 查看控制台错误消息

---

## 🎮 快速操作指南 | Quick Operations

### 进入零部件仓库 | Enter Parts Warehouse
```
方式1: 点击船体左侧绿色标记
方式2: GUI → 舱室系统 → 选择 "parts-warehouse"
方式3: 控制台 → cabinManager.enterCabin('parts-warehouse')
```

### 进入数据中心 | Enter Data Center
```
方式1: 点击船体右侧绿色标记
方式2: GUI → 舱室系统 → 选择 "data-center"
方式3: 控制台 → cabinManager.enterCabin('data-center')
```

### 退出舱室 | Exit Cabin
```
方式1: 按 ESC 键
方式2: GUI → 舱室系统 → 点击"退出舱室"
方式3: 控制台 → cabinManager.exitCabin()
```

### 查看燃油数据 | View Fuel Data
```
方式1: 旋转相机到船体左前方，查找燃油表盘
方式2: 控制台 → virtualDataSource.getRealtimeData()
```

### 调试模式 | Debug Mode
```javascript
// 在浏览器控制台输入：

// 1. 显示所有舱室信息
console.log(cabinManager.getCabinsInfo());

// 2. 显示所有数据对象位置
realtimeDisplaySystem.displayObjects.forEach((display, key) => {
  console.log(key, display.group.position);
});

// 3. 显示当前活动舱室
console.log(cabinManager.getActiveCabin());

// 4. 获取实时数据
console.log(virtualDataSource.getRealtimeData());
```

---

## 📚 相关文档 | Related Documentation

- [项目 README](./README.md) - 项目总览
- [GUI 使用说明](./GUI_USAGE.md) - GUI详细说明
- [架构文档](./ARCHITECTURE.md) - 系统架构
- [开发进度](./DEVELOPMENT_PROGRESS.md) - 功能开发状态

---

**更新时间 | Last Updated**: 2025-12-25  
**版本 | Version**: v2.3.0-features-visible



