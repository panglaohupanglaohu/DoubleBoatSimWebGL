#!/usr/bin/env python3
"""
pixel-agents-cli.py - Pixel Agents CLI 注入工具

通过以下步骤将 Agent 注入 Pixel Agents 面板:
1. 在 VS Code 中创建名为 "Claude Code #N" 的终端
2. 在终端中执行 claude --session-id <uuid>
3. 将 agent 记录写入 VS Code workspaceState (SQLite)
4. 重载 VS Code 窗口后，Pixel Agents 扩展自动恢复所有 Agent

用法:
    python3 scripts/pixel-agents-cli.py inject -n 7     # 注入 7 个 Agent
    python3 scripts/pixel-agents-cli.py inject -n 3     # 注入 3 个 Agent
    python3 scripts/pixel-agents-cli.py status           # 查看面板状态
    python3 scripts/pixel-agents-cli.py sessions         # 列出会话文件
    python3 scripts/pixel-agents-cli.py clear            # 清空已注册的 Agent
"""

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import uuid
from pathlib import Path


# ── 项目目录解析 ──────────────────────────────────────

def get_project_dir(workspace=None):
    """获取当前项目在 .claude/projects/ 中的会话目录 (与 Pixel Agents 一致)"""
    ws = workspace or os.getcwd()
    slug = re.sub(r'[^a-zA-Z0-9-]', '-', ws)
    return Path.home() / ".claude" / "projects" / slug


def get_workspace_state_db(workspace=None):
    """找到当前工作空间的 VS Code workspaceState 数据库"""
    storage_root = Path.home() / "Library" / "Application Support" / "Code" / "User" / "workspaceStorage"
    if not storage_root.exists():
        return None

    ws = workspace or os.getcwd()
    workspace_uri = f"file://{ws}"

    for d in storage_root.iterdir():
        ws_file = d / "workspace.json"
        if ws_file.exists():
            try:
                data = json.loads(ws_file.read_text())
                if data.get("folder") == workspace_uri:
                    db = d / "state.vscdb"
                    if db.exists():
                        return db
            except (json.JSONDecodeError, KeyError):
                continue
    return None


# ── 读写 workspaceState ──────────────────────────────

def read_pixel_agents_state(db_path):
    """读取 Pixel Agents 扩展的 workspaceState"""
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


def write_pixel_agents_state(db_path, state):
    """写入 Pixel Agents 扩展的 workspaceState"""
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


# ── 核心命令 ──────────────────────────────────────────

def cmd_inject(args):
    """注入 Agent: 逐个创建终端运行 claude，让扩展自动检测 JSONL"""
    count = args.count
    proj_dir = get_project_dir()
    proj_dir.mkdir(parents=True, exist_ok=True)

    # 获取注入前的已有 JSONL 文件集合
    existing_jsonl = set(f.name for f in proj_dir.glob("*.jsonl"))

    print(f"🚀 准备注入 {count} 个 Agent 到 Pixel Agents 面板")
    print(f"   会话目录: {proj_dir}")
    print(f"   已有会话: {len(existing_jsonl)}")
    print()
    print("⚠️  请确保 VS Code 在前台且 Pixel Agents 面板已打开")
    print()

    sessions = []

    for i in range(count):
        agent_num = i + 1
        session_id = str(uuid.uuid4())
        sessions.append(session_id)

        print(f"  [{agent_num}/{count}] 创建 Agent (session: {session_id[:8]}...)...")

        # 通过 AppleScript 在 VS Code 中创建新终端并运行 claude
        # Pixel Agents 扩展的 Dr() 扫描器每秒检查新 JSONL 文件
        # 新文件会被绑定到当前活跃终端 (刚创建的那个)
        applescript = f'''
        tell application "Visual Studio Code"
            activate
        end tell
        delay 0.8
        tell application "System Events"
            tell process "Code"
                key code 50 using {{control down, shift down}}
                delay 1.5
                keystroke "claude --session-id {session_id}"
                delay 0.2
                key code 36
            end tell
        end tell
        '''

        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"    ⚠️  终端创建可能失败: {result.stderr.strip()}")
        else:
            print(f"    ✅ 终端已创建")

        # 等待 claude 启动生成 JSONL + Pixel Agents 扫描检测
        print(f"    ⏳ 等待 JSONL 生成...")
        waited = 0
        found = False
        while waited < 15:
            time.sleep(1)
            waited += 1
            jsonl_file = proj_dir / f"{session_id}.jsonl"
            if jsonl_file.exists():
                found = True
                print(f"    ✅ JSONL 已生成 ({waited}s)")
                break

        if not found:
            print(f"    ⚠️  {waited}s 内未检测到 JSONL")

        # 额外等 3 秒让 Pixel Agents 的 Dr() 扫描器和 webview 处理完毕
        time.sleep(3)
        print()

    print(f"🎉 已创建 {count} 个 Claude 终端!")
    print()

    # 验证结果
    db = get_workspace_state_db()
    if db:
        state = read_pixel_agents_state(db)
        registered = len(state.get("pixel-agents.agents", []))
        print(f"📊 Pixel Agents 已注册: {registered} 个 Agent")
        if registered < count:
            print(f"   (如果不足 {count} 个，请重载窗口后检查)")
    print()
    print("💡 如果面板中看不到，尝试: Cmd+Shift+P → Developer: Reload Window")


