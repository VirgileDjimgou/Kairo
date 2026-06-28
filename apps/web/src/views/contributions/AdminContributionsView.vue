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
        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createContributionModal">
          <i class="bi bi-plus-circle me-1"></i>Add contribution
        </button>
      </div>
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
    <div v-else class="card shadow-sm border-0">
      <div class="table-responsive">
        <table class="table table-hover mb-0 align-middle">
          <thead class="table-light">
            <tr>
              <th class="ps-4">Year</th>
              <th>Member</th>
              <th>Expected</th>
              <th>Paid</th>
              <th>Balance</th>
              <th>Status</th>
              <th>Due</th>
              <th class="text-end pe-4">Actions</th>
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
                <button class="btn btn-sm btn-outline-primary me-1" title="Record payment"
                  @click="openPaymentModal(c)">
                  <i class="bi bi-cash"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" title="Delete"
                  @click="confirmDeleteContribution(c)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
            <tr v-if="contributions.length === 0">
              <td colspan="8" class="text-center text-muted py-4">
                <i class="bi bi-cash-stack me-2"></i>No contribution records for {{ selectedYear }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Contribution Modal -->
    <div class="modal fade" id="createContributionModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add contribution</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">Member profile ID</label>
              <input v-model="contribForm.membership_profile_id" class="form-control form-control-sm" required />
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
    <div class="modal fade" id="paymentModal" tabindex="-1">
      <div class="modal-dialog modal-sm">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Record payment</h5>
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
import { listContributions, createContribution, deleteContribution, recordPayment, getContributionSummary } from '@/api/contributions.api'
import { listMembers } from '@/api/membership.api'
import type { ContributionRecordResponse, ContributionSummary } from '@/api/contributions.api'
import type { MembershipProfileResponse } from '@/api/membership.api'

const loading = ref(true)
const saving = ref(false)
const contributions = ref<ContributionRecordResponse[]>([])
const members = ref<MembershipProfileResponse[]>([])
const summary = ref<ContributionSummary | null>(null)
const selectedYear = ref(new Date().getFullYear())
const years = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i)

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

const deletingContribution = ref<ContributionRecordResponse | null>(null)

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
  } catch { /* handled by interceptor */ }
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
  } catch { /* handled by interceptor */ }
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
  } catch { /* handled by interceptor */ }
  finally { saving.value = false }
}

function confirmDeleteContribution(contribution: ContributionRecordResponse) {
  deletingContribution.value = contribution
  if (confirm(`Delete contribution record for ${contribution.year}?`)) {
    handleDeleteContribution(contribution.id)
  }
}

async function handleDeleteContribution(id: string) {
  saving.value = true
  try {
    await deleteContribution(id)
    await loadData()
  } catch { /* handled by interceptor */ }
  finally { saving.value = false }
}

onMounted(loadData)
</script>
