from flask import Blueprint, jsonify
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from ..models import Order, OrderItem, Product

health_bp = Blueprint("health", __name__)


@health_bp.get("/healthz")
def healthz():
    return jsonify(status="ok"), 200


@health_bp.get("/ready")
def ready():
    try:
        # Verify connectivity and migrated tables without reading business rows.
        for model in (Product, Order, OrderItem):
            db.session.execute(select(model.id).limit(0))
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(status="not_ready"), 503
    return jsonify(status="ready"), 200
