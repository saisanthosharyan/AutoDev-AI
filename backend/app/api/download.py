from pathlib import Path

from fastapi import APIRouter, HTTPException

from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.logger import logger

router = APIRouter(
    prefix="/download",
    tags=["Download"],
)


# --------------------------------------------------
# Download Generated Project
# --------------------------------------------------

@router.get("/{project_name}")
async def download_project(
    project_name: str,
):

    try:

        # Prevent path traversal attacks
        project_name = Path(project_name).name

        project_dir = Path(
            settings.GENERATED_PROJECTS_DIR
        ).resolve()

        zip_path = (
            project_dir /
            f"{project_name}.zip"
        ).resolve()

        # Ensure requested file stays inside generated_projects
        try:
            zip_path.relative_to(project_dir)
        except ValueError:

            logger.warning(
                f"Invalid download request: {project_name}"
            )

            raise HTTPException(
                status_code=400,
                detail="Invalid project name.",
            )

        if not zip_path.exists():

            logger.warning(
                f"ZIP not found: {zip_path}"
            )

            raise HTTPException(
                status_code=404,
                detail="Project ZIP not found.",
            )

        logger.info(
            f"Downloading project: {zip_path.name}"
        )

        return FileResponse(
            path=zip_path,
            filename=zip_path.name,
            media_type="application/zip",
        )

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "Project download failed."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to download project.",
        )