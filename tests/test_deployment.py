import os
import unittest
from unittest import mock

from app import create_app


class DeploymentConfigurationTestCase(unittest.TestCase):
    def test_create_app_prefers_runtime_environment_variables(self):
        with mock.patch.dict(
            os.environ,
            {
                "DATABASE_PATH": "/tmp/render-campus.sqlite3",
                "SECRET_KEY": "render-secret-key",
            },
            clear=False,
        ):
            app = create_app({"TESTING": True, "INIT_DATABASE": False})

        self.assertEqual(app.config["DATABASE_PATH"], "/tmp/render-campus.sqlite3")
        self.assertEqual(app.config["SECRET_KEY"], "render-secret-key")


if __name__ == "__main__":
    unittest.main()
