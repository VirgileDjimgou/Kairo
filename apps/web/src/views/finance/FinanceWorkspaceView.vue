<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">{{ t('finance.workspaceKicker') }}</div>
        <h1 class="h4 fw-bold mb-1">{{ t('finance.workspaceTitle') }}</h1>
        <p class="text-muted mb-0">
          {{ t('finance.workspaceSubtitle') }}
        </p>
      </div>
      <div class="d-flex gap-2 align-items-start">
        <select v-model="selectedYear" class="form-select form-select-sm" style="width: auto" @change="refreshFinanceData">
          <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
        </select>
        <button class="btn btn-outline-secondary btn-sm" type="button" @click="refreshAll" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
          {{ t('common.refresh') }}
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger border-0 shadow-sm mb-4" role="alert">
      <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3">
        <div>
          <div class="fw-semibold mb-1">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ t('finance.workspaceErrorTitle') }}
          </div>
          <p class="mb-0 small">{{ error }}</p>
          <p class="mb-0 small text-muted mt-1">{{ t('common.recoveryHint') }}</p>
        </div>
        <button class="btn btn-outline-secondary btn-sm flex-shrink-0" type="button" @click="retryAll" :disabled="isRecovering">
          <span v-if="isRecovering" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          {{ isRecovering ? t('common.loading') : t('common.retry') }}
        </button>
      </div>
    </div>

    <div v-if="notice" class="alert alert-success alert-dismissible small py-2 mb-4" role="status">
      <i class="bi bi-check-circle me-1"></i>{{ notice }}
      <button type="button" class="btn-close py-2" @click="notice = ''"></button>
    </div>

    <div v-if="summary" class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card shadow-sm border-0 bg-primary-subtle">
          <div class="card-body text-center py-3">
            <div class="text-muted small">{{ t('contributions.expected') }}</div>
            <div class="fw-bold fs-4">{{ summary.total_expected }} EUR</div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm border-0 bg-success-subtle">
          <div class="card-body text-center py-3">
            <div class="text-muted small">{{ t('contributions.paid') }}</div>
            <div class="fw-bold fs-4">{{ summary.total_paid }} EUR</div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm border-0" :class="Number(summary.total_balance) > 0 ? 'bg-warning-subtle' : 'bg-success-subtle'">
          <div class="card-body text-center py-3">
            <div class="text-muted small">{{ t('finance.outstandingBalance') }}</div>
            <div class="fw-bold fs-4">{{ summary.total_balance }} EUR</div>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-xl-4">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h2 class="h6 fw-bold mb-0">{{ t('finance.memberLookup') }}</h2>
              <span class="badge text-bg-light border text-dark">{{ members.length }} {{ t('finance.membersCountSuffix') }}</span>
            </div>

            <div class="mb-3">
              <label for="finance-balance-member" class="form-label small fw-medium">{{ t('common.member') }}</label>
              <select
                id="finance-balance-member"
                v-model="selectedMemberId"
                class="form-select"
                @change="loadSelectedMemberBalance"
              >
                <option value="">{{ t('finance.selectMember') }}</option>
                <option v-for="member in members" :key="member.id" :value="member.id">
                  {{ member.display_name }} ({{ member.member_code }})
                </option>
              </select>
            </div>

            <div v-if="selectedMemberBalance" class="border rounded-3 p-3 bg-light-subtle" data-testid="finance-member-balance">
              <div class="fw-semibold mb-1">{{ selectedMemberBalance.profile.display_name }}</div>
              <div class="small text-muted mb-3">{{ selectedMemberBalance.profile.member_code }}</div>
              <div class="row g-2 small">
                <div class="col-6">
                  <div class="text-muted">{{ t('contributions.expected') }}</div>
                  <div class="fw-semibold">{{ selectedMemberBalance.total_expected }} EUR</div>
                </div>
                <div class="col-6">
                  <div class="text-muted">{{ t('contributions.paid') }}</div>
                  <div class="fw-semibold">{{ selectedMemberBalance.total_paid }} EUR</div>
                </div>
                <div class="col-12">
                  <div class="text-muted">{{ t('contributions.balance') }}</div>
                  <div class="fw-semibold" :class="Number(selectedMemberBalance.total_balance) > 0 ? 'text-danger' : 'text-success'">
                    {{ selectedMemberBalance.total_balance }} EUR
                  </div>
                </div>
              </div>
            </div>
            <p v-else class="text-muted small mb-0">
              {{ t('finance.selectMemberHint') }}
            </p>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <h2 class="h6 fw-bold mb-3">{{ t('finance.createContribution') }}</h2>
            <form class="vstack gap-3" @submit.prevent="handleCreateContribution">
              <div>
                <label for="finance-create-member" class="form-label small fw-medium">{{ t('common.member') }}</label>
                <select id="finance-create-member" v-model="createForm.membership_profile_id" class="form-select" required>
                  <option value="" disabled>{{ t('finance.selectMember') }}</option>
                  <option v-for="member in members" :key="member.id" :value="member.id">
                    {{ member.display_name }} ({{ member.member_code }})
                  </option>
                </select>
              </div>
              <div class="row g-2">
                <div class="col-6">
                  <label for="finance-create-year" class="form-label small fw-medium">{{ t('common.year') }}</label>
                  <input id="finance-create-year" v-model.number="createForm.year" type="number" class="form-control" min="2000" max="2100" required />
                </div>
                <div class="col-6">
                  <label for="finance-create-status" class="form-label small fw-medium">{{ t('common.status') }}</label>
                  <select id="finance-create-status" v-model="createForm.status" class="form-select">
                    <option value="pending">{{ copy.pending }}</option>
                    <option value="partial">{{ copy.partial }}</option>
                    <option value="paid">{{ copy.paid }}</option>
                    <option value="overdue">{{ copy.overdue }}</option>
                  </select>
                </div>
              </div>
              <div>
                <label for="finance-create-amount" class="form-label small fw-medium">{{ t('finance.expectedAmount') }} (EUR)</label>
                <input id="finance-create-amount" v-model="createForm.expected_amount" type="number" step="0.01" min="0" class="form-control" required />
              </div>
              <button class="btn btn-primary" type="submit" :disabled="savingContribution">
                {{ savingContribution ? t('common.saving') : t('finance.createContribution') }}
              </button>
            </form>
          </div>
        </div>
      </div>

      <div class="col-xl-8">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h2 class="h6 fw-bold mb-0">{{ t('finance.recentPayments') }}</h2>
              <span class="badge text-bg-light border text-dark">{{ recentPayments.length }} {{ t('finance.itemsCountSuffix') }}</span>
            </div>

            <div v-if="recentPayments.length === 0" class="text-muted small mb-0">
              {{ t('finance.noPayments') }}
            </div>

            <div v-else class="list-group list-group-flush">
              <div v-for="payment in recentPayments" :key="payment.id" class="list-group-item px-0">
                <div class="d-flex justify-content-between gap-3">
                  <div>
                    <div class="fw-medium">{{ paymentMemberLabel(payment.contribution_record_id) }}</div>
                    <div class="small text-muted">
                      {{ payment.amount }} EUR · {{ formatPaymentMethod(payment.payment_method) }}
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

        <div v-if="remindersEnabled" class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <div>
                <h2 class="h6 fw-bold mb-0">{{ t('finance.reminders') }}</h2>
                <p class="text-muted small mb-0">{{ t('finance.remindersLead') }}</p>
              </div>
              <span class="badge text-bg-light border text-dark">{{ reminderHistory.length }} {{ t('finance.recentCountSuffix') }}</span>
            </div>

            <form class="row g-3 align-items-end mb-4" @submit.prevent="handleBatchReminder">
              <div class="col-md-4">
                <label for="finance-reminder-scope" class="form-label small fw-medium">{{ t('finance.dueScope') }}</label>
                <select id="finance-reminder-scope" v-model="reminderBatchForm.due_scope" class="form-select">
                  <option value="overdue">{{ t('finance.overdueOnly') }}</option>
                  <option value="due_soon">{{ t('finance.dueSoon') }}</option>
                  <option value="all_outstanding">{{ t('finance.allOutstanding') }}</option>
                </select>
              </div>
              <div class="col-md-4">
                <label for="finance-reminder-status" class="form-label small fw-medium">{{ t('finance.contributionStatus') }}</label>
                <select id="finance-reminder-status" v-model="reminderBatchForm.status" class="form-select">
                  <option value="">{{ t('finance.anyOutstanding') }}</option>
                  <option value="pending">{{ copy.pending }}</option>
                  <option value="partial">{{ copy.partial }}</option>
                  <option value="overdue">{{ copy.overdue }}</option>
                </select>
              </div>
              <div class="col-md-2">
                <label for="finance-reminder-limit" class="form-label small fw-medium">{{ t('finance.limit') }}</label>
                <input id="finance-reminder-limit" v-model.number="reminderBatchForm.limit" type="number" min="1" max="100" class="form-control" />
              </div>
              <div class="col-md-2 d-grid">
                <button class="btn btn-outline-primary" type="submit" :disabled="sendingBatchReminders">
                  {{ sendingBatchReminders ? t('finance.sending') : t('finance.sendBatch') }}
                </button>
              </div>
            </form>

            <div v-if="reminderHistory.length === 0" class="text-muted small mb-0">
              {{ t('finance.noReminders') }}
            </div>

            <div v-else class="list-group list-group-flush" data-testid="finance-reminder-history">
              <div v-for="reminder in reminderHistory" :key="reminder.id" class="list-group-item px-0">
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

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h2 class="h6 fw-bold mb-0">{{ t('contributions.recordPayment') }}</h2>
              <span v-if="paymentTarget" class="badge text-bg-light border text-dark">{{ paymentTarget.year }}</span>
            </div>

            <div v-if="paymentTarget" class="border rounded-3 p-3 bg-light-subtle">
              <div class="fw-semibold">{{ memberLabel(paymentTarget.membership_profile_id) }}</div>
              <div class="small text-muted mb-3">
                {{ paymentTargetCopy(paymentTarget.balance, paymentTarget.year) }}
              </div>
              <form class="row g-3 align-items-end" @submit.prevent="handleRecordPayment">
                <div class="col-md-4">
                  <label for="finance-payment-amount" class="form-label small fw-medium">{{ t('common.amount') }} (EUR)</label>
                  <input id="finance-payment-amount" v-model="paymentForm.amount" type="number" step="0.01" min="0.01" class="form-control" required />
                </div>
                <div class="col-md-4">
                  <label for="finance-payment-method" class="form-label small fw-medium">{{ t('contributions.paymentMethod') }}</label>
                  <select id="finance-payment-method" v-model="paymentForm.payment_method" class="form-select">
                    <option value="cash">{{ t('contributions.cash') }}</option>
                    <option value="bank_transfer">{{ t('contributions.bankTransfer') }}</option>
                    <option value="card">{{ t('finance.card') }}</option>
                    <option value="check">{{ t('contributions.check') }}</option>
                    <option value="other">{{ t('finance.other') }}</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label for="finance-payment-reference" class="form-label small fw-medium">{{ t('finance.reference') }}</label>
                  <input id="finance-payment-reference" v-model="paymentForm.reference" class="form-control" />
                </div>
                <div class="col-12 d-flex gap-2">
                  <button class="btn btn-primary" type="submit" :disabled="savingPayment">
                    {{ savingPayment ? t('common.saving') : t('contributions.recordPayment') }}
                  </button>
                  <button class="btn btn-outline-secondary" type="button" @click="resetPaymentForm">
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

        <div class="card shadow-sm border-0">
          <div class="card-body p-0">
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">{{ t('common.loading') }}</span>
              </div>
            </div>

            <div v-else-if="contributions.length === 0" class="empty-state p-5">
              <i class="bi bi-cash-stack display-6 text-secondary"></i>
              <p class="mb-1 fw-semibold">{{ noContributionRecordsLabel }}</p>
              <p class="text-muted mb-0">{{ t('finance.noContributionRecordsHint') }}</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0" :aria-label="t('finance.tableAriaLabel')">
                <thead class="table-light">
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
                </thead>
                <tbody>
                  <tr v-for="contribution in contributions" :key="contribution.id">
                    <td class="ps-4">
                      <div class="fw-medium">{{ memberLabel(contribution.membership_profile_id) }}</div>
                      <div class="small text-muted">{{ contribution.membership_profile_id.slice(0, 8) }}…</div>
                    </td>
                    <td>{{ contribution.year }}</td>
                    <td>{{ contribution.expected_amount }}</td>
                    <td>{{ contribution.paid_amount }}</td>
                    <td :class="Number(contribution.balance) > 0 ? 'text-danger fw-semibold' : 'text-success fw-semibold'">
                      {{ contribution.balance }}
                    </td>
                    <td>
                      <span class="badge" :class="statusBadgeClass(contribution.status)">{{ contribution.status }}</span>
                    </td>
                    <td class="small">{{ formatDate(contribution.updated_at) }}</td>
                    <td class="text-end pe-4">
                      <div class="d-flex justify-content-end gap-2">
                        <button class="btn btn-sm btn-outline-primary" type="button" @click="selectPaymentTarget(contribution)">
                          {{ t('contributions.recordPayment') }}
                        </button>
                        <button
                          v-if="remindersEnabled && Number(contribution.balance) > 0"
                          class="btn btn-sm btn-outline-secondary"
                          type="button"
                          :disabled="sendingSingleReminderId === contribution.id"
                          @click="handleSingleReminder(contribution)"
                        >
                          {{ sendingSingleReminderId === contribution.id ? t('finance.sending') : t('finance.sendReminder') }}
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  createContribution,
  getContributionSummary,
  listContributions,
  listContributionReminders,
  listTenantPayments,
  recordPayment,
  sendContributionReminder,
  sendContributionReminderBatch,
  type ContributionReminderResponse,
  type ContributionRecordResponse,
  type ContributionSummary,
  type PaymentRecordResponse,
} from '@/api/contributions.api'
import {
  getMemberBalance,
  listMembers,
  type MemberBalanceResponse,
  type MembershipProfileResponse,
} from '@/api/membership.api'
import { useTenantStore } from '@/stores/tenant.store'
import { useLocaleStore } from '@/stores/locale.store'
import { useRecoveryState } from '@/composables/useRecoveryState'
import { computed, onMounted, ref } from 'vue'

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)

const { loading, error, isRecovering, run, retry, clearError } = useRecoveryState()
const notice = ref('')
const savingContribution = ref(false)
const savingPayment = ref(false)
const sendingSingleReminderId = ref('')
const sendingBatchReminders = ref(false)

const members = ref<MembershipProfileResponse[]>([])
const contributions = ref<ContributionRecordResponse[]>([])
const summary = ref<ContributionSummary | null>(null)
const selectedMemberBalance = ref<MemberBalanceResponse | null>(null)
const selectedMemberId = ref('')
const paymentTarget = ref<ContributionRecordResponse | null>(null)
const recentPayments = ref<PaymentRecordResponse[]>([])
const reminderHistory = ref<ContributionReminderResponse[]>([])
const tenantStore = useTenantStore()

const currentYear = new Date().getFullYear()
const years = [currentYear - 1, currentYear, currentYear + 1]
const selectedYear = ref(currentYear)
const remindersEnabled = computed(() => tenantStore.isModuleEnabled('notifications'))
const copy = computed(() => {
  if (localeStore.currentLocale === 'de') {
    return {
      pending: 'Ausstehend',
      partial: 'Teilweise',
      paid: 'Bezahlt',
      overdue: 'Überfällig',
      sent: 'Gesendet',
      simulated: 'Simuliert',
      failed: 'Fehlgeschlagen',
      skipped: 'Übersprungen',
      unknownMember: 'Unbekanntes Mitglied',
      outstandingFor: (balance: string, year: number) => `Offen ${balance} EUR für ${year}`,
    }
  }
  if (localeStore.currentLocale === 'en') {
    return {
      pending: 'Pending',
      partial: 'Partial',
      paid: 'Paid',
      overdue: 'Overdue',
      sent: 'Sent',
      simulated: 'Simulated',
      failed: 'Failed',
      skipped: 'Skipped',
      unknownMember: 'Unknown member',
      outstandingFor: (balance: string, year: number) => `Outstanding ${balance} EUR for ${year}`,
    }
  }
  return {
    pending: 'En attente',
    partial: 'Partiel',
    paid: 'Payé',
    overdue: 'En retard',
    sent: 'Envoyé',
    simulated: 'Simulé',
    failed: 'Échoué',
    skipped: 'Ignoré',
    unknownMember: 'Membre inconnu',
    outstandingFor: (balance: string, year: number) => `Solde ouvert ${balance} EUR pour ${year}`,
  }
})
const noContributionRecordsLabel = computed(() => `${t('contributions.noRecords').replace('{year}', String(selectedYear.value))}`)

const createForm = ref({
  membership_profile_id: '',
  year: currentYear,
  expected_amount: '100.00',
  status: 'pending',
})

const paymentForm = ref({
  amount: '',
  payment_method: 'bank_transfer',
  reference: '',
})

const reminderBatchForm = ref({
  due_scope: 'overdue' as 'all_outstanding' | 'overdue' | 'due_soon',
  status: '',
  limit: 25,
})

const membersById = computed(() =>
  Object.fromEntries(members.value.map((member) => [member.id, member])),
)

const contributionsById = computed(() =>
  Object.fromEntries(contributions.value.map((contribution) => [contribution.id, contribution])),
)

function memberLabel(profileId: string): string {
  const member = membersById.value[profileId]
  if (!member) return copy.value.unknownMember
  return `${member.display_name} (${member.member_code})`
}

function formatDate(value: string | null): string {
  if (!value) return '—'
  return new Date(value).toLocaleDateString()
}

function formatPaymentMethod(value: string): string {
  return value.replace('_', ' ')
}

function reminderStatusLabel(value: ContributionReminderResponse['delivery_status']): string {
  const map = {
    sent: copy.value.sent,
    simulated: copy.value.simulated,
    failed: copy.value.failed,
    skipped: copy.value.skipped,
  }
  return map[value] || value
}

