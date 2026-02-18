import { describe, expect, it, beforeEach, vi } from 'vitest'

vi.mock('../../api', () => {
  return {
    apiEndpoints: {
      runAnalysisWorkflow: vi.fn(),
      getAnalysisHistory: vi.fn(),
      reuseAnalysisHistory: vi.fn()
    }
  }
})

import { apiEndpoints } from '../../api'
import { useAnalysisWorkflow } from '../useAnalysisWorkflow'

describe('useAnalysisWorkflow', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('runWorkflow stores result on success', async () => {
    const mockData = { summary: { overall_recommendation: 'ok' }, history_id: 1 }
    apiEndpoints.runAnalysisWorkflow.mockResolvedValue({ data: mockData })

    const { runWorkflow, loading, result } = useAnalysisWorkflow()
    const output = await runWorkflow({ product_keyword: '服务器' })

    expect(apiEndpoints.runAnalysisWorkflow).toHaveBeenCalledTimes(1)
    expect(output).toEqual(mockData)
    expect(result.value).toEqual(mockData)
    expect(loading.value).toBe(false)
  })

  it('runWorkflow sets error on failure', async () => {
    apiEndpoints.runAnalysisWorkflow.mockRejectedValue(new Error('workflow failed'))
    const { runWorkflow, error, loading } = useAnalysisWorkflow()

    await expect(runWorkflow({})).rejects.toThrow('workflow failed')
    expect(error.value).toBe('workflow failed')
    expect(loading.value).toBe(false)
  })

  it('fetchHistory updates history and total', async () => {
    apiEndpoints.getAnalysisHistory.mockResolvedValue({
      data: [{ id: 11 }, { id: 12 }],
      total: 2
    })

    const { fetchHistory, history, total } = useAnalysisWorkflow()
    await fetchHistory(1, 10)

    expect(history.value).toHaveLength(2)
    expect(total.value).toBe(2)
  })

  it('reuseHistory updates result', async () => {
    apiEndpoints.reuseAnalysisHistory.mockResolvedValue({
      data: { history_id: 22, summary: { overall_recommendation: 'reused' } }
    })

    const { reuseHistory, result } = useAnalysisWorkflow()
    const reused = await reuseHistory(11)

    expect(apiEndpoints.reuseAnalysisHistory).toHaveBeenCalledWith(11)
    expect(reused.history_id).toBe(22)
    expect(result.value.history_id).toBe(22)
  })
})
