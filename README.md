# 本地前后端联调工作区

本工作区包含两个独立项目：

- `web`：React + Ant Design 前端
- `service`：FastAPI + SQLAlchemy + 本地 MySQL / PostgreSQL / SQLite 后端

## 独立运行

### 前端

```bash
cd /Users/zhangguofeng/Documents/test/web
npm run install:local
npm run build
npm run dev:host
```

默认访问：`http://127.0.0.1:5173`

### 后端

```bash
cd /Users/zhangguofeng/Documents/test/service
cp .env.example .env
make run-debug
```

默认访问：`http://127.0.0.1:8090`

后端启动命令已经放在 [service/Makefile](service/Makefile) 中，常用目标：

- `make install`：创建虚拟环境并安装依赖
- `make run`：启动后端
- `make run-debug`：以调试模式启动后端
- `make health`：检查后端健康状态

## 重点标注

### 前端和后台通讯

- 浏览器中的 React 页面通过 Axios 调用 `/api/health`、`/api/users`
- Vite 在开发环境将 `/api` 代理到 `http://127.0.0.1:8090`
- 所以前端和后台之间的主要通讯方式是：`HTTP + JSON`

### 后台和数据库通讯

- FastAPI 接口收到请求后，使用 SQLAlchemy Session 获取数据库连接
- CRUD 逻辑在 `service/app/crud.py`
- ORM 模型在 `service/app/models.py`
- 数据最终写入本地 MySQL 或 PostgreSQL；未配置时回退到 `service/app.db`
- 所以后台和数据库之间的主要通讯方式是：`SQLAlchemy ORM + MySQL/PostgreSQL/SQLite`

## 本地数据库示例

本机已检测到 `mysql` 客户端命令，但没有检测到正在监听的 3306 或 5432 端口。因此代码已经支持本地 MySQL / PostgreSQL 配置，但真正切换到外部数据库前，你需要先启动本地数据库服务。

MySQL：

```bash
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/test_demo?charset=utf8mb4
```

PostgreSQL：

```bash
DATABASE_URL=postgresql+pg8000://postgres:password@127.0.0.1:5432/test_demo
```