function statusBadgeClass(status: string): string {
  const map: Record<string, string> = {
    pending: 'bg-secondary-subtle text-secondary',
    partial: 'bg-warning-subtle text-warning',
    paid: 'bg-success-subtle text-success',
    overdue: 'bg-danger-subtle text-danger',
    waived: 'bg-info-subtle text-info',
  }
  return map[status] || 'bg-light text-dark'
}

function paymentMemberLabel(contributionId: string): string {
  const contribution = contributionsById.value[contributionId]
  if (!contribution) return copy.value.unknownMember
  return memberLabel(contribution.membership_profile_id)
}

function paymentTargetCopy(balance: string, year: number) {
  return copy.value.outstandingFor(balance, year)
}

async function refreshFinanceData() {
  const reminderPromise = remindersEnabled.value ? listContributionReminders(selectedYear.value) : Promise.resolve([])
  const [contributionRows, summaryData, paymentRows, reminderRows] = await Promise.all([
    listContributions(selectedYear.value),
    getContributionSummary(selectedYear.value),
    listTenantPayments(),
    reminderPromise,
  ])
  contributions.value = contributionRows
  summary.value = summaryData
  recentPayments.value = paymentRows.slice(0, 8)
  reminderHistory.value = reminderRows.slice(0, 8)
}

