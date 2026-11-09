from sqlalchemy import event

from product_api.extensions import db
from product_api.models import Product


def product(client, sku, stock=10):
    response = client.post("/api/v1/products", json={
        "sku": sku, "name": sku, "price_cents": 1500, "qty_in_stock": stock
    })
    assert response.status_code == 201
    return response.get_json()["id"]


def test_post_order_multiple_products(client, app):
    ids = [product(client, "SKU-A"), product(client, "SKU-B")]
    response = client.post("/api/v1/orders", json={"items": [
        {"product_id": ids[0], "qty": 2}, {"product_id": ids[1], "qty": 3}
    ]})
    assert response.status_code == 201
    body = response.get_json()
    assert len(body["items"]) == 2
    assert body["items"][0]["unit_price_cents"] == 1500
    assert client.get(response.headers["Location"]).get_json() == body
    with app.app_context():
        assert [db.session.get(Product, id).qty_in_stock for id in ids] == [8, 7]


def test_order_failure_rolls_back_stock(client, app):
    first = product(client, "SKU-A")
    second = product(client, "SKU-B", stock=0)
    response = client.post("/api/v1/orders", json={"items": [
        {"product_id": first, "qty": 2}, {"product_id": second, "qty": 1}
    ]})
    assert response.status_code == 409
    assert client.get("/api/v1/orders").get_json()["total"] == 0
    with app.app_context():
        assert db.session.get(Product, first).qty_in_stock == 10


def test_order_validation_and_missing_product(client):
    id = product(client, "SKU-A")
    for payload in ({}, {"items": []}, {"items": [{"product_id": id, "qty": 0}]},
                    {"items": [{"product_id": id, "qty": True}]},
                    {"items": [{"product_id": id, "qty": 1}] * 2}):
        assert client.post("/api/v1/orders", json=payload).status_code == 422
    assert client.post("/api/v1/orders", json={"items": [{"product_id": 999, "qty": 1}]}).status_code == 404
    assert client.get("/api/v1/orders/999").status_code == 404


def test_get_orders_eager_loading_has_constant_query_count(client, app):
    ids = [product(client, "SKU-A", 100), product(client, "SKU-B", 100)]
    payload = {"items": [{"product_id": id, "qty": 1} for id in ids]}
    assert client.post("/api/v1/orders", json=payload).status_code == 201
    with app.app_context():
        engine = db.engine
    statements = []

    def count_select(connection, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    def read_count(expected):
        statements.clear()
        event.listen(engine, "before_cursor_execute", count_select)
        try:
            response = client.get("/api/v1/orders")
            assert response.status_code == 200
            body = response.get_json()
            assert len(body["items"]) == expected
            assert all(len(order["items"]) == 2 for order in body["items"])
            assert all(item["product"]["sku"] for order in body["items"] for item in order["items"])
            return len(statements)
        finally:
            event.remove(engine, "before_cursor_execute", count_select)

    assert read_count(1) == 3  # orders + items/products + total
    for _ in range(4):
        assert client.post("/api/v1/orders", json=payload).status_code == 201
    assert read_count(5) == 3


def test_health_and_readiness_are_separate(client, app):
    assert client.get("/healthz").status_code == 200
    assert client.get("/ready").status_code == 200
    with app.app_context():
        db.drop_all()
    assert client.get("/healthz").status_code == 200
    assert client.get("/ready").status_code == 503
