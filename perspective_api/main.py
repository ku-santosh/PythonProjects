import uvicorn
from fastapi import FastAPI
from api.v1.endpoints import perspective

# Initialize the FastAPI application
app = FastAPI(title="Perspective API", version="1.0.0")

# Include the API router
app.include_router(perspective.router, prefix="/api/v1", tags=["Perspectives"])