from pathlib import Path


class ProjectValidator:
    """
    Validates a generated project by checking whether
    important files and folders exist.
    """

    REQUIRED_FILES = [
        "README.md",
        ".gitignore",
    ]

    REQUIRED_ANY = [
        ["requirements.txt", "package.json"],
    ]

    REQUIRED_DIRECTORIES = [
        "app",
    ]

    def validate(self, project_path: str):

        project = Path(project_path)

        report = {
            "valid": True,
            "score": 100,
            "missing_files": [],
            "missing_directories": [],
            "warnings": [],
        }

        if not project.exists():
            return {
                "valid": False,
                "score": 0,
                "missing_files": [],
                "missing_directories": [],
                "warnings": [
                    f"Project folder does not exist: {project_path}"
                ],
            }

        # Required files
        for file in self.REQUIRED_FILES:
            if not (project / file).exists():
                report["missing_files"].append(file)
                report["score"] -= 10

        # Either/or files
        for group in self.REQUIRED_ANY:
            found = any((project / item).exists() for item in group)

            if not found:
                report["missing_files"].append(" OR ".join(group))
                report["score"] -= 10

        # Required folders
        for directory in self.REQUIRED_DIRECTORIES:
            if not (project / directory).exists():
                report["missing_directories"].append(directory)
                report["score"] -= 10

        if report["missing_files"] or report["missing_directories"]:
            report["valid"] = False

        report["score"] = max(report["score"], 0)

        if report["missing_files"]:
            report["warnings"].append(
                f"Missing files: {', '.join(report['missing_files'])}"
            )

        if report["missing_directories"]:
            report["warnings"].append(
                f"Missing directories: {', '.join(report['missing_directories'])}"
            )

        return report