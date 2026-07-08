import asyncio

from google import genai
from pydantic import BaseModel

from app.core.config import settings
from app.services.llm.base import BaseLLMService


class GeminiService(BaseLLMService):
    """
    Service for interacting with Google's Gemini models.
    """

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )
        self.model = settings.GEMINI_MODEL

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

    async def chat(self, messages: list) -> str:
        """
        Generate a response using conversation history.
        """
        try:
            prompt = "\n".join(
                f"{msg.get('role', 'user').upper()}: {msg.get('content', '')}"
                for msg in messages
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
            )

            return response.text or ""

        except Exception as e:
            raise Exception(f"Gemini Error: {e}")

    async def generate_structured(
        self,
        prompt: str,
        schema: BaseModel
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