import { nextTick } from 'vue'
import { describe, expect, it, beforeEach } from 'vitest'

import { useDraftCache } from '../useDraftCache'

describe('useDraftCache', () => {
  const key = 'test-draft-cache'

  beforeEach(() => {
    localStorage.clear()
  })

  it('loads cached draft into state', () => {
    localStorage.setItem(
      key,
      JSON.stringify({ requirement_text: 'cached content', budget: 12345 })
    )

    const { state, loadDraft } = useDraftCache(key, {
      requirement_text: '',
      budget: null
    })
    loadDraft()

    expect(state.value.requirement_text).toBe('cached content')
    expect(state.value.budget).toBe(12345)
  })

  it('syncs state changes to localStorage', async () => {
    const { state } = useDraftCache(key, {
      requirement_text: '',
      budget: null
    })
    state.value.requirement_text = 'new value'
    await nextTick()

    const saved = JSON.parse(localStorage.getItem(key))
    expect(saved.requirement_text).toBe('new value')
  })

  it('clearDraft resets cache and state', async () => {
    const { state, clearDraft } = useDraftCache(key, {
      requirement_text: '',
      budget: null
    })
    state.value.requirement_text = 'to be cleared'
    await nextTick()
    expect(localStorage.getItem(key)).toBeTruthy()

    clearDraft()
    await nextTick()

    expect(localStorage.getItem(key)).toBeNull()
    expect(state.value.requirement_text).toBe('')
    expect(state.value.budget).toBeNull()
  })

  it('reports hasDraft and restoredFromDraft state', () => {
    localStorage.setItem(key, JSON.stringify({ requirement_text: 'cached' }))
    const { hasDraft, restoredFromDraft, loadDraft, clearDraft } = useDraftCache(key, {
      requirement_text: ''
    })

    expect(hasDraft.value).toBe(true)
    expect(restoredFromDraft.value).toBe(false)

    loadDraft()
    expect(restoredFromDraft.value).toBe(true)

    clearDraft()
    expect(hasDraft.value).toBe(false)
    expect(restoredFromDraft.value).toBe(false)
  })

  it('persists auto-restore preference', () => {
    const { autoRestoreEnabled, setAutoRestoreEnabled } = useDraftCache(key, {
      requirement_text: ''
    })

    expect(autoRestoreEnabled.value).toBe(true)
    setAutoRestoreEnabled(false)
    expect(localStorage.getItem(`${key}:auto_restore`)).toBe('false')

    const next = useDraftCache(key, { requirement_text: '' })
    expect(next.autoRestoreEnabled.value).toBe(false)
  })

  it('respects auto-restore setting when restoring draft', () => {
    localStorage.setItem(key, JSON.stringify({ requirement_text: 'cached content' }))
    localStorage.setItem(`${key}:auto_restore`, 'false')

    const { state, maybeRestoreDraft, setAutoRestoreEnabled, restoredFromDraft } = useDraftCache(key, {
      requirement_text: ''
    })

    expect(maybeRestoreDraft()).toBe(false)
    expect(restoredFromDraft.value).toBe(false)
    expect(state.value.requirement_text).toBe('')

    setAutoRestoreEnabled(true)
    expect(maybeRestoreDraft()).toBe(true)
    expect(restoredFromDraft.value).toBe(true)
    expect(state.value.requirement_text).toBe('cached content')
  })
})
