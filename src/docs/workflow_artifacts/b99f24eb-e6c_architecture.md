# 架构设计 — architect

任务: 任务指令已下达：
步骤: architecture
Agent: build_architect

---

📋 任务: b99f24eb-e6c
🤖 Agent: Architect (architect)
📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
⏱️ 超时: 300s
────────────────────────────────────────────────────────────
📝 提示词:
  你是 PoseidonX 系统的 Architect (architect)。
  请执行以下开发任务:
  
  你是系统架构师。请为以下任务设计技术方案:
  
  ## 任务
  任务指令已下达：
  好的，船长。已收到您的指令。
  
  **任务指令已下达：**
  
  **收件人：** Build团队项目经理
  **主题：** 紧急任务 - 优化 navigation-v2.html 页面所有功能
  **任务内容：**
  1.  **目标：** 对 `navigation-v2.html` 页面的**所有功能**进行全面优化。
  2.  **范围：** 涵盖该页面当前所有交互、计算、显示及数据处理功能。
  3.  **时间要求：** 立即开始，进行**连续4小时**的集中优化工作。
  4.  **交付物：** 优化后的 `navigation-v2.html` 页面，确保功能更流畅、响应更迅速、计算更准确。
  
  **船长指示：**
  *   此任务优先级为最高。
  *   请PM立即组织资源，明确分工，确保在4小时窗口内达成优化目标。
  *   优化过程中需确保核心导航与态势显示功能的稳定与精确，任何改动不得影响航行安全相关的基础计算。
  *   4小时后，我需要看到明确的优化成果报告。
  
  请确认任务接收并开始执行。
  
  ## 前序步骤的产出 (请仔细阅读)
  
  ## 上一步产出 — PM分解 (project_manager)
  
  # PM分解 — project_manager
  
  任务: 任务指令已下达：
  步骤: pm_decompose
  Agent: build_pm
  
  ---
  
  📋 任务: b99f24eb-e6c
  🤖 Agent: PM (project_manager)
  📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  ⏱️ 超时: 300s
  ────────────────────────────────────────────────────────────
  📝 提示词:
    你是 PoseidonX 系统的 PM (project_manager)。
    请执行以下开发任务:
    
    你是项目经理 (PM)。请对以下任务进行分解和规划:
    
    ## 任务
    任务指令已下达：
    好的，船长。已收到您的指令。
    
    **任务指令已下达：**
    
    **收件人：** Build团队项目经理
    **主题：** 紧急任务 - 优化 navigation-v2.html 页面所有功能
    **任务内容：**
    1.  **目标：** 对 `navigation-v2.html` 页面的**所有功能**进行全面优化。
    2.  **范围：** 涵盖该页面当前所有交互、计算、显示及数据处理功能。
    3.  **时间要求：** 立即开始，进行**连续4小时**的集中优化工作。
    4.  **交付物：** 优化后的 `navigation-v2.html` 页面，确保功能更流畅、响应更迅速、计算更准确。
    
    **船长指示：**
    *   此任务优先级为最高。
    *   请PM立即组织资源，明确分工，确保在4小时窗口内达成优化目标。
    *   优化过程中需确保核心导航与态势显示功能的稳定与精确，任何改动不得影响航行安全相关的基础计算。
    *   4小时后，我需要看到明确的优化成果报告。
    
    请确认任务接收并开始执行。
    
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
  🔗 使用模型池默认: deepseek-chat (deepseek)
  
  🔗 API: api.deepseek.com | 模型: deepseek-chat
  ────────────────────────────────────────────────────────────
  
  # PoseidonX 系统 - navigation-v2.html 页面优化任务分解
  
  ## 1. 任务概述
  **任务名称**: navigation-v2.html 页面功能优化  
  **优先级**: 最高 (P0)  
  **时间窗口**: 4小时连续工作  
  **负责人**: PM (项目经理)  
  **开始时间**: 立即  
  
  ## 2. 目标分解
  ### 2.1 核心目标
  - 提升页面所有功能的性能与用户体验
  - 确保核心导航与态势显示功能的稳定性
  - 优化计算准确性和响应速度
  
  ### 2.2 成功标准
  - 页面加载时间减少 ≥30%
  - 交互响应延迟 ≤100ms
  - 计算准确性100%
  - 无功能回归
  
  ## 3. 任务分解与分工
  
  ### 3.1 阶段一：分析与评估 (0-30分钟)
  **负责人**: 架构师 + 研究员
  
  #### 子任务：
  1. **页面功能清单梳理** (15分钟)
     - 识别所有交互功能
     - 列出所有计算模块
     - 标记所有数据展示组件
     - 记录所有API调用
  
  2. **性能基准测试** (15分钟)
     - 使用Chrome DevTools进行性能分析
     - 记录关键指标：
       - 首次内容绘制 (FCP)
       - 最大内容绘制 (LCP)
       - 首次输入延迟 (FID)
       - 累计布局偏移 (CLS)
     - 识别性能瓶颈
  
  ### 3.2 阶段二：优化实施 (30分钟 - 3.5小时)
  **负责人**: 前端开发团队 (2-3人)
  
  #### 子任务分组：
  
  #### A组：JavaScript优化 (主要开发者)
  1. **代码分析与重构** (45分钟)
     - 审查 `navigation-v2.html` 及相关JS文件
     - 识别并优化低效算法
     - 减少全局变量使用
     - 优化事件处理机制
  
  2. **计算性能优化** (60分钟)
     - 优化导航计算逻辑
     - 实现计算缓存机制
     - 减少不必要的重新计算
     - 优化数学运算（如三角函数计算）
  
  3. **异步处理优化** (45分钟)
     - 优化API调用序列
     - 实现请求合并
     - 添加请求取消机制
     - 优化WebSocket连接管理
  
  #### B组：渲染与交互优化 (主要开发者)
  1. **DOM操作优化** (60分钟)
     - 减少DOM查询次数
     - 使用文档片段批量更新
     - 优化CSS选择器性能
     - 实现虚拟滚动（如适用）
  
  2. **动画与过渡优化** (45分钟)
     - 使用CSS transform代替top/left
     - 优化重绘和回流
     - 使用requestAnimationFrame
     - 减少图层数量
  
  3. **内存管理优化** (30分钟)
     - 修复内存泄漏
     - 优化事件监听器管理
     - 清理未使用的对象引用
     - 优化图片资源加载
  
  ### 3.3 阶段三：测试与验证 (3.5 - 4小时)
  **负责人**: 质量保证工程师
  
  #### 子任务：
  1. **功能回归测试** (15分钟)
     - 验证所有原有功能正常
     - 测试边界条件
     - 验证数据准确性
  
  2. **性能对比测试** (15分钟)
     - 与优化前基准对比
     - 验证性能提升指标
     - 压力测试（模拟高负载）
  
  3. **安全与稳定性验证** (10分钟)
     - 验证核心导航计算准确性
     - 检查错误处理机制
     - 验证异常情况处理
  
  ## 4. 技术风险与依赖关系
  
  ### 4.1 技术风险
  | 风险项 | 概率 | 影响 | 缓解措施 |
  |--------|------|------|----------|
  | 优化引入新bug | 中 | 高 | 严格测试，保留原始版本备份 |
  | 性能提升不明显 | 低 | 中 | 多方案并行，优先实施高ROI优化 |
  | 兼容性问题 | 低 | 低 | 使用标准API，避免实验性特性 |
  | 时间不足 | 中 | 高 | 聚焦核心瓶颈，采用增量优化 |
  
  ### 4.2 依赖关系
  - **后端API稳定性**: 确保后端服务在优化期间稳定
  - **测试环境**: 需要与生产环境相似的数据集
  - **监控工具**: Chrome DevTools, Lighthouse, 性能监控脚本
  
  ## 5. 资源分配
  
  ### 5.1 人员配置
  - **项目经理 (PM)**: 1人 - 整体协调，进度跟踪
  - **架构师**: 1人 - 技术指导，方案审核
  - **前端开发者**: 2-3人 - 具体实施
  - **质量保证**: 1人 - 测试验证
  
  ### 5.2 工具准备
  - 代码编辑器/IDE
  - Chrome DevTools
  - Lighthouse
  - 性能监控脚本
  - Git版本控制
  - 本地测试服务器
  
  ## 6. 执行指导
  
  ### 6.1 开发指导原则
  1. **安全第一**: 任何改动不得影响航行安全相关计算
  2. **渐进增强**: 优先优化最影响用户体验的部分
  3. **可测量**: 所有优化必须有可量化的改进
  4. **可回滚**: 每个优化点应有独立提交，便于回滚
  
  ### 6.2 代码规范
  - 遵循现有代码风格
  - 添加有意义的注释
  - 更新相关文档
  - 确保向后兼容
  
  ### 6.3 测试要求
  - 单元测试覆盖关键计算函数
  - 集成测试验证整体功能
  - 性能测试对比优化效果
  - 跨浏览器测试（Chrome, Firefox, Edge）
  
  ## 7. 交付物清单
  
  ### 7.1 代码交付
  - 优化后的 `navigation-v2.html`
  - 相关的CSS/JS文件更新
  - 性能监控脚本（如开发）
  
  ### 7.2 文档交付
  - 优化报告（包含前后性能对比）
  - 修改清单（列出所有改动点）
  - 测试报告（功能与性能验证结果）
  - 后续优化建议
  
  ### 7.3 运行验证
  ```bash
  # 优化完成后运行测试
  cd /Users/panglaohu/Downloads/DoubleBoatClawSystem
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short
  ```
  
  ## 8. 时间线
  
  | 时间段 | 阶段 | 关键产出 |
  |--------|------|----------|
  | 0-30min | 分析与评估 | 性能���准报告，瓶颈分析 |
  | 30min-2h | 核心优化实施 | 主要性能问题修复 |
  | 2h-3.5h | 细节优化与调整 | 用户体验提升 |
  | 3.5h-4h | 测试与验证 | 测试报告，性能对比 |
  | 4h | 交付与汇报 | 优化成果报告 |
  
  ## 9. 沟通机制
  
  ### 9.1 进度同步
  - **每30分钟**: 简短站会，同步进展
  - **关键节点**: 即时通报重大发现或问题
  - **最终汇报**: 4小时后向船长汇报
  
  ### 9.2 问题上报
  1. 技术问题 → 架构师 → PM
  2. 资源问题 → PM
  3. 范围/时间问题 → PM → 船长
  
  ---
  
  **任务确认**: ✅ 已接收并开始执行  
  **开始时间**: NOW  
  **预计完成**: NOW + 4小时  
  
  **PM备注**: 所有团队成员请立即开始执行分配的任务。保持沟通畅通，遇到问题立即上报。优先保证核心导航功能的稳定性和准确性。
  
  ────────────────────────────────────────────────────────────
  ✅ deepseek-chat 完成
  
  
  
  ## 上一步产出 — 研究分析 (researcher)
  
  # 研究分析 — researcher
  
  任务: 任务指令已下达：
  步骤: research
  Agent: build_researcher
  
  ---
  
  📋 任务: b99f24eb-e6c
  🤖 Agent: Researcher (researcher)
  📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
  ⏱️ 超时: 300s
  ────────────────────────────────────────────────────────────
  📝 提示词:
    你是 PoseidonX 系统的 Researcher (researcher)。
    请执行以下开发任务:
    
    你是技术研究员。请对以下任务进行技术调研:
    
    ## 任务
    任务指令已下达：
    好的，船长。已收到您的指令。
    
    **任务指令已下达：**
    
    **收件人：** Build团队项目经理
    **主题：** 紧急任务 - 优化 navigation-v2.html 页面所有功能
    **任务内容：**
    1.  **目标：** 对 `navigation-v2.html` 页面的**所有功能**进行全面优化。
    2.  **范围：** 涵盖该页面当前所有交互、计算、显示及数据处理功能。
    3.  **时间要求：** 立即开始，进行**连续4小时**的集中优化工作。
    4.  **交付物：** 优化后的 `navigation-v2.html` 页面，确保功能更流畅、响应更迅速、计算更准确。
    
    **船长指示：**
    *   此任务优先级为最高。
    *   请PM立即组织资源，明确分工，确保在4小时窗口内达成优化目标。
    *   优化过程中需确保核心导航与态势显示功能的稳定与精确，任何改动不得影响航行安全相关的基础计算。
    *   4小时后，我需要看到明确的优化成果报告。
    
    请确认任务接收并开始执行。
    
    ## 前序步骤的产出 (请仔细阅读)
    
    ## 上一步产出 — PM分解 (project_manager)
    
    # PM分解 — project_manager
    
    任务: 任务指令已下达：
    步骤: pm_decompose
    Agent: build_pm
    
    ---
    
    📋 任务: b99f24eb-e6c
    🤖 Agent: PM (project_manager)
    📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
    ⏱️ 超时: 300s
    ────────────────────────────────────────────────────────────
    📝 提示词:
      你是 PoseidonX 系统的 PM (project_manager)。
      请执行以下开发任务:
      
      你是项目经理 (PM)。请对以下任务进行分解和规划:
      
      ## 任务
      任务指令已下达：
      好的，船长。已收到您的指令。
      
      **任务指令已下达：**
      
      **收件人：** Build团队项目经理
      **主题：** 紧急任务 - 优化 navigation-v2.html 页面所有功能
      **任务内容：**
      1.  **目标：** 对 `navigation-v2.html` 页面的**所有功能**进行全面优化。
      2.  **范围：** 涵盖该页面当前所有交互、计算、显示及数据处理功能。
      3.  **时间要求：** 立即开始，进行**连续4小时**的集中优化工作。
      4.  **交付物：** 优化后的 `navigation-v2.html` 页面，确保功能更流畅、响应更迅速、计算更准确。
      
      **船长指示：**
      *   此任务优先级为最高。
      *   请PM立即组织资源，明确分工，确保在4小时窗口内达成优化目标。
      *   优化过程中需确保核心导航与态势显示功能的稳定与精确，任何改动不得影响航行安全相关的基础计算。
      *   4小时后，我需要看到明确的优化成果报告。
      
      请确认任务接收并开始执行。
      
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
    🔗 使用模型池默认: deepseek-chat (deepseek)
    
    🔗 API: api.deepseek.com | 模型: deepseek-chat
    ────────────────────────────────────────────────────────────
    
    # PoseidonX 系统 - navigation-v2.html 页面优化任务分解
    
    ## 1. 任务概述
    **任务名称**: navigation-v2.html 页面功能优化  
    **优先级**: 最高 (P0)  
    **时间窗口**: 4小时连续工作  
    **负责人**: PM (项目经理)  
    **开始时间**: 立即  
    
    ## 2. 目标分解
    ### 2.1 核心目标
    - 提升页面所有功能的性能与用户体验
    - 确保核心导航与态势显示功能的稳定性
    - 优化计算准确性和响应速度
    
    ### 2.2 成功标准
    - 页面加载时间减少 ≥30%
    - 交互响应延迟 ≤100ms
    - 计算准确性100%
    - 无功能回归
    
    ## 3. 任务分解与分工
    
    ### 3.1 阶段一：分析与评估 (0-30分钟)
    **负责人**: 架构师 + 研究员
    
    #### 子任务：
    1. **页面功能清单梳理** (15分钟)
       - 识别所有交互功能
       - 列出所有计算模块
       - 标记所有数据展示组件
       - 记录所有API调用
    
    2. **性能基准测试** (15分钟)
       - 使用Chrome DevTools进行性能分析
       - 记录关键指标：
         - 首次内容绘制 (FCP)
         - 最大内容绘制 (LCP)
         - 首次输入延迟 (FID)
         - 累计布局偏移 (CLS)
       - 识别性能瓶颈
    
    ### 3.2 阶段二：优化实施 (30分钟 - 3.5小时)
    **负责人**: 前端开发团队 (2-3人)
    
    #### 子任务分组：
    
    #### A组：JavaScript优化 (主要开发者)
    1. **代码分析与重构** (45分钟)
       - 审查 `navigation-v2.html` 及相关JS文件
       - 识别并优化低效算法
       - 减少全局变量使用
       - 优化事件处理机制
    
    2. **计算性能优化** (60分钟)
       - 优化导航计算逻辑
       - 实现计算缓存机制
       - 减少不必要的重新计算
       - 优化数学运算（如三角函数计算）
    
    3. **异步处理优化** (45分钟)
       - 优化API调用序列
       - 实现请求合并
       - 添加请求取消机制
       - 优化WebSocket连接管理
    
    #### B组：渲染与交互优化 (主要开发者)
    1. **DOM操作优化** (60分钟)
       - 减少DOM查询次数
       - 使用文档片段批量更新
       - 优化CSS选择器性能
       - 实现虚拟滚动（如适用）
    
    2. **动画与过渡优化** (45分钟)
       - 使用CSS transform代替top/left
       - 优化重绘和回流
       - 使用requestAnimationFrame
       - 减少图层数量
    
    3. **内存管理优化** (30分钟)
       - 修复内存泄漏
       - 优化事件监听器管理
       - 清理未使用的对象引用
       - 优化图片资源加载
    
    ### 3.3 阶段三：测试与验证 (3.5 - 4小时)
    **负责人**: 质量保证工程师
    
    #### 子任务：
    1. **功能回归测试** (15分钟)
       - 验证所有原有功能正常
       - 测试边界条件
       - 验证数据准确性
    
    2. **性能对比测试** (15分钟)
       - 与优化前基准对比
       - 验证性能提升指标
       - 压力测试（模拟高负载）
    
    3. **安全与稳定性验证** (10分钟)
       - 验证核心导航计算准确性
       - 检查错误处理机制
       - 验证异常情况处理
    
    ## 4. 技术风险与依赖关系
    
    ### 4.1 技术风险
    | 风险项 | 概率 | 影响 | 缓解措施 |
    |--------|------|------|----------|
    | 优化引入新bug | 中 | 高 | 严格测试，保留原始版本备份 |
    | 性能提升不明显 | 低 | 中 | 多方案并行，优先实施高ROI优化 |
    | 兼容性问题 | 低 | 低 | 使用标准API，避免实验性特性 |
    | 时间不足 | 中 | 高 | 聚焦核心瓶颈，采用增量优化 |
    
    ### 4.2 依赖关系
    - **后端API稳定性**: 确保后端服务在优化期间稳定
    - **测试环境**: 需要与生产环境相似的数据集
    - **监控工具**: Chrome DevTools, Lighthouse, 性能监控脚本
    
    ## 5. 资源分配
    
    ### 5.1 人员配置
    - **项目经理 (PM)**: 1人 - 整体协调，进度跟踪
    - **架构师**: 1人 - 技术指导，方案审核
    - **前端开发者**: 2-3人 - 具体实施
    - **质量保证**: 1人 - 测试验证
    
    ### 5.2 工具准备
    - 代码编辑器/IDE
    - Chrome DevTools
    - Lighthouse
    - 性能监控脚本
    - Git版本控制
    - 本地测试服务器
    
    ## 6. 执行指导
    
    ### 6.1 开发指导原则
    1. **安全第一**: 任何改动不得影响航行安全相关计算
    2. **渐进增强**: 优先优化最影响用户体验的部分
    3. **可测量**: 所有优化必须有可量化的改进
    4. **可回滚**: 每个优化点应有独立提交，便于回滚
    
    ### 6.2 代码规范
    - 遵循现有代码风格
    - 添加有意义的注释
    - 更新相关文档
    - 确保向后兼容
    
    ### 6.3 测试要求
    - 单元测试覆盖关键计算函数
    - 集成测试验证整体功能
    - 性能测试对比优化效果
    - 跨浏览器测试（Chrome, Firefox, Edge）
    
    ## 7. 交付物清单
    
    ### 7.1 代码交付
    - 优化后的 `navigation-v2.html`
    - 相关的CSS/JS文件更新
    - 性能监控脚本（如开发）
    
    ### 7.2 文档交付
    - 优化报告（包含前后性能对比）
    - 修改清单（列出所有改动点）
    - 测试报告（功能与性能验证结果）
    - 后续优化建议
    
    ### 7.3 运行验证
    ```bash
    # 优化完成后运行测试
    cd /Users/panglaohu/Downloads/DoubleBoatClawSystem
    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short
    ```
    
    ## 8. 时间线
    
    | 时间段 | 阶段 | 关键产出 |
    |--------|------|----------|
    | 0-30min | 分析与评估 | 性能���准报告，瓶颈分析 |
    | 30min-2h | 核心优化实施 | 主要性能问题修复 |
    | 2h-3.5h | 细节优化与调整 | 用户体验提升 |
    | 3.5h-4h | 测试与验证 | 测试报告，性能对比 |
    | 4h | 交付与汇报 | 优化成果报告 |
    
    ## 9. 沟通机制
    
    ### 9.1 进度同步
    - **每30分钟**: 简短站会，同步进展
    - **关键节点**: 即时通报重大发现或问题
    - **最终汇报**: 4小时后向船长汇报
    
    ### 9.2 问题上报
    1. 技术问题 → 架构师 → PM
    2. 资源问题 → PM
    3. 范围/时间问题 → PM → 船长
    
    ---
    
    **任务确认**: ✅ 已接收并开始执行  
    **开始时间**: NOW  
    **预计完成**: NOW + 4小时  
    
    **PM备注**: 所有团队成员请立即开始执行分配的任务。保持沟通畅通，遇到问题立即上报。优先保证核心导航功能的稳定性和准确性。
    
    ────────────────────────────────────────────────────────────
    ✅ deepseek-chat 完成
    
    
    
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
  🔗 使用模型池默认: deepseek-chat (deepseek)
  
  🔗 API: api.deepseek.com | 模型: deepseek-chat
  ────────────────────────────────────────────────────────────
  
  # navigation-v2.html 页面优化技术调研报告
  
  ## 1. 调研概述
  
  **调研目标**: 分析 `navigation-v2.html` 页面的现有代码结构、功能模块和性能瓶颈，为4小时优化工作提供技术指导。
  
  **调研时间**: 30分钟
  **调研范围**: 前端相关文件，重点关注 `navigation-v2.html` 及其依赖的JS/CSS文件
  
  ## 2. 文件结构分析
  
  ### 2.1 核心文件清单
  
  ```
  src/frontend/
  ├── navigation-v2.html                    # 主页面文件
  ├── css/
  │   ├── navigation-v2.css                # 页面样式
  │   └── common.css                       # 通用样式
  ├── js/
  │   ├── navigation-v2.js                 # 主逻辑文件
  │   ├── map-renderer.js                  # 地图渲染模块
  │   ├── data-processor.js                # 数据处理模块
  │   ├── navigation-calculator.js         # 导航计算模块
  │   ├── ui-controller.js                 # UI控制模块
  │   └── utils.js                         # 工具函数
  └── lib/
      ├── leaflet/                         # 地图库
      ├── chart.js/                        # 图表库
      └── socket.io/                       # WebSocket库
  ```
  
  ### 2.2 后端API接口
  
  ```
  src/backend/
  ├── api/
  │   ├── navigation.py                    # 导航相关API
  │   ├── vessel_data.py                   # 船舶数据API
  │   └── weather.py                       # 天气数据API
  └── websocket/
      └── realtime_handler.py              # 实时数据推送
  ```
  
  ## 3. 代码分析
  
  ### 3.1 navigation-v2.html 结构分析
  
  ```html
  <!-- 关键代码片段 -->
  <!DOCTYPE html>
  <html lang="zh-CN">
  <head>
      <meta charset="UTF-8">
      <title>导航系统 v2.0</title>
      <!-- 大量CSS和JS引入 -->
      <link rel="stylesheet" href="css/navigation-v2.css">
      <link rel="stylesheet" href="css/common.css">
      <link rel="stylesheet" href="lib/leaflet/leaflet.css">
      
      <script src="lib/socket.io/socket.io.js"></script>
      <script src="lib/leaflet/leaflet.js"></script>
      <script src="lib/chart.js/chart.min.js"></script>
      
      <!-- 自定义JS按顺序加载 -->
      <script src="js/utils.js"></script>
      <script src="js/data-processor.js"></script>
      <script src="js/navigation-calculator.js"></script>
      <script src="js/map-renderer.js"></script>
      <script src="js/ui-controller.js"></script>
      <script src="js/navigation-v2.js"></script>
  </head>
  <body>
      <!-- 复杂DOM结构，包含多个功能区域 -->
      <div id="app-container">
          <!-- 地图区域 -->
          <div id="map-container" class="map-area">
              <div id="map"></div>
              <!-- 多个覆盖层和控件 -->
          </div>
          
          <!-- 侧边栏 -->
          <div id="sidebar" class="sidebar">
              <!-- 多个功能面板 -->
              <div class="panel" id="vessel-info-panel">...</div>
              <div class="panel" id="navigation-panel">...</div>
              <div class="panel" id="weather-panel">...</div>
              <div class="panel" id="alerts-panel">...</div>
          </div>
          
          <!-- 底部状态栏 -->
          <div id="status-bar" class="status-bar">...</div>
      </div>
  </body>
  </html>
  ```
  
  ### 3.2 JavaScript模块分析
  
  #### 3.2.1 navigation-v2.js (主文件)
  ```javascript
  // 发现的问题：
  // 1. 全局变量过多
  var mapInstance;
  var vesselData = {};
  var weatherData = {};
  var navigationData = {};
  var alertData = [];
  
  // 2. 频繁的DOM查询
  function updateUI() {
      var vesselName = document.getElementById('vessel-name');
      var speedDisplay = document.getElementById('speed-display');
      var courseDisplay = document.getElementById('course-display');
      // ... 更多DOM查询
  }
  
  // 3. 同步API调用阻塞UI
  function fetchAllData() {
      // 同步调用多个API
      fetchVesselData();
      fetchWeatherData();
      fetchNavigationData();
      fetchAlertsData();
  }
  
  // 4. 频繁的事件监听器绑定
  document.addEventListener('click', handleClick);
  document.addEventListener('mousemove', handleMouseMove);
  window.addEventListener('resize', handleResize);
  // ... 更多事件监听
  ```
  
  #### 3.2.2 map-renderer.js (地图渲染)
  ```javascript
  // 发现的问题：
  // 1. 频繁的地图图层更新
  function updateMapLayers() {
      mapInstance.eachLayer(function(layer) {
          // 遍历所有图层
          if (layer instanceof L.Marker) {
              updateMarkerPosition(layer);
          }
      });
  }
  
  // 2. 大量的标记点渲染
  function renderVesselMarkers(vessels) {
      vessels.forEach(function(vessel) {
          var marker = L.marker([vessel.lat, vessel.lon]);
          mapInstance.addLayer(marker);
          // 为每个标记添加事件监听
          marker.on('click', function() {
              showVesselDetails(vessel);
          });
      });
  }
  ```
  
  #### 3.2.3 data-processor.js (数据处理)
  ```javascript
  // 发现的问题：
  // 1. 低效的数据处理算法
  function processVesselData(data) {
      // 嵌套循环导致O(n²)复杂度
      for (var i = 0; i < data.length; i++) {
          for (var j = 0; j < data.length; j++) {
              if (i !== j) {
                  calculateDistance(data[i], data[j]);
              }
          }
      }
  }
  
  // 2. 重复计算
  function calculateCourse(lat1, lon1, lat2, lon2) {
      // 每次调用都重新计算三角函数
      var y = Math.sin(lon2 - lon1) * Math.cos(lat2);
      var x = Math.cos(lat1) * Math.sin(lat2) - 
              Math.sin(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1);
      return Math.atan2(y, x) * 180 / Math.PI;
  }
  ```
  
  ## 4. 性能瓶颈识别
  
  ### 4.1 加载性能问题
  1. **资源加载顺序**: JS文件按顺序加载，阻塞渲染
  2. **未使用的库**: 可能加载了未使用的库文件
  3. **缺少懒加载**: 所有资源一次性加载
  
  ### 4.2 运行时性能问题
  1. **DOM操作频繁**: 大量querySelector/getElementById调用
  2. **事件监听器过多**: 未使用事件委托
  3. **内存泄漏**: 事件监听器未正确清理
  4. **重绘/回流频繁**: 样式修改导致布局重新计算
  
  ### 4.3 计算性能问题
  1. **算法复杂度高**: 嵌套循环处理数据
  2. **重复计算**: 相同参数多次计算相同结果
  3. **同步操作**: 阻塞UI的同步API调用
  
  ### 4.4 网络性能问题
  1. **API调用频繁**: 多个独立API调用
  2. **缺少缓存**: 相同数据重复请求
  3. **WebSocket重连**: 连接不稳定导致频繁重连
  
  ## 5. 优化方案可行性分析
  
  ### 5.1 高优先级优化（立即实施）
  
  | 优化项 | 可行性 | 预计时间 | 影响范围 |
  |--------|--------|----------|----------|
  | JS文件异步/延迟加载 | 高 | 15分钟 | navigation-v2.html |
  | DOM查询缓存 | 高 | 30分钟 | 所有JS文件 |
  | 事件委托优化 | 高 | 45分钟 | navigation-v2.js, ui-controller.js |
  | 计算函数缓存 | 高 | 30分钟 | navigation-calculator.js |
  | API请求合并 | 中 | 60分钟 | data-processor.js, 后端API |
  
  ### 5.2 中优先级优化（时间允许时实施）
  
  | 优化项 | 可行性 | 预计时间 | 影响范围 |
  |--------|--------|----------|----------|
  | 虚拟滚动列表 | 中 | 90分钟 | ui-controller.js, HTML结构 |
  | WebSocket连接优化 | 中 | 60分钟 | 所有使用WebSocket的模块 |
  | 地图标记聚合 | 中 | 75分钟 | map-renderer.js |
  | CSS动画优化 | 高 | 30分钟 | navigation-v2.css |
  
  ### 5.3 低优先级优化（后续考虑）
  
  | 优化项 | 可行性 | 预计时间 | 影响范围 |
  |--------|--------|----------|----------|
  | Web Workers计算 | 低 | 120分钟 | navigation-calculator.js |
  | Service Worker缓存 | 低 | 90分钟 | 整体架构 |
  | 代码分割 | 中 | 120分钟 | 所有JS文件 |
  
  ## 6. 需要修改的文件清单
  
  ### 6.1 必须修改的文件
  1. **navigation-v2.html** - 资源加载优化
  2. **navigation-v2.js** - 主逻辑优化
  3. **map-renderer.js** - 地图渲染优化
  4. **data-processor.js** - 数据处理优化
  5. **navigation-calculator.js** - 计算优化
  6. **ui-controller.js** - UI交互优化
  
  ### 6.2 可能修改的文件
  1. **navigation-v2.css** - 样式优化
  2. **utils.js** - 工具函数优化
  3. 后端API文件 - 支持请求合并
  
  ### 6.3 影响范围评估
  - **前端**: 所有用户交互和显示功能
  - **后端**: API调用方式和频率可能变化
  - **数据流**: 数据处���和传输方式优化
  - **用户体验**: 响应速度和流畅度提升
  
  ## 7. 技术风险与缓解措施
  
  ### 7.1 高风险项
  1. **功能回归风险**
     - 缓解：严格测试，保留原始代码备份
     - 措施：逐功能验证，对比测试
  
  2. **计算准确性风险**
     - 缓解：核心导航计算单独验证
     - 措施：单元测试覆盖，人工复核
  
  ### 7.2 中风险项
  1. **浏览器兼容性**
     - 缓解：使用标准API，避免实验性特性
     - 措施：多浏览器测试
  
  2. **性能提升不明显**
     - 缓解：优先实施高ROI优化
     - 措施：性能监控，实时调整策略
  
  ## 8. 实施建议
  
  ### 8.1 第一阶段（0-2小时）：核心优化
  1. **资源加载优化** (15分钟)
     - 将JS改为async/defer加载
     - 移除未使用的库引用
  
  2. **DOM操作优化** (45分钟)
     - 缓存DOM查询结果
     - 使用事件委托
     - 批量DOM更新
  
  3. **计算优化** (60分钟)
     - 实现函数缓存（memoization）
     - 优化算法复杂度
     - 减少重复计算
  
  ### 8.2 第二阶段（2-3.5小时）：细节优化
  1. **API调用优化** (45分钟)
     - 合并相关API请求
     - 实现请求缓存
     - 优化WebSocket重连逻辑
  
  2. **渲染优化** (45分钟)
     - 优化CSS选择器
     - 减少重绘/回流
     - 使用transform代替top/left
  
  ### 8.3 第三阶段（3.5-4小时）：测试验证
  1. **功能测试** (15分钟)
  2. **性能对比** (15分钟)
  3. **安全验证** (10分钟)
  
  ## 9. 预期成果
  
  ### 9.1 量化指标
  - 页面加载时间减少：≥40%
  - 交互响应延迟：≤50ms
  - 内存使用减少：≥30%
  - CPU使用率降低：≥25%
  
  ### 9.2 用户体验改进
  - 更流畅的地图交互
  - 更快的实时数据更新
  - 更稳定的WebSocket连接
  - 更准确的计算结果显示
  
  ## 10. 后续建议
  
  ### 10.1 短期建议（本次优化后）
  1. 添加性能监控脚本
  2. 建立性能基准测试
  3. 编写优化文档
  
  ### 10.2 长期建议
  1. 考虑前端框架迁移（如Vue/React）
  2. 实现代码分割和懒加载
  3. 引入状态管理
  4. 优化构建流程
  
  ---
  
  **调研结论**: `navigation-v2.html` 页面存在明显的性能优化空间，主要集中在资源加载、DOM操作、计算算法和网络请求方面。建议按照上述方案分阶段实施，优先解决核心瓶颈问题。
  
  **风��评估**: 中等，需要严格控制改动范围，确保核心导航功能不受影响。
  
  **可行性**: 高，4小时时间窗口足够实施关键优化。
  
  ────────────────────────────────────────────────────────────
  ✅ deepseek-chat 完成
  
  
  
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
🔗 使用模型池默认: deepseek-chat (deepseek)

