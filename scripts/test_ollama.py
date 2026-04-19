import http.client, json

conn = http.client.HTTPConnection("localhost", 11434, timeout=120)
payload = json.dumps({
    "model": "qwen3.5-35b-claude",
    "max_tokens": 4096,
    "stream": True,
    "messages": [{"role": "user", "content": "say hello"}],
    "tools": [
        {
            "name": "Bash",
            "description": "Run a command",
            "input_schema": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        }
    ],
})
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
if resp.status != 200:
    print(f"Body: {resp.read().decode()[:500]}")
else:
    data = resp.read(4096).decode()
    print(f"Streaming OK\nFirst 500 chars:\n{data[:500]}")
conn.close()
