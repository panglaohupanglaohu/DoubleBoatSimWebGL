# 架构设计 — architect

任务: 优化航海日志可视化
步骤: architecture
Agent: build_architect

---

📋 任务: 06c160fe-9b6
🤖 Agent: Architect (architect)
📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
⏱️ 超时: 300s
────────────────────────────────────────────────────────────
📝 提示词:
  你是 PoseidonX 系统的 Architect (architect)。
  请执行以下开发任务:
  
  你是系统架构师。请为以下任务设计技术方案:
  
  ## 任务
  优化航海日志可视化
  在前端添加航海日志的时间轴视图
  
  ## 前序步骤的产出 (请仔细阅读)
  
  ## 上一步产出 — PM分解 (project_manager)
  
  # PM分解 — project_manager
  
  任务: 优化航海日志可视化
  步骤: pm_decompose
  Agent: build_pm
  
  ---
  
  📋 任务: 06c160fe-9b6
  🤖 Agent: PM (project_manager)
  📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  ⏱️ 超时: 300s
  ────────────────────────────────────────────────────────────
  📝 提示词:
    你是 PoseidonX 系统的 PM (project_manager)。
    请执行以下开发任务:
    
    你是项目经理 (PM)。请对以下任务进行分解和规划:
    
    ## 任务
    优化航海日志可视化
    在前端添加航海日志的时间轴视图
    
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
  🔗 使用 Ollama 直连模式
  
  🔗 Ollama 直连: 127.0.0.1:11435 | 模型: qwen3.5-35b-claude
  ────────────────────────────────────────────────────────────
  
  <think>
  
  </think>
  
  # PoseidonX 系统任务分解文档：航海日志可视化优化
  
  **文档版本**: 1.0.0  
  **日期**: 2023-10-27  
  **项目经理 (PM)**: PoseidonX_PM  
  **涉及系统模块**: 可视化模块 (Vis), 日志服务 (Log Service), 前端核心 (Frontend Core)
  
  ---
  
  ## 1. 需求分析与功能拆解
  
  ### 1.1 核心目标
  在现有 PoseidonX 系统的 HTML/JS 前端中集成一个**航海日志时间轴视图**。该视图需以时间顺序直观展示船舶航行过程中的关键事件（如定位、机械状态、异常报警等），支持滚动、缩放及事件详情查看。
  
  ### 1.2 任务拆解 (WBS)
  
  我们将任务拆解为四个主要阶段：**数据层适配**、**数据可视化组件开发**、**前端交互集成**、**测试与验收**。
  
  #### 阶段一：后端数据层适配 (Data Layer)
  *负责团队：后端开发者 (Python/FastAPI)*
  1.  **数据模型梳理**：确认日志表结构，提取关键时间字段（`log_time`）、事件类型（`event_type`）、内容（`content`）。
  2.  **API 接口开发**：
      *   新增 `/api/v1/logs/timeline` 接口。
      *   支持参数：`start_time`, `end_time`, `page_size`, `cursor` (用于分页/无限滚动)。
      *   返回格式：JSON，包含排序后的日志列表及元数据。
  3.  **索引优化**：在 PostgreSQL/SQLite 中对时间字段添加索引，确保时间轴数据加载延迟 < 200ms。
  
  #### 阶段二：可视化组件开发 (UI Component)
  *负责团队：前端开发者 (HTML/JS)*
  1.  **选型与初始化**：
      *   方案 A（轻量级）：使用原生 SVG 或 Canvas 绘制自定义时间轴（推荐，减少依赖）。
      *   方案 B（库支持）：引入轻量级图表库（如 `Chart.js` 或 `Furnace.js`）的特定插件。
      *   *决策*：鉴于项目采用原生 HTML+JS，建议优先采用 **自定义 SVG 渲染** 或 **轻量级库 (vis-timeline)** 以获得最佳兼容性。
  2.  **布局设计**：
      *   设计响应式容器，支持 PC 端宽屏展示和移动端滚动展示。
      *   定义时间轴刻度样式（年/月/日/时）。
  3.  **事件点渲染**：
      *   绘制不同类别的节点（颜色区分：正常、警告、错误）。
      *   实现节点悬浮提示 (Tooltip) 显示详情。
  
  #### 阶段三：前端交互集成 (Integration)
  *负责团队：前端开发者 + UI 设计师*
  1.  **路由挂载**：在现有前端结构中增加“航海日志”入口页面或 Modal。
  2.  **数据流对接**：编写 JS 逻辑调用后端 API，处理加载状态 (Loading)、空状态 (Empty) 和错误处理 (Error)。
  3.  **交互逻辑**：
      *   实现时间范围筛选器。
      *   支持点击节点钻取查看详情。
      *   支持时间轴拖拽缩放（若使用库则内置，自研需实现缩放算法）。
  
  #### 阶段四：测试与验收 (QA)
  *负责团队：全栈工程师*
  1.  **单元测试**：覆盖 API 分页逻辑及前端数据解析逻辑。
  2.  **集成测试**：验证大数据量（如 >1000 条日志）下的渲染性能。
  3.  **验收标准**：符合设计稿，无布局断裂，API 响应时间达标。
  
  ---
  
  ## 2. 技术风险与依赖关系识别
  
  ### 2.1 技术风险 (Risks)
  
  | 风险等级 | 风险描述 | 缓解方案 |
  | :--- | :--- | :--- |
  | **高** | **大数据量渲染卡顿**：若日志量超过 10,000 条，原生 DOM/SVG 渲染可能导致页面冻结。 | 1. 后端强制分页/游标分页。<br>2. 前端采用虚拟滚动 (Virtual Scrolling) 或 Canvas 渲染。<br>3. 限制初始加载数量（如 50 条），采用无限下拉加载。 |
  | **中** | **第三方库依赖冲突**：引入外部图表库可能污染全局命名空间或样式冲突。 | 1. 优先评估原生实现可行性。<br>2. 若引入库，使用 Shadow DOM 或严格封装 CSS Scope。<br>3. 锁定库版本。 |
  | **中** | **时区处理不一致**：后端存储与前端展示时区不一致导致时间轴偏移。 | 1. 确立统一时区标准（建议后端始终存 UTC，前端根据用户环境转换）。<br>2. 数据接口明确返回 ISO 8601 格式。 |
  
  ### 2.2 依赖关系 (Dependencies)
  
  *   **强依赖**：
      *   后端 API 开发进度 -> 前端数据对接。
      *   数据库索引建立 -> 前端列表加载性能。
  *   **弱依赖**：
      *   UI 设计规范图 -> 前端组件样式实现。
  
  ---
  
  ## 3. 角色执行指导
  
  ### 🧪 给研究人员 (Researchers)
  *   **关注点**：数据定义与业务逻辑。
  *   **行动项**：
      *   确认“航海日志”的具体事件类型分类标准（Tagging System）。
      *   定义时间轴上需要高亮显示的特殊事件阈值（例如：航速异常超过某值自动标红）。
      *   提供历史数据样本，用于前端性能测试的数据集。
  
  ### 🏗️ 给架构师 (Architects)
  *   **关注点**：性能架构与数据流。
  *   **行动项**：
      *   审核 `/api/v1/logs/timeline` 的 SQL 查询计划，确保 `WHERE` 子句利用索引。
      *   决定时间轴渲染技术栈（Canvas vs DOM）。考虑到项目路径 `src/frontend` 为 HTML+JS，若无现成库，建议**引入 `vis-timeline` (CDN 或本地) 以降低自研成本**。
      *   制定接口限流策略，防止前端轮询或大数据拉取拖垮服务。
  
  ### 👨‍💻 给开发者 (Developers)
  *   **行动项**：
      *   **后端**：快速在 `src/backend/routes/` 下创建 `timeline.py`，完成分页逻辑。
      *   **前端**：在 `src/frontend/views/` 创建 `timeline.html` 及 `timeline.js`。
      *   **代码规范**：
          *   后端：遵循 FastAPI 风格，使用 Pydantic 进行数据模型校验。
          *   前端：使用模块化写法（ES6 Modules），避免全局变量污染。
      *   **测试执行**：
          *   开发完成后，务必运行项目要求的测试命令：
          ```bash
          cd /Users/panglaohu/Downloads/DoubleBoatClawSystem
          PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short
          ```
          *   确保所有测试用例通过，特别是针对 API 时间筛选的测试。
  
  ---
  
  ## 4. 开发路线图 (Timeline)
  
  | 阶段 | 任务描述 | 预计工时 | 负责人 | 交付物 |
  | :--- | :--- | :--- | :--- :--- |
  | **T+1** | 后端 API 设计与开发 (`/timeline`) | 4h | Backend Dev | API 文档、单元测试 |
  | **T+2** | 架构图定稿与组件选型确认 | 2h | Architect | 技术选型确认书 |
  | **T+3~4** | 前端时间轴组件开发 (渲染/交互) | 12h | Frontend Dev | 可交互的 HTML/JS 文件 |
  | **T+5** | 前后端联调与边界测试 | 4h | Full Stack | 集成测试结果 |
  | **T+6** | 性能优化与全量测试 | 4h | QA/Dev | 最终测试报告 |
  
  ---
  
  ## 5. 下一步行动 (Next Steps)
  
  1.  **Architecture Review**：请架构师在 [时间] 前确认时间轴渲染技术方案（自研 vs 开源库）。
  2.  **API Spec**：后端团队请在 [时间] 前提交 API 接口文档。
  3.  **环境准备**：前端团队准备测试环境数据，运行本地开发服务。
  
  **项目经理备注**：请务必关注数据量级的影响，避免在首页直接加载全量日志。时间轴的核心价值在于“可探索性”，而非“全量展示”。
  
  ────────────────────────────────────────────────────────────
  ✅ Ollama 直连完成
  
  
  
  ## 上一步产出 — 研究分析 (researcher)
  
  # 研究分析 — researcher
  
  任务: 优化航海日志可视化
  步骤: research
  Agent: build_researcher
  
  ---
  
  📋 任务: 06c160fe-9b6
  🤖 Agent: Researcher (researcher)
  📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  ⏱️ 超时: 300s
  ────────────────────────────────────────────────────────────
  📝 提示词:
    你是 PoseidonX 系统的 Researcher (researcher)。
    请执行以下开发任务:
    
    你是技术研究员。请对以下任务进行技术调研:
    
    ## 任务
    优化航海日志可视化
    在前端添加航海日志的时间轴视图
    
    ## 前序步骤的产出 (请仔细阅读)
    
    ## 上一步产出 — PM分解 (project_manager)
    
    # PM分解 — project_manager
    
    任务: 优化航海日志可视化
    步骤: pm_decompose
    Agent: build_pm
    
    ---
    
    📋 任务: 06c160fe-9b6
    🤖 Agent: PM (project_manager)
    📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
    ⏱️ 超时: 300s
    ────────────────────────────────────────────────────────────
    📝 提示词:
      你是 PoseidonX 系统的 PM (project_manager)。
      请执行以下开发任务:
      
      你是项目经理 (PM)。请对以下任务进行分解和规划:
      
      ## 任务
      优化航海日志可视化
      在前端添加航海日志的时间轴视图
      
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
    🔗 使用 Ollama 直连模式
    
    🔗 Ollama 直连: 127.0.0.1:11435 | 模型: qwen3.5-35b-claude
    ────────────────────────────────────────────────────────────
    
    <think>
    
    </think>
    
    # PoseidonX 系统任务分解文档：航海日志可视化优化
    
    **文档版本**: 1.0.0  
    **日期**: 2023-10-27  
    **项目经理 (PM)**: PoseidonX_PM  
    **涉及系统模块**: 可视化模块 (Vis), 日志服务 (Log Service), 前端核心 (Frontend Core)
    
    ---
    
    ## 1. 需求分析与功能拆解
    
    ### 1.1 核心目标
    在现有 PoseidonX 系统的 HTML/JS 前端中集成一个**航海日志时间轴视图**。该视图需以时间顺序直观展示船舶航行过程中的关键事件（如定位、机械状态、异常报警等），支持滚动、缩放及事件详情查看。
    
    ### 1.2 任务拆解 (WBS)
    
    我们将任务拆解为四个主要阶段：**数据层适配**、**数据可视化组件开发**、**前端交互集成**、**测试与验收**。
    
    #### 阶段一：后端数据层适配 (Data Layer)
    *负责团队：后端开发者 (Python/FastAPI)*
    1.  **数据模型梳理**：确认日志表结构，提取关键时间字段（`log_time`）、事件类型（`event_type`）、内容（`content`）。
    2.  **API 接口开发**：
        *   新增 `/api/v1/logs/timeline` 接口。
        *   支持参数：`start_time`, `end_time`, `page_size`, `cursor` (用于分页/无限滚动)。
        *   返回格式：JSON，包含排序后的日志列表及元数据。
    3.  **索引优化**：在 PostgreSQL/SQLite 中对时间字段添加索引，确保时间轴数据加载延迟 < 200ms。
    
    #### 阶段二：可视化组件开发 (UI Component)
    *负责团队：前端开发者 (HTML/JS)*
    1.  **选型与初始化**：
        *   方案 A（轻量级）：使用原生 SVG 或 Canvas 绘制自定义时间轴（推荐，减少依赖）。
        *   方案 B（库支持）：引入轻量级图表库（如 `Chart.js` 或 `Furnace.js`）的特定插件。
        *   *决策*：鉴于项目采用原生 HTML+JS，建议优先采用 **自定义 SVG 渲染** 或 **轻量级库 (vis-timeline)** 以获得最佳兼容性。
    2.  **布局设计**：
        *   设计响应式容器，支持 PC 端宽屏展示和移动端滚动展示。
        *   定义时间轴刻度样式（年/月/日/时）。
    3.  **事件点渲染**：
        *   绘制不同类别的节点（颜色区分：正常、警告、错误）。
        *   实现节点悬浮提示 (Tooltip) 显示详情。
    
    #### 阶段三：前端交互集成 (Integration)
    *负责团队：前端开发者 + UI 设计师*
    1.  **路由挂载**：在现有前端结构中增加“航海日志”入口页面或 Modal。
    2.  **数据流对接**：编写 JS 逻辑调用后端 API，处理加载状态 (Loading)、空状态 (Empty) 和错误处理 (Error)。
    3.  **交互逻辑**：
        *   实现时间范围筛选器。
        *   支持点击节点钻取查看详情。
        *   支持时间轴拖拽缩放（若使用库则内置，自研需实现缩放算法）。
    
    #### 阶段四：测试与验收 (QA)
    *负责团队：全栈工程师*
    1.  **单元测试**：覆盖 API 分页逻辑及前端数据解析逻辑。
    2.  **集成测试**：验证大数据量（如 >1000 条日志）下的渲染性能。
    3.  **验收标准**：符合设计稿，无布局断裂，API 响应时间达标。
    
    ---
    
    ## 2. 技术风险与依赖关系识别
    
    ### 2.1 技术风险 (Risks)
    
    | 风险等级 | 风险描述 | 缓解方案 |
    | :--- | :--- | :--- |
    | **高** | **大数据量渲染卡顿**：若日志量超过 10,000 条，原生 DOM/SVG 渲染可能导致页面冻结。 | 1. 后端强制分页/游标分页。<br>2. 前端采用虚拟滚动 (Virtual Scrolling) 或 Canvas 渲染。<br>3. 限制初始加载数量（如 50 条），采用无限下拉加载。 |
    | **中** | **第三方库依赖冲突**：引入外部图表库可能污染全局命名空间或样式冲突。 | 1. 优先评估原生实现可行性。<br>2. 若引入库，使用 Shadow DOM 或严格封装 CSS Scope。<br>3. 锁定库版本。 |
    | **中** | **时区处理不一致**：后端存储与前端展示时区不一致导致时间轴偏移。 | 1. 确立统一时区标准（建议后端始终存 UTC，前端根据用户环境转换）。<br>2. 数据接口明确返回 ISO 8601 格式。 |
    
    ### 2.2 依赖关系 (Dependencies)
    
    *   **强依赖**：
        *   后端 API 开发进度 -> 前端数据对接。
        *   数据库索引建立 -> 前端列表加载性能。
    *   **弱依赖**：
        *   UI 设计规范图 -> 前端组件样式实现。
    
    ---
    
    ## 3. 角色执行指导
    
    ### 🧪 给研究人员 (Researchers)
    *   **关注点**：数据定义与业务逻辑。
    *   **行动项**：
        *   确认“航海日志”的具体事件类型分类标准（Tagging System）。
        *   定义时间轴上需要高亮显示的特殊事件阈值（例如：航速异常超过某值自动标红）。
        *   提供历史数据样本，用于前端性能测试的数据集。
    
    ### 🏗️ 给架构师 (Architects)
    *   **关注点**：性能架构与数据流。
    *   **行动项**：
        *   审核 `/api/v1/logs/timeline` 的 SQL 查询计划，确保 `WHERE` 子句利用索引。
        *   决定时间轴渲染技术栈（Canvas vs DOM）。考虑到项目路径 `src/frontend` 为 HTML+JS，若无现成库，建议**引入 `vis-timeline` (CDN 或本地) 以降低自研成本**。
        *   制定接口限流策略，防止前端轮询或大数据拉取拖垮服务。
    
    ### 👨‍💻 给开发者 (Developers)
    *   **行动项**：
        *   **后端**：快速在 `src/backend/routes/` 下创建 `timeline.py`，完成分页逻辑。
        *   **前端**：在 `src/frontend/views/` 创建 `timeline.html` 及 `timeline.js`。
        *   **代码规范**：
            *   后端：遵循 FastAPI 风格，使用 Pydantic 进行数据模型校验。
            *   前端：使用模块化写法（ES6 Modules），避免全局变量污染。
        *   **测试执行**：
            *   开发完成后，务必运行项目要求的测试命令：
            ```bash
            cd /Users/panglaohu/Downloads/DoubleBoatClawSystem
            PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short
            ```
            *   确保所有测试用例通过，特别是针对 API 时间筛选的测试。
    
    ---
    
    ## 4. 开发路线图 (Timeline)
    
    | 阶段 | 任务描述 | 预计工时 | 负责人 | 交付物 |
    | :--- | :--- | :--- | :--- :--- |
    | **T+1** | 后端 API 设计与开发 (`/timeline`) | 4h | Backend Dev | API 文档、单元测试 |
    | **T+2** | 架构图定稿与组件选型确认 | 2h | Architect | 技术选型确认书 |
    | **T+3~4** | 前端时间轴组件开发 (渲染/交互) | 12h | Frontend Dev | 可交互的 HTML/JS 文件 |
    | **T+5** | 前后端联调与边界测试 | 4h | Full Stack | 集成测试结果 |
    | **T+6** | 性能优化与全量测试 | 4h | QA/Dev | 最终测试报告 |
    
    ---
    
    ## 5. 下一步行动 (Next Steps)
    
    1.  **Architecture Review**：请架构师在 [时间] 前确认时间轴渲染技术方案（自研 vs 开源库）。
    2.  **API Spec**：后端团队请在 [时间] 前提交 API 接口文档。
    3.  **环境准备**：前端团队准备测试环境数据，运行本地开发服务。
    
    **项目经理备注**：请务必关注数据量级的影响，避免在首页直接加载全量日志。时间轴的核心价值在于“可探索性”，而非“全量展示”。
    
    ────────────────────────────────────────────────────────────
    ✅ Ollama 直连完成
    
    
    
    ## 要求
    1. 调研现有代码库中相关的文件和模块
    2. 分析实现方案的可行性
    3. 列出需要修改的文件和影响范围
    4. 输出一份调研报告 (Markdown 格式)，包含代码片段引用
    
    项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
    后端: src/backend/ (Python FastAPI)
    前端: src/frontend/ (HTML + JS)
    
    
    项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
    后端: src/backend/ (Python FastAPI)
    前端: src/frontend/ (HTML + JS)
    完成后运行: PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short
    
  ────────────────────────────────────────────────────────────
  🔗 使用 Ollama 直连模式
  
  🔗 Ollama 直连: 127.0.0.1:11435 | 模型: qwen3.5-35b-claude
  ────────────────────────────────────────────────────────────
  
  <think>
  
  </think>
  
  # PoseidonX 系统技术调研报告：航海日志时间轴视图优化
  
  **调研人**: Researcher (PoseidonX)  
  **日期**: 2023-10-27  
  **上下文**: 响应 PM 分解任务 (ID: 06c160fe-9b6)，针对“前端添加航海日志时间轴视图”进行技术可行性分析与现状调研。
  
  ---
  
  ## 1. 代码库现状调研与分析
  
  ### 1.1 项目结构概览
  根据项目根目录 `/Users/panglaohu/Downloads/DoubleBoatClawSystem`，我们首先梳理了现有的代码结构，确认了后端与前端的技术栈及现有模块分布。
  
  ```text
  /Users/panglaohu/Downloads/DoubleBoatClawSystem
  ├── src/
  │   ├── backend/                # Python FastAPI
  │   │   ├── main.py             # 应用入口
  │   │   ├── models/             # 数据模型 (SQLAlchemy/Motor)
  │   │   ├── routes/             # API 路由 (日志/导航/控制)
  │   │   └── services/           # 业务逻辑层
  │   └── frontend/               # HTML + JS (原生/Vue/React未指定，按描述为原生)
  │       ├── index.html
  │       ├── css/
  │       ├── js/
  │       └── views/              # 各个功能模块页面
  ├── tests/                      # 测试目录
  ├── requirements.txt
  └── README.md
  ```
  
  ### 1.2 现有日志相关模块分析
  
  #### A. 后端数据层 (`src/backend`)
  *   **发现**: 在 `src/backend/models/` 或 `src/backend/routes/` 中已存在日志记录功能。
  *   **潜在问题**: 
      *   现有 API 可能仅支持列表加载或按条件查询，缺乏专门针对“时间轴展示”的优化接口（如按时间窗口聚合、分页游标优化）。
      *   JSON 返回格式可能未标准化为 ISO 8601，导致前端时间转换困难。
  *   **待确认文件**:
      *   `src/backend/models/log.py` (或类似名称): 检查日志表结构 (Schema)。
      *   `src/backend/routes/logs.py`: 检查现有查询接口逻辑。
  
  #### B. 前端表现层 (`src/frontend`)
  *   **发现**: 前端目前使用 HTML + JS。
  *   **现状**: 
      *   检查 `src/frontend/views/` 下是否有现有的日志列表页面（例如 `log_list.html`）。
      *   检查 `src/frontend/js/` 下是否有通用的图表渲染工具或 API 调用封装。
  *   **技术债务**: 
      *   原生 DOM 操作可能较多，缺乏现代组件化思想，添加复杂的时间轴组件需特别注意代码隔离，避免污染全局命名空间。
      *   缺乏现成的时间轴库引用，需评估引入外部库（如 `vis-timeline`）的可行性。
  
  ---
  
  ## 2. 实现方案可行性分析
  
  ### 方案一：原生 JavaScript + SVG/Canvas 绘制 (高风险，零依赖)
  *   **描述**: 完全手动编写代码，利用 HTML5 Canvas 或 SVG 绘制时间轴轴线、刻度和事件点。
  *   **优点**: 
      *   无外部依赖，加载速度快。
      *   完全可控，样式极致定制。
  *   **缺点**: 
      *   开发成本高，需处理复杂的缩放、拖拽、响应式逻辑。
      *   性能优化难度大，大数据量下（>5000 条）极易卡顿。
  *   **可行性**: ⭐⭐ (适合日志量极少且对定制化要求极高的场景)
  
  ### 方案二：引入轻量级时间轴库 (推荐)
  *   **描述**: 使用成熟的 JavaScript 时间轴库，如 **Vis.js (vis-timeline)** 或 **Google Charts Timeline**。
  *   **优点**: 
      *   开箱即用，内置缩放、拖拽、事件交互。
      *   社区成熟，文档丰富，开发成本低。
      *   Vis.js 支持数据分组和层级，非常适合航海日志的“事件分类”展示。
  *   **缺点**: 
      *   需引入外部 CSS/JS 文件（可通过 CDN 或本地打包解决）。
      *   样式定制需通过库提供的 API 或 CSS 覆盖。
  *   **可行性**: ⭐⭐⭐⭐⭐ (最适合 PoseidonX 当前技术栈)
  
  ### 方案三：后端聚合 + 前端简单渲染 (折中方案)
  *   **描述**: 后端在生成 JSON 时预计算时间窗口（如按小时聚合），前端仅渲染静态点。
  *   **优点**: 前端逻辑简化。
  *   **缺点**: 失去时间轴的动态探索能力（如随时缩放查看细节），用户体验不佳。
  *   **可行性**: ⭐⭐ (不推荐，违背“可视化”初衷)
  
  **决策**: 采用 **方案二**。鉴于项目为 HTML+JS 架构，引入 `vis-timeline` 能最快速度实现高品质交付。
  
  ---
  
  ## 3. 代码修改文件与影响范围
  
  基于上述决策，以下是需要修改和新增的文件列表：
  
  ### 3.1 后端修改 (Backend)
  
  | 文件路径 | 操作 | 修改内容描述 | 影响范围 |
  | :--- | :--- | :--- | :--- |
  | `src/backend/models/log.py` | 审查/调整 | 确保时间字段索引化；确认序列化是否包含 UTC 时间戳。 | SQL 查询性能 |
  | `src/backend/routes/logs.py` | **新增/修改** | 新增 `/api/v1/logs/timeline` 接口。<br>支持：`start`, `end`, `type`, `limit`, `offset`。 | API 响应速度 (需优化分页) |
  | `tests/test_logs.py` | 新增 | 编写针对时间轴接口的单元测试。 | 回归测试覆盖 |
  
  **代码片段示例 (修改后端接口):**
  
  ```python
  # src/backend/routes/logs.py (新增)
  from fastapi import APIRouter, Query, HTTPException
  from sqlalchemy.orm import Session
  from ...models import Log
  from pydantic import BaseModel
  
  router = APIRouter(prefix="/logs", tags=["logs"])
  
  class TimelineResponse(BaseModel):
      events: list[dict]
      total: int
  
  @router.get("/timeline")
  async def get_log_timeline(
      start_time: str = Query(..., description="ISO 8601 start time"),
      end_time: str = Query(..., description="ISO 8601 end time"),
      limit: int = Query(100, le=1000),
      skip: int = Query(0)
  ):
      # 优化：确保 SQL 使用了时间索引
      # 逻辑实现...
      return {"events": [...], "total": count}
  ```
  
  ### 3.2 前端修改 (Frontend)
  
  | 文件路径 | 操作 | 修改内容描述 | 影响范围 |
  | :--- | :--- | :--- | :--- |
  | `src/frontend/index.html` | **修改** | 引入 `vis-timeline` 的 CSS 和 JS 库 (CDN 或本地)。 | 页面加载资源 |
  | `src/frontend/views/` | **新建** | `timeline.html`: 包含时间轴渲染容器 `<div id="visualization"></div>`。 | 新增页面 |
  | `src/frontend/js/` | **新建** | `timeline.js`: 处理 API 轮询/请求，配置 Vis.js 数据结构。 | 新增业务逻辑 |
  | `src/frontend/css/style.css` | 新增 | `timeline.css`: 覆盖 Vis.js 默认样式，使其匹配 PoseidonX 主题色。 | 样式整合 |
  | `src/frontend/index.html` (导航) | **修改** | 在导航栏添加“日志时间轴”入口。 | 用户交互路径 |
  
  **代码片段示例 (前端初始化):**
  
  ```javascript
  // src/frontend/js/timeline.js
  import 'https://unpkg.com/vis-timeline/standalone/umd/vis-timeline-graph2d.min.js';
  
  function initTimeline() {
    const container = document.getElementById('timelineContainer');
    
    // 获取数据
    fetch('/api/v1/logs/timeline?start=2023-01-01T00:00:00Z&end=2023-12-31T23:59:59Z')
      .then(res => res.json())
      .then(data => {
        const items = new vis.DataSet(data.events);
        const options = {
          align: 'left',
          groupOrder: 'type',
          orientation: 'top',
          editable: false,
          margin: { item: 10, axis: 5 }
        };
  
        const timeline = new vis.Timeline(container, items, options);
        
        // 交互事件绑定
        timeline.on('click', function (params) {
          console.log('Event clicked: ', params.items);
        });
      });
  }
  
  initTimeline();
  ```
  
  ---
  
  ## 4. 风险评估与应对
  
  1.  **性能风险**: 
      *   *现象*: 前端一次性渲染 1000+ 个节点时，JS 主线程卡顿。
      *   *应对*: 后端强制限制每页返回数量（如 200 条），前端支持“虚拟滚动”或“按需加载”（点击加载更多）。Vis.js 本身对大数量级有优���，但需配合后端分页。
  
  2.  **兼容性风险**:
      *   *现象*: 旧版本浏览器不支持 ES6 模块或 Canvas。
      *   *应对*: 确保构建流程（如有）或引入库时使用兼容语法；Vis.js 对现代浏览器支持极好，IE11 已不再作为官方支持目标 (需确认 project 需求)。
  
  3.  **数据一致性**:
      *   *现象*: 后端时间格式与前端解析库冲突。
      *   *应对*: 严格统一使用 **ISO 8601** 格式 (带时区偏移量)，后端输出 JSON ��标准化，前端 `Date.parse` 解析。
  
  ---
  
  ## 5. 测试计划与验收
  
  ### 5.1 自动化测试 (pytest)
  根据任务要求，所有后端代码变更必须通过以下测试命令：
  
  ```bash
  cd /Users/panglaohu/Downloads/DoubleBoatClawSystem
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short
  ```
  
  **重点关注测试用例**:
  *   `tests/test_api_logs.py`: 验证 `/timeline` 接口的分页逻辑、时间范围过滤准确性。
  *   `tests/test_performance.py`: (可选) ��拟大量数据写入，验证查询耗时。
  
  ### 5.2 前端验收标准
  *   [ ] 页面加载后，时间轴能在 1 秒内渲染当前时间范围的数据。
  *   [ ] 支持水平拖拽缩放，无闪烁。
  *   [ ] 点击事件点，正确显示对应的日志详情。
  *   [ ] 移动端适配：在手机上查看时间轴不会发生横向溢出或错位。
  
  ---
  
  ## 6. 结论与下一步建议
  
  **结论**: 
  在现有 `src/frontend` (HTML+JS) 和 `src/backend` (FastAPI) 架构下，引入 **Vis.js Timeline** 库是实现“航海日志时间轴视图”的最优解。方案成本最低，效果最佳，且无需重构现有前端架构。
  
  **建议行动**:
  1.  **架构师**: 确认 `Vis.js` 库的引入方式（本地 `npm` 包还是 CDN），建议本项目优先使用本地静态文件管理以保证内网离线可用性。
  2.  **后端开发**: 立即修改 `routes/logs.py` 并添加分页支持。
  3.  **前端开发**: 创建新视图文件，集成 Vis.js。
  4.  **测试阶段**: 修改完成后，立即运行 `pytest` 确保无回归破坏。
  
  ---
  **Researcher Signature**: PoseidonX_AI
  **Status**: Ready for Implementation
  
  ────────────────────────────────────────────────────────────
  ✅ Ollama 直连完成
  
  
  
  ## 要求
  1. 基于调研结果，设计详细的技术方案
  2. 定义接口规范 (API 路由、参数、返回值)
  3. 画出模块交互关系
  4. 编写开发人员可直接参考的实现指南 (Markdown 格式)
  5. 指出需要修改的具体文件和函数
  
  项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  后端: src/backend/ (Python FastAPI)
  前端: src/frontend/ (HTML + JS)
  
  
  项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  后端: src/backend/ (Python FastAPI)
  前端: src/frontend/ (HTML + JS)
  完成后运行: PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short
  
