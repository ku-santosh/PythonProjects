from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from ...schemas.perspective import ViewSetting, Perspective
from ...services.perspective import PerspectiveService
from ...database.database import get_db

filter_model_bp = Blueprint('filter_model', __name__)

@filter_model_bp.route('/<int:perspective_id>', methods=['PUT'])
def update_filter_model_route(perspective_id):
    """
    Handles PUT requests to replace the filter_model of a perspective.
    This route expects the full list of filters in the request body.
    """
    try:
        data = request.json
        # Validate that the incoming data is a list of ViewSetting objects
        view_settings_in = [ViewSetting.model_validate(item) for item in data]

        conn, curr = get_db()
        service = PerspectiveService(conn, curr)

        # Call the service method to update only the filter_model
        updated_perspective = service.update_filter_model(perspective_id, view_settings_in)

        if not updated_perspective:
            return jsonify({"message": f"Perspective with id {perspective_id} not found"}), 404

        validated_updated_perspective = Perspective.model_validate(updated_perspective, from_attributes=True)
        return jsonify(validated_updated_perspective.model_dump(mode='json')), 200
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@filter_model_bp.route('/<int:perspective_id>/save_single_filter', methods=['POST'])
def save_single_filter_route(perspective_id):
    """
    Handles POST requests to add or update a single filter or a list of filters
    within a perspective's filter_model.
    """
    try:
        data = request.json
        conn, curr = get_db()
        service = PerspectiveService(conn, curr)
        updated_perspective = None

        if isinstance(data, list):
            # If the data is a list, validate each item
            filters_in = [ViewSetting.model_validate(item) for item in data]
            updated_perspective = service.save_multiple_filters(perspective_id, filters_in)
        else:
            # If the data is a single object, validate it as before
            filter_in = ViewSetting.model_validate(data)
            updated_perspective = service.save_single_filter(perspective_id, filter_in)

        if not updated_perspective:
            return jsonify({"message": f"Perspective with id {perspective_id} not found"}), 404

        validated_updated_perspective = Perspective.model_validate(updated_perspective, from_attributes=True)
        return jsonify(validated_updated_perspective.model_dump(mode='json')), 200
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
