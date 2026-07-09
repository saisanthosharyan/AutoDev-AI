from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.crud import (
    get_projects,
    get_project,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    return get_projects(db)


@router.get("/{project_id}")
def project_details(
    project_id: int,
    db: Session = Depends(get_db),
):
    return get_project(db, project_id)