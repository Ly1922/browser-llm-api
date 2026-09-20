"""Start the local Browser LLM API when needed, then serve its stdio MCP.

This launcher is intentionally shell-free: Codex invokes the repository's
virtual-environment Python directly, and the API subprocess is started with an
explicit executable and argument list.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request


ROOT = Path(__file__).resolve().parent
API_BASE = "http://127.0.0.1:8081"


def api_ready() -> bool:
    try:
        with urllib.request.urlopen(f"{API_BASE}/api/status", timeout=2) as response:
            return bool(json.load(response).get("ok"))
    except Exception:
        return False


def start_api() -> None:
    logs = ROOT / "logs"
    logs.mkdir(exist_ok=True)

    env = os.environ.copy()
    env.setdefault("DEFAULT_PROVIDER", "chatgpt-browser")
    env.setdefault("GEMINI_IMAGE_DIR", str(ROOT / "generated-images"))
    env.setdefault("GEMINI_PUBLIC_URL", API_BASE)

    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    with (logs / "server.stdout.log").open("ab") as stdout_log, (
        logs / "server.stderr.log"
    ).open("ab") as stderr_log:
        subprocess.Popen(
            [sys.executable, str(ROOT / "server.py")],
            cwd=ROOT,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stdout_log,
            stderr=stderr_log,
            creationflags=flags,
        )

    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if api_ready():
            return
        time.sleep(0.5)
    raise RuntimeError(f"browser-llm API did not become ready at {API_BASE}")


def main() -> None:
    if not api_ready():
        start_api()

    os.environ.setdefault("BROWSER_LLM_API", API_BASE)
    os.environ.setdefault("BROWSER_LLM_MODEL", "chatgpt-browser")
    os.environ.setdefault("BROWSER_LLM_MCP_TIMEOUT", "440")

    import mcp_server

    mcp_server.main()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"browser-llm launcher failed: {exc}", file=sys.stderr, flush=True)
        raise
