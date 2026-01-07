# 重构更新日志

## 🎉 v2.1.0 - 完整功能整合

### ✅ 新增核心类

#### 1. **ShipController** (`src/ship/ShipController.js`)
完整的船舶控制器类，封装所有船体操作：

**功能**：
- ✅ GLB模型加载（多路径尝试 + 盒子后备）
- ✅ 自动缩放到目标尺寸（100米）
- ✅ 物理体创建和管理
- ✅ 船体姿态控制（reset, placeOnWater）
- ✅ 质量和吃水深度动态调整
- ✅ 坐标轴辅助器（可切换）
- ✅ 状态查询

**使用示例**：
```javascript
const shipController = new ShipController(scene, world, {
  mass: 20000,
  draftDepth: 10,
  size: { x: 100, y: 10, z: 20 }
});

await shipController.load();
shipController.placeOnWater(time);
shipController.reset();
```

#### 2. **StabilizerAlgorithm** (`src/physics/algorithms/StabilizerAlgorithm.js`)
自稳系统算法，提供船体恢复直立的力矩：

**参数**：
- `enableStabilizer` - 启用/禁用自稳
- `uprightStiffness` - 自稳刚度（0-15）
- `uprightDamping` - 自稳阻尼（0-10）
- `wobbleBoost` - 摇晃增强系数（>1=更摇晃）

**物理原理**：
```
自稳力矩 = (船体上方向 × 世界上方向) × 刚度 - 角速度 × 阻尼
有效刚度 = 刚度 / wobbleBoost
```

### 📦 从 main.js 提取的功能

#### ✅ 完全迁移的功能

1. **自稳系统**
   - ✅ 原版 `applyUprightTorque()` → `StabilizerAlgorithm`
   - ✅ 所有参数保持一致
   - ✅ 可通过GUI动态调整

2. **吃水深度控制**
   - ✅ `draftDepth` 参数
   - ✅ `placeBoatOnWater()` 函数
   - ✅ 动态调整并立即生效

3. **船体操作**
   - ✅ `resetBoatPose()` → `shipController.reset()`
   - ✅ `focusBoat()` → 聚焦并重置船体
   - ✅ 质量动态调整

4. **坐标轴辅助器**
   - ✅ 显示/隐藏切换
   - ✅ X/Y/Z标签显示
   - ✅ 跟随船体移动

5. **状态显示**
   - ✅ 船体位置、质量
   - ✅ 水面高度
   - ✅ 离水面距离
   - ✅ 完整天气信息

### 🎨 GUI 增强

#### 新增控制面板

**⚓ Buoyancy & Stability**（原Buoyancy扩展）：
- 浮力系数（200-1200）
- 阻尼系数（0-20）
- 水密度（0.5-2.0）⭐ 新增
- 船体质量（1000-100000 kg）⭐ 新增
- 吃水深度（-5 to 25 m）⭐ 新增
- **启用自稳系统**⭐ 新增
- **自稳刚度**（0-15）⭐ 新增
- **自稳阻尼**（0-10）⭐ 新增
- **摇晃增强**（0.2-5.0）⭐ 新增
- 🔄 重置船体

**⚙️ Algorithms**：
- Buoyancy (P100)
- **Stabilizer (P90)**⭐ 新增
- Wind (P80)
- Rain (P70)
- 每个都可独立启用/禁用

**👁️ Display**：
- 显示天气指示器
- 水面线框
- **显示坐标轴**⭐ 新增
- **📍 聚焦船体**⭐ 新增

### 🔄 代码对比

#### 原版 (main.js)
```javascript
// 分散的全局变量
let boatMesh, boatBody, buoyancyPointsLocal;

// 分散的函数
function applyBuoyancyForces() { ... }
function applyUprightTorque() { ... }
function resetBoatPose() { ... }

// 在animate中调用
applyBuoyancyForces(elapsed);
applyUprightTorque();
```

