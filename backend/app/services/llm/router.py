from app.core.config import settings
from app.core.logger import logger

from app.services.llm.providers.openai_service import OpenAIService
from app.services.llm.providers.gemini_service import GeminiService


class LLMRouter:
    """
    Singleton router for LLM providers.

    Selects the highest-priority configured provider and
    reuses provider instances for better performance.
    """

    _instances: dict[str, object] = {}

    # --------------------------------------------------
    # Provider Factory
    # --------------------------------------------------

    @classmethod
    def _get_provider(cls, provider: str):

        provider = provider.strip().lower()

        if provider in cls._instances:
            return cls._instances[provider]

        logger.info(f"Initializing LLM provider: {provider}")

        providers = {
            "gemini": GeminiService,
            "openai": OpenAIService,
        }

        provider_class = providers.get(provider)

        if provider_class is None:
            raise ValueError(
                f"Unsupported LLM provider: {provider}"
            )

        cls._instances[provider] = provider_class()

        return cls._instances[provider]

    # --------------------------------------------------
    # Provider Priority
    # --------------------------------------------------

    @classmethod
    def _providers(cls) -> list[str]:

        priority = getattr(settings, "LLM_PRIORITY", "")

        providers = [
            provider.strip().lower()
            for provider in priority.split(",")
            if provider.strip()
        ]

        if not providers:

            logger.warning(
                "LLM_PRIORITY not configured. Falling back to Gemini."
            )

            providers = ["gemini"]

        return providers

    # --------------------------------------------------
    # Public
    # --------------------------------------------------

    @classmethod
    def get_llm(cls):
        """
        Returns the highest-priority configured provider.
        """

        providers = cls._providers()

        logger.info(
            f"Selected LLM Provider: {providers[0]}"
        )

        return cls._get_provider(providers[0])