<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          Policies
        </div>
        <h1 class="h4 fw-bold mb-1">Policy administration</h1>
        <p class="text-muted mb-0">
          Create, update, archive, and publish tenant policy records.
        </p>
      </div>
      <button class="btn om-primary-btn align-self-start" type="button" @click="resetForm">
        New policy
      </button>
    </div>

    <div class="row g-4">
      <div class="col-lg-4">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h2 class="h6 fw-bold mb-0">
                {{ editingId ? 'Edit policy' : 'Create policy' }}
              </h2>
              <span class="badge text-bg-light text-dark border">
                {{ policies.length }} records
              </span>
            </div>

            <form class="vstack gap-3" @submit.prevent="savePolicy">
              <div>
                <label class="form-label">Title</label>
                <input v-model.trim="form.title" class="form-control" type="text" required />
              </div>

              <div>
                <label class="form-label">Category</label>
                <input v-model.trim="form.category" class="form-control" type="text" list="policy-category-list" required />
                <datalist id="policy-category-list">
                  <option v-for="category in categories" :key="category" :value="category" />
                </datalist>
              </div>

              <div>
                <label class="form-label">Description</label>
                <textarea v-model.trim="form.description" class="form-control" rows="4" />
              </div>

              <div>
                <label class="form-label">Linked document</label>
                <select v-model="form.document_id" class="form-select">
                  <option value="">No document</option>
                  <option v-for="document in documents" :key="document.id" :value="document.id">
                    {{ document.title }}
                  </option>
                </select>
              </div>

              <div>
                <label class="form-label">Status</label>
                <select v-model="form.status" class="form-select">
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                  <option value="archived">Archived</option>
                </select>
              </div>

              <div class="d-flex gap-2">
                <button class="btn btn-primary" type="submit" :disabled="saving">
                  {{ saving ? 'Saving...' : editingId ? 'Update policy' : 'Create policy' }}
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
              Loading policies...
            </div>

            <div v-else-if="policies.length === 0" class="empty-state">
              <i class="bi bi-journal-check display-6 text-secondary"></i>
              <p class="mb-1 fw-semibold">No policies yet</p>
              <p class="text-muted mb-0">
                Start by creating the first public or draft policy record.
              </p>
            </div>

            <div v-else class="table-responsive">
              <table class="table align-middle">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Linked document</th>
                    <th>Updated</th>
                    <th class="text-end">Actions</th>
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
                          Edit
                        </button>
                        <button class="btn btn-outline-danger" type="button" @click="removePolicy(policy)">
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
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
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

const loading = ref(true)
const saving = ref(false)
const policies = ref<PolicyRecordResponse[]>([])
const categories = ref<string[]>([])
const documents = ref<DocumentListItemResponse[]>([])
const editingId = ref<string | null>(null)

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

async function refreshPolicies() {
  loading.value = true
  try {
    const [policyList, categoryList, documentList] = await Promise.all([
      listPolicies(),
      listPolicyCategories(),
      listDocuments(),
    ])
    policies.value = policyList
    categories.value = categoryList.categories
    documents.value = documentList
  } finally {
    loading.value = false
  }
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
  } finally {
    saving.value = false
  }
}

async function removePolicy(policy: PolicyRecordResponse) {
  if (!confirm(`Delete policy "${policy.title}"?`)) {
    return
  }
  saving.value = true
  try {
    await deletePolicy(policy.id)
    await refreshPolicies()
    if (editingId.value === policy.id) {
      resetForm()
    }
  } finally {
    saving.value = false
  }
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString()
}

onMounted(async () => {
  await refreshPolicies()
})
</script>
