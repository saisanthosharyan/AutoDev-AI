import re
import shutil
from pathlib import Path
from datetime import datetime

from app.core.logger import logger


class ProjectBuilder:
    """
    Builds and rebuilds generated projects from LLM output.

    Expected LLM format:

    FILE: package.json

    {
        ...
    }

    FILE: src/server.js

    ...
    """

    def __init__(self):

        root_dir = Path(
            __file__
        ).resolve().parents[3]

        self.output_dir = (
            root_dir / "generated_projects"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==========================================================
    # BUILD
    # ==========================================================

    def build(
        self,
        project_name: str,
        llm_output: str,
        project_path: str | None = None,
    ) -> dict:

        safe_name = self._safe_name(
            project_name
        )

        if not safe_name:

            safe_name = "generated_project"

        # ------------------------------------------------------
        # New project
        # ------------------------------------------------------

        if project_path is None:

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            project_path = (
                self.output_dir
                / f"{safe_name}_{timestamp}"
            )

        else:

            project_path = Path(
                project_path
            ).resolve()

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

        if not created_files:

            raise ValueError(
                "No files were created."
            )

        zip_path = self.create_zip(
            project_path
        )

        logger.info(
            f"Project built successfully with "
            f"{len(created_files)} files."
        )

        return {
            "project_path": str(
                project_path
            ),

            "zip_path": zip_path,

            "files": created_files,

            "file_count": len(
                created_files
            ),
        }

    # ==========================================================
    # REBUILD
    # ==========================================================

    def rebuild(
        self,
        project_path: str,
        llm_output: str,
    ) -> dict:

        project = Path(
            project_path
        ).resolve()

        if not project.exists():

            raise FileNotFoundError(
                f"Project does not exist: {project}"
            )

        logger.info(
            f"Rebuilding project: {project}"
        )

        # ------------------------------------------------------
        # Build repaired project in temporary directory first.
        #
        # This prevents a bad LLM response from destroying
        # the currently working project.
        # ------------------------------------------------------

        temp_project = project.parent / (
            f".{project.name}_repairing"
        )

        if temp_project.exists():

            shutil.rmtree(
                temp_project
            )

        temp_project.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            updated_files = self._write_files(
                temp_project,
                llm_output,
            )

            if not updated_files:

                raise ValueError(
                    "AI repair produced no files."
                )

            # --------------------------------------------------
            # Create archive before replacing project
            # --------------------------------------------------

            self.create_zip(
                temp_project
            )

            # --------------------------------------------------
            # Remove old project
            # --------------------------------------------------

            shutil.rmtree(
                project
            )

            # --------------------------------------------------
            # Rename repaired project
            # --------------------------------------------------

            temp_project.rename(
                project
            )

            zip_path = self.create_zip(
                project
            )

            logger.info(
                "Project rebuilt successfully."
            )

            return {
                "project_path": str(
                    project
                ),

                "zip_path": zip_path,

                "files": [
                    str(
                        project / Path(file).relative_to(
                            temp_project
                        )
                    )
                    for file in updated_files
                ],

                "file_count": len(
                    updated_files
                ),
            }

        except Exception:

            logger.exception(
                "Project rebuild failed."
            )

            # --------------------------------------------------
            # Remove failed temporary build
            # --------------------------------------------------

            if temp_project.exists():

                try:

                    shutil.rmtree(
                        temp_project
                    )

                except Exception:

                    logger.exception(
                        "Failed to remove temporary "
                        "repair directory."
                    )

            raise

    # ==========================================================
    # WRITE FILES
    # ==========================================================

    def _write_files(
        self,
        project_path: Path,
        llm_output: str,
    ) -> list[str]:

        if not llm_output:

            raise ValueError(
                "LLM output is empty."
            )

        llm_output = self._clean_output(
            llm_output
        )

        # ------------------------------------------------------
        # FILE parser
        # ------------------------------------------------------

        pattern = (
            r"^\s*FILE\s*:\s*(.*?)\s*$"
            r"([\s\S]*?)"
            r"(?=^\s*FILE\s*:|\Z)"
        )

        matches = re.findall(
            pattern,
            llm_output,
            flags=re.MULTILINE,
        )

        if not matches:

            logger.error(
                "No FILE: sections found in LLM output."
            )

            raise ValueError(
                "LLM returned no project files."
            )

        created = []

        seen = set()

        ignored = {
            ".git",
            ".github",
            ".idea",
            ".vscode",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".DS_Store",
            "__MACOSX",
            "node_modules",
        }

        project_root = (
            project_path.resolve()
        )

        for raw_file_path, content in matches:

            # --------------------------------------------------
            # Normalize path
            # --------------------------------------------------

            file_path = (
                raw_file_path
                .strip()
                .replace("\\", "/")
            )

            file_path = re.sub(
                r"/+",
                "/",
                file_path,
            )

            file_path = file_path.lstrip(
                "./"
            )

            # --------------------------------------------------
            # Validate path
            # --------------------------------------------------

            if not file_path:

                logger.warning(
                    "Skipping empty file path."
                )

                continue

            path_parts = Path(
                file_path
            ).parts

            if any(
                part in {
                    "",
                    ".",
                    "..",
                }
                for part in path_parts
            ):

                raise ValueError(
                    f"Unsafe file path detected: {file_path}"
                )

            # --------------------------------------------------
            # Ignore generated system files
            # --------------------------------------------------

            first_part = (
                path_parts[0]
                if path_parts
                else ""
            )

            if (
                file_path.lower() in ignored
                or first_part.lower() in ignored
            ):

                logger.warning(
                    f"Ignoring system file: {file_path}"
                )

                continue

            # --------------------------------------------------
            # Duplicate file
            # --------------------------------------------------

            normalized_key = (
                file_path.lower()
            )

            if normalized_key in seen:

                logger.warning(
                    f"Duplicate file ignored: {file_path}"
                )

                continue

            seen.add(
                normalized_key
            )

            # --------------------------------------------------
            # Content
            # --------------------------------------------------

            content = content.strip(
                "\n"
            )

            if not content.strip():

                logger.warning(
                    f"Skipping empty file: {file_path}"
                )

                continue

            # --------------------------------------------------
            # Destination
            # --------------------------------------------------

            destination = (
                project_root
                / file_path
            ).resolve()

            try:

                destination.relative_to(
                    project_root
                )

            except ValueError:

                raise ValueError(
                    f"Unsafe file path detected: "
                    f"{file_path}"
                )

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            # --------------------------------------------------
            # Write
            # --------------------------------------------------

            try:

                destination.write_text(
                    content,
                    encoding="utf-8",
                    newline="\n",
                )

                relative = (
                    destination.relative_to(
                        project_root
                    )
                )

                logger.info(
                    f"Created file: {relative}"
                )

                created.append(
                    str(relative)
                )

            except Exception:

                logger.exception(
                    f"Failed writing file: "
                    f"{file_path}"
                )

                raise

        if not created:

            raise ValueError(
                "LLM output contained no valid project files."
            )

        return created

    # ==========================================================
    # CREATE ZIP
    # ==========================================================

    def create_zip(
        self,
        project_path: Path,
    ) -> str:

        project_path = Path(
            project_path
        ).resolve()

        if not project_path.exists():

            raise FileNotFoundError(
                f"Cannot zip missing project: "
                f"{project_path}"
            )

        zip_file = project_path.with_suffix(
            ".zip"
        )

        if zip_file.exists():

            zip_file.unlink()

        archive = shutil.make_archive(
            base_name=str(
                project_path
            ),
            format="zip",
            root_dir=str(
                project_path
            ),
        )

        logger.info(
            f"Created archive: {archive}"
        )

        return archive

    # ==========================================================
    # CLEAR PROJECT
    # ==========================================================

    def _clear_project(
        self,
        project_path: Path,
    ):

        if not project_path.exists():

            return

        for item in project_path.iterdir():

            try:

                if item.is_dir():

                    shutil.rmtree(
                        item
                    )

                else:

                    item.unlink()

            except Exception:

                logger.exception(
                    f"Unable to remove {item}"
                )

                raise

    # ==========================================================
    # CLEAN LLM OUTPUT
    # ==========================================================

    def _clean_output(
        self,
        text: str,
    ) -> str:

        if not text:

            return ""

        text = text.strip()

        # Remove opening markdown code fences.
        text = re.sub(
            r"^\s*```(?:text|plaintext|python|javascript|"
            r"typescript|json|bash|shell|java|cpp|c\+\+)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        # Remove ending fence.
        text = re.sub(
            r"\s*```\s*$",
            "",
            text,
        )

        # Remove remaining standalone fences.
        text = text.replace(
            "```",
            "",
        )

        return text.strip()

    # ==========================================================
    # SAFE PROJECT NAME
    # ==========================================================

    def _safe_name(
        self,
        name: str,
    ) -> str:

        if not name:

            return "generated_project"

        safe = re.sub(
            r"[^a-zA-Z0-9_-]",
            "_",
            name,
        )

        safe = re.sub(
            r"_+",
            "_",
            safe,
        )

        return safe.strip(
            "_"
        ).lower()