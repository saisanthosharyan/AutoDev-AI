import json

from app.services.llm.router import LLMRouter
from app.agents.base_agent import BaseAgent
from app.core.logger import logger


class FixerAgent(BaseAgent):
    """
    AI agent responsible for repairing generated projects
    after execution failures.

    The agent receives:
        - Existing generated project
        - Code review
        - Execution/debug report

    It returns the COMPLETE corrected project using FILE sections.
    """

    async def run(
        self,
        code: str,
        review: str,
        execution_error: dict | str = "",
    ) -> str:

        if not code or not code.strip():

            raise ValueError(
                "Generated project code cannot be empty."
            )

        llm = LLMRouter.get_llm()

        # ------------------------------------------------------
        # Convert debug report into readable JSON
        # ------------------------------------------------------

        if isinstance(
            execution_error,
            dict,
        ):

            execution_error_text = json.dumps(
                execution_error,
                indent=2,
                ensure_ascii=False,
            )

        else:

            execution_error_text = str(
                execution_error or ""
            )

        prompt = f"""
You are a Principal Software Engineer and Software Architect.

You are repairing an automatically generated software project.

Your goal is to produce a COMPLETE corrected project that:

1. Runs successfully.
2. Fixes the reported execution failure.
3. Preserves all existing functionality.
4. Preserves the project architecture where possible.
5. Does not remove working features.
6. Does not invent unnecessary functionality.
7. Contains all required files.
8. Contains correct dependencies.
9. Contains correct configuration.
10. Contains correct imports.
11. Contains correct entry points.
12. Uses valid syntax.
13. Can actually be executed by the appropriate runtime.

==================================================
CURRENT GENERATED PROJECT
==================================================

{code}

==================================================
CODE REVIEW
==================================================

{review or "No code review available."}

==================================================
EXECUTION / DEBUG REPORT
==================================================

{execution_error_text}

==================================================
REPAIR OBJECTIVES
==================================================

Fix the actual root cause of the execution failure.

Check all of the following where applicable:

- syntax errors
- runtime errors
- import errors
- missing dependencies
- incorrect dependencies
- incorrect package versions
- missing files
- broken file paths
- incorrect entry points
- broken APIs
- incorrect function calls
- incorrect configuration
- environment variable handling
- database configuration
- frontend/backend communication
- Node.js module configuration
- Python package configuration
- Java compilation problems
- C++ compilation problems
- Docker configuration
- port configuration
- file/folder structure
- duplicate code
- incomplete files

IMPORTANT:

Do NOT solve the problem by deleting features.

Do NOT replace a real implementation with placeholder code.

Do NOT return partial files.

Do NOT return explanations.

Do NOT return analysis.

Do NOT return a summary.

Do NOT return markdown.

Do NOT use code fences.

==================================================
STRICT OUTPUT FORMAT
==================================================

Return ONLY project files.

Every file MUST start exactly with:

FILE: relative/path/to/file

Example:

FILE: package.json

{{
  "name": "example"
}}

FILE: src/server.js

const express = require("express");

...

Rules:

- Use relative file paths only.
- Never use absolute paths.
- Include every required project file.
- Include unchanged files if they are part of the project.
- Do not omit package.json.
- Do not omit requirements.txt when required.
- Do not omit configuration files when required.
- Do not omit source files.
- Do not add explanations before or after the files.
- Do not use ```.

Return the COMPLETE corrected project.
"""

        logger.info(
            "Starting AI project repair..."
        )

        response = await llm.generate(
            prompt
        )

        if response is None:

            raise RuntimeError(
                "Fixer LLM returned None."
            )

        response = response.strip()

        if not response:

            raise RuntimeError(
                "Fixer LLM returned an empty response."
            )

        logger.info(
            "AI project repair completed."
        )

        return response