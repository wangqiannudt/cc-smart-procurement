import { ref } from 'vue'
import { apiEndpoints } from '../api'

export function useAnalysisWorkflow() {
  const loading = ref(false)
  const error = ref('')
  const result = ref(null)
  const history = ref([])
  const total = ref(0)

  const runWorkflow = async (payload) => {
    loading.value = true
    error.value = ''
    try {
      const res = await apiEndpoints.runAnalysisWorkflow(payload)
      result.value = res.data
      return res.data
    } catch (e) {
      error.value = e.message || '分析失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchHistory = async (page = 1, pageSize = 10) => {
    try {
      const res = await apiEndpoints.getAnalysisHistory({ page, page_size: pageSize })
      history.value = res.data || []
      total.value = res.total || 0
      return res
    } catch (e) {
      error.value = e.message || '获取历史记录失败'
      throw e
    }
  }

  const reuseHistory = async (historyId) => {
    loading.value = true
    error.value = ''
    try {
      const res = await apiEndpoints.reuseAnalysisHistory(historyId)
      result.value = res.data
      return res.data
    } catch (e) {
      error.value = e.message || '复用分析失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  const clearResult = () => {
    result.value = null
  }

  return {
    loading,
    error,
    result,
    history,
    total,
    runWorkflow,
    fetchHistory,
    reuseHistory,
    clearResult
  }
}
