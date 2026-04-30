# 架构设计 — architect

任务: 给build团队的PM分配一个任务，在AR CAS Pro菜单显示雷达图，此图与双体船及货船运动相关
步骤: architecture
Agent: build_architect

---

📋 任务: 8163284c-7fa
🤖 Agent: Architect (architect)
📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
🔧 执行方式: DeepSeek API (直连)
⏱️ 超时: 1200s
────────────────────────────────────────────────────────────
📝 提示词:
  你是 PoseidonX 系统的 Architect (architect)。
  请执行以下开发任务:
  
  你是系统架构师。请为以下任务设计技术方案:
  
  ## 任务
  给build团队的PM分配一个任务，在AR CAS Pro菜单显示雷达图，此图与双体船及货船运动相关
  给build团队的PM分配一个任务，在AR CAS Pro菜单显示雷达图，此图与双体船及货船运动相关
  
  ---
  
  ## Captain Agent 安全指令 (必须遵循)
  
  **任务分配通知**
  
  **任务编号:** TASK-2025-AR-001  
  **任务名称:** AR CAS Pro 菜单雷达图显示开发  
  **负责人:** Build 团队 PM  
  **优先级:** 高  
  
  **任务描述:**  
  在 AR CAS Pro 菜单界面中集成并显示雷达图，该雷达图需实时反映当前海域内双体船（MMSI 567890123）及货船（MMSI 345678901）的运动态势。
  
  **关键要求:**  
  1. 雷达图需包含双体船与货船的实时位置、航向（COG）、航速（SOG）数据。  
  2. 雷达图应支持动态更新，刷新频率不低于每 2 秒一次。  
  3. 界面需清晰标注两船相对本船（位置: 30.9036°N, 122.4036°E）的方位与距离。  
  4. 需考虑两船运动趋势（双体船航向 46°、航速 9.0 kn；货船航向 90°、航速 12.0 kn）对碰撞风险的提示。  
  
  **依赖项:**  
  - 雷达图渲染组件（待确认是否已有现成模块）  
  - AIS 数据接口（当前已接入 8 个目标）  
  
  **截止时间:** 请于 2025-03-21 18:00 前确认资源与初步排期。  
  
  请确认接收并反馈预计工时。
  
  
  ## 前序步骤的产出 (递进式摘要)
  
  ### 步骤 01: pm_decompose
  任务: 给build团队的PM分配一个任务，在AR CAS Pro菜单显示雷达图，此图与双体船及货船运动相关
  步骤: pm_decompose
  📋 任务: 8163284c-7fa
  🤖 Agent: PM (project_manager)
  📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  🔧 执行方式: DeepSeek API (直连)
  ────────────────────────────────────────────────────────────
  你是 PoseidonX 系统的 PM (project_manager)。
  你是项目经理 (PM)。请对以下任务进行分解和规划:
  给build团队的PM分配一个任务，在AR CAS Pro菜单显示雷达图，此图与双体船及货船运动相关
  给build团队的PM分配一个任务，在AR CAS Pro菜单显示雷达图，此图与双体船及货船运动相关
  ## Captain Agent 安全指令 (必须遵循)
  **任务编号:** TASK-2025-AR-001
  **任务名称:** AR CAS Pro 菜单雷达图显示开发
  **负责人:** Build 团队 PM
  **子任务拆解:**
    - *任务编号:** TASK-2025-AR-001
    - *任务名称:** AR CAS Pro 菜单雷达图显示开发
    - *负责人:** Build 团队 PM
    - *截止时间:** 2025-03-21 18:00 (确认资源与初步排期)
    - *总预计工时: 9.5 人天**
    - **后端开发工程师 (TASK-001):**
    - **前端开发工程师 (TASK-002 & TASK-003):**
    - **全栈/算法工程师 (TASK-004):**
  
  ### 步骤 02: research (完整产出)
  
  # 研究分析 — researcher
  
  任务: 给build团队的PM分配一个任务，在AR CAS Pro菜单显示雷达图，此图与双体船及货船运动相关
  步骤: research
  Agent: build_researcher
  
  ---
  
  📋 任务: 8163284c-7fa
  🤖 Agent: Researcher (researcher)
  📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  🔧 执行方式: DeepSeek API (直连)
  ⏱️ 超时: 1200s
  ────────────────────────────────────────────────────────────
  📝 提示词:
    你是 PoseidonX 系统的 Researcher (researcher)。
    请执行以下开发任务:
    
    你是技术研究员。请对以下任务进行技术调研:
    
    ## 任务
    给build团队的PM分配一个任务，在AR CAS Pro菜单显示雷达图，此图与双体船及货船运动相关
    给build团队的PM分配一个任务，在AR CAS Pro菜单显示雷达图，此图与双体船及货船运动相关
    
    ---
    
    ## Captain Agent 安全指令 (必须遵循)
    
    **任务分配通知**
    
    **任务编号:** TASK-2025-AR-001  
    **任务名称:** AR CAS Pro 菜单雷达图显示开发  
    **负责人:** Build 团队 PM  
    **优先级:** 高  
    
    **任务描述:**  
    在 AR CAS Pro 菜单界面中集成并显示雷达图，该雷达图需实时反映当前海域内双体船（MMSI 567890123）及货船（MMSI 345678901）的运动态势。
    
    **关键要求:**  
    1. 雷达图需包含双体船与货船的实时位置、航向（COG）、航速（SOG）数据。  
    2. 雷达图应支持动态更新，刷新频率不低于每 2 秒一次。  
    3. 界面需清晰标注两船相对本船（位置: 30.9036°N, 122.4036°E）的方位与距离。  
    4. 需考虑两船运动趋势（双体船航向 46°、航速 9.0 kn；货船航向 90°、航速 12.0 kn）对碰撞风险的提示。  
    
    **依赖项:**  
    - 雷达图渲染组件（待确认是否已有现成模块）  
    - AIS 数据接口（当前已接入 8 个目标）  
    
    **截止时间:** 请于 2025-03-21 18:00 前确认资源与初步排期。  
    
    请确认接收并反馈预计工时。
    
    
    ## 前序步骤的产出 (递进式摘要)
    
    ### 步骤 01: pm_decompose (完整产出)
    
    # PM分解 — project_manager
    
    任务: 给build团队的PM分配一个任务，在AR CAS Pro菜单显示雷达图，此图与双体船及货船运动相关
    步骤: pm_decompose
    Agent: build_pm
    
    ---
    
    📋 任务: 8163284c-7fa
    🤖 Agent: PM (project_manager)
    📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
    🔧 执行方式: DeepSeek API (直连)
    ⏱️ 超时: 1200s
    ────────────────────────────────────────────────────────────
    📝 提示词:
      你是 PoseidonX 系统的 PM (project_manager)。
      请执行以下开发任务:
      
      你是项目经理 (PM)。请对以下任务进行分解和规划:
      
      ## 任务
      给build团队的PM分配一个任务，在AR CAS Pro菜单显示雷达图，此图与双体船及货船运动相关
      给build团队的PM分配一个任务，在AR CAS Pro菜单显示雷达图，此图与双体船及货船运动相关
      
      ---
      
      ## Captain Agent 安全指令 (必须遵循)
      
      **任务分配通知**
      
      **任务编号:** TASK-2025-AR-001  
      **任务名称:** AR CAS Pro 菜单雷达图显示开发  
      **负责人:** Build 团队 PM  
      **优先级:** 高  
      
      **任务描述:**  
      在 AR CAS Pro 菜单界面中集成并显示雷达图，该雷达图需实时反映当前海域内双体船（MMSI 567890123）及货船（MMSI 345678901）的运动态势。
      
      **关键要求:**  
      1. 雷达图需包含双体船与货船的实时位置、航向（COG）、航速（SOG）数据。  
      2. 雷达图应支持动态更新，刷新频率不低于每 2 秒一次。  
      3. 界面需清晰标注两船相对本船（位置: 30.9036°N, 122.4036°E）的方位与距离。  
      4. 需考虑两船运动趋势（双体船航向 46°、航速 9.0 kn；货船航向 90°、航速 12.0 kn）对碰撞风险的提示。  
      
      **依赖项:**  
      - 雷达图渲染组件（待确认是否已有现成模块）  
      - AIS 数据接口（当前已接入 8 个目标）  
      
      **截止时间:** 请于 2025-03-21 18:00 前确认资源与初步排期。  
      
      请确认接收并反馈预计工时。
      
      
      ## 要求
      1. 分析任务需求，拆解为可执行的子步骤
      2. 识别技术风险和依赖关系
      3. 为后续研究人员、架构师、开发者提供清晰的指导
      4. 输出一份结构化的任务分解文档 (Markdown 格式)
      
      ## ⚠️ 重要提示
      系统已自动预加载项目文件结构和相关源文件（见下方 📂 项目上下文）。
      请基于**实际存在的文件**进行分析，不要猜测文件名。
      
      项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
      后端: src/backend/ (Python FastAPI)
      前端: src/frontend/ (HTML + JS)
      
      
      项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
      后端: src/backend/ (Python FastAPI)
      前端: src/frontend/ (HTML + JS)
      
    ────────────────────────────────────────────────────────────
    ⚡ 使用 DeepSeek V4 直连 (64K 输出, 流式)...
    
    🔗 API: api.deepseek.com | 模型: deepseek-chat
    ────────────────────────────────────────────────────────────
    
    好的，作为 PoseidonX 系统的项目经理 (PM)，我已收到并分析了该任务。
    
    根据 Captain Agent 的指令和系统现有文件结构，我将对该任务进行详细分解和规划，并输出一份结构化的任务分解文档。
    
    ---
    
    ### 任务分解文档: AR CAS Pro 菜单雷达图显示开发
    
    **任务编号:** TASK-2025-AR-001
    **任务名称:** AR CAS Pro 菜单雷达图显示开发
    **负责人:** Build 团队 PM
    **优先级:** 高
    **截止时间:** 2025-03-21 18:00 (确认资源与初步排期)
    
    ---
    
    #### 1. 任务目标
    
    在 `AR CAS Pro` 菜单界面中，集成并显示一个动态雷达图，该雷达图需实时展示本船（位置: 30.9036°N, 122.4036°E）与目标双体船（MMSI: 567890123）及货船（MMSI: 345678901）的相对运动态势，并具备碰撞风险提示功能。
    
    #### 2. 需求分析与子任务拆解
    
    为确保任务可执行，我将此任务拆解为以下 5 个核心子任务：
    
    | 子任务 ID | 子任务名称 | 详细描述 | 负责人 (角色) | 预计工时 (人天) |
    | :--- | :--- | :--- | :--- | :--- |
    | **TASK-001** | **后端 AIS 数据过滤与接口开发** | 开发一个新的 API 端点，从现有的 AIS 数据流中过滤出指定 MMSI（567890123 和 345678901）的目标数据，并计算其相对于本船（30.9036°N, 122.4036°E）的方位和距离。 | 后端开发工程师 | 2 |
    | **TASK-002** | **前端雷达图组件开发/集成** | 开发或集成一个用于绘制雷达图的 JavaScript 组件。该组件需支持动态更新数据点，并能够显示方位圈、距离圈、目标标签（船名/MMSI）和运动矢量（COG/SOG）。 | 前端开发工程师 | 3 |
    | **TASK-003** | **前端 AR CAS Pro 菜单集成** | 将 TASK-002 开发的雷达图组件嵌入到 `AR CAS Pro` 菜单的对应页面中。确保菜单切换、布局和样式与现有系统一致。 | 前端开发工程师 | 1 |
    | **TASK-004** | **碰撞风险提示逻辑开发** | 基于两船的运动趋势（COG, SOG）和相对位置，开发一个简单的碰撞风险评估算法（如 CPA/TCPA 计算），并在雷达图上以视觉方式（如颜色变化、警告标签）提示风险等级。 | 全栈/算法工程师 | 2 |
    | **TASK-005** | **端到端集成测试与性能调优** | 将前后端集成，进行完整的端到端测试。重点验证数据刷新频率（≤2秒）、数据准确性、UI 响应性和碰撞提示逻辑的正确性。 | QA 工程师 / 开发工程师 | 1.5 |
    
    **总预计工时: 9.5 人天**
    
    #### 3. 技术依赖与风险识别
    
    | 依赖/风险类型 | 描述 | 影响 | 缓解措施 |
    | :--- | :--- | :--- | :--- |
    | **依赖: 雷达图组件** | 项目是否已有现成的雷达图渲染组件？如果没有，需要寻找或开发一个。 | 影响 TASK-002 的工时和技术选型。 | 立即检查 `/Users/panglaohu/Downloads/DoubleBoatClawSystem/src/frontend/` 下是否存在相关组件。若无，评估使用 `ECharts`、`D3.js` 或 `Canvas API` 自行开发的成本。 |
    | **依赖: AIS 数据接口** | 现有 AIS 数据接口的稳定性和数据格式。 | 影响 TASK-001 的开发难度和数据解析。 | 确认现有接口（已接入 8 个目标）的协议（WebSocket/HTTP）、数据格式（JSON/XML）和字段定义。 |
    | **风险: 数据刷新性能** | 前端雷达图每 2 秒刷新一次，如果数据量大或渲染逻辑复杂，可能导致 UI 卡顿。 | 影响用户体验和系统性能。 | 在 TASK-005 中进行压力测试。优化渲染逻辑（如使用 `requestAnimationFrame`），考虑使用 Web Worker 进行数据处理。 |
    | **风险: 碰撞算法准确性** | 简单的 CPA/TCPA 算法可能无法处理所有复杂会遇局面，导致误报或漏报。 | 影��功能的核心价值。 | 在 TASK-004 中明确算法边界条件，并在测试阶段使用多种模拟场景进行验证。初期可先实现基础版本，后续迭代优化。 |
    
    #### 4. 对后续团队的指导
    
    - **架构师:**
        - 请确认前端项目结构，并指导前端工程师将雷达图组件设计为可复用的模块。
        - 请确认后端 API 设计规范，确保 TASK-001 的接口符合 RESTful 或 WebSocket 的最佳实践。
        - 评估是否需要引入状态管理库（如 Vuex/Pinia 或 Redux）来管理雷达图数据。
    
    - **后端开发工程师 (TASK-001):**
        - **输入:** 现有 AIS 数据流（请从 `src/backend/` 中查找相关数据源代码）。
        - **输出:** 一个新的 API 端点，例如 `/api/v1/ais/targets?mmsi=567890123,345678901`。
        - **数据处理:** 在返回数据中，除了原始 AIS 数据（MMSI, COG, SOG, 经纬度），**必须**包含计算好的相对本船的 `bearing`（方位角，0-360度）和 `range`（距离，单位海里或公里）。本船位置硬编码为 `30.9036°N, 122.4036°E`。
        - **技术建议:** 使用 FastAPI 的 `BackgroundTasks` 或 WebSocket 实现数据推送，以满足 2 秒刷新要求。
    
    - **前端开发工程师 (TASK-002 & TASK-003):**
        - **TASK-002:**
            - 在 `src/frontend/` 下创建一个新的组件文件，例如 `RadarChart.js` 或 `RadarChart.vue`。
            - 组件应接收一个 `targets` 数组作为 prop，数组元素包含 `mmsi`, `bearing`, `range`, `cog`, `sog`。
            - 使用 Canvas 或 SVG 绘制雷达图。中心点代表本船。绘制距离圈（如 1nm, 2nm, 5nm）和方位线（如每 30 度一条）。
            - 为每个目标绘制一个点，并显示其 MMSI 和运动矢量（从目标点沿 COG 方向画一条线，长度与 SOG 成正比）。
        - **TASK-003:**
            - 找到 `AR CAS Pro` 菜单对应的 HTML 文件（可能在 `src/frontend/pages/` 或类似目录）。
            - 在菜单内容区域引入 `RadarChart` 组件。
            - 编写一个数据获取逻辑（调用 TASK-001 的 API），每 2 秒获取一次数据，并更新 `RadarChart` 组件的 `targets` prop。
    
    - **全栈/算法工程师 (TASK-004):**
        - **算法:** 实现 CPA (Closest Point of Approach) 和 TCPA (Time to CPA) 计算。
        - **输入:** 本船位置、航向、航速（假设本船静止或已知运动状态）；目标船位置、航向、航速。
        - **输出:** CPA 距离和 TCPA 时间。
        - **集成:** 将计算结果作为新字段（`cpa`, `tcpa`）添加到 TASK-001 的 API 返回数据中，或者在前端进行计算。
        - **UI 提示:**
            - 如果 TCPA < 10 分钟 且 CPA < 1 海里: 目标点显示为红色，并弹出警告。
            - 如果 TCPA < 20 分钟 且 CPA < 2 海里: 目标点显示为黄色。
            - 其他情况: 目标点显示为绿色。
    
    #### 5. 下一步行动
    
    1.  **立即行动:** 请 Build 团队 PM 确认接收此任务，并反馈预计工时和资源安排。
    2.  **技术调研 (即日):** 前端负责人需在 2025-03-21 18:00 前，确认 `src/frontend/` 下是否存在现成的雷达图组件，并给出技术选型建议。
    3.  **任务启动会:** 计划于 2025-03-22 10:00 召开任务启动会，邀请架构师、前后端开发工程师、QA 工程师参加，明确技术细节和分工。
    
    ────────────────────────────────────────────────────────────
    ✅ deepseek-chat 完成
    
    ## ⚠️ 最重要的规则
    系统已自动预加载项目文件结构和相关源文件（见上方 📂 项目上下文）。
    **你必须只引用上方提供的实际文件**，严禁凭想象编造文件名或路径。
    如果上下文中没有某个文件，说明该文件不存在。
    
    ## 要求
    1. 仔细阅读上方提供的项目文件结构和源文件内容
    2. 根据**实际存在的文件**分析哪些需要修改
    3. 列出需要修改的文件的**完整路径** (必须是项目上下文中出现的路径)
    4. 分析实现方案的可行性
    5. 引用具体代码行号说明修改点
    
    项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
    后端: src/backend/ (Python FastAPI)
    前端: src/frontend/ (HTML + JS)
    
    
    项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
    后端: src/backend/ (Python FastAPI)
    前端: src/frontend/ (HTML + JS)
    
  ────────────────────────────────────────────────────────────
  ⚡ 使用 DeepSeek V4 直连 (64K 输出, 流式)...
  
  🔗 API: api.deepseek.com | 模型: deepseek-chat
  ────────────────────────────────────────────────────────────
  
  好的，作为 PoseidonX 系统的 Researcher，我已收到任务并仔细分析了项目上下文。以下是我的技术调研报告。
  
  ---
  
  ## 技术调研报告: AR CAS Pro 菜单雷达图显示开发
  
  **任务编号:** TASK-2025-AR-001
  **调研目标:** 评估在现有项目结构下，实现“AR CAS Pro 菜单雷达图显示”功能的可行性、技术方案及具体修改点。
  
  ### 1. 项目现状分析
  
  根据提供的项目文件结构，系统是一个典型的 FastAPI + HTML/JS 架构。
  
  - **后端 (`src/backend/`)**:
      - 核心应用在 `app/` 目录下，包含 `main.py` (FastAPI 入口), `models/` (数据模型), `routers/` (API 路由), `services/` (业务逻辑)。
      - 存在 `ais_data_service.py`，表明已有 AIS 数据处理服务。
      - 存在 `websocket_manager.py`，表明系统已支持 WebSocket 通信，这为实现实时数据推送提供了非常好的基础。
      - 存在 `collision_risk_service.py`，表明已有碰撞风险评估相关的服务，可以直接复用或扩展。
  
  - **前端 (`src/frontend/`)**:
      - 使用原生 HTML + JavaScript，无 Vue/React 等框架。
      - 存在 `static/` 目录存放静态资源，`js/` 目录存放 JavaScript 文件。
      - 存在 `pages/` 目录，其中 `ar_cas_pro.html` 是目标页面。
      - 存在 `js/ar_cas_pro.js`，是目标页面的逻辑文件。
      - 存在 `js/radar_chart.js`，**这是一个非常关键的发现**，表明项目可能已经有一个雷达图组件。
  
  ### 2. 可行性分析
  
  **结论: 完全可行，且现有项目基础良好，开发工作量可控。**
  
  - **后端:** 已有 AIS 数据服务和 WebSocket 支持，只需新增或修改一个 API 端点，过滤出指定 MMSI 的目标数据，并计算相对本船的方位和距离即可。
  - **前端:** 已有目标页面 (`ar_cas_pro.html`) 和逻辑文件 (`ar_cas_pro.js`)。最关键的是，存在 `radar_chart.js`，这很可能是一个现成的或半成品的雷达图组件，可以极大地减少前端开发工作量。
  - **碰撞风险:** 已有 `collision_risk_service.py`，可以直接调用其功能，将结果集成到雷达图显示中。
  
  ### 3. 需要修改的文件及具体修改点
  
  以下是基于现有文件结构，需要修改或创建的文件列表及详细修改建议。
  
  #### 3.1 后端修���
  
  **文件 1: `src/backend/app/routers/ais_data.py`** (或新建一个路由文件)
  
  - **修改点:** 新增一个 WebSocket 端点，用于推送指定目标的雷达图数据。
  - **原因:** 任务要求刷新频率不低于 2 秒，WebSocket 是最佳选择，可以避免 HTTP 轮询的开销。
  - **具体代码示例:**
      ```python
      # 在 ais_data.py 或新建 radar_data.py 中
      from fastapi import APIRouter, WebSocket, WebSocketDisconnect
      from ..services.ais_data_service import get_target_data
      from ..services.collision_risk_service import calculate_risk
      import asyncio
  
      router = APIRouter()
  
      @router.websocket("/ws/radar/{mmsi_list}")
      async def websocket_radar_data(websocket: WebSocket, mmsi_list: str):
          await websocket.accept()
          target_mmsis = mmsi_list.split(",")  # 例如: "567890123,345678901"
          try:
              while True:
                  # 1. 获取指定 MMSI 的 AIS 数据
                  targets_data = get_target_data(target_mmsis)
                  
                  # 2. 计算相对本船 (30.9036, 122.4036) 的方位和距离
                  own_ship_pos = (30.9036, 122.4036)
                  for target in targets_data:
                      target['bearing'], target['range'] = calculate_bearing_and_range(
                          own_ship_pos, (target['latitude'], target['longitude'])
                      )
                  
                  # 3. 计算碰撞风险
                  risk_data = calculate_risk(own_ship_pos, targets_data)
                  
                  # 4. 合并数据并发送
                  response_data = {
                      "targets": targets_data,
                      "risks": risk_data
                  }
                  await websocket.send_json(response_data)
                  
                  # 5. 等待 2 秒
                  await asyncio.sleep(2)
          except WebSocketDisconnect:
              print("Client disconnected")
      ```
  
  **文件 2: `src/backend/app/services/ais_data_service.py`**
  
  - **修改点:** 新增一个函数 `get_target_data(mmsi_list)`，用于根据 MMSI 列表过滤数据。
  - **原因:** 现有服务可能返回所有目标的数据，需要增加过滤功能。
  - **具体代码示例:**
      ```python
      # 在 ais_data_service.py 中新增
      def get_target_data(mmsi_list: list) -> list:
          """
          从数据源获取指定 MMSI 列表的目标数据。
          """
          # 假设 self.all_targets 是存储所有 AIS 目标数据的列表
          filtered_targets = [target for target in self.all_targets if target['mmsi'] in mmsi_list]
          return filtered_targets
      ```
  
  **文件 3: `src/backend/app/services/collision_risk_service.py`**
  
  - **修改点:** 确认或新增一个函数 `calculate_risk(own_ship_pos, targets_data)`，用于计算 CPA/TCPA。
  - **原因:** 任务要求考虑碰撞风险提示，需要确保该服务可用。
  - **具体代码示例:**
      ```python
      # 在 collision_risk_service.py 中
      def calculate_risk(own_ship_pos: tuple, targets: list) -> list:
          """
          计算本船与所有目标船的碰撞风险。
          """
          risk_results = []
          for target in targets:
              # 假设本船静止，或从 own_ship_pos 获取本船运动状态
              cpa, tcpa = calculate_cpa_tcpa(
                  own_ship_pos, (0, 0),  # 本船位置和运动状态 (假设静止)
                  (target['latitude'], target['longitude']),
                  (target['cog'], target['sog'])
              )
              risk_results.append({
                  'mmsi': target['mmsi'],
                  'cpa': cpa,
                  'tcpa': tcpa
              })
          return risk_results
      ```
  
  #### 3.2 前端修改
  
  **文件 4: `src/frontend/js/radar_chart.js`**
  
  - **修改点:** 检查并完善该组件，确保其能接收 `targets` 数据并正确渲染。
  - **原因:** 这是核心的雷达图渲染组件，需要确认其接口和功能。
  - **具体代码示例 (假设该组件已存在):**
      ```javascript
      // 在 radar_chart.js 中
      class RadarChart {
          constructor(containerId) {
              this.container = document.getElementById(containerId);
              // ... 初始化 Canvas 或 SVG
          }
  
          // 更新数据的方法
          updateData(targets, risks) {
              // 1. 清空画布
              // 2. 绘制方位圈、距离圈
              // 3. 遍历 targets，绘制每个目标点
              targets.forEach(target => {
                  // 根据 bearing 和 range 计算屏幕坐标
                  const {x, y} = this.calculatePosition(target.bearing, target.range);
                  // 绘制目标点
                  this.drawTarget(x, y, target.mmsi, target.cog, target.sog);
                  
                  // 根据风险等级设置颜色
                  const risk = risks.find(r => r.mmsi === target.mmsi);
                  if (risk) {
                      this.setRiskColor(risk.cpa, risk.tcpa);
                  }
              });
          }
      }
      ```
  
  **文件 5: `src/frontend/js/ar_cas_pro.js`**
  
  - **修改点:** 新增 WebSocket 连接逻辑，接收后端推送的数据，并更新雷达图组件。
  - **原因:** 这是 `ar_cas_pro.html` 页面的主逻辑文件，需要在这里集成数据获取和雷达图更新。
  - **具体代码示例:**
      ```javascript
      // 在 ar_cas_pro.js 中
      import RadarChart from './radar_chart.js'; // 假设支持模块化
  
      document.addEventListener('DOMContentLoaded', function() {
          // 1. 初始化雷达图组件
          const radarChart = new RadarChart('radar-chart-container');
  
          // 2. 建立 WebSocket 连接
          const ws = new WebSocket('ws://localhost:8000/ws/radar/567890123,345678901');
  
          ws.onmessage = function(event) {
              const data = JSON.parse(event.data);
              // 3. 更新雷达图
              radarChart.updateData(data.targets, data.risks);
          };
  
          ws.onerror = function(error) {
              console.error('WebSocket Error: ', error);
          };
      });
      ```
  
  **文件 6: `src/frontend/pages/ar_cas_pro.html`**
  
  - **修改点:** 在页面中添加一个用于放置雷达图的容器元素。
  - **原因:** 需要为 `RadarChart` 组件提供一个挂载点。
  - **具体代码示例:**
      ```html
      <!-- 在 ar_cas_pro.html 的 <body> 中合适位置添加 -->
      <div id="radar-chart-container" style="width: 600px; height: 600px; border: 1px solid #ccc;">
          <!-- 雷达图将在这里渲染 -->
      </div>
      ```
  
  ### 4. 技术风险与建议
  
  | 风险 | 建议 |
  | :--- | :--- |
  | **`radar_chart.js` 可能不完整或不存在** | 立即检查该文件的实际内容。如果不存在或功能不足，建议使用成熟的库如 `ECharts` 或 `D3.js` 进行开发，或基于 Canvas API 自行开发。 |
  | **WebSocket 连接稳定性** | 在 `ar_cas_pro.js` 中添加重连机制，确保连接断开后能自动恢复。 |
  | **碰撞风险评估算法准确性** | 初期可先实现简单的 CPA/TCPA 计算，后续根据实际测试结果进行迭代优化。 |
  | **前端性能** | 如果雷达图渲染复杂，考虑使用 `requestAnimationFrame` 优化渲染，或使用 Web Worker 进行数据处理。 |
  
  ### 5. 总结
  
  本次技术调研表明，基于现有项目结构，实现“AR CAS Pro 菜单雷达图显示”功能是**完全可行**的。主要工作集中在：
  
  1.  **后端:** 新增一个 WebSocket 端点，过滤并计算指定目标的雷达图数据。
  2.  **前端:** 完善或开发雷达图组件，并在目标页面中集成 WebSocket 数据更新逻辑。
  
  建议开发团队立即检查 `radar_chart.js` 的实际状态，以确定前端开发的具体工作量。
  
  ────────────────────────────────────────────────────────────
  ✅ deepseek-chat 完成
  
  ## ⚠️ 重要提示
  上方 📂 项目上下文 包含了任务相关的实际源文件。
  请基于这些文件设计方案，不要引用不存在的文件。
  
  ## 要求
  1. 基于调研结果和实际源码，设计详细技术方案
  2. 明确指出需要修改的文件和具体修改内容
  3. 定义接口规范（如有新增 API）
  4. 为开发工程师提供逐步实施指南
  
  项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  后端: src/backend/ (Python FastAPI)
  前端: src/frontend/ (HTML + JS)
  
  
  项目根目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  后端: src/backend/ (Python FastAPI)
  前端: src/frontend/ (HTML + JS)
  
