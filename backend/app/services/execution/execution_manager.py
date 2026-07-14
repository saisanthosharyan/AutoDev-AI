from pathlib import Path

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

        # Docker has highest priority
        if (project / "Dockerfile").exists():
            return "docker"

        # Node.js
        if (project / "package.json").exists():
            return "node"

        # Java
        if list(project.rglob("*.java")):
            return "java"

        # C++
        if list(project.rglob("*.cpp")):
            return "cpp"

        # Python
        if (
            (project / "requirements.txt").exists()
            or (project / "pyproject.toml").exists()
            or (project / "manage.py").exists()
            or list(project.rglob("*.py"))
        ):
            return "python"

        return "unknown"

    def run(self, project_path: str):

        project_type = self.detect_project_type(project_path)

        if project_type == "python":
            result = self.python.run(project_path)

        elif project_type == "node":
            result = self.node.run(project_path)

        elif project_type == "java":
            result = self.java.run(project_path)

        elif project_type == "cpp":
            result = self.cpp.run(project_path)

        elif project_type == "docker":
            result = self.docker.run(project_path)

        else:
            result = {
                "success": False,
                "language": "Unknown",
                "framework": "Unknown",
                "stdout": "",
                "stderr": "Unsupported project type.",
                "return_code": -1,
                "execution_time": 0,
                "command": "",
            }

        result["project_type"] = project_type

        return result