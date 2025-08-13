from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
from ...schemas.perspective import PerspectiveCreate, PerspectiveUpdate, ColumnState, Perspective
from ...services.perspective import PerspectiveService
from ...database.database import get_db

column_state_bp = Blueprint('column_state', __name__)


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
            perspective_update = PerspectiveUpdate(
                username=username,
                layout_name=existing_perspective.layout_name,  # Retain existing layout_name
                updated_by=data.get('updated_by', existing_perspective.updated_by),  # Use existing or new updated_by
                column_state=validated_column_state,
                sort_model=existing_perspective.sort_model,  # Retain existing sort_model
                filter_model=existing_perspective.filter_model  # Retain existing filter_model
            )
            updated_perspective_model = service.update_perspective_by_username(username, perspective_update)
            validated_updated_perspective = Perspective.model_validate(updated_perspective_model, from_attributes=True)
            return jsonify(validated_updated_perspective.model_dump(mode='json')), 200
        else:
            # If perspective does not exist, create a new one
            perspective_create = PerspectiveCreate(
                username=username,
                layout_name=data.get('layout_name', f"{username}'s layout"),
                updated_by=data.get('updated_by', username),
                column_state=validated_column_state,
                sort_model=[],
                filter_model=[]
            )
            new_perspective_model = service.create_perspective(perspective_create)
            validated_new_perspective = Perspective.model_validate(new_perspective_model, from_attributes=True)
            return jsonify(validated_new_perspective.model_dump(mode='json')), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500