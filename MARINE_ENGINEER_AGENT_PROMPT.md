# 供 OpenClaw marine_engineer_agent 使用的代码分析请求

**使用方式**：在 OpenClaw 中选中或调用 `marine_engineer_agent`，将下方「发给 agent 的提问」整段复制粘贴，并根据需要附上本仓库中的相关源文件（或本文件中的代码摘要），请其从船舶工程与代码实现双重视角做问题分析。

---

## 发给 agent 的提问（可直接复制）

```
请以船舶工程师和代码审查双重身份，对下面这段船舶数字孪生/仿真相关代码做问题分析。

背景：
- 项目：DoubleBoatSimWebGL，基于 Three.js + Cannon-es 的 WebGL 船舶仿真，含浮力、自稳、天气、Poseidon-X 智能体等。
- 船型：138 米双体客船，排水量约 37000 吨，两片体中心距 80 m，单船体宽约 26 m，吃水约 5.5 m。
- 已有模块：浮力算法(BuoyancyAlgorithm)、自稳算法(StabilizerAlgorithm)、双体船稳性(CatamaranStability)、船舶运动响应(ShipMotionResponse)、Poseidon 的 MarineEngineeringModule 与 EnhancedEngineerAgent。

请重点分析并指出：
1) 船舶工程/规范方面：公式是否与 IMO、ISO 或常用船舶理论一致？单位、符号、常数是否合理？双体船 GMt、BMt、横摇/纵摇周期、GZ 曲线等计算是否有误或存在简化不当？
2) 代码实现方面：参数传递顺序、单位混用（如吨 vs kg）、与物理引擎(Cannon)的衔接是否一致？是否有明显 bug 或易导致误用的接口？
3) 优化与安全：对极端海况（如 17 级台风）、大倾角稳性、晕船/舒适度等是否有改进空间？与物理仿真闭环（浮力/自稳参数与稳性模块的反馈）是否缺失？

请按「问题描述 + 位置/引用 + 建议修改」格式逐条列出，并标注严重程度（严重/中等/建议）。
```

---

## 代码摘要（可一并粘贴给 agent）

### 1. 双体船 GMt / BMt / 横摇周期（CatamaranStability.js）

```javascript
// BMt 横稳心半径 (双体船简化)
// BMt ≈ (hullSpacing² - beam²) / (12 * draft)
const BMt = (hullSpacing * hullSpacing - beam * beam) / (12 * this.config.defaultDraft);
const GMt = KB + BMt - KG;

// 横摇周期 Tr = 2π * B / √(GMt * g)
const Tr = 2 * Math.PI * B / Math.sqrt(GMt * g);

// 纵摇周期 Tp = 2π * L / √(GMl * g)
const Tp = 2 * Math.PI * length / Math.sqrt(GMl * g);
```

### 2. 浮力算法（BuoyancyAlgorithm.js）关键参数

```javascript
// 船体质量 37,000,000 kg，约 95 个浮力点，双体两列 + 中心线
this.buoyancyCoeff = config.buoyancyCoeff || 40000000;
// 双体船浮力点：左列 x=-40m，右列 x=+40m，沿 Z 轴（船长 138m）每 3m 一个点
const catamaranSpacing = 80.0;
```

### 3. 自稳算法（StabilizerAlgorithm.js）

```javascript
// 自稳力矩 = 恢复力矩 - 阻尼力矩
// restoreTorque = axis * angle * stiffness, dampingTorque = angularVelocity * damping
const effStiffness = this.uprightStiffness / wobble;
const effDamping = this.uprightDamping / wobble;
const totalTorque = restoreTorque.vsub(dampingTorque);
```

### 4. MarineEngineeringModule 调用稳性计算（已修复前）

```javascript
// 正确调用应为：calculateGMt(displacement, hullSpacing, beam)
const gmData = this.stabilityCalc.calculateGMt(
  this.config.displacement,
  this.config.hullSpacing,  // 80 m，两片体中心距
  this.config.beam          // 26 m，单船体宽
);
```

### 5. POSEIDON 文档中的公式（POSEIDON_OPTIMIZATION.md）

```text
GMt = KB + BMt - KG
BMt = (hullSpacing² - beam²) / (12 * draft)
Tr = 2π * B / √(GMt * g)
Tp = 2π * L / √(GMl * g)
```

---

## 已发现并修复的问题（可作 agent 对照）

| 问题 | 位置 | 修复 |
|------|------|------|
| `calculateGMt` 参数顺序错误 | `MarineEngineeringModule.js` 中调用 `this.stabilityCalc.calculateGMt(displacement, beam, draft)` | 改为 `calculateGMt(displacement, hullSpacing, beam)`，并在 config 中增加 `hullSpacing: 80`。 |

---

## 建议让 agent 重点看的文件路径

- `src/physics/CatamaranStability.js` — 双体船 GMt、BMt、GZ、横摇/纵摇周期
- `src/physics/algorithms/BuoyancyAlgorithm.js` — 浮力点分布与系数
- `src/physics/algorithms/StabilizerAlgorithm.js` — 自稳力矩与阻尼
- `src/poseidon/MarineEngineeringModule.js` — 稳性监控与 IMO 检查
- `src/physics/ShipMotionResponse.js` — 运动响应 / RAO（若有）

完成上述粘贴后，即可在 OpenClaw 中向 marine_engineer_agent 发起请求，获取更专业的船舶工程与实现层面的分析结果。
