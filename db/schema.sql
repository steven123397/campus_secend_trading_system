DROP VIEW IF EXISTS sold_items_view;
DROP VIEW IF EXISTS unsold_items_view;
DROP TRIGGER IF EXISTS prevent_sold_item_reset;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    user_id TEXT PRIMARY KEY,
    user_name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE item (
    item_id TEXT PRIMARY KEY,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL CHECK (price >= 0),
    status INTEGER NOT NULL CHECK (status IN (0, 1)),
    seller_id TEXT NOT NULL,
    FOREIGN KEY (seller_id) REFERENCES user(user_id)
);

CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    item_id TEXT NOT NULL UNIQUE,
    buyer_id TEXT NOT NULL,
    order_date TEXT NOT NULL,
    FOREIGN KEY (item_id) REFERENCES item(item_id),
    FOREIGN KEY (buyer_id) REFERENCES user(user_id)
);

CREATE VIEW sold_items_view AS
SELECT item.item_name, orders.buyer_id
FROM item
JOIN orders ON orders.item_id = item.item_id
WHERE item.status = 1;

CREATE VIEW unsold_items_view AS
SELECT item_id, item_name, category, price, status, seller_id
FROM item
WHERE status = 0;

CREATE TRIGGER prevent_sold_item_reset
BEFORE UPDATE OF status ON item
FOR EACH ROW
WHEN NEW.status = 0
  AND EXISTS (SELECT 1 FROM orders WHERE item_id = OLD.item_id)
BEGIN
    SELECT RAISE(ABORT, 'sold item cannot be reset to unsold while order exists');
END;
