from pathlib import Path

from app.agents.planner import PlannerAgent
from app.agents.coder import CoderAgent
from app.builders.project_builder import ProjectBuilder


async def main():

    print("=" * 60)
    print("AUTODEV AI - BUILD PIPELINE TEST")
    print("=" * 60)

    # --------------------------------------------------
    # STEP 1 - Planner
    # --------------------------------------------------

    print("\nSTEP 1 - Generating plan...")

    planner = PlannerAgent()

    task = await planner.run(
        "Create a simple Python CLI calculator with "
        "addition, subtraction, multiplication, division "
        "and division-by-zero handling."
    )

    print("\nPLAN:")
    print(task)

    # --------------------------------------------------
    # STEP 2 - Coder
    # --------------------------------------------------

    print("\nSTEP 2 - Generating project...")

    coder = CoderAgent()

    coder_output = await coder.run(task)

    print("\nCODER OUTPUT:")
    print(coder_output)

    # --------------------------------------------------
    # STEP 3 - Build
    # --------------------------------------------------

    print("\nSTEP 3 - Building project...")

    builder = ProjectBuilder()

    result = builder.build(
        project_name="python_cli_calculator",
        llm_output=coder_output,
    )

    print("\nBUILD RESULT")
    print("=" * 60)

    print("Project path:")
    print(result["project_path"])

    print("\nZIP path:")
    print(result["zip_path"])

    print("\nFiles:")
    for file in result["files"]:
        print(" -", file)

    print("\nFile count:")
    print(result["file_count"])

    print("\nBUILD SUCCESS")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())