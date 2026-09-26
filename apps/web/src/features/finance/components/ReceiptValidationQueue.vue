<template>
  <section class="card shadow-sm border-0 mb-4 receipt-queue" data-testid="finance-receipt-validation-queue">
    <div class="card-body p-4">
      <div class="d-flex flex-column flex-md-row justify-content-between gap-2 mb-3">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary mb-1">{{ t('finance.receiptValidationKicker') }}</div>
          <h2 class="h5 fw-bold mb-1">{{ t('finance.receiptValidationTitle') }}</h2>
          <p class="small text-muted mb-0">{{ t('finance.receiptValidationLead') }}</p>
        </div>
        <span class="badge align-self-start text-bg-warning">{{ items.length }}</span>
      </div>
      <p v-if="items.length === 0" class="small text-muted mb-0">{{ t('finance.noReceiptDeclarations') }}</p>
      <div v-else class="vstack gap-2">
        <article v-for="item in items" :key="item.id" class="receipt-queue-item rounded-3 p-3">
          <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
            <div>
              <div class="fw-semibold">{{ labelFor(item) }}</div>
              <div class="small text-muted">{{ receiptIncomeTypeLabel(item.income_type) }} · {{ item.amount }} {{ item.currency }} · {{ item.declarant_role_code }} · {{ formatDate(item.received_at) }}</div>
              <div v-if="item.note" class="small mt-2">{{ item.note }}</div>
            </div>
            <div class="d-flex gap-2 align-items-start">
              <button class="btn btn-sm btn-success" type="button" @click="emit('decide', item, 'validated')">{{ t('finance.validateReceipt') }}</button>
              <button class="btn btn-sm btn-outline-danger" type="button" @click="emit('decide', item, 'rejected')">{{ t('finance.rejectReceipt') }}</button>
            </div>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { ContributionReceiptDeclarationResponse } from '@/api/contributions.api'
import { useLocaleStore } from '@/stores/locale.store'
import type { ReceiptDecisionAction } from '../composables/useFinanceWorkspace'
import { useFinanceFormatting } from '../composables/useFinanceFormatting'

defineProps<{
  items: ContributionReceiptDeclarationResponse[]
  labelFor: (item: ContributionReceiptDeclarationResponse) => string
}>()

const emit = defineEmits<{
  decide: [item: ContributionReceiptDeclarationResponse, action: ReceiptDecisionAction]
}>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const { receiptIncomeTypeLabel, formatDate } = useFinanceFormatting()
</script>

<style scoped>
.receipt-queue { border-top: 4px solid var(--bs-warning); }
.receipt-queue-item { background: var(--bs-warning-bg-subtle); border: 1px solid #f0d38a; }
</style>
