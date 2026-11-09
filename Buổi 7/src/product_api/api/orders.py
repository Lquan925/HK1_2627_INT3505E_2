from flask import Blueprint, abort, jsonify, request, url_for
from marshmallow import ValidationError
from sqlalchemy import func, select, update
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models import Order, OrderItem, Product
from .errors import Conflict
from .order_schemas import OrderIn, OrderOut
from .products import load_body

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")


def order_query():
    # Two SELECTs: orders, then all items joined to their products.
    return select(Order).options(selectinload(Order.items).joinedload(OrderItem.product))


def get_order(id):
    order = db.session.scalar(order_query().where(Order.id == id))
    if order is None:
        abort(404, description="Order not found.")
    return order


@orders_bp.post("")
def create_order():
    body = load_body(OrderIn())
    order = Order()
    db.session.add(order)
    # Stable ordering reduces deadlocks for concurrent multi-product orders.
    for item in sorted(body["items"], key=lambda item: item["product_id"]):
        product = db.session.get(Product, item["product_id"])
        if product is None or product.archived:
            db.session.rollback()
            abort(404, description="Product not found.")
        result = db.session.execute(
            update(Product).where(
                Product.id == product.id,
                Product.archived.is_(False),
                Product.qty_in_stock >= item["qty"],
            ).values(qty_in_stock=Product.qty_in_stock - item["qty"])
            .execution_options(synchronize_session=False)
        )
        if result.rowcount != 1:
            raise Conflict("Insufficient stock.")
        order.items.append(OrderItem(
            product_id=product.id, qty=item["qty"], unit_price_cents=product.price_cents
        ))
    db.session.flush()
    order_id = order.id
    db.session.commit()
    return OrderOut().dump(get_order(order_id)), 201, {
        "Location": url_for("orders.read_order", id=order_id)
    }


@orders_bp.get("/<int:id>")
def read_order(id):
    return OrderOut().dump(get_order(id)), 200


@orders_bp.get("")
def list_orders():
    try:
        page = max(1, int(request.args.get("page", 1)))
        size = min(100, max(1, int(request.args.get("size", 20))))
    except ValueError:
        raise ValidationError({"pagination": ["page and size must be integers."]}) from None
    orders = db.session.scalars(order_query().order_by(Order.id).offset((page - 1) * size).limit(size)).all()
    total = db.session.scalar(select(func.count()).select_from(Order))
    return jsonify(items=OrderOut(many=True).dump(orders), page=page, size=size, total=total)
