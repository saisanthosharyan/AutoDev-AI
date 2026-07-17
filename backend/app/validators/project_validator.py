from pathlib import Path


class ProjectValidator:

    REQUIRED_FILES = [
        "README.md",
        ".gitignore",
    ]

    REQUIRED_ANY = [
        ["requirements.txt", "package.json", "pyproject.toml"],
    ]

    def validate(self, project_path: str):

        project = Path(project_path)

        report = {
            "valid": True,
            "score": 100,
            "missing_files": [],
            "warnings": [],
        }

        if not project.exists():
            return {
                "valid": False,
                "score": 0,
                "missing_files": [],
                "warnings": [f"Project folder does not exist: {project_path}"],
            }

        # --------------------------
        # Required files
        # --------------------------

        for file in self.REQUIRED_FILES:

            if not (project / file).exists():

                report["missing_files"].append(file)
                report["score"] -= 10

        # --------------------------
        # One of these must exist
        # --------------------------

        for group in self.REQUIRED_ANY:

            found = any((project / item).exists() for item in group)

            if not found:

                report["missing_files"].append(" OR ".join(group))
                report["score"] -= 10

        # --------------------------
        # At least one source file
        # --------------------------

        source_exists = (
            list(project.rglob("*.py"))
            or list(project.rglob("*.js"))
            or list(project.rglob("*.ts"))
            or list(project.rglob("*.java"))
            or list(project.rglob("*.cpp"))
        )

        if not source_exists:

            report["warnings"].append("No source files found.")
            report["score"] -= 20

        report["score"] = max(report["score"], 0)

        if report["missing_files"]:
            report["valid"] = False

        return report