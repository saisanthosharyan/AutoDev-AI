from __future__ import annotations

import re

from app.agents.base_agent import BaseAgent
from app.core.logger import logger
from app.models.task import Task
from app.services.llm.router import LLMRouter


class CoderAgent(BaseAgent):
    """
    Converts a Planner Task into a complete executable project.

    The LLM must return files in this format:

    FILE: app.py
    import argparse

    FILE: requirements.txt
    pytest

    FILE: tests/test_app.py
    def test_example():
        assert True
    """

    MIN_RESPONSE_LENGTH = 50
    MAX_FILE_PATH_LENGTH = 250

    FORBIDDEN_PATH_PATTERNS = (
        ".env",
        ".env.local",
        ".env.production",
        ".env.development",
        "id_rsa",
        "id_ed25519",
        ".pem",
        ".key",
        "__pycache__",
        ".pyc",
        "node_modules",
        ".git/",
    )

    LANGUAGE_LABELS = {
        "python",
        "py",
        "javascript",
        "js",
        "typescript",
        "ts",
        "json",
        "html",
        "css",
        "java",
        "cpp",
        "c++",
        "c",
        "bash",
        "shell",
        "sh",
        "yaml",
        "yml",
        "markdown",
        "md",
        "text",
        "plaintext",
    }

    # ==========================================================
    # MAIN
    # ==========================================================

    async def run(self, task: Task) -> str:

        logger.info("=" * 60)
        logger.info("Coder Agent Started")
        logger.info("=" * 60)

        if task is None:
            raise ValueError(
                "CoderAgent received an empty task."
            )

        if not task.title:
            raise ValueError(
                "Task title is required."
            )

        if not task.description:
            raise ValueError(
                "Task description is required."
            )

        # ------------------------------------------------------
        # Get LLM
        # ------------------------------------------------------

        llm = LLMRouter.get_llm()

        # ------------------------------------------------------
        # Format Planner Steps
        # ------------------------------------------------------

        steps = "\n".join(
            f"{index}. {step}"
            for index, step in enumerate(
                task.steps or [],
                start=1,
            )
        )

        # ------------------------------------------------------
        # Build Prompt
        # ------------------------------------------------------

        prompt = self._build_prompt(
            task=task,
            steps=steps,
        )

        logger.info(
            "Generating complete software project..."
        )

        # ------------------------------------------------------
        # Generate
        # ------------------------------------------------------

        response = await llm.generate(prompt)

        if response is None:
            raise RuntimeError(
                "Coder Agent received None from LLM."
            )

        if not isinstance(response, str):
            response = str(response)

        response = response.strip()

        if not response:
            raise RuntimeError(
                "Coder Agent received an empty response from LLM."
            )

        logger.info(
            f"Raw coder response length: {len(response)}"
        )

        # ------------------------------------------------------
        # Normalize
        # ------------------------------------------------------

        response = self._normalize_response(
            response
        )

        # ------------------------------------------------------
        # Validate
        # ------------------------------------------------------

        self._validate_response(
            response
        )

        logger.info(
            "Coder Agent generated valid project output."
        )

        logger.info("=" * 60)
        logger.info("Coder Agent Finished")
        logger.info("=" * 60)

        return response

    # ==========================================================
    # PROMPT
    # ==========================================================

    def _build_prompt(
        self,
        task: Task,
        steps: str,
    ) -> str:

        return f"""
You are AutoDev AI, an autonomous software engineer.

Generate a COMPLETE, EXECUTABLE software project.

============================================================
PROJECT
============================================================

PROJECT TITLE:
{task.title}

PROJECT DESCRIPTION:
{task.description}

IMPLEMENTATION PLAN:
{steps or "No implementation steps were provided."}

============================================================
IMPORTANT PROJECT RULES
============================================================

1. Choose the simplest appropriate technology.
2. Do not add unnecessary frameworks.
3. Do not add unnecessary databases.
4. Do not add unnecessary Docker configuration.
5. Preserve the requested functionality.
6. Every required source file must be complete.
7. Every import must be valid.
8. Every dependency must actually exist.
9. Every entry point must be executable.
10. Do not generate fake implementations.
11. Do not generate TODO placeholders.
12. Do not generate FIXME placeholders.
13. Do not generate pseudocode.
14. Do not generate real secrets.
15. Never create .env files.
16. Use .env.example for configuration examples.
17. Generate real executable tests when appropriate.

============================================================
PYTHON REQUIREMENTS
============================================================

If Python is selected:

- Use valid Python syntax.
- Generate requirements.txt only when dependencies are needed.
- Use pytest for tests when appropriate.
- Ensure entry points work.
- Avoid interactive programs unless explicitly required.
- CLI applications must provide valid command/help behavior.
- Do not leave variables undefined.
- Handle invalid input safely.
- Handle division by zero where applicable.
- Do not put a language name such as "python" on the
  first line of a Python source file.

============================================================
NODE REQUIREMENTS
============================================================

If Node.js is selected:

- package.json must be valid JSON.
- All imports must match installed dependencies.
- The start entry point must exist.
- Use correct CommonJS or ESM configuration.
- Do not mix require() and import incorrectly.

============================================================
TESTING REQUIREMENTS
============================================================

Generate real executable tests when appropriate.

Python:
- Prefer pytest.
- Tests must actually test application functionality.

Node.js:
- Use an appropriate test framework only when required.
- Tests must actually execute.

Do not generate fake tests that only assert True unless
the project genuinely requires a basic smoke test.

============================================================
README REQUIREMENTS
============================================================

When a README is appropriate, include:

1. Project overview
2. Features
3. Technology stack
4. Project structure
5. Installation
6. Configuration
7. Environment variables
8. Usage
9. API documentation when applicable
10. Running the application
11. Running tests
12. Deployment information when applicable

============================================================
SECURITY
============================================================

Never generate real:

- API keys
- passwords
- private keys
- access tokens
- credentials
- secrets

Never create an actual .env file.

Use .env.example when environment configuration is needed.

============================================================
OUTPUT FORMAT
============================================================

THIS IS EXTREMELY IMPORTANT.

Return ONLY project files.

Every file MUST begin with:

FILE: relative/path/to/file.ext

Example:

FILE: app.py
import argparse

FILE: requirements.txt
pytest

FILE: tests/test_app.py
def test_example():
    assert 1 + 1 == 2

============================================================
STRICT FILE RULES
============================================================

- Start immediately with FILE:
- Do not write anything before the first FILE:
- Do not write anything after the final file.
- Do not use markdown code fences.
- Do not write ```python.
- Do not write ```javascript.
- Do not write ```json.
- Do not write language names before source code.
- Do not explain the files.
- Do not provide a summary.
- Do not provide analysis.

A file must look like:

FILE: app.py
import argparse

NOT:

FILE: app.py
python
import argparse

NOT:

FILE: app.py
```python
import argparse

============================================================
FINAL REQUIREMENT
============================================================

The generated project must be executable without manual
modification.

Start the response immediately with:

FILE:

Return ONLY the FILE blocks.
"""

    # ==========================================================
    # RESPONSE NORMALIZATION
    # ==========================================================

    def _normalize_response(
        self,
        response: str,
    ) -> str:
        """
        Clean common formatting mistakes from the LLM response.
        """

        response = response.strip()

        # ------------------------------------------------------
        # Remove opening markdown fences
        # ------------------------------------------------------

        response = re.sub(
            r"^\s*```(?:text|plaintext)?\s*",
            "",
            response,
            flags=re.IGNORECASE,
        )

        # ------------------------------------------------------
        # Remove closing markdown fence
        # ------------------------------------------------------

        response = re.sub(
            r"\s*```\s*$",
            "",
            response,
        )

        response = response.strip()

        # ------------------------------------------------------
        # Remove accidental text before FILE:
        # ------------------------------------------------------

        first_file = response.find("FILE:")

        if first_file > 0:

            logger.warning(
                "Removing text before first FILE: marker."
            )

            response = response[
                first_file:
            ]

        # ------------------------------------------------------
        # Remove accidental language labels after FILE:
        # ------------------------------------------------------

        response = self._remove_language_labels(
            response
        )

        return response.strip()

    # ==========================================================
    # REMOVE LANGUAGE LABELS
    # ==========================================================

    def _remove_language_labels(
        self,
        response: str,
    ) -> str:
        """
        Remove accidental language labels such as:

        FILE: app.py
        python
        import argparse

        The word 'python' should not become part of app.py.
        """

        pattern = re.compile(
            r"(?m)"
            r"^(FILE:\s*[^\r\n]+)"
            r"(\r?\n)"
            r"(python|py|javascript|js|typescript|ts|"
            r"json|html|css|java|cpp|c\+\+|c|bash|shell|sh|"
            r"yaml|yml|markdown|md|text|plaintext)"
            r"(\r?\n)",
            flags=re.IGNORECASE,
        )

        return pattern.sub(
            r"\1\2\4",
            response,
        )

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def _validate_response(
        self,
        response: str,
    ) -> None:
        """
        Validate that the coder response contains valid
        FILE blocks.
        """

        if not response:

            raise RuntimeError(
                "Coder Agent returned an empty project."
            )

        if len(response) < self.MIN_RESPONSE_LENGTH:

            raise RuntimeError(
                "Coder Agent response is too short "
                "to be a project."
            )

        if not response.startswith("FILE:"):

            raise RuntimeError(
                "Invalid coder output. "
                "Project must start with FILE:."
            )

        file_blocks = self._extract_file_blocks(
            response
        )

        if not file_blocks:

            raise RuntimeError(
                "Coder Agent generated no project files."
            )

        logger.info(
            f"Coder generated {len(file_blocks)} file(s)."
        )

        for path, content in file_blocks:

            self._validate_file_path(
                path
            )

            if not content.strip():

                raise RuntimeError(
                    f"Generated file is empty: {path}"
                )

            logger.debug(
                f"Validated generated file: {path}"
            )

    # ==========================================================
    # EXTRACT FILE BLOCKS
    # ==========================================================

    def _extract_file_blocks(
        self,
        response: str,
    ) -> list[tuple[str, str]]:
        """
        Extract FILE blocks.

        Example:

        FILE: app.py
        print("Hello")

        FILE: README.md
        # Project
        """

        pattern = re.compile(
            r"(?m)^FILE:\s*(.+?)\s*$"
        )

        matches = list(
            pattern.finditer(
                response
            )
        )

        if not matches:
            return []

        files: list[
            tuple[str, str]
        ] = []

        for index, match in enumerate(matches):

            path = match.group(
                1
            ).strip()

            content_start = match.end()

            if index + 1 < len(matches):

                content_end = matches[
                    index + 1
                ].start()

            else:

                content_end = len(
                    response
                )

            content = response[
                content_start:content_end
            ].strip()

            files.append(
                (
                    path,
                    content,
                )
            )

        return files

    # ==========================================================
    # FILE PATH VALIDATION
    # ==========================================================

    def _validate_file_path(
        self,
        path: str,
    ) -> None:
        """
        Validate generated file paths.
        """

        if not path:

            raise RuntimeError(
                "Generated file contains an empty path."
            )

        if len(path) > self.MAX_FILE_PATH_LENGTH:

            raise RuntimeError(
                f"Generated file path is too long: {path}"
            )

        # ------------------------------------------------------
        # Normalize Windows separators
        # ------------------------------------------------------

        normalized = path.replace(
            "\\",
            "/",
        )

        # ------------------------------------------------------
        # Absolute Unix path
        # ------------------------------------------------------

        if normalized.startswith("/"):

            raise RuntimeError(
                f"Absolute file path is not allowed: {path}"
            )

        # ------------------------------------------------------
        # Windows drive path
        # ------------------------------------------------------

        if re.match(
            r"^[A-Za-z]:",
            normalized,
        ):

            raise RuntimeError(
                "Absolute Windows path is not allowed: "
                f"{path}"
            )

        # ------------------------------------------------------
        # Directory traversal
        # ------------------------------------------------------

        parts = normalized.split("/")

        if ".." in parts:

            raise RuntimeError(
                f"Directory traversal is not allowed: {path}"
            )

        # ------------------------------------------------------
        # Empty path components
        # ------------------------------------------------------

        if any(
            not part.strip()
            for part in parts
        ):

            raise RuntimeError(
                f"Invalid file path: {path}"
            )

        # ------------------------------------------------------
        # Forbidden files
        # ------------------------------------------------------

        lower_path = normalized.lower()

        for forbidden in self.FORBIDDEN_PATH_PATTERNS:

            if forbidden in lower_path:

                raise RuntimeError(
                    f"Forbidden file path generated: {path}"
                )

    # ==========================================================
    # DEBUG INFORMATION
    # ==========================================================

    def get_file_blocks(
        self,
        response: str,
    ) -> list[tuple[str, str]]:
        """
        Public helper useful for debugging and testing.
        """

        normalized = self._normalize_response(
            response
        )

        return self._extract_file_blocks(
            normalized
        )