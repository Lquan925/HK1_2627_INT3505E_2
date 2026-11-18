from datetime import datetime, timezone
from email.utils import format_datetime

from flask import Flask, request, send_from_directory

from blueprints.v1 import bp as v1_bp
from blueprints.v2 import bp as v2_bp

app = Flask(__name__)
app.json.ensure_ascii = False
# Ngày ngừng hỗ trợ minh họa cho bài tập, có thể thay đổi tại đây.
app.config["V1_SUNSET"] = format_datetime(
    datetime(2027, 12, 31, 23, 59, 59, tzinfo=timezone.utc), usegmt=True
)
app.register_blueprint(v1_bp, url_prefix="/api/v1")
app.register_blueprint(v2_bp, url_prefix="/api/v2")


@app.after_request
def add_sunset_header(response):
    # Bao gồm cả lỗi 404/405 dưới đường dẫn v1.
    if request.path == "/api/v1" or request.path.startswith("/api/v1/"):
        response.headers["Sunset"] = app.config["V1_SUNSET"]
    return response


@app.get("/openapi.yaml")
def openapi():
    return send_from_directory(app.root_path, "openapi.yaml", mimetype="application/yaml")


@app.get("/")
def index():
    return {
        "message": "User API v1 và v2",
        "examples": ["/api/v1/users/1", "/api/v2/users/1"],
        "openapi": "/openapi.yaml",
        "create_user": "POST /api/v2/users",
    }


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
