from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from app.core.logger import logger


class PythonExecutor:
    """
    Executes generated Python projects safely with timeouts.

    Execution strategy:

    1. Validate project.
    2. Install declared dependencies only.
    3. Run pytest only when tests exist.
    4. Otherwise locate an entry point.
    5. Compile Python files first.
    6. Execute the entry point.
    7. Return structured execution information.
    """

    EXECUTION_TIMEOUT = 30
    INSTALL_TIMEOUT = 120

    ENTRY_FILES = (
        "main.py",
        "app.py",
        "run.py",
        "cli.py",
        "manage.py",
    )

    IGNORED_DIRS = {
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".git",
        "node_modules",
        "tests",
    }

    IGNORED_FILES = {
        "__init__.py",
        "setup.py",
        "conftest.py",
    }

    def run(
        self,
        project_path: str,
    ) -> dict:

        start_time = time.time()

        project = Path(
            project_path
        ).resolve()

        if not project.exists():
            return self._error(
                f"Project does not exist: {project}"
            )

        if not project.is_dir():
            return self._error(
                f"Project is not a directory: {project}"
            )

        logger.info(
            f"PythonExecutor running: {project}"
        )

        try:

            # --------------------------------------------------
            # Dependencies
            # --------------------------------------------------

            dependency_result = (
                self._install_dependencies(
                    project
                )
            )

            if not dependency_result["success"]:
                return self._finish(
                    dependency_result,
                    start_time,
                )

            # --------------------------------------------------
            # Tests
            # --------------------------------------------------

            tests_dir = project / "tests"

            if tests_dir.exists() and tests_dir.is_dir():

                logger.info(
                    "Tests directory detected."
                )

                result = self._run_pytest(
                    project
                )

                return self._finish(
                    result,
                    start_time,
                )

            # --------------------------------------------------
            # Entry point
            # --------------------------------------------------

            entry = self.find_entry(
                project
            )

            if entry is None:
                return self._finish(
                    self._error(
                        "No runnable Python entry file found."
                    ),
                    start_time,
                )

            logger.info(
                f"Python entry point: "
                f"{entry.relative_to(project)}"
            )

            # --------------------------------------------------
            # Syntax validation
            # --------------------------------------------------

            syntax_result = (
                self._compile_project(
                    project
                )
            )

            if not syntax_result["success"]:
                return self._finish(
                    syntax_result,
                    start_time,
                )

            # --------------------------------------------------
            # Detect interactive application
            # --------------------------------------------------

            content = entry.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            if self._is_interactive(
                content
            ):

                logger.warning(
                    "Interactive application detected."
                )

                return self._finish(
                    {
                        "success": True,
                        "stdout": "",
                        "stderr": (
                            "Interactive application "
                            "detected; execution skipped."
                        ),
                        "return_code": 0,
                    },
                    start_time,
                )

            # --------------------------------------------------
            # Determine command
            # --------------------------------------------------

            command = [
                sys.executable,
                str(entry),
            ]

            # If argparse is used, --help is a safe smoke test.
            if (
                "argparse" in content
                and "ArgumentParser" in content
            ):
                command.append("--help")

            logger.info(
                "Executing Python project..."
            )

            process = subprocess.run(
                command,
                cwd=project,
                capture_output=True,
                text=True,
                timeout=self.EXECUTION_TIMEOUT,
                stdin=subprocess.DEVNULL,
            )

            return self._finish(
                {
                    "success": process.returncode == 0,
                    "stdout": process.stdout or "",
                    "stderr": process.stderr or "",
                    "return_code": process.returncode,
                },
                start_time,
            )

        except subprocess.TimeoutExpired as exc:

            logger.error(
                "Python execution timed out."
            )

            return self._finish(
                {
                    "success": False,
                    "stdout": (
                        self._timeout_output(
                            exc.stdout
                        )
                    ),
                    "stderr": (
                        f"Execution timed out after "
                        f"{self.EXECUTION_TIMEOUT} seconds."
                    ),
                    "return_code": -1,
                },
                start_time,
            )

        except Exception as exc:

            logger.exception(
                "PythonExecutor failed."
            )

            return self._finish(
                self._error(
                    str(exc)
                ),
                start_time,
            )

    # ==========================================================
    # INSTALL DEPENDENCIES
    # ==========================================================

    def _install_dependencies(
        self,
        project: Path,
    ) -> dict:

        requirements = (
            project / "requirements.txt"
        )

        if not requirements.exists():
            return {
                "success": True
            }

        if requirements.stat().st_size == 0:
            return {
                "success": True
            }

        logger.info(
            "Installing project dependencies..."
        )

        try:

            process = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    "requirements.txt",
                ],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=self.INSTALL_TIMEOUT,
            )

            if process.returncode != 0:

                return {
                    "success": False,
                    "stdout": process.stdout or "",
                    "stderr": (
                        process.stderr
                        or "Dependency installation failed."
                    ),
                    "return_code": process.returncode,
                }

            return {
                "success": True,
                "stdout": process.stdout or "",
                "stderr": process.stderr or "",
                "return_code": 0,
            }

        except subprocess.TimeoutExpired:

            return {
                "success": False,
                "stdout": "",
                "stderr": (
                    "Dependency installation timed out "
                    f"after {self.INSTALL_TIMEOUT} seconds."
                ),
                "return_code": -1,
            }

    # ==========================================================
    # PYTEST
    # ==========================================================

    def _run_pytest(
        self,
        project: Path,
    ) -> dict:

        logger.info(
            "Running pytest..."
        )

        try:

            process = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                ],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=self.EXECUTION_TIMEOUT,
                stdin=subprocess.DEVNULL,
            )

            # pytest return code 5 means no tests collected.
            if process.returncode == 5:

                return {
                    "success": True,
                    "stdout": (
                        process.stdout
                        or "No tests collected."
                    ),
                    "stderr": process.stderr or "",
                    "return_code": 0,
                }

            return {
                "success": process.returncode == 0,
                "stdout": process.stdout or "",
                "stderr": process.stderr or "",
                "return_code": process.returncode,
            }

        except subprocess.TimeoutExpired:

            return {
                "success": False,
                "stdout": "",
                "stderr": (
                    "pytest timed out after "
                    f"{self.EXECUTION_TIMEOUT} seconds."
                ),
                "return_code": -1,
            }

    # ==========================================================
    # COMPILE
    # ==========================================================

    def _compile_project(
        self,
        project: Path,
    ) -> dict:

        logger.info(
            "Validating Python syntax..."
        )

        python_files = list(
            project.rglob("*.py")
        )

        python_files = [
            file
            for file in python_files
            if not self._is_ignored(
                file,
                project,
            )
        ]

        if not python_files:
            return self._error(
                "No Python source files found."
            )

        for file in python_files:

            try:

                process = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "py_compile",
                        str(file),
                    ],
                    cwd=project,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if process.returncode != 0:

                    return {
                        "success": False,
                        "stdout": process.stdout or "",
                        "stderr": (
                            process.stderr
                            or f"Syntax error in {file.name}"
                        ),
                        "return_code": process.returncode,
                    }

            except subprocess.TimeoutExpired:

                return self._error(
                    f"Syntax validation timed out: {file}"
                )

        return {
            "success": True,
            "stdout": "Python syntax validation passed.",
            "stderr": "",
            "return_code": 0,
        }

    # ==========================================================
    # FIND ENTRY
    # ==========================================================

    def find_entry(
        self,
        project: Path,
    ) -> Path | None:

        for filename in self.ENTRY_FILES:

            candidate = (
                project / filename
            )

            if candidate.exists():
                return candidate

        candidates = []

        for file in project.rglob("*.py"):

            if self._is_ignored(
                file,
                project,
            ):
                continue

            if file.name in self.IGNORED_FILES:
                continue

            candidates.append(file)

        if not candidates:
            return None

        # Prefer shallow files.
        candidates.sort(
            key=lambda p: (
                len(p.relative_to(project).parts),
                str(p).lower(),
            )
        )

        return candidates[0]

    # ==========================================================
    # INTERACTIVE DETECTION
    # ==========================================================

    def _is_interactive(
        self,
        content: str,
    ) -> bool:

        patterns = (
            "input(",
            "cmdloop(",
            "start_repl(",
            "while True:",
        )

        return any(
            pattern in content
            for pattern in patterns
        )

    # ==========================================================
    # IGNORED FILE
    # ==========================================================

    def _is_ignored(
        self,
        file: Path,
        project: Path,
    ) -> bool:

        relative = file.relative_to(
            project
        )

        return any(
            part in self.IGNORED_DIRS
            for part in relative.parts
        )

    # ==========================================================
    # FINISH
    # ==========================================================

    def _finish(
        self,
        result: dict,
        start_time: float,
    ) -> dict:

        result.setdefault(
            "success",
            False,
        )

        result.setdefault(
            "stdout",
            "",
        )

        result.setdefault(
            "stderr",
            "",
        )

        result.setdefault(
            "return_code",
            -1,
        )

        result["execution_time"] = round(
            time.time() - start_time,
            2,
        )

        return result

    # ==========================================================
    # ERROR
    # ==========================================================

    def _error(
        self,
        message: str,
    ) -> dict:

        return {
            "success": False,
            "stdout": "",
            "stderr": message,
            "return_code": -1,
            "execution_time": 0,
        }

    # ==========================================================
    # TIMEOUT OUTPUT
    # ==========================================================

    def _timeout_output(
        self,
        output,
    ) -> str:

        if output is None:
            return ""

        if isinstance(
            output,
            bytes,
        ):
            return output.decode(
                errors="replace"
            )

        return str(output)