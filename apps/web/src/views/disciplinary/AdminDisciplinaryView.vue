<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          Discipline
        </div>
        <h1 class="h4 fw-bold mb-1">Disciplinary administration</h1>
        <p class="text-muted mb-0">
          Track open, under review, resolved, and waived records for tenant members.
        </p>
      </div>
      <button class="btn om-primary-btn align-self-start" type="button" @click="resetForm">
        New record
      </button>
    </div>

    <div class="row g-4">
      <div class="col-lg-4">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h2 class="h6 fw-bold mb-0">
                {{ editingId ? 'Edit record' : 'Create record' }}
              </h2>
              <span class="badge text-bg-light text-dark border">{{ records.length }} records</span>
            </div>

            <form class="vstack gap-3" @submit.prevent="saveRecord">
              <div>
                <label class="form-label">Member</label>
                <select v-model="form.membership_profile_id" class="form-select" required>
                  <option value="" disabled>Select member</option>
                  <option v-for="member in members" :key="member.id" :value="member.id">
                    {{ member.display_name }} ({{ member.member_code }})
                  </option>
                </select>
              </div>

              <div>
                <label class="form-label">Policy</label>
                <select v-model="form.policy_record_id" class="form-select">
                  <option value="">No linked policy</option>
                  <option v-for="policy in policies" :key="policy.id" :value="policy.id">
                    {{ policy.title }} · {{ policy.category }}
                  </option>
                </select>
              </div>

              <div>
                <label class="form-label">Title</label>
                <input v-model.trim="form.title" class="form-control" type="text" required />
              </div>

              <div>
                <label class="form-label">Description</label>
                <textarea v-model.trim="form.description" class="form-control" rows="4" />
              </div>

              <div class="row g-2">
                <div class="col-7">
                  <label class="form-label">Amount</label>
                  <input v-model="form.amount" class="form-control" type="number" step="0.01" min="0" />
                </div>
                <div class="col-5">
                  <label class="form-label">Currency</label>
                  <input v-model.trim="form.currency" class="form-control" type="text" maxlength="3" />
                </div>
              </div>

              <div>
                <label class="form-label">Status</label>
                <select v-model="form.status" class="form-select">
                  <option value="open">Open</option>
                  <option value="under_review">Under review</option>
                  <option value="resolved">Resolved</option>
                  <option value="waived">Waived</option>
                </select>
              </div>

              <div class="d-flex gap-2">
                <button class="btn btn-primary" type="submit" :disabled="saving">
                  {{ saving ? 'Saving...' : editingId ? 'Update record' : 'Create record' }}
                </button>
                <button class="btn btn-outline-secondary" type="button" @click="resetForm">
                  Reset
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-lg-8">
        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div v-if="loading" class="text-muted py-5 text-center">
              Loading disciplinary records...
            </div>

            <div v-else-if="records.length === 0" class="empty-state">
              <i class="bi bi-shield-lock display-6 text-secondary"></i>
              <p class="mb-1 fw-semibold">No records yet</p>
              <p class="text-muted mb-0">
                Create the first disciplinary or waiver record for this tenant.
              </p>
            </div>

            <div v-else class="table-responsive">
              <table class="table align-middle">
                <thead>
                  <tr>
                    <th>Member</th>
                    <th>Title</th>
                    <th>Policy</th>
                    <th>Amount</th>
                    <th>Status</th>
                    <th>Recorded</th>
                    <th class="text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="record in records" :key="record.id">
                    <td>
                      <div class="fw-semibold">{{ record.membership_display_name || 'Unknown member' }}</div>
                      <div class="small text-muted">{{ record.membership_profile_id }}</div>
                    </td>
                    <td>
                      <div class="fw-semibold">{{ record.title }}</div>
                      <div class="small text-muted">{{ record.description || 'No description provided.' }}</div>
                    </td>
                    <td class="small">{{ record.policy_title || '—' }}</td>
                    <td class="fw-semibold">{{ record.amount }} {{ record.currency }}</td>
                    <td>
                      <span class="badge" :class="statusClass(record.status)">{{ record.status }}</span>
                    </td>
                    <td class="small">{{ formatDate(record.recorded_at) }}</td>
                    <td class="text-end">
                      <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" type="button" @click="editRecord(record)">
                          Edit
                        </button>
                        <button class="btn btn-outline-danger" type="button" @click="removeRecord(record)">
                          Delete
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

  <ConfirmModal v-if="showDeleteModal && deletingItem"
    title="Delete disciplinary record"
    :message="`Delete disciplinary record &quot;${deletingItem.title}&quot;?`"
    @confirm="handleDelete"
    @cancel="showDeleteModal = false; deletingItem = null"
  />
