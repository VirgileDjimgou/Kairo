<template>
  <div v-if="decision" class="modal d-block" tabindex="-1" role="dialog" aria-modal="true">
    <div class="modal-dialog modal-dialog-centered"><div class="modal-content shadow">
      <div class="modal-header"><h2 class="modal-title fs-5">{{ t('receipt.reviewTitle') }}</h2><button class="btn-close" type="button" @click="emit('close')"></button></div>
      <div class="modal-body vstack gap-3"><p class="mb-0">{{ labelFor(decision.item) }} · {{ decision.item.amount }} {{ decision.item.currency }}</p>
        <div v-if="decision.action === 'validated'"><label class="form-label" for="handover-reminder-days">{{ t('receipt.reminderDays') }}</label><select id="handover-reminder-days" v-model.number="reminderDays" class="form-select"><option v-for="day in 7" :key="day" :value="day">{{ day }}</option></select></div>
        <div v-else><label class="form-label" for="receipt-rejection-reason">{{ t('receipt.rejectionReason') }}</label><textarea id="receipt-rejection-reason" v-model.trim="note" class="form-control" rows="3" required></textarea></div>
      </div>
      <div class="modal-footer"><button class="btn btn-outline-secondary" type="button" @click="emit('close')">{{ t('common.cancel') }}</button><button class="btn" :class="decision.action === 'validated' ? 'btn-success' : 'btn-danger'" type="button" :disabled="decision.action === 'rejected' && !note" @click="confirm">{{ decision.action === 'validated' ? t('finance.validateReceipt') : t('finance.rejectReceipt') }}</button></div>
    </div></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { ContributionReceiptDeclarationResponse } from '@/api/contributions.api'
import { useLocaleStore } from '@/stores/locale.store'
import type { ReceiptDecision, ReceiptDecisionConfirmation } from '../composables/useFinanceWorkspace'

const props = defineProps<{
  decision: ReceiptDecision | null
  labelFor: (item: ContributionReceiptDeclarationResponse) => string
}>()

const emit = defineEmits<{
  confirm: [confirmation: ReceiptDecisionConfirmation]
  close: []
}>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)

const note = ref('')
const reminderDays = ref(2)

watch(() => props.decision, (decision) => {
  if (!decision) return
  note.value = ''
  reminderDays.value = 2
})

function confirm() {
  emit('confirm', { reminderDays: reminderDays.value, note: note.value })
}
</script>
