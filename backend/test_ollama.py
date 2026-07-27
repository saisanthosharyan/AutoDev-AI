import asyncio

from ollama import AsyncClient


async def main():

    print("Testing Ollama...")

    client = AsyncClient(
        host="http://localhost:11434"
    )

    response = await client.chat(
        model="qwen2.5-coder:7b",
        messages=[
            {
                "role": "user",
                "content": "Write one sentence saying hello from AutoDev AI."
            }
        ],
    )

    print("\nSUCCESS!")
    print(response.message.content)


if __name__ == "__main__":
    asyncio.run(main())