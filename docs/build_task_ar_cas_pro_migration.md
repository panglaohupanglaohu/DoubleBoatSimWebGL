# Build Team 任务: AR-CAS Pro 功能平移到数字孪生页面

## 任务概述

将 `http://localhost:5173/worldmonitor-ar-cas-pro.html` 的 **AR-CAS Pro**（船舶避免碰撞增强现实系统专业版）的全部功能平移到 `http://localhost:5173/digital-twin.html` 的 **AR-CAS Pro** 浮动面板中。

**核心原则**: 数字孪生页面（digital-twin.html）已有的 3D 场景（Three.js 船舶模型、海洋环境、天气系统）作为 AR 的基础载体，AR-CAS Pro 的增强现实能力叠加在这个基础之上。

---

## 源文件分析

### 源: `src/frontend/worldmonitor-ar-cas-pro.html` (2198 行)

这是一个独立的 AR-CAS Pro 页面，包含以下功能模块：

#### 1. 地图层 (MapLibre GL)
- OpenStreetMap 底图
- AIS 目标标记（船舶位置、航向、速度）
- 本船位置标记
- 航线显示
- 地图交互（点击选择目标）

#### 2. 左侧边栏 (Sidebar)
- **特殊场景预警**: 峡谷航行警告、冰山预警
- **COLREGs 合规警告**: 国际海上避碰规则分析
- **AIS 目标列表 (AR-CAS Pro)**: 
  - CPA/TCPA/DCPA 指标
  - 目标卡片（类型、MMSI、位置、航向、航速、风险等级）
  - 高风险/中风险/低风险标记
- **气象详情**: 风速、风向、浪高、流向、能见度
- **附近港口**: 港口名称和距离

#### 3. 右侧面板 (Right Panel)
- **驾驶台报警菜单**: 报警卡片（级别、时间、消息、来源）
- **本船信息**: 位置、航向、航速
- **AR 监控摄像头**: 
  - 前视摄像头 + AR 叠加层（目标标记、轨迹预测）
  - 后视摄像头 + AR 叠加层
  - AR 目标圆圈、冰山三角形、峡谷标记
- **航线规划**: 起点、航点、终点
- **AI Agent 洞察**: 
  - Agent 团队状态
  - 决策摘要
  - 快捷命令（分析 AIS 态势、评估碰撞风险、航线建议）

#### 4. VR 浮动菜单 (核心 AR 功能)
- **可拖拽/可调整大小的浮动面板**
- **VR 场景渲染 (Canvas 2D)**:
  - 高斯泼溅式语义粒子渲染
  - 本船船体绘制（Bridge/Overhead/Corridor 三种视角）
  - 环境粒子（风、浪）
  - AIS 目标粒子（按风险着色）
  - 冰山粒子
  - 峡谷标记
- **控制面板**:
  - View Mode: Bridge / Overhead / Corridor
  - Environment Layer: All / Traffic / Weather
- **HUD 信息**: Hull State, Sea Surface, Threat Focus, Gaussian Splats 计数
- **语义菜单**: Focus Target, Environment, Alarm Posture
- **目标提示框**: 鼠标悬停显示目标详情
- **图例**: 安全/中风险/高风险/船体颜色

#### 5. JavaScript 核心逻辑
- `bridgeState`: 本船、目标、报警、天气、CPA 结果状态管理
- `vrState`: 视角模式、图层模式、动画帧
- `map` (MapLibre): 地图初始化、AIS 数据加载、天气数据加载
- `syncVrScene()`: 同步 VR 场景与数据
- `renderVrScene()`: 动画循环渲染 VR 场景
- `drawGaussianSplat()`: 高斯泼溅绘制
- `drawOwnShipHull()`: 船体绘制
- `drawEnvironmentSplats()`: 环境粒子绘制
- `getVrTrafficHit()`: 鼠标碰撞检测
- `updateVrTooltip()`: 提示框更新
- `loadAISData()`, `loadWeatherData()`: 数据加载
- `checkSpecialScenarios()`: 特殊场景检测
- `focusOnTarget()`: 目标聚焦
- `escapeHtml()`: HTML 转义

