from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/download", tags=["Download"])


@router.get("/{project_name}")
async def download_project(project_name: str):

    zip_path = Path("generated_projects") / f"{project_name}.zip"

    if not zip_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Project ZIP not found."
        )

    return FileResponse(
        path=zip_path,
        filename=zip_path.name,
        media_type="application/zip",
    )