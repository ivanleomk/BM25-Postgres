from pydantic import BaseModel
from typing import List
from datetime import datetime


class CommentChunk(BaseModel):
    chunk_id: str
    context: str
    vector: List[float]
    repo: str
    text: str
    issue_id: int
    issue_number: int
    timestamp: datetime