---

## 目标文件分析

### 目标: `src/frontend/digital-twin.html` (3947 行)

数字孪生页面已有以下基础设施：

#### 已有 AR-CAS Pro 面板 (行 3445-3600)
- 浮动可拖拽面板（右下角）
- 标题栏（带拖拽、折叠、关闭按钮）
- 内容区域:
  - 本船状态
  - 风险汇总（高风险/中风险/冰山计数）
  - 监视目标列表
  - COLREGs 建议
  - 环境信息
  - 数据源说明
- 调整大小手柄
- 位置/大小持久化（localStorage）

#### 已有 3D 场景基础设施
- Three.js 船舶模型（`boatMesh`）
- 海洋环境（波浪、天气效果）
- AIS 目标（3D 场景中的货船标记）
- 冰山（3D 场景中的冰山模型）
- 天气控制系统（Weather Control Panel）
- 波浪设置（Wave Settings Panel）
- 相机控制（Bridge/Overhead/Free 视角）
- 数字孪生主程序 (`main.js`)
- NavigationMonitor, DataAggregator 等模块

#### 已有数据流
- `window.DigitalTwin` 全局对象
- `DigitalTwin.getState()` 获取状态
- `DigitalTwin.setSelectedTarget()` 选择目标
- `DigitalTwin.applyExternalSync()` 外部数据同步
- `window.__digitalTwinAisTargets` AIS 目标数据
- `window.aiNativeAggregator` 数据聚合器

---

## 迁移方案

### 架构设计

```
digital-twin.html
├── 已有 3D 场景 (Three.js) ← AR 基础载体
├── 已有 Weather/Wave Controls
├── 已有 AIS 目标列表
├── 已有 Captain Cockpit
└── AR-CAS Pro 浮动面板 (增强)
    ├── 本船状态 (已有, 增强)
    ├── 风险汇总 (已有, 增强)
    ├── 监视目标列表 (已有, 增强)
    ├── COLREGs 建议 (已有, 增强)
    ├── 环境信息 (已有, 增强)
    ├── VR 场景渲染 (新增) ← Canvas 2D 高斯泼溅
    │   ├── View Mode 切换 (Bridge/Overhead/Corridor)
    │   ├── Layer 切换 (All/Traffic/Weather)
    │   ├── 船体绘制
    │   ├── 环境粒子
    │   ├── AIS 目标粒子
    │   ├── 冰山/峡谷标记
    │   └── 鼠标交互 (悬停提示/点击选择)
    ├── 语义菜单 (新增)
    ├── 图例 (新增)
    └── 特殊场景预警 (新增)
```

### 详细任务分解

#### 任务 1: 创建 AR-CAS Pro 核心 JS 模块

**文件**: `src/frontend/digital-twin/ArCasProEngine.js`

创建一个独立的 ES Module，封装 AR-CAS Pro 的核心逻辑：

```javascript
export class ArCasProEngine {
  constructor(config = {}) {
    // 状态管理
    this.state = {
      ownShip: null,
      targets: [],
      cpaResults: [],
      alarms: [],
      weather: null,
      selectedTarget: null,
      hoveredTarget: null,
      viewMode: 'bridge',      // bridge | overhead | corridor
      layerMode: 'all',         // all | traffic | weather
      animationTick: 0,
      specialScenario: { inCanyon: false, hasIceberg: false, icebergs: [] }
    };
    
    // 配置
    this.config = {
      canvasId: config.canvasId || 'ar-cas-vr-canvas',
      panelId: config.panelId || 'ar-cas-floating',
      ...config
    };
  }
  
  // 初始化
  initialize() { ... }
  
  // 数据更新
  updateState(data) { ... }
  
  // VR 场景渲染
  renderScene() { ... }
  
  // 高斯泼溅绘制
  drawGaussianSplat(x, y, radius, color, alpha) { ... }
  
  // 船体绘制
  drawOwnShipHull(width, height) { ... }
  
  // 环境粒子
  drawEnvironmentSplats(width, height) { ... }
  
  // 碰撞检测
  getHitTarget(clientX, clientY) { ... }
  
  // 提示框
  updateTooltip(hitEntry) { ... }
  
  // 语义菜单更新
  updateSemanticMenu() { ... }
  
  // 特殊场景检测
  checkSpecialScenarios() { ... }
  
  // CPA 计算
  calculateCPA(targets) { ... }
  
  // COLREGs 规则分析
  analyzeCOLREGs(target, ownShip) { ... }
  
  // 报警生成
  buildAlarms(cpaResults, targets, scenario) { ... }
  
  // 清理
  dispose() { ... }
}
```

