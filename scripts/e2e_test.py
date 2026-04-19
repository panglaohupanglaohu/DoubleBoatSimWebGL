#!/usr/bin/env python3
"""E2E test for the task workflow + Claude Code pipeline."""
import http.client
import json
import time
import sys

HOST = "localhost"
PORT = 8080
BASE = "/api/v1/agent-config"


def api(method, path, data=None):
    conn = http.client.HTTPConnection(HOST, PORT, timeout=15)
    headers = {"Content-Type": "application/json"} if data else {}
    body = json.dumps(data) if data else None
    conn.request(method, f"{BASE}{path}", body=body, headers=headers)
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8")
    conn.close()
    if resp.status >= 400:
        print(f"  ❌ HTTP {resp.status}: {raw[:200]}")
        return None
    return json.loads(raw, strict=False)


def main():
    print("=" * 55)
    print("E2E TEST: 完整流水线 (Ollama tunnel)")
    print("=" * 55)

    # 1. Create task
    task = api("POST", "/teams/build_system/tasks", {
        "title": "给thruster-control添加刷新按钮",
        "agent_id": "build_pm",
        "priority": 2,
        "description": "在推进控制页面右上角添加'刷新数据'按钮"
    })
    if not task:
        print("❌ Task creation failed")
        return 1
    tid = task["task_id"]
    print(f"✅ 任务 {tid} 创建成功")

    # 2. Advance 3x to reach develop
    for name in ["PM分解", "研究分析", "架构设计"]:
        d = api("POST", f"/teams/build_system/tasks/{tid}/workflow/advance")
        if not d:
            print(f"❌ Advance failed at {name}")
            return 1
        print(f"  → {name} 完成")

    # 3. Find session
    session_id = None
    for s in d["workflow"]:
        mark = " ⬅" if s["status"] == "active" else ""
        sid = s.get("session_id", "")
        if sid:
            session_id = sid
        print(f'  {s["label"]:8s} [{s["status"]:9s}]{mark} {sid}')

    if not session_id:
        print("❌ No Claude Code session auto-started!")
        return 1

    print(f"\n✅ Claude Code Session: {session_id}")
    print(f"   Model: qwen3.5-35b-claude via SSH tunnel → gpu11")
    print(f"⏳ 等待模型响应...\n")

    # 4. Poll
    for wait in [15, 20, 30, 40, 60, 60, 60]:
        time.sleep(wait)
        sd = api("GET", f"/claude-sessions/{session_id}")
        if not sd:
            print("❌ Session query failed")
            return 1

        elapsed = sd["elapsed"]
        lines = sd["line_count"]
        st = sd["status"]
        print(f"  [{elapsed:.0f}s] status={st} lines={lines}")

        if st in ("completed", "failed", "error", "stopped"):
            emoji = "✅" if st == "completed" else "❌"
            print(f"\n{emoji} {st} (exit={sd['exit_code']})")
            out = sd.get("output", [])
            real = [l for l in out if l.strip() and "─" * 10 not in l]
            print(f"\n--- Output ({len(real)} lines) ---")
            for l in real[-40:]:
                print(f"  {l.rstrip()}")
            return 0 if st == "completed" else 1

        if lines > 22:
            out = sd.get("output", [])
            new_lines = [l for l in out[20:] if l.strip()]
            print(f"    ({len(new_lines)} new output lines)")
            for l in new_lines[-3:]:
                print(f"    | {l.rstrip()}")

    # Timeout
    sd = api("GET", f"/claude-sessions/{session_id}")
    print(f"\n⏳ 超过 5 分钟仍在运行 ({sd['elapsed']:.0f}s)")
    for l in sd.get("output", [])[-20:]:
        print(f"  {l.rstrip()}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
