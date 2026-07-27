<template>
  <div class="p-4">
    <div class="d-flex flex-column flex-md-row align-items-md-start align-items-center justify-content-between gap-3 mb-4">
      <div>
        <h1 class="h4 fw-bold mb-0">{{ t('contributions.title') }}</h1>
        <p class="text-muted small mb-0">{{ t('contributions.subtitle') }}</p>
      </div>
      <div class="d-flex flex-wrap gap-2 align-items-center w-100 w-md-auto justify-content-end">
        <select v-model="selectedYear" class="form-select form-select-sm" style="width: auto" @change="loadData">
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
        <button class="btn btn-outline-secondary btn-sm" @click="exportContributions" :disabled="exporting">
          <i v-if="exporting" class="spinner-border spinner-border-sm me-1"></i>
          <i v-else class="bi bi-download me-1"></i>{{ t('common.exportCsv') }}
        </button>
        <button class="btn btn-outline-primary btn-sm" data-bs-toggle="modal" data-bs-target="#importContributionModal">
          <i class="bi bi-upload me-1"></i>{{ t('common.importCsv') }}
        </button>
        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createContributionModal">
          <i class="bi bi-plus-circle me-1"></i>{{ t('contributions.addContribution') }}
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger alert-dismissible small py-2 mb-3" role="alert">
      <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
      <button type="button" class="btn-close py-2" @click="error = ''"></button>
    </div>

    <!-- Summary cards -->
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
        <div class="card shadow-sm border-0"
          :class="Number(summary.total_balance) > 0 ? 'bg-danger-subtle' : 'bg-success-subtle'">
          <div class="card-body text-center py-3">
            <div class="text-muted small">{{ t('contributions.balance') }}</div>
            <div class="fw-bold fs-4">{{ summary.total_balance }} EUR</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('common.loading') }}</span>
      </div>
    </div>

    <!-- Contributions table -->
    <ResponsiveDataView v-else-if="contributions.length > 0" :items="contributions" :aria-label="t('contributions.listAriaLabel')">
      <template #thead>
        <tr>
          <th class="ps-4" scope="col">{{ t('common.year') }}</th>
          <th scope="col">{{ t('common.member') }}</th>
          <th scope="col">{{ t('contributions.expected') }}</th>
          <th scope="col">{{ t('contributions.paid') }}</th>
          <th scope="col">{{ t('contributions.balance') }}</th>
          <th scope="col">{{ t('common.status') }}</th>
          <th scope="col">{{ t('contributions.due') }}</th>
          <th class="text-end pe-4" scope="col">{{ t('common.actions') }}</th>
        </tr>
      </template>
      <template #rows>
        <tr v-for="contribution in contributions" :key="contribution.id">
          <td class="ps-4">{{ contribution.year }}</td>
          <td>
            <div class="fw-medium">{{ memberFor(contribution.membership_profile_id)?.display_name || t('common.member') }}</div>
            <div class="font-monospace small text-muted">{{ memberFor(contribution.membership_profile_id)?.member_code || contribution.membership_profile_id.slice(0, 8) }}</div>
          </td>
          <td>{{ contribution.expected_amount }}</td>
          <td>{{ contribution.paid_amount }}</td>
          <td class="fw-medium" :class="Number(contribution.balance) > 0 ? 'text-danger' : 'text-success'">
            {{ contribution.balance }}
          </td>
          <td><span class="badge" :class="statusBadgeClass(contribution.status)">{{ contribution.status }}</span></td>
          <td class="small">{{ contribution.due_date ? formatDate(contribution.due_date) : '-' }}</td>
          <td class="text-end pe-4">
            <button class="btn btn-sm btn-outline-primary me-1" :aria-label="t('contributions.recordPayment')" @click="openPaymentModal(contribution)">
              <i class="bi bi-cash"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" :aria-label="t('contributions.deleteContribution')" @click="confirmDeleteContribution(contribution)">
              <i class="bi bi-trash"></i>
            </button>
          </td>
        </tr>
      </template>
      <template #card="{ item: contribution }">
        <div class="d-flex align-items-start justify-content-between gap-3">
          <div class="min-w-0">
            <div class="fw-semibold">{{ memberFor(contribution.membership_profile_id)?.display_name || t('common.member') }}</div>
            <div class="small text-muted font-monospace">{{ memberFor(contribution.membership_profile_id)?.member_code || contribution.membership_profile_id.slice(0, 8) }}</div>
            <div class="small text-muted om-technical-value">{{ contribution.membership_profile_id }}</div>
          </div>
          <span class="badge" :class="statusBadgeClass(contribution.status)">{{ contribution.status }}</span>
        </div>
        <div class="row g-2 small mt-1">
          <div class="col-6"><div class="text-muted">{{ t('common.year') }}</div><div class="fw-semibold">{{ contribution.year }}</div></div>
          <div class="col-6"><div class="text-muted">{{ t('contributions.due') }}</div><div class="fw-semibold">{{ contribution.due_date ? formatDate(contribution.due_date) : '-' }}</div></div>
          <div class="col-4"><div class="text-muted">{{ t('contributions.expected') }}</div><div>{{ contribution.expected_amount }}</div></div>
          <div class="col-4"><div class="text-muted">{{ t('contributions.paid') }}</div><div>{{ contribution.paid_amount }}</div></div>
          <div class="col-4"><div class="text-muted">{{ t('contributions.balance') }}</div><div class="fw-semibold" :class="Number(contribution.balance) > 0 ? 'text-danger' : 'text-success'">{{ contribution.balance }}</div></div>
        </div>
        <div class="om-data-card-actions">
          <button class="btn btn-sm btn-outline-primary" type="button" @click="openPaymentModal(contribution)">
            <i class="bi bi-cash me-1"></i>{{ t('contributions.recordPayment') }}
          </button>
          <button class="btn btn-sm btn-outline-danger" type="button" @click="confirmDeleteContribution(contribution)">
            <i class="bi bi-trash me-1"></i>{{ t('common.delete') }}
          </button>
        </div>
      </template>
    </ResponsiveDataView>
    <div v-else class="empty-state">
      <i class="bi bi-cash-stack display-6 text-secondary"></i>
      <p class="mb-1 fw-semibold">{{ t('contributions.noRecords').replace('{year}', String(selectedYear)) }}</p>
      <p class="text-muted mb-0">{{ t('contributions.noRecordsHint') }}</p>
    </div>

    <ConfirmModal v-if="showDeleteModal && deletingContribution"
      :title="t('contributions.deleteContribution')"
      :message="`Delete contribution record for ${deletingContribution.year}?`"
      @confirm="handleDeleteContribution"
      @cancel="showDeleteModal = false; deletingContribution = null"
    />

    <!-- Import Contributions Modal -->
    <div class="modal fade" id="importContributionModal" tabindex="-1" aria-labelledby="importContributionModalLabel">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="importContributionModalLabel">{{ t('contributions.importTitle') }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" @click="resetContribImport"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('common.csvFile') }}</label>
              <input ref="contribImportFileInput" class="form-control form-control-sm" type="file" accept=".csv" @change="onContribImportFileChange" />
              <div class="form-text small">{{ t('contributions.requiredColumns') }}</div>
            </div>
            <div class="form-check mb-3">
              <input id="contribImportDryRun" v-model="contribImportDryRun" type="checkbox" class="form-check-input" />
              <label for="contribImportDryRun" class="form-check-label small">{{ t('common.dryRun') }}</label>
            </div>
            <div v-if="contribImportResult" class="mt-3">
              <hr />
              <div class="d-flex gap-3 mb-3">
                <span class="badge bg-secondary">{{ t('common.total') }}: {{ contribImportResult.total }}</span>
                <span class="badge bg-success">{{ t('common.successCount') }}: {{ contribImportResult.success_count }}</span>
                <span class="badge" :class="contribImportResult.error_count > 0 ? 'bg-danger' : 'bg-success'">{{ t('common.errorCount') }}: {{ contribImportResult.error_count }}</span>
              </div>
              <div v-if="contribImportResult.errors.length > 0" class="mb-3">
                <h6 class="small fw-bold text-danger">{{ t('common.validationErrors') }}</h6>
                <div class="table-responsive">
                  <table class="table table-sm small mb-0">
                    <thead><tr><th>{{ t('common.row') }}</th><th>{{ t('common.errorColumn') }}</th></tr></thead>
                    <tbody>
                      <tr v-for="err in contribImportResult.errors" :key="err.row">
                        <td>{{ err.row }}</td>
                        <td><div class="text-break">{{ err.message }}</div></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div v-if="contribImportResult.error_count === 0 && !contribImportDryRun" class="alert alert-success small py-2 mb-0">
                {{ t('contributions.importSuccess').replace('{count}', String(contribImportResult.success_count)) }}
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal" @click="resetContribImport">{{ t('common.cancel') }}</button>
            <button v-if="contribImportDryRun && contribImportResult && contribImportResult.error_count === 0" type="button" class="btn btn-sm btn-primary" @click="confirmContribImport" :disabled="contribImporting">
              {{ contribImporting ? t('common.importing') : t('common.confirmImport') }}
            </button>
            <button v-else type="button" class="btn btn-sm btn-primary" @click="handleContribImport" :disabled="contribImporting || !contribImportSelectedFile">
              {{ contribImporting ? t('common.importing') : contribImportDryRun ? t('common.validate') : t('common.import') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Contribution Modal -->
    <div class="modal fade" id="createContributionModal" tabindex="-1" aria-labelledby="createContributionModalLabel">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="createContributionModalLabel">{{ t('contributions.addContribution') }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('common.member') }}</label>
              <select v-model="contribForm.membership_profile_id" class="form-select form-select-sm" required>
                <option value="" disabled>{{ t('finance.selectMember') }}</option>
                <option v-for="m in members" :key="m.id" :value="m.id">
                  {{ m.display_name }} ({{ m.member_code }})
                </option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('common.year') }}</label>
              <input v-model.number="contribForm.year" type="number" class="form-control form-control-sm" required />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('contributions.expectedAmount') }}</label>
              <input v-model="contribForm.expected_amount" type="number" step="0.01" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('common.status') }}</label>
              <select v-model="contribForm.status" class="form-select form-select-sm">
                <option value="pending">Pending</option>
                <option value="paid">Paid</option>
                <option value="partial">Partial</option>
                <option value="overdue">Overdue</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">{{ t('common.cancel') }}</button>
            <button type="button" class="btn btn-sm btn-primary" @click="handleCreateContribution" :disabled="saving">
              {{ saving ? t('common.saving') : t('common.save') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Record Payment Modal -->
    <div class="modal fade" id="paymentModal" tabindex="-1" aria-labelledby="paymentModalLabel">
      <div class="modal-dialog modal-sm">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="paymentModalLabel">{{ t('contributions.recordPayment') }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('contributions.amountEur') }}</label>
              <input v-model="paymentForm.amount" type="number" step="0.01" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('contributions.paymentMethod') }}</label>
              <select v-model="paymentForm.payment_method" class="form-select form-select-sm">
                <option value="cash">{{ t('contributions.cash') }}</option>
                <option value="bank_transfer">{{ t('contributions.bankTransfer') }}</option>
                <option value="card">{{ t('contributions.card') }}</option>
                <option value="check">{{ t('contributions.check') }}</option>
                <option value="other">{{ t('contributions.other') }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('contributions.reference') }}</label>
              <input v-model="paymentForm.reference" class="form-control form-control-sm" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">{{ t('common.cancel') }}</button>
            <button type="button" class="btn btn-sm btn-primary" @click="handleRecordPayment" :disabled="saving">
              {{ saving ? t('common.saving') : t('common.save') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as bootstrap from 'bootstrap'
import ConfirmModal from '@/components/ConfirmModal.vue'
import ResponsiveDataView from '@/components/ui/ResponsiveDataView.vue'
import { listContributions, createContribution, deleteContribution, recordPayment, getContributionSummary, importContributionsCsv, exportContributionsCsv } from '@/api/contributions.api'
import { listMembers } from '@/api/membership.api'
import type { ContributionRecordResponse, ContributionSummary, ImportResult } from '@/api/contributions.api'
import type { MembershipProfileResponse } from '@/api/membership.api'
import { useCsvExport } from '@/composables/useCsvExport'
import { useLocaleStore } from '@/stores/locale.store'

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)

const loading = ref(true)
const error = ref('')
const saving = ref(false)
const contributions = ref<ContributionRecordResponse[]>([])
const members = ref<MembershipProfileResponse[]>([])

function memberFor(profileId: string) {
  return members.value.find((member) => member.id === profileId)
}
const summary = ref<ContributionSummary | null>(null)
const selectedYear = ref(new Date().getFullYear())
const years = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i)

