import subprocess
import sys
import time
from pathlib import Path

from app.core.logger import logger


class PythonTestRunner:
    """
    Runs pytest for Python projects.
    """

    TIMEOUT = 120

    def run(self, project_path: str):

        project = Path(project_path).resolve()

        if not project.exists():
            return self._result(
                False,
                "",
                f"Project does not exist: {project}",
                -1,
                0,
            )

        logger.info("=" * 60)
        logger.info("Python Test Runner Started")
        logger.info("=" * 60)

        requirements = project / "requirements.txt"

        try:

            # --------------------------------------------------
            # Install Project Dependencies
            # --------------------------------------------------

            if requirements.exists():

                logger.info("Installing project dependencies...")

                install = subprocess.run(
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
                )

                if install.stdout:
                    logger.info(install.stdout)

                if install.stderr:
                    logger.error(install.stderr)

                if install.returncode != 0:

                    logger.error("Dependency installation failed.")

                    return self._result(
                        False,
                        install.stdout,
                        install.stderr,
                        install.returncode,
                        0,
                    )

            # --------------------------------------------------
            # Ensure pytest exists
            # --------------------------------------------------

            logger.info("Installing pytest (if required)...")

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

            logger.info("Running pytest...")

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
                timeout=self.TIMEOUT,
            )

            execution_time = round(time.time() - start, 2)

            if process.stdout:
                logger.info(process.stdout)

            if process.stderr:
                logger.error(process.stderr)

            # pytest exit code 5 = no tests collected
            if process.returncode == 5:

                logger.warning("No tests found.")

                return self._result(
                    True,
                    "No tests found.",
                    "",
                    0,
                    execution_time,
                )

            logger.info(
                f"Testing finished in {execution_time} seconds."
            )

            return self._result(
                process.returncode == 0,
                process.stdout,
                process.stderr,
                process.returncode,
                execution_time,
            )

        except subprocess.TimeoutExpired:

            logger.error(
                f"Pytest timed out after {self.TIMEOUT} seconds."
            )

            return self._result(
                False,
                "",
                f"Pytest timed out after {self.TIMEOUT} seconds.",
                -1,
                self.TIMEOUT,
            )

        except Exception as e:

            logger.exception("Python testing failed.")

            return self._result(
                False,
                "",
                str(e),
                -1,
                0,
            )

        finally:

            logger.info("=" * 60)
            logger.info("Python Test Runner Finished")
            logger.info("=" * 60)

    def _result(
        self,
        success: bool,
        stdout: str,
        stderr: str,
        return_code: int,
        execution_time: float,
    ):
        return {
            "success": success,
            "stdout": stdout,
            "stderr": stderr,
            "return_code": return_code,
            "execution_time": execution_time,
        }