────────────────────────────────────────────────────────────
⚡ 使用 DeepSeek V4 直连 (64K 输出, 流式)...

🔗 API: api.deepseek.com | 模型: deepseek-chat
────────────────────────────────────────────────────────────

好的，作为 PoseidonX 系统的架构师 (Architect)，我已收到任务并仔细分析了项目经理 (PM) 的任务分解和技术研究员 (Researcher) 的调研报告。

基于现有项目结构和源码，我将设计一份详细、可执行的技术方案，指导 Build 团队完成开发。

---

## 技术方案: AR CAS Pro 菜单雷达图显示开发

**任务编号:** TASK-2025-AR-001
**方案版本:** 1.0
**负责人:** Build 团队 PM

### 1. 总体架构设计

本方案采用 **WebSocket 实时数据推送 + 前端 Canvas 渲染** 的架构。

- **后端 (FastAPI):** 新增一个 WebSocket 端点，负责从现有的 AIS 数据服务中过滤出指定目标（双体船、货船），计算其相对于本船的方位、距离以及碰撞风险（CPA/TCPA），然后每 2 秒推送一次数据给前端。
- **前端 (HTML/JS):** 在 `ar_cas_pro.html` 页面中集成一个基于 Canvas 的雷达图组件 (`radar_chart.js`)。该组件通过 WebSocket 接收后端数据，并动态绘制雷达图，包括方位圈、距离圈、目标点、运动矢量以及碰撞风险等级。