🔗 API: api.deepseek.com | 模型: deepseek-chat
────────────────────────────────────────────────────────────

# navigation-v2.html 页面优化技术方案

## 1. 总体架构设计

### 1.1 优化目标
- **性能提升**: 页面加载时间减少 ≥40%，交互响应延迟 ≤50ms
- **稳定性保障**: 核心导航计算100%准确，无功能回归
- **内存优化**: 内存使用减少 ≥30%，无内存泄漏
- **代码质量**: 模块化重构，提高可维护性

### 1.2 架构原则
1. **渐进式优化**: 优先解决核心瓶颈，逐步优化细节
2. **可测量性**: 每个优化点必须有量化指标
3. **向后兼容**: 保持现有API接口不变
4. **安全第一**: 核心导航计算独立验证

## 2. 模块交互关系图

```mermaid
graph TB
    subgraph "前端优化模块"
        A[navigation-v2.html] --> B[资源加载优化]
        A --> C[DOM结构优化]
        
        subgraph "JavaScript优化"
            D[navigation-v2.js] --> E[事件管理优化]
            D --> F[状态管理优化]
            G[map-renderer.js] --> H[地图渲染优化]
            I[data-processor.js] --> J[数据处理优化]
            K[navigation-calculator.js] --> L[计算缓存优化]
            M[ui-controller.js] --> N[UI交互优化]
        end
        
        subgraph "样式优化"
            O[navigation-v2.css] --> P[CSS性能优化]
            O --> Q[动画优化]
        end
    end
    
    subgraph "后端适配"
        R[API路由优化] --> S[请求合并接口]
        T[WebSocket优化] --> U[连接管理优化]
    end
    
    B --> V[性能监控]
    C --> V
    E --> V
    H --> V
    J --> V
    L --> V
    N --> V
    P --> V
    Q --> V
    S --> V
    U --> V
```

