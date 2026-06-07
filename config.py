"""
config.py — Centralised settings loaded from .env
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is missing. "
            "Check your .env file."
        )
    return value


# ── Required ──────────────────────────────────────────────────────────────────
GOOGLE_API_KEY: str = _require("GOOGLE_API_KEY")

# ── Optional LangSmith tracing ────────────────────────────────────────────────
LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_TRACING: bool = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "personal-board-of-directors-web")

# ── Model selection ───────────────────────────────────────────────────────────
# Set LLM_PROVIDER="openrouter" in .env to use OpenRouter/LLaMA instead of Gemini
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")

# OpenRouter settings (only used when LLM_PROVIDER="openrouter")
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL: str = os.getenv(
    "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
)
OPENROUTER_MODEL: str = os.getenv(
    "OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"
)

# Gemini model name
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ── Apply LangSmith env vars if tracing is enabled ────────────────────────────
if LANGSMITH_TRACING and LANGSMITH_API_KEY:
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT
