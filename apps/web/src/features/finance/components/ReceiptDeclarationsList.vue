<template>
  <section class="card shadow-sm border-0 mb-4" data-testid="finance-receipt-declarations">
    <div class="card-body p-4">
      <div class="d-flex flex-column flex-lg-row justify-content-between gap-2 mb-3">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary-emphasis">
            {{ t('finance.receiptValidationKicker') }}
          </div>
          <h2 class="h5 fw-bold mb-1">{{ t('finance.declarationsTitle') }}</h2>
          <p class="small text-muted mb-0">{{ t('finance.declarationsLead') }}</p>
        </div>
        <button class="btn btn-outline-secondary btn-sm align-self-lg-start" type="button" :disabled="loading" @click="load">
          {{ t('common.refresh') }}
        </button>
      </div>

      <div v-if="errorMessage" class="alert alert-warning border-0 shadow-sm mb-3" role="alert">
        {{ errorMessage }}
      </div>
      <p v-if="!loading && rows.length === 0" class="text-muted small mb-0">
        {{ t('finance.noReceiptDeclarations') }}
      </p>

      <div v-else class="table-responsive">
        <table class="table table-sm align-middle mb-0">
          <thead>
            <tr>
              <th scope="col">{{ t('finance.receivedAt') }}</th>
              <th scope="col">{{ t('receipt.sourceName') }}</th>
              <th scope="col">{{ t('finance.filterCategory') }}</th>
              <th scope="col" class="text-end">{{ t('common.amount') }}</th>
              <th scope="col">{{ t('finance.statusValue') }}</th>
              <th scope="col">{{ t('finance.handoverStatus') }}</th>
              <th scope="col">{{ t('finance.processedAt') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="declaration in rows" :key="declaration.id">
              <td class="text-nowrap">{{ formatDate(declaration.received_at) }}</td>
              <td>{{ labelFor(declaration) }}</td>
              <td>{{ receiptIncomeTypeLabel(declaration.income_type) }}</td>
              <td class="text-end text-nowrap">{{ formatMoney(declaration.amount) }}</td>
              <td>
                <span class="badge" :class="statusClass(declaration.status)">
                  {{ t(`finance.declarationStatus.${declaration.status}`) }}
                </span>
              </td>
              <td class="small">{{ handoverStatusLabel(declaration.cash_handover_status) }}</td>
              <td class="small">
                <div v-if="declaration.processed_at">{{ formatDate(declaration.processed_at) }}</div>
                <div v-if="declaration.processing_note" class="text-muted">
                  {{ declaration.processing_note }}
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  listContributionReceiptDeclarations,
  type ContributionReceiptDeclarationResponse,
} from '@/api/contributions.api'
import { listMembers, type MembershipProfileResponse } from '@/api/membership.api'
import { useLocaleStore } from '@/stores/locale.store'
import { useFinanceFormatting } from '../composables/useFinanceFormatting'

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const { formatDate, formatMoney, receiptIncomeTypeLabel, handoverStatusLabel } =
  useFinanceFormatting()

const rows = ref<ContributionReceiptDeclarationResponse[]>([])
const membersById = ref<Record<string, MembershipProfileResponse>>({})
const loading = ref(false)
const errorMessage = ref('')

function labelFor(declaration: ContributionReceiptDeclarationResponse): string {
  if (declaration.membership_profile_id) {
    const member = membersById.value[declaration.membership_profile_id]
    if (member) return `${member.member_code} · ${member.display_name}`
  }
  return declaration.source_name || t('finance.unknownMember')
}

function statusClass(status: string): string {
  if (status === 'validated' || status === 'partially_validated') return 'text-bg-success'
  if (status === 'rejected' || status === 'cancelled') return 'text-bg-danger'
  if (status === 'clarification_requested') return 'text-bg-warning'
  return 'text-bg-secondary'
}

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const [declarations, members] = await Promise.all([
      listContributionReceiptDeclarations(),
      listMembers(),
    ])
    rows.value = declarations
    membersById.value = Object.fromEntries(members.map((member) => [member.id, member]))
  } catch {
    errorMessage.value = t('finance.receiptProcessingFailed')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
