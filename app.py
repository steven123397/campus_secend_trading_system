import sqlite3
from pathlib import Path

from flask import (
    Flask,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from services.queries import list_queries, run_query

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE_PATH = BASE_DIR / "db" / "campus_trading.sqlite3"
DEFAULT_SCHEMA_PATH = BASE_DIR / "db" / "schema.sql"
DEFAULT_SEED_PATH = BASE_DIR / "db" / "seed.sql"


def create_connection(database_path):
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(database_path, force=False, schema_path=None, seed_path=None):
    database_file = Path(database_path)
    schema_file = Path(schema_path or DEFAULT_SCHEMA_PATH)
    seed_file = Path(seed_path or DEFAULT_SEED_PATH)

    if force and database_file.exists():
        database_file.unlink()

    if database_file.exists():
        return

    database_file.parent.mkdir(parents=True, exist_ok=True)

    connection = create_connection(str(database_file))
    try:
        connection.executescript(schema_file.read_text(encoding="utf-8"))
        connection.executescript(seed_file.read_text(encoding="utf-8"))
        connection.commit()
    finally:
        connection.close()


def get_db():
    if "db" not in g:
        g.db = create_connection(current_app.config["DATABASE_PATH"])
    return g.db


def fetch_all(query, params=()):
    return get_db().execute(query, params).fetchall()


def fetch_one(query, params=()):
    return get_db().execute(query, params).fetchone()


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def parse_price(raw_value):
    return float(raw_value)


def build_query_result(group):
    query_id = request.args.get("query", "").strip()
    if not query_id:
        return None
    return run_query(get_db(), group, query_id)


def generate_order_id(connection):
    row = connection.execute(
        "SELECT MAX(CAST(SUBSTR(order_id, 2) AS INTEGER)) AS max_id FROM orders"
    ).fetchone()
    next_number = (row["max_id"] or 0) + 1
    return f"o{next_number:03d}"


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="dev",
        DATABASE_PATH=str(DEFAULT_DATABASE_PATH),
        SCHEMA_PATH=str(DEFAULT_SCHEMA_PATH),
        SEED_PATH=str(DEFAULT_SEED_PATH),
        INIT_DATABASE=True,
    )

    if test_config:
        app.config.update(test_config)

    if app.config.get("INIT_DATABASE", True):
        initialize_database(
            app.config["DATABASE_PATH"],
            schema_path=app.config["SCHEMA_PATH"],
            seed_path=app.config["SEED_PATH"],
        )

    app.teardown_appcontext(close_db)

    @app.route("/")
    def home():
        item_count = fetch_all("SELECT COUNT(*) AS count FROM item")[0]["count"]
        user_count = fetch_all("SELECT COUNT(*) AS count FROM user")[0]["count"]
        order_count = fetch_all("SELECT COUNT(*) AS count FROM orders")[0]["count"]
        return render_template(
            "index.html",
            item_count=item_count,
            user_count=user_count,
            order_count=order_count,
        )

    @app.route("/items")
    def items_page():
        items = fetch_all(
            """
            SELECT item_id, item_name, category, price, status, seller_id
            FROM item
            ORDER BY item_id
            """
        )
        users = fetch_all("SELECT user_id, user_name FROM user ORDER BY user_id")
        unsold_items = fetch_all(
            "SELECT item_id, item_name FROM item WHERE status = 0 ORDER BY item_id"
        )
        return render_template(
            "items.html",
            items=items,
            users=users,
            unsold_items=unsold_items,
            available_queries=list_queries("items"),
            query_result=build_query_result("items"),
        )

    @app.post("/items/add")
    def add_item():
        connection = get_db()

        try:
            connection.execute(
                """
                INSERT INTO item (item_id, item_name, category, price, status, seller_id)
                VALUES (?, ?, ?, ?, 0, ?)
                """,
                (
                    request.form["item_id"].strip(),
                    request.form["item_name"].strip(),
                    request.form["category"].strip(),
                    parse_price(request.form["price"]),
                    request.form["seller_id"].strip(),
                ),
            )
            connection.commit()
            flash("商品新增成功。", "success")
        except (KeyError, ValueError):
            connection.rollback()
            flash("新增失败：请填写完整且合法的商品信息。", "error")
        except sqlite3.IntegrityError as error:
            connection.rollback()
            flash(f"新增失败：{error}", "error")

        return redirect(url_for("items_page"))

    @app.post("/items/update-price")
    def update_item_price():
        connection = get_db()

        try:
            new_price = parse_price(request.form["price"])
            cursor = connection.execute(
                "UPDATE item SET price = ? WHERE item_id = ?",
                (new_price, request.form["item_id"].strip()),
            )
            if cursor.rowcount == 0:
                flash("改价失败：未找到目标商品。", "error")
            else:
                connection.commit()
                flash("商品价格修改成功。", "success")
        except (KeyError, ValueError):
            connection.rollback()
            flash("改价失败：请输入合法价格。", "error")
        except sqlite3.IntegrityError as error:
            connection.rollback()
            flash(f"改价失败：{error}", "error")

        return redirect(url_for("items_page"))

    @app.post("/items/delete")
    def delete_item():
        connection = get_db()
        item_id = request.form.get("item_id", "").strip()
        item = fetch_one("SELECT status FROM item WHERE item_id = ?", (item_id,))

        if item is None:
            flash("删除失败：未找到目标商品。", "error")
            return redirect(url_for("items_page"))

        if item["status"] == 1:
            flash("只能删除未售出的商品。", "error")
            return redirect(url_for("items_page"))

        connection.execute("DELETE FROM item WHERE item_id = ?", (item_id,))
        connection.commit()
        flash("未售商品删除成功。", "success")
        return redirect(url_for("items_page"))

    @app.post("/items/purchase")
    def purchase_item():
        connection = get_db()
        item_id = request.form.get("item_id", "").strip()
        buyer_id = request.form.get("buyer_id", "").strip()
        order_date = request.form.get("order_date", "").strip()

        try:
            if not item_id or not buyer_id or not order_date:
                raise ValueError("购买失败：请填写完整的购买信息。")

            connection.execute("BEGIN")
            item = connection.execute(
                "SELECT status FROM item WHERE item_id = ?", (item_id,)
            ).fetchone()

            if item is None:
                raise ValueError("购买失败：未找到目标商品。")
            if item["status"] == 1:
                raise ValueError("已售商品不能再次购买。")

            order_id = generate_order_id(connection)
            connection.execute(
                """
                INSERT INTO orders (order_id, item_id, buyer_id, order_date)
                VALUES (?, ?, ?, ?)
                """,
                (order_id, item_id, buyer_id, order_date),
            )
            connection.execute(
                "UPDATE item SET status = 1 WHERE item_id = ?",
                (item_id,),
            )
            connection.commit()
            flash(f"购买成功，订单编号 {order_id}。", "success")
        except ValueError as error:
            connection.rollback()
            flash(str(error), "error")
        except sqlite3.IntegrityError as error:
            connection.rollback()
            flash(f"购买失败：{error}", "error")

        return redirect(url_for("items_page"))

    @app.route("/users")
    def users_page():
        users = fetch_all(
            """
            SELECT user_id, user_name, phone
            FROM user
            ORDER BY user_id
            """
        )
        return render_template(
            "users.html",
            users=users,
            available_queries=list_queries("users"),
            query_result=build_query_result("users"),
        )

    @app.route("/orders")
    def orders_page():
        orders = fetch_all(
            """
            SELECT order_id, item_id, buyer_id, order_date
            FROM orders
            ORDER BY order_id
            """
        )
        return render_template(
            "orders.html",
            orders=orders,
            available_queries=list_queries("orders"),
            query_result=build_query_result("orders"),
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