────────────────────────────────────────────────────────────
🔗 使用 Ollama 直连模式

🔗 Ollama 直连: 127.0.0.1:11435 | 模型: qwen3.5-35b-claude
────────────────────────────────────────────────────────────

<think>

</think>

# PoseidonX 系统技术方案设计文档：航海日志时间轴视图

**文档版本**: 2.0.0  
**日期**: 2023-10-27  
**角色**: Architect (Architecture)  
**基于**: Research Report (Researcher) + PM Plan (Project Manager)  
**决策**: 引入 `vis-timeline` 库 + 后端 FastAPI 接口优化

---

## 1. 系统架构设计

### 1.1 模块交互关系图 (Mermaid)

```mermaid
flowchart TD
    subgraph Frontend ["Frontend (HTML + JS)"]
        UI[Navigation/Menu] --> View[Timeline View (timeline.html)]
        View --> Lib[vis-timeline Library]
        View --> API_Caller[fetch() API Call]
    end

    subgraph Gateway ["API Gateway / Proxy (Optional)"]
        LB[Load Balancer] --> API_Caller
    end

    subgraph Backend ["Backend (Python FastAPI)"]
        Routes[Routes / logs.py] --> Services[Log Service]
        Services --> DB[[PostgreSQL / SQLite]]
        Routes --> Response[JSON Response]
    end

    View -."Http Request".-> API_Caller
    API_Caller -."JSON Data".-> Routes
    Routes -."Read/Write".-> DB
    Response -.-> View

    style Frontend fill:#e1f5fe
    style Backend fill:#e8f5e9
    style DB fill:#fff3e0
```

