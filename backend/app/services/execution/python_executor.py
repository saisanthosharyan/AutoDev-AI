import subprocess
import time
from pathlib import Path


class PythonExecutor:

    def _find_entry_file(self, project: Path):
        """
        Find the best Python entry file.
        """

        priority = [
            "main.py",
            "app.py",
            "run.py",
            "manage.py",
        ]

        # Look for common filenames recursively
        for name in priority:
            for file in project.rglob(name):
                return file

        # Fallback to first Python file
        py_files = list(project.rglob("*.py"))

        if py_files:
            return py_files[0]

        return None

    def _detect_framework(self, project: Path):

        if (project / "manage.py").exists():
            return "Django"

        for file in project.rglob("*.py"):

            try:
                content = file.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

                if "FastAPI(" in content:
                    return "FastAPI"

                if "Flask(" in content:
                    return "Flask"

            except Exception:
                pass

        return "Python"

    def _install_dependencies(self, project: Path):

        requirements = project / "requirements.txt"

        if not requirements.exists():
            return

        subprocess.run(
            [
                "pip",
                "install",
                "-r",
                "requirements.txt",
            ],
            cwd=project,
            capture_output=True,
            text=True,
        )

    def run(self, project_path: str):

        project = Path(project_path)

        framework = self._detect_framework(project)

        self._install_dependencies(project)

        main_file = self._find_entry_file(project)

        if main_file is None:

            return {
                "success": False,
                "language": "Python",
                "framework": framework,
                "stdout": "",
                "stderr": "No runnable Python file found.",
                "return_code": -1,
                "execution_time": 0,
                "command": "",
            }

        command = ["python", str(main_file)]

        start = time.time()

        try:

            process = subprocess.run(
                command,
                cwd=project,
                capture_output=True,
                text=True,
                timeout=60,
            )

            elapsed = round(time.time() - start, 2)

            return {
                "success": process.returncode == 0,
                "language": "Python",
                "framework": framework,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode,
                "execution_time": elapsed,
                "command": " ".join(command),
            }

        except subprocess.TimeoutExpired:

            return {
                "success": False,
                "language": "Python",
                "framework": framework,
                "stdout": "",
                "stderr": "Execution timed out after 60 seconds.",
                "return_code": -1,
                "execution_time": 60,
                "command": " ".join(command),
            }

        except Exception as e:

            return {
                "success": False,
                "language": "Python",
                "framework": framework,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "execution_time": 0,
                "command": " ".join(command),
            }