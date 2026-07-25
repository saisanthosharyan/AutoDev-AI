import shutil
import subprocess
import time
from pathlib import Path

from app.core.logger import logger


class JavaTestRunner:
    """
    Compiles Java projects to verify they are error-free.
    """

    COMPILE_TIMEOUT = 120

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

        javac_path = shutil.which("javac")

        if javac_path is None:

            return {
                "success": False,
                "stdout": "",
                "stderr": "javac not found in PATH.",
                "return_code": -1,
                "execution_time": 0,
            }

        logger.info("Searching for Java files...")

        java_files = list(project.rglob("*.java"))

        if not java_files:

            return {
                "success": False,
                "stdout": "",
                "stderr": "No Java files found.",
                "return_code": -1,
                "execution_time": 0,
            }

        logger.info(f"Found {len(java_files)} Java files.")

        start = time.time()

        try:

            process = subprocess.run(
                [javac_path] + [str(f.relative_to(project)) for f in java_files],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=self.COMPILE_TIMEOUT,
            )

            end = time.time()

            execution_time = round(end - start, 2)

            if process.stdout:
                logger.info(process.stdout)

            if process.stderr:
                logger.error(process.stderr)

            logger.info(
                f"Java compilation finished in {execution_time} seconds."
            )

            return {
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode,
                "execution_time": execution_time,
            }

        except subprocess.TimeoutExpired:

            logger.error(
                f"Java compilation timed out after {self.COMPILE_TIMEOUT} seconds."
            )

            return {
                "success": False,
                "stdout": "",
                "stderr": f"Java compilation timed out after {self.COMPILE_TIMEOUT} seconds.",
                "return_code": -1,
                "execution_time": self.COMPILE_TIMEOUT,
            }

        except Exception as e:

            logger.exception("Java test execution failed.")

            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "execution_time": 0,
            }