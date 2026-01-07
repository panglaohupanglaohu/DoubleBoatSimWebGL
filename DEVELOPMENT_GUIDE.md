# 船舶数字孪生系统 - 开发指南

## 🎯 快速开始

### 1. 查看重构后的Demo

```bash
# 启动服务器
npm start

# 访问重构版Demo
http://localhost:3000/index-refactored.html
```

### 2. 核心特性展示

重构后的系统实现了以下核心功能：

✅ **可插拔模拟器引擎** - 动态添加/移除算法  
✅ **天气系统** - 风、雨模拟及对船体的物理影响  
✅ **数据接口管理器** - 虚拟数据源与真实系统对接  
✅ **事件驱动架构** - 模块间解耦，易于扩展

## 📚 核心模块使用指南

### 1. 模拟器引擎（SimulatorEngine）

可插拔算法架构，支持动态管理物理模拟算法。

**基本使用：**

```javascript
import { SimulatorEngine } from './physics/SimulatorEngine.js';
import { BuoyancyAlgorithm } from './physics/algorithms/BuoyancyAlgorithm.js';
import { WindAlgorithm } from './physics/algorithms/WindAlgorithm.js';

// 创建模拟器引擎
const simulator = new SimulatorEngine(physicsWorld);

// 注册算法
const buoyancy = new BuoyancyAlgorithm({ buoyancyCoeff: 520 });
simulator.registerAlgorithm(buoyancy);

const wind = new WindAlgorithm({ windSpeed: 10 });
simulator.registerAlgorithm(wind);

// 更新循环中调用
function update(deltaTime) {
  const shipState = { body: boatBody, mesh: boatMesh };
  const environment = { time: elapsed, weather: weatherState };
  
  simulator.update(deltaTime, shipState, environment);
}
```

**添加自定义算法：**

```javascript
import { SimulationAlgorithm } from './physics/SimulatorEngine.js';
import * as CANNON from 'cannon-es';

export class CustomAlgorithm extends SimulationAlgorithm {
  constructor(config) {
    super('CustomName', 50); // name, priority
    this.description = 'My custom algorithm';
    this.config = config;
  }

  initialize(physicsWorld) {
    // 初始化逻辑
  }

  update(deltaTime, shipState, environment) {
    const { body } = shipState;
    
    // 计算力和力矩
    const force = new CANNON.Vec3(0, 100, 0);
    const torque = new CANNON.Vec3(0, 0, 0);
    
    return {
      force,
      torque,
      metadata: { /* 调试信息 */ }
    };
  }

  dispose() {
    // 清理资源
  }
}

// 使用
simulator.registerAlgorithm(new CustomAlgorithm({ param: value }));
```

**算法优先级：**

- 100+：核心算法（浮力）
- 80-99：高优先级（风力、推进）
- 50-79：中优先级（阻尼、碰撞）
- 0-49：低优先级（效果、辅助）

### 2. 天气系统（WeatherSystem）

统一管理风、雨、海况等天气要素。

**基本使用：**

```javascript
import { WeatherSystem } from './weather/WeatherSystem.js';

// 创建天气系统
const weather = new WeatherSystem(scene, simulatorEngine);
weather.initialize();

// 设置天气预设
weather.setWeatherPreset('storm'); // calm, moderate, storm, typhoon

// 或手动设置
weather.setWind(15, 180);  // speed (m/s), direction (degrees)
weather.setRain(25);        // intensity (mm/h)
weather.setSeaState(5);     // 0-9

// 更新循环
weather.update(deltaTime);

// 监听天气变化
weather.on('wind:changed', ({ speed, direction }) => {
  console.log(`Wind: ${speed} m/s from ${direction}°`);
});
```

**天气预设：**

| 预设 | 风速 | 降雨 | 海况 | 适用场景 |
|------|------|------|------|----------|
| calm | 2 m/s | 0 mm/h | 0 | 平静海面 |
| moderate | 10 m/s | 5 mm/h | 3 | 中等海况 |
| storm | 20 m/s | 30 mm/h | 6 | 风暴天气 |
| typhoon | 35 m/s | 80 mm/h | 9 | 台风级别 |

### 3. 数据接口管理器（DataInterfaceManager）

管理虚拟数据源和真实系统的对接。

