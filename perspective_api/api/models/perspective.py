from datetime import datetime
from typing import Optional, List, Dict, Any

class FilterDetail:
    def __init__(self, type: str, filter: str):
        self.type = type
        self.filter = filter

class ColumnState:
    def __init__(self, name: str, view: str, defaultColumns: List[str], default: bool):
        self.name = name
        self.view = view
        self.defaultColumns = defaultColumns
        self.default = default

class ViewSetting:
    def __init__(self, name: str, view: str, filters: Dict[str, FilterDetail], default: bool):
        self.name = name
        self.view = view
        self.filters = filters
        self.default = default

class Perspective:
    def __init__(self, id: int, username: str, layout_name: str, updated_by: str, updated_time: datetime,
                 column_state: Optional[List[ColumnState]] = None, sort_model: Optional[List[ViewSetting]] = None,
                 filter_model: Optional[List[ViewSetting]] = None):
        self.id = id
        self.username = username
        self.layout_name = layout_name
        self.updated_by = updated_by
        self.updated_time = updated_time
        self.column_state = column_state if column_state is not None else []
        self.sort_model = sort_model if sort_model is not None else []
        self.filter_model = filter_model if filter_model is not None else []
