import psycopg2
from psycopg2 import OperationalError

import socket


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


def create_connection():
    try:
        connection = psycopg2.connect(
            database="mydatabase",
            user="myuser",
            password="mypassword",
            host="localhost",
            port="5432",
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        raise e
        print(f"The error '{e}' occurred")
    return connection


# Connect to the PostgreSQL database
create_connection()
