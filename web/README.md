# React 前端项目

这是一个可独立运行的 React + Ant Design 前端项目，默认通过 Vite 开发代理访问本地 Python 后端。

## 技术栈

- React 19
- Vite
- TypeScript
- Ant Design
- Axios

## 重点通讯链路

### 1. 前端和后台通讯

前端统一通过 `src/api.ts` 发起请求：

- `GET /api/health`
- `GET /api/users`
- `POST /api/users`

开发环境下，Vite 会把 `/api` 自动代理到本地后端：

- 前端地址：`http://127.0.0.1:5173`
- 后端地址：`http://127.0.0.1:8090`
- 浏览器实际请求：`/api/...`
- 代理转发目标：`http://127.0.0.1:8090/api/...`

### 2. 页面展示内容

页面重点展示三件事：

1. 后端是否联通
2. 数据库是否联通
3. 提交表单后，数据是否从前端写入后端并最终落库

## 运行方式

如果你的全局 npm 缓存没有权限，建议使用项目内缓存安装：

```bash
cd /Users/zhangguofeng/Documents/test/web
npm run install:local
npm run dev:host
```

如果后续需要显式指定后端地址，可复制 `.env.example` 为 `.env` 并调整：

```bash
VITE_API_BASE_URL=/api
```
