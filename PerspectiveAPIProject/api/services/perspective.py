import psycopg2
from psycopg2.extras import DictCursor
from typing import List, Optional
import json
from ..models.perspective import Perspective as PerspectiveModel
from ..schemas.perspective import PerspectiveCreate, PerspectiveUpdate
from psycopg2.extensions import connection, cursor


class PerspectiveService:
    """Service class for performing CRUD operations on Perspective data using psycopg2."""

    def __init__(self, db_conn: connection, db_curr: cursor):
        self.db_conn = db_conn
        self.db_curr = db_curr

    def get_all_perspectives(self) -> List[PerspectiveModel]:
        """Retrieves all perspective records from the database."""
        self.db_curr.execute("SELECT * FROM recsui.perspectives;")
        perspectives = self.db_curr.fetchall()
        return [PerspectiveModel.from_dict(p) for p in perspectives]

    def get_perspective_by_id(self, perspective_id: int) -> Optional[PerspectiveModel]:
        """Retrieves a single perspective record by its ID."""
        self.db_curr.execute("SELECT * FROM recsui.perspectives WHERE id = %s;", (perspective_id,))
        perspective = self.db_curr.fetchone()
        return PerspectiveModel.from_dict(perspective)

    def get_perspective_by_username(self, username: str) -> Optional[PerspectiveModel]:
        """Retrieves a single perspective record by its username."""
        self.db_curr.execute("SELECT * FROM recsui.perspectives WHERE username = %s;", (username,))
        perspective = self.db_curr.fetchone()
        return PerspectiveModel.from_dict(perspective)

    def create_perspective(self, perspective_in: PerspectiveCreate) -> PerspectiveModel:
        """Creates a new perspective record in the database."""
        # Convert Pydantic models to JSON strings for database insertion
        column_state_json = json.dumps([cs.model_dump() for cs in perspective_in.column_state])
        sort_model_json = json.dumps([sm.model_dump() for sm in perspective_in.sort_model])
        filter_model_json = json.dumps([fm.model_dump() for fm in perspective_in.filter_model])

        try:
            self.db_curr.execute(
                """
                INSERT INTO recsui.perspectives (username, layout_name, updated_by, column_state, sort_model, filter_model)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING *;
                """,
                (
                    perspective_in.username,
                    perspective_in.layout_name,
                    perspective_in.updated_by,
                    column_state_json,
                    sort_model_json,
                    filter_model_json
                )
            )
            new_perspective = self.db_curr.fetchone()
            self.db_conn.commit()
            return PerspectiveModel.from_dict(new_perspective)
        except Exception as e:
            self.db_conn.rollback()
            raise e

    def update_perspective(self, perspective_id: int, perspective_in: PerspectiveUpdate) -> Optional[PerspectiveModel]:
        """Updates an existing perspective record."""
        # Check if the perspective exists
        perspective_to_update = self.get_perspective_by_id(perspective_id)
        if not perspective_to_update:
            return None

        # Build the update query dynamically
        update_clauses = []
        update_data = []

        # Convert Pydantic models to JSON strings for database update
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
            return PerspectiveModel.from_dict(updated_perspective)
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

    def update_perspective_by_username(self, username: str, perspective_in: PerspectiveUpdate) -> Optional[
        PerspectiveModel]:
        """Updates an existing perspective record by its username."""
        # Check if the perspective exists
        perspective_to_update = self.get_perspective_by_username(username)
        if not perspective_to_update:
            return None

        # Build the update query dynamically
        update_clauses = []
        update_data = []

        # Convert Pydantic models to JSON strings for database update
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
            return PerspectiveModel.from_dict(perspective_to_update)  # No changes to apply

        query = f"UPDATE recsui.perspectives SET {', '.join(update_clauses)} WHERE username = %s RETURNING *;"
        update_data.append(username)

        try:
            self.db_curr.execute(query, tuple(update_data))
            updated_perspective = self.db_curr.fetchone()
            self.db_conn.commit()
            return PerspectiveModel.from_dict(updated_perspective)
        except Exception as e:
            self.db_conn.rollback()
            raise e