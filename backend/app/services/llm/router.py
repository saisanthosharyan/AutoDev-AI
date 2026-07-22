from app.core.config import settings
from app.core.logger import logger

from app.services.llm.providers.openai_service import OpenAIService
from app.services.llm.providers.gemini_service import GeminiService


class LLMRouter:
    """
    Returns the highest-priority available LLM provider.

    The router maintains singleton instances of providers to avoid
    recreating clients repeatedly.
    """

    _instances = {}

    # --------------------------------------------------
    # Provider Factory
    # --------------------------------------------------

    @classmethod
    def _get_provider(cls, provider: str):

        provider = provider.lower()

        if provider in cls._instances:
            return cls._instances[provider]

        logger.info(f"Initializing LLM provider: {provider}")

        if provider == "gemini":

            cls._instances[provider] = GeminiService()

        elif provider == "openai":

            cls._instances[provider] = OpenAIService()

        else:

            raise ValueError(
                f"Unsupported LLM provider: {provider}"
            )

        return cls._instances[provider]

    # --------------------------------------------------
    # Provider Priority
    # --------------------------------------------------

    @classmethod
    def _providers(cls):

        providers = []

        if getattr(settings, "LLM_PRIORITY", None):

            providers = [
                provider.strip().lower()
                for provider in settings.LLM_PRIORITY.split(",")
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
        Returns the highest-priority configured LLM provider.

        Example:

            llm = LLMRouter.get_llm()
            await llm.generate(...)
        """

        providers = cls._providers()

        logger.info(
            f"Selected LLM Provider: {providers[0]}"
        )

        return cls._get_provider(providers[0])