```
+-------------------+      WebSocket (JSON)       +-------------------+
|                   |  <------------------------>  |                   |
|   FastAPI 后端    |      /ws/radar/{mmsis}      |   前端 HTML/JS    |
|                   |                              |                   |
|  - ais_data_service|                              |  - ar_cas_pro.html |
|  - collision_risk  |                              |  - ar_cas_pro.js   |
|  - websocket_manager|                             |  - radar_chart.js  |
+-------------------+                              +-------------------+
```

### 2. 详细接口规范

#### 2.1 WebSocket 接口

- **端点:** `ws://<host>:<port>/ws/radar/{mmsi_list}`
- **路径参数:**
    - `mmsi_list`: 字符串，多个 MMSI 用逗号分隔。例如: `567890123,345678901`
- **数据格式:** JSON
- **推送频率:** 每 2 秒一次
- **推送数据结构 (Server -> Client):**

```json
{
  "timestamp": "2025-03-21T10:00:00Z",
  "own_ship": {
    "latitude": 30.9036,
    "longitude": 122.4036
  },
  "targets": [
    {
      "mmsi": "567890123",
      "ship_name": "双体船",
      "latitude": 30.9100,
      "longitude": 122.4100,
      "cog": 46.0,
      "sog": 9.0,
      "bearing": 35.5,
      "range": 1.2,
      "risk_level": "medium"
    },
    {
      "mmsi": "345678901",
      "ship_name": "货船",
      "latitude": 30.9200,
      "longitude": 122.4300,
      "cog": 90.0,
      "sog": 12.0,
      "bearing": 80.2,
      "range": 2.8,
      "risk_level": "low"
    }
  ]
}
```

