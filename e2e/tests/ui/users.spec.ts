import { test, expect } from '@playwright/test'
import { safeDelete, uniq } from '../../utils/api'

test.describe('UI: 用户管理', () => {
  test('通过 UI 新增用户后,列表中可见', async ({ page, request }) => {
    const tag = uniq('uiu')
    const name = `用户_${tag}`
    const email = `${tag}@example.com`

    await page.goto('/')
    await page.getByRole('tab', { name: /用户/ }).first().click()

    // antd Form.Item 自动给 input 注入 id=name 字段名,通过 css id 定位最稳。
    await page.locator('#name').fill(name)
    await page.locator('#email').fill(email)
    // 角色字段保留默认 viewer

    await page.getByRole('button', { name: /写入本地数据库/ }).click()

    const tableRow = page.locator('tr.ant-table-row').filter({ hasText: name })
    await expect(tableRow.first()).toBeVisible({ timeout: 10_000 })
    await expect(tableRow.first()).toContainText(email)

    // 通过 API 收集真实 id 用于事后清理
    const res = await request.get(
      `http://127.0.0.1:8090/api/users?name=${encodeURIComponent(tag)}&page=1&page_size=10`,
    )
    const body = await res.json()
    const created = (body?.data?.data ?? []).find(
      (u: { email: string }) => u.email === email,
    )
    if (created?.id) await safeDelete(request, `/users/${created.id}`)
  })

  test('通过 UI 删除用户:行从表格中消失', async ({ page, request }) => {
    const tag = uniq('uidel')
    const email = `${tag}@example.com`
    const createRes = await request.post('http://127.0.0.1:8090/api/users', {
      data: { name: `待删_${tag}`, email, role: 'viewer' },
      headers: { 'Content-Type': 'application/json' },
    })
    expect(createRes.ok()).toBeTruthy()

    await page.goto('/')
    await page.getByRole('tab', { name: /用户/ }).first().click()

    // 用搜索框过滤(antd 防抖触发 onInput 重新拉数据)
    await page.getByPlaceholder('搜索用户').fill(tag)

    const targetRow = page.locator('tr.ant-table-row').filter({ hasText: email })
    await expect(targetRow.first()).toBeVisible({ timeout: 10_000 })

    // 点击该行的 danger 按钮(antd 的 <Button danger> 会带上 ant-btn-dangerous)
    await targetRow.first().locator('button.ant-btn-dangerous').click()

    await expect(targetRow).toHaveCount(0, { timeout: 10_000 })
  })
})
