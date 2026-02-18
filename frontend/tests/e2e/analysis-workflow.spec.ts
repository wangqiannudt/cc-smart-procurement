import { expect, Page, test } from '@playwright/test'

type WorkflowResult = {
  summary: {
    overall_recommendation: string
    priority: string
    dimensions: Record<string, boolean>
  }
  risk_score: number
  evidence: {
    rules: Array<Record<string, unknown>>
    price_sources: Array<Record<string, unknown>>
    contract_clauses: Array<Record<string, unknown>>
  }
  history_id: number
  requirement_result: Record<string, unknown>
  price_result: Record<string, unknown>
  contract_result: Record<string, unknown>
}

const TEST_USER = {
  id: 1,
  username: 'e2e-admin',
  email: 'e2e-admin@example.com',
  role: 'admin'
}

const buildWorkflowResult = (
  recommendation: string,
  historyId: number,
  riskScore = 42
): WorkflowResult => ({
  summary: {
    overall_recommendation: recommendation,
    priority: 'P1',
    dimensions: {
      requirements: true,
      price: true,
      contract: true
    }
  },
  risk_score: riskScore,
  evidence: {
    rules: [],
    price_sources: [],
    contract_clauses: []
  },
  history_id: historyId,
  requirement_result: { issue_count: 1 },
  price_result: { total: 3 },
  contract_result: { risk_level: '中风险' }
})

const jsonResponse = (payload: unknown) => ({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify(payload)
})

async function setLoggedInState(page: Page) {
  await page.addInitScript((user) => {
    localStorage.setItem('smart_procurement_token', 'e2e-token')
    localStorage.setItem('smart_procurement_user', JSON.stringify(user))
  }, TEST_USER)
}

async function mockApi(
  page: Page,
  options?: {
    historyRows?: Array<Record<string, unknown>>
    workflowResult?: WorkflowResult
    reuseResult?: WorkflowResult
    onWorkflowSubmit?: (payload: Record<string, unknown>) => void
  }
) {
  const historyRows = options?.historyRows ?? []
  const workflowResult = options?.workflowResult ?? buildWorkflowResult('默认分析建议', 1001)
  const reuseResult = options?.reuseResult ?? buildWorkflowResult('默认复用建议', 1002)

  await page.route('**/api/**', async (route) => {
    const request = route.request()
    const pathname = new URL(request.url()).pathname
    const method = request.method()
    if (!pathname.startsWith('/api/')) {
      return route.continue()
    }

    if (pathname === '/api/auth/login' && method === 'POST') {
      return route.fulfill(
        jsonResponse({
          success: true,
          data: {
            access_token: 'e2e-token',
            token_type: 'bearer',
            user: TEST_USER
          }
        })
      )
    }

    if (pathname === '/api/analysis/history' && method === 'GET') {
      return route.fulfill(
        jsonResponse({
          success: true,
          data: historyRows,
          total: historyRows.length,
          page: 1,
          page_size: 10
        })
      )
    }

    if (pathname === '/api/analysis/workflow' && method === 'POST') {
      if (options?.onWorkflowSubmit) {
        const payload = request.postDataJSON() as Record<string, unknown>
        options.onWorkflowSubmit(payload)
      }
      return route.fulfill(
        jsonResponse({
          success: true,
          data: workflowResult
        })
      )
    }

    if (pathname.match(/^\/api\/analysis\/history\/\d+\/reuse$/) && method === 'POST') {
      return route.fulfill(
        jsonResponse({
          success: true,
          data: reuseResult
        })
      )
    }

    return route.fulfill(
      jsonResponse({
        success: true,
        data: {}
      })
    )
  })
}

test.describe('analysis workflow smoke @smoke', () => {
  test('登录 -> 分析 -> 查看结果', async ({ page }) => {
    await mockApi(page, {
      workflowResult: buildWorkflowResult('建议按模板推进采购', 11, 38)
    })

    await page.goto('/login')
    await page.locator('input[placeholder="用户名"]').fill('admin')
    await page.locator('input[placeholder="密码"]').fill('admin123')
    await page.getByRole('button', { name: '登录' }).click()

    await expect(page).toHaveURL(/\/$/)

    await page.getByText('综合分析').first().click()
    await expect(page).toHaveURL(/\/analysis-workbench$/)

    await page.getByPlaceholder('输入采购需求文本').fill('采购数据库服务器，需支持高可用。')
    await page.getByPlaceholder('如：服务器、工作站').fill('服务器')
    await page.getByRole('button', { name: '开始分析' }).click()

    await expect(page.getByText('建议按模板推进采购')).toBeVisible()
    await expect(page.getByText('风险分 38')).toBeVisible()
  })

  test('模板生成 -> 调整 -> 提交', async ({ page }) => {
    let submittedPayload: Record<string, unknown> | null = null
    await setLoggedInState(page)
    await mockApi(page, {
      workflowResult: buildWorkflowResult('模板提交分析完成', 21, 29),
      onWorkflowSubmit: (payload) => {
        submittedPayload = payload
      }
    })

    await page.goto('/analysis-workbench')
    await expect(page).toHaveURL(/\/analysis-workbench$/)

    const templateSelect = page
      .locator('.el-form-item')
      .filter({ hasText: '场景模板' })
      .locator('.el-select')
      .first()
    await templateSelect.click()
    await page.locator('.el-select-dropdown__item').filter({ hasText: '服务器采购' }).first().click()
    await expect(page.locator('textarea[placeholder="输入采购需求文本"]')).toHaveValue(/采购服务器/)

    const budgetInput = page
      .locator('.el-form-item')
      .filter({ hasText: '预算（元）' })
      .locator('input')
      .first()
    await budgetInput.fill('250000')
    await page.locator('textarea[placeholder="输入采购需求文本"]').fill('采购图形渲染服务器，要求双路 CPU。')
    await page.getByRole('button', { name: '开始分析' }).click()

    await expect(page.getByText('模板提交分析完成')).toBeVisible()
    expect(submittedPayload?.template_type).toBe('server')
    expect(submittedPayload?.budget).toBe(250000)
    expect(String(submittedPayload?.requirement_text || '')).toContain('图形渲染服务器')
  })

  test('历史记录复用 -> 再分析', async ({ page }) => {
    await setLoggedInState(page)
    await mockApi(page, {
      historyRows: [
        {
          id: 7,
          template_type: 'server',
          risk_score: 44,
          created_at: '2026-02-18T10:00:00'
        }
      ],
      reuseResult: buildWorkflowResult('复用历史分析已完成', 8, 35)
    })

    await page.goto('/analysis-workbench')
    await expect(page).toHaveURL(/\/analysis-workbench$/)
    await expect(page.locator('.el-table')).toContainText('7')

    await page.getByRole('button', { name: '复用' }).click()

    await expect(page.getByText('复用历史分析已完成')).toBeVisible()
    await expect(page.getByText('#8')).toBeVisible()
  })
})
