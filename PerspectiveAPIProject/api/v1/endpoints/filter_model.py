from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
from ...schemas.perspective import PerspectiveCreate, PerspectiveUpdate, Perspective, ViewSetting, FilterDetail
from ...services.perspective import PerspectiveService
from ...database.database import get_db

filter_model_bp = Blueprint('filter_model', __name__)


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


@filter_model_bp.route('/save_single_filter', methods=['POST'])
def save_single_filter_model_route():
    """
    Handles POST requests to save or update one or more filter_model items.
    This function implements an upsert logic based on the combination of 'name' and 'view'.
    - If a filter_model item with the same name and view exists, it is updated.
    - If not, a new filter_model item is added.
    - If the user does not exist, a new perspective is created.
    """
    try:
        data = request.json
        username = data.get('username')
        filter_model_data = data.get('filter_model')

        if not username:
            return jsonify({"error": "Username is required."}), 400

        if filter_model_data is None:
            return jsonify({"error": "filter_model data is required."}), 400

        filters_to_process = filter_model_data if isinstance(filter_model_data, list) else [filter_model_data]

        # Validate the incoming list of filter_model data
        try:
            validated_filter_models = [ViewSetting.model_validate(fm) for fm in filters_to_process]
        except ValidationError as e:
            return jsonify({"error": "Invalid filter_model data", "detail": e.errors()}), 400

        conn, curr = get_db()
        service = PerspectiveService(conn, curr)

        existing_perspective = service.get_perspective_by_username(username)

        if existing_perspective:
            # User exists, so apply the upsert logic
            existing_filter_model_list = existing_perspective.filter_model

            for validated_item in validated_filter_models:
                # Convert the Pydantic model back to a dictionary for easier comparison and update
                validated_item_dict = validated_item.model_dump()

                found = False
                for i, existing_item in enumerate(existing_filter_model_list):
                    # Check for a match on both 'name' and 'view'
                    if existing_item.name == validated_item_dict['name'] and existing_item.view == validated_item_dict[
                        'view']:
                        # Update the existing DTO object's attributes
                        existing_filter_model_list[i].filters = validated_item_dict['filters']
                        existing_filter_model_list[i].default = validated_item_dict['default']
                        found = True
                        break

                if not found:
                    # If no match was found, create a new DTO and append it to the list
                    new_filters = {}
                    for k, v in validated_item_dict.get('filters', {}).items():
                        new_filters[k] = FilterDetail(**v)
                    existing_filter_model_list.append(ViewSetting(
                        name=validated_item_dict['name'],
                        view=validated_item_dict['view'],
                        filters=new_filters,
                        default=validated_item_dict['default']
                    ))

            # Now, create a list of dictionaries from the updated list of DTOs for the Pydantic model
            final_filter_model_list_for_pydantic = _convert_view_settings_to_dicts(existing_filter_model_list)

            layout_name_from_body = data.get('layout_name')
            updated_by_from_body = data.get('updated_by')

            # Convert existing nested DTOs to dictionaries for Pydantic validation
            sort_model_as_dict = _convert_view_settings_to_dicts(existing_perspective.sort_model)
            column_state_as_dict = [cs.__dict__ for cs in existing_perspective.column_state]

            perspective_update = PerspectiveUpdate(
                username=username,
                layout_name=layout_name_from_body if layout_name_from_body else existing_perspective.layout_name,
                updated_by=updated_by_from_body if updated_by_from_body else existing_perspective.updated_by,
                column_state=column_state_as_dict,
                sort_model=sort_model_as_dict,
                filter_model=final_filter_model_list_for_pydantic
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
                column_state=[],
                sort_model=[],
                filter_model=validated_filter_models
            )
            new_perspective_model = service.create_perspective(perspective_create)
            validated_new_perspective = Perspective.model_validate(new_perspective_model, from_attributes=True)
            return jsonify(validated_new_perspective.model_dump(mode='json')), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500