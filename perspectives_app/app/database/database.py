# ------------------ FILE: database/database.py ------------------
# Handles the PostgreSQL database connection and session management.
#
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base

# Define the database connection URL.
# Replace the placeholders with your actual PostgreSQL credentials.
# The database name 'skg023' and schema 'recsui' are used as specified.
#DATABASE_URL = "postgresql+asyncpg://user:password@host:5432/skg023"
DATABASE_URL = "postgresql+psycopg2://postgres:232222@localhost:5432/skg023"

# Create the asynchronous database engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a sessionmaker for generating new AsyncSession objects
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# A base class for declarative models
Base = declarative_base()

# Dependency function to get a database session
async def get_db() -> AsyncSession:
    """Provides an asynchronous database session for endpoints."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:232222@localhost:5432/skg023"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print(f"engine => ", engine)
print(f"SessionLocal => ", SessionLocal)
"""
""

