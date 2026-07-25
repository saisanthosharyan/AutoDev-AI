from pathlib import Path
import shutil
import time

from app.core.logger import logger

from app.services.execution.python_executor import PythonExecutor
from app.services.execution.node_executor import NodeExecutor
from app.services.execution.java_executor import JavaExecutor
from app.services.execution.cpp_executor import CPPExecutor
from app.services.execution.docker_executor import DockerExecutor
from app.services.execution.execution_logger import ExecutionLogger


class ExecutionManager:
    """
    Detects the generated project type and executes it
    using the appropriate executor.
    """

    def __init__(self):

        self.executors = {
            "python": PythonExecutor(),
            "node": NodeExecutor(),
            "java": JavaExecutor(),
            "cpp": CPPExecutor(),
            "docker": DockerExecutor(),
        }

    # --------------------------------------------------
    # Detect Project Type
    # --------------------------------------------------

    def detect_project_type(self, project_path: str) -> str:

        project = Path(project_path).resolve()

        if not project.exists():
            raise FileNotFoundError(
                f"Project directory does not exist: {project}"
            )

        logger.info(f"Detecting project type: {project}")

        # -----------------------------
        # Python
        # -----------------------------

        if (
            (project / "requirements.txt").exists()
            or (project / "pyproject.toml").exists()
            or any(project.rglob("*.py"))
        ):
            logger.info("Detected Python project.")
            return "python"

        # -----------------------------
        # Node
        # -----------------------------

        if (project / "package.json").exists():
            logger.info("Detected Node.js project.")
            return "node"

        # -----------------------------
        # Java
        # -----------------------------

        if any(project.rglob("*.java")):
            logger.info("Detected Java project.")
            return "java"

        # -----------------------------
        # C++
        # -----------------------------

        if any(project.rglob("*.cpp")):
            logger.info("Detected C++ project.")
            return "cpp"

        # -----------------------------
        # Docker
        # -----------------------------

        if (
            (project / "Dockerfile").exists()
            and shutil.which("docker")
        ):
            logger.info("Detected Docker project.")
            return "docker"

        logger.warning("Unknown project type.")
        return "unknown"

    # --------------------------------------------------
    # Execute
    # --------------------------------------------------

    def run(self, project_path: str):

        logger.info("=" * 60)
        logger.info("Execution Manager Started")
        logger.info("=" * 60)

        start = time.time()

        try:

            project_type = self.detect_project_type(project_path)

            executor = self.executors.get(project_type)

            if executor is None:

                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Unsupported project type: {project_type}",
                    "return_code": -1,
                    "execution_time": 0,
                }

            logger.info(f"Using executor: {project_type}")

            result = executor.run(project_path)
            ExecutionLogger(project_path).save(result)
            # -----------------------------
            # Automatic Docker Fallback
            # -----------------------------

            if (
                project_type == "docker"
                and result.get("skip", False)
            ):

                logger.info(
                    "Docker unavailable. Falling back to Python executor..."
                )

                result = self.executors["python"].run(project_path)

            result.setdefault("success", False)
            result.setdefault("stdout", "")
            result.setdefault("stderr", "")
            result.setdefault("return_code", -1)

            result["execution_time"] = round(
                time.time() - start,
                2,
            )

            if result["success"]:

                logger.info("Execution completed successfully.")

            else:

                logger.warning("Execution failed.")
                logger.error(result["stderr"])

            return result

        except Exception as e:

            logger.exception("Execution Manager crashed.")

            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "execution_time": round(
                    time.time() - start,
                    2,
                ),
            }

        finally:

            logger.info("=" * 60)
            logger.info("Execution Manager Finished")
            logger.info("=" * 60)