**字段说明:**
- `own_ship`: 本船固定位置信息。
- `targets`: 目标船列表。
    - `bearing`: 目标相对本船的方位角（度），正北为0度，顺时针。
    - `range`: 目标相对本船的距离（海里）。
    - `risk_level`: 碰撞风险等级，由后端计算。`high`, `medium`, `low`。

### 3. 需要修改的文件及具体实施指南

#### 3.1 后端修改

**文件 1: `src/backend/app/routers/ais_data.py`** (或新建 `src/backend/app/routers/radar_data.py`)

- **操作:** 新增一个 WebSocket 路由。
- **具体代码:**

```python
# 在 ais_data.py 或新建 radar_data.py 中
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.ais_data_service import get_target_data
from ..services.collision_risk_service import calculate_risk
from ..utils.geo_utils import calculate_bearing_and_range
import asyncio
import json

router = APIRouter()

@router.websocket("/ws/radar/{mmsi_list}")
async def websocket_radar_data(websocket: WebSocket, mmsi_list: str):
    await websocket.accept()
    target_mmsis = mmsi_list.split(",")
    # 本船固定位置
    own_ship_pos = (30.9036, 122.4036)
    
    try:
        while True:
            # 1. 获取指定 MMSI 的 AIS 数据
            targets_data = get_target_data(target_mmsis)
            
            # 2. 计算相对本船的方位和距离，并评估风险
            processed_targets = []
            for target in targets_data:
                target_pos = (target['latitude'], target['longitude'])
                bearing, range_nm = calculate_bearing_and_range(own_ship_pos, target_pos)
                
                # 计算碰撞风险
                risk_level = calculate_risk(own_ship_pos, (0, 0), target_pos, (target['cog'], target['sog']))
                
                processed_targets.append({
                    "mmsi": target['mmsi'],
                    "ship_name": target.get('ship_name', 'Unknown'),
                    "latitude": target['latitude'],
                    "longitude": target['longitude'],
                    "cog": target['cog'],
                    "sog": target['sog'],
                    "bearing": round(bearing, 1),
                    "range": round(range_nm, 2),
                    "risk_level": risk_level
                })
            
            # 3. 构建响应数据
            response_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "own_ship": {
                    "latitude": own_ship_pos[0],
                    "longitude": own_ship_pos[1]
                },
                "targets": processed_targets
            }
            
            # 4. 发送数据
            await websocket.send_json(response_data)
            
            # 5. 等待 2 秒
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        print(f"Client disconnected from radar websocket for MMSIs: {mmsi_list}")
```

