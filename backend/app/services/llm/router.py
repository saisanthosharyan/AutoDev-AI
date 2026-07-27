from app.core.config import settings
from app.core.logger import logger

from app.services.llm.base import BaseLLMService
from app.services.llm.fallback_service import FallbackLLMService

from app.services.llm.providers.gemini_service import GeminiService
from app.services.llm.providers.openai_service import OpenAIService
from app.services.llm.providers.ollama_service import OllamaService


class LLMRouter:
    """
    LLM provider router with automatic fallback support.

    Providers are attempted in the order defined by LLM_PRIORITY.

    Example:

        LLM_PRIORITY=ollama,gemini,openai

    Priority:

        1. Ollama
        2. Gemini
        3. OpenAI

    If Ollama fails, Gemini is attempted.
    If Gemini fails, OpenAI is attempted.
    """

    _instances: dict[str, BaseLLMService] = {}

    # --------------------------------------------------
    # Provider Factory
    # --------------------------------------------------

    @classmethod
    def _get_provider(
        cls,
        provider: str,
    ) -> BaseLLMService:

        provider = provider.strip().lower()

        # Reuse already initialized provider
        if provider in cls._instances:

            logger.info(
                f"Reusing existing LLM provider: {provider}"
            )

            return cls._instances[provider]

        logger.info(
            f"Initializing LLM provider: {provider}"
        )

        # --------------------------------------------------
        # Supported Providers
        # --------------------------------------------------

        providers = {
            "ollama": OllamaService,
            "gemini": GeminiService,
            "openai": OpenAIService,
        }

        provider_class = providers.get(provider)

        if provider_class is None:

            raise ValueError(
                f"Unsupported LLM provider: {provider}"
            )

        # --------------------------------------------------
        # Initialize Provider
        # --------------------------------------------------

        instance = provider_class()

        cls._instances[provider] = instance

        logger.info(
            f"LLM provider initialized successfully: {provider}"
        )

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

        # --------------------------------------------------
        # Default Provider
        # --------------------------------------------------

        if not providers:

            logger.warning(
                "LLM_PRIORITY not configured. "
                "Falling back to Ollama."
            )

            providers = ["ollama"]

        return providers

    # --------------------------------------------------
    # Public
    # --------------------------------------------------

    @classmethod
    def get_llm(cls) -> BaseLLMService:
        """
        Return an LLM service with automatic fallback support.

        Provider order comes from:

            settings.LLM_PRIORITY

        Example:

            ollama,gemini,openai
        """

        provider_names = cls._providers()

        logger.info(
            "Configured LLM providers: "
            + ", ".join(provider_names)
        )

        providers: list[
            tuple[str, BaseLLMService]
        ] = []

        # --------------------------------------------------
        # Initialize Providers
        # --------------------------------------------------

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

                continue

        # --------------------------------------------------
        # No Providers Available
        # --------------------------------------------------

        if not providers:

            raise RuntimeError(
                "No configured LLM providers are available."
            )

        # --------------------------------------------------
        # Return Fallback Service
        # --------------------------------------------------

        logger.info(
            "Creating fallback LLM service with providers: "
            + ", ".join(
                name
                for name, _ in providers
            )
        )

        return FallbackLLMService(
            providers
        )