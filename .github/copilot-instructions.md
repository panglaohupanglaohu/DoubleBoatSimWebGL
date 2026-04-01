# PoseidonX — 深海远洋双体船舶智能综合信息系统

## 项目概况

AI Native 海事 CPS 系统: Python 3.14 FastAPI 后端 + Three.js 数字孪生前端

## 关键路径

- 后端入口: `src/backend/main.py`
- Channel 基类: `src/backend/channels/marine_base.py` — 所有 Channel 继承 `MarineChannel`
- Channel 注册: `src/backend/register_channels.py`
- 前端入口: `src/frontend/digital-twin/main.js`
- 配置: `config/settings.json`

## 开发环境

```bash
source venv/bin/activate
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q --tb=short
cd src/backend && python main.py --port 8080
npx vite --config vite.config.mjs
```

## 编码规范

- Channel 接口: `process_event()`, `get_status()`, `start()`, `stop()`
- 向后兼容: 修改签名时新参数必须有默认值
- 可变默认值: 使用工厂函数，不用模块级 dict/list 共享
- 零值安全: `any(v is None for v in [lat, lon])` 而非 `not all([lat, lon])`
- pytest 必须加 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`（Python 3.14 兼容）

## 架构分层 (L0-L5)

详见 `docs/architecture/ARCHITECTURE.md`

## Agent 团队

7 个专业 Agent 在 `.github/agents/` 中配置，通过 VS Code 聊天面板的 Agent 选择器使用。
