import json
from typing import Any

from ollama import AsyncClient

from app.core.config import settings
from app.core.logger import logger
from app.services.llm.base import BaseLLMService


class OllamaService(BaseLLMService):
    """
    Local LLM provider using Ollama.
    """

    def __init__(self):

        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

        self.client = AsyncClient(
            host=self.base_url
        )

        logger.info(
            f"Ollama service initialized: "
            f"{self.model} @ {self.base_url}"
        )

    # --------------------------------------------------
    # Generate
    # --------------------------------------------------

    async def generate(
        self,
        prompt: str,
    ) -> str:

        logger.info(
            f"Generating response using Ollama "
            f"({self.model})..."
        )

        try:

            response = await self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
            )

            result = response.response

            if not result:
                raise RuntimeError(
                    "Ollama returned an empty response."
                )

            logger.info(
                "Ollama text generation completed successfully."
            )

            return result

        except Exception as e:

            logger.exception(
                "Ollama text generation failed."
            )

            raise RuntimeError(
                f"Ollama request failed: {e}"
            ) from e

    # --------------------------------------------------
    # Chat
    # --------------------------------------------------

    async def chat(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        logger.info(
            f"Chat request using Ollama ({self.model})..."
        )

        try:

            response = await self.client.chat(
                model=self.model,
                messages=messages,
                stream=False,
            )

            result = response.message.content

            if not result:
                raise RuntimeError(
                    "Ollama returned an empty chat response."
                )

            logger.info(
                "Ollama chat completed successfully."
            )

            return result

        except Exception as e:

            logger.exception(
                "Ollama chat failed."
            )

            raise RuntimeError(
                f"Ollama chat request failed: {e}"
            ) from e

    # --------------------------------------------------
    # Structured Generation
    # --------------------------------------------------

    async def generate_structured(
        self,
        prompt: str,
        schema: type[Any],
    ) -> Any:

        logger.info(
            f"Generating structured response using Ollama "
            f"({self.model})..."
        )

        try:

            json_schema = schema.model_json_schema()

            structured_prompt = f"""
Return ONLY valid JSON matching the following schema.

JSON SCHEMA:

{json.dumps(json_schema, indent=2)}

USER REQUEST:

{prompt}

Do not add markdown.
Do not add explanations.
Do not add code fences.
Return only JSON.
"""

            response = await self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": structured_prompt,
                    }
                ],
                format=json_schema,
                stream=False,
                options={
                    "temperature": 0,
                },
            )

            content = response.message.content

            if not content:
                raise RuntimeError(
                    "Ollama returned empty structured response."
                )

            result = schema.model_validate_json(
                content
            )

            logger.info(
                "Ollama structured generation completed successfully."
            )

            return result

        except Exception as e:

            logger.exception(
                "Ollama structured generation failed."
            )

            raise RuntimeError(
                f"Ollama structured generation failed: {e}"
            ) from e