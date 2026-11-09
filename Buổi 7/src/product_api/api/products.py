from flask import Blueprint, abort, jsonify, request, url_for
from marshmallow import ValidationError
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from .errors import Conflict
from ..extensions import db
from ..models import Product
from .schemas import ProductIn, ProductOut, ProductPatch, ReserveIn

products_bp = Blueprint("products", __name__, url_prefix="/api/v1/products")


def load_body(schema):
    if not request.is_json:
        raise ValidationError({"body": ["Content-Type must be application/json."]})
    try:
        body = request.get_json()
    except BadRequest:
        raise ValidationError({"body": ["Malformed JSON."]}) from None
    return schema.load(body)


def get_active_product(id):
    product = db.session.scalar(
        select(Product).where(Product.id == id, Product.archived.is_(False))
    )
    if product is None:
        abort(404, description="Product not found.")
    return product


@products_bp.get("")
def list_products():
    try:
        page = max(1, int(request.args.get("page", 1)))
        size = min(100, max(1, int(request.args.get("size", 20))))
    except ValueError:
        raise ValidationError({"pagination": ["page and size must be integers."]}) from None
    base = select(Product).where(Product.archived.is_(False))
    rows = db.session.scalars(
        base.order_by(Product.id).offset((page - 1) * size).limit(size)
    ).all()
    total = db.session.scalar(
        select(func.count()).select_from(Product).where(Product.archived.is_(False))
    )
    return jsonify(items=ProductOut(many=True).dump(rows), page=page, size=size, total=total)


@products_bp.get("/<int:id>")
def get_product(id):
    return ProductOut().dump(get_active_product(id)), 200


@products_bp.post("")
def create_product():
    product = Product(**load_body(ProductIn()))
    db.session.add(product)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Conflict("sku already exists") from None
    return ProductOut().dump(product), 201, {
        "Location": url_for("products.get_product", id=product.id)
    }


@products_bp.patch("/<int:id>")
def patch_product(id):
    body = load_body(ProductPatch())
    product = get_active_product(id)
    for key, value in body.items():
        setattr(product, key, value)
    db.session.commit()
    return ProductOut().dump(product), 200


@products_bp.post("/<int:id>/reserve")
def reserve_product(id):
    body = load_body(ReserveIn())
    # Check and decrement in one statement to prevent concurrent overselling.
    result = db.session.execute(
        update(Product)
        .where(
            Product.id == id,
            Product.archived.is_(False),
            Product.qty_in_stock >= body["qty"],
        )
        .values(qty_in_stock=Product.qty_in_stock - body["qty"])
        .execution_options(synchronize_session=False)
    )
    if result.rowcount == 0:
        db.session.rollback()
        get_active_product(id)
        raise Conflict("Insufficient stock.")
    db.session.commit()
    return ProductOut().dump(get_active_product(id)), 200


@products_bp.delete("/<int:id>")
def delete_product(id):
    product = get_active_product(id)
    product.archived = True
    db.session.commit()
    return "", 204