### 1.2 核心设计原则
1.  **前后端分离**: 后端仅负责数据排序、过滤、分页；前端负责渲染、交互、计算视口比例。
2.  **分页加载 (Pagination vs Virtual Scroll)**: 
    *   鉴于 Vis.js 的优化机制，我们采用**后端游标分页**（Cursor-based）或**范围分页**（Range-based）结合前端“无限滚动”加载，避免一次性加载大量数据。
3.  **时区统一**: 后端存储与传输统一使用 **ISO 8601 (UTC)**，前端根据浏览器环境或用户设置进行展示转换。

---

## 2. 接口规范定义 (API Specification)

### 2.1 接口概览

| 接口方法 | 路由路径 | 描述 | 认证 |
| :--- | :--- | :--- | :--- |
| GET | `/api/v1/logs/timeline` | 获取时间轴事件列表 | JWT (Optional) |

### 2.2 请求参数 (Query Parameters)

| 参数名 | 类型 | 必填 | 说明 | 示例 |
| :--- | :--- | :--- | :--- | :--- |
| `start` | string | 是 | 开始时间 (ISO 8601) | `2023-10-01T00:00:00Z` |
| `end` | string | 是 | 结束时间 (ISO 8601) | `2023-10-07T23:59:59Z` |
| `limit` | int | 否 | 每页数量 (默认 100), 最大 500 | `100` |
| `skip` | int | 否 | 跳过记录数 (用于分页) | `0` |
| `event_type` | string | 否 | 事件类型过滤 (逗号分隔) | `navigation,error` |

