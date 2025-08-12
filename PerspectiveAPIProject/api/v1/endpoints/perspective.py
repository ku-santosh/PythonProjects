from flask import Blueprint, jsonify, request
import psycopg2
from pydantic import ValidationError
from typing import List
from ...database.database import get_db
from ...schemas.perspective import Perspective, PerspectiveCreate, PerspectiveUpdate
from ...services.perspective import PerspectiveService

# Create a Blueprint for this module
perspective_bp = Blueprint('perspective_bp', __name__)


@perspective_bp.route("/perspectives/", methods=["GET"])
def get_all():
    """Retrieves all perspectives from the database."""
    conn, curr = get_db()
    try:
        service = PerspectiveService(conn, curr)
        perspectives = service.get_all_perspectives()
        # The serializer in the Perspective schema now expects a dictionary-like object,
        # which our DTO provides.
        return jsonify([Perspective(**p.__dict__).model_dump() for p in perspectives])
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


@perspective_bp.route("/perspectives/<int:perspective_id>", methods=["GET"])
def get_by_id(perspective_id: int):
    """Retrieves a single perspective by its ID."""
    conn, curr = get_db()
    try:
        service = PerspectiveService(conn, curr)
        perspective = service.get_perspective_by_id(perspective_id)
        if not perspective:
            return jsonify({"detail": "Perspective not found"}), 404
        return jsonify(Perspective(**perspective.__dict__).model_dump())
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


@perspective_bp.route("/perspectives/", methods=["POST"])
def create():
    """Creates a new perspective in the database."""
    conn, curr = get_db()
    try:
        perspective_in = PerspectiveCreate(**request.json)
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 422

    try:
        service = PerspectiveService(conn, curr)
        new_perspective = service.create_perspective(perspective_in)
        return jsonify(Perspective(**new_perspective.__dict__).model_dump()), 201
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


@perspective_bp.route("/perspectives/<int:perspective_id>", methods=["PUT"])
def update(perspective_id: int):
    """Updates an existing perspective by its ID."""
    conn, curr = get_db()
    try:
        perspective_in = PerspectiveUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 422

    try:
        service = PerspectiveService(conn, curr)
        updated_perspective = service.update_perspective(perspective_id, perspective_in)
        if not updated_perspective:
            return jsonify({"detail": "Perspective not found"}), 404
        return jsonify(Perspective(**updated_perspective.__dict__).model_dump())
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


@perspective_bp.route("/perspectives/<int:perspective_id>", methods=["DELETE"])
def delete(perspective_id: int):
    """Deletes a perspective by its ID."""
    conn, curr = get_db()
    try:
        service = PerspectiveService(conn, curr)
        if not service.delete_perspective(perspective_id):
            return jsonify({"detail": "Perspective not found"}), 404
        return "", 204
    except Exception as e:
        return jsonify({"detail": str(e)}), 500