from app.agents.base_agent import BaseAgent
from app.core.logger import logger
from app.models.task import Task
from app.services.llm.router import LLMRouter


class CoderAgent(BaseAgent):
    """
    Generates a complete production-ready software project
    from the implementation plan.
    """

    async def run(
        self,
        task: Task,
    ) -> str:

        logger.info("=" * 60)
        logger.info("Coder Agent Started")
        logger.info("=" * 60)

        llm = LLMRouter.get_llm()

        steps = "\n".join(
            f"- {step}"
            for step in task.steps
        )

        prompt = f"""
You are AutoDev AI.

You are a Principal Software Engineer, Software Architect, DevOps Engineer,
QA Engineer, Security Engineer and Database Engineer.

Your responsibility is to generate a COMPLETE production-ready software project.

==================================================
PROJECT INFORMATION
==================================================

Title:
{task.title}

Description:
{task.description}

Implementation Steps:
{steps}

==================================================
YOUR RESPONSIBILITIES
==================================================

Determine the best:

• Programming language
• Framework
• Database
• Project architecture
• Folder structure
• Dependencies
• Configuration
• Testing framework

Choose modern technologies automatically.

==================================================
PROJECT REQUIREMENTS
==================================================

Generate a COMPLETE project.

Include every required file.

Examples:

README.md

.gitignore

.env.example

requirements.txt OR package.json

Dockerfile

docker-compose.yml (if required)

Configuration files

Database models

API routes

Frontend

Backend

Utilities

Assets

Tests

CI configuration (if appropriate)

Documentation

==================================================
CODE QUALITY
==================================================

Every generated file MUST:

- Compile successfully
- Execute successfully
- Contain production-ready code
- Follow SOLID principles
- Follow DRY principles
- Use meaningful names
- Include error handling
- Include logging where appropriate
- Use type hints when applicable
- Include docstrings where appropriate
- Avoid duplicate code

Never generate:

- TODO
- FIXME
- Placeholder code
- Pseudo code
- Empty implementations

==================================================
DEPENDENCIES
==================================================

Ensure:

- Every dependency is declared.
- Every import exists.
- No missing packages.
- No broken imports.
- No invalid references.

==================================================
TESTING
==================================================

Generate executable tests.

Include:

- Unit tests
- Integration tests (when appropriate)

The generated project should pass automated execution.

==================================================
README
==================================================

README must include:

Project Overview

Features

Installation

Usage

Folder Structure

Environment Variables

Dependencies

Running the Project

Running Tests

Deployment

License

==================================================
OUTPUT FORMAT
==================================================

Return ONLY project files.

Every file MUST begin exactly like this:

FILE: path/to/file.ext

<file contents>

Example:

FILE: app/main.py

print("Hello")

FILE: requirements.txt

fastapi
uvicorn

==================================================
RULES
==================================================

- Return ONLY project files.
- Do NOT use markdown.
- Do NOT use ``` fences.
- Do NOT explain anything.
- Do NOT summarize.
- Do NOT output comments outside files.
- Begin immediately with FILE:
- Every generated file must be included.
- The project must be executable without manual modifications.
"""

        logger.info("Generating production-ready project...")

        response = await llm.generate(prompt)

        logger.info(
            f"Generated {len(response)} characters of source code."
        )

        logger.info("=" * 60)
        logger.info("Coder Agent Finished")
        logger.info("=" * 60)

        return response