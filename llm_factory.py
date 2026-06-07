"""
llm_factory.py — Builds the LLM client based on config settings.

Supports:
  • Google Gemini 2.5 Flash  (default, LLM_PROVIDER=gemini)
  • OpenRouter / LLaMA-3.3-70B  (LLM_PROVIDER=openrouter)
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
    """Return a configured LangChain chat model based on LLM_PROVIDER."""

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
