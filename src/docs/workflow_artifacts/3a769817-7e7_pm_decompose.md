# PM分解 — project_manager

任务: 测试emoji
步骤: pm_decompose
Agent: build_pm

---

📋 任务: 3a769817-7e7
🤖 Agent: PM (project_manager)
📂 工作目录: /Users/panglaohu/Downloads/DoubleBoatClawSystem
⏱️ 超时: 300s
────────────────────────────────────────────────────────────
📝 提示词:
  你是 PoseidonX 系统的 PM (project_manager)。
  请执行以下开发任务:
  
  你是项目经理 (PM)。请对以下任务进行分解和规划:
  
  ## 任务
  测试emoji
  测试emoji
  
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

# PoseidonX System - 任务分解与规划文档
**项目名称**: DoubleBoatClawSystem  
**任务 ID**: T-TEST-EMOJI-001  
**执行者**: PoseidonX Project Manager (PM)  
**状态**: 规划完成，等待执行  
**最后更新**: 2023-10-27  

---

## 1. 任务背景与目标
当前任务为“测试 emoji”，在 PoseidonX 系统中，这通常意味着验证前后端对 Unicode 表情符号集的正确处理能力。考虑到系统名称 `DoubleBoatClawSystem`，该功能可能涉及：
- 用户在抓取游戏（Claw Machine）中的昵称、状态、弹幕或结果描述中显示 Emoji。
- 验证后端 Python FastAPI 在序列化/反序列化时是否发生乱码。
- 验证前端 HTML/JS 渲染是否正常。

**核心目标**：确保系统在极端字符输入（Emoji）场景下，数据流转无损失、无乱码，且 UI 渲染正常。

---

## 2. 任务拆解 (Sub-tasks)

