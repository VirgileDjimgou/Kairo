import { ref, type Ref } from 'vue'

export type RecoveryLoader = () => Promise<void>

export type RecoveryState = {
  loading: Ref<boolean>
  error: Ref<string | null>
  isRecovering: Ref<boolean>
  run: (loader: RecoveryLoader) => Promise<void>
  retry: (loader: RecoveryLoader) => Promise<void>
  clearError: () => void
}

/**
 * Shared loading/recovery contract for role workspaces.
 *
 * Keeps error handling consistent across member and office surfaces: a failed
 * load is shown with a localized recovery hint and a retry control that re-runs
 * the same guarded backend loader without leaving the workspace.
 */
export function useRecoveryState(): RecoveryState {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isRecovering = ref(false)

  async function run(loader: RecoveryLoader) {
    loading.value = true
    error.value = null
    try {
      await loader()
    } catch (err: any) {
      error.value =
        err?.response?.data?.detail ||
        (err instanceof Error ? err.message : null)
    } finally {
      loading.value = false
    }
  }

  async function retry(loader: RecoveryLoader) {
    isRecovering.value = true
    error.value = null
    try {
      await loader()
    } catch (err: any) {
      error.value =
        err?.response?.data?.detail ||
        (err instanceof Error ? err.message : null)
    } finally {
      isRecovering.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  return { loading, error, isRecovering, run, retry, clearError }
}