## 3. 详细技术方案

### 3.1 资源加载优化

#### 3.1.1 HTML文件修改 (`navigation-v2.html`)
```html
<!-- 修改前 -->
<script src="lib/socket.io/socket.io.js"></script>
<script src="lib/leaflet/leaflet.js"></script>
<script src="lib/chart.js/chart.min.js"></script>
<script src="js/utils.js"></script>
<script src="js/data-processor.js"></script>
<script src="js/navigation-calculator.js"></script>
<script src="js/map-renderer.js"></script>
<script src="js/ui-controller.js"></script>
<script src="js/navigation-v2.js"></script>

<!-- 修改后 -->
<!-- 关键库使用async加载 -->
<script src="lib/socket.io/socket.io.js" async></script>
<script src="lib/leaflet/leaflet.js" async></script>
<script src="lib/chart.js/chart.min.js" defer></script>

<!-- 自定义模块使用defer，按依赖顺序 -->
<script src="js/utils.js" defer></script>
<script src="js/data-processor.js" defer></script>
<script src="js/navigation-calculator.js" defer></script>
<script src="js/map-renderer.js" defer></script>
<script src="js/ui-controller.js" defer></script>
<script src="js/navigation-v2.js" defer></script>

<!-- 添加预加载 -->
<link rel="preload" href="css/navigation-v2.css" as="style">
<link rel="preload" href="lib/leaflet/leaflet.css" as="style">
```

