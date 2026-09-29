<template>
  <div class="card shadow-sm border-0 mb-4">
    <div class="card-body p-4">
      <div class="d-flex align-items-center justify-content-between gap-3 mb-3">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary-emphasis mb-1">
            {{ copy.tenantSnapshot }}
          </div>
          <h2 class="h6 fw-bold mb-0">{{ copy.liveUsageSignals }}</h2>
        </div>
        <button class="btn btn-outline-secondary btn-sm" type="button" @click="emit('refresh')" :disabled="loading">
          {{ copy.refresh }}
        </button>
      </div>

      <div class="row g-3">
        <div v-for="metric in metrics" :key="metric.label" class="col-6">
          <div class="metric-card h-100">
            <div class="small text-muted">{{ metric.label }}</div>
            <div class="fs-4 fw-bold lh-1 mb-1">{{ metric.value }}</div>
            <div class="small text-secondary">{{ metric.hint }}</div>
          </div>
        </div>
      </div>

      <hr class="my-4" />

      <div class="small text-uppercase fw-semibold text-secondary mb-2">
        {{ copy.currentTenant }}
      </div>
      <div class="vstack gap-2 small">
        <div class="d-flex justify-content-between gap-2">
          <span class="text-muted">{{ copy.tenant }}</span>
          <span class="fw-semibold text-end">{{ tenantName }}</span>
        </div>
        <div class="d-flex justify-content-between gap-2">
          <span class="text-muted">{{ copy.role }}</span>
          <span class="fw-semibold text-end">
            {{ rolesLabel || '—' }}
          </span>
        </div>
        <div class="d-flex justify-content-between gap-2">
          <span class="text-muted">{{ copy.checklistComplete }}</span>
          <span class="fw-semibold text-end">
            {{ completedCount }} / {{ checklistLength }}
          </span>
        </div>
        <div class="d-flex justify-content-between gap-2">
          <span class="text-muted">{{ copy.lastRefresh }}</span>
          <span class="fw-semibold text-end">
            {{ lastRefreshedAt ? formatDateTime(lastRefreshedAt) : copy.justLoaded }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { OnboardingSummaryMetric } from '@/composables/useTenantOnboarding'
import type { DashboardCopy } from '../composables/useDashboardCopy'

defineProps<{
  copy: DashboardCopy
  metrics: OnboardingSummaryMetric[]
  tenantName: string
  rolesLabel: string
  completedCount: number
  checklistLength: number
  lastRefreshedAt: string | null
  loading: boolean
}>()

const emit = defineEmits<{ refresh: [] }>()

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}
</script>

<style scoped>
.metric-card {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 0.95rem;
  padding: 0.9rem;
  background: #fff;
}
</style>
