import { test, expect } from '@playwright/test'
import { api, createMenu, createRole, createUser, safeDelete } from '../../utils/api'

test.describe('API: 关联关系', () => {
  test('用户 <-> 角色:绑定 / 查询 / 替换', async ({ request }) => {
    const user = await createUser(request)
    const role1 = await createRole(request)
    const role2 = await createRole(request)

    // 绑定两个角色
    const bind = await api(request, {
      method: 'POST',
      path: '/users/relation-roles',
      data: { id: user.id, role_ids: [role1.id, role2.id] },
    })
    expect(bind.status).toBe(200)

    const listed = await api<Array<{ id: number }>>(request, {
      method: 'GET',
      path: '/users/relation-roles',
      params: { id: user.id },
    })
    expect(listed.status).toBe(200)
    const ids = listed.payload.map((r) => r.id)
    expect(ids).toEqual(expect.arrayContaining([role1.id, role2.id]))

    // 替换为只剩 role1
    await api(request, {
      method: 'POST',
      path: '/users/relation-roles',
      data: { id: user.id, role_ids: [role1.id] },
    })
    const after = await api<Array<{ id: number }>>(request, {
      method: 'GET',
      path: '/users/relation-roles',
      params: { id: user.id },
    })
    const afterIds = after.payload.map((r) => r.id)
    expect(afterIds).toContain(role1.id)
    expect(afterIds).not.toContain(role2.id)

    // 清空
    await api(request, {
      method: 'POST',
      path: '/users/relation-roles',
      data: { id: user.id, role_ids: [] },
    })

    await safeDelete(request, `/users/${user.id}`)
    await safeDelete(request, `/roles/${role1.id}`)
    await safeDelete(request, `/roles/${role2.id}`)
  })

  test('角色 <-> 菜单:绑定 / 查询', async ({ request }) => {
    const role = await createRole(request)
    const m1 = await createMenu(request)
    const m2 = await createMenu(request)

    const bind = await api(request, {
      method: 'POST',
      path: '/roles/relation-menus',
      data: { id: role.id, menu_ids: [m1.id, m2.id] },
    })
    expect(bind.status).toBe(200)

    const listed = await api<Array<{ id: number }>>(request, {
      method: 'GET',
      path: '/roles/relation-menus',
      params: { id: role.id },
    })
    expect(listed.status).toBe(200)
    const ids = listed.payload.map((m) => m.id)
    expect(ids).toEqual(expect.arrayContaining([m1.id, m2.id]))

    await safeDelete(request, `/roles/${role.id}`)
    await safeDelete(request, `/menus/${m1.id}`)
    await safeDelete(request, `/menus/${m2.id}`)
  })
})
