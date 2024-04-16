from typing import List
from openai import AsyncOpenAI, OpenAI
from openai.types import CreateEmbeddingResponse
from lib.metrics import calculate_mrr, calculate_recall, slice_predictions_at_k
from lib.models import EvalItem
from lib.db import vector_search, ngram_query
from lib.process import batch as batch_items
from tqdm.asyncio import tqdm_asyncio as asyncio
from asyncio import run
import itertools
import json
import pandas as pd

import os

SIZES = [3, 10, 15, 25]
metrics = {"recall": calculate_recall, "mrr": calculate_mrr}
evals = {}

for metric, sz in itertools.product(metrics.keys(), SIZES):
    evals[f"{metric}@{sz}"] = slice_predictions_at_k(sz, metrics[metric])


async def embed_items(items: List[EvalItem]):
    async def embed_batch(item_batch: List[EvalItem]):
        client = AsyncOpenAI()
        questions = [item.question for item in item_batch]
        response: CreateEmbeddingResponse = await client.embeddings.create(
            input=questions, model="text-embedding-3-small"
        )

        return [
            {"embedding": embedding.embedding, "query": query.question, "id": query.id}
            for embedding, query in zip(response.data, item_batch)
        ]

    batches = batch_items(items)
    coros = [embed_batch(items) for items in batches]
    res = []
    for processed_batch in await asyncio.gather(*coros):
        res.append(processed_batch)
    return processed_batch


async def evaluate(question_file: str, method: str = "semantic"):
    res = []

    items = []
    with open(question_file, "r") as file:
        for line in file:
            eval_item = EvalItem(**json.loads(line))
            items.append(eval_item)

    if method == "semantic":
        embeddings = await embed_items(items)
        results = [vector_search(eval_item["embedding"]) for eval_item in embeddings]
    elif method == "ngram":
        results = [ngram_query(eval_item[""]) for eval_item in embeddings]
    else:
        raise ValueError(f"Invalid method of {method} used")

    for result, eval_item in zip(results, items):
        metrics = {
            label: metric_fn(eval_item.id, [item["id"] for item in result])
            for label, metric_fn in evals.items()
        }
        metrics = {label: round(value, 4) for label, value in metrics.items()}
        res.append(metrics)

    df = pd.DataFrame(res)
    print(df.mean())


evals_file_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/evals.jsonl")
)
run(evaluate(evals_file_path))
