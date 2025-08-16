from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
from ...schemas.perspective import PerspectiveCreate, PerspectiveUpdate, ColumnState, Perspective
from ...services.perspective import PerspectiveService
from ...database.database import get_db

column_state_bp = Blueprint('column_state', __name__)


def _convert_view_settings_to_dicts(view_settings):
    """
    Recursively converts a list of ViewSetting DTOs to a list of dictionaries,
    including the nested FilterDetail DTOs.
    """
    if not view_settings:
        return []

    dict_list = []
    for vs in view_settings:
        filters_dict = {k: v.__dict__ for k, v in vs.filters.items()}
        dict_list.append({
            "name": vs.name,
            "view": vs.view,
            "filters": filters_dict,
            "default": vs.default
        })
    return dict_list

@column_state_bp.route('/save', methods=['POST'])
def save_column_state_route():
    """
    Handles POST requests to save a column_state.
    If the user does not exist, a new perspective is created.
    If the user exists, the existing perspective's column_state is updated.
    """
    try:
        data = request.json
        username = data.get('username')
        column_state_data = data.get('column_state', [])

        if not username:
            return jsonify({"error": "Username is required."}), 400

        # Validate the incoming column_state data
        try:
            validated_column_state = [ColumnState.model_validate(cs) for cs in column_state_data]
        except ValidationError as e:
            return jsonify({"error": "Invalid column_state data", "detail": e.errors()}), 400

        conn, curr = get_db()
        service = PerspectiveService(conn, curr)

        existing_perspective = service.get_perspective_by_username(username)

        if existing_perspective:
            # If perspective exists, update the column_state
            layout_name_from_body = data.get('layout_name')
            updated_by_from_body = data.get('updated_by')

            # Recursively convert nested DTOs to dictionaries for Pydantic validation
            sort_model_as_dict = _convert_view_settings_to_dicts(existing_perspective.sort_model)
            filter_model_as_dict = _convert_view_settings_to_dicts(existing_perspective.filter_model)

            perspective_update = PerspectiveUpdate(
                username=username,
                layout_name=layout_name_from_body if layout_name_from_body else existing_perspective.layout_name,
                updated_by=updated_by_from_body if updated_by_from_body else existing_perspective.updated_by,
                column_state=validated_column_state,
                sort_model=sort_model_as_dict,
                filter_model=filter_model_as_dict
                #sort_model=existing_perspective.sort_model,
                #filter_model=existing_perspective.filter_model
            )
            updated_perspective_model = service.update_perspective_by_username(username, perspective_update)
            validated_updated_perspective = Perspective.model_validate(updated_perspective_model, from_attributes=True)
            return jsonify(validated_updated_perspective.model_dump(mode='json')), 200
        else:
            # If perspective does not exist, create a new one
            layout_name = data.get('layout_name')
            updated_by = data.get('updated_by')

            if not layout_name:
                return jsonify({"error": "layout_name is required for new perspectives."}), 400
            if not updated_by:
                return jsonify({"error": "updated_by is required for new perspectives."}), 400

            perspective_create = PerspectiveCreate(
                username=username,
                layout_name=layout_name,
                updated_by=updated_by,
                column_state=validated_column_state,
                sort_model=[],
                filter_model=[]
            )
            new_perspective_model = service.create_perspective(perspective_create)
            validated_new_perspective = Perspective.model_validate(new_perspective_model, from_attributes=True)
            return jsonify(validated_new_perspective.model_dump(mode='json')), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@column_state_bp.route('/save_single_column_state', methods=['POST'])
