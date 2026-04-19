# -*- coding: utf-8 -*-
"""
Token Factory — 自主 Token 工厂

统一管理 LLM 推理资源的生命周期：
  1. SSH 隧道管理（连接远程 GPU 服务器上的 Ollama）
  2. Ollama / 云端 LLM 端点健康探测
  3. 模型可用性缓存与自动刷新
  4. 为 ChatHarness / Bridge Chat 提供 ensure_ready() 预检

用法：
    factory = TokenFactory.instance()
    await factory.ensure_ready()          # 启动前调用，确保推理可用
    status = await factory.health()       # 获取所有 provider 状态
    models = await factory.list_models()  # 列出 Ollama 模型
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import signal
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("TokenFactory")


# ─── Tunnel Config ────────────────────────────────────────────
@dataclass
class TunnelConfig:
    """SSH tunnel parameters."""
    local_port: int = 11434
    remote_port: int = 11434
    remote_host: str = "gpu11"
    jump_host: str = "root@111.186.43.30"
    ssh_key_path: str = ""           # path to private key file
    connect_timeout: int = 15
    alive_interval: int = 30


class TunnelState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"


# ─── Provider Health ──────────────────────────────────────────
@dataclass
class ProviderHealth:
    """Health snapshot for a single LLM provider."""
    name: str
    url: str
    reachable: bool = False
    latency_ms: float = 0.0
    models: List[str] = field(default_factory=list)
    error: str = ""
    checked_at: float = 0.0


# ─── Token Factory ───────────────────────────────────────────
class TokenFactory:
    """Autonomous Token Factory — 自主 Token 工厂.

    Singleton that manages:
    - SSH tunnel to remote Ollama
    - Health probing for all configured LLM providers
    - Model availability cache
    """

    _instance: Optional["TokenFactory"] = None

    def __init__(self):
        self._tunnel_config = TunnelConfig()
        self._tunnel_state = TunnelState.STOPPED
        self._tunnel_pid: Optional[int] = None
        self._provider_health: Dict[str, ProviderHealth] = {}
        self._ollama_models: List[Dict[str, Any]] = []
        self._last_health_check: float = 0.0
        self._health_ttl: float = 30.0  # cache health for 30s
        self._claude_code_health: Dict[str, Any] = {}  # cached Claude Code probe result
        self._lock = asyncio.Lock()
        self._load_tunnel_config()

    @classmethod
    def instance(cls) -> "TokenFactory":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── Config ────────────────────────────────────────────────

    def _load_tunnel_config(self):
        """Load tunnel config from config/settings.json if present."""
        base_dir = Path(__file__).parent.parent.parent
        settings_path = base_dir / "config" / "settings.json"
        if settings_path.exists():
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                tc = settings.get("token_factory", {}).get("tunnel", {})
                if tc:
                    self._tunnel_config.local_port = tc.get("local_port", self._tunnel_config.local_port)
                    self._tunnel_config.remote_port = tc.get("remote_port", self._tunnel_config.remote_port)
                    self._tunnel_config.remote_host = tc.get("remote_host", self._tunnel_config.remote_host)
                    self._tunnel_config.jump_host = tc.get("jump_host", self._tunnel_config.jump_host)
                    self._tunnel_config.ssh_key_path = tc.get("ssh_key_path", self._tunnel_config.ssh_key_path)
            except Exception as e:
                logger.debug("Failed to load tunnel config: %s", e)

    # ── SSH Tunnel ────────────────────────────────────────────

    def _find_tunnel_pid(self) -> Optional[int]:
        """Find existing SSH tunnel process."""
        try:
            result = subprocess.run(
                ["pgrep", "-f", f"ssh.*-L.*{self._tunnel_config.local_port}.*{self._tunnel_config.jump_host}"],
                capture_output=True, text=True, timeout=5
            )
            pids = result.stdout.strip().split("\n")
            return int(pids[0]) if pids[0] else None
        except Exception:
            return None

    def _sync_tunnel_state(self) -> bool:
        """Sync cached tunnel state with the actual SSH process list.

        Returns True when the observed state changed.
        """
        prev_state = self._tunnel_state
        prev_pid = self._tunnel_pid
        pid = self._find_tunnel_pid()
        if pid:
            self._tunnel_pid = pid
            self._tunnel_state = TunnelState.RUNNING
        else:
            self._tunnel_pid = None
            if self._tunnel_state != TunnelState.STARTING:
                self._tunnel_state = TunnelState.STOPPED
        return prev_state != self._tunnel_state or prev_pid != self._tunnel_pid

    def _invalidate_health_cache(self):
        """Force the next health request to re-probe providers."""
        self._last_health_check = 0.0

    async def start_tunnel(self) -> bool:
        """Start SSH tunnel to remote Ollama. Returns True if tunnel is up."""
        async with self._lock:
            # Already running?
            if self._sync_tunnel_state() or self._tunnel_pid:
                self._invalidate_health_cache()
            if self._tunnel_pid:
                logger.info("Tunnel already running (PID: %d)", self._tunnel_pid)
                return True

            self._tunnel_state = TunnelState.STARTING

            # Find the tunnel script
            base_dir = Path(__file__).parent.parent.parent
            tunnel_script = None
            # Check common locations
            for candidate in [
                Path.home() / "Downloads" / "tunnel-remote.sh",
                base_dir / "scripts" / "tunnel-remote.sh",
                base_dir / "tunnel-remote.sh",
            ]:
                if candidate.exists():
                    tunnel_script = candidate
                    break

            if tunnel_script:
                return await self._start_via_script(tunnel_script)
            else:
                return await self._start_via_ssh()

    async def _start_via_script(self, script_path: Path) -> bool:
        """Start tunnel using the shell script."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "bash", str(script_path), "start",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
            output = ((stdout or b"") + (stderr or b"")).decode()
            if "成功" in output or "已在运行" in output or "已成功建立" in output:
                self._sync_tunnel_state()
                self._invalidate_health_cache()
                logger.info("Tunnel started via script (PID: %s)", self._tunnel_pid)
                return True
            else:
                self._tunnel_state = TunnelState.ERROR
                logger.warning("Tunnel script output: %s", output[:200])
                return False
        except Exception as e:
            self._tunnel_state = TunnelState.ERROR
            logger.error("Failed to start tunnel via script: %s", e)
            return False

    async def _start_via_ssh(self) -> bool:
        """Start tunnel directly via ssh command."""
        tc = self._tunnel_config
        if not tc.ssh_key_path or not Path(tc.ssh_key_path).exists():
            self._tunnel_state = TunnelState.ERROR
            logger.warning("No SSH key configured for tunnel")
            return False

        cmd = [
            "ssh",
            "-i", tc.ssh_key_path,
            "-o", f"ConnectTimeout={tc.connect_timeout}",
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", f"ServerAliveInterval={tc.alive_interval}",
            "-o", "ExitOnForwardFailure=yes",
            "-L", f"{tc.local_port}:{tc.remote_host}:{tc.remote_port}",
            tc.jump_host,
            "-N", "-f",
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.communicate(), timeout=20)
            await asyncio.sleep(1)
            self._sync_tunnel_state()
            if self._tunnel_pid:
                self._invalidate_health_cache()
                logger.info("Tunnel started via SSH (PID: %d)", self._tunnel_pid)
                return True
            self._tunnel_state = TunnelState.ERROR
            return False
        except Exception as e:
            self._tunnel_state = TunnelState.ERROR
            logger.error("SSH tunnel start failed: %s", e)
            return False

    async def stop_tunnel(self):
        """Stop the SSH tunnel."""
        pid = self._find_tunnel_pid()
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                logger.info("Tunnel stopped (PID: %d)", pid)
            except ProcessLookupError:
                pass
        self._tunnel_pid = None
        self._tunnel_state = TunnelState.STOPPED
        self._invalidate_health_cache()

    # ── Health Probing ────────────────────────────────────────

    async def _probe_endpoint(self, name: str, url: str, path: str = "/models") -> ProviderHealth:
        """Probe a single LLM endpoint."""
        import aiohttp
        health = ProviderHealth(name=name, url=url, checked_at=time.time())
        try:
            t0 = time.monotonic()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url.rstrip("/") + path,
                    timeout=aiohttp.ClientTimeout(total=8),
                ) as resp:
                    health.latency_ms = round((time.monotonic() - t0) * 1000, 1)
                    if resp.status == 200:
                        health.reachable = True
                        try:
                            data = await resp.json()
                            # Ollama format
                            if "models" in data:
                                health.models = [m["name"] for m in data["models"]]
                            # OpenAI format
                            elif "data" in data:
                                health.models = [m["id"] for m in data["data"]]
                        except Exception:
                            pass
                    else:
                        health.error = f"HTTP {resp.status}"
        except Exception as e:
            health.error = str(e)[:120]
        return health

    async def health(self, force: bool = False) -> Dict[str, Any]:
        """Get health status of all providers."""
        now = time.time()
        if self._sync_tunnel_state():
            force = True
        if not force and (now - self._last_health_check) < self._health_ttl:
            return self._format_health()

        # Probe in parallel
        probes = [
            self._probe_endpoint("ollama_local", "http://127.0.0.1:11434", "/api/tags"),
            self._probe_endpoint("deepseek", "https://api.deepseek.com/v1", "/models"),
        ]

        # Add qwen if configured
        results = await asyncio.gather(*probes, return_exceptions=True)
        for r in results:
            if isinstance(r, ProviderHealth):
                self._provider_health[r.name] = r
                if r.name == "ollama_local" and r.reachable:
                    self._ollama_models = [{"name": m} for m in r.models]

        self._last_health_check = now
        return self._format_health()

    def _format_health(self) -> Dict[str, Any]:
        tunnel_info = {
            "state": self._tunnel_state.value,
            "pid": self._tunnel_pid,
            "config": {
                "local_port": self._tunnel_config.local_port,
                "remote_host": self._tunnel_config.remote_host,
                "jump_host": self._tunnel_config.jump_host,
            },
        }
        providers = {}
        for name, h in self._provider_health.items():
            providers[name] = {
                "reachable": h.reachable,
                "latency_ms": h.latency_ms,
                "models": h.models,
                "error": h.error,
                "checked_at": h.checked_at,
            }
        # Include cached Claude Code health (via DeepSeek)
        if self._claude_code_health:
            providers["claude_code"] = self._claude_code_health

        claude_ok = bool(self._claude_code_health and self._claude_code_health.get("ok"))
        return {
            "tunnel": tunnel_info,
            "providers": providers,
            "ollama_models": [m["name"] for m in self._ollama_models],
            "ready": any(p.reachable for p in self._provider_health.values()) or claude_ok,
        }

    async def _probe_claude_code(self, prompt: str = "hi") -> Dict[str, Any]:
        """Probe Claude Code CLI by running `claude -p --bare`.

        Tests the real Claude Code CLI → DeepSeek chain.
        Uses --bare to skip hooks/LSP/CLAUDE.md that can hang in subprocess.
        Result is cached in ``_claude_code_health``.
        """
        result: Dict[str, Any] = {
            "ok": False, "reply": "", "latency_ms": 0,
            "error": "", "model": "deepseek-chat", "checked_at": time.time(),
        }
        # Find claude binary
        claude_bin = shutil.which("claude")
        if not claude_bin:
            result["error"] = "claude CLI not found in PATH"
            self._claude_code_health = result
            return result

        # Build clean env from ~/.claude/settings.json
        probe_env = os.environ.copy()
        for k in list(probe_env.keys()):
            if k.startswith("ANTHROPIC_"):
                del probe_env[k]
        try:
            settings_path = Path.home() / ".claude" / "settings.json"
            if settings_path.exists():
                with open(settings_path, "r") as f:
                    settings = json.load(f)
                for k, v in settings.get("env", {}).items():
                    probe_env[k] = v
        except Exception:
            pass

        try:
            t0 = time.monotonic()
            proc = await asyncio.create_subprocess_exec(
                claude_bin, "-p", "--bare",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=probe_env,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=prompt.encode("utf-8")), timeout=15
            )
            latency = round((time.monotonic() - t0) * 1000, 1)
            result["latency_ms"] = latency
            reply = (stdout or b"").decode("utf-8", errors="replace").strip()
            err_text = (stderr or b"").decode("utf-8", errors="replace").strip()
            if reply:
                result["ok"] = True
                result["reply"] = reply[:2000]
            else:
                result["error"] = err_text[:300] or f"exit code {proc.returncode}"
        except asyncio.TimeoutError:
            result["error"] = "claude CLI timeout (60s)"
        except Exception as e:
            result["error"] = str(e)[:200]

        self._claude_code_health = result
        return result

    async def list_models(self) -> List[Dict[str, Any]]:
        """List available Ollama models."""
        h = self._provider_health.get("ollama_local")
        if not h or not h.reachable:
            await self.health(force=True)
        return self._ollama_models

    # ── ensure_ready — 启动前预检 ─────────────────────────────

    async def ensure_ready(self, start_tunnel: bool = True) -> Dict[str, Any]:
        """Ensure at least one LLM provider is reachable.

        1. Probe all endpoints
        2. If Ollama not reachable and start_tunnel=True, try starting SSH tunnel
        3. Re-probe after tunnel start
        4. Return health status
        """
        status = await self.health(force=True)
        if status["ready"]:
            logger.info("Token Factory ready: %s", [n for n, p in self._provider_health.items() if p.reachable])
            return status

        # Ollama not reachable — try tunnel
        if start_tunnel:
            logger.info("No LLM reachable, attempting SSH tunnel...")
            tunnel_ok = await self.start_tunnel()
            if tunnel_ok:
                await asyncio.sleep(2)
                status = await self.health(force=True)
                if status["ready"]:
                    logger.info("Token Factory ready after tunnel: %s",
                                [n for n, p in self._provider_health.items() if p.reachable])
                    return status

        # Try Claude Code via DeepSeek — send "hi" and check for response
        try:
            logger.info("Probing Claude Code via DeepSeek...")
            cc = await self._probe_claude_code()
            if cc.get("ok"):
                logger.info("Claude Code via DeepSeek is ready (reply: %s)", cc.get("reply", "")[:60])
                return self._format_health()
        except Exception as e:
            logger.debug("Claude Code probe failed: %s", e)

        logger.warning("Token Factory: no LLM provider reachable")
        return self._format_health()


