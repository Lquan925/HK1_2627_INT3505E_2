import hashlib
import unittest
from unittest.mock import patch

from app import app


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def post(self, account="ordinary", cohort=None):
        headers = {} if cohort is None else {"X-Cohort": cohort}
        return self.client.post("/orders", json={"account_id": account}, headers=headers)

    def assert_handler(self, response, which):
        self.assertEqual(response.status_code, 201 if which == "v2" else 200)
        self.assertEqual(response.headers["X-Order-Handler"], which)
        self.assertEqual(response.get_json()["version"], which)

    def test_cohort_overrides_zero_percent(self):
        with patch("gateway.V2_PERCENT", 0):
            for cohort in ("beta", "internal", "BETA"):
                self.assert_handler(self.post(cohort=cohort), "v2")

    def test_allow_list_overrides_zero_percent(self):
        with patch("gateway.V2_PERCENT", 0):
            for account in ("acct_42", "acct_99"):
                self.assert_handler(self.post(account), "v2")

    def test_five_percent_is_stable_and_uses_bucket_boundary(self):
        # Buckets 4 and 5 exercise both sides of the 5% boundary.
        accounts = {}
        for i in range(10000):
            account = f"ordinary_{i}"
            bucket = int(hashlib.md5(account.encode()).hexdigest(), 16) % 100
            if bucket in (4, 5):
                accounts[bucket] = account
            if len(accounts) == 2:
                break
        self.assertEqual(set(accounts), {4, 5})
        with patch("gateway.V2_PERCENT", 5):
            for bucket, account in accounts.items():
                for _ in range(3):
                    self.assert_handler(self.post(account), "v2" if bucket == 4 else "v1")

    def test_rollout_zero_and_one_hundred(self):
        for percent, which in ((0, "v1"), (100, "v2")):
            with patch("gateway.V2_PERCENT", percent):
                self.assert_handler(self.post(), which)

    def test_invalid_body(self):
        for body in (None, [], {}, {"account_id": 42}, {"account_id": " "}):
            response = self.client.post("/orders", json=body, content_type="application/json")
            self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
