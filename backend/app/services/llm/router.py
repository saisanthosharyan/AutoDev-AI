import asyncio

from app.core.logger import logger
from app.core.config import settings

from app.services.llm.providers.openai_service import OpenAIService
from app.services.llm.providers.gemini_service import GeminiService


class LLMRouter:
    """
    Automatically switches to another LLM if one fails.
    """

    _instances = {}

    # --------------------------------------------------

    @classmethod
    def _get_provider(cls, provider: str):

        provider = provider.lower()

        if provider in cls._instances:
            return cls._instances[provider]

        if provider == "gemini":
            cls._instances[provider] = GeminiService()

        elif provider == "openai":
            cls._instances[provider] = OpenAIService()

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        return cls._instances[provider]

    # --------------------------------------------------

    @classmethod
    def _providers(cls):

        providers = [
            p.strip().lower()
            for p in settings.LLM_PRIORITY.split(",")
            if p.strip()
        ]

        if not providers:
            providers = ["gemini"]

        return providers

    # --------------------------------------------------

    @classmethod
    def get_llm(cls):
        """
        Returns the highest-priority provider.
        """
        return cls._get_provider(cls._providers()[0])

    # --------------------------------------------------

    @classmethod
    def generate(cls, prompt: str):

        last_error = None

        for provider in cls._providers():

            try:

                logger.info(f"Trying {provider}...")

                llm = cls._get_provider(provider)

                return asyncio.run(
                    llm.generate(prompt)
                )

            except Exception as e:

                logger.warning(
                    f"{provider} failed: {e}"
                )

                last_error = e

        raise last_error

    # --------------------------------------------------

    @classmethod
    def chat(cls, messages: list):

        last_error = None

        for provider in cls._providers():

            try:

                logger.info(f"Trying {provider}...")

                llm = cls._get_provider(provider)

                return asyncio.run(
                    llm.chat(messages)
                )

            except Exception as e:

                logger.warning(
                    f"{provider} failed: {e}"
                )

                last_error = e

        raise last_error

    # --------------------------------------------------

    @classmethod
    def generate_structured(cls, prompt, schema):

        last_error = None

        for provider in cls._providers():

            try:

                logger.info(
                    f"Trying structured generation using {provider}..."
                )

                llm = cls._get_provider(provider)

                return asyncio.run(
                    llm.generate_structured(
                        prompt,
                        schema,
                    )
                )

            except Exception as e:

                logger.warning(
                    f"{provider} failed: {e}"
                )

                last_error = e

        raise last_error