# Mainline Status

**项目名称：** 校园二手交易平台数据库系统  
**对应计划：** `docs/mainline_plan.md`  
**建立日期：** 2026-04-13  
**最近更新：** 2026-04-13  
**当前阶段：** M7 进行中  
**总进度：** 6 / 8 任务完成

## 状态维护规则

- 开始某个任务前，先把该任务状态改为「进行中」。
- 完成任务并通过最小验证后，再把状态改为「已完成」。
- 每次状态变化都要同步更新「最近更新」、`总进度`、`更新日志`。
- 如果任务范围、优先级或实现方案变更，必须同步更新 `docs/mainline_plan.md`。
- 如果出现阻塞，必须写入「当前阻塞」，并在「更新日志」中记录影响与处理动作。

## 主线任务看板

| ID | 任务名称 | 当前状态 | 完成标准 | 最近一次说明 |
|----|----------|----------|----------|--------------|
| M1 | 项目初始化与最小可运行骨架 | 已完成 | 本地可启动应用，首页可访问 | 已完成 Flask 最小骨架，首页返回 HTTP 200 |
| M2 | 数据库建模、约束与初始化数据 | 已完成 | 三张表、两个视图和初始数据落库 | 已完成 schema、seed 与自动初始化逻辑，约束验证通过 |
| M3 | 基础数据展示页面 | 已完成 | 首页、商品页、用户页、订单页可展示真实数据 | 已完成 4 个页面的真实数据渲染与导航联调 |
| M4 | 数据操作功能 | 已完成 | 新增商品、修改价格、删除未售商品可用 | 已完成商品表单操作并通过真实落库验证 |
| M5 | 基础查询、连接查询与聚合展示 | 已完成 | 所有题目要求查询可在页面展示 | 已完成基础查询、连接查询与聚合结果面板 |
| M6 | 购买商品业务逻辑与一致性保护 | 已完成 | 购买流程事务化，重复购买被阻止 | 已完成购买事务、订单生成与重复购买保护 |
| M7 | 部署与在线访问地址 | 进行中 | 获得可访问公网网址并完成线上验证 | 已补齐 Render 部署入口并完成本地 Gunicorn 验证，等待平台侧创建服务并获取公网地址 |
| M8 | 提交材料、说明文档与演示准备 | 未开始 | 文档、截图、简答、视频脚本齐备 | 待执行 |

## 当前阻塞

- M7 仍需在部署平台侧完成账号登录、仓库授权与服务创建；若选择 Render 且要保留 SQLite 数据，需要使用支持 Persistent Disk 的付费 Web Service。
- 在拿到最终公网地址前，暂时无法完成线上页面验收与状态收尾。

## 更新日志

- 2026-04-13：创建 `docs/mainline_plan.md` 与 `docs/mainline_status.md`，初始化主线任务与状态维护规则。
- 2026-04-13：开始执行 M1，进入项目初始化与最小可运行骨架阶段。
- 2026-04-13：完成 M1，已创建 Flask 应用骨架、首页模板、基础样式、依赖清单与 `db/` 目录；验证命令 `.venv/bin/python -m unittest tests/test_app.py` 通过，`curl -I http://127.0.0.1:5000/` 返回 HTTP 200。
- 2026-04-13：开始执行 M2，进入数据库建模、约束与初始化数据阶段。
- 2026-04-13：完成 M2，已新增 `db/schema.sql`、`db/seed.sql`，并在 `app.py` 中实现自动建库与连接管理；验证命令 `.venv/bin/python -m unittest tests/test_database.py` 与 `.venv/bin/python -m unittest tests/test_app.py` 全部通过。
- 2026-04-13：开始执行 M3，进入基础数据展示页面阶段。
- 2026-04-13：完成 M3，已新增商品页、用户页、订单页模板并改造首页，4 个页面均从真实数据库渲染；验证命令 `.venv/bin/python -m unittest tests/test_pages.py tests/test_app.py tests/test_database.py` 全部通过。
- 2026-04-13：开始执行 M4，进入商品新增、改价、删除功能阶段。
- 2026-04-13：完成 M4，商品页已支持新增商品、修改价格、删除未售商品，并通过数据库断言验证真实落库；验证命令 `.venv/bin/python -m unittest tests/test_item_operations.py tests/test_pages.py tests/test_app.py tests/test_database.py` 全部通过。
- 2026-04-13：开始执行 M5，进入基础查询、连接查询与聚合展示阶段。
- 2026-04-13：完成 M5，已新增 `services/queries.py` 并在商品、用户、订单页面接入题目要求的全部查询结果面板；验证命令 `.venv/bin/python -m unittest tests/test_queries.py tests/test_item_operations.py tests/test_pages.py tests/test_app.py tests/test_database.py` 全部通过。
- 2026-04-13：开始执行 M6，进入购买商品业务逻辑与一致性保护阶段。
- 2026-04-13：完成 M6，商品页已支持购买商品事务、自动生成订单编号、重复购买拦截与失败回滚；验证命令 `.venv/bin/python -m unittest tests/test_purchase.py tests/test_queries.py tests/test_item_operations.py tests/test_pages.py tests/test_app.py tests/test_database.py` 全部通过。
- 2026-04-13：开始执行 M7，已将部署目标确定为 Render，并进入部署入口文件与说明文档补齐阶段；当前待用户在平台侧完成账号登录、仓库授权与服务创建。
- 2026-04-13：补齐 Render 部署入口，已新增 `render.yaml`、`wsgi.py`、`docs/report.md`，并在 `app.py` 中支持从环境变量读取 `DATABASE_PATH` 与 `SECRET_KEY`；验证命令 `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` 通过，且使用 `DATABASE_PATH=/tmp/... .venv/bin/gunicorn --bind 127.0.0.1:5080 --workers 1 wsgi:app` 启动后，`/`、`/items`、`/users`、`/orders` 均返回 HTTP 200。

## 使用提醒

- 执行主线任务时，`docs/mainline_status.md` 是唯一的实时进度记录。
- `docs/mainline_plan.md` 负责描述做什么、按什么顺序做；`docs/mainline_status.md` 负责记录做到哪一步。
- 每完成一个任务，都必须先更新本文件，再开始下一个任务。
