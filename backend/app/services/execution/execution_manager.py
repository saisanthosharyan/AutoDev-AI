from pathlib import Path

from app.core.logger import logger

from app.services.execution.python_executor import PythonExecutor
from app.services.execution.node_executor import NodeExecutor
from app.services.execution.java_executor import JavaExecutor
from app.services.execution.cpp_executor import CPPExecutor
from app.services.execution.docker_executor import DockerExecutor


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

        logger.info(f"Detecting project type inside: {project}")

        # --------------------------------------------------
        # Python (Highest Priority)
        # --------------------------------------------------

        if (
            (project / "requirements.txt").exists()
            or (project / "pyproject.toml").exists()
            or any(project.rglob("*.py"))
        ):
            logger.info("Detected Python project.")
            return "python"

        # --------------------------------------------------
        # Node.js
        # --------------------------------------------------

        if (project / "package.json").exists():
            logger.info("Detected Node.js project.")
            return "node"

        # --------------------------------------------------
        # Java
        # --------------------------------------------------

        if any(project.rglob("*.java")):
            logger.info("Detected Java project.")
            return "java"

        # --------------------------------------------------
        # C++
        # --------------------------------------------------

        if any(project.rglob("*.cpp")):
            logger.info("Detected C++ project.")
            return "cpp"

        # --------------------------------------------------
        # Docker (Fallback)
        # --------------------------------------------------

        if (project / "Dockerfile").exists():
            logger.info("Detected Docker project.")
            return "docker"

        logger.warning(f"Unable to detect project type: {project}")

        return "unknown"

    # --------------------------------------------------
    # Execute Project
    # --------------------------------------------------

    def run(self, project_path: str):

        logger.info("=" * 60)
        logger.info("Execution Manager Started")
        logger.info("=" * 60)

        try:

            project_type = self.detect_project_type(project_path)

            logger.info(f"Selected executor: {project_type}")

            executor = self.executors.get(project_type)

            if executor is None:
                logger.error(
                    f"No executor available for '{project_type}'"
                )

                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Unsupported project type: {project_type}",
                    "return_code": -1,
                    "execution_time": 0,
                }

            result = executor.run(project_path)

            logger.info(
                f"{project_type.capitalize()} execution finished."
            )

            if result.get("success"):
                logger.info("Project executed successfully.")
            else:
                logger.warning("Project execution failed.")

            return result

        except Exception as e:

            logger.exception("Execution Manager crashed.")

            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "execution_time": 0,
            }

        finally:

            logger.info("=" * 60)
            logger.info("Execution Manager Finished")
            logger.info("=" * 60)