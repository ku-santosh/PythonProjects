# ====================================================================================
# File: perspective_route.py
# Description: API routes/endpoints for the perspective service.
# It uses the Pydantic schemas for data validation and the model for database interaction.
# ====================================================================================

from fastapi import APIRouter, HTTPException, Path
from typing import List

from  perspectives_app.perspective_schemas import UserPerspectiveCreate, ColumnState, ColumnStateUpdate
from perspectives_app.perspective_model import PerspectiveModel
from perspectives_app.database import get_db_connection, close_db_connection

# Create an instance of the router.
router = APIRouter(
    prefix="/perspectives",
    tags=["perspectives"],
    responses={404: {"description": "Not found"}},
)

# Initialize the database model.
db_model = PerspectiveModel()

@router.post("/column_state", response_model=bool)
def create_or_update_column_states(data: UserPerspectiveCreate):
    """
    Creates a new user perspective or updates an existing one.
    This endpoint handles the logic of checking if the user exists and
    then either inserting a new record or updating the column_state array.
    """
    conn, curr = None, None
    try:
        conn, curr = get_db_connection()
        success = db_model.create_or_update_perspective(conn, curr, data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save perspective data.")
        return True
    finally:
        if conn and curr:
            close_db_connection(conn, curr)

@router.get("/column_state/{username}", response_model=List[ColumnState])
def get_column_states(username: str):
    """
    Retrieves all column states for a specified user.
    """
    conn, curr = None, None
    try:
        conn, curr = get_db_connection()
        column_states = db_model.get_all_column_states(curr, username)
        if column_states is None:
            raise HTTPException(status_code=404, detail=f"User '{username}' or their column states not found.")
        return column_states
    finally:
        if conn and curr:
            close_db_connection(conn, curr)

@router.put("/column_state/{username}/{name}", response_model=bool)
def update_column_state_by_name(
    username: str,
    name: str,
    update_data: ColumnStateUpdate
):
    """
    Updates a specific column state entry by its unique name for a given user.
    """
    conn, curr = None, None
    try:
        conn, curr = get_db_connection()
        success = db_model.update_column_state_by_name(conn, curr, username, name, update_data)
        if not success:
            raise HTTPException(status_code=404, detail=f"Column state '{name}' not found or update failed.")
        return True
    finally:
        if conn and curr:
            close_db_connection(conn, curr)

@router.delete("/column_state/{username}/{name}", response_model=bool)
def delete_column_state_by_name(username: str, name: str):
    """
    Deletes a specific column state entry by its unique name for a given user.
    """
    conn, curr = None, None
    try:
        conn, curr = get_db_connection()
        success = db_model.delete_column_state_by_name(conn, curr, username, name)
        if not success:
            raise HTTPException(status_code=404, detail=f"Column state '{name}' not found or delete failed.")
        return True
    finally:
        if conn and curr:
            close_db_connection(conn, curr)