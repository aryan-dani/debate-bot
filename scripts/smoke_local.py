#!/usr/bin/env python3
"""Smoke checks for local Ollama path (no Groq key required).

Usage (backend must be running on :8000):
  python scripts/smoke_local.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.getenv("SMOKE_BASE", "http://127.0.0.1:8000")


def get(path: str) -> tuple[int, dict]:
    req = urllib.request.Request(f"{BASE}{path}", headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {"raw": body}
        return e.code, data


def main() -> int:
    print(f"Checking {BASE}/api/status …")
    code, status = get("/api/status")
    if code != 200:
        print(f"FAIL: /api/status returned {code}: {status}")
        return 1

    provider = status.get("provider")
    model = status.get("model")
    print(f"  provider={provider} model={model} ready={status.get('ready')} local={status.get('local')}")

    if provider != "ollama":
        print("FAIL: expected LLM_PROVIDER=ollama for the submission smoke test")
        return 1

    if not status.get("local"):
        print("FAIL: expected local=true for Ollama")
        return 1

    expected_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    if model != expected_model:
        print(f"WARN: model is {model!r}, env default is {expected_model!r}")

    if status.get("ready"):
        print("PASS: Ollama is ready — full practice flow can run without GROQ_API_KEY")
        return 0

    checklist = status.get("checklist") or []
    print("PASS (setup path): Ollama not ready, but checklist is present (no silent Groq):")
    for item in checklist:
        print(f"  - {item}")
    if not checklist:
        print("FAIL: ready=false but checklist empty")
        return 1
    detail = status.get("detail")
    if detail:
        print(f"  detail: {detail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
