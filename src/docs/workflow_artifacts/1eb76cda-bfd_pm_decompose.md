# PM分解 — project_manager

任务: debug test: 在statusbar添加一个version标签
步骤: pm_decompose
Agent: build_pm

---

📋 任务: 1eb76cda-bfd
🤖 Agent: PM (project_manager)
📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
⏱️ 超时: 300s
────────────────────────────────────────────────────────────
📝 提示词:
  你是 PoseidonX 系统的 PM (project_manager)。
  请执行以下开发任务:
  
  你是项目经理 (PM)。请对以下任务进行分解和规划:
  
  ## 任务
  debug test: 在statusbar添加一个version标签
  debug test: 在statusbar添加一个version标签
  
  ## 要求
  1. 分析任务需求，拆解为可执行的子步骤
  2. 识别技术风险和依赖关系
  3. 为后续研究人员、架构师、开发者提供清晰的指导
  4. 输出一份结构化的任务分解文档 (Markdown 格式)
  
  项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  后端: src/backend/ (Python FastAPI)
  前端: src/frontend/ (HTML + JS)
  
  
  项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  后端: src/backend/ (Python FastAPI)
  前端: src/frontend/ (HTML + JS)
  完成后运行: PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short
  
────────────────────────────────────────────────────────────
⏳ 正在启动 Claude Code CLI...

⚠️ Claude CLI 15s 内无输出

🔄 Claude CLI 未响应，切换到 Ollama 直连模式...

🔗 Ollama 直连: 127.0.0.1:11435 | 模型: qwen3.5-35b-claude
────────────────────────────────────────────────────────────

<think>

</think>

# PoseidonX 系统开发任务分解文档
**任务编号**: PX-TASK-202405-001  
**任务标题**: Debug 测试：在状态栏 (Statusbar) 添加版本标签  
**负责人**: Project Manager (AI Agent)  
**状态**: 规划完成，待执行  
**预计工期**: 0.5 - 1.0 人天 (含自测)

---

## 1. 任务需求分析

### 1.1 核心目标
在 PoseidonX 系统前端界面的状态栏（Statusbar）区域新增一个可视化的“版本号”标签，用于调试和测试环境快速识别当前构建版本。

### 1.2 验收标准 (Acceptance Criteria)
- [ ] 前端页面的状态栏底部或导航栏右侧成功渲染版本号（格式建议：`vX.Y.Z` 或 `Build-20240520`）。
- [ ] 版本号与后端服务动态获取的版本号一致（或为硬编码的构建信息，视架构而定）。
- [ ] 页面无控制台报错 (Console Error)。
- [ ] 响应式设计正常，版本号在移动端和桌面端均不被遮挡。
- [ ] **运行测试命令后无故障**: 执行 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short` 通过后。

---

## 2. 任务拆解与执行步骤

### 阶段一：信息收集与定义 (Research & Definition)
*目标：确定版本号的来源和展示形式。*

1.  **确定版本号来源**：
    - 检查 `src/backend/` 现有的版本定义文件（如 `version.py`, `pyproject.toml` 或 `__init__.py`）。
    - 确认后端是否提供获取版本信息的 API（例如 `/api/v1/info`），若无，约定硬编码或从环境变量读取。
2.  **定义 UI 样式**：
    - 确定状态栏现有结构（CSS 类名、HTML 结构）。
    - 确定标签颜色、字体大小、对齐方式（通常靠右，灰色或半透明）。
3.  **确认展示格式**：
    - 格式示例：`PoseidonX v1.0.0 (Debug)`

### 阶段二：后端实现 (Backend Implementation)
*目录：`src/backend/`*

1.  **代码修改**：
    - 如果后端无版本接口，创建一个简单的 FastAPI 路由：
      ```python
      # src/backend/app/routes/system.py
      @app.get("/api/v1/version")
      def get_version():
          return {"version": "1.0.0-dev"} # 需替换为实际版本号获取逻辑
      ```
    - 确保代码符合项目现有的 API 规范。
2.  **依赖注入检查**：
    - 检查 `main.py` 或路由注册模块，确保新路由已包含。

### 阶段三：前端实现 (Frontend Implementation)
*目录：`src/frontend/`*

1.  **HTML 结构修改**：
    - 定位状态栏 HTML 模板文件（如 `statusbar.html` 或 JS 渲染逻辑）。
    - 插入标签元素：`<span id="version-tag"></span>`。
2.  **JavaScript 逻辑实现**：
    - 编写脚本调用后端 `/api/v1/version` 接口。
    - 获取响应数据并 DOM 插入到 `#version-tag`。
    - **降级处理**：若接口调用失败，显示默认值 "Unknown" 或不显示，避免阻碍页面加载。
