<template>
  <section class="card shadow-sm border-0 mb-4" data-testid="finance-period-card">
    <div class="card-body p-3 p-lg-4 d-flex flex-column flex-lg-row justify-content-between align-items-lg-center gap-3">
      <div class="d-flex align-items-center gap-3">
        <span class="period-icon" aria-hidden="true">
          <i class="bi" :class="isClosed ? 'bi-lock-fill' : 'bi-unlock'"></i>
        </span>
        <div>
          <div class="text-uppercase small fw-semibold text-secondary-emphasis">
            {{ t('finance.exercise') }} {{ year }}
          </div>
          <div class="d-flex align-items-center gap-2">
            <span
              class="badge"
              :class="isClosed ? 'text-bg-danger' : 'text-bg-success'"
              data-testid="finance-period-status"
            >
              {{ isClosed ? t('finance.exerciseClosed') : t('finance.exerciseOpen') }}
            </span>
            <span v-if="isClosed" class="small text-muted">
              {{ t('finance.periodClosedNotice') }}
            </span>
          </div>
        </div>
      </div>
      <div class="d-flex flex-wrap gap-2 align-items-center">
        <span v-if="errorMessage" class="small text-danger" role="alert">{{ errorMessage }}</span>
        <button
          v-if="canClose && !isClosed"
          class="btn btn-outline-danger btn-sm"
          type="button"
          :disabled="loading || closing"
          data-testid="finance-period-close"
          @click="closePeriod"
        >
          <span v-if="closing" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
          {{ t('finance.closeExercise') }}
        </button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { closeFinancePeriod, getFinancePeriod } from '@/api/contributions.api'
import { useLocaleStore } from '@/stores/locale.store'

const props = defineProps<{
  year: number
  canClose?: boolean
}>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)

const status = ref<'open' | 'closed'>('open')
const loading = ref(false)
const closing = ref(false)
const errorMessage = ref('')

const isClosed = computed(() => status.value === 'closed')

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const period = await getFinancePeriod(props.year)
    status.value = period.status
  } catch {
    errorMessage.value = t('finance.periodCloseFailed')
  } finally {
    loading.value = false
  }
}

async function closePeriod() {
  const confirmed = window.confirm(
    t('finance.closeExerciseConfirm').replace('{year}', String(props.year)),
  )
  if (!confirmed) return
  closing.value = true
  errorMessage.value = ''
  try {
    const period = await closeFinancePeriod(props.year)
    status.value = period.status
  } catch {
    errorMessage.value = t('finance.periodCloseFailed')
  } finally {
    closing.value = false
  }
}

watch(() => props.year, load)
onMounted(load)

defineExpose({ reload: load })
</script>

<style scoped>
.period-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  background: var(--bs-secondary-bg);
  font-size: 1.1rem;
}
</style>
