from psycopg2.extras import DictCursor
from lib.db import get_connection
from lib.models import CommentChunk, QuestionAnswerPair, EvalItem
from tqdm.asyncio import tqdm_asyncio as asyncio
import os
import ast
from typing import List
from tenacity import retry, stop_after_attempt, wait_fixed
import instructor
from openai import AsyncOpenAI
from asyncio import run


def fetch_rows(n=100, min_characters=150):
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=DictCursor)
    cursor.execute(f"SELECT * FROM chunk LIMIT {2*n};")
    rows = cursor.fetchall()
    return [
        CommentChunk(**{**item, "vector": ast.literal_eval(item["vector"])})
        for item in rows
        if len(item["text"]) > min_characters
    ][:n]


@retry(stop=stop_after_attempt(5), wait=wait_fixed(30))
async def generate_synthethic_questions(chunks: List[CommentChunk]):
    async def generate_question(chunk: CommentChunk):
        client = instructor.from_openai(AsyncOpenAI())
        res = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a world class algorithm that excels at generating great questions that can be only answered by a specific text that will soon be passed to you.",
                },
                {
                    "role": "assistant",
                    "content": f"Generate a question and answer pair that uses information and content that is specific to the following text chunk, including a chain of thought:\n\n{chunk.text[:10000]}",
                },
            ],
            response_model=QuestionAnswerPair,
            max_retries=3,
        )
        return EvalItem(
            question=res.question,
            answer=res.answer,
            id=chunk.id,
            text=chunk.text,
            context=chunk.context,
            repo=chunk.repo,
            issue_id=chunk.issue_id,
            issue_number=chunk.issue_number,
        )

    coros = [generate_question(chunk) for chunk in chunks]
    res = await asyncio.gather(*coros)
    return res


if __name__ == "__main__":
    rows = fetch_rows(100)
    # Filter out rows with a text that has < 150 characters
    evals_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../data/evals.jsonl")
    )
    questions = run(generate_synthethic_questions(rows))
    with open(evals_file_path, "w") as f:
        for row in questions:
            f.write(row.model_dump_json() + "\n")
    print(f"Wrote {len(rows)} rows to {evals_file_path}")
