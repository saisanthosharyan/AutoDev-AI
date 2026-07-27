import asyncio

from app.services.llm.router import LLMRouter


async def main():

    print("=" * 60)
    print("AUTODEV AI - LLM ROUTER TEST")
    print("=" * 60)

    llm = LLMRouter.get_llm()

    print(f"Service: {type(llm).__name__}")
    print()

    prompt = """
You are testing the local LLM used by AutoDev AI.

Reply with exactly:

OLLAMA ROUTER WORKING
"""

    print("Sending request to LLM...")
    print()

    response = await llm.generate(prompt)

    print("=" * 60)
    print("LLM RESPONSE")
    print("=" * 60)

    print(response)

    print("=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())