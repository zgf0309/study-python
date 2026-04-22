# Python 后端项目

这是一个可独立运行的 FastAPI 后端项目，支持本地 MySQL、PostgreSQL，也保留 SQLite 作为回退方案。

## 目录结构

- `app/main.py`：应用入口，负责初始化、CORS 与路由注册
- `app/routes/`：接口分包目录
- `app/routes/health.py`：健康检查相关接口
- `app/routes/users.py`：用户相关接口
- `app/routes/menus.py`：菜单相关接口
- `app/database.py`：数据库引擎、Session、Base 定义
- `app/models.py`：SQLAlchemy ORM 模型（User、Menu）
- `app/schemas.py`：轻量数据结构与序列化逻辑
- `app/crud.py`：数据库读写逻辑
- `app.db`：未配置外部数据库时自动生成的本地 SQLite 文件
- `.env.example`：本地 MySQL/PostgreSQL 连接示例

## 重点通讯链路

### 1. 前端和后台通讯

前端页面通过 HTTP 请求访问以下接口：

- `GET /api/health`
- `GET /api/users`
- `POST /api/users`
- `PUT /api/users`
- `DELETE /api/users/{id}`
- `GET /api/menus`
- `GET /api/menus/{id}`
- `POST /api/menus`
- `PUT /api/menus`
- `DELETE /api/menus/{id}`

开发环境推荐走前端代理：

- React 开发服务器地址：`http://127.0.0.1:5173`
- Python 服务地址：`http://127.0.0.1:8090`
- 前端请求地址：`/api/...`
- Vite 自动代理到：`http://127.0.0.1:8090/api/...`

### 2. 后台和数据库通讯

后端通过 FastAPI + SQLAlchemy 和本地数据库通讯：

1. `app/main.py` 接收接口请求
2. 通过 `SessionLocal()` 获取数据库 Session
3. 调用 `app/crud.py` 执行业务查询或写入
4. SQLAlchemy 把 ORM 操作转换为 SQL
5. 数据落到本地 MySQL / PostgreSQL，或在未配置时落到本地 SQLite 文件 `app.db`

## 运行方式

```bash
cd /Users/zhangguofeng/Documents/test/service
cp .env.example .env
make run-debug
```

## 启动命令位置

后端启动已经收口到 [service/Makefile](service/Makefile)。

常用目标：

- `make install`：创建 `.venv` 并安装依赖
- `make run`：启动后端
- `make run-debug`：调试模式启动后端
- `make health`：访问 `http://127.0.0.1:8090/api/health`

## 本地数据库配置

默认优先读取 `.env` 里的 `DATABASE_URL`。

如果本地 MySQL 使用 `caching_sha2_password` 或 `sha256_password` 认证方式，项目依赖中的 `cryptography` 已用于完成认证握手。

本地 MySQL 示例：

```bash
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/test_demo?charset=utf8mb4
```

本地 PostgreSQL 示例：

```bash
DATABASE_URL=postgresql+pg8000://postgres:password@127.0.0.1:5432/test_demo
```

如果本地没有启动 MySQL 或 PostgreSQL，服务会回退到 SQLite。
