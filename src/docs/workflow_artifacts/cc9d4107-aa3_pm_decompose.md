# PM分解 — project_manager

任务: 测试完整流水线v3
步骤: pm_decompose
Agent: build_pm

---

📋 任务: cc9d4107-aa3
🤖 Agent: PM (project_manager)
📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
🔧 执行方式: DeepSeek API (直连)
⏱️ 超时: 300s
────────────────────────────────────────────────────────────
📝 提示词:
  你是 PoseidonX 系统的 PM (project_manager)。
  请执行以下开发任务:
  
  你是项目经理 (PM)。请对以下任务进行分解和规划:
  
  ## 任务
  测试完整流水线v3
  在前端agent-team-config页面的Token Factory区域，增加一个DeepSeek API连通性测试按钮
  
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
  
────────────────────────────────────────────────────────────
⚡ 使用 DeepSeek API 直连 (快速模式)...

🔗 API: api.deepseek.com | 模型: deepseek-chat
────────────────────────────────────────────────────────────

# 任务分解文档：DeepSeek API连通性测试功能开发

## 1. 任务概述
**目标**：在前端agent-team-config页面的Token Factory区域，增加DeepSeek API连通性测试按钮，验证完整流水线v3功能。

**业务价值**：
- 提供用户友好的API连通性验证工具
- 确保Token配置正确性，减少调试时间
- 验证完整流水线v3的端到端功能

## 2. 任务分解

### 2.1 需求分析与设计阶段
**负责人**：PM + 架构师
**预计工时**：0.5天

**子任务**：
1. **需求确认**
   - 确认测试按钮的具体位置和样式要求
   - 确定测试结果的展示方式（成功/失败提示、详细错误信息）
   - 明确测试范围：仅测试连通性，还是包含简单的功能测试

2. **API设计**
   - 设计后端测试接口的请求/响应格式
   - 确定测试参数（API Key、Endpoint、模型等）
   - 设计错误处理机制

3. **UI/UX设计**
   - 按钮位置：Token Factory区域内
   - 按钮样式：与现有UI风格一致
   - 测试状态反馈设计（加载中、成功、失败）

### 2.2 后端开发阶段
**负责人**：后端开发者
**预计工时**：1天

**���任务**：
1. **创建测试接口**
   - 文件位置：`src/backend/api/deepseek_test.py`
   - 接口路径：`POST /api/deepseek/test-connection`
   - 请求参数：
     ```json
     {
       "api_key": "string",
       "endpoint": "string (可选，默认使用配置)",
       "model": "string (可选，默认deepseek-chat)"
     }
     ```

2. **实现测试逻辑**
   - 使用提供的API Key调用DeepSeek API
   - 发送简单的测试请求（如："Hello"）
   - 验证响应状态和格式
   - 实现超时和错误处理

3. **集成到现有系统**
   - 在FastAPI应用中注册新路由
   - 更新API文档（如有）
   - 确保与现有认证/授权机制兼容

### 2.3 前端开发阶段
**负责人**：前端开发者
**预计工时**：1天

**子任务**：
1. **定位目标页面**
   - 文件位置：`src/frontend/agent-team-config.html`
   - 找到Token Factory区域DOM结构

2. **添加测试按钮**
   - 在Token Factory区域添加按钮元素
   - 应用现有CSS样式
   - 添加点击事件处理函数

3. **实现测试功能**
   - 从页面获取API Key输入值
   - 调用后端测试接口
   - 实现加载状态显示
   - 处理响应并显示结果

4. **用户反馈**
   - 成功：显示绿色提示信息
   - 失败：显示红色错误信息（包含具体原因）
   - 网络错误：显示友好提示

### 2.4 测试与验证阶段
**负责人**：测试人员 + 开发者
**预计工时**：0.5天

**子任务**：
1. **单元测试**
   - 后端接口单元测试
   - 前端功能单元测试

2. **集成测试**
   - 测试完整流水线：前端 → 后端 → DeepSeek API → 响应返回
   - 测试各种边界情况：
     - 无效API Key
     - 网络超时
     - DeepSeek服务不可用
     - 空/错误的参数

3. **UI测试**
   - 验证按钮位置和样式
   - 测试响应式布局
   - 验证用户交互流程

### 2.5 部署与文档
**负责人**：PM + 开发者
**预计工时**：0.5天

**子任务**：
1. **代码审查与合并**
2. **更新文档**
   - 更新功能说明文档
   - 添加使用指南
3. **部署验证**
   - 验证生产环境功能
   - 监控错误��志

## 3. 技术风险与依赖关系

### 3.1 技术风险
1. **API变更风险**
   - **风险**：DeepSeek API接口或响应格式变更
   - **缓解**：使用标准的OpenAI兼容接口，添加版本兼容性检查

2. **网络稳定性**
   - **风险**：网络延迟或中断导致测试失败
   - **缓解**：设置合理的超时时间（建议5-10秒），提供重试机制

3. **安全性**
   - **风险**：API Key在前端暴露
   - **缓解**：所有API调用通过后端代理，不在前端直接调用第三方API

