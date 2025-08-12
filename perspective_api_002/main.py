# ====================================================================================
# File: main.py
# Description: Main entry point for the FastAPI application.
# It initializes the app and includes the API router.
# ====================================================================================

import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import Dict, Any

from perspectives_app.perspective_route import router

# A global variable to store the database connection pool or client.
# In a real application, you would initialize your database connection here.
db_client = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This function will run on application startup and shutdown.
    It's a perfect place to initialize and close resources, like a database connection pool.
    """
    print("Application startup...")
    # In a real app, initialize your database connection here.
    # For example:
    # from perspectives_app.perspective_model import get_database_connection
    # db_client['pool'] = await get_database_connection()
    yield
    print("Application shutdown...")
    # In a real app, close your database connection here.
    # For example:
    # await db_client['pool'].close()

app = FastAPI(
    title="Perspective API",
    description="A CRUD API for managing user perspectives and their column states.",
    version="1.0.0",
    lifespan=lifespan
)

# Include the router for the perspective endpoints.
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Perspective API"}

if __name__ == "__main__":
    # Use Uvicorn to run the FastAPI application.
    # The `reload=True` option is great for development as it restarts the server on code changes.
    uvicorn.run(app, host="0.0.0.0", port=8000)