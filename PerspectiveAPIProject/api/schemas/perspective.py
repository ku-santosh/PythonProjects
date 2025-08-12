from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_serializer

# Schema for the nested filter details within sort and filter models
class FilterDetail(BaseModel):
    type: str
    filter: str

# Schema for the column_state data structure
class ColumnState(BaseModel):
    name: str
    view: str
    defaultColumns: List[str]
    default: bool

# Schema for the sort_model and filter_model data structures
class ViewSetting(BaseModel):
    name: str
    view: str
    filters: Dict[str, FilterDetail]
    default: bool

# Base schema for creating or updating a perspective.
# All fields are validated to be non-empty strings as requested.
class PerspectiveBase(BaseModel):
    username: str = Field(..., min_length=1, description="Username cannot be empty")
    layout_name: str = Field(..., min_length=1, description="Layout name cannot be empty")
    updated_by: str = Field(..., min_length=1, description="Updater's email cannot be empty")
    column_state: Optional[List[ColumnState]] = []
    sort_model: Optional[List[ViewSetting]] = []
    filter_model: Optional[List[ViewSetting]] = []

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
    sort_model: Optional[List[ViewSetting]] = None
    filter_model: Optional[List[ViewSetting]] = None

# Full schema for a perspective, including auto-generated fields.
class Perspective(PerspectiveBase):
    id: int
    updated_time: str

    class Config:
        from_attributes = True