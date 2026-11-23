import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from flask import Flask

from sunset import deprecate_at


class SunsetTests(unittest.TestCase):
    def setUp(self):
        self.deadline = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        app = Flask(__name__)
        self.calls = []

        @app.get("/old")
        @deprecate_at(self.deadline, replacement="/new")
        def old():
            self.calls.append(True)
            return {"ok": True}, 202, {"X-Original": "kept"}

        self.client = app.test_client()

    def request_at(self, instant):
        with patch("sunset.datetime") as clock:
            clock.now.return_value = instant
            with self.assertLogs("sunset", level="WARNING") as logs:
                response = self.client.get("/old")
        self.assertEqual(len(logs.output), 1)
        self.assertIn("deprecated_call /old", logs.output[0])
        self.assertEqual(response.headers["Sunset"], "Thu, 31 Dec 2026 23:59:59 GMT")
        self.assertEqual(response.headers["Deprecation"], "true")
        self.assertEqual(response.headers["Link"], '</new>; rel="successor-version"')
        return response

    def test_before_sunset_preserves_endpoint_response(self):
        response = self.request_at(self.deadline - timedelta(seconds=1))
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.get_json(), {"ok": True})
        self.assertEqual(response.headers["X-Original"], "kept")
        self.assertEqual(self.calls, [True])

    def test_at_and_after_sunset_block_endpoint(self):
        for instant in (self.deadline, self.deadline + timedelta(seconds=1)):
            with self.subTest(instant=instant):
                response = self.request_at(instant)
                self.assertEqual(response.status_code, 410)
                self.assertEqual(response.get_json()["error"], "gone")
                self.assertEqual(response.get_json()["use_instead"], "/new")
                self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
