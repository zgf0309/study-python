# E2E 测试 (Playwright)

端到端测试,真实启动后端 + 前端 + 浏览器,验证完整链路。

## 目录结构

```
e2e/
  playwright.config.ts   # 自动启动 service / web,并指定隔离测试数据库
  tests/
    health.spec.ts       # 后端健康检查 + 前端首页冒烟
    users.spec.ts        # 用户 Tab 渲染冒烟
  .tmp/                  # 测试数据库 (e2e.db) 存放处,自动清理
```

## 前置条件

1. 后端虚拟环境已就绪:在 `service/` 下执行过 `make install`,存在 `.venv`。
2. 前端依赖已安装:在 `web/` 下执行过 `npm install`。

## 安装与初始化

```bash
cd e2e
npm install
npx playwright install --with-deps chromium
```

## 运行

```bash
# 无头运行
npm test

# 带 UI 调试器
npm run test:ui

# 显示浏览器
npm run test:headed

# 查看 HTML 报告
npm run report
```

## 工作机制

- `playwright.config.ts` 中的 `webServer` 会自动启动:
  - 后端: `service/.venv` + `DATABASE_URL=sqlite:///e2e/.tmp/e2e.db`,端口 8090
  - 前端: `web` 的 vite dev server,端口 5173
- 每次启动前删除 `.tmp/e2e.db`,保证空库;FastAPI 启动时会自动 `create_all` 建表。
- 默认仅在 chromium 上运行,需要扩展可在 `projects` 中加入 firefox / webkit。

## 端口/环境变量

```bash
E2E_BACKEND_PORT=8091 E2E_FRONTEND_PORT=5174 npm test
```

## CI 注意事项

CI 环境必须先准备好 `service/.venv` 与 `web/node_modules`;`reuseExistingServer` 在 CI 下为 false,Playwright 会负责拉起服务并在测试结束后关闭。
