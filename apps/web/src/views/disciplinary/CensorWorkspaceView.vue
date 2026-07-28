<template>
  <div class="p-4 p-lg-5">
    <div class="censor-hero rounded-4 p-4 p-lg-5 mb-4" data-testid="censor-workspace-hero">
      <div class="d-flex flex-column flex-xl-row justify-content-between gap-4">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary mb-2">
            {{ t('censor.kicker') }}
          </div>
          <h1 class="h3 fw-bold mb-2">{{ t('censor.title') }}</h1>
          <p class="text-muted mb-0 hero-copy">
            {{ t('censor.subtitle') }}
          </p>
        </div>
        <div class="d-flex gap-2 align-items-start">
          <button class="btn btn-outline-secondary btn-sm" type="button" @click="refreshAll" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
            {{ t('common.refresh') }}
          </button>
          <button
            v-if="canManageRecords"
            class="btn btn-primary btn-sm"
            type="button"
            @click="resetForm"
          >
            {{ t('censor.newRecord') }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger border-0 shadow-sm mb-4" role="alert">
      <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3">
        <div>
          <div class="fw-semibold mb-1">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ t('censor.workspaceErrorTitle') }}
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

    <div class="row g-3 mb-4">
      <div class="col-md-3" v-for="metric in metrics" :key="metric.label">
        <div class="metric-card h-100">
          <div class="text-muted small">{{ metric.label }}</div>
          <div class="fw-bold fs-4">{{ metric.value }}</div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-xl-4">
        <div v-if="canSearchMembers" class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <h2 class="h6 fw-bold mb-1">{{ t('censor.memberLookupTitle') }}</h2>
            <p class="small text-muted mb-3">{{ t('censor.memberLookupLead') }}</p>

            <div class="position-relative mb-3">
              <label class="visually-hidden" for="censor-member-search">{{ t('censor.searchMember') }}</label>
              <input
                id="censor-member-search"
                v-model.trim="memberSearch"
                class="form-control"
                :placeholder="t('censor.searchMember')"
                autocomplete="off"
                @focus="showMemberResults = true"
              />
              <div v-if="showMemberResults && memberSearch" class="list-group position-absolute w-100 shadow-sm discipline-member-results">
                <button
                  v-for="member in filteredMembers.slice(0, 8)"
                  :key="member.id"
                  class="list-group-item list-group-item-action text-start"
                  type="button"
                  @click="selectMember(member)"
                >
                  <span class="fw-semibold d-block">{{ member.display_name }}</span>
                  <span class="small text-muted">{{ member.member_code }} · {{ member.email || member.phone || t('censor.notProvided') }}</span>
                </button>
                <div v-if="filteredMembers.length === 0" class="list-group-item small text-muted">{{ t('censor.noMemberFound') }}</div>
              </div>
            </div>

            <label class="form-label" for="censor-member-list">{{ t('censor.chooseMemberFromList') }}</label>
            <select id="censor-member-list" v-model="selectedMemberId" class="form-select" @change="selectMemberById">
              <option value="">{{ t('censor.chooseMemberFromList') }}</option>
              <option v-for="member in members" :key="member.id" :value="member.id">
                {{ member.display_name }} · {{ member.member_code }}
              </option>
            </select>

            <div v-if="selectedMember" class="discipline-member-summary mt-3">
              <div class="d-flex justify-content-between gap-2 align-items-start">
                <div>
                  <div class="fw-semibold">{{ selectedMember.display_name }}</div>
                  <div class="small text-muted">{{ selectedMember.member_code }}</div>
                </div>
                <button class="btn btn-sm btn-link p-0" type="button" @click="clearSelectedMember">{{ t('common.reset') }}</button>
              </div>
              <div class="small text-muted mt-2 text-break">{{ selectedMember.email || selectedMember.phone || t('censor.notProvided') }}</div>
            </div>
          </div>
        </div>

        <div v-if="canManageRecords" class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h2 class="h6 fw-bold mb-0">
                {{ editingId ? t('censor.editRecord') : t('censor.createRecord') }}
              </h2>
              <span class="badge text-bg-light text-dark border">{{ records.length }} {{ t('common.records') }}</span>
            </div>

            <form class="vstack gap-3" @submit.prevent="saveRecord">
              <div>
                <label class="form-label" for="censor-member-select">{{ t('common.member') }}</label>
                <select
                  id="censor-member-select"
                  v-model="form.membership_profile_id"
                  class="form-select"
                  required
                  @change="selectMemberById"
                >
                  <option value="" disabled>{{ t('censor.selectMember') }}</option>
                  <option v-for="member in members" :key="member.id" :value="member.id">
                    {{ member.display_name }} ({{ member.member_code }})
                  </option>
                </select>
              </div>

              <div>
                <label class="form-label" for="censor-policy-select">Policy</label>
                <select id="censor-policy-select" v-model="form.policy_record_id" class="form-select">
                  <option value="">{{ t('censor.noPolicy') }}</option>
                  <option v-for="policy in policies" :key="policy.id" :value="policy.id">
                    {{ policy.title }} · {{ policy.category }}
                  </option>
                </select>
              </div>

              <div>
                <label class="form-label" for="censor-title-input">{{ t('common.title') }}</label>
                <input
                  id="censor-title-input"
                  v-model.trim="form.title"
                  class="form-control"
                  type="text"
                  required
                />
              </div>

              <div>
                <label class="form-label" for="censor-description-input">{{ t('common.description') }}</label>
                <textarea
                  id="censor-description-input"
                  v-model.trim="form.description"
                  class="form-control"
                  rows="4"
                />
              </div>

              <div class="row g-2">
                <div class="col-7">
                  <label class="form-label" for="censor-amount-input">{{ t('common.amount') }}</label>
                  <input
                    id="censor-amount-input"
                    v-model="form.amount"
                    class="form-control"
                    type="number"
                    step="0.01"
                    min="0"
                  />
                </div>
                <div class="col-5">
                  <label class="form-label" for="censor-currency-input">{{ t('common.currency') }}</label>
                  <input
                    id="censor-currency-input"
                    v-model.trim="form.currency"
                    class="form-control"
                    type="text"
                    maxlength="3"
                  />
                </div>
              </div>

              <div>
                <label class="form-label" for="censor-status-select">{{ t('common.status') }}</label>
                <select id="censor-status-select" v-model="form.status" class="form-select">
                  <option value="open">{{ t('disciplinary.open') }}</option>
                  <option value="under_review">{{ t('disciplinary.underReview') }}</option>
                  <option value="resolved">{{ t('disciplinary.resolved') }}</option>
                  <option value="waived">{{ t('disciplinary.waived') }}</option>
                </select>
              </div>

              <div class="d-flex gap-2">
                <button class="btn btn-primary" type="submit" :disabled="saving">
                  {{ saving ? t('common.saving') : editingId ? t('disciplinary.updateRecord') : t('disciplinary.createRecord') }}
                </button>
                <button class="btn btn-outline-secondary" type="button" @click="resetForm">
                  {{ t('common.reset') }}
                </button>
              </div>
            </form>
          </div>
        </div>

        <div v-else class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center gap-2 mb-3">
              <i class="bi bi-shield-lock fs-5 text-secondary"></i>
              <h2 class="h6 fw-bold mb-0">{{ t('censor.readOnlyTitle') }}</h2>
            </div>
            <p class="text-muted small mb-3">
              {{ t('censor.readOnlyDescription') }}
            </p>
            <div class="vstack gap-2 small">
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ t('censor.visibleRecords') }}</span>
                <span class="fw-semibold">{{ records.length }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ t('common.status') }}</span>
                <span class="fw-semibold">{{ t('censor.reviewOnly') }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="d-flex align-items-center gap-2 mb-3">
              <i class="bi bi-lock text-secondary"></i>
              <h2 class="h6 fw-bold mb-0">Privacy boundaries</h2>
            </div>
            <ul class="small text-muted mb-0 ps-3">
              <li>Only tenant-scoped records are loaded.</li>
              <li>Member details stay limited to the linked profile label and policy title.</li>
              <li>Every create, update, and delete action is audited on the backend.</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="col-xl-8">
        <div v-if="selectedMember" class="card shadow-sm border-0 mb-4 discipline-history-card">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-primary mb-1">{{ t('censor.memberHistoryKicker') }}</div>
                <h2 class="h5 fw-bold mb-1">{{ selectedMember.display_name }}</h2>
                <p class="text-muted small mb-0">{{ t('censor.memberHistoryLead') }}</p>
              </div>
              <span class="badge text-bg-primary align-self-start">{{ selectedMemberHistory.length }} {{ t('common.records') }}</span>
            </div>

            <div class="row g-2 mb-3">
              <div class="col-sm-4"><div class="history-metric"><span>{{ t('censor.historyTotal') }}</span><strong>{{ selectedMemberHistory.length }}</strong></div></div>
              <div class="col-sm-4"><div class="history-metric"><span>{{ t('censor.historyOpen') }}</span><strong class="text-danger">{{ selectedMemberOpenCount }}</strong></div></div>
              <div class="col-sm-4"><div class="history-metric"><span>{{ t('censor.historyAmount') }}</span><strong>{{ selectedMemberTotalAmount }}</strong></div></div>
            </div>

            <div v-if="selectedMemberHistory.length === 0" class="alert alert-light border mb-0">{{ t('censor.noMemberHistory') }}</div>
            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0 discipline-history-table">
                <thead>
                  <tr>
                    <th>{{ t('censor.historyDate') }}</th>
                    <th>{{ t('common.title') }}</th>
                    <th>{{ t('censor.historyCircumstances') }}</th>
                    <th>{{ t('censor.historyPolicy') }}</th>
                    <th>{{ t('common.amount') }}</th>
                    <th>{{ t('common.status') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="record in selectedMemberHistory" :key="record.id">
                    <td class="text-nowrap small">{{ formatDate(record.recorded_at) }}</td>
                    <td class="fw-semibold">{{ record.title }}</td>
                    <td class="small text-muted history-description">{{ record.description || t('censor.noCircumstances') }}</td>
                    <td class="small">{{ record.policy_title || '—' }}</td>
                    <td class="fw-semibold text-nowrap">{{ formatMoney(record.amount, record.currency) }}</td>
                    <td><span class="badge" :class="statusClass(record.status)">{{ statusLabel(record.status) }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-1">
                  Tenant disciplinary records
                </div>
                <h2 class="h6 fw-bold mb-0">Sanctions and compliance actions</h2>
              </div>
              <span class="badge text-bg-light border text-dark">{{ records.length }} items</span>
            </div>

            <div v-if="loading" class="text-muted py-5 text-center">
              {{ t('censor.loadingRecords') }}
            </div>

            <div v-else-if="records.length === 0" class="empty-state">
              <i class="bi bi-shield-lock display-6 text-secondary"></i>
              <p class="mb-1 fw-semibold">{{ t('censor.noRecords') }}</p>
              <p class="text-muted mb-0">
                {{ t('censor.noRecordsHint') }}
              </p>
            </div>

            <ResponsiveDataView v-else :items="records" :item-key="(record) => record.id" :mobile-aria-label="t('censor.title')">
              <template #thead>
                  <tr>
                    <th>{{ t('common.member') }}</th>
                    <th>{{ t('common.title') }}</th>
                    <th>Policy</th>
                    <th>{{ t('common.amount') }}</th>
                    <th>{{ t('common.status') }}</th>
                    <th>Recorded</th>
                    <th v-if="canManageRecords" class="text-end">Actions</th>
                  </tr>
              </template>
              <template #rows>
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
                    <td v-if="canManageRecords" class="text-end">
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
              </template>
              <template #mobile-title="{ item: record }">
                <div>{{ record.membership_display_name || t('common.member') }}</div>
                <div class="small text-muted">{{ record.title }}</div>
              </template>
              <template #mobile-status="{ item: record }">
                <span class="badge" :class="statusClass(record.status)">{{ record.status }}</span>
              </template>
              <template #mobile-fields="{ item: record }">
                <div class="om-data-card-row"><span class="om-data-card-label">Policy</span><span class="om-data-card-value">{{ record.policy_title || '—' }}</span></div>
                <div class="om-data-card-row"><span class="om-data-card-label">{{ t('common.amount') }}</span><span class="om-data-card-value text-nowrap fw-semibold">{{ record.amount }} {{ record.currency }}</span></div>
                <div class="om-data-card-row"><span class="om-data-card-label">Recorded</span><span class="om-data-card-value">{{ formatDate(record.recorded_at) }}</span></div>
                <p v-if="record.description" class="small text-muted mb-0">{{ record.description }}</p>
              </template>
              <template v-if="canManageRecords" #mobile-actions="{ item: record }">
                <button class="btn btn-outline-primary" type="button" @click="editRecord(record)">Edit</button>
                <button class="btn btn-outline-danger" type="button" @click="removeRecord(record)">Delete</button>
              </template>
            </ResponsiveDataView>
          </div>
        </div>
      </div>
    </div>
  </div>

  <ConfirmModal
    v-if="showDeleteModal && deletingItem"
    title="Delete disciplinary record"
    :message="`Delete disciplinary record &quot;${deletingItem.title}&quot;?`"
    @confirm="handleDelete"
    @cancel="showDeleteModal = false; deletingItem = null"
  />
</template>

<script setup lang="ts">
import ConfirmModal from '@/components/ConfirmModal.vue'
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import { useLocaleStore } from '@/stores/locale.store'
import ResponsiveDataView from '@/components/ui/ResponsiveDataView.vue'
import { useRecoveryState } from '@/composables/useRecoveryState'
import { listMembers, type MembershipProfileResponse } from '@/api/membership.api'
import { listPublicPolicies, type PolicyRecordResponse } from '@/api/policies.api'
import {
  createDisciplinaryRecord,
  deleteDisciplinaryRecord,
  listDisciplinaryRecords,
  updateDisciplinaryRecord,
  type CreateDisciplinaryPayload,
  type DisciplinaryRecordResponse,
  type UpdateDisciplinaryPayload,
} from '@/api/disciplinary.api'

const authStore = useAuthStore()
const localeStore = useLocaleStore()
const { loading, error, isRecovering, run, retry, clearError } = useRecoveryState()
const t = (key: string) => localeStore.t(key)

const saving = ref(false)
const records = ref<DisciplinaryRecordResponse[]>([])
const members = ref<MembershipProfileResponse[]>([])
const policies = ref<PolicyRecordResponse[]>([])
const editingId = ref<string | null>(null)
const showDeleteModal = ref(false)
const deletingItem = ref<DisciplinaryRecordResponse | null>(null)
const memberSearch = ref('')
const showMemberResults = ref(false)
const selectedMemberId = ref('')

const form = ref<CreateDisciplinaryPayload>({
  membership_profile_id: '',
  policy_record_id: null,
  title: '',
  description: '',
  amount: '0.00',
  currency: 'EUR',
  status: 'open',
})

const canManageRecords = computed(() =>
  authStore.hasAnyRole(['censor', 'principal_admin', 'admin']).value,
)
const canSearchMembers = computed(() =>
  authStore.hasAnyRole(['censor', 'president', 'secretary_general', 'principal_admin', 'admin']).value,
)
const filteredMembers = computed(() => {
  const query = memberSearch.value.toLocaleLowerCase()
  if (!query) return members.value
  return members.value.filter((member) =>
    [member.display_name, member.first_name, member.last_name, member.member_code, member.email, member.phone]
      .filter(Boolean)
      .join(' ')
      .toLocaleLowerCase()
      .includes(query),
  )
})
const selectedMember = computed(() =>
  members.value.find((member) => member.id === selectedMemberId.value) ?? null,
)
const selectedMemberHistory = computed(() =>
  records.value
    .filter((record) => record.membership_profile_id === selectedMemberId.value)
    .sort((left, right) => new Date(right.recorded_at).getTime() - new Date(left.recorded_at).getTime()),
)
const selectedMemberOpenCount = computed(() =>
  selectedMemberHistory.value.filter((record) => record.status === 'open' || record.status === 'under_review').length,
)
const selectedMemberTotalAmount = computed(() => {
  const totals = new Map<string, number>()
  selectedMemberHistory.value.forEach((record) => {
    totals.set(record.currency, (totals.get(record.currency) ?? 0) + Number(record.amount))
  })
  return [...totals.entries()].map(([currency, amount]) => formatMoney(amount, currency)).join(' · ') || '0.00 EUR'
})

const openCount = computed(() => records.value.filter((record) => record.status === 'open').length)
const reviewCount = computed(() => records.value.filter((record) => record.status === 'under_review').length)
const resolvedCount = computed(() =>
  records.value.filter((record) => record.status === 'resolved' || record.status === 'waived').length,
)

const metrics = computed(() => [
  { label: t('censor.totalRecords'), value: records.value.length },
  { label: t('censor.openCases'), value: openCount.value },
  { label: t('censor.underReview'), value: reviewCount.value },
  { label: t('censor.resolvedCases'), value: resolvedCount.value },
])

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
  records.value = await listDisciplinaryRecords()

  if (canSearchMembers.value) {
    members.value = await listMembers()
  } else {
    members.value = []
  }

  // Published policies are needed solely for a censor's creation form.
  policies.value = canManageRecords.value ? await listPublicPolicies() : []
}

async function refreshAll() {
  await run(refreshData)
}

async function retryAll() {
  await retry(refreshData)
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

function selectMember(member: MembershipProfileResponse) {
  selectedMemberId.value = member.id
  memberSearch.value = member.display_name
  showMemberResults.value = false
  if (canManageRecords.value) {
    form.value.membership_profile_id = member.id
  }
}

function selectMemberById() {
  const member = members.value.find((item) => item.id === form.value.membership_profile_id)
    ?? members.value.find((item) => item.id === selectedMemberId.value)
  if (member) {
    selectMember(member)
  }
}

function clearSelectedMember() {
  selectedMemberId.value = ''
  memberSearch.value = ''
  showMemberResults.value = true
  if (canManageRecords.value) {
    form.value.membership_profile_id = ''
  }
}

function editRecord(record: DisciplinaryRecordResponse) {
  editingId.value = record.id
  selectedMemberId.value = record.membership_profile_id
  memberSearch.value = members.value.find((member) => member.id === record.membership_profile_id)?.display_name ?? ''
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
  clearError()
  try {
    const payload = {
      membership_profile_id: form.value.membership_profile_id,
      policy_record_id: form.value.policy_record_id || null,
      title: form.value.title,
      description: form.value.description || null,
      amount: form.value.amount || '0.00',
      currency: form.value.currency || 'EUR',
      status: form.value.status ?? 'open',
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
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to save the disciplinary record.'
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
  clearError()
  try {
    await deleteDisciplinaryRecord(deletingItem.value.id)
    await refreshData()
    if (editingId.value === deletingItem.value.id) {
      resetForm()
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to delete the disciplinary record.'
  } finally {
    saving.value = false
    showDeleteModal.value = false
    deletingItem.value = null
  }
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString(localeStore.currentLocale === 'fr' ? 'fr-FR' : localeStore.currentLocale === 'de' ? 'de-DE' : 'en-US')
}

function formatMoney(amount: string | number, currency: string): string {
  return new Intl.NumberFormat(localeStore.currentLocale === 'fr' ? 'fr-FR' : localeStore.currentLocale === 'de' ? 'de-DE' : 'en-US', {
    style: 'currency',
    currency,
  }).format(Number(amount))
}

function statusLabel(status: string): string {
  const keyByStatus: Record<string, string> = {
    open: 'disciplinary.open',
    under_review: 'disciplinary.underReview',
    resolved: 'disciplinary.resolved',
    waived: 'disciplinary.waived',
  }
  return t(keyByStatus[status] || 'common.status')
}

onMounted(async () => {
  await refreshAll()
})
</script>

<style scoped>
.censor-hero {
  background:
    radial-gradient(circle at top right, rgba(254, 215, 170, 0.36), transparent 34%),
    linear-gradient(135deg, #f8f7f4 0%, #ffffff 70%);
  border: 1px solid #e5ddd1;
}

.hero-copy {
  max-width: 44rem;
}

.metric-card {
  border-radius: 1rem;
  padding: 1rem 1.1rem;
  border: 1px solid #e5ddd1;
  background: #fff;
}

.discipline-member-results {
  z-index: 1050;
  max-height: 17rem;
  overflow-y: auto;
}

.discipline-member-summary {
  border: 1px solid rgba(13, 110, 253, 0.25);
  border-radius: 0.75rem;
  background: rgba(13, 110, 253, 0.06);
  padding: 0.75rem;
}

.discipline-history-card {
  border-top: 4px solid var(--bs-primary) !important;
}

.history-metric {
  min-height: 4.75rem;
  padding: 0.75rem;
  border-radius: 0.75rem;
  background: var(--bs-light);
}

.history-metric span,
.history-metric strong {
  display: block;
}

.history-metric span {
  color: var(--bs-secondary-color);
  font-size: 0.8rem;
}

.history-metric strong {
  font-size: 1.1rem;
}

.discipline-history-table thead th {
  color: var(--bs-primary);
  background: rgba(13, 110, 253, 0.06);
  border-bottom-width: 2px;
}

.history-description {
  min-width: 14rem;
  max-width: 22rem;
}
</style>
