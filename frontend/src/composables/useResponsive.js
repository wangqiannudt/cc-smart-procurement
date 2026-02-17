import { ref, onMounted, onUnmounted } from 'vue'

/**
 * 响应式布局 composable
 * 提供屏幕尺寸检测和移动端判断
 */
export function useResponsive(breakpoint = 768) {
  const isMobile = ref(false)
  const screenWidth = ref(window.innerWidth)

  const checkScreenSize = () => {
    screenWidth.value = window.innerWidth
    isMobile.value = window.innerWidth < breakpoint
  }

  onMounted(() => {
    checkScreenSize()
    window.addEventListener('resize', checkScreenSize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', checkScreenSize)
  })

  return {
    isMobile,
    screenWidth
  }
}
