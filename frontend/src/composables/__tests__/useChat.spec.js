import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../../api', () => ({
  apiEndpoints: {
    chat: vi.fn()
  }
}))

import { apiEndpoints } from '../../api'
import { useChat } from '../useChat'

describe('useChat', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('initSession should prepare local welcome without remote chat call', async () => {
    const { initSession, messages, sessionId, loading } = useChat()

    await initSession()

    expect(apiEndpoints.chat).not.toHaveBeenCalled()
    expect(loading.value).toBe(false)
    expect(sessionId.value).toBeTruthy()
    expect(messages.value).toHaveLength(1)
    expect(messages.value[0].role).toBe('assistant')
    expect(messages.value[0].content).toContain('AI助手')
  })
})
