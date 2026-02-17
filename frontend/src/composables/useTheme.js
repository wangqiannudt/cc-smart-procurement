/**
 * 主题切换 Composable
 * 支持三种风格：default(深邃星空)、nord(北欧冷调)、apple(极简高端)
 */
import { ref, watch, computed } from 'vue'

const STORAGE_KEY = 'procurement-theme'

// 主题配置
const themes = {
  default: {
    id: 'default',
    name: '深邃星空',
    description: '深色科技感，专业沉稳',
    mode: 'dark',
    preview: {
      bg: 'linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%)',
      color: '#409EFF',
      icon: '🌙'
    }
  },
  nord: {
    id: 'nord',
    name: '北欧冷调',
    description: '北极冰川蓝灰，专业冷静',
    mode: 'light',
    preview: {
      bg: 'linear-gradient(135deg, #ECEFF4 0%, #E5E9F0 100%)',
      color: '#5E81AC',
      icon: '❄️'
    }
  },
  apple: {
    id: 'apple',
    name: 'Apple',
    description: '极简高端，大量留白',
    mode: 'light',
    preview: {
      bg: '#FFFFFF',
      color: '#0066CC',
      icon: '🍎'
    }
  }
}

// 全局状态（单例）
const currentThemeId = ref('default')

// 初始化：从 localStorage 读取
const initTheme = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved && themes[saved]) {
      currentThemeId.value = saved
    }
  } catch (e) {
    console.warn('Failed to read theme from localStorage:', e)
  }
  applyTheme(currentThemeId.value)
}

// 应用主题到 DOM
const applyTheme = (themeId) => {
  const html = document.documentElement
  // 设置主题属性（所有主题都需要设置，包括 default）
  html.setAttribute('data-theme', themeId)
}

// 保存到 localStorage
const saveTheme = (themeId) => {
  try {
    localStorage.setItem(STORAGE_KEY, themeId)
  } catch (e) {
    console.warn('Failed to save theme to localStorage:', e)
  }
}

export function useTheme() {
  // 初始化（只执行一次）
  if (currentThemeId.value === 'default' && !document.documentElement.hasAttribute('data-theme-init')) {
    document.documentElement.setAttribute('data-theme-init', 'true')
    initTheme()
  }

  // 当前主题对象
  const currentTheme = computed(() => themes[currentThemeId.value] || themes.default)

  // 是否为深色模式
  const isDark = computed(() => currentTheme.value.mode === 'dark')

  // 是否为浅色模式
  const isLight = computed(() => currentTheme.value.mode === 'light')

  // 可用主题列表
  const availableThemes = computed(() => Object.values(themes))

  // 切换主题
  const setTheme = (themeId) => {
    if (!themes[themeId]) {
      console.warn(`Unknown theme: ${themeId}`)
      return
    }
    currentThemeId.value = themeId
    applyTheme(themeId)
    saveTheme(themeId)
  }

  // 循环切换主题
  const toggleTheme = () => {
    const themeKeys = Object.keys(themes)
    const currentIndex = themeKeys.indexOf(currentThemeId.value)
    const nextIndex = (currentIndex + 1) % themeKeys.length
    setTheme(themeKeys[nextIndex])
  }

  return {
    // 状态
    currentThemeId,
    currentTheme,
    isDark,
    isLight,
    availableThemes,

    // 方法
    setTheme,
    toggleTheme,
    themes
  }
}

// 导出主题配置供其他模块使用
export { themes }
