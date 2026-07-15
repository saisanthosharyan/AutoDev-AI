import subprocess
import sys
import time
from pathlib import Path

from app.core.logger import logger


class PythonTestRunner:

    def run(self, project_path: str):

        project = Path(project_path)

        # -------------------------
        # Install dependencies
        # -------------------------
        requirements = project / "requirements.txt"

        if requirements.exists():

            logger.info("Installing Python test dependencies...")

            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(requirements),
                ],
                cwd=project,
                capture_output=True,
                text=True,
            )

        logger.info("Running pytest...")

        start = time.time()

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
                timeout=120,
            )

            success = process.returncode == 0
            stdout = process.stdout
            stderr = process.stderr
            return_code = process.returncode

        except FileNotFoundError as e:

            success = False
            stdout = ""
            stderr = str(e)
            return_code = -1

        except subprocess.TimeoutExpired:

            success = False
            stdout = ""
            stderr = "Pytest timed out."
            return_code = -1

        end = time.time()

        return {
            "success": success,
            "stdout": stdout,
            "stderr": stderr,
            "return_code": return_code,
            "execution_time": round(end - start, 2),
        }