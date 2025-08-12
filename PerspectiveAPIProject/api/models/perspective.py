from typing import Optional, List, Dict, Any
from datetime import datetime


class ColumnState:
    """Represents the structure of a single item in the column_state array."""

    def __init__(self, name: str, view: str, defaultColumns: List[str], default: bool):
        self.name = name
        self.view = view
        self.defaultColumns = defaultColumns
        self.default = default


class FilterDetail:
    """Represents the structure of a filter detail."""

    def __init__(self, type: str, filter: str):
        self.type = type
        self.filter = filter


class ViewSetting:
    """Represents the structure of a single item in the sort_model or filter_model arrays."""

    def __init__(self, name: str, view: str, filters: Dict[str, FilterDetail], default: bool):
        self.name = name
        self.view = view
        self.filters = filters
        self.default = default


class Perspective:
    """
    Data Transfer Object (DTO) for the 'perspectives' table.
    This class is not tied to an ORM and is used to represent a database row.
    """

    def __init__(self, id: int, username: str, layout_name: str, updated_by: str,
                 column_state: List[ColumnState], sort_model: List[ViewSetting],
                 filter_model: List[ViewSetting], updated_time: datetime):
        self.id = id
        self.username = username
        self.layout_name = layout_name
        self.updated_by = updated_by
        self.column_state = column_state
        self.sort_model = sort_model
        self.filter_model = filter_model
        self.updated_time = updated_time

    @staticmethod
    def from_dict(data: dict):
        """Converts a dictionary (from a psycopg2 query) to a Perspective object."""
        if not data:
            return None

        # Recursively create objects for nested data
        column_state = [ColumnState(**cs) for cs in data.get('column_state', [])]

        sort_model = []
        for sm in data.get('sort_model', []):
            filters = {k: FilterDetail(**v) for k, v in sm.get('filters', {}).items()}
            sort_model.append(ViewSetting(name=sm['name'], view=sm['view'], filters=filters, default=sm['default']))

        filter_model = []
        for fm in data.get('filter_model', []):
            filters = {k: FilterDetail(**v) for k, v in fm.get('filters', {}).items()}
            filter_model.append(ViewSetting(name=fm['name'], view=fm['view'], filters=filters, default=fm['default']))

        return Perspective(
            id=data['id'],
            username=data['username'],
            layout_name=data['layout_name'],
            updated_by=data['updated_by'],
            column_state=column_state,
            sort_model=sort_model,
            filter_model=filter_model,
            updated_time=data['updated_time']
        )