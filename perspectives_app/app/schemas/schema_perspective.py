# Defines the Pydantic schemas for request and response validation.
#
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# Schema for the column_state data structure
class ColumnState(BaseModel):
    name: str
    view: str
    defaultColumns: List[str]
    default: bool

# Schema for the sort_model data structure
class SortModel(BaseModel):
    name: str
    view: str
    filters: Dict[str, Any]
    default: bool

# Base schema for creating or updating a perspective.
# All fields are validated to be non-empty strings as requested.
class PerspectiveBase(BaseModel):
    username: str = Field(..., min_length=1, description="Username cannot be empty")
    layout_name: str = Field(..., min_length=1, description="Layout name cannot be empty")
    updated_by: str = Field(..., min_length=1, description="Updater's email cannot be empty")
    column_state: Optional[List[ColumnState]] = []
    sort_model: Optional[List[SortModel]] = []
    filter_model: Optional[Dict[str, Any]] = {}

# Schema for creating a new perspective (inherits from PerspectiveBase)
class PerspectiveCreate(PerspectiveBase):
    pass

# Schema for updating an existing perspective.
# All fields are optional for partial updates.
class PerspectiveUpdate(PerspectiveBase):
    username: Optional[str] = Field(None, min_length=1, description="Username cannot be empty")
    layout_name: Optional[str] = Field(None, min_length=1, description="Layout name cannot be empty")
    updated_by: Optional[str] = Field(None, min_length=1, description="Updater's email cannot be empty")
    column_state: Optional[List[ColumnState]] = None
    sort_model: Optional[List[SortModel]] = None
    filter_model: Optional[Dict[str, Any]] = None

# Full schema for a perspective, including auto-generated fields.
class Perspective(PerspectiveBase):
    id: int
    updated_time: datetime

    class Config:
        from_attributes = True