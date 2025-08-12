# ====================================================================================
# File: perspective_model.py
# Description: Data access layer for interacting with the PostgreSQL database.
# This module contains the business logic for all CRUD operations on the
# `perspectives` table. It no longer manages the database connection itself.
# ====================================================================================

import psycopg2
from psycopg2.extensions import connection, cursor
from typing import List, Optional, Dict, Any
import json
import os

from perspectives_app.perspective_schemas import ColumnState, UserPerspectiveCreate, ColumnStateUpdate


class PerspectiveModel:
    """
    Handles all business logic for CRUD operations on the 'perspectives' table.
    Methods in this class accept a cursor object to perform database operations.
    """

    def get_user_perspective(self, curr: cursor, username: str) -> Optional[Dict[str, Any]]:
        """Fetches the entire perspective for a given username."""
        try:
            query = "SELECT * FROM perspectives WHERE username = %s;"
            curr.execute(query, (username,))
            record = curr.fetchone()
            if record:
                columns = [desc[0] for desc in curr.description]
                perspective_data = dict(zip(columns, record))
                for key in ['column_state', 'sort_model', 'filter_model']:
                    if key in perspective_data and isinstance(perspective_data[key], str):
                        perspective_data[key] = json.loads(perspective_data[key])
                return perspective_data
            return None
        except psycopg2.Error as e:
            print(f"Error fetching user perspective: {e}")
            return None

    def create_or_update_perspective(self, conn: connection, curr: cursor, data: UserPerspectiveCreate) -> bool:
        """
        Inserts a new perspective for a user or updates it if the user already exists.
        """
        try:
            existing_user = self.get_user_perspective(curr, data.username)

            if existing_user:
                current_column_states = existing_user.get('column_state', [])
                new_column_states = data.column_state
                current_map = {cs['name']: cs for cs in current_column_states}

                updated_column_states = []
                for new_cs in new_column_states:
                    if new_cs.name in current_map:
                        current_map[new_cs.name] = new_cs.model_dump()
                    else:
                        updated_column_states.append(new_cs.model_dump())

                final_column_states = list(current_map.values()) + updated_column_states

                update_query = """
                               UPDATE perspectives \
                               SET column_state = %s::jsonb, 
                        updated_by = %s
                               WHERE username = %s; \
                               """
                curr.execute(update_query, (
                    json.dumps(final_column_states),
                    data.updated_by,
                    data.username
                ))
                conn.commit()
                return True
            else:
                insert_query = """
                               INSERT INTO perspectives (username, layout_name, column_state, sort_model, filter_model, \
                                                         updated_by)
                               VALUES (%s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s); \
                               """
                curr.execute(insert_query, (
                    data.username,
                    data.layout_name,
                    json.dumps([cs.model_dump() for cs in data.column_state]),
                    json.dumps(data.sort_model),
                    json.dumps(data.filter_model),
                    data.updated_by
                ))
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Error creating or updating perspective: {e}")
            conn.rollback()
            return False

    def get_all_column_states(self, curr: cursor, username: str) -> Optional[List[Dict[str, Any]]]:
        """Fetches all column states for a given user."""
        perspective = self.get_user_perspective(curr, username)
        return perspective.get('column_state') if perspective else None

    def update_column_state_by_name(self, conn: connection, curr: cursor, username: str, name: str,
                                    update_data: ColumnStateUpdate) -> bool:
        """
        Updates a specific column state entry by its name for a given user.
        """
        try:
            perspective = self.get_user_perspective(curr, username)
            if not perspective:
                return False

            column_states = perspective.get('column_state', [])
            found = False
            for cs in column_states:
                if cs.get('name') == name:
                    update_dict = update_data.model_dump(exclude_unset=True)
                    cs.update(update_dict)
                    found = True
                    break

            if found:
                update_query = "UPDATE perspectives SET column_state = %s::jsonb WHERE username = %s;"
                curr.execute(update_query, (json.dumps(column_states), username))
                conn.commit()
                return True
            else:
                print(f"Column state with name '{name}' not found for user '{username}'.")
                return False
        except psycopg2.Error as e:
            print(f"Error updating column state by name: {e}")
            conn.rollback()
            return False

    def delete_column_state_by_name(self, conn: connection, curr: cursor, username: str, name: str) -> bool:
        """Deletes a specific column state entry by its name for a given user."""
        try:
            perspective = self.get_user_perspective(curr, username)
            if not perspective:
                return False

            column_states = perspective.get('column_state', [])
            initial_count = len(column_states)
            updated_column_states = [cs for cs in column_states if cs.get('name') != name]

            if len(updated_column_states) < initial_count:
                update_query = "UPDATE perspectives SET column_state = %s::jsonb WHERE username = %s;"
                curr.execute(update_query, (json.dumps(updated_column_states), username))
                conn.commit()
                return True
            else:
                print(f"Column state with name '{name}' not found for user '{username}'.")
                return False
        except psycopg2.Error as e:
            print(f"Error deleting column state by name: {e}")
            conn.rollback()
            return False