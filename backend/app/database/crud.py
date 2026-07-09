from sqlalchemy.orm import Session

from .models import Project


def create_project(
    db: Session,
    session_id: str,
    title: str,
    prompt: str,
    project_path: str,
    zip_path: str,
):
    project = Project(
        session_id=session_id,
        title=title,
        prompt=prompt,
        project_path=project_path,
        zip_path=zip_path,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def get_projects(db: Session):
    return db.query(Project).all()


def get_project(db: Session, project_id: int):
    return (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )