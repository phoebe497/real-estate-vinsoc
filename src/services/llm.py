from langchain_openai import ChatOpenAI

from src.config import get_settings


def get_llm(temperature: float | None = None) -> ChatOpenAI:
    """Return an OpenAI-compatible chat client.

    Supported by env only:
    - OpenRouter: LLM_PROVIDER=openrouter + OPENROUTER_API_KEY
    - OpenAI: LLM_PROVIDER=openai + OPENAI_API_KEY
    - Custom OpenAI-compatible gateway: LLM_PROVIDER=custom + LLM_BASE_URL/LLM_API_KEY/LLM_MODEL
    """
    settings = get_settings()
    temp = temperature if temperature is not None else settings.llm_temperature
    # Clamp temperature between 0.2 and 0.4 to prevent hallucinations and maintain safety boundaries
    temp = max(0.2, min(0.4, temp))

    return ChatOpenAI(
        model=settings.effective_llm_model,
        api_key=settings.effective_llm_api_key,
        base_url=settings.effective_llm_base_url,
        temperature=temp,
        timeout=30.0,  # Allow sufficient time for free-tier LLM API responses
        default_headers={
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
        },
    )
