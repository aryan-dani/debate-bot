"""LLM provider abstraction: Ollama (default) and optional Groq fallback.

Never silently falls back from Ollama to Groq. Readiness is checked at
request time so the app can start without a running Ollama daemon.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv

# Load repo-root .env regardless of uvicorn cwd
_BACKEND_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _BACKEND_DIR.parent
load_dotenv(_REPO_ROOT / ".env")
load_dotenv(_BACKEND_DIR / ".env")

DEFAULT_OLLAMA_HOST = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "llama3.2:3b"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"

OLLAMA_CHECKLIST = [
    "Install Ollama from https://ollama.com",
    "Start the Ollama app (or run `ollama serve`)",
    "Pull the model: `ollama pull llama3.2:3b`",
    "Set LLM_PROVIDER=ollama in .env",
    "Set OLLAMA_HOST=http://127.0.0.1:11434 (default)",
    "Set OLLAMA_MODEL=llama3.2:3b (or llama3.2:1b on ~4GB RAM)",
]


class ProviderNotReadyError(Exception):
    """Raised when the configured LLM provider cannot serve requests."""

    def __init__(self, message: str, checklist: list[str] | None = None):
        super().__init__(message)
        self.message = message
        self.checklist = checklist or []


def get_provider_name() -> str:
    return os.getenv("LLM_PROVIDER", "ollama").strip().lower() or "ollama"


def get_model_name() -> str:
    provider = get_provider_name()
    if provider == "groq":
        return os.getenv("LLM_MODEL", DEFAULT_GROQ_MODEL)
    return os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)


def get_ollama_host() -> str:
    return os.getenv("OLLAMA_HOST", DEFAULT_OLLAMA_HOST).rstrip("/")


def is_local_provider() -> bool:
    return get_provider_name() == "ollama"


def _build_ollama_llm():
    from langchain_ollama import ChatOllama

    return ChatOllama(
        base_url=get_ollama_host(),
        model=get_model_name(),
        temperature=0.6,
    )


def _build_groq_llm():
    from langchain_groq import ChatGroq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key.startswith("your_"):
        raise ProviderNotReadyError(
            "GROQ_API_KEY is missing. Set it in .env, or switch to LLM_PROVIDER=ollama.",
            checklist=[
                "Get a key from https://console.groq.com",
                "Set GROQ_API_KEY in .env",
                "Set LLM_PROVIDER=groq",
                "Or use local mode: LLM_PROVIDER=ollama (no key needed)",
            ],
        )
    return ChatGroq(
        temperature=0.6,
        model=get_model_name(),
        api_key=api_key,
    )


def get_llm():
    """Return a LangChain chat model for the configured provider."""
    provider = get_provider_name()
    if provider == "groq":
        return _build_groq_llm()
    if provider == "ollama":
        return _build_ollama_llm()
    raise ProviderNotReadyError(
        f"Unknown LLM_PROVIDER={provider!r}. Use 'ollama' or 'groq'.",
        checklist=["Set LLM_PROVIDER=ollama (recommended) or LLM_PROVIDER=groq"],
    )


def _http_json(url: str, timeout: float = 3.0) -> Any:
    req = Request(url, headers={"Accept": "application/json"})
    with urlopen(req, timeout=timeout) as resp:
        import json

        return json.loads(resp.read().decode("utf-8"))


def check_ollama_ready() -> tuple[bool, list[str], str | None]:
    """Return (ready, checklist, detail). Checklist always listed for UI."""
    host = get_ollama_host()
    model = get_model_name()
    checklist = list(OLLAMA_CHECKLIST)
    try:
        data = _http_json(f"{host}/api/tags")
    except (URLError, TimeoutError, OSError) as exc:
        return False, checklist, f"Cannot reach Ollama at {host}: {exc}"

    models = data.get("models") or []
    names = [
        (m.get("name") or m.get("model") or "")
        for m in models
        if (m.get("name") or m.get("model"))
    ]

    def model_pulled(wanted: str, pulled: str) -> bool:
        if pulled == wanted:
            return True
        # llama3.2:3b matches llama3.2:3b-q4_K_M style tags
        if pulled.startswith(wanted + "-") or pulled.startswith(wanted + ":"):
            return True
        return False

    found = any(model_pulled(model, n) for n in names)
    if not found:
        return (
            False,
            checklist,
            f"Model {model!r} not found. Run: ollama pull {model}. Pulled: {names or '(none)'}",
        )
    return True, checklist, None


def get_status() -> dict[str, Any]:
    provider = get_provider_name()
    model = get_model_name()
    local = provider == "ollama"

    if provider == "ollama":
        ready, checklist, detail = check_ollama_ready()
        return {
            "provider": provider,
            "model": model,
            "local": local,
            "ready": ready,
            "checklist": checklist,
            "detail": detail,
            "host": get_ollama_host(),
        }

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        ready = bool(api_key and not api_key.startswith("your_"))
        checklist = [
            "Get a key from https://console.groq.com",
            "Set GROQ_API_KEY in .env",
            "Set LLM_PROVIDER=groq",
            "Optional: set LLM_MODEL (default llama-3.3-70b-versatile)",
        ]
        return {
            "provider": provider,
            "model": model,
            "local": False,
            "ready": ready,
            "checklist": checklist,
            "detail": None if ready else "GROQ_API_KEY is not set",
            "host": None,
        }

    return {
        "provider": provider,
        "model": model,
        "local": False,
        "ready": False,
        "checklist": ["Set LLM_PROVIDER=ollama or groq"],
        "detail": f"Unknown provider {provider!r}",
        "host": None,
    }


def ensure_ready() -> dict[str, Any]:
    """Raise ProviderNotReadyError if the active provider cannot run."""
    status = get_status()
    if not status["ready"]:
        raise ProviderNotReadyError(
            status.get("detail") or "LLM provider is not ready",
            checklist=status.get("checklist") or [],
        )
    return status


def invoke_llm(prompt: str) -> str:
    """Invoke the configured LLM and return text content."""
    ensure_ready()
    llm = get_llm()
    try:
        response = llm.invoke(prompt)
    except Exception as exc:
        # Surface Ollama connectivity failures as setup errors (never call Groq)
        if get_provider_name() == "ollama":
            raise ProviderNotReadyError(
                f"Ollama request failed: {exc}",
                checklist=OLLAMA_CHECKLIST,
            ) from exc
        raise
    content = response.content
    return str(content) if not isinstance(content, str) else content
