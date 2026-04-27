# Campus Second-Hand Trading System

校园二手交易平台数据库系统。项目基于 Flask + SQLite 实现，支持在线浏览商品、用户和订单数据，并提供登录注册、商品管理、购买事务、基础查询、连接查询、聚合查询和数据库视图等功能。

## 在线地址

- 云服务器地址：`https://campus2hand.site`
- 备用部署地址：`https://campus-secend-trading-system.onrender.com`

## 默认账号

系统内置 4 个初始用户，默认密码均为：

```text
campus123
```

可直接使用用户编号或手机号登录，例如：

```text
账号：u001
密码：campus123
```

## 功能概览

- 首页：展示平台概览、商品总数、用户总数和订单总数。
- 登录注册：支持真实登录、注册、退出，密码使用哈希存储。
- 商品页面：展示商品列表，支持新增商品、修改价格、删除未售商品、购买商品。
- 用户页面：展示用户列表，支持商品总数、分类数量、平均价格、发布最多用户等聚合查询。
- 订单页面：展示订单列表，支持已售商品买家、订单明细、指定卖家商品购买状态等连接查询。
- 数据库约束：包含主键、外键、唯一约束、检查约束、视图和触发器。
- 事务保护：购买商品时在同一事务内插入订单并更新商品状态，阻止重复购买。

## 技术栈

- Python 3.11
- Flask 3
- SQLite
- Jinja2
- Gunicorn
- Docker / Docker Compose
- Nginx reverse proxy

## 项目结构

```text
.
├── app.py                  # Flask 应用入口和路由
├── wsgi.py                 # Gunicorn 入口
├── requirements.txt        # Python 依赖
├── Dockerfile              # Docker 镜像构建文件
├── render.yaml             # Render 部署配置
├── db/
│   ├── schema.sql          # 数据库表、视图、触发器定义
│   └── seed.sql            # 初始数据
├── services/
│   └── queries.py          # 查询定义
├── templates/              # 页面模板
├── static/                 # CSS 和 JS
├── tests/                  # 自动化测试
└── docs/                   # 作业要求和项目说明文档
```

## 本地运行

1. 克隆仓库：

```bash
git clone https://github.com/steven123397/campus_secend_trading_system.git
cd campus_secend_trading_system
```

2. 创建虚拟环境并安装依赖：

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

3. 启动应用：

```bash
python app.py
```

4. 访问本地页面：

```text
http://127.0.0.1:5000/
```

首次启动时会自动创建 SQLite 数据库并写入初始数据。默认数据库路径为：

```text
db/campus_trading.sqlite3
```

## Docker 运行

如果项目位于 `/srv/apps/trading-system/app`，可以在上级目录 `/srv/apps/trading-system` 使用 Docker Compose 部署。

示例 `docker-compose.yml`：

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

示例 `.env`：

```env
SECRET_KEY=replace-with-a-random-secret
DATABASE_PATH=/app/data/campus_trading.sqlite3
```

启动服务：

```bash
docker compose up -d --build
```

容器内服务监听 `8000`，宿主机本地访问端口为 `127.0.0.1:8101`。生产环境可通过 Nginx 反向代理到该端口。

## 测试

本地虚拟环境中运行：

```bash
python -m unittest discover -s tests -v
```

Docker 环境中运行：

```bash
docker run --rm -v /srv/apps/trading-system/app:/app -w /app trading-system-app python -m unittest discover -s tests -v
```

当前版本测试覆盖：

- 首页和数据页面访问
- 数据库初始化和约束
- 商品新增、改价、删除
- 查询功能
- 购买事务和重复购买保护
- 登录、注册和写操作权限校验

## 数据库说明

系统包含三张核心表：

- `user`：用户表，包含用户编号、用户名、手机号和密码哈希。
- `item`：商品表，包含商品编号、名称、类别、价格、状态和卖家编号。
- `orders`：订单表，包含订单编号、商品编号、买家编号和订单日期。

系统还包含两个视图：

- `sold_items_view`：已售商品视图。
- `unsold_items_view`：未售商品视图。

购买商品时，系统会同时执行：

- 向 `orders` 表插入一条订单记录。
- 将对应 `item.status` 更新为 `1`。

这两个操作在同一个事务中完成，失败时会整体回滚。

## 文档

- 作业要求：[docs/request.md](docs/request.md)
- 项目说明文件：[docs/project_description.md](docs/project_description.md)
- 部署说明：[docs/report.md](docs/report.md)

