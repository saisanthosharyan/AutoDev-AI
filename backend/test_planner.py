import asyncio

from app.agents.planner import PlannerAgent


async def main():

    print("=" * 60)
    print("AUTODEV AI - PLANNER AGENT TEST")
    print("=" * 60)

    planner = PlannerAgent()

    request = """
Create a simple Python calculator CLI application.

It must support:
- addition
- subtraction
- multiplication
- division
- division by zero handling
- user-friendly command-line interaction
"""

    print()
    print("Sending request to Planner Agent...")
    print()

    try:

        plan = await planner.run(request)

        print("=" * 60)
        print("PLANNER RESULT")
        print("=" * 60)

        print(plan)

        print()
        print("=" * 60)
        print("RESULT TYPE")
        print("=" * 60)

        print(type(plan))

        print()
        print("=" * 60)
        print("PLANNER TEST PASSED")
        print("=" * 60)

    except Exception as e:

        print()
        print("=" * 60)
        print("PLANNER TEST FAILED")
        print("=" * 60)

        print(f"Error: {e}")

        raise


if __name__ == "__main__":
    asyncio.run(main())