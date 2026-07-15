import subprocess
import time
from pathlib import Path

from app.core.logger import logger


class PythonExecutor:

    def run(self, project_path: str):

        project = Path(project_path)

        # --------------------------
        # Install dependencies
        # --------------------------
        requirements = project / "requirements.txt"

        if requirements.exists():

            logger.info("Installing Python dependencies...")

            subprocess.run(
                [
                    "pip",
                    "install",
                    "-r",
                    str(requirements)
                ],
                cwd=project,
                capture_output=True,
                text=True,
            )

        # --------------------------
        # Find entry file
        # --------------------------
        candidates = [
            "main.py",
            "app.py",
            "run.py",
            "manage.py",
        ]

        main_file = None

        for file in candidates:

            if (project / file).exists():

                main_file = project / file
                break

        if main_file is None:

            return {
                "success": False,
                "stdout": "",
                "stderr": "No runnable Python file found.",
                "return_code": -1,
                "execution_time": 0,
            }

        logger.info(f"Running {main_file.name}")

        start = time.time()

        process = subprocess.run(
            ["python", str(main_file)],
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