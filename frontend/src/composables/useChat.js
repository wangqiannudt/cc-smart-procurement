import { ref, nextTick } from 'vue'
import { apiEndpoints } from '../api'
import { useFormat } from './useFormat'

/**
 * AI 对话 composable
 * 封装对话逻辑，支持多会话管理
 */
export function useChat() {
  const messages = ref([])
  const loading = ref(false)
  const sessionId = ref(null)
  const messagesContainer = ref(null)
  const { formatContent } = useFormat()

  /**
   * 初始化会话
   */
  const initSession = async () => {
    try {
      const result = await apiEndpoints.chat({ message: '你好' })
      if (result.success && result.data.session_id) {
        sessionId.value = result.data.session_id
        messages.value.push({
          role: 'assistant',
          content: result.data.response,
          time: new Date().toLocaleTimeString()
        })
      }
    } catch (e) {
      console.error('初始化会话失败:', e)
      messages.value.push({
        role: 'assistant',
        content: '您好！我是智慧采购系统的AI助手，有什么可以帮您的吗？',
        time: new Date().toLocaleTimeString()
      })
    }
  }

  /**
   * 发送消息
   */
  const sendMessage = async (userMessage) => {
    if (!userMessage.trim() || loading.value) return

    // 添加用户消息
    messages.value.push({
      role: 'user',
      content: userMessage,
      time: new Date().toLocaleTimeString()
    })

    scrollToBottom()
    loading.value = true

    try {
      const requestData = { message: userMessage }
      if (sessionId.value) {
        requestData.session_id = sessionId.value
      }

      const result = await apiEndpoints.chat(requestData)

      if (result.success) {
        sessionId.value = result.data.session_id
        messages.value.push({
          role: 'assistant',
          content: result.data.response,
          time: new Date().toLocaleTimeString(),
          actions: result.data.suggested_actions || []
        })
      } else {
        messages.value.push({
          role: 'assistant',
          content: '抱歉，处理您的请求时出现了问题，请稍后重试。',
          time: new Date().toLocaleTimeString()
        })
      }
    } catch (e) {
      console.error('发送消息失败:', e)
      messages.value.push({
        role: 'assistant',
        content: '网络连接出现问题，请检查您的网络后重试。',
        time: new Date().toLocaleTimeString()
      })
    } finally {
      loading.value = false
      scrollToBottom()
    }
  }

  /**
   * 滚动到底部
   */
  const scrollToBottom = () => {
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    })
  }

  /**
   * 清空对话
   */
  const clearChat = async () => {
    messages.value = []
    sessionId.value = null
    await initSession()
  }

  return {
    messages,
    loading,
    sessionId,
    messagesContainer,
    formatContent,
    initSession,
    sendMessage,
    scrollToBottom,
    clearChat
  }
}
