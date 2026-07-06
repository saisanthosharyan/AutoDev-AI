from app.core.config import settings
from app.services.llm.providers.openai_service import OpenAIService
from app.services.llm.providers.gemini_service import GeminiService


class LLMRouter:
    """
    Returns the configured LLM provider.
    """

    @staticmethod
    def get_llm():
        provider = settings.LLM_PROVIDER.lower()

        if provider == "openai":
            return OpenAIService()

        elif provider == "gemini":
            return GeminiService()

        raise ValueError(
            f"Unsupported LLM Provider: {provider}"
        )