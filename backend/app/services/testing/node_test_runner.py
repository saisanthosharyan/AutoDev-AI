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

        logger.info("Installing Node test dependencies...")

        subprocess.run(
            ["npm", "install"],
            cwd=project,
            capture_output=True,
            text=True,
        )

        logger.info("Running npm test...")

        start = time.time()

        process = subprocess.run(
            ["npm", "test"],
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