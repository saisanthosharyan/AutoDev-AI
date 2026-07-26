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

    Supported:
        - Python
        - Node.js
        - Java
        - C++
        - Docker
    """

    def __init__(self):

        self.executors = {
            "python": PythonExecutor(),
            "node": NodeExecutor(),
            "java": JavaExecutor(),
            "cpp": CPPExecutor(),
            "docker": DockerExecutor(),
        }

    # ==========================================================
    # PROJECT TYPE DETECTION
    # ==========================================================

    def detect_project_type(self, project_path: str) -> str:

        project = Path(project_path).resolve()

        if not project.exists():
            raise FileNotFoundError(
                f"Project directory does not exist: {project}"
            )

        if not project.is_dir():
            raise NotADirectoryError(
                f"Project path is not a directory: {project}"
            )

        logger.info(
            f"Detecting project type: {project}"
        )

        # ------------------------------------------------------
        # Docker should be checked FIRST.
        # ------------------------------------------------------

        dockerfile = project / "Dockerfile"

        if dockerfile.exists():
            if shutil.which("docker"):
                logger.info(
                    "Dockerfile detected and Docker is available."
                )
                return "docker"

            logger.warning(
                "Dockerfile detected but Docker is unavailable."
            )

        # ------------------------------------------------------
        # Node.js
        # ------------------------------------------------------

        if (project / "package.json").exists():

            logger.info(
                "Detected Node.js project."
            )

            return "node"

        # ------------------------------------------------------
        # Python
        # ------------------------------------------------------

        if (
            (project / "requirements.txt").exists()
            or (project / "pyproject.toml").exists()
            or (project / "setup.py").exists()
            or any(project.rglob("*.py"))
        ):

            logger.info(
                "Detected Python project."
            )

            return "python"

        # ------------------------------------------------------
        # Java
        # ------------------------------------------------------

        if any(project.rglob("*.java")):

            logger.info(
                "Detected Java project."
            )

            return "java"

        # ------------------------------------------------------
        # C++
        # ------------------------------------------------------

        if (
            any(project.rglob("*.cpp"))
            or any(project.rglob("*.cc"))
            or any(project.rglob("*.cxx"))
        ):

            logger.info(
                "Detected C++ project."
            )

            return "cpp"

        logger.warning(
            "Unable to determine project type."
        )

        return "unknown"

    # ==========================================================
    # EXECUTE
    # ==========================================================

    def run(self, project_path: str) -> dict:

        logger.info("=" * 60)
        logger.info("Execution Manager Started")
        logger.info("=" * 60)

        start_time = time.time()

        result = {
            "success": False,
            "stdout": "",
            "stderr": "",
            "return_code": -1,
            "execution_time": 0,
            "project_type": "unknown",
        }

        try:

            # --------------------------------------------------
            # Detect project
            # --------------------------------------------------

            project_type = self.detect_project_type(
                project_path
            )

            result["project_type"] = project_type

            if project_type == "unknown":

                result["stderr"] = (
                    "Unable to detect generated project type."
                )

                logger.error(
                    result["stderr"]
                )

                return result

            executor = self.executors.get(
                project_type
            )

            if executor is None:

                result["stderr"] = (
                    f"No executor registered for "
                    f"project type: {project_type}"
                )

                logger.error(
                    result["stderr"]
                )

                return result

            logger.info(
                f"Using executor: {project_type}"
            )

            # --------------------------------------------------
            # Execute project
            # --------------------------------------------------

            execution_result = executor.run(
                project_path
            )

            if execution_result is None:

                execution_result = {
                    "success": False,
                    "stdout": "",
                    "stderr": (
                        "Executor returned no result."
                    ),
                    "return_code": -1,
                }

            # --------------------------------------------------
            # Docker fallback
            # --------------------------------------------------

            if (
                project_type == "docker"
                and execution_result.get("skip", False)
            ):

                logger.warning(
                    "Docker execution skipped."
                )

                logger.info(
                    "Attempting fallback project detection."
                )

                fallback_type = self._detect_non_docker_type(
                    project_path
                )

                if fallback_type:

                    fallback_executor = self.executors.get(
                        fallback_type
                    )

                    if fallback_executor:

                        logger.info(
                            f"Using fallback executor: "
                            f"{fallback_type}"
                        )

                        execution_result = (
                            fallback_executor.run(
                                project_path
                            )
                        )

                        result["project_type"] = (
                            fallback_type
                        )

            # --------------------------------------------------
            # Normalize result
            # --------------------------------------------------

            result.update({
                "success": bool(
                    execution_result.get(
                        "success",
                        False,
                    )
                ),
                "stdout": (
                    execution_result.get(
                        "stdout",
                        "",
                    )
                    or ""
                ),
                "stderr": (
                    execution_result.get(
                        "stderr",
                        "",
                    )
                    or ""
                ),
                "return_code": execution_result.get(
                    "return_code",
                    -1,
                ),
            })

            return result

        except Exception as e:

            logger.exception(
                "Execution Manager crashed."
            )

            result.update({
                "success": False,
                "stderr": str(e),
                "return_code": -1,
            })

            return result

        finally:

            result["execution_time"] = round(
                time.time() - start_time,
                2,
            )

            # --------------------------------------------------
            # Save execution log
            # --------------------------------------------------

            try:

                ExecutionLogger(
                    project_path
                ).save(result)

            except Exception:

                logger.exception(
                    "Failed to save execution log."
                )

            # --------------------------------------------------
            # Logging
            # --------------------------------------------------

            if result["success"]:

                logger.info(
                    "Execution completed successfully."
                )

            else:

                logger.warning(
                    "Execution failed."
                )

                if result.get("stderr"):

                    logger.error(
                        result["stderr"]
                    )

            logger.info("=" * 60)
            logger.info("Execution Manager Finished")
            logger.info("=" * 60)

    # ==========================================================
    # FALLBACK DETECTION
    # ==========================================================

    def _detect_non_docker_type(
        self,
        project_path: str,
    ) -> str | None:

        project = Path(
            project_path
        ).resolve()

        # Node first
        if (project / "package.json").exists():

            return "node"

        # Python
        if (
            (project / "requirements.txt").exists()
            or (project / "pyproject.toml").exists()
            or (project / "setup.py").exists()
            or any(project.rglob("*.py"))
        ):

            return "python"

        # Java
        if any(project.rglob("*.java")):

            return "java"

        # C++
        if (
            any(project.rglob("*.cpp"))
            or any(project.rglob("*.cc"))
            or any(project.rglob("*.cxx"))
        ):

            return "cpp"

        return None