from abc import ABC, abstractmethod


class BaseLLMService(ABC):
    """
    Abstract base class for all LLM providers.
    Every provider (OpenAI, Gemini, Ollama, etc.)
    must implement these methods.
    """

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """
        Generate a response from a single prompt.
        """
        pass

    @abstractmethod
    async def chat(self, messages: list) -> str:
        """
        Generate a response from a conversation.
        """
        pass