const { exportCsv, exporting } = useCsvExport()

function setError(err: unknown) {
  error.value = (err as any)?.response?.data?.detail || (err as any)?.message || 'An unexpected error occurred'
}

const contribForm = ref({
  membership_profile_id: '',
  year: new Date().getFullYear(),
  expected_amount: '0.00',
  paid_amount: '0.00',
  status: 'pending',
})

const paymentForm = ref({
  contribution_record_id: '',
  amount: '0.00',
  payment_method: 'cash',
  reference: '',
})

const showDeleteModal = ref(false)
const deletingContribution = ref<ContributionRecordResponse | null>(null)

const contribImportSelectedFile = ref<File | null>(null)
const contribImportDryRun = ref(true)
const contribImporting = ref(false)
const contribImportResult = ref<ImportResult | null>(null)
const contribImportFileInput = ref<HTMLInputElement | null>(null)

function resetContribImport() {
  contribImportSelectedFile.value = null
  contribImportDryRun.value = true
  contribImporting.value = false
  contribImportResult.value = null
  if (contribImportFileInput.value) contribImportFileInput.value.value = ''
}

function onContribImportFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  contribImportSelectedFile.value = input.files?.[0] ?? null
  contribImportResult.value = null
}

async function handleContribImport() {
  if (!contribImportSelectedFile.value) return
  contribImporting.value = true
  try {
    contribImportResult.value = await importContributionsCsv(contribImportSelectedFile.value, contribImportDryRun.value)
  } finally { contribImporting.value = false }
}