**文件 2: `src/backend/app/services/ais_data_service.py`**

- **操作:** 新增 `get_target_data` 函数。
- **具体代码:**

```python
# 在 ais_data_service.py 中新增
def get_target_data(self, mmsi_list: list) -> list:
    """
    从数据源获取指定 MMSI 列表的目标数据。
    """
    # 假设 self.all_targets 是存储所有 AIS 目标数据的列表
    # 实际实现中，可能需要从数据库或缓存中查询
    filtered_targets = [target for target in self.all_targets if target['mmsi'] in mmsi_list]
    return filtered_targets
```

**文件 3: `src/backend/app/services/collision_risk_service.py`**

- **操作:** 修改 `calculate_risk` 函数，使其返回风险等级字符串。
- **具体代码:**

```python
# 在 collision_risk_service.py 中
def calculate_risk(own_pos, own_motion, target_pos, target_motion):
    """
    计算碰撞风险等级。
    返回: 'high', 'medium', 'low'
    """
    # 1. 计算 CPA 和 TCPA (使用现有或新增的算法)
    cpa, tcpa = calculate_cpa_tcpa(own_pos, own_motion, target_pos, target_motion)
    
    # 2. 根据 CPA 和 TCPA 判断风险等级
    if tcpa is not None and tcpa < 10 and cpa is not None and cpa < 1.0:
        return 'high'
    elif tcpa is not None and tcpa < 20 and cpa is not None and cpa < 2.0:
        return 'medium'
    else:
        return 'low'
```

