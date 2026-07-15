import subprocess
import time
from pathlib import Path

from app.core.logger import logger


class JavaExecutor:

    def run(self, project_path: str):

        project = Path(project_path)

        java_files = list(project.rglob("*.java"))

        if not java_files:
            return {
                "success": False,
                "stdout": "",
                "stderr": "No Java source files found.",
                "return_code": -1,
                "execution_time": 0,
            }

        source = java_files[0]

        logger.info(f"Compiling {source.name}")

        compile_result = subprocess.run(
            ["javac", source.name],
            cwd=source.parent,
            capture_output=True,
            text=True,
        )

        if compile_result.returncode != 0:
            return {
                "success": False,
                "stdout": compile_result.stdout,
                "stderr": compile_result.stderr,
                "return_code": compile_result.returncode,
                "execution_time": 0,
            }

        logger.info(f"Running {source.stem}")

        start = time.time()

        run_result = subprocess.run(
            ["java", source.stem],
            cwd=source.parent,
            capture_output=True,
            text=True,
            timeout=60,
        )

        end = time.time()

        return {
            "success": run_result.returncode == 0,
            "stdout": run_result.stdout,
            "stderr": run_result.stderr,
            "return_code": run_result.returncode,
            "execution_time": round(end - start, 2),
        }