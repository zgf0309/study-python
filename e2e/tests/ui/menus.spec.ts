import { test, expect } from '@playwright/test'
import { safeDelete, uniq } from '../../utils/api'

test.describe('UI: 菜单管理', () => {
  test('通过 UI 新增菜单后,列表可见', async ({ page, request }) => {
    const tag = uniq('uim')
    const name = `菜单_${tag}`
    const path = `/${tag}`

    await page.goto('/')
    await page.getByRole('tab', { name: /菜单/ }).first().click()

    // 等待菜单表单挂载完成。
    await expect(page.locator('#name')).toBeVisible()

    await page.locator('#name').fill(name)
    await page.locator('#path').fill(path)
    await page.locator('#sort').fill('5')
    await page.locator('#icon').fill('home')

    // status 字段 valuePropName='checked' + required,默认未选中会卡校验,需要显式打开。
    const statusSwitch = page.locator('#status')
    if ((await statusSwitch.getAttribute('aria-checked')) !== 'true') {
      await statusSwitch.click()
    }

    // 监听后端 POST /api/menus 的真实响应,提交失败时立即暴露。
    const [response] = await Promise.all([
      page.waitForResponse(
        (r) => r.url().includes('/api/menus') && r.request().method() === 'POST',
        { timeout: 10_000 },
      ),
      page.getByRole('button', { name: /写入本地数据库/ }).click(),
    ])
    expect(response.status(), '后端创建菜单接口应成功').toBeLessThan(400)

    const row = page.locator('tr.ant-table-row').filter({ hasText: name })
    await expect(row.first()).toBeVisible({ timeout: 10_000 })
    await expect(row.first()).toContainText(path)

    const res = await request.get(
      `http://127.0.0.1:8090/api/menus?name=${encodeURIComponent(tag)}&page=1&page_size=10`,
    )
    const body = await res.json()
    const created = (body?.data?.data ?? []).find(
      (m: { path: string }) => m.path === path,
    )
    if (created?.id) await safeDelete(request, `/menus/${created.id}`)
  })
})
