from flask import Blueprint, request, url_for

from .users_data import create_user, get_user

bp = Blueprint("v2", __name__)


@bp.get("/users/<int:uid>")
def get(uid):
    user = get_user(uid)
    if user is None:
        return {"error": "User not found"}, 404
    return {"id": uid, **user}


@bp.post("/users")
def create():
    if not request.is_json:
        return {"error": "Content-Type must be application/json"}, 415
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"error": "Body must be a valid JSON object"}, 400

    fields = ("first_name", "last_name", "email")
    if set(data) != set(fields):
        return {"error": "Exactly first_name, last_name and email are required"}, 400
    if any(not isinstance(data[key], str) or not data[key].strip() for key in fields):
        return {"error": "All fields must be non-empty strings"}, 400

    user = create_user({key: data[key].strip() for key in fields})
    return user, 201, {"Location": url_for("v2.get", uid=user["id"])}
