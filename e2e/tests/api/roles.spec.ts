import { test, expect } from '@playwright/test'
import { api, safeDelete, uniq } from '../../utils/api'

test.describe('API: 角色 CRUD', () => {
  test('完整流程:创建 -> 查询 -> 更新 -> 删除', async ({ request }) => {
    const tag = uniq('apir')

    const created = await api<{ id: number; name: string; status: string }>(request, {
      method: 'POST',
      path: '/roles',
      data: { name: `角色_${tag}`, description: 'desc', sort: 5, status: 'enabled' },
    })
    expect(created.status).toBe(200)
    expect(created.payload.id).toBeGreaterThan(0)
    expect(created.payload.status).toBe('enabled')
    const id = created.payload.id

    const listed = await api<Array<{ id: number; name: string }>>(request, {
      method: 'GET',
      path: '/roles',
      params: { name: tag, page: 1, page_size: 10 },
    })
    expect(listed.payload.find((r) => r.id === id)).toBeTruthy()
    expect(listed.total).toBeGreaterThanOrEqual(1)

    const updated = await api<{ id: number; name: string; status: string }>(request, {
      method: 'PUT',
      path: '/roles',
      data: {
        id,
        name: `角色_${tag}_v2`,
        description: 'desc-2',
        sort: 9,
        status: 'disabled',
      },
    })
    expect(updated.payload.name).toBe(`角色_${tag}_v2`)
    expect(updated.payload.status).toBe('disabled')

    const removed = await api(request, { method: 'DELETE', path: `/roles/${id}` })
    expect(removed.status).toBe(200)

    const removeAgain = await api(request, { method: 'DELETE', path: `/roles/${id}` })
    expect(removeAgain.status).toBe(404)
  })

  test('创建参数校验:空名 / 非法状态', async ({ request }) => {
    const r1 = await api(request, {
      method: 'POST',
      path: '/roles',
      data: { name: '', sort: 1, description: 'x', status: 'enabled' },
    })
    expect(r1.status).toBe(400)

    const r2 = await api(request, {
      method: 'POST',
      path: '/roles',
      data: { name: 'X', sort: 1, description: 'x', status: 'whatever' },
    })
    expect(r2.status).toBe(400)
  })
})
