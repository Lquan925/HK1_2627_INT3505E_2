import os
from datetime import datetime

from flask import Flask

from sunset import deprecate_at

app = Flask(__name__)
app.json.ensure_ascii = False

# Override the deadline to demonstrate HTTP 410 without changing the system clock.
V1_SUNSET = datetime.fromisoformat(
    os.environ.get("V1_SUNSET", "2026-12-31T23:59:59+00:00")
)


@app.get("/api/v1/users/<int:uid>")
@deprecate_at(V1_SUNSET, replacement="/api/v2/users")
def get_v1(uid):
    return {"id": uid, "full_name": "Nguyễn Văn A"}


@app.get("/api/v2/users/<int:uid>")
def get_v2(uid):
    return {"id": uid, "first_name": "Văn A", "last_name": "Nguyễn"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
