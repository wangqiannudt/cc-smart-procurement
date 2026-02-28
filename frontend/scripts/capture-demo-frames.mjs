import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from '@playwright/test'

const scriptDir = path.dirname(fileURLToPath(import.meta.url))
const frontendDir = path.resolve(scriptDir, '..')
const repoRoot = path.resolve(frontendDir, '..')
const dateStr = new Date().toISOString().slice(0, 10)
const demoRoot = path.join(repoRoot, 'docs', 'worklogs', 'demos', `${dateStr}-all-demo-paths`)
const framesRoot = path.join(demoRoot, 'frames')
const metaPath = path.join(demoRoot, 'meta.json')

const scenarios = [
  {
    id: 'demo-01-login-analysis-full',
    title: '登录到综合分析完整链路',
    description: '登录 -> 综合分析 -> 模板填充 -> 提交分析 -> 历史复用',
    route: '/analysis-workbench'
  },
  {
    id: 'demo-02-home-overview',
    title: '系统概览',
    description: '进入首页概览，展示状态卡片、推荐、活动和快捷入口',
    route: '/'
  },
  {
    id: 'demo-03-chat-assistant',
    title: 'AI对话',
    description: '进入对话页并发送问题，展示回答和快捷操作',
    route: '/chat'
  },
  {
    id: 'demo-04-requirements-review',
    title: '需求审查',
    description: '录入需求文本并执行审查，展示结果面板',
    route: '/requirements'
  },
  {
    id: 'demo-05-price-reference',
    title: '价格参考',
    description: '执行价格查询与预测，展示趋势图和预测图',
    route: '/price'
  },
  {
    id: 'demo-06-contract-analysis',
    title: '合同分析',
    description: '录入合同文本并分析，展示风险条款分层',
    route: '/contract'
  },
  {
    id: 'demo-07-admin-console',
    title: '管理后台',
    description: '查看用户管理、工作量和分类统计三个管理视图',
    route: '/admin'
  }
]

function createRecorder(page, scenarioDir) {
  let frameIndex = 1

  const snap = async (waitMs = 0, repeats = 1) => {
    for (let i = 0; i < repeats; i += 1) {
      const file = path.join(scenarioDir, `frame-${String(frameIndex).padStart(4, '0')}.png`)
      await page.screenshot({ path: file })
      frameIndex += 1
      if (waitMs > 0) {
        await page.waitForTimeout(waitMs)
      }
    }
  }

  return {
    snap,
    getFrameCount: () => frameIndex - 1
  }
}

async function dismissDraftRestore(page) {
  const dismissButton = page.getByRole('button', { name: '暂不恢复' })
  if (await dismissButton.isVisible({ timeout: 1200 }).catch(() => false)) {
    await dismissButton.click()
    await page.waitForTimeout(300)
  }
}

async function clickMenu(page, menuText, urlPattern) {
  const menuItem = page.locator('.el-menu-item').filter({ hasText: menuText }).first()
  await menuItem.waitFor({ state: 'visible', timeout: 15000 })
  await menuItem.click()
  await page.waitForURL(urlPattern, { timeout: 20000 })
}

async function showcasePageScroll(page, snap, options = {}) {
  const {
    downSteps = 2,
    upSteps = 2,
    deltaY = 520,
    waitMs = 260,
    startPauseMs = 180
  } = options

  await snap(startPauseMs, 2)
  for (let i = 0; i < downSteps; i += 1) {
    await page.mouse.wheel(0, deltaY)
    await snap(waitMs, 2)
  }
  for (let i = 0; i < upSteps; i += 1) {
    await page.mouse.wheel(0, -deltaY)
    await snap(waitMs, 2)
  }
}

async function clickFirstButtonIfVisible(page, buttonName, snap) {
  const button = page.getByRole('button', { name: buttonName }).first()
  if (await button.isVisible({ timeout: 1500 }).catch(() => false)) {
    await button.click()
    if (snap) await snap(220, 2)
    return true
  }
  return false
}

async function login(page, snap) {
  await page.goto('/login', { waitUntil: 'networkidle' })
  await snap(220, 2)
  await page.mouse.wheel(0, 180)
  await snap(180, 1)
  await page.mouse.wheel(0, -180)
  await snap(180, 1)
  await page.locator('input[placeholder="用户名"]').fill('admin')
  await snap(120, 1)
  await page.locator('input[placeholder="密码"]').fill('admin123')
  await snap(120, 1)
  await page.getByRole('button', { name: '登录' }).click()
  await page.waitForURL('**/', { timeout: 15000 })
  await snap(220, 2)
}

