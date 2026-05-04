# 校园二手交易平台数据库系统项目说明文件

## 在线访问网址

- 云服务器正式访问地址：`https://campus2hand.site`
- 备用部署地址：`https://campus-secend-trading-system.onrender.com`
- 测试登录账号：`u001`
- 测试登录密码：`campus123`

> 截图说明：本文档使用的截图文件位于 `docs/image/` 目录。

## 一、项目概述

本项目实现了一个校园二手交易平台数据库系统。系统使用 Flask 作为 Web 框架，SQLite 作为数据库，前端页面通过 Jinja2 模板渲染数据库中的真实数据，并提供商品浏览、用户浏览、订单浏览、登录注册、商品新增、改价、删除未售商品、购买商品、基础查询、连接查询、聚合查询等功能。

系统包含以下核心页面：

- 首页：展示平台导航、商品数量、用户数量、订单数量等概览信息。
- 登录页：提供真实登录、注册、退出功能。
- 商品列表页：展示商品数据，并支持新增商品、修改价格、删除未售商品、购买商品和基础查询。
- 用户列表页：展示用户数据，并支持聚合统计查询。
- 订单列表页：展示订单数据，并支持连接查询。

## 二、项目运行与部署步骤

### 2.1 本地运行步骤

1. 获取项目代码：

```bash
git clone https://github.com/steven123397/campus_secend_trading_system.git
cd campus_secend_trading_system
```

2. 创建 Python 虚拟环境并安装依赖：

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

3. 启动 Flask 应用：

```bash
python app.py
```

4. 本地浏览器访问：

```text
http://127.0.0.1:5000/
```

应用首次启动时会自动执行 `db/schema.sql` 和 `db/seed.sql`，创建数据库表、视图、触发器并写入初始数据。如果数据库文件已经存在，系统会直接复用原数据库；如果旧数据库缺少登录密码字段，系统会自动迁移并补充默认密码哈希。

### 2.2 云服务器 Docker 部署步骤

当前云服务器采用 Docker Compose + Gunicorn + Nginx 反向代理部署。

1. 在服务器创建项目目录：

```bash
sudo mkdir -p /srv/apps/trading-system
cd /srv/apps/trading-system
```

2. 拉取应用代码：

```bash
git clone https://github.com/steven123397/campus_secend_trading_system.git app
```

3. 创建运行数据目录：

```bash
mkdir -p data logs
```

4. 创建环境变量文件 `.env`：

```bash
SECRET_KEY=请替换为随机安全字符串
DATABASE_PATH=/app/data/campus_trading.sqlite3
```

5. 在 `/srv/apps/trading-system/docker-compose.yml` 中写入 Compose 配置：

