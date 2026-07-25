from abc import ABC, abstractmethod
from typing import Any, Type


class BaseLLMService(ABC):
    """
    Base interface for all LLM providers.

    Every provider (OpenAI, Gemini, Claude, Groq, Ollama, etc.)
    must implement these methods.
    """

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """
        Generate a text response from a prompt.
        """
        raise NotImplementedError

    @abstractmethod
    async def chat(self, messages: list[dict[str, str]]) -> str:
        """
        Generate a response from a chat conversation.
        """
        raise NotImplementedError

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Type[Any],
    ) -> Any:
        """
        Generate a structured response that matches
        the supplied Pydantic schema.
        """
        raise NotImplementedError