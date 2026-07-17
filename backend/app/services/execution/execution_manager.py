from pathlib import Path

from app.core.logger import logger

from app.services.execution.python_executor import PythonExecutor
from app.services.execution.node_executor import NodeExecutor
from app.services.execution.java_executor import JavaExecutor
from app.services.execution.cpp_executor import CPPExecutor
from app.services.execution.docker_executor import DockerExecutor


class ExecutionManager:

    def __init__(self):
        self.python = PythonExecutor()
        self.node = NodeExecutor()
        self.java = JavaExecutor()
        self.cpp = CPPExecutor()
        self.docker = DockerExecutor()

    def detect_project_type(self, project_path: str):

        project = Path(project_path)

        # -------------------------
        # Python (Highest Priority)
        # -------------------------

        if (
            (project / "requirements.txt").exists()
            or (project / "pyproject.toml").exists()
            or list(project.rglob("*.py"))
        ):
            logger.info("Detected Python project.")
            return "python"

        # -------------------------
        # Node
        # -------------------------

        if (project / "package.json").exists():
            logger.info("Detected Node project.")
            return "node"

        # -------------------------
        # Java
        # -------------------------

        if list(project.rglob("*.java")):
            logger.info("Detected Java project.")
            return "java"

        # -------------------------
        # C++
        # -------------------------

        if list(project.rglob("*.cpp")):
            logger.info("Detected C++ project.")
            return "cpp"

        # -------------------------
        # Docker (Lowest Priority)
        # -------------------------

        if (project / "Dockerfile").exists():
            logger.info("Detected Docker project.")
            return "docker"

        logger.warning("Unknown project type.")
        return "unknown"

    def run(self, project_path: str):

        logger.info(f"Detecting project type: {project_path}")

        project_type = self.detect_project_type(project_path)

        logger.info(f"Project type: {project_type}")

        executors = {
            "python": self.python,
            "node": self.node,
            "java": self.java,
            "cpp": self.cpp,
            "docker": self.docker,
        }

        executor = executors.get(project_type)

        if executor is None:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Unsupported project type: {project_type}",
                "return_code": -1,
                "execution_time": 0,
            }

        try:
            return executor.run(project_path)

        except Exception as e:

            logger.exception("Execution Manager crashed.")

            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "execution_time": 0,
            }