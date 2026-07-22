import asyncio

from google import genai
from pydantic import BaseModel

from app.core.config import settings
from app.core.logger import logger

from app.services.llm.base import BaseLLMService
from app.utils.retry import retry


class GeminiService(BaseLLMService):
    """
    Service for interacting with Google's Gemini models.
    """

    def __init__(self):

        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = settings.GEMINI_MODEL

        logger.info(
            f"Initialized GeminiService with model: {self.model}"
        )

    # --------------------------------------------------
    # Generate Text
    # --------------------------------------------------

    @retry(max_retries=3, delay=2)
    async def generate(self, prompt: str) -> str:
        """
        Generate plain text response.
        """

        try:

            logger.info(
                f"Generating response using Gemini ({self.model})..."
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
            )

            if not response.text:

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            logger.info(
                "Gemini text generation completed successfully."
            )

            return response.text

        except Exception as e:

            logger.exception(
                "Gemini text generation failed."
            )

            raise RuntimeError(
                f"Gemini request failed: {e}"
            ) from e

    # --------------------------------------------------
    # Chat
    # --------------------------------------------------

    @retry(max_retries=3, delay=2)
    async def chat(self, messages: list) -> str:
        """
        Generate a response using conversation history.
        """

        try:

            logger.info(
                f"Generating chat response using Gemini ({self.model})..."
            )

            prompt = "\n".join(
                f"{message.get('role', 'user').upper()}: "
                f"{message.get('content', '')}"
                for message in messages
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
            )

            if not response.text:

                raise RuntimeError(
                    "Gemini returned an empty chat response."
                )

            logger.info(
                "Gemini chat completed successfully."
            )

            return response.text

        except Exception as e:

            logger.exception(
                "Gemini chat request failed."
            )

            raise RuntimeError(
                f"Gemini chat failed: {e}"
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
                f"Generating structured response using Gemini ({self.model})..."
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": schema,
                },
            )

            if not response.text:

                raise RuntimeError(
                    "Gemini returned an empty structured response."
                )

            parsed = schema.model_validate_json(
                response.text
            )

            logger.info(
                "Gemini structured generation completed successfully."
            )

            return parsed

        except Exception as e:

            logger.exception(
                "Gemini structured generation failed."
            )

            raise RuntimeError(
                f"Gemini structured request failed: {e}"
            ) from e