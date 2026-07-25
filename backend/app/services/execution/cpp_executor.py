import os
import shutil
import subprocess
import time
from pathlib import Path

from app.core.logger import logger


class CPPExecutor:
    """
    Executes C++ projects by compiling and running
    the first discovered .cpp source file.
    """

    EXECUTION_TIMEOUT = 60

    def run(self, project_path: str) -> dict:

        project = Path(project_path).resolve()

        if not project.exists():
            return self._result(
                False,
                "",
                f"Project does not exist: {project}",
                -1,
                0,
            )

        compiler = shutil.which("g++")

        if compiler is None:
            return self._result(
                False,
                "",
                "g++ compiler not found in PATH.",
                -1,
                0,
            )

        cpp_files = list(project.rglob("*.cpp"))

        if not cpp_files:
            return self._result(
                False,
                "",
                "No C++ source files found.",
                -1,
                0,
            )

        source = cpp_files[0]

        executable = (
            "program.exe"
            if os.name == "nt"
            else "program"
        )

        logger.info("=" * 60)
        logger.info("C++ Executor Started")
        logger.info("=" * 60)

        logger.info(f"Compiling: {source}")

        try:

            compile_result = subprocess.run(
                [
                    compiler,
                    source.name,
                    "-o",
                    executable,
                ],
                cwd=source.parent,
                capture_output=True,
                text=True,
            )

            if compile_result.returncode != 0:

                logger.error("Compilation failed.")

                return self._result(
                    False,
                    compile_result.stdout,
                    compile_result.stderr,
                    compile_result.returncode,
                    0,
                )

            logger.info("Compilation successful.")

            command = (
                executable
                if os.name == "nt"
                else f"./{executable}"
            )

            logger.info(f"Running: {command}")

            start = time.time()

            run_result = subprocess.run(
                [command],
                cwd=source.parent,
                capture_output=True,
                text=True,
                timeout=self.EXECUTION_TIMEOUT,
            )

            execution_time = round(
                time.time() - start,
                2,
            )

            if run_result.stdout:
                logger.info(run_result.stdout)

            if run_result.stderr:
                logger.error(run_result.stderr)

            return self._result(
                run_result.returncode == 0,
                run_result.stdout,
                run_result.stderr,
                run_result.returncode,
                execution_time,
            )

        except subprocess.TimeoutExpired:

            logger.error("Execution timed out.")

            return self._result(
                False,
                "",
                f"Execution timed out after {self.EXECUTION_TIMEOUT} seconds.",
                -1,
                self.EXECUTION_TIMEOUT,
            )

        except Exception as e:

            logger.exception("C++ execution failed.")

            return self._result(
                False,
                "",
                str(e),
                -1,
                0,
            )

        finally:

            logger.info("=" * 60)
            logger.info("C++ Executor Finished")
            logger.info("=" * 60)

    def _result(
        self,
        success: bool,
        stdout: str,
        stderr: str,
        return_code: int,
        execution_time: float,
    ) -> dict:

        return {
            "success": success,
            "stdout": stdout,
            "stderr": stderr,
            "return_code": return_code,
            "execution_time": execution_time,
        }