async function waitForVisibleWithCapture(locator, snap, loops = 50, waitMs = 250) {
  for (let i = 0; i < loops; i += 1) {
    if (await locator.isVisible().catch(() => false)) {
      return true
    }
    await snap(waitMs, 1)
  }
  return false
}

async function runScenario(page, scenario, scenarioDir) {
  await mkdir(scenarioDir, { recursive: true })
  const { snap, getFrameCount } = createRecorder(page, scenarioDir)

  if (scenario.id === 'demo-01-login-analysis-full') {
    await login(page, snap)
    await clickMenu(page, '综合分析', '**/analysis-workbench')
    await showcasePageScroll(page, snap, { downSteps: 2, upSteps: 2, deltaY: 420 })

    const templateSelect = page
      .locator('.el-form-item')
      .filter({ hasText: '场景模板' })
      .locator('.el-select')
      .first()
    await templateSelect.click()
    await snap(140, 1)
    await page.locator('.el-select-dropdown__item').filter({ hasText: '服务器采购' }).first().click()
    await snap(200, 2)

    const budgetInput = page
      .locator('.el-form-item')
      .filter({ hasText: '预算（元）' })
      .locator('input')
      .first()
    await budgetInput.fill('280000')
    await page.locator('textarea[placeholder="输入采购需求文本"]').fill('采购数据库服务器，要求双机热备与高可用。')
    await page.locator('textarea[placeholder="输入合同条款文本以进行风险分析"]').fill('合同应约定验收标准、质保期限、违约责任及交付时限。')
    await page.locator('input[placeholder="如：服务器、工作站"]').fill('服务器')
    await snap(260, 3)
    await showcasePageScroll(page, snap, { downSteps: 2, upSteps: 2, deltaY: 460, waitMs: 240 })

    await page.getByRole('button', { name: '开始分析' }).click()
    await snap(220, 2)
    await waitForVisibleWithCapture(page.getByText('综合分析结果'), snap, 80, 240)
    await snap(300, 4)
    await showcasePageScroll(page, snap, { downSteps: 2, upSteps: 2, deltaY: 500, waitMs: 240 })

    const firstRow = page.locator('.history-panel .el-table__body-wrapper tbody tr').first()
    const reuseButton = firstRow.getByRole('button', { name: '复用' })
    if (await reuseButton.isVisible({ timeout: 2500 }).catch(() => false)) {
      await reuseButton.click()
      await snap(240, 2)
      await waitForVisibleWithCapture(page.getByText('综合分析结果'), snap, 50, 240)
      await snap(300, 4)
      await showcasePageScroll(page, snap, { downSteps: 1, upSteps: 1, deltaY: 420, waitMs: 240 })
    }
  }

  if (scenario.id === 'demo-02-home-overview') {
    await clickMenu(page, '系统概览', '**/')
    await showcasePageScroll(page, snap, { downSteps: 3, upSteps: 3, deltaY: 500, waitMs: 240 })
    const opened = await clickFirstButtonIfVisible(page, '查看详情', snap)
    if (opened) {
      await showcasePageScroll(page, snap, { downSteps: 2, upSteps: 2, deltaY: 520, waitMs: 220 })
      await clickMenu(page, '系统概览', '**/')
      await snap(240, 2)
    }
  }

  if (scenario.id === 'demo-03-chat-assistant') {
    await clickMenu(page, 'AI对话', '**/chat')
    await showcasePageScroll(page, snap, { downSteps: 1, upSteps: 1, deltaY: 320, waitMs: 220 })
    const input = page.locator('textarea[placeholder="输入您的问题，按 Enter 发送..."]')
    await input.fill('请给一个数据库服务器采购建议，预算 30 万。')
    await snap(180, 1)
    await page.getByRole('button', { name: '发送' }).click()
    await snap(260, 2)
    await waitForVisibleWithCapture(
      page.locator('.message.assistant').nth(1),
      snap,
      60,
      260
    )
    await snap(300, 4)
    await showcasePageScroll(page, snap, { downSteps: 2, upSteps: 2, deltaY: 460, waitMs: 240 })
  }

  if (scenario.id === 'demo-04-requirements-review') {
    await clickMenu(page, '需求审查', '**/requirements')
    await dismissDraftRestore(page)
    await showcasePageScroll(page, snap, { downSteps: 2, upSteps: 2, deltaY: 420, waitMs: 240 })
    await page.locator('textarea[placeholder="请输入或粘贴需求文档内容..."]').fill(
      '需采购 10 台数据库服务器，用于双活容灾。要求提供原厂三年质保，支持虚拟化部署。'
    )
    await snap(220, 2)
    await page.getByRole('button', { name: '开始审查' }).click()
    await snap(240, 2)
    await waitForVisibleWithCapture(page.getByText('问题清单'), snap, 70, 240)
    await snap(280, 3)
    await showcasePageScroll(page, snap, { downSteps: 2, upSteps: 2, deltaY: 480, waitMs: 240 })
  }

  if (scenario.id === 'demo-05-price-reference') {
    await clickMenu(page, '价格参考', '**/price')
    await dismissDraftRestore(page)
    await showcasePageScroll(page, snap, { downSteps: 2, upSteps: 2, deltaY: 420, waitMs: 220 })
    await page.locator('input[placeholder="产品名称或规格"]').fill('服务器')
    await page.getByRole('button', { name: '查询' }).click()
    await snap(260, 3)
    await waitForVisibleWithCapture(page.locator('.chart-container canvas').first(), snap, 45, 220)
    await page.locator('input[placeholder*="输入产品关键词"]').fill('服务器')
    await page.getByRole('button', { name: /开始预测/ }).click()
    await snap(240, 2)
    await waitForVisibleWithCapture(page.locator('.prediction-chart canvas').first(), snap, 60, 240)
    await snap(300, 4)
    await showcasePageScroll(page, snap, { downSteps: 3, upSteps: 3, deltaY: 520, waitMs: 220 })
  }

  if (scenario.id === 'demo-06-contract-analysis') {
    await clickMenu(page, '合同分析', '**/contract')
    await dismissDraftRestore(page)
    await showcasePageScroll(page, snap, { downSteps: 2, upSteps: 2, deltaY: 420, waitMs: 220 })
    await page.locator('textarea[placeholder="请输入或粘贴合同文档内容..."]').fill(
      '甲方采购服务器设备，乙方应在 30 日内完成交付。若延期每延迟一天按合同金额 1% 赔付，最终解释权归乙方。'
    )
    await snap(240, 2)
    await page.getByRole('button', { name: '开始分析' }).click()
    await snap(240, 2)
    await waitForVisibleWithCapture(page.getByText('风险条款'), snap, 70, 240)
    await snap(300, 4)
    await showcasePageScroll(page, snap, { downSteps: 3, upSteps: 3, deltaY: 520, waitMs: 220 })
  }

  if (scenario.id === 'demo-07-admin-console') {
    await clickMenu(page, '管理后台', '**/admin')
    await showcasePageScroll(page, snap, { downSteps: 2, upSteps: 2, deltaY: 460, waitMs: 220 })
    await page.getByRole('tab', { name: '经办人工作量' }).click()
    await showcasePageScroll(page, snap, { downSteps: 2, upSteps: 2, deltaY: 500, waitMs: 220, startPauseMs: 120 })
    await page.getByRole('tab', { name: '采购分类统计' }).click()
    await showcasePageScroll(page, snap, { downSteps: 2, upSteps: 2, deltaY: 500, waitMs: 220, startPauseMs: 120 })
    await page.getByRole('tab', { name: '用户管理' }).click()
    await showcasePageScroll(page, snap, { downSteps: 2, upSteps: 2, deltaY: 500, waitMs: 220, startPauseMs: 120 })
  }

  await snap(400, 2)
  return getFrameCount()
}

async function main() {
  await mkdir(framesRoot, { recursive: true })

  const browser = await chromium.launch({
    headless: true,
    channel: 'chrome'
  })
  const context = await browser.newContext({
    baseURL: 'http://127.0.0.1:5173',
    viewport: { width: 1366, height: 768 }
  })
  const page = await context.newPage()

  const collected = []
  try {
    for (const scenario of scenarios) {
      const scenarioDir = path.join(framesRoot, scenario.id)
      const frameCount = await runScenario(page, scenario, scenarioDir)
      collected.push({
        ...scenario,
        frame_dir: scenarioDir,
        frame_count: frameCount
      })
      console.log(`captured:${scenario.id}:${frameCount}`)
    }
  } finally {
    await context.close()
    await browser.close()
  }

  const meta = {
    generated_at: new Date().toISOString(),
    date: dateStr,
    demo_root: demoRoot,
    frames_root: framesRoot,
    scenarios: collected
  }
  await writeFile(metaPath, JSON.stringify(meta, null, 2), 'utf-8')

  console.log(`meta:${metaPath}`)
}

main().catch((error) => {
  console.error(error)
  process.exitCode = 1
})
