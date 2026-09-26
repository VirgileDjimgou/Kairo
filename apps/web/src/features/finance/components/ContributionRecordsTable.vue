<template>
  <ResponsiveDataView :items="contributions" :aria-label="t('finance.tableAriaLabel')">
    <template #thead>
      <tr>
        <th class="ps-4" scope="col">{{ t('common.member') }}</th>
        <th scope="col">{{ t('common.year') }}</th>
        <th scope="col">{{ t('contributions.expected') }}</th>
        <th scope="col">{{ t('contributions.paid') }}</th>
        <th scope="col">{{ t('contributions.balance') }}</th>
        <th scope="col">{{ t('common.status') }}</th>
        <th scope="col">{{ t('finance.updated') }}</th>
        <th class="text-end pe-4" scope="col">{{ t('common.actions') }}</th>
      </tr>
    </template>
    <template #rows>
      <tr v-for="contribution in contributions" :key="contribution.id">
        <td class="ps-4"><div class="fw-medium">{{ memberLabel(contribution.membership_profile_id) }}</div><div class="small text-muted">{{ contribution.membership_profile_id.slice(0, 8) }}...</div></td>
        <td>{{ contribution.year }}</td>
        <td>{{ contribution.expected_amount }}</td>
        <td>{{ contribution.paid_amount }}</td>
        <td :class="Number(contribution.balance) > 0 ? 'text-danger fw-semibold' : 'text-success fw-semibold'">{{ contribution.balance }}</td>
        <td><span class="badge" :class="statusBadgeClass(contribution.status)">{{ contribution.status }}</span></td>
        <td class="small">{{ formatDate(contribution.updated_at) }}</td>
        <td class="text-end pe-4">
          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-sm btn-outline-primary" type="button" @click="emit('record-payment', contribution)">{{ t('contributions.recordPayment') }}</button>
            <button v-if="remindersEnabled && Number(contribution.balance) > 0" class="btn btn-sm btn-outline-secondary" type="button" :disabled="sendingSingleReminderId === contribution.id" @click="emit('send-reminder', contribution)">
              {{ sendingSingleReminderId === contribution.id ? t('finance.sending') : t('finance.sendReminder') }}
            </button>
          </div>
        </td>
      </tr>
    </template>
    <template #card="{ item: contribution }">
      <div class="d-flex align-items-start justify-content-between gap-3">
        <div class="min-w-0"><div class="fw-semibold">{{ memberLabel(contribution.membership_profile_id) }}</div><div class="small text-muted text-break">{{ contribution.membership_profile_id }}</div></div>
        <span class="badge" :class="statusBadgeClass(contribution.status)">{{ contribution.status }}</span>
      </div>
      <div class="row g-2 small mt-1">
        <div class="col-6"><div class="text-muted">{{ t('common.year') }}</div><div class="fw-semibold">{{ contribution.year }}</div></div>
        <div class="col-6"><div class="text-muted">{{ t('finance.updated') }}</div><div class="fw-semibold">{{ formatDate(contribution.updated_at) }}</div></div>
        <div class="col-4"><div class="text-muted">{{ t('contributions.expected') }}</div><div>{{ contribution.expected_amount }}</div></div>
        <div class="col-4"><div class="text-muted">{{ t('contributions.paid') }}</div><div>{{ contribution.paid_amount }}</div></div>
        <div class="col-4"><div class="text-muted">{{ t('contributions.balance') }}</div><div class="fw-semibold" :class="Number(contribution.balance) > 0 ? 'text-danger' : 'text-success'">{{ contribution.balance }}</div></div>
      </div>
      <div class="om-data-card-actions">
        <button class="btn btn-sm btn-outline-primary" type="button" @click="emit('record-payment', contribution)">{{ t('contributions.recordPayment') }}</button>
        <button v-if="remindersEnabled && Number(contribution.balance) > 0" class="btn btn-sm btn-outline-secondary" type="button" :disabled="sendingSingleReminderId === contribution.id" @click="emit('send-reminder', contribution)">
          {{ sendingSingleReminderId === contribution.id ? t('finance.sending') : t('finance.sendReminder') }}
        </button>
      </div>
    </template>
  </ResponsiveDataView>
</template>

<script setup lang="ts">
import type { ContributionRecordResponse } from '@/api/contributions.api'
import ResponsiveDataView from '@/components/ui/ResponsiveDataView.vue'
import { useLocaleStore } from '@/stores/locale.store'

defineProps<{
  contributions: ContributionRecordResponse[]
  memberLabel: (profileId: string) => string
  statusBadgeClass: (status: string) => string
  formatDate: (value: string | null) => string
  remindersEnabled: boolean
  sendingSingleReminderId: string
}>()

const emit = defineEmits<{
  'record-payment': [contribution: ContributionRecordResponse]
  'send-reminder': [contribution: ContributionRecordResponse]
}>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
</script>