# ── FastAPI Router ────────────────────────────────────────────

def register_token_factory_routes(app):
    """Register Token Factory API endpoints on the FastAPI app."""
    from fastapi import Request

    @app.get("/api/v1/token-factory/health")
    async def token_factory_health():
        """Get Token Factory health status."""
        factory = TokenFactory.instance()
        return await factory.health()

    @app.post("/api/v1/token-factory/ensure-ready")
    async def token_factory_ensure_ready():
        """Ensure LLM inference is available (starts tunnel if needed)."""
        factory = TokenFactory.instance()
        return await factory.ensure_ready()

    @app.get("/api/v1/token-factory/models")
    async def token_factory_models():
        """List available Ollama models."""
        factory = TokenFactory.instance()
        models = await factory.list_models()
        return {"models": models}

    @app.post("/api/v1/token-factory/tunnel/start")
    async def token_factory_tunnel_start():
        """Start SSH tunnel."""
        factory = TokenFactory.instance()
        ok = await factory.start_tunnel()
        return {"ok": ok, "state": factory._tunnel_state.value, "pid": factory._tunnel_pid}

    @app.post("/api/v1/token-factory/tunnel/stop")
    async def token_factory_tunnel_stop():
        """Stop SSH tunnel."""
        factory = TokenFactory.instance()
        await factory.stop_tunnel()
        return {"ok": True, "state": factory._tunnel_state.value}

    @app.get("/api/v1/token-factory/probe/ollama")
    async def token_factory_probe_ollama():
        """Probe Ollama endpoint and return raw HTTP response."""
        import aiohttp
        url = "http://127.0.0.1:11434"
        result = {"url": url, "reachable": False}
        try:
            t0 = time.monotonic()
            async with aiohttp.ClientSession() as session:
                # 1) Root endpoint
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                    latency = round((time.monotonic() - t0) * 1000, 1)
                    body = await resp.text()
                    result["root"] = {
                        "status": resp.status,
                        "body": body[:500],
                        "latency_ms": latency,
                    }
                    result["reachable"] = resp.status == 200
                # 2) /api/tags
                t1 = time.monotonic()
                async with session.get(url + "/api/tags", timeout=aiohttp.ClientTimeout(total=8)) as resp2:
                    latency2 = round((time.monotonic() - t1) * 1000, 1)
                    try:
                        data = await resp2.json()
                    except Exception:
                        data = await resp2.text()
                    models = []
                    if isinstance(data, dict) and "models" in data:
                        models = [m.get("name", "?") for m in data["models"]]
                    result["api_tags"] = {
                        "status": resp2.status,
                        "models": models,
                        "model_count": len(models),
                        "latency_ms": latency2,
                    }
        except Exception as e:
            result["error"] = str(e)[:200]
        return result

    @app.post("/api/v1/token-factory/probe/claude")
    async def token_factory_probe_claude(request: Request = None):
        """Test Claude Code CLI by running `claude -p <prompt>`.

        Invokes the real CLI binary to verify the full chain:
        claude CLI → DeepSeek API → response.
        """
        body = {}
        if request:
            try:
                body = await request.json()
            except Exception:
                pass
        prompt = body.get("prompt", "hi")

        factory = TokenFactory.instance()
        result = await factory._probe_claude_code(prompt=prompt)
        return result

    @app.get("/api/v1/token-factory/tunnel/status")
    async def token_factory_tunnel_status():
        """Get tunnel status."""
        factory = TokenFactory.instance()
        pid = factory._find_tunnel_pid()
        if pid:
            factory._tunnel_pid = pid
            factory._tunnel_state = TunnelState.RUNNING
        else:
            factory._tunnel_pid = None
            factory._tunnel_state = TunnelState.STOPPED
        return {
            "state": factory._tunnel_state.value,
            "pid": factory._tunnel_pid,
            "config": {
                "local_port": factory._tunnel_config.local_port,
                "remote_host": factory._tunnel_config.remote_host,
            },
        }

    logger.info("✅ Token Factory API 端点注册成功")