**文件 4: `src/backend/app/utils/geo_utils.py`** (可能不存在，需要新建)

- **操作:** 新建工具文件，包含 `calculate_bearing_and_range` 函数。
- **具体代码:**

```python
# 新建 src/backend/app/utils/geo_utils.py
import math

def calculate_bearing_and_range(origin, destination):
    """
    计算从 origin 到 destination 的方位角和距离。
    origin, destination: (latitude, longitude) 元组
    返回: (bearing_deg, range_nm)
    """
    lat1, lon1 = math.radians(origin[0]), math.radians(origin[1])
    lat2, lon2 = math.radians(destination[0]), math.radians(destination[1])
    
    dlon = lon2 - lon1
    
    # 计算方位角
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360
    
    # 计算距离 (使用 Haversine 公式)
    a = math.sin((lat2 - lat1) / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_km = 6371 * c  # 地球半径 6371 km
    distance_nm = distance_km / 1.852  # 转换为海里
    
    return bearing, distance_nm
```

#### 3.2 前端修改

**文件 5: `src/frontend/js/radar_chart.js`**

- **操作:** 检查并完善该组件。假设该组件已存在基础框架，需要确保其 `updateData` 方法能正确处理新的数据格式。
- **具体代码 (核心逻辑):**

```javascript
// 在 radar_chart.js 中
class RadarChart {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.canvas = document.createElement('canvas');
        this.container.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');
        this.width = this.container.clientWidth;
        this.height = this.container.clientHeight;
        this.canvas.width = this.width;
        this.canvas.height = this.height;
        this.centerX = this.width / 2;
        this.centerY = this.height / 2;
        this.maxRange = options.maxRange || 5; // 最大显示距离 (海里)
        this.scale = Math.min(this.width, this.height) / 2 / this.maxRange;
    }

    // 更新数据
    updateData(data) {
        this.ctx.clearRect(0, 0, this.width, this.height);
        this.drawBackground();
        
        if (data && data.targets) {
            data.targets.forEach(target => {
                this.drawTarget(target);
            });
        }
    }

    // 绘制背景 (方位圈、距离圈)
    drawBackground() {
        const ctx = this.ctx;
        // 绘制距离圈 (1nm, 2nm, 3nm...)
        for (let i = 1; i <= this.maxRange; i++) {
            ctx.beginPath();
            ctx.arc(this.centerX, this.centerY, i * this.scale, 0, 2 * Math.PI);
            ctx.strokeStyle = 'rgba(0, 255, 0, 0.3)';
            ctx.stroke();
        }
        // 绘制方位线 (每30度)
        for (let deg = 0; deg < 360; deg += 30) {
            let rad = deg * Math.PI / 180;
            ctx.beginPath();
            ctx.moveTo(this.centerX, this.centerY);
            ctx.lineTo(this.centerX + Math.sin(rad) * this.maxRange * this.scale, 
                       this.centerY - Math.cos(rad) * this.maxRange * this.scale);
            ctx.strokeStyle = 'rgba(0, 255, 0, 0.2)';
            ctx.stroke();
        }
    }

    // 绘制单个目标
    drawTarget(target) {
        const ctx = this.ctx;
        const bearingRad = target.bearing * Math.PI / 180;
        const rangePx = target.range * this.scale;
        
        // 计算目标在 Canvas 上的坐标
        const x = this.centerX + Math.sin(bearingRad) * rangePx;
        const y = this.centerY - Math.cos(bearingRad) * rangePx;
        
        // 根据风险等级设置颜色
        let color;
        switch(target.risk_level) {
            case 'high': color = 'red'; break;
            case 'medium': color = 'yellow'; break;
            default: color = 'green';
        }
        
        // 绘制目标点
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = 'white';
        ctx.stroke();
        
        // 绘制目标标签
        ctx.fillStyle = 'white';
        ctx.font = '12px Arial';
        ctx.fillText(`${target.ship_name} (${target.mmsi})`, x + 10, y - 10);
        ctx.fillText(`COG: ${target.cog}° SOG: ${target.sog}kn`, x + 10, y + 5);
        
        // 绘制运动矢量
        const cogRad = target.cog * Math.PI / 180;
        const vectorLength = target.sog * 2; // 矢量长度与速度成正比
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + Math.sin(cogRad) * vectorLength, y - Math.cos(cogRad) * vectorLength);
        ctx.strokeStyle = color;
        ctx.stroke();
    }
}
```

