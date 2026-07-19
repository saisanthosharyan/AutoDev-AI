import re
import shutil
from pathlib import Path
from datetime import datetime

from app.core.logger import logger


class ProjectBuilder:
    """
    Builds and rebuilds generated projects from LLM output.
    """

    def __init__(self):
        self.output_dir = Path("generated_projects").resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # Public
    # --------------------------------------------------

    def build(
        self,
        project_name: str,
        llm_output: str,
        project_path: str | None = None,
    ) -> dict:

        safe_name = self._safe_name(project_name)

        if project_path is None:

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            project_path = (
                self.output_dir
                / f"{safe_name}_{timestamp}"
            )

        else:
            project_path = Path(project_path).resolve()

        project_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        logger.info(
            f"Building project at: {project_path}"
        )

        created_files = self._write_files(
            project_path,
            llm_output,
        )

        zip_path = self.create_zip(project_path)

        logger.info(
            f"Project built successfully with {len(created_files)} files."
        )

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
    ) -> dict:

        project = Path(project_path).resolve()

        logger.info(
            f"Rebuilding project: {project}"
        )

        self._clear_project(project)

        updated_files = self._write_files(
            project,
            llm_output,
        )

        zip_path = self.create_zip(project)

        logger.info(
            f"Project rebuilt successfully with {len(updated_files)} files."
        )

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
    ) -> list[str]:

        llm_output = self._clean_output(llm_output)

        pattern = (
            r"FILE:\s*(.+?)\n"
            r"(.*?)(?=\nFILE:\s*|\Z)"
        )

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

        project_root = project_path.resolve()

        for file_path, content in matches:

            file_path = (
                file_path.strip()
                .replace("\\", "/")
            )

            if file_path in seen:
                logger.warning(
                    f"Duplicate file ignored: {file_path}"
                )
                continue

            seen.add(file_path)

            content = content.lstrip("\n")

            destination = (
                project_root / file_path
            ).resolve()

            if not str(destination).startswith(
                str(project_root)
            ):
                raise ValueError(
                    f"Unsafe file path detected: {file_path}"
                )

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            destination.write_text(
                content,
                encoding="utf-8",
            )

            logger.info(
                f"Created {destination.relative_to(project_root)}"
            )

            created.append(str(destination))

        return created

    # --------------------------------------------------

    def create_zip(
        self,
        project_path: Path,
    ) -> str:

        zip_file = project_path.with_suffix(".zip")

        if zip_file.exists():
            zip_file.unlink()

        archive = shutil.make_archive(
            base_name=str(project_path),
            format="zip",
            root_dir=str(project_path),
        )

        logger.info(
            f"Created archive: {archive}"
        )

        return archive

    # --------------------------------------------------

    def _clear_project(
        self,
        project_path: Path,
    ):

        if not project_path.exists():
            return

        for item in project_path.iterdir():

            if item.is_dir():
                shutil.rmtree(item)

            else:
                item.unlink()

    # --------------------------------------------------

    def _clean_output(
        self,
        text: str,
    ) -> str:

        text = re.sub(
            r"```[\w+-]*\n?",
            "",
            text,
        )

        text = text.replace(
            "```",
            "",
        )

        return text.strip()

    # --------------------------------------------------

    def _safe_name(
        self,
        name: str,
    ) -> str:

        return re.sub(
            r"[^a-zA-Z0-9_-]",
            "_",
            name,
        ).lower()