from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/items")
def items_placeholder():
    return "<h1>商品列表页开发中</h1><p>将在 M3 阶段接入真实数据库数据。</p>"


@app.route("/users")
def users_placeholder():
    return "<h1>用户列表页开发中</h1><p>将在 M3 阶段接入真实数据库数据。</p>"


@app.route("/orders")
def orders_placeholder():
    return "<h1>订单列表页开发中</h1><p>将在 M3 阶段接入真实数据库数据。</p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
