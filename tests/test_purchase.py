import tempfile
import unittest
from pathlib import Path

from app import create_app, create_connection, initialize_database


class PurchaseFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "campus.sqlite3"
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE_PATH": str(self.database_path),
            }
        )
        initialize_database(self.app.config["DATABASE_PATH"], force=True)
        self.client = self.app.test_client()
        self.client.post(
            "/login",
            data={"mode": "login", "identifier": "u001", "password": "campus123"},
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_purchase_unsold_item_creates_order_and_marks_item_sold(self):
        response = self.client.post(
            "/items/purchase",
            data={
                "item_id": "i001",
                "buyer_id": "u003",
                "order_date": "2026-04-13",
            },
            follow_redirects=True,
        )
        html = response.data.decode("utf-8")

        connection = create_connection(self.app.config["DATABASE_PATH"])
        item = connection.execute(
            "SELECT status FROM item WHERE item_id = 'i001'"
        ).fetchone()
        order = connection.execute(
            "SELECT buyer_id, order_date FROM orders WHERE item_id = 'i001'"
        ).fetchone()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(item["status"], 1)
        self.assertEqual(order["buyer_id"], "u003")
        self.assertEqual(order["order_date"], "2026-04-13")
        self.assertIn("购买成功", html)

    def test_repurchase_is_blocked(self):
        response = self.client.post(
            "/items/purchase",
            data={
                "item_id": "i002",
                "buyer_id": "u003",
                "order_date": "2026-04-13",
            },
            follow_redirects=True,
        )
        html = response.data.decode("utf-8")

        connection = create_connection(self.app.config["DATABASE_PATH"])
        order_count = connection.execute(
            "SELECT COUNT(*) FROM orders WHERE item_id = 'i002'"
        ).fetchone()[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(order_count, 1)
        self.assertIn("已售商品不能再次购买", html)

    def test_failed_purchase_rolls_back(self):
        response = self.client.post(
            "/items/purchase",
            data={
                "item_id": "i003",
                "buyer_id": "u999",
                "order_date": "2026-04-13",
            },
            follow_redirects=True,
        )
        html = response.data.decode("utf-8")

        connection = create_connection(self.app.config["DATABASE_PATH"])
        item = connection.execute(
            "SELECT status FROM item WHERE item_id = 'i003'"
        ).fetchone()
        order = connection.execute(
            "SELECT order_id FROM orders WHERE item_id = 'i003'"
        ).fetchone()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(item["status"], 0)
        self.assertIsNone(order)
        self.assertIn("购买失败", html)

    def test_items_page_contains_purchase_form(self):
        response = self.client.get("/items")
        html = response.data.decode("utf-8")

        self.assertIn("购买商品", html)
        self.assertIn("buyer_id", html)
        self.assertIn("order_date", html)


if __name__ == "__main__":
    unittest.main()
