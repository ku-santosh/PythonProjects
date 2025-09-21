from datetime import datetime


class Feedback:
    """DTO for recsFeedback table with JSONB user_feedbacks"""

    def __init__(self, id: int, user_gpn: str, user_name: str, user_email: str,
                 user_feedbacks: list, updated_time: datetime):
        self.id = id
        self.user_gpn = user_gpn
        self.user_name = user_name
        self.user_email = user_email
        self.user_feedbacks = user_feedbacks
        self.updated_time = updated_time

    @staticmethod
    def from_dict(data: dict):
        return Feedback(
            id=data['id'],
            user_gpn=data['user_gpn'],
            user_name=data['user_name'],
            user_email=data['user_email'],
            user_feedbacks=data['user_feedbacks'],
            updated_time=data['updated_time']
        )
