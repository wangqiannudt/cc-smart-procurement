import { describe, expect, it, vi } from 'vitest'

import { createEchartsLoader } from '../echartsLazyLoader'

describe('echarts lazy loader', () => {
  it('loads runtime only once for concurrent calls', async () => {
    const echartsMock = { init: vi.fn() }
    const importRuntime = vi.fn().mockResolvedValue(echartsMock)
    const loadEcharts = createEchartsLoader(importRuntime)

    const [first, second] = await Promise.all([loadEcharts(), loadEcharts()])

    expect(importRuntime).toHaveBeenCalledTimes(1)
    expect(first).toBe(echartsMock)
    expect(second).toBe(echartsMock)
  })

  it('retries after previous load failure', async () => {
    const echartsMock = { init: vi.fn() }
    const importRuntime = vi
      .fn()
      .mockRejectedValueOnce(new Error('runtime load failed'))
      .mockResolvedValueOnce(echartsMock)
    const loadEcharts = createEchartsLoader(importRuntime)

    await expect(loadEcharts()).rejects.toThrow('runtime load failed')
    await expect(loadEcharts()).resolves.toBe(echartsMock)
    expect(importRuntime).toHaveBeenCalledTimes(2)
  })
})
