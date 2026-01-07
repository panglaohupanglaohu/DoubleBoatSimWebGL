# 新模块使用指南 | New Modules Guide

## 🎉 新增模块

本次更新实现了三个核心模块：

1. **安全态势监控系统** (`SafetyMonitor`)
2. **场景预演系统** (`ScenarioSimulator`)
3. **船岸数据同步系统** (`ShipShoreSync`)

---

## 1. 安全态势监控系统 | Safety Monitoring System

### 📍 位置
`src/monitoring/SafetyMonitor.js`

### 🎯 功能
实时监控船舶安全状态，包括：

- **主机状态监控**
  - 温度、转速、压力实时显示
  - 状态指示灯（绿色=正常，黄色=警告，红色=故障）
  - 3D主机模型可视化

- **燃油消耗监控**
  - 实时燃油消耗率（L/h）
  - 燃油表盘可视化
  - 指针动态指示

- **舵机系统监控**
  - 健康度百分比
  - 舵角实时显示
  - 状态指示灯

- **推进系统监控**
  - 健康度百分比
  - 效率百分比
  - 状态指示灯

- **结构应力监控**
  - 船首、船中、船尾应力传感器
  - 实时应力值显示
  - 颜色编码（绿色=正常，黄色=警告，红色=危险）

- **应急设备监控**
  - 消防泵可用状态
  - 救生艇可用状态
  - 状态指示灯

### 🎨 可视化位置

| 监控对象 | 位置 | 说明 |
|---------|------|------|
| 主机状态 | 船体后部 (-25, 5, 0) | 发动机舱 |
| 燃油消耗 | 船体左前方 (-12, 6, -18) | 燃油舱附近 |
| 舵机系统 | 船体后部 (0, 4, 18) | 舵机舱 |
| 推进系统 | 船体后部 (0, 4, 20) | 推进器舱 |
| 结构应力 | 船首/中/尾 (0, 8, ±20/0) | 船体表面 |
| 应急设备 | 船体左右 (±8, 6, 15) | 甲板层 |

### 📊 状态阈值

系统自动根据阈值判断状态等级：

- **正常 (Normal)**: 绿色指示灯
- **警告 (Warning)**: 黄色指示灯
- **危险 (Critical)**: 红色指示灯

### 🎮 GUI控制

在GUI菜单中找到 **"安全态势监控 | Safety Monitor"** 面板：

- **查看状态** 按钮：在控制台输出当前安全态势摘要

### 💻 代码使用

```javascript
// 获取监控状态摘要
const summary = safetyMonitor.getStatusSummary();

// 获取警报列表
const alerts = safetyMonitor.getAlerts();
```

---

## 2. 场景预演系统 | Scenario Simulation System

### 📍 位置
`src/simulation/ScenarioSimulator.js`

### 🎯 功能
支持自定义场景预演，包括：

- **暴雨漏水场景**
  - 暴雨天气模拟
  - 船舱漏水效果（粒子系统）
  - 积水效果
  - 巡检人员路径

- **第一人称视角**
  - WASD键移动
  - 鼠标拖动旋转视角
  - 平滑相机控制

- **路径跟随**
  - 自动跟随预设路径
  - 路径可视化（绿色线条）
  - 路径点标记（起点=绿色，终点=红色，中间点=黄色）

### 🎬 预定义场景

#### 暴雨漏水场景 (`heavyRainLeak`)
- **天气**: 暴风雨（风速25m/s，降雨80mm/h，海况6级）
- **路径**: 
  1. 起始点：住宿舱室 (0, 3, -15)
  2. 走廊1 (0, 3, -10)
  3. 走廊2 (0, 3, -5)
  4. 漏水点：货仓 (5, 2, 0)

### 🎮 控制方式

#### 第一人称控制
- **W**: 前进
- **S**: 后退
- **A**: 左移
- **D**: 右移
- **鼠标拖动**: 旋转视角

#### GUI控制
在GUI菜单中找到 **"场景预演 | Scenario Simulation"** 面板：

- **选择场景**: 下拉菜单选择场景
- **启动场景**: 开始场景预演
- **停止场景**: 停止当前场景
- **自动跟随路径**: 自动沿路径移动

### 💻 代码使用

```javascript
// 启动场景
scenarioSimulator.startScenario('heavyRainLeak');

// 停止场景
scenarioSimulator.stopScenario();

// 进入第一人称
scenarioSimulator.enterFirstPerson();

// 退出第一人称
scenarioSimulator.exitFirstPerson();

// 跟随路径
scenarioSimulator.followPath(1.0); // 速度1.0

// 获取可用场景
const scenarios = scenarioSimulator.getAvailableScenarios();
```

---

## 3. 船岸数据同步系统 | Ship-Shore Sync System

### 📍 位置
`src/data/ShipShoreSync.js`

### 🎯 功能
实现船端和岸端数字孪生系统的数据同步：

- **静态数据批次传输**
  - 船体基本信息
  - 设备规格信息
  - 结构信息
  - 传输频率：每5秒

