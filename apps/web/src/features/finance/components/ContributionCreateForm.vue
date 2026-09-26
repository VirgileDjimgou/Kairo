<template>
  <div class="card shadow-sm border-0">
    <div class="card-body p-4">
      <h2 class="h6 fw-bold mb-3">{{ t('finance.createContribution') }}</h2>
      <form class="vstack gap-3" @submit.prevent="submitContribution">
        <div>
          <label for="finance-create-member" class="form-label small fw-medium">{{ t('common.member') }}</label>
          <select id="finance-create-member" v-model="form.membership_profile_id" class="form-select" required>
            <option value="" disabled>{{ t('finance.selectMember') }}</option>
            <option v-for="member in members" :key="member.id" :value="member.id">
              {{ member.display_name }} ({{ member.member_code }})
            </option>
          </select>
        </div>
        <div class="row g-2">
          <div class="col-6">
            <label for="finance-create-year" class="form-label small fw-medium">{{ t('common.year') }}</label>
            <input id="finance-create-year" v-model.number="form.year" type="number" class="form-control" min="2000" max="2100" required />
          </div>
          <div class="col-6">
            <label for="finance-create-status" class="form-label small fw-medium">{{ t('common.status') }}</label>
            <select id="finance-create-status" v-model="form.status" class="form-select">
              <option value="pending">{{ copy.pending }}</option>
              <option value="partial">{{ copy.partial }}</option>
              <option value="paid">{{ copy.paid }}</option>
              <option value="overdue">{{ copy.overdue }}</option>
            </select>
          </div>
        </div>
        <div>
          <label for="finance-create-amount" class="form-label small fw-medium">{{ t('finance.expectedAmount') }} (EUR)</label>
          <input id="finance-create-amount" v-model="form.expected_amount" type="number" step="0.01" min="0" class="form-control" required />
        </div>
        <button class="btn btn-primary" type="submit" :disabled="saving">
          {{ saving ? t('common.saving') : t('finance.createContribution') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import type { MembershipProfileResponse } from '@/api/membership.api'
import { useLocaleStore } from '@/stores/locale.store'
import { useFinanceFormatting } from '../composables/useFinanceFormatting'
import type { ContributionCreateInput } from '../composables/useFinanceWorkspace'

const props = defineProps<{
  members: MembershipProfileResponse[]
  year: number
  saving: boolean
  resetToken: number
}>()

const emit = defineEmits<{ submit: [payload: ContributionCreateInput] }>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const { copy } = useFinanceFormatting()

function defaultForm() {
  return {
    membership_profile_id: '',
    year: props.year,
    expected_amount: '100.00',
    status: 'pending',
  }
}

const form = ref(defaultForm())

function resetForm() {
  form.value = defaultForm()
}

function submitContribution() {
  emit('submit', { ...form.value })
}

onMounted(resetForm)
watch(() => props.resetToken, resetForm)
</script>