**文件 6: `src/frontend/js/ar_cas_pro.js`**

- **操作:** 新增 WebSocket 连接和雷达图初始化逻辑。
- **具体代码:**

```javascript
// 在 ar_cas_pro.js 中
document.addEventListener('DOMContentLoaded', function() {
    // 1. 初始化雷达图组件
    const radarChart = new RadarChart('radar-chart-container', { maxRange: 5 });

    // 2. 建立 WebSocket 连接
    const ws = new WebSocket('ws://localhost:8000/ws/radar/567890123,345678901');

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        // 3. 更新雷达图
        radarChart.updateData(data);
    };

    ws.onerror = function(error) {
        console.error('WebSocket Error: ', error);
    };

    ws.onclose = function() {
        console.log('WebSocket connection closed. Attempting to reconnect...');
        // 可以在这里添加重连逻辑
        setTimeout(() => {
            // 重新连接
        }, 5000);
    };
});
```

**文件 7: `src/frontend/pages/ar_cas_pro.html`**

- **操作:** 在页面中添加雷达图容器，并引入必要的 JS 文件。
- **具体代码:**

```html
<!-- 在 ar_cas_pro.html 的 <body> 中合适位���添加 -->
<div id="radar-chart-container" style="width: 600px; height: 600px; border: 1px solid #00ff00; background-color: rgba(0, 0, 0, 0.8);">
    <!-- 雷达图将在这里渲染 -->
</div>

<!-- 确保在页面底部引入 JS 文件 -->
<script src="/static/js/radar_chart.js"></script>
<script src="/static/js/ar_cas_pro.js"></script>
```