#### 3.1.2 新增模块加载器 (`js/module-loader.js`)
```javascript
// 模块加载状态管理
class ModuleLoader {
    constructor() {
        this.modules = new Map();
        this.dependencies = {
            'utils': [],
            'data-processor': ['utils'],
            'navigation-calculator': ['utils'],
            'map-renderer': ['utils'],
            'ui-controller': ['utils', 'data-processor'],
            'navigation-v2': ['utils', 'data-processor', 'navigation-calculator', 'map-renderer', 'ui-controller']
        };
    }

    async loadModule(moduleName) {
        if (this.modules.has(moduleName)) {
            return this.modules.get(moduleName);
        }

        // 检查依赖
        const deps = this.dependencies[moduleName] || [];
        for (const dep of deps) {
            await this.loadModule(dep);
        }

        // 动态加载模块
        const module = await import(`./${moduleName}.js`);
        this.modules.set(moduleName, module);
        return module;
    }
}

// 全局实例
window.moduleLoader = new ModuleLoader();
```

### 3.2 JavaScript优化方案

#### 3.2.1 全局状态管理 (`js/state-manager.js`)
```javascript
// 新增状态管理模块
class StateManager {
    constructor() {
        this.state = {
            vesselData: null,
            weatherData: null,
            navigationData: null,
            alertData: [],
            uiState: {},
            cache: new Map()
        };
        
        this.subscribers = new Map();
        this.batchUpdates = false;
        this.updateQueue = [];
    }

    // 状态更新（支持批量）
    setState(key, value) {
        if (this.batchUpdates) {
            this.updateQueue.push({ key, value });
            return;
        }
        
        const oldValue = this.state[key];
        this.state[key] = value;
        this.notify(key, value, oldValue);
    }

    // 批量更新
    batchUpdate(updates) {
        this.batchUpdates = true;
        Object.entries(updates).forEach(([key, value]) => {
            this.setState(key, value);
        });
        this.batchUpdates = false;
        
        // 执行队列中的更新
        this.updateQueue.forEach(update => {
            this.setState(update.key, update.value);
        });
        this.updateQueue = [];
    }

    // 订阅状态变化
    subscribe(key, callback) {
        if (!this.subscribers.has(key)) {
            this.subscribers.set(key, new Set());
        }
        this.subscribers.get(key).add(callback);
        
        // 返回取消订阅函数
        return () => {
            this.subscribers.get(key)?.delete(callback);
        };
    }

    // 通知订阅者
    notify(key, newValue, oldValue) {
        const callbacks = this.subscribers.get(key);
        if (callbacks) {
            callbacks.forEach(callback => {
                callback(newValue, oldValue);
            });
        }
    }

    // 缓存管理
    cacheResult(key, fn, ttl = 60000) {
        const cacheKey = JSON.stringify(key);
        const cached = this.state.cache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < ttl) {
            return cached.value;
        }
        
        const result = fn();
        this.state.cache.set(cacheKey, {
            value: result,
            timestamp: Date.now()
        });
        
        return result;
    }
}

// 全局状态实例
window.appState = new StateManager();
```

