import os
from datetime import datetime

from flask_mail import Mail
from flask import Flask, jsonify, request

from extensions import db
from models import Assignment, APIToken
from helpers import token_required, send_email

# Create a Flask app
app = Flask(__name__)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure the smtp server
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

mail = Mail(app)

# Initialize the database
db.init_app(app)

# User dummy data structure for create a token
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

    # If user already has a token, return it
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


# Default home route for checking the server status
@app.route("/", methods=["GET"])
def home():
    return "Hello PAS!"


# Get all assignments for a specific uid
@app.route("/api/assignments", methods=["GET"])
@token_required
def get_assignments():
    # Check if uid is provided
    uid = request.args.get("u")
    if not uid:
        return jsonify({"success": False, "message": "UID is missing"}), 400

    # Check if completed is provided
    completed = request.args.get("c", default=False, type=bool)

    # Check if task_id is provided
    task_id = request.args.get("tid", default=None, type=int)

    if task_id:
        # Fetch all assignments for a specific task_id
        assignments = Assignment.query.filter(
            Assignment.uid == uid,
            Assignment.is_completed == completed,
            Assignment.task_id == task_id,
        ).all()
    else:
        # Fetch all assignments
        assignments = Assignment.query.filter(
            Assignment.uid == uid, Assignment.is_completed == completed
        ).all()

    # If no assignments found, return 404
    if not assignments:
        return jsonify({"success": False, "message": "No assignments found"}), 404

    # Return the serialized assignments
    return jsonify([assignment.serialize() for assignment in assignments])


# Create a new assignment
@app.route("/api/assignment", methods=["POST"])
@token_required
def create_assignment():
    # Get the data from the request
    data = request.get_json()
    # Create a new assignment
    new_assignment = Assignment(
        todo_id=data["todo_id"],
        task_id=data["task_id"],
        from_name=data["from_name"] if "from_name" in data else "",
        to_name=data["to_name"] if "to_name" in data else "",
        to_email=data["to_email"],
        uid=data["uid"],
        assignment=data["assignment"] if "assignment" in data else "",
    )
    print(new_assignment.serialize())

    # Add the new assignment to the database
    db.session.add(new_assignment)
    db.session.commit()
    print("Assignment created in DB")

    # Send an email notification
    email_status = send_email(
        mail,
        data,
    )
    if email_status:
        print("Email sent successfully")

    return (
        jsonify(
            {
                "success": True,
                "message": "Assignment created",
                "email_success": email_status,
            }
        ),
        201,
    )


# Mark an assignment as completed route for the recipient
@app.route(
    "/api/assignment/<uid>/<todo_id>/<task_id>/complete", methods=["GET"]
)
def set_assignment_by_recipient(uid, todo_id, task_id):
    # Check if the assignment exists
    assignment = (
        db.session.query(Assignment)
        .filter(
            Assignment.todo_id == todo_id,
            Assignment.task_id == task_id,
            Assignment.uid == uid,
        )
        .first()
    )

    # If the assignment exists, mark it as completed by update the
    # completed_date and is_completed fields
    if assignment:
        assignment.completed_date = datetime.now()
        assignment.is_completed = True

        # Commit the changes
        db.session.commit()
        print(f"Assignment completed for {uid}!")

        # Return a simple message in html
        return "<center><h3>🎉 Assignment completed successfully!</h3></center>"
    else:
        # Otherwise, return a 404 and a message
        print(f"Assignment not found for {uid}!")
        return "<center><h3>❌ Assignment not found!</h3></center>", 404


# Check if the task is completed
@app.route("/api/assignment/<uid>/<todo_id>/<task_id>/status", methods=["GET"])
@token_required
def check_assignment_status(uid, todo_id, task_id):
    # Check if the assignment exists
    assignment = (
        db.session.query(Assignment)
        .filter(
            Assignment.todo_id == todo_id,
            Assignment.task_id == task_id,
            Assignment.uid == uid,
        )
        .first()
    )
    print("uid", uid, "todo_id", todo_id, "task_id", task_id)
    # If the assignment exists, return the status
    if assignment:
        return jsonify({"success": True, "is_completed": assignment.is_completed})
    else:
        # Otherwise, return a 404 and a message
        return jsonify({"success": False, "message": "Assignment not found"}), 404


# General error handler for 404
@app.errorhandler(404)
def page_not_found(error):
    return jsonify({"success": False, "error": "Something went wrong!"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default="5000"))
