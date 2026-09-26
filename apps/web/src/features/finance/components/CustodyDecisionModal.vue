<template>
  <div v-if="decision" class="modal d-block" tabindex="-1" role="dialog" aria-modal="true">
    <div class="modal-dialog modal-dialog-centered"><div class="modal-content shadow border-0">
      <div class="modal-header"><div><div class="text-uppercase small fw-semibold text-primary">{{ t('receipt.custodyKicker') }}</div><h2 class="modal-title fs-5">{{ decision.action === 'reminder' ? t('receipt.changeReminder') : t('receipt.closeInTreasury') }}</h2></div><button class="btn-close" type="button" @click="emit('close')"></button></div>
      <div class="modal-body vstack gap-3"><div class="rounded-3 bg-light p-3"><div class="fw-semibold">{{ labelFor(decision.item) }}</div><div class="small text-muted">{{ decision.item.amount }} {{ decision.item.currency }} · {{ handoverStatusLabel(decision.item.cash_handover_status) }}</div></div>
        <template v-if="decision.action === 'reminder'"><label class="form-label mb-0" for="custody-reminder-days">{{ t('receipt.reminderDays') }}</label><select id="custody-reminder-days" v-model.number="reminderDays" class="form-select"><option v-for="day in 7" :key="day" :value="day">{{ day }} {{ t('receipt.days') }}</option></select><p class="small text-muted mb-0">{{ t('receipt.reminderUpdateHint') }}</p></template>
        <template v-else><p class="small text-muted mb-0">{{ t('receipt.closeTreasuryHint') }}</p><div><label class="form-label" for="custody-method">{{ t('receipt.handoverMethod') }}</label><select id="custody-method" v-model="method" class="form-select"><option value="cash">{{ t('receipt.handoverCash') }}</option><option value="bank_transfer">{{ t('receipt.handoverTransfer') }}</option></select></div><div><label class="form-label" for="custody-note">{{ t('receipt.closureNote') }}</label><textarea id="custody-note" v-model.trim="note" class="form-control" rows="3" :placeholder="t('receipt.closureNotePlaceholder')"></textarea></div></template>
      </div>
      <div class="modal-footer"><button class="btn btn-outline-secondary" type="button" @click="emit('close')">{{ t('common.cancel') }}</button><button class="btn btn-primary" type="button" @click="confirm">{{ decision.action === 'reminder' ? t('receipt.saveReminder') : t('receipt.confirmClosure') }}</button></div>
    </div></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { ContributionReceiptDeclarationResponse } from '@/api/contributions.api'
import { useLocaleStore } from '@/stores/locale.store'
import type { CustodyDecision, CustodyDecisionConfirmation } from '../composables/useFinanceWorkspace'
import { useFinanceFormatting } from '../composables/useFinanceFormatting'

const props = defineProps<{
  decision: CustodyDecision | null
  labelFor: (item: ContributionReceiptDeclarationResponse) => string
}>()

const emit = defineEmits<{
  confirm: [confirmation: CustodyDecisionConfirmation]
  close: []
}>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const { handoverStatusLabel } = useFinanceFormatting()

const reminderDays = ref(2)
const method = ref<'cash' | 'bank_transfer'>('cash')
const note = ref('')

watch(() => props.decision, (decision) => {
  if (!decision) return
  reminderDays.value = decision.item.handover_reminder_days || 2
  method.value = decision.item.handover_method === 'bank_transfer' ? 'bank_transfer' : 'cash'
  note.value = ''
})

function confirm() {
  emit('confirm', { reminderDays: reminderDays.value, method: method.value, note: note.value })
}
</script>
