import unittest

from product_api import create_app
from product_api.extensions import db
from product_api.models import Product


class ProductAPITest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        })
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.url = "/api/v1/products"

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def create(self, **changes):
        data = dict(sku="SKU-001", name="Keyboard", price_cents=15000, qty_in_stock=5)
        data.update(changes)
        return self.client.post(self.url, json=data)

    def test_crud_pagination_and_soft_delete(self):
        response = self.create()
        self.assertEqual(response.status_code, 201)
        item = response.get_json()
        url = f"{self.url}/{item['id']}"
        self.assertEqual(self.client.get(url).get_json()["sku"], "SKU-001")
        self.create(sku="SKU-002")
        listing = self.client.get(self.url + "?page=2&size=1").get_json()
        self.assertEqual((listing["page"], listing["size"], listing["total"]), (2, 1, 2))
        self.assertEqual(listing["items"][0]["sku"], "SKU-002")
        response = self.client.patch(url, json={"name": "New keyboard"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["price_cents"], 15000)
        self.assertEqual(response.get_json()["name"], "New keyboard")
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertTrue(db.session.get(Product, item["id"]).archived)
        for method in ("get", "delete", "patch"):
            kwargs = {"json": {"name": "hidden"}} if method == "patch" else {}
            self.assertEqual(getattr(self.client, method)(url, **kwargs).status_code, 404)
        self.assertEqual(self.client.post(url + "/reserve", json={"qty": 1}).status_code, 404)
        self.assertEqual(self.client.get(self.url).get_json()["total"], 1)

    def test_reserve_and_conflicts(self):
        item = self.create().get_json()
        url = f"{self.url}/{item['id']}/reserve"
        self.assertEqual(self.create().status_code, 409)
        response = self.client.post(url, json={"qty": 5})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["qty_in_stock"], 0)
        response = self.client.post(url, json={"qty": 1})
        self.assertEqual(response.status_code, 409)
        self.assertIn("message", response.get_json())
        self.assertEqual(db.session.get(Product, item["id"]).qty_in_stock, 0)
        self.assertEqual(self.client.post(self.url + "/999/reserve", json={"qty": 1}).status_code, 404)

    def test_validation_and_error_format(self):
        for changes in ({"sku": "ab"}, {"name": ""}, {"price_cents": -1},
                        {"price_cents": 1.5}, {"price_cents": True},
                        {"qty_in_stock": -1}, {"archived": True}):
            with self.subTest(changes=changes):
                response = self.create(**changes)
                self.assertEqual(response.status_code, 422)
                self.assertEqual(set(response.get_json()), {"code", "message"})
        for body in (None, [], {}, {"sku": "ABC"}):
            response = self.client.post(self.url, json=body)
            self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.post(self.url, data="{", content_type="application/json").status_code, 422)
        self.assertEqual(self.client.get(self.url + "?page=abc").status_code, 422)
        self.assertEqual(self.client.get(self.url + "/999").status_code, 404)
        item = self.create().get_json()
        url = f"{self.url}/{item['id']}"
        for qty in (0, -1, 1.2, True, "2"):
            self.assertEqual(self.client.post(url + "/reserve", json={"qty": qty}).status_code, 422)
        self.assertEqual(self.client.patch(url, json={"name": ""}).status_code, 422)

    def test_default_stock_and_pagination_limits(self):
        response = self.client.post(self.url, json={"sku": "ABC", "name": "Pen", "price_cents": 0})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["qty_in_stock"], 0)
        result = self.client.get(self.url + "?page=0&size=1000").get_json()
        self.assertEqual((result["page"], result["size"]), (1, 100))


if __name__ == "__main__":
    unittest.main()

