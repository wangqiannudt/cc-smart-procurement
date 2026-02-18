import { ref, watch } from 'vue'

export function useDraftCache(storageKey, initialValue) {
  const autoRestoreKey = `${storageKey}:auto_restore`
  const state = ref({ ...initialValue })
  const hasDraft = ref(!!localStorage.getItem(storageKey))
  const restoredFromDraft = ref(false)
  const autoRestoreEnabled = ref(localStorage.getItem(autoRestoreKey) !== 'false')
  const skipNextPersist = ref(false)

  const loadDraft = () => {
    try {
      const raw = localStorage.getItem(storageKey)
      if (!raw) {
        restoredFromDraft.value = false
        return false
      }
      const parsed = JSON.parse(raw)
      state.value = { ...initialValue, ...parsed }
      hasDraft.value = true
      restoredFromDraft.value = true
      return true
    } catch {
      state.value = { ...initialValue }
      hasDraft.value = false
      restoredFromDraft.value = false
      return false
    }
  }

  const clearDraft = () => {
    localStorage.removeItem(storageKey)
    skipNextPersist.value = true
    hasDraft.value = false
    state.value = { ...initialValue }
    restoredFromDraft.value = false
  }

  const setAutoRestoreEnabled = (enabled) => {
    const value = !!enabled
    autoRestoreEnabled.value = value
    localStorage.setItem(autoRestoreKey, String(value))
  }

  const maybeRestoreDraft = () => {
    if (!autoRestoreEnabled.value || !hasDraft.value) {
      restoredFromDraft.value = false
      return false
    }
    return loadDraft()
  }

  watch(
    state,
    (value) => {
      if (skipNextPersist.value) {
        skipNextPersist.value = false
        return
      }
      localStorage.setItem(storageKey, JSON.stringify(value))
      hasDraft.value = true
    },
    { deep: true }
  )

  return {
    state,
    hasDraft,
    restoredFromDraft,
    autoRestoreEnabled,
    loadDraft,
    maybeRestoreDraft,
    clearDraft,
    setAutoRestoreEnabled
  }
}
