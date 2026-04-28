import { test, expect } from '@playwright/test'
import { api, createUser, safeDelete, uniq } from '../../utils/api'

test.describe('API: 用户 CRUD', () => {
  test('完整流程:创建 -> 查询 -> 更新 -> 删除', async ({ request }) => {
    const tag = uniq('apiu')
    const email = `${tag}@example.com`

    // 创建
    const created = await api<{ id: number; name: string; email: string; role: string }>(
      request,
      {
        method: 'POST',
        path: '/users',
        data: { name: `张三_${tag}`, email, role: 'editor' },
      },
    )
    expect(created.status).toBe(200)
    expect(created.payload.id).toBeGreaterThan(0)
    expect(created.payload.email).toBe(email)
    expect(created.payload.role).toBe('editor')
    const id = created.payload.id

    // 列表查询(按名称模糊)
    const listed = await api<Array<{ id: number; name: string }>>(request, {
      method: 'GET',
      path: '/users',
      params: { name: tag, page: 1, page_size: 10 },
    })
    expect(listed.status).toBe(200)
    expect(Array.isArray(listed.payload)).toBe(true)
    expect(listed.payload.find((u) => u.id === id)).toBeTruthy()
    expect(listed.total).toBeGreaterThanOrEqual(1)

    // 更新
    const updated = await api<{ id: number; name: string; role: string }>(request, {
      method: 'PUT',
      path: '/users',
      data: { id, name: `李四_${tag}`, email, role: 'admin' },
    })
    expect(updated.status).toBe(200)
    expect(updated.payload.name).toBe(`李四_${tag}`)
    expect(updated.payload.role).toBe('admin')

    // 删除
    const removed = await api(request, { method: 'DELETE', path: `/users/${id}` })
    expect(removed.status).toBe(200)

    // 再次删除应 404
    const removeAgain = await api(request, { method: 'DELETE', path: `/users/${id}` })
    expect(removeAgain.status).toBe(404)
  })

  test('创建参数校验:缺姓名 / 邮箱非法 / 角色非法', async ({ request }) => {
    const r1 = await api(request, {
      method: 'POST',
      path: '/users',
      data: { name: '', email: 'a@b.com', role: 'viewer' },
    })
    expect(r1.status).toBe(400)

    const r2 = await api(request, {
      method: 'POST',
      path: '/users',
      data: { name: 'X', email: 'invalid', role: 'viewer' },
    })
    expect(r2.status).toBe(400)

    const r3 = await api(request, {
      method: 'POST',
      path: '/users',
      data: { name: 'X', email: 'x@y.com', role: 'super' },
    })
    expect(r3.status).toBe(400)
  })

  test('邮箱唯一约束:重复邮箱返回 400', async ({ request }) => {
    const u = await createUser(request)
    const dup = await api(request, {
      method: 'POST',
      path: '/users',
      data: { name: '重复', email: u.email, role: 'viewer' },
    })
    expect(dup.status).toBe(400)
    await safeDelete(request, `/users/${u.id}`)
  })
})
