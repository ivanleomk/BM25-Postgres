import psycopg2
from lib.env import Settings
from psycopg2.extensions import connection

settings = Settings()


def get_connection() -> connection:
    return psycopg2.connect(
        database=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host="localhost",
        port="5432",
    )
