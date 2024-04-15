import json
from openai import AsyncOpenAI
from openai.types import CreateEmbeddingResponse
from tqdm.asyncio import tqdm_asyncio as asyncio
from asyncio import run
from lib.models import CommentChunk
from lib.db import get_connection
import os
from typing import List
from lib.process import batch_items


def read_jsonl_file(file_path):
    with open(file_path, "r") as file:
        for line in file:
            row = json.loads(line)
            if not row["text"]:
                continue
            yield row


async def embed_data(data) -> List[CommentChunk]:
    async def embed_batch(batch):
        client = AsyncOpenAI()
        res: CreateEmbeddingResponse = await client.embeddings.create(
            # Clip to max of 6000 chars for now since max emebdding context is 8k
            input=[item["text"][:6000] for item in batch],
            model="text-embedding-3-small",
        )
        return [
            CommentChunk(
                context=row["context"],
                text=row["text"],
                repo=row["repo"],
                vector=embedding.embedding,
                issue_id=row["issue_id"],
                issue_number=row["issue_number"],
                timestamp=row["timestamp"],
            )
            for embedding, row in zip(res.data, batch)
        ]

    batches = batch_items(data)
    coros = [embed_batch(batch) for batch in batches]
    res = await asyncio.gather(*coros)
    return [item for sublist in res for item in sublist]


def insert_into_db(items: List[CommentChunk]):
    insert_query = """INSERT INTO chunk (context, repo, vector, text, issue_id, issue_number, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    connection = get_connection()
    cursor = connection.cursor()
    chunk_data = [
        (
            item.context,
            item.repo,
            item.vector,
            item.text,
            item.issue_id,
            item.issue_number,
            item.timestamp,
        )
        for item in items
    ]
    cursor.executemany(insert_query, chunk_data)
    connection.commit()


if __name__ == "__main__":
    # Example usage
    file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../data/issues.jsonl")
    )
    cache_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../data/issues-cached.jsonl")
    )
    if not os.path.exists(cache_path):
        issues = read_jsonl_file(file_path)
        embedded_issues = run(embed_data(issues))
        with open(cache_path, "a+") as outfile:
            for issue in embedded_issues:
                outfile.write(issue.model_dump_json() + "\n")
    else:
        embedded_issues = []
        with open(cache_path, "r") as infile:
            for line in infile:
                embedded_issues.append(CommentChunk(**json.loads(line.strip())))
        print(f"Read in {len(embedded_issues)}")

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM chunk;")
    connection.commit()
    insert_into_db(embedded_issues)
