from app.core.config import settings
from app.services.llm.providers.openai_service import OpenAIService
from app.services.llm.providers.gemini_service import GeminiService


class LLMRouter:

    _llm = None

    @staticmethod
    def get_llm():

        if LLMRouter._llm is not None:
            return LLMRouter._llm

        provider = settings.LLM_PROVIDER.lower()

        if provider == "openai":
            LLMRouter._llm = OpenAIService()

        elif provider == "gemini":
            LLMRouter._llm = GeminiService()

        else:
            raise ValueError(
                f"Unsupported LLM Provider: {provider}"
            )

        return LLMRouter._llm