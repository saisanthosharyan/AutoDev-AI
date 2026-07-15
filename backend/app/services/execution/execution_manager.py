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
        # Python Project
        # -------------------------
        if (
            (project / "requirements.txt").exists()
            or (project / "pyproject.toml").exists()
            or (project / "main.py").exists()
            or (project / "app.py").exists()
            or (project / "manage.py").exists()
        ):
            logger.info("Detected Python project.")
            return "python"

        # -------------------------
        # Node Project
        # -------------------------
        if (project / "package.json").exists():
            logger.info("Detected Node project.")
            return "node"

        # -------------------------
        # Java Project
        # -------------------------
        if list(project.rglob("*.java")):
            logger.info("Detected Java project.")
            return "java"

        # -------------------------
        # C++ Project
        # -------------------------
        if list(project.rglob("*.cpp")):
            logger.info("Detected C++ project.")
            return "cpp"

        # -------------------------
        # Docker Project
        # -------------------------
        if (project / "Dockerfile").exists():
            logger.info("Detected Docker project.")
            return "docker"

        logger.warning("Unknown project type.")
        return "unknown"

    def run(self, project_path: str):

        logger.info(f"Detecting project type: {project_path}")

        project_type = self.detect_project_type(project_path)

        if project_type == "python":
            logger.info("Running Python executor...")
            return self.python.run(project_path)

        if project_type == "node":
            logger.info("Running Node executor...")
            return self.node.run(project_path)

        if project_type == "java":
            logger.info("Running Java executor...")
            return self.java.run(project_path)

        if project_type == "cpp":
            logger.info("Running C++ executor...")
            return self.cpp.run(project_path)

        if project_type == "docker":
            logger.info("Running Docker executor...")
            return self.docker.run(project_path)

        logger.warning("No executor available.")

        return {
            "success": False,
            "stdout": "",
            "stderr": "Unknown project type.",
            "return_code": -1,
        }