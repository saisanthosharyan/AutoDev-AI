from app.core.config import settings
from app.core.logger import logger

from app.services.llm.base import BaseLLMService
from app.services.llm.fallback_service import FallbackLLMService
from app.services.llm.providers.gemini_service import GeminiService
from app.services.llm.providers.openai_service import OpenAIService


class LLMRouter:
    """
    LLM provider router with automatic fallback support.

    Providers are attempted in the order defined by LLM_PRIORITY.
    """

    _instances: dict[str, BaseLLMService] = {}

    # --------------------------------------------------
    # Provider Factory
    # --------------------------------------------------

    @classmethod
    def _get_provider(cls, provider: str) -> BaseLLMService:

        provider = provider.strip().lower()

        if provider in cls._instances:
            return cls._instances[provider]

        logger.info(
            f"Initializing LLM provider: {provider}"
        )

        providers = {
            "gemini": GeminiService,
            "openai": OpenAIService,
        }

        provider_class = providers.get(provider)

        if provider_class is None:
            raise ValueError(
                f"Unsupported LLM provider: {provider}"
            )

        instance = provider_class()

        cls._instances[provider] = instance

        return instance

    # --------------------------------------------------
    # Provider Priority
    # --------------------------------------------------

    @classmethod
    def _providers(cls) -> list[str]:

        priority = getattr(
            settings,
            "LLM_PRIORITY",
            "",
        )

        providers = [
            provider.strip().lower()
            for provider in priority.split(",")
            if provider.strip()
        ]

        if not providers:

            logger.warning(
                "LLM_PRIORITY not configured. "
                "Falling back to Gemini."
            )

            providers = ["gemini"]

        return providers

    # --------------------------------------------------
    # Public
    # --------------------------------------------------

    @classmethod
    def get_llm(cls) -> BaseLLMService:
        """
        Return an LLM service with automatic fallback support.
        """

        provider_names = cls._providers()

        logger.info(
            "Configured LLM providers: "
            + ", ".join(provider_names)
        )

        providers: list[tuple[str, BaseLLMService]] = []

        for provider_name in provider_names:

            try:

                provider = cls._get_provider(
                    provider_name
                )

                providers.append(
                    (
                        provider_name,
                        provider,
                    )
                )

            except Exception as e:

                logger.warning(
                    f"Unable to initialize provider "
                    f"{provider_name}: {e}"
                )

        if not providers:

            raise RuntimeError(
                "No configured LLM providers are available."
            )

        return FallbackLLMService(providers)