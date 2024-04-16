from src.dataset import fetch_dataset_rows
from src.openai import embed_data
from src.models import CommentChunk, SyntheticDataQuestion, RetrievalResult
from src.db import (
    insert_chunks,
    fetch_all_chunks,
    reset_db,
    insert_chunks_with_id,
    vector_search,
    keyword_search,
)
from src.caching import (
    dump_chunks_to_jsonl,
    read_chunks_from_jsonl,
    dump_questions_to_jsonl,
    read_questions_from_jsonl,
)
from src.generate import (
    generate_synthethic_questions,
    generate_keywords_for_question_batch,
)
from src.string import generate_ngrams
from typing import List
import os
from asyncio import run
from rich import print as rich_print
import numpy as np
from src.evaluate import calculate_mrr, calculate_recall, slice_predictions_at_k
import itertools
from typing import Literal
from pandas import DataFrame
import pandas as pd

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
ISSUE_JSONL = os.path.join(DATA_DIR, "issues.jsonl")
QUESTION_JSONL = os.path.join(DATA_DIR, "questions.jsonl")
NUMBER_OF_ISSUES = 200
NUMBER_OF_SYNTHETHIC_QUESTIONS = 40
CHOSEN_REPOS = set(
    [
        "facebook/react",
        "pytorch/pytorch",
    ]
)

SIZES = [3, 10, 15, 25]
metrics = {"recall": calculate_recall, "mrr": calculate_mrr}
evals = {}

for metric, sz in itertools.product(metrics.keys(), SIZES):
    evals[f"{metric}@{sz}"] = slice_predictions_at_k(sz, metrics[metric])


def log_with_rich(str):
    rich_print(f"[bold magenta]{str}[/bold magenta]\n")


def setup_db_with_chunks():
    if os.path.exists(ISSUE_JSONL):
        log_with_rich(
            f"Reading existing issues from {ISSUE_JSONL}. ( Delete file if you'd like to regenerate issues )"
        )
        chunks = read_chunks_from_jsonl(ISSUE_JSONL)
        reset_db()
        insert_chunks_with_id(chunks)
    else:
        log_with_rich("Fetching and embedding database issues")
        dataset_rows = fetch_dataset_rows(NUMBER_OF_ISSUES, CHOSEN_REPOS)

        dataset_rows_with_embedded_text = run(embed_data(dataset_rows))
        chunks = [
            {**item["item"], "vector": item["embedding"]}
            for item in dataset_rows_with_embedded_text
        ]
        chunks: List[CommentChunk] = [CommentChunk(**item) for item in chunks]
        reset_db()
        insert_chunks(chunks)

        chunks = fetch_all_chunks()
        dump_chunks_to_jsonl(chunks, ISSUE_JSONL)

    return chunks


def get_questions(chunks: List[CommentChunk]):
    if not os.path.exists(QUESTION_JSONL):
        log_with_rich(
            f"Generating {NUMBER_OF_SYNTHETHIC_QUESTIONS} Synthethic Questions"
        )
        valid_chunks = [chunk for chunk in chunks if len(chunk.text) > 150]
        selected_chunks = np.random.choice(
            valid_chunks, NUMBER_OF_SYNTHETHIC_QUESTIONS, replace=False
        )
        questions = run(generate_synthethic_questions(selected_chunks))

        dump_questions_to_jsonl(questions, QUESTION_JSONL)
    else:
        log_with_rich(
            f"Reading existing {NUMBER_OF_SYNTHETHIC_QUESTIONS} Synthethic Questions from file. ( Delete file to regenerate questions)"
        )
        questions = read_questions_from_jsonl(QUESTION_JSONL)

    return questions


def query_db(
    queries: List[SyntheticDataQuestion],
    query_type: Literal["semantic", "keyword", "bigram"],
) -> List[RetrievalResult]:
    if query_type == "semantic":
        query_text = [
            {"text": query.question.question, "query": query} for query in queries
        ]
        embedded_queries = run(embed_data(query_text))
        return [
            RetrievalResult(
                results=vector_search(embedded_query["embedding"]),
                source=embedded_query["item"]["query"],
            )
            for embedded_query in embedded_queries
        ]

    elif query_type == "keyword":
        keywords_and_query = run(generate_keywords_for_question_batch(queries))
        return [
            RetrievalResult(
                results=keyword_search(query.keywords.keywords), source=query.question
            )
            for query in keywords_and_query
        ]
    elif query_type == "bigram":
        ngrams = [generate_ngrams(query.question.question) for query in queries]
        return [
            RetrievalResult(results=keyword_search(keywords), source=query)
            for keywords, query in zip(ngrams, queries)
        ]
    else:
        raise ValueError(f"Unsupported query type of {query_type}")


def score(results: List[RetrievalResult]):
    res = []
    for result in results:
        original_chunk_id = result.source.source.chunk_id
        result_chunk_ids = [item.chunk_id for item in result.results]

        metrics = {
            label: metric_fn(original_chunk_id, result_chunk_ids)
            for label, metric_fn in evals.items()
        }
        metrics = {label: round(value, 4) for label, value in metrics.items()}
        res.append(metrics)

    return DataFrame(res)


if __name__ == "__main__":
    chunks = setup_db_with_chunks()
    questions = get_questions(chunks)

    method_results = {}
    for method in ["keyword", "semantic", "bigram"]:
        query_results = query_db(questions, method)
        df = score(query_results)
        method_results[method] = df.mean()

    combined_df = pd.DataFrame(method_results)
    print(combined_df)
    print(combined_df.to_markdown())
