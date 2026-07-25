import asyncio

from google import genai
from pydantic import BaseModel

from app.core.config import settings
from app.core.logger import logger
from app.services.llm.base import BaseLLMService
from app.utils.retry import retry


class GeminiService(BaseLLMService):
    """
    Gemini LLM Service
    """

    def __init__(self):

        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = settings.GEMINI_MODEL

        logger.info(
            f"Initialized GeminiService with model: {self.model}"
        )

    # --------------------------------------------------------
    # Internal Helper
    # --------------------------------------------------------

    def _extract_text(self, response) -> str:
        """
        Extract text safely from Gemini response.
        """

        try:

            if getattr(response, "text", None):
                return response.text.strip()

        except Exception:
            pass

        try:

            if getattr(response, "candidates", None):

                texts = []

                for candidate in response.candidates:

                    content = getattr(candidate, "content", None)

                    if content is None:
                        continue

                    parts = getattr(content, "parts", [])

                    for part in parts:

                        text = getattr(part, "text", None)

                        if text:
                            texts.append(text)

                if texts:
                    return "\n".join(texts).strip()

        except Exception:

            logger.exception(
                "Failed extracting candidate text."
            )

        return ""

    # --------------------------------------------------------
    # TEXT GENERATION
    # --------------------------------------------------------

    @retry(max_retries=3, delay=2)
    async def generate(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        try:

            logger.info(
                f"Generating response using Gemini ({self.model})..."
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
            )

            logger.debug(response)

            text = self._extract_text(response)

            if not text:

                logger.error(
                    f"Raw Gemini Response:\n{response}"
                )

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            logger.info(
                "Gemini text generation completed successfully."
            )

            return text

        except Exception as e:

            logger.exception(
                "Gemini text generation failed."
            )

            raise RuntimeError(
                f"Gemini request failed: {e}"
            ) from e

    # --------------------------------------------------------
    # CHAT
    # --------------------------------------------------------

    @retry(max_retries=3, delay=2)
    async def chat(self, messages: list) -> str:
        if not messages:
            raise ValueError("Messages cannot be empty.")

        try:

            logger.info(
                f"Generating chat using Gemini ({self.model})..."
            )

            prompt = "\n".join(
                f"{m.get('role','user').upper()}: {m.get('content','')}"
                for m in messages
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
            )

            text = self._extract_text(response)

            if not text:

                logger.error(
                    f"Raw Gemini Response:\n{response}"
                )

                raise RuntimeError(
                    "Gemini returned an empty chat response."
                )

            logger.info(
                "Gemini chat completed successfully."
            )

            return text

        except Exception as e:

            logger.exception(
                "Gemini chat failed."
            )

            raise RuntimeError(
                f"Gemini chat failed: {e}"
            ) from e

    # --------------------------------------------------------
    # STRUCTURED OUTPUT
    # --------------------------------------------------------

    @retry(max_retries=3, delay=2)
    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
    ):
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

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

            text = self._extract_text(response)

            if not text:

                logger.error(
                    f"Raw Gemini Response:\n{response}"
                )

                raise RuntimeError(
                    "Gemini returned an empty structured response."
                )

            parsed = schema.model_validate_json(text)

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