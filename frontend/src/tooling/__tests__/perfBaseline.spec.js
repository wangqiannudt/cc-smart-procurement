import { describe, expect, it } from 'vitest'

import { createPerfSummary, formatBytes } from '../perfBaseline'

describe('performance baseline summary', () => {
  it('aggregates bundle sizes by type and total', () => {
    const summary = createPerfSummary([
      { file: 'assets/main-aaa.js', size: 2048 },
      { file: 'assets/vendor-bbb.js', size: 4096 },
      { file: 'assets/index-ccc.css', size: 1024 },
      { file: 'index.html', size: 512 },
      { file: 'assets/logo.svg', size: 256 }
    ])

    expect(summary.fileCount).toBe(5)
    expect(summary.totalBytes).toBe(7936)
    expect(summary.byType.js.bytes).toBe(6144)
    expect(summary.byType.css.bytes).toBe(1024)
    expect(summary.byType.html.bytes).toBe(512)
    expect(summary.byType.other.bytes).toBe(256)
  })

  it('sorts top assets by size', () => {
    const summary = createPerfSummary(
      [
        { file: 'assets/a.js', size: 10 },
        { file: 'assets/c.js', size: 30 },
        { file: 'assets/b.css', size: 20 }
      ],
      { topN: 2 }
    )

    expect(summary.topAssets).toEqual([
      { file: 'assets/c.js', size: 30, type: 'js' },
      { file: 'assets/b.css', size: 20, type: 'css' }
    ])
  })

  it('formats bytes to kibibytes', () => {
    expect(formatBytes(1536)).toBe('1.50 KiB')
  })
})
