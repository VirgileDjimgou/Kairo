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
      <div v-if="receiptError" class="alert alert-warning small py-2 mb-2" role="alert">
        {{ receiptError }}
      </div>

      <div v-if="payments.length > 0" class="list-group list-group-flush">
        <div v-for="payment in payments" :key="payment.id" class="list-group-item px-0">
          <div class="d-flex justify-content-between gap-3">
            <div>
              <div class="fw-medium">{{ labelFor(payment.contribution_record_id) }}</div>
              <div class="small text-muted">
                {{ payment.amount }} {{ currency }} · {{ formatPaymentMethod(payment.payment_method) }}
              </div>
              <div v-if="payment.receipt_number" class="small text-muted">
                {{ t('finance.receiptNumber') }} {{ payment.receipt_number }}
                <button
                  v-if="!payment.reversed_at"
                  class="btn btn-link btn-sm p-0 ms-1"
                  type="button"
                  @click="downloadReceipt(payment)"
                >
                  {{ t('finance.downloadReceiptPdf') }}
                </button>
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
import { ref } from 'vue'
import { downloadPaymentReceipt, type PaymentRecordResponse } from '@/api/contributions.api'
import { useLocaleStore } from '@/stores/locale.store'
import { useFinanceFormatting } from '../composables/useFinanceFormatting'

defineProps<{
  payments: PaymentRecordResponse[]
  labelFor: (contributionId: string) => string
}>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const { formatDate, formatPaymentMethod, currency } = useFinanceFormatting()
const receiptError = ref('')

async function downloadReceipt(payment: PaymentRecordResponse) {
  receiptError.value = ''
  try {
    const blob = await downloadPaymentReceipt(payment.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `quittance-${payment.receipt_number || payment.id}.pdf`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch {
    receiptError.value = t('finance.uploadFailed')
  }
}
</script>
