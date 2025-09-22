from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from ...schemas.feedback import FeedbackCreate, FeedbackUpdate, Feedback
from ...services.feedback import FeedbackService
from ...database.database import get_db

feedback_bp = Blueprint('feedback', __name__)


@feedback_bp.route('/', methods=['GET'])
def get_all_feedbacks_route():
    try:
        conn, curr = get_db()
        service = FeedbackService(conn, curr)
        feedbacks = service.get_all_feedbacks()
        return jsonify([Feedback.model_validate(vars(f)).model_dump(mode="json") for f in feedbacks]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/<int:feedback_id>', methods=['GET'])
def get_feedback_by_id_route(feedback_id):
    try:
        conn, curr = get_db()
        service = FeedbackService(conn, curr)
        feedback = service.get_feedback_by_id(feedback_id)
        if not feedback:
            return jsonify({"user_feedbacks": [], "message": f"No feedback found with id '{feedback_id}'"}), 200
        return jsonify(Feedback.model_validate(vars(feedback)).model_dump(mode="json")), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/gpn/<string:user_gpn>', methods=['GET'])
def get_feedback_by_gpn_route(user_gpn):
    try:
        conn, curr = get_db()
        service = FeedbackService(conn, curr)
        feedback = service.get_feedback_by_gpn(user_gpn)
        if not feedback:
            return jsonify({"user_gpn": user_gpn, "user_feedbacks": [], "message": f"No feedback found for user_gpn '{user_gpn}'"}), 200
        return jsonify(Feedback.model_validate(vars(feedback)).model_dump(mode="json")), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/', methods=['POST'])
def create_or_append_feedback_route():
    try:
        data = request.json
        feedback_in = FeedbackCreate.model_validate(data)

        conn, curr = get_db()
        service = FeedbackService(conn, curr)
        result = service.create_or_append_feedback(feedback_in)

        return jsonify(result), 201 if "created" in result["message"].lower() else 200
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/gpn/<string:user_gpn>', methods=['PUT'])
def update_feedback_by_gpn_route(user_gpn):
    try:
        data = request.json
        feedback_in = FeedbackUpdate.model_validate(data)

        conn, curr = get_db()
        service = FeedbackService(conn, curr)

        user_name = data.get("user_name")
        user_email = data.get("user_email")

        result = service.update_feedback_by_gpn(user_gpn, feedback_in, user_name, user_email)

        return jsonify(result), 201 if "created" in result["message"].lower() else 200
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/<int:feedback_id>', methods=['DELETE'])
def delete_feedback_route(feedback_id):
    try:
        conn, curr = get_db()
        service = FeedbackService(conn, curr)
        deleted = service.delete_feedback(feedback_id)
        if not deleted:
            return jsonify({"message": f"No feedback found with id '{feedback_id}'"}), 200
        return jsonify({"message": "Feedback deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
