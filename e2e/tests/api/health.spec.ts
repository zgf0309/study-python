import { test, expect } from '@playwright/test'
import { api } from '../../utils/api'

test.describe('API: 健康检查', () => {
  test('GET /api/health 返回 ok 与数据库已连接', async ({ request }) => {
    const { envelope, payload, status } = await api<{
      service: string
      status: string
      database: string
    }>(request, { method: 'GET', path: '/health' })

    expect(status).toBe(200)
    expect(envelope.code).toBe(200)
    expect(payload.status).toBe('ok')
    expect(payload.service).toContain('FastAPI')
    expect(payload.database).toContain('connected')
  })
})