async function confirmContribImport() {
  contribImportDryRun.value = false
  await handleContribImport()
  if (contribImportResult.value && contribImportResult.value.error_count > 0) {
    contribImportDryRun.value = true
  } else {
    await loadData()
  }
}

async function exportContributions() {
  try {
    await exportCsv(() => exportContributionsCsv(selectedYear.value), `contributions-${selectedYear.value}.csv`)
  } catch (err) { setError(err) }
}

function statusBadgeClass(status: string): string {
  const map: Record<string, string> = {
    paid: 'bg-success-subtle text-success',
    pending: 'bg-warning-subtle text-warning',
    partial: 'bg-info-subtle text-info',
    overdue: 'bg-danger-subtle text-danger',
    waived: 'bg-secondary-subtle text-secondary',
  }
  return map[status] || 'bg-secondary-subtle text-secondary'
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

async function loadData() {
  loading.value = true
  try {
    members.value = await listMembers()
    contributions.value = await listContributions(selectedYear.value)
    summary.value = await getContributionSummary(selectedYear.value)
  } catch (err) { setError(err) }
  finally { loading.value = false }
}

async function handleCreateContribution() {
  saving.value = true
  try {
    await createContribution(contribForm.value)
    await loadData()
    const modal = bootstrap.Modal.getInstance(document.getElementById('createContributionModal')!)
    modal?.hide()
    contribForm.value = { membership_profile_id: '', year: new Date().getFullYear(), expected_amount: '0.00', paid_amount: '0.00', status: 'pending' }
  } catch (err) { setError(err) }
  finally { saving.value = false }
}

function openPaymentModal(contribution: ContributionRecordResponse) {
  paymentForm.value = { contribution_record_id: contribution.id, amount: '0.00', payment_method: 'cash', reference: '' }
  nextTick(() => {
    const modal = new bootstrap.Modal(document.getElementById('paymentModal')!)
    modal.show()
  })
}

async function handleRecordPayment() {
  saving.value = true
  try {
    await recordPayment(paymentForm.value)
    await loadData()
    const modal = bootstrap.Modal.getInstance(document.getElementById('paymentModal')!)
    modal?.hide()
  } catch (err) { setError(err) }
  finally { saving.value = false }
}

function confirmDeleteContribution(contribution: ContributionRecordResponse) {
  deletingContribution.value = contribution
  showDeleteModal.value = true
}

async function handleDeleteContribution() {
  if (!deletingContribution.value) return
  saving.value = true
  try {
    await deleteContribution(deletingContribution.value.id)
    await loadData()
  } catch (err) { setError(err) }
  finally {
    saving.value = false
    showDeleteModal.value = false
    deletingContribution.value = null
  }
}

onMounted(loadData)
</script>
