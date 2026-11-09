from marshmallow import Schema, fields, validate, validates_schema, ValidationError

from .schemas import ProductOut


class OrderItemIn(Schema):
    product_id = fields.Int(required=True, strict=True, validate=validate.Range(min=1))
    qty = fields.Int(required=True, strict=True, validate=validate.Range(min=1))


class OrderIn(Schema):
    items = fields.List(fields.Nested(OrderItemIn), required=True, validate=validate.Length(min=1, max=100))

    @validates_schema
    def unique_products(self, data, **kwargs):
        ids = [item["product_id"] for item in data["items"]]
        if len(ids) != len(set(ids)):
            raise ValidationError({"items": ["Each product may appear only once."]})


class OrderItemOut(Schema):
    id = fields.Int()
    product_id = fields.Int()
    qty = fields.Int()
    unit_price_cents = fields.Int()
    product = fields.Nested(ProductOut)


class OrderOut(Schema):
    id = fields.Int()
    created_at = fields.DateTime()
    items = fields.List(fields.Nested(OrderItemOut))
