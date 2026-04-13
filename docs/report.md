# 校园二手交易平台数据库系统说明文档

## 在线访问网址

- 最终公网地址：`https://campus-secend-trading-system.onrender.com`

## 当前部署方案

- 推荐平台：Render
- 推荐形式：`Web Service + Persistent Disk`
- 当前仓库已补齐：`requirements.txt`、`wsgi.py`、`render.yaml`
- 当前状态：已完成首次部署，并获得稳定 HTTPS 访问地址

## 为什么当前选择 Render

- 该项目是标准的 Flask Web 应用，适合直接部署为 Python Web Service。
- Render 默认分配 HTTPS 公网地址，部署完成后可直接用于作业提交。
- 当前仓库已经准备好 Blueprint 文件，平台可以直接读取部署配置。

## Render 部署步骤

### 方案 A：使用仓库内的 `render.yaml`（推荐）

1. 确认当前代码已经推送到 GitHub 远程仓库。
2. 登录 Render 控制台，进入 Blueprint 页面。
3. 选择 `New Blueprint Instance`。
4. 连接仓库 `steven123397/campus_secend_trading_system`。
5. 让 Render 读取仓库根目录下的 `render.yaml`。
6. 确认将创建 1 个 Python Web Service，服务名默认为 `campus-secend-trading-system`。
7. 保持构建命令为 `pip install -r requirements.txt`。
8. 保持启动命令为 `gunicorn --bind 0.0.0.0:$PORT --workers 1 wsgi:app`。
9. 确认环境变量：
   - `SECRET_KEY`：平台自动生成
   - `DATABASE_PATH`：`/var/data/campus_trading.sqlite3`
10. 确认挂载磁盘：
   - 挂载目录：`/var/data`
   - 磁盘大小：`5 GB`
11. 点击创建并等待首次部署完成。
12. 部署成功后，记录 Render 分配的 HTTPS 地址并补充到本文件开头。

### 方案 B：在控制台手动创建 Web Service

如果 Blueprint 没有成功读取，也可以手动填写以下配置：

- Runtime：Python
- Build Command：`pip install -r requirements.txt`
- Start Command：`gunicorn --bind 0.0.0.0:$PORT --workers 1 wsgi:app`
- Environment Variables：
  - `SECRET_KEY`：生成随机值
  - `DATABASE_PATH`：`/var/data/campus_trading.sqlite3`
- Persistent Disk：
  - Mount Path：`/var/data`
  - Size：`5 GB`

## 部署后的验证清单

部署完成后，应至少验证以下地址：

- `https://campus-secend-trading-system.onrender.com/`
- `https://campus-secend-trading-system.onrender.com/items`
- `https://campus-secend-trading-system.onrender.com/users`
- `https://campus-secend-trading-system.onrender.com/orders`

并确认以下行为：

- 首页能正常打开并显示导航
- 商品、用户、订单页面都能显示数据库中的真实数据
- 商品新增、改价、删除、购买功能可正常使用
- 查询面板能够返回结果

## 当前线上验证结果（2026-04-13）

- 已验证首页可正常打开，并显示商品总数 5、用户总数 4、订单总数 2。
- 已验证商品页、用户页、订单页均可在线访问，且页面数据来自真实数据库。
- 已验证商品页基础查询 `未售商品查询结果` 可以在线返回 3 条记录。
- 已验证用户页聚合查询 `商品总数统计` 可以在线返回结果 `5`。
- 已验证订单页连接查询 `已售商品及买家姓名` 可以在线返回 2 条记录。

## 重要说明

- 当前项目使用 SQLite，本地数据库文件需要持久化存储。
- 如果部署平台不提供持久化磁盘，商品增删改和购买结果可能会在服务重启后丢失。
- 因此，Render 方案下建议使用带 Persistent Disk 的 Web Service。

## 备用方案

- 如果你不想使用 Render 的付费 Web Service，可以改为 PythonAnywhere 等支持持久化文件系统的平台，但需要调整部署流程并重新记录步骤。
