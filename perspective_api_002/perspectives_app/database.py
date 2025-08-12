# ====================================================================================
# File: database.py
# Description: This file manages the PostgreSQL database connection and cursor.
# The connection logic is now separate from the business logic.
# ====================================================================================

import psycopg2
from psycopg2.extensions import connection, cursor
from typing import Tuple

#DATABASE_URL = "postgresql+asyncpg://user:password@host:5432/skg023"
#DATABASE_URL = "postgresql+asyncpg://postgres:232222@localhost:5432/skg023"

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
        curr = conn.cursor()
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