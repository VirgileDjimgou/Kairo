<template>
  <div class="p-4">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h1 class="h4 fw-bold mb-0">Contributions</h1>
        <p class="text-muted small mb-0">Manage member contributions and payments</p>
      </div>
      <div class="d-flex gap-2 align-items-center">
        <select v-model="selectedYear" class="form-select form-select-sm" style="width: auto" @change="loadData">
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
        <button class="btn btn-outline-secondary btn-sm" @click="exportContributions" :disabled="exporting">
          <i v-if="exporting" class="spinner-border spinner-border-sm me-1"></i>
          <i v-else class="bi bi-download me-1"></i>Export CSV
        </button>
        <button class="btn btn-outline-primary btn-sm" data-bs-toggle="modal" data-bs-target="#importContributionModal">
          <i class="bi bi-upload me-1"></i>Import CSV
        </button>
        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createContributionModal">
          <i class="bi bi-plus-circle me-1"></i>Add contribution
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
            <div class="text-muted small">Expected</div>
            <div class="fw-bold fs-4">{{ summary.total_expected }} EUR</div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm border-0 bg-success-subtle">
          <div class="card-body text-center py-3">
            <div class="text-muted small">Paid</div>
            <div class="fw-bold fs-4">{{ summary.total_paid }} EUR</div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm border-0"
          :class="Number(summary.total_balance) > 0 ? 'bg-danger-subtle' : 'bg-success-subtle'">
          <div class="card-body text-center py-3">
            <div class="text-muted small">Balance</div>
            <div class="fw-bold fs-4">{{ summary.total_balance }} EUR</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Contributions table -->
    <div v-else-if="contributions.length > 0" class="card shadow-sm border-0">
      <div class="table-responsive">
        <table class="table table-hover mb-0 align-middle" aria-label="Contributions list">
          <thead class="table-light">
            <tr>
              <th class="ps-4" scope="col">Year</th>
              <th scope="col">Member</th>
              <th scope="col">Expected</th>
              <th scope="col">Paid</th>
              <th scope="col">Balance</th>
              <th scope="col">Status</th>
              <th scope="col">Due</th>
              <th class="text-end pe-4" scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in contributions" :key="c.id">
              <td class="ps-4">{{ c.year }}</td>
              <td class="fw-medium font-monospace small">{{ c.membership_profile_id.slice(0, 8) }}…</td>
              <td>{{ c.expected_amount }}</td>
              <td>{{ c.paid_amount }}</td>
              <td class="fw-medium" :class="Number(c.balance) > 0 ? 'text-danger' : 'text-success'">
                {{ c.balance }}
              </td>
              <td>
                <span class="badge"
                  :class="statusBadgeClass(c.status)">{{ c.status }}</span>
              </td>
              <td class="small">{{ c.due_date ? formatDate(c.due_date) : '—' }}</td>
              <td class="text-end pe-4">
                <button class="btn btn-sm btn-outline-primary me-1" aria-label="Record payment"
                  @click="openPaymentModal(c)">
                  <i class="bi bi-cash"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" aria-label="Delete contribution"
                  @click="confirmDeleteContribution(c)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else class="empty-state">
      <i class="bi bi-cash-stack display-6 text-secondary"></i>
      <p class="mb-1 fw-semibold">No contribution records for {{ selectedYear }}</p>
      <p class="text-muted mb-0">Add contribution records manually or import them from a CSV file.</p>
    </div>

    <ConfirmModal v-if="showDeleteModal && deletingContribution"
      title="Delete contribution"
      :message="`Delete contribution record for ${deletingContribution.year}?`"
      @confirm="handleDeleteContribution"
      @cancel="showDeleteModal = false; deletingContribution = null"
    />

    <!-- Import Contributions Modal -->
    <div class="modal fade" id="importContributionModal" tabindex="-1" aria-labelledby="importContributionModalLabel">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="importContributionModalLabel">Import contributions from CSV</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" @click="resetContribImport"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">CSV file</label>
              <input ref="contribImportFileInput" class="form-control form-control-sm" type="file" accept=".csv" @change="onContribImportFileChange" />
              <div class="form-text small">Required columns: <code>member_code</code>, <code>year</code>, <code>expected_amount</code>. Optional: <code>paid_amount</code>, <code>status</code>.</div>
            </div>
            <div class="form-check mb-3">
              <input id="contribImportDryRun" v-model="contribImportDryRun" type="checkbox" class="form-check-input" />
              <label for="contribImportDryRun" class="form-check-label small">Dry run (validate only, no changes saved)</label>
            </div>
            <div v-if="contribImportResult" class="mt-3">
              <hr />
              <div class="d-flex gap-3 mb-3">
                <span class="badge bg-secondary">Total: {{ contribImportResult.total }}</span>
                <span class="badge bg-success">Success: {{ contribImportResult.success_count }}</span>
                <span class="badge" :class="contribImportResult.error_count > 0 ? 'bg-danger' : 'bg-success'">Errors: {{ contribImportResult.error_count }}</span>
              </div>
              <div v-if="contribImportResult.errors.length > 0" class="mb-3">
                <h6 class="small fw-bold text-danger">Validation errors</h6>
                <table class="table table-sm small mb-0">
                  <thead><tr><th>Row</th><th>Error</th></tr></thead>
                  <tbody>
                    <tr v-for="err in contribImportResult.errors" :key="err.row">
                      <td>{{ err.row }}</td>
                      <td>{{ err.message }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-if="contribImportResult.error_count === 0 && !contribImportDryRun" class="alert alert-success small py-2 mb-0">
                Successfully imported {{ contribImportResult.success_count }} contributions.
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal" @click="resetContribImport">Cancel</button>
            <button v-if="contribImportDryRun && contribImportResult && contribImportResult.error_count === 0" type="button" class="btn btn-sm btn-primary" @click="confirmContribImport" :disabled="contribImporting">
              {{ contribImporting ? 'Importing...' : 'Confirm import' }}
            </button>
            <button v-else type="button" class="btn btn-sm btn-primary" @click="handleContribImport" :disabled="contribImporting || !contribImportSelectedFile">
              {{ contribImporting ? 'Importing...' : contribImportDryRun ? 'Validate' : 'Import' }}
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
            <h5 class="modal-title" id="createContributionModalLabel">Add contribution</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">Member</label>
              <select v-model="contribForm.membership_profile_id" class="form-select form-select-sm" required>
                <option value="" disabled>Select member</option>
                <option v-for="m in members" :key="m.id" :value="m.id">
                  {{ m.display_name }} ({{ m.member_code }})
                </option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Year</label>
              <input v-model.number="contribForm.year" type="number" class="form-control form-control-sm" required />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Expected amount (EUR)</label>
              <input v-model="contribForm.expected_amount" type="number" step="0.01" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Status</label>
              <select v-model="contribForm.status" class="form-select form-select-sm">
                <option value="pending">Pending</option>
                <option value="paid">Paid</option>
                <option value="partial">Partial</option>
                <option value="overdue">Overdue</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-sm btn-primary" @click="handleCreateContribution" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save' }}
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
            <h5 class="modal-title" id="paymentModalLabel">Record payment</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">Amount (EUR)</label>
              <input v-model="paymentForm.amount" type="number" step="0.01" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Method</label>
              <select v-model="paymentForm.payment_method" class="form-select form-select-sm">
                <option value="cash">Cash</option>
                <option value="bank_transfer">Bank transfer</option>
                <option value="card">Card</option>
                <option value="check">Check</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Reference</label>
              <input v-model="paymentForm.reference" class="form-control form-control-sm" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-sm btn-primary" @click="handleRecordPayment" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save' }}
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
import { listContributions, createContribution, deleteContribution, recordPayment, getContributionSummary, importContributionsCsv, exportContributionsCsv } from '@/api/contributions.api'
import { listMembers } from '@/api/membership.api'
import type { ContributionRecordResponse, ContributionSummary, ImportResult } from '@/api/contributions.api'
import type { MembershipProfileResponse } from '@/api/membership.api'
import { useCsvExport } from '@/composables/useCsvExport'

const loading = ref(true)
const error = ref('')
const saving = ref(false)
const contributions = ref<ContributionRecordResponse[]>([])
const members = ref<MembershipProfileResponse[]>([])
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
