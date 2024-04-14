from psycopg2 import OperationalError
from lib.env import Settings
import socket
from lib.db import get_connection

settings = Settings()


def check_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)  # Timeout for the operation
    try:
        sock.connect((ip, port))
        sock.shutdown(socket.SHUT_RDWR)
        return True
    except OperationalError as e:
        raise e


# Check port 5432 on localhost
if check_port("127.0.0.1", 5432):
    print("Port 5432 is open")
else:
    print("Port 5432 is not open")


def verify_connection():
    try:
        connection = get_connection()
        print("Succesfully connected to database!")

        cursor = connection.cursor()
        insert_query = """INSERT INTO chunk (context, repo, vector, text, issue_id, issue_number, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id"""
        chunk_data = (
            "Sample context",
            "Sample repo",
            [0.0 for _ in range(1536)],
            "Sample text",
            1,
            1,
            "2021-01-01 00:00:00",
        )
        cursor.execute(insert_query, chunk_data)
        inserted_row_id = cursor.fetchone()[0]
        connection.commit()
        print(f"Row inserted into the chunk table with ID {inserted_row_id}")

        delete_query = """DELETE FROM chunk WHERE id = %s"""
        cursor.execute(delete_query, (inserted_row_id,))
        connection.commit()
        print(f"Row with ID {inserted_row_id} removed from the chunk table")
    except OperationalError as e:
        raise e
        print(f"The error '{e}' occurred")
    return connection


# Connect to the PostgreSQL database
verify_connection()
