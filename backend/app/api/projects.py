from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.database.database import get_db
from app.database.crud import (
    get_project,
    get_projects,
    get_projects_by_session,
)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


# --------------------------------------------------
# List Projects
# --------------------------------------------------

@router.get("/")
def list_projects(
    session_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):

    try:

        if session_id:

            logger.info(
                f"Fetching projects for session: {session_id}"
            )

            projects = get_projects_by_session(
                db,
                session_id,
            )

        else:

            logger.info("Fetching all projects.")

            projects = get_projects(db)

        return {
            "success": True,
            "count": len(projects),
            "projects": projects,
        }

    except Exception:

        logger.exception(
            "Failed to fetch projects."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve projects.",
        )


# --------------------------------------------------
# Project Details
# --------------------------------------------------

@router.get("/{project_id}")
def project_details(
    project_id: int,
    db: Session = Depends(get_db),
):

    try:

        project = get_project(
            db,
            project_id,
        )

        if project is None:

            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        return {
            "success": True,
            "project": project,
        }

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "Failed to retrieve project."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve project.",
        )