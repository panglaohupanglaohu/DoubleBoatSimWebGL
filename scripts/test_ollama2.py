import http.client, json

conn = http.client.HTTPConnection("localhost", 11434, timeout=60)

# Simulate what Claude Code actually sends - with system prompt, many tools
payload = json.dumps({
    "model": "qwen3.5-35b-claude",
    "max_tokens": 16384,
    "stream": True,
    "system": [{"type": "text", "text": "You are Claude Code, a coding assistant."}],
    "messages": [{"role": "user", "content": "respond OK"}],
    "tools": [
        {
            "name": f"tool_{i}",
            "description": f"Tool {i}",
            "input_schema": {
                "type": "object",
                "properties": {"x": {"type": "string"}},
            },
        }
        for i in range(20)
    ],
})

print(f"Payload size: {len(payload)} bytes")
conn.request(
    "POST",
    "/v1/messages",
    body=payload,
    headers={
        "Content-Type": "application/json",
        "x-api-key": "ollama",
        "anthropic-version": "2023-06-01",
    },
)
resp = conn.getresponse()
print(f"Status: {resp.status}")
body = resp.read(2048).decode()
if resp.status != 200:
    print(f"Error: {body[:500]}")
else:
    print(f"OK: {body[:300]}")
conn.close()
