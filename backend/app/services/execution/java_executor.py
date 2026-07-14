import subprocess
from pathlib import Path


class JavaExecutor:

    def run(self, project_path: str):

        project = Path(project_path)

        # Search for Java files recursively
        java_files = list(project.rglob("*.java"))

        if not java_files:
            return {
                "success": False,
                "stdout": "",
                "stderr": "No Java file found.",
                "return_code": -1,
            }

        main = java_files[0]

        # Compile
        compile_result = subprocess.run(
            ["javac", str(main)],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if compile_result.returncode != 0:
            return {
                "success": False,
                "stdout": compile_result.stdout,
                "stderr": compile_result.stderr,
                "return_code": compile_result.returncode,
            }

        # Run
        run_result = subprocess.run(
            ["java", main.stem],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=60,
        )

        return {
            "success": run_result.returncode == 0,
            "stdout": run_result.stdout,
            "stderr": run_result.stderr,
            "return_code": run_result.returncode,
        }