async function loadSelectedMemberBalance() {
  if (!selectedMemberId.value) {
    selectedMemberBalance.value = null
    return
  }
  selectedMemberBalance.value = await getMemberBalance(selectedMemberId.value)
}

async function refreshAll() {
  await run(async () => {
    members.value = await listMembers()
    await refreshFinanceData()
    if (selectedMemberId.value) {
      await loadSelectedMemberBalance()
    }
  })
}

async function retryAll() {
  await retry(async () => {
    members.value = await listMembers()
    await refreshFinanceData()
    if (selectedMemberId.value) {
      await loadSelectedMemberBalance()
    }
  })
}

async function handleSingleReminder(contribution: ContributionRecordResponse) {
  sendingSingleReminderId.value = contribution.id
  clearError()
  notice.value = ''
  try {
    const result = await sendContributionReminder(contribution.id)
    notice.value = `${reminderStatusLabel(result.delivery_status)} reminder for ${result.member_display_name}.`
    await refreshFinanceData()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to send the reminder.'
  } finally {
    sendingSingleReminderId.value = ''
  }
}

async function handleBatchReminder() {
  sendingBatchReminders.value = true
  clearError()
  notice.value = ''
  try {
    const result = await sendContributionReminderBatch({
      year: selectedYear.value,
      due_scope: reminderBatchForm.value.due_scope,
      status: reminderBatchForm.value.status || undefined,
      limit: reminderBatchForm.value.limit,
    })
    notice.value = `Processed ${result.attempted_count} reminder target(s).`
    await refreshFinanceData()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to send reminder batch.'
  } finally {
    sendingBatchReminders.value = false
  }
}