#### 3.2.2 DOM查询优化 (`js/dom-manager.js`)
```javascript
// DOM查询缓存管理器
class DOMManager {
    constructor() {
        this.cache = new Map();
        this.observer = null;
        this.initObserver();
    }

    // 初始化MutationObserver监听DOM变化
    initObserver() {
        this.observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    // DOM结构变化时清理相关缓存
                    this.clearCacheForRemovedNodes(mutation.removedNodes);
                }
            });
        });
        
        this.observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // 获取DOM元素（带缓存）
    getElement(selector, context = document) {
        const cacheKey = `${selector}-${context === document ? 'doc' : context.id || 'ctx'}`;
        
        if (this.cache.has(cacheKey)) {
            const element = this.cache.get(cacheKey);
            if (document.body.contains(element)) {
                return element;
            }
            this.cache.delete(cacheKey);
        }
        
        const element = context.querySelector(selector);
        if (element) {
            this.cache.set(cacheKey, element);
        }
        
        return element;
    }

    // 批量获取DOM元素
    getElements(selector, context = document) {
        const cacheKey = `all-${selector}-${context === document ? 'doc' : context.id || 'ctx'}`;
        
        if (this.cache.has(cacheKey)) {
            const elements = this.cache.get(cacheKey);
            // 验证所有元素仍然存在
            if (elements.every(el => document.body.contains(el))) {
                return elements;
            }
            this.cache.delete(cacheKey);
        }
        
        const elements = Array.from(context.querySelectorAll(selector));
        this.cache.set(cacheKey, elements);
        return elements;
    }

    // 清理缓存
    clearCacheForRemovedNodes(nodes) {
        nodes.forEach(node => {
            if (node.nodeType === Node.ELEMENT_NODE) {
                this.cache.forEach((value, key) => {
                    if (value === node || 
                        (Array.isArray(value) && value.includes(node))) {
                        this.cache.delete(key);
                    }
                });
            }
        });
    }

    // 批量更新DOM
    batchUpdate(callback) {
        // 使用文档片段
        const fragment = document.createDocumentFragment();
        callback(fragment);
        
        // 一次性插入
        const container = this.getElement('#app-container');
        if (container) {
            container.appendChild(fragment);
        }
    }
}

// 全局DOM管理器
window.domManager = new DOMManager();
```

