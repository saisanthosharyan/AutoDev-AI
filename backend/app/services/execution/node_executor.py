import subprocess
import time
import json
from pathlib import Path


class NodeExecutor:

    def _install_dependencies(self, project: Path):

        package = project / "package.json"

        if not package.exists():
            return

        subprocess.run(
            ["npm", "install"],
            cwd=project,
            capture_output=True,
            text=True,
        )

    def _detect_framework(self, project: Path):

        package = project / "package.json"

        if not package.exists():
            return "Node"

        try:

            data = json.loads(package.read_text())

            deps = {}

            deps.update(data.get("dependencies", {}))
            deps.update(data.get("devDependencies", {}))

            if "express" in deps:
                return "Express"

            if "next" in deps:
                return "Next.js"

            if "react" in deps:
                return "React"

        except Exception:
            pass

        return "Node"

    def _find_entry(self, project: Path):

        candidates = [
            "index.js",
            "server.js",
            "app.js",
            "main.js",
        ]

        for name in candidates:
            for file in project.rglob(name):
                return file

        js_files = list(project.rglob("*.js"))

        if js_files:
            return js_files[0]

        return None

    def run(self, project_path: str):

        project = Path(project_path)

        framework = self._detect_framework(project)

        self._install_dependencies(project)

        package = project / "package.json"

        start = time.time()

        try:

            if package.exists():

                try:
                    data = json.loads(package.read_text())
                    scripts = data.get("scripts", {})

                    if "start" in scripts:
                        command = ["npm", "start"]

                    elif "dev" in scripts:
                        command = ["npm", "run", "dev"]

                    else:
                        entry = self._find_entry(project)

                        if entry is None:
                            raise FileNotFoundError("No entry file found.")

                        command = ["node", str(entry)]

                except Exception:

                    entry = self._find_entry(project)

                    if entry is None:
                        raise FileNotFoundError("No entry file found.")

                    command = ["node", str(entry)]

            else:

                entry = self._find_entry(project)

                if entry is None:
                    raise FileNotFoundError("No entry file found.")

                command = ["node", str(entry)]

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
                "language": "Node.js",
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
                "language": "Node.js",
                "framework": framework,
                "stdout": "",
                "stderr": "Execution timed out.",
                "return_code": -1,
                "execution_time": 60,
                "command": "",
            }

        except Exception as e:

            return {
                "success": False,
                "language": "Node.js",
                "framework": framework,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "execution_time": 0,
                "command": "",
            }