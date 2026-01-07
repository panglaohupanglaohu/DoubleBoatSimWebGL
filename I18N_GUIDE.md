# 国际化指南 | Internationalization Guide

## 📋 当前状态 | Current Status

**版本 | Version**: v2.1.0-bilingual  
**语言支持 | Language Support**: 中文 + English（双语显示 | Bilingual Display）  
**未来计划 | Future Plan**: 完整国际化支持（可切换语言 | Switchable Languages）

## 🎯 设计理念 | Design Philosophy

### 为什么使用双语模式？| Why Bilingual Mode?

1. **过渡方案 | Transition Solution**
   - 当前阶段保持中英文同时显示
   - 为将来的多语言支持做好准备
   - 用户无需切换即可看到两种语言

2. **技术准备 | Technical Preparation**
   - 所有文本集中管理在 `src/utils/i18n.js`
   - 统一的文本格式：`中文 | English`
   - 易于扩展为完整的国际化系统

3. **用户体验 | User Experience**
   - 中英文用户都能理解界面
   - 专业术语同时展示，减少歧义
   - 适合国际合作项目

## 📁 文件结构 | File Structure

```
src/utils/i18n.js          # 国际化配置文件 | i18n configuration
  ├── i18n                  # 双语文本对象 | Bilingual text object
  ├── getText()             # 获取文本函数 | Get text function
  └── formatBilingual()     # 格式化函数 | Format function

src/demo-refactored.js     # 使用双语文本 | Using bilingual text
index-refactored.html      # 双语HTML界面 | Bilingual HTML interface
```

## 🔧 使用方法 | Usage

### 1. 在 JavaScript 中使用 | Using in JavaScript

```javascript
import { i18n, getText } from './utils/i18n.js';

// 方法1：直接访问（推荐 | Recommended）
const title = i18n.gui.title;
// 输出 | Output: "🚢 数字孪生控制面板 | Digital Twin Control Panel"

// 方法2：使用路径访问
const amplitude = getText('wave.amplitude');
// 输出 | Output: "波高 | Amplitude"

// 方法3：动态拼接
import { formatBilingual } from './utils/i18n.js';
const text = formatBilingual('测试', 'Test');
// 输出 | Output: "测试 | Test"
```

### 2. 在 GUI 中使用 | Using in GUI

```javascript
// 创建文件夹
const folder = gui.addFolder(i18n.wave.folder);
// 显示 | Display: "🌊 波浪参数 | Wave Parameters"

// 添加控件
folder.add(params, 'value', 0, 100)
  .name(i18n.wave.amplitude);
// 显示 | Display: "波高 | Amplitude"
```

### 3. 在 HTML 中使用 | Using in HTML

```html
<!-- 标题 -->
<h1>🚢 船舶数字孪生系统 | Ship Digital Twin System</h1>

<!-- 说明文字 -->
<p>拖动旋转 | Drag to rotate • 滚轮缩放 | Scroll to zoom</p>

<!-- 徽章 -->
<span class="badge">✅ 可插拔模拟器 | Pluggable Simulator</span>
```

## 📝 添加新文本 | Adding New Text

### 步骤 | Steps

1. **编辑配置文件 | Edit Configuration File**

在 `src/utils/i18n.js` 中添加：

```javascript
export const i18n = {
  // 现有内容...
  
  // 添加新的模块
  newModule: {
    folder: '📦 新模块 | New Module',
    parameter1: '参数1 | Parameter 1',
    parameter2: '参数2 | Parameter 2',
    button: '🔘 按钮 | Button'
  }
};
```

2. **在代码中使用 | Use in Code**

```javascript
const folder = gui.addFolder(i18n.newModule.folder);
folder.add(config, 'param1').name(i18n.newModule.parameter1);
```

## 🌍 未来国际化计划 | Future Internationalization Plan

### Phase 1: 双语模式（当前 | Current）✅
- ✅ 所有界面文本双语显示
- ✅ 统一文本管理
- ✅ 格式规范化

### Phase 2: 多语言支持（计划中 | Planned）
- [ ] 添加语言切换功能
- [ ] 支持更多语言（日语、韩语等）
- [ ] 动态语言加载
- [ ] 本地存储语言偏好

### Phase 3: 完整国际化（未来 | Future）
- [ ] 日期/时间本地化
- [ ] 数字格式本地化
- [ ] 单位转换（公制/英制）
- [ ] 右到左语言支持

## 🔄 迁移到完整国际化 | Migration to Full i18n

### 当前格式 | Current Format
```javascript
// 双语字符串
text: "中文 | English"
```

### 未来格式 | Future Format
```javascript
// 分离语言
text: {
  zh: "中文",
  en: "English",
  ja: "日本語",
  ko: "한국어"
}

// 使用函数获取当前语言
const text = i18n.t('wave.amplitude', currentLanguage);
```