- **动态数据批次传输**
  - 船体位置和姿态
  - 主机状态
  - 燃油消耗
  - 舵机推进系统状态
  - 结构应力
  - 应急设备状态
  - 传输频率：每1秒

- **数据压缩**
  - 自动压缩大于1KB的数据
  - 移除不必要的空格和换行
  - 压缩率统计

- **数据筛选**
  - 只发送变化的数据
  - 变化阈值：1%
  - 减少网络传输量

- **优先级管理**
  - **关键优先级**: 应急设备、结构应力、主机状态
  - **高优先级**: 燃油、舵机、推进系统
  - **普通优先级**: 人员、库存、实验
  - **低优先级**: 环境、目标物

- **网络模拟**
  - 模拟网络延迟（默认100ms）
  - 模拟丢包率（默认1%）
  - 传输统计

### 📊 数据结构

#### 静态数据批次
```javascript
{
  timestamp: 1234567890,
  type: 'static',
  shipInfo: {
    id: 'SHIP-001',
    name: '数字孪生船舶',
    length: 100,
    width: 20,
    height: 10,
    mass: 7000,
    draftDepth: 1.2
  },
  equipment: { ... },
  structure: { ... }
}
```

#### 动态数据批次
```javascript
{
  timestamp: 1234567890,
  type: 'dynamic',
  position: { x, y, z },
  orientation: { x, y, z, w },
  velocity: { x, y, z },
  mainEngine: { ... },
  fuel: { ... },
  rudder: { ... },
  propulsion: { ... },
  structure: { ... },
  emergency: { ... }
}
```

### 🎮 GUI控制

在GUI菜单中找到 **"船岸数据同步 | Ship-Shore Sync"** 面板：

- **连接状态**: 显示当前连接状态
- **切换连接**: 连接/断开岸端系统
- **查看统计**: 在控制台输出传输统计
- **重置统计**: 重置统计数据

### 📈 统计数据

系统自动统计：

- 静态数据发送次数
- 动态数据发送次数
- 总发送字节数
- 压缩字节数
- 丢包数
- 平均延迟
- 队列大小
- 压缩率

### 💻 代码使用

```javascript
// 连接岸端
shipShoreSync.connect();

// 断开连接
shipShoreSync.disconnect();

// 获取统计数据
const stats = shipShoreSync.getStats();
console.log('传输统计:', stats);

// 重置统计
shipShoreSync.resetStats();

// 监听数据发送事件
shipShoreSync.on('dataSent', (data) => {
  console.log('数据已发送:', data);
});

shipShoreSync.on('batchSent', (data) => {
  console.log('批次已发送:', data);
});
```

### ⚙️ 配置选项

```javascript
const sync = new ShipShoreSync(dataSource, {
  enableCompression: true,      // 启用压缩
  enablePriority: true,         // 启用优先级
  enableFiltering: true,         // 启用筛选
  networkLatency: 100,          // 网络延迟（ms）
  packetLossRate: 0.01,         // 丢包率（1%）
  batchSize: 50                 // 批次大小
});
```

---

## 🚀 快速开始

### 1. 刷新页面
```
Ctrl + Shift + R
```

### 2. 等待初始化
查看控制台，应该看到：
```
✅ Virtual data source initialized
✅ Realtime display system initialized
✅ Safety monitoring system initialized
✅ Scenario simulation system initialized
✅ Ship-shore sync system initialized and connected
```

### 3. 使用GUI控制
- 打开右上角GUI菜单
- 找到新模块的控制面板
- 开始使用！

---

## 📝 注意事项

### 安全态势监控
- 监控对象会自动跟随船体移动
- 状态指示灯会根据阈值自动变色
- 数据每200ms更新一次

### 场景预演
- 启动场景后会自动切换到第一人称视角
- 可以使用WASD键和鼠标控制移动
- 路径可视化会显示在场景中

### 船岸数据同步
- 系统启动后自动连接
- 静态数据每5秒发送一次
- 动态数据每1秒发送一次
- 只发送变化的数据，减少网络负载

---

## 🐛 故障排查

### 如果看不到监控对象
1. 等待初始化完成（1.5秒后）
2. 旋转相机，从不同角度查看
3. 检查控制台是否有错误

### 如果场景无法启动
1. 确保天气系统已初始化
2. 检查控制台错误信息
3. 尝试手动进入第一人称视角

### 如果数据同步不工作
1. 检查连接状态（GUI面板）
2. 查看统计数据（可能有丢包）
3. 检查控制台事件输出

---

## 📚 相关文件

- `src/monitoring/SafetyMonitor.js` - 安全态势监控系统
- `src/simulation/ScenarioSimulator.js` - 场景预演系统
- `src/data/ShipShoreSync.js` - 船岸数据同步系统
- `src/demo-refactored.js` - 主程序（已集成）

---

**更新时间**: 2025-12-25  
**版本**: v3.0.0-new-modules  
**状态**: ✅ 完成 | Completed



