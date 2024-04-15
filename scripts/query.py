from openai import OpenAI
from lib.db import get_connection
from lib.models import CommentChunk
from psycopg2.extras import DictCursor
import ast
from rich.table import box
from rich.console import Console
from rich.table import Table
from typing import List
import re
from itertools import chain


def visualise_results(results):
    console = Console()
    table = Table(title="Results", box=box.HEAVY, padding=(1, 2), show_lines=True)
    table.add_column("ID", style="dim", width=12)
    table.add_column("Text", justify="left")
    table.add_column("Repo", justify="left")
    table.add_column("Context", justify="left")
    table.add_column("BM25", justify="left")

    for result in results:
        table.add_row(
            str(result["id"]),
            result["text"][:100],
            result["repo"],
            result["context"][:200] + "...",
            str(result.get("rank_bm25", "")),
        )

    console.print(table)
    print(f"{len(results)}")


def run_text_query(query: str):
    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=DictCursor)
        query = f"""
        SELECT *, paradedb.rank_bm25(id)
        FROM search_idx.search(
          '(text:"{query}" OR context:"{query}")',
          limit_rows => 5
        );
        """
        cursor.execute(query)
        results = [dict(item) for item in cursor.fetchall()]
        results = [
            {**item, "vector": ast.literal_eval(item["vector"])} for item in results
        ]
        visualise_results(results)
    except Exception as e:
        print(f"An error occurred: {e}")


def query_search(query: str):
    client = OpenAI()
    # Embed the query using the text-embedding-small model
    response = client.embeddings.create(input=query, model="text-embedding-3-small")
    embedding = response.data[0].embedding
    # Convert embedding list to string representation
    embedding_str = str(embedding)

    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=DictCursor)
        # Write a query to the database using the embedding
        query = f"""
        SELECT * FROM chunk 
        ORDER BY vector <-> '{embedding_str}'::vector
        LIMIT 5;
        """
        cursor.execute(query)
        results = [dict(item) for item in cursor.fetchall()]
        visualise_results(results)
    except Exception as e:
        print(f"An error occurred: {e}")


def naive_bigram(query: str):
    search_terms = generate_ngrams(query)
    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=DictCursor)
        queries = ",\n".join(
            [
                f"paradedb.term(field => 'text', value => '{gram}'),\nparadedb.term(field => 'context', value => '{gram}')"
                for gram in search_terms
            ]
        )
        query = f"""
        SELECT *, paradedb.rank_bm25(id) FROM search_idx.search(
            query => paradedb.term_set(
                terms => ARRAY[
                   {queries}
                ]
            ),
            limit_rows => 5
        )
        ORDER BY rank_bm25 ASC;
        """
        cursor.execute(query)
        results = [dict(item) for item in cursor.fetchall()]

        results = [
            {**item, "vector": ast.literal_eval(item["vector"])} for item in results
        ]
        visualise_results(results)
    except Exception as e:
        print(f"An error occurred: {e}")


def generate_ngrams(query: str):
    # Remove punctuation from the query
    query = re.sub(r"[^\w\s]", "", query)
    # Split the query into words
    words = query.split()
    # Generate unigrams (which are just the individual words)
    unigrams = words
    # Generate bigrams by zipping the words with itself offset by one
    bigrams = zip(words, words[1:])
    # Combine unigrams and bigrams into a single list
    all_ngrams = list(chain(unigrams, bigrams))
    # Convert bigrams tuples into a single string
    all_ngrams = [
        " ".join(ngram) if isinstance(ngram, tuple) else ngram for ngram in all_ngrams
    ]
    return all_ngrams


# run_text_query("wheel torch")
# naive_bigram("How can I identify a memory leak in Cuda")
query_search("How can I create a functional component?")
