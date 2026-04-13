import tempfile
import unittest
from pathlib import Path

from app import create_app, initialize_database


class DataPagesTestCase(unittest.TestCase):
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

    def test_items_page_renders_database_data(self):
        response = self.client.get("/items")
        html = response.data.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("CalculusBook", html)
        self.assertIn("Microcontroller", html)
        self.assertIn("u001", html)

    def test_users_page_renders_database_data(self):
        response = self.client.get("/users")
        html = response.data.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("ZhangSan", html)
        self.assertIn("13800000004", html)

    def test_orders_page_renders_database_data(self):
        response = self.client.get("/orders")
        html = response.data.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("o001", html)
        self.assertIn("2024-05-03", html)
        self.assertIn("i004", html)


if __name__ == "__main__":
    unittest.main()