def save_single_column_state_route():
    """
    Handles POST requests to save or update one or more column_state items.
    This function implements an upsert logic based on the 'name' of each column state item.
    - If a column_state with the same name exists, it is updated.
    - If not, a new column_state item is added.
    - If the user does not exist, a new perspective is created.
    """
    try:
        data = request.json
        username = data.get('username')
        column_state_data = data.get('column_state')

        if not username:
            return jsonify({"error": "Username is required."}), 400

        if column_state_data is None:
            return jsonify({"error": "column_state data is required."}), 400

        column_states_to_process = column_state_data if isinstance(column_state_data, list) else [column_state_data]

        for item in column_states_to_process:
            if not isinstance(item, dict) or 'name' not in item:
                return jsonify(
                    {"error": "Each column state item must be a single JSON object with a 'name' field."}), 400

        try:
            validated_column_states = [ColumnState.model_validate(item) for item in column_states_to_process]
        except ValidationError as e:
            return jsonify({"error": "Invalid column_state data", "detail": e.errors()}), 400

        conn, curr = get_db()
        service = PerspectiveService(conn, curr)

        existing_perspective = service.get_perspective_by_username(username)

        if existing_perspective:
            # User exists, so apply the upsert logic
            existing_column_state_list = existing_perspective.column_state

            for validated_item in validated_column_states:
                # Convert the Pydantic model back to a dictionary for easier comparison and update
                validated_item_dict = validated_item.model_dump()
                # Ensure defaultColumns list has no duplicates
                validated_item_dict['defaultColumns'] = list(set(validated_item_dict['defaultColumns']))

                found = False
                for i, existing_item in enumerate(existing_column_state_list):
                    if existing_item.name == validated_item_dict['name']:
                        # Update the existing DTO object's attributes
                        existing_column_state_list[i].view = validated_item_dict['view']
                        existing_column_state_list[i].defaultColumns = validated_item_dict['defaultColumns']
                        existing_column_state_list[i].default = validated_item_dict['default']
                        found = True
                        break

                if not found:
                    # If no match was found, create a new DTO and append it to the list
                    existing_column_state_list.append(ColumnState(**validated_item_dict))

            # Now, create a list of dictionaries from the updated list of DTOs for the Pydantic model
            final_column_state_list_for_pydantic = [item.__dict__ for item in existing_column_state_list]

            layout_name_from_body = data.get('layout_name')
            updated_by_from_body = data.get('updated_by')

            # Recursively convert nested DTOs to dictionaries for Pydantic validation
            sort_model_as_dict = _convert_view_settings_to_dicts(existing_perspective.sort_model)
            filter_model_as_dict = _convert_view_settings_to_dicts(existing_perspective.filter_model)

            perspective_update = PerspectiveUpdate(
                username=username,
                layout_name=layout_name_from_body if layout_name_from_body else existing_perspective.layout_name,
                updated_by=updated_by_from_body if updated_by_from_body else existing_perspective.updated_by,
                column_state=final_column_state_list_for_pydantic,
                sort_model=sort_model_as_dict,
                filter_model=filter_model_as_dict
                #sort_model=existing_perspective.sort_model,
                #filter_model=existing_perspective.filter_model
            )
            updated_perspective_model = service.update_perspective_by_username(username, perspective_update)
            validated_updated_perspective = Perspective.model_validate(updated_perspective_model, from_attributes=True)
            return jsonify(validated_updated_perspective.model_dump(mode='json')), 200
        else:
            # User does not exist, create a new perspective
            layout_name = data.get('layout_name')
            updated_by = data.get('updated_by')

            if not layout_name:
                return jsonify({"error": "layout_name is required for new perspectives."}), 400
            if not updated_by:
                return jsonify({"error": "updated_by is required for new perspectives."}), 400

            # Use the list of validated items to create the new perspective
            perspective_create = PerspectiveCreate(
                username=username,
                layout_name=layout_name,
                updated_by=updated_by,
                column_state=validated_column_states,
                sort_model=[],
                filter_model=[]
            )
            new_perspective_model = service.create_perspective(perspective_create)
            validated_new_perspective = Perspective.model_validate(new_perspective_model, from_attributes=True)
            return jsonify(validated_new_perspective.model_dump(mode='json')), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@column_state_bp.route('/delete_single', methods=['DELETE'])