### 2.3 响应体 (JSON Response)

```json
{
  "events": [
    {
      "id": "log_001",
      "content": "GPS 信号丢失",
      "start": "2023-10-27T10:30:00Z",
      "end": null,  // 单点事件 end 为 null 或 start
      "group": "error", // 对应 Vis.js 的 group
      "className": "error-event"
    },
    {
      "id": "log_002",
      "content": "航速更新：12.5 kn",
      "start": "2023-10-27T10:35:00Z",
      "group": "navigation"
    }
  ],
  "groups": [
    {"id": "error", "label": "错误报警", "style": "color: #d32f2f"},
    {"id": "navigation", "label": "导航信息", "style": "color: #1976d2"}
  ],
  "pagination": {
    "total": 1500,
    "limit": 100,
    "has_more": true
  }
}
```

---

## 3. 详细实现指南

### 3.1 后端实现 (FastAPI)

#### 3.1.1 需修改/新建的文件

1.  `src/backend/routes/logs.py`: 新增时间轴接口。
2.  `src/backend/models/log.py` (或现有日志模型): 新增 `event_type` 字段或映射。
3.  `tests/test_logs_api.py`: 新增时间轴接口测试用例。

#### 3.1.2 代码实现要点 (代码片段)

**文件**: `src/backend/routes/logs.py`

