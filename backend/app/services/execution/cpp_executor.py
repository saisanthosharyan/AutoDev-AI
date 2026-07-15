import os
import subprocess
import time
from pathlib import Path

from app.core.logger import logger


class CPPExecutor:

    def run(self, project_path: str):

        project = Path(project_path)

        cpp_files = list(project.rglob("*.cpp"))

        if not cpp_files:
            return {
                "success": False,
                "stdout": "",
                "stderr": "No C++ source files found.",
                "return_code": -1,
                "execution_time": 0,
            }

        source = cpp_files[0]

        executable = "program.exe" if os.name == "nt" else "program"

        logger.info(f"Compiling {source.name}")

        compile_result = subprocess.run(
            [
                "g++",
                source.name,
                "-o",
                executable,
            ],
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

        logger.info("Running executable")

        command = executable if os.name == "nt" else f"./{executable}"

        start = time.time()

        run_result = subprocess.run(
            [command],
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