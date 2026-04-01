#!/usr/bin/env python3
"""Directly inject agent records into Pixel Agents workspaceState."""

import json
import sqlite3
import re
from pathlib import Path

WORKSPACE = '/Users/panglaohu/Downloads/DoubleBoatClawSystem'
DB_PATH = Path.home() / 'Library/Application Support/Code/User/workspaceStorage/7570512343c704a5a66729f318c620fb/state.vscdb'

AGENT_ROLES = [
    "Chief Director",
    "System Architect",
    "Marine Researcher",
    "Dev Lead",
    "Code Writer",
    "QA Engineer",
    "Doc Writer",
]

def main():
    slug = re.sub(r'[^a-zA-Z0-9-]', '-', WORKSPACE)
    proj_dir = str(Path.home() / '.claude/projects' / slug)

    # Find latest JSONL session files
    jsonl_dir = Path(proj_dir)
    if not jsonl_dir.exists():
        print(f"ERROR: JSONL dir not found: {jsonl_dir}")
        return
    jsonl_files = sorted(jsonl_dir.glob('*.jsonl'), key=lambda f: f.stat().st_mtime, reverse=True)[:7]
    print(f"Found {len(jsonl_files)} session files")

    # Build agent records
    agents = []
    for i, jf in enumerate(jsonl_files):
        agents.append({
            'id': i + 1,
            'terminalName': f'Claude Code #{i+1}',
            'jsonlFile': str(jf),
            'projectDir': proj_dir,
        })
        print(f"  Agent #{i+1} ({AGENT_ROLES[i] if i < len(AGENT_ROLES) else 'extra'}): {jf.name}")

    # Build seats (color palettes)
    seats = {}
    for a in agents:
        seats[str(a['id'])] = {'palette': (a['id'] - 1) % 6, 'hueShift': 0}

    # Build state
    state = {
        'pixel-agents.agents': agents,
        'pixel-agents.agentSeats': seats,
    }

    # Write to workspaceState
    if not DB_PATH.exists():
        print(f"ERROR: DB not found: {DB_PATH}")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT OR REPLACE INTO ItemTable (key, value) VALUES ('pablodelucca.pixel-agents', ?)",
        (json.dumps(state, ensure_ascii=False),)
    )
    conn.commit()
    conn.close()

    print(f"\nWrote {len(agents)} agents to workspaceState")
    print("Next: Reload VS Code window (Cmd+Shift+P -> 'Developer: Reload Window')")
    print("Then open Pixel Agents panel to see agents")

    # Verify
    conn = sqlite3.connect(str(DB_PATH))
    row = conn.execute("SELECT value FROM ItemTable WHERE key = 'pablodelucca.pixel-agents'").fetchone()
    conn.close()
    if row:
        data = json.loads(row[0])
        n = len(data.get('pixel-agents.agents', []))
        print(f"\nVerification: {n} agents in workspaceState")

if __name__ == '__main__':
    main()
