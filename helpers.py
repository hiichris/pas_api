from flask import request, jsonify
from functools import wraps
from models import APIToken
from flask_mail import Message


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


def send_email(mail, send_to, email_message):
    msg = Message(
        'Hello from Flask',
        recipients=[send_to]  # Replace with the recipient's email address
    )
    msg.html = """
    Can I use the <b>html</b> tag here?
    """

    mail.send(msg)