**基本使用：**

```javascript
import { DataInterfaceManager } from './data/DataInterfaceManager.js';
import { VirtualDataSource } from './data/VirtualDataSource.js';

// 创建管理器
const dataManager = new DataInterfaceManager();

// 注册虚拟数据源（开发阶段）
const virtualSource = new VirtualDataSource({ updateInterval: 1000 });
dataManager.registerDataSource('virtual-ship', virtualSource);

// 绑定虚拟对象到数据源
dataManager.bindData(
  'fuelGauge',              // 虚拟对象ID
  'virtual-ship',           // 数据源ID
  'ship.fuel.level',        // 数据路径
  (value) => value / 100    // 转换函数（可选）
);

// 订阅数据变化
dataManager.subscribe('fuelGauge', (value) => {
  updateFuelGaugeDisplay(value);
});

// 更新循环
dataManager.update(deltaTime);

// 导出配置（保存设置）
const config = dataManager.exportConfig();
localStorage.setItem('dataBindings', JSON.stringify(config));
```

**数据路径示例：**

```javascript
// 基本信息
'ship.info.name'                 // "Digital Twin Vessel"
'ship.info.length'               // 100

// 燃油系统
'ship.fuel.level'                // 75.5 (%)
'ship.fuel.flowRate'             // 12.3 (L/h)
'ship.fuel.remaining'            // 45000 (L)

// 主机状态
'ship.mainEngine.status'         // "Running"
'ship.mainEngine.rpm'            // 1200
'ship.mainEngine.health'         // 95 (%)

// 吊机加速度
'ship.crane.acceleration.x'      // 0.02 (g)
'ship.crane.acceleration.y'      // 0.01 (g)
'ship.crane.acceleration.z'      // 0.03 (g)

// 人员情况
'ship.personnel.total'           // 28
'ship.personnel.locations.bridge' // 3

// 物资仓储
'ship.storage.food.level'        // 68 (%)
'ship.storage.water.liters'      // 49200

// 实验任务
'ship.experiments.completionRate' // 60 (%)
'ship.experiments.current.progress' // 45 (%)

// 应急设备
'ship.emergency.firePump.status'  // "Ready"
'ship.emergency.firePump.health'  // 100 (%)

// 环境数据
'environment.wind.speed'          // 5.2 (m/s)
'environment.wave.height'         // 1.2 (m)
'environment.temperature.air'     // 22.5 (°C)
```

### 4. 连接真实系统

**准备阶段（使用虚拟数据源）：**

```javascript
// 1. 配置虚拟对象和数据绑定
dataManager.bindData('objectId', 'virtual-ship', 'ship.fuel.level');

// 2. 开发可视化组件
function FuelGauge() {
  const unsubscribe = dataManager.subscribe('objectId', (value) => {
    gauge.setValue(value);
  });
}

// 3. 导出配置
const config = dataManager.exportConfig();
```

**生产阶段（连接真实系统）：**

```javascript
// 1. 创建真实数据源（GraphQL/WebSocket/REST）
import { GraphQLDataSource } from './data/GraphQLDataSource.js';

const realSource = new GraphQLDataSource({
  endpoint: 'wss://ship-server.com/graphql',
  token: 'auth-token'
});

// 2. 注册真实数据源
dataManager.registerDataSource('real-ship', realSource);

// 3. 导入之前保存的配置
dataManager.importConfig(savedConfig);

// 4. 连接
await dataManager.connect();

// 虚拟对象会自动接收真实数据！
```

## 🔧 扩展开发

### 添加新的舱室

```javascript
// src/ship/cabins/MyCustomCabin.js
export class MyCustomCabin {
  constructor() {
    this.id = 'custom-cabin';
    this.name = 'Custom Cabin';
    this.type = 'custom';
    this.bounds = new THREE.Box3(
      new THREE.Vector3(-5, 0, -5),
      new THREE.Vector3(5, 3, 5)
    );
  }

  build(scene) {
    // 创建舱室3D模型
    const geometry = new THREE.BoxGeometry(10, 3, 10);
    const material = new THREE.MeshStandardMaterial({ color: 0x808080 });
    const cabin = new THREE.Mesh(geometry, material);
    scene.add(cabin);
    return cabin;
  }

  getCameraConfig() {
    return {
      position: [0, 2, 5],
      target: [0, 1.5, 0],
      fov: 75
    };
  }
}
```

