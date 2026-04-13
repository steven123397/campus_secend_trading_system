import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import create_app, initialize_database


class DatabaseInitializationTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "campus.sqlite3"
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE_PATH": str(self.database_path),
            }
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initialize_database_creates_tables_views_and_seed_data(self):
        initialize_database(self.app.config["DATABASE_PATH"], force=True)

        connection = sqlite3.connect(self.app.config["DATABASE_PATH"])
        connection.row_factory = sqlite3.Row

        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        views = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='view'"
            ).fetchall()
        }

        self.assertTrue({"user", "item", "orders"}.issubset(tables))
        self.assertTrue({"sold_items_view", "unsold_items_view"}.issubset(views))

        user_count = connection.execute("SELECT COUNT(*) FROM user").fetchone()[0]
        item_count = connection.execute("SELECT COUNT(*) FROM item").fetchone()[0]
        order_count = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

        self.assertEqual(user_count, 4)
        self.assertEqual(item_count, 5)
        self.assertEqual(order_count, 2)

    def test_constraints_are_enforced(self):
        initialize_database(self.app.config["DATABASE_PATH"], force=True)

        connection = sqlite3.connect(self.app.config["DATABASE_PATH"])
        connection.execute("PRAGMA foreign_keys = ON")

        with self.assertRaises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO item (item_id, item_name, category, price, status, seller_id)
                VALUES ('i999', 'BadItem', 'Book', 10, 0, 'u999')
                """
            )

        with self.assertRaises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO orders (order_id, item_id, buyer_id, order_date)
                VALUES ('o999', 'i002', 'u001', '2026-04-13')
                """
            )


if __name__ == "__main__":
    unittest.main()
