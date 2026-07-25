import json
import shutil
import subprocess
import time
from pathlib import Path

from app.core.logger import logger



class NodeExecutor:
    """
    Executes Node.js based projects.

    Supported:
    - React
    - Vite
    - Next.js
    - Express
    - NestJS
    - Plain Node.js
    """

    INSTALL_TIMEOUT = 300
    EXECUTION_TIMEOUT = 120
    
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

        logger.info("=" * 60)
        logger.info("Node Executor Started")
        logger.info("=" * 60)

        node_path = shutil.which("node")
        npm_path = shutil.which("npm")

        if node_path is None:
            return self._result(
                False,
                "",
                "Node.js not found in PATH.",
                -1,
                0,
            )

        if npm_path is None:
            return self._result(
                False,
                "",
                "npm not found in PATH.",
                -1,
                0,
            )

        logger.info(f"Node executable : {node_path}")
        logger.info(f"NPM executable  : {npm_path}")

        package_json = project / "package.json"

        try:

            if package_json.is_file():

                package = self._read_package(package_json)

                install_result = self._install_dependencies(
                    project,
                    npm_path,
                )

                if install_result is not None:
                    return install_result

                command = self._select_command(
                    package,
                    project,
                    npm_path,
                    node_path,
                )

            else:

                command = self._fallback_command(
                    project,
                    node_path,
                )

            return self._execute(project, command)
        

        except RuntimeError as e:

            return self._result(
                False,
                "",
                str(e),
                -1,
                0,
            )   
        finally:

            logger.info("=" * 60)
            logger.info("Node Executor Finished")
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

    def _read_package(self, package_json: Path):

        try:
            with open(package_json, "r", encoding="utf-8") as file:
                package = json.load(file)

                if not isinstance(package, dict):
                    raise RuntimeError("Invalid package.json")

            logger.info("package.json loaded successfully.")
            return package

        except Exception as e:
            logger.exception("Failed to read package.json")
            raise RuntimeError(str(e))

    def _install_dependencies(
        self,
        project: Path,
        npm_path: str,
    ):

        node_modules = project / "node_modules"

        if node_modules.exists() and node_modules.is_dir():
            logger.info("Dependencies already installed.")
            return None

        logger.info("Installing Node dependencies...")

        start = time.time()

        try:

            process = subprocess.run(
                [npm_path, "install"],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=self.INSTALL_TIMEOUT,
            )

            end = time.time()

            if process.stdout:
                logger.info(process.stdout)

            if process.stderr:
                logger.error(process.stderr)

            if process.returncode != 0:
                return self._result(
                    False,
                    process.stdout,
                    process.stderr,
                    process.returncode,
                    round(end - start, 2),
                )

            logger.info(
                f"Dependencies installed successfully in {round(end - start, 2)} seconds."
            )

            return None

        except subprocess.TimeoutExpired:
            return self._result(
                False,
                "",
                "npm install timed out.",
                -1,
                self.INSTALL_TIMEOUT,
            )

        except Exception as e:
            logger.exception("Dependency installation failed.")

            return self._result(
                False,
                "",
                str(e),
                -1,
                0,
            )
            
    def _select_command(
        self,
        package: dict,
        project: Path,
        npm_path: str,
        node_path: str,
    ):

        scripts = package.get("scripts", {})

        dependencies = {
            **package.get("dependencies", {}),
            **package.get("devDependencies", {}),
        }

        logger.info("Detecting Node.js project type...")

        # -------------------------------------------------
        # Next.js
        # -------------------------------------------------

        if "next" in dependencies:

            logger.info("Detected Next.js project.")

            if "build" in scripts:
                return [npm_path, "run", "build"]

            if "dev" in scripts:
                return [npm_path, "run", "dev"]

        # -------------------------------------------------
        # React + Vite
        # -------------------------------------------------

        if "vite" in dependencies:

            logger.info("Detected Vite project.")

            if "build" in scripts:
                return [npm_path, "run", "build"]

            if "dev" in scripts:
                return [npm_path, "run", "dev"]

        # -------------------------------------------------
        # React (Create React App)
        # -------------------------------------------------

        if "react-scripts" in dependencies:

            logger.info("Detected React project.")

            if "build" in scripts:
                return [npm_path, "run", "build"]

            if "start" in scripts:
                return [npm_path, "run", "start"]

        # -------------------------------------------------
        # NestJS
        # -------------------------------------------------

        if "@nestjs/core" in dependencies:

            logger.info("Detected NestJS project.")

            if "build" in scripts:
                return [npm_path, "run", "build"]

            if "start" in scripts:
                return [npm_path, "run", "start"]

        # -------------------------------------------------
        # Express
        # -------------------------------------------------

        if "express" in dependencies:

            logger.info("Detected Express project.")

            if "start" in scripts:
                return [npm_path, "run", "start"]

            if "dev" in scripts:
                return [npm_path, "run", "dev"]

            server = project / "server.js"

            if server.exists():
                return [node_path, str(server)]

        # -------------------------------------------------
        # Generic package.json scripts
        # -------------------------------------------------

        priority = [
            "build",
            "start",
            "dev",
            "serve",
            "preview",
        ]

        for script in priority:

            if script in scripts:

                logger.info(f"Using npm script: {script}")

                return [
                    npm_path,
                    "run",
                    script,
                ]

        # -------------------------------------------------
        # Plain Node.js fallback
        # -------------------------------------------------

        return self._fallback_command(
            project,
            node_path,
        )
        
        
    def _fallback_command(
        self,
        project: Path,
        node_path: str,
    ):

        logger.info("Using fallback Node.js execution.")

        candidates = [
            "server.js",
            "index.js",
            "app.js",
            "main.js",
            "src/server.js",
            "src/index.js",
            "src/app.js",
            "src/main.js",
        ]

        for candidate in candidates:

            file = project / candidate

            if file.exists():

                logger.info(f"Found entry file: {candidate}")

                return [
                    node_path,
                    str(file),
                ]

        raise RuntimeError(
            "No runnable Node.js entry file found."
        )
    def _execute(
        self,
        project: Path,
        command: list[str],
    ):

        logger.info("=" * 60)
        logger.info("Executing Node Project")
        logger.info("=" * 60)

        logger.info(f"Command: {' '.join(command)}")

        start = time.time()

        try:

            process = subprocess.run(
                command,
                cwd=project,
                capture_output=True,
                text=True,
                timeout=self.EXECUTION_TIMEOUT,
            )

            end = time.time()

            execution_time = round(end - start, 2)

            if process.stdout:
                logger.info(process.stdout)

            if process.stderr:
                logger.error(process.stderr)

            logger.info(
                f"Execution finished in {execution_time} seconds."
            )

            return self._result(
                success=process.returncode == 0,
                stdout=process.stdout,
                stderr=process.stderr,
                return_code=process.returncode,
                execution_time=execution_time,
            )

        except subprocess.TimeoutExpired:

            logger.error(
                f"Execution timed out after {self.EXECUTION_TIMEOUT} seconds."
            )

            return self._result(
                False,
                "",
                f"Execution timed out after {self.EXECUTION_TIMEOUT} seconds.",
                -1,
                self.EXECUTION_TIMEOUT,
            )

        except Exception as e:

            logger.exception("Unexpected execution error.")

            return self._result(
                False,
                "",
                str(e),
                -1,
                0,
            )