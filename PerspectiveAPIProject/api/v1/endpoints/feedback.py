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
    """
        {
          "user_gpn": "49056020",
          "user_name": "Santosh Kumar",
          "user_email": "santhosh.kumar.2@ubs.com",
          "user_feedbacks": [
            {
              "componentName": "Name001",
              "activeExpression": "Good",
              "comment": "Long Text",
              "dateTime": "2025-09-01T06:26:12.817693Z"
            }
          ]
        }
    """
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

@feedback_bp.route('/gpn/<string:user_gpn>/latest', methods=['GET'])
def get_latest_feedbacks_by_gpn_route(user_gpn):
    """
        GET /api/v1/feedback/gpn/<user_gpn>/latest
    """
    try:
        conn, curr = get_db()
        service = FeedbackService(conn, curr)
        results = service.get_latest_feedbacks_by_gpn(user_gpn)
        if not results:
            return jsonify({"user_gpn": user_gpn, "feedbacks": [], "message": f"No feedback found for user_gpn '{user_gpn}'"}), 200
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/gpn/<string:user_gpn>/date_range', methods=['GET'])
def get_feedbacks_by_date_range_route(user_gpn):
    """
        GET /api/v1/feedback/gpn/<user_gpn>/date_range?start=<ISO8601>&end=<ISO8601>
        start → optional (default = 1970-01-01T00:00:00Z)
        end → optional (default = 9999-12-31T23:59:59Z)
        Example -- GET /api/v1/feedback/gpn/49056020/date_range?start=2025-09-01&end=2025-09-10
    """
    try:
        start = request.args.get("start", "1970-01-01T00:00:00Z")
        end = request.args.get("end", "9999-12-31T23:59:59Z")

        conn, curr = get_db()
        service = FeedbackService(conn, curr)
        results = service.get_feedbacks_by_date_range(user_gpn, start, end)
        if not results:
            return jsonify({"user_gpn": user_gpn, "feedbacks": [], "message": f"No feedback found for user_gpn '{user_gpn}' in date range"}), 200
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/<string:user_gpn>/component/<string:component_name>', methods=['GET'])
def get_feedbacks_by_component_route(user_gpn, component_name):
    """
        GET /api/v1/feedback/49056020/component/Name001
    """
    try:
        conn, curr = get_db()
        service = FeedbackService(conn, curr)
        results = service.get_feedbacks_by_component(user_gpn, component_name)
        if not results:
            return jsonify({
                "user_gpn": user_gpn,
                "component": component_name,
                "feedbacks": [],
                "message": f"No feedback found for component '{component_name}' and user_gpn '{user_gpn}'"
            }), 200
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

