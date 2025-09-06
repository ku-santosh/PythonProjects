from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from ...schemas.perspective import ColumnState, Perspective
from ...services.perspective import PerspectiveService
from ...database.database import get_db

column_state_bp = Blueprint('column_state', __name__)


@column_state_bp.route('/<int:perspective_id>', methods=['PUT'])
def update_column_state_route(perspective_id):
    """
    Handles PUT requests to update the column_state of a perspective.
    """
    try:
        data = request.json
        # Validate that the incoming data is a list of ColumnState objects
        column_states_in = [ColumnState.model_validate(item) for item in data]

        conn, curr = get_db()
        service = PerspectiveService(conn, curr)

        # Call the service method to update only the column_state
        updated_perspective = service.update_column_state(perspective_id, column_states_in)

        if not updated_perspective:
            return jsonify({"message": f"Perspective with id {perspective_id} not found"}), 404

        validated_updated_perspective = Perspective.model_validate(updated_perspective, from_attributes=True)
        return jsonify(validated_updated_perspective.model_dump(mode='json')), 200
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
