from datetime import datetime
from extensions import db

# Assignement model
class Assignment(db.Model):
    __tablename__ = 'assignments'

    todo_id = db.Column(db.Integer, primary_key=True)
    from_name = db.Column(db.String(100), nullable=False)
    from_email = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime, nullable=True)

    def serialize(self):
        return {
            'todo_id': self.todo_id,
            'from_name': self.from_name,
            'from_email': self.from_email,
            'token': self.token,
            'status': self.status,
            'request_date': self.request_date.isoformat(),
            'completed_date': self.completed_date.isoformat() if self.completed_date else None
        }
