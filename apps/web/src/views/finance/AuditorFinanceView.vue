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
        <div class="auditor-actions">
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
          <button class="btn btn-outline-primary btn-sm" type="button" @click="downloadMemberReport('xlsx')" :disabled="exporting">
            {{ t('finance.exportExcel') }}
          </button>
          <button class="btn btn-outline-primary btn-sm" type="button" @click="downloadMemberReport('pdf')" :disabled="exporting">
            {{ t('finance.exportPdf') }}
          </button>
          <button class="btn btn-outline-success btn-sm" type="button" @click="shareWhatsappSummary" :disabled="exporting">
            {{ t('finance.copyForWhatsapp') }}
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

    <section class="card shadow-sm border-0 mb-4 auditor-member-lookup">
      <div class="card-body p-4">
        <div class="text-uppercase small fw-semibold text-secondary mb-1">{{ t('finance.memberLookup') }}</div>
        <h2 class="h6 fw-bold mb-3">{{ t('finance.memberFinanceSearchTitle') }}</h2>
        <div class="position-relative">
          <input v-model.trim="memberSearch" class="form-control" :placeholder="t('finance.memberSearchPlaceholder')" @focus="showMemberResults = true" />
          <div v-if="showMemberResults && memberSearch" class="list-group position-absolute w-100 shadow-sm auditor-member-results">
            <button v-for="member in filteredMembers.slice(0, 8)" :key="member.id" class="list-group-item list-group-item-action text-start" type="button" @click="selectMember(member)">
              <span class="fw-semibold">{{ member.display_name }}</span><span class="small text-muted ms-2">{{ member.member_code }}</span>
            </button>
            <div v-if="filteredMembers.length === 0" class="list-group-item small text-muted">{{ t('finance.noMemberFound') }}</div>
          </div>
        </div>
        <div v-if="selectedStatement" class="auditor-selected-member mt-3 rounded-3 p-3">
          <div class="d-flex justify-content-between gap-2"><div><strong>{{ selectedStatement.profile.display_name }}</strong><div class="small text-muted">{{ selectedStatement.profile.member_code }}</div></div><button class="btn-close" type="button" :aria-label="t('common.close')" @click="selectedStatement = null"></button></div>
          <div class="row g-2 text-center small mt-2">
            <div class="col-4"><div class="metric expected"><span>{{ t('contributions.expected') }}</span><strong>{{ selectedStatement.summary.total_expected }} €</strong></div></div>
            <div class="col-4"><div class="metric paid"><span>{{ t('contributions.paid') }}</span><strong>{{ selectedStatement.summary.total_paid }} €</strong></div></div>
            <div class="col-4"><div class="metric balance"><span>{{ t('contributions.balance') }}</span><strong>{{ selectedStatement.summary.total_balance }} €</strong></div></div>
          </div>
          <div class="small mt-3"><strong>{{ t('finance.contributionHistory') }}</strong></div>
          <div v-for="contribution in selectedStatement.contributions" :key="contribution.id" class="d-flex justify-content-between border-top pt-2 mt-2 small"><span>{{ contribution.year }} · {{ contribution.status }}</span><span>{{ contribution.paid_amount }} / {{ contribution.expected_amount }} € · <strong>{{ contribution.balance }} €</strong></span></div>
        </div>
      </div>
    </section>

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

            <ResponsiveDataView v-else :items="memberRows" :item-key="(row) => row.id" :mobile-aria-label="t('auditor.memberBalances')">
              <template #thead>
                  <tr>
                    <th class="ps-4" scope="col">{{ t('common.member') }}</th>
                    <th scope="col">{{ t('contributions.expected') }}</th>
                    <th scope="col">{{ t('contributions.paid') }}</th>
                    <th scope="col">Balance</th>
                    <th class="pe-4" scope="col">{{ t('common.records') }}</th>
                  </tr>
              </template>
              <template #rows>
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
              </template>
              <template #mobile-title="{ item: row }">
                <div>{{ row.display_name }}</div>
                <div class="small text-muted font-monospace">{{ row.member_code }}</div>
              </template>
              <template #mobile-status="{ item: row }">
                <span class="badge" :class="Number(row.totalBalance) > 0 ? 'text-bg-danger' : 'text-bg-success'">
                  {{ Number(row.totalBalance) > 0 ? t('finance.outstandingBalance') : t('contributions.paid') }}
                </span>
              </template>
              <template #mobile-fields="{ item: row }">
                <div class="om-data-card-row"><span class="om-data-card-label">{{ t('contributions.expected') }}</span><span class="om-data-card-value text-nowrap">{{ row.totalExpected }} EUR</span></div>
                <div class="om-data-card-row"><span class="om-data-card-label">{{ t('contributions.paid') }}</span><span class="om-data-card-value text-nowrap">{{ row.totalPaid }} EUR</span></div>
                <div class="om-data-card-row"><span class="om-data-card-label">{{ t('finance.outstandingBalance') }}</span><span class="om-data-card-value text-nowrap fw-semibold" :class="Number(row.totalBalance) > 0 ? 'text-danger' : 'text-success'">{{ row.totalBalance }} EUR</span></div>
                <div class="om-data-card-row"><span class="om-data-card-label">{{ t('common.records') }}</span><span class="om-data-card-value">{{ row.contributionCount }}</span></div>
              </template>
            </ResponsiveDataView>
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
  exportMemberFinanceReport,
  getContributionSummary,
  listContributions,
  listTenantPayments,
  type ContributionRecordResponse,
  type ContributionSummary,
  type PaymentRecordResponse,
  type MemberFinanceExportFormat,
} from '@/api/contributions.api'
import { getMemberStatement, listMembers, type MemberStatementResponse, type MembershipProfileResponse } from '@/api/membership.api'
import { useCsvExport } from '@/composables/useCsvExport'
import { useRecoveryState } from '@/composables/useRecoveryState'
import { useLocaleStore } from '@/stores/locale.store'
import ResponsiveDataView from '@/components/ui/ResponsiveDataView.vue'
import { notifyOperation } from '@/services/operation-notifications'
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
const memberSearch = ref('')
const showMemberResults = ref(false)
const selectedStatement = ref<MemberStatementResponse | null>(null)

