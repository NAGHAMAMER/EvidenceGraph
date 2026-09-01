from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


class LLMConfigurationError(RuntimeError):
    """Raised when the configured LLM cannot be initialized."""


@lru_cache
def get_chat_model() -> ChatGoogleGenerativeAI:
    provider = settings.llm_provider.strip().lower()

    if provider != "google":
        raise LLMConfigurationError(
            f"Unsupported LLM provider: {provider or 'empty'}."
        )

    if not settings.llm_model.strip():
        raise LLMConfigurationError(
            "LLM_MODEL is not configured."
        )

    if not settings.llm_api_key.strip():
        raise LLMConfigurationError(
            "LLM_API_KEY is not configured."
        )

    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        temperature=1.0,
        timeout=settings.llm_timeout_seconds,
        max_retries=2,
    )
