from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from ..extensions import db


class ApiError(Exception):
    def __init__(self, code, message, status_code=400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class Conflict(ApiError):
    def __init__(self, message):
        super().__init__("conflict", message, 409)


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def validation_error(error):
        return jsonify(code="validation_error", message=error.messages), 422

    @app.errorhandler(ApiError)
    def _on_api(err):
        db.session.rollback()
        return jsonify({"code": err.code, "message": err.message}), err.status_code

    @app.errorhandler(HTTPException)
    def _on_http(err):
        return jsonify(
            {"code": err.name.lower().replace(" ", "_"), "message": err.description}
        ), err.code

    @app.errorhandler(Exception)
    def _on_err(err):
        db.session.rollback()
        app.logger.exception("unhandled")
        return jsonify({"code": "internal_error"}), 500

