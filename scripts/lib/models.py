from pydantic import BaseModel
from typing import List
from datetime import datetime


class CommentChunk(BaseModel):
    id: int = None
    context: str
    repo: str
    vector: List[float]
    text: str
    issue_id: int
    issue_number: int
    timestamp: datetime
