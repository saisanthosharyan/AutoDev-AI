from google import genai

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
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text

    async def chat(self, messages: list) -> str:
        prompt = ""

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            prompt += f"{role.upper()}: {content}\n"

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text