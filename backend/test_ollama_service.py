import asyncio

from app.services.llm.providers.ollama_service import OllamaService


async def main():

    service = OllamaService()

    response = await service.generate(
        "Write a Python function that adds two numbers."
    )

    print("=" * 60)
    print("OLLAMA SERVICE TEST")
    print("=" * 60)
    print(response)
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())