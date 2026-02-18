function detectType(file) {
  if (file.endsWith('.js')) {
    return 'js'
  }
  if (file.endsWith('.css')) {
    return 'css'
  }
  if (file.endsWith('.html')) {
    return 'html'
  }
  return 'other'
}

function createTypeSummary() {
  return {
    js: { bytes: 0, files: 0 },
    css: { bytes: 0, files: 0 },
    html: { bytes: 0, files: 0 },
    other: { bytes: 0, files: 0 }
  }
}

export function formatBytes(bytes) {
  if (bytes < 1024) {
    return `${bytes} B`
  }

  return `${(bytes / 1024).toFixed(2)} KiB`
}

export function createPerfSummary(assets, options = {}) {
  const topN = options.topN ?? 5
  const byType = createTypeSummary()

  let totalBytes = 0
  for (const asset of assets) {
    const type = detectType(asset.file)
    byType[type].bytes += asset.size
    byType[type].files += 1
    totalBytes += asset.size
  }

  const topAssets = [...assets]
    .map((asset) => ({
      ...asset,
      type: detectType(asset.file)
    }))
    .sort((a, b) => b.size - a.size)
    .slice(0, topN)

  return {
    generatedAt: new Date().toISOString(),
    fileCount: assets.length,
    totalBytes,
    byType,
    topAssets
  }
}

export function createMarkdownReport(summary) {
  const lines = [
    '# Frontend Performance Baseline',
    '',
    `- Generated at: ${summary.generatedAt}`,
    `- Asset files: ${summary.fileCount}`,
    `- Total size: ${formatBytes(summary.totalBytes)} (${summary.totalBytes} B)`,
    '',
    '## Breakdown',
    '',
    '| Type | Files | Size |',
    '| --- | ---: | ---: |',
    `| JavaScript | ${summary.byType.js.files} | ${formatBytes(summary.byType.js.bytes)} |`,
    `| CSS | ${summary.byType.css.files} | ${formatBytes(summary.byType.css.bytes)} |`,
    `| HTML | ${summary.byType.html.files} | ${formatBytes(summary.byType.html.bytes)} |`,
    `| Other | ${summary.byType.other.files} | ${formatBytes(summary.byType.other.bytes)} |`,
    '',
    '## Top Assets',
    '',
    '| File | Type | Size |',
    '| --- | --- | ---: |'
  ]

  for (const asset of summary.topAssets) {
    lines.push(`| ${asset.file} | ${asset.type} | ${formatBytes(asset.size)} |`)
  }

  lines.push('')
  return lines.join('\n')
}
