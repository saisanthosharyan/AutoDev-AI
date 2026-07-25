import shutil
import subprocess
import time
from pathlib import Path

from app.core.logger import logger


class JavaExecutor:
    """
    Executes Java projects.

    Supports:
    - Plain Java
    - Package-based Java
    - Maven
    - Gradle
    """

    COMPILE_TIMEOUT = 120
    EXECUTION_TIMEOUT = 60

    def run(self, project_path: str) -> dict:

        project = Path(project_path).resolve()

        if not project.exists():
            return self._result(
                False,
                "",
                f"Project does not exist: {project}",
                -1,
                0,
            )

        javac = shutil.which("javac")
        java = shutil.which("java")

        if javac is None:
            return self._result(
                False,
                "",
                "javac not found. Please install JDK.",
                -1,
                0,
            )

        if java is None:
            return self._result(
                False,
                "",
                "java executable not found.",
                -1,
                0,
            )

        logger.info("=" * 60)
        logger.info("Java Executor Started")
        logger.info("=" * 60)

        try:

            # -------------------------------
            # Maven
            # -------------------------------

            if (project / "pom.xml").exists():

                logger.info("Detected Maven project.")

                return self._run_command(
                    ["mvn", "test"],
                    project,
                )

            # -------------------------------
            # Gradle
            # -------------------------------

            if (
                (project / "build.gradle").exists()
                or (project / "build.gradle.kts").exists()
            ):

                logger.info("Detected Gradle project.")

                gradle = (
                    "gradlew.bat"
                    if (project / "gradlew.bat").exists()
                    else "gradlew"
                )

                return self._run_command(
                    [gradle, "test"],
                    project,
                )

            # -------------------------------
            # Plain Java
            # -------------------------------

            java_files = list(project.rglob("*.java"))

            if not java_files:

                return self._result(
                    False,
                    "",
                    "No Java source files found.",
                    -1,
                    0,
                )

            logger.info(f"Found {len(java_files)} Java files.")

            compile = subprocess.run(
                [
                    javac,
                    "-d",
                    "out",
                ] + [str(f.relative_to(project)) for f in java_files],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=self.COMPILE_TIMEOUT,
            )

            if compile.returncode != 0:

                return self._result(
                    False,
                    compile.stdout,
                    compile.stderr,
                    compile.returncode,
                    0,
                )

            main_class = self._find_main_class(project)

            if main_class is None:

                return self._result(
                    False,
                    "",
                    "Main class not found.",
                    -1,
                    0,
                )

            logger.info(f"Running {main_class}")

            start = time.time()

            run = subprocess.run(
                [
                    java,
                    "-cp",
                    "out",
                    main_class,
                ],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=self.EXECUTION_TIMEOUT,
            )

            end = time.time()

            return self._result(
                run.returncode == 0,
                run.stdout,
                run.stderr,
                run.returncode,
                round(end - start, 2),
            )

        except subprocess.TimeoutExpired:

            return self._result(
                False,
                "",
                "Java execution timed out.",
                -1,
                self.EXECUTION_TIMEOUT,
            )

        except Exception as e:

            logger.exception("Java execution failed.")

            return self._result(
                False,
                "",
                str(e),
                -1,
                0,
            )

        finally:

            logger.info("=" * 60)
            logger.info("Java Executor Finished")
            logger.info("=" * 60)

    def _find_main_class(self, project: Path):

        for file in project.rglob("*.java"):

            try:

                text = file.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

                if "public static void main" not in text:
                    continue

                package = ""

                for line in text.splitlines():

                    line = line.strip()

                    if line.startswith("package "):
                        package = (
                            line.replace("package", "")
                            .replace(";", "")
                            .strip()
                        )

                name = file.stem

                return f"{package}.{name}" if package else name

            except Exception:
                continue

        return None

    def _run_command(
        self,
        command: list[str],
        cwd: Path,
    ):

        start = time.time()

        process = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=self.COMPILE_TIMEOUT,
        )

        end = time.time()

        return self._result(
            process.returncode == 0,
            process.stdout,
            process.stderr,
            process.returncode,
            round(end - start, 2),
        )

    def _result(
        self,
        success,
        stdout,
        stderr,
        return_code,
        execution_time,
    ):

        return {
            "success": success,
            "stdout": stdout,
            "stderr": stderr,
            "return_code": return_code,
            "execution_time": execution_time,
        }