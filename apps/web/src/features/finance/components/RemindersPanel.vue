<template>
  <div class="card shadow-sm border-0 mb-4">
    <div class="card-body p-4">
      <div class="d-flex align-items-center justify-content-between mb-3">
        <div>
          <h2 class="h6 fw-bold mb-0">{{ t('finance.reminders') }}</h2>
          <p class="text-muted small mb-0">{{ t('finance.remindersLead') }}</p>
        </div>
        <span class="badge text-bg-light border text-dark">{{ history.length }} {{ t('finance.recentCountSuffix') }}</span>
      </div>

      <form class="row g-3 align-items-end mb-4" @submit.prevent="submitBatch">
        <div class="col-md-4">
          <label for="finance-reminder-scope" class="form-label small fw-medium">{{ t('finance.dueScope') }}</label>
          <select id="finance-reminder-scope" v-model="batchForm.due_scope" class="form-select">
            <option value="overdue">{{ t('finance.overdueOnly') }}</option>
            <option value="due_soon">{{ t('finance.dueSoon') }}</option>
            <option value="all_outstanding">{{ t('finance.allOutstanding') }}</option>
          </select>
        </div>
        <div class="col-md-4">
          <label for="finance-reminder-status" class="form-label small fw-medium">{{ t('finance.contributionStatus') }}</label>
          <select id="finance-reminder-status" v-model="batchForm.status" class="form-select">
            <option value="">{{ t('finance.anyOutstanding') }}</option>
            <option value="pending">{{ copy.pending }}</option>
            <option value="partial">{{ copy.partial }}</option>
            <option value="overdue">{{ copy.overdue }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <label for="finance-reminder-limit" class="form-label small fw-medium">{{ t('finance.limit') }}</label>
          <input id="finance-reminder-limit" v-model.number="batchForm.limit" type="number" min="1" max="100" class="form-control" />
        </div>
        <div class="col-md-2 d-grid">
          <button class="btn btn-outline-primary" type="submit" :disabled="sendingBatch">
            {{ sendingBatch ? t('finance.sending') : t('finance.sendBatch') }}
          </button>
        </div>
      </form>

      <div v-if="history.length === 0" class="text-muted small mb-0">
        {{ t('finance.noReminders') }}
      </div>

      <div v-else class="list-group list-group-flush" data-testid="finance-reminder-history">
        <div v-for="reminder in history" :key="reminder.id" class="list-group-item px-0">
          <div class="d-flex justify-content-between gap-3">
            <div>
              <div class="fw-medium">{{ reminder.member_display_name }} ({{ reminder.member_code }})</div>
              <div class="small text-muted">{{ reminder.subject }}</div>
              <div class="small text-muted">
                {{ reminder.balance_snapshot }} EUR · {{ reminderStatusLabel(reminder.delivery_status) }}
              </div>
            </div>
            <div class="text-end small text-muted">
              <div>{{ formatDate(reminder.sent_at) }}</div>
              <div>{{ reminder.provider_message || reminder.recipient }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ContributionReminderResponse } from '@/api/contributions.api'
import { useLocaleStore } from '@/stores/locale.store'
import { useFinanceFormatting } from '../composables/useFinanceFormatting'
import type { ReminderBatchInput } from '../composables/useFinanceWorkspace'

defineProps<{
  history: ContributionReminderResponse[]
  sendingBatch: boolean
}>()

const emit = defineEmits<{ submit: [payload: ReminderBatchInput] }>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const { copy, formatDate, reminderStatusLabel } = useFinanceFormatting()

const batchForm = ref<ReminderBatchInput>({
  due_scope: 'overdue',
  status: '',
  limit: 25,
})

function submitBatch() {
  emit('submit', { ...batchForm.value })
}
</script>
