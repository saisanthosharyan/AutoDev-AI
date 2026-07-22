from app.services.llm.router import LLMRouter
from app.agents.base_agent import BaseAgent
from app.models.task import Task
from app.core.logger import logger


class CoderAgent(BaseAgent):

    async def run(self, task: Task):

        llm = LLMRouter.get_llm()

        steps = "\n".join(
            f"- {step}" for step in task.steps
        )

        prompt = f"""
You are AutoDev AI, an expert senior software engineer capable of building complete production-ready software projects.

=========================
PROJECT INFORMATION
=========================

Title:
{task.title}

Description:
{task.description}

Implementation Steps:
{steps}

=========================
YOUR RESPONSIBILITIES
=========================

Determine the most appropriate:

- Programming language
- Framework
- Database
- Folder structure
- Architecture
- Dependencies

Use modern best practices.

=========================
PROJECT REQUIREMENTS
=========================

Generate a COMPLETE project.

Include every required file.

Examples include:

README.md
requirements.txt OR package.json
.gitignore
.env.example
Dockerfile
docker-compose.yml (if needed)

Configuration files

Source code

Tests

Assets

Documentation

Generate a complete folder structure.

=========================
CODE QUALITY
=========================

Every file must:

- Be production ready
- Use clean architecture
- Use proper naming
- Include type hints where applicable
- Include docstrings
- Handle exceptions
- Use logging when appropriate
- Follow SOLID principles
- Follow DRY principles

Never generate placeholder code.

Never generate TODO.

Never generate FIXME.

Never generate pseudo code.

Never skip implementations.

=========================
TESTING
=========================

Generate tests.

Tests should be executable.

Generate unit tests.

Generate integration tests when appropriate.

=========================
README
=========================

README must include:

Project Overview

Features

Installation

Usage

Folder Structure

Environment Variables

Dependencies

How to Run

How to Test

License

=========================
OUTPUT FORMAT
=========================

Return ONLY files.

Every file MUST begin exactly like:

FILE: path/to/file.ext

<content>

Example:

FILE: app/main.py

print("Hello")

FILE: requirements.txt

fastapi
uvicorn

Rules:

Do NOT use markdown.

Do NOT use ```.

Do NOT explain anything.

Do NOT add comments outside files.

Begin immediately with the first FILE:.

Never output anything except project files.
"""

        logger.info("Generating project source code...")

        response = await llm.generate(prompt)

        logger.info(f"Coder generated {len(response)} characters.")

        return response