```yaml
services:
  app:
    build: ./app
    container_name: trading-system
    restart: unless-stopped
    env_file:
      - .env
    ports:
      - "127.0.0.1:8101:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

6. 使用 Docker Compose 启动服务：

```bash
docker compose up -d --build
```

当前服务器的 Docker Compose 将容器内部 `8000` 端口映射到宿主机本地 `127.0.0.1:8101`，并将数据库持久化到宿主机的 `./data` 目录。

7. 配置 Nginx 反向代理：

```nginx
server {
    server_name campus2hand.site;

    location / {
        proxy_pass http://127.0.0.1:8101;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

8. 使用 Certbot 配置 HTTPS 证书：

```bash
sudo certbot --nginx -d campus2hand.site
```

9. 访问最终网址：

```text
https://campus2hand.site
```

## 三、数据库设计

### 3.1 用户表 `user`

| 字段名 | 类型 | 约束 | 含义 |
|---|---|---|---|
| user_id | TEXT | PRIMARY KEY | 用户编号 |
| user_name | TEXT | NOT NULL | 用户名 |
| phone | TEXT | NOT NULL, UNIQUE | 手机号 |
| password_hash | TEXT | NOT NULL | 登录密码哈希 |

### 3.2 商品表 `item`

| 字段名 | 类型 | 约束 | 含义 |
|---|---|---|---|
| item_id | TEXT | PRIMARY KEY | 商品编号 |
| item_name | TEXT | NOT NULL | 商品名称 |
| category | TEXT | NOT NULL | 商品类别 |
| price | REAL | NOT NULL, CHECK(price >= 0) | 商品价格 |
| status | INTEGER | NOT NULL, CHECK(status IN (0, 1)) | 商品状态，0 表示未售出，1 表示已售出 |
| seller_id | TEXT | NOT NULL, FOREIGN KEY | 卖家编号，关联 user.user_id |

### 3.3 订单表 `orders`

| 字段名 | 类型 | 约束 | 含义 |
|---|---|---|---|
| order_id | TEXT | PRIMARY KEY | 订单编号 |
| item_id | TEXT | NOT NULL, UNIQUE, FOREIGN KEY | 商品编号，关联 item.item_id，且每个商品只能出现一次 |
| buyer_id | TEXT | NOT NULL, FOREIGN KEY | 买家编号，关联 user.user_id |
| order_date | TEXT | NOT NULL | 订单日期 |

### 3.4 视图

系统创建了两个视图：

- `sold_items_view`：已售商品视图，包含商品名和买家编号。
- `unsold_items_view`：未售商品视图，包含未售商品的主要字段。

### 3.5 一致性约束

系统通过以下方式保证商品和订单一致性：

- `orders.item_id` 设置 `UNIQUE`，保证每个商品最多只能产生一条订单。
- `item.seller_id`、`orders.buyer_id`、`orders.item_id` 设置外键，保证商品、买家、卖家都来自合法记录。
- `item.status` 使用 `CHECK(status IN (0, 1))`，限制状态只能为未售出或已售出。
- `prevent_sold_item_reset` 触发器阻止已经产生订单的商品被改回未售状态。
- 购买商品时使用事务，同时插入订单并更新商品状态。

## 四、网页截图与功能说明

### 4.1 首页

访问地址：`https://campus2hand.site/`

首页展示系统导航、平台介绍、商品总数、用户总数和订单总数。

![首页整体截图](<image/4.1 首页整体截图.png>)

### 4.2 登录页

访问地址：`https://campus2hand.site/login`

登录页支持使用用户编号或手机号登录，也支持注册新用户。初始用户可使用默认密码 `campus123` 登录。

![登录页截图](<image/4.2 登录页截图.png>)

![登录成功后页面截图](<image/4.2 登录成功后页面截图.png>)

### 4.3 商品列表页面

访问地址：`https://campus2hand.site/items`

商品列表页面展示所有商品编号、商品名称、类别、价格、状态和卖家编号。登录后可以执行新增商品、修改价格、删除未售商品和购买商品操作。

![商品列表页面截图](<image/4.3 商品列表页面截图.png>)

![新增商品运行结果截图](<image/4.3 新增商品运行结果截图.png>)

![修改商品价格运行结果截图](<image/4.3 修改商品价格运行结果截图.png>)

![删除未售商品运行结果截图](<image/4.3 删除未售商品运行结果截图.png>)

![购买商品 CalculusBook 运行结果截图](<image/4.3 购买商品CalculusBook运行结果截图.png>)

![重复购买 CalculusBook 被阻止运行结果截图](<image/4.3 重复购买CalculusBook被阻止运行结果截图.png>)

### 4.4 用户列表页面

访问地址：`https://campus2hand.site/users`

用户列表页面展示用户编号、用户名和手机号，并提供聚合统计查询入口。

![用户列表页面截图](<image/4.4 用户列表页面截图.png>)

### 4.5 订单列表页面

访问地址：`https://campus2hand.site/orders`

订单列表页面展示订单编号、商品编号、买家编号和订单日期，并提供连接查询入口。

![订单列表页面截图](<image/4.5 订单列表页面截图.png>)

## 五、数据操作功能说明

### 5.1 插入初始数据

系统在首次启动时读取 `db/seed.sql`，插入题目要求的 4 条用户数据、5 条商品数据和 2 条订单数据。刷新首页和各列表页面后可以看到数据库中的初始数据。

![初始数据页面展示截图](<image/4.3 商品列表页面截图.png>)

### 5.2 插入新商品

在商品列表页填写商品编号、商品名称、类别、价格和卖家编号，提交后系统会向 `item` 表插入一条新商品记录，状态默认为未售出。

![插入新商品运行结果截图](<image/4.3 新增商品运行结果截图.png>)

### 5.3 修改商品价格

在商品列表页选择商品编号并填写新价格，提交后系统会执行 `UPDATE item SET price = ? WHERE item_id = ?`，刷新页面后可以看到价格变化。

![修改商品价格运行结果截图](<image/4.3 修改商品价格运行结果截图.png>)

### 5.4 删除未售商品

在商品列表页选择未售商品编号并提交删除操作。系统会先检查目标商品是否存在、是否已售出；只有 `status = 0` 的商品允许删除。

![删除未售商品运行结果截图](<image/4.3 删除未售商品运行结果截图.png>)

## 六、查询功能与运行结果说明

### 6.1 基本查询

系统在商品列表页实现了以下基本查询：

- 查询所有未售出的商品。
- 查询价格大于 30 的商品。
- 查询生活用品类商品，即 `category = 'DailyGoods'`。
- 查询 `u001` 发布的所有商品。

### 6.2 连接查询

系统在订单列表页实现了以下连接查询：

- 查询所有已售商品及其买家姓名。
- 查询每个订单的商品名、买家名和日期。
- 查询卖家是 `u001` 的商品是否被购买。

### 6.3 聚合与分组查询

系统在用户列表页实现了以下聚合与分组查询：

- 统计商品总数。
- 统计每类商品数量。
- 计算所有商品平均价格。
- 查询发布商品数量最多的用户。

### 6.4 视图查询

系统创建了 `sold_items_view` 和 `unsold_items_view` 两个视图。其中未售商品查询使用 `unsold_items_view`，已售商品视图可用于验证商品和订单之间的已售关系。

## 七、购买商品业务逻辑说明

购买商品操作在后端通过事务完成，流程如下：

1. 检查商品编号、买家编号和订单日期是否填写完整。
2. 开启数据库事务。
3. 查询商品当前状态。
4. 如果商品不存在或已经售出，回滚事务并提示失败。
5. 自动生成新的订单编号。
6. 向 `orders` 表插入订单记录。
7. 将 `item.status` 更新为 `1`。
8. 提交事务。

该流程保证插入订单和更新商品状态是一个整体操作。如果中间任何一步失败，事务会回滚，不会出现只生成订单但商品状态未更新，或商品状态已更新但订单未生成的情况。

![购买商品成功结果截图](<image/4.3 购买商品CalculusBook运行结果截图.png>)

![已售商品再次购买失败结果截图](<image/4.3 重复购买CalculusBook被阻止运行结果截图.png>)

## 八、安全性简答

### 8.1 如何防止普通用户删除数据

系统不允许用户直接连接数据库执行 SQL，所有删除操作都必须经过后端路由。当前版本已经对新增、改价、删除、购买等写操作增加登录校验，未登录用户无法执行删除操作；删除商品时后端还会检查商品状态，只允许删除未售出的商品，已售商品不能删除。

如果要进一步区分管理员和普通用户，可以在 `user` 表中增加 `role` 字段，例如 `admin`、`user`，并在删除路由中判断当前登录用户是否为管理员或商品发布者。这样可以做到普通用户只能浏览和购买，管理员或商品发布者才可以删除指定商品。

### 8.2 如何限制用户只能查询数据

系统通过 Web 后端控制用户权限。普通浏览页面只执行固定的 `SELECT` 查询，查询入口使用白名单方式定义在 `services/queries.py` 中，用户只能选择预设查询编号，不能提交任意 SQL 语句。

如果使用 MySQL、PostgreSQL 等数据库，也可以进一步创建只读数据库账号，只授予 `SELECT` 权限，不授予 `INSERT`、`UPDATE`、`DELETE` 权限，从数据库层限制用户只能查询数据。

## 九、并发与恢复简答

### 9.1 两个用户同时购买同一商品会出现什么问题

如果两个用户几乎同时购买同一件未售商品，可能出现并发竞争：两个请求都先看到商品状态为未售出，然后都尝试插入订单并更新商品状态。如果没有约束和事务，可能导致同一商品被重复购买，产生多条订单。

### 9.2 如何解决并发购买问题

本系统通过事务和唯一约束解决该问题。购买流程使用事务包裹，订单表中的 `item_id` 设置了 `UNIQUE` 约束，因此同一个商品最多只能插入一条订单。即使两个请求同时到达，也只有一个请求能成功提交，另一个请求会因为商品已售或唯一约束冲突而失败并回滚。

如果使用支持行级锁的数据库，例如 MySQL 或 PostgreSQL，还可以在购买时使用行锁，例如 `SELECT ... FOR UPDATE`，锁定目标商品记录，确保同一时间只有一个事务可以修改该商品。

### 9.3 如果系统崩溃，如何恢复订单数据

购买操作中的订单插入和商品状态更新在同一个事务内完成。数据库崩溃时，已提交事务会保留，未提交事务会自动回滚，因此不会出现半完成订单。

当前云服务器部署将 SQLite 数据库文件持久化到服务器的 `data` 目录，即容器重建后数据库不会丢失。为了进一步提高恢复能力，应定期备份 `data/campus_trading.sqlite3`，如果服务器磁盘损坏或误操作删除数据，可以使用最近一次备份恢复订单数据。

## 十、测试与验证

项目包含自动化测试，覆盖页面访问、数据库初始化、数据展示、数据操作、查询功能、购买事务和登录注册等功能。

在 Docker 环境中执行测试：

```bash
docker run --rm -v /srv/apps/trading-system/app:/app -w /app trading-system-app python -m unittest discover -s tests -v
```

当前版本测试结果：

```text
Ran 22 tests
OK
```

## 十一、提交材料建议

按照作业要求，建议提交材料包含：

- 完整项目代码压缩包。
- 本项目说明文件。
- 补充好实际截图后的说明文件。
- 网站操作视频，视频内容应包含输入网址、进入首页、登录、浏览商品、浏览用户、浏览订单、执行查询、执行新增/改价/删除/购买等操作流程。
