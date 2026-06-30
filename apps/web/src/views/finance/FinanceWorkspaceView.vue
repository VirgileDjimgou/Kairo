<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">Finance workspace</div>
        <h1 class="h4 fw-bold mb-1">Treasury operations</h1>
        <p class="text-muted mb-0">
          Review member balances, create contribution records, and record payments without opening the full admin console.
        </p>
      </div>
      <div class="d-flex gap-2 align-items-start">
        <select v-model="selectedYear" class="form-select form-select-sm" style="width: auto" @change="refreshFinanceData">
          <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
        </select>
        <button class="btn btn-outline-secondary btn-sm" type="button" @click="refreshAll" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
          Refresh
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger alert-dismissible small py-2 mb-4" role="alert">
      <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
      <button type="button" class="btn-close py-2" @click="error = ''"></button>
    </div>

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
        <div class="card shadow-sm border-0" :class="Number(summary.total_balance) > 0 ? 'bg-warning-subtle' : 'bg-success-subtle'">
          <div class="card-body text-center py-3">
            <div class="text-muted small">Outstanding balance</div>
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
              <h2 class="h6 fw-bold mb-0">Member balance lookup</h2>
              <span class="badge text-bg-light border text-dark">{{ members.length }} members</span>
            </div>

            <div class="mb-3">
              <label for="finance-balance-member" class="form-label small fw-medium">Member</label>
              <select
                id="finance-balance-member"
                v-model="selectedMemberId"
                class="form-select"
                @change="loadSelectedMemberBalance"
              >
                <option value="">Select a member</option>
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
                  <div class="text-muted">Expected</div>
                  <div class="fw-semibold">{{ selectedMemberBalance.total_expected }} EUR</div>
                </div>
                <div class="col-6">
                  <div class="text-muted">Paid</div>
                  <div class="fw-semibold">{{ selectedMemberBalance.total_paid }} EUR</div>
                </div>
                <div class="col-12">
                  <div class="text-muted">Balance</div>
                  <div class="fw-semibold" :class="Number(selectedMemberBalance.total_balance) > 0 ? 'text-danger' : 'text-success'">
                    {{ selectedMemberBalance.total_balance }} EUR
                  </div>
                </div>
              </div>
            </div>
            <p v-else class="text-muted small mb-0">
              Select a member to review the current contribution balance before recording a payment.
            </p>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <h2 class="h6 fw-bold mb-3">Create contribution record</h2>
            <form class="vstack gap-3" @submit.prevent="handleCreateContribution">
              <div>
                <label for="finance-create-member" class="form-label small fw-medium">Member</label>
                <select id="finance-create-member" v-model="createForm.membership_profile_id" class="form-select" required>
                  <option value="" disabled>Select member</option>
                  <option v-for="member in members" :key="member.id" :value="member.id">
                    {{ member.display_name }} ({{ member.member_code }})
                  </option>
                </select>
              </div>
              <div class="row g-2">
                <div class="col-6">
                  <label for="finance-create-year" class="form-label small fw-medium">Year</label>
                  <input id="finance-create-year" v-model.number="createForm.year" type="number" class="form-control" min="2000" max="2100" required />
                </div>
                <div class="col-6">
                  <label for="finance-create-status" class="form-label small fw-medium">Status</label>
                  <select id="finance-create-status" v-model="createForm.status" class="form-select">
                    <option value="pending">Pending</option>
                    <option value="partial">Partial</option>
                    <option value="paid">Paid</option>
                    <option value="overdue">Overdue</option>
                  </select>
                </div>
              </div>
              <div>
                <label for="finance-create-amount" class="form-label small fw-medium">Expected amount (EUR)</label>
                <input id="finance-create-amount" v-model="createForm.expected_amount" type="number" step="0.01" min="0" class="form-control" required />
              </div>
              <button class="btn btn-primary" type="submit" :disabled="savingContribution">
                {{ savingContribution ? 'Saving...' : 'Create contribution' }}
              </button>
            </form>
          </div>
        </div>
      </div>

      <div class="col-xl-8">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h2 class="h6 fw-bold mb-0">Record payment</h2>
              <span v-if="paymentTarget" class="badge text-bg-light border text-dark">{{ paymentTarget.year }}</span>
            </div>

            <div v-if="paymentTarget" class="border rounded-3 p-3 bg-light-subtle">
              <div class="fw-semibold">{{ memberLabel(paymentTarget.membership_profile_id) }}</div>
              <div class="small text-muted mb-3">
                Outstanding {{ paymentTarget.balance }} EUR for {{ paymentTarget.year }}
              </div>
              <form class="row g-3 align-items-end" @submit.prevent="handleRecordPayment">
                <div class="col-md-4">
                  <label for="finance-payment-amount" class="form-label small fw-medium">Amount (EUR)</label>
                  <input id="finance-payment-amount" v-model="paymentForm.amount" type="number" step="0.01" min="0.01" class="form-control" required />
                </div>
                <div class="col-md-4">
                  <label for="finance-payment-method" class="form-label small fw-medium">Method</label>
                  <select id="finance-payment-method" v-model="paymentForm.payment_method" class="form-select">
                    <option value="cash">Cash</option>
                    <option value="bank_transfer">Bank transfer</option>
                    <option value="card">Card</option>
                    <option value="check">Check</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label for="finance-payment-reference" class="form-label small fw-medium">Reference</label>
                  <input id="finance-payment-reference" v-model="paymentForm.reference" class="form-control" />
                </div>
                <div class="col-12 d-flex gap-2">
                  <button class="btn btn-primary" type="submit" :disabled="savingPayment">
                    {{ savingPayment ? 'Saving...' : 'Record payment' }}
                  </button>
                  <button class="btn btn-outline-secondary" type="button" @click="resetPaymentForm">
                    Clear
                  </button>
                </div>
              </form>
            </div>
            <p v-else class="text-muted small mb-0">
              Choose a contribution from the table below to start a payment entry.
            </p>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-0">
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="contributions.length === 0" class="empty-state p-5">
              <i class="bi bi-cash-stack display-6 text-secondary"></i>
              <p class="mb-1 fw-semibold">No contribution records for {{ selectedYear }}</p>
              <p class="text-muted mb-0">Create the first record for this financial year from the form on the left.</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0" aria-label="Finance contribution list">
                <thead class="table-light">
                  <tr>
                    <th class="ps-4" scope="col">Member</th>
                    <th scope="col">Year</th>
                    <th scope="col">Expected</th>
                    <th scope="col">Paid</th>
                    <th scope="col">Balance</th>
                    <th scope="col">Status</th>
                    <th scope="col">Updated</th>
                    <th class="text-end pe-4" scope="col">Action</th>
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
                      <button class="btn btn-sm btn-outline-primary" type="button" @click="selectPaymentTarget(contribution)">
                        Record payment
                      </button>
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
  recordPayment,
  type ContributionRecordResponse,
  type ContributionSummary,
} from '@/api/contributions.api'
import {
  getMemberBalance,
  listMembers,
  type MemberBalanceResponse,
  type MembershipProfileResponse,
} from '@/api/membership.api'
import { computed, onMounted, ref } from 'vue'

