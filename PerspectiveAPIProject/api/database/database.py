import os
import psycopg2
from psycopg2.extras import DictCursor, register_uuid
from psycopg2.extensions import connection, cursor
from flask import g
from typing import Tuple

# Register UUID support for psycopg2
register_uuid()

# Database connection details (replace with your actual details or environment variables).
DB_NAME = "skg023"
DB_USER = "postgres"
DB_PASSWORD = "232222"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_SCHEMA = "recsui"


def get_db_connection() -> Tuple[connection, cursor]:
    """
    Establishes a connection to the PostgreSQL database and returns
    both the connection and a cursor object.

    Raises:
        psycopg2.Error: If the connection fails.
    """
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        # Use DictCursor to return query results as dictionaries
        curr = conn.cursor(cursor_factory=DictCursor)
        curr.execute(f"SET search_path TO {DB_SCHEMA};")
        print("Successfully connected to the database.")
        return conn, curr
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        raise


def close_db_connection(conn: connection, curr: cursor):
    """Closes the database cursor and connection."""
    if curr:
        curr.close()
    if conn:
        conn.close()
    print("Database connection closed.")


def get_db():
    """
    Provides a database connection and cursor that is local to the current request.
    If they don't exist for the request, it creates new ones.
    """
    if 'db_conn' not in g or 'db_curr' not in g:
        try:
            conn, curr = get_db_connection()
            g.db_conn = conn
            g.db_curr = curr
        except psycopg2.Error as e:
            raise ConnectionError(f"Failed to get database connection: {e}") from e

    return g.db_conn, g.db_curr