def delete_single_column_state_route():
    """
    Handles DELETE requests to remove a single column_state item by name.
    The request body must contain the username and the name of the column state to delete.
    """
    try:
        data = request.json
        username = data.get('username')
        column_state_name_to_delete = data.get('column_state_name')

        if not username or not column_state_name_to_delete:
            return jsonify({"error": "Username and column_state_name are required."}), 400

        conn, curr = get_db()
        service = PerspectiveService(conn, curr)

        existing_perspective = service.get_perspective_by_username(username)

        if not existing_perspective:
            return jsonify({"message": f"Perspective for user '{username}' not found."}), 404

        # Step 1: Get the current list of column states from the existing perspective.
        original_column_state_list = existing_perspective.column_state

        # Step 2: Create a new list that excludes the item you want to delete.
        # This is a key part of the logic. We're filtering the list.
        updated_column_state_list = [
            cs for cs in original_column_state_list if cs.name != column_state_name_to_delete
        ]

        # Step 3: Check if the list size changed. If not, the item was not found.
        if len(updated_column_state_list) == len(original_column_state_list):
            return jsonify({"message": f"Column state with name '{column_state_name_to_delete}' not found."}), 404

        # Step 4: Convert the updated list of DTOs into a list of dictionaries.
        # This is necessary because the PerspectiveUpdate Pydantic model expects dictionaries.
        final_column_state_list_for_pydantic = [item.__dict__ for item in updated_column_state_list]

        # Step 5: Prepare the PerspectiveUpdate object.
        # We need to correctly convert the nested DTOs in sort_model and filter_model to dictionaries.
        sort_model_as_dict = _convert_view_settings_to_dicts(existing_perspective.sort_model)
        filter_model_as_dict = _convert_view_settings_to_dicts(existing_perspective.filter_model)

        perspective_update = PerspectiveUpdate(
            username=username,
            layout_name=existing_perspective.layout_name,
            updated_by=existing_perspective.updated_by,
            column_state=final_column_state_list_for_pydantic,
            sort_model=sort_model_as_dict,
            filter_model=filter_model_as_dict
        )

        # Step 6: Call the service layer to perform the database update.
        updated_perspective_model = service.update_perspective_by_username(username, perspective_update)

        # Step 7: Validate the final model and return the JSON response.
        validated_updated_perspective = Perspective.model_validate(updated_perspective_model, from_attributes=True)
        return jsonify(validated_updated_perspective.model_dump(mode='json')), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@column_state_bp.route('/singleSaveUpdate', methods=['POST'])
def save_update_single_column_state_route():
    """
    Handles POST requests to save a list of column_state items.
    If the user does not exist, a new perspective is created.
    If the user exists, the existing perspective's column_state is updated.
    """
    try:
        data = request.json
        username = data.get('username')
        column_state_data = data.get('column_state', [])

        if not username:
            return jsonify({"error": "Username is required."}), 400

        # Validate the incoming list of column_state data
        try:
            validated_column_state = [ColumnState.model_validate(cs) for cs in column_state_data]
        except ValidationError as e:
            return jsonify({"error": "Invalid column_state data", "detail": e.errors()}), 400

        conn, curr = get_db()
        service = PerspectiveService(conn, curr)

        existing_perspective = service.get_perspective_by_username(username)

        if existing_perspective:
            # If perspective exists, update the column_state
            layout_name_from_body = data.get('layout_name')
            updated_by_from_body = data.get('updated_by')

            # Recursively convert nested DTOs to dictionaries for Pydantic validation
            sort_model_as_dict = _convert_view_settings_to_dicts(existing_perspective.sort_model)
            filter_model_as_dict = _convert_view_settings_to_dicts(existing_perspective.filter_model)

            perspective_update = PerspectiveUpdate(
                username=username,
                layout_name=layout_name_from_body if layout_name_from_body else existing_perspective.layout_name,
                updated_by=updated_by_from_body if updated_by_from_body else existing_perspective.updated_by,
                column_state=[cs.model_dump() for cs in validated_column_state],
                sort_model=sort_model_as_dict,
                filter_model=filter_model_as_dict
                #sort_model=existing_perspective.sort_model,
                #filter_model=existing_perspective.filter_model
            )
            updated_perspective_model = service.update_perspective_by_username(username, perspective_update)
            validated_updated_perspective = Perspective.model_validate(updated_perspective_model, from_attributes=True)
            return jsonify(validated_updated_perspective.model_dump(mode='json')), 200
        else:
            # If perspective does not exist, create a new one
            layout_name = data.get('layout_name')
            updated_by = data.get('updated_by')

            if not layout_name:
                return jsonify({"error": "layout_name is required for new perspectives."}), 400
            if not updated_by:
                return jsonify({"error": "updated_by is required for new perspectives."}), 400

            perspective_create = PerspectiveCreate(
                username=username,
                layout_name=layout_name,
                updated_by=updated_by,
                column_state=validated_column_state,
                sort_model=[],
                filter_model=[]
            )
            new_perspective_model = service.create_perspective(perspective_create)
            validated_new_perspective = Perspective.model_validate(new_perspective_model, from_attributes=True)
            return jsonify(validated_new_perspective.model_dump(mode='json')), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500