import tempfile
import unittest
from pathlib import Path

from app import create_app, create_connection, initialize_database


class ItemOperationTestCase(unittest.TestCase):
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

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_item_persists_to_database(self):
        response = self.client.post(
            "/items/add",
            data={
                "item_id": "i006",
                "item_name": "GraphNotebook",
                "category": "Book",
                "price": "18",
                "seller_id": "u002",
            },
            follow_redirects=True,
        )

        connection = create_connection(self.app.config["DATABASE_PATH"])
        item = connection.execute(
            "SELECT item_name, price, seller_id, status FROM item WHERE item_id = 'i006'"
        ).fetchone()

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(item)
        self.assertEqual(item["item_name"], "GraphNotebook")
        self.assertEqual(item["seller_id"], "u002")
        self.assertEqual(item["status"], 0)

    def test_update_price_changes_only_target_item(self):
        response = self.client.post(
            "/items/update-price",
            data={"item_id": "i001", "price": "26.5"},
            follow_redirects=True,
        )

        connection = create_connection(self.app.config["DATABASE_PATH"])
        item = connection.execute(
            "SELECT item_name, price FROM item WHERE item_id = 'i001'"
        ).fetchone()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(item["item_name"], "CalculusBook")
        self.assertEqual(item["price"], 26.5)

    def test_delete_unsold_item_removes_row(self):
        response = self.client.post(
            "/items/delete",
            data={"item_id": "i005"},
            follow_redirects=True,
        )

        connection = create_connection(self.app.config["DATABASE_PATH"])
        item = connection.execute(
            "SELECT item_id FROM item WHERE item_id = 'i005'"
        ).fetchone()

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(item)

    def test_delete_sold_item_is_blocked(self):
        response = self.client.post(
            "/items/delete",
            data={"item_id": "i002"},
            follow_redirects=True,
        )
        html = response.data.decode("utf-8")

        connection = create_connection(self.app.config["DATABASE_PATH"])
        item = connection.execute(
            "SELECT item_id FROM item WHERE item_id = 'i002'"
        ).fetchone()

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(item)
        self.assertIn("只能删除未售出的商品", html)


if __name__ == "__main__":
    unittest.main()
