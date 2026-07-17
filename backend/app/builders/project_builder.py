import re
import shutil
from pathlib import Path
from datetime import datetime


class ProjectBuilder:

    def __init__(self):
        self.output_dir = Path("generated_projects")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # Public
    # --------------------------------------------------

    def build(
        self,
        project_name: str,
        llm_output: str,
        project_path: str | None = None,
    ):

        safe_name = self._safe_name(project_name)

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

        created_files = self._write_files(
            project_path,
            llm_output,
        )

        zip_path = self.create_zip(project_path)

        return {
            "project_path": str(project_path),
            "zip_path": zip_path,
            "files": created_files,
            "file_count": len(created_files),
        }

    # --------------------------------------------------

    def rebuild(
        self,
        project_path: str,
        llm_output: str,
    ):

        project = Path(project_path)

        updated_files = self._write_files(
            project,
            llm_output,
        )

        zip_path = self.create_zip(project)

        return {
            "project_path": str(project),
            "zip_path": zip_path,
            "files": updated_files,
            "file_count": len(updated_files),
        }

    # --------------------------------------------------

    def _write_files(
        self,
        project_path: Path,
        llm_output: str,
    ):

        llm_output = llm_output.replace("```text", "")
        llm_output = llm_output.replace("```python", "")
        llm_output = llm_output.replace("```json", "")
        llm_output = llm_output.replace("```", "")

        pattern = r"FILE:\s*(.*?)\n(.*?)(?=\nFILE:|\nFile:|\Z)"

        matches = re.findall(
            pattern,
            llm_output,
            flags=re.DOTALL | re.IGNORECASE,
        )

        if not matches:
            raise ValueError(
                "LLM returned no project files."
            )

        created = []

        seen = set()

        for file_path, content in matches:

            file_path = file_path.strip().replace("\\", "/")

            if file_path in seen:
                continue

            seen.add(file_path)

            content = content.lstrip("\n")

            destination = project_path / file_path

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            destination.write_text(
                content,
                encoding="utf-8",
            )

            created.append(str(destination))

        return created

    # --------------------------------------------------

    def create_zip(
        self,
        project_path: Path,
    ):

        return shutil.make_archive(
            base_name=str(project_path),
            format="zip",
            root_dir=str(project_path),
        )

    # --------------------------------------------------

    def _safe_name(
        self,
        name: str,
    ):

        return re.sub(
            r"[^a-zA-Z0-9_-]",
            "_",
            name,
        ).lower()