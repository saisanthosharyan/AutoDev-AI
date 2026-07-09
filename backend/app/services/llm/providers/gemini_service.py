import asyncio

from google import genai
from pydantic import BaseModel

from app.core.config import settings
from app.services.llm.base import BaseLLMService
from app.utils.retry import retry


class GeminiService(BaseLLMService):
    """
    Service for interacting with Google's Gemini models.
    """

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = settings.GEMINI_MODEL

    @retry(max_retries=3, delay=2)
    async def generate(self, prompt: str) -> str:
        """
        Generate plain text response.
        """

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
            )

            return response.text or ""

        except Exception as e:
            raise Exception(f"Gemini Error: {e}")

    @retry(max_retries=3, delay=2)
    async def chat(self, messages: list) -> str:
        """
        Generate response using conversation history.
        """

        try:
            prompt = "\n".join(
                f"{message.get('role', 'user').upper()}: {message.get('content', '')}"
                for message in messages
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
            )

            return response.text or ""

        except Exception as e:
            raise Exception(f"Gemini Error: {e}")

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
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": schema,
                },
            )

            return schema.model_validate_json(response.text)

        except Exception as e:
            raise Exception(f"Gemini Structured Error: {e}")