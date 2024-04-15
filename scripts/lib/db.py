import psycopg2
from lib.env import Settings
from psycopg2.extensions import connection
from typing import List
from openai import OpenAI
from psycopg2.extras import DictCursor

settings = Settings()


def get_connection() -> connection:
    return psycopg2.connect(
        database=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host="localhost",
        port="5432",
    )


def vector_search(embedding, max_items: str = 25):
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