### 迁移工具（待开发 | To Be Developed）
```javascript
// 自动转换脚本
function convertToMultiLingual(bilingualText) {
  const parts = bilingualText.split(' | ');
  return {
    zh: parts[0],
    en: parts[1]
  };
}
```

## 📐 文本格式规范 | Text Format Standards

### 1. 双语分隔符 | Bilingual Separator
- 使用 ` | `（空格+竖线+空格）
- 中文在前，English在后
- 保持一致性

✅ **正确 | Correct**:
```javascript
"波高 | Amplitude"
"风速 | Wind Speed (m/s)"
```

❌ **错误 | Wrong**:
```javascript
"波高|Amplitude"        // 缺少空格
"Amplitude | 波高"      // 顺序错误
"波高 - Amplitude"      // 分隔符错误
```

### 2. 单位标注 | Unit Notation
```javascript
// 单位放在英文后面
"风速 | Wind Speed (m/s)"
"质量 | Mass (kg)"

// 不要重复单位
❌ "风速(m/s) | Wind Speed (m/s)"
✅ "风速 | Wind Speed (m/s)"
```

### 3. Emoji 使用 | Emoji Usage
```javascript
// Emoji 放在最前面
"🌊 波浪参数 | Wave Parameters"
"⚓ 浮力系统 | Buoyancy System"
"🔄 重置 | Reset"
```

### 4. 按钮和操作 | Buttons and Actions
```javascript
// 使用动词
"🔄 重置船体 | Reset Boat"
"📍 聚焦船体 | Focus Boat"
"✅ 启用 | Enable"
```

## 🎨 示例集合 | Example Collection

### GUI 文件夹命名 | GUI Folder Names
```javascript
"🌊 波浪参数 | Wave Parameters"
"⛈️ 天气系统 | Weather System"
"⚙️ 算法管理 | Algorithms"
"⚓ 浮力与稳定性 | Buoyancy & Stability"
"👁️ 显示选项 | Display Options"
```

### 参数名称 | Parameter Names
```javascript
"波高 | Amplitude"
"波长 | Wavelength"
"风速 | Wind Speed (m/s)"
"吃水深度 | Draft Depth (m)"
"自稳刚度 | Stabilizer Stiffness"
```

### 状态信息 | Status Information
```javascript
"船体状态 | Ship Status"
"天气状态 | Weather Status"
"位置 | Position"
"质量 | Mass"
"能见度 | Visibility"
```

### 操作按钮 | Action Buttons
```javascript
"🔄 重置船体 | Reset Boat"
"📍 聚焦船体 | Focus Boat"
"✅ 启用自稳 | Enable Stabilizer"
"🔘 开始模拟 | Start Simulation"
```

## 🛠️ 开发者注意事项 | Developer Notes

### 1. 添加新功能时 | When Adding New Features
- ✅ **必须**在 `i18n.js` 中添加双语文本
- ✅ **必须**遵循格式规范
- ✅ **必须**更新此文档

### 2. 文本长度考虑 | Text Length Considerations
```javascript
// 考虑长文本显示
// GUI宽度已调整为 360px 以容纳双语文本
const gui = new GUI({ width: 360 });
```

### 3. 特殊字符处理 | Special Character Handling
```javascript
// 使用 HTML 实体或 Unicode
"角度 | Angle (°)"      // ° 度数符号
"小于等于 | Less than or equal (≤)"
```

## 📊 当前覆盖率 | Current Coverage

| 模块 | 双语覆盖 | 状态 |
|------|----------|------|
| GUI 控制面板 | 100% | ✅ |
| HTML 界面 | 100% | ✅ |
| 状态显示 | 100% | ✅ |
| 控制台日志 | 部分 | 🟡 |
| 注释文档 | 部分 | 🟡 |

## 🔗 相关文档 | Related Documents

- [重构更新日志 | Refactoring Changelog](./REFACTORING_CHANGELOG.md)
- [开发指南 | Development Guide](./DEVELOPMENT_GUIDE.md)
- [架构文档 | Architecture](./ARCHITECTURE.md)

---

## 💡 常见问题 | FAQ

**Q: 为什么不直接做多语言切换？| Why not implement language switching directly?**  
A: 当前阶段双语显示更适合项目需求，同时为将来扩展做好准备。

**Q: 如何添加第三种语言？| How to add a third language?**  
A: 目前不支持，需要等待 Phase 2 的完整国际化实现。

**Q: 文本太长怎么办？| What if text is too long?**  
A: GUI 宽度已增加到 360px，如仍然不够可使用缩写或换行。

**Q: 是否需要翻译代码注释？| Should code comments be translated?**  
A: 建议重要注释使用双语，普通注释可以只用英文。

---

**维护者 | Maintainer**: Digital Twin Development Team  
**最后更新 | Last Updated**: 2025-12-25  
**版本 | Version**: v2.1.0

