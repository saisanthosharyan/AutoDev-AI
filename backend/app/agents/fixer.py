import json

from app.agents.base_agent import BaseAgent
from app.core.logger import logger
from app.services.llm.router import LLMRouter


class FixerAgent(BaseAgent):
    """
    AI agent responsible for repairing generated projects.

    The fixer receives:
        - Complete current project source
        - Previous AI review
        - Execution/debug information

    It must return the COMPLETE repaired project using:

        FILE: relative/path/to/file

    format.

    The complete project is returned because ProjectBuilder.rebuild()
    rebuilds the project from the returned file set.
    """

    async def run(
        self,
        code: str,
        review: dict | str | None = None,
        execution_error: dict | str | None = None,
    ) -> str:

        # ==========================================================
        # VALIDATE INPUT
        # ==========================================================

        if not code or not code.strip():
            raise ValueError(
                "Generated project code cannot be empty."
            )

        # ==========================================================
        # LLM
        # ==========================================================

        llm = LLMRouter.get_llm()

        # ==========================================================
        # NORMALIZE REVIEW
        # ==========================================================

        if isinstance(review, dict):

            review_text = json.dumps(
                review,
                indent=2,
                ensure_ascii=False,
            )

        else:

            review_text = str(
                review or ""
            )

        if not review_text.strip():
            review_text = (
                "No previous code review is available."
            )

        # ==========================================================
        # NORMALIZE EXECUTION ERROR
        # ==========================================================

        if isinstance(execution_error, dict):

            execution_error_text = json.dumps(
                execution_error,
                indent=2,
                ensure_ascii=False,
            )

        else:

            execution_error_text = str(
                execution_error or ""
            )

        if not execution_error_text.strip():
            execution_error_text = (
                "No execution error information is available."
            )

        # ==========================================================
        # PROMPT
        # ==========================================================

        prompt = f"""
You are AutoDev AI's autonomous software repair engineer.

You are responsible for repairing an existing generated software
project after execution, validation, or testing failures.

Your job is NOT to redesign the project.

Your job is to identify the actual problem and return a COMPLETE
corrected version of the project.

============================================================
CURRENT PROJECT
============================================================

The following is the COMPLETE current project:

{code}

============================================================
PREVIOUS CODE REVIEW
============================================================

{review_text}

============================================================
EXECUTION / DEBUG REPORT
============================================================

{execution_error_text}

============================================================
REPAIR OBJECTIVE
============================================================

Fix the actual root cause of the failure.

Preserve all existing working functionality.

Do not remove features merely to make execution succeed.

Do not replace working implementations with simplified
placeholder implementations.

Do not redesign the architecture unless the existing architecture
is directly responsible for the failure.

============================================================
CHECK THESE AREAS
============================================================

Check the complete project for:

1. Syntax errors
2. Runtime errors
3. Import errors
4. Missing dependencies
5. Incorrect dependencies
6. Incorrect package versions
7. Missing files
8. Incorrect file paths
9. Incorrect entry points
10. Broken function calls
11. Incorrect APIs
12. Incorrect configuration
13. Environment variable problems
14. Database configuration problems
15. Frontend/backend communication problems
16. Node.js module configuration
17. Python package configuration
18. Java compilation problems
19. C++ compilation problems
20. Docker configuration
21. Port configuration
22. Broken project structure
23. Incorrect test configuration
24. Missing executable files
25. Incorrect imports
26. Incorrect dependency declarations

============================================================
IMPORTANT REPAIR RULES
============================================================

DO:

- Fix the root cause.
- Preserve working functionality.
- Preserve the existing architecture where possible.
- Keep all required files.
- Keep package.json when the project uses Node.js.
- Keep requirements.txt when the project uses Python.
- Keep configuration files when required.
- Keep source files.
- Keep tests when they already exist.
- Correct dependencies when necessary.
- Correct imports when necessary.
- Correct entry points when necessary.
- Make the project executable.
- Make the project internally consistent.

DO NOT:

- Delete features to hide errors.
- Delete tests to make testing pass.
- Delete dependencies without checking usage.
- Replace the entire project with a trivial example.
- Generate TODO.
- Generate FIXME.
- Generate placeholder implementations.
- Generate pseudocode.
- Generate incomplete files.
- Return only changed files.
- Return explanations.
- Return analysis.
- Return summaries.
- Return markdown.
- Return code fences.

============================================================
CRITICAL REQUIREMENT
============================================================

YOU MUST RETURN THE COMPLETE PROJECT.

Even if only one file needs modification, return every project
file required for the project to work.

The ProjectBuilder will rebuild the project from your response.

Therefore, omitting an existing required file can destroy the
working project.

============================================================
OUTPUT FORMAT
============================================================

Return ONLY project files.

Every file must start exactly with:

FILE: relative/path/to/file

Example:

FILE: package.json

{{
  "name": "example"
}}

FILE: src/main.py

print("Hello")

FILE: README.md

# Example

============================================================
STRICT OUTPUT RULES
============================================================

1. Start immediately with FILE:
2. Use relative paths only.
3. Never use absolute Windows paths.
4. Never use markdown code fences.
5. Never add explanations.
6. Never add analysis.
7. Never add a summary.
8. Never add text before the first FILE:
9. Never add text after the final file.
10. Return the COMPLETE corrected project.
11. Do not omit unchanged required files.
12. Do not create unnecessary files.
13. Do not create unnecessary tests.
14. Do not remove existing tests.
15. Do not remove working features.
16. Ensure every import refers to an existing file/package.
17. Ensure every dependency is declared.
18. Ensure the project has a valid entry point.
19. Ensure the generated project can actually run.

============================================================
FINAL VALIDATION BEFORE RESPONSE
============================================================

Before returning the project, internally verify:

- Every FILE path is valid.
- Every required file is included.
- Imports match the files provided.
- Dependencies match imports.
- Entry point exists.
- Configuration is consistent.
- No syntax errors are introduced.
- The reported execution problem is actually fixed.
- Existing functionality is preserved.

Return ONLY the complete corrected project.
"""

        # ==========================================================
        # GENERATE REPAIR
        # ==========================================================

        logger.info(
            "Starting AI project repair..."
        )

        try:

            response = await llm.generate(
                prompt
            )

        except Exception:

            logger.exception(
                "LLM project repair request failed."
            )

            raise

        # ==========================================================
        # VALIDATE RESPONSE
        # ==========================================================

        if response is None:

            raise RuntimeError(
                "Fixer LLM returned None."
            )

        response = response.strip()

        if not response:

            raise RuntimeError(
                "Fixer LLM returned an empty response."
            )

        # ==========================================================
        # BASIC FORMAT VALIDATION
        # ==========================================================

        if not response.lstrip().startswith(
            "FILE:"
        ):

            logger.error(
                "Fixer returned invalid project format."
            )

            raise RuntimeError(
                "Fixer response does not start with FILE:."
            )

        if "FILE:" not in response:

            raise RuntimeError(
                "Fixer response contains no project files."
            )

        # ==========================================================
        # LOG
        # ==========================================================

        file_count = response.count(
            "\nFILE:"
        )

        if response.startswith("FILE:"):
            file_count += 1

        logger.info(
            f"AI project repair completed. "
            f"Generated approximately {file_count} files."
        )

        return response