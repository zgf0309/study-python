import { test, expect } from '@playwright/test'
import { api, createMenu, createRole, createUser, safeDelete } from '../../utils/api'

test.describe('UI: 关联关系配置', () => {
  test('用户 -> 配置角色:UI 勾选并保存后,后端关联生效', async ({ page, request }) => {
    // 通过 API 准备好数据,UI 只负责"勾选 + 保存"。
    const user = await createUser(request)
    const role = await createRole(request)

    await page.goto('/')
    await page.getByRole('tab', { name: /用户/ }).first().click()

    // 在用户列表中找到刚创建的行,点击该行的"配置"按钮。
    const userRow = page.locator('tr.ant-table-row').filter({ hasText: user.name })
    await expect(userRow).toBeVisible({ timeout: 10_000 })
    // antd 中文双字按钮会插入空格("配 置"),用正则匹配。
    await userRow.getByRole('button', { name: /^配\s*置$/ }).click()

    // 进入"配置角色"面板,等待表格加载完成。
    await expect(page.getByText(/^配\s*置\s*角\s*色$/)).toBeVisible()
    const roleRow = page
      .locator('.ant-card', { hasText: /配\s*置\s*角\s*色/ })
      .locator('tr.ant-table-row')
      .filter({ hasText: role.name })
    await expect(roleRow).toBeVisible({ timeout: 10_000 })

    // 勾选行内的复选框。
    await roleRow.locator('input[type="checkbox"]').check()

    // 点击"配置权限",并等待后端 POST /api/users/relation-roles 成功。
    const [bindResp] = await Promise.all([
      page.waitForResponse(
        (r) => r.url().includes('/api/users/relation-roles') && r.request().method() === 'POST',
        { timeout: 10_000 },
      ),
      page.getByRole('button', { name: /配置权限/ }).click(),
    ])
    expect(bindResp.status(), '后端配置角色接口应成功').toBeLessThan(400)

    // 通过 API 复核绑定结果,确保 UI 行为真的写库了。
    const verify = await api<Array<{ id: number }>>(request, {
      method: 'GET',
      path: '/users/relation-roles',
      params: { id: user.id },
    })
    expect(verify.payload.map((r) => r.id)).toContain(role.id)

    // 清理,避免污染后续用例。
    await api(request, {
      method: 'POST',
      path: '/users/relation-roles',
      data: { id: user.id, role_ids: [] },
    })
    await safeDelete(request, `/users/${user.id}`)
    await safeDelete(request, `/roles/${role.id}`)
  })

  test('角色 -> 配置菜单:UI 勾选并保存后,后端关联生效', async ({ page, request }) => {
    const role = await createRole(request)
    const menu = await createMenu(request)

    await page.goto('/')
    await page.getByRole('tab', { name: /角色/ }).first().click()

    const roleRow = page.locator('tr.ant-table-row').filter({ hasText: role.name })
    await expect(roleRow).toBeVisible({ timeout: 10_000 })
    await roleRow.getByRole('button', { name: /^配\s*置$/ }).click()

    await expect(page.getByText(/^配\s*置\s*菜\s*单$/)).toBeVisible()
    const menuRow = page
      .locator('.ant-card', { hasText: /配\s*置\s*菜\s*单/ })
      .locator('tr.ant-table-row')
      .filter({ hasText: menu.name })
    await expect(menuRow).toBeVisible({ timeout: 10_000 })

    await menuRow.locator('input[type="checkbox"]').check()

    const [bindResp] = await Promise.all([
      page.waitForResponse(
        (r) => r.url().includes('/api/roles/relation-menus') && r.request().method() === 'POST',
        { timeout: 10_000 },
      ),
      page.getByRole('button', { name: /配置权限/ }).click(),
    ])
    expect(bindResp.status(), '后端配置菜单接口应成功').toBeLessThan(400)

    const verify = await api<Array<{ id: number }>>(request, {
      method: 'GET',
      path: '/roles/relation-menus',
      params: { id: role.id },
    })
    expect(verify.payload.map((m) => m.id)).toContain(menu.id)

    await api(request, {
      method: 'POST',
      path: '/roles/relation-menus',
      data: { id: role.id, menu_ids: [] },
    })
    await safeDelete(request, `/roles/${role.id}`)
    await safeDelete(request, `/menus/${menu.id}`)
  })
})
