<template>
  <div class="card shadow-sm border-0 mb-4">
    <div class="card-body p-4">
      <div class="d-flex align-items-center justify-content-between mb-3">
        <h2 class="h6 fw-bold mb-0">{{ t('contributions.recordPayment') }}</h2>
        <span v-if="target" class="badge text-bg-light border text-dark">{{ target.year }}</span>
      </div>

      <div v-if="target" class="border rounded-3 p-3 bg-light-subtle">
        <div class="fw-semibold">{{ memberLabel }}</div>
        <div class="small text-muted mb-3">
          {{ targetCopy }}
        </div>
        <form class="row g-3 align-items-end" @submit.prevent="submitPayment">
          <div class="col-md-4">
            <label for="finance-payment-amount" class="form-label small fw-medium">{{ t('common.amount') }} (EUR)</label>
            <input id="finance-payment-amount" v-model="form.amount" type="number" step="0.01" min="0.01" class="form-control" required />
          </div>
          <div class="col-md-4">
            <label for="finance-payment-method" class="form-label small fw-medium">{{ t('contributions.paymentMethod') }}</label>
            <select id="finance-payment-method" v-model="form.payment_method" class="form-select">
              <option value="cash">{{ t('contributions.cash') }}</option>
              <option value="bank_transfer">{{ t('contributions.bankTransfer') }}</option>
              <option value="card">{{ t('finance.card') }}</option>
              <option value="check">{{ t('contributions.check') }}</option>
              <option value="other">{{ t('finance.other') }}</option>
            </select>
          </div>
          <div class="col-md-4">
            <label for="finance-payment-reference" class="form-label small fw-medium">{{ t('finance.reference') }}</label>
            <input id="finance-payment-reference" v-model="form.reference" class="form-control" />
          </div>
          <div class="col-12 d-flex gap-2">
            <button class="btn btn-primary" type="submit" :disabled="saving">
              {{ saving ? t('common.saving') : t('contributions.recordPayment') }}
            </button>
            <button class="btn btn-outline-secondary" type="button" @click="emit('clear')">
              {{ t('finance.clear') }}
            </button>
          </div>
        </form>
      </div>
      <p v-else class="text-muted small mb-0">
        {{ t('finance.chooseContribution') }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { ContributionRecordResponse } from '@/api/contributions.api'
import { useLocaleStore } from '@/stores/locale.store'
import type { PaymentInput } from '../composables/useFinanceWorkspace'

const props = defineProps<{
  target: ContributionRecordResponse | null
  memberLabel: string
  targetCopy: string
  saving: boolean
  resetToken: number
}>()

const emit = defineEmits<{
  submit: [payload: PaymentInput]
  clear: []
}>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)

function defaultForm(balance = '') {
  return {
    amount: balance,
    payment_method: 'bank_transfer',
    reference: '',
  }
}

const form = ref(defaultForm())

watch(() => props.target, (target) => {
  if (target) form.value = defaultForm(target.balance)
})

watch(() => props.resetToken, () => {
  form.value = defaultForm()
})

function submitPayment() {
  emit('submit', { ...form.value })
}
</script>
