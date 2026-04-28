import { defineConfig, devices } from '@playwright/test'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(__dirname, '..')

// 独立的 E2E 测试数据库文件，避免污染本地开发数据。
const TEST_DB_PATH = resolve(__dirname, '.tmp', 'e2e.db')
const TEST_DATABASE_URL = `sqlite:///${TEST_DB_PATH}`

const BACKEND_PORT = Number(process.env.E2E_BACKEND_PORT ?? 8090)
const FRONTEND_PORT = Number(process.env.E2E_FRONTEND_PORT ?? 5173)

// 演示模式:SLOWMO=500 npm run test:headed 让每个动作之间停 500ms,便于讲解。
const SLOW_MO = Number(process.env.SLOWMO ?? 0)
// 默认动作超时;演示时整体放慢,适当抬高单步超时避免误判。
const ACTION_TIMEOUT = SLOW_MO > 0 ? 30_000 : 10_000

export default defineConfig({
  testDir: './tests',
  timeout: SLOW_MO > 0 ? 120_000 : 30_000,
  expect: { timeout: SLOW_MO > 0 ? 15_000 : 5_000 },
  fullyParallel: false,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: `http://127.0.0.1:${FRONTEND_PORT}`,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: ACTION_TIMEOUT,
    launchOptions: {
      slowMo: SLOW_MO,
    },
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      // 启动后端：使用独立测试数据库 + 测试端口。
      command: `bash -lc "rm -f '${TEST_DB_PATH}' && mkdir -p '${dirname(TEST_DB_PATH)}' && cd '${repoRoot}/service' && DATABASE_URL='${TEST_DATABASE_URL}' .venv/bin/python3 -m uvicorn --app-dir . app.main:app --host 127.0.0.1 --port ${BACKEND_PORT}"`,
      url: `http://127.0.0.1:${BACKEND_PORT}/api/health`,
      timeout: 60_000,
      reuseExistingServer: !process.env.CI,
      stdout: 'pipe',
      stderr: 'pipe',
    },
    {
      // 启动前端 dev server。
      command: `bash -lc "cd '${repoRoot}/web' && npm run dev -- --host 127.0.0.1 --port ${FRONTEND_PORT}"`,
      url: `http://127.0.0.1:${FRONTEND_PORT}`,
      timeout: 60_000,
      reuseExistingServer: !process.env.CI,
      stdout: 'pipe',
      stderr: 'pipe',
    },
  ],
})
