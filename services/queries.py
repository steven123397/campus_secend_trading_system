QUERY_DEFINITIONS = {
    "items": {
        "unsold": {
            "title": "未售商品查询结果",
            "description": "查询所有未售出的商品。",
            "columns": [
                {"key": "item_id", "label": "商品编号"},
                {"key": "item_name", "label": "商品名称"},
                {"key": "category", "label": "类别"},
                {"key": "price", "label": "价格"},
                {"key": "seller_id", "label": "卖家编号"},
            ],
            "sql": """
                SELECT item_id, item_name, category, price, seller_id
                FROM unsold_items_view
                ORDER BY item_id
            """,
        },
        "price_gt_30": {
            "title": "价格大于 30 的商品",
            "description": "查询价格高于 30 元的商品。",
            "columns": [
                {"key": "item_id", "label": "商品编号"},
                {"key": "item_name", "label": "商品名称"},
                {"key": "price", "label": "价格"},
            ],
            "sql": """
                SELECT item_id, item_name, price
                FROM item
                WHERE price > 30
                ORDER BY item_id
            """,
        },
        "daily_goods": {
            "title": "生活用品类商品",
            "description": "查询分类为 DailyGoods 的商品。",
            "columns": [
                {"key": "item_id", "label": "商品编号"},
                {"key": "item_name", "label": "商品名称"},
                {"key": "price", "label": "价格"},
            ],
            "sql": """
                SELECT item_id, item_name, price
                FROM item
                WHERE category = 'DailyGoods'
                ORDER BY item_id
            """,
        },
        "seller_u001": {
            "title": "u001 发布的商品",
            "description": "查询卖家编号为 u001 的全部商品。",
            "columns": [
                {"key": "item_id", "label": "商品编号"},
                {"key": "item_name", "label": "商品名称"},
                {"key": "status_text", "label": "状态"},
            ],
            "sql": """
                SELECT item_id, item_name,
                       CASE WHEN status = 1 THEN '已售出' ELSE '未售出' END AS status_text
                FROM item
                WHERE seller_id = 'u001'
                ORDER BY item_id
            """,
        },
    },
    "orders": {
        "sold_with_buyer": {
            "title": "已售商品及买家姓名",
            "description": "查询所有已售商品及其买家姓名。",
            "columns": [
                {"key": "item_name", "label": "商品名称"},
                {"key": "buyer_name", "label": "买家姓名"},
            ],
            "sql": """
                SELECT item.item_name, user.user_name AS buyer_name
                FROM orders
                JOIN item ON item.item_id = orders.item_id
                JOIN user ON user.user_id = orders.buyer_id
                ORDER BY orders.order_id
            """,
        },
        "order_details": {
            "title": "订单明细查询结果",
            "description": "查询每个订单的商品名、买家名与日期。",
            "columns": [
                {"key": "item_name", "label": "商品名称"},
                {"key": "buyer_name", "label": "买家姓名"},
                {"key": "order_date", "label": "下单日期"},
            ],
            "sql": """
                SELECT item.item_name, user.user_name AS buyer_name, orders.order_date
                FROM orders
                JOIN item ON item.item_id = orders.item_id
                JOIN user ON user.user_id = orders.buyer_id
                ORDER BY orders.order_id
            """,
        },
        "seller_u001_purchase_status": {
            "title": "u001 商品购买情况",
            "description": "查询卖家为 u001 的商品是否已被购买。",
            "columns": [
                {"key": "item_name", "label": "商品名称"},
                {"key": "purchase_status", "label": "购买状态"},
            ],
            "sql": """
                SELECT item.item_name,
                       CASE WHEN orders.order_id IS NOT NULL THEN '已购买' ELSE '未购买' END AS purchase_status
                FROM item
                LEFT JOIN orders ON orders.item_id = item.item_id
                WHERE item.seller_id = 'u001'
                ORDER BY item.item_id
            """,
        },
    },
    "users": {
        "item_total": {
            "title": "商品总数统计",
            "description": "统计当前平台商品总数。",
            "columns": [
                {"key": "item_total", "label": "商品总数"},
            ],
            "sql": "SELECT COUNT(*) AS item_total FROM item",
        },
        "category_counts": {
            "title": "每类商品数量统计",
            "description": "按照商品类别进行分组统计。",
            "columns": [
                {"key": "category", "label": "类别"},
                {"key": "item_count", "label": "数量"},
            ],
            "sql": """
                SELECT category, COUNT(*) AS item_count
                FROM item
                GROUP BY category
                ORDER BY category
            """,
        },
        "average_price": {
            "title": "商品平均价格",
            "description": "计算全部商品的平均价格。",
            "columns": [
                {"key": "average_price", "label": "平均价格"},
            ],
            "sql": "SELECT ROUND(AVG(price), 2) AS average_price FROM item",
        },
        "top_seller": {
            "title": "发布商品数量最多的用户",
            "description": "找出发布商品数量最多的用户。",
            "columns": [
                {"key": "user_id", "label": "用户编号"},
                {"key": "user_name", "label": "用户名"},
                {"key": "item_count", "label": "发布商品数"},
            ],
            "sql": """
                SELECT user.user_id, user.user_name, COUNT(item.item_id) AS item_count
                FROM user
                LEFT JOIN item ON item.seller_id = user.user_id
                GROUP BY user.user_id, user.user_name
                ORDER BY item_count DESC, user.user_id
                LIMIT 1
            """,
        },
    },
}


def list_queries(group):
    return [
        {"id": query_id, "title": definition["title"]}
        for query_id, definition in QUERY_DEFINITIONS[group].items()
    ]


def run_query(connection, group, query_id):
    definition = QUERY_DEFINITIONS.get(group, {}).get(query_id)
    if definition is None:
        return None

    rows = connection.execute(definition["sql"]).fetchall()
    return {
        "id": query_id,
        "title": definition["title"],
        "description": definition["description"],
        "columns": definition["columns"],
        "rows": rows,
        "row_count": len(rows),
    }
