"""Proxy to intercept Claude Code requests and see what it sends."""
import http.server
import http.client
import json
import sys
import threading


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""

        print(f"\n{'='*60}")
        print(f"[PROXY] {self.command} {self.path}")
        print(f"[PROXY] Headers:")
        for k, v in self.headers.items():
            if k.lower() not in ("host", "user-agent", "accept-encoding"):
                print(f"  {k}: {v}")

        try:
            data = json.loads(body)
            # Print key fields, skip large content
            interesting = {}
            for k, v in data.items():
                if k == "messages":
                    interesting["messages"] = f"[{len(v)} messages]"
                elif k == "tools":
                    interesting["tools"] = f"[{len(v)} tools: {', '.join(t['name'] for t in v[:5])}...]"
                elif k == "system":
                    if isinstance(v, list):
                        interesting["system"] = f"[{len(v)} blocks, {sum(len(json.dumps(b)) for b in v)} bytes]"
                    else:
                        interesting["system"] = f"[{len(str(v))} chars]"
                else:
                    interesting[k] = v
            print(f"[PROXY] Body keys: {json.dumps(interesting, indent=2, default=str)}")
        except Exception:
            print(f"[PROXY] Body ({len(body)} bytes): {body[:200]}")

        # Forward to Ollama
        conn = http.client.HTTPConnection("localhost", 11434, timeout=120)
        fwd_headers = {}
        for k, v in self.headers.items():
            if k.lower() not in ("host", "transfer-encoding"):
                fwd_headers[k] = v
        conn.request(self.command, self.path, body=body, headers=fwd_headers)
        resp = conn.getresponse()

        print(f"[PROXY] Response: {resp.status}")

        self.send_response(resp.status)
        for k, v in resp.getheaders():
            if k.lower() not in ("transfer-encoding",):
                self.send_header(k, v)
        self.end_headers()

        # Stream response back
        while True:
            chunk = resp.read(4096)
            if not chunk:
                break
            self.wfile.write(chunk)
        conn.close()

    def log_message(self, format, *args):
        pass  # Suppress default logging


def main():
    port = 11435
    server = http.server.HTTPServer(("0.0.0.0", port), ProxyHandler)
    print(f"Proxy listening on :{port} -> Ollama :11434")
    print(f"Set ANTHROPIC_BASE_URL=http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
