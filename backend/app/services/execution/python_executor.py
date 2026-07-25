import subprocess
import sys
import time
from pathlib import Path

from app.core.logger import logger


class PythonExecutor:

    EXECUTION_TIMEOUT = 60

    def run(self, project_path: str):

        project = Path(project_path).resolve()

        if not project.exists():

            return self._error(
                f"Project does not exist: {project}"
            )

        # --------------------------------------------------
        # Install dependencies
        # --------------------------------------------------

        requirements = project / "requirements.txt"

        if (
            requirements.exists()
            and requirements.stat().st_size > 0
        ):

            logger.info(
                "Installing Python dependencies..."
            )

            install = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    requirements.name,
                ],
                cwd=project,
                capture_output=True,
                text=True,
            )

            if install.returncode != 0:

                logger.error(
                    "Dependency installation failed."
                )

                return {
                    "success": False,
                    "stdout": install.stdout,
                    "stderr": install.stderr,
                    "return_code": install.returncode,
                    "execution_time": 0,
                }

        # Ensure pytest exists

        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "pytest",
            ],
            capture_output=True,
            text=True,
        )

        # --------------------------------------------------
        # Run Tests
        # --------------------------------------------------

        if (project / "tests").exists():

            logger.info(
                "Running pytest..."
            )

            start = time.time()

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
            )

            end = time.time()

            if process.returncode == 5:

                return {
                    "success": True,
                    "stdout": "No tests collected.",
                    "stderr": "",
                    "return_code": 0,
                    "execution_time": round(end - start, 2),
                }

            return {
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode,
                "execution_time": round(end - start, 2),
            }

        # --------------------------------------------------
        # Find Entry Point
        # --------------------------------------------------

        entry = self.find_entry(project)

        if entry is None:

            return self._error(
                "No runnable Python entry file found."
            )

        relative = entry.relative_to(project)

        logger.info(
            f"Executing {relative}"
        )

        # --------------------------------------------------
        # Detect Interactive Apps
        # --------------------------------------------------

        try:

            content = entry.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            patterns = [
                "input(",
                "cmdloop(",
                "start_repl(",
                "while True",
                "prompt(",
            ]

            if any(
                p in content
                for p in patterns
            ):

                logger.warning(
                    "Interactive application detected."
                )

                return {
                    "success": True,
                    "stdout": "",
                    "stderr": "Interactive application skipped.",
                    "return_code": 0,
                    "execution_time": 0,
                }

        except Exception:
            pass

        # --------------------------------------------------
        # Execute
        # --------------------------------------------------

        start = time.time()

        try:

            process = subprocess.run(
                [
                    sys.executable,
                    str(relative),
                ],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=self.EXECUTION_TIMEOUT,
            )

            end = time.time()

            return {
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode,
                "execution_time": round(end - start, 2),
            }

        except subprocess.TimeoutExpired:

            return self._error(
                f"Execution timed out after {self.EXECUTION_TIMEOUT} seconds."
            )

        except Exception as e:

            logger.exception(
                "Python execution failed."
            )

            return self._error(str(e))

    # --------------------------------------------------

    def find_entry(
        self,
        project: Path,
    ):

        priority = [

            project / "main.py",
            project / "app.py",
            project / "run.py",
            project / "manage.py",

            project / "src" / "main.py",
            project / "src" / "app.py",
            project / "src" / "run.py",

            project / "app" / "main.py",
            project / "app.py",

        ]

        for file in priority:

            if file.exists():
                return file

        ignored_dirs = {
            ".venv",
            "venv",
            "__pycache__",
            ".pytest_cache",
            "tests",
            "node_modules",
        }

        ignored_files = {
            "__init__.py",
            "setup.py",
            "conftest.py",
        }

        for file in project.rglob("*.py"):

            if file.name in ignored_files:
                continue

            if any(
                part in ignored_dirs
                for part in file.parts
            ):
                continue

            return file

        return None

    # --------------------------------------------------

    def _error(
        self,
        message: str,
    ):

        return {
            "success": False,
            "stdout": "",
            "stderr": message,
            "return_code": -1,
            "execution_time": 0,
        }