### 4. 实施步骤与排期建议

| 步骤 | 任务描述 | 负责人 | 预计工时 |
| :--- | :--- | :--- | :--- |
| 1 | 后端: 新增 `geo_utils.py` 工具函数 | 后端工程师 | 0.5 人天 |
| 2 | 后端: 修改 `ais_data_service.py`，新增过滤函数 | 后端工程师 | 0.5 人天 |
| 3 | 后端: 修改 `collision_risk_service.py`，返回风险等级 | 后端工程师 | 0.5 人天 |
| 4 | 后端: 新增 WebSocket 路由 (`ais_data.py` 或新建文件) | 后端工程师 | 1 人天 |
| 5 | 前端: 完善 `radar_chart.js` 组件 | 前端工程师 | 2 人天 |
| 6 | 前端: 修改 `ar_cas_pro.js`，集成 WebSocket 和雷达图 | 前端工程师 | 1 人天 |
| 7 | 前端: 修改 `ar_cas_pro.html`，添加容器和 JS 引用 | 前端工程师 | 0.5 人天 |
| 8 | 集成测试与联调 | 全栈/QA | 1 人天 |
| **总计** | | | **7 人天** |

### 5. 风险与应对

- **风险:** `radar_chart.js` 可能不存在或功能严重不足。
    - **应对:** 如果不存在，前端工程师需基于 Canvas API 从头开发，工时增加至 3 人天。如果功能不足，评估修改成本。
- **风险:** WebSocket 连接不稳定。
    - **应对:** 在前端 `ar_cas_pro.js` 中实现自动重连机制，并添加友好的用户提示。
- **风险:** 碰撞风险评估算法过于简单，导致误报。
    - **应对:** 初期实现基础版本，后续根据实际测试数据迭代优化算法。在 UI 上明确提示此为“辅助决策”信息。

请 Build 团队 PM 确认此技术方案，并据此分配任务给开发工程师。

────────────────────────────────────────────────────────────
✅ deepseek-chat 完成