```python
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_

router = APIRouter()

@router.get("/timeline")
async def get_log_timeline(
    start_time: str = Query(..., description="Start time (ISO 8601 UTC)"),
    end_time: str = Query(..., description="End time (ISO 8601 UTC)"),
    limit: int = Query(100, le=500, description="Page size"),
    skip: int = Query(0, description="Offset"),
    event_type: str | None = Query(None, description="Filter by event type")
):
    db: Session = get_db() # 依赖注入
    
    try:
        # 1. 基础查询构建
        query = db.query(LogModel)
        
        # 2. 时间过滤
        time_filter = and_(
            LogModel.timestamp >= start_time,
            LogModel.timestamp <= end_time
        )
        
        if event_type:
            types = [t.strip() for t in event_type.split(',')]
            query = query.filter(LogModel.type.in_(types))
            
        query = query.filter(time_filter)

        # 3. 排序 (时间倒序或正序，时间轴通常正序展示)
        query = query.order_by(LogModel.timestamp.asc())

        # 4. 分页截取
        total_count = query.count()
        logs = query.limit(limit).offset(skip).all()

        # 5. 数据转换 (DTO)
        events = []
        groups_map = {}
        
        for log in logs:
            event = {
                "id": log.id,
                "content": log.message,
                "start": log.timestamp.isoformat() + "Z", # 强制加 Z
                "end": log.timestamp.isoformat() + "Z" if log.timestamp != log.end_time else None,
                "group": log.type,
                "className": "event-" + log.type
            }
            events.append(event)
            groups_map[log.type] = True
            
        # 6. 构建 Group 数据
        groups = [
            {"id": grp_id, "label": grp_id.replace("_", " ").title(), "style": f"color: palette[{grp_id}]"} 
            for grp_id in groups_map.keys()
        ]

        return {
            "events": events,
            "groups": groups,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "skip": skip,
                "has_more": (skip + limit) < total_count
            }
        }
    except Exception as e:
        logging.error(f"Timeline query error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

### 3.2 前端实现 (HTML + JS)

#### 3.2.1 需新建/修改的文件

1.  `src/frontend/timeline.html`: **新建** 时间轴视图页面。
2.  `src/frontend/js/timeline_controller.js`: **新建** 控制逻辑。
3.  `src/frontend/css/style.css`: **新增** 自定义覆盖样式 (`.vis-time-axis`, `.vis-item`).
4.  `src/frontend/index.html`: **修改** 导航菜单，添加入口。

#### 3.2.2 依赖引入 (CDN 方式，建议后续改为本地打包)

在 `timeline.html` 的 `<head>` 中引入：

```html
<!-- Vis-Timeline CSS -->
<link href="https://unpkg.com/vis-timeline/styles/vis-timeline-graph2d.min.css" rel="stylesheet" type="text/css" />
<!-- Vis-Timeline JS (and dependencies) -->
<script type="text/javascript" src="https://unpkg.com/vis-timeline/standalone/umd/vis-timeline-graph2d.min.js"></script>
```

#### 3.2.3 核心逻辑代码片段

**文件**: `src/frontend/js/timeline_controller.js`

```javascript
let timeline = null;
let items = null;
const container = document.getElementById("timeline-container");

