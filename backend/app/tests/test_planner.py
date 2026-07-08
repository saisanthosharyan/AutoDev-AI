import asyncio

from app.agents.planner import PlannerAgent


async def main():

    planner = PlannerAgent()

    plan = await planner.run("Build a Todo App")

    print(plan)


if __name__ == "__main__":
    asyncio.run(main())