import subprocess
import time
from pathlib import Path

from app.core.logger import logger


class NodeExecutor:

    def run(self, project_path: str):

        project = Path(project_path)

        # --------------------------
        # Install dependencies
        # --------------------------
        package_json = project / "package.json"

        if package_json.exists():

            logger.info("Installing Node dependencies...")

            subprocess.run(
                ["npm", "install"],
                cwd=project,
                capture_output=True,
                text=True,
            )

        # --------------------------
        # Find entry file
        # --------------------------
        candidates = [
            "index.js",
            "server.js",
            "app.js",
            "main.js",
        ]

        main_file = None

        for file in candidates:

            if (project / file).exists():

                main_file = project / file
                break

        if main_file is None:

            return {
                "success": False,
                "stdout": "",
                "stderr": "No runnable Node.js entry file found.",
                "return_code": -1,
                "execution_time": 0,
            }

        logger.info(f"Running {main_file.name}")

        start = time.time()

        process = subprocess.run(
            ["node", str(main_file)],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=60,
        )

        end = time.time()

        return {
            "success": process.returncode == 0,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "return_code": process.returncode,
            "execution_time": round(end - start, 2),
        }