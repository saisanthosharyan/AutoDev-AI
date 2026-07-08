from pydantic import BaseModel
from typing import List


class Task(BaseModel):
    title: str
    description: str
    steps: List[str]