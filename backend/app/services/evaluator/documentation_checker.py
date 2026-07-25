from pathlib import Path

from app.core.logger import logger


class DocumentationChecker:
    """
    Evaluates project documentation quality.

    Checks for:

    - README.md
    - LICENSE
    - Python docstrings
    - Code comments

    Returns

    {
        "score": 90,
        "missing": [...],
        "found": [...]
    }
    """

    def check(self, project_path: str) ->dict:

        logger.info(
            "Checking project documentation..."
        )

        project = Path(project_path).resolve()

        if not project.exists():

            return {
                "score": 0,
                "found": [],
                "missing": [
                    "Project directory not found."
                ],
            }

        found = []
        missing = []

        # ------------------------------------------
        # README
        # ------------------------------------------

        readme = project / "README.md"

        if readme.exists():

            found.append("README.md")

            try:

                text = readme.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

                if len(text.strip()) < 100:

                    missing.append(
                        "README is too small."
                    )

            except Exception:

                missing.append(
                    "Unable to read README."
                )

        else:

            missing.append("README.md")

        # ------------------------------------------
        # LICENSE
        # ------------------------------------------

        licenses = [

            "LICENSE",
            "LICENSE.txt",
            "LICENSE.md",

        ]

        license_found = False

        for name in licenses:

            if (project / name).exists():

                found.append(name)

                license_found = True

                break

        if not license_found:

            missing.append("LICENSE")

        # ------------------------------------------
        # Source Files
        # ------------------------------------------

        extensions = {

            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".cpp",
            ".c",

        }

        ignored_dirs = {

            ".git",
            ".venv",
            "venv",
            "__pycache__",
            "node_modules",
            "build",
            "dist",

        }

        source_files = []

        for file in project.rglob("*"):

            if not file.is_file():
                continue

            if any(
                part in ignored_dirs
                for part in file.parts
            ):
                continue

            if file.suffix.lower() in extensions:

                source_files.append(file)

        comment_files = 0

        docstring_files = 0

        total_files = len(source_files)

        for file in source_files:

            try:

                content = file.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

            except Exception:

                continue

            # ----------------------------
            # Comments
            # ----------------------------

            if (

                "#" in content
                or "//" in content
                or "/*" in content

            ):

                comment_files += 1

            # ----------------------------
            # Python Docstrings
            # ----------------------------

            if file.suffix == ".py":

                if (

                    '"""' in content
                    or "'''" in content

                ):

                    docstring_files += 1

        # ------------------------------------------
        # Evaluate
        # ------------------------------------------

        if comment_files > 0:

            found.append(
                f"Comments ({comment_files} files)"
            )

        else:

            missing.append(
                "No code comments found."
            )

        if docstring_files > 0:

            found.append(
                f"Python docstrings ({docstring_files} files)"
            )

        elif any(
            f.suffix == ".py"
            for f in source_files
        ):

            missing.append(
                "Python docstrings missing."
            )

        # ------------------------------------------
        # Score
        # ------------------------------------------

        total_checks = len(found) + len(missing)

        if total_checks == 0:

            score = 0

        else:

            score = round(
                (len(found) / total_checks) * 100
            )

        logger.info(
            f"Documentation score: {score}"
        )

        return {

            "score": score,

            "found": found,

            "missing": missing,

        }