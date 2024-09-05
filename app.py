from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime
from extensions import db
from models import Assignment

# Load the dotenv file
load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)


@app.route('/api/assignments', methods=['GET'])
def get_assignments():
    # Fetch all assignments
    assignments = Assignment.query.all()
    return jsonify([assignment.serialize() for assignment in assignments])


@app.route('/api/assignments', methods=['POST'])
def create_assignment():
    data = request.get_json()
    new_assignment = Assignment(
        todo_id=data['todo_id'],
        from_name=data['from_name'],
        from_email=data['from_email'],
        token=data['token'],
        status=data['status'],
        request_date=datetime.utcnow(),
        completed_date=None
    )

    db.session.add(new_assignment)
    db.session.commit()

    return jsonify(new_assignment.serialize()), 201


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
