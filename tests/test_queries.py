import tempfile
import unittest
from pathlib import Path

from app import create_app, create_connection, initialize_database
from services.queries import run_query


class QueryFeatureTestCase(unittest.TestCase):
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
        self.connection = create_connection(self.app.config["DATABASE_PATH"])

    def tearDown(self):
        self.connection.close()
        self.temp_dir.cleanup()

    def test_basic_queries_return_expected_results(self):
        unsold = run_query(self.connection, "items", "unsold")
        expensive = run_query(self.connection, "items", "price_gt_30")
        daily_goods = run_query(self.connection, "items", "daily_goods")
        seller_u001 = run_query(self.connection, "items", "seller_u001")

        self.assertEqual(len(unsold["rows"]), 3)
        self.assertEqual(len(expensive["rows"]), 3)
        self.assertEqual(len(daily_goods["rows"]), 2)
        self.assertEqual(len(seller_u001["rows"]), 2)
        self.assertEqual(unsold["title"], "未售商品查询结果")

    def test_join_queries_return_expected_results(self):
        sold_with_buyer = run_query(self.connection, "orders", "sold_with_buyer")
        order_details = run_query(self.connection, "orders", "order_details")
        seller_purchase_status = run_query(
            self.connection, "orders", "seller_u001_purchase_status"
        )

        self.assertEqual(len(sold_with_buyer["rows"]), 2)
        self.assertEqual(order_details["rows"][0]["item_name"], "DeskLamp")
        self.assertEqual(
            seller_purchase_status["rows"][0]["purchase_status"], "未购买"
        )

    def test_aggregate_queries_return_expected_results(self):
        item_total = run_query(self.connection, "users", "item_total")
        category_counts = run_query(self.connection, "users", "category_counts")
        average_price = run_query(self.connection, "users", "average_price")
        top_seller = run_query(self.connection, "users", "top_seller")

        self.assertEqual(item_total["rows"][0]["item_total"], 5)
        self.assertEqual(len(category_counts["rows"]), 4)
        self.assertEqual(average_price["rows"][0]["average_price"], 40.0)
        self.assertEqual(top_seller["rows"][0]["user_id"], "u001")

    def test_query_pages_render_result_panels(self):
        items_response = self.client.get("/items?query=unsold")
        users_response = self.client.get("/users?query=top_seller")
        orders_response = self.client.get("/orders?query=order_details")

        self.assertIn("未售商品查询结果", items_response.data.decode("utf-8"))
        self.assertIn("结果共 3 条", items_response.data.decode("utf-8"))

        self.assertIn("发布商品数量最多的用户", users_response.data.decode("utf-8"))
        self.assertIn("u001", users_response.data.decode("utf-8"))

        self.assertIn("订单明细查询结果", orders_response.data.decode("utf-8"))
        self.assertIn("DeskLamp", orders_response.data.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
