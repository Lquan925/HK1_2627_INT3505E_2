import logging

from flask import Flask, jsonify, request

from gateway import dispatch

app = Flask(__name__)
app.json.ensure_ascii = False


@app.post("/orders")
def create_order():
    body = request.get_json()
    if not isinstance(body, dict):
        return {"error": "JSON body must be an object"}, 400
    account = body.get("account_id")
    if not isinstance(account, str) or not account.strip():
        return {"error": "account_id must be a non-empty string"}, 400
    which, result = dispatch(body)
    response = jsonify(result)
    response.headers["X-Order-Handler"] = which
    return response, (201 if which == "v2" else 200)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="127.0.0.1", port=5000, debug=True)
