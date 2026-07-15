import subprocess
import time
from pathlib import Path

from app.core.logger import logger


class JavaTestRunner:

    def run(self, project_path: str):

        project = Path(project_path)

        logger.info("Searching for Java tests...")

        java_files = list(project.rglob("*.java"))

        if not java_files:
            return {
                "success": False,
                "stdout": "",
                "stderr": "No Java files found.",
                "return_code": -1,
                "execution_time": 0,
            }

        start = time.time()

        compile_result = subprocess.run(
            ["javac"] + [str(f.relative_to(project)) for f in java_files],
            cwd=project,
            capture_output=True,
            text=True,
        )

        end = time.time()

        return {
            "success": compile_result.returncode == 0,
            "stdout": compile_result.stdout,
            "stderr": compile_result.stderr,
            "return_code": compile_result.returncode,
            "execution_time": round(end - start, 2),
        }