#### 3.2.3 事件管理优化 (`js/event-manager.js`)
```javascript
// 事件委托管理器
class EventManager {
    constructor() {
        this.handlers = new Map();
        this.delegatedHandlers = new Map();
    }

    // 事件委托注册
    delegate(eventType, selector, handler, context = document) {
        const key = `${eventType}-${selector}`;
        
        if (!this.delegatedHandlers.has(key)) {
            const delegatedHandler = (event) => {
                const target = event.target;
                const matchingElement = target.closest(selector);
                
                if (matchingElement && context.contains(matchingElement)) {
                    handler(event, matchingElement);
                }
            };
            
            context.addEventListener(eventType, delegatedHandler);
            this.delegatedHandlers.set(key, {
                handler: delegatedHandler,
                context: context
            });
        }
    }

    // 移除事件委托
    undelegate(eventType, selector, context = document) {
        const key = `${eventType}-${selector}`;
        const entry = this.delegatedHandlers.get(key);
        
        if (entry && entry.context === context) {
            context.removeEventListener(eventType, entry.handler);
            this.delegatedHandlers.delete(key);
        }
    }

    // 智能节流
    throttle(fn, delay = 100) {
        let lastCall = 0;
        let timeoutId = null;
        
        return function(...args) {
            const now = Date.now();
            const remaining = delay - (now - lastCall);
            
            if (remaining <= 0) {
                lastCall = now;
                fn.apply(this, args);
            } else if (!timeoutId) {
                timeoutId = setTimeout(() => {
                    lastCall = Date.now();
                    timeoutId = null;
                    fn.apply(this, args);
                }, remaining);
            }
        };
    }

    // 智能防抖
    debounce(fn, delay = 300, immediate = false) {
        let timeoutId = null;
        
        return function(...args) {
            const callNow = immediate && !timeoutId;
            
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                timeoutId = null;
                if (!immediate) {
                    fn.apply(this, args);
                }
            }, delay);
            
            if (callNow) {
                fn.apply(this, args);
            }
        };
    }
}

// 全局事件管理器
window.eventManager = new EventManager();
```

### 3.3 计算性能优化

#### 3.3.1 导航计算优化 (`js/navigation-calculator.js`)
```javascript
// 修改前
function calculateCourse(lat1, lon1, lat2, lon2) {
    var y = Math.sin(lon2 - lon1) * Math.cos(lat2);
    var x = Math.cos(lat1) * Math.sin(lat2) - 
            Math.sin(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1);
    return Math.atan2(y, x) * 180 / Math.PI;
}

// 修改后 - 添加缓存和优化
class NavigationCalculator {
    constructor() {
        this.courseCache = new Map();
        this.distanceCache = new Map();
        this.PRECISION = 100000; // 经纬度精度到小数点后5位
    }

    // 计算航向（带缓存）
    calculateCourse(lat1, lon1, lat2, lon2) {
        const key = this.getCacheKey(lat1, lon1, lat2, lon2);
        
        if (this.courseCache.has(key)) {
            return this.courseCache.get(key);
        }
        
        // 转换为弧度
        const lat1Rad = lat1 * Math.PI / 180;
        const lon1Rad = lon1 * Math.PI / 180;
        const lat2Rad = lat2 * Math.PI / 180;
        const lon2Rad = lon2 * Math.PI / 180;
        
        // 预计算三角函数值
        const cosLat1 = Math.cos(lat1Rad);
        const sinLat1 = Math.sin(lat1Rad);
        const cosLat2 = Math.cos(lat2Rad);
        const sinLat2 = Math.sin(lat2Rad);
        const dLon = lon2Rad - lon1Rad;
        
        const y = Math.sin(dLon) * cosLat2;
        const x = cosLat1 * sinLat2 - sinLat1 * cosLat2 * Math.cos(dLon);
        
        const course = Math.atan2(y, x) * 180 / Math.PI;
        const normalizedCourse = (course + 360) % 360;
        
        this.courseCache.set(key, normalizedCourse);
        return normalizedCourse;
    }

    // 计算距离（使用Haversine公式优化）
    calculateDistance(lat1, lon1, lat2, lon2) {
        const key = this.getCacheKey(lat1, lon1, lat2, lon2);
        
        if (this.distanceCache.has(key)) {
            return this.distanceCache.get(key);
        }
        
        const R = 6371000; // 地球半径（米）
        const φ1 = lat1 * Math.PI / 180;
        const φ2 = lat2 * Math.PI / 180;
        const Δφ = (lat2 - lat1) * Math.PI / 180;
        const Δλ = (lon2 - lon1) * Math.PI / 180;
        
        const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
                  Math.cos(φ1) * Math.cos(φ2) *
                  Math.sin(Δλ/2) * Math.sin(Δλ/2);
        
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        const distance = R * c;
        
        this.distanceCache.set(key, distance);
        return distance;
    }

    // 批量计算
    batchCalculateCourses(points) {
        const results = [];
        const batchSize = 100;
        
        for (let i = 0; i < points.length; i += batchSize) {
            const batch = points.slice(i, i + batchSize);
            
            // 使用Web Worker进行批量计算（如果可用）
            if (window.Worker && this.worker) {
                results.push(...this.calculateWithWorker(batch));
            } else {
                results.push(...this.calculateSync(batch));
            }
        }
        
        return results;
    }

    // 同步计算
    calculateSync(batch) {
        return batch.map(point => 
            this.calculateCourse(point.lat1, point.lon1, point.lat2, point.lon2)
        );
    }

    // 生成缓存键
    getCacheKey(lat1, lon1, lat2, lon2) {
        return `${Math.round(lat1 * this.PRECISION)}_${Math.round(lon1 * this.PRECISION)}_${Math.round(lat2 * this.PRECISION)}_${Math.round(lon2 * this.PRECISION)}`;
    }

    // 清理缓存
    clearCache() {
        this.courseCache.clear();
        this.distanceCache.clear();
    }
}

// 替换全局函数
window.navigationCalculator = new NavigationCalculator();
```

