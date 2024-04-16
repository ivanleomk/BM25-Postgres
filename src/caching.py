import json
from typing import List
from src.models import CommentChunk, SyntheticDataQuestion


def dump_chunks_to_jsonl(chunks: List[CommentChunk], path: str):
    with open(path, "w") as file:
        for chunk in chunks:
            file.write(chunk.model_dump_json() + "\n")


def dump_questions_to_jsonl(chunks: List[SyntheticDataQuestion], path):
    with open(path, "w") as file:
        for chunk in chunks:
            file.write(chunk.model_dump_json() + "\n")


def read_chunks_from_jsonl(path: str):
    chunks = []
    with open(path, "r") as file:
        for line in file:
            chunk = CommentChunk(**json.loads(line))
            chunks.append(chunk)
    return chunks


def read_questions_from_jsonl(path: str):
    questions = []
    with open(path, "r") as file:
        for line in file:
            chunk = SyntheticDataQuestion(**json.loads(line))
            questions.append(chunk)
    return questions
