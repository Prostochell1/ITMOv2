"""Functional contract and exercise containment; security regressions are student work."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sandbox import Sandbox
from service import Shop


class ShopTest(unittest.TestCase):
    def setUp(self):
        self.shop = Shop()
        self.addCleanup(self.shop.close)

    def request(self, method, path, body=None, headers=None):
        with self.shop.lock:
            return self.shop.dispatch(method, path, body or {}, headers or {})

    def login(self, username="alice", password="learn-alice"):
        status, result = self.request("POST", "/login", {"username": username, "password": password})
        self.assertEqual(status, 200)
        return {"X-Token": result["token"]}

    def test_health_and_catalog(self):
        self.assertEqual(self.request("GET", "/health"), (200, {"status": "ok"}))
        self.assertEqual(self.request("GET", "/products"), (200, {"chair": 5000, "lamp": 1500}))

    def test_wrong_password_rejected(self):
        self.assertEqual(self.request("POST", "/login", {"username": "alice", "password": "wrong"})[0], 401)

    def test_tokens_identify_distinct_users(self):
        alice, bob = self.login(), self.login("bob", "learn-bob")
        self.assertNotEqual(alice, bob)
        self.assertEqual(self.request("GET", "/profile?id=1", headers=alice)[1][0]["name"], "TEST_ALICE")
        self.assertEqual(self.request("GET", "/profile?id=2", headers=bob)[1][0]["name"], "TEST_BOB")

    def test_staff_can_export_with_staff_session(self):
        auth = self.login("staff", "learn-staff")
        status, profiles = self.request("GET", "/admin/export", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(len(profiles), 2)

    def test_own_profile_and_receipt(self):
        auth = self.login()
        status, profile = self.request("GET", "/profile?id=2", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(profile[0]["name"], "TEST_ALICE")
        status, receipt = self.request("GET", "/files?user=alice&path=receipt.txt", headers=auth)
        self.assertEqual(status, 200)
        self.assertIn("TEST_ALICE", receipt["content"])

    def test_customer_can_buy_at_catalog_price(self):
        status, order = self.request("POST", "/orders", {"product": "lamp", "price": 1}, self.login())
        self.assertEqual(status, 201)
        self.assertEqual((order["owner"], order["price"]), (1, 1500))

    def test_unknown_product_rejected(self):
        self.assertEqual(self.request("POST", "/orders", {"product": "unknown"}, self.login())[0], 400)

    def test_review_can_be_submitted_and_viewed(self):
        auth = self.login()
        self.assertEqual(self.request("POST", "/reviews", {"product": "chair", "text": "Comfortable"}, auth)[0], 201)
        html = self.request("GET", "/reviews/view", headers=auth)[1]
        self.assertIn("Comfortable", html)
        # Ensure html is escaped
        self.request("POST", "/reviews", {"product": "chair", "text": "<script>alert(1)</script>"}, auth)
        html = self.request("GET", "/reviews/view", headers=auth)[1]
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertNotIn("<script>", html)

    def test_assistant_can_return_own_receipt(self):
        auth = self.login()
        status, context = self.request("GET", "/assistant/context?order_id=1", headers=auth)
        self.assertEqual(status, 200)
        self.assertIn("chair", context["prompt"])
        status, result = self.request("POST", "/assistant/execute", {
            "decision": {"tool": "read_file", "arguments": {"path": "files/alice/receipt.txt"}}
        }, auth)
        self.assertEqual(status, 200)
        self.assertIn("TEST_ALICE", result["content"])

    # New security tests
    def test_profile_customer_only_self(self):
        alice = self.login()
        # Asking for another id must still return alice
        status, rows = self.request("GET", "/profile?id=2", headers=alice)
        self.assertEqual(status, 200)
        self.assertEqual(rows[0]["id"], 1)

    def test_orders_customer_scope(self):
        alice = self.login()
        status, rows = self.request("GET", "/orders", headers=alice)
        self.assertEqual(status, 200)
        self.assertTrue(all(r["owner"] == 1 for r in rows))

    def test_orders_staff_all(self):
        staff = self.login("staff", "learn-staff")
        status, rows = self.request("GET", "/orders", headers=staff)
        self.assertEqual(status, 200)
        self.assertGreaterEqual(len(rows), 2)

    def test_orders_price_ignored(self):
        alice = self.login()
        status, order = self.request("POST", "/orders", {"product": "lamp", "price": 1}, alice)
        self.assertEqual(status, 201)
        self.assertEqual(order["price"], 1500)

    def test_files_receipt_only_and_own(self):
        alice = self.login()
        # valid own receipt
        self.assertEqual(self.request("GET", "/files?user=alice&path=receipt.txt", headers=alice)[0], 200)
        # traversal blocked
        self.assertEqual(self.request("GET", "/files?user=alice&path=../bob/receipt.txt", headers=alice)[0], 403)
        # other user blocked
        self.assertEqual(self.request("GET", "/files?user=bob&path=receipt.txt", headers=alice)[0], 403)
        # staff can access others
        staff = self.login("staff", "learn-staff")
        self.assertEqual(self.request("GET", "/files?user=bob&path=receipt.txt", headers=staff)[0], 200)

    def test_admin_export_requires_staff(self):
        alice = self.login()
        self.assertEqual(self.request("GET", "/admin/export", headers=alice)[0], 403)
        staff = self.login("staff", "learn-staff")
        self.assertEqual(self.request("GET", "/admin/export", headers=staff)[0], 200)

    def test_assistant_execute_policy(self):
        alice = self.login()
        # own file ok
        self.assertEqual(self.request("POST", "/assistant/execute", {"decision": {"tool": "read_file", "arguments": {"path": "files/alice/receipt.txt"}}}, alice)[0], 200)
        # foreign file forbidden
        self.assertEqual(self.request("POST", "/assistant/execute", {"decision": {"tool": "read_file", "arguments": {"path": "files/bob/receipt.txt"}}}, alice)[0], 403)
        # export requires staff
        self.assertEqual(self.request("POST", "/assistant/execute", {"decision": {"tool": "export_profiles"}}, alice)[0], 403)
        staff = self.login("staff", "learn-staff")
        self.assertEqual(self.request("POST", "/assistant/execute", {"decision": {"tool": "export_profiles"}}, staff)[0], 200)
        # delete tree requires staff
        self.assertEqual(self.request("POST", "/assistant/execute", {"decision": {"tool": "delete_tree", "arguments": {"path": "."}}}, alice)[0], 403)

    def test_debug_logs_requires_staff(self):
        alice = self.login()
        self.assertEqual(self.request("GET", "/debug/logs", headers=alice)[0], 403)
        staff = self.login("staff", "learn-staff")
        status, logs = self.request("GET", "/debug/logs", headers=staff)
        self.assertEqual(status, 200)
        # Ensure tokens are masked in logs
        self.assertTrue(all(h.get("X-Token", "") != logs[0]["headers"].get("X-Token") for h in [logs[0]["headers"]]))


class SandboxTest(unittest.TestCase):
    def setUp(self):
        self.sandbox = Sandbox()
        self.addCleanup(self.sandbox.close)

    def test_parent_paths_cannot_escape_exercise(self):
        for name in ("../../outside.txt", "/etc/passwd"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.sandbox.read(name)

    def test_external_directory_cannot_be_deleted(self):
        with TemporaryDirectory() as directory:
            sentinel = Path(directory) / "sentinel.txt"
            sentinel.write_text("keep")
            with self.assertRaises(ValueError):
                self.sandbox.delete_tree(directory)
            self.assertEqual(sentinel.read_text(), "keep")

    def test_symlink_cannot_escape_exercise(self):
        with TemporaryDirectory() as directory:
            sentinel = Path(directory) / "sentinel.txt"
            sentinel.write_text("keep")
            link = self.sandbox.root / "escape"
            link.symlink_to(directory, target_is_directory=True)
            with self.assertRaises(ValueError):
                self.sandbox.read("escape/sentinel.txt")
            with self.assertRaises(ValueError):
                self.sandbox.delete_tree("escape")
            self.assertEqual(sentinel.read_text(), "keep")

    def test_delete_of_fixture_root_stays_inside_exercise(self):
        with TemporaryDirectory() as directory:
            sentinel = Path(directory) / "sentinel.txt"
            sentinel.write_text("keep")
            self.sandbox.delete_tree(".")
            self.assertFalse(self.sandbox.root.exists())
            self.assertEqual(sentinel.read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
