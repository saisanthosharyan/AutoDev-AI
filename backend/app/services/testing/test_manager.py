from pathlib import Path

from app.core.logger import logger

from app.services.testing.python_test_runner import PythonTestRunner
from app.services.testing.node_test_runner import NodeTestRunner
from app.services.testing.java_test_runner import JavaTestRunner
from app.services.testing.cpp_test_runner import CPPTestRunner


class TestManager:
    """
    Detects the project type and runs the appropriate test runner.
    """

    def __init__(self):
        self.runners = {
            "python": PythonTestRunner(),
            "node": NodeTestRunner(),
            "java": JavaTestRunner(),
            "cpp": CPPTestRunner(),
        }

    def detect_project_type(self, project_path: str) -> str:
        project = Path(project_path)

        # Python
        if (
            (project / "requirements.txt").exists()
            or (project / "pyproject.toml").exists()
            or list(project.rglob("*.py"))
        ):
            return "python"

        # Node.js
        if (project / "package.json").exists():
            return "node"

        # Java
        if list(project.rglob("*.java")):
            return "java"

        # C++
        if list(project.rglob("*.cpp")):
            return "cpp"

        return "unknown"

    def run(self, project_path: str):
        """
        Run tests for the detected project type.
        """

        project_type = self.detect_project_type(project_path)

        logger.info(
            f"Running tests for {project_type} project..."
        )

        runner = self.runners.get(project_type)

        if runner is None:

            logger.warning(
                "No supported test runner found."
            )

            return {
                "success": False,
                "stdout": "",
                "stderr": f"No supported test runner for '{project_type}' project.",
                "return_code": -1,
                "execution_time": 0,
            }

        try:
            return runner.run(project_path)

        except Exception as e:

            logger.exception(
                "Test execution failed."
            )

            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "execution_time": 0,
            }