import json
from typing import List, Optional
from psycopg2.extensions import connection, cursor
from ..models.feedback import Feedback as FeedbackDTO
from ..schemas.feedback import FeedbackCreate, FeedbackUpdate, Feedback


class FeedbackService:
    def __init__(self, db_conn: connection, db_curr: cursor):
        self.db_conn = db_conn
        self.db_curr = db_curr

    def get_all_feedbacks(self) -> List[Feedback]:
        self.db_curr.execute("SELECT * FROM recsui.recsFeedback;")
        rows = self.db_curr.fetchall()
        return [FeedbackDTO.from_dict(r) for r in rows]

    def get_feedback_by_id(self, feedback_id: int) -> Optional[Feedback]:
        self.db_curr.execute("SELECT * FROM recsui.recsFeedback WHERE id = %s;", (feedback_id,))
        row = self.db_curr.fetchone()
        return FeedbackDTO.from_dict(row) if row else None

    def get_feedback_by_gpn(self, user_gpn: str) -> Optional[Feedback]:
        self.db_curr.execute("SELECT * FROM recsui.recsFeedback WHERE user_gpn = %s;", (user_gpn,))
        row = self.db_curr.fetchone()
        return FeedbackDTO.from_dict(row) if row else None

    def create_or_append_feedback(self, feedback_in: FeedbackCreate) -> dict:
        self.db_curr.execute("SELECT * FROM recsui.recsFeedback WHERE user_gpn = %s;", (feedback_in.user_gpn,))
        existing = self.db_curr.fetchone()

        feedbacks_json = json.dumps([f.model_dump(mode="json") for f in feedback_in.user_feedbacks])

        if existing:
            self.db_curr.execute(
                """
                UPDATE recsui.recsFeedback
                SET user_feedbacks = user_feedbacks || %s::jsonb,
                    user_name = %s,
                    user_email = %s,
                    updated_time = NOW()
                WHERE user_gpn = %s
                RETURNING *;
                """,
                (feedbacks_json, feedback_in.user_name, feedback_in.user_email, feedback_in.user_gpn)
            )
            row = self.db_curr.fetchone()
            self.db_conn.commit()
            feedback = FeedbackDTO.from_dict(row)
            return {**Feedback.model_validate(vars(feedback)).model_dump(mode="json"),
                    "message": f"Feedback appended for user_gpn '{feedback_in.user_gpn}'"}
        else:
            self.db_curr.execute(
                """
                INSERT INTO recsui.recsFeedback (user_gpn, user_name, user_email, user_feedbacks, updated_time)
                VALUES (%s, %s, %s, %s, NOW())
                RETURNING *;
                """,
                (feedback_in.user_gpn, feedback_in.user_name, feedback_in.user_email, feedbacks_json)
            )
            row = self.db_curr.fetchone()
            self.db_conn.commit()
            feedback = FeedbackDTO.from_dict(row)
            return {**Feedback.model_validate(vars(feedback)).model_dump(mode="json"),
                    "message": "user_gpn not found, created new record"}

    def update_feedback_by_gpn(self, user_gpn: str, feedback_in: FeedbackUpdate,
                               user_name: Optional[str] = None, user_email: Optional[str] = None) -> Optional[dict]:
        feedbacks_json = json.dumps([f.model_dump(mode="json") for f in feedback_in.user_feedbacks]) if feedback_in.user_feedbacks else "[]"

        self.db_curr.execute("SELECT * FROM recsui.recsFeedback WHERE user_gpn = %s;", (user_gpn,))
        existing = self.db_curr.fetchone()

        if existing:
            self.db_curr.execute(
                """
                UPDATE recsui.recsFeedback
                SET user_feedbacks = user_feedbacks || %s::jsonb,
                    user_name = COALESCE(%s, user_name),
                    user_email = COALESCE(%s, user_email),
                    updated_time = NOW()
                WHERE user_gpn = %s
                RETURNING *;
                """,
                (feedbacks_json, user_name, user_email, user_gpn)
            )
            row = self.db_curr.fetchone()
            self.db_conn.commit()
            feedback = FeedbackDTO.from_dict(row)
            return {**Feedback.model_validate(vars(feedback)).model_dump(mode="json"),
                    "message": f"Feedback appended for user_gpn '{user_gpn}'"}
        else:
            self.db_curr.execute(
                """
                INSERT INTO recsui.recsFeedback (user_gpn, user_name, user_email, user_feedbacks, updated_time)
                VALUES (%s, %s, %s, %s, NOW())
                RETURNING *;
                """,
                (user_gpn, user_name or "Unknown", user_email or "unknown@example.com", feedbacks_json)
            )
            row = self.db_curr.fetchone()
            self.db_conn.commit()
            feedback = FeedbackDTO.from_dict(row)
            return {**Feedback.model_validate(vars(feedback)).model_dump(mode="json"),
                    "message": "user_gpn not found, created new record"}

    def delete_feedback(self, feedback_id: int) -> bool:
        self.db_curr.execute("DELETE FROM recsui.recsFeedback WHERE id = %s RETURNING id;", (feedback_id,))
        row = self.db_curr.fetchone()
        if row:
            self.db_conn.commit()
            return True
        self.db_conn.rollback()
        return False