**需要实现的方法** (从 worldmonitor-ar-cas-pro.html 移植):

| 方法 | 源位置 | 说明 |
|------|--------|------|
| `drawGaussianSplat()` | 行 ~1400 | 高斯泼溅绘制 |
| `drawOwnShipHull()` | 行 ~1420 | 船体绘制 |
| `drawEnvironmentSplats()` | 行 ~1450 | 环境粒子 |
| `drawVrBackground()` | 行 ~1390 | 背景绘制 |
| `renderVrScene()` | 行 ~1530 | 主渲染循环 |
| `getVrTrafficHit()` | 行 ~1500 | 碰撞检测 |
| `updateVrTooltip()` | 行 ~1490 | 提示框 |
| `updateVrHud()` | 行 ~1520 | HUD 更新 |
| `updateVrSemanticMenu()` | 行 ~1350 | 语义菜单 |
| `getVrPalette()` | 行 ~1380 | 风险色板 |
| `formatVrTargetLabel()` | 行 ~1310 | 目标标签 |
| `isSameTarget()` | 行 ~1320 | 目标比较 |
| `getScenarioLabel()` | 行 ~1330 | 场景标签 |
| `buildVrAlarms()` | 行 ~1280 | 报警生成 |
| `renderWorldMonitorAlarms()` | 行 ~1260 | 报警渲染 |
| `checkSpecialScenarios()` | 需移植 | 特殊场景检测 |
| `calculateCPA()` | 需移植 | CPA 计算 |
| `escapeHtml()` | 行 ~1600 | HTML 转义 |

#### 任务 2: 增强 digital-twin.html 的 AR-CAS Pro 面板

**文件**: `src/frontend/digital-twin.html`

在现有 AR-CAS Pro 面板基础上进行以下增强：

##### 2.1 面板结构增强

在 `#ar-cas-body` 内新增以下区域：

```html
<!-- VR 场景画布 -->
<div id="ar-cas-vr-container" style="width:100%;height:240px;margin-bottom:10px;position:relative;background:oklch(0.96 0.003 110);border:1px solid rgba(244,67,54,0.2);overflow:hidden;">
  <canvas id="ar-cas-vr-canvas" style="width:100%;height:100%;display:block;"></canvas>
  <!-- VR 控制覆盖层 -->
  <div id="ar-cas-vr-controls" style="position:absolute;top:4px;left:4px;display:flex;gap:4px;">
    <button class="vr-chip active" data-vr-view="bridge">Bridge</button>
    <button class="vr-chip" data-vr-view="overhead">Overhead</button>
    <button class="vr-chip" data-vr-view="corridor">Corridor</button>
  </div>
  <div id="ar-cas-vr-layer-controls" style="position:absolute;top:4px;right:4px;display:flex;gap:4px;">
    <button class="vr-chip active" data-vr-layer="all">All</button>
    <button class="vr-chip" data-vr-layer="traffic">Traffic</button>
    <button class="vr-chip" data-vr-layer="weather">Weather</button>
  </div>
  <!-- 目标提示框 -->
  <div id="ar-cas-vr-tooltip" style="position:absolute;display:none;..."></div>
  <!-- 图例 -->
  <div id="ar-cas-vr-legend" style="position:absolute;right:4px;bottom:4px;..."></div>
</div>

<!-- 特殊场景预警 -->
<div id="ar-cas-special-alerts" style="margin-bottom:10px;">
  <div id="ar-cas-canyon-alert" style="display:none;...">🏔️ 峡谷航行警告</div>
  <div id="ar-cas-iceberg-alert" style="display:none;...">🧊 冰山预警</div>
</div>

<!-- 语义菜单 -->
<div id="ar-cas-semantic" style="...">
  <div>Focus Target: <span id="ar-cas-sem-target">未锁定</span></div>
  <div>Environment: <span id="ar-cas-sem-env">Open Sea</span></div>
  <div>Alarm Posture: <span id="ar-cas-sem-alarm">正常监视</span></div>
</div>

<!-- AI Agent 快捷命令 -->
<div id="ar-cas-agent-commands" style="...">
  <button onclick="arCasEngine.analyzeAIS()">分析 AIS 态势</button>
  <button onclick="arCasEngine.evaluateRisk()">评估碰撞风险</button>
  <button onclick="arCasEngine.suggestRoute()">航线建议</button>
</div>
```