</template>

<script setup lang="ts">
import ConfirmModal from '@/components/ConfirmModal.vue'
import { onMounted, ref } from 'vue'
import { listMembers, type MembershipProfileResponse } from '@/api/membership.api'
import { listPolicies, type PolicyRecordResponse } from '@/api/policies.api'
import {
  createDisciplinaryRecord,
  deleteDisciplinaryRecord,
  listDisciplinaryRecords,
  updateDisciplinaryRecord,
  type CreateDisciplinaryPayload,
  type DisciplinaryRecordResponse,
  type UpdateDisciplinaryPayload,
} from '@/api/disciplinary.api'

const loading = ref(true)
const saving = ref(false)
const records = ref<DisciplinaryRecordResponse[]>([])
const members = ref<MembershipProfileResponse[]>([])
const policies = ref<PolicyRecordResponse[]>([])
const editingId = ref<string | null>(null)
const showDeleteModal = ref(false)
const deletingItem = ref<DisciplinaryRecordResponse | null>(null)

const form = ref<CreateDisciplinaryPayload>({
  membership_profile_id: '',
  policy_record_id: null,
  title: '',
  description: '',
  amount: '0.00',
  currency: 'EUR',
  status: 'open',
})

function statusClass(status: string): string {
  const map: Record<string, string> = {
    open: 'bg-danger-subtle text-danger border border-danger-subtle',
    under_review: 'bg-warning-subtle text-warning border border-warning-subtle',
    resolved: 'bg-success-subtle text-success border border-success-subtle',
    waived: 'bg-secondary-subtle text-secondary border border-secondary-subtle',
  }
  return map[status] || 'bg-light text-dark border'
}

async function refreshData() {
  loading.value = true
  try {
    const [recordList, memberList, policyList] = await Promise.all([
      listDisciplinaryRecords(),
      listMembers(),
      listPolicies(),
    ])
    records.value = recordList
    members.value = memberList
    policies.value = policyList
  } finally {
    loading.value = false
  }
}

function resetForm() {
  editingId.value = null
  form.value = {
    membership_profile_id: '',
    policy_record_id: null,
    title: '',
    description: '',
    amount: '0.00',
    currency: 'EUR',
    status: 'open',
  }
}

function editRecord(record: DisciplinaryRecordResponse) {
  editingId.value = record.id
  form.value = {
    membership_profile_id: record.membership_profile_id,
    policy_record_id: record.policy_record_id,
    title: record.title,
    description: record.description ?? '',
    amount: record.amount,
    currency: record.currency,
    status: record.status,
  }
}

async function saveRecord() {
  saving.value = true
  try {
    const payload = {
      membership_profile_id: form.value.membership_profile_id,
      policy_record_id: form.value.policy_record_id || null,
      title: form.value.title,
      description: form.value.description || null,
      amount: form.value.amount || '0.00',
      currency: form.value.currency || 'EUR',
      status: form.value.status,
    }
    if (editingId.value) {
      const updatePayload: UpdateDisciplinaryPayload = {
        policy_record_id: payload.policy_record_id,
        title: payload.title,
        description: payload.description,
        amount: payload.amount,
        currency: payload.currency,
        status: payload.status,
      }
      await updateDisciplinaryRecord(editingId.value, updatePayload)
    } else {
      await createDisciplinaryRecord(payload as CreateDisciplinaryPayload)
    }
    await refreshData()
    resetForm()
  } finally {
    saving.value = false
  }
}

function removeRecord(record: DisciplinaryRecordResponse) {
  deletingItem.value = record
  showDeleteModal.value = true
}

async function handleDelete() {
  if (!deletingItem.value) return
  saving.value = true
  try {
    await deleteDisciplinaryRecord(deletingItem.value.id)
    await refreshData()
    if (editingId.value === deletingItem.value.id) {
      resetForm()
    }
  } finally {
    saving.value = false
    showDeleteModal.value = false
    deletingItem.value = null
  }
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString()
}

onMounted(async () => {
  await refreshData()
})
</script>
