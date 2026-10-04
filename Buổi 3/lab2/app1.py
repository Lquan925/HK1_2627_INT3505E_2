import logging
from flask import Flask, request, jsonify, make_response
from werkzeug.exceptions import HTTPException

logging.basicConfig(level=logging.ERROR)

app = Flask(__name__)

class ProblemError(Exception):
    def __init__(self, status=400, title="Bad Request", detail=None, type_uri="about:blank", instance=None):
        super().__init__()
        self.status = status
        self.title = title
        self.detail = detail
        self.type = type_uri
        self.instance = instance

def make_problem_response(status, title, detail=None, type_url="about:blank", instance=None):
    payload = {
        "type": type_url,
        "title": title,
        "status": status,
    }
    if detail:
        payload["detail"] = detail
        
    if instance:
        payload["instance"] = instance
    else:
        payload["instance"] = request.path

    response = make_response(jsonify(payload))
    response.status_code = status
    response.headers['Content-Type'] = 'application/problem+json'
    return response

@app.errorhandler(ProblemError)
def handle_problem_error(e):
    return make_problem_response(
        status=e.status,
        title=e.title,
        detail=e.detail,
        type_url=e.type,
        instance=e.instance
    )

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    return make_problem_response(
        status=e.code,
        title=e.name,
        detail=e.description
    )

@app.errorhandler(Exception)
def handle_unhandled_exception(e):
    logging.exception("Unhandled Exception occurred: %s", str(e))
    return make_problem_response(
        status=500,
        title="Internal Server Error",
        detail="Đã xảy ra sự cố không mong muốn từ phía máy chủ. Vui lòng thử lại sau."
    )

@app.route('/resources/<int:id>', methods=['GET'])
def get_resource(id):
    raise ProblemError(
        status=404, 
        title="Resource Not Found", 
        detail=f"Resource với ID {id} không tồn tại trong hệ thống."
    )

@app.route('/resources/crash', methods=['GET'])
def trigger_unhandled_exception():
    return str(1 / 0)

if __name__ == '__main__':
    app.run(debug=True)
