import http.client, json

conn = http.client.HTTPConnection("localhost", 11434, timeout=60)

# Test with anthropic-beta header (which Claude Code v2.1.92 sends)
payload = json.dumps({
    "model": "qwen3.5-35b-claude",
    "max_tokens": 16384,
    "stream": True,
    "system": [{"type": "text", "text": "You are a coding assistant."}],
    "messages": [{"role": "user", "content": "respond OK"}],
})

print(f"Payload size: {len(payload)} bytes")

# Try with various beta headers that Claude Code sends
for beta in [
    None,
    "tools-2024-04-04",
    "prompt-caching-2024-07-31",
    "interleaved-thinking-2025-05-14",
]:
    conn2 = http.client.HTTPConnection("localhost", 11434, timeout=30)
    headers = {
        "Content-Type": "application/json",
        "x-api-key": "ollama",
        "anthropic-version": "2023-06-01",
    }
    if beta:
        headers["anthropic-beta"] = beta
    conn2.request("POST", "/v1/messages", body=payload, headers=headers)
    resp = conn2.getresponse()
    body = resp.read(512).decode()
    beta_str = beta or "(none)"
    if resp.status != 200:
        print(f"  beta={beta_str:45s} -> {resp.status} {body[:100]}")
    else:
        print(f"  beta={beta_str:45s} -> OK")
    conn2.close()
