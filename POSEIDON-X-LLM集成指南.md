# Poseidon-X LLM 集成指南

## 🧠 真实 LLM 集成（DeepSeek / GPT-4 / Claude）

---

## 🚀 快速开始

### Step 1: 配置 LLM

访问配置页面：

**http://localhost:3000/poseidon-config.html**

### Step 2: 选择 DeepSeek（推荐）

1. 点击 **DeepSeek** 卡片
2. 输入你的 API Key
3. 点击 **🧪 测试连接**（验证配置）
4. 点击 **💾 保存并启动**

### Step 3: 开始对话

系统会自动跳转到：**http://localhost:3000/poseidon-x-demo.html**

现在 Bridge Chat 会使用**真实的 DeepSeek API**！

---

## 🔧 配置说明

### DeepSeek 配置

**获取 API Key**:
1. 访问：https://platform.deepseek.com/api_keys
2. 注册/登录
3. 创建新的 API Key
4. 复制 Key 到配置页面

**API Endpoint**: `https://api.deepseek.com/v1`  
**推荐模型**: `deepseek-chat`  
**Context Length**: 64K tokens

**优势**:
- ✅ 性价比高（比 GPT-4 便宜很多）
- ✅ 支持中文
- ✅ 速度快
- ✅ 兼容 OpenAI API 格式

---

## 📊 当前架构

### LLM 调用流程

```
用户输入
  ↓
Bridge Chat (_callLLM)
  ↓
LLMClient.chat()
  ↓
[真实 API 调用]
  ├─ DeepSeek API (https://api.deepseek.com/v1/chat/completions)
  ├─ OpenAI API (https://api.openai.com/v1/chat/completions)
  └─ Anthropic API (https://api.anthropic.com/v1/messages)
  ↓
返回响应
  ↓
Bridge Chat 显示给用户
```

### Agent 推理流程

```
Agent.execute(task, context)
  ↓
Agent.think(query, context)
  ↓
Agent._callLLM(prompt)
  ↓
LLMClient.chat(messages)
  ↓
[真实 LLM 推理]
  ↓
返回决策
  ↓
Agent.useTool(toolName, params)
  ↓
返回结果
```

---

## 🎯 已集成的功能

### 1. Bridge Chat（舰桥对话）

**文件**: `src/poseidon/layer1-interface/BridgeChat.js`

**真实 LLM 调用**:
```javascript
// 现在使用真实的 DeepSeek API
const response = await this.llmClient.chat(messages);
// response.content 是真实的 AI 回复
```

**Vibe 优化**:
```javascript
vibe: `你是 Poseidon-X 船舶智能系统的核心 AI 助手。
你管理着 4 个专业智能体：
1. Navigator Agent（领航员）
2. Engineer Agent（轮机长）
3. Steward Agent（大管家）
4. Safety Agent（安全官）

当用户提问时，你要判断应该由哪个Agent处理...`
```

现在 AI 知道自己管理 4 个智能体！

### 2. AgentBase（智能体基类）

**文件**: `src/poseidon/layer2-agents/AgentBase.js`

**真实 LLM 推理**:
```javascript
async _callLLM(prompt) {
  const messages = [
    { role: 'system', content: this.vibe },
    { role: 'user', content: prompt }
  ];
  
  // 真实 API 调用
  const response = await this.llmClient.chat(messages);
  return { content: response.content };
}
```

### 3. LLMClient（API 客户端）

**文件**: `src/poseidon/layer1-interface/LLMClient.js`

**支持的提供商**:
- ✅ DeepSeek (推荐)
- ✅ OpenAI (GPT-4)
- ✅ Anthropic (Claude)
- ✅ 本地模型 (Ollama)

---

## 💬 对话示例（真实 LLM）

### Before（模拟响应）

```
用户: 那4个智能体
AI: 收到您的指令："那4个智能体"。我正在协调相关智能体...
```

❌ 问题：AI 不知道具体有哪些智能体

### After（真实 DeepSeek）

```
用户: 那4个智能体
DeepSeek AI: 我管理着 4 个专业智能体：

1. ⚓ Navigator Agent（领航员）
   - 职责：航行路径规划、避碰决策、气象路由
   
2. ⚙️ Engineer Agent（轮机长）
   - 职责：设备健康管理、能效监控、故障诊断
   
3. 🏠 Steward Agent（大管家）
   - 职责：仓储管理、伙食安排、环境控制
   
4. 🛡️ Safety Agent（安全官）
   - 职责：视觉监控、应急响应、安全巡检

您想了解哪个智能体的详细信息？
```

✅ 准确：AI 清楚地知道自己的能力

---

## 🔄 集成步骤

### 已完成 ✅

1. ✅ 创建配置页面（poseidon-config.html）
2. ✅ 创建 LLMClient（支持多提供商）
3. ✅ 修改 BridgeChat 使用真实 LLM
4. ✅ 修改 AgentBase 使用真实 LLM
5. ✅ 配置持久化（localStorage）

### 待完成 🔜

6. ⏳ 每个专业 Agent 的详细实现
7. ⏳ Tool Use 与真实系统集成
8. ⏳ 向量数据库（长期记忆）
9. ⏳ Function Calling（工具调用）
10. ⏳ Streaming 响应（打字机效果）

---

## 📝 配置文件结构

### localStorage 存储

**Key**: `poseidon_config`

**Value** (JSON):
```json
{
  "llmProvider": "deepseek",
  "apiKey": "sk-xxx...xxx",
  "apiEndpoint": "https://api.deepseek.com/v1",
  "model": "deepseek-chat",
  "temperature": 0.7,
  "maxContextTokens": 64000,
  "language": "zh-CN",
  "enableVoice": false
}
```

### 配置优先级

1. 构造函数参数（最高优先级）
2. localStorage 配置
3. 默认值

---

## 🎓 使用指南

### 首次使用

1. 访问：**http://localhost:3000/poseidon-config.html**
2. 配置 DeepSeek API Key
3. 点击"保存并启动"
4. 自动跳转到主页面
5. 在 Bridge Chat 对话

### 后续使用

配置会自动保存，直接访问：

**http://localhost:3000/poseidon-x-demo.html**

### 重新配置

重新访问配置页面，或点击"重置配置"按钮

---

## 🔍 测试 LLM 集成

### 控制台测试

打开浏览器控制台（F12）：

```javascript
// 测试 LLM Client
const client = LLMClient.loadFromStorage();
const result = await client.testConnection();
console.log(result);

// 测试对话
const response = await client.chat([
  { role: 'user', content: 'Poseidon-X 有几个智能体？' }
]);
console.log(response.content);
```

### Bridge Chat 测试

在 Bridge Chat 对话框输入：

- "你管理哪些智能体？"
- "Navigator Agent 能做什么？"
- "当前有几个 Agent 在运行？"

现在 AI 会给出准确的回答！

---

## 🎊 集成完成

✅ **真实 LLM 已集成**  
✅ **配置页面已创建**  
✅ **DeepSeek API 已支持**  
✅ **4个 Agent 都能使用真实 LLM**  

**立即配置**: http://localhost:3000/poseidon-config.html 🚀
