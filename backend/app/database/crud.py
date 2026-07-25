from sqlalchemy.orm import Session

from .models import Project


# --------------------------------------------------
# Create
# --------------------------------------------------


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

    try:

        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    except Exception:

        db.rollback()
        raise


# --------------------------------------------------
# Read All
# --------------------------------------------------


def get_projects(db: Session):

    return (
        db.query(Project)
        .order_by(Project.created_at.desc())
        .all()
    )


# --------------------------------------------------
# Read One
# --------------------------------------------------


def get_project(
    db: Session,
    project_id: int,
):

    return (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )


# --------------------------------------------------
# Read By Session
# --------------------------------------------------


def get_projects_by_session(
    db: Session,
    session_id: str,
):

    return (
        db.query(Project)
        .filter(Project.session_id == session_id)
        .order_by(Project.created_at.desc())
        .all()
    )


# --------------------------------------------------
# Delete
# --------------------------------------------------


def delete_project(
    db: Session,
    project_id: int,
):

    project = get_project(db, project_id)

    if project is None:
        return None

    try:

        db.delete(project)
        db.commit()

        return project

    except Exception:

        db.rollback()
        raise