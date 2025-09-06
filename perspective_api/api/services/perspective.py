import psycopg2
from psycopg2.extras import DictCursor
from typing import List, Optional
import json
from ..models.perspective import Perspective as PerspectiveModel, ViewSetting as ViewSettingModel, \
    FilterDetail as FilterDetailModel, ColumnState as ColumnStateModel
from ..schemas.perspective import PerspectiveCreate, PerspectiveUpdate
from psycopg2.extensions import connection, cursor
from datetime import datetime


class PerspectiveService:
    """Service class for performing CRUD operations on Perspective data using psycopg2."""

    def __init__(self, db_conn: connection, db_curr: cursor):
        self.db_conn = db_conn
        self.db_curr = db_curr

    def get_all_perspectives(self) -> List[PerspectiveModel]:
        """Retrieves all perspective records from the database and maps them to PerspectiveModel objects."""
        self.db_curr.execute("SELECT * FROM recsui.perspectives;")
        perspectives = self.db_curr.fetchall()
        return [self._map_record_to_model(p) for p in perspectives]

    def get_perspective_by_id(self, perspective_id: int) -> Optional[PerspectiveModel]:
        """Retrieves a single perspective record by its ID."""
        self.db_curr.execute("SELECT * FROM recsui.perspectives WHERE id = %s;", (perspective_id,))
        perspective = self.db_curr.fetchone()
        return self._map_record_to_model(perspective) if perspective else None

    def get_perspective_by_username(self, username: str) -> Optional[PerspectiveModel]:
        """Retrieves a single perspective record by its username."""
        self.db_curr.execute("SELECT * FROM recsui.perspectives WHERE username = %s;", (username,))
        perspective = self.db_curr.fetchone()
        return self._map_record_to_model(perspective) if perspective else None

    def create_perspective(self, perspective_in: PerspectiveCreate) -> PerspectiveModel:
        """Creates a new perspective record in the database."""
        try:
            self.db_curr.execute(
                """
                INSERT INTO recsui.perspectives (username, layout_name, updated_by, column_state, sort_model, filter_model)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *;
                """,
                (
                    perspective_in.username,
                    perspective_in.layout_name,
                    perspective_in.updated_by,
                    json.dumps([cs.model_dump() for cs in perspective_in.column_state]),
                    json.dumps([sm.model_dump() for sm in perspective_in.sort_model]),
                    json.dumps([fm.model_dump() for fm in perspective_in.filter_model])
                )
            )
            new_perspective = self.db_curr.fetchone()
            self.db_conn.commit()
            return self._map_record_to_model(new_perspective)
        except Exception as e:
            self.db_conn.rollback()
            raise e

    def update_perspective(self, perspective_id: int, perspective_in: PerspectiveUpdate) -> Optional[PerspectiveModel]:
        """Updates an existing perspective record."""
        # Find the existing perspective by ID
        perspective_to_update = self.get_perspective_by_id(perspective_id)
        if not perspective_to_update:
            return None

        # Build the update query dynamically
        update_clauses = []
        update_data = []

        perspective_dict = perspective_in.model_dump(exclude_unset=True)

        if 'username' in perspective_dict:
            update_clauses.append("username = %s")
            update_data.append(perspective_dict['username'])
        if 'layout_name' in perspective_dict:
            update_clauses.append("layout_name = %s")
            update_data.append(perspective_dict['layout_name'])
        if 'updated_by' in perspective_dict:
            update_clauses.append("updated_by = %s")
            update_data.append(perspective_dict['updated_by'])
        if 'column_state' in perspective_dict:
            update_clauses.append("column_state = %s")
            update_data.append(json.dumps([cs.model_dump() for cs in perspective_in.column_state]))
        if 'sort_model' in perspective_dict:
            update_clauses.append("sort_model = %s")
            update_data.append(json.dumps([sm.model_dump() for sm in perspective_in.sort_model]))
        if 'filter_model' in perspective_dict:
            update_clauses.append("filter_model = %s")
            update_data.append(json.dumps([fm.model_dump() for fm in perspective_in.filter_model]))

        if not update_clauses:
            return perspective_to_update  # No changes to apply

        query = f"UPDATE recsui.perspectives SET {', '.join(update_clauses)} WHERE id = %s RETURNING *;"
        update_data.append(perspective_id)

        try:
            self.db_curr.execute(query, tuple(update_data))
            updated_perspective = self.db_curr.fetchone()
            self.db_conn.commit()
            return self._map_record_to_model(updated_perspective)
        except Exception as e:
            self.db_conn.rollback()
            raise e

    def update_column_state(self, perspective_id: int, column_states: List[ColumnStateModel]) -> Optional[
        PerspectiveModel]:
        """Updates only the column_state for a perspective record."""
        try:
            self.db_curr.execute(
                "UPDATE recsui.perspectives SET column_state = %s WHERE id = %s RETURNING *;",
                (json.dumps([cs.model_dump() for cs in column_states]), perspective_id)
            )
            updated_perspective = self.db_curr.fetchone()
            if updated_perspective:
                self.db_conn.commit()
                return self._map_record_to_model(updated_perspective)
            else:
                self.db_conn.rollback()
                return None
        except Exception as e:
            self.db_conn.rollback()
            raise e

    def update_filter_model(self, perspective_id: int, view_settings: List[ViewSettingModel]) -> Optional[
        PerspectiveModel]:
        """Updates only the filter_model for a perspective record."""
        try:
            self.db_curr.execute(
                "UPDATE recsui.perspectives SET filter_model = %s WHERE id = %s RETURNING *;",
                (json.dumps([vs.model_dump() for vs in view_settings]), perspective_id)
            )
            updated_perspective = self.db_curr.fetchone()
            if updated_perspective:
                self.db_conn.commit()
                return self._map_record_to_model(updated_perspective)
            else:
                self.db_conn.rollback()
                return None
        except Exception as e:
            self.db_conn.rollback()
            raise e

    def save_single_filter(self, perspective_id: int, new_filter: ViewSettingModel) -> Optional[PerspectiveModel]:
        """
        Adds or updates a single filter within a perspective's filter_model.
        """
        try:
            # 1. Fetch the current perspective's filter_model
            current_perspective = self.get_perspective_by_id(perspective_id)
            if not current_perspective:
                return None

            current_filters = current_perspective.filter_model or []
            updated = False

            # 2. Iterate and update if the filter already exists
            for i, filter_item in enumerate(current_filters):
                if filter_item.name == new_filter.name and filter_item.view == new_filter.view:
                    current_filters[i] = new_filter
                    updated = True
                    break

            # 3. If no existing filter was found, append the new one
            if not updated:
                current_filters.append(new_filter)

            # 4. Save the updated list back to the database
            self.db_curr.execute(
                "UPDATE recsui.perspectives SET filter_model = %s WHERE id = %s RETURNING *;",
                (json.dumps([f.model_dump() for f in current_filters]), perspective_id)
            )
            updated_perspective = self.db_curr.fetchone()
            if updated_perspective:
                self.db_conn.commit()
                return self._map_record_to_model(updated_perspective)
            else:
                self.db_conn.rollback()
                return None
        except Exception as e:
            self.db_conn.rollback()
            raise e

    def delete_perspective(self, perspective_id: int) -> bool:
        """Deletes a perspective record by its ID."""
        try:
            self.db_curr.execute("DELETE FROM recsui.perspectives WHERE id = %s RETURNING id;", (perspective_id,))
            deleted_row = self.db_curr.fetchone()
            if deleted_row:
                self.db_conn.commit()
                return True
            else:
                self.db_conn.rollback()
                return False
        except Exception as e:
            self.db_conn.rollback()
            raise e

    def _map_record_to_model(self, record: dict) -> PerspectiveModel:
        """Helper to map a database record (dict) to a PerspectiveModel object."""
        # Convert JSON strings from database to Python objects
        column_state_data = json.loads(record['column_state']) if record['column_state'] else []
        sort_model_data = json.loads(record['sort_model']) if record['sort_model'] else []
        filter_model_data = json.loads(record['filter_model']) if record['filter_model'] else []

        # Map the nested data to their respective models
        column_state_models = [ColumnStateModel(**cs) for cs in column_state_data]
        sort_model_models = [ViewSettingModel(
            name=sm['name'],
            view=sm['view'],
            filters={k: FilterDetailModel(**v) for k, v in sm['filters'].items()},
            default=sm['default']
        ) for sm in sort_model_data]
        filter_model_models = [ViewSettingModel(
            name=fm['name'],
            view=fm['view'],
            filters={k: FilterDetailModel(**v) for k, v in fm['filters'].items()},
            default=fm['default']
        ) for fm in filter_model_data]

        # Create the top-level PerspectiveModel object
        return PerspectiveModel(
            id=record['id'],
            username=record['username'],
            layout_name=record['layout_name'],
            updated_by=record['updated_by'],
            updated_time=record['updated_time'],
            column_state=column_state_models,
            sort_model=sort_model_models,
            filter_model=filter_model_models
        )