### 3.2 依赖关系
1. **前端依赖**
   - 现有agent-team-config页面结构稳定
   - 现有的CSS样式库可用

2. **后端依赖**
   - FastAPI框架正常运行
   - 网络访问权限（能访问DeepSeek API）

3. **外部依赖**
   - DeepSeek API服务可用性
   - 用户拥有有效的DeepSeek API Key

## 4. 实施指导

### 4.1 给架构师的指导
1. **技术选型确认**
   - 确认使用OpenAI SDK还是直接HTTP请求
   - 建议：使用`openai`库（兼容DeepSeek）

2. **错误处理策略**
   - 定义统一的错误响应格式
   - 建议错误分类：网络错误、认证错误、API错误、超时

3. **性能考虑**
   - 测试接口应设置速率限制
   - 考虑缓存测试结果（短期）

### 4.2 给开发者的指导
1. **后端开发要点**
   ```python
   # 伪代码示例
   async def test_deepseek_connection(api_key: str, endpoint: Optional[str] = None):
       try:
           client = OpenAI(api_key=api_key, base_url=endpoint or "https://api.deepseek.com")
           response = client.chat.completions.create(
               model="deepseek-chat",
               messages=[{"role": "user", "content": "Hello"}],
               max_tokens=10,
               timeout=10.0
           )
           return {"status": "success", "message": "Connection successful"}
       except AuthenticationError:
           return {"status": "error", "message": "Invalid API Key"}
       except Timeout:
           return {"status": "error", "message": "Request timeout"}
       except Exception as e:
           return {"status": "error", "message": f"Connection failed: {str(e)}"}
   ```

2. **前端开发要点**
   ```javascript
   // 伪代码示例
   async function testDeepSeekConnection() {
       const apiKey = document.getElementById('api-key-input').value;
       const button = document.getElementById('test-button');
       
       // 显示加载状态
       button.disabled = true;
       button.textContent = 'Testing...';
       
       try {
           const response = await fetch('/api/deepseek/test-connection', {
               method: 'POST',
               headers: {'Content-Type': 'application/json'},
               body: JSON.stringify({api_key: apiKey})
           });
           
           const result = await response.json();
           
           if (result.status === 'success') {
               showSuccessMessage('DeepSeek API connection successful!');
           } else {
               showErrorMessage(`Test failed: ${result.message}`);
           }
       } catch (error) {
           showErrorMessage('Network error. Please try again.');
       } finally {
           // 恢复按钮状态
           button.disabled = false;
           button.textContent = 'Test Connection';
       }
   }
   ```

### 4.3 给测试人员的指导
1. **测试用例设计**
   - 有效API Key测试
   - 无效API Key测试
   - 空API Key测试
   - 网络断开测试
   - 并发测试（多个用户同时点击）

2. **验证标准**
   - 按钮点击后应有视觉反馈
   - 测试结果应在3秒内返回（正常情况）
   - 错误信息应明确指导用户解决问题

## 5. 验收标准

### 5.1 功能验收
- [ ] 按钮正确显示在Token Factory区域
- [ ] 点击按钮触发API连通性测试
- [ ] 测试期间按钮显示加载状态
- [ ] 成功连接时显示明确成功提示
- [ ] 连接失败时显示具体错误原因
- [ ] 测试不影响现有功能

### 5.2 非功能验收
- [ ] 测试响应时间 < 5秒（正常情况）
- [ ] 前端代码无内存泄漏
- [ ] 后端接口有适当的错误处理
- [ ] 代码符合项目编码规范

## 6. 时间计划

| 阶段 | 负责人 | 开始时间 | 结束时间 | 状态 |
|------|--------|----------|----------|------|
| 需求分析与设计 | PM + 架构师 | Day 1 AM | Day 1 PM | 待开始 |
| 后端开发 | 后端开发者 | Day 1 PM | Day 2 PM | 待开始 |
| 前端开发 | 前端开发者 | Day 2 AM | Day 3 AM | 待开始 |
| 测试与验证 | 测试人员 | Day 3 AM | Day 3 PM | 待开始 |
| 部署与文档 | 全体 | Day 3 PM | Day 4 AM | 待开始 |

**总预计工时**：3.5人日
**目标完成日期**：4个工作日内

---

## 附录：文件结构变更

### 新增文件
```
src/backend/api/deepseek_test.py      # DeepSeek测试接口
src/backend/tests/test_deepseek.py    # 后端测试文件
```

### 修改文件
```
src/frontend/agent-team-config.html   # 添加测试按钮
src/frontend/js/agent-team-config.js  # 添加测试功能
```

### 配置文件更新
```
requirements.txt                       # 添加openai依赖（如需要）
```

---

**注意事项**：
1. 开发前请确认现有代码结构和命名规范
2. 所有API Key处理必须通过后端，避免前端直接调用第三方API
3. 确保测试功能不会消耗过多API额度（使用最小化测试请求）
4. 考虑添加测试频率限制，防止滥用

────────────────────────────────────────────────────────────
✅ deepseek-chat 完成
