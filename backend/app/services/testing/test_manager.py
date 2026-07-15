from pathlib import Path

from app.core.logger import logger

from app.services.testing.python_test_runner import PythonTestRunner
from app.services.testing.node_test_runner import NodeTestRunner
from app.services.testing.java_test_runner import JavaTestRunner
from app.services.testing.cpp_test_runner import CPPTestRunner


class TestManager:

    def __init__(self):
        self.python = PythonTestRunner()
        self.node = NodeTestRunner()
        self.java = JavaTestRunner()
        self.cpp = CPPTestRunner()

    def detect_project_type(self, project_path: str):

        project = Path(project_path)

        if (
            (project / "requirements.txt").exists()
            or (project / "pyproject.toml").exists()
        ):
            return "python"

        if (project / "package.json").exists():
            return "node"

        if list(project.rglob("*.java")):
            return "java"

        if list(project.rglob("*.cpp")):
            return "cpp"

        return "unknown"

    def run(self, project_path: str):

        project_type = self.detect_project_type(project_path)

        logger.info(f"Running tests for {project_type} project...")

        if project_type == "python":
            return self.python.run(project_path)

        if project_type == "node":
            return self.node.run(project_path)

        if project_type == "java":
            return self.java.run(project_path)

        if project_type == "cpp":
            return self.cpp.run(project_path)

        return {
            "success": False,
            "stdout": "",
            "stderr": "No supported test runner found.",
            "return_code": -1,
            "execution_time": 0,
        }