from openai import AsyncOpenAI
from pydantic import BaseModel

from app.core.config import settings
from app.core.logger import logger

from app.services.llm.base import BaseLLMService
from app.utils.retry import retry


class OpenAIService(BaseLLMService):
    """
    Service for interacting with OpenAI models.
    """

    def __init__(self):

        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        )

        self.model = settings.OPENAI_MODEL

        logger.info(
            f"Initialized OpenAIService with model: {self.model}"
        )

    # --------------------------------------------------
    # Generate Text
    # --------------------------------------------------

    @retry(max_retries=3, delay=2)
    async def generate(self, prompt: str) -> str:
        """
        Generate plain text.
        """

        try:

            logger.info(
                f"Generating response using OpenAI ({self.model})..."
            )

            response = await self.client.responses.create(
                model=self.model,
                input=prompt,
            )

            if not response.output_text:

                raise RuntimeError(
                    "OpenAI returned an empty response."
                )

            logger.info(
                "OpenAI text generation completed successfully."
            )

            return response.output_text

        except Exception as e:

            logger.exception(
                "OpenAI text generation failed."
            )

            raise RuntimeError(
                f"OpenAI request failed: {e}"
            ) from e

    # --------------------------------------------------
    # Chat
    # --------------------------------------------------

    @retry(max_retries=3, delay=2)
    async def chat(self, messages: list) -> str:
        """
        Generate chat response.
        """

        try:

            logger.info(
                f"Generating chat response using OpenAI ({self.model})..."
            )

            response = await self.client.responses.create(
                model=self.model,
                input=messages,
            )

            if not response.output_text:

                raise RuntimeError(
                    "OpenAI returned an empty chat response."
                )

            logger.info(
                "OpenAI chat completed successfully."
            )

            return response.output_text

        except Exception as e:

            logger.exception(
                "OpenAI chat request failed."
            )

            raise RuntimeError(
                f"OpenAI chat failed: {e}"
            ) from e

    # --------------------------------------------------
    # Structured Output
    # --------------------------------------------------

    @retry(max_retries=3, delay=2)
    async def generate_structured(
        self,
        prompt: str,
        schema: BaseModel,
    ):
        """
        Generate structured JSON using a Pydantic schema.
        """

        try:

            logger.info(
                f"Generating structured response using OpenAI ({self.model})..."
            )

            response = await self.client.responses.parse(
                model=self.model,
                input=prompt,
                text_format=schema,
            )

            if response.output_parsed is None:

                raise RuntimeError(
                    "Failed to parse structured response."
                )

            logger.info(
                "OpenAI structured generation completed successfully."
            )

            return response.output_parsed

        except Exception as e:

            logger.exception(
                "OpenAI structured generation failed."
            )

            raise RuntimeError(
                f"OpenAI structured request failed: {e}"
            ) from e