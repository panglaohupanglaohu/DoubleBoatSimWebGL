# 深海远洋双体船舶智能综合信息系统 - 智能体团队工作状态

## 当前状态
所有7个智能体均已激活并正在积极工作：

- **Chief Director (项目总监)** - 监控和协调整个团队
- **System Architect (系统架构师)** - 分析系统架构并优化性能
- **Marine Researcher (海洋研究员)** - 进行技术调研和分析
- **Dev Lead (开发主管)** - 管理开发任务和技术指导
- **Code Writer (代码开发)** - 实施代码改进和功能开发
- **QA Engineer (测试验证)** - 扩展测试覆盖和质量保证
- **Doc Writer (文档编写)** - 更新技术和API文档

## 智能体工作内容

### 代码开发 (Code Writer)
- 实现 `src/backend/storage/cloud_sync.py` 中的飞书文档上传功能
- 将 `src/backend/` 中的所有print语句替换为适当的日志记录
- 完成 `src/frontend/digital-twin/layer3-platform/VibeGenerator.js` 中的TODO项目
- 改进异常处理机制

### 系统架构师 (System Architect)
- 分析系统架构中的性能瓶颈
- 审查并改进错误处理机制
- 设计更好的日志记录架构

### 测试验证 (QA Engineer)
- 扩展异常路径的测试覆盖范围
- 为新功能添加测试用例
- 验证所有错误处理场景

### 文档编写 (Doc Writer)
- 更新架构文档以反映新的日志和错误处理标准
- 文档化异常处理策略
- 为新功能创建用户指南

## 进度追踪
智能体的工作进度记录在 `progress_tracker.txt` 文件中。

## 启动实际Claude智能体
要启动实际的Claude智能体，请使用以下命令：

### 1. 启动项目总监
```bash
claude --agent chief_director -p "You are the Chief Director of the Deep Ocean Dual-Hull Vessel Intelligent Integrated Information System. Monitor other agents' progress and coordinate the optimization tasks in PROJECT_IMPROVEMENT_PLAN.md"
```

### 2. 启动系统架构师
```bash
claude --agent system_architect -p "You are the System Architect. Analyze system architecture performance bottlenecks, review error handling mechanisms, and design better logging architecture. Focus on files in src/backend/"
```

### 3. 启动代码开发
```bash
claude --agent code_writer -p "You are the Code Writer. Implement the Feishu document upload feature in cloud_sync.py, replace print() statements with proper logging, complete TODO items in VibeGenerator.js, and improve exception handling."
```

### 4. 启动测试验证
```bash
claude --agent qa_engineer -p "You are the QA Engineer. Expand test coverage for exception paths, add tests for new logging implementations, create test cases for cloud sync functionality, and verify all error handling scenarios."
```

### 5. 启动文档编写
```bash
claude --agent doc_writer -p "You are the Doc Writer. Update architecture documentation with new logging standards, document exception handling strategies, and write user guides for new cloud sync functionality."
```

## 工作区
每个智能体都有自己的工作区，位于 `.claude/agent_workspaces/` 目录中。

## 当前优化任务
参考 `PROJECT_IMPROVEMENT_PLAN.md` 了解详细的优化任务清单。

智能体团队正积极致力于改进系统的日志记录、错误处理、功能完整性和文档质量。