### 3.4 地图渲染优化 (`js/map-renderer.js`)

```javascript
// 修改前
function updateMapLayers() {
    mapInstance.eachLayer(function(layer) {
        if (layer instanceof L.Marker) {
            updateMarkerPosition(layer);
        }
    });
}

// 修改后 - 优化地图渲染
class OptimizedMapRenderer {
    constructor(mapInstance) {
        this.map = mapInstance;
        this.markers = new Map();
        this.cluster = null;
        this.updateQueue = [];
        this.isUpdating = false;
        
        this.initMarkerCluster();
        this.initUpdateScheduler();
    }

    // 初始化标记聚类
    initMarkerCluster() {
        if (L.markerClusterGroup) {
            this.cluster = L.markerClusterGroup({
                chunkedLoading: true,
                chunkInterval: 100,
                chunkDelay: 50,
                maxClusterRadius: 80,
                spiderfyOnMaxZoom: true,
                showCoverageOnHover: false,
                zoomToBoundsOnClick: true
            });
            this.map.addLayer(this.cluster);
        }
    }

    // 初始化更新调度器
    initUpdateScheduler() {
        this.updateScheduler = window.eventManager.throttle(() => {
            this.processUpdateQueue();
        }, 50); // 50ms更新间隔
    }

    // 添加标记（批量）
    addMarkers(vessels) {
        const markers = vessels.map(vessel => {
            const marker = L.marker([vessel.lat, vessel.lon], {
                title: vessel.name,
                icon: this.createOptimizedIcon(vessel.type)
            });
            
            // 使用事件委托
            marker.on('click', (e) => {
                this.handleMarkerClick(vessel);
            });
            
            this.markers.set(vessel.id, marker);
            return marker;
        });
        
        if (this.cluster) {
            this.cluster.addLayers(markers);
        } else {
            markers.forEach(marker => this.map.addLayer(marker));
        }
    }

    // 创建优化图标
    createOptimizedIcon(vesselType) {
        // 使用预定义的图标，避免重复创建
        if (!this.iconCache) {
            this.iconCache = new Map();
        }
        
        if (this.iconCache.has(vesselType)) {
            return this.iconCache.get(vesselType);
        }
        
        const icon = L.divIcon({
            className: `vessel-icon vessel-${vesselType}`,
            html: '<div class="vessel-marker"></div>',
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });
        
        this.iconCache.set(vesselType, icon);
        return icon;
    }

    // 更新标记位置（批量）
    updateMarkerPositions(vesselUpdates) {
        // 添加到更新队列
        this.updateQueue.push(...vesselUpdates);
        
        // 调度更新
        this.updateScheduler();
    }

    // 处理更新队列
    processUpdateQueue() {
        if (this.isUpdating || this.updateQueue.length === 0) {
            return;
        }
        
        this.isUpdating = true;
        
        // 使用requestAnimationFrame确保在重绘前更新
        requestAnimationFrame(() => {
            const batch = this.updateQueue.splice(0, 100); // 每次处理100个
            
            batch.forEach(update => {
                const marker = this.markers.get(update.id);
                if (marker) {
                    marker.setLatLng([update.lat, update.lon]);
                    
                    // 更新标记数据
                    marker._vesselData = update;
                }
            });
            
            this.isUpdating = false;
            
            // 如果队列还有数据，继续处理
            if (this.updateQueue.length > 0) {
                this.updateScheduler();
            }
        });
    }

    // 处理标记点击（事件委托）
    handleMarkerClick(vessel) {
        // 使用全局事件管理器
        window.eventManager.delegate('click', '.vessel-marker', (event, element) => {
            const marker = element.closest('.leaflet-marker-icon');
            if (marker && marker._vesselData) {
                this.showVesselDetails(marker._vesselData);
            }
        }, this.map.getContainer());
    }

    // 清理资源
    cleanup() {
        if (this.cluster) {
            this.cluster.clearLayers();
        }
        this.markers.clear();
        this.updateQueue = [];
    }
}

// 替换原有地图渲染逻辑
window.mapRenderer = null;

function initMapRenderer(mapInstance) {
    window.mapRenderer = new OptimizedMapRenderer(mapInstance);
}
```

### 3.5 API请求优化

#### 3.5.1 前端请求合并 (`js/api-manager.js`)
```javascript
// API请求管理器
class APIManager {
    constructor() {
        this.baseURL = '/api';
        this.pendingRequests = new Map();
        this.requestQueue = [];
        this.batchInterval = 100; // 100ms批量请求间隔
        this.cache = new Map();
        this.cacheTTL = 30000; // 30秒缓存
        
        this.initBatchProcessor();
    }

    // 初始化批量处理器
    initBatchProcessor() {
        setInterval(() => {
            this.processBatchRequests();
        }, this.batchInterval);
    }

    // 获取数据（支持单个和批量）
    async get(endpoint, params = {}, useCache = true) {
        const cacheKey = this.getCacheKey(endpoint, params);
        
        // 检查缓存
        if (useCache && this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheTTL) {
                return cached.data;
            }
            this.cache.delete(cacheKey);
        }
        
        // 添加到批量请求队列
        return new Promise((resolve, reject) => {
            const requestId = Date.now() + Math.random();
            
            this.requestQueue.push({
                id: requestId,
                endpoint,
                params,
                resolve,
                reject,
                timestamp: Date.now()
            });
            
            // 设置超时
            setTimeout(() => {
                const index = this.requestQueue.findIndex(req => req.id === requestId);
                if (index !== -1) {
                    this.requestQueue.splice(index, 1);
                    reject(new Error('Request timeout'));
                }
            }, 5000);
        });
    }

    // 处理批量请求
    async processBatchRequests() {
        if (this.requestQueue.length === 0) return;
        
        const batch = this.requestQueue.splice(0, 10); // 每次处理10个请求
        const batchRequests = batch.map(req => ({
            endpoint: req.endpoint,
            params: req.params,
            id: req.id
        }));
        
        try {
            const response = await fetch(`${this.baseURL}/batch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ requests: batchRequests })
            });
            
            if (!response.ok) {
                throw new Error(`Batch request failed: ${response.status}`);
            }
            
            const results = await response.json();
            
            // 分发结果
            batch.forEach(req => {
                const result = results[req.id];
                if (result) {
                    // 缓存结果
                    const cacheKey = this.getCacheKey(req.endpoint, req.params);
                    this.cache.set(cacheKey, {
                        data: result,
                        timestamp: Date.now()
                    });
                    
                    req.resolve(result);
                } else {
                    req.reject(new Error('No result in batch response'));
                }
            });
        } catch (error) {
            // 批量请求失败，回退到单个请求
            await this.fallbackToIndividualRequests(batch);
        }
    }

    // 回退到单个请求
    async fallbackToIndividualRequests(batch) {
        for (const req of batch) {
            try {
                const queryString = new URLSearchParams(req.params).toString();
                const url = `${this.baseURL}${req.endpoint}${queryString ? '?' + queryString : ''}`;
                
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`Request failed: ${response.status}`);
                }
                
                const data = await response.json();
                
                // 缓存结果
                const cacheKey = this.getCacheKey(req.endpoint, req.params);
                this.cache.set(cacheKey, {
                    data: data,
                    timestamp: Date.now()
                });
                
                req.resolve(data);
            } catch (error) {
                req.reject(error);
            }
        }
    }

    // WebSocket连接管理
    initWebSocket() {
        this.ws = new WebSocket(`ws://${window.location.host}/ws/navigation`);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleRealtimeData(data);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.scheduleReconnect();
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    // 处理重连
    scheduleReconnect() {
        this.reconnectAttempts = (this.reconnectAttempts || 0) + 1;
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
        
        setTimeout(() => {
            if (this.ws.readyState === WebSocket.CLOSED) {
                this.initWebSocket();
            }
        }, delay);
    }

    // 生成缓存键
    getCacheKey(endpoint, params) {
        return `${endpoint}:${JSON.stringify(params)}`;
    }

    // 清理缓存
    clearCache() {
        this.cache.clear();
    }
}

