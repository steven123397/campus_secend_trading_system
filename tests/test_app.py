import unittest

from app import app


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


if __name__ == "__main__":
    unittest.main()
