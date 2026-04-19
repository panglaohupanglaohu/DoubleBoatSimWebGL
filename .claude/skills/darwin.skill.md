# 达尔文 · 棘轮演化 Skill (Darwin Ratchet Evolution)

> 自然选择 + 棘轮机制 (Muller's Ratchet reversed) — 系统只增不减地积累有益特性

## 核心理念

**棘轮机制 (Ratchet Mechanism)**:
1. 每一次演化产生一个新特性 (Feature / Mutation)
2. 通过适应度测试 (Fitness Test): 通过则固化为"已锁定"
3. 已锁定的特性不可回退、不可删除（只进不退 = 棘轮）
4. 未通过的特性进入"实验池"继续迭代直至通过或被替代

## 工作流

```
观察 (Observe) → 变异 (Mutate) → 选择 (Select) → 固化 (Lock) → 累积 (Accumulate)
    ↑                                                                    │
    └────────────── 永不回退的特性棘轮 ←──────────────────────────────┘
```

## 在本项目中的应用

### 范围 (Scope)
- 数字孪生页面 `digital-twin.html`
- 后端 Channel `src/backend/channels/`
- 前端可视化组件

### 棘轮状态持久化
- 浏览器端: `localStorage['poseidonx.ratchet']`
- 服务端: `storage/ratchet/evolution_log.jsonl`

### 演化项分类 (Category)
| 类别 | 颜色 | 示例 |
|------|------|------|
| scene | 🎨 青 | 船舱内饰 / 天空 / 灯光 |
| ui | 🟣 紫 | 面板 / 按钮 / 快捷键 |
| data | 🟢 绿 | AIS 融合 / 冰山检测 |
| physics | 🟠 橙 | 波浪 / 浮力 / 姿态 |
| ai | 🔴 红 | COLREGs / 决策编排 |
| safety | 🟡 黄 | 避碰 / 火灾 / MOB |

### Fitness 评分
- ✅ pass: 单元测试通过 + 手动验收通过 → 锁定
- 🟡 pending: 已实现, 待验收
- 🔴 reject: 验收失败 → 进入实验池重试

### 锁定后保证
- 代码与 UI 不会在后续变更中被移除
- 其他特性的改动不能破坏已锁定特性的行为
- 违反时, 测试必须失败

## 使用方式

### 前端 API
```js
window.Darwin.record({
  id: 'cabin-interiors-v1',
  title: '6 舱室 3D 内饰',
  category: 'scene',
  description: '驾驶台/机舱/ECR/货舱/船员舱/厨房',
  fitness: 'pass'
});

window.Darwin.list();         // 列出所有演化项
window.Darwin.locked();       // 只列出已锁定
window.Darwin.stats();        // 统计: {total, locked, pending, reject}
```

### 后端 (Python)
```python
from pathlib import Path
import json, datetime

def ratchet_record(item):
    fp = Path('storage/ratchet/evolution_log.jsonl')
    fp.parent.mkdir(parents=True, exist_ok=True)
    item['ts'] = datetime.datetime.utcnow().isoformat()
    with fp.open('a') as f:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')
```

## 数字孪生页面已记录的演化项

1. cabin-interiors-v1 — 6 舱室 3D 内饰
2. cabin-split-screen-v1 — 分屏舱室信息系统
3. cabin-search-keywords-v1 — 搜索框识别舱室中文名
4. ar-cas-floating-v2 — AR-CAS Pro 可拖拽独立面板
5. ar-cas-enriched-v1 — AR-CAS Pro 本船/环境/COLREGs建议
6. ais-iceberg-merge-v1 — AIS 列表聚合本地冰山+货船
7. day-mode-lighting-v1 — 日间模式亮化 + 天空着色器
8. cabin-dropdown-menu-v1 — 舱室快速进入下拉菜单
9. sky-shader-day-v1 — 程序化天空 (日间蓝)
10. darwin-ratchet-v1 — 达尔文棘轮机制本身

## 棘轮保证

一旦某演化项 `fitness === 'pass'` 被记录, 即表示:
> **此特性永久保留, 不可回退, 后续开发必须兼容之**
