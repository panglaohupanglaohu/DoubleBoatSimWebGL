# 架构设计 — architect

任务: 给build团队的PM发出一个任务，让货船距离双体船远一些，这个页面缺乏碰撞检测，或者给双体船添加货船的运动轨迹添加碰撞检测，产生避让动作
步骤: architecture
Agent: build_architect

---

📋 任务: ca077585-3e4
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
  给build团队的PM发出一个任务，让货船距离双体船远一些，这个页面缺乏碰撞检测，或者给双体船添加货船的运动轨迹添加碰撞检测，产生避让动作
  给build团队的PM发出一个任务，让货船距离双体船远一些，这个页面缺乏碰撞检测，或者给双体船添加货船的运动轨迹添加碰撞检测，产生避让动作
  
  ---
  
  ## Captain Agent 安全指令 (必须遵循)
  
  **任务指令**
  
  **发件人:** 系统架构师  
  **收件人:** Build 团队 PM  
  **优先级:** 高  
  **状态:** 待确认
  
  ---
  
  ### 任务描述
  
  当前系统缺乏对双体船与周边货船（AIS目标）之间的碰撞检测与自动避让逻辑。为确保航行安全，需实现以下功能之一（二选一）：
  
  1. **方案A（推荐）：** 为双体船添加基于AIS目标运动轨迹的碰撞检测算法，并在检测到碰撞风险时，自动生成避让动作（如调整航向/航速），使双体船主动远离高风险货船。
  
  2. **方案B（备选）：** 强制要求所有货船（AIS目标）在接近双体船时，自动调整航向/航速，保持安全距离。
  
  **建议采用方案A**，因为双体船作为本船，控制权更直接，且不影响外部AIS目标的原始数据。
  
  ---
  
  ### 具体要求
  
  - **碰撞检测逻辑：** 基于AIS目标的COG、SOG、位置，结合本船（双体船）的航向、航速，计算最近会遇点（CPA）和到达最近会遇点时间（TCPA）。当CPA小于安全阈值（如0.5海里）且TCPA小于阈值（如10分钟）时，触发警报。
  - **避让动作：** 自动调整双体船航向（如转向右舷）或航速（如减速），确保CPA增大至安全范围。避让动作应平滑、符合COLREGs规则。
  - **UI反馈：** 在界面上高亮显示高风险目标，并显示避让动作提示或自动执行状态。
  
  ---
  
  ### 交付物
  
  1. 碰撞检测算法模块（含CPA/TCPA计算）。
  2. 避让决策与执行逻辑（航向/航速调整）。
  3. 单元测试与模拟场景验证（至少3个典型碰撞风险场景）。
  4. 集成到现有船舶状态更新循环中，不影响其他功能。
  
  ---
  
  ### 截止时间
  
  请于 **2025-04-10 18:00** 前提交设计方案与开发排期。
  
  ---
  
  请确认收到并分配资源。如有疑问，请及时沟通。
  
  
  ## 前序步骤的产出 (递进式摘要)
  
  ### 步骤 01: pm_decompose
  任务: 给build团队的PM发出一个任务，让货船距离双体船远一些，这个页面缺乏碰撞检测，或者给双体船添加货船的运动轨迹添加碰撞检测，产生避让动作
  步骤: pm_decompose
  📋 任务: ca077585-3e4
  🤖 Agent: PM (project_manager)
  📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  🔧 执行方式: DeepSeek API (直连)
  ────────────────────────────────────────────────────────────
  你是 PoseidonX 系统的 PM (project_manager)。
  你是项目经理 (PM)。请对以下任务进行分解和规划:
  给build团队的PM发出一个任务，让货船距离双体船远一些，这个页面缺乏碰撞检测，或者给双体船添加货船的运动轨迹添加碰撞检测，产生避让动作
  给build团队的PM发出一个任务，让货船距离双体船远一些，这个页面缺乏碰撞检测，或者给双体船添加货船的运动轨迹添加碰撞检测，产生避让动作
  ## Captain Agent 安全指令 (必须遵循)
  **收件人:** Build 团队 PM
  当前系统缺乏对双体船与周边货船（AIS目标）之间的碰撞检测与自动避让逻辑。为确保航行安全，需实现以下功能之一（二选一）：
  1. **方案A（推荐）：** 为双体船添加基于AIS目标运动轨迹的碰撞检测算法，并在检测到碰撞风险时，自动生成避让动作（如调整航向/航速），使双体船主动远离高风险货船。
  **子任务拆解:**
    - *项目名称:** PoseidonX 船舶碰撞检测与避让系统
    - *任务ID:** TASK-BUILD-20250407-001
    - *发件人:** 系统架构师
    - *收件人:** Build 团队 PM
    - *状态:** 规划中
    - *核心决策:** 采用 **方案A**，即由双体船主动进行碰撞检测和避让。
    - **目标:** 开发一个独立的、可复用的 Python 模块，用于计算本船与目标船之间的最近会遇点（CPA）和到达最近会遇点时间（TCPA）。
    -    **输入:**
  
  ### 步骤 02: research (完整产出)
  
  # 研究分析 — researcher
  
  任务: 给build团队的PM发出一个任务，让货船距离双体船远一些，这个页面缺乏碰撞检测，或者给双体船添加货船的运动轨迹添加碰撞检测，产生避让动作
  步骤: research
  Agent: build_researcher
  
  ---
  
  📋 任务: ca077585-3e4
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
    给build团队的PM发出一个任务，让货船距离双体船远一些，这个页面缺乏碰撞检测，或者给双体船添加货船的运动轨迹添加碰撞检测，产生避让动作
    给build团队的PM发出一个任务，让货船距离双体船远一些，这个页面缺乏碰撞检测，或者给双体船添加货船的运动轨迹添加碰撞检测，产生避让动作
    
    ---
    
    ## Captain Agent 安全指令 (必须遵循)
    
    **任务指令**
    
    **发件人:** 系统架构师  
    **收件人:** Build 团队 PM  
    **优先级:** 高  
    **状态:** 待确认
    
    ---
    
    ### 任务描述
    
    当前系统缺乏对双体船与周边货船（AIS目标）之间的碰撞检测与自动避让逻辑。为确保航行安全，需实现以下功能之一（二选一）：
    
    1. **方案A（推荐）：** 为双体船添加基于AIS目标运动轨迹的碰撞检测算法，并在检测到碰撞风险时，自动生成避让动作（如调整航向/航速），使双体船主动远离高风险货船。
    
    2. **方案B（备选）：** 强制要求所有货船（AIS目标）在接近双体船时，自动调整航向/航速，保持安全距离。
    
    **建议采用方案A**，因为双体船作为本船，控制权更直接，且不影响外部AIS目标的原始数据。
    
    ---
    
    ### 具体要求
    
    - **碰撞检测逻辑：** 基于AIS目标的COG、SOG、位置，结合本船（双体船）的航向、航速，计算最近会遇点（CPA）和到达最近会遇点时间（TCPA）。当CPA小于安全阈值（如0.5海里）且TCPA小于阈值（如10分钟）时，触发警报。
    - **避让动作：** 自动调整双体船航向（如转向右舷）或航速（如减速），确保CPA增大至安全范围。避让动作应平滑、符合COLREGs规则。
    - **UI反馈：** 在界面上高亮显示高风险目标，并显示避让动作提示或自动执行状态。
    
    ---
    
    ### 交付物
    
    1. 碰撞检测算法模块（含CPA/TCPA计算）。
    2. 避让决策与执行逻辑（航向/航速调整）。
    3. 单元测试与模拟场景验证（至少3个典型碰撞风险场景）。
    4. 集成到现有船舶状态更新循环中，不影响其他功能。
    
    ---
    
    ### 截止时间
    
    请于 **2025-04-10 18:00** 前提交设计方案与开发排期。
    
    ---
    
    请确认收到并分配资源。如有疑问，请及时沟通。
    
    
    ## 前序步骤的产出 (递进式摘要)
    
    ### 步骤 01: pm_decompose (完整产出)
    
    # PM分解 — project_manager
    
    任务: 给build团队的PM发出一个任务，让货船距离双体船远一些，这个页面缺乏碰撞检测，或者给双体船添加货船的运动轨迹添加碰撞检测，产生避让动作
    步骤: pm_decompose
    Agent: build_pm
    
    ---
    
    📋 任务: ca077585-3e4
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
      给build团队的PM发出一个任务，让货船距离双体船远一些，这个页面缺乏碰撞检测，或者给双体船添加货船的运动轨迹添加碰撞检测，产生避让动作
      给build团队的PM发出一个任务，让货船距离双体船远一些，这个页面缺乏碰撞检测，或者给双体船添加货船的运动轨迹添加碰撞检测，产生避让动作
      
      ---
      
      ## Captain Agent 安全指令 (必须遵循)
      
      **任务指令**
      
      **发件人:** 系统架构师  
      **收件人:** Build 团队 PM  
      **优先级:** 高  
      **状态:** 待确认
      
      ---
      
      ### 任务描述
      
      当前系统缺乏对双体船与周边货船（AIS目标）之间的碰撞检测与自动避让逻辑。为确保航行安全，需实现以下功能之一（二选一）：
      
      1. **方案A（推荐）：** 为双体船添加基于AIS目标运动轨迹的碰撞检测算法，并在检测到碰撞风险时，自动生成避让动作（如调整航向/航速），使双体船主动远离高风险货船。
      
      2. **方案B（备选）：** 强制要求所有货船（AIS目标）在接近双体船时，自动调整航向/航速，保持安全距离。
      
      **建议采用方案A**，因为双体船作为本船，控制权更直接，且不影响外部AIS目标的原始数据。
      
      ---
      
      ### 具体要求
      
      - **碰撞检测逻辑：** 基于AIS目标的COG、SOG、位置，结合本船（双体船）的航向、航速，计算最近会遇点（CPA）和到达最近会遇点时间（TCPA）。当CPA小于安全阈值（如0.5海里）且TCPA小于阈值（如10分钟）时，触发警报。
      - **避让动作：** 自动调整双体船航向（如转向右舷）或航速（如减速），确保CPA增大至安全范围。避让动作应平滑、符合COLREGs规则。
      - **UI反馈：** 在界面上高亮显示高风险目标，并显示避让动作提示或自动执行状态。
      
      ---
      
      ### 交付物
      
      1. 碰撞检测算法模块（含CPA/TCPA计算）。
      2. 避让决策与执行逻辑（航向/航速调整）。
      3. 单元测试与模拟场景验证（至少3个典型碰撞风险场景）。
      4. 集成到现有船舶状态更新循环中，不影响其他功能。
      
      ---
      
      ### 截止时间
      
      请于 **2025-04-10 18:00** 前提交设计方案与开发排期。
      
      ---
      
      请确认收到并分配资源。如有疑问，请及时沟通。
      
      
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
    
    好的，项目经理。我已收到系统架构师下达的高优先级任务指令。
    
    作为 PoseidonX 系统的项目经理，我将对该任务进行详细分解、风险评估和规划，并输出一份结构化的任务分解文档，供后续团队执行。
    
    ---
    
    ### 任务分解文档
    
    **项目名称:** PoseidonX 船舶碰撞检测与避让系统
    **任务ID:** TASK-BUILD-20250407-001
    **发件人:** 系统架构师
    **收件人:** Build 团队 PM
    **优先级:** 高
    **状态:** 规划中
    
    ---
    
    ### 1. 任务概述
    
    为 PoseidonX 系统增加核心安全功能：基于 AIS 数据的碰撞检测与自动避让逻辑。系统需能实时计算本船（双体船）与周边货船（AIS目标）的碰撞风险，并在必要时自动执行避让动作，确保航行安全。
    
    **核心决策:** 采用 **方案A**，即由双体船主动进行碰撞检测和避让。
    
    ### 2. 需求分析与子任务拆解
    
    根据任务要求，我将此任务拆解为以下 5 个可执行的子步骤：
    
    #### 子任务 1: 碰撞检测算法模块开发 (CPA/TCPA 计算)
    
    -   **目标:** 开发一个独立的、可复用的 Python 模块，用于计算本船与目标船之间的最近会遇点（CPA）和到达最近会遇点时间（TCPA）。
    -   **输入:**
        -   本船（双体船）: 纬度、经度、航向（COG）、航速（SOG）。
        -   目标船（货船）: 纬度、经度、航向（COG）、航速（SOG）。
    -   **输出:**
        -   `cpa_distance`: 最近会遇距离（海里）。
        -   `tcpa_time`: 到达最近会遇点的时间（分钟）。
        -   `is_collision_risk`: 布尔值，当 `cpa_distance < 安全阈值` 且 `tcpa_time < 时间阈值` 时为 `True`。
    -   **依赖关系:** 无。这是一个纯数学计算模块，可独立开发测试。
    -   **技术风险:** 低。算法成熟，有标准公式可循。
    -   **负责人:** 算法工程师
    
    #### 子任务 2: 避让决策与执行逻辑开发
    
    -   **目标:** 开发决策逻辑，当检测到碰撞风险时，生成具体的避让动作指令（调整航向/航速）。
    -   **核心逻辑:**
        -   **决策:** 基于 CPA/TCPA 结果，判断风险等级（警告、危险、紧急）。
        -   **动作生成:** 根据 COLREGs 规则（国际海上避碰规则），生成避让动作。例如：
            -   默认转向右舷。
            -   若无法转向，则减速。
            -   动作幅度需平滑，避免剧烈变化。
        -   **执行:** 将生成的航向/航速指令发送给船舶控制系统（或模拟接口）。
    -   **输入:** 子任务1的输出（`is_collision_risk`, `cpa_distance`, `tcpa_time`）。
    -   **输出:** 避让指令（`new_course`, `new_speed`）。
    -   **依赖关系:** 强依赖于子任务1的输出。
    -   **技术风险:** 中。COLREGs 规则复杂，需要正确理解和实现，避免产生新的风险。
    -   **负责人:** 算法工程师 / 领域专家
    
    #### 子任务 3: UI 反馈与交互开发
    
    -   **目标:** 在前端界面上，为操作员提供清晰的碰撞风险视觉反馈和避让状态提示。
    -   **功能:**
        -   **高亮风险目标:** 在雷达/海图界面上，用红色或闪烁边框高亮显示被判定为高风险的目标船。
        -   **显示风险信息:** 在目标信息面板或弹窗中显示 CPA、TCPA 值。
        -   **避让状态指示:** 显示一个状态栏或图标，指示当前系统是否处于自动避让模式，以及正在执行的避让动作（如“正在右转10度”）。
    -   **输入:** 子任务1和2的输出数据（风险目标列表、避让指令）。
    -   **输出:** 前端 UI 更新。
    -   **依赖关系:** 依赖于子任务1和2提供的后端 API 或 WebSocket 数据。
    -   **技术风险:** 低。前端技术栈成熟，主要工作是数据绑定和 UI 组件开发。
    -   **负责人:** 前端工程师
    
    #### 子任务 4: 系统集成与状态循环更新
    
    -   **目标:** 将上述三个模块无缝集成到现有的 PoseidonX 后端系统中，并确保其在主状态更新循环中被正确调用。
    -   **集成点:**
        -   在 `backend/services/ship_state_service.py` 或类似的主循环中，增加对碰撞检测模块的调用。
        -   将避让指令写入船舶状态对象，供其他模块（如自动驾���模块）读取。
        -   通过 WebSocket 将风险数据和避让状态推送给前端。
    -   **依赖关系:** 强依赖于子任务1、2、3的完成。
    -   **技术风险:** 中。需要确保新逻辑不阻塞主循环，不影响现有功能（如数据记录、AIS 解析）。需要设计好接口和异常处理。
    -   **负责人:** 后端工程师
    
    #### 子任务 5: 测试与验证
    
    -   **目标:** 确保所有功能正确、稳定，并覆盖典型碰撞风险场景。
    -   **测试内容:**
        -   **单元测试:** 对 CPA/TCPA 计算、避让决策逻辑进行单元测试。
        -   **模拟场景测试:** 创建至少 3 个模拟场景进行端到端测试：
            1.  **正面交叉相遇:** 货船从右舷接近，本船应右转。
            2.  **对遇局面:** 货船迎面而来，本船应右转。
            3.  **追越局面:** 货船从后方追越，本船应保持航向航速或小幅调整。
        -   **回归测试:** 确保新功能不影响现有功能。
    -   **依赖关系:** 依赖于子任务4的集成完成。
    -   **技术风险:** 低。测试框架已存在。
    -   **负责人:** QA 工程师 / 开发者
    
    ### 3. 技术风险与依赖关系总结
    
    | 风险/依赖 | 描述 | 影响 | 缓解措施 |
    | :--- | :--- | :--- | :--- |
    | **COLREGs 规则复杂性** | 避让逻辑需要正确理解和实现 COLREGs 规则，否则可能产生不安全行为。 | 高 | 邀请航海领域专家参与评审，使用模拟器进行充分测试。 |
    | **主循环性能** | 碰撞检测算法（尤其是对大量 AIS 目标）可能成为性能瓶颈，阻塞主循环。 | 中 | 优化算法，使用异步计算或线程池，设置计算频率上限。 |
    | **数据接口变更** | 后端 API 或 WebSocket 数据结构的变更可能导致前后端对接失败。 | 中 | 在开发前定义好接口契约（API Schema），进行接口联调。 |
    | **依赖关系** | 子任务2、3、4 都强依赖于子任务1。 | 高 | 优先安排子任务1的开发，并尽早提供模拟数据供其他任务并行开发。 |
    
    ### 4. 开发排期与资源分配
    
    | 子任务 | 负责人 | 预计工时 (人天) | 开始日期 | 结束日期 | 关键里程碑 |
    | :--- | :--- | :--- | :--- | :--- | :--- |
    | 1. 碰撞检测算法模块 | 算法工程师 | 2 | 2025-04-08 | 2025-04-09 | 完成算法原型和单元测试 |
    | 2. 避让决策与执行逻辑 | 算法工程师 | 3 | 2025-04-09 | 2025-04-11 | 完成决策逻辑和模拟验证 |
    | 3. UI 反馈与交互开发 | 前端工程师 | 2 | 2025-04-10 | 2025-04-11 | 完成 UI 组件开发和联调 |
    | 4. 系统集成与状态循环 | 后端工程师 | 2 | 2025-04-11 | 2025-04-12 | 完成集成并部署到测试环境 |
    | 5. 测试与验证 | QA / 开发者 | 2 | 2025-04-12 | 2025-04-13 | 完成所有测试用例，输出测试报告 |
    
    **总工期:** 6 天 (2025-04-08 至 2025-04-13)
    **交付日期:** **2025-04-13 18:00** (早于要求的截止日期)
    
    ### 5. 后续行动
    
    1.  **资源确认:** 请确认上述资源分配（算法工程师、前端工程师、后端工程师、QA）是否可用。
    2.  **启动会议:** 计划于 **2025-04-08 10:00** 召开项目启动会，向所有成员传达任务细节和技术方案。
    3.  **接口定义:** 后端工程师和前端工程师需在 **2025-04-09 12:00** 前完成 WebSocket 数据接口的定义。
    4.  **领域知识:** 请安排一位熟悉 COLREGs 规则的同事，在 **2025-04-09** 下午为算法工程师提供一次简短的培训或评审。
    
    请确认收到此规划。如有任何疑问或资源冲突，请及时沟通。
    
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
  
  好的，Researcher 收到任务。
  
  作为 PoseidonX 系统的技术研究员，我已仔细阅读了系统架构师的任务指令和项目经理的任务分解文档。现在，我将基于项目实际存在的文件，进行技术调研，分析实现方案的可行性，并列出具体的修改点。
  
  ---
  
  ### 技术调研报告
  
  **任务:** 双体船碰撞检测与自动避让系统
  **调研人:** Researcher
  **日期:** 2025-04-07
  
  #### 1. 项目现状分析
  
  根据提供的项目文件结构，我分析了以下关键文件：
  
  -   **后端核心:**
      -   `src/backend/main.py`: FastAPI 应用入口，定义了路由和应用生命周期。
      -   `src/backend/models/ship.py`: 定义了 `Ship` 和 `AISTarget` 数据模型。
      -   `src/backend/services/ship_state_service.py`: 船舶状态服务，包含 `update_ship_state` 主循环，是集成的关键点。
      -   `src/backend/services/collision_avoidance.py`: **此文件尚不存在**，需要新建。
      -   `src/backend/services/ais_service.py`: AIS 服务，负责解析和提供 AIS 目标数据。
  -   **前端核心:**
      -   `src/frontend/index.html`: 主页面，包含 Canvas 用于绘制海图。
      -   `src/frontend/js/simulation.js`: 核心仿真逻辑，包含 `updateSimulation` 主循环和 `drawScene` 绘制函数。
      -   `src/frontend/js/aisManager.js`: 管理 AIS 目标数据。
      -   `src/frontend/js/stateManager.js`: 管理应用状态。
  
  **结论:** 项目结构清晰，前后端分离。后端使用 FastAPI，前端使用原生 HTML/JS。现有代码为集成碰撞检测和避让逻辑提供了良好的基础。
  
  #### 2. 方案可行性分析
  
  **方案A（推荐）：双体船主动避让** 是完全可行的。
  
  -   **技术可行性:** CPA/TCPA 算法是成熟的标准算法，易于实现。COLREGs 规则可以简化为几种典型场景（交叉、对遇、追越）的决策逻辑。前端 Canvas 绘制可以轻松实现高亮和状态显示。
  -   **架构可行性:** 后端 `ship_state_service.py` 的主循环是理想的集成点。我们可以创建一个新的 `collision_avoidance.py` 服务模块，在其中实现核心算法，然后在主循环中调用它。
  -   **风险:** 主要风险在于 COLREGs 规则的实现复杂性，以及实时计算对主循环性能的影响。但通过合理的算法设计和异步处理，这些风险是可控的。
  
  #### 3. 需要修改/新建的文件及具体修改点
  
  以下是根据项目实际文件，列出的详细修改计划：
  
  ##### 3.1 新建文件: `src/backend/services/collision_avoidance.py`
  
  **目的:** 封装碰撞检测和避让决策的核心算法。
  
  **内容:**
  1.  **`calculate_cpa_tcpa(own_ship: Ship, target: AISTarget) -> tuple`**:
      -   **输入:** 本船 (`Ship`) 和目标船 (`AISTarget`) 对象。
      -   **逻辑:** 实现标准的 CPA/TCPA 计算公式。需要从 `Ship` 对象获取 `latitude`, `longitude`, `cog`, `sog`；从 `AISTarget` 对象获取 `latitude`, `longitude`, `cog`, `sog`。
      -   **输出:** `cpa_distance` (海里), `tcpa_time` (秒或分钟), `is_collision_risk` (布尔值)。
      -   **参考代码行:** `src/backend/models/ship.py` 第 10-30 行定义了 `Ship` 和 `AISTarget` 的数据结构。
  
  2.  **`decide_avoidance_action(own_ship: Ship, target: AISTarget, cpa_distance: float, tcpa_time: float) -> dict`**:
      -   **输入:** 本船、目标船、CPA、TCPA。
      -   **逻辑:** 基于 CPA/TCPA 和 COLREGs 规则（简化版）生成避让指令。
          -   如果 `cpa_distance < 0.5` 海里且 `tcpa_time < 600` 秒 (10分钟):
              -   判断会遇局面（交叉、对遇、追越）。
              -   生成指令，例如 `{'action': 'turn', 'value': 15}` (右转15度) 或 `{'action': 'slow_down', 'value': 5}` (减速5节)。
      -   **输出:** 包含避让动作的字典。
  
  ##### 3.2 修改文件: `src/backend/services/ship_state_service.py`
  
  **目的:** 将碰撞检测和避让逻辑集成到主状态更新循环中。
  
  **修改点:**
  1.  **导入新模块:** 在文件顶部添加 `from .collision_avoidance import calculate_cpa_tcpa, decide_avoidance_action`。
  2.  **在 `update_ship_state` 函数中集成 (约第 50-80 行):**
      -   在更新完本船位置和 AIS 目标列表后，添加以下逻辑：
          ```python
          # 伪代码
          from .collision_avoidance import calculate_cpa_tcpa, decide_avoidance_action
          
          # 获取本船状态 (假设从全局状态或参数传入)
          own_ship = get_current_ship_state() 
          ais_targets = get_current_ais_targets()
          
          for target in ais_targets:
              cpa, tcpa, is_risk = calculate_cpa_tcpa(own_ship, target)
              if is_risk:
                  # 标记高风险目标
                  target.is_high_risk = True 
                  # 生成避让动作
                  action = decide_avoidance_action(own_ship, target, cpa, tcpa)
                  # 将避让指令应用到本船 (例如，修改 own_ship 的 target_course 和 target_speed)
                  apply_avoidance_action(own_ship, action)
                  # 记录日志
                  logger.warning(f"Collision risk detected with target {target.mmsi}. Action: {action}")
                  break # 一次只处理一个最高风险的目标，或处理所有风险
          ```
      -   **性能考虑:** 如果 AIS 目标数量很大（>100），建议使用 `asyncio` 或线程池来并行计算 CPA/TCPA，避免阻塞主循环。
  
  ##### 3.3 修改文件: `src/backend/models/ship.py`
  
  **目的:** 为 `AISTarget` 模型添加风险状态字段，方便前端识别。
  
  **修改点:**
  1.  **在 `AISTarget` 类中 (约第 25 行):**
      -   添加一个新字段 `is_high_risk: bool = False`。
      -   添加一个新字段 `cpa_distance: Optional[float] = None`。
      -   添加一个新字段 `tcpa_time: Optional[float] = None`。
      -   添加一个新字段 `suggested_action: Optional[str] = None`。
  
  ##### 3.4 修改文件: `src/frontend/js/simulation.js`
  
  **目的:** 在前端绘制高风险目标和避让状态。
  
  **修改点:**
  1.  **在 `drawScene` 函数中 (约第 150-250 行):**
      -   在绘制 AIS 目标的循环中，检查 `target.is_high_risk` 属性。
      -   如果为 `True`，则改变绘制颜色（例如，从默认颜色变为红色），并增加闪烁效果或外发光。
      -   在 Canvas 的角落或状态栏绘制当前避让状态，例如从 `stateManager` 获取 `avoidanceStatus`。
  
  ##### 3.5 修改文件: `src/frontend/js/aisManager.js`
  
  **目的:** 确保前端能正确解析后端传来的新字段。
  
  **修改点:**
  1.  **在 `updateAISTargets` 或类似的数据处理函数中 (约第 40-60 行):**
      -   确保在解析后端 WebSocket 或 API 返回的 JSON 数据时，能正确读取 `is_high_risk`, `cpa_distance`, `tcpa_time`, `suggested_action` 字段，并更新到对应的 `AISTarget` 对象上。
  
  ##### 3.6 修改文件: `src/frontend/js/stateManager.js`
  
  **目的:** 管理避让系统的全局状态。
  
  **修改点:**
  1.  **在 `initialState` 对象中 (约第 5 行):**
      -   添加一个新状态: `avoidanceActive: false`。
      -   添加一个新状态: `currentAvoidanceAction: null`。
  2.  **添加更新方法:**
      -   `setAvoidanceActive(status: boolean)`
      -   `setCurrentAvoidanceAction(action: object)`
  
  #### 4. 总结与建议
  
  -   **方案可行:** 基于现有项目结构，实现方案A是直接且高效的。
  -   **核心工作在后端:** 主要开发工作集中在新建的 `collision_avoidance.py` 和修改 `ship_state_service.py`。
  -   **前端改动较小:** 前端主要是 UI 层面的视觉反馈，改动量不大。
  -   **建议:** 开发时，先实现一个简化的 COLREGs 逻辑（例如，只处理交叉相遇局面），然后逐步迭代完善。同时，务必为 `collision_avoidance.py` 编写充分的单元测试。
  
  我已经准备好将这份详细的技术调研报告提交给 Build 团队的 PM，作为任务执行的依据。
  
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

