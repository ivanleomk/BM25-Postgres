import psycopg2
from lib.env import Settings
from psycopg2.extensions import connection
from typing import List
from openai import OpenAI
from psycopg2.extras import DictCursor
import re
from itertools import chain

settings = Settings()


def get_connection() -> connection:
    return psycopg2.connect(
        database=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host="localhost",
        port="5432",
    )


def vector_search(embedding, max_items: int = 25):
    # Convert embedding list to string representation
    embedding_str = str(embedding)

    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=DictCursor)
        # Write a query to the database using the embedding
        query = f"""
        SELECT * FROM chunk 
        ORDER BY vector <-> '{embedding_str}'::vector
        LIMIT {max_items};
        """
        cursor.execute(query)
        return [dict(item) for item in cursor.fetchall()]
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


def ngram_query(query: str, max_items: int = 25):
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
            limit_rows => {max_items}
        )
        ORDER BY rank_bm25 ASC;
        """
        cursor.execute(query)
        return [dict(item) for item in cursor.fetchall()]

    except Exception as e:
        print(f"An error occurred: {e}")
