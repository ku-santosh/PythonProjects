import os
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text

""" 
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="skg023",
        user="postgres",
        password="232222"
    )
    print("Connection to PostgreSQL successful!")

    # You can now create a cursor and execute queries
    # cur = conn.cursor()
    # cur.execute("SELECT version();")
    # print(cur.fetchone())

except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL: {e}")

finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("PostgreSQL connection closed.")

"""

# Define the database connection URL.
# Replace the placeholders with your actual PostgreSQL credentials.
# The database name 'skg023' and schema 'recsui' are used as specified.
#DATABASE_URL = "postgresql+asyncpg://user:password@host:5432/skg023"
DATABASE_URL = "postgresql+asyncpg://postgres:232222@localhost:5432/skg023"
print(f'DATABASE_URL => ', DATABASE_URL)

# Create the asynchronous database engine
engine = create_async_engine(DATABASE_URL, echo=True)
"""
# You can now use the engine to interact with the database
with engine.connect() as connection:
    result = connection.execute(text("SELECT version();"))
    print(f'result.scalar() => ', result.scalar())
"""

# Create a sessionmaker for generating new AsyncSession objects
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# A base class for declarative models
Base = declarative_base()

# Dependency function to get a database session
async def get_db() -> AsyncGenerator[AsyncSession | Any, Any]:
    """Provides an asynchronous database session for endpoints."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()