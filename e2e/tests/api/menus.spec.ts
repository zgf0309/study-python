import { test, expect } from '@playwright/test'
import { api, createMenu, safeDelete, uniq } from '../../utils/api'

test.describe('API: 菜单 CRUD', () => {
  test('完整流程:创建 -> 详情 -> 列表 -> 更新 -> 删除', async ({ request }) => {
    const tag = uniq('apim')
    const path = `/${tag}`

    const created = await api<{ id: number; name: string; path: string; status: string }>(
      request,
      {
        method: 'POST',
        path: '/menus',
        data: { name: `菜单_${tag}`, path, icon: 'home', sort: 3, status: 'enabled' },
      },
    )
    expect(created.status).toBe(200)
    expect(created.payload.path).toBe(path)
    const id = created.payload.id

    const detail = await api<{ id: number; name: string }>(request, {
      method: 'GET',
      path: `/menus/${id}`,
    })
    expect(detail.status).toBe(200)
    expect(detail.payload.id).toBe(id)

    const listed = await api<Array<{ id: number }>>(request, {
      method: 'GET',
      path: '/menus',
      params: { name: tag, page: 1, page_size: 10 },
    })
    expect(listed.payload.find((m) => m.id === id)).toBeTruthy()

    const updated = await api<{ id: number; name: string; status: string }>(request, {
      method: 'PUT',
      path: '/menus',
      data: {
        id,
        name: `菜单_${tag}_v2`,
        path,
        icon: 'setting',
        sort: 8,
        status: 'disabled',
      },
    })
    expect(updated.payload.name).toBe(`菜单_${tag}_v2`)
    expect(updated.payload.status).toBe('disabled')

    const removed = await api(request, { method: 'DELETE', path: `/menus/${id}` })
    expect(removed.status).toBe(200)
  })

  test('参数校验:path 必须以 / 开头 / 状态非法', async ({ request }) => {
    const r1 = await api(request, {
      method: 'POST',
      path: '/menus',
      data: { name: 'X', path: 'no-slash', icon: 'a', sort: 1, status: 'enabled' },
    })
    expect(r1.status).toBe(400)

    const r2 = await api(request, {
      method: 'POST',
      path: '/menus',
      data: { name: 'X', path: '/x', icon: 'a', sort: 1, status: 'foo' },
    })
    expect(r2.status).toBe(400)
  })

  test('菜单 path 唯一', async ({ request }) => {
    const m = await createMenu(request)
    const dup = await api(request, {
      method: 'POST',
      path: '/menus',
      data: { name: 'dup', path: m.path, icon: 'a', sort: 1, status: 'enabled' },
    })
    expect(dup.status).toBe(400)
    await safeDelete(request, `/menus/${m.id}`)
  })
})
