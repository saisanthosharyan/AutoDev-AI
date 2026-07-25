import shutil
import subprocess
import time
from pathlib import Path

from app.core.logger import logger


class CPPTestRunner:

    COMPILE_TIMEOUT = 120

    def run(self, project_path: str):

        project = Path(project_path).resolve()

        logger.info("=" * 60)
        logger.info("C++ Test Runner Started")
        logger.info("=" * 60)

        gpp = shutil.which("g++")

        if gpp is None:
            return self._result(
                False,
                "",
                "g++ compiler not found in PATH.",
                -1,
                0,
            )

        logger.info(f"g++ executable : {gpp}")

        cpp_files = list(project.rglob("*.cpp"))

        if not cpp_files:
            return self._result(
                False,
                "",
                "No C++ files found.",
                -1,
                0,
            )

        logger.info(f"Found {len(cpp_files)} C++ file(s).")

        output_file = project / "test_program"

        command = [
            gpp,
            *[str(f) for f in cpp_files],
            "-o",
            str(output_file),
        ]

        logger.info(f"Compile command: {' '.join(command)}")

        start = time.time()

        try:

            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.COMPILE_TIMEOUT,
            )

            execution_time = round(time.time() - start, 2)

            if process.stdout:
                logger.info(process.stdout)

            if process.stderr:
                logger.error(process.stderr)

            logger.info(
                f"Compilation finished in {execution_time} seconds."
            )

            return self._result(
                success=process.returncode == 0,
                stdout=process.stdout,
                stderr=process.stderr,
                return_code=process.returncode,
                execution_time=execution_time,
            )

        except subprocess.TimeoutExpired:

            logger.error("C++ compilation timed out.")

            return self._result(
                False,
                "",
                "Compilation timed out.",
                -1,
                self.COMPILE_TIMEOUT,
            )

        except Exception:

            logger.exception("C++ compilation failed.")

            return self._result(
                False,
                "",
                "Unexpected error during compilation.",
                -1,
                0,
            )

        finally:

            logger.info("=" * 60)
            logger.info("C++ Test Runner Finished")
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