function resetCreateForm() {
  createForm.value = {
    membership_profile_id: '',
    year: selectedYear.value,
    expected_amount: '100.00',
    status: 'pending',
  }
}

function selectPaymentTarget(contribution: ContributionRecordResponse) {
  paymentTarget.value = contribution
  paymentForm.value.amount = contribution.balance
  paymentForm.value.payment_method = 'bank_transfer'
  paymentForm.value.reference = ''
}

function resetPaymentForm() {
  paymentTarget.value = null
  paymentForm.value = {
    amount: '',
    payment_method: 'bank_transfer',
    reference: '',
  }
}

async function handleCreateContribution() {
  savingContribution.value = true
  clearError()
  try {
    await createContribution({
      membership_profile_id: createForm.value.membership_profile_id,
      year: createForm.value.year,
      expected_amount: createForm.value.expected_amount,
      paid_amount: '0.00',
      status: createForm.value.status,
    })
    resetCreateForm()
    await refreshAll()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to create the contribution record.'
  } finally {
    savingContribution.value = false
  }
}

async function handleRecordPayment() {
  if (!paymentTarget.value) return

  savingPayment.value = true
  clearError()
  try {
    await recordPayment({
      contribution_record_id: paymentTarget.value.id,
      amount: paymentForm.value.amount,
      payment_method: paymentForm.value.payment_method,
      reference: paymentForm.value.reference || null,
    })
    const targetMemberId = paymentTarget.value.membership_profile_id
    resetPaymentForm()
    await refreshAll()
    if (selectedMemberId.value === targetMemberId) {
      await loadSelectedMemberBalance()
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to record the payment.'
  } finally {
    savingPayment.value = false
  }
}

onMounted(async () => {
  members.value = await listMembers()
  resetCreateForm()
  await refreshAll()
})
</script>