#### 重构版 (demo-refactored.js)
```javascript
// 统一的船舶控制器
const shipController = new ShipController(scene, world, config);

// 算法注册
simulatorEngine.registerAlgorithm(new BuoyancyAlgorithm());
simulatorEngine.registerAlgorithm(new StabilizerAlgorithm());

// 在animate中统一调用
simulatorEngine.update(deltaTime, shipState, environment);
shipController.update(deltaTime);
```

### 📊 算法优先级

| 算法 | 优先级 | 功能 |
|------|--------|------|
| Buoyancy | 100 | 多点浮力计算 |
| **Stabilizer** | **90** | **自稳力矩** ⭐ |
| Wind | 80 | 风力影响 |
| Rain | 70 | 降雨影响 |

优先级高的先执行，所有力和力矩最后统一施加到船体。

### 🎯 功能完整度对比

| 功能 | 原版 | 重构版 |
|------|------|--------|
| 浮力系统 | ✅ | ✅ |
| 自稳系统 | ✅ | ✅ |
| 天气系统 | ❌ | ✅ |
| 吃水深度 | ✅ | ✅ |
| 船体重置 | ✅ | ✅ |
| 聚焦船体 | ✅ | ✅ |
| 坐标轴辅助 | ✅ | ✅ |
| 质量调整 | ✅ | ✅ |
| 算法管理 | ❌ | ✅ |
| 模型自动加载 | ✅ | ✅ |
| 数据接口 | ❌ | ✅ |

**结论**：✅ 重构版包含原版所有功能 + 新增扩展功能

### 🚀 改进点

1. **代码组织**
   - ✅ 从分散的函数 → 类和模块
   - ✅ 从全局变量 → 封装的控制器
   - ✅ 从硬编码 → 可配置参数

2. **可维护性**
   - ✅ 算法独立，易于测试
   - ✅ 船体操作集中管理
   - ✅ 清晰的职责划分

3. **可扩展性**
   - ✅ 新增算法只需2行代码
   - ✅ 新增船舶类型无需修改核心代码
   - ✅ 数据接口预留完善

4. **用户体验**
   - ✅ 更多可调参数
   - ✅ 更直观的控制面板
   - ✅ 实时状态反馈

### 📝 迁移指南

#### 如果你要从原版迁移到重构版：

**步骤1**：更新引用
```javascript
// 原版
if (boatBody) { ... }

// 重构版
if (shipController && shipController.body) { ... }
```

**步骤2**：更新操作
```javascript
// 原版
boatBody.position.set(0, 10, 0);
boatBody.velocity.setZero();

// 重构版
shipController.reset();
```

**步骤3**：使用算法系统
```javascript
// 原版
function applyMyForce() {
  const force = new CANNON.Vec3(0, 100, 0);
  boatBody.applyForce(force, boatBody.position);
}

// 重构版
class MyAlgorithm extends SimulationAlgorithm {
  update(dt, ship, env) {
    return { force: new CANNON.Vec3(0, 100, 0) };
  }
}
simulatorEngine.registerAlgorithm(new MyAlgorithm());
```

### 🐛 已知问题 & 解决方案

**问题1**：首次加载可能看不到船模型
**解决**：刷新页面（Ctrl+Shift+R）清除缓存

**问题2**：船体位置初始不在水面
**解决**：加载完成后自动调用 `placeOnWater()`

**问题3**：算法禁用后GUI值还在变
**解决**：算法禁用时不会施加力，只是GUI不同步（正常）

### 📚 相关文档

- 架构设计：[ARCHITECTURE.md](./ARCHITECTURE.md)
- 开发指南：[DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md)
- 项目总结：[PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)
- 参数说明：[README.md](./README.md)

---

## 🎊 总结

✅ **原版所有功能已完整迁移**  
✅ **代码质量显著提升**  
✅ **架构更加清晰和可扩展**  
✅ **用户体验更加友好**

**访问重构版Demo**：
```
http://localhost:3000/index-refactored.html
```

**Happy Sailing! ⚓🌊**

