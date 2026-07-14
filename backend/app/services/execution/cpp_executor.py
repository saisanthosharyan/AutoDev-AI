import subprocess
from pathlib import Path


class CPPExecutor:

    def run(self, project_path: str):

        project = Path(project_path)

        cpp_files = list(project.glob("*.cpp"))

        if not cpp_files:
            return {
                "success": False,
                "stdout": "",
                "stderr": "No C++ file found."
            }

        source = cpp_files[0]

        compile_result = subprocess.run(
            [
                "g++",
                source.name,
                "-o",
                "program"
            ],
            cwd=project,
            capture_output=True,
            text=True
        )

        if compile_result.returncode != 0:
            return {
                "success": False,
                "stdout": compile_result.stdout,
                "stderr": compile_result.stderr
            }

        executable = "program.exe" if __import__("os").name == "nt" else "./program"

        run_result = subprocess.run(
            [executable],
            cwd=project,
            capture_output=True,
            text=True
        )

        return {
            "success": run_result.returncode == 0,
            "stdout": run_result.stdout,
            "stderr": run_result.stderr
        }