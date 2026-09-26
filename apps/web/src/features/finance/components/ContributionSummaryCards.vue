<template>
  <div v-if="summary" class="row g-3 mb-4">
    <div class="col-md-4">
      <div class="card shadow-sm border-0 bg-primary-subtle">
        <div class="card-body text-center py-3">
          <div class="text-muted small">{{ t('contributions.expected') }}</div>
          <div class="fw-bold fs-4">{{ summary.total_expected }} EUR</div>
        </div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card shadow-sm border-0 bg-success-subtle">
        <div class="card-body text-center py-3">
          <div class="text-muted small">{{ t('contributions.paid') }}</div>
          <div class="fw-bold fs-4">{{ summary.total_paid }} EUR</div>
        </div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card shadow-sm border-0" :class="Number(summary.total_balance) > 0 ? 'bg-warning-subtle' : 'bg-success-subtle'">
        <div class="card-body text-center py-3">
          <div class="text-muted small">{{ t('finance.outstandingBalance') }}</div>
          <div class="fw-bold fs-4">{{ summary.total_balance }} EUR</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ContributionSummary } from '@/api/contributions.api'
import { useLocaleStore } from '@/stores/locale.store'

defineProps<{ summary: ContributionSummary | null }>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
</script>