好的，系统架构师收到。

作为 PoseidonX 系统的架构师，我已审阅了项目经理 (PM) 的任务分解和研究员 (Researcher) 的技术调研报告。基于他们的产出，我将为 Build 团队制定一份详细、可执行的技术方案。

---

## 技术方案: 双体船碰撞检测与自动避让系统

**版本:** 1.0
**起草人:** 系统架构师
**日期:** 2025-04-07

### 1. 概述

本方案旨在为 PoseidonX 系统增加核心安全功能：基于 AIS 数据的实时碰撞检测与自动避让逻辑。系统将采用 **方案A**，即由双体船（本船）主动进行碰撞检测和避让，以确保航行安全，符合 COLREGs 规则。

### 2. 架构设计

本功能将作为后端服务的一个独立模块实现，并通过 WebSocket 与前端进行数据同步。

```mermaid
graph TD
    subgraph "后端 (Python FastAPI)"
        A[ship_state_service.py<br>(主循环)] --> B{collision_avoidance.py<br>(碰撞检测与避让模块)};
        B --> C[models/ship.py<br>(数据模型)];
        C --> D[WebSocket 管理器];
        D --> E[前端];
    end

    subgraph "前端 (HTML/JS)"
        E --> F[stateManager.js<br>(状态管理)];
        F --> G[aisManager.js<br>(AIS 数据管理)];
        G --> H[simulation.js<br>(绘制与交互)];
    end

    B --> I[日志系统];
```

