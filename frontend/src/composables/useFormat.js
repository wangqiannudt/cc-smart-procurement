import DOMPurify from 'dompurify'

/**
 * 格式化工具 composable
 * 提供文本格式化和 XSS 防护
 */
export function useFormat() {
  /**
   * 格式化消息内容（处理换行和粗体）- 使用 DOMPurify 防止 XSS
   */
  const formatContent = (content) => {
    if (!content) return ''
    const formatted = content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>')
    return DOMPurify.sanitize(formatted, {
      ALLOWED_TAGS: ['strong', 'br', 'b', 'i', 'em', 'u', 'a', 'p', 'span'],
      ALLOWED_ATTR: ['href', 'target', 'rel']
    })
  }

  /**
   * 格式化金额
   */
  const formatCurrency = (value, currency = '¥') => {
    if (typeof value !== 'number') return value
    return `${currency}${value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  /**
   * 格式化百分比
   */
  const formatPercent = (value, decimals = 1) => {
    if (typeof value !== 'number') return value
    return `${value.toFixed(decimals)}%`
  }

  /**
   * 格式化日期
   */
  const formatDate = (date, format = 'short') => {
    if (!date) return ''
    const d = new Date(date)
    if (format === 'short') {
      return d.toLocaleDateString('zh-CN')
    }
    return d.toLocaleString('zh-CN')
  }

  return {
    formatContent,
    formatCurrency,
    formatPercent,
    formatDate
  }
}