// 全局API管理器
window.apiManager = new APIManager();
```

#### 3.5.2 后端批量API接口 (`src/backend/api/batch.py`)
```python
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import asyncio
import aiohttp
from datetime import datetime

router = APIRouter()

class BatchProcessor:
    def __init__(self):
        self.max_concurrent = 10
        self.timeout = 5.0
    
    async def process_batch(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """处理批量请求"""
        results = {}
        
        # 分组处理（按端点分组）
        endpoint_groups = {}
        for req in requests:
            endpoint = req.get('endpoint', '')
            if endpoint not in endpoint_groups:
                endpoint_groups[endpoint] = []
            endpoint_groups[endpoint].append(req)
        
        # 并行处理每个端点组
        tasks = []
        for endpoint, req_list in endpoint_groups.items():
            if len(req_list) == 1:
                # 单个请求直接处理
                task = self.process_single_request(req_list[0])
            else:
                # 多个请求合并处理
                task = self.process_grouped_requests(endpoint, req_list)
            tasks.append(task)
        
        # 等待所有任务完成
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果
        for result in batch_results:
            if isinstance(result, dict):
                results.update(result)
        
        return results
    
    async def process_single_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个请求"""
        request_id = request.get('id')
        endpoint = request.get('endpoint', '')
        params = request.get('params', {})
        
        try:
            # 这里调用实际的API处理逻辑
            result = await self.call_internal_api(endpoint, params)
            return {request_id: result}
        except Exception as e:
            return {request_id: {'error': str(e)}}
    
    async def process_grouped_requests(self, endpoint: str, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """处理分组请求（合并相似请求）"""
        results = {}
        
        if endpoint == '/api/vessels':
            # 合并船舶数据请求
            vessel_ids = set()
            for req in requests:
                if 'id' in req.get('params', {}):
                    vessel_ids.add(req['params']['id'])
            
            # 批量获取船舶数据
            vessels_data = await self.get_vessels_batch(list(vessel_ids))
            
            # 分配结果
            for req in requests:
                vessel_id = req['params'].get('id')
                if vessel_id in vessels_data:
                    results[req['id']] = vessels_data[vessel_id]
                else:
                    results[req['id']] = {'error': 'Vessel not found'}
        
        return results
    
    async def call_internal_api(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用内部API"""
        # 这里实现实际的API调用逻辑
        # 可以根据端点路由到不同的处理函数
        
        if endpoint == '/api/vessels':
            from .vessel_data import get_vessel_data
            return await get_vessel_data(params.get('id'))
        elif endpoint == '/api/weather':
            from .weather import get_weather_data
            return await get_weather_data(params.get('lat'), params.get('lon'))
        elif endpoint == '/api/navigation':
            from .navigation import get_navigation_data
            return await get_navigation_data(params)
        else:
            raise HTTPException(status_code=404, detail=f"Endpoint {endpoint} not found")
    
    async def get_vessels_batch(self, vessel_ids: List[str]) -> Dict[str, Any]:
        """批量获取船舶数据"""
        # 这里实现批量数据库查询
        # 示例：返回模拟数据
        return {
            vid: {
                'id': vid,
                'name': f'Vessel {vid}',
                'lat': 30.0,
                'lon': 120.0,
                'speed': 10.0,
                'course': 45.0
            }
            for vid in vessel_ids
        }

batch_processor = BatchProcessor()

@router.post("/batch")
async def handle_batch_request(request: Dict[str, Any]):
    """处理批量API请求"""
    try:
        requests = request.get('requests', [])
        
        if not requests:
            return {'error': 'No requests provided'}
        
        if len(requests) > 50:
            return {'error': 'Too many requests in batch (max 50)'}
        
        results = await batch_processor.process_batch(requests)
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3.6 CSS性能优化 (`css/navigation-v2.css`)

```css
/* 优化前 */
.vessel-marker {
    width: 20px;
    height: 20px;
    background-color: blue;
    border-radius: 50%;
    position: absolute;
    top: 0;
    left: 0;
    transition: all 0.3s ease;
}

/* 优化后 */
.vessel-marker {
    width: 20px;
    height: 20px;
    background-color: blue;
    border-radius: 50%;
    /* 使用transform代替top/left */
    transform: translate(var(--x, 0), var(--y, 0));
    /* 使用will-change提示浏览器优化 */
    will-change: transform;
    /* 使用GPU加速 */
    transform: translateZ(0);
    /* 优化过渡动画 */
    transition: transform 0.1s linear;
}

/* 优化选择器性能 */
/* 避免使用通配符和深层嵌套 */
.map-area .vessel-layer .vessel-marker { /* 不好 */
    /* ... */
}

.vessel-marker { /* 好 */
    /* ... */
}

/* 使用CSS变量避免重复计算 */
:root {
    --primary-color: #0066cc;
    --secondary-color: #6699cc;
    --border-radius: 4px;
}

.panel {
    background-color: var(--primary-color);
    border-radius: var(--border-radius);
}

/* 优化动画性能 */
@keyframes pulse {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.7;
        transform: scale(1.05);
    }
}

.alert-pulse {
    animation: pulse 2s infinite;
    /* 使用transform和opacity，避免影响布局 */
    transform-origin: center;
}

/* 减少重绘区域 */
.static-background {
    /* 背景固定，不随滚动变化 */
    background-attachment: fixed;
}

/* 优化字体加载 */
@font-face {
    font-family: 'NavigationFont';
    src: url('../fonts/navigation.woff2') format('woff2'),
         url('../fonts/navigation.woff') format('woff');
    font-display: swap; /* 使用swap避免阻塞渲染 */
}

body {
    font-family: 'NavigationFont', sans-serif;
}
```

## 4. 接口规范

### 4.1 批量API接口

**路由**: `POST /api/batch`

**请求参数**:
```json
{
  "requests": [
    {
      "id": "request_1",
      "endpoint": "/api/vessels",
      "params": {
        "id": "vessel_001"
      }
    },
    {
      "id": "request_2", 
      "endpoint": "/api/weather",
      "params": {
        "lat": 30.0,
        "lon": 120.0
      }
    }
  ]
}
```

**响应格式**:
```json
{
  "request_1": {
    "id": "vessel_001",
    "name": "Ocean Explorer",
    "lat": 30.123,
    "lon": 120.456,
    "speed": 12.5,
    "course": 45.0
  },
  "request_2": {
    "temperature": 25.0,
    "humidity": 65,
    "wind_speed": 8.0,
    "wind_direction": 90
  }
}
```

### 4.2 WebSocket接口

**连接地址**: `ws://{host}/ws/navigation`

**消息格式**:
```json
{
  "type": "vessel_update",
  "data": {
    "id": "vessel_001",
    "lat": 30.124,
    "lon": 120.457,
    "speed": 12.6,
    "course": 45.5,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## 5. 实施指南

### 5.1 开发人员检查清单

#### 第一阶段：基础优化（0-1小时）
1. [ ] 修改 `navigation-v2.html` 的资源加载方式
2. [ ] 创建并集成 `js/module-loader.js`
3. [ ] 创建并集成 `js/state-manager.js`
4. [ ] 创建并集成 `js/dom-manager.js`
5. [ ] 创建并集成 `js/event-manager.js`

#### 第二阶段：核心优化（1-2.5小时）
1. [ ] 优化 `js/navigation-calculator.js` 的计算逻辑
2. [ ] 优化 `js/map-renderer.js` 的地图渲染
3. [ ] 创建并集成 `js/api-manager.js`
4. [ ] 优化 `css/n

────────────────────────────────────────────────────────────
✅ deepseek-chat 完成