def cmd_status(args):
    """显示 Pixel Agents 面板状态"""
    db = get_workspace_state_db()
    if not db:
        print("❌ 未找到当前工作空间的 VS Code 状态数据库")
        return

    state = read_pixel_agents_state(db)
    agents = state.get("pixel-agents.agents", [])
    seats = state.get("pixel-agents.agentSeats", {})

    print(f"🤖 Pixel Agents 面板状态")
    print(f"   已注册 Agent: {len(agents)}")
    print(f"   座位分配: {len(seats)}")
    print(f"   数据库: {db}")
    print()

    if agents:
        for a in agents:
            aid = a.get("id", "?")
            term = a.get("terminalName", "?")
            jsonl = a.get("jsonlFile", "N/A")
            jsonl_exists = "✅" if Path(jsonl).exists() else "❌"
            print(f"   Agent #{aid}: {term}")
            print(f"     JSONL: {jsonl_exists} {Path(jsonl).name}")
    else:
        print("   (面板中暂无 Agent)")


def cmd_sessions(args):
    """列出所有 Claude Code 会话"""
    proj_dir = get_project_dir()
    if not proj_dir.exists():
        print(f"项目目录不存在: {proj_dir}")
        return

    jsonl_files = sorted(proj_dir.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
    print(f"📁 项目会话目录: {proj_dir}")
    print(f"📊 共 {len(jsonl_files)} 个会话文件\n")

    for f in jsonl_files[:15]:
        stat = f.stat()
        size = stat.st_size
        mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
        size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / 1024 / 1024:.1f} MB"
        print(f"  {mtime}  {size_str:>10}  {f.stem}")

    if len(jsonl_files) > 15:
        print(f"\n  ... 还有 {len(jsonl_files) - 15} 个更早的会话")


def cmd_clear(args):
    """清空已注册的 Agent"""
    db = get_workspace_state_db()
    if not db:
        print("❌ 未找到当前工作空间的 VS Code 状态数据库")
        return

    state = read_pixel_agents_state(db)
    count = len(state.get("pixel-agents.agents", []))

    state["pixel-agents.agents"] = []
    state["pixel-agents.agentSeats"] = {}
    write_pixel_agents_state(db, state)

    print(f"🗑  已清除 {count} 个 Agent 注册记录")
    print("   重载 VS Code 窗口后生效")


# ── 入口 ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Pixel Agents CLI - 管理 VS Code Pixel Agents 面板中的 Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 scripts/pixel-agents-cli.py inject -n 7   # 注入 7 个 Agent
  python3 scripts/pixel-agents-cli.py status         # 查看面板状态
  python3 scripts/pixel-agents-cli.py clear          # 清空 Agent
        """
    )
    sub = parser.add_subparsers(dest="command")

    inject_parser = sub.add_parser("inject", help="注入 Agent 到 Pixel Agents 面板")
    inject_parser.add_argument("-n", "--count", type=int, default=7, help="Agent 数量 (默认 7)")

    sub.add_parser("status", help="显示当前面板状态")
    sub.add_parser("sessions", help="列出会话文件")
    sub.add_parser("clear", help="清空已注册的 Agent")

    args = parser.parse_args()

    commands = {
        "inject": cmd_inject,
        "status": cmd_status,
        "sessions": cmd_sessions,
        "clear": cmd_clear,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

