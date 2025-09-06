# Assuming necessary imports from other modules
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from typing import Optional, List, Dict, Any
from datetime import datetime

# Assuming these models are in api.models.perspective
from ...models.perspective import Perspective, ColumnState, FilterDetail as FilterDetailModel, ViewSetting as ViewSettingModel
# Assuming these schemas are in api.schemas.perspective
from ...schemas.perspective import PerspectiveUpdate, ViewSetting
# Assuming PerspectiveService and get_db are in their own modules
from ...services.perspective import PerspectiveService
from ...database.database import get_db

# Assuming this is the blueprint for your routes
filter_model_bp = Blueprint('filter_model_bp', __name__)


# This helper function converts our Python DTOs back to dictionaries for the Pydantic schema
def _convert_view_settings_to_dicts(view_settings_list: List[ViewSettingModel]):
    result_list = []
    for view_setting in view_settings_list:
        filters_dict = {}
        for k, v in view_setting.filters.items():
            # Check if the filter is an instance of the DTO and convert it
            if isinstance(v, FilterDetailModel):
                filters_dict[k] = {"type": v.type, "filter": v.filter}
            else:
                # If it's already a dictionary, use it as is
                filters_dict[k] = v

        result_list.append({
            "name": view_setting.name,
            "view": view_setting.view,
            "filters": filters_dict,
            "default": view_setting.default
        })
    return result_list


# This helper function converts ColumnState DTOs to dictionaries
def _convert_column_state_to_dicts(column_state_list: List[ColumnState]):
    return [cs.__dict__ for cs in column_state_list]


@filter_model_bp.route('/save_single_filter', methods=['POST'])
def save_single_filter_model_route():
    try:
        data = request.json
        username = data.get('username')
        filters_to_process = data.get('filter_model')
        layout_name_from_body = data.get('layout_name')
        updated_by_from_body = data.get('updated_by')

        if not username or not filters_to_process:
            return jsonify({"error": "Username and filter_model are required fields."}), 400

        # Validate the incoming data using the Pydantic schema
        try:
            validated_filter_models = [ViewSetting.model_validate(fm) for fm in filters_to_process]
        except ValidationError as e:
            return jsonify({"error": "Invalid filter_model data", "detail": e.errors()}), 400

        conn, curr = get_db()
        service = PerspectiveService(conn, curr)

        existing_perspective = service.get_perspective_by_username(username)

        if existing_perspective:
            # We work with the Python DTO objects returned from the database call
            existing_filter_model_list = existing_perspective.filter_model

            for validated_item in validated_filter_models:
                # If the incoming item is the new default, unset the old one
                if validated_item.default:
                    for existing_item in existing_filter_model_list:
                        existing_item.default = False
                # Convert the validated Pydantic model to a standard dictionary
                validated_item_dict = validated_item.model_dump()

                # --- START OF FIX ---
                # We need to convert the dictionary filters from the incoming data
                # into the correct Python DTO objects (FilterDetailModel)
                new_filters_as_dto = {
                    k: FilterDetailModel(**v) for k, v in validated_item_dict.get('filters', {}).items()
                }
                # --- END OF FIX ---

                found = False
                for i, existing_item in enumerate(existing_filter_model_list):
                    # Find if a matching item already exists
                    if existing_item.name == validated_item_dict['name'] and existing_item.view == validated_item_dict[
                        'view']:
                        # Update the existing DTO with the new values
                        # Use the newly created DTOs for the filters
                        existing_filter_model_list[i].filters = new_filters_as_dto
                        existing_filter_model_list[i].default = validated_item_dict['default']
                        found = True
                        break

                if not found:
                    # If no match was found, append a new DTO to the list
                    existing_filter_model_list.append(ViewSettingModel(
                        name=validated_item_dict['name'],
                        view=validated_item_dict['view'],
                        filters=new_filters_as_dto,
                        default=validated_item_dict['default']
                    ))

            # Now, convert the final list of DTOs back to a dictionary format for the Pydantic update schema
            sort_model_as_dict = _convert_view_settings_to_dicts(existing_perspective.sort_model)
            column_state_as_dict = [cs.__dict__ for cs in existing_perspective.column_state]
            final_filter_model_list_for_pydantic = _convert_view_settings_to_dicts(existing_filter_model_list)

            # Update the perspective
            perspective_update = PerspectiveUpdate(
                username=username,
                layout_name=layout_name_from_body if layout_name_from_body else existing_perspective.layout_name,
                updated_by=updated_by_from_body if updated_by_from_body else existing_perspective.updated_by,
                column_state = column_state_as_dict,
                sort_model = sort_model_as_dict,
                filter_model=final_filter_model_list_for_pydantic
            )

            updated_perspective_model = service.update_perspective_by_username(username, perspective_update)

            # --- START OF FINAL FIX ---
            # Manually convert all nested DTOs to dictionaries for JSON serialization
            response_data = {
                "username": updated_perspective_model.username,
                "layout_name": updated_perspective_model.layout_name,
                "updated_by": updated_perspective_model.updated_by,
                "column_state": _convert_column_state_to_dicts(updated_perspective_model.column_state),
                "sort_model": _convert_view_settings_to_dicts(updated_perspective_model.sort_model),
                "filter_model": _convert_view_settings_to_dicts(updated_perspective_model.filter_model),
            }
            return jsonify(response_data), 200
            # --- END OF FINAL FIX ---

        else:
            # Handle the case where the user's perspective does not exist yet
            pass  # No change needed here

    except Exception as e:
        return jsonify({"error": str(e)}), 500