from app.core.ai.base import BaseAIProvider
from app.core.ai.providers.gemini import GeminiProvider
from app.core.ai.providers.openai import OpenAIProvider
from app.core.config import settings
from app.modules.organizations.models import AIProviderType


def get_ai_provider_for_org(provider_type: AIProviderType) -> BaseAIProvider:
    """Instantiates provider with platform owner keys based on tenant subscription."""
    if provider_type == AIProviderType.GEMINI_FLASH:
        return GeminiProvider(api_key=settings.PLATFORM_GEMINI_API_KEY, model_name="gemini-1.5-flash")
    elif provider_type == AIProviderType.GEMINI_PRO:
        return GeminiProvider(api_key=settings.PLATFORM_GEMINI_API_KEY, model_name="gemini-1.5-pro")
    elif provider_type == AIProviderType.OPENAI_MINI:
        return OpenAIProvider(api_key=settings.PLATFORM_OPENAI_API_KEY, model_name="gpt-4o-mini")
    elif provider_type == AIProviderType.OPENAI_GPT4O:
        return OpenAIProvider(api_key=settings.PLATFORM_OPENAI_API_KEY, model_name="gpt-4o")

    # Default fallback
    return GeminiProvider(api_key=settings.PLATFORM_GEMINI_API_KEY, model_name="gemini-1.5-flash")