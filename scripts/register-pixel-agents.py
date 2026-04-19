#!/usr/bin/env python3
"""
register-pixel-agents.py — 将 7 个 PoseidonX Agent 注册到 Pixel Agents 面板

运行后 Agent 立即出现在 VS Code 的 Pixel Agents 侧栏面板中。
可配置为 VS Code 启动任务 (runOn: folderOpen) 实现"打开即显示"。

用法:
    python3 scripts/register-pixel-agents.py          # 注册
    python3 scripts/register-pixel-agents.py --clear   # 清空
    python3 scripts/register-pixel-agents.py --status  # 查看状态
"""

import json
import os
import sqlite3
import sys
import time
import uuid
from pathlib import Path

# ── Agent 定义 ──────────────────────────────────────

AGENTS = [
    {
        "name": "Chief Director",
        "slug": "chief_director",
        "role": "项目总监",
        "emoji": "👔",
        "description": "项目总监 — 任务分解、进度跟踪、跨 Agent 协调",
    },
    {
        "name": "System Architect",
        "slug": "system_architect",
        "role": "架构设计师",
        "emoji": "🏗️",
        "description": "架构设计师 — 系统分层 L0-L5、接口规范、技术选型",
    },
    {
        "name": "Dev Lead",
        "slug": "dev_lead",
        "role": "开发主管",
        "emoji": "🔧",
        "description": "开发主管 — 代码审查、任务分配、技术指导",
    },
    {
        "name": "Code Writer",
        "slug": "code_writer",
        "role": "代码开发者",
        "emoji": "💻",
        "description": "代码开发者 — 功能开发、Bug 修复、单元测试",
    },
    {
        "name": "QA Engineer",
        "slug": "qa_engineer",
        "role": "测试工程师",
        "emoji": "🧪",
        "description": "测试工程师 — pytest 1203+ 测试、质量保证",
    },
    {
        "name": "Marine Researcher",
        "slug": "marine_researcher",
        "role": "海洋研究员",
        "emoji": "🌊",
        "description": "海洋研究员 — COLREGs、WPC 物理模型、IMO 标准",
    },
    {
        "name": "Doc Writer",
        "slug": "doc_writer",
        "role": "文档工程师",
        "emoji": "📝",
        "description": "文档工程师 — 架构文档、API 文档、README",
    },
]


# ── 工具函数 ──────────────────────────────────────────

def get_workspace_state_db():
    """找到当前工作空间的 VS Code workspaceState 数据库"""
    storage_root = Path.home() / "Library" / "Application Support" / "Code" / "User" / "workspaceStorage"
    if not storage_root.exists():
        return None

    ws = os.environ.get("VSCODE_WORKSPACE", str(Path(__file__).resolve().parent.parent))
    workspace_uri = f"file://{ws}"

    for d in storage_root.iterdir():
        ws_file = d / "workspace.json"
        if ws_file.exists():
            try:
                data = json.loads(ws_file.read_text())
                folder = data.get("folder", "")
                if folder == workspace_uri or ws in folder:
                    db = d / "state.vscdb"
                    if db.exists():
                        return db
            except (json.JSONDecodeError, KeyError):
                continue
    return None


def get_project_dir():
    """获取 Claude Code 项目目录"""
    ws = str(Path(__file__).resolve().parent.parent)
    import re
    slug = re.sub(r'[^a-zA-Z0-9-]', '-', ws)
    return Path.home() / ".claude" / "projects" / slug


def read_state(db_path):
    """读取 Pixel Agents 状态"""
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.execute(
            "SELECT value FROM ItemTable WHERE key='pablodelucca.pixel-agents'"
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return {"pixel-agents.agents": [], "pixel-agents.agentSeats": {}}
    finally:
        conn.close()


def write_state(db_path, state):
    """写入 Pixel Agents 状态"""
    conn = sqlite3.connect(str(db_path))
    try:
        value = json.dumps(state, ensure_ascii=False)
        conn.execute(
            "INSERT OR REPLACE INTO ItemTable (key, value) VALUES ('pablodelucca.pixel-agents', ?)",
            (value,)
        )
        conn.commit()
    finally:
        conn.close()


# ── JSONL 会话存根 ──────────────────────────────────

def create_session_stubs():
    """为每个 Agent 创建 JSONL 会话存根文件"""
    proj_dir = get_project_dir()
    proj_dir.mkdir(parents=True, exist_ok=True)

    session_map = {}  # slug -> (session_id, jsonl_path)

    for agent in AGENTS:
        # 使用固定的确定性 UUID (基于 agent slug)，避免每次创建新文件
        session_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"poseidonx.{agent['slug']}"))
        jsonl_path = proj_dir / f"{session_id}.jsonl"

        if not jsonl_path.exists():
            # 写入初始消息
            init_msg = {
                "type": "system",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "message": f"PoseidonX Agent: {agent['name']} ({agent['role']})",
                "agentSlug": agent["slug"],
                "agentName": agent["name"],
            }
            jsonl_path.write_text(json.dumps(init_msg, ensure_ascii=False) + "\n")

        session_map[agent["slug"]] = (session_id, str(jsonl_path))

    return session_map


