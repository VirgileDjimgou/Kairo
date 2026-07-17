<template>
  <div class="p-4 p-lg-5">
    <div class="auditor-hero rounded-4 p-4 p-lg-5 mb-4" data-testid="auditor-finance-overview">
      <div class="d-flex flex-column flex-xl-row justify-content-between gap-4">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary mb-2">
            {{ t('auditor.kicker') }}
          </div>
          <h1 class="h3 fw-bold mb-2">{{ t('auditor.title') }}</h1>
          <p class="text-muted mb-0 hero-copy">
            {{ t('auditor.subtitle') }}
          </p>
        </div>
        <div class="d-flex gap-2 align-items-start">
          <select v-model="selectedYear" class="form-select form-select-sm" style="width: auto" @change="refreshAll">
            <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
          </select>
          <button class="btn btn-outline-secondary btn-sm" type="button" @click="refreshAll" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
            {{ t('common.refresh') }}
          </button>
          <button class="btn btn-primary btn-sm" type="button" @click="downloadReport" :disabled="exporting">
            <span v-if="exporting" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
            {{ exporting ? t('auditor.exporting') : t('auditor.exportReport') }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="errorMessage" class="alert alert-warning border-0 shadow-sm mb-4" role="alert">
      <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
        <div>
          <div class="fw-semibold">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ t('auditor.workspaceErrorTitle') }}
          </div>
          <p class="small mb-0 mt-2">{{ errorMessage }}</p>
          <p class="mb-0 small text-muted mt-1">{{ t('common.recoveryHint') }}</p>
        </div>
        <button
          v-if="error"
          class="btn btn-outline-secondary btn-sm align-self-start"
          type="button"
          @click="retryRefresh"
          :disabled="isRecovering"
        >
          <span v-if="isRecovering" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
          {{ isRecovering ? t('common.loading') : t('common.retry') }}
        </button>
      </div>
    </div>

    <div v-if="summary" class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="metric-card bg-primary-subtle">
          <div class="text-muted small">{{ t('contributions.expected') }}</div>
          <div class="fw-bold fs-4">{{ summary.total_expected }} EUR</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="metric-card bg-success-subtle">
          <div class="text-muted small">{{ t('contributions.paid') }}</div>
          <div class="fw-bold fs-4">{{ summary.total_paid }} EUR</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="metric-card" :class="Number(summary.total_balance) > 0 ? 'bg-warning-subtle' : 'bg-success-subtle'">
          <div class="text-muted small">{{ t('finance.outstandingBalance') }}</div>
          <div class="fw-bold fs-4">{{ summary.total_balance }} EUR</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="metric-card bg-light">
          <div class="text-muted small">{{ t('auditor.paymentsLogged') }}</div>
          <div class="fw-bold fs-4">{{ payments.length }}</div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-xl-7">
        <div class="card shadow-sm border-0">
          <div class="card-body p-0">
            <div class="px-4 pt-4 pb-2 d-flex justify-content-between align-items-center">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-1">{{ t('auditor.memberBalances') }}</div>
                <h2 class="h6 fw-bold mb-0">{{ t('auditor.memberExposure') }}</h2>
              </div>
              <span class="badge text-bg-light border text-dark">{{ memberRows.length }} members</span>
            </div>

            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">{{ t('common.loading') }}</span>
              </div>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0" aria-label="Auditor member balances">
                <thead class="table-light">
                  <tr>
                    <th class="ps-4" scope="col">{{ t('common.member') }}</th>
                    <th scope="col">{{ t('contributions.expected') }}</th>
                    <th scope="col">{{ t('contributions.paid') }}</th>
                    <th scope="col">Balance</th>
                    <th class="pe-4" scope="col">{{ t('common.records') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in memberRows" :key="row.id">
                    <td class="ps-4">
                      <div class="fw-medium">{{ row.display_name }}</div>
                      <div class="small text-muted">{{ row.member_code }}</div>
                    </td>
                    <td>{{ row.totalExpected }}</td>
                    <td>{{ row.totalPaid }}</td>
                    <td :class="Number(row.totalBalance) > 0 ? 'text-danger fw-semibold' : 'text-success fw-semibold'">
                      {{ row.totalBalance }}
                    </td>
                    <td class="pe-4">{{ row.contributionCount }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-5">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body p-0">
            <div class="px-4 pt-4 pb-2 d-flex justify-content-between align-items-center">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-1">{{ t('auditor.paymentActivity') }}</div>
                <h2 class="h6 fw-bold mb-0">Recent recorded payments</h2>
              </div>
              <span class="badge text-bg-light border text-dark">{{ visiblePayments.length }} shown</span>
            </div>

            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">{{ t('common.loading') }}</span>
              </div>
            </div>

            <div v-else-if="visiblePayments.length === 0" class="p-4 text-muted small">
              {{ t('auditor.noPayments') }}
            </div>

            <div v-else class="list-group list-group-flush">
              <div v-for="payment in visiblePayments" :key="payment.id" class="list-group-item px-4 py-3">
                <div class="d-flex justify-content-between gap-3">
                  <div>
                    <div class="fw-medium">{{ payment.memberLabel }}</div>
                    <div class="small text-muted">
                      {{ payment.amount }} EUR · {{ formatPaymentMethod(payment.payment_method) }}
                    </div>
                  </div>
                  <div class="text-end small text-muted">
                    <div>{{ formatDate(payment.paid_at) }}</div>
                    <div>{{ payment.reference || 'No reference' }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  exportFinanceReportCsv,
  getContributionSummary,
  listContributions,
  listTenantPayments,
  type ContributionRecordResponse,
  type ContributionSummary,
  type PaymentRecordResponse,
} from '@/api/contributions.api'
import { listMembers, type MembershipProfileResponse } from '@/api/membership.api'
import { useCsvExport } from '@/composables/useCsvExport'
import { useRecoveryState } from '@/composables/useRecoveryState'
import { useLocaleStore } from '@/stores/locale.store'
import { computed, onMounted, ref } from 'vue'

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)

type AuditorPaymentRow = PaymentRecordResponse & { memberLabel: string }

const { loading, error, isRecovering, run, retry, clearError } = useRecoveryState()
const exporting = ref(false)
const actionError = ref('')
const members = ref<MembershipProfileResponse[]>([])
const contributions = ref<ContributionRecordResponse[]>([])
const payments = ref<PaymentRecordResponse[]>([])
const summary = ref<ContributionSummary | null>(null)

const currentYear = new Date().getFullYear()
const years = [currentYear - 1, currentYear, currentYear + 1]
const selectedYear = ref(currentYear)
const { exportCsv } = useCsvExport()

const memberMap = computed(() =>
  Object.fromEntries(members.value.map((member) => [member.id, member])),
)

const contributionMap = computed(() =>
  Object.fromEntries(contributions.value.map((contribution) => [contribution.id, contribution])),
)

const memberRows = computed(() => {
  return members.value
    .map((member) => {
      const scoped = contributions.value.filter((item) => item.membership_profile_id === member.id)
      const totalExpected = scoped.reduce((sum, item) => sum + Number(item.expected_amount), 0)
      const totalPaid = scoped.reduce((sum, item) => sum + Number(item.paid_amount), 0)
      const totalBalance = scoped.reduce((sum, item) => sum + Number(item.balance), 0)
      return {
        id: member.id,
        display_name: member.display_name,
        member_code: member.member_code,
        contributionCount: scoped.length,
        totalExpected: totalExpected.toFixed(2),
        totalPaid: totalPaid.toFixed(2),
        totalBalance: totalBalance.toFixed(2),
      }
    })
    .sort((a, b) => Number(b.totalBalance) - Number(a.totalBalance))
  })

const visiblePayments = computed<AuditorPaymentRow[]>(() => {
  return payments.value.slice(0, 10).map((payment) => {
    const contribution = contributionMap.value[payment.contribution_record_id]
    const member = contribution ? memberMap.value[contribution.membership_profile_id] : null
    return {
      ...payment,
      memberLabel: member ? `${member.display_name} (${member.member_code})` : 'Unknown member',
    }
  })
})

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString()
}

function formatPaymentMethod(value: string): string {
  return value.replace('_', ' ')
}

async function refreshAll() {
  clearError()
  actionError.value = ''
  await run(async () => {
    const [memberRows, contributionRows, summaryData, paymentRows] = await Promise.all([
      listMembers(),
      listContributions(selectedYear.value),
      getContributionSummary(selectedYear.value),
      listTenantPayments(),
    ])
    members.value = memberRows
    contributions.value = contributionRows
    summary.value = summaryData
    payments.value = paymentRows
  })
}

async function retryRefresh() {
  actionError.value = ''
  await retry(async () => {
    const [memberRows, contributionRows, summaryData, paymentRows] = await Promise.all([
      listMembers(),
      listContributions(selectedYear.value),
      getContributionSummary(selectedYear.value),
      listTenantPayments(),
    ])
    members.value = memberRows
    contributions.value = contributionRows
    summary.value = summaryData
    payments.value = paymentRows
  })
}

async function downloadReport() {
  exporting.value = true
  actionError.value = ''
  try {
    await exportCsv(exportFinanceReportCsv, 'finance-report.csv')
  } catch (err) {
    actionError.value = err instanceof Error ? err.message : 'Unable to export the finance report.'
  } finally {
    exporting.value = false
  }
}

const errorMessage = computed(() => actionError.value || error.value)

onMounted(refreshAll)
</script>

<style scoped>
.auditor-hero {
  background:
    radial-gradient(circle at top right, rgba(191, 219, 254, 0.35), transparent 32%),
    linear-gradient(135deg, #f6f8fb 0%, #ffffff 70%);
  border: 1px solid #dde6ef;
}

.hero-copy {
  max-width: 42rem;
}

.metric-card {
  border-radius: 1rem;
  padding: 1rem 1.1rem;
  border: 1px solid #dde6ef;
}
</style>