##### 2.2 面板交互增强

- 展开/折叠时 VR 画布自动调整大小
- 面板大小变化时 VR 画布 resize
- 鼠标进入 VR 画布时显示交互光标
- 点击 VR 画布中的目标时同步到 3D 场景

##### 2.3 数据同步

- 从 `window.DigitalTwin.getState()` 获取本船位置、AIS 目标、冰山数据
- 从 `window.__digitalTwinAisTargets` 获取 AIS 目标列表
- 从天气控制系统获取天气数据
- 每 3 秒同步一次数据

#### 任务 3: 集成到数字孪生主程序

**文件**: `src/frontend/digital-twin/main.js`

在 main.js 中添加 AR-CAS Pro 引擎的初始化和数据连接：

```javascript
import { ArCasProEngine } from './ArCasProEngine.js';

// 在数字孪生初始化完成后
const arCasEngine = new ArCasProEngine({
  canvasId: 'ar-cas-vr-canvas',
  panelId: 'ar-cas-floating'
});

// 暴露到全局
window.arCasEngine = arCasEngine;

// 数据同步循环
setInterval(() => {
  const dtState = window.DigitalTwin?.getState?.();
  if (dtState) {
    arCasEngine.updateState({
      ownShip: dtState.boatMesh?.position,
      targets: window.__digitalTwinAisTargets || [],
      icebergs: dtState.icebergs || [],
      weather: dtState.weather || {}
    });
  }
}, 3000);
```

#### 任务 4: 样式适配

**文件**: `src/frontend/digital-twin.html`

在 `<style>` 中添加 AR-CAS Pro VR 场景相关样式：

```css
/* VR 场景容器 */
#ar-cas-vr-container {
  border-radius: 4px;
  transition: height 0.3s ease;
}

/* VR 控制按钮 */
#ar-cas-vr-container .vr-chip {
  padding: 2px 8px;
  font-size: 9px;
  border: 1px solid rgba(244,67,54,0.3);
  background: rgba(244,67,54,0.1);
  color: oklch(0.55 0.005 110);
  cursor: pointer;
  border-radius: 3px;
  font-family: inherit;
}

#ar-cas-vr-container .vr-chip.active {
  background: rgba(244,67,54,0.25);
  border-color: rgba(244,67,54,0.5);
  color: oklch(0.48 0.07 22);
}

/* 特殊场景预警 */
#ar-cas-special-alerts .alert-card {
  padding: 8px 10px;
  margin-bottom: 6px;
  border-radius: 4px;
  font-size: 11px;
  line-height: 1.5;
}

/* 语义菜单 */
#ar-cas-semantic {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  padding: 8px 10px;
  background: rgba(244,67,54,0.05);
  border: 1px solid rgba(244,67,54,0.15);
  border-radius: 4px;
  font-size: 11px;
  margin-bottom: 10px;
}

/* AI Agent 命令按钮 */
#ar-cas-agent-commands {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 8px;
}

#ar-cas-agent-commands button {
  padding: 4px 10px;
  font-size: 10px;
  border: 1px solid rgba(79,195,247,0.25);
  background: rgba(79,195,247,0.1);
  color: oklch(0.52 0.04 160);
  cursor: pointer;
  border-radius: 3px;
  font-family: inherit;
}
```