### 添加第一人称控制器

```javascript
// src/scenario/FirstPersonController.js
export class FirstPersonController {
  constructor(camera) {
    this.camera = camera;
    this.position = new THREE.Vector3();
    this.velocity = new THREE.Vector3();
    this.direction = new THREE.Vector3();
    
    this.moveSpeed = 2.0;  // m/s
    this.lookSpeed = 0.002;
    
    this.keys = { w: false, a: false, s: false, d: false };
    
    this._setupControls();
  }

  _setupControls() {
    document.addEventListener('keydown', (e) => {
      if (e.key.toLowerCase() in this.keys) {
        this.keys[e.key.toLowerCase()] = true;
      }
    });
    
    document.addEventListener('keyup', (e) => {
      if (e.key.toLowerCase() in this.keys) {
        this.keys[e.key.toLowerCase()] = false;
      }
    });
    
    document.addEventListener('mousemove', (e) => {
      this.camera.rotation.y -= e.movementX * this.lookSpeed;
      this.camera.rotation.x -= e.movementY * this.lookSpeed;
      this.camera.rotation.x = Math.max(-Math.PI/2, Math.min(Math.PI/2, this.camera.rotation.x));
    });
  }

  update(deltaTime) {
    // 前后左右移动
    this.direction.set(0, 0, 0);
    
    if (this.keys.w) this.direction.z -= 1;
    if (this.keys.s) this.direction.z += 1;
    if (this.keys.a) this.direction.x -= 1;
    if (this.keys.d) this.direction.x += 1;
    
    this.direction.normalize();
    this.direction.applyQuaternion(this.camera.quaternion);
    
    this.velocity.copy(this.direction).multiplyScalar(this.moveSpeed);
    this.position.addScaledVector(this.velocity, deltaTime);
    
    this.camera.position.copy(this.position);
  }
}
```

## 🎨 UI开发

### 创建自定义数据面板

```html
<div id="custom-panel" class="data-panel">
  <h3>燃油系统</h3>
  <div class="gauge" id="fuel-gauge"></div>
  <div class="value" id="fuel-value">--</div>
</div>
```

```javascript
// 绑定数据
dataManager.subscribe('fuelGauge', (value) => {
  document.getElementById('fuel-value').textContent = `${value.toFixed(1)}%`;
  document.getElementById('fuel-gauge').style.width = `${value}%`;
});
```

## 📦 项目结构总结

```
src/
├── physics/              # 物理模拟
│   ├── SimulatorEngine.js     ← 核心：可插拔算法引擎
│   └── algorithms/             ← 各种算法实现
├── weather/              # 天气系统
│   └── WeatherSystem.js       ← 核心：天气管理
├── data/                 # 数据系统
│   ├── DataInterfaceManager.js ← 核心：数据接口管理
│   └── VirtualDataSource.js   ← 虚拟数据源
├── ship/                 # 船舶系统（待实现）
├── monitoring/           # 监控系统（待实现）
├── scenario/             # 场景预演（待实现）
└── sync/                 # 船岸同步（待实现）
```

## 🚀 下一步开发

1. **舱室系统** - 零部件仓库、数据中心、场景切换
2. **实时监控** - HUD显示、仪表盘、状态面板
3. **安全态势** - 设备健康度、应急系统监控
4. **场景预演** - 第一人称视角、路径规划、暴雨漏水场景
5. **船岸同步** - 数据压缩、优先级队列、批次传输
6. **可视化连线编辑器** - 拖拽式数据接口配置

## 💡 最佳实践

1. **算法开发**：继承 `SimulationAlgorithm`，实现 `update()` 方法
2. **数据绑定**：先用虚拟数据源开发，再切换到真实数据源
3. **事件通信**：使用 `EventEmitter` 实现模块解耦
4. **性能优化**：合理设置算法优先级，避免不必要的计算
5. **配置管理**：使用 `exportConfig()` 保存用户配置

## 📞 技术支持

查看 `ARCHITECTURE.md` 了解详细的系统架构设计。

---

**Happy Coding! 🚢⚓**

