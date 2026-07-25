from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from .database import Base


class Project(Base):
    """
    Stores generated projects.
    """

    __tablename__ = "projects"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    session_id = Column(
        String(100),
        index=True,
        nullable=False,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    prompt = Column(
        Text,
        nullable=False,
    )

    project_path = Column(
        String(500),
        nullable=False,
    )

    zip_path = Column(
        String(500),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )