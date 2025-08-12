# ------------------ FILE: api/v1/endpoints/perspective.py ------------------
# Defines the API routes for the perspective resource.
#
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database.database import get_db
from ...schemas.perspective import Perspective, PerspectiveCreate, PerspectiveUpdate
from ...services.perspective import PerspectiveService

# Create an APIRouter for this module
router = APIRouter()

@router.get("/perspectives/", response_model=List[Perspective])
async def get_all(db: AsyncSession = Depends(get_db)):
    """Retrieves all perspectives from the database."""
    service = PerspectiveService(db)
    perspectives = await service.get_all_perspectives()
    return perspectives

@router.get("/perspectives/{perspective_id}", response_model=Perspective)
async def get_by_id(perspective_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieves a single perspective by its ID."""
    service = PerspectiveService(db)
    perspective = await service.get_perspective_by_id(perspective_id)
    if not perspective:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perspective not found")
    return perspective

@router.post("/perspectives/", response_model=Perspective, status_code=status.HTTP_201_CREATED)
async def create(perspective_in: PerspectiveCreate, db: AsyncSession = Depends(get_db)):
    """Creates a new perspective in the database."""
    service = PerspectiveService(db)
    new_perspective = await service.create_perspective(perspective_in)
    return new_perspective

@router.put("/perspectives/{perspective_id}", response_model=Perspective)
async def update(perspective_id: int, perspective_in: PerspectiveUpdate, db: AsyncSession = Depends(get_db)):
    """Updates an existing perspective by its ID."""
    service = PerspectiveService(db)
    updated_perspective = await service.update_perspective(perspective_id, perspective_in)
    if not updated_perspective:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perspective not found")
    return updated_perspective

@router.delete("/perspectives/{perspective_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(perspective_id: int, db: AsyncSession = Depends(get_db)):
    """Deletes a perspective by its ID."""
    service = PerspectiveService(db)
    if not await service.delete_perspective(perspective_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perspective not found")
    return