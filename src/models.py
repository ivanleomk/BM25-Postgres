from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import ast


class CommentChunk(BaseModel):
    id: Optional[int] = None
    context: str
    repo: str
    vector: List[float]
    text: str
    issue_id: int
    issue_number: int
    timestamp: datetime
    chunk_id: str

    @classmethod
    def from_dict(cls, chunk):
        chunk["vector"] = ast.literal_eval(chunk["vector"])
        return cls(**chunk)


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


class Keywords(BaseModel):
    """
    This model represents a set of keywords that are relevant to the question that is being asked in the prompt. Make sure to perform the following
    1. Expand any accronyms
    2. Add in additional context which might surface related content
    """

    chain_of_thought: str = Field(
        ...,
        description="Quick brainstorming on relevant concepts, words, synonyms or phrases that might be relevant to the query",
    )
    keywords: List[str] = Field(
        ...,
        description="This is the list of keywords that will be used to execute a search query to identify helpful sources of information to answer the question asked in the prompt",
        min_items=3,
    )

    @field_validator("keywords")
    @classmethod
    def check_keywords_non_empty(cls, v: List[str]) -> List[str]:
        if not all(v):
            raise ValueError(
                f'Keywords were  {",".join(v)}. Make sure to generate non-empty keywords.'
            )
        return v


class SyntheticDataQuestion(BaseModel):
    question: QuestionAnswerPair
    source: CommentChunk


class KeywordGenerationResult(BaseModel):
    keywords: Keywords
    question: SyntheticDataQuestion


class RetrievalResult(BaseModel):
    results: List[CommentChunk]
    source: SyntheticDataQuestion