---

## 实现优先级

### P0 (必须完成)
1. ✅ 创建 `ArCasProEngine.js` 核心模块
2. ✅ VR 场景渲染（高斯泼溅、船体、环境粒子、AIS 目标）
3. ✅ 视角模式切换（Bridge/Overhead/Corridor）
4. ✅ 图层模式切换（All/Traffic/Weather）
5. ✅ 鼠标交互（悬停提示、点击选择）
6. ✅ 数据同步（从 DigitalTwin 获取状态）

### P1 (重要)
1. 特殊场景检测（峡谷、冰山）
2. COLREGs 规则分析
3. CPA/TCPA 计算
4. 报警生成与显示
5. 语义菜单更新
6. AI Agent 快捷命令

### P2 (锦上添花)
1. 面板位置/大小持久化
2. 动画优化（帧率控制）
3. 移动端适配
4. 键盘快捷键

---

## 数据流设计

```
DigitalTwin (3D Scene)
    │
    ├── boatMesh.position ──────────────► ArCasProEngine.state.ownShip
    ├── getState().icebergs ────────────► ArCasProEngine.state.specialScenario.icebergs
    ├── getState().weather ─────────────► ArCasProEngine.state.weather
    │
    ├── window.__digitalTwinAisTargets ─► ArCasProEngine.state.targets
    │
    └── setSelectedTarget(target) ◄──── ArCasProEngine (点击 VR 目标时回调)
                                            │
                                            ▼
                                    ArCasProEngine.renderScene()
                                            │
                                            ▼
                                    Canvas 2D (VR 场景)
```

---

## 文件修改清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/frontend/digital-twin/ArCasProEngine.js` | **新建** | AR-CAS Pro 核心引擎模块 |
| `src/frontend/digital-twin.html` | **修改** | 增强 AR-CAS Pro 面板（HTML+CSS+JS） |
| `src/frontend/digital-twin/main.js` | **修改** | 集成 ArCasProEngine 初始化 |

---

## 验收标准

1. **VR 场景渲染**: 数字孪生页面的 AR-CAS Pro 面板中能看到高斯泼溅渲染的 VR 场景
2. **视角切换**: Bridge/Overhead/Corridor 三种视角可切换
3. **图层切换**: All/Traffic/Weather 三种图层可切换
4. **目标显示**: AIS 目标以彩色粒子显示（绿=低风险，黄=中风险，红=高风险）
5. **鼠标交互**: 悬停目标显示提示框，点击目标同步到 3D 场景
6. **数据同步**: AR-CAS Pro 面板数据与数字孪生 3D 场景实时同步
7. **特殊场景**: 峡谷和冰山场景能正确检测并显示预警
8. **COLREGs**: 能根据目标态势给出避碰规则建议
9. **性能**: VR 场景渲染帧率不低于 30fps
10. **兼容性**: 不破坏数字孪生页面现有功能

---

## 注意事项

1. **不要覆盖大文件**: digital-twin.html 有 3947 行，使用 patch_file 精准修改
2. **保持 Wabi-Sabi 设计风格**: 颜色、字体、阴影风格与现有页面一致
3. **向后兼容**: 所有新增参数必须有默认值
4. **模块化**: ArCasProEngine.js 必须是独立的 ES Module
5. **不要重复造轮子**: 复用 DigitalTwin 已有的数据和方法
6. **VR 场景使用 Canvas 2D**: 不要引入额外的 3D 引擎，保持轻量
7. **面板默认折叠**: 首次加载时 AR-CAS Pro 面板默认折叠，不遮挡视线
