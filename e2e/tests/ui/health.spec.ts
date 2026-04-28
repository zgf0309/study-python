import { test, expect } from '@playwright/test'

test.describe('UI: 健康概览', () => {
  test('首页可正常加载并显示健康卡片信息', async ({ page }) => {
    await page.goto('/')
    // antd Tabs 页签存在
    await expect(page.getByRole('tab', { name: /用户/ })).toBeVisible()
    await expect(page.getByRole('tab', { name: /角色/ })).toBeVisible()
    await expect(page.getByRole('tab', { name: /菜单/ })).toBeVisible()
    // 健康概览中应包含数据库相关字样(SQLite/connected/数据库)
    await expect(
      page.getByText(/connected|SQLite|数据库/i).first(),
    ).toBeVisible({ timeout: 10_000 })
  })
})
