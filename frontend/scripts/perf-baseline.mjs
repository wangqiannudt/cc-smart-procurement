import { mkdir, readdir, readFile, stat, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { createMarkdownReport, createPerfSummary } from '../src/tooling/perfBaseline.js'

const scriptDir = path.dirname(fileURLToPath(import.meta.url))
const frontendDir = path.resolve(scriptDir, '..')
const distDir = path.join(frontendDir, 'dist')
const repoRoot = path.resolve(frontendDir, '..')
const reportDir = path.join(repoRoot, 'docs', 'worklogs')

async function walkFiles(dir) {
  const entries = await readdir(dir, { withFileTypes: true })
  const files = []

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      files.push(...(await walkFiles(fullPath)))
    } else if (entry.isFile()) {
      files.push(fullPath)
    }
  }

  return files
}

async function readAssets() {
  const files = await walkFiles(distDir)
  const assets = []

  for (const file of files) {
    const fileStat = await stat(file)
    assets.push({
      file: path.relative(distDir, file).replace(/\\/g, '/'),
      size: fileStat.size
    })
  }

  return assets
}

function createReportFilename() {
  const isoDate = new Date().toISOString().slice(0, 10)
  return `${isoDate}-frontend-perf-baseline.md`
}

async function main() {
  await readFile(path.join(distDir, 'index.html'))

  const assets = await readAssets()
  const summary = createPerfSummary(assets)
  const markdown = createMarkdownReport(summary)

  await mkdir(reportDir, { recursive: true })
  const reportPath = path.join(reportDir, createReportFilename())
  await writeFile(reportPath, markdown, 'utf-8')

  console.log(`Perf baseline saved: ${reportPath}`)
  console.log(`Assets: ${summary.fileCount}, Total: ${summary.totalBytes} B`)
}

main().catch((error) => {
  console.error('Failed to generate perf baseline report.')
  console.error(error)
  process.exitCode = 1
})
