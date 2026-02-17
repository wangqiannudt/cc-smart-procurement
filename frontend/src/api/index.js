import axios from 'axios'
import { ElLoading, ElMessage } from 'element-plus'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 全局 loading 实例
let loadingInstance = null
let requestCount = 0

// 显示 loading
const showLoading = () => {
  if (requestCount === 0) {
    loadingInstance = ElLoading.service({
      lock: true,
      text: '加载中...',
      background: 'rgba(15, 15, 26, 0.85)',
      spinner: 'el-icon-loading'
    })
  }
  requestCount++
}

// 隐藏 loading
const hideLoading = () => {
  requestCount--
  if (requestCount <= 0) {
    requestCount = 0
    if (loadingInstance) {
      loadingInstance.close()
      loadingInstance = null
    }
  }
}

// 显示错误提示
const showError = (message) => {
  ElMessage({
    type: 'error',
    message: message,
    duration: 4000,
    showClose: true
  })
}

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 对于非静默请求，显示 loading
    if (!config.silent) {
      showLoading()
    }
    return config
  },
  (error) => {
    hideLoading()
    showError('请求发送失败，请检查网络连接')
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    hideLoading()

    // 检查业务状态
    const { data } = response
    if (data.success === false) {
      const errorMsg = data.error || data.message || '操作失败'
      if (!response.config.silent) {
        showError(errorMsg)
      }
      return Promise.reject(new Error(errorMsg))
    }

    return data
  },
  (error) => {
    hideLoading()

    // 根据错误类型显示不同提示
    let errorMessage = '请求失败，请稍后重试'

    if (error.response) {
      // 服务器返回错误
      const { status, data } = error.response

      switch (status) {
        case 400:
          errorMessage = data?.detail || '请求参数错误'
          break
        case 401:
          errorMessage = '未授权，请重新登录'
          break
        case 403:
          errorMessage = '没有权限访问'
          break
        case 404:
          errorMessage = '请求的资源不存在'
          break
        case 500:
          errorMessage = data?.detail || '服务器内部错误'
          break
        case 502:
        case 503:
          errorMessage = '服务暂时不可用，请稍后重试'
          break
        default:
          errorMessage = data?.detail || `请求失败 (${status})`
      }
    } else if (error.code === 'ECONNABORTED') {
      errorMessage = '请求超时，请检查网络后重试'
    } else if (error.message?.includes('Network Error')) {
      errorMessage = '网络连接失败，请检查您的网络'
    }

    if (!error.config?.silent) {
      showError(errorMessage)
    }

    return Promise.reject(error)
  }
)

// 导出带便捷方法的 API 对象
export const request = {
  get: (url, params, config = {}) => api.get(url, { params, ...config }),
  post: (url, data, config = {}) => api.post(url, data, config),
  put: (url, data, config = {}) => api.put(url, data, config),
  delete: (url, config = {}) => api.delete(url, config),
  upload: (url, formData, config = {}) => {
    return api.post(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

// API 端点定义
export const apiEndpoints = {
  // 健康检查
  health: () => request.get('/health'),

  // 需求审查
  reviewRequirements: (formData) => request.upload('/review-requirements', formData),

  // 价格参考
  getPriceReference: (params) => request.get('/price-reference', params),
  analyzePrice: (data) => request.post('/price-reference/analyze', data),

  // 合同分析
  analyzeContract: (formData) => request.upload('/contract-analysis', formData),

  // 聊天
  chat: (data) => request.post('/chat/conversation', data),
  procurementAnalysis: (data) => request.post('/chat/procurement-analysis', data),
  priceRecommendation: (data) => request.post('/chat/price-recommendation', data)
}

export default api
