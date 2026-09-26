<template>
  <section class="card shadow-sm border-0 mb-4 custody-workspace" data-testid="finance-cash-custody-queue">
    <div class="card-body p-4">
      <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-3">
        <div>
          <div class="text-uppercase small fw-semibold text-primary mb-1">{{ t('receipt.custodyKicker') }}</div>
          <h2 class="h5 fw-bold mb-1">{{ t('receipt.cashPending') }}</h2>
          <p class="small text-muted mb-0">{{ t('receipt.custodyLead') }}</p>
        </div>
        <span class="badge rounded-pill text-bg-primary align-self-start px-3 py-2">{{ items.length }} {{ t('finance.itemsCountSuffix') }}</span>
      </div>
      <div class="vstack gap-3">
        <article v-for="item in items" :key="item.id" class="custody-card rounded-4 p-3 p-md-4" :class="item.cash_handover_status === 'handover_reported' ? 'custody-card-reported' : 'custody-card-pending'">
          <div class="d-flex flex-column flex-lg-row justify-content-between gap-3">
            <div class="flex-grow-1">
              <div class="d-flex flex-wrap align-items-center gap-2 mb-2"><span class="fw-bold">{{ labelFor(item) }}</span><span class="badge rounded-pill" :class="item.cash_handover_status === 'handover_reported' ? 'text-bg-info' : 'text-bg-warning'">{{ handoverStatusLabel(item.cash_handover_status) }}</span></div>
              <div class="small text-muted mb-3">{{ receiptIncomeTypeLabel(item.income_type) }} · {{ item.amount }} {{ item.currency }} · {{ t('receipt.receivedBy') }} {{ item.declarant_role_code }}</div>
              <div class="custody-meta-grid small">
                <div><span>{{ t('receipt.currentReminder') }}</span><strong>{{ item.handover_reminder_days || 2 }} {{ t('receipt.days') }}</strong></div>
                <div><span>{{ t('receipt.dueDate') }}</span><strong>{{ formatDate(item.handover_due_at) }}</strong></div>
                <div v-if="item.handover_method"><span>{{ t('receipt.handoverMethod') }}</span><strong>{{ item.handover_method === 'bank_transfer' ? t('receipt.handoverTransfer') : t('receipt.handoverCash') }}</strong></div>
              </div>
            </div>
            <div class="custody-actions align-self-lg-center">
              <button class="btn btn-outline-primary" type="button" @click="emit('decide', item, 'reminder')"><i class="bi bi-clock-history me-1"></i>{{ t('receipt.changeReminder') }}</button>
              <button class="btn btn-primary" type="button" @click="emit('decide', item, 'close')"><i class="bi bi-safe2 me-1"></i>{{ t('receipt.closeInTreasury') }}</button>
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
import type { CustodyDecisionAction } from '../composables/useFinanceWorkspace'
import { useFinanceFormatting } from '../composables/useFinanceFormatting'

defineProps<{
  items: ContributionReceiptDeclarationResponse[]
  labelFor: (item: ContributionReceiptDeclarationResponse) => string
}>()

const emit = defineEmits<{
  decide: [item: ContributionReceiptDeclarationResponse, action: CustodyDecisionAction]
}>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const { handoverStatusLabel, receiptIncomeTypeLabel, formatDate } = useFinanceFormatting()
</script>

<style scoped>
.custody-workspace { border-top: 4px solid var(--bs-primary); background: linear-gradient(135deg, #fff 0%, #f5f9ff 100%); }
.custody-card { border: 1px solid #d9e3f2; box-shadow: 0 0.35rem 1.1rem rgba(24, 62, 111, 0.07); }
.custody-card-pending { background: linear-gradient(135deg, #fffdf6 0%, #fff 58%); border-left: 5px solid var(--bs-warning); }
.custody-card-reported { background: linear-gradient(135deg, #f2fbff 0%, #fff 58%); border-left: 5px solid var(--bs-info); }
.custody-meta-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.75rem; }
.custody-meta-grid > div { display: grid; gap: 0.15rem; padding: 0.65rem 0.75rem; border-radius: 0.75rem; background: rgba(255, 255, 255, 0.82); border: 1px solid #e3e9f2; }
.custody-meta-grid span { color: var(--bs-secondary); }
.custody-actions { display: grid; gap: 0.5rem; min-width: 12.5rem; }

@media (max-width: 767.98px) {
  .custody-meta-grid { grid-template-columns: 1fr; }
  .custody-actions { width: 100%; min-width: 0; }
  .custody-actions .btn { min-height: 44px; }
}
</style>
