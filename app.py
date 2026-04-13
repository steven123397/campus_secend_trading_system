import sqlite3
from pathlib import Path

from flask import Flask, current_app, g, render_template

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


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


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
        return render_template("items.html", items=items)

    @app.route("/users")
    def users_page():
        users = fetch_all(
            """
            SELECT user_id, user_name, phone
            FROM user
            ORDER BY user_id
            """
        )
        return render_template("users.html", users=users)

    @app.route("/orders")
    def orders_page():
        orders = fetch_all(
            """
            SELECT order_id, item_id, buyer_id, order_date
            FROM orders
            ORDER BY order_id
            """
        )
        return render_template("orders.html", orders=orders)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
