from flask import Blueprint, request, jsonify, g
import psycopg2
from pydantic import ValidationError
from typing import List
from ...database.database import get_db
from ...schemas.perspective import Perspective, PerspectiveCreate, PerspectiveUpdate
from ...services.perspective import PerspectiveService

# Create a Blueprint for this module
perspective_bp = Blueprint('perspective_bp', __name__)


@perspective_bp.route('/', methods=['GET'])
def get_all_perspectives_route():
    """
    Handles GET requests to retrieve all perspectives.
    """
    try:
        conn, curr = get_db()
        service = PerspectiveService(conn, curr)
        perspectives = service.get_all_perspectives()
        if not perspectives:
            return jsonify({"message": "No perspectives found"}), 404

        # Manually validate and serialize each item using Pydantic's from_attributes
        validated_perspectives = [Perspective.model_validate(p, from_attributes=True) for p in perspectives]

        return jsonify([p.model_dump(mode='json') for p in validated_perspectives]), 200
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@perspective_bp.route('/user/<string:username>', methods=['GET'])
def get_perspective_by_username_route(username):
    """
    Handles GET requests to retrieve a single perspective by username.
    """
    try:
        conn, curr = get_db()
        service = PerspectiveService(conn, curr)
        perspective = service.get_perspective_by_username(username)
        if not perspective:
            return jsonify({"message": f"Perspective for user '{username}' not found"}), 404

        # Validate and serialize the single item
        validated_perspective = Perspective.model_validate(perspective, from_attributes=True)
        return jsonify(validated_perspective.model_dump(mode='json')), 200
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@perspective_bp.route('/<int:perspective_id>', methods=['GET'])
def get_perspective_by_id_route(perspective_id):
    """
    Handles GET requests to retrieve a single perspective by its ID.
    """
    try:
        conn, curr = get_db()
        service = PerspectiveService(conn, curr)
        perspective = service.get_perspective_by_id(perspective_id)
        if not perspective:
            return jsonify({"message": f"Perspective with id {perspective_id} not found"}), 404

        # Validate and serialize the single item
        validated_perspective = Perspective.model_validate(perspective, from_attributes=True)
        return jsonify(validated_perspective.model_dump(mode='json')), 200
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@perspective_bp.route('/', methods=['POST'])
def create_perspective_route():
    """
    Handles POST requests to create a new perspective.
    """
    try:
        data = request.json
        perspective_in = PerspectiveCreate.model_validate(data)
        conn, curr = get_db()
        service = PerspectiveService(conn, curr)
        new_perspective = service.create_perspective(perspective_in)

        validated_new_perspective = Perspective.model_validate(new_perspective, from_attributes=True)
        return jsonify(validated_new_perspective.model_dump(mode='json')), 201
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@perspective_bp.route('/<int:perspective_id>', methods=['PUT'])
def update_perspective_route(perspective_id):
    """
    Handles PUT requests to update an existing perspective.
    """
    try:
        data = request.json
        perspective_in = PerspectiveUpdate.model_validate(data)
        conn, curr = get_db()
        service = PerspectiveService(conn, curr)
        updated_perspective = service.update_perspective(perspective_id, perspective_in)
        if not updated_perspective:
            return jsonify({"message": f"Perspective with id {perspective_id} not found"}), 404

        validated_updated_perspective = Perspective.model_validate(updated_perspective, from_attributes=True)
        return jsonify(validated_updated_perspective.model_dump(mode='json')), 200
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@perspective_bp.route('/<int:perspective_id>', methods=['DELETE'])
def delete_perspective_route(perspective_id):
    """
    Handles DELETE requests to delete a perspective.
    """
    try:
        conn, curr = get_db()
        service = PerspectiveService(conn, curr)
        deleted = service.delete_perspective(perspective_id)
        if not deleted:
            return jsonify({"message": f"Perspective with id {perspective_id} not found"}), 404
        return jsonify({"message": f"Perspective with id {perspective_id} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500