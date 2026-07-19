import shutil
import subprocess
import time
from pathlib import Path

from app.core.logger import logger


class NodeExecutor:

    def run(self, project_path: str):

        project = Path(project_path)

        if not project.exists():
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Project does not exist: {project}",
                "return_code": -1,
                "execution_time": 0,
            }

        # -------------------------------------------------
        # Check Node installation
        # -------------------------------------------------

        node_path = shutil.which("node")
        npm_path = shutil.which("npm")

        if node_path is None:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Node.js is not installed or not found in PATH.",
                "return_code": -1,
                "execution_time": 0,
            }

        if npm_path is None:
            return {
                "success": False,
                "stdout": "",
                "stderr": "npm is not installed or not found in PATH.",
                "return_code": -1,
                "execution_time": 0,
            }

        logger.info(f"Node executable: {node_path}")
        logger.info(f"NPM executable : {npm_path}")

        # -------------------------------------------------
        # Install dependencies
        # -------------------------------------------------

        package_json = project / "package.json"

        if package_json.exists():

            logger.info("Installing Node dependencies...")

            try:

                install = subprocess.run(
                    [npm_path, "install"],
                    cwd=project,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if install.returncode != 0:

                    return {
                        "success": False,
                        "stdout": install.stdout,
                        "stderr": install.stderr,
                        "return_code": install.returncode,
                        "execution_time": 0,
                    }

            except subprocess.TimeoutExpired:

                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "npm install timed out.",
                    "return_code": -1,
                    "execution_time": 300,
                }

            except Exception as e:

                return {
                    "success": False,
                    "stdout": "",
                    "stderr": str(e),
                    "return_code": -1,
                    "execution_time": 0,
                }

        # -------------------------------------------------
        # Detect entry file
        # -------------------------------------------------

        candidates = [
            "index.js",
            "server.js",
            "app.js",
            "main.js",
            "src/index.js",
            "src/server.js",
            "src/app.js",
            "src/main.js",
        ]

        main_file = None

        for candidate in candidates:

            file = project / candidate

            if file.exists():

                main_file = file

                break

        if main_file is None:

            return {
                "success": False,
                "stdout": "",
                "stderr": "No runnable Node.js entry file found.",
                "return_code": -1,
                "execution_time": 0,
            }

        logger.info(f"Running {main_file}")

        # -------------------------------------------------
        # Execute project
        # -------------------------------------------------

        start = time.time()

        try:

            process = subprocess.run(
                [node_path, str(main_file)],
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

        except subprocess.TimeoutExpired:

            return {
                "success": False,
                "stdout": "",
                "stderr": "Node execution timed out.",
                "return_code": -1,
                "execution_time": 60,
            }

        except Exception as e:

            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "execution_time": 0,
            }