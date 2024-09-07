import os

from dotenv import load_dotenv
from datetime import datetime

from flask import Flask, jsonify, request, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

from extensions import db
from models import Assignment, APIToken
from helpers import token_required

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)


users = {"": {"password": ""}}


# Login route to generate a long-lived API token
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Check if the user exists and the password matches
    user = users.get(email)
    if not user or user["password"] != password:
        return jsonify({"msg": "Invalid credentials"}), 401

    # Check if user already has a persistent token
    existing_token = APIToken.query.filter_by(user_email=email).first()

    if existing_token:
        token = existing_token.token
        print(f"User {email} already has a token: {token}")
    else:
        # Generate a new token and store it
        new_token = APIToken(user_email=email)
        db.session.add(new_token)
        db.session.commit()
        token = new_token.token
        print(f"Generated a new token for user {email}")

    return jsonify(api_token=token), 200


@app.route("/", methods=["GET"])
def home():
    return "Hello PAS!"


@app.route("/api/assignments", methods=["GET"])
@token_required
def get_assignments():
    # Check if uid is provided
    uid = request.args.get("u")
    if not uid:
        return jsonify({"success": False, "message": "UID is missing"}), 400

    # Check if completed is provided
    completed = request.args.get("c", default=False, type=bool)

    # Fetch all assignments
    assignments = Assignment.query.filter(
        Assignment.uid == uid, Assignment.is_completed == completed
    ).all()

    # If no assignments found, return 404
    if not assignments:
        return jsonify({"success": False, "message": "No assignments found"}), 404
    
    # Return the serialized assignments
    return jsonify([assignment.serialize() for assignment in assignments])


@app.route("/api/assignment", methods=["POST"])
@token_required
def create_assignment():
    # Get the data from the request
    data = request.get_json()
    # Create a new assignment
    new_assignment = Assignment(
        todo_id=data["todo_id"],
        task_id=data["task_id"],
        from_name=data["from_name"] if "from_name" in data else None,
        from_email=data["from_email"] if "from_email" in data else None,
        uid=data["uid"],
    )
    print(new_assignment.serialize())

    db.session.add(new_assignment)
    db.session.commit()

    return jsonify(new_assignment.serialize()), 201


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
