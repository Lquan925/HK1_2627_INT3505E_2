from functools import wraps

from flask import Flask, current_app, request

LATEST = "2"
SUPPORTED = {"1", "2", "2024-06-20"}
USERS = {1: {"f": "Văn", "l": "Nguyễn", "e": "a@vnu.vn"}}

app = Flask(__name__)
app.json.ensure_ascii = False


def api_version(supported=SUPPORTED, default=LATEST):
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            version = request.headers.get("X-API-Version", default)
            if version not in supported:
                response = current_app.make_response(
                    ({"error": "unsupported version", "supported": sorted(supported)}, 400)
                )
            else:
                # make_response xử lý được cả dict và tuple (dict, status).
                response = current_app.make_response(fn(version, *args, **kwargs))
                response.headers["X-API-Version-Served"] = version
            # Cache cần phân biệt response theo header chọn phiên bản.
            response.vary.add("X-API-Version")
            return response

        return wrapper

    return decorate


@app.get("/users/<int:uid>")
@api_version()
def get_user(version, uid):
    user = USERS.get(uid)
    if user is None:
        return {"error": "not found"}, 404
    if version == "1":
        return {"id": uid, "full_name": user["f"] + " " + user["l"]}
    # Phiên bản theo ngày dùng cùng schema với v2 theo đề bài.
    return {
        "id": uid,
        "first_name": user["f"],
        "last_name": user["l"],
        "email": user["e"],
    }


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