const currentYear = new Date().getFullYear()
const years = [currentYear - 1, currentYear, currentYear + 1]
const selectedYear = ref(currentYear)
const { exportCsv } = useCsvExport()

const memberMap = computed(() =>
  Object.fromEntries(members.value.map((member) => [member.id, member])),
)

const filteredMembers = computed(() => {
  const query = memberSearch.value.toLocaleLowerCase()
  if (!query) return members.value
  return members.value.filter((member) =>
    `${member.display_name} ${member.first_name} ${member.last_name} ${member.member_code} ${member.phone || ''} ${member.email || ''}`
      .toLocaleLowerCase()
      .includes(query),
  )
})

async function selectMember(member: MembershipProfileResponse) {
  memberSearch.value = member.display_name
  showMemberResults.value = false
  selectedStatement.value = await getMemberStatement(member.id)
}

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

async function downloadMemberReport(format: Exclude<MemberFinanceExportFormat, 'whatsapp'>) {
  exporting.value = true
  actionError.value = ''
  try {
    const blob = await exportMemberFinanceReport(format, selectedYear.value)
    downloadBlob(blob, `rapport-financier-${selectedYear.value}.${format}`)
  } catch (err) {
    actionError.value = err instanceof Error ? err.message : t('finance.exportFailed')
  } finally {
    exporting.value = false
  }
}

async function shareWhatsappSummary() {
  exporting.value = true
  actionError.value = ''
  try {
    const summary = await (await exportMemberFinanceReport('whatsapp', selectedYear.value)).text()
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(summary)
      notifyOperation({ level: 'success', messageKey: 'finance.whatsappCopied' })
    } else {
      downloadBlob(new Blob([summary], { type: 'text/plain;charset=utf-8' }), `rapport-financier-${selectedYear.value}-whatsapp.txt`)
      notifyOperation({ level: 'info', messageKey: 'finance.whatsappFileDownloaded' })
    }
  } catch (err) {
    if ((err as DOMException)?.name !== 'AbortError') actionError.value = err instanceof Error ? err.message : t('finance.exportFailed')
  } finally {
    exporting.value = false
  }
}

function downloadBlob(blob: Blob, filename: string) {
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
  URL.revokeObjectURL(link.href)
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

.auditor-actions {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.auditor-actions .btn,
.auditor-actions .form-select {
  min-height: 44px;
}

.auditor-member-lookup { border-top: 4px solid #5b8def; }
.auditor-member-results { z-index: 1040; max-height: 17rem; overflow-y: auto; }
.auditor-selected-member { background: #f7fbff; border: 1px solid #bdd6fb; }
.metric { border-radius: .75rem; padding: .5rem .25rem; display: grid; gap: .2rem; }
.metric span { color: var(--bs-secondary-color); font-size: .72rem; }
.metric.expected { background: #dcecff; }.metric.paid { background: #d9f2e5; }.metric.balance { background: #fff0c8; }

@media (max-width: 767.98px) {
  .auditor-actions {
    display: grid;
    width: 100%;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .auditor-actions .form-select {
    width: 100% !important;
  }

  .auditor-actions .btn {
    width: 100%;
    white-space: normal;
  }

  .auditor-actions .btn-primary,
  .auditor-actions .btn-outline-primary,
  .auditor-actions .btn-outline-success {
    grid-column: 1 / -1;
  }
}
</style>
