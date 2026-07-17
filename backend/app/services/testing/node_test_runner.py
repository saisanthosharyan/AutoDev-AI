import json
import subprocess
import time
from pathlib import Path

from app.core.logger import logger


class NodeTestRunner:

    def run(self, project_path: str):

        project = Path(project_path)

        package_json = project / "package.json"

        if not package_json.exists():

            return {
                "success": False,
                "stdout": "",
                "stderr": "package.json not found.",
                "return_code": -1,
                "execution_time": 0,
            }

        # -----------------------------------------
        # Read package.json
        # -----------------------------------------

        try:

            package = json.loads(
                package_json.read_text(encoding="utf-8")
            )

        except Exception as e:

            return {
                "success": False,
                "stdout": "",
                "stderr": f"Invalid package.json: {e}",
                "return_code": -1,
                "execution_time": 0,
            }

        scripts = package.get("scripts", {})

        if "test" not in scripts:

            logger.warning("No test script found.")

            return {
                "success": True,
                "stdout": "No tests defined.",
                "stderr": "",
                "return_code": 0,
                "execution_time": 0,
            }

        # -----------------------------------------
        # Install dependencies
        # -----------------------------------------

        logger.info("Installing Node dependencies...")

        install = subprocess.run(
            [
                "npm",
                "install",
            ],
            cwd=project,
            capture_output=True,
            text=True,
        )

        if install.returncode != 0:

            return {
                "success": False,
                "stdout": install.stdout,
                "stderr": install.stderr,
                "return_code": install.returncode,
                "execution_time": 0,
            }

        logger.info("Running npm test...")

        start = time.time()

        try:

            process = subprocess.run(
                [
                    "npm",
                    "test",
                ],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=120,
            )

            end = time.time()

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
                "stderr": "npm test timed out.",
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