async function loadTimeline(start, end) {
    document.getElementById('loading').style.display = 'block';
    
    try {
        // 调用后端接口
        const url = `/api/v1/logs/timeline?start=${start}&end=${end}&limit=200&skip=0`;
        const response = await fetch(url);
        const data = await response.json();

        // 1. 初始化或更新 DataSets
        items = new vis.DataSet(data.events);
        const groups = new vis.DataSet(data.groups);

        // 2. 初始化 Timeline 配置
        const options = {
            editable: false,
            editable: {
                add: false,
                updateTime: false,
                remove: false
            },
            orientation: 'top',
            groupOrder: 'label',
            stack: true,
            showCurrentTime: true,
            visibleTime: {
                start: start,
                end: end
            },
            onResize: loadMoreData, // 自定义缩放逻辑，触发更多数据加载 (简化版)
            zoomKey: 'ctrlKey' // 使用 Ctrl + 滚轮缩放
        };

        if (timeline) {
            timeline.setData(items);
            timeline.setGroups(groups);
        } else {
            timeline = new vis.Timeline(container, items, options);
            timeline.setGroups(groups);
            
            // 监听结束时间，实现无限滚动加载 (简化：仅演示基础加载)
            timeline.on("rangechanged", function (properties) {
                // 这里可以实现：当用户滚动到尾部时，自动调用 API 加载下一页数据
                // 为了本方案简化，仅展示基础渲染
                console.log("Range changed: New visible time", properties.start);
                // 实际生产环境建议实现：detect scrolling to bottom -> fetch next batch
            });
        }
    } catch (err) {
        console.error("Failed to load timeline:", err);
        alert("Failed to load log timeline");
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

// 页面加载时调用 (模拟获取最近 7 天数据)
window.addEventListener('DOMContentLoaded', () => {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 7);
    
    loadTimeline(startDate.toISOString(), endDate.toISOString());
});
```

---

## 4. 测试与验证计划

### 4.1 后端单元测试 (pytest)

在 `tests/test_logs_api.py` 中添加以下测试：

```python
import pytest

@pytest.mark.asyncio
async def test_timeline_api_pagination(async_client, auth_headers):
    response = await async_client.get(
        "/api/v1/logs/timeline",
        params={"start": "2023-01-01T00:00:00Z", "end": "2023-01-07T00:00:00Z", "limit": 10},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert "groups" in data
    assert len(data["events"]) <= 10
    # 验证 ISO 格式
    for item in data["events"]:
        assert "+" in item["start"] or "Z" in item["start"]

@pytest.mark.asyncio
async def test_timeline_no_data(async_client, auth_headers, empty_db):
    response = await async_client.get(
        "/api/v1/logs/timeline",
        params={"start": "2100-01-01T00:00:00Z", "end": "2100-01-02T00:00:00Z"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["events"] == []
```

### 4.2 验收命令

在提交代码前，必须执行：

```bash
cd /Users/panglaohu/Downloads/DoubleBoatClawSystem
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short
```

---

## 5. 文件修改清单 (Action List)

请开发人员按以下顺序执行：

1.  **Backend**:
    *   [ ] 修改 `src/backend/routes/logs.py` -> **新增** `get_log_timeline` 函数。
    *   [ ] 确保 `src/backend/models/log.py` 中包含 `timestamp` 和 `type` 字段，并添加数据库索引 `CREATE INDEX idx_log_time ON log(timestamp);`。
    *   [ ] 新增 `tests/test_logs_api.py` 内容。
2.  **Frontend**:
    *   [ ] 新建 `src/frontend/timeline.html` (包含 `<div id="timeline-container"></div>`)。
    *   [ ] 新建 `src/frontend/js/timeline_controller.js` (包含上述 JS 代码片段)。
    *   [ ] 修改 `src/frontend/index.html` (在导航栏添加 `/timeline` 链接)。
    *   [ ] 调整 `src/frontend/css/style.css` (增加 `.vis-item` 的样式以匹配主题)。
3.  **Validation**:
    *   [ ] 运行 `pytest`，确保所有测试通过。
    *   [ ] 本地启动服务 (`uvicorn src.backend.main:app --reload`)。
    *   [ ] 在浏览器访问 `http://localhost:8000/timeline` 检查渲染效果。

---

**Architect Note**: 
本方案采用了“轻量级库 + 后端分页”模式，平衡了开发效率与系统性能。如果未来日志量达到百万级，需引入 Elasticsearch 进行时间序列数据检索，并在前端引入虚拟滚动技术（如 `@visjs/vis-timeline-virtual`）。当前阶段请按此方案执行。

────────────────────────────────────────────────────────────
✅ Ollama 直连完成
