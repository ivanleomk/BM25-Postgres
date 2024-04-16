from src.env import Settings
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor
import psycopg2
from typing import List
from src.models import CommentChunk
import ast

settings = Settings()


def get_connection() -> connection:
    return psycopg2.connect(
        database=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host="localhost",
        port="5432",
    )


def reset_db():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM chunk;")
    connection.commit()


def insert_chunks_with_id(items: List[CommentChunk]):
    """
    If we're running evaluations on the same chunks we've saved to disk earlier, we want to make sure we insert in the id too
    """
    insert_query = """INSERT INTO chunk (id,context, repo, vector, text, issue_id, issue_number, timestamp,chunk_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s)"""
    connection = get_connection()
    cursor = connection.cursor()
    chunk_data = [
        (
            item.id,
            item.context,
            item.repo,
            item.vector,
            item.text,
            item.issue_id,
            item.issue_number,
            item.timestamp,
            item.chunk_id,
        )
        for item in items
    ]
    cursor.executemany(insert_query, chunk_data)
    connection.commit()


def insert_chunks(items: List[CommentChunk]):
    """
    This is used to insert chunks that don't have a given id
    """
    insert_query = """INSERT INTO chunk (context, repo, vector, text, issue_id, issue_number, timestamp,chunk_id) VALUES (%s, %s, %s, %s, %s, %s,%s,%s)"""
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
            item.chunk_id,
        )
        for item in items
    ]
    cursor.executemany(insert_query, chunk_data)
    connection.commit()


def fetch_all_chunks():
    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=DictCursor)
        cursor.execute("SELECT * FROM chunk")
        extracted_chunks = cursor.fetchall()
        comment_chunks = [CommentChunk.from_dict(chunk) for chunk in extracted_chunks]
        for chunk in comment_chunks:
            assert chunk.id is not None, "Chunk id is missing"
        return comment_chunks
    except Exception as e:
        print(f"An error occurred while fetching chunks: {e}")
        raise e


def vector_search(embedding, max_items: int = 25):
    # Convert embedding list to string representation
    embedding_str = str(embedding)

    connection = get_connection()
    cursor = connection.cursor(cursor_factory=DictCursor)
    # Write a query to the database using the embedding
    query = f"""
    SELECT * FROM chunk 
    ORDER BY vector <-> '{embedding_str}'::vector
    LIMIT {max_items};
    """
    cursor.execute(query)
    return [CommentChunk.from_dict(item) for item in cursor.fetchall()]


def keyword_search(keywords, max_items: int = 25):
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=DictCursor)
    queries = ",\n".join(
        [
            f"paradedb.term(field => 'text', value => '{keyword}'),\nparadedb.term(field => 'context', value => '{keyword}')"
            for keyword in keywords
        ]
    )
    query = f"""
    SELECT * FROM search_idx.search(
        query => paradedb.term_set(
            terms => ARRAY[
                {queries}
            ]
        ),
        limit_rows => {max_items}
    )
    """
    cursor.execute(query)
    return [CommentChunk.from_dict(item) for item in cursor.fetchall()]