### 3. 详细设计

#### 3.1 后端模块: `src/backend/services/collision_avoidance.py` (新建)

**职责:** 封装碰撞检测和避让决策的核心算法。

**核心函数:**

1.  **`calculate_cpa_tcpa(own_ship: Ship, target: AISTarget) -> tuple`**
    -   **算法:** 使用标准的大地测量学公式，将经纬度转换为笛卡尔坐标系（或直接使用球面三角法），计算两船相对速度向量，进而求出最近会遇点 (CPA) 和到达时间 (TCPA)。
    -   **输入:**
        -   `own_ship`: 本船对象，包含 `latitude`, `longitude`, `cog`, `sog`。
        -   `target`: 目标船对象，包含 `latitude`, `longitude`, `cog`, `sog`。
    -   **输出:**
        -   `cpa_distance` (海里): 最近会遇距离。
        -   `tcpa_time` (秒): 到达最近会遇点的时间。
        -   `is_collision_risk` (bool): 当 `cpa_distance < CPA_THRESHOLD` (如 0.5 海里) 且 `tcpa_time < TCPA_THRESHOLD` (如 600 秒) 时为 `True`。

2.  **`decide_avoidance_action(own_ship: Ship, target: AISTarget, cpa_distance: float, tcpa_time: float) -> dict`**
    -   **逻辑 (简化版 COLREGs):**
        -   **风险等级判定:**
            -   `DANGER`: `cpa_distance < 0.3` 海里 且 `tcpa_time < 300` 秒。
            -   `WARNING`: `cpa_distance < 0.5` 海里 且 `tcpa_time < 600` 秒。
        -   **局面判定 (基于相对方位和航向):**
            -   **对遇 (Head-on):** 目标船在正前方 ±6° 内，且航向相反。
            -   **交叉 (Crossing):** 目标船在右舷或左舷。
            -   **追越 (Overtaking):** 目标船从后方接近。
        -   **动作生成 (遵循 COLREGs):**
            -   **对遇/右舷交叉:** 本船向右转向 (如 15°-30°)。
            -   **左舷交叉:** 本船保向保速 (让路船是对方)。
            -   **追越:** 本船保向保速 (让路船是对方)。
            -   **紧急情况:** 大幅转向或减速。
    -   **输出:**
        -   `action`: 字符串，如 `"turn_starboard"`, `"slow_down"`, `"maintain"`。
        -   `value`: 动作幅度，如转向角度 (度) 或减速值 (节)。
        -   `risk_level`: 风险等级，如 `"DANGER"`, `"WARNING"`。

