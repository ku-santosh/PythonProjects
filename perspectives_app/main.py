#
# This is a complete, runnable FastAPI application for a Perspective CRUD API.
# It is structured into a logical folder layout as requested.
# To run this application, you need to have FastAPI, Uvicorn, SQLAlchemy, and psycopg2 installed:
# pip install fastapi uvicorn "sqlalchemy[asyncio]" psycopg2-binary
#
# Remember to update the database connection string with your actual credentials.
#
# ------------------ FILE: main.py ------------------
# The main application entry point.
#
# To run: uvicorn main:app --reload
#
import uvicorn
from fastapi import FastAPI
from perspectives_app.app.routes.perspectives import perspective
from perspectives_app.app.database.database import engine, Base

# This function creates the database tables when the application starts.
async def create_db_and_tables():
    """Initializes the database and creates tables based on the models."""
    async with engine.begin() as conn:
        # Use a transaction to create tables within the specified schema
        await conn.execute("CREATE SCHEMA IF NOT EXISTS recsui")
        await conn.run_sync(Base.metadata.create_all)

# Initialize the FastAPI application
app = FastAPI(title="Perspective API", version="1.0.0")

# Include the API router
app.include_router(perspective.router, prefix="/api/v1", tags=["Perspectives"])

# Register the event to create tables on startup
@app.on_event("startup")
async def startup_event():
    await create_db_and_tables()
    print("Database tables created/checked.")