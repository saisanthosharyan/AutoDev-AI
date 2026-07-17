import subprocess
import sys
import time
from pathlib import Path

from app.core.logger import logger


class PythonTestRunner:

    def run(self, project_path: str):

        project = Path(project_path).resolve()

        requirements = project / "requirements.txt"

        print("=" * 60)
        print("PROJECT :", project)
        print("REQUIREMENTS :", requirements)
        print("EXISTS :", requirements.exists())
        print("=" * 60)

        # --------------------------------------------------
        # Install project dependencies
        # --------------------------------------------------

        if requirements.exists():

            logger.info("Installing Python test dependencies...")

            install = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    "requirements.txt",   # <-- FIXED
                ],
                cwd=project,
                capture_output=True,
                text=True,
            )

            print("RETURN CODE:", install.returncode)
            print("STDOUT:")
            print(install.stdout)
            print("STDERR:")
            print(install.stderr)

            if install.returncode != 0:

                logger.error("Dependency installation failed.")

                return {
                    "success": False,
                    "stdout": install.stdout,
                    "stderr": install.stderr,
                    "return_code": install.returncode,
                    "execution_time": 0,
                }

        # --------------------------------------------------
        # Ensure pytest exists
        # --------------------------------------------------

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

            end = time.time()

            if process.returncode == 5:

                logger.warning("No tests found.")

                return {
                    "success": True,
                    "stdout": "No tests found.",
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

        except subprocess.TimeoutExpired:

            return {
                "success": False,
                "stdout": "",
                "stderr": "Pytest timed out after 120 seconds.",
                "return_code": -1,
                "execution_time": 120,
            }

        except Exception as e:

            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "execution_time": 0,
            }