3.  **样式调整 (CSS)**：
    - 确保 `#version-tag` 的样式与状态栏背景融合，且字体不影响其他功能。

### 阶段四：测试与验证 (Verification)
*目标：确保功能可用且不影响现有测试。*

1.  **手动测试**：
    - 启动后端服务 (`python -m uvicorn ...` 或项目脚本)。
    - 启动前端服务。
    - 在浏览器打开应用，检查版本标签是否显示，点击其他功能是否正常。
2.  **自动化测试执行**：
    - 必须执行项目规定的测试命令，确保未破坏现有逻辑：
      ```bash
      PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short
      ```
    - *注意*：如果测试涉及 API 调用，需确保 `conftest.py` 中 Mock 了新的版本接口（如果测试失败）。

---

## 3. 技术风险与依赖关系识别

| 风险点 | 描述 | 缓解策略 |
| :--- | :--- | :--- |
| **跨域问题 (CORS)** | 若前端和后端运行在不同端口，JS 请求版本接口可能失败。 | 检查 `src/backend/main.py` 中 CORS 配置，确保允许前端源。 |
| **版本获取失败** | 后端配置错误或文件缺失导致 API 500 错误。 | 前端增加 `try-catch` 捕获异常，显示默认文本而非空白。 |
| **状态栏样式破坏** | 新增标签导致状态栏高度溢出或文字重叠。 | 使用 Flexbox 布局预留宽度，或设置 `white-space: nowrap`。 |
| **测试破坏** | 新增代码导致现有测试用例失败。 | 优先运行测试用例进行回归验证；若涉及新 API，在测试配置中 Mock。 |

**依赖关系**:
- **前端依赖**: 后端 `/api/v1/version` 接口必须就绪。
- **构建依赖**: 无外部 NPM 包依赖（仅原生 JS），无后端 Python 新包依赖。

---

## 4. 角色指导 (Actionable Guidance)

### 👨‍💻 给后端开发者 (Backend Dev)
1.  **位置**: `src/backend/app/routes/` 或 `controllers/`。
2.  **行动**:
    - 创建一个 `GET /api/v1/info` 或 `GET /api/v1/version` 接口。
    - 内容返回 JSON: `{"version": "1.0.0"}`。
    - **关键**: 确保该接口不阻塞主请求，响应时间在 50ms 以内。
    - 如果版本号从 `pyproject.toml` 读取，请确保导入逻辑不引入不必要的依赖。

### 🎨 给前端开发者 (Frontend Dev)
1.  **位置**: `src/frontend/js/statusbar.js` 或对应 HTML 文件。
2.  **行动**:
    - 在状态栏 HTML 容器中添加 `<div class="version-info"></div>`。
    - 编写 `fetch('/api/v1/info')` 逻辑。
    - **样式**: 使用 CSS 类 `.version-info { color: #aaa; font-size: 12px; align-self: center; }` (根据实际 UI 调整)。
    - 确保代码无阻塞加载（非同步请求）。

### 🔬 给测试人员/架构师 (QA / Architect)
1.  **验证点**:
    - 检查新版本标签是否在多分辨率屏幕（1920x1080, 1366x768, 手机模拟）中正常显示。
    - 执行命令 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short`。
    - 检查测试日志中是否有 `ConnectionRefused` 或 `Timeout` 新增错误。
2.  **架构审查**:
    - 确认版本信息是否硬编码在前端？(最佳实践：应从后端获取，避免前端发布即失效)。
    - 确认是否已添加到 API 文档 (Swagger/OpenAPI)。

---

## 5. 执行检查清单 (Checklist)

- [ ] **本地启动**: 后端与前端服务启动成功。
- [ ] **接口验证**: 直接访问 `http://localhost:8000/api/v1/version` 返回正确 JSON。
- [ ] **UI 验证**: 页面加载后状态栏显示版本标签。
- [ ] **报错检查**: 浏览器控制台无 Red Errors。
- [ ] **测试通过**: 终端运行 pytest 命令，输出 `passed`。
- [ ] **提交代码**: 代码已 commit 并推送至分支。

---
*文档生成时间：2024-05-20*  
*PoseidonX Project Management Office*

────────────────────────────────────────────────────────────
✅ Ollama 直连完成
