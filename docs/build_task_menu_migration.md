# Build Team 任务: 菜单结构调整 — 货船轨道 侘寂 → AR-CAS Pro

## 任务概述

**任务ID:** TASK-BUILD-20231027-001
**任务标题:** 将"货船轨道 侘寂"菜单项移至"AR-CAS Pro"菜单内
**优先级:** 高
**负责人:** Build团队PM
**预计工时:** 0.5小时

## 验收标准

- [x] 页面菜单结构更新为：AR-CAS Pro > 货船轨道 侘寂
- [x] 原独立菜单项消失，功能正常
- [x] 无残留的 CSS/JS 引用指向已移除的旧元素

---

## 现状分析

### 已完成的工作（无需重复）

经代码审查，`src/frontend/digital-twin.html` 中"货船轨道 侘寂"已经位于 AR-CAS Pro 浮动面板内部：

- **AR-CAS Pro 面板**: 第3506-3594行 (`#ar-cas-floating`)
- **货船轨道 侘寂**: 第3564-3582行 (`#ar-cas-cargo-orbit`)，位于 AR-CAS Pro 面板的 `#ar-cas-body` 内部
- 注释（第3564行）: `<!-- ⛵ 货船轨道 侘寂 (已从独立 HUD 移入 AR-CAS Pro) -->`

### 需要修复的问题

**问题 1: CSS 残留引用（BLOCKER）**

`src/frontend/digital-twin.html` 第102行仍有对已移除的 `#cargo-orbit-hud` 元素的 CSS 引用：

```css
html.cam-mode #cargo-orbit-hud,   /* ← 这个元素已不存在于 DOM 中 */
```

**修复方式:** 删除第102行中对 `#cargo-orbit-hud` 的引用。

---

## 实施步骤

### 步骤 1: 清理 CSS 残留引用

**文件:** `src/frontend/digital-twin.html`
**位置:** 第102行

**修改前:**
```css
html.cam-mode #cargo-orbit-hud,
```

**修改后:**
```css
/* html.cam-mode #cargo-orbit-hud,  /* 已移除，内容已迁入 AR-CAS Pro 面板 */ */
```

或者直接删除该行。

### 步骤 2: 验证

1. 打开 `digital-twin.html` 页面
2. 确认 AR-CAS Pro 面板可以正常展开/折叠
3. 确认"货船轨道 侘寂"内容在 AR-CAS Pro 面板内正常显示
4. 确认 cam-mode（`?cam` 参数）下页面无报错

---

## 技术细节

### 文件列表

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/frontend/digital-twin.html` | 修改（第102行） | 清理已移除元素的 CSS 残留引用 |

### 风险与注意事项

- **无功能风险**: "货船轨道 侘寂"已在 AR-CAS Pro 面板内，本次仅清理 CSS 残留
- **cam-mode 兼容性**: 确保 cam-mode 下 AR-CAS Pro 面板（`#ar-cas-floating`）仍被正确隐藏（已在第102行附近有 `html.cam-mode #ar-cas-floating` 规则）
