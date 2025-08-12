# ====================================================================================
# File: perspective_schemas.py
# Description: Pydantic models for data validation and serialization.
# These schemas define the structure of the data for requests and responses.
# ====================================================================================

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Schema for the individual column state object.
class ColumnState(BaseModel):
    name: str = Field(..., description="The unique name for the column state.")
    view: str
    defaultColumns: List[str]
    default: bool

# Schema for the incoming request body that contains all data.
class UserPerspectiveCreate(BaseModel):
    username: str
    layout_name: str
    column_state: List[ColumnState]
    sort_model: List[Dict[str, Any]]
    filter_model: List[Dict[str, Any]]
    updated_by: str

# Schema for a partial update of a column state.
class ColumnStateUpdate(BaseModel):
    view: Optional[str] = None
    defaultColumns: Optional[List[str]] = None
    default: Optional[bool] = None