#### 3.2 数据模型修改: `src/backend/models/ship.py`

**修改点:** 为 `AISTarget` 类添加风险相关字段，以便将计算结果传递给前端。

```python
# 在 AISTarget 类中增加 (约第 25 行)
class AISTarget(BaseModel):
    # ... 现有字段 ...
    is_high_risk: bool = False
    cpa_distance: Optional[float] = None
    tcpa_time: Optional[float] = None
    suggested_action: Optional[str] = None
    risk_level: Optional[str] = None
```

#### 3.3 主循环集成: `src/backend/services/ship_state_service.py`

**修改点:** 在 `update_ship_state` 函数中集成碰撞检测和避让逻辑。

```python
# 在文件顶部添加导入 (约第 5 行)
from .collision_avoidance import calculate_cpa_tcpa, decide_avoidance_action
from ..models.ship import Ship, AISTarget

# 在 update_ship_state 函数中 (约第 50-80 行)
async def update_ship_state():
    # ... 现有逻辑 ...
    
    # 获取本船和所有 AIS 目标
    own_ship: Ship = get_current_ship_state()
    ais_targets: List[AISTarget] = get_current_ais_targets()
    
    # 碰撞检测与避让
    highest_risk_target = None
    highest_risk_score = 0
    
    for target in ais_targets:
        cpa, tcpa, is_risk = calculate_cpa_tcpa(own_ship, target)
        target.cpa_distance = cpa
        target.tcpa_time = tcpa
        
        if is_risk:
            target.is_high_risk = True
            # 计算风险评分 (例如: 1/cpa * 1/tcpa)
            risk_score = 1.0 / (cpa + 0.01) * 1.0 / (tcpa + 1.0)
            if risk_score > highest_risk_score:
                highest_risk_score = risk_score
                highest_risk_target = target
    
    # 对最高风险目标执行避让
    if highest_risk_target:
        action = decide_avoidance_action(own_ship, highest_risk_target, 
                                          highest_risk_target.cpa_distance, 
                                          highest_risk_target.tcpa_time)
        highest_risk_target.suggested_action = f"{action['action']}: {action['value']}"
        highest_risk_target.risk_level = action['risk_level']
        
        # 应用避让动作到本船 (例如，修改 own_ship 的 target_course)
        if action['action'] == 'turn_starboard':
            own_ship.target_course = (own_ship.cog + action['value']) % 360
        elif action['action'] == 'slow_down':
            own_ship.target_speed = max(0, own_ship.sog - action['value'])
        # ... 其他动作
        
        logger.warning(f"Collision risk with target {highest_risk_target.mmsi}. Action: {action}")
    
    # ... 后续逻辑 (通过 WebSocket 发送状态)
```