const loading = ref(true)
const error = ref('')
const savingContribution = ref(false)
const savingPayment = ref(false)

const members = ref<MembershipProfileResponse[]>([])
const contributions = ref<ContributionRecordResponse[]>([])
const summary = ref<ContributionSummary | null>(null)
const selectedMemberBalance = ref<MemberBalanceResponse | null>(null)
const selectedMemberId = ref('')
const paymentTarget = ref<ContributionRecordResponse | null>(null)

const currentYear = new Date().getFullYear()
const years = [currentYear - 1, currentYear, currentYear + 1]
const selectedYear = ref(currentYear)

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

const membersById = computed(() =>
  Object.fromEntries(members.value.map((member) => [member.id, member])),
)

function memberLabel(profileId: string): string {
  const member = membersById.value[profileId]
  if (!member) return 'Unknown member'
  return `${member.display_name} (${member.member_code})`
}

function formatDate(value: string | null): string {
  if (!value) return '—'
  return new Date(value).toLocaleDateString()
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

async function refreshFinanceData() {
  const [contributionRows, summaryData] = await Promise.all([
    listContributions(selectedYear.value),
    getContributionSummary(selectedYear.value),
  ])
  contributions.value = contributionRows
  summary.value = summaryData
}

async function loadSelectedMemberBalance() {
  if (!selectedMemberId.value) {
    selectedMemberBalance.value = null
    return
  }
  selectedMemberBalance.value = await getMemberBalance(selectedMemberId.value)
}

async function refreshAll() {
  loading.value = true
  error.value = ''
  try {
    members.value = await listMembers()
    await refreshFinanceData()
    if (selectedMemberId.value) {
      await loadSelectedMemberBalance()
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to load finance workspace.'
  } finally {
    loading.value = false
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
  error.value = ''
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
  error.value = ''
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
  try {
    members.value = await listMembers()
    resetCreateForm()
    await refreshAll()
  } catch (err) {
    loading.value = false
    error.value = err instanceof Error ? err.message : 'Unable to initialize the finance workspace.'
  }
})
</script>
