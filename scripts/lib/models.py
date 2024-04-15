from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from typing import Optional


class CommentChunk(BaseModel):
    id: Optional[int] = None
    context: str
    repo: str
    vector: List[float]
    text: str
    issue_id: int
    issue_number: int
    timestamp: datetime


class QuestionAnswerPair(BaseModel):
    """
    This model represents a pair of a question generated from a text chunk, its corresponding answer,
    and the chain of thought leading to the answer. The chain of thought provides insight into how the answer
    was derived from the question.
    """

    chain_of_thought: str = Field(
        ..., description="The reasoning process leading to the answer."
    )
    question: str = Field(
        ..., description="The generated question from the text chunk."
    )
    answer: str = Field(..., description="The answer to the generated question.")


class EvalItem(BaseModel):
    question: str
    answer: str
    id: int
    text: str
    context: str
    repo: str
    issue_id: int
    issue_number: int
