<template>
  <div class="p-4">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h1 class="h4 fw-bold mb-0">Members</h1>
        <p class="text-muted small mb-0">Manage organization member profiles</p>
      </div>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-secondary btn-sm" @click="exportMembers" :disabled="exporting">
          <i v-if="exporting" class="spinner-border spinner-border-sm me-1"></i>
          <i v-else class="bi bi-download me-1"></i>Export CSV
        </button>
        <button class="btn btn-outline-primary btn-sm" data-bs-toggle="modal" data-bs-target="#importMemberModal">
          <i class="bi bi-upload me-1"></i>Import CSV
        </button>
        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createMemberModal">
          <i class="bi bi-person-plus me-1"></i>Add member
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger alert-dismissible small py-2 mb-3" role="alert">
      <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
      <button type="button" class="btn-close py-2" @click="error = ''"></button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="members.length === 0" class="empty-state">
      <i class="bi bi-people display-6 text-secondary"></i>
      <p class="mb-1 fw-semibold">No member profiles yet</p>
      <p class="text-muted mb-3">
        Add the first member manually or import a CSV to give the tenant a working directory.
      </p>
      <div class="d-flex flex-wrap justify-content-center gap-2">
        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createMemberModal">
          Add first member
        </button>
        <button class="btn btn-outline-secondary btn-sm" data-bs-toggle="modal" data-bs-target="#importMemberModal">
          Import CSV
        </button>
        <RouterLink to="/admin/settings" class="btn btn-outline-secondary btn-sm">
          Review settings
        </RouterLink>
      </div>
    </div>

    <div v-else class="card shadow-sm border-0">
      <div class="table-responsive">
        <table class="table table-hover mb-0 align-middle" aria-label="Members list">
          <thead class="table-light">
            <tr>
              <th class="ps-4" scope="col">Code</th>
              <th scope="col">Name</th>
              <th scope="col">Email</th>
              <th scope="col">Status</th>
              <th scope="col">Joined</th>
              <th class="text-end pe-4" scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="member in members" :key="member.id">
              <td class="ps-4 font-monospace small">{{ member.member_code }}</td>
              <td class="fw-medium">{{ member.display_name }}</td>
              <td class="small text-muted">{{ member.email || '—' }}</td>
              <td>
                <span class="badge"
                  :class="member.status === 'active' ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'">
                  {{ member.status }}
                </span>
              </td>
              <td class="small">{{ formatDate(member.joined_at) }}</td>
              <td class="text-end pe-4">
                <button class="btn btn-sm btn-outline-secondary me-1" aria-label="Edit member"
                  @click="editMember(member)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" aria-label="Delete member"
                  @click="confirmDelete(member)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>

          </tbody>
        </table>
      </div>
    </div>

    <!-- Import Members Modal -->
    <div class="modal fade" id="importMemberModal" tabindex="-1" aria-labelledby="importMemberModalLabel">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="importMemberModalLabel">Import members from CSV</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" @click="resetImport"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">CSV file</label>
              <input ref="importFileInput" class="form-control form-control-sm" type="file" accept=".csv" @change="onImportFileChange" />
              <div class="form-text small">Required columns: <code>member_code</code>, <code>first_name</code>, <code>last_name</code>. Optional: <code>display_name</code>, <code>email</code>, <code>phone</code>, <code>status</code>.</div>
            </div>
            <div class="form-check mb-3">
              <input id="importDryRun" v-model="importDryRun" type="checkbox" class="form-check-input" />
              <label for="importDryRun" class="form-check-label small">Dry run (validate only, no changes saved)</label>
            </div>
            <div v-if="importResult" class="mt-3">
              <hr />
              <div class="d-flex gap-3 mb-3">
                <span class="badge bg-secondary">Total: {{ importResult.total }}</span>
                <span class="badge bg-success">Success: {{ importResult.success_count }}</span>
                <span class="badge" :class="importResult.error_count > 0 ? 'bg-danger' : 'bg-success'">Errors: {{ importResult.error_count }}</span>
              </div>
              <div v-if="importResult.errors.length > 0" class="mb-3">
                <h6 class="small fw-bold text-danger">Validation errors</h6>
                <table class="table table-sm small mb-0">
                  <thead><tr><th>Row</th><th>Error</th></tr></thead>
                  <tbody>
                    <tr v-for="err in importResult.errors" :key="err.row">
                      <td>{{ err.row }}</td>
                      <td>{{ err.message }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-if="importResult.error_count === 0 && !importDryRun" class="alert alert-success small py-2 mb-0">
                Successfully imported {{ importResult.success_count }} members.
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal" @click="resetImport">Cancel</button>
            <button v-if="importDryRun && importResult && importResult.error_count === 0" type="button" class="btn btn-sm btn-primary" @click="confirmImport" :disabled="importing">
              {{ importing ? 'Importing...' : 'Confirm import' }}
            </button>
            <button v-else type="button" class="btn btn-sm btn-primary" @click="handleImport" :disabled="importing || !importSelectedFile">
              {{ importing ? 'Importing...' : importDryRun ? 'Validate' : 'Import' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Member Modal -->
    <div class="modal fade" id="createMemberModal" tabindex="-1" aria-labelledby="createMemberModalLabel">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="createMemberModalLabel">Add member</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">Member code</label>
              <input v-model="form.member_code" class="form-control form-control-sm" required />
            </div>
            <div class="row g-2 mb-3">
              <div class="col">
                <label class="form-label small fw-medium">First name</label>
                <input v-model="form.first_name" class="form-control form-control-sm" required />
              </div>
              <div class="col">
                <label class="form-label small fw-medium">Last name</label>
                <input v-model="form.last_name" class="form-control form-control-sm" required />
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Display name</label>
              <input v-model="form.display_name" class="form-control form-control-sm" required />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Email</label>
              <input v-model="form.email" type="email" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Phone</label>
              <input v-model="form.phone" class="form-control form-control-sm" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-sm btn-primary" @click="handleCreate" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Member Modal -->
    <div class="modal fade" id="editMemberModal" tabindex="-1" aria-labelledby="editMemberModalLabel">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editMemberModalLabel">Edit member</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">Member code</label>
              <input v-model="editForm.member_code" class="form-control form-control-sm" />
            </div>
            <div class="row g-2 mb-3">
              <div class="col">
                <label class="form-label small fw-medium">First name</label>
                <input v-model="editForm.first_name" class="form-control form-control-sm" />
              </div>
              <div class="col">
                <label class="form-label small fw-medium">Last name</label>
                <input v-model="editForm.last_name" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Display name</label>
              <input v-model="editForm.display_name" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Email</label>
              <input v-model="editForm.email" type="email" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Phone</label>
              <input v-model="editForm.phone" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Status</label>
              <select v-model="editForm.status" class="form-select form-select-sm">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="suspended">Suspended</option>
                <option value="resigned">Resigned</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-sm btn-primary" @click="handleUpdate" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteMemberModal" tabindex="-1" aria-labelledby="deleteMemberModalLabel">
      <div class="modal-dialog modal-sm">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="deleteMemberModalLabel">Confirm delete</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p class="mb-0 small">Remove <strong>{{ deletingMember?.display_name }}</strong>?</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-sm btn-danger" @click="handleDelete" :disabled="saving">
              {{ saving ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import * as bootstrap from 'bootstrap'
import { listMembers, createMember, updateMember, deleteMember, importMembersCsv, exportMembersCsv } from '@/api/membership.api'
import type { MembershipProfileResponse, CreateMemberPayload, UpdateMemberPayload, ImportResult } from '@/api/membership.api'
import { useCsvExport } from '@/composables/useCsvExport'

const loading = ref(true)
const error = ref('')
const members = ref<MembershipProfileResponse[]>([])
const saving = ref(false)
const deletingMember = ref<MembershipProfileResponse | null>(null)

function setError(err: unknown) {
  error.value = (err as any)?.response?.data?.detail || (err as any)?.message || 'An unexpected error occurred'
}

const form = ref<CreateMemberPayload>({
  member_code: '',
  first_name: '',
  last_name: '',
  display_name: '',
  email: '',
  phone: '',
})

const editForm = ref<UpdateMemberPayload>({})
const editingId = ref<string | null>(null)

const importSelectedFile = ref<File | null>(null)
const importDryRun = ref(true)
const importing = ref(false)
const importResult = ref<ImportResult | null>(null)
const importFileInput = ref<HTMLInputElement | null>(null)

const { exportCsv, exporting } = useCsvExport()

function resetImport() {
  importSelectedFile.value = null
  importDryRun.value = true
  importing.value = false
  importResult.value = null
  if (importFileInput.value) importFileInput.value.value = ''
}

function onImportFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  importSelectedFile.value = input.files?.[0] ?? null
  importResult.value = null
}

async function handleImport() {
  if (!importSelectedFile.value) return
  importing.value = true
  try {
    importResult.value = await importMembersCsv(importSelectedFile.value, importDryRun.value)
  } finally { importing.value = false }
}

async function confirmImport() {
  importDryRun.value = false
  await handleImport()
  if (importResult.value && importResult.value.error_count > 0) {
    importDryRun.value = true
  } else {
    await loadMembers()
  }
}

async function exportMembers() {
  try {
    await exportCsv(exportMembersCsv, 'members.csv')
  } catch (err) { setError(err) }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

async function loadMembers() {
  try {
    members.value = await listMembers()
  } catch (err) { setError(err) }
  finally { loading.value = false }
}

function resetForm() {
  form.value = { member_code: '', first_name: '', last_name: '', display_name: '', email: '', phone: '' }
}

async function handleCreate() {
  saving.value = true
  try {
    await createMember(form.value)
    resetForm()
    await loadMembers()
    const modal = bootstrap.Modal.getInstance(document.getElementById('createMemberModal')!)
    modal?.hide()
  } catch (err) { setError(err) }
  finally { saving.value = false }
}

function editMember(member: MembershipProfileResponse) {
  editingId.value = member.id
  editForm.value = {
    member_code: member.member_code,
    first_name: member.first_name,
    last_name: member.last_name,
    display_name: member.display_name,
    email: member.email || '',
    phone: member.phone || '',
    status: member.status,
  }
  nextTick(() => {
    const modal = new bootstrap.Modal(document.getElementById('editMemberModal')!)
    modal.show()
  })
}

async function handleUpdate() {
  if (!editingId.value) return
  saving.value = true
  try {
    await updateMember(editingId.value, editForm.value)
    await loadMembers()
    const modal = bootstrap.Modal.getInstance(document.getElementById('editMemberModal')!)
    modal?.hide()
  } catch (err) { setError(err) }
  finally { saving.value = false }
}

function confirmDelete(member: MembershipProfileResponse) {
  deletingMember.value = member
  nextTick(() => {
    const modal = new bootstrap.Modal(document.getElementById('deleteMemberModal')!)
    modal.show()
  })
}

async function handleDelete() {
  if (!deletingMember.value) return
  saving.value = true
  try {
    await deleteMember(deletingMember.value.id)
    await loadMembers()
    const modal = bootstrap.Modal.getInstance(document.getElementById('deleteMemberModal')!)
    modal?.hide()
  } catch (err) { setError(err) }
  finally { saving.value = false; deletingMember.value = null }
}

onMounted(loadMembers)
</script>
