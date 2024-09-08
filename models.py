from datetime import datetime
from extensions import db
import uuid


# Assignement model
class Assignment(db.Model):
    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True)
    todo_id = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.Integer, nullable=False)
    from_name = db.Column(db.String(100), nullable=True)
    to_name = db.Column(db.String(100), nullable=True)
    to_email = db.Column(db.String(100), nullable=False)
    uid = db.Column(db.String(100), nullable=False)
    assignment = db.Column(db.String(255), nullable=False)
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    completed_date = db.Column(db.DateTime, nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "todo_id": self.todo_id,
            "task_id": self.task_id,
            "from_name": self.from_name if self.from_name else None,
            "to_name": self.to_name if self.to_name else None,
            "to_email": self.to_email,
            "uid": self.uid,
            "assignment": self.assignment,
            "is_completed": self.is_completed,
            "request_date": self.request_date,
            "completed_date": (
                self.completed_date.isoformat() if self.completed_date else None
            ),
        }


# API Token model
class APIToken(db.Model):
    __tablename__ = "api_tokens"

    token_id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(200), nullable=False, unique=True)
    user_email = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_email):
        self.token = str(uuid.uuid4())
        self.user_email = user_email

    def serialize(self):
        return {
            "token_id": self.token_id,
            "token": self.token,
            "created_date": self.created_date.isoformat(),
        }