#### 3.4 前端修改

1.  **`src/frontend/js/stateManager.js`**: 添加 `avoidanceActive` 和 `currentAvoidanceAction` 状态。
2.  **`src/frontend/js/aisManager.js`**: 确保能解析后端传来的 `is_high_risk`, `cpa_distance` 等新字段。
3.  **`src/frontend/js/simulation.js`**:
    -   在 `drawScene` 函数中，检查 `target.is_high_risk`，若为 `True` 则用红色高亮绘制，并显示 CPA/TCPA 值。
    -   在 Canvas 上显示当前避让状态（从 `stateManager` 获取）。

### 4. 接口规范

**WebSocket 消息 (后端 -> 前端):**

```json
{
  "type": "state_update",
  "data": {
    "ownShip": { ... },
    "aisTargets": [
      {
        "mmsi": "123456789",
        "latitude": 30.0,
        "longitude": 120.0,
        "cog": 45.0,
        "sog": 12.0,
        "is_high_risk": true,
        "cpa_distance": 0.3,
        "tcpa_time": 120,
        "suggested_action": "turn_starboard: 15",
        "risk_level": "WARNING"
      }
    ],
    "avoidanceActive": true,
    "currentAvoidanceAction": "正在右转15度"
  }
}
```

### 5. 实施步骤 (给 Build 团队)

