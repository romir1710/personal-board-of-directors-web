"""
llm_factory.py — Builds the LLM client based on config settings.

Supports (server default):
  • Google Gemini 2.5 Flash  (default, LLM_PROVIDER=gemini)
  • OpenRouter / LLaMA-3.3-70B  (LLM_PROVIDER=openrouter)

Per-request overrides (user-supplied API keys, Phase 2):
  • build_llm_for_request(provider, model, api_key, base_url)
    Providers: gemini | openai | anthropic | openrouter | custom
"""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel

from config import (
    GEMINI_MODEL,
    GOOGLE_API_KEY,
    LLM_PROVIDER,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
)


def build_llm(temperature: float = 0.7) -> BaseChatModel:
    """Return a configured LangChain chat model based on LLM_PROVIDER (server default)."""

    if LLM_PROVIDER == "openrouter":
        if not OPENROUTER_API_KEY:
            raise EnvironmentError(
                "LLM_PROVIDER is set to 'openrouter' but OPENROUTER_API_KEY is missing."
            )
        from langchain_openai import ChatOpenAI  # type: ignore

        return ChatOpenAI(
            model=OPENROUTER_MODEL,
            temperature=temperature,
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base=OPENROUTER_BASE_URL,
        )

    # Default → Google Gemini
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=temperature,
        google_api_key=GOOGLE_API_KEY,
    )


# ── Per-request LLM factory (Phase 2 — user-supplied API keys) ────────────────

_OPENROUTER_BASE = "https://openrouter.ai/api/v1"

def build_llm_for_request(
    provider: str,
    model: str,
    api_key: str,
    base_url: str | None = None,
    temperature: float = 0.7,
) -> BaseChatModel:
    """
    Build a one-off LangChain chat model from user-supplied credentials.

    Args:
        provider:    One of 'gemini', 'openai', 'anthropic', 'openrouter', 'custom'.
        model:       Model name string (e.g. 'gemini-2.5-flash', 'gpt-4o', etc.)
        api_key:     The user's secret API key — NEVER logged.
        base_url:    Required for 'openrouter' and 'custom'; ignored otherwise.
        temperature: Sampling temperature (default 0.7).
    """
    provider = (provider or "").lower().strip()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
        return ChatGoogleGenerativeAI(
            model=model or "gemini-2.5-flash",
            temperature=temperature,
            google_api_key=api_key,
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI  # type: ignore
        return ChatOpenAI(
            model=model or "gpt-4o",
            temperature=temperature,
            openai_api_key=api_key,
        )

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic  # type: ignore
        return ChatAnthropic(
            model=model or "claude-3-5-sonnet-20241022",
            temperature=temperature,
            anthropic_api_key=api_key,
        )

    if provider == "openrouter":
        from langchain_openai import ChatOpenAI  # type: ignore
        return ChatOpenAI(
            model=model or "openai/gpt-4o",
            temperature=temperature,
            openai_api_key=api_key,
            openai_api_base=base_url or _OPENROUTER_BASE,
        )

    if provider == "custom":
        if not base_url:
            raise ValueError("A 'base_url' is required for the 'custom' provider.")
        from langchain_openai import ChatOpenAI  # type: ignore
        return ChatOpenAI(
            model=model or "gpt-4o",
            temperature=temperature,
            openai_api_key=api_key,
            openai_api_base=base_url,
        )

    raise ValueError(
        f"Unknown provider '{provider}'. "
        "Must be one of: gemini, openai, anthropic, openrouter, custom."
    )