# ── 命令 ──────────────────────────────────────────────

def cmd_register():
    """注册所有 Agent 到 Pixel Agents 面板"""
    db = get_workspace_state_db()
    if not db:
        print("❌ 未找到 VS Code workspaceState 数据库")
        print("   请确保在 VS Code 终端中运行，或设置 VSCODE_WORKSPACE 环境变量")
        sys.exit(1)

    print(f"📂 数据库: {db}")

    # 创建 JSONL 会话存根
    session_map = create_session_stubs()

    # 构建 agent 记录
    state = read_state(db)
    agents = []
    seats = state.get("pixel-agents.agentSeats", {})

    # 保留已有 seat (通常 seat "1" 是用户自己)
    for i, agent in enumerate(AGENTS):
        agent_id = i + 1
        session_id, jsonl_path = session_map[agent["slug"]]

        agents.append({
            "id": agent_id,
            "terminalName": f"Claude Code #{agent_id}",
            "jsonlFile": jsonl_path,
            "sessionId": session_id,
            "agentName": agent["name"],
            "agentSlug": agent["slug"],
            "agentRole": agent["role"],
            "agentEmoji": agent["emoji"],
        })

        # 为每个 Agent 分配座位 (从 seat 2 开始, seat 1 留给用户)
        seat_key = str(agent_id + 1)
        if seat_key not in seats:
            seats[seat_key] = {
                "palette": i % 8,
                "hueShift": i * 45,
                "seatId": f"agent-{agent['slug']}-{int(time.time())}",
            }

    state["pixel-agents.agents"] = agents
    state["pixel-agents.agentSeats"] = seats
    write_state(db, state)

    print(f"\n✅ 已注册 {len(agents)} 个 Agent 到 Pixel Agents 面板:\n")
    for a in agents:
        emoji = next((ag["emoji"] for ag in AGENTS if ag["slug"] == a["agentSlug"]), "")
        print(f"   {emoji} #{a['id']}  {a['agentName']:20s}  ({a['agentRole']})")

    print(f"\n📁 JSONL 会话目录: {get_project_dir()}")
    print(f"\n💡 如面板未刷新，按 Cmd+Shift+P → 'Developer: Reload Window'")


def cmd_clear():
    """清空所有注册的 Agent"""
    db = get_workspace_state_db()
    if not db:
        print("❌ 未找到数据库")
        sys.exit(1)

    state = read_state(db)
    count = len(state.get("pixel-agents.agents", []))
    state["pixel-agents.agents"] = []
    # 保留 seat 1 (用户)
    seats = state.get("pixel-agents.agentSeats", {})
    state["pixel-agents.agentSeats"] = {"1": seats.get("1", {})} if "1" in seats else {}
    write_state(db, state)
    print(f"🗑  已清除 {count} 个 Agent")


def cmd_status():
    """显示当前面板状态"""
    db = get_workspace_state_db()
    if not db:
        print("❌ 未找到数据库")
        sys.exit(1)

    state = read_state(db)
    agents = state.get("pixel-agents.agents", [])
    seats = state.get("pixel-agents.agentSeats", {})

    print(f"🤖 Pixel Agents 面板状态")
    print(f"   数据库: {db}")
    print(f"   已注册: {len(agents)} 个 Agent")
    print(f"   座位: {len(seats)} 个\n")

    if agents:
        for a in agents:
            name = a.get("agentName", a.get("terminalName", "?"))
            role = a.get("agentRole", "")
            jsonl = a.get("jsonlFile", "")
            exists = "✅" if Path(jsonl).exists() else "❌"
            print(f"   #{a.get('id', '?'):2}  {name:20s}  {role:10s}  JSONL:{exists}")
    else:
        print("   (无 Agent)")


def main():
    if "--clear" in sys.argv:
        cmd_clear()
    elif "--status" in sys.argv:
        cmd_status()
    else:
        cmd_register()


if __name__ == "__main__":
    main()
