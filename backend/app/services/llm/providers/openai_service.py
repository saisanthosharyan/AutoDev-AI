from openai import AsyncOpenAI
from pydantic import BaseModel

from app.core.config import settings
from app.services.llm.base import BaseLLMService
from app.utils.retry import retry


class OpenAIService(BaseLLMService):
    """
    Service for interacting with OpenAI models.
    """

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        )
        self.model = settings.OPENAI_MODEL

    @retry(max_retries=3, delay=2)
    async def generate(self, prompt: str) -> str:
        """
        Generate plain text.
        """
        try:
            response = await self.client.responses.create(
                model=self.model,
                input=prompt,
            )

            return response.output_text

        except Exception as e:
            raise Exception(f"OpenAI Error: {e}")

    @retry(max_retries=3, delay=2)
    async def chat(self, messages: list) -> str:
        """
        Generate chat response.
        """
        try:
            response = await self.client.responses.create(
                model=self.model,
                input=messages,
            )

            return response.output_text

        except Exception as e:
            raise Exception(f"OpenAI Error: {e}")

    @retry(max_retries=3, delay=2)
    async def generate_structured(
        self,
        prompt: str,
        schema: BaseModel
    ):
        """
        Generate structured JSON using Pydantic schema.
        """
        try:
            response = await self.client.responses.parse(
                model=self.model,
                input=prompt,
                text_format=schema,
            )

            return response.output_parsed

        except Exception as e:
            raise Exception(f"OpenAI Structured Error: {e}")