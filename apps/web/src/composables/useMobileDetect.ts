import { ref, onMounted, onUnmounted } from 'vue'

const BREAKPOINT_MOBILE = 768

export function useMobileDetect() {
  const isMobile = ref(false)

  let debounceTimer: ReturnType<typeof setTimeout> | null = null

  function check() {
    isMobile.value = window.innerWidth < BREAKPOINT_MOBILE
  }

  function onResize() {
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
    debounceTimer = setTimeout(check, 80)
  }

  onMounted(() => {
    check()
    window.addEventListener('resize', onResize)
    window.addEventListener('orientationchange', onResize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', onResize)
    window.removeEventListener('orientationchange', onResize)
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
  })

  return {
    isMobile,
    isDesktop: () => window.innerWidth >= BREAKPOINT_MOBILE,
    breakpoint: BREAKPOINT_MOBILE,
  }
}
