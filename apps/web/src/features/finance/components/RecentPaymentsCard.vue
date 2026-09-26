<template>
  <div class="card shadow-sm border-0 mb-4">
    <div class="card-body p-4">
      <div class="d-flex align-items-center justify-content-between mb-3">
        <h2 class="h6 fw-bold mb-0">{{ t('finance.recentPayments') }}</h2>
        <span class="badge text-bg-light border text-dark">{{ payments.length }} {{ t('finance.itemsCountSuffix') }}</span>
      </div>

      <div v-if="payments.length === 0" class="text-muted small mb-0">
        {{ t('finance.noPayments') }}
      </div>

      <div v-else class="list-group list-group-flush">
        <div v-for="payment in payments" :key="payment.id" class="list-group-item px-0">
          <div class="d-flex justify-content-between gap-3">
            <div>
              <div class="fw-medium">{{ labelFor(payment.contribution_record_id) }}</div>
              <div class="small text-muted">
                {{ payment.amount }} EUR · {{ formatPaymentMethod(payment.payment_method) }}
              </div>
            </div>
            <div class="text-end small text-muted">
              <div>{{ formatDate(payment.paid_at) }}</div>
              <div>{{ payment.reference || t('finance.noReference') }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PaymentRecordResponse } from '@/api/contributions.api'
import { useLocaleStore } from '@/stores/locale.store'
import { useFinanceFormatting } from '../composables/useFinanceFormatting'

defineProps<{
  payments: PaymentRecordResponse[]
  labelFor: (contributionId: string) => string
}>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const { formatDate, formatPaymentMethod } = useFinanceFormatting()
</script>
