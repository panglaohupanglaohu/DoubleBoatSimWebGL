import http.client, json

conn = http.client.HTTPConnection("localhost", 11434, timeout=60)

# Test with thinking parameter (Claude Code v2.1.92 enables extended thinking)
tests = [
    ("no thinking", {}),
    ("thinking enabled", {"thinking": {"type": "enabled", "budget_tokens": 10000}}),
    ("thinking + betas", {"thinking": {"type": "enabled", "budget_tokens": 10000}}),
]

for name, extra in tests:
    c = http.client.HTTPConnection("localhost", 11434, timeout=30)
    payload = {
        "model": "qwen3.5-35b-claude",
        "max_tokens": 4096,
        "stream": True,
        "messages": [{"role": "user", "content": "say OK"}],
    }
    payload.update(extra)

    headers = {
        "Content-Type": "application/json",
        "x-api-key": "ollama",
        "anthropic-version": "2023-06-01",
    }
    if "thinking" in name:
        headers["anthropic-beta"] = "interleaved-thinking-2025-05-14"

    body = json.dumps(payload)
    c.request("POST", "/v1/messages", body=body, headers=headers)
    resp = c.getresponse()
    data = resp.read(512).decode()
    status = resp.status
    if status != 200:
        print(f"  {name:30s} -> {status} {data[:200]}")
    else:
        print(f"  {name:30s} -> OK")
    c.close()
