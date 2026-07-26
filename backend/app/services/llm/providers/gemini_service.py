import asyncio
import json

from google import genai
from pydantic import BaseModel

from app.core.config import settings
from app.core.logger import logger
from app.services.llm.base import BaseLLMService
from app.utils.retry import retry


class GeminiQuotaError(RuntimeError):
    """Raised when Gemini API quota is exhausted."""

    pass


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
    # Internal Helpers
    # --------------------------------------------------------

    def _extract_text(self, response) -> str:
        """
        Safely extract text from Gemini response.
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

    def _handle_error(self, error: Exception, operation: str):
        """
        Convert Gemini errors into meaningful application errors.
        """

        error_text = str(error)

        # Gemini quota / rate limit
        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "quota" in error_text.lower()
        ):

            logger.error(
                f"Gemini quota exhausted during {operation}."
            )

            raise GeminiQuotaError(
                "Gemini API quota has been exhausted. "
                "Please wait for the quota to reset or configure "
                "another LLM provider."
            ) from error

        logger.exception(
            f"Gemini {operation} failed."
        )

        raise RuntimeError(
            f"Gemini {operation} failed: {error}"
        ) from error

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

        except GeminiQuotaError:
            raise

        except Exception as e:

            self._handle_error(
                e,
                "text generation"
            )

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
                f"{m.get('role', 'user').upper()}: "
                f"{m.get('content', '')}"
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

        except GeminiQuotaError:
            raise

        except Exception as e:

            self._handle_error(
                e,
                "chat"
            )

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
                f"Generating structured response using Gemini "
                f"({self.model})..."
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

        except GeminiQuotaError:
            raise

        except Exception as e:

            self._handle_error(
                e,
                "structured generation"
            )