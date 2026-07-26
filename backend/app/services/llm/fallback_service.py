from typing import Any

from app.core.logger import logger
from app.services.llm.base import BaseLLMService


class FallbackLLMService(BaseLLMService):
    """
    LLM service that automatically falls back to the next
    configured provider when the current provider fails.
    """

    def __init__(self, providers: list[tuple[str, BaseLLMService]]):

        if not providers:
            raise ValueError(
                "At least one LLM provider is required."
            )

        self.providers = providers

        logger.info(
            "FallbackLLMService initialized with providers: "
            + ", ".join(name for name, _ in providers)
        )

    async def generate(self, prompt: str) -> str:

        last_error: Exception | None = None

        for name, provider in self.providers:

            try:

                logger.info(
                    f"Attempting text generation with provider: {name}"
                )

                result = await provider.generate(prompt)

                logger.info(
                    f"Provider {name} successfully generated response."
                )

                return result

            except Exception as e:

                last_error = e

                logger.warning(
                    f"Provider {name} failed: {e}"
                )

                continue

        logger.error(
            "All configured LLM providers failed."
        )

        raise RuntimeError(
            f"All configured LLM providers failed. "
            f"Last error: {last_error}"
        ) from last_error

    async def chat(self, messages: list[dict[str, str]]) -> str:

        last_error: Exception | None = None

        for name, provider in self.providers:

            try:

                logger.info(
                    f"Attempting chat with provider: {name}"
                )

                result = await provider.chat(messages)

                logger.info(
                    f"Provider {name} successfully handled chat."
                )

                return result

            except Exception as e:

                last_error = e

                logger.warning(
                    f"Provider {name} chat failed: {e}"
                )

                continue

        logger.error(
            "All configured LLM providers failed during chat."
        )

        raise RuntimeError(
            f"All configured LLM providers failed during chat. "
            f"Last error: {last_error}"
        ) from last_error

    async def generate_structured(
        self,
        prompt: str,
        schema: type[Any],
    ) -> Any:

        last_error: Exception | None = None

        for name, provider in self.providers:

            try:

                logger.info(
                    f"Attempting structured generation with provider: {name}"
                )

                result = await provider.generate_structured(
                    prompt,
                    schema,
                )

                logger.info(
                    f"Provider {name} successfully generated structured response."
                )

                return result

            except Exception as e:

                last_error = e

                logger.warning(
                    f"Provider {name} structured generation failed: {e}"
                )

                continue

        logger.error(
            "All configured LLM providers failed during structured generation."
        )

        raise RuntimeError(
            "All configured LLM providers failed during structured generation. "
            f"Last error: {last_error}"
        ) from last_error