1.  **创建 `collision_avoidance.py`**: 实现 `calculate_cpa_tcpa` 和 `decide_avoidance_action` 函数。**（负责人：算法工程师，预计 2 天）**
2.  **修改 `ship.py`**: 为 `AISTarget` 添加风险相关字段。**（负责人：后端工程师，预计 0.5 天）**
3.  **修改 `ship_state_service.py`**: 集成碰撞检测和避让逻辑到主循环。**（负责人：后端工程师，预计 1 天）**
4.  **修改前端文件**: 更新 `stateManager.js`, `aisManager.js`, `simulation.js` 以显示风险信息和避让状态。**（负责人：前端工程师，预计 1.5 天）**
5.  **编写单元测试**: 为 `collision_avoidance.py` 编写至少 3 个场景的测试用例。**（负责人：算法工程师，预计 1 天）**
6.  **集成测试**: 部署到测试环境，进行端到端验证。**（负责人：QA 工程师，预计 1 天）**

### 6. 风险与缓解措施

| 风险 | 缓解措施 |
| :--- | :--- |
| COLREGs 规则实现复杂 | 先实现简化版（对遇、右舷交叉），后续迭代完善。邀请航海专家评审。 |
| 主循环性能下降 | 使用 `asyncio.gather` 或线程池并行计算 CPA/TCPA。设置计算频率上限 (如 1Hz)。 |
| 前端数据解析错误 | 前后端开发前，共同确认 WebSocket 消息的 JSON Schema。 |

---

**请 Build 团队 PM 确认收到此技术方案，并按照实施步骤分配资源。如有疑问，请及时沟通。**

────────────────────────────────────────────────────────────
✅ deepseek-chat 完成
