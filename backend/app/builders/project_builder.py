import re
import shutil
from pathlib import Path
from datetime import datetime


class ProjectBuilder:
    """
    Builds a complete project from the LLM-generated output.
    """

    def __init__(self):
        self.output_dir = Path("generated_projects")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build(
        self,
        project_name: str,
        llm_output: str,
        project_path: str | None = None,
    ) -> dict:
        """
        Parses the LLM response, creates all files and folders,
        and generates a ZIP archive of the project.
        """

        # Create a filesystem-safe project name
        safe_name = re.sub(
            r"[^a-zA-Z0-9_-]",
            "_",
            project_name
        ).lower()

        # -------------------------------------
        # Create new project or rebuild existing
        # -------------------------------------

        if project_path is None:

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            project_path = (
                self.output_dir /
                f"{safe_name}_{timestamp}"
            )

        else:

            project_path = Path(project_path)

        project_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Matches:
        #
        # FILE: README.md
        # content...
        #
        # FILE: app/main.py
        # content...
        #
        pattern = r"FILE:\s*(.+?)\n(.*?)(?=\nFILE:|\Z)"

        matches = re.findall(
            pattern,
            llm_output,
            re.DOTALL
        )

        if not matches:
            raise ValueError(
                "No project files were found in the LLM response."
            )

        created_files = []

        for relative_path, content in matches:

            relative_path = relative_path.strip()
            content = content.strip()

            destination = project_path / relative_path

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            # overwrite old file if it exists

            destination.write_text(
                content,
                encoding="utf-8"
            )

            created_files.append(str(destination))

        # Create ZIP archive
        zip_path = self.create_zip(project_path)

        return {
            "project_path": str(project_path),
            "zip_path": zip_path,
            "files": created_files,
            "file_count": len(created_files),
        }

    def create_zip(self, project_path: Path) -> str:
        """
        Creates a ZIP archive of the generated project.
        """

        zip_file = shutil.make_archive(
            base_name=str(project_path),
            format="zip",
            root_dir=str(project_path)
        )

        return zip_file
    def rebuild(self, project_path: str, llm_output: str) -> dict:
        """
        Rebuilds an existing project by overwriting files
        using the latest LLM output.
        """

        project = Path(project_path)

        pattern = r"FILE:\s*(.+?)\n(.*?)(?=\nFILE:|\Z)"

        matches = re.findall(
            pattern,
            llm_output,
            re.DOTALL
        )

        if not matches:
            raise ValueError(
                "No project files were found in the LLM response."
            )

        updated_files = []

        for relative_path, content in matches:

            relative_path = relative_path.strip()
            content = content.strip()

            destination = project / relative_path

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            # overwrite old file if it exists

            destination.write_text(
                content,
                encoding="utf-8"
            )

            updated_files.append(str(destination))

        zip_path = self.create_zip(project)

        return {
            "project_path": str(project),
            "zip_path": zip_path,
            "files": updated_files,
            "file_count": len(updated_files),
        }