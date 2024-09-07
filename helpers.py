from flask import request, jsonify
from functools import wraps
from models import APIToken
from flask_mail import Message


COMPLETION_STATUS_ENDPOINT = (
    "https//pasapi-dev.up.railway.app/api/assignment/{}/{}/{}/complete"
)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"success": False, "message": "Token is missing"}), 401

        # Validate the token
        token = token.split(" ")[1]
        token_record = APIToken.query.filter_by(token=token).first()

        if not token_record:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated


def send_email(mail, assignment):
    print(assignment)
    msg = Message(
        f"🍅 Todomato: Hi {assignment['from_name']}, {assignment['to_name']} "
        "has assigned you a task!",
        recipients=[assignment["to_email"]],
    )
    msg.html = f"""
        <p>👋 Hi {assignment["to_name"]},</p>
        <p>This is an automated email from Todomato app.
        {assignment["from_name"]} has assigned you a task!</p>
        <p>Please complete the following task:</p>
        <p><font face="Courier New" size="2">
        <b>{assignment["assignment"]}</b></font></p>
        <br/>
        <p>
            Once you have completed the task, please click
            <a href="{COMPLETION_STATUS_ENDPOINT.format(
                assignment["to_email"],
                assignment["todo_id"],
                assignment["task_id"]
            )}">
                ✅ Mark as completed
            </a>.
        </p>

        <p>
            Cheers, <br/>
            🍅 Todomato Team
        </p>
    """
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(e)
        return False
