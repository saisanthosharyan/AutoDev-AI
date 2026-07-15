import subprocess
import time
from pathlib import Path

from app.core.logger import logger


class CPPTestRunner:

    def run(self, project_path: str):

        project = Path(project_path)

        logger.info("Searching for C++ files...")

        cpp_files = list(project.rglob("*.cpp"))

        if not cpp_files:
            return {
                "success": False,
                "stdout": "",
                "stderr": "No C++ files found.",
                "return_code": -1,
                "execution_time": 0,
            }

        source = cpp_files[0]

        logger.info(f"Compiling {source.name}")

        start = time.time()

        compile_result = subprocess.run(
            [
                "g++",
                source.name,
                "-o",
                "test_program",
            ],
            cwd=source.parent,
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