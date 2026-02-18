import { expect, test, type Page } from '@playwright/test'

async function loginAndOpenWorkbench(page: Page) {
  await page.goto('/login')
  await page.locator('input[placeholder="用户名"]').fill('admin')
  await page.locator('input[placeholder="密码"]').fill('admin123')
  await page.getByRole('button', { name: '登录' }).click()
  await expect(page).toHaveURL(/\/$/)

  await page.getByText('综合分析').first().click()
  await expect(page).toHaveURL(/\/analysis-workbench$/)
}

async function runWorkflow(page: Page, requirementText: string) {
  await page.locator('textarea[placeholder="输入采购需求文本"]').fill(requirementText)
  await page.locator('input[placeholder="如：服务器、工作站"]').fill('服务器')
  await page.getByRole('button', { name: '开始分析' }).click()
  await expect(page.getByText('综合分析结果')).toBeVisible()
  await expect(page.locator('.result-panel').getByText(/风险分\s+\d+/).first()).toBeVisible()
}

test.describe('backend integration @integration', () => {
  test('login and run workflow with real backend', async ({ page }) => {
    test.setTimeout(60000)

    await loginAndOpenWorkbench(page)
    await runWorkflow(page, '采购数据库服务器，要求高可用与可扩展。')
  })

  test('template submit and history shows server workflow', async ({ page }) => {
    test.setTimeout(60000)

    await loginAndOpenWorkbench(page)

    const templateSelect = page
      .locator('.el-form-item')
      .filter({ hasText: '场景模板' })
      .locator('.el-select')
      .first()
    await templateSelect.click()
    await page.locator('.el-select-dropdown__item').filter({ hasText: '服务器采购' }).first().click()

    const budgetInput = page
      .locator('.el-form-item')
      .filter({ hasText: '预算（元）' })
      .locator('input')
      .first()
    await budgetInput.fill('260000')

    await runWorkflow(page, '采购图形渲染服务器，要求双路 CPU 与高速存储。')
    await expect(page.locator('.history-panel .el-table')).toContainText('server')
  })

  test('reuse history creates a new workflow result', async ({ page }) => {
    test.setTimeout(60000)

    await loginAndOpenWorkbench(page)
    await runWorkflow(page, '采购计算服务器，要求支持虚拟化部署。')

    const idCell = page
      .locator('.history-panel .el-table__body-wrapper tbody tr')
      .first()
      .locator('td')
      .first()
    const sourceId = Number((await idCell.innerText()).trim())
    expect(sourceId).toBeGreaterThan(0)

    await page
      .locator('.history-panel .el-table__body-wrapper tbody tr')
      .first()
      .getByRole('button', { name: '复用' })
      .click()

    await expect(page.getByText('综合分析结果')).toBeVisible()

    const historyTag = page.locator('.result-panel').getByText(/#\d+/).first()
    await expect(historyTag).toBeVisible()
    const newId = Number((await historyTag.innerText()).replace('#', '').trim())
    expect(newId).toBeGreaterThan(0)
    expect(newId).not.toBe(sourceId)
  })
})
