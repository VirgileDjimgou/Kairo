<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          {{ t('policies.kicker') }}
        </div>
        <h1 class="h4 fw-bold mb-1">{{ t('policies.adminTitle') }}</h1>
        <p class="text-muted mb-0">
          {{ t('policies.adminSubtitle') }}
        </p>
      </div>
      <button class="btn om-primary-btn align-self-start" type="button" @click="resetForm">
        {{ t('policies.newPolicy') }}
      </button>
    </div>

    <div class="row g-4">
      <div class="col-lg-4">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h2 class="h6 fw-bold mb-0">
                {{ editingId ? t('policies.editPolicy') : t('policies.createPolicy') }}
              </h2>
              <span class="badge text-bg-light text-dark border">
                {{ policies.length }} {{ t('common.records') }}
              </span>
            </div>

            <form class="vstack gap-3" @submit.prevent="savePolicy">
              <div>
                <label class="form-label">{{ t('common.title') }}</label>
                <input v-model.trim="form.title" class="form-control" type="text" required />
              </div>

              <div>
                <label class="form-label">{{ t('common.category') }}</label>
                <input v-model.trim="form.category" class="form-control" type="text" list="policy-category-list" required />
                <datalist id="policy-category-list">
                  <option v-for="category in categories" :key="category" :value="category" />
                </datalist>
              </div>

              <div>
                <label class="form-label">{{ t('common.description') }}</label>
                <textarea v-model.trim="form.description" class="form-control" rows="4" />
              </div>

              <div>
                <label class="form-label">{{ t('policies.linkedDocument') }}</label>
                <select v-model="form.document_id" class="form-select">
                  <option value="">{{ t('common.noDocument') }}</option>
                  <option v-for="document in documents" :key="document.id" :value="document.id">
                    {{ document.title }}
                  </option>
                </select>
              </div>

              <div>
                <label class="form-label">{{ t('common.status') }}</label>
                <select v-model="form.status" class="form-select">
                  <option value="draft">{{ t('common.draft') }}</option>
                  <option value="published">{{ t('common.published') }}</option>
                  <option value="archived">{{ t('common.archived') }}</option>
                </select>
              </div>

              <div class="d-flex gap-2">
                <button class="btn btn-primary" type="submit" :disabled="saving">
                  {{ saving ? t('common.saving') : editingId ? t('policies.updatePolicy') : t('policies.createPolicy') }}
                </button>
                <button class="btn btn-outline-secondary" type="button" @click="resetForm">
                  {{ t('common.reset') }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-lg-8">
        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div v-if="error" class="alert alert-warning border-0 shadow-sm mb-4" role="alert">
              <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
                <div>
                  <div class="fw-semibold">
                    <i class="bi bi-exclamation-triangle me-2"></i>{{ t('policies.workspaceErrorTitle') }}
                  </div>
                  <p class="small mb-0 mt-2">{{ error }}</p>
                  <p class="mb-0 small text-muted mt-1">{{ t('common.recoveryHint') }}</p>
                </div>
                <button class="btn btn-outline-secondary btn-sm align-self-start" type="button" @click="retryPolicies" :disabled="isRecovering">
                  <span v-if="isRecovering" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
                  {{ isRecovering ? t('common.loading') : t('common.retry') }}
                </button>
              </div>
            </div>

            <div v-if="actionError" class="alert alert-danger alert-dismissible small py-2 mb-3" role="alert">
              <i class="bi bi-exclamation-triangle me-1"></i>{{ actionError }}
              <button type="button" class="btn-close py-2" @click="actionError = ''"></button>
            </div>

            <div v-if="loading" class="text-muted py-5 text-center">
              {{ t('policies.loadingPolicies') }}
            </div>

            <div v-else-if="policies.length === 0" class="empty-state">
              <i class="bi bi-journal-check display-6 text-secondary"></i>
              <p class="mb-1 fw-semibold">{{ t('policies.noPolicies') }}</p>
              <p class="text-muted mb-0">
                {{ t('policies.noPoliciesHint') }}
              </p>
            </div>

            <div v-else class="table-responsive">
              <table class="table align-middle">
                <thead>
                  <tr>
                    <th>{{ t('common.title') }}</th>
                    <th>{{ t('common.category') }}</th>
                    <th>{{ t('common.status') }}</th>
                    <th>{{ t('policies.linkedDocument') }}</th>
                    <th>{{ t('common.updated') }}</th>
                    <th class="text-end">{{ t('common.actions') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="policy in policies" :key="policy.id">
                    <td>
                      <div class="fw-semibold">{{ policy.title }}</div>
                      <div class="small text-muted">
                        {{ policy.description || 'No description provided.' }}
                      </div>
                    </td>
                    <td>{{ policy.category }}</td>
                    <td>
                      <span class="badge" :class="statusClass(policy.status)">{{ policy.status }}</span>
                    </td>
                    <td class="small">{{ policy.document_title || '—' }}</td>
                    <td class="small">{{ formatDate(policy.updated_at) }}</td>
                    <td class="text-end">
                      <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" type="button" @click="editPolicy(policy)">
                          {{ t('common.edit') }}
                        </button>
                        <button class="btn btn-outline-danger" type="button" @click="removePolicy(policy)">
                          {{ t('common.delete') }}
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
    :title="t('policies.deletePolicy')"
    :message="`Delete policy &quot;${deletingItem.title}&quot;?`"
    @confirm="handleDelete"
    @cancel="showDeleteModal = false; deletingItem = null"
  />
</template>

<script setup lang="ts">
import ConfirmModal from '@/components/ConfirmModal.vue'
import { onMounted, ref } from 'vue'
import { useRecoveryState } from '@/composables/useRecoveryState'
import { useLocaleStore } from '@/stores/locale.store'
import { listDocuments, type DocumentListItemResponse } from '@/api/documents.api'
import {
  createPolicy,
  deletePolicy,
  listPolicies,
  listPolicyCategories,
  updatePolicy,
  type CreatePolicyPayload,
  type PolicyRecordResponse,
  type UpdatePolicyPayload,
} from '@/api/policies.api'

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)

const { loading, error, isRecovering, run, retry, clearError } = useRecoveryState()
const saving = ref(false)
const policies = ref<PolicyRecordResponse[]>([])
const categories = ref<string[]>([])
const documents = ref<DocumentListItemResponse[]>([])
const editingId = ref<string | null>(null)
const showDeleteModal = ref(false)
const deletingItem = ref<PolicyRecordResponse | null>(null)
const actionError = ref('')

const form = ref<CreatePolicyPayload>({
  title: '',
  category: '',
  description: '',
  document_id: null,
  status: 'published',
})

function statusClass(status: string): string {
  const map: Record<string, string> = {
    draft: 'bg-warning-subtle text-warning border border-warning-subtle',
    published: 'bg-success-subtle text-success border border-success-subtle',
    archived: 'bg-secondary-subtle text-secondary border border-secondary-subtle',
  }
  return map[status] || 'bg-light text-dark border'
}

function setActionError(err: unknown) {
  actionError.value =
    (err as any)?.response?.data?.detail ||
    (err as any)?.message ||
    localeStore.t('common.error')
}

async function loadPolicies() {
  const [policyList, categoryList, documentList] = await Promise.all([
    listPolicies(),
    listPolicyCategories(),
    listDocuments(),
  ])
  policies.value = policyList
  categories.value = categoryList.categories
  documents.value = documentList
}

async function refreshPolicies() {
  actionError.value = ''
  clearError()
  await run(loadPolicies)
}

async function retryPolicies() {
  actionError.value = ''
  await retry(loadPolicies)
}

function resetForm() {
  editingId.value = null
  form.value = {
    title: '',
    category: '',
    description: '',
    document_id: null,
    status: 'published',
  }
}

function editPolicy(policy: PolicyRecordResponse) {
  editingId.value = policy.id
  form.value = {
    title: policy.title,
    category: policy.category,
    description: policy.description ?? '',
    document_id: policy.document_id,
    status: policy.status,
  }
}

async function savePolicy() {
  saving.value = true
  actionError.value = ''
  try {
    const payload = {
      title: form.value.title,
      category: form.value.category,
      description: form.value.description || null,
      document_id: form.value.document_id || null,
      status: form.value.status,
    }
    if (editingId.value) {
      await updatePolicy(editingId.value, payload as UpdatePolicyPayload)
    } else {
      await createPolicy(payload as CreatePolicyPayload)
    }
    await refreshPolicies()
    resetForm()
  } catch (err) {
    setActionError(err)
  } finally {
    saving.value = false
  }
}

function removePolicy(policy: PolicyRecordResponse) {
  deletingItem.value = policy
  showDeleteModal.value = true
}

async function handleDelete() {
  if (!deletingItem.value) return
  saving.value = true
  actionError.value = ''
  try {
    await deletePolicy(deletingItem.value.id)
    await refreshPolicies()
    if (editingId.value === deletingItem.value.id) {
      resetForm()
    }
  } catch (err) {
    setActionError(err)
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
  await refreshPolicies()
})
</script>
