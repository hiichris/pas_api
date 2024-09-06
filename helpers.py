from flask import request, jsonify
from functools import wraps
from models import APIToken


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        print(f"Autorization header: {token}")
        if not token:
            return jsonify({"success": False, "message": "Token is missing"}), 401

        # Validate the token
        token = token.split(" ")[1]
        token_record = APIToken.query.filter_by(token=token).first()

        if not token_record:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated
