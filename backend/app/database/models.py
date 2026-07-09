from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime

from datetime import datetime

from .database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(String, index=True)

    title = Column(String)

    prompt = Column(Text)

    project_path = Column(String)

    zip_path = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )