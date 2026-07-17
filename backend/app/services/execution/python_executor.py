import subprocess
import sys
import time
from pathlib import Path

from app.core.logger import logger


class PythonExecutor:

    def run(self, project_path: str):

        project = Path(project_path).resolve()

        if not project.exists():
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Project does not exist: {project}",
                "return_code": -1,
                "execution_time": 0,
            }

        # -------------------------------------------------
        # Install dependencies
        # -------------------------------------------------

        requirements = project / "requirements.txt"

        if requirements.exists():

            logger.info("Installing Python dependencies...")

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

                logger.error("Dependency installation failed.")

                return {
                    "success": False,
                    "stdout": install.stdout,
                    "stderr": install.stderr,
                    "return_code": install.returncode,
                    "execution_time": 0,
                }

        # -------------------------------------------------
        # Run tests if present
        # -------------------------------------------------

        tests_dir = project / "tests"

        if tests_dir.exists():

            logger.info("Tests detected. Running pytest...")

            start = time.time()

            process = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-v",
                ],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=60,
            )

            end = time.time()

            return {
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode,
                "execution_time": round(end - start, 2),
            }

        # -------------------------------------------------
        # Locate entry point
        # -------------------------------------------------

        entry = self.find_entry(project)

        if entry is None:

            return {
                "success": False,
                "stdout": "",
                "stderr": "No runnable python entry file found.",
                "return_code": -1,
                "execution_time": 0,
            }

        relative_entry = entry.relative_to(project)

        logger.info(f"Running {relative_entry}")

        # -------------------------------------------------
        # Detect interactive CLI
        # -------------------------------------------------

        try:
            content = entry.read_text(encoding="utf-8", errors="ignore")

            interactive_patterns = [
                "input(",
                "start_repl(",
                "cmdloop(",
                "while True",
            ]

            if any(pattern in content for pattern in interactive_patterns):

                logger.warning(
                    "Interactive CLI detected. Skipping execution."
                )

                return {
                    "success": True,
                    "stdout": "",
                    "stderr": "Interactive CLI application detected. Skipped execution.",
                    "return_code": 0,
                    "execution_time": 0,
                }

        except Exception:
            pass

        # -------------------------------------------------
        # Execute project
        # -------------------------------------------------

        start = time.time()

        try:

            process = subprocess.run(
                [
                    sys.executable,
                    str(relative_entry),
                ],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=60,
            )

            end = time.time()

            if process.stdout:
                logger.info(process.stdout)

            if process.stderr:
                logger.error(process.stderr)

            return {
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode,
                "execution_time": round(end - start, 2),
            }

        except subprocess.TimeoutExpired:

            return {
                "success": False,
                "stdout": "",
                "stderr": "Execution timed out after 60 seconds.",
                "return_code": -1,
                "execution_time": 60,
            }

        except Exception as e:

            logger.exception("Python execution failed.")

            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "execution_time": 0,
            }

    # -------------------------------------------------

    def find_entry(self, project: Path):

        priority = [

            project / "main.py",
            project / "app.py",
            project / "run.py",

            project / "src" / "main.py",
            project / "src" / "app.py",
            project / "src" / "run.py",

        ]

        for file in priority:
            if file.exists():
                return file

        ignored = {
            "__init__.py",
            "setup.py",
            "conftest.py",
        }

        ignored_dirs = {
            ".venv",
            "venv",
            "__pycache__",
            "tests",
            ".pytest_cache",
        }

        for file in project.rglob("*.py"):

            if file.name in ignored:
                continue

            if any(part in ignored_dirs for part in file.parts):
                continue

            return file

        return None