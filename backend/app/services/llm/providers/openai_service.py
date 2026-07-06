from openai import AsyncOpenAI

from app.core.config import settings
from app.services.llm.base import BaseLLMService


class OpenAIService(BaseLLMService):
    """
    Service for interacting with OpenAI models.
    """

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        )

        self.model = settings.OPENAI_MODEL

    async def generate(self, prompt: str) -> str:
        """
        Generate a response from a single prompt.
        """

        response = await self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text

    async def chat(self, messages: list) -> str:
        """
        Generate a response from a conversation.
        """

        response = await self.client.responses.create(
            model=self.model,
            input=messages,
        )

        return response.output_text