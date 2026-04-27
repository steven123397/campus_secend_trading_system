import unittest
import tempfile
from pathlib import Path

from app import app, create_app, initialize_database


class AppTestCase(unittest.TestCase):
    def test_homepage_is_available(self):
        client = app.test_client()

        response = client.get("/")
        html = response.data.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("校园二手交易平台数据库系统", html)
        self.assertIn('href="/items"', html)
        self.assertIn('href="/users"', html)
        self.assertIn('href="/orders"', html)


class AuthTestCase(unittest.TestCase):
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

    def test_existing_user_can_login_with_default_password(self):
        response = self.client.post(
            "/login",
            data={"mode": "login", "identifier": "u001", "password": "campus123"},
            follow_redirects=True,
        )
        html = response.data.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("欢迎回来，ZhangSan", html)
        self.assertIn("ZhangSan", html)

    def test_register_creates_logged_in_user(self):
        response = self.client.post(
            "/login",
            data={
                "mode": "signup",
                "user_name": "NewStudent",
                "phone": "13800009999",
                "new_password": "secret123",
            },
            follow_redirects=True,
        )
        html = response.data.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("注册成功", html)
        self.assertIn("NewStudent", html)

    def test_item_mutation_requires_login(self):
        response = self.client.post(
            "/items/delete",
            data={"item_id": "i005"},
            follow_redirects=True,
        )
        html = response.data.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("请先登录后再进行交易操作", html)


if __name__ == "__main__":
    unittest.main()