### 2.1 环境准备与依赖检查
- **步骤 2.1.1 [DevOps]**: 确认 `src/backend/` 的 Python 环境（虚拟环境）已激活，并安装 `pytest`。
- **步骤 2.1.2 [DevOps]**: 确认 `TESTING` 环境变量配置正确（特别是 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` 的使用场景，确保没有插件污染）。
- **步骤 2.1.3 [DevOps]**: 检查数据库配置（如有），确保 `UTF-8mb4` 字符集设置正确（MySQL/PostgreSQL/SQLite 均需注意）。

### 2.2 后端测试开发 (Python FastAPI)
**负责人**: Backend Developer  
**路径**: `src/backend/tests/`

- **步骤 2.2.1 [Code]**: 创建测试模块 `test_emoji_handling.py`。
- **步骤 2.2.2 [Code]**: 编写测试用例，覆盖以下场景：
  1. **单 Emoji**: 发送 `{"text": "🎣"}`。
  2. **混合字符串**: 发送 `{"text": "抓到啦！🏆🚤"}`。
  3. **极长 Emoji 序列**: 发送包含多个表情组合的长字符串。
  4. **特殊 Emoji (如皮肤修饰符/组合键)**: 测试 `👨‍👩‍👧‍👦` 等零宽连接符的输入。
  5. **API 响应验证**: 验证 FastAPI 返回的 JSON 中，Emoji 未被转义成 `\uXXXX` 或乱码。
- **步骤 2.2.3 [Code]**: 验证数据库存入过程，确保写入数据库后读取出来依然完整。

### 2.3 前端测试验证 (HTML + JS)
**负责人**: Frontend Developer  
**路径**: `src/frontend/` (需配合临时 HTML 文件或调试模式)

- **步骤 2.3.1 [Manual/Auto]**: 编写本地 HTML 测试脚本或手动操作。
  - 模拟用户输入框输入各类 Emoji，点击发送。
  - 验证控制台 (`console.log`) 接收到的原始数据是否正确（无乱码）。
  - 验证 DOM 渲染结果，确保 Emoji 正常显示，未被解析为方块 (□) 或空白。
- **步骤 2.3.2 [Code]**: (可选) 如果前端有 JS 单元测试，添加对应的断言测试。

### 2.4 集成测试执行
**负责人**: QA / All Devs  
**执行命令**:
```bash
cd /Users/panglaohu/Downloads/DoubleBoatClawSystem
# 确保进入项目根目录
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short
```

---

## 3. 技术风险与依赖分析

| 风险点 | 描述 | 缓解措施 |
| :--- | :--- | :--- |
| **数据库字符集** | 若数据库未设置 `utf8mb4`，Emoji 可能被截断或报错 `Incorrect string value`。 | 强制检查数据库连接字符串配置；本地开发环境建议直接复用 SQLite (通常无损) 或确保 MySQL 配置正确。 |
| **HTTP 协议头** | Content-Type 头若未明确包含 `charset=utf-8`，部分旧浏览器或中间件可能导致渲染问题。 | 确认 FastAPI 中间件配置默认包含 UTF-8。 |
| **字体支持** | 前端运行环境（操作系统/容器）若缺少 Emoji 字体，显示会异常。 | 测试时需覆盖 macOS (原生支持好), Windows, 以及标准 Linux 容器环境。 |
| **JSON 序列化** | Python `json` 默认会转义非 ASCII 字符（`\u...`），影响阅读但功能通常正常。 | 在测试中明确是否要求“原始字符”显示。若需原始字符，需设置 `ensure_ascii=False`。 |
| **命令执行权限** | `PYTEST_DISABLE_PLUGIN_AUTOLOAD` 标志可能在某些自动化管道中干扰插件加载。 | 仅在本地验证环境使用此命令；CI/CD 流程需另行配置。 |

**依赖关系**:
- **依赖**: `src/backend/main.py` (FaskAPI 入口), `tests/` (测试目录)。
- **阻塞**: 若后端 API 尚未提供 `POST /test-emoji` 接口，测试无法执行。
  - *建议*: 如果没有真实接口，先创建一个 Mock 路由或直接在代码层面测试序列化逻辑。

---

## 4. 实施指导 (Actionable Guides)

### 给后端开发者 (Backend Dev)
1. **代码修改**: 检查 `src/backend/main.py` 或相关路由处理器，确保在返回 JSON 时使用了 `json_response(..., ensure_ascii=False)` (FastAPI `JSONResponse` 默认处理得当，但需确认自定义解析器)。
2. **测试编写**: 在 `src/backend/tests/test_emoji_handling.py` 中构建如下案例：
   ```python
   import json
   from fastapi.testclient import TestClient
   from src.backend.main import app

   client = TestClient(app)

   def test_emoji_in_body():
       data = {"message": "Double Boat Win ⛵💪🎉"}
       # 假设有一个测试接口，如果没有，直接测试 JSON 序列化
       response = client.post("/test", json=data) 
       assert response.status_code == 200
       data = response.json()
       assert data["message"] == "Double Boat Win ⛵💪🎉" # 必须完全匹配，不能是 \u...
   ```

### 给前端开发者 (Frontend Dev)
1. **调试工具**: 打开浏览器开发者工具 (F12) -> Network 面板，观察发送和接收的 Payload。
2. **可视化验证**: 创建一个简单的 HTML 页面，内容包含：
   ```html
   <div id="output"></div>
   <input type="text" id="input" value="🚤🎣">
   <button onclick="test()">Test</button>
   <script>
     function test() {
       const val = document.getElementById('input').value;
       console.log("Raw:", val, val.length);
       document.getElementById('output').innerText = val;
       // 检查是否显示为方块
       if (document.getElementById('output').textContent.length !== val.length) {
         console.error("Render error: length mismatch");
       }
     }
   </script>
   ```

### 给 PM (PoseidonX)
- **验收标准**: 
  1. `python -m pytest tests/ -q --tb=short` 执行全部通过 (`PASSED`)。
  2. 无警告信息 (`warnings`).
  3. 本地运行脚本验证人工观察无乱码。
- **交付物**: 更新后的测试文件 `tests/test_emoji_handling.py` 及执行通过的日志截图。

---

## 5. 执行计划时间表 (预估)

| 阶段 | 任务 | 预计耗时 | 负责角色 |
| :--- | :--- | :--- | :--- |
| **T+0m** | 环境确认与接口确认 | 15 min | PM + Backend |
| **T+30m** | 后端测试脚本编写与通过 | 45 min | Backend |
| **T+75m** | 前端手动/自动验证 | 30 min | Frontend |
| **T+105m** | 集成运行最终命令 | 5 min | All |
| **T+110m** | 文档更新与封库 | 10 min | PM |

---

**下一步行动**：
请 **Backend Developer** 立即检查是否存在对应的 Mock 接口，若无，请创建临时路由以支持测试脚本运行。请 **Frontend Developer** 准备测试脚本。完成后请立即执行根目录下的 pytest 命令。

────────────────────────────────────────────────────